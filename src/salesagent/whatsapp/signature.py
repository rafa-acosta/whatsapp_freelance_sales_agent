"""Webhook signature verification (contracts/whatsapp-webhook.md, R-004).

The signature is HMAC-SHA256 of the raw request body, keyed with the app secret. It is
compared in constant time. The body must not be parsed before this check passes.
"""

from __future__ import annotations

import hashlib
import hmac

SIGNATURE_PREFIX = "sha256="


def compute_signature(raw_body: bytes, app_secret: str) -> str:
    digest = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return SIGNATURE_PREFIX + digest


def verify_signature(raw_body: bytes, header_value: str | None, app_secret: str) -> bool:
    if not header_value or not app_secret:
        return False
    if not header_value.startswith(SIGNATURE_PREFIX):
        return False
    expected = compute_signature(raw_body, app_secret)
    return hmac.compare_digest(expected, header_value)
