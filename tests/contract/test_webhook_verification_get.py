"""T128: GET subscription challenge (contracts/whatsapp-webhook.md)."""

import pytest
from django.conf import settings
from django.test import Client


@pytest.fixture
def client():
    return Client()


def _get(client, **params):
    return client.get("/webhooks/whatsapp/", params)


def test_correct_token_returns_challenge_as_plain_text(client):
    response = _get(
        client,
        **{
            "hub.mode": "subscribe",
            "hub.verify_token": settings.WHATSAPP_VERIFY_TOKEN.get(),
            "hub.challenge": "123456",
        },
    )
    assert response.status_code == 200
    assert response.content == b"123456"
    assert response["Content-Type"].startswith("text/plain")


@pytest.mark.parametrize(
    "params",
    [
        {"hub.mode": "subscribe", "hub.verify_token": "wrong-token", "hub.challenge": "1"},
        {"hub.mode": "unsubscribe", "hub.verify_token": "test-verify-token", "hub.challenge": "1"},
        {"hub.mode": "subscribe", "hub.verify_token": "test-verify-token"},
        {},
    ],
)
def test_any_other_request_is_forbidden(client, params):
    response = _get(client, **params)
    assert response.status_code == 403
    assert b"1" != response.content
