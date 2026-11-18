"""Structured JSON logging with redaction (R-018). Event names are fixed strings."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

from salesagent.logging.masking import RedactingFilter
from salesagent.settings.secrets import registered_secret_values


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
            "logger": record.name,
        }
        for key in ("reference", "outcome", "masked_contact", "error_code"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RedactingFilter(registered_secret_values))
    root = logging.getLogger("salesagent")
    root.handlers = [handler]
    root.setLevel(level)
    root.propagate = False
