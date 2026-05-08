from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditLog, Event


class EventService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def emit(
        self,
        *,
        clinic_id: str,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, Any] | None = None,
        actor_user_id: str | None = None,
    ) -> Event:
        event = Event(
            clinic_id=clinic_id,
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload or {},
            processed_at=datetime.utcnow(),
        )
        self.db.add(event)
        self.db.add(
            AuditLog(
                clinic_id=clinic_id,
                actor_user_id=actor_user_id,
                action=event_type,
                entity_type=aggregate_type,
                entity_id=aggregate_id,
                metadata_json=payload or {},
            )
        )
        return event

