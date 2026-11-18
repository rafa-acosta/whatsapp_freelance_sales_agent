# Data Model: WhatsApp Freelance Sales Agent (MVP)

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Research**: [research.md](research.md) | **Date**: 2026-11-18

This model covers the entities in the spec's Key Entities section and the state each one needs to satisfy FR-018, FR-026b, FR-025, and FR-051. Field names are logical; exact column types are set during implementation. Data minimization (FR-024) applies to every field: a field exists only if a requirement needs it.

Conventions:
- Every table has `id` (UUID), `created_at`, and `updated_at`.
- `expires_at` is set on every table that holds personal data, so the retention job (R-010 and FR-025) can enforce the periods.
- No table stores secrets in plain text.

---

## Entity: Conversation

One conversation per customer WhatsApp contact.

| Field | Type | Notes |
|---|---|---|
| `contact_key` | keyed hash (R-018) | HMAC of the WhatsApp contact ID. The plain identifier is needed to reply and is stored only in `contact_ref`, encrypted at the host level (R-017). |
| `control_state` | enum: `AI_ACTIVE`, `HUMAN_HANDOFF` | Owned by the control-state transition function. Only the admin interface or the handoff transition may change it (FR-018e). |
| `qualification_state` | enum: `NEW`, `COLLECTING`, `NEEDS_INFO`, `QUALIFIED`, `NOT_QUALIFIED` | Set by the qualification engine (R-012). |
| `language_variant` | enum: `es-CR`, `en`, `pt-BR`, nullable | Set by detection or explicit choice (R-011). |
| `language_source` | enum: `detected`, `customer_choice` | Records how the variant was set. |
| `lock_version` | integer | Used with the row lock (R-016). |
| `expires_at` | timestamp | Conversation retention: 90 days from last activity (FR-025(a)). |

**Invariants**:
- `control_state = HUMAN_HANDOFF` blocks every autonomous outbound message except approved acknowledgments that FR-042 requires.
- A conversation can be `QUALIFIED` only if the qualification engine returned `QUALIFIED` at the time of the transition.

---

## Entity: Message

| Field | Type | Notes |
|---|---|---|
| `conversation_id` | FK | |
| `direction` | enum: `INBOUND`, `OUTBOUND` | |
| `platform_message_id` | string, unique | Deduplicates webhook retries (R-016). |
| `message_type` | enum: `TEXT`, `UNSUPPORTED_MEDIA` | Any non-text type is `UNSUPPORTED_MEDIA` and its content is never fetched or stored (FR-037). |
| `body` | text, nullable | Stored for text messages only, for the 90-day retention window and for Rafael's review in the admin view. Never logged (R-018). |
| `source` | enum: `CUSTOMER`, `MODEL_DRAFT`, `TEMPLATE`, `FALLBACK` | Records how an outbound message was produced. |
| `guard_result` | enum: `PASSED`, `BLOCKED`, `NOT_APPLICABLE` | Set by the outbound guard (R-013). |
| `send_status` | enum: `PENDING`, `SENT`, `FAILED`, `NEEDS_REVIEW` | See R-016. |
| `detected_language` | variant, nullable | |
| `expires_at` | timestamp | 90 days (FR-025(a)). |

**Invariant**: An outbound message with `source = MODEL_DRAFT` cannot be `SENT` unless `guard_result = PASSED`.

---

## Entity: Lead

Business information about one prospect, one-to-one with a conversation. Fields follow FR-010 exactly.

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | text | yes (for qualification) | |
| `company` | text | no | |
| `problem_description` | text | yes (for qualification) | |
| `project_scope` | text | yes (for qualification) | |
| `urgency_text` | text | yes (for qualification) | Customer's own words, preserved. |
| `start_within_months` | integer 0–36, nullable | yes (for qualification) | Extracted by the model, validated by schema. Unknown is `null`. |
| `preferred_contact_method` | enum: `WHATSAPP`, `EMAIL`, `PHONE` | yes (for qualification) | |
| `contact_email` | email, nullable | only if `preferred_contact_method = EMAIL` | Used only for Rafael's follow-up when the customer chose email as contact method. Never used for deletion verification (FR-026b(3), R-009). |
| `budget_text` | text, nullable | no | Original customer wording (FR-038). Never read by pricing code (FR-039). |
| `budget_currency` | text, nullable | no | Stored only when the customer explicitly gave a currency (FR-038). |
| `service_category_id` | FK to catalog category, nullable | no | Set only from an APPROVED catalog entry (FR-044). |
| `qualification_result` | enum: `QUALIFIED`, `NOT_QUALIFIED`, `NEEDS_INFO`, nullable | | |
| `not_qualified_reason` | enum: `SERVICE_NOT_OFFERED`, `NO_CONCRETE_PROJECT`, `NO_CONTACT_METHOD`, `TIMING_OUTSIDE_WINDOW`, nullable | | Matches the failed FR-013 criterion. |
| `expires_at` | timestamp | | Lead summaries kept 12 months (FR-025(b)). |

