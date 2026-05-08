from __future__ import annotations

from app.models import Intent


def detect_intent(text: str) -> tuple[Intent, float]:
    value = text.lower().strip()
    confirm_terms = ["yes", "confirm", "confirmed", "oui", "eh", "ok", "tamem", "أكيد"]
    cancel_terms = ["cancel", "ma fine eje", "can't come", "cant come", "لا أستطيع", "annuler"]
    reschedule_terms = [
        "baddi ghayer",
        "fine bukra",
        "can we move",
        "move it",
        "reschedule",
        "reporter",
        "je veux reporter",
        "ghayer",
        "bukra",
    ]
    question_terms = ["?", "when", "what time", "combien", "wen", "where", "price"]

    if any(term in value for term in reschedule_terms):
        return Intent.RESCHEDULE, 0.94
    if any(term in value for term in cancel_terms):
        return Intent.CANCEL, 0.9
    if any(term == value or term in value for term in confirm_terms):
        return Intent.CONFIRM, 0.88
    if any(term in value for term in question_terms):
        return Intent.QUESTION, 0.72
    return Intent.UNKNOWN, 0.35


def suggested_action(intent: Intent) -> tuple[str, str]:
    if intent == Intent.CONFIRM:
        return "Mark appointment confirmed", "Perfect, your appointment is confirmed. See you soon."
    if intent == Intent.CANCEL:
        return "Cancel appointment and open slot recovery", "No problem. Should we help you find another time?"
    if intent == Intent.RESCHEDULE:
        return (
            "Offer tomorrow's available slots",
            "Sure, we have openings tomorrow at 11:00 AM or 3:30 PM. Which works better?",
        )
    if intent == Intent.QUESTION:
        return "Assign to secretary", "Thanks for your message. The clinic team will reply shortly."
    return "Review manually", "Thanks for the message. The clinic team will follow up."

