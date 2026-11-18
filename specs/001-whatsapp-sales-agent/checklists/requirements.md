# Specification Quality Checklist: WhatsApp Freelance Sales Agent (MVP)

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-15
**Last Validated**: 2026-11-17 (iteration 5)
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs). Architecture requirements (FR-043 to FR-046, FR-018d, FR-048) state outcomes and constraints, not technologies or providers.
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable (SC-001 to SC-019)
- [x] Success criteria are technology-agnostic
- [x] All acceptance scenarios defined, including pricing override (US5-4), handoff resumption (US3-4), and deletion workflow (US6)
- [x] Edge cases identified: out-of-hours and holidays, HUMAN_HANDOFF silence, multimedia, model-drafted prices, unauthenticated admin access, unverified deletion, unapproved templates
- [x] Scope bounded (FR-028, FR-029; admin interface limited by FR-018d(e))
- [x] Dependencies and assumptions identified

## Constitution Alignment (v1.0.1)

- [x] Principle I (human-controlled sales): FR-021 to FR-023; FR-026a prevents email from authorizing commitments or deletion
- [x] Principle II (no hallucinated capabilities): FR-006, FR-007, FR-032
- [x] Principle III (human-exclusive pricing): FR-020, FR-038, FR-039, FR-053 (no template may state a price), SC-005, SC-009
- [x] Principle IV (privacy and security): FR-024, FR-025, FR-026, FR-026b, FR-047, FR-048; SC-017, SC-018
- [x] Principle V (deterministic logic): FR-013, FR-018b, FR-040c, FR-044
- [x] Principle VI (observability): FR-018c (no message content in control records), FR-019, FR-046; deletion audit minimal (FR-026b(8))
- [x] Principle VII (human handoff): FR-015, FR-018, FR-018a, FR-042; SC-011
- [x] Principle VIII (test-driven quality): SC-004, SC-005, SC-009 to SC-011, SC-014, SC-016, SC-017
- [x] Principle IX (modular architecture): FR-043 to FR-046; module split left to planning
- [x] Principle X (MVP-first): admin limited to what is needed; no CRM or dashboard; WhatsApp notifications excluded

## Feature Readiness

- [x] All functional requirements have acceptance or success criteria
- [x] User scenarios cover all primary flows in the three language variants
- [x] Success criteria are measurable and map to requirements
- [x] No implementation details leak into the specification

## Design Decisions Deferred to `/speckit-plan`

- [x] Administrator sign-in method, session policy, and CSRF approach (FR-018d): Django password authentication with TOTP, research R-008
- [x] Requester verification for deletion requests (FR-026b(3)): human verification by Rafael, based on the WhatsApp association, with proportionate additional verification. No customer email code (round 6, OI-1, R-009)
- [ ] Backup and processor-held data handling for deletion (FR-026b(7)), dependent on the legal review
- [x] Email provider (FR-048): Amazon SES over authenticated SMTP. Secret store chosen at deployment (R-007)
- [ ] Holiday calendar load, verification, and annual update process (FR-040b, FR-040c)

## Review Gates (must be cleared before the stated milestone)

- [ ] **Before production with real customer data**: Legal Review 3a complete, with findings and corrective actions documented (FR-047). Not complete. No legal compliance may be claimed until then.
- [ ] **Before production**: every standard message approved by Rafael in es-CR, English, and pt-BR; no DRAFT template in use (FR-051, FR-052). Currently all templates are DRAFT.
- [ ] **Before go-live**: MTSS holiday calendar loaded and verified against the official source for the operating years, with closures configured (FR-040b to FR-040d).

## Notes

- Iteration 1: qualification rules, notifications, retention resolved.
- Iteration 2: catalog and pricing decisions (Open Questions 4 and 10).
- Iteration 3: Open Questions 5 to 9 and FR-026a; Legal Review 3a recorded as a gate; alignment with Constitution v1.0.1.
- Iteration 4: business hours, holidays, and out-of-hours handling (FR-040 to FR-042, SC-014, SC-015).
- Iteration 5 (this revision): administrative handoff control with AI_ACTIVE and HUMAN_HANDOFF states (FR-018 to FR-018e, SC-011, SC-016); controlled deletion workflow (FR-026, FR-026b, US6, SC-017); environment-based secrets and `.env.example` (FR-048, SC-018); three language variants (FR-033); standard-message governance (FR-050 to FR-053, SC-019). The deletion verification procedure and the admin sign-in method remain open design decisions.
- Interpretation to confirm: an out-of-hours handoff request moves the conversation to HUMAN_HANDOFF (required by FR-018), which suspends automation until Rafael resumes it. This is the only reading that satisfies FR-042's "change only what the handoff requires."
- Numbering: FR-049 is intentionally unused, so that FR-050 to FR-053 keep their numbers from the earlier draft references.
- Iteration 6 (2026-11-18): project-owner decisions on OI-1 (human-verified deletion, no customer email code), OI-2 (no customer verification email in the MVP), and OI-3 (Git repository and feature branch, no push). Approved technology stack recorded in plan.md. FR-026a, FR-026b, data-model, contracts, quickstart S10 and S14, and research R-009 and R-019 updated to match. `/speckit-tasks` not run.
