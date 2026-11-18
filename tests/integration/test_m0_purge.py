"""T133: the M0 purge removes only M0 test rows and reports counts only."""

import io

import pytest
from django.core.management import call_command

from salesagent.persistence.models import Conversation, Message, MessageDirection


@pytest.mark.django_db
def test_purge_removes_only_m0_test_conversations():
    test_conv = Conversation.objects.create(contact_key="k-test", contact_ref="15555550100", m0_test=True)
    Message.objects.create(conversation=test_conv, direction=MessageDirection.INBOUND, platform_message_id="p-1")
    kept_conv = Conversation.objects.create(contact_key="k-kept", contact_ref="", m0_test=False)
    Message.objects.create(conversation=kept_conv, direction=MessageDirection.INBOUND, platform_message_id="p-2")

    out = io.StringIO()
    call_command("m0_purge_test_data", stdout=out)

    assert "conversations=1 messages=1" in out.getvalue()
    assert not Conversation.objects.filter(pk=test_conv.pk).exists()
    assert Conversation.objects.filter(pk=kept_conv.pk).exists()
    assert Message.objects.filter(platform_message_id="p-2").exists()
    assert "15555550100" not in out.getvalue()
