# Contract: Email Notifications

**Direction**: application → Rafael's configured email address only. The MVP sends no customer-facing email (OI-2 excluded).
**Owner**: `src/salesagent/notifications/`
**Related**: FR-019, FR-026a, FR-026b(2), FR-026b(3), FR-048, R-006, R-009

## Transport

- Authenticated SMTP over TLS to the configured provider (R-006). Credentials and the recipient address come only from configuration (FR-048).
- The `From` address and reply handling are configuration values.
- Every message carries a plain-text body. HTML is not used in the MVP.

## Recipients

| Event | Recipient |
|---|---|
| `QUALIFIED_LEAD`, `HUMAN_HANDOFF`, `COMMERCIAL_ESCALATION`, `DELETION_REQUEST` | Rafael's configured address only |

No other recipients are permitted. The sender refuses to send to any address other than the configured recipient. No event type sends email to a customer, including for deletion verification (OI-2).

## Event payloads

Each email has a fixed subject pattern and a fixed set of fields. Nothing else is included (FR-019, FR-026a).

### QUALIFIED_LEAD

- **Subject**: `[Lead cualificado] <service category> — <reference>` (the subject language is fixed by Rafael's configuration, not the customer's language, since Rafael reads it)
- **Fields**: reference ID, name, company (if given), contact method and contact value, requested service category, project summary (generated from the lead fields), urgency (customer's words), start-within estimate, qualification result, budget text (only if given, original wording).
- **Excluded**: full transcript, message history, any identifier not in the list.

### HUMAN_HANDOFF

- **Subject**: `[Solicitud de persona] <reference>`, with `[fuera de horario]` appended when the handoff is out of hours
- **Fields**: reference ID, hours status, name if known, contact method and contact value, qualification state, short reason (`CUSTOMER_REQUEST`, `CLAIM_BLOCKED`, `MODEL_UNAVAILABLE`), and a link to the conversation in the admin interface.
- **Excluded**: transcript. Rafael reads the context in the admin interface after logging in (FR-018d).

### COMMERCIAL_ESCALATION

- **Subject**: `[Consulta comercial] <reference>`
- **Fields**: reference ID, contact method and contact value, the customer's question in their own words (quoted once, truncated to a fixed length), and the admin link.
- **Note**: this email never authorizes a price or commitment (FR-026a).

### DELETION_REQUEST

- **Subject**: `[Solicitud de eliminación] <request_id>`
- **Fields**: request ID, registration time, status (`UNDER_REVIEW`), and the instruction "verification required in the admin interface". No name, no contact value, no WhatsApp identifier, no message content.
- **Note**: this email does not verify, authorize, or erase anything. Verification (FR-026b(3)) and authorization (FR-026b(4)) happen only in the admin interface, with TOTP.

There is no customer-facing deletion verification email. The earlier one-time code email design was withdrawn (OI-1, OI-2).

## Delivery and records

- Each send creates a Notification Attempt row before the call and updates it afterward (data-model).
- A failure is recorded with an error code and the provider's message ID when available. The error text never includes the email body (FR-019).
- Failed notifications are retried with backoff up to a configured limit. The item remains visible in the admin interface until a notification succeeds (FR-031).
- The 60-second processing target (FR-019) is measured from event creation to the provider accepting the message.

## Logging

Logs record the event type, the reference ID, the outcome, and a keyed hash of the recipient. They never record the recipient address, the subject, or the body (R-018).
