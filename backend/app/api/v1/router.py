from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentActor, get_current_actor, require_roles
from app.core.db import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import (
    Appointment,
    Clinic,
    ClinicMembership,
    ClinicSetting,
    Doctor,
    FollowUpTask,
    InboxStatus,
    InboxItem,
    Message,
    Package,
    PackageSession,
    Patient,
    PreferredLanguage,
    RecoveryOpportunity,
    RecoveryType,
    Role,
    Service,
    SlotOpportunity,
    TaskStatus,
    User,
    VisitRecord,
    WaitlistEntry,
)
from app.schemas import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentPatch,
    CancelRequest,
    CompleteAppointmentRequest,
    DoctorCreate,
    DoctorOut,
    FollowUpTaskOut,
    InboxItemOut,
    InboxPatch,
    LoginRequest,
    MeOut,
    MergePatientRequest,
    MessageDraftCreate,
    MessageOut,
    MockReplyCreate,
    PackageCreate,
    PackageOut,
    PatientCreate,
    PatientOut,
    PatientUpdate,
    RecoveryOut,
    RegisterOwnerRequest,
    RescheduleRequest,
    ServiceCreate,
    ServiceOut,
    SettingOut,
    SettingsPatch,
    SlotOpportunityOut,
    Token,
    UserOut,
    VisitCreate,
    VisitOut,
    WaitlistCreate,
    WaitlistOut,
)
from app.services.appointments import AppointmentService
from app.services.dashboard import AnalyticsService, DashboardService
from app.services.events import EventService
from app.services.messages import MessageService

api_router = APIRouter(prefix="/api/v1")


def get_tenant_or_404(db: Session, model, clinic_id: str, object_id: str):
    obj = db.get(model, object_id)
    if not obj or obj.clinic_id != clinic_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return obj


@api_router.post("/auth/register-owner", response_model=Token)
def register_owner(payload: RegisterOwnerRequest, db: Session = Depends(get_db)) -> Token:
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    clinic = Clinic(name=payload.clinic_name)
    user = User(email=payload.email.lower(), full_name=payload.full_name, password_hash=hash_password(payload.password))
    db.add_all([clinic, user])
    db.flush()
    membership = ClinicMembership(clinic_id=clinic.id, user_id=user.id, role=Role.OWNER_ADMIN)
    db.add(membership)
    db.add(ClinicSetting(clinic_id=clinic.id, key="language_settings", value={"languages": ["english", "arabic", "french", "arabizi"]}))
    db.commit()
    return Token(access_token=create_access_token(user.id, clinic.id, {"role": membership.role.value}))


@api_router.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    membership = db.scalar(select(ClinicMembership).where(ClinicMembership.user_id == user.id))
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no clinic membership")
    return Token(access_token=create_access_token(user.id, membership.clinic_id, {"role": membership.role.value}))


@api_router.get("/auth/me", response_model=MeOut)
def me(actor: CurrentActor = Depends(get_current_actor), db: Session = Depends(get_db)) -> MeOut:
    clinic = db.get(Clinic, actor.clinic_id)
    return MeOut(
        user=UserOut.model_validate(actor.user),
        clinic_id=actor.clinic_id,
        clinic_name=clinic.name if clinic else "Clinic",
        role=actor.role,
    )


@api_router.get("/dashboard/today")
def dashboard_today(actor: CurrentActor = Depends(get_current_actor), db: Session = Depends(get_db)):
    return DashboardService(db).today(actor.clinic_id)


@api_router.get("/patients", response_model=list[PatientOut])
def list_patients(
    q: str | None = None,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY, Role.ASSISTANT)),
    db: Session = Depends(get_db),
):
    stmt = select(Patient).where(Patient.clinic_id == actor.clinic_id).order_by(Patient.name)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((Patient.name.ilike(like)) | (Patient.normalized_phone.ilike(like)))
    return list(db.scalars(stmt))


