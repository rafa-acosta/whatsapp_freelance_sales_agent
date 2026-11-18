"""Sends session text messages through the WhatsApp Cloud API (R-004, M0).

Uses only the standard library HTTP client, so no new dependency is added. Tests replace
`send_text`; no test makes a network call.
"""

from __future__ import annotations

import json
import urllib.request

from django.conf import settings


class SendError(RuntimeError):
    """Raised when the platform does not accept the message. The message text is not included."""


def send_text(to_wa_id: str, text: str) -> str:
    """Send a session text message and return the platform message ID."""
    url = (
        f"{settings.WHATSAPP_GRAPH_BASE_URL}/{settings.WHATSAPP_GRAPH_API_VERSION}/"
        f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    body = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_wa_id,
            "type": "text",
            "text": {"body": text},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": "Bearer " + settings.WHATSAPP_ACCESS_TOKEN.get(),
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - fixed HTTPS host from config
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - re-raised without the body or token
        raise SendError(type(exc).__name__) from None
    try:
        return data["messages"][0]["id"]
    except (KeyError, IndexError, TypeError):
        raise SendError("unexpected_response") from None
