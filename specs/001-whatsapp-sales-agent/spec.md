# Feature Specification: WhatsApp Freelance Sales Agent (MVP)

**Feature Branch**: `001-whatsapp-sales-agent` (created in the Git repository initialized 2026-11-18; not pushed to any remote)

**Created**: 2026-11-15

**Last Updated**: 2026-11-18 (clarification round 6: OI-1 deletion verification by human review, OI-2 no customer verification email, OI-3 Git repository, approved technology stack; aligned with Constitution v1.0.1)

**Status**: Draft. Ready for `/speckit-plan` once the design decisions and review gates listed below are accepted for planning. Production use is gated (see FR-047 and FR-051).

**Input**: User description: "Conversational sales assistant that helps Rafael promote his freelance services through WhatsApp, understand prospective customers' needs, qualify sales opportunities, and transfer qualified leads to Rafael for personal follow-up."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start a Conversation and Find the Right Service (Priority: P1)

A prospective customer sends a first message to Rafael's WhatsApp number in Spanish, English, or Portuguese. The assistant introduces itself as Rafael's AI sales assistant, listens to the customer's problem in natural language, and identifies the most relevant service category from the approved catalog (Private AI and RAG, AI agents and workflow automation, Python automation, network automation and configuration compliance, network monitoring automation, Power BI and data analytics). It answers questions only with information that is verified and documented in the catalog.

**Why this priority**: This is the entry point of every sales conversation. Without a clear introduction and accurate service matching, no lead can be qualified, so it delivers the core value on its own.

**Independent Test**: Send a first message describing a business problem from a test phone to the assistant; confirm the reply identifies the assistant as AI, is in the customer's language, names the relevant service category, and contains no information absent from the approved catalog.

**Acceptance Scenarios**:

1. **Given** a customer has never messaged before, **When** they send their first message, **Then** the reply states that the assistant is Rafael's AI sales assistant before any other content, using an APPROVED greeting template (FR-051).
2. **Given** a customer describes a problem such as "we want our internal documents searchable with an AI chatbot", **When** the assistant processes the message, **Then** it identifies the Private AI and RAG solutions category and asks at least one relevant follow-up question.
3. **Given** a customer asks about a service that is not in the catalog, **When** the assistant responds, **Then** it says the service is not among those offered and offers to pass the request to Rafael, without claiming any capability.
4. **Given** a customer asks a factual question about Rafael's experience or certifications, **When** the approved catalog does not contain the answer, **Then** the assistant says it does not have that information and offers human follow-up.

---

### User Story 2 - Qualify a Lead and Hand It to Rafael (Priority: P1)

Through natural conversation, the assistant collects the essential lead information: the customer's name, company or business (if applicable), problem description, project scope, urgency, preferred contact method, and optionally an approximate budget in free text. Once enough information is gathered, it produces a structured opportunity summary and evaluates whether the lead is qualified under Rafael's explicit criteria. Rafael is then notified by email so he can follow up personally.

**Why this priority**: This is the business outcome the product exists for: turning inbound conversations into opportunities Rafael can act on. It is the second half of the minimum viable product, together with US1.

**Independent Test**: Run a complete scripted conversation with a test customer who provides every required field; confirm a structured summary is produced containing all collected fields, the qualification outcome is recorded, and Rafael receives the email notification.

**Acceptance Scenarios**:

1. **Given** a customer has provided a name, problem, scope, urgency, and preferred contact method, **When** the assistant has collected these, **Then** it produces a structured opportunity summary containing each field and marks any optional field (company, budget) as "not provided" if the customer did not give it.
2. **Given** a lead meets all qualification criteria in FR-013, **When** the qualification is determined, **Then** Rafael is notified by email and the opportunity appears in the summary record for his review.
3. **Given** a lead fails any qualification criterion in FR-013, **When** the qualification is determined, **Then** the lead is recorded as not qualified with the failed criterion as the reason, and the customer is told politely that Rafael will review the request.
4. **Given** the customer declines to give a budget, **When** the assistant continues, **Then** it does not repeat the budget question and the conversation proceeds to the next missing field.
5. **Given** the customer has already given their name earlier in the conversation, **When** the assistant reaches the contact step, **Then** it does not ask for the name again.

---

### User Story 3 - Request Human Assistance at Any Time (Priority: P1)

At any point in a conversation, the customer can ask to speak with Rafael or a person. The assistant stops automated qualification, confirms the request to the customer, notifies Rafael by email with the necessary context, and moves the conversation to HUMAN_HANDOFF. The assistant does not resume autonomous responses until Rafael explicitly resumes automation through the authenticated administration interface (see FR-018a). Outside business hours, on weekends, or on holidays, the request is registered and Rafael is notified for review during the next working period (see FR-042).

**Why this priority**: Handoff is a mandatory safeguard. A customer who cannot reach a human is a failure of the product regardless of how well the rest works.

**Independent Test**: In the middle of a qualification conversation, send "I want to talk to a person"; confirm the assistant acknowledges the request, an email reaches Rafael with the necessary context, the conversation is in HUMAN_HANDOFF, and the assistant stops asking qualification questions.

