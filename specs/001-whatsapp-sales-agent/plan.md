# Implementation Plan: WhatsApp Freelance Sales Agent (MVP)

**Branch**: `001-whatsapp-sales-agent` (created 2026-11-18 in the initialized Git repository; no remote, nothing pushed) | **Date**: 2026-11-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-whatsapp-sales-agent/spec.md`, Constitution v1.0.1

**Status**: Planning complete for Phase 0 and Phase 1. No application code has been written. Production use is blocked by the gates listed under "Production Gates."

## Summary

Build a WhatsApp sales assistant for Rafael that answers inbound prospects in Spanish (es-CR), English, or Brazilian Portuguese (pt-BR). It identifies the service need from an approved, Rafael-owned catalog, collects lead information, qualifies leads with deterministic rules, and notifies Rafael by email. It hands conversations to Rafael on request and only resumes automation after his explicit action in a minimal authenticated admin interface. It runs a controlled personal-data deletion workflow.

The central design choice: **the language model proposes; deterministic application code decides.** The model extracts fields, classifies intent, and drafts wording. Code owns the control state, qualification, business hours, catalog eligibility, commercial restrictions, template approval, and the outbound guard that every message must pass before it is sent.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Django (current LTS, for the web app, sessions, CSRF, and password hashing), `psycopg` (PostgreSQL driver), `anthropic` SDK (language model access, isolated behind an internal interface), `django-otp` (TOTP second factor for the administrator), `python-dateutil` (Easter calculation for movable holidays), standard-library `zoneinfo` (time zone `America/Costa_Rica`). Details in [research.md](research.md).

**Storage**: PostgreSQL. Holiday and closure configuration in version-controlled files. Catalog and templates in version-controlled Markdown and YAML files.

**Testing**: pytest with pytest-django. Unit tests for deterministic logic; contract tests for the WhatsApp webhook and admin routes using synthetic payloads; integration tests with a fake language-model client and a fake email sender. Mandatory test categories are listed under "Approved technology stack" below.

**Target Platform**: Linux containers (Docker Compose) on one host with HTTPS termination in front of the web service. Host choice is a deployment decision (see research.md, R-017) and must be reviewed under FR-047.

**Project Type**: Web service (webhook and administration) plus a background worker and a scheduled job, in one repository.

**Performance Goals**: Webhook acknowledges within 2 seconds (the platform retries if it does not). Lead and handoff email processing targeted within 60 seconds of the triggering event (FR-019). Reply latency to customers is not a formal target in the spec and will be measured, not promised.

**Constraints**: No real customer data in any environment before the legal review in FR-047 is complete. WhatsApp replies are sent only within the platform's customer-service window; the MVP sends no unsolicited messages (FR-028). Holiday data is configuration, not code (FR-040c). Every secret comes from the environment or a secret store (FR-048).

**Scale/Scope**: One operator, one WhatsApp number. Volume is assumed to be low (fewer than 1,000 conversations per month). This assumption must be checked during the planned pilot and does not drive the MVP architecture.

### Approved technology stack

Approved by the project owner on 2026-11-18 (resolution of OI-1 to OI-3). The rationale and alternatives for each choice are in [research.md](research.md).

| Area | Approved choice | Notes |
|---|---|---|
| Language | Python 3.12 | R-001 |
| Web framework | Django (current LTS) | One application; sessions, CSRF, password hashing (R-002) |
| Database | PostgreSQL | Row locks and unique constraints (R-003) |
| Language model | Anthropic API, Claude Sonnet 5.5 as the initial model | The model identifier is configuration. Calls go only through the internal `ai/` interface (R-005) |
| Email notifications | Amazon SES over authenticated SMTP with TLS | Provider, region, and sender are configuration. The SMTP interface keeps the provider replaceable (R-006) |
| Deployment | Docker Compose on one host (`web`, `worker`, `db`) | R-017 |
| Transport | HTTPS through a reverse proxy, the only public entry point | R-004, R-017 |
| Administrator authentication | Django password authentication with a TOTP second factor (`django-otp`) | Protects handoff resumption and deletion authorization (R-008) |

**Stack rules**:
- The LLM provider sits behind an internal abstraction (`ai/`). Orchestration imports the interface, never the SDK (Principle IX).
- The email provider is configurable. No infrastructure region, credential, or API key is hardcoded (R-006, R-007).
- Human-exclusive pricing (Principle III) and the authoritative approved catalog are preserved. Business rules are enforced by deterministic application logic (FR-043, FR-044).

**Mandatory automated test categories** (Principle VIII; each must exist before the feature is considered implemented):
1. Pricing restrictions: no price, range, estimate, or discount reaches the customer, including adversarial and misleading commercial requests.
2. Unauthorized state transitions: no control-state or deletion-state change from a chat message, model output, timer, or unauthenticated request.
3. Deletion authorization: no data is erased or anonymized without a human verification and an authorization, and the customer is told of completion only after completion.
4. Unapproved service claims: the guard blocks uncited, unapproved, or missing catalog claims.
5. Adversarial prompt injection: customer messages and retrieved content that try to override rules, grant authority, or claim prior approval have no effect.

**Before production** (Production Gate 6): measure actual language-model costs at expected volume, and document the data-processing implications of the Anthropic API and SES for the legal review (FR-047).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | How the plan satisfies it | Status |
|---|---|---|
| I. Human-controlled sales | No code path sends a price, date, or commitment. The outbound guard (`guard/`) blocks them (R-013). Commercial questions route to Rafael by email. | PASS |
| II. No hallucinated capabilities | The model receives only approved catalog entries for the matched category. Its output must cite catalog entry IDs. The guard rejects citations to unapproved or missing entries. | PASS, with residual risk: the guard cannot fully verify free-text claims. Mitigation is the citation rule plus the review in Rafael's approval of the catalog (see Residual Risks). |
| III. Human-exclusive pricing | No price data exists in the catalog schema (catalog validator rejects a `price` field). Budget is stored as free text and never read by pricing code (FR-039). Price-pattern and commitment lexicon checks run on every outbound draft in es, en, and pt. | PASS |
| IV. Privacy and security | Minimal data fields. Secrets from the environment only, with a `.env.example` and `.gitignore` for `.env`. Email uses an authenticated, TLS-secured provider. Logs use masked identifiers and never record message bodies at INFO. Deletion follows FR-026b: human verification and authorization, no customer email, no erasure on a chat message. Legal review gates production (FR-047). | PASS, conditional on FR-047 |
| V. Deterministic business logic | Control state, qualification, business hours, deletion state, and template status are pure functions or database state transitions in code, with unit tests. The model cannot write control state (FR-018e). | PASS |
| VI. Observability | Structured JSON logs for events, errors, and transitions. Masked identifiers. Control events and notification attempts stored without message content (FR-018c, FR-019). | PASS |
| VII. Human handoff | Handoff is detected by a deterministic keyword list in es, en, and pt, plus the model's intent. Either one triggers handoff. Out-of-hours handoffs are registered and emailed. Automation resumes only through an authenticated admin action. | PASS |
| VIII. Test-driven quality | Core logic (state machine, qualification, calendar, guard, deletion, templates, catalog loader) has unit tests written first. Contract tests cover the webhook and admin routes. | PASS. Tests are scheduled before implementation in `tasks.md`. |
| IX. Modular architecture | Separate packages for WhatsApp transport, orchestration, AI services, outbound guard, persistence, notifications, admin, and compliance. Orchestration imports interfaces, not the WhatsApp or model SDKs. | PASS |
| X. MVP-first | One repository, one database, two processes (web and worker). No CRM, no dashboard, no queue broker, no retrieval infrastructure. Each extra component is justified in Complexity Tracking. | PASS |

**Constitution gate result**: PASS. No unjustified violations.

**Governance note**: The draft amendment (`proposals/constitution-1.1.0-draft.md`) is awaiting approval. This plan implements both proposed rules (automation resumption and verified deletion) in code and tests, so it does not depend on the amendment being approved. If the amendment is rejected, the rules remain in the specification.

## Architecture Overview

Two runtime processes and one scheduled job share one PostgreSQL database.

```text
Customer (WhatsApp)
   │  webhook (HTTPS, signed)
   ▼
