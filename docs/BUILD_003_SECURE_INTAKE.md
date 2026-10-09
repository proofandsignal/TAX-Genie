# BUILD-003: Secure intake — technical pilot only

## Demonstrated in code
- FastAPI endpoints for creating/retrieving/deleting cases and uploading PDF documents.
- Per-tenant bearer-token authentication from deployment secrets; constant-time token comparison.
- Per-tenant case/documents isolation in SQL queries. Out-of-tenant references return 404.
- Strict 5 MiB size cap, 20-page PDF cap, basic parser validation.
- AES-GCM encrypted PDF blobs, authenticated with tenant/case/document IDs as AAD.
- SHA256 evidence fingerprint and document metadata in case output.
- PDF selectable-text detection. **No OCR, no invoice field extraction, no tax eligibility assessment.**
- Human-review-only case status and API tests.
- Deletion endpoint for active records.

## Run locally (test/synthetic documents ONLY)
```bash
python -m pip install -r requirements.txt
export TAX_GENIE_DATABASE=/secure/private/tax-genie.db
export TAX_GENIE_AES_KEY_B64="$(python -c 'import os,base64;print(base64.b64encode(os.urandom(32)).decode())')"
export TAX_GENIE_TENANT_TOKENS_JSON='{"pilot":"REPLACE_WITH_32_OR_MORE_RANDOM_CHARACTERS"}'
uvicorn tax_genie.api:application_from_env --factory --host 127.0.0.1 --port 8000
python -m unittest discover -s tests -v
```

## Production blockers — do NOT deploy with real client documents yet
- No HTTPS reverse proxy, request rate limits, abuse prevention or security audit.
- No enterprise-grade identity provider, token rotation, RBAC, MFA or managed secrets.
- No audited key rotation, backups, disaster recovery, deletion of database backups/WAL.
- No persistent audit trail, consent workflow, customer data export or retention policy.
- pypdf is NOT an antivirus/sandbox; malware screening and safe document processing needed.
- PDF parsing is in-process; isolate uploads in a resource-limited worker for production.
- No data processing agreements, DPIA/privacy review or jurisdiction-specific legal sign-off.
- SQLite is local pilot only; switch to production database with tenant isolation controls.
- API is intentionally bound to loopback in local run instructions.
- No customer-facing auto-filing or legal conclusions.

## BUILD-004 gates
Confidential security review, private deployment with transport security, object storage/key management, real identity, privacy/legal signoff. Then scoped document field extraction, field-level source provenance and a qualified-human verification workflow.
