from __future__ import annotations

from app.models import Message
from app.providers.messaging.base import MessagingProvider


class MockMessagingProvider(MessagingProvider):
    def send(self, message: Message) -> str:
        return f"mock_{message.id}"

