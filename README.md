# Clinic Autopilot

Clinic Autopilot is a premium AI operations system for private clinics. This repo contains:

- A Next.js frontend in `src/`
- A FastAPI backend in `app/`
- PostgreSQL/Alembic persistence
- Event-driven service workflows for appointments, reminders, recovery, inbox, follow-ups, waitlists, packages, and analytics

## Frontend

```bash
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

## Backend

Create a virtual environment and install the API:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Start Postgres and Redis:

```bash
docker compose up -d
```

Run migrations and seed data:

```bash
alembic upgrade head
python scripts/seed.py
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

API health check: [http://localhost:8000/health](http://localhost:8000/health)

Seed users:

- Owner: `owner@karimclinic.com` / `password123`
- Secretary: `secretary@karimclinic.com` / `password123`

## Backend Checks

```bash
pytest
```

## Core API

- `POST /api/v1/auth/register-owner`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/dashboard/today`
- `GET|POST /api/v1/patients`
- `GET|POST /api/v1/doctors`
- `GET|POST /api/v1/services`
- `GET|POST /api/v1/appointments`
- `POST /api/v1/appointments/{id}/confirm`
- `POST /api/v1/appointments/{id}/cancel`
- `POST /api/v1/appointments/{id}/reschedule`
- `POST /api/v1/appointments/{id}/complete`
- `POST /api/v1/appointments/{id}/no-show`
- `GET /api/v1/messages`
- `POST /api/v1/messages/draft`
- `POST /api/v1/messages/{id}/approve`
- `POST /api/v1/messages/{id}/send`
- `POST /api/v1/messages/mock-reply`
- `GET /api/v1/inbox`
- `GET /api/v1/follow-ups`
- `GET /api/v1/recovery`
- `GET|POST /api/v1/waitlist`
- `GET /api/v1/slot-opportunities`
- `GET|POST /api/v1/packages`
- `GET|POST /api/v1/visits`
- `GET /api/v1/analytics/summary`
- `GET|PATCH /api/v1/settings`

