from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, time
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


def new_id() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class IdMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)


class TenantMixin:
    clinic_id: Mapped[str] = mapped_column(String(36), ForeignKey("clinics.id"), index=True, nullable=False)


class Role(str, enum.Enum):
    OWNER_ADMIN = "owner_admin"
    DOCTOR = "doctor"
    SECRETARY = "secretary"
    ASSISTANT = "assistant"


class PreferredLanguage(str, enum.Enum):
    ENGLISH = "english"
    ARABIC = "arabic"
    FRENCH = "french"
    ARABIZI = "arabizi"


class AppointmentStatus(str, enum.Enum):
    BOOKED = "booked"
    CONFIRMED = "confirmed"
    UNCONFIRMED = "unconfirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class MessageStatus(str, enum.Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    REPLIED = "replied"
    CANCELLED = "cancelled"


class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class InboxStatus(str, enum.Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"


class Intent(str, enum.Enum):
    CONFIRM = "confirm"
    CANCEL = "cancel"
    RESCHEDULE = "reschedule"
    QUESTION = "question"
    UNKNOWN = "unknown"


class RecoveryType(str, enum.Enum):
    MISSED_NOT_RESCHEDULED = "missed_not_rescheduled"
    CANCELLED_NOT_REBOOKED = "cancelled_not_rebooked"
    OVERDUE_FOLLOW_UP = "overdue_follow_up"
    INACTIVE_PATIENT = "inactive_patient"
    PACKAGE_INCOMPLETE = "package_incomplete"


class TaskStatus(str, enum.Enum):
    OPEN = "open"
    APPROVED = "approved"
    SKIPPED = "skipped"
    COMPLETED = "completed"


class Clinic(IdMixin, TimestampMixin, Base):
    __tablename__ = "clinics"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(80), default="Asia/Beirut", nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))

    memberships: Mapped[list["ClinicMembership"]] = relationship(back_populates="clinic")


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    memberships: Mapped[list["ClinicMembership"]] = relationship(back_populates="user")


class ClinicMembership(IdMixin, TimestampMixin, Base):
    __tablename__ = "clinic_memberships"
    __table_args__ = (UniqueConstraint("clinic_id", "user_id", name="uq_membership_clinic_user"),)

    clinic_id: Mapped[str] = mapped_column(String(36), ForeignKey("clinics.id"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False), nullable=False)

    clinic: Mapped[Clinic] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship(back_populates="memberships")


class Patient(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "patients"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    normalized_phone: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    preferred_language: Mapped[PreferredLanguage] = mapped_column(
        Enum(PreferredLanguage, native_enum=False), default=PreferredLanguage.ENGLISH, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    no_show_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicate_of_patient_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("patients.id"))


class PatientNote(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "patient_notes"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True, nullable=False)
    author_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Doctor(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "doctors"

    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Service(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "services"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    requires_follow_up: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    follow_up_days: Mapped[int | None] = mapped_column(Integer)


class DoctorService(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "doctor_services"
    __table_args__ = (UniqueConstraint("doctor_id", "service_id", name="uq_doctor_service"),)

    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("doctors.id"), index=True, nullable=False)
    service_id: Mapped[str] = mapped_column(String(36), ForeignKey("services.id"), index=True, nullable=False)


class WorkingHour(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "working_hours"

    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("doctors.id"), index=True, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)


class BlockedTime(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "blocked_times"

    doctor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("doctors.id"))
    starts_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)


class AppointmentSeries(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "appointment_series"

    recurrence_rule: Mapped[str] = mapped_column(String(255), nullable=False)
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date | None] = mapped_column(Date)


class Appointment(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "appointments"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True, nullable=False)
    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("doctors.id"), index=True, nullable=False)
    service_id: Mapped[str] = mapped_column(String(36), ForeignKey("services.id"), index=True, nullable=False)
    series_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointment_series.id"))
    package_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("packages.id"))
    starts_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, native_enum=False), default=AppointmentStatus.UNCONFIRMED, index=True, nullable=False
    )
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    patient: Mapped[Patient] = relationship()
    doctor: Mapped[Doctor] = relationship()
    service: Mapped[Service] = relationship()