**Acceptance Scenarios**:

1. **Given** a customer is in the middle of qualification, **When** they write a request for a human (in any wording that clearly asks for a person), **Then** the assistant confirms that the request was passed to Rafael and asks no further qualification questions.
2. **Given** a customer requests a human, **When** Rafael is notified, **Then** the notification includes the information needed to identify and process the request, and Rafael can continue the conversation without the customer repeating themselves (the full history is available to him in the administration interface, not in the email).
3. **Given** a conversation is in HUMAN_HANDOFF, **When** the customer sends further messages, **Then** the assistant does not respond autonomously, does not commit to anything, and records the messages for Rafael.
4. **Given** a conversation is in HUMAN_HANDOFF, **When** Rafael resumes automation through the administration interface, **Then** the conversation returns to AI_ACTIVE, the authorization and the state transition are recorded, and the prior context is preserved.

---

### User Story 4 - Continue a Conversation Across Sessions (Priority: P2)

A customer returns to the conversation hours or days later. The assistant recalls the context of the earlier exchange (the service of interest, the information already collected, and open questions) and continues from there rather than starting over. Conversations are kept for the retention periods in FR-025.

**Why this priority**: Freelance sales cycles are long, and customers often reply after a delay. Continuity improves the experience and reduces repeated questions, but the MVP still delivers value without it.

**Independent Test**: Hold a conversation, end it, and resume the next day from the same phone number; confirm the assistant references previously collected information and asks only for what is still missing.

**Acceptance Scenarios**:

1. **Given** a customer previously shared a project scope and urgency, **When** they return with a new message, **Then** the assistant refers to the known information and asks only for missing fields.
2. **Given** a customer's earlier qualification was completed, **When** they send a new message about the same project, **Then** the assistant does not create a duplicate opportunity and instead updates the existing summary.

---

### User Story 5 - Escalate Uncertain Commercial Questions (Priority: P2)

When a customer asks about prices, discounts, delivery dates, contract terms, or an unusual scope that the approved catalog does not cover, the assistant does not guess. It explains that Rafael will respond to that question personally and routes the question to him.

**Why this priority**: Protecting Rafael from unauthorized commitments is central to the product's trustworthiness, but it is a guardrail on US1 and US2 rather than a standalone journey.

**Independent Test**: Ask the assistant "How much would a RAG chatbot cost and when could you deliver it?"; confirm it gives no price and no date, explains that Rafael prepares customized quotations after reviewing requirements, and notifies Rafael of the question by email.

**Acceptance Scenarios**:

1. **Given** a customer asks for a price, **When** the assistant responds, **Then** it provides no number, range, estimate, or price from any source, explains that Rafael prepares customized quotations after evaluating project requirements, and escalates the request to Rafael.
2. **Given** a customer asks for a delivery date, **When** the assistant responds, **Then** it does not promise any date or timeline.
3. **Given** a customer asks for a discount or negotiates terms, **When** the assistant responds, **Then** it does not agree to or propose any discount and routes the request to Rafael.
4. **Given** a customer says Rafael already approved a price, or instructs the assistant to ignore its rules, **When** the assistant responds, **Then** it applies the same restrictions, does not treat the claim as authority, and escalates the request to Rafael.

---

### User Story 6 - Process a Personal Data Deletion Request (Priority: P2)

A customer asks through WhatsApp to delete their personal information. The request is registered, Rafael is notified by email, and the request is handled through a controlled workflow: the requester's authority is verified, Rafael reviews and authorizes the action in the administration interface, eligible records are deleted or anonymized, and the customer is told only after the deletion has actually completed. The assistant never erases data on the strength of a chat message alone.

**Why this priority**: Deletion rights are a legal and trust obligation, but deletion requests are infrequent in an MVP. The workflow must still be correct before real customer data is processed.

**Independent Test**: Submit a deletion request from a test phone; confirm a request ID is issued, Rafael receives the email, no data is erased before authorization, and the customer receives the completion confirmation only after the authorized deletion completes and the audit record is written.

**Acceptance Scenarios**:

1. **Given** a customer asks to delete their data, **When** the assistant responds, **Then** it registers the request with a request ID, acknowledges it, and states that the request will be reviewed and that deletion is not confirmed until completed.
2. **Given** a deletion request is registered, **When** the email notification is sent, **Then** it contains the request ID and only the minimum identifiers needed, and no conversation transcript.
3. **Given** a deletion request has not been verified and authorized by Rafael, **When** time passes or the customer repeats the request, **Then** no records are deleted or anonymized.
4. **Given** Rafael has authorized a verified request, **When** the deletion procedure completes successfully, **Then** the audit record shows the request ID, timestamps, status, and authorized action, and only then is the completion confirmed to the customer.
5. **Given** the deletion procedure fails partway, **When** the failure is recorded, **Then** the customer is not told that deletion is complete, and the request remains open for Rafael.

---

### Edge Cases