**Validation rules**:
- `start_within_months` outside 0 to 36 is set to `null`.
- `contact_email` is rejected unless `preferred_contact_method = EMAIL`. No deletion or verification path reads it.
- `budget_text` is free text with a maximum length; no range is enforced.

---

## Entity: Opportunity Summary

A structured record derived from the lead, produced for Rafael's review (FR-012). Not stored as a separate table in the MVP: it is generated from `Lead` and `Conversation` when a qualified or escalated event occurs, and the generated text is stored with the notification attempt so it can be re-sent without regeneration. The summary includes only the fields in FR-019.

---

## Entity: Service Catalog Entry (file-backed, indexed in memory)

Not a database table. Loaded from `knowledge/services/*.md` (R-014).

| Field | Notes |
|---|---|
| `id` | Stable identifier, one of the six categories. |
| `status` | `approved` or `draft`. Production loads only `approved`. |
| `version`, `approved_by`, `approved_on` | Required when `approved`. |
| `languages` | Variants Rafael has approved content for. |
| body sections | Description, problems addressed, technologies, scope and limitations, experience and references, FAQ. |

**Forbidden fields**: any field named `price`, `precio`, `preço`, or `tarifa` causes the loader to reject the file (Principle III).

---

## Entity: Handoff Request

| Field | Type | Notes |
|---|---|---|
| `conversation_id` | FK | |
| `reason` | enum: `CUSTOMER_REQUEST`, `COMMERCIAL_ESCALATION`, `CLAIM_BLOCKED`, `MODEL_UNAVAILABLE` | |
| `hours_status` | enum: `WITHIN_HOURS`, `OUT_OF_HOURS` | Set by the business calendar at receipt (FR-040). |
| `status` | enum: `PENDING`, `NOTIFIED`, `ACKNOWLEDGED`, `CLOSED` | `PENDING` is the out-of-hours registration (FR-042). |
| `notification_status` | enum: `NOT_SENT`, `SENT`, `FAILED` | See `NotificationAttempt`. |
| `expires_at` | timestamp | |

---

## Entity: Control Event (audit, no message content)

Records every control-state transition and every authorization (FR-018c).

| Field | Notes |
|---|---|
| `conversation_id` | FK |
| `event_type` | enum: `HANDOFF_REQUESTED`, `PAUSED_BY_ADMIN`, `RESUMED_BY_ADMIN`, `REJECTED_UNAUTHENTICATED`, `TRANSITION_DENIED` |
| `actor` | enum: `CUSTOMER`, `ADMIN`, `SYSTEM` (never `MODEL`; FR-018e) |
| `admin_user_id` | FK, nullable; set when `actor = ADMIN` |
| `previous_state`, `new_state` | control states |
| `request_ref` | correlation ID (R-018) |
| `occurred_at` | timestamp |

**Invariant**: No row may be written with `actor = MODEL`. The schema has no such enum value, and the transition function is the only writer.

---

## Entity: Deletion Request

State machine (FR-026b, owner decision OI-1):

```text
REGISTERED ──(Rafael notified)──▶ UNDER_REVIEW
UNDER_REVIEW ──(verify: WHATSAPP_ASSOCIATION_REVIEWED)──────────────▶ VERIFIED
UNDER_REVIEW ──(additional-verification)──────────────────────────▶ ADDITIONAL_VERIFICATION
ADDITIONAL_VERIFICATION ──(verify: ADDITIONAL_VERIFICATION_COMPLETED)──▶ VERIFIED
UNDER_REVIEW | ADDITIONAL_VERIFICATION ──(verify: NOT_VERIFIED)──▶ VERIFICATION_FAILED (stays open)
UNDER_REVIEW | ADDITIONAL_VERIFICATION | VERIFICATION_FAILED ──(reject)──▶ REJECTED (nothing erased)
VERIFIED ──(authorize)──▶ AUTHORIZED ──▶ EXECUTING ──▶ COMPLETED
EXECUTING ──(any step fails)──▶ FAILED (stays open, Rafael notified)
```

`REGISTERED` is set when the request is stored. It becomes `UNDER_REVIEW` when Rafael is notified. If the notification fails, the request remains `UNDER_REVIEW` and is visible to Rafael (FR-031).

| Field | Notes |
|---|---|
| `request_id` | Unique, human-readable reference shown to the customer and to Rafael (FR-026b(1)). Generated with the `secrets` module. |
| `conversation_id` | FK. Associates the request with the customer's WhatsApp identifier and the records linked to it (FR-026b(1)). The conversation may later be deleted; the request keeps only what the audit needs. |
| `status` | enum from the state machine above. |
| `verification_basis` | enum: `WHATSAPP_ASSOCIATION_REVIEWED`, `ADDITIONAL_VERIFICATION_COMPLETED`; nullable until `VERIFIED`. |
| `verified_by`, `verified_at` | Set only by the admin verification route, with TOTP (FR-018d, R-009). |
| `authorized_by`, `authorized_at` | Set only by the admin authorization route, with TOTP (FR-018d). |
| `rejection_reason_code` | Enum from R-009 when closed as `REJECTED`. |
| `completed_at`, `failure_reason_code` | Completion timestamp, or a short code (never personal data). |

