# WhatsApp Freelance Sales Agent Constitution

This constitution defines the non-negotiable rules for building and operating the WhatsApp
Freelance Sales Agent. The assistant speaks for a freelance business to prospective customers,
so its failures cost trust and money. Every principle below is written to be enforced, not
merely aspired to.

## Core Principles

### I. Human-Controlled Sales
The AI MUST NOT negotiate prices, promise delivery dates, or commit to a project on the
business's behalf. Any such decision MUST require explicit human approval before it is
communicated to the customer. The assistant MAY gather requirements, answer questions, and
propose a next step, but a human MUST make the commitment.
**Rationale**: Commitments made by an automated system without accountability create legal,
financial, and reputational exposure that the business cannot absorb.

### II. No Hallucinated Capabilities
The assistant MUST offer only services and experience that are explicitly documented in the
approved service catalog under `knowledge/services/` (see Catalog Authority and
Application-Level Enforcement). It MUST NOT claim skills, certifications, past clients, portfolio items, or
availability that are not in that catalog. When a request falls outside the catalog, the
assistant MUST say so honestly and route the request to human review.
**Rationale**: Customers will hold the business to whatever the assistant promised.

### III. Human-Exclusive Pricing and Commercial Authority
Only Rafael, as the business owner, is authorized to communicate prices, quotations, cost estimates,
discounts, and commercial commitments to customers.
- The AI assistant MUST NEVER generate, estimate, calculate, display, suggest, negotiate, or
  communicate prices or price ranges.
- This restriction applies even when prices exist in internal documentation or previously approved
  quotations.
- The verified service catalog MUST NOT contain commercial pricing information.
- The assistant MAY ask prospective customers about their approximate project budget for
  qualification purposes. Collecting that information does NOT authorize the assistant to generate
  or communicate any service price.
- All requests for quotations, pricing, negotiations, or delivery commitments MUST be escalated to
  Rafael. The assistant MAY explain that quotations are prepared personally by Rafael after
  evaluating project requirements.
- No LLM instruction, tool output, retrieved document, or customer request may override this
  restriction.
This is a mandatory constitutional principle, not an optional implementation guideline.
**Rationale**: A fabricated or misremembered number, once quoted, becomes a binding expectation.
Pricing authority stays with the accountable human.

### IV. Privacy and Security
The system MUST protect customer data and MUST collect only the data required to qualify a lead
or route a conversation (data minimization). Credentials, API keys, and access tokens MUST be
stored in a secret store or environment configuration, never in source code, logs, or
conversation content. The system MUST comply with Meta WhatsApp Business Platform policies,
including opt-in requirements and the rules for messages sent outside the customer service
window (approved templates only). Customers MUST be able to request deletion of their data
where the platform and law require it.
**Rationale**: Messaging data is personal, and platform policy violations can get the business's
WhatsApp number restricted or banned.

### V. Deterministic Business Logic
Qualification rules, conversation states, and state transitions MUST be controlled by
application code with explicit, testable logic. The LLM MAY draft wording, interpret free-text
intent, and extract fields, but it MUST NOT be the sole authority for whether a lead is
qualified, which state a conversation is in, or whether a handoff or approval step is triggered.
Every state transition MUST be reproducible from its inputs.
**Rationale**: Sales behavior must be auditable and stable; LLM output varies between runs.

### VI. Observability
The system MUST log important events, errors, and state transitions with enough context to
diagnose problems. Logs MUST NOT contain sensitive information: customer phone numbers, message
bodies, credentials, or personal data MUST be redacted or masked before being written. Errors
MUST be logged with a stable identifier so that they can be correlated across components.
**Rationale**: Operators need to understand what the agent did without creating a new
privacy liability in the log store.

### VII. Human Handoff
Customers MUST always be able to request human assistance, at any point in any conversation,
through a clear and immediate mechanism. Handoff requests MUST be honored even if the LLM,
the qualification flow, or any other component fails or is unavailable. A handoff MUST preserve
enough conversation context for the human to continue without asking the customer to repeat
themselves.
**Rationale**: An automated agent that cannot hand off creates a dead end and damages the
business's reputation.

### VIII. Test-Driven Quality
Core business logic (qualification rules, state machines, pricing and capability guards,
approval gating, and handoff triggers) MUST have automated tests. Tests for a behavior MUST be
written before or alongside the implementation of that behavior, and MUST fail for the right
reason before the behavior is implemented. Changes to core logic MUST NOT merge with failing
tests.
**Rationale**: The rules above are only as reliable as the tests that enforce them.