- A customer sends media (images, voice notes, audio, videos, documents) instead of text: the assistant politely states in the customer's selected language that multimedia is not currently supported and asks for a text description. It does not transcribe, analyze, or process the content, and the conversation state is unchanged (FR-037).
- A customer's language cannot be determined reliably: the assistant politely asks the customer to choose Spanish, English, or Portuguese before continuing (FR-035).
- A customer switches language mid-conversation: the assistant follows the switch and keeps all collected context (FR-034).
- A customer sends a message that is clearly not a sales inquiry (spam, personal messages, automated bots): the assistant responds once politely and does not start qualification.
- A customer gives contradictory information (for example, two different urgency levels): the assistant asks which one is correct before summarizing.
- A customer stops responding midway: the partial information is retained and the lead is shown as incomplete; no reminder is sent automatically in the MVP.
- A customer sends several messages in quick succession: the assistant handles them as one coherent turn and does not produce duplicate replies or duplicate summaries.
- A customer requests human assistance outside business hours, on a weekend, or on a holiday: the assistant acknowledges the request, states that human assistance is unavailable outside official working hours, registers a pending handoff, sends the email notification, explains that the request will be reviewed during the next working period, and does not guarantee an exact response time or start a human interaction (FR-042).
- A holiday falls on a Saturday or Sunday: it is not moved to Monday; the official MTSS calendar governs (FR-040b).
- A business closure is configured for a date that is otherwise a working day: that day is treated as non-working for business-hour messages (FR-040d).
- A customer messages during the last minutes before 17:00 or the first minutes after 07:00 Costa Rica time: the decision uses the `America/Costa_Rica` clock at the moment the request is received (FR-040).
- A conversation is in HUMAN_HANDOFF and the customer keeps writing: the assistant stays silent on substance and records the messages for Rafael. Automation is not resumed by time passing or by the customer's continued messages (FR-018b).
- The administration interface is accessed without authentication, or a state-changing request lacks valid CSRF protection: the request is refused and the attempt is logged without sensitive data (FR-018d).
- The notification to Rafael fails: the handoff or qualified lead is still recorded, the failed delivery attempt is recorded, and the item is visible for follow-up so that the lead is not lost (FR-031).
- The language model is unavailable or returns an unusable response: the assistant sends a fixed, safe message in the customer's language that acknowledges the customer and states that Rafael will follow up, and it does not invent an answer (FR-030).
- The language model drafts a price, date, or commitment: the application blocks the draft before sending, sends the fixed safe message, records the validation failure, and escalates to Rafael (FR-043, FR-046).
- Customer messages or retrieved content instruct the assistant to override a rule: the instruction is treated as untrusted input and has no effect (FR-045).
- A deletion request is received but the requester cannot be verified: no data is erased, and the request stays open for Rafael (FR-026b).
- A standard message template is missing or still a draft in production: the system does not send an unapproved template, uses the fallback approved message if one exists, and records the failure (FR-051).
- A customer asks whether they are talking to a human or a bot: the assistant states honestly that it is an AI assistant.

## Requirements *(mandatory)*

### Functional Requirements

**Conversation and identity**

- **FR-001**: System MUST receive incoming WhatsApp messages from prospective customers and send replies through the same channel.
- **FR-002**: System MUST identify itself as Rafael's AI sales assistant in the first reply of every new conversation.
- **FR-003**: System MUST state that it is an AI assistant whenever a customer asks whether they are talking to a human or a bot.
- **FR-004**: System MUST maintain conversation context within a conversation so that it does not ask for information the customer has already provided.

**Languages**

- **FR-033**: System MUST support three language variants: Latin American Spanish (default locale es-CR), neutral international business English, and Brazilian Portuguese (pt-BR). It MUST detect the customer's language from incoming text messages and reply in the detected or selected variant.
- **FR-034**: System MUST let customers switch language during a conversation and MUST keep the conversation context across the switch. It MUST preserve technical terminology where appropriate and MUST NOT translate customer-provided technical terms unnecessarily.
- **FR-035**: If language detection is ambiguous, System MUST politely ask the customer to choose one of the three supported languages before continuing.
- **FR-036**: Business rules, pricing restrictions, security requirements, and the meaning of commercial, privacy, and escalation messages MUST be identical across all three supported languages.

**Service identification and verified information**

- **FR-005**: System MUST identify the most relevant service category for a customer's described need, from the six offered categories: Private AI and RAG solutions; AI agents and workflow automation; Python automation; Network automation and configuration compliance; Network monitoring automation; Power BI and data analytics.
- **FR-006**: System MUST answer questions about services, experience, and certifications only using the approved service catalog stored as Markdown files under `knowledge/services/`, which is the Single Source of Truth for these claims (see Service Catalog Entry).
- **FR-007**: System MUST NOT state or imply any service, experience, certification, past client, or availability that is absent from the approved catalog.
- **FR-008**: System MUST tell the customer clearly when a request falls outside the offered services or when the answer is not in the approved catalog, and MUST offer to pass the question to Rafael.
- **FR-032**: System MUST use only approved catalog content in customer-facing responses. When catalog information is unavailable or ambiguous, System MUST acknowledge the limitation to the customer and offer human escalation.

**Qualification and lead capture**

