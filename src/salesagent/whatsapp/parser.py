"""Parses WhatsApp Cloud API webhook payloads (M0 subset).

Only the fields M0 needs are extracted: platform message ID, sender's WhatsApp ID, message
type, and text body for text messages. Status updates and unknown shapes produce no events.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InboundEvent:
    platform_message_id: str
    wa_id: str
    message_type: str  # "text" or "unsupported"
    text: str | None


def parse_inbound_messages(payload: object) -> list[InboundEvent]:
    events: list[InboundEvent] = []
    if not isinstance(payload, dict):
        return events
    for entry in payload.get("entry") or []:
        for change in (entry or {}).get("changes") or []:
            value = (change or {}).get("value") or {}
            for message in value.get("messages") or []:
                event = _event_from_message(message)
                if event is not None:
                    events.append(event)
    return events


def _event_from_message(message: object) -> InboundEvent | None:
    if not isinstance(message, dict):
        return None
    message_id = message.get("id")
    wa_id = message.get("from")
    if not isinstance(message_id, str) or not isinstance(wa_id, str):
        return None
    if message.get("type") == "text":
        body = (message.get("text") or {}).get("body")
        if not isinstance(body, str):
            return None
        return InboundEvent(message_id, wa_id, "text", body)
    # Images, audio, video, documents, and others: recorded, never fetched (FR-037).
    return InboundEvent(message_id, wa_id, "unsupported", None)