class AppointmentStatusHistory(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "appointment_status_history"

    appointment_id: Mapped[str] = mapped_column(String(36), ForeignKey("appointments.id"), index=True, nullable=False)
    from_status: Mapped[AppointmentStatus | None] = mapped_column(Enum(AppointmentStatus, native_enum=False))
    to_status: Mapped[AppointmentStatus] = mapped_column(Enum(AppointmentStatus, native_enum=False), nullable=False)
    changed_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    reason: Mapped[str | None] = mapped_column(Text)


class MessageThread(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "message_threads"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True, nullable=False)
    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointments.id"), index=True)
    channel: Mapped[str] = mapped_column(String(50), default="whatsapp", nullable=False)
    subject: Mapped[str | None] = mapped_column(String(255))


class Message(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    thread_id: Mapped[str] = mapped_column(String(36), ForeignKey("message_threads.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True, nullable=False)
    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointments.id"), index=True)
    direction: Mapped[MessageDirection] = mapped_column(Enum(MessageDirection, native_enum=False), nullable=False)
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus, native_enum=False), default=MessageStatus.DRAFT, index=True, nullable=False
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(255))
    intent: Mapped[Intent | None] = mapped_column(Enum(Intent, native_enum=False))
    confidence: Mapped[float | None] = mapped_column(Float)


class MessageTemplate(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "message_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[PreferredLanguage] = mapped_column(Enum(PreferredLanguage, native_enum=False), nullable=False)
    purpose: Mapped[str] = mapped_column(String(80), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class MessageDeliveryEvent(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "message_delivery_events"

    message_id: Mapped[str] = mapped_column(String(36), ForeignKey("messages.id"), index=True, nullable=False)
    status: Mapped[MessageStatus] = mapped_column(Enum(MessageStatus, native_enum=False), nullable=False)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)


class InboxItem(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "inbox_items"

    thread_id: Mapped[str] = mapped_column(String(36), ForeignKey("message_threads.id"), index=True, nullable=False)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True, nullable=False)
    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointments.id"), index=True)
    inbound_message_id: Mapped[str] = mapped_column(String(36), ForeignKey("messages.id"), nullable=False)
    status: Mapped[InboxStatus] = mapped_column(Enum(InboxStatus, native_enum=False), default=InboxStatus.OPEN, nullable=False)
    detected_intent: Mapped[Intent] = mapped_column(Enum(Intent, native_enum=False), default=Intent.UNKNOWN, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    suggested_action: Mapped[str] = mapped_column(String(255), nullable=False)
    suggested_reply: Mapped[str] = mapped_column(Text, nullable=False)
    assigned_to_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))


class FollowUpRule(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "follow_up_rules"

    service_id: Mapped[str] = mapped_column(String(36), ForeignKey("services.id"), index=True, nullable=False)
    days_after_visit: Mapped[int] = mapped_column(Integer, nullable=False)
    message_template_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("message_templates.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class FollowUpTask(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "follow_up_tasks"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True, nullable=False)
    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointments.id"), index=True)
    service_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("services.id"))
    due_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, native_enum=False), default=TaskStatus.OPEN, nullable=False)
    suggested_message: Mapped[str | None] = mapped_column(Text)


class RecoveryOpportunity(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "recovery_opportunities"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True, nullable=False)
    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointments.id"), index=True)
    type: Mapped[RecoveryType] = mapped_column(Enum(RecoveryType, native_enum=False), index=True, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, native_enum=False), default=TaskStatus.OPEN, nullable=False)
    estimated_value_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    suggested_action: Mapped[str] = mapped_column(String(255), nullable=False)
    suggested_message: Mapped[str | None] = mapped_column(Text)


class WaitlistEntry(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "waitlist_entries"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True, nullable=False)
    service_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("services.id"), index=True)
    doctor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("doctors.id"), index=True)
    preferred_from: Mapped[datetime | None] = mapped_column(DateTime)
    preferred_to: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, native_enum=False), default=TaskStatus.OPEN, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class SlotOpportunity(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "slot_opportunities"

    appointment_id: Mapped[str] = mapped_column(String(36), ForeignKey("appointments.id"), index=True, nullable=False)
    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("doctors.id"), index=True, nullable=False)
    service_id: Mapped[str] = mapped_column(String(36), ForeignKey("services.id"), index=True, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    candidate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus, native_enum=False), default=TaskStatus.OPEN, nullable=False)


class Package(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "packages"

    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True, nullable=False)
    service_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("services.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    remaining_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    next_session_due: Mapped[date | None] = mapped_column(Date)


class PackageSession(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "package_sessions"

    package_id: Mapped[str] = mapped_column(String(36), ForeignKey("packages.id"), index=True, nullable=False)
    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointments.id"))
    session_number: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)


class VisitRecord(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "visit_records"

    appointment_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("appointments.id"), index=True)
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), index=True, nullable=False)
    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("doctors.id"), index=True, nullable=False)
    service_id: Mapped[str] = mapped_column(String(36), ForeignKey("services.id"), index=True, nullable=False)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason_for_visit: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    treatment_done: Mapped[str | None] = mapped_column(Text)
    follow_up_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    follow_up_date: Mapped[date | None] = mapped_column(Date)
    private_notes: Mapped[str | None] = mapped_column(Text)


class Event(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "events"

    event_type: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(80), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime)


class AuditLog(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(36))
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)


class ClinicSetting(IdMixin, TenantMixin, TimestampMixin, Base):
    __tablename__ = "clinic_settings"
    __table_args__ = (UniqueConstraint("clinic_id", "key", name="uq_clinic_setting_key"),)

    key: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

