# BUILD-022 — Tax Genie Pilot Screen v0.3 / Operations

Status: **DRAFT ONLY** — no merge, Cloudflare deployment or public update performed.
Repository: `proofandsignal/TAX-Genie`. Branch: `build/022-pilot-screen-v03`.
Existing BUILD-021 external fixture review remains a separate, blocked PR.

## Customer-facing improvements

- Copy a synthetic research summary **only on explicit click**; no real invoices, VAT IDs, company names or personal information are accepted.
- Print / save a synthetic scenario with an explicit no-eligibility/no-recovery warning.
- Reset sample values and validate malformed VAT input (including excess decimal places).
- Include selected expense category in the result as **NOT VERIFIED**, rather than silently ignoring the selection.
- Year choices roll forward with calendar year (only hypothetical and current research periods).
- Clearer route / status explanation, case-level evidence checklist, and 3 linked primary official sources.
- Keep fixed EN-only copy, mobile responsive view, no accounts, no upload, no backend, no third-party scripts, `noindex` and `connect-src 'none'`.

## Internal administration / support (not a public admin login)

Do NOT create an unprotected administrator route or a public dashboard of leads.
Keep a private operational board in approved systems, tracking:
`FIRST_SEEN → SOURCE_VERIFIED → CONTACT_VERIFIED → USER_CONFIRMED_SENT → REPLY → DISCOVERY → PILOT_INTEREST → PAID`.
Preserve `USER CONFIRMED SENT → DO NOT RESEND`. Payhawk and Spendesk were user-confirmed SENT; do not re-contact as new leads.
Capture only non-sensitive commercial metadata and references, never invoice/PII payloads in GitHub.

For each pilot release:
1. Confirm explicit user/human approval before deployment to `taxgenie.proofandsignal.xyz`.
2. Confirm exactly `index.html`, `_headers`, `health.txt` at the root of the static Pages deployment. Never deploy `worker.mjs` as a Pages asset (prior 404 root cause).
3. Run synthetic browser and negative tests; review actual published `/health.txt` and root URL with HTTP 200; verify custom domain and certificate.
4. Check from desktop and Android; country pair, annual/short threshold, expired general deadline, malformed input, reset, copy, print, mailto.
5. Do not allow copy/print/feedback to claim country-specific VAT restrictions or recoverable sums.
6. Keep `noindex`, CSP `connect-src 'none'` and analytics disabled until privacy/analytics QA and approval. Do not add tracking pixels or silent data transfer.
7. Inspect client feedback manually. Count replies, qualified need, actual usage and payments separately. Public traffic is not proof of customer value.

## Scope limits and critical gates

- The v0.3 UI does NOT implement Verification Agent, VIES, EN16931 validation, national rule packs, live rule update monitoring or claim determination.
- Same-country scenarios are explicitly refused as a route under Directive 2008/9/EC.
- EU-wide €400 / €50 thresholds and 30 September deadlines are reference information only. Always check country-specific rules, currencies, exceptions and current legal applicability.
- **No expert review sign-off or legal audit is implied by passing technical tests.**
- Keep BUILD-021 draft and merge locked. BUILD-022 is a separate draft with its own QA and approval gate.
- No Cloudflare changes, real documents, money movement, client invoice handling or paid API usage in this build.
