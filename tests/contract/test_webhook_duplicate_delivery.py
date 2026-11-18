"""T129: duplicate deliveries are stored and answered once (R-016, FR-031)."""

import pytest
from django.test import Client

from salesagent.persistence.models import Message, MessageDirection, QueueStatus
from salesagent.orchestration.worker import process_queue
from tests.fixtures.whatsapp.payloads import text_payload, to_bytes
from tests.fixtures.whatsapp.signing import sign

WA_ID = "15555550100"
MSG_ID = "wamid.TEST-DUP-0001"


@pytest.mark.django_db
def test_redelivered_message_is_stored_and_answered_once(fake_sender):
    client = Client()
    body = to_bytes(text_payload(WA_ID, MSG_ID, "prueba"))
    headers = {"HTTP_X_HUB_SIGNATURE_256": sign(body)}

    first = client.post("/webhooks/whatsapp/", data=body, content_type="application/json", **headers)
    second = client.post("/webhooks/whatsapp/", data=body, content_type="application/json", **headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert Message.objects.filter(platform_message_id=MSG_ID).count() == 1
    assert Message.objects.filter(direction=MessageDirection.INBOUND).count() == 1

    process_queue()
    process_queue()
    assert len(fake_sender.calls) == 1
    assert Message.objects.get(platform_message_id=MSG_ID).queue_status == QueueStatus.DONE
