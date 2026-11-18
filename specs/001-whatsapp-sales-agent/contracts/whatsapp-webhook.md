# Contract: WhatsApp Webhook

**Direction**: WhatsApp Business Platform (Meta) → web service
**Owner**: `src/salesagent/whatsapp/`
**Related**: R-004, R-016, FR-001, FR-016, FR-037

## Endpoint

`/webhooks/whatsapp/` on the public HTTPS host. This is the only unauthenticated public route, and it is protected by signature verification instead of a session.

## Subscription verification (GET)

Query parameters supplied by the platform: `hub.mode`, `hub.verify_token`, `hub.challenge`.

| Condition | Response |
|---|---|
| `hub.mode = subscribe` and `hub.verify_token` matches the configured verify token (compared in constant time) | `200`, body is `hub.challenge` as plain text |
| Anything else | `403`, empty body; logged as `webhook.verify_rejected` |

## Event delivery (POST)

**Required header**: `X-Hub-Signature-256: sha256=<hex>`.

**Verification**: HMAC-SHA256 of the raw request body, keyed with the app secret, compared in constant time. The body is not parsed before the check.

| Condition | Response | Side effect |
|---|---|---|
| Missing or invalid signature | `403` | Logged as `webhook.signature_rejected` without the body |
| Body is not valid JSON | `400` | Logged as `webhook.malformed` |
| Valid, no messages (status callbacks only) | `200` | Status updates recorded against outbound messages |
| Valid, one or more inbound messages | `200` | Each message stored once; duplicates ignored |

The handler must respond within 2 seconds. It does not call the model, the email provider, or the guard. Those run in the worker (plan, inbound pipeline).

## Inbound message handling (what is stored)

For each inbound message in the payload:

| Platform field | Stored as | Rule |
|---|---|---|
| message `id` | `platform_message_id` | Unique; a duplicate is ignored |
| `from` | contact reference | Stored as the keyed hash for lookup; the plain value is kept only for sending replies |
| `type` | `message_type` | `text` → `TEXT`; any other type → `UNSUPPORTED_MEDIA` |
| `text.body` (text only) | `body` | Stored. Never logged. |
| `timestamp` | `received_at` | Used for ordering within a conversation |

**Not stored**: media identifiers, media URLs, profile names beyond what the lead needs, and any field not listed above (FR-024). Unsupported media is never downloaded (FR-037).

## Outbound sending (used by the worker)

- Endpoint: the platform's messages endpoint for the configured phone number ID, using the access token from configuration.
- Only session messages inside the customer's service window are sent (R-004).
- Before any call, the outbound guard must have passed the message, or the message must be an APPROVED template (R-013, R-015).
- The attempt is recorded first. A response that does not confirm acceptance leaves the message `NEEDS_REVIEW`, not retried blindly (R-016).

## Errors

| Situation | Behavior |
|---|---|
| Platform rejects an outbound message (for example, outside the service window) | Message is `FAILED`; a `notification` is raised to Rafael only if it involves a handoff or qualified lead (FR-031). No retry. |
| Platform rate limit | Retry with backoff, recorded per attempt, capped. |
| Database unavailable at webhook time | Respond `503` so the platform retries. Nothing is acknowledged that was not stored. |
