"""T013: secrets never appear in repr/str; no key-like literals in source (R-007, FR-048)."""

import re
from pathlib import Path

from salesagent.settings.secrets import SecretValue, registered_secret_values

SRC = Path(__file__).resolve().parents[2] / "src"
KEY_PATTERNS = [
    re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"),
    re.compile(r"EAA[A-Za-z0-9]{30,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def test_secret_repr_and_str_are_masked():
    secret = SecretValue("super-secret-value-123")
    assert "super-secret-value-123" not in repr(secret)
    assert "super-secret-value-123" not in str(secret)
    assert "super-secret-value-123" not in f"{secret}"
    assert secret.get() == "super-secret-value-123"


def test_registered_secrets_are_available_to_the_log_filter():
    SecretValue("registered-for-filter-test")
    assert "registered-for-filter-test" in registered_secret_values()


def test_no_key_like_literals_in_source():
    offenders = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for pattern in KEY_PATTERNS:
            if pattern.search(text):
                offenders.append(str(path))
    assert offenders == []


def test_no_region_or_provider_hardcoded_in_settings():
    text = (SRC / "salesagent" / "settings" / "base.py").read_text(encoding="utf-8")
    assert "amazonaws" not in text
    assert "us-east" not in text