- **FR-009**: System MUST ask qualification questions that are relevant to the identified service and to the information still missing.
- **FR-010**: System MUST collect the following lead information: name (required), business or company name (when applicable), problem description (required), project scope (required), urgency (required), preferred contact method (required), and approximate budget (optional, free text, see FR-038).
- **FR-011**: System MUST NOT repeat a question for information the customer has already provided, and MUST NOT repeatedly ask for an optional field the customer has declined to provide.
- **FR-012**: System MUST generate a structured opportunity summary containing all collected lead information, the identified service category, and the qualification outcome.
- **FR-013**: System MUST determine whether a lead is qualified using the explicit criteria below, and MUST NOT apply any criterion not defined here. A lead is qualified only if all of the following are met:
  (a) the need matches one of the six offered service categories;
  (b) the customer has described a concrete problem and project scope;
  (c) the customer has provided a preferred contact method;
  (d) the customer wants to start within 3 months of first contact.
  A lead that fails any criterion is marked not qualified, with the failed criterion recorded as the reason. No budget minimum and no project-size minimum apply in the MVP.
- **FR-014**: System MUST record the qualification outcome and, for leads that are not qualified, the reason.

**Budget**

- **FR-038**: System MUST collect budget as optional free-text input. It MUST NOT force selection from predefined ranges. It MUST accept approximate amounts, ranges, or descriptive responses; it MUST accept a currency only when the customer explicitly provides one; and it MUST preserve the customer's original budget wording.
- **FR-039**: System MUST NOT use customer budget information to calculate, suggest, or influence any service price. Budget is used for qualification only (see FR-020).

**Multimedia**

- **FR-037**: The MVP supports text messages only. System MUST detect unsupported message types (voice notes, audio, images, videos, documents). It MUST politely inform the customer, in their selected language, that multimedia is not currently supported and ask them to describe their requirements in text. It MUST NOT transcribe, analyze, or process such content, and MUST NOT interrupt or reset the existing conversation state.

**Business hours**

- **FR-040**: Official business hours are Monday through Friday, 07:00 to 17:00 Costa Rica time, time zone America/Costa_Rica (UTC-06:00), equivalent to 13:00 to 23:00 UTC. Saturdays and Sundays are non-working days. System MUST use the IANA identifier `America/Costa_Rica` for all business-day and business-hour calculations and MUST NOT use ambiguous references to "CST" without specifying Costa Rica or UTC-06:00. System MUST communicate the business hours to the customer when relevant, in the customer's selected language.
- **FR-040a**: All officially recognized Costa Rican national public holidays, both mandatory-paid and non-mandatory-paid, are non-working days. This includes Christmas Day (December 25), New Year's Day (January 1), Holy Thursday, Good Friday, and every other officially recognized national holiday.
- **FR-040b**: The official Costa Rican Ministry of Labor (MTSS) holiday calendar is the authoritative reference. A holiday that falls on a weekend MUST NOT be assumed to transfer to Monday; the official calendar governs.
- **FR-040c**: Holiday data MUST be configuration, not code. The system MUST NOT hardcode any single year's holiday dates, MUST support updates when official dates or regulations change, and MUST calculate movable holidays (including Holy Thursday and Good Friday) for each calendar year. Business-day and business-hour determination MUST be deterministic application logic (Principle V).
- **FR-040d**: Business-specific closures MUST be supported as configurable exceptions. They are treated as non-working periods in the same way as holidays.
- **FR-041**: Automated lead qualification MAY continue outside business hours, on weekends, and on holidays.
- **FR-042**: For a human-assistance request received outside business hours (including weekends and holidays), System MUST acknowledge the request, register a pending handoff, send the FR-019 email notification, and clearly inform the customer that human assistance is unavailable outside official working hours and that the request will be reviewed during the next working period. System MUST NOT promise an exact response time and MUST NOT automatically initiate a human interaction. The out-of-hours acknowledgment MUST NOT change or interrupt conversation state beyond what FR-018 requires for a handoff request. All these messages MUST be delivered in the customer's selected language.

**Human handoff and control states**

- **FR-015**: System MUST allow the customer to request human assistance at any point in a conversation, in any clearly worded request.
- **FR-016**: System MUST confirm to the customer when a human-assistance request has been passed to Rafael.
- **FR-017**: System MUST notify Rafael when human intervention is required, including for handoff requests, qualified leads, and commercial questions that require his response, as specified in FR-019 and FR-026a.
- **FR-018**: Every conversation MUST be in exactly one of two control states: AI_ACTIVE or HUMAN_HANDOFF. When a handoff is requested, the conversation MUST move to HUMAN_HANDOFF, all autonomous responses MUST be suspended, and the conversation history and relevant qualification context MUST be preserved.
- **FR-018a**: Rafael MUST be able to pause automation (AI_ACTIVE to HUMAN_HANDOFF) and resume it (HUMAN_HANDOFF to AI_ACTIVE) manually, through the authenticated administration interface in FR-018d. Resumption MUST require an explicit, authenticated action by Rafael.
- **FR-018b**: System MUST NEVER change a conversation's control state based on elapsed time, customer inactivity, customer messages, retrieved documents, or any language model output.
- **FR-018c**: System MUST record every authorization event and every state transition, including the actor, timestamp, previous and new state, and a request reference. These records MUST NOT contain message content. Conversation context MUST be preserved when automation resumes.
- **FR-018d**: Human handoff management MUST be provided through a minimal administration interface, and it MUST meet these requirements:
  (a) Rafael MUST authenticate before any administrative function is available;
  (b) sessions MUST be secure, and access controls MUST restrict every administrative operation to the authenticated administrator;
  (c) state-changing requests MUST be protected against cross-site request forgery;
  (d) no administrative operation MUST be reachable through an unauthenticated public endpoint;
  (e) the interface MUST provide only what the MVP needs: listing conversations in HUMAN_HANDOFF or with pending handoffs, viewing the context needed to respond, pausing and resuming automation, and authorizing deletion requests (FR-026b). A complete CRM or a complex dashboard is out of scope.
