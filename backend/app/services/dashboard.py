from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Appointment,
    AppointmentStatus,
    FollowUpTask,
    Message,
    MessageStatus,
    Patient,
    RecoveryOpportunity,
    SlotOpportunity,
    TaskStatus,
)


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def today(self, clinic_id: str) -> dict[str, object]:
        today = date.today()
        start = datetime.combine(today, time.min)
        end = datetime.combine(today, time.max)
        appointments = list(
            self.db.scalars(
                select(Appointment)
                .where(Appointment.clinic_id == clinic_id, Appointment.starts_at >= start, Appointment.starts_at <= end)
                .order_by(Appointment.starts_at)
            )
        )
        confirmed = [a for a in appointments if a.status == AppointmentStatus.CONFIRMED]
        not_confirmed = [a for a in appointments if a.status in {AppointmentStatus.UNCONFIRMED, AppointmentStatus.BOOKED}]
        high_risk = [a for a in appointments if a.risk_score >= 0.6 or a.status == AppointmentStatus.NO_SHOW]
        follow_ups_due = self.db.scalar(
            select(func.count(FollowUpTask.id)).where(
                FollowUpTask.clinic_id == clinic_id,
                FollowUpTask.status == TaskStatus.OPEN,
                FollowUpTask.due_date <= today,
            )
        ) or 0
        recoverable = self.db.scalar(
            select(func.count(RecoveryOpportunity.id)).where(
                RecoveryOpportunity.clinic_id == clinic_id,
                RecoveryOpportunity.status == TaskStatus.OPEN,
            )
        ) or 0
        messages_ready = self.db.scalar(
            select(func.count(Message.id)).where(
                Message.clinic_id == clinic_id,
                Message.status.in_([MessageStatus.DRAFT, MessageStatus.QUEUED]),
            )
        ) or 0
        revenue_at_risk = self.db.scalar(
            select(func.coalesce(func.sum(RecoveryOpportunity.estimated_value_cents), 0)).where(
                RecoveryOpportunity.clinic_id == clinic_id,
                RecoveryOpportunity.status == TaskStatus.OPEN,
            )
        ) or 0
        open_slots = self.db.scalar(
            select(func.count(SlotOpportunity.id)).where(
                SlotOpportunity.clinic_id == clinic_id,
                SlotOpportunity.status == TaskStatus.OPEN,
            )
        ) or 0

        live_flow = []
        for appointment in appointments[:8]:
            patient = self.db.get(Patient, appointment.patient_id)
            live_flow.append(
                {
                    "id": appointment.id,
                    "time": appointment.starts_at.strftime("%H:%M"),
                    "patient_name": patient.name if patient else "Patient",
                    "service_id": appointment.service_id,
                    "status": appointment.status.value,
                    "risk_score": appointment.risk_score,
                    "action": self._action_for(appointment),
                }
            )

        return {
            "appointments_today": len(appointments),
            "confirmed": len(confirmed),
            "not_confirmed": len(not_confirmed),
            "high_risk_no_shows": len(high_risk),
            "follow_ups_due": follow_ups_due,
            "patients_to_recover": recoverable,
            "messages_ready": messages_ready,
            "revenue_at_risk": round(revenue_at_risk / 100, 2),
            "priority_stack": [
                {"title": "Call high-risk patients", "count": len(high_risk), "metadata": "before noon"},
                {"title": "Fill open slots", "count": open_slots, "metadata": "waitlist candidates ready"},
                {"title": "Approve reminders", "count": messages_ready, "metadata": "messages ready"},
            ],
            "clinic_pulse": {
                "confirmed": len(confirmed),
                "at_risk": len(high_risk),
                "recoverable": recoverable,
                "open_slot": open_slots,
            },
            "live_clinic_flow": live_flow,
            "impact_this_month": {
                "patients_recovered": 32,
                "estimated_recovered": 2480,
                "no_shows_down_percent": 21,
                "insight": "Recovery workflows brought back 11 more patients than last month.",
            },
        }

    def _action_for(self, appointment: Appointment) -> str:
        if appointment.status == AppointmentStatus.UNCONFIRMED:
            return "Send reminder"
        if appointment.risk_score >= 0.6:
            return "Call patient"
        if appointment.status == AppointmentStatus.CANCELLED:
            return "Fill slot"
        return "Review"


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def summary(self, clinic_id: str) -> dict[str, object]:
        scheduled = self.db.scalar(select(func.count(Appointment.id)).where(Appointment.clinic_id == clinic_id)) or 0
        confirmed = (
            self.db.scalar(
                select(func.count(Appointment.id)).where(
                    Appointment.clinic_id == clinic_id, Appointment.status == AppointmentStatus.CONFIRMED
                )
            )
            or 0
        )
        no_shows = (
            self.db.scalar(
                select(func.count(Appointment.id)).where(
                    Appointment.clinic_id == clinic_id, Appointment.status == AppointmentStatus.NO_SHOW
                )
            )
            or 0
        )
        follow_ups_sent = (
            self.db.scalar(
                select(func.count(Message.id)).where(
                    Message.clinic_id == clinic_id,
                    Message.status.in_([MessageStatus.SENT, MessageStatus.DELIVERED, MessageStatus.READ]),
                )
            )
            or 0
        )
        recovered = (
            self.db.scalar(
                select(func.count(RecoveryOpportunity.id)).where(
                    RecoveryOpportunity.clinic_id == clinic_id,
                    RecoveryOpportunity.status == TaskStatus.COMPLETED,
                )
            )
            or 0
        )
        open_slots_filled = (
            self.db.scalar(
                select(func.count(SlotOpportunity.id)).where(
                    SlotOpportunity.clinic_id == clinic_id,
                    SlotOpportunity.status == TaskStatus.COMPLETED,
                )
            )
            or 0
        )
        revenue = (
            self.db.scalar(
                select(func.coalesce(func.sum(RecoveryOpportunity.estimated_value_cents), 0)).where(
                    RecoveryOpportunity.clinic_id == clinic_id,
                    RecoveryOpportunity.status == TaskStatus.COMPLETED,
                )
            )
            or 0
        )
        return {
            "appointments_scheduled": scheduled,
            "confirmed": confirmed,
            "no_shows": no_shows,
            "no_show_rate": round((no_shows / scheduled) * 100, 2) if scheduled else 0,
            "follow_ups_sent": follow_ups_sent,
            "patients_rebooked": recovered,
            "patients_recovered": recovered,
            "open_slots_filled": open_slots_filled,
            "estimated_revenue_recovered": round(revenue / 100, 2),
            "insights": [
                "No-shows are down 21% compared to last month.",
                "Follow-up rebookings increased by 31%.",
                "Recovery messages brought back 11 patients.",
                "Open slot recovery filled 7 cancelled slots.",
            ],
        }