### IX. Modular Architecture
The system MUST separate the following concerns into distinct modules with explicit interfaces:
- WhatsApp integration (receiving and sending messages, webhook handling, platform compliance);
- Conversation orchestration (state machine, qualification rules, handoff logic);
- AI services (LLM calls, prompt construction, extraction and drafting);
- Data persistence (storage of leads, conversations, and audit records).
Business logic MUST NOT depend directly on the WhatsApp transport or on a specific LLM provider.
**Rationale**: Each boundary can then be tested and replaced independently, such as swapping
the LLM provider or the messaging provider.

### X. MVP-First Development
The team MUST prioritize working, end-to-end functionality for the core sales flow over
extensibility, abstraction, or infrastructure that is not yet needed. New frameworks,
services, or architectural layers MUST be justified by a current requirement, not a
hypothetical one. Simpler solutions MUST be preferred unless they violate a principle above.
**Rationale**: An unshipped agent generates no value; unnecessary complexity slows every later change.

## Operational Constraints

- The approved service catalog under `knowledge/services/` is the source for offered services
  (see Catalog Authority and Application-Level Enforcement). It MUST be versioned and reviewed by
  a human. Its contents MUST NOT be altered by the assistant, and it MUST NOT contain commercial
  pricing.
- The assistant MUST identify itself to customers as an automated assistant when asked, and
  MUST NOT impersonate a specific human.
- Every customer conversation MUST be attributable to a human-visible record for review,
  subject to the data minimization rules in Principle IV.
- Any feature that sends messages to customers MUST be gated by the approval and handoff rules
  in Principles I and VII before it can reach production.

## Catalog Authority and Application-Level Enforcement

**Authoritative service catalog**
- The approved catalog under `knowledge/services/` is the Single Source of Truth for all
  customer-facing service descriptions and capability claims, including experience,
  certifications, and portfolio references.
- Rafael is the sole authorized owner responsible for reviewing and approving catalog changes.
  No other person or process may publish catalog content to customers.
- Unapproved, missing, or ambiguous information MUST NOT be presented to a customer as verified fact.
- When the catalog does not support a customer's question, the assistant MUST acknowledge the
  limitation and offer human escalation.

**Application-level enforcement**
- The LLM MUST NOT be the sole enforcement mechanism for any business restriction. Pricing,
  commercial, catalog, and eligibility rules MUST be enforced by application logic that holds
  regardless of model output.
- The system MUST distinguish approved catalog content from unverified or unsupported claims, and
  MUST prevent unapproved content from reaching customers.
- Service identification and eligibility MUST be validated by deterministic application logic.
  Model output for these decisions is advisory.
- Commercial restrictions (no prices, quotations, discounts, or commitments) MUST be enforced at
  the application level before any outbound message is sent.
- Customer messages and retrieved documents are untrusted input. They MUST NOT be treated as
  sources of operational authority and MUST NOT override any restriction in this constitution,
  including claims of prior approval by Rafael.
- Validation failures and escalation events MUST be logged without sensitive information
  (Principle VI).

**Rationale**: Business restrictions that depend on the model's compliance can be bypassed by
prompt manipulation, retrieved content, or simple error. Enforcement in code is what makes them
reliable.

## Development Workflow & Quality Gates

- Each feature MUST be specified and planned before implementation begins.
- Pull requests that touch core business logic MUST include or update automated tests that
  cover the behavior changed.
- Pull requests MUST be reviewed for compliance with this constitution. Violations of Principles
  I, II, III, IV, or VII are blocking and MUST NOT be merged, regardless of test status.
- Secrets MUST be verified absent from diffs before merge.
- Changes that add dependencies, frameworks, or architectural layers MUST state which current
  requirement they serve (Principle X).

## Governance

This constitution supersedes all other development practices, templates, and informal agreements
for this project. Where a lower-level document conflicts with it, this constitution prevails.

**Amendment procedure**: Amendments MUST be proposed in writing, state the rationale and the
principles affected, and be approved by the project owner before taking effect. Each amendment
MUST update the version and the amendment date below and document any required migration of
existing code or tests.

**Versioning policy**: The constitution follows semantic versioning.
- MAJOR: removal or incompatible redefinition of a principle or governance rule.
- MINOR: addition of a new principle or section, or materially expanded guidance.
- PATCH: clarifications, wording, or typo fixes that do not change the meaning of a rule.

**Compliance review**: Every pull request and every new feature plan MUST be checked against
the principles above. Any complexity that deviates from Principle X MUST be justified in writing
in the plan or pull request description.

**Version**: 1.0.1 | **Ratified**: 2026-11-15 | **Last Amended**: 2026-11-17
