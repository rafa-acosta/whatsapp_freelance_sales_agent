# Contract: Content Files (Catalog and Standard Messages)

**Direction**: Rafael (author and approver) → repository → application at startup and on load
**Owner**: `src/salesagent/catalog/` and `src/salesagent/messages/`
**Related**: R-014, R-015, FR-006, FR-032, FR-050 to FR-053, Principle III

These files are the only source of service claims and customer-facing standard wording. Changes are version-controlled commits. Rafael approves each change.

## Catalog entry: `knowledge/services/<category-id>.md`

### Front matter (required)

```yaml
id: private-ai-rag            # one of the six approved category IDs
status: approved              # approved | draft
version: 1                    # integer, incremented on every approved change
approved_by: "Rafael"         # required when status is approved
approved_on: 2026-11-18       # ISO date, required when status is approved
languages: [es-CR, en, pt-BR] # variants with approved content
```

Allowed category IDs (the six from FR-005):
`private-ai-rag`, `ai-agents-automation`, `python-automation`, `network-automation-compliance`, `network-monitoring-automation`, `powerbi-analytics`.

### Required body sections (in this order)

1. Description
2. Customer problems addressed
3. Supported technologies
4. Scope and limitations
5. Verified experience and portfolio references
6. Frequently asked questions

### Validation (loader rejects the file on any failure)

- Front matter parses and all required keys are present.
- `id` is one of the six allowed IDs, and matches the file name.
- `status: approved` requires `approved_by` and `approved_on`.
- No front-matter key or body heading named `price`, `precio`, `preço`, `tarifa`, `cost`, `costo`, or `custo` (Principle III). The body may mention that pricing is by quotation, using the standard wording.
- Every section heading is present.

### Citation format used by the model

The model cites an entry by `id` and section number (for example `private-ai-rag#2`). The guard checks that the cited `id` exists, is `approved`, and includes the requested `languages` variant (R-013).

## Standard message: `content/messages/<variant>/<message_id>.yml`

`<variant>` is one of `es-CR`, `en`, `pt-BR`.

### Format

```yaml
message_id: handoff_ack       # from the required set
variant: es-CR
status: APPROVED              # DRAFT | APPROVED
version: 1
approved_by: "Rafael"         # required when APPROVED
approved_on: 2026-11-18       # required when APPROVED
text: |
  Gracias. Ya le pasé su solicitud a Rafael, quien le responderá personalmente.
```

### Required message IDs

`greeting`, `ai_identification`, `business_hours`, `handoff_ack`, `out_of_hours_handoff`, `pricing_refusal`, `multimedia_notice`, `privacy_notice`, `deletion_ack`, `deletion_completed`, `language_selection`, `fallback`, and `closing`. No deletion verification code template exists (OI-2).

### Validation

- Exactly one file per required ID per variant. Missing or duplicate files fail the startup check.
- `status` is `DRAFT` or `APPROVED`. In production (`SALESAGENT_ENV=production`), any required ID that is `DRAFT` in any variant fails the startup check (FR-051).
- `APPROVED` requires `approved_by` and `approved_on`.
- The `text` must pass the guard's template checks: no price patterns, no commitment patterns (R-013).
- `pricing_refusal` must not contain any number, currency term, or date (FR-020).

### Translation rule

A model-generated translation is written with `status: DRAFT` and a `translated_from` key pointing to the approved source variant. It stays DRAFT until Rafael reviews it and changes the status himself in a commit (FR-052). The application never changes a status.

### Consistency rule

Commercial, privacy, and escalation messages must carry the same meaning across the three variants (FR-036, FR-053). The reviewer checks this by reading the variants side by side; the MVP does not automate meaning comparison.
