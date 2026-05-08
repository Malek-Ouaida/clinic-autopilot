from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import (
    AppointmentStatus,
    InboxStatus,
    Intent,
    MessageDirection,
    MessageStatus,
    PreferredLanguage,
    RecoveryType,
    Role,
    TaskStatus,
)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterOwnerRequest(BaseModel):
    clinic_name: str = Field(min_length=2)
    full_name: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORMModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool


class MeOut(BaseModel):
    user: UserOut
    clinic_id: str
    clinic_name: str
    role: Role


class PatientCreate(BaseModel):
    name: str
    normalized_phone: str
    email: EmailStr | None = None
    preferred_language: PreferredLanguage = PreferredLanguage.ENGLISH
    notes: str | None = None
    status: str = "active"


class PatientUpdate(BaseModel):
    name: str | None = None
    normalized_phone: str | None = None
    email: EmailStr | None = None
    preferred_language: PreferredLanguage | None = None
    notes: str | None = None
    status: str | None = None


class PatientOut(ORMModel):
    id: str
    clinic_id: str
    name: str
    normalized_phone: str
    email: str | None
    preferred_language: PreferredLanguage
    notes: str | None
    status: str
    no_show_count: int
    duplicate_of_patient_id: str | None
    created_at: datetime


class MergePatientRequest(BaseModel):
    duplicate_patient_id: str


class DoctorCreate(BaseModel):
    name: str
    specialty: str | None = None
    user_id: str | None = None


class DoctorOut(ORMModel):
    id: str
    clinic_id: str
    name: str
    specialty: str | None
    is_active: bool


class ServiceCreate(BaseModel):
    name: str
    duration_minutes: int = 30
    price_cents: int = 0
    requires_follow_up: bool = False
    follow_up_days: int | None = None


class ServiceOut(ORMModel):
    id: str
    clinic_id: str
    name: str
    duration_minutes: int
    price_cents: int
    requires_follow_up: bool
    follow_up_days: int | None


class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    service_id: str
    starts_at: datetime
    ends_at: datetime
    status: AppointmentStatus = AppointmentStatus.UNCONFIRMED
    package_id: str | None = None


class AppointmentPatch(BaseModel):
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: AppointmentStatus | None = None
    cancellation_reason: str | None = None


class RescheduleRequest(BaseModel):
    starts_at: datetime
    ends_at: datetime


class CancelRequest(BaseModel):
    reason: str | None = None


class CompleteAppointmentRequest(BaseModel):
    reason_for_visit: str | None = None
    notes: str | None = None
    treatment_done: str | None = None
    follow_up_required: bool = False
    follow_up_date: date | None = None
    private_notes: str | None = None


class AppointmentOut(ORMModel):
    id: str
    clinic_id: str
    patient_id: str
    doctor_id: str
    service_id: str
    starts_at: datetime
    ends_at: datetime
    status: AppointmentStatus
    risk_score: float
    package_id: str | None


class MessageDraftCreate(BaseModel):
    patient_id: str
    appointment_id: str | None = None
    body: str


class MockReplyCreate(BaseModel):
    patient_id: str
    appointment_id: str | None = None
    body: str


class MessageOut(ORMModel):
    id: str
    clinic_id: str
    thread_id: str
    patient_id: str
    appointment_id: str | None
    direction: MessageDirection
    status: MessageStatus
    body: str
    intent: Intent | None
    confidence: float | None
    created_at: datetime


class InboxPatch(BaseModel):
    status: InboxStatus | None = None
    assigned_to_user_id: str | None = None


class InboxItemOut(ORMModel):
    id: str
    clinic_id: str
    patient_id: str
    appointment_id: str | None
    status: InboxStatus
    detected_intent: Intent
    confidence: float
    suggested_action: str
    suggested_reply: str
    created_at: datetime


class FollowUpTaskOut(ORMModel):
    id: str
    clinic_id: str
    patient_id: str
    appointment_id: str | None
    service_id: str | None
    due_date: date
    status: TaskStatus
    suggested_message: str | None


class RecoveryOut(ORMModel):
    id: str
    clinic_id: str
    patient_id: str
    appointment_id: str | None
    type: RecoveryType
    status: TaskStatus
    estimated_value_cents: int
    suggested_action: str
    suggested_message: str | None


class WaitlistCreate(BaseModel):
    patient_id: str
    service_id: str | None = None
    doctor_id: str | None = None
    preferred_from: datetime | None = None
    preferred_to: datetime | None = None
    notes: str | None = None


class WaitlistOut(ORMModel):
    id: str
    clinic_id: str
    patient_id: str
    service_id: str | None
    doctor_id: str | None
    status: TaskStatus


class SlotOpportunityOut(ORMModel):
    id: str
    clinic_id: str
    appointment_id: str
    doctor_id: str
    service_id: str
    starts_at: datetime
    ends_at: datetime
    candidate_count: int
    status: TaskStatus


class PackageCreate(BaseModel):
    patient_id: str
    name: str
    total_sessions: int
    service_id: str | None = None
    completed_sessions: int = 0
    next_session_due: date | None = None


class PackageOut(ORMModel):
    id: str
    clinic_id: str
    patient_id: str
    service_id: str | None
    name: str
    total_sessions: int
    completed_sessions: int
    remaining_sessions: int
    status: str
    next_session_due: date | None


class VisitCreate(BaseModel):
    appointment_id: str | None = None
    patient_id: str
    doctor_id: str
    service_id: str
    visit_date: date
    reason_for_visit: str | None = None
    notes: str | None = None
    treatment_done: str | None = None
    follow_up_required: bool = False
    follow_up_date: date | None = None
    private_notes: str | None = None


class VisitOut(ORMModel):
    id: str
    clinic_id: str
    appointment_id: str | None
    patient_id: str
    doctor_id: str
    service_id: str
    visit_date: date
    reason_for_visit: str | None
    notes: str | None
    treatment_done: str | None
    follow_up_required: bool
    follow_up_date: date | None


class SettingsPatch(BaseModel):
    value: dict[str, Any]


class SettingOut(ORMModel):
    id: str
    clinic_id: str
    key: str
    value: dict[str, Any]
