"""Queue worker, M0 subset (plan.md, R-016).

Consumes inbound messages from the database queue, one conversation at a time, and sends the
fixed M0 test response. The full pipeline (plan.md steps 1 to 9) replaces this later.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from salesagent.persistence.models import (
    Message,
    MessageDirection,
    MessageSource,
    MessageType,
    QueueStatus,
    SendStatus,
)
from salesagent.persistence.repositories import lock_conversation
from salesagent.whatsapp import sender
from salesagent.whatsapp.sender import SendError

log = logging.getLogger("salesagent.worker")

MAX_ATTEMPTS = 5


def process_queue(limit: int = 50) -> int:
    """Process up to `limit` due inbound messages. Returns the number handled."""
    now = timezone.now()
    due_ids = list(
        Message.objects.filter(
            direction=MessageDirection.INBOUND,
            queue_status=QueueStatus.QUEUED,
            next_attempt_at__lte=now,
        )
        .order_by("created_at")
        .values_list("id", flat=True)[:limit]
    )
    handled = 0
    for message_id in due_ids:
        handled += _process_one(message_id)
    return handled


def _process_one(message_id) -> int:
    with transaction.atomic():
        # Read the conversation id without a lock, then take the conversation lock first (R-016).
        conversation_id = Message.objects.values_list("conversation_id", flat=True).get(pk=message_id)
        conversation = lock_conversation(conversation_id)
        message = Message.objects.filter(pk=message_id, queue_status=QueueStatus.QUEUED).first()
        if message is None:
            return 0  # Another worker finished it first.

        message.queue_status = QueueStatus.PROCESSING
        message.save(update_fields=["queue_status", "updated_at"])

        if message.message_type != MessageType.TEXT:
            # Media is recorded and never fetched; no reply in M0 (FR-037).
            _finish(message)
            log.info("m0.unsupported_media_no_reply", extra={"reference": str(message.pk)})
            return 1

        if not settings.WHATSAPP_M0_MODE:
            _finish(message)
            log.info("m0.disabled_no_reply", extra={"reference": str(message.pk)})
            return 1

        outbound = Message.objects.create(
            conversation=conversation,
            direction=MessageDirection.OUTBOUND,
            source=MessageSource.M0_TEST,
            send_status=SendStatus.PENDING,
            queue_status=QueueStatus.DONE,
        )
        try:
            outbound_id = sender.send_text(conversation.contact_ref, settings.WHATSAPP_M0_RESPONSE_TEXT)
        except SendError as exc:
            outbound.send_status = SendStatus.FAILED
            outbound.save(update_fields=["send_status", "updated_at"])
            _retry_or_fail(message, str(exc))
            return 1

        outbound.platform_message_id = outbound_id
        outbound.send_status = SendStatus.SENT
        outbound.save(update_fields=["platform_message_id", "send_status", "updated_at"])
        _finish(message)
        log.info("m0.response_sent", extra={"reference": outbound_id})
        return 1


def _finish(message: Message) -> None:
    message.queue_status = QueueStatus.DONE
    message.next_attempt_at = None
    message.save(update_fields=["queue_status", "next_attempt_at", "updated_at"])


def _retry_or_fail(message: Message, error_code: str) -> None:
    message.attempts += 1
    if message.attempts >= MAX_ATTEMPTS:
        message.queue_status = QueueStatus.FAILED
        message.next_attempt_at = None
    else:
        message.queue_status = QueueStatus.QUEUED
        message.next_attempt_at = timezone.now() + timedelta(seconds=5 * 2 ** message.attempts)
    message.save(update_fields=["queue_status", "attempts", "next_attempt_at", "updated_at"])
    log.warning("m0.send_failed", extra={"error_code": error_code, "reference": str(message.pk)})