@api_router.post("/patients", response_model=PatientOut)
def create_patient(
    payload: PatientCreate,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY)),
    db: Session = Depends(get_db),
):
    duplicate = db.scalar(
        select(Patient).where(
            Patient.clinic_id == actor.clinic_id,
            Patient.normalized_phone == payload.normalized_phone,
        )
    )
    patient = Patient(clinic_id=actor.clinic_id, **payload.model_dump())
    if duplicate:
        patient.duplicate_of_patient_id = duplicate.id
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@api_router.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str, actor: CurrentActor = Depends(get_current_actor), db: Session = Depends(get_db)):
    return get_tenant_or_404(db, Patient, actor.clinic_id, patient_id)


@api_router.patch("/patients/{patient_id}", response_model=PatientOut)
def patch_patient(
    patient_id: str,
    payload: PatientUpdate,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY)),
    db: Session = Depends(get_db),
):
    patient = get_tenant_or_404(db, Patient, actor.clinic_id, patient_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient


@api_router.post("/patients/{patient_id}/merge", response_model=PatientOut)
def merge_patient(
    patient_id: str,
    payload: MergePatientRequest,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY)),
    db: Session = Depends(get_db),
):
    patient = get_tenant_or_404(db, Patient, actor.clinic_id, patient_id)
    duplicate = get_tenant_or_404(db, Patient, actor.clinic_id, payload.duplicate_patient_id)
    duplicate.duplicate_of_patient_id = patient.id
    duplicate.status = "merged"
    db.commit()
    db.refresh(patient)
    return patient


@api_router.get("/doctors", response_model=list[DoctorOut])
def list_doctors(actor: CurrentActor = Depends(get_current_actor), db: Session = Depends(get_db)):
    return list(db.scalars(select(Doctor).where(Doctor.clinic_id == actor.clinic_id).order_by(Doctor.name)))


@api_router.post("/doctors", response_model=DoctorOut)
def create_doctor(
    payload: DoctorCreate,
    actor: CurrentActor = Depends(require_roles(Role.OWNER_ADMIN)),
    db: Session = Depends(get_db),
):
    doctor = Doctor(clinic_id=actor.clinic_id, **payload.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@api_router.get("/services", response_model=list[ServiceOut])
def list_services(actor: CurrentActor = Depends(get_current_actor), db: Session = Depends(get_db)):
    return list(db.scalars(select(Service).where(Service.clinic_id == actor.clinic_id).order_by(Service.name)))


@api_router.post("/services", response_model=ServiceOut)
def create_service(
    payload: ServiceCreate,
    actor: CurrentActor = Depends(require_roles(Role.OWNER_ADMIN)),
    db: Session = Depends(get_db),
):
    service = Service(clinic_id=actor.clinic_id, **payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@api_router.get("/appointments", response_model=list[AppointmentOut])
def list_appointments(actor: CurrentActor = Depends(get_current_actor), db: Session = Depends(get_db)):
    return list(
        db.scalars(select(Appointment).where(Appointment.clinic_id == actor.clinic_id).order_by(Appointment.starts_at))
    )


@api_router.post("/appointments", response_model=AppointmentOut)
def create_appointment(
    payload: AppointmentCreate,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY)),
    db: Session = Depends(get_db),
):
    appointment = AppointmentService(db).create(actor.clinic_id, payload, actor.user.id)
    db.commit()
    db.refresh(appointment)
    return appointment


@api_router.get("/appointments/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: str, actor: CurrentActor = Depends(get_current_actor), db: Session = Depends(get_db)):
    return get_tenant_or_404(db, Appointment, actor.clinic_id, appointment_id)


@api_router.patch("/appointments/{appointment_id}", response_model=AppointmentOut)
def patch_appointment(
    appointment_id: str,
    payload: AppointmentPatch,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY, Role.ASSISTANT)),
    db: Session = Depends(get_db),
):
    appointment = get_tenant_or_404(db, Appointment, actor.clinic_id, appointment_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(appointment, key, value)
    db.commit()
    db.refresh(appointment)
    return appointment


@api_router.post("/appointments/{appointment_id}/confirm", response_model=AppointmentOut)
def confirm_appointment(
    appointment_id: str,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY, Role.ASSISTANT)),
    db: Session = Depends(get_db),
):
    appointment = get_tenant_or_404(db, Appointment, actor.clinic_id, appointment_id)
    AppointmentService(db).confirm(appointment, actor.user.id)
    db.commit()
    db.refresh(appointment)
    return appointment


