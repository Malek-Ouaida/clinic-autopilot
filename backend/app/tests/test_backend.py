from __future__ import annotations

from datetime import datetime, timedelta

from fastapi.testclient import TestClient

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
    response = client.post("/api/v1/auth/login", json={"email": "owner@clinic.test", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_tenant_isolation(client: TestClient):
    headers_one = auth_headers(client, "one@clinic.test", "Clinic One")
    headers_two = auth_headers(client, "two@clinic.test", "Clinic Two")
    patient = client.post(
        "/api/v1/patients",
        headers=headers_one,
        json={"name": "Maya Haddad", "normalized_phone": "+96170000001", "preferred_language": "english"},
    ).json()
    response = client.get(f"/api/v1/patients/{patient['id']}", headers=headers_two)
    assert response.status_code == 404


def test_create_appointment_drafts_reminder(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    create_appointment(client, headers, core)
    messages = client.get("/api/v1/messages", headers=headers).json()
    assert len(messages) == 1
    assert messages[0]["status"] == "draft"


def test_cancel_appointment_creates_slot_opportunity(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    appointment = create_appointment(client, headers, core)
    response = client.post(f"/api/v1/appointments/{appointment['id']}/cancel", headers=headers, json={"reason": "Patient cancelled"})
    assert response.status_code == 200
    slots = client.get("/api/v1/slot-opportunities", headers=headers).json()
    assert len(slots) == 1
    assert slots[0]["appointment_id"] == appointment["id"]


def test_no_show_creates_recovery_opportunity(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    appointment = create_appointment(client, headers, core)
    response = client.post(f"/api/v1/appointments/{appointment['id']}/no-show", headers=headers)
    assert response.status_code == 200
    opportunities = client.get("/api/v1/recovery", headers=headers).json()
    assert len(opportunities) == 1
    assert opportunities[0]["type"] == "missed_not_rescheduled"


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


def test_dashboard_today_returns_expected_structure(client: TestClient):
    headers = auth_headers(client)
    core = seed_core(client, headers)
    create_appointment(client, headers, core, datetime.now().replace(hour=10, minute=0, second=0, microsecond=0))
    response = client.get("/api/v1/dashboard/today", headers=headers)
    assert response.status_code == 200
    data = response.json()
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

