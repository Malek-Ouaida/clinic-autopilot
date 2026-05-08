from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import get_db
from app.main import app
from app.models import Base


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def auth_headers(client: TestClient, email: str = "owner@example.com", clinic: str = "Test Clinic") -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register-owner",
        json={"clinic_name": clinic, "full_name": "Dr. Owner", "email": email, "password": "password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def seed_core(client: TestClient, headers: dict[str, str]) -> dict[str, str]:
    doctor = client.post("/api/v1/doctors", headers=headers, json={"name": "Dr. Karim", "specialty": "Dental"}).json()
    service = client.post(
        "/api/v1/services",
        headers=headers,
        json={"name": "Consultation", "duration_minutes": 30, "price_cents": 5000},
    ).json()
    patient = client.post(
        "/api/v1/patients",
        headers=headers,
        json={
            "name": "Rami Khoury",
            "normalized_phone": "+96170123456",
            "preferred_language": "arabizi",
        },
    ).json()
    return {"doctor_id": doctor["id"], "service_id": service["id"], "patient_id": patient["id"]}
