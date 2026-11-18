"""PII masking for logs (R-018, Principle VI).

Identifiers are never written in plain text. They are written as a keyed HMAC so that
events can be correlated without exposing the value. Message bodies are never logged at
INFO or above; the redaction filter also removes phone-like and email-like text and any
configured secret value.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import re

_PHONE_RE = re.compile(r"\+?\d[\d\s().-]{6,}\d")
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
REDACTED = "[REDACTED]"


def hmac_identifier(value: str, key: str) -> str:
    """Keyed HMAC-SHA256 of an identifier, hex encoded. Same input and key give the same output."""
    digest = hmac.new(key.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest


def mask_identifier(value: str, key: str) -> str:
    """Short, log-friendly form of the keyed HMAC, such as 'id:3f9a1c7e2b40'."""
    return "id:" + hmac_identifier(value, key)[:12]


def redact_text(text: str, secrets: list[str]) -> str:
    for secret in secrets:
        if secret:
            text = text.replace(secret, REDACTED)
    text = _EMAIL_RE.sub(REDACTED, text)
    text = _PHONE_RE.sub(REDACTED, text)
    return text


class RedactingFilter(logging.Filter):
    """Redacts the rendered message of every record. Must be attached to the handler."""

    def __init__(self, secrets_provider):
        super().__init__()
        self._secrets_provider = secrets_provider

    def filter(self, record: logging.LogRecord) -> bool:
        rendered = record.getMessage()
        record.msg = redact_text(rendered, self._secrets_provider())
        record.args = ()
        return True
