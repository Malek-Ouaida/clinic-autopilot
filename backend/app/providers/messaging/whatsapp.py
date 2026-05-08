from __future__ import annotations

from app.models import Message
from app.providers.messaging.base import MessagingProvider


class WhatsAppMessagingProvider(MessagingProvider):
    def send(self, message: Message) -> str:
        raise NotImplementedError("WhatsApp provider is intentionally wired as a v2 integration boundary.")