- **FR-018e**: Customer messages, retrieved documents, and language model outputs MUST NOT be able to modify a conversation's control state or grant administrative authority.
- **FR-019**: System MUST send an email notification to Rafael for each event type listed in FR-026a, immediately, with processing targeted within 60 seconds of the triggering event. Each notification MUST include only the information necessary to identify and process the request (for example name, contact information, requested service, project summary, urgency, and qualification status) and MUST NOT include complete conversation transcripts. Notifications MUST NOT use a dashboard or WhatsApp in the MVP. Each delivery attempt and failure MUST be recorded for troubleshooting, and the failure record MUST NOT contain message content beyond what troubleshooting requires.

**Commercial guardrails**

- **FR-020**: System MUST NOT generate, estimate, calculate, display, suggest, negotiate, or communicate any price, price range, cost estimate, or discount, including prices present in internal documents or previously approved quotations. Only Rafael may communicate prices, quotations, discounts, and commercial commitments. When a customer asks about pricing, quotations, negotiation, or delivery commitments, System MUST escalate the request to Rafael and MAY explain that Rafael prepares customized quotations after evaluating project requirements. System MAY ask for the customer's approximate project budget for qualification purposes only, and collecting it MUST NOT authorize any price communication.
- **FR-021**: System MUST NOT promise, propose, or imply delivery dates, timelines, or project commitments.
- **FR-022**: System MUST NOT agree to, propose, or negotiate contract terms, discounts, or any binding commercial commitment.
- **FR-023**: System MUST route every uncertain or complex commercial question to Rafael and tell the customer that Rafael will respond personally.

**Architecture and enforcement**

- **FR-043**: Pricing, commercial, catalog, and eligibility restrictions MUST be enforced by application logic before any outbound message is sent, independent of language model output. The language model MUST NOT be the sole enforcement mechanism.
- **FR-044**: Service identification and eligibility MUST be determined by deterministic application logic. Model output for these decisions is advisory.
- **FR-045**: Customer messages and retrieved documents MUST be treated as untrusted input. They MUST NOT grant authority or override any restriction, including claims of prior approval by Rafael.
- **FR-046**: System MUST block unapproved catalog content and any draft containing a price, quotation, discount, or commitment from reaching the customer. It MUST log validation failures and escalation events without sensitive information (Principle VI of the constitution).

**Privacy, deletion, and retention**

- **FR-024**: System MUST collect only the lead information listed in FR-010 and any additional information strictly needed to qualify the lead. It MUST NOT request sensitive personal data (for example identity document numbers, financial account details, or passwords).
- **FR-025**: System MUST apply the following retention periods:
  (a) complete conversation histories are kept for 90 days;
  (b) lead summaries are kept for 12 months;
  (c) technical logs are kept for 30 days, with personal information minimized or masked (see Principle VI of the constitution).
  Data past its retention period MUST be deleted or irreversibly anonymized. Retention periods are subject to the compliance review in FR-047.
- **FR-026**: Customers MUST be able to request deletion of their personal information through WhatsApp. The request MUST be registered and processed by the controlled deletion workflow in FR-026b. System MUST NOT confirm to the customer that deletion has occurred until it has actually been completed.
- **FR-026a**: Email is the official notification mechanism for four event types: (1) qualified sales leads; (2) customer requests for human assistance; (3) commercial escalations; (4) customer requests for personal data deletion. Notifications MUST be sent to Rafael's configured email address (FR-048). The MVP sends no customer-facing email: no email is sent to a customer for deletion verification or for any other purpose. Email notifications MUST NOT independently authorize commercial commitments or data deletion. Each delivery attempt and failure MUST be recorded.
- **FR-026b**: Personal data deletion MUST follow this controlled workflow:
  (1) register the request with a unique request ID and timestamp, and associate it with the customer's WhatsApp identifier and the stored records linked to that identifier (conversation, messages, lead, handoff, and notification records);
  (2) notify Rafael by email (FR-026a), including the request ID and only the minimum identifiers needed;
  (3) Rafael verifies the requester's authority before any action. This is a human decision, recorded in the administration interface (FR-018d) with the verifier's identity and time. Possession of the WhatsApp identifier is not treated as definitive proof of legal identity. If the request is suspicious, concerns information about a third party, or the requester's identity cannot be established, Rafael MUST apply additional verification proportionate to the risk. Additional verification MUST NOT require sensitive personal data (FR-024) or an email address solely for deletion verification. No customer email is used. A chat message, model output, or elapsed time never verifies a request. If verification is not completed, no data is erased, the request stays open, and Rafael decides the next step;
  (4) Rafael reviews the verified request and explicitly authorizes the action through the administration interface (FR-018d);
  (5) identify the applicable records;
  (6) delete or irreversibly anonymize the eligible conversation records and lead information;
  (7) address backups and third-party processor data according to an approved retention and deletion policy (validated under FR-047);
  (8) keep a minimal audit record containing the request ID, timestamps, processing status, and authorized action, without retaining unnecessary personal data;
  (9) confirm completion to the customer only after the procedure has successfully completed.
  System MUST NOT erase customer data automatically based solely on an unverified chat message. Legal exceptions, mandatory retention obligations, and processing deadlines MUST be validated during FR-047.
