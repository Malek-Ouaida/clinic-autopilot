from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Job:
    name: str
    payload: dict[str, Any]


class JobQueue:
    """Redis-ready job boundary. V1 runs workflows synchronously, later workers can enqueue here."""

    def enqueue(self, name: str, payload: dict[str, Any]) -> Job:
        return Job(name=name, payload=payload)

