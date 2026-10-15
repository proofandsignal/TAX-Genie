# BUILD-017 — External custody connector (NOT activated)

## Code
Optional S3 Object Lock COMPLIANCE-mode storage adapter with explicit retention acknowledgement, object-version-specific receipts, exact-version retrieval and content digest checks. Synthetic mock tests cover readback, tampering and retention refusal.

**Not deployed**: no object store, credentials, billing or IAM roles configured. Not all S3-compatible services implement versioning and Object Lock; unsupported backends MUST fail closed. Object Lock cannot substitute for independent governance, KMS key policy, retention decisions and external review.

## Minimum provider evidence before any activation
1. Independent AWS account or equivalent Object Lock-capable provider and private, versioned bucket with Object Lock configured at creation; COMPLIANCE mode enforced.
2. Separate restricted IAM writer and read-only auditor; deny delete, policy mutations and overwrite where supported. Retain receipt/version outside application DB, monitor missing writes.
3. KMS-managed keys, separate signing and encryption key domains, revocation/rotation rehearsals, controlled secret injection and incident recovery.
4. Confirm lawful retention period with privacy counsel (365 days currently illustrative only), no raw taxpayer identifiers in third-party checkpoint content and jurisdiction review.
5. Execute live **synthetic-only** put/read/retention tests, check durable receipt, rejection of wrong permissions, audit provider access logs, and capture evidence.

## Non-negotiable status
External custody production integration: BLOCKED until provider access, signed security review, and a synthetic end-to-end deployment test.
Production IAM, protected PDF worker, real malware scanner: BLOCKED.
GDPR/DPIA, DE→FR VAT specialist review (PR #2), independent extraction benchmark, real PAPER 50: BLOCKED.
Customer documents and public launch: BLOCKED.
