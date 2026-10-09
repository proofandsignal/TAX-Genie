# Architecture and release stages

## Boundaries
TAX-Genie is completely independent from all other repositories. External lead-discovery services may integrate only through versioned APIs, not code copying or cross-repo commits.

## Pipeline
1. Intake/consent service — jurisdiction, applicant type, expense category, document metadata.
2. Document processing adapter — secure object store, malware scan, OCR with redaction and retention policy (not yet implemented).
3. Extraction validator — typed amount/currency/date, confidence and provenance.
4. Versioned jurisdiction rules — reviewed sources, effective/expiry dates, eligibility conditions, exceptions.
5. Decision service — deterministic NOT_ASSESSED / REVIEW_REQUIRED / candidate after rule verification.
6. Evidence checklist — missing data and reviewer questions.
7. Case management/audit — append-only events, restricted access, GDPR export/deletion paths.
8. Partner review — human decision and approved preparation/filing.
9. Outcome journal — permitted claim status and actual recovery, never predictive guarantees.

## Planned tech stack
Python 3.12 API (FastAPI after dependencies approved), PostgreSQL with row-scoped tenant isolation, object storage encryption, background workers, provider-agnostic LLM adapter gated behind sourced rules. Frontend: Next.js when the backend contract is stable. Start stdlib-only to keep BUILD-001 auditable.

## Threat model / controls
- Taxpayer ID and invoice PII are sensitive; never place in this public repository, logs or sample fixtures.
- No direct government account credentials; no unsupervised filing or payments.
- Minimize document retention; encrypt at rest/in transit; role-based access, separation of tenants, audit logs.
- Prompt injection in uploaded documents cannot change rules, tool permissions or case status.
- For every legal conclusion require rule_id, jurisdiction, effective date, reliable source URL and human approval.
- Need external qualified legal/privacy review for each market and AI-specific compliance obligations before production.

## Milestones
- BUILD-001: isolated project, deterministic triage and tests (this PR).
- BUILD-002: validated rule registry + sourced cross-border VAT case fixtures.
- BUILD-003: secure intake, tenant auth, evidence handling.
- BUILD-004: agent-assisted draft preparation gated by human review.
- BUILD-005: private pilot + metrics + pricing.
- BUILD-006: hardened deployment and monitoring.

**No declared compliance until independently checked.**
