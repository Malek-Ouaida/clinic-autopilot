from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    InboxItem,
    Message,
    MessageDeliveryEvent,
    MessageDirection,
    MessageStatus,
    MessageThread,
)
from app.providers.messaging.mock import MockMessagingProvider
from app.services.events import EventService
from app.services.intent import detect_intent, suggested_action


class MessageService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.events = EventService(db)
        self.provider = MockMessagingProvider()

    def get_or_create_thread(self, clinic_id: str, patient_id: str, appointment_id: str | None = None) -> MessageThread:
        thread = self.db.scalar(
            select(MessageThread).where(
                MessageThread.clinic_id == clinic_id,
                MessageThread.patient_id == patient_id,
                MessageThread.appointment_id == appointment_id,
            )
        )
        if thread:
            return thread
        thread = MessageThread(
            clinic_id=clinic_id,
            patient_id=patient_id,
            appointment_id=appointment_id,
            subject="Patient operations",
        )
        self.db.add(thread)
        self.db.flush()
        return thread

    def draft(
        self,
        *,
        clinic_id: str,
        patient_id: str,
        body: str,
        appointment_id: str | None = None,
        actor_user_id: str | None = None,
    ) -> Message:
        thread = self.get_or_create_thread(clinic_id, patient_id, appointment_id)
        message = Message(
            clinic_id=clinic_id,
            thread_id=thread.id,
            patient_id=patient_id,
            appointment_id=appointment_id,
            direction=MessageDirection.OUTBOUND,
            status=MessageStatus.DRAFT,
            body=body,
        )
        self.db.add(message)
        self.db.flush()
        self.events.emit(
            clinic_id=clinic_id,
            event_type="MessageDrafted",
            aggregate_type="message",
            aggregate_id=message.id,
            payload={"appointment_id": appointment_id},
            actor_user_id=actor_user_id,
        )
        return message

    def approve(self, message: Message, actor_user_id: str | None = None) -> Message:
        message.status = MessageStatus.QUEUED
        self.events.emit(
            clinic_id=message.clinic_id,
            event_type="MessageApproved",
            aggregate_type="message",
            aggregate_id=message.id,
            actor_user_id=actor_user_id,
        )
        return message

    def send(self, message: Message, actor_user_id: str | None = None) -> Message:
        message.provider_message_id = self.provider.send(message)
        message.status = MessageStatus.SENT
        self.db.add(MessageDeliveryEvent(clinic_id=message.clinic_id, message_id=message.id, status=MessageStatus.SENT))
        self.db.add(
            MessageDeliveryEvent(clinic_id=message.clinic_id, message_id=message.id, status=MessageStatus.DELIVERED)
        )
        message.status = MessageStatus.DELIVERED
        self.events.emit(
            clinic_id=message.clinic_id,
            event_type="MessageSent",
            aggregate_type="message",
            aggregate_id=message.id,
            payload={"provider_message_id": message.provider_message_id},
            actor_user_id=actor_user_id,
        )
        return message

    def mock_reply(
        self,
        *,
        clinic_id: str,
        patient_id: str,
        body: str,
        appointment_id: str | None = None,
    ) -> tuple[Message, InboxItem]:
        thread = self.get_or_create_thread(clinic_id, patient_id, appointment_id)
        intent, confidence = detect_intent(body)
        action, reply = suggested_action(intent)
        message = Message(
            clinic_id=clinic_id,
            thread_id=thread.id,
            patient_id=patient_id,
            appointment_id=appointment_id,
            direction=MessageDirection.INBOUND,
            status=MessageStatus.REPLIED,
            body=body,
            intent=intent,
            confidence=confidence,
        )
        self.db.add(message)
        self.db.flush()
        inbox_item = InboxItem(
            clinic_id=clinic_id,
            thread_id=thread.id,
            patient_id=patient_id,
            appointment_id=appointment_id,
            inbound_message_id=message.id,
            detected_intent=intent,
            confidence=confidence,
            suggested_action=action,
            suggested_reply=reply,
        )
        self.db.add(inbox_item)
        self.events.emit(
            clinic_id=clinic_id,
            event_type="MessageReplied",
            aggregate_type="message",
            aggregate_id=message.id,
            payload={"intent": intent.value, "inbox_item_id": inbox_item.id},
        )
        return message, inbox_item

