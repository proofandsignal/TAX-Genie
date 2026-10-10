# PAPER 50 — Frozen evaluation contract

PAPER 50 is an invoice **field extraction** benchmark, not a VAT refund prediction experiment.

- 50 unique cases per locked evaluation with id, dataset, text and independently verified truth labels.
- Datasets: synthetic or consented_real. Report them separately, never blend accuracy.
- No real invoice documents or taxpayer identifiers in public GitHub.
- Source field accuracy metrics: TP/FP/FN/TN, precision, recall and whole-document exact match.
- Ground truth must be blinded to candidate output. Freeze cohort and code revision before scoring.
- Null denominators are reported as null, not assumed to be perfect.
- Target thresholds for future review: precision >=95%, recall >=90%, zero invented refund eligibility claims.
- These targets are hypotheses, not achieved results. No 50-case evaluation has been run.
- Adapter defaults to OCR-disabled, and a reviewed provider is necessary to process scans.
- No external model transfers or production rollout before security, privacy and legal review.
