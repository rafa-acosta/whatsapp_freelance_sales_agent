# Research: WhatsApp Freelance Sales Agent (MVP)

**Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Date**: 2026-11-18

Each decision below resolves a technical design question left open in the specification. Where a decision has legal or production consequences, it is marked and carried into the Production Gates in the plan.

---

## R-001: Language and runtime

**Decision**: Python 3.12.

**Rationale**: The model SDK, the Django framework, and the test tooling are mature in Python. The conversational logic is text-heavy, and the team (one operator) benefits from one language across the web app, worker, and tests. Python 3.12 is a supported version with a long support window.

**Alternatives considered**: TypeScript/Node (good WhatsApp SDKs, weaker fit for the admin security features that Django provides out of the box). Go (strong concurrency, more code for the same MVP).

---

## R-002: Web framework

**Decision**: Django (current LTS release at implementation time), used as a single application.

**Rationale**: FR-018d requires secure sessions, CSRF protection, access control, and authentication before any admin action. Django provides session management, CSRF middleware, and password hashing as tested defaults. Using only what the MVP needs avoids Django admin and other extras. The webhook endpoint is a plain view.

**Alternatives considered**: FastAPI (faster to start, but session, CSRF, and login would be hand-built, which is a larger security risk for the admin surface). Flask (similar issue, more extensions).

---

## R-003: Database

**Decision**: PostgreSQL (current supported major version).

**Rationale**: The per-conversation lock (R-016) relies on row-level locking. Deduplication of platform message IDs relies on unique constraints. Personal data needs a production-grade database with encryption at rest provided by the host (see R-017).

**Alternatives considered**: SQLite (simpler to run, but serializes writes and offers weaker guarantees under concurrent webhook and worker access). A managed cloud database (valid later; adds cost and a region decision that belongs to the legal review).

---

## R-004: WhatsApp channel

**Decision**: WhatsApp Business Platform Cloud API. The web app receives webhooks, verifies the subscription challenge, and checks the request signature (HMAC-SHA256 of the raw body with the app secret, in the signature header) before reading any payload. Replies are sent as session messages inside the customer's service window. The MVP sends no template messages to customers outside the window, because it sends no unsolicited messages (FR-028).

**Rationale**: Signed webhooks prevent forged inbound messages. The 24-hour service window restriction matches FR-028 and Principle IV. Session-only replies avoid needing template approvals from Meta for the MVP.

**Alternatives considered**: Third-party WhatsApp gateways (add a processor, complicating FR-047 processor review and cross-border questions). Unofficial clients (violate Meta policy, prohibited by Principle IV).

**Note**: Standard message templates in `content/messages/` are internal content approved by Rafael (FR-051). They are not Meta-approved WhatsApp message templates. The name overlap is intentional only in the spec's wording; implementation must keep the two concepts separate in code and documentation.

---

## R-005: Language model

**Decision**: Anthropic Claude via the official `anthropic` SDK, using `claude-sonnet-5-5` by default, set through configuration so the model can change without code changes. Calls are made only through an internal interface in `src/salesagent/ai/`. The orchestration code imports the interface, not the SDK (Principle IX).

**Rationale**: Consistent quality across Spanish, English, and Portuguese. Structured outputs can be validated against a JSON schema before use. The internal interface lets tests run with a fake client and makes provider changes local.

**Alternatives considered**: Running an open-weight model locally (avoids a third-party processor, but requires hardware and ops work out of scope for the MVP, and raises the same processor-review questions for any hosted option). A smaller model for extraction only (valid cost optimization, left for later; the interface allows it).

**Legal note**: The model provider processes customer message content. This is a third-party processor relationship under FR-047 and may involve transfers outside Costa Rica. It must be reviewed before production.

**Production evaluation (plan Production Gate 6)**: Before production, measure actual token costs per conversation at expected volume with synthetic traffic, and record the processor terms, data-retention settings, and transfer locations in the legal review. The model identifier is configuration, so the evaluation can compare models without code changes.

---

## R-006: Email provider

**Decision**: Amazon SES, used through authenticated SMTP over TLS (STARTTLS or implicit TLS as the provider requires), with a dedicated IAM SMTP credential. Sender domain and DKIM configured in the provider. The application uses Python's standard `smtplib` with TLS, so changing the provider only changes configuration.