**Invariants**:
- No data is erased or anonymized unless the request has passed `VERIFIED` and is `AUTHORIZED` (FR-026b(3), (4)).
- Only the administration verification and authorization routes can set `VERIFIED` or `AUTHORIZED`. A chat message, model output, timer, or unauthenticated request cannot (FR-018e).
- The customer is told completion only after `COMPLETED` (FR-026, FR-026b(9)).

---

## Entity: Deletion Audit Record (FR-026b(8))

Minimal, kept after the personal data is gone.

| Field | Notes |
|---|---|
| `request_id` | |
| `registered_at`, `verified_at`, `authorized_at`, `completed_at` | Timestamps only. |
| `status_history` | Status values and timestamps. |
| `authorized_action` | Fixed value, for example `DELETE_AND_ANONYMIZE`. |

No names, phone numbers, emails, or message content. `expires_at` is set to the legal retention period once the legal review sets it (open item under FR-047).

---

## Entity: Message Template (file-backed)

Not a database table. Loaded from `content/messages/<variant>/*.yml` (R-015).

| Field | Notes |
|---|---|
| `message_id` | Required set: greeting, ai_identification, business_hours, handoff_ack, out_of_hours_handoff, pricing_refusal, multimedia_notice, privacy_notice, deletion_ack, deletion_completed, language_selection, fallback, closing. |
| `variant` | `es-CR`, `en`, or `pt-BR`. |
| `status` | `DRAFT` or `APPROVED`. Production refuses `DRAFT` (FR-051). |
| `version`, `approved_by`, `approved_on` | Required when `APPROVED`. |
| `text` | The message. Must pass the guard's template checks (R-013). |

---

## Entity: Notification Attempt

| Field | Notes |
|---|---|
| `event_type` | enum from FR-026a: `QUALIFIED_LEAD`, `HUMAN_HANDOFF`, `COMMERCIAL_ESCALATION`, `DELETION_REQUEST`, plus `OUT_OF_HOURS_HANDOFF` as a sub-case of `HUMAN_HANDOFF`. All recipients are Rafael; the model has no customer-facing email type (OI-2). |
| `reference_id` | `Lead`, `Handoff Request`, or `Deletion Request` ID. |
| `attempted_at`, `status` | `SENT`, `FAILED`, or `RETRYING`. |
| `provider_message_id` | Returned by the email provider, for troubleshooting (FR-019). |
| `error_code` | Short code, never the message content (FR-019). |
| `expires_at` | 90 days. |

---

## Entity: Admin User

Single administrator (Rafael). Standard Django user model with a TOTP device (R-008). Created by management command only.

---

## Entity: Retention Job Run

| Field | Notes |
|---|---|
| `run_at`, `status` | Daily job (plan, Architecture Overview). |
| `deleted_counts` | Per table, counts only. |

Deletes or anonymizes rows where `expires_at` has passed, subject to any legal hold the legal review sets (FR-047).

---

## State Machines Summary

**Control state (Conversation.control_state)**:

```text
AI_ACTIVE ──(customer handoff request | pause by admin | claim blocked | model unavailable repeatedly)──▶ HUMAN_HANDOFF
HUMAN_HANDOFF ──(resume by admin, authenticated, recorded)──▶ AI_ACTIVE
```

Forbidden transitions: any transition triggered by the model, a timer, customer inactivity, or a customer message other than a handoff request (FR-018a, FR-018b, FR-018e).

**Qualification state (Conversation.qualification_state)**: `NEW → COLLECTING → NEEDS_INFO ⇄ COLLECTING → QUALIFIED | NOT_QUALIFIED`. Transitions happen only in the qualification engine (R-012).

**Handoff request**: `PENDING → NOTIFIED → ACKNOWLEDGED → CLOSED`. `PENDING` is used only for out-of-hours registrations until the notification succeeds (FR-042).

---

## Requirements Traceability

| Requirement | Entities and fields |
|---|---|
| FR-010, FR-038, FR-039 | Lead fields, budget stored as text |
| FR-013, FR-014 | Lead, `qualification_result`, `not_qualified_reason` |
| FR-018 to FR-018e | Conversation `control_state`, Control Event |
| FR-019, FR-026a, FR-031 | Notification Attempt, Handoff Request `notification_status` |
| FR-024, FR-025 | `expires_at` on each entity; minimal fields |
| FR-026, FR-026b | Deletion Request, Deletion Audit Record |
| FR-033 to FR-036 | Conversation `language_variant`, Message Template variants |
| FR-037 | Message `message_type` |
| FR-040 to FR-042 | Handoff Request `hours_status`, `status` |
| FR-043, FR-046 | Message `guard_result` |
| FR-050 to FR-053 | Message Template `status`, approval fields |
