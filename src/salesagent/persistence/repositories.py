"""Repository helpers for M0: conversation lookup and per-conversation row lock (R-016)."""

from django.db import transaction

from salesagent.persistence.models import Conversation


def get_or_create_conversation(contact_key: str, contact_ref: str, m0_test: bool) -> Conversation:
    conversation, _ = Conversation.objects.get_or_create(
        contact_key=contact_key,
        defaults={"contact_ref": contact_ref, "m0_test": m0_test},
    )
    return conversation


def lock_conversation(conversation_id) -> Conversation:
    """Return the conversation with a row lock held until the surrounding transaction ends.

    Must be called inside transaction.atomic().
    """
    if not transaction.get_connection().in_atomic_block:
        raise RuntimeError("lock_conversation must run inside transaction.atomic()")
    return Conversation.objects.select_for_update().get(pk=conversation_id)
