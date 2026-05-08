from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import Message


class MessagingProvider(ABC):
    @abstractmethod
    def send(self, message: Message) -> str:
        raise NotImplementedError

