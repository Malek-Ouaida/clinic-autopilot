from __future__ import annotations

from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models import (
    Appointment,
    AppointmentStatus,
    AppointmentStatusHistory,
    BlockedTime,
    FollowUpRule,
    FollowUpTask,
    Package,
    PackageSession,
    Patient,
    RecoveryOpportunity,
    RecoveryType,
    Service,
    SlotOpportunity,
    TaskStatus,
    VisitRecord,
    WaitlistEntry,
)
from app.schemas import AppointmentCreate, CompleteAppointmentRequest, RescheduleRequest
from app.services.events import EventService
from app.services.messages import MessageService


class AppointmentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)
        self.messages = MessageService(db)

    def _assert_no_conflict(
        self, clinic_id: str, doctor_id: str, starts_at, ends_at, exclude_appointment_id: str | None = None
    ) -> None:
        conflict_query = select(Appointment).where(
            Appointment.clinic_id == clinic_id,
            Appointment.doctor_id == doctor_id,
            Appointment.status.notin_([AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]),
            Appointment.starts_at < ends_at,
            Appointment.ends_at > starts_at,
        )
        if exclude_appointment_id:
            conflict_query = conflict_query.where(Appointment.id != exclude_appointment_id)
        if self.db.scalar(conflict_query):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Appointment conflicts with doctor schedule")

        blocked = self.db.scalar(
            select(BlockedTime).where(
                BlockedTime.clinic_id == clinic_id,
                or_(BlockedTime.doctor_id == doctor_id, BlockedTime.doctor_id.is_(None)),
                BlockedTime.starts_at < ends_at,
                BlockedTime.ends_at > starts_at,
            )
        )
        if blocked:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Doctor or clinic is blocked at this time")

    def create(self, clinic_id: str, payload: AppointmentCreate, actor_user_id: str | None = None) -> Appointment:
        self._assert_no_conflict(clinic_id, payload.doctor_id, payload.starts_at, payload.ends_at)
        patient = self.db.get(Patient, payload.patient_id)
        if not patient or patient.clinic_id != clinic_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
        risk_score = min(1.0, 0.25 + (patient.no_show_count * 0.2))
        appointment = Appointment(
            clinic_id=clinic_id,
            patient_id=payload.patient_id,
            doctor_id=payload.doctor_id,
            service_id=payload.service_id,
            starts_at=payload.starts_at,
            ends_at=payload.ends_at,
            status=payload.status,
            package_id=payload.package_id,
            risk_score=risk_score,
        )
        self.db.add(appointment)
        self.db.flush()
        self._record_status(appointment, None, appointment.status, actor_user_id, "created")
        self.messages.draft(
            clinic_id=clinic_id,
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            body="Hi {patient_name}, please confirm your appointment at {appointment_time}.",
            actor_user_id=actor_user_id,
        )
        self.events.emit(
            clinic_id=clinic_id,
            event_type="AppointmentCreated",
            aggregate_type="appointment",
            aggregate_id=appointment.id,
            payload={"drafted_confirmation": True, "reminder_jobs_scheduled": True},
            actor_user_id=actor_user_id,
        )
        return appointment

    def _record_status(
        self,
        appointment: Appointment,
        from_status: AppointmentStatus | None,
        to_status: AppointmentStatus,
        actor_user_id: str | None,
        reason: str | None = None,
    ) -> None:
        self.db.add(
            AppointmentStatusHistory(
                clinic_id=appointment.clinic_id,
                appointment_id=appointment.id,
                from_status=from_status,
                to_status=to_status,
                changed_by_user_id=actor_user_id,
                reason=reason,
            )
        )

    def transition(
        self,
        appointment: Appointment,
        to_status: AppointmentStatus,
        *,
        actor_user_id: str | None = None,
        reason: str | None = None,
    ) -> Appointment:
        from_status = appointment.status
        appointment.status = to_status
        self._record_status(appointment, from_status, to_status, actor_user_id, reason)
        self.events.emit(
            clinic_id=appointment.clinic_id,
            event_type=f"Appointment{to_status.value.title().replace('_', '')}",
            aggregate_type="appointment",
            aggregate_id=appointment.id,
            payload={"from_status": from_status.value, "to_status": to_status.value, "reason": reason},
            actor_user_id=actor_user_id,
        )
        return appointment

    def confirm(self, appointment: Appointment, actor_user_id: str | None = None) -> Appointment:
        return self.transition(appointment, AppointmentStatus.CONFIRMED, actor_user_id=actor_user_id)

    def cancel(self, appointment: Appointment, reason: str | None = None, actor_user_id: str | None = None) -> Appointment:
        appointment.cancellation_reason = reason
        self.transition(appointment, AppointmentStatus.CANCELLED, actor_user_id=actor_user_id, reason=reason)
        candidate_count = self.db.scalar(
            select(func.count(WaitlistEntry.id)).where(
                WaitlistEntry.clinic_id == appointment.clinic_id,
                WaitlistEntry.status == TaskStatus.OPEN,
                or_(WaitlistEntry.doctor_id.is_(None), WaitlistEntry.doctor_id == appointment.doctor_id),
                or_(WaitlistEntry.service_id.is_(None), WaitlistEntry.service_id == appointment.service_id),
            )
        ) or 0
        slot = SlotOpportunity(
            clinic_id=appointment.clinic_id,
            appointment_id=appointment.id,
            doctor_id=appointment.doctor_id,
            service_id=appointment.service_id,
            starts_at=appointment.starts_at,
            ends_at=appointment.ends_at,
            candidate_count=candidate_count,
        )
        self.db.add(slot)
        service = self.db.get(Service, appointment.service_id)
        estimated = service.price_cents if service else 0
        self.db.add(
            RecoveryOpportunity(
                clinic_id=appointment.clinic_id,
                patient_id=appointment.patient_id,
                appointment_id=appointment.id,
                type=RecoveryType.CANCELLED_NOT_REBOOKED,
                estimated_value_cents=estimated,
                suggested_action="Send cancellation recovery message",
                suggested_message="We can help you find a new time this week. Would tomorrow work?",
            )
        )
        self.events.emit(
            clinic_id=appointment.clinic_id,
            event_type="AppointmentCancelled",
            aggregate_type="appointment",
            aggregate_id=appointment.id,
            payload={"slot_opportunity_id": slot.id, "candidate_count": candidate_count},
            actor_user_id=actor_user_id,
        )
        return appointment

    def reschedule(
        self, appointment: Appointment, payload: RescheduleRequest, actor_user_id: str | None = None
    ) -> Appointment:
        self._assert_no_conflict(
            appointment.clinic_id, appointment.doctor_id, payload.starts_at, payload.ends_at, appointment.id
        )
        appointment.starts_at = payload.starts_at
        appointment.ends_at = payload.ends_at
        appointment.status = AppointmentStatus.RESCHEDULED
        self._record_status(appointment, None, AppointmentStatus.RESCHEDULED, actor_user_id, "rescheduled")
        self.events.emit(
            clinic_id=appointment.clinic_id,
            event_type="AppointmentRescheduled",
            aggregate_type="appointment",
            aggregate_id=appointment.id,
            actor_user_id=actor_user_id,
        )
        return appointment

    def no_show(self, appointment: Appointment, actor_user_id: str | None = None) -> Appointment:
        self.transition(appointment, AppointmentStatus.NO_SHOW, actor_user_id=actor_user_id)
        patient = self.db.get(Patient, appointment.patient_id)
        if patient:
            patient.no_show_count += 1
        service = self.db.get(Service, appointment.service_id)
        self.db.add(
            RecoveryOpportunity(
                clinic_id=appointment.clinic_id,
                patient_id=appointment.patient_id,
                appointment_id=appointment.id,
                type=RecoveryType.MISSED_NOT_RESCHEDULED,
                estimated_value_cents=service.price_cents if service else 0,
                suggested_action="Send no-show recovery message",
                suggested_message="We missed you today. Would you like us to help you rebook?",
            )
        )
        self.events.emit(
            clinic_id=appointment.clinic_id,
            event_type="AppointmentNoShow",
            aggregate_type="appointment",
            aggregate_id=appointment.id,
            payload={"risk_score_increased": True},
            actor_user_id=actor_user_id,
        )
        return appointment

    def complete(
        self, appointment: Appointment, payload: CompleteAppointmentRequest, actor_user_id: str | None = None
    ) -> Appointment:
        self.transition(appointment, AppointmentStatus.COMPLETED, actor_user_id=actor_user_id)
        visit = VisitRecord(
            clinic_id=appointment.clinic_id,
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            service_id=appointment.service_id,
            visit_date=appointment.starts_at.date(),
            reason_for_visit=payload.reason_for_visit,
            notes=payload.notes,
            treatment_done=payload.treatment_done,
            follow_up_required=payload.follow_up_required,
            follow_up_date=payload.follow_up_date,
            private_notes=payload.private_notes,
        )
        self.db.add(visit)

        rule = self.db.scalar(
            select(FollowUpRule).where(
                FollowUpRule.clinic_id == appointment.clinic_id,
                FollowUpRule.service_id == appointment.service_id,
                FollowUpRule.is_active.is_(True),
            )
        )
        if rule or payload.follow_up_required:
            due_date = payload.follow_up_date or (
                appointment.starts_at.date() + timedelta(days=rule.days_after_visit if rule else 30)
            )
            self.db.add(
                FollowUpTask(
                    clinic_id=appointment.clinic_id,
                    patient_id=appointment.patient_id,
                    appointment_id=appointment.id,
                    service_id=appointment.service_id,
                    due_date=due_date,
                    suggested_message="It is time for your follow-up. Would you like to book a visit?",
                )
            )

        if appointment.package_id:
            package = self.db.get(Package, appointment.package_id)
            if package and package.clinic_id == appointment.clinic_id and package.remaining_sessions > 0:
                package.completed_sessions += 1
                package.remaining_sessions = max(0, package.total_sessions - package.completed_sessions)
                self.db.add(
                    PackageSession(
                        clinic_id=appointment.clinic_id,
                        package_id=package.id,
                        appointment_id=appointment.id,
                        session_number=package.completed_sessions,
                        completed_at=appointment.ends_at,
                    )
                )
                if package.remaining_sessions <= 1:
                    self.db.add(
                        RecoveryOpportunity(
                            clinic_id=appointment.clinic_id,
                            patient_id=package.patient_id,
                            appointment_id=appointment.id,
                            type=RecoveryType.PACKAGE_INCOMPLETE,
                            estimated_value_cents=0,
                            suggested_action="Draft renewal message",
                            suggested_message="You have one session remaining. Would you like us to prepare a renewal?",
                        )
                    )

        self.events.emit(
            clinic_id=appointment.clinic_id,
            event_type="AppointmentCompleted",
            aggregate_type="appointment",
            aggregate_id=appointment.id,
            payload={"visit_record_created": True, "follow_up_checked": True, "package_checked": True},
            actor_user_id=actor_user_id,
        )
        return appointment

