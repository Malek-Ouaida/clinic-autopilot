# Clinic Autopilot

Clinic Autopilot is a premium AI operations system for private clinics.

This repo contains:

- Next.js frontend in `src/`
- FastAPI backend in `backend/app/`
- PostgreSQL and Redis local services through Docker Compose
- SQLAlchemy 2.0 models and Alembic migrations
- Event-driven backend workflows for appointments, reminders, inbox, recovery, follow-ups, waitlists, packages, visits, dashboard, and analytics

## Frontend

```bash
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

## Backend Install

From the repo root:

```bash
python3.11 -m venv backend/.venv
backend/.venv/bin/pip install -e "backend[dev]"
cp .env.example .env
```

If Python 3.11 is installed as `python3`, use `python3 -m venv backend/.venv`.

## Environment

`.env.example` contains the local defaults:

```bash
APP_NAME=Clinic Autopilot API
ENVIRONMENT=local
SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=postgresql+psycopg://clinic:clinic@localhost:5432/clinic_autopilot
REDIS_URL=redis://localhost:6379/0
BACKEND_CORS_ORIGINS=http://localhost:3000
```

For SQLite smoke tests, override `DATABASE_URL`, for example:

```bash
DATABASE_URL=sqlite:////tmp/clinic_autopilot.db
```

## Database

Start Postgres and Redis:

```bash
docker compose up -d
```

Run migrations:

```bash
backend/.venv/bin/alembic upgrade head
```

Seed demo data:

```bash
backend/.venv/bin/python scripts/seed.py
```

## Run Backend

```bash
cd backend
DATABASE_URL=postgresql+psycopg://clinic:clinic@localhost:5432/clinic_autopilot \
  .venv/bin/uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

OpenAPI:

```bash
curl http://127.0.0.1:8000/openapi.json
```

## Demo Login

After running the seed script:

- Owner: `owner@karimclinic.com` / `password123`
- Secretary: `secretary@karimclinic.com` / `password123`

## Backend Tests

```bash
cd backend
.venv/bin/pytest
```

The pytest suite uses an in-memory SQLite database so it can run without Docker.

## Core API

- `POST /api/v1/auth/register-owner`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/dashboard/today`
- `GET|POST /api/v1/patients`
- `GET|PATCH /api/v1/patients/{id}`
- `POST /api/v1/patients/{id}/merge`
- `GET|POST /api/v1/doctors`
- `GET|POST /api/v1/services`
- `GET|POST /api/v1/appointments`
- `GET|PATCH /api/v1/appointments/{id}`
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
- `GET|PATCH /api/v1/inbox/{id}`
- `POST /api/v1/inbox/{id}/resolve`
- `GET /api/v1/follow-ups`
- `POST /api/v1/follow-ups/{id}/approve`
- `POST /api/v1/follow-ups/{id}/skip`
- `GET /api/v1/recovery`
- `POST /api/v1/recovery/{id}/approve-message`
- `POST /api/v1/recovery/{id}/mark-recovered`
- `GET|POST /api/v1/waitlist`
- `GET /api/v1/slot-opportunities`
- `POST /api/v1/slot-opportunities/{id}/offer`
- `GET|POST /api/v1/packages`
- `POST /api/v1/packages/{id}/complete-session`
- `GET|POST /api/v1/visits`
- `GET /api/v1/analytics/summary`
- `GET|PATCH /api/v1/settings`

## Known Limitations

- Background jobs are synchronous service calls in v1. `backend/app/workers/jobs.py` is the Redis-ready boundary for async workers.
- The WhatsApp provider is intentionally a placeholder. The mock provider is functional and used by tests.
- Doctor-specific self-schedule restrictions are basic; deeper doctor/user ownership policies should be added before production.
