# Contract: Administration Routes

**Direction**: Rafael's browser → web service
**Owner**: `src/salesagent/admin/`
**Related**: R-008, R-009, FR-018a, FR-018c, FR-018d, FR-018e, FR-026b(3), FR-026b(4)

These are the only administrative functions in the MVP (FR-018d(e)). No other admin surface may exist.

## Common rules (apply to every route)

- Every route except `/admin/login/` and `/admin/login/totp/` requires an authenticated session with a completed second factor.
- Every state-changing route is `POST` only and requires a valid CSRF token. A missing or invalid token returns `403` and is logged as `admin.csrf_rejected`.
- Sessions: secure, HTTP-only, same-site cookies, idle timeout set in configuration.
- An unauthenticated request to any protected route redirects to login. It never returns data.
- Responses contain only what the screen needs. Message bodies are shown only in the conversation detail view, never in lists.
- Every state change writes a Control Event or Deletion Request history row with the administrator's ID (R-008, data-model).

## Authentication

| Route | Method | Purpose | Notes |
|---|---|---|---|
| `/admin/login/` | GET, POST | Password step | Rate-limited per IP and per account. Failures are logged without the password. |
| `/admin/login/totp/` | GET, POST | Second-factor step | Required before any protected route. |
| `/admin/logout/` | POST | End session | CSRF-protected. |

## Handoff management (FR-018a, FR-018d)

| Route | Method | Purpose | Result |
|---|---|---|---|
| `/admin/handoffs/` | GET | List conversations in `HUMAN_HANDOFF` or with a `PENDING` handoff | Shows request time, hours status, qualification state, and a link. No message bodies. |
| `/admin/conversations/<id>/` | GET | View context needed to respond: lead fields, summary, recent messages | Read-only. Does not change state. |
| `/admin/conversations/<id>/pause/` | POST | Move `AI_ACTIVE` → `HUMAN_HANDOFF` | Writes `PAUSED_BY_ADMIN`. Idempotent. |
| `/admin/conversations/<id>/resume/` | POST | Move `HUMAN_HANDOFF` → `AI_ACTIVE` | Requires the form field `confirm=RESUME` and a fresh TOTP code in the same request (explicit, authenticated action per FR-018a). Writes `RESUMED_BY_ADMIN` with actor and time. |
| `/admin/conversations/<id>/reply/` | — | Not provided in the MVP | Rafael replies from WhatsApp directly; the admin interface does not send messages. |

**Rules**:
- Resume is refused if the conversation is not in `HUMAN_HANDOFF` (`409`).
- No route accepts a control-state value from a customer message or a model output (FR-018e). Control state is set only by these routes and by the handoff transition in the worker, which is triggered by customer intent and recorded.

## Deletion review (FR-026b(4))

| Route | Method | Purpose | Result |
|---|---|---|---|
| `/admin/deletions/` | GET | List requests with status, excluding message content | Shows `request_id`, status, and timestamps. |
| `/admin/deletions/<request_id>/` | GET | Review request: WhatsApp association summary, status history, and verification outcome | No message content. Shows only what the review needs. |
| `/admin/deletions/<request_id>/verify/` | POST | Record Rafael's verification decision (FR-026b(3)) | Requires `confirm=VERIFY`, `outcome` (`VERIFIED` or `NOT_VERIFIED`), a `basis` when `VERIFIED` (`WHATSAPP_ASSOCIATION_REVIEWED` from `UNDER_REVIEW`, or `ADDITIONAL_VERIFICATION_COMPLETED` from `ADDITIONAL_VERIFICATION`), and a fresh TOTP code. `VERIFIED` sets `VERIFIED`. `NOT_VERIFIED` sets `VERIFICATION_FAILED` and leaves the request open. Records `verified_by` and `verified_at`. |
| `/admin/deletions/<request_id>/additional-verification/` | POST | Mark a request that needs proportionate additional verification | Requires `confirm=ADDITIONAL_VERIFICATION` and a fresh TOTP code. Sets `ADDITIONAL_VERIFICATION`. Used when the request is suspicious, concerns a third party, or the identity cannot be established. |
| `/admin/deletions/<request_id>/authorize/` | POST | Authorize deletion for a `VERIFIED` request (FR-026b(4)) | Requires `confirm=AUTHORIZE` and a fresh TOTP code. Sets `AUTHORIZED`. Starts execution. |
| `/admin/deletions/<request_id>/reject/` | POST | Close a request that cannot be verified, or a duplicate | Requires `confirm=REJECT`, a `reason_code` (`NOT_VERIFIED`, `THIRD_PARTY_NOT_AUTHORIZED`, `DUPLICATE`, `OTHER`), and a fresh TOTP code. Allowed from `UNDER_REVIEW`, `ADDITIONAL_VERIFICATION`, or `VERIFICATION_FAILED`. Sets `REJECTED`. Does not erase anything. |

**Rules**:
- `verify` is refused unless the status is `UNDER_REVIEW` or `ADDITIONAL_VERIFICATION` (`409`). A `basis` that does not match the current status is refused (`409`).
- `additional-verification` is refused unless the status is `UNDER_REVIEW` (`409`).
- `authorize` is refused unless the status is `VERIFIED` (`409`).
- `reject` is refused once the request is `AUTHORIZED`, `EXECUTING`, `COMPLETED`, or `FAILED` (`409`).
- Additional verification is performed by Rafael outside the system, through a channel permitted by Meta policy. The system sends nothing for it. It never requires identity-document numbers (FR-024) or an email address.
- No route accepts a verification or authorization from a customer message, a model output, or an unauthenticated request (FR-018e, FR-026b(3)).
- Authorization never runs in the request thread. The request sets `AUTHORIZED`; the worker performs the steps in FR-026b(5) to (9) and writes the audit record.
- The customer is notified of completion only by the worker after `COMPLETED` (FR-026b(9)).

## Out of scope for the MVP

- Editing the catalog, templates, holiday data, or prompts. These change through version-controlled files and reviewed commits.
- Viewing or exporting data in bulk.
- User management beyond the single administrator.
- Any route that sends a message to a customer.
