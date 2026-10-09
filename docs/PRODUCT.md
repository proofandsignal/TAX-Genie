# Tax Genie — Product definition (BUILD-001)

## Objective
International B2B-first software that helps discover **potential** recoverable taxes and fees, organize evidence, and prepare cases for qualified human review.

## Initial wedge
EU cross-border business VAT on documented foreign business expenses. **Country-to-country eligibility rules require sourced expert review before production claims.** UK tax overpayment discovery is a separate future module. Bulgaria is not a target market.

## Product workflow
Consent and intake → encrypted document storage (future) → extraction → validation → jurisdiction-specific versioned rules → opportunity assessment → evidence and deadline checklist → human review → claim preparation → partner-led filing → outcome journal.

## BUILD-001 scope
- Deterministic, offline, data-minimal opportunity triage.
- Explicit results: REVIEW_REQUIRED / NOT_ASSESSED (never an unsupported ELIGIBLE).
- Synthetic fixture and runnable unit tests.
- No OCR, LLM, payment provider, lead scraping, submissions, refund calculations or live legal advice in this build.

## User roles
- Business submitter: provides documents and explicit consent.
- Operator: checks data accuracy, case states and audit record.
- Qualified tax reviewer: verifies applicable legislation, evidence, deadlines and permitted services.
- Partner accountant: handles regulated preparation or submissions when needed.

## 50-case pilot gates
- 50 consented or synthetic cases with known ground truth; separate synthetic vs real results.
- Zero fabricated legal citations and zero autonomous filings.
- Extraction accuracy, false-positive rate, missing-evidence recall and reviewer minutes per case tracked.
- At least five expert/customer discovery interviews before charging.
- No release or paid launch until privacy, legal scope, source provenance and security checks pass.

## Lead discovery
Use only independently verified public B2B signals (conference exhibitors, cross-border operations, accounting practices). Signals indicate fit, **not** an established refund claim. Record source URL, collected date, justification, outreach permissions and opt-out. No scraping behind logins; GDPR/ePrivacy/UK PECR legal review before country launches.

## Monetization hypotheses
Free preliminary screening; paid evidence-backed recovery assessment; accountant seat-based subscription. Validate willingness to pay, servicing cost and regulatory boundaries. Do not imply guaranteed recovery.
