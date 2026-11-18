# M0 validation record: WhatsApp connectivity

**Status**: automated checks passed. The live Meta test (T135) has **not** been run, because it needs the owner's Meta developer app, test number, and temporary HTTPS callback.

**Date of automated run**: 2026-11-18. **Environment**: Python 3.12 (uv venv), Django 5.2, PostgreSQL 16 (local container), gunicorn. All data synthetic (reserved 555-01xx numbers, fake message IDs, test-only secrets).

## Automated results

| Check | Result |
|---|---|
| `pytest` (29 tests: settings, logging masking, signature, GET challenge, duplicate delivery, M0 flow, purge) | 29 passed |
| Mutation: signature check removed | caught (1 test fails) |
| Mutation: M0 allowlist gate removed | caught (1 test fails) |
| Mutation: pre-check for duplicates removed | not caught by a test, which is expected: the unique database constraint and the `IntegrityError` handler still enforce it |
| Local smoke under gunicorn: GET challenge echoed | pass |
| Local smoke: signed POST from allowlisted synthetic number | 200, one message stored |
| Local smoke: unsigned POST | 403, nothing stored |
| Local smoke: raw test number in server log | none |
| Local smoke: purge command after run | removed the test row |
| Docker image build (`deploy/Dockerfile`) | built; runs as non-root user `app`; no `.env` in image |
| `docker compose config` (`deploy/docker-compose.yml`) | valid; services `db`, `web`, `worker`; no published ports |

## Acceptance criteria (tasks.md, Milestone M0)

| # | Criterion | Automated | Live Meta |
|---|---|---|---|
| 1 | Webhook verification succeeds only with the correct token | pass (T128) | pending |
| 2 | Signed text from allowlisted number: 200, one message, one queue item | pass (T130) | pending |
| 3 | Unsigned or wrongly signed POST: 403, nothing stored | pass (T027, T130) | pending |
| 4 | Duplicate delivery: no second message or reply | pass (T129) | pending |
| 5 | Worker sends the fixed text and Meta accepts it | pass with fake sender (T130) | pending |
| 6 | Non-allowlisted sender: not stored, not answered | pass (T130) | pending |
| 7 | Media: stored as `UNSUPPORTED_MEDIA`, no body, no fetch, no reply | pass (T130) | pending |
| 8 | AI package never loaded during M0 | pass (T130) | n/a |
| 9 | Purge removes test rows, prints counts only | pass (T133) | pending |

## Known deviations and limits

- The Graph API version is a configuration value. It is not pinned in code. Check the current version in Meta's documentation before the live run.
- `contact_ref` is stored in plain text for the M0 reply only, and only for allowlisted test numbers. Host-level encryption is a production gate (T141).
- Sending uses the standard library HTTP client, so no new dependency was added. Tests replace the sender, and an autouse fixture blocks all network access during tests.
- Implementation and tests were written in the same session. The mutation checks above show the key tests fail when the protected behavior is removed.
- No live message has been sent to Meta or to any number.
