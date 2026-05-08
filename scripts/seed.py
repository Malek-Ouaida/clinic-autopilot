from __future__ import annotations

from datetime import datetime, time, timedelta

from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models import (
    Appointment,
    AppointmentStatus,
    Clinic,
    ClinicMembership,
    ClinicSetting,
    Doctor,
    DoctorService,
    FollowUpRule,
    MessageTemplate,
    Package,
    Patient,
    PreferredLanguage,
    RecoveryOpportunity,
    RecoveryType,
    Role,
    Service,
    TaskStatus,
    User,
    WaitlistEntry,
    WorkingHour,
)


def run() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(Clinic).where(Clinic.name == "Dr. Karim Dental Clinic"))
        if existing:
            print("Seed data already exists.")
            return

        clinic = Clinic(name="Dr. Karim Dental Clinic", timezone="Asia/Beirut", phone="+961 1 555 100")
        db.add(clinic)
        db.flush()

        owner = User(
            email="owner@karimclinic.com",
            full_name="Dr. Karim",
            password_hash=hash_password("password123"),
        )
        secretary = User(
            email="secretary@karimclinic.com",
            full_name="Lea Secretary",
            password_hash=hash_password("password123"),
        )
        db.add_all([owner, secretary])
        db.flush()
        db.add_all(
            [
                ClinicMembership(clinic_id=clinic.id, user_id=owner.id, role=Role.OWNER_ADMIN),
                ClinicMembership(clinic_id=clinic.id, user_id=secretary.id, role=Role.SECRETARY),
            ]
        )

        doctors = [
            Doctor(clinic_id=clinic.id, name="Dr. Karim", specialty="Dental"),
            Doctor(clinic_id=clinic.id, name="Dr. Lina", specialty="Aesthetic"),
            Doctor(clinic_id=clinic.id, name="Dr. Sara", specialty="Physio"),
        ]
        db.add_all(doctors)
        db.flush()

        services = [
            Service(clinic_id=clinic.id, name="Consultation", duration_minutes=30, price_cents=5000),
            Service(clinic_id=clinic.id, name="Cleaning", duration_minutes=45, price_cents=7000, requires_follow_up=True, follow_up_days=180),
            Service(clinic_id=clinic.id, name="Whitening", duration_minutes=60, price_cents=18000),
            Service(clinic_id=clinic.id, name="Braces follow-up", duration_minutes=30, price_cents=6000, requires_follow_up=True, follow_up_days=30),
            Service(clinic_id=clinic.id, name="Laser session", duration_minutes=40, price_cents=12000),
            Service(clinic_id=clinic.id, name="Botox follow-up", duration_minutes=20, price_cents=4000, requires_follow_up=True, follow_up_days=14),
            Service(clinic_id=clinic.id, name="Physio session", duration_minutes=50, price_cents=9000),
            Service(clinic_id=clinic.id, name="HydraFacial", duration_minutes=50, price_cents=13000),
            Service(clinic_id=clinic.id, name="Root canal", duration_minutes=90, price_cents=25000),
        ]
        db.add_all(services)
        db.flush()
        for doctor in doctors:
            for service in services[:4]:
                db.add(DoctorService(clinic_id=clinic.id, doctor_id=doctor.id, service_id=service.id))
            for dow in range(0, 5):
                db.add(
                    WorkingHour(
                        clinic_id=clinic.id,
                        doctor_id=doctor.id,
                        day_of_week=dow,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                    )
                )

        patients = [
            Patient(clinic_id=clinic.id, name="Maya Haddad", normalized_phone="+96170111111", preferred_language=PreferredLanguage.ENGLISH),
            Patient(clinic_id=clinic.id, name="Rami Khoury", normalized_phone="+96170222222", preferred_language=PreferredLanguage.ARABIZI, no_show_count=1),
            Patient(clinic_id=clinic.id, name="Nour Saad", normalized_phone="+96170333333", preferred_language=PreferredLanguage.ARABIC),
            Patient(clinic_id=clinic.id, name="Elie Mansour", normalized_phone="+96170444444", preferred_language=PreferredLanguage.FRENCH),
            Patient(clinic_id=clinic.id, name="Sara Tannous", normalized_phone="+96170555555", preferred_language=PreferredLanguage.ENGLISH),
            Patient(clinic_id=clinic.id, name="Karim Daher", normalized_phone="+96170666666", preferred_language=PreferredLanguage.ARABIZI),
            Patient(clinic_id=clinic.id, name="Lea Khoury", normalized_phone="+96170777777", preferred_language=PreferredLanguage.ENGLISH),
            Patient(clinic_id=clinic.id, name="Tarek Nassar", normalized_phone="+96170888888", preferred_language=PreferredLanguage.ARABIC),
            Patient(clinic_id=clinic.id, name="Aisha Mohamed", normalized_phone="+96170999999", preferred_language=PreferredLanguage.ENGLISH),
            Patient(clinic_id=clinic.id, name="Omar Hassan", normalized_phone="+96170000000", preferred_language=PreferredLanguage.FRENCH),
        ]
        db.add_all(patients)
        db.flush()

        now = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        appointments = [
            Appointment(clinic_id=clinic.id, patient_id=patients[0].id, doctor_id=doctors[0].id, service_id=services[1].id, starts_at=now, ends_at=now + timedelta(minutes=45), status=AppointmentStatus.CONFIRMED),
            Appointment(clinic_id=clinic.id, patient_id=patients[1].id, doctor_id=doctors[0].id, service_id=services[0].id, starts_at=now + timedelta(hours=1, minutes=30), ends_at=now + timedelta(hours=2), status=AppointmentStatus.UNCONFIRMED, risk_score=0.7),
            Appointment(clinic_id=clinic.id, patient_id=patients[2].id, doctor_id=doctors[1].id, service_id=services[5].id, starts_at=now + timedelta(hours=3), ends_at=now + timedelta(hours=3, minutes=20), status=AppointmentStatus.UNCONFIRMED, risk_score=0.82),
        ]
        db.add_all(appointments)
        db.flush()

        for service in services:
            if service.requires_follow_up:
                db.add(FollowUpRule(clinic_id=clinic.id, service_id=service.id, days_after_visit=service.follow_up_days or 30))

        templates = [
            MessageTemplate(clinic_id=clinic.id, name="Appointment reminder EN", language=PreferredLanguage.ENGLISH, purpose="reminder", body="Hi {patient_name}, your {service_name} appointment is at {appointment_time}."),
            MessageTemplate(clinic_id=clinic.id, name="Recovery Arabizi", language=PreferredLanguage.ARABIZI, purpose="recovery", body="Hi {patient_name}, baddak nle2e wa2et jdid la {service_name}?"),
            MessageTemplate(clinic_id=clinic.id, name="Follow-up FR", language=PreferredLanguage.FRENCH, purpose="follow_up", body="Bonjour {patient_name}, il est temps pour votre suivi chez {clinic_name}."),
        ]
        db.add_all(templates)

        db.add_all(
            [
                WaitlistEntry(clinic_id=clinic.id, patient_id=patients[6].id, service_id=services[0].id, doctor_id=doctors[0].id, notes="Prefers afternoon"),
                WaitlistEntry(clinic_id=clinic.id, patient_id=patients[7].id, service_id=services[0].id, doctor_id=doctors[0].id),
                Package(clinic_id=clinic.id, patient_id=patients[8].id, service_id=services[4].id, name="Laser Package", total_sessions=10, completed_sessions=6, remaining_sessions=4),
                Package(clinic_id=clinic.id, patient_id=patients[9].id, service_id=services[6].id, name="Physio Package", total_sessions=8, completed_sessions=3, remaining_sessions=5),
                RecoveryOpportunity(clinic_id=clinic.id, patient_id=patients[1].id, appointment_id=appointments[1].id, type=RecoveryType.MISSED_NOT_RESCHEDULED, estimated_value_cents=5000, suggested_action="Send recovery message", suggested_message="We missed you. Would you like to rebook?"),
                ClinicSetting(clinic_id=clinic.id, key="clinic_profile", value={"brand": "Dr. Karim Dental Clinic", "timezone": "Asia/Beirut"}),
            ]
        )
        db.commit()
        print("Seeded Dr. Karim Dental Clinic.")
        print("Owner: owner@karimclinic.com / password123")
        print("Secretary: secretary@karimclinic.com / password123")
    finally:
        db.close()


if __name__ == "__main__":
    run()

