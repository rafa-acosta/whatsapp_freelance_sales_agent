"""Synthetic WhatsApp Cloud API webhook payloads. Reserved 555-01xx numbers only."""

import json


def _envelope(messages=None, statuses=None):
    value = {
        "messaging_product": "whatsapp",
        "metadata": {"display_phone_number": "15555550000", "phone_number_id": "test-phone-number-id"},
    }
    if messages is not None:
        value["messages"] = messages
    if statuses is not None:
        value["statuses"] = statuses
    return {
        "object": "whatsapp_business_account",
        "entry": [{"id": "TEST_WABA", "changes": [{"field": "messages", "value": value}]}],
    }


def text_payload(wa_id: str, message_id: str, text: str) -> dict:
    return _envelope(
        messages=[{"from": wa_id, "id": message_id, "timestamp": "1700000000", "type": "text", "text": {"body": text}}]
    )


def image_payload(wa_id: str, message_id: str) -> dict:
    return _envelope(
        messages=[{"from": wa_id, "id": message_id, "timestamp": "1700000000", "type": "image", "image": {"id": "TEST_MEDIA"}}]
    )


def status_payload(message_id: str) -> dict:
    return _envelope(statuses=[{"id": message_id, "status": "delivered", "recipient_id": "15555550100"}])


def to_bytes(payload: dict) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")
