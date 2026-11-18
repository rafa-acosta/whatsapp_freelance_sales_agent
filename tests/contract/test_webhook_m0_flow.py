"""T130: M0 end-to-end with synthetic signed payloads only.

Covers: allowlisted text answered with the fixed test response; unsigned and wrongly signed
requests rejected before parsing; non-allowlisted senders ignored; media never fetched;
send failures retried; outside M0 mode nothing is stored; the AI package is never loaded.
"""

import logging
import sys
from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client, override_settings
from django.utils import timezone

from salesagent.orchestration.worker import MAX_ATTEMPTS, process_queue
from salesagent.persistence.models import (
    Conversation,
    Message,
    MessageDirection,
    MessageSource,
    MessageType,
    QueueStatus,
    SendStatus,
)
from tests.fixtures.whatsapp.payloads import image_payload, status_payload, text_payload, to_bytes
from tests.fixtures.whatsapp.signing import sign

ALLOWED = settings.TEST_ALLOWED_WA_ID
OTHER = settings.TEST_OTHER_WA_ID
URL = "/webhooks/whatsapp/"


def _post(client, body: bytes, signature: str | None = None):
    headers = {}
    headers["HTTP_X_HUB_SIGNATURE_256"] = signature if signature is not None else sign(body)
    return client.post(URL, data=body, content_type="application/json", **headers)


@pytest.mark.django_db
def test_allowlisted_text_gets_fixed_test_response(fake_sender):
    client = Client()
    body = to_bytes(text_payload(ALLOWED, "wamid.TEST-M0-0001", "Hola, prueba"))

    response = _post(client, body)
    assert response.status_code == 200

    conversation = Conversation.objects.get()
    assert conversation.m0_test is True
    assert conversation.contact_ref == ALLOWED

    inbound = Message.objects.get(direction=MessageDirection.INBOUND)
    assert inbound.queue_status == QueueStatus.QUEUED

    assert process_queue() == 1
    assert fake_sender.calls == [(ALLOWED, settings.WHATSAPP_M0_RESPONSE_TEXT)]

    outbound = Message.objects.get(direction=MessageDirection.OUTBOUND)
    assert outbound.source == MessageSource.M0_TEST
    assert outbound.send_status == SendStatus.SENT
    assert outbound.platform_message_id.startswith("wamid.TEST")
    inbound.refresh_from_db()
    assert inbound.queue_status == QueueStatus.DONE


@pytest.mark.django_db
def test_unsigned_or_wrongly_signed_request_is_rejected_before_parsing(fake_sender):
    client = Client()
    body = to_bytes(text_payload(ALLOWED, "wamid.TEST-M0-0002", "x"))

    assert _post(client, body, signature="").status_code == 403
    assert _post(client, body, signature="sha256=" + "0" * 64).status_code == 403
    # Invalid JSON with a bad signature must still be refused: the signature is checked first.
    assert _post(client, b"not json", signature="sha256=" + "0" * 64).status_code == 403

    assert Message.objects.count() == 0
    assert Conversation.objects.count() == 0
    assert fake_sender.calls == []


@pytest.mark.django_db
def test_non_allowlisted_sender_is_neither_stored_nor_answered(fake_sender, caplog):
    caplog.set_level(logging.INFO)
    client = Client()
    body = to_bytes(text_payload(OTHER, "wamid.TEST-M0-0003", "hola"))

    assert _post(client, body).status_code == 200
    assert Conversation.objects.count() == 0
    assert Message.objects.count() == 0
    process_queue()
    assert fake_sender.calls == []
    assert OTHER not in caplog.text
    assert "m0.sender_not_allowlisted" in caplog.text


@pytest.mark.django_db
def test_message_bodies_never_reach_logs(fake_sender, caplog):
    caplog.set_level(logging.INFO)
    client = Client()
    secret_phrase = "frase-privada-del-prueba-9731"
    _post(client, to_bytes(text_payload(ALLOWED, "wamid.TEST-M0-0004", secret_phrase)))
    process_queue()
    assert secret_phrase not in caplog.text
    assert ALLOWED not in caplog.text


@pytest.mark.django_db
def test_media_is_recorded_without_fetch_or_reply(fake_sender):
    client = Client()
    _post(client, to_bytes(image_payload(ALLOWED, "wamid.TEST-M0-0005")))
    message = Message.objects.get(platform_message_id="wamid.TEST-M0-0005")
    assert message.message_type == MessageType.UNSUPPORTED_MEDIA
    assert message.body is None

    process_queue()
    assert fake_sender.calls == []
    message.refresh_from_db()
    assert message.queue_status == QueueStatus.DONE


@pytest.mark.django_db
def test_status_only_payload_creates_nothing(fake_sender):
    client = Client()
    assert _post(client, to_bytes(status_payload("wamid.OUT-1"))).status_code == 200
    assert Message.objects.count() == 0


@pytest.mark.django_db
def test_send_failure_is_retried_then_marked_failed(fake_sender):
    client = Client()
    _post(client, to_bytes(text_payload(ALLOWED, "wamid.TEST-M0-0006", "reintento")))
    fake_sender.fail_next = MAX_ATTEMPTS
    for _ in range(MAX_ATTEMPTS):
        # Make the message due again, then run one worker pass.
        Message.objects.filter(platform_message_id="wamid.TEST-M0-0006").update(
            next_attempt_at=timezone.now() - timedelta(seconds=1)
        )
        process_queue()
    message = Message.objects.get(platform_message_id="wamid.TEST-M0-0006")
    assert message.queue_status == QueueStatus.FAILED
    assert message.attempts == MAX_ATTEMPTS
    assert fake_sender.calls == []
    assert Message.objects.filter(direction=MessageDirection.OUTBOUND, send_status=SendStatus.FAILED).exists()


@pytest.mark.django_db
def test_failed_send_is_not_marked_done_and_retries_later(fake_sender):
    client = Client()
    _post(client, to_bytes(text_payload(ALLOWED, "wamid.TEST-M0-0007", "una vez")))
    fake_sender.fail_next = 1
    process_queue()
    message = Message.objects.get(platform_message_id="wamid.TEST-M0-0007")
    assert message.queue_status == QueueStatus.QUEUED
    assert message.attempts == 1
    assert message.next_attempt_at is not None


@pytest.mark.django_db
@override_settings(WHATSAPP_M0_MODE=False)
def test_nothing_is_stored_outside_m0_mode(fake_sender):
    client = Client()
    response = _post(client, to_bytes(text_payload(ALLOWED, "wamid.TEST-M0-0008", "x")))
    assert response.status_code == 200
    assert Message.objects.count() == 0


@pytest.mark.django_db
def test_ai_package_is_never_loaded_during_m0(fake_sender):
    client = Client()
    _post(client, to_bytes(text_payload(ALLOWED, "wamid.TEST-M0-0009", "hola")))
    process_queue()
    assert not any(name == "salesagent.ai" or name.startswith("salesagent.ai.") for name in sys.modules)