- **FR-027**: System MUST NOT expose one customer's conversation data or summary to any other customer.
- **FR-047**: Production deployment involving real customer data MUST NOT occur until the legal and privacy compliance review (Legal Review 3a) is completed and its findings and required corrective actions are documented. The review MUST cover: Costa Rican Law 8968 and its regulations; privacy notice and consent requirements; whether database registration obligations apply; third-party processor contracts and international data transfers; retention and deletion procedures, including backups; and Meta WhatsApp Business Platform policies. The project MUST NOT claim legal compliance before this review is complete. Development and testing MAY use synthetic data or explicitly authorized test data before then.
- **FR-048**: Rafael's notification email address and all credentials, API tokens, passwords, and sensitive configuration MUST be supplied through environment-based configuration or a managed secret store. They MUST NOT be hardcoded in source code, committed to version control, or written to logs. The project MUST provide a `.env.example` file with placeholder values only. `.env` and sensitive configuration files MUST be excluded from version control. Credentials MUST be restricted in access and rotatable without code changes. Email delivery MUST use a supported transactional email service or an authenticated SMTP provider over secure transport. The concrete provider is selected during planning.

**Standard messages**

- **FR-050**: All standard customer-facing messages MUST be stored as structured, version-controlled template files. They cover: initial greeting; AI assistant identification; business hours; human handoff acknowledgment; pricing and quotation refusal or escalation; unsupported multimedia responses; privacy notices; data deletion acknowledgments; and conversation closing messages.
- **FR-051**: Each template MUST be explicitly marked DRAFT or APPROVED, with a version and an approval record (approver, version, date). System MUST NOT use a DRAFT template in production.
- **FR-052**: AI-generated translations MUST NOT be treated as approved. Rafael MUST review and explicitly approve every standard message in each of the three language variants (es-CR, English, pt-BR) before production deployment.
- **FR-053**: Templates for commercial, privacy, and escalation content MUST be consistent in meaning across the three language variants (see FR-036). No template may state or imply a price (see FR-020).

**Scope boundaries**

- **FR-028**: System MUST operate only on inbound conversations initiated by the customer; it MUST NOT send unsolicited outbound marketing messages.
- **FR-029**: System MUST NOT process payments, generate proposals or contracts, negotiate autonomously, or integrate with external CRM systems in the MVP.

**Resilience**

- **FR-030**: When the language model is unavailable or produces an unusable response, System MUST send a fixed, safe message in the customer's language that acknowledges the customer and states that Rafael will follow up, and MUST NOT invent a substitute answer. The fallback message MUST be an APPROVED template (FR-051).
- **FR-031**: When a notification to Rafael fails, System MUST retain the handoff request, qualified lead, or deletion request and make it visible for follow-up.

### Key Entities *(include if feature involves data)*