[web]  Django: webhook receiver + admin (login, TOTP, CSRF)
   │  stores inbound message once (deduplicated by platform message ID)
   ▼
[PostgreSQL]  conversations, messages, leads, handoffs, deletion requests, audit events
   ▲
   │  locks one conversation at a time
[worker]  process_inbox loop
   │  deterministic pipeline (see below)
   ├─► ai/        model client → structured output → schema validation
   ├─► guard/     outbound validator (prices, commitments, catalog citations)
   ├─► catalog/ messages/ business_calendar/   approved content and hours
   └─► notifications/  email to Rafael (SES over authenticated SMTP)
   
[scheduler]  retention job, holiday-calendar integrity check (daily)
```

**Inbound pipeline (worker, per message)**:

1. Acquire the conversation lock (database row lock). This serializes rapid successive messages (edge case: quick succession).
2. If the message type is not text, send the approved multimedia notice in the detected language. Do not change state (FR-037).
3. Deterministic deletion-intent check: keyword list in es, en, pt (for example "borren mis datos", "apague mis datos", "apaguem meus dados"), with model intent as advisory input. A match registers a deletion request associated with the conversation (FR-026b(1)), notifies Rafael (FR-026a), and, in AI_ACTIVE, sends the approved deletion acknowledgment. In HUMAN_HANDOFF the request is registered and Rafael is notified, but no automatic reply is sent (FR-018b). No inbound message verifies or authorizes a deletion. Verification and authorization are human actions in the administration interface.
4. Deterministic handoff check: keyword list in es, en, pt (for example "hablar con una persona", "hablar con alguien", "falar com uma pessoa", "talk to a person"). Matching triggers handoff.
5. If the control state is `HUMAN_HANDOFF`, store the message and do not respond (FR-018b). Stop.
6. Model extraction: language variant, intent, service-category candidates, field values, and the start-within-months estimate, returned as strict JSON. Invalid output triggers the approved fallback message (FR-030).
7. Deterministic update: merge extracted fields, apply qualification rules (R-012), select the next question, or trigger a handoff or commercial escalation.
8. Drafting: the model drafts the reply from approved catalog entries and approved templates only, with citations. The outbound guard checks the draft (R-013). A failed check blocks the send, records the failure, and escalates (FR-046).
9. Send the reply within the service window. Record the outbound message. Emit notifications for qualification, handoff, commercial escalation, or deletion.

## Project Structure

### Documentation (this feature)

```text
specs/001-whatsapp-sales-agent/
├── spec.md
├── plan.md                  # this file
├── research.md              # Phase 0 decisions
├── data-model.md            # Phase 1 entities and state machines
├── quickstart.md            # Phase 1 validation guide
├── contracts/               # Phase 1 interface contracts
│   ├── whatsapp-webhook.md
│   ├── admin-routes.md
│   ├── email-notifications.md
│   └── content-files.md     # catalog entry and message template formats
├── checklists/requirements.md
└── proposals/constitution-1.1.0-draft.md
```

`tasks.md` is produced by `/speckit-tasks`, not by this plan.

### Source Code (repository root, planned; not yet created)

```text
knowledge/services/                    # approved catalog, one Markdown file per service (Rafael-owned)
content/messages/es-CR/                # standard messages, YAML, one file per message ID
content/messages/en/
content/messages/pt-BR/
config/calendar/                       # holidays per year + closures, YAML (FR-040c)
src/salesagent/
├── settings/                          # environment-based configuration only
├── whatsapp/                          # webhook verification, signature check, parsing, sending
├── orchestration/                     # conversation pipeline, control states, handoff
├── qualification/                     # pure qualification rules (FR-013)
├── ai/                                # model client interface, prompts, schemas, output validation
├── guard/                             # deterministic outbound validator (R-013)
├── catalog/                           # catalog loader, approval status, citation lookup
├── messages/                          # template loader, DRAFT/APPROVED enforcement
├── business_calendar/                 # hours, holidays, closures (America/Costa_Rica)
├── persistence/                       # Django models and repositories
├── notifications/                     # event builders, email sender, delivery attempts
├── admin/                             # authenticated handoff and deletion views
├── compliance/                        # deletion workflow, retention job, audit records
└── logging/                           # structured logs with PII masking
tests/
├── unit/                              # deterministic logic first
├── contract/                          # webhook and admin route contracts with synthetic payloads
└── integration/                       # pipeline with fake model client and fake email sender
deploy/                                # Dockerfile, docker-compose.yml, reverse-proxy config
.env.example                           # placeholders only
.gitignore                             # excludes .env and secret files
```

**Structure Decision**: One repository with a single Python package (`src/salesagent/`) organized by responsibility, following Principle IX. The Django project is one application, not multiple services. The package name `business_calendar` avoids shadowing the standard-library `calendar` module.

## Production Gates

These gates do not block planning or development with synthetic data. They block production with real customer data.

1. **Legal Review 3a (FR-047)**: complete and documented, including Law 8968, notice and consent, database registration, processor contracts, international transfers (SES region choice and any cross-border host, see R-006 and R-017), retention and deletion, and Meta policies.
2. **Standard messages (FR-051, FR-052)**: every template in es-CR, en, and pt-BR is APPROVED by Rafael. The application refuses to start in production if any required template is DRAFT.
3. **Catalog (FR-006, FR-032)**: every catalog entry used in production is APPROVED by Rafael.
4. **Holiday calendar (FR-040b)**: the MTSS calendar is loaded and verified against the official source for the operating years.
5. **Repository hygiene (FR-048)**: the repository is initialized with `.gitignore` excluding `.env` and secrets (done 2026-11-18, with no secrets in the staged set). Before any push: confirm the remote's visibility, reconcile with the existing `whatsapp_freelance_sales_agent-1` clone, and run a secret scan of the full history.
6. **LLM cost and data processing**: measure actual language-model token costs at expected volume with synthetic traffic, and document the Anthropic API and SES data flows, processor terms, and any transfers for the legal review (FR-047).

## Residual Risks

- **Claim verification is partial.** The outbound guard checks citations, prices, and commitments. It cannot prove that every free-text sentence matches the catalog. Mitigation: the model receives only approved entries, must cite them, and runs with a low-temperature setting; Rafael reviews the transcript sample in the pilot (SC-006 measures it).
- **Language detection is model-based.** Short messages can be ambiguous between Spanish and Portuguese. Mitigation: low-confidence results trigger the approved language-selection question (FR-035).
- **Deletion identity is established by human judgment.** The WhatsApp association shows that the request came from the number that holds the records. It does not prove who the person is. Rafael's review and proportionate additional verification carry this risk. It is accepted for the MVP and remains subject to the legal review (FR-047).

## Open Issues Found During Planning

These were inconsistencies or gaps found during planning. All three are resolved by the project owner on 2026-11-18.

- **OI-1 (resolved: human-verified deletion, no customer email code)**: The email-code option is withdrawn. A deletion request is associated with the customer's WhatsApp identifier and the stored records linked to it (FR-026b(1)). Rafael verifies the requester's authority in the administration interface (FR-026b(3), FR-018d), and applies proportionate additional verification for suspicious, third-party, or unidentified cases. Additional verification never requires an email address or sensitive data. Rafael authorizes execution separately (FR-026b(4)). Updated: spec FR-026b; research R-009; data-model Deletion Request; contracts `admin-routes.md` and `email-notifications.md`; quickstart S10. The remaining deletion-related legal items stay as production gates (FR-047).
- **OI-2 (resolved: excluded from the MVP)**: Customer-facing verification emails are not part of the MVP. FR-026a covers only notifications to Rafael. No customer OTP is generated, delivered, stored, expired, or validated. The `deletion_code` template and the `DELETION_VERIFICATION_CODE` email type are removed.
- **OI-3 (resolved: Git repository initialized)**: The project directory is a Git repository with `.gitignore` for Python, Django, environment files, virtual environments, local databases, credentials, and temporary files. Spec Kit artifacts are preserved and tracked. The feature branch `001-whatsapp-sales-agent` is created. Nothing is committed or pushed, and no remote is configured. Before any push, confirm the repository visibility (Production Gate 5). A separate clone, `whatsapp_freelance_sales_agent-1`, already has a GitHub `origin` and one commit (LICENSE and .gitignore). It is not connected to this repository. Decide how the two are reconciled before pushing.

## Complexity Tracking

| Violation or addition | Why needed | Simpler alternative rejected because |
|---|---|---|
| Two processes (web and worker) | Webhooks must be acknowledged within the platform's time limit, while model calls take seconds. The spec requires that acknowledged messages are not lost (FR-031). | Processing inline in the webhook risks timeouts and duplicate processing. A single-process queue inside the web app would be harder to test and to keep under the conversation lock. |
| PostgreSQL instead of SQLite | Row-level locking for the per-conversation lock, deduplication constraints, and a standard production database for personal data. | SQLite serializes all writes and gives weaker guarantees for concurrent webhook and worker access. |
| Admin web interface (TOTP login, CSRF) | FR-018a and FR-018d require authenticated, controlled resumption and deletion authorization. | Editing the database by hand, or a chat command, cannot meet FR-018d(a) to (d) or FR-018e. |
| Django framework | Ships session handling, CSRF protection, and password hashing, which FR-018d requires. Building these from scratch is a larger security risk. | A minimal framework needs hand-written CSRF and session code for a security-sensitive admin. |
| Separate outbound guard module | Principle III and FR-043 require enforcement independent of the model. | Prompt instructions alone are prohibited by FR-043 and Principle V. |

## Phase 0 and Phase 1 Outputs

- [research.md](research.md): decisions R-001 to R-018 with rationale and alternatives.
- [data-model.md](data-model.md): entities, fields, validation rules, and state machines.
- [contracts/](contracts/): webhook, admin routes, email notifications, and content file formats.
- [quickstart.md](quickstart.md): validation scenarios that prove the feature works end to end once implemented.
