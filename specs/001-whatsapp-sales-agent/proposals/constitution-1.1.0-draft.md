# Proposed Constitution Amendment: Version 1.1.0 (DRAFT, not applied)

**Status**: Proposed. Not applied to `.specify/memory/constitution.md`. Requires approval by the project owner (Rafael) under the Governance amendment procedure.
**Proposed by**: Specification review, 2026-11-18
**Current version**: 1.0.1
**Proposed version**: 1.1.0 (MINOR: new rules that materially expand guidance, per the Versioning Policy)

## Rationale

Two rules required by the approved specification are not yet stated in the constitution:

1. Automation must resume only through an explicit, authenticated human action. Nothing may resume it through elapsed time, customer inactivity, or model output. The specification (FR-018a, FR-018b) requires this; the constitution does not.
2. Personal data deletion must be completed through a verified, authorized procedure, and the customer must not be told it is complete until it has actually completed. The specification (FR-026, FR-026b) requires this; the constitution's Principle IV covers deletion only "where the platform and law require it."

Both rules are safety-relevant, so they belong in the constitution rather than only in the feature spec.

## Proposed change 1: Principle VII (Human Handoff), add the following paragraph after the existing text

> Automation MUST resume only through an explicit, authenticated action by the business owner, recorded as an authorization event. Elapsed time, customer inactivity, customer messages, retrieved documents, and language model output MUST NOT resume automation or change a conversation's control state. Human handoff management MUST be reachable only through authenticated, access-controlled, CSRF-protected administrative functions.

## Proposed change 2: Principle IV (Privacy and Security), replace the final sentence

Current text:

> Customers MUST be able to request deletion of their data where the platform and law require it.

Proposed text:

> Customers MUST be able to request deletion of their personal information. Each request MUST be registered, verified by a defined procedure before any action, authorized by the business owner, and carried out through a controlled, audited workflow. A chat message alone MUST NOT trigger erasure. Customers MUST NOT be told that deletion is complete until it has actually completed. Legal exceptions and mandatory retention obligations MUST be validated before production use.

## Proposed change 3: Versioning and metadata

- Version line: `**Version**: 1.1.0 | **Ratified**: 2026-11-15 | **Last Amended**: <date of approval>`
- Sync Impact Report: record the change from 1.0.1 to 1.1.0, the two modified principle paragraphs, and "no principles removed."

## What this does not change

- No existing principle is removed or redefinition-changed in meaning. The proposal adds constraints; it does not relax any.
- Principles I, II, III, V, VI, VIII, IX, and X are unchanged.
- The Versioning Policy's MINOR classification applies because new rules are added.

## Decision requested

- [ ] Approve as drafted
- [ ] Approve with changes (specify)
- [ ] Reject; keep the rules in the feature specification only