**Rationale**: Mature transactional service, supports authenticated SMTP, rotatable credentials, delivery event logs, and a managed domain-authentication setup. The SMTP interface keeps the application independent of a vendor SDK.

**Alternatives considered**: Postmark or Resend (similar capabilities, smaller ecosystems for enterprise-style credential rotation). Self-hosted SMTP (rejected: deliverability and security burden for one operator).

**Legal and production note**: SES must be used in a region chosen during the legal review (FR-047). The region determines where email content, including customer contact information, is processed. This is an open item (see R-017 and the plan's Production Gates). The region is a configuration value, never hardcoded in code. The email provider remains configurable (approved stack, plan.md).

---

## R-007: Secrets and configuration

**Decision**: All configuration is read from environment variables through a single settings module. A committed `.env.example` lists every variable with placeholder values. `.env` and any `*.secret` or local override files are excluded in `.gitignore`. Production uses the host's secret store or environment injection; a managed secret store is used when the production host supports one. Rafael's notification address, the SMTP credential, the model API key, the WhatsApp app secret and access token, and the database password are all configuration values. Credential rotation requires only a restart with the new values.

**Rationale**: Satisfies FR-048 and Principle IV. Keeping secrets out of code also keeps them out of logs and version history.

**Alternatives considered**: Encrypted secret files committed to the repository (rejected: key management risk, and FR-048 forbids committing secrets). Hard-coded values (prohibited).

**Logging rule**: Settings objects must implement a `__repr__` that masks secret values, and the logging filter (R-018) strips any value matching a configured secret.

---

## R-008: Administrator authentication

**Decision**: Django's built-in authentication for a single administrator account, with a time-based one-time password (TOTP) second factor provided by `django-otp`. Sessions use secure, HTTP-only, same-site cookies with an idle timeout. Every state-changing admin request is protected by Django's CSRF middleware. Login attempts are rate-limited per IP and per account. The administrator account is created through a management command, not a web sign-up.

**Rationale**: FR-018d requires authentication, secure sessions, access control, and CSRF protection. A second factor protects the handoff and deletion authorization functions, which can change customer-facing behavior and erase data.

**Alternatives considered**: Single sign-on through a third-party identity provider (adds a processor and an account dependency for one user). Password-only login (weaker for functions that erase data).

**Open detail**: The rate-limit thresholds and the idle timeout are set during implementation and recorded in `quickstart.md`.

---

## R-009: Deletion requester verification

**Decision (owner decision on OI-1, 2026-11-18)**: Rafael verifies the requester's authority. No code is sent to the customer, and no email address is needed.

- **Registration (FR-026b(1))**: each request gets a unique, human-readable request ID (generated with the `secrets` module) and is associated with the conversation's WhatsApp identifier and the stored records linked to it.
- **Notification (FR-026b(2))**: the DELETION_REQUEST email to Rafael carries only the request ID, registration time, and status.
- **Verification (FR-026b(3))**: `VERIFIED` is set only by the administration route `POST /admin/deletions/<request_id>/verify/`. It requires `confirm=VERIFY`, a fresh TOTP code, an `outcome` (`VERIFIED` or `NOT_VERIFIED`), and, for `VERIFIED`, a `basis` value: `WHATSAPP_ASSOCIATION_REVIEWED` or `ADDITIONAL_VERIFICATION_COMPLETED`. The verifier's ID and time are recorded.
- **Additional verification**: if the request is suspicious, concerns a third party, or identity cannot be established, Rafael sets the status to `ADDITIONAL_VERIFICATION` (`POST /admin/deletions/<request_id>/additional-verification/`, with the same confirmation and TOTP). He then performs proportionate checks himself, through a channel permitted by Meta policy (FR-047). Checks never require identity-document numbers (FR-024) or an email address.
- **Failure**: if Rafael records `NOT_VERIFIED`, the status is `VERIFICATION_FAILED` and the request stays open. Rafael may close it with `POST /admin/deletions/<request_id>/reject/` and a reason code (`NOT_VERIFIED`, `THIRD_PARTY_NOT_AUTHORIZED`, `DUPLICATE`, `OTHER`). Nothing is erased in either case.
- **No automatic expiry or retries**: there are no codes, attempt counters, or time limits. Time passing never verifies a request (FR-018b analogue for deletion).

**Rationale**: The WhatsApp association links the request to the records without collecting new personal data, which fits Principle IV and FR-024. Human review gives a decision that can be recorded and audited, and it avoids a model or chat message deciding erasure. The association is not legal identity proof, so the residual risk is recorded in plan.md and stays under the legal review (FR-047).

**Alternatives considered and rejected**:
- One-time code sent to the lead's email address. Withdrawn: it needs an email address that customers do not have to give, it adds a customer-facing email type (OI-2 excluded from the MVP), and it gives no proof of legal identity.
- Email link. Same objections, plus a browser step for the customer.
- Identity-document upload. Prohibited by FR-024.

**Dependency**: none on email addresses or customer-facing messages. Deadlines, backup handling, and legal exceptions remain open under FR-026b(7) and FR-047.

---

## R-010: Business calendar

**Decision**: A pure module (`src/salesagent/business_calendar/`) with these functions:
- `is_business_time(instant)`: converts the instant to `America/Costa_Rica` using `zoneinfo`, then checks weekday, hour (07:00 inclusive to 17:00 exclusive), and whether the date is a holiday or closure.
- `holidays_for(year)`: merges the configured national holiday list for the year with the movable holidays for that year. Holy Thursday is Easter minus 3 days and Good Friday is Easter minus 2 days, computed with `dateutil.easter`.
- `closures_for(date)`: configured business-specific closures.

Holiday data lives in `config/calendar/<year>.yml` (fixed-date holidays only; movable holidays are calculated). A startup check fails in production if the configured year does not cover the current date, which prompts an update before holidays are missed. The MTSS list itself is loaded only after verification against the official source (production gate).

**Rationale**: Satisfies FR-040 to FR-040d without hardcoding years. Using `zoneinfo` with the IANA identifier avoids ambiguous "CST" references. Pure functions make the holiday and hour rules straightforward to test with fixed instants.

**Alternatives considered**: A third-party holiday library (may not match the MTSS official list for Costa Rica; the spec requires MTSS as the authority, so the list must be verified directly). Hardcoded dates (prohibited).

**Test approach**: Table-driven tests covering boundaries at 06:59, 07:00, 16:59, and 17:00; weekend days; each holiday for two years; Holy Thursday and Good Friday across leap and non-leap years; a holiday falling on a weekend (not moved); a closure on a normal weekday.

---

## R-011: Language detection and variant selection

**Decision**: The model returns a language variant (`es-CR`, `en`, `pt-BR`, or `unknown`) with a confidence value as part of the structured extraction output. Code applies a deterministic threshold: below the threshold, or `unknown`, the assistant sends the approved language-selection message (FR-035). Explicit customer choices ("en español", "in English", "em português") override detection and are matched deterministically. The chosen variant is stored on the conversation and used for all approved templates.

**Rationale**: The model handles informal, mixed-language messages well. Deterministic override and threshold rules keep the outcome predictable and testable (Principle V). The threshold value is set during implementation with a labeled test set.

**Alternatives considered**: A separate language-identification library (weak on short messages and on the Spanish-Portuguese boundary, which is the main risk). Detection on the first message only (rejected: FR-034 requires switching).

---

## R-012: Qualification engine

**Decision**: A pure function in `src/salesagent/qualification/` takes the lead record and the validated category match and returns one of: `QUALIFIED`, `NOT_QUALIFIED(reason)`, or `NEEDS_INFO(missing_fields)`. The rules are exactly FR-013 (a) to (d):
- (a) the matched category is one of the six approved categories (checked against the catalog, not the model's text);
- (b) problem description and project scope are both present and non-empty;
- (c) preferred contact method is present;
- (d) the start-within estimate is known and is 3 months or less.

If (d) is unknown, the state is `NEEDS_INFO`, and the next question asks about timing. The estimate is an integer months value extracted by the model and validated by schema; a value outside 0 to 36 is treated as unknown.

**Rationale**: Qualification is a business decision, so it must be deterministic and auditable (Principle V). Separating the rules from the orchestration makes them easy to test exhaustively.

**Alternatives considered**: Asking the model to decide qualification (prohibited by Principle V and FR-044). Adding a budget minimum (not in the approved rules; FR-013 forbids it).

---

## R-013: Outbound guard

**Decision**: Every outbound customer message, whether drafted by the model or taken from a template, passes through `src/salesagent/guard/` before it is sent. The guard performs these checks and blocks the message on any failure:
1. **Price and money patterns**: currency symbols and codes (for example `$`, `€`, `₡`, `R$`, `USD`, `CRC`, `BRL`, `colones`, `reais`), amounts with separators, percentage signs, and words for discounts or prices in es, en, and pt.
2. **Commitment patterns**: date and time expressions that could be read as delivery dates, and commitment phrases in es, en, and pt (for example "te entrego el", "we will deliver", "garantizamos", "garantimos", "fechamos").
3. **Catalog citations**: every service claim in a model draft must cite catalog entry IDs. Each cited ID must exist and be APPROVED. A draft with an uncited or unapproved claim is blocked.
4. **Template integrity**: a template-sourced message must match an APPROVED template in the customer's variant.
5. **Length and content limits**: messages above a set length are blocked and escalated, since long drafts are more likely to contain unverified claims.

A blocked message is replaced by the approved fallback (FR-030), a validation-failure event is logged without the message content, and Rafael is notified when the block involves a commercial or claim issue.

**Rationale**: FR-043 requires enforcement independent of the model. Patterns plus citation rules catch the common failure modes. The guard is tested with a shared fixture set of positive and negative examples in all three languages (SC-009, SC-010).

**Limits**: The guard cannot prove that every free-text sentence is true. Residual risk is listed in the plan and is measured in the pilot.

**Alternatives considered**: A second model call as a judge (valid later; it is itself model output and cannot replace deterministic checks, so it may only add a review signal).

---

## R-014: Catalog format and approval

**Decision**: Each service is one Markdown file under `knowledge/services/` with YAML front matter: `id` (stable identifier, the category), `status` (`approved` or `draft`), `version`, `approved_by`, `approved_on`, and `languages` (the variants Rafael has approved content for). The body contains the required sections from the spec: description, customer problems addressed, supported technologies, scope and limitations, verified experience and portfolio references, and FAQ. The catalog loader rejects any file that contains a field named `price`, `precio`, `preço`, or `tarifa`, and rejects a file missing `approved_by` when `status` is `approved`. Production loads only `approved` entries. Changes are made through version-controlled commits reviewed by Rafael.

**Rationale**: The schema makes the catalog the enforceable single source of truth (FR-006) and keeps prices out of it (Principle III). Version control gives an audit trail of approvals.

**Alternatives considered**: A CMS or admin editor (explicitly excluded by the spec). A database table for the catalog (adds an editing surface and a second source of truth; excluded in the spec's MVP scope).

---

## R-015: Standard message templates and approval enforcement

**Decision**: Each standard message is one YAML file under `content/messages/<variant>/`, keyed by message ID (greeting, AI identification, business hours, handoff acknowledgment, out-of-hours handoff, pricing refusal, multimedia notice, privacy notice, deletion acknowledgment, deletion completion, language selection, fallback, closing). Each file has `status` (`DRAFT` or `APPROVED`), `version`, `approved_by`, and `approved_on`. The loader returns only `APPROVED` templates when the application runs in production mode (`SALESAGENT_ENV=production`). In production, the startup check fails if any required message ID is missing or DRAFT in any of the three variants.

Translations generated by a model are written as DRAFT. Nothing becomes APPROVED except by a commit that Rafael makes with his approval recorded in the file.

**Rationale**: Satisfies FR-050 to FR-053 and makes the approval gate enforced by the code, not just by process. The fail-closed startup check prevents an unapproved message from reaching customers.

**Alternatives considered**: A review workflow inside the admin interface (scope creep for the MVP; the repository history already records approval).

---

## R-016: Concurrency, idempotency, and ordering

**Decision**:
- Inbound messages are stored once. The platform message ID is unique in the database. A repeated webhook delivery is acknowledged and ignored.
- The worker takes a row lock on the conversation (`SELECT ... FOR UPDATE`) before processing any message for it. Messages for one conversation are processed in arrival order; messages for different conversations proceed in parallel.
- Outbound sends record an attempt before calling the platform and update the record afterward. A send that times out is retried only if the platform confirms the message was not accepted; otherwise the attempt is marked for review. This avoids duplicate replies.
- The worker processes messages from a queue table with `status`, `attempts`, and `next_attempt_at`, so a crash does not lose messages (FR-031).

**Rationale**: Covers the edge case of quick successive messages and the requirement that no acknowledged message is lost. Using the database as the queue avoids a message broker, consistent with Principle X.

**Alternatives considered**: A message broker such as Redis or RabbitMQ (more components, not justified for the expected volume). In-memory queues (lose messages on restart).

---

## R-017: Hosting and deployment

**Decision**: Docker Compose on one host, with three containers: `web` (Django under a production WSGI or ASGI server), `worker` (the `process_inbox` command), and `db` (PostgreSQL). A reverse proxy terminates HTTPS and is the only public entry point; the database is not exposed. A scheduled job (host cron or the `worker` container's scheduler) runs the retention job and the calendar-integrity check daily.

**Rationale**: Meets the HTTPS requirement of the WhatsApp webhook with minimal moving parts (Principle X). A single host keeps data-location decisions to one place for the legal review.

**Open decision (legal)**: The host's physical location and provider must be chosen during the legal review (FR-047), because it determines where personal data is stored and processed. The plan does not select a hosting provider. This is a production gate.

**Alternatives considered**: A managed platform-as-a-service (simpler operations, but the data location and processor contract need review first). Kubernetes (not justified for one operator).

---

## R-018: Logging and PII masking

**Decision**: Structured JSON logs with a fixed set of event names (for example `inbound.received`, `control.transition`, `guard.blocked`, `notification.failed`, `deletion.completed`). Phone numbers and email addresses are never logged in plain text; they are logged as a keyed hash (HMAC with a secret from configuration) so events can be correlated without exposing the value. Message bodies are never logged at INFO or above. A logging filter removes any configured secret value. Errors include an error code and a correlation ID.

**Rationale**: Principle VI requires logs that are useful for diagnosis and free of sensitive information. Keyed hashes allow correlating events for one customer without storing identifiers in logs.

**Alternatives considered**: Plain-text identifiers in logs (violates Principle VI). No correlation (hard to diagnose delivery failures, which FR-019 requires recording).

---

## R-019: Version control and repository setup

**Decision (owner decision on OI-3, 2026-11-18)**: The existing project directory is initialized as a Git repository. The feature branch `001-whatsapp-sales-agent` is created. The root `.gitignore` excludes Python bytecode and caches, virtual environments, `.env` and other environment files (with `.env.example` kept), secrets and credential files, local databases and dumps, Docker local overrides, temporary and editor files, and per-user Claude settings. Spec Kit artifacts are tracked. Nothing is committed or pushed by the setup, and no remote is configured.

**Rationale**: FR-048 and Principle IV require the repository to be under version control with secrets excluded. Initializing the existing directory keeps all Spec Kit artifacts in place. Pushing needs a separate authorization.

**Verification performed**: the staged candidate set contains no `.env`, key, credential, or database file. Spec Kit's machine-local `feature.json` is ignored by its own `.specify/.gitignore`.

**Open items**: confirm the GitHub repository's visibility and reconcile with the separate clone `whatsapp_freelance_sales_agent-1` (which has an `origin` and one commit) before any push. Run a secret scan of the full history before the first push.

## Summary of Decisions Affecting Production

| Decision | Production consequence |
|---|---|
| R-005 model provider | Processor contract and international transfer review (FR-047) |
| R-006 SES region | Determines where email content is processed (FR-047) |
| R-010 holiday list | MTSS verification before go-live (FR-040b) |
| R-014 and R-015 approvals | Catalog and templates must be APPROVED before production (FR-051, FR-052) |
| R-017 hosting location | Storage location of personal data (FR-047) |
| R-009 verification | Human verification by Rafael; deadlines and backup handling await FR-047 |
| R-005 model costs and processing | Cost measurement and processor review before production (plan Production Gate 6) |

## Items Not Resolved by Research

- Exact rate-limit thresholds and idle timeouts (set during implementation).
- Language-confidence threshold (set during implementation with a labeled test set).
- Hosting provider and SES region (legal review).
- Deadlines for processing deletion requests, and the authorized backup and processor deletion procedure (FR-026b(7), FR-047).
- Concrete additional-verification checks for suspicious deletion requests. The principle is set in FR-026b(3); the checks are chosen case by case by Rafael.
