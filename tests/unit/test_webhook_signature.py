"""T027: HMAC-SHA256 over the raw body, constant-time comparison (contracts/whatsapp-webhook.md)."""

from salesagent.whatsapp.signature import compute_signature, verify_signature

SECRET = "unit-test-app-secret"
BODY = b'{"entry":[]}'


def test_valid_signature_passes():
    assert verify_signature(BODY, compute_signature(BODY, SECRET), SECRET)


def test_wrong_secret_fails():
    assert not verify_signature(BODY, compute_signature(BODY, "other-secret"), SECRET)


def test_tampered_body_fails():
    assert not verify_signature(BODY + b" ", compute_signature(BODY, SECRET), SECRET)


def test_missing_header_or_prefix_fails():
    digest = compute_signature(BODY, SECRET).split("=", 1)[1]
    assert not verify_signature(BODY, None, SECRET)
    assert not verify_signature(BODY, "", SECRET)
    assert not verify_signature(BODY, digest, SECRET)


def test_missing_secret_fails_closed():
    assert not verify_signature(BODY, compute_signature(BODY, ""), "")
