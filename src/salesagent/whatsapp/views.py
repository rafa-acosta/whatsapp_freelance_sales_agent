"""WhatsApp webhook receiver (contracts/whatsapp-webhook.md, M0 subset).

GET: subscription challenge. POST: signed inbound messages, stored once per platform message
ID. Processing happens later in the worker; this view only verifies, stores, and acknowledges.
"""

from __future__ import annotations

import hmac
import json
import logging

from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from salesagent.logging.masking import hmac_identifier, mask_identifier
from salesagent.persistence.models import (
    Conversation,
    Message,
    MessageDirection,
    MessageType,
    QueueStatus,
)
from salesagent.persistence.repositories import get_or_create_conversation
from salesagent.whatsapp.parser import parse_inbound_messages
from salesagent.whatsapp.signature import verify_signature

log = logging.getLogger("salesagent.whatsapp")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def whatsapp_webhook(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return _verify_subscription(request)
    return _receive(request)


def _verify_subscription(request: HttpRequest) -> HttpResponse:
    mode = request.GET.get("hub.mode", "")
    token = request.GET.get("hub.verify_token", "")
    challenge = request.GET.get("hub.challenge", "")
    expected = settings.WHATSAPP_VERIFY_TOKEN.get()
    token_ok = bool(expected) and hmac.compare_digest(token.encode(), expected.encode())
    if mode == "subscribe" and token_ok and challenge:
        log.info("webhook.subscription_verified")
        return HttpResponse(challenge, content_type="text/plain", status=200)
    log.warning("webhook.subscription_rejected")
    return HttpResponseForbidden()


def _receive(request: HttpRequest) -> HttpResponse:
    raw_body = request.body
    # The signature is checked before the body is parsed (contract).
    if not verify_signature(
        raw_body,
        request.headers.get("X-Hub-Signature-256"),
        settings.WHATSAPP_APP_SECRET.get(),
    ):
        log.warning("webhook.signature_rejected")
        return HttpResponseForbidden()
    if not settings.WHATSAPP_M0_MODE:
        # Until the full pipeline exists (later phases), no customer message is stored (T132).
        log.info("webhook.disabled_outside_m0")
        return HttpResponse(status=200)

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        log.warning("webhook.malformed_body")
        return HttpResponse(status=200)  # Acknowledge so the platform does not retry forever.

    for event in parse_inbound_messages(payload):
        _store_inbound(event)
    return HttpResponse(status=200)


def _store_inbound(event) -> None:
    contact_key = hmac_identifier(event.wa_id, settings.LOG_HMAC_KEY.get())
    masked = mask_identifier(event.wa_id, settings.LOG_HMAC_KEY.get())

    if settings.WHATSAPP_M0_MODE and contact_key not in settings.WHATSAPP_TEST_RECIPIENT_HMACS:
        # M0 allowlist gate (T132): not stored, not answered.
        log.info("m0.sender_not_allowlisted", extra={"masked_contact": masked})
        return

    if Message.objects.filter(platform_message_id=event.platform_message_id).exists():
        log.info("inbound.duplicate_ignored", extra={"masked_contact": masked})
        return

    try:
        with transaction.atomic():
            conversation: Conversation = get_or_create_conversation(
                contact_key=contact_key,
                contact_ref=event.wa_id,
                m0_test=settings.WHATSAPP_M0_MODE,
            )
            Message.objects.create(
                conversation=conversation,
                direction=MessageDirection.INBOUND,
                platform_message_id=event.platform_message_id,
                message_type=(
                    MessageType.TEXT if event.message_type == "text" else MessageType.UNSUPPORTED_MEDIA
                ),
                # Text body is stored for the conversation record but never logged (R-018).
                body=event.text if event.message_type == "text" else None,
                queue_status=QueueStatus.QUEUED,
                next_attempt_at=timezone.now(),
            )
    except IntegrityError:
        # A concurrent duplicate delivery won the race; the unique constraint keeps one copy.
        log.info("inbound.duplicate_ignored", extra={"masked_contact": masked})
        return
    log.info("inbound.stored", extra={"masked_contact": masked})