@api_router.post("/appointments/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_appointment(
    appointment_id: str,
    payload: CancelRequest | None = None,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY)),
    db: Session = Depends(get_db),
):
    appointment = get_tenant_or_404(db, Appointment, actor.clinic_id, appointment_id)
    AppointmentService(db).cancel(appointment, payload.reason if payload else None, actor.user.id)
    db.commit()
    db.refresh(appointment)
    return appointment


@api_router.post("/appointments/{appointment_id}/reschedule", response_model=AppointmentOut)
def reschedule_appointment(
    appointment_id: str,
    payload: RescheduleRequest,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY)),
    db: Session = Depends(get_db),
):
    appointment = get_tenant_or_404(db, Appointment, actor.clinic_id, appointment_id)
    AppointmentService(db).reschedule(appointment, payload, actor.user.id)
    db.commit()
    db.refresh(appointment)
    return appointment


@api_router.post("/appointments/{appointment_id}/complete", response_model=AppointmentOut)
def complete_appointment(
    appointment_id: str,
    payload: CompleteAppointmentRequest,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR)),
    db: Session = Depends(get_db),
):
    appointment = get_tenant_or_404(db, Appointment, actor.clinic_id, appointment_id)
    AppointmentService(db).complete(appointment, payload, actor.user.id)
    db.commit()
    db.refresh(appointment)
    return appointment


@api_router.post("/appointments/{appointment_id}/no-show", response_model=AppointmentOut)
def no_show_appointment(
    appointment_id: str,
    actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY)),
    db: Session = Depends(get_db),
):
    appointment = get_tenant_or_404(db, Appointment, actor.clinic_id, appointment_id)
    AppointmentService(db).no_show(appointment, actor.user.id)
    db.commit()
    db.refresh(appointment)
    return appointment


@api_router.get("/messages", response_model=list[MessageOut])
def list_messages(actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)), db: Session = Depends(get_db)):
    return list(db.scalars(select(Message).where(Message.clinic_id == actor.clinic_id).order_by(Message.created_at.desc())))


@api_router.post("/messages/draft", response_model=MessageOut)
def draft_message(
    payload: MessageDraftCreate,
    actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)),
    db: Session = Depends(get_db),
):
    message = MessageService(db).draft(
        clinic_id=actor.clinic_id,
        patient_id=payload.patient_id,
        appointment_id=payload.appointment_id,
        body=payload.body,
        actor_user_id=actor.user.id,
    )
    db.commit()
    db.refresh(message)
    return message


@api_router.post("/messages/{message_id}/approve", response_model=MessageOut)
def approve_message(message_id: str, actor: CurrentActor = Depends(require_roles(Role.SECRETARY)), db: Session = Depends(get_db)):
    message = get_tenant_or_404(db, Message, actor.clinic_id, message_id)
    MessageService(db).approve(message, actor.user.id)
    db.commit()
    db.refresh(message)
    return message


@api_router.post("/messages/{message_id}/send", response_model=MessageOut)
def send_message(message_id: str, actor: CurrentActor = Depends(require_roles(Role.SECRETARY)), db: Session = Depends(get_db)):
    message = get_tenant_or_404(db, Message, actor.clinic_id, message_id)
    MessageService(db).send(message, actor.user.id)
    db.commit()
    db.refresh(message)
    return message


@api_router.post("/messages/mock-reply", response_model=MessageOut)
def mock_reply(payload: MockReplyCreate, actor: CurrentActor = Depends(get_current_actor), db: Session = Depends(get_db)):
    message, _ = MessageService(db).mock_reply(
        clinic_id=actor.clinic_id,
        patient_id=payload.patient_id,
        appointment_id=payload.appointment_id,
        body=payload.body,
    )
    db.commit()
    db.refresh(message)
    return message


@api_router.get("/inbox", response_model=list[InboxItemOut])
def list_inbox(actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)), db: Session = Depends(get_db)):
    return list(db.scalars(select(InboxItem).where(InboxItem.clinic_id == actor.clinic_id).order_by(InboxItem.created_at.desc())))