- **Conversation**: A sequence of messages between one prospective customer and the assistant, identified by the customer's WhatsApp contact. Holds the control state (AI_ACTIVE or HUMAN_HANDOFF), the qualification state (for example: new, collecting information, qualified, not qualified), the detected language variant, the collected lead information, and the history needed for follow-up.
- **Lead**: The set of collected business information about a prospective customer: name, company (optional), problem description, project scope, urgency, preferred contact method, and approximate budget (optional, original wording preserved). Belongs to one conversation and can be updated across sessions.
- **Opportunity Summary**: A structured, human-readable record of a lead with identified service category, qualification outcome, reason (if not qualified), and collected fields. Produced for Rafael's review.
- **Service Catalog Entry**: A verified Markdown document under `knowledge/services/`, one per service category, containing: service name and description; customer problems addressed; supported technologies; scope and limitations; verified experience and portfolio references; and frequently asked questions. It is the only source for service-related statements. It is version-controlled and approved and maintained solely by Rafael. It MUST NOT contain commercial pricing information.
- **Handoff and Control Event**: A record of a handoff request, a commercial escalation, a pause or resume of automation, and the actor, timestamp, previous and new state, and request reference. Contains no message content.
- **Deletion Request**: A record with a request ID, registration timestamp, association with the customer's WhatsApp identifier, verification status and verifier (Rafael), Rafael's authorization, processing status, and completion timestamp. Kept as the minimal audit record in FR-026b(8).
- **Message Template**: A versioned standard message in one of the three language variants, with its status (DRAFT or APPROVED) and approval record (FR-051).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of new conversations open with a message that identifies the assistant as an AI sales assistant for Rafael, verified across a test set of at least 50 scripted first messages.
- **SC-002**: At least 85% of test conversations describing one of the six offered service needs are matched to the correct service category on the first or second customer message.
- **SC-003**: In a test set of conversations with complete information, at least 95% of resulting opportunity summaries contain every required field with values matching what the customer provided.
- **SC-004**: 100% of human-assistance requests in test conversations (in at least five different wordings, in each of the three language variants) result in a confirmation to the customer, a conversation in HUMAN_HANDOFF, and an email notification to Rafael within 60 seconds.
- **SC-005**: 0 instances in the commercial-question test set (prices, discounts, delivery dates, contract terms) where the assistant provides a price, price range, date, discount, or binding commitment.
- **SC-006**: 0 instances in the test set where the assistant claims a service, experience, or certification that is absent from the approved catalog.
- **SC-007**: Rafael can review a complete opportunity summary and decide on next steps without reading the full conversation transcript, as confirmed by a review with Rafael using at least 10 test opportunities.
- **SC-008**: A qualified customer who has provided all required fields reaches a completed summary and Rafael notification in no more than 12 customer messages, measured across the scripted test scenarios.
- **SC-009**: 0 price-bearing outputs in an adversarial test set of at least 50 prompts (including attempts to extract prices from documents, claims of prior approval, and instructions to ignore rules), with every blocked draft logged.
- **SC-010**: 100% of drafts containing unapproved catalog claims or commercial commitments in the validation test set are blocked before delivery, with no reliance on model behavior.
- **SC-011**: 0 autonomous customer-facing responses in conversations in HUMAN_HANDOFF, and 0 resumptions of automation without a recorded authenticated authorization.
- **SC-012**: At least 95% of test messages in es-CR, English, and pt-BR receive replies in the detected language variant, and 100% of ambiguous-language cases trigger the language-selection request.
- **SC-013**: 100% of unsupported multimedia messages receive the notice and the text request, with no transcription or change to conversation state.
- **SC-014**: In a calendar test set covering every weekday and weekend day, each holiday configured for at least two different years (including Holy Thursday and Good Friday, calculated per year), and a configured closure, 100% of business-hour decisions are made in `America/Costa_Rica`, and 0 holidays falling on a weekend are moved to Monday.
- **SC-015**: 100% of human-assistance requests received outside business hours, on weekends, or on holidays receive the out-of-hours message in the customer's language, a registered pending handoff, and an email notification, and 0 of those messages promise an exact response time.
- **SC-016**: 0 administrative operations succeed without authentication, and 0 state-changing requests succeed without valid CSRF protection, in the administration test set.
- **SC-017**: 0 personal-data records are deleted or anonymized before Rafael's authorization, and 100% of completed deletions produce an audit record, with the customer confirmation sent only after completion.
- **SC-018**: 0 credentials, tokens, or Rafael's email address are present in source code, committed configuration, or logs, verified by a secrets scan of the repository and log samples.
- **SC-019**: 0 DRAFT templates are used in production, and 100% of production standard messages are APPROVED in the language variant in which they are sent.

## Assumptions

- The target audience is inbound prospects in small and medium businesses, IT departments, technology companies, and professionals seeking AI, automation, networking, or data analytics services.
- The approved service catalog is maintained as version-controlled Markdown under `knowledge/services/` in the project repository. Rafael is the sole owner responsible for approving and maintaining its content.
- The administration interface is minimal and serves one authenticated administrator (Rafael). A complete CRM or dashboard is out of scope for the MVP.
- All prices, quotations, discounts, and delivery commitments are issued only by Rafael after explicit approval.
- Rafael is the sole decision-maker for prices, dates, and commercial commitments; no other team member is involved in the MVP.
- Customers initiate every conversation; outbound follow-up is out of scope.
- The MVP handles text messages only. Multimedia is detected and declined with a request for text (FR-037).
- The success-criteria thresholds (for example 85%, 95%, 12 messages, 60 seconds) are proposed starting targets and have not been confirmed by Rafael.
- Standard messages in es-CR, English, and pt-BR are drafted and then reviewed and approved by Rafael (FR-052). No translation is assumed approved.
- Email is the only operator notification channel in the MVP.
- Business hours and holidays are as stated in FR-040 to FR-040d; holiday data is loaded from configuration and verified against the MTSS source.

## Open Questions and Review Gates

These items are resolved, or held open with a stated reason. Nothing below has been silently converted into an approved requirement.

**Resolved in clarification rounds 1–5**

