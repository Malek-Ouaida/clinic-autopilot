from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import (
    Appointment,
    AppointmentStatusHistory,
    BlockedTime,
    Clinic,
    ClinicMembership,
    Event,
    MessageDeliveryEvent,
    RecoveryOpportunity,
    Role,
    TaskStatus,
    User,
    VisitRecord,
    WorkingHour,
)
from app.core.security import hash_password
from app.tests.conftest import auth_headers, seed_core


def create_appointment(client: TestClient, headers: dict[str, str], core: dict[str, str], start: datetime | None = None):
    start = start or datetime(2026, 5, 8, 10, 0, 0)
    response = client.post(
        "/api/v1/appointments",
        headers=headers,
        json={
            "patient_id": core["patient_id"],
            "doctor_id": core["doctor_id"],
            "service_id": core["service_id"],
            "starts_at": start.isoformat(),
            "ends_at": (start + timedelta(minutes=30)).isoformat(),
            "status": "unconfirmed",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_auth_login(client: TestClient):
    auth_headers(client)
    response = client.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {response.json()['access_token']}"})
    assert me.status_code == 200
    assert me.json()["role"] == "owner_admin"
    assert client.get("/api/v1/patients").status_code == 401
    assert client.get("/api/v1/patients", headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_role_enforcement_for_assistant(client: TestClient, db_session):
    owner_headers = auth_headers(client)
    me = client.get("/api/v1/auth/me", headers=owner_headers).json()
    user = User(
        email="assistant@example.com",
        full_name="Assistant User",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.flush()
    db_session.add(ClinicMembership(clinic_id=me["clinic_id"], user_id=user.id, role=Role.ASSISTANT))
    db_session.commit()
    token = client.post(
        "/api/v1/auth/login",
        json={"email": "assistant@example.com", "password": "password123"},
    ).json()["access_token"]
    assistant_headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/patients", headers=assistant_headers).status_code == 200
    assert (
        client.post(
            "/api/v1/patients",
            headers=assistant_headers,
            json={"name": "Lea Khoury", "normalized_phone": "+96170111110", "preferred_language": "english"},
        ).status_code
        == 403
    )


def test_tenant_isolation(client: TestClient):
    headers_one = auth_headers(client, "one@example.com", "Clinic One")
    headers_two = auth_headers(client, "two@example.com", "Clinic Two")
    patient = client.post(
        "/api/v1/patients",
        headers=headers_one,
        json={"name": "Maya Haddad", "normalized_phone": "+96170000001", "preferred_language": "english"},
    ).json()
    response = client.get(f"/api/v1/patients/{patient['id']}", headers=headers_two)
    assert response.status_code == 404


def test_patient_flow_search_update_duplicate_merge(client: TestClient):
    headers = auth_headers(client)
    first = client.post(
        "/api/v1/patients",
        headers=headers,
        json={"name": "Maya Haddad", "normalized_phone": "+96170000001", "preferred_language": "english"},
    ).json()
    duplicate = client.post(
        "/api/v1/patients",
        headers=headers,
        json={"name": "Maya H.", "normalized_phone": "+96170000001", "preferred_language": "arabic"},
    ).json()
    assert duplicate["duplicate_of_patient_id"] == first["id"]
    search = client.get("/api/v1/patients?q=Maya", headers=headers).json()
    assert len(search) == 2
    updated = client.patch(f"/api/v1/patients/{first['id']}", headers=headers, json={"notes": "VIP patient"}).json()
    assert updated["notes"] == "VIP patient"
    merge = client.post(
        f"/api/v1/patients/{first['id']}/merge",
        headers=headers,
        json={"duplicate_patient_id": duplicate["id"]},
    )
    assert merge.status_code == 200


def test_create_appointment_drafts_reminder(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    create_appointment(client, headers, core)
    messages = client.get("/api/v1/messages", headers=headers).json()
    assert len(messages) == 1
    assert messages[0]["status"] == "draft"


def test_appointment_confirm_creates_status_history_event_and_dashboard(client: TestClient, db_session):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    appointment = create_appointment(client, headers, core, datetime.now().replace(hour=11, minute=0, second=0, microsecond=0))
    response = client.post(f"/api/v1/appointments/{appointment['id']}/confirm", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
    histories = list(
        db_session.scalars(
            select(AppointmentStatusHistory).where(AppointmentStatusHistory.appointment_id == appointment["id"])
        )
    )
    assert [item.to_status.value for item in histories] == ["unconfirmed", "confirmed"]
    assert db_session.scalar(select(Event).where(Event.event_type == "AppointmentConfirmed"))
    dashboard = client.get("/api/v1/dashboard/today", headers=headers).json()
    assert dashboard["metrics"]["confirmed"] == 1


def test_appointment_conflict_and_blocked_time_are_rejected(client: TestClient, db_session):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    start = datetime(2026, 5, 8, 10, 0, 0)
    create_appointment(client, headers, core, start)
    conflict = client.post(
        "/api/v1/appointments",
        headers=headers,
        json={
            "patient_id": core["patient_id"],
            "doctor_id": core["doctor_id"],
            "service_id": core["service_id"],
            "starts_at": (start + timedelta(minutes=10)).isoformat(),
            "ends_at": (start + timedelta(minutes=40)).isoformat(),
            "status": "unconfirmed",
        },
    )
    assert conflict.status_code == 409
    db_session.add(
        BlockedTime(
            clinic_id=client.get("/api/v1/auth/me", headers=headers).json()["clinic_id"],
            doctor_id=core["doctor_id"],
            starts_at=start + timedelta(hours=2),
            ends_at=start + timedelta(hours=3),
            reason="Lunch",
        )
    )
    db_session.commit()
    blocked = client.post(
        "/api/v1/appointments",
        headers=headers,
        json={
            "patient_id": core["patient_id"],
            "doctor_id": core["doctor_id"],
            "service_id": core["service_id"],
            "starts_at": (start + timedelta(hours=2, minutes=10)).isoformat(),
            "ends_at": (start + timedelta(hours=2, minutes=40)).isoformat(),
            "status": "unconfirmed",
        },
    )
    assert blocked.status_code == 409


def test_doctor_working_hours_are_enforced(client: TestClient, db_session):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    clinic_id = client.get("/api/v1/auth/me", headers=headers).json()["clinic_id"]
    db_session.add(
        WorkingHour(
            clinic_id=clinic_id,
            doctor_id=core["doctor_id"],
            day_of_week=0,
            start_time=datetime(2027, 1, 4, 9, 0).time(),
            end_time=datetime(2027, 1, 4, 17, 0).time(),
        )
    )
    db_session.commit()
    outside = client.post(
        "/api/v1/appointments",
        headers=headers,
        json={
            "patient_id": core["patient_id"],
            "doctor_id": core["doctor_id"],
            "service_id": core["service_id"],
            "starts_at": datetime(2027, 1, 4, 18, 0).isoformat(),
            "ends_at": datetime(2027, 1, 4, 18, 30).isoformat(),
            "status": "unconfirmed",
        },
    )
    assert outside.status_code == 409
    inside = client.post(
        "/api/v1/appointments",
        headers=headers,
        json={
            "patient_id": core["patient_id"],
            "doctor_id": core["doctor_id"],
            "service_id": core["service_id"],
            "starts_at": datetime(2027, 1, 4, 10, 0).isoformat(),
            "ends_at": datetime(2027, 1, 4, 10, 30).isoformat(),
            "status": "unconfirmed",
        },
    )
    assert inside.status_code == 200


def test_cancel_appointment_creates_slot_opportunity(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    appointment = create_appointment(client, headers, core)
    response = client.post(f"/api/v1/appointments/{appointment['id']}/cancel", headers=headers, json={"reason": "Patient cancelled"})
    assert response.status_code == 200
    slots = client.get("/api/v1/slot-opportunities", headers=headers).json()
    assert len(slots) == 1
    assert slots[0]["appointment_id"] == appointment["id"]


def test_waitlist_candidate_count_and_slot_offer(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    client.post("/api/v1/waitlist", headers=headers, json={"patient_id": core["patient_id"], "service_id": core["service_id"], "doctor_id": core["doctor_id"]})
    appointment = create_appointment(client, headers, core)
    client.post(f"/api/v1/appointments/{appointment['id']}/cancel", headers=headers, json={"reason": "Patient cancelled"})
    slot = client.get("/api/v1/slot-opportunities", headers=headers).json()[0]
    assert slot["candidate_count"] == 1
    offered = client.post(f"/api/v1/slot-opportunities/{slot['id']}/offer", headers=headers)
    assert offered.status_code == 200
    assert offered.json()["status"] == "approved"


def test_no_show_creates_recovery_opportunity(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    appointment = create_appointment(client, headers, core)
    response = client.post(f"/api/v1/appointments/{appointment['id']}/no-show", headers=headers)
    assert response.status_code == 200
    opportunities = client.get("/api/v1/recovery", headers=headers).json()
    assert len(opportunities) == 1
    assert opportunities[0]["type"] == "missed_not_rescheduled"
    messages = client.get("/api/v1/messages", headers=headers).json()
    assert len(messages) == 2


def test_complete_appointment_creates_followup_task(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    appointment = create_appointment(client, headers, core)
    response = client.post(
        f"/api/v1/appointments/{appointment['id']}/complete",
        headers=headers,
        json={"follow_up_required": True, "notes": "Completed visit"},
    )
    assert response.status_code == 200
    followups = client.get("/api/v1/follow-ups", headers=headers).json()
    assert len(followups) == 1
    assert followups[0]["status"] == "open"


def test_followup_approve_and_skip(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    appointment = create_appointment(client, headers, core)
    client.post(
        f"/api/v1/appointments/{appointment['id']}/complete",
        headers=headers,
        json={"follow_up_required": True, "notes": "Completed visit"},
    )
    task = client.get("/api/v1/follow-ups", headers=headers).json()[0]
    assert client.post(f"/api/v1/follow-ups/{task['id']}/approve", headers=headers).json()["status"] == "approved"
    assert client.post(f"/api/v1/follow-ups/{task['id']}/skip", headers=headers).json()["status"] == "skipped"


def test_inbound_mock_reply_creates_inbox_item(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    appointment = create_appointment(client, headers, core)
    response = client.post(
        "/api/v1/messages/mock-reply",
        headers=headers,
        json={
            "patient_id": core["patient_id"],
            "appointment_id": appointment["id"],
            "body": "ma fine eje lyom, fine bukra?",
        },
    )
    assert response.status_code == 200
    inbox = client.get("/api/v1/inbox", headers=headers).json()
    assert len(inbox) == 1
    assert inbox[0]["detected_intent"] == "reschedule"
    assert client.post(f"/api/v1/inbox/{inbox[0]['id']}/resolve", headers=headers).json()["status"] == "resolved"


def test_message_lifecycle_delivery_events(client: TestClient, db_session):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    draft = client.post(
        "/api/v1/messages/draft",
        headers=headers,
        json={"patient_id": core["patient_id"], "body": "Please confirm your appointment."},
    ).json()
    assert client.post(f"/api/v1/messages/{draft['id']}/approve", headers=headers).json()["status"] == "queued"
    sent = client.post(f"/api/v1/messages/{draft['id']}/send", headers=headers).json()
    assert sent["status"] == "delivered"
    delivery_events = list(
        db_session.scalars(select(MessageDeliveryEvent).where(MessageDeliveryEvent.message_id == draft["id"]))
    )
    assert [event.status.value for event in delivery_events] == ["sent", "delivered"]


def test_package_session_completion_updates_remaining_sessions(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    package = client.post(
        "/api/v1/packages",
        headers=headers,
        json={"patient_id": core["patient_id"], "service_id": core["service_id"], "name": "Laser Package", "total_sessions": 10, "completed_sessions": 6},
    ).json()
    response = client.post(f"/api/v1/packages/{package['id']}/complete-session", headers=headers)
    assert response.status_code == 200
    assert response.json()["completed_sessions"] == 7
    assert response.json()["remaining_sessions"] == 3


def test_package_low_session_completion_creates_recovery(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    package = client.post(
        "/api/v1/packages",
        headers=headers,
        json={"patient_id": core["patient_id"], "service_id": core["service_id"], "name": "Laser Package", "total_sessions": 2, "completed_sessions": 0},
    ).json()
    client.post(f"/api/v1/packages/{package['id']}/complete-session", headers=headers)
    response = client.post(f"/api/v1/packages/{package['id']}/complete-session", headers=headers)
    assert response.json()["remaining_sessions"] == 0
    opportunities = client.get("/api/v1/recovery", headers=headers).json()
    assert any(item["type"] == "package_incomplete" for item in opportunities)


def test_recovery_approval_mark_recovered_updates_analytics(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    appointment = create_appointment(client, headers, core)
    client.post(f"/api/v1/appointments/{appointment['id']}/no-show", headers=headers)
    opportunity = client.get("/api/v1/recovery", headers=headers).json()[0]
    assert client.post(f"/api/v1/recovery/{opportunity['id']}/approve-message", headers=headers).json()["status"] == "approved"
    assert client.post(f"/api/v1/recovery/{opportunity['id']}/mark-recovered", headers=headers).json()["status"] == "completed"
    analytics = client.get("/api/v1/analytics/summary", headers=headers).json()
    assert analytics["patients_recovered"] == 1
    assert analytics["estimated_revenue_recovered"] == 50


def test_visit_records_and_tenant_isolation(client: TestClient, db_session):
    headers_one = auth_headers(client, "visit-one@example.com", "Clinic One")
    headers_two = auth_headers(client, "visit-two@example.com", "Clinic Two")
    core = seed_core(client, headers_one)
    visit = client.post(
        "/api/v1/visits",
        headers=headers_one,
        json={
            "patient_id": core["patient_id"],
            "doctor_id": core["doctor_id"],
            "service_id": core["service_id"],
            "visit_date": "2026-05-09",
            "reason_for_visit": "Consultation",
            "notes": "Light record",
        },
    )
    assert visit.status_code == 200
    assert len(client.get("/api/v1/visits", headers=headers_one).json()) == 1
    assert len(client.get("/api/v1/visits", headers=headers_two).json()) == 0
    assert db_session.scalar(select(VisitRecord).where(VisitRecord.id == visit.json()["id"]))


def test_dashboard_today_returns_expected_structure(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    create_appointment(client, headers, core, datetime.now().replace(hour=10, minute=0, second=0, microsecond=0))
    response = client.get("/api/v1/dashboard/today", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["briefing"]["status"] in {"clinic_under_control", "attention_needed"}
    assert isinstance(data["clinic_pulse"], list)
    assert len(data["clinic_pulse"]) == 6
    for key in [
        "appointments_today",
        "confirmed",
        "not_confirmed",
        "high_risk_no_shows",
        "follow_ups_due",
        "patients_to_recover",
        "messages_ready",
        "revenue_at_risk",
        "priority_stack",
        "clinic_pulse",
        "live_clinic_flow",
        "impact_this_month",
    ]:
        assert key in data
    for key in [
        "appointments_today",
        "confirmed",
        "not_confirmed",
        "high_risk_no_shows",
        "follow_ups_due",
        "patients_to_recover",
        "messages_ready",
        "revenue_at_risk",
    ]:
        assert key in data["metrics"]


def test_openapi_registers_required_routes(client: TestClient):
    paths = client.get("/openapi.json").json()["paths"]
    expected = [
        "/api/v1/auth/register-owner",
        "/api/v1/auth/login",
        "/api/v1/auth/me",
        "/api/v1/dashboard/today",
        "/api/v1/patients",
        "/api/v1/patients/{patient_id}",
        "/api/v1/patients/{patient_id}/merge",
        "/api/v1/doctors",
        "/api/v1/services",
        "/api/v1/appointments",
        "/api/v1/appointments/{appointment_id}",
        "/api/v1/appointments/{appointment_id}/confirm",
        "/api/v1/appointments/{appointment_id}/cancel",
        "/api/v1/appointments/{appointment_id}/reschedule",
        "/api/v1/appointments/{appointment_id}/complete",
        "/api/v1/appointments/{appointment_id}/no-show",
        "/api/v1/messages",
        "/api/v1/messages/draft",
        "/api/v1/messages/{message_id}/approve",
        "/api/v1/messages/{message_id}/send",
        "/api/v1/messages/mock-reply",
        "/api/v1/inbox",
        "/api/v1/inbox/{inbox_id}",
        "/api/v1/inbox/{inbox_id}/resolve",
        "/api/v1/follow-ups",
        "/api/v1/recovery",
        "/api/v1/waitlist",
        "/api/v1/slot-opportunities",
        "/api/v1/packages",
        "/api/v1/packages/{package_id}/complete-session",
        "/api/v1/visits",
        "/api/v1/analytics/summary",
        "/api/v1/settings",
    ]
    for path in expected:
        assert path in paths
