# BUILD-004 — Document Intelligence / Evidence Candidates

## Implemented
- Deterministic **candidate** field extraction from selectable PDF text on invoice-like documents.
- Explicitly labeled invoice number, invoice date, supplier VAT ID/country, currency, VAT and total amount.
- 1-based original text-line provenance for each extracted candidate.
- Flags for missing/conflicting data, future invoice dates, VAT amount exceeding total.
- Integrated in existing encrypted upload pipeline. Tenant isolation inherited from BUILD-003.
- Does NOT send invoice content to an external AI provider. No OCR or AI inference yet.

## Known constraints
This is **not** a general-purpose multilingual invoice reader. Only exact labels in English and limited French are supported, dot-decimal figures only. VAT IDs are **format hints only** and are not VIES-verified. No country inference from VAT ID, no deductibility conclusion, no amounts recovered, no automatic filing. AI extraction will require strict source provenance, tenant privacy protections and evaluation before activation. Qualitative confidence must not be fabricated.

## PAPER 50 — benchmark definition before testing
- 50 anonymized/consented invoice cases (or synthetic only if none consented), held securely outside GitHub.
- Freeze expected field values, reviewer labels and extraction logic before evaluating.
- Track per-field precision/recall and exact match, missing flags, conflicts, false positives, PDF failures, runtime.
- Keep synthetic and real evidence in separate reporting buckets.
- Tax reviewers assess legal eligibility separately after vetted jurisdiction rules exist.
- No personal financial documents in the public repository or PRs.
