"""T014: logs never contain phone numbers, emails, secrets, or message bodies (R-018, Principle VI)."""

import io
import logging

from salesagent.logging.masking import RedactingFilter, hmac_identifier, mask_identifier, redact_text
from salesagent.logging.setup import JsonFormatter


def _capture(messages, secrets):
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RedactingFilter(lambda: secrets))
    logger = logging.getLogger("salesagent.test_masking")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for message in messages:
        logger.info(message)
    return stream.getvalue()


def test_phone_email_and_secret_are_redacted():
    out = _capture(
        ["contact +506 8888 1234 wrote to ana@example.com using token-XYZ-999"],
        secrets=["token-XYZ-999"],
    )
    assert "8888 1234" not in out
    assert "ana@example.com" not in out
    assert "token-XYZ-999" not in out
    assert "[REDACTED]" in out


def test_identifiers_are_keyed_hashes_not_plain_text():
    masked = mask_identifier("15555550100", "log-key")
    assert masked.startswith("id:")
    assert "15555550100" not in masked
    assert masked == mask_identifier("15555550100", "log-key")
    assert masked != mask_identifier("15555550100", "other-key")
    assert "15555550100" not in hmac_identifier("15555550100", "log-key")


def test_redact_text_leaves_event_names_intact():
    assert redact_text("inbound.stored", []) == "inbound.stored"