@api_router.patch("/inbox/{inbox_id}", response_model=InboxItemOut)
def patch_inbox(
    inbox_id: str,
    payload: InboxPatch,
    actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)),
    db: Session = Depends(get_db),
):
    item = get_tenant_or_404(db, InboxItem, actor.clinic_id, inbox_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@api_router.post("/inbox/{inbox_id}/resolve", response_model=InboxItemOut)
def resolve_inbox(inbox_id: str, actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)), db: Session = Depends(get_db)):
    item = get_tenant_or_404(db, InboxItem, actor.clinic_id, inbox_id)
    item.status = InboxStatus.RESOLVED
    db.commit()
    db.refresh(item)
    return item


@api_router.get("/follow-ups", response_model=list[FollowUpTaskOut])
def list_followups(actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)), db: Session = Depends(get_db)):
    return list(db.scalars(select(FollowUpTask).where(FollowUpTask.clinic_id == actor.clinic_id).order_by(FollowUpTask.due_date)))


@api_router.post("/follow-ups/{task_id}/approve", response_model=FollowUpTaskOut)
def approve_followup(task_id: str, actor: CurrentActor = Depends(require_roles(Role.SECRETARY)), db: Session = Depends(get_db)):
    task = get_tenant_or_404(db, FollowUpTask, actor.clinic_id, task_id)
    task.status = TaskStatus.APPROVED
    db.commit()
    db.refresh(task)
    return task


@api_router.post("/follow-ups/{task_id}/skip", response_model=FollowUpTaskOut)
def skip_followup(task_id: str, actor: CurrentActor = Depends(require_roles(Role.SECRETARY)), db: Session = Depends(get_db)):
    task = get_tenant_or_404(db, FollowUpTask, actor.clinic_id, task_id)
    task.status = TaskStatus.SKIPPED
    db.commit()
    db.refresh(task)
    return task


@api_router.get("/recovery", response_model=list[RecoveryOut])
def list_recovery(actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)), db: Session = Depends(get_db)):
    return list(db.scalars(select(RecoveryOpportunity).where(RecoveryOpportunity.clinic_id == actor.clinic_id).order_by(RecoveryOpportunity.created_at.desc())))


@api_router.post("/recovery/{opportunity_id}/approve-message", response_model=RecoveryOut)
def approve_recovery_message(opportunity_id: str, actor: CurrentActor = Depends(require_roles(Role.SECRETARY)), db: Session = Depends(get_db)):
    opportunity = get_tenant_or_404(db, RecoveryOpportunity, actor.clinic_id, opportunity_id)
    opportunity.status = TaskStatus.APPROVED
    db.commit()
    db.refresh(opportunity)
    return opportunity


@api_router.post("/recovery/{opportunity_id}/mark-recovered", response_model=RecoveryOut)
def mark_recovered(opportunity_id: str, actor: CurrentActor = Depends(require_roles(Role.SECRETARY)), db: Session = Depends(get_db)):
    opportunity = get_tenant_or_404(db, RecoveryOpportunity, actor.clinic_id, opportunity_id)
    opportunity.status = TaskStatus.COMPLETED
    db.commit()
    db.refresh(opportunity)
    return opportunity


@api_router.get("/waitlist", response_model=list[WaitlistOut])
def list_waitlist(actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)), db: Session = Depends(get_db)):
    return list(db.scalars(select(WaitlistEntry).where(WaitlistEntry.clinic_id == actor.clinic_id).order_by(WaitlistEntry.created_at.desc())))


@api_router.post("/waitlist", response_model=WaitlistOut)
def create_waitlist(payload: WaitlistCreate, actor: CurrentActor = Depends(require_roles(Role.SECRETARY)), db: Session = Depends(get_db)):
    entry = WaitlistEntry(clinic_id=actor.clinic_id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@api_router.get("/slot-opportunities", response_model=list[SlotOpportunityOut])
def list_slots(actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)), db: Session = Depends(get_db)):
    return list(db.scalars(select(SlotOpportunity).where(SlotOpportunity.clinic_id == actor.clinic_id).order_by(SlotOpportunity.starts_at)))


@api_router.post("/slot-opportunities/{slot_id}/offer", response_model=SlotOpportunityOut)
def offer_slot(slot_id: str, actor: CurrentActor = Depends(require_roles(Role.SECRETARY)), db: Session = Depends(get_db)):
    slot = get_tenant_or_404(db, SlotOpportunity, actor.clinic_id, slot_id)
    slot.status = TaskStatus.APPROVED
    db.commit()
    db.refresh(slot)
    return slot


