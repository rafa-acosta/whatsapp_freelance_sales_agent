"""Persistence models for M0 (data-model.md, subset).

M0 stores only what the connectivity test needs: a conversation per test contact, and the
inbound and outbound messages with their queue state. Lead, handoff, deletion, and other
entities are added in later tasks.

Plain-text `contact_ref` is kept only so the worker can reply. M0 accepts only allowlisted
synthetic test contacts, and `m0_purge_test_data` removes them. Host-level encryption of
`contact_ref` is a production readiness requirement (R-017, task T141).
"""

import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class ControlState(models.TextChoices):
    AI_ACTIVE = "AI_ACTIVE", "AI active"
    HUMAN_HANDOFF = "HUMAN_HANDOFF", "Human handoff"


class QualificationState(models.TextChoices):
    NEW = "NEW", "New"
    COLLECTING = "COLLECTING", "Collecting"
    NEEDS_INFO = "NEEDS_INFO", "Needs info"
    QUALIFIED = "QUALIFIED", "Qualified"
    NOT_QUALIFIED = "NOT_QUALIFIED", "Not qualified"


class Conversation(BaseModel):
    contact_key = models.CharField(max_length=64, unique=True)
    contact_ref = models.CharField(max_length=32, blank=True)
    control_state = models.CharField(
        max_length=16, choices=ControlState.choices, default=ControlState.AI_ACTIVE
    )
    qualification_state = models.CharField(
        max_length=16, choices=QualificationState.choices, default=QualificationState.NEW
    )
    language_variant = models.CharField(max_length=8, null=True, blank=True)
    language_source = models.CharField(max_length=16, null=True, blank=True)
    lock_version = models.PositiveIntegerField(default=0)
    m0_test = models.BooleanField(default=False)

    class Meta:
        app_label = "persistence"


class MessageDirection(models.TextChoices):
    INBOUND = "INBOUND", "Inbound"
    OUTBOUND = "OUTBOUND", "Outbound"


class MessageType(models.TextChoices):
    TEXT = "TEXT", "Text"
    UNSUPPORTED_MEDIA = "UNSUPPORTED_MEDIA", "Unsupported media"


class MessageSource(models.TextChoices):
    CUSTOMER = "CUSTOMER", "Customer"
    MODEL_DRAFT = "MODEL_DRAFT", "Model draft"
    TEMPLATE = "TEMPLATE", "Template"
    FALLBACK = "FALLBACK", "Fallback"
    M0_TEST = "M0_TEST", "M0 test response"


class SendStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"
    NEEDS_REVIEW = "NEEDS_REVIEW", "Needs review"


class QueueStatus(models.TextChoices):
    QUEUED = "QUEUED", "Queued"
    PROCESSING = "PROCESSING", "Processing"
    DONE = "DONE", "Done"
    FAILED = "FAILED", "Failed"


class Message(BaseModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    direction = models.CharField(max_length=8, choices=MessageDirection.choices)
    # Inbound platform message IDs are unique. This deduplicates webhook retries (R-016).
    platform_message_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    message_type = models.CharField(max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    # Stored for text messages only (data-model.md). Never logged.
    body = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=16, choices=MessageSource.choices, default=MessageSource.CUSTOMER)
    send_status = models.CharField(max_length=16, choices=SendStatus.choices, default=SendStatus.PENDING)
    # Queue fields (R-016): the database is the queue, so a crash does not lose messages (FR-031).
    queue_status = models.CharField(max_length=16, choices=QueueStatus.choices, default=QueueStatus.QUEUED)
    attempts = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "persistence"
        indexes = [models.Index(fields=["queue_status", "next_attempt_at"])]