1. **Qualification rules**: Option B, with a 3-month timing window (FR-013).
2. **Notification channel and response time**: email, within 60 seconds (FR-019, FR-026a).
3. **Data retention**: 90 days for conversations, 12 months for lead summaries, 30 days for technical logs (FR-025). Subject to FR-047.
4. **Verified service catalog**: Markdown under `knowledge/services/`, owned by Rafael (FR-006, FR-032).
5. **Supported languages**: Latin American Spanish (es-CR default), neutral international English, Brazilian Portuguese (pt-BR), with detection, switching, and language selection on ambiguity (FR-033 to FR-036).
6. **Budget input**: optional free text, original wording preserved, currency only when explicitly given, never used for pricing (FR-038, FR-039).
7. **Multimedia**: text only; unsupported media is declined with a text request and does not change conversation state (FR-037).
8. **Business hours and holidays**: Monday to Friday, 07:00 to 17:00 America/Costa_Rica (UTC-06:00). Weekends and MTSS-recognized national holidays are non-working. Holiday data is configuration (FR-040 to FR-040d, FR-041, FR-042).
9. **Handoff authorization**: conversations are AI_ACTIVE or HUMAN_HANDOFF. Rafael pauses and resumes automation through a minimal authenticated administration interface. Resumption requires his explicit action and is recorded. Nothing resumes automation by time or model decision (FR-018 to FR-018e).
10. **Pricing and quotations**: human-exclusive, with application-level enforcement (FR-020, FR-043 to FR-046; Constitution Principle III).
11. **Notification routing**: email for qualified leads, human-assistance requests, commercial escalations, and deletion requests (FR-026a).
12. **Email configuration and secrets**: environment-based configuration or managed secret store; `.env.example` with placeholders; `.env` excluded from version control; no credentials in code or logs; rotatable credentials (FR-048). The concrete provider is chosen in planning.
13. **Deletion procedure**: a nine-step controlled workflow with authority verification, Rafael's authorization, a minimal audit record, and completion-only confirmation (FR-026, FR-026b).
14. **Standard message governance**: version-controlled templates marked DRAFT or APPROVED; no DRAFT in production; AI translations never approved by default; Rafael approves each message in each variant (FR-050 to FR-053).

**Resolved in clarification round 6 (2026-11-18, project-owner decisions on OI-1, OI-2, OI-3)**

15. **Deletion requester verification (OI-1)**: no customer email one-time code. Requests are associated with the customer's WhatsApp identifier and stored records; Rafael verifies the requester's authority in the administration interface; additional proportionate verification applies to suspicious, third-party, or unidentified cases; no email address is required for deletion (FR-026b(1), FR-026b(3)). The WhatsApp association and human authorization procedure is the one the owner approved; it is not a legal identity proof.
16. **Customer verification emails (OI-2)**: excluded from the MVP. FR-026a covers only notifications to Rafael. No customer OTP is generated, delivered, stored, expired, or validated (FR-026a, FR-026b(3)).
17. **Version control (OI-3)**: the project directory is a Git repository on the feature branch `001-whatsapp-sales-agent`, with a `.gitignore` for Python, Django, environment files, virtual environments, local databases, credentials, and temporary files. No remote is configured and nothing is pushed (plan.md, OI-3; research.md, R-019).
18. **Technology stack**: approved as listed in plan.md (Technical Context, "Approved technology stack"): Python 3.12, Django, PostgreSQL, Anthropic API with a configurable model identifier (Claude Sonnet 5.5 initially), Amazon SES, Docker Compose, HTTPS, and administrative password authentication with TOTP.

**Held open: pre-production gate (not complete)**

- **Legal Review 3a (FR-047)**: The compliance review under Law 8968 and its regulations, privacy notice and consent requirements, database registration obligations, processor contracts and international transfers, retention and deletion (including backups), and Meta WhatsApp Business Platform policies. This review has NOT been completed. No legal compliance is claimed. Production with real customer data is blocked until the review's findings and corrective actions are documented.
- **Statutory deadlines and exceptions for deletion (FR-026b, FR-047)**: legal exceptions, mandatory retention obligations, and deadlines are unknown until the review is complete.
- **Model provider and email processing (FR-047)**: the Anthropic API and Amazon SES process customer content. Their processor terms, transfer exposure, and the SES region are legal-review items. Actual LLM costs and data-processing implications must be evaluated before production (plan, Production Gates).

**Decided in planning (see plan.md and research.md)**

- **Administrator authentication (FR-018d)**: Django password authentication with a TOTP second factor (`django-otp`), secure sessions, and CSRF middleware (R-008).
- **Requester verification for deletion (FR-026b(3))**: human verification by Rafael, as recorded in clarification round 6. Parameters are in research R-009. The earlier email-code option is withdrawn.
- **Email provider (FR-048)**: Amazon SES over authenticated SMTP with TLS; the provider and region are configuration (R-006, R-007). The secret store is the host's secret store or environment injection, chosen at deployment.

**Held open: technical and legal items**

- **Backup handling for deletion (FR-026b(7))**: the approved retention and deletion policy for backups and processor-held data depends on the legal review.
- **Holiday calendar maintenance (FR-040b, FR-040c)**: how the MTSS calendar is loaded, verified, and updated each year, and whether the MTSS list includes conditional or one-off days that need explicit handling. The calendar is not enumerated in this spec.

**Held open: content (not architecture)**

- **Standard message wording**: drafts must be written and approved by Rafael in es-CR, English, and pt-BR before go-live (FR-051 to FR-052). Until then, all templates are DRAFT.