@api_router.get("/packages", response_model=list[PackageOut])
def list_packages(actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)), db: Session = Depends(get_db)):
    return list(db.scalars(select(Package).where(Package.clinic_id == actor.clinic_id).order_by(Package.created_at.desc())))


@api_router.post("/packages", response_model=PackageOut)
def create_package(payload: PackageCreate, actor: CurrentActor = Depends(require_roles(Role.SECRETARY, Role.DOCTOR)), db: Session = Depends(get_db)):
    package = Package(
        clinic_id=actor.clinic_id,
        **payload.model_dump(exclude={"completed_sessions"}),
        completed_sessions=payload.completed_sessions,
        remaining_sessions=payload.total_sessions - payload.completed_sessions,
    )
    db.add(package)
    db.commit()
    db.refresh(package)
    return package


@api_router.post("/packages/{package_id}/complete-session", response_model=PackageOut)
def complete_package_session(package_id: str, actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY)), db: Session = Depends(get_db)):
    package = get_tenant_or_404(db, Package, actor.clinic_id, package_id)
    if package.remaining_sessions > 0:
        package.completed_sessions += 1
        package.remaining_sessions = max(0, package.total_sessions - package.completed_sessions)
        db.add(
            PackageSession(
                clinic_id=actor.clinic_id,
                package_id=package.id,
                session_number=package.completed_sessions,
                completed_at=datetime.utcnow(),
            )
        )
        EventService(db).emit(
            clinic_id=actor.clinic_id,
            event_type="PackageSessionCompleted",
            aggregate_type="package",
            aggregate_id=package.id,
            payload={"remaining_sessions": package.remaining_sessions},
            actor_user_id=actor.user.id,
        )
        if package.remaining_sessions <= 1:
            db.add(
                RecoveryOpportunity(
                    clinic_id=actor.clinic_id,
                    patient_id=package.patient_id,
                    type=RecoveryType.PACKAGE_INCOMPLETE,
                    estimated_value_cents=0,
                    suggested_action="Draft renewal message",
                    suggested_message="Only one session remains. Would you like to renew your package?",
                )
            )
    db.commit()
    db.refresh(package)
    return package


@api_router.get("/visits", response_model=list[VisitOut])
def list_visits(actor: CurrentActor = Depends(require_roles(Role.DOCTOR, Role.SECRETARY)), db: Session = Depends(get_db)):
    return list(db.scalars(select(VisitRecord).where(VisitRecord.clinic_id == actor.clinic_id).order_by(VisitRecord.visit_date.desc())))


@api_router.post("/visits", response_model=VisitOut)
def create_visit(payload: VisitCreate, actor: CurrentActor = Depends(require_roles(Role.DOCTOR)), db: Session = Depends(get_db)):
    visit = VisitRecord(clinic_id=actor.clinic_id, **payload.model_dump())
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


@api_router.get("/analytics/summary")
def analytics_summary(actor: CurrentActor = Depends(require_roles(Role.OWNER_ADMIN, Role.DOCTOR)), db: Session = Depends(get_db)):
    return AnalyticsService(db).summary(actor.clinic_id)


@api_router.get("/settings", response_model=list[SettingOut])
def get_settings(actor: CurrentActor = Depends(require_roles(Role.OWNER_ADMIN)), db: Session = Depends(get_db)):
    return list(db.scalars(select(ClinicSetting).where(ClinicSetting.clinic_id == actor.clinic_id).order_by(ClinicSetting.key)))


@api_router.patch("/settings", response_model=SettingOut)
def patch_settings(
    key: str,
    payload: SettingsPatch,
    actor: CurrentActor = Depends(require_roles(Role.OWNER_ADMIN)),
    db: Session = Depends(get_db),
):
    setting = db.scalar(select(ClinicSetting).where(ClinicSetting.clinic_id == actor.clinic_id, ClinicSetting.key == key))
    if not setting:
        setting = ClinicSetting(clinic_id=actor.clinic_id, key=key, value=payload.value)
        db.add(setting)
    else:
        setting.value = payload.value
    db.commit()
    db.refresh(setting)
    return setting
