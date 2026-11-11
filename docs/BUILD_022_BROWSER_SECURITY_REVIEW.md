# BUILD-022 — Internal Browser, Tax-Claims & Security Review (v0.3)

**Scope:** `site/taxgenie-screen-pilot` static research-only UI in Draft PR #22.
**Review type:** internal code/automated-browser review, **not** independent security, privacy or VAT-legal signoff.
**Deployment:** NOT PERFORMED. The custom domain continues to serve the separately uploaded v0.2.1 pilot.

## Test and evidence plan

The standard GitHub Actions `Tax Genie Tests` workflow runs:
- Existing Python unit tests and negative tests, including locked invoice/ingress tests.
- `node tests/browser_qa_v03.cjs`, which starts an actual installed headless Chromium browser, navigates to the repository v0.3 HTML and exercises live DOM events (not a mocked DOM).
- Headless test cases: 27-country selection, synthetic €1,200 annual scenario, €50/€400 *legal reference* display, no inferred refund threshold from charged VAT, same-country warning, invalid/negative numbers, hypothetical expense treatment, business-status warning, explicit non-recovery summary, Reset, contact mailto and 390px mobile horizontal-overflow check. CSS and JS assets must load in Chromium.
- Additional cases cover a valid remainder-of-year period and expiry warnings. Actual Android/Samsung visual QA and **public HTTPS browser QA** are separate tasks after deployment.

## Source-backed legal wording review

Official legal reference: Directive 2008/9/EC, Articles 15–17,
`https://eur-lex.europa.eu/eli/dir/2008/9/oj`.
- Article 15: ordinary submission deadline 30 September after the refund period.
- Article 16: ordinary periods at least 3 months and no longer than a calendar year, with a remainder-of-year exception.
- Article 17: minimum **VAT refund requested** of €400 (qualifying shorter period) or €50 (calendar year or remaining portion), or equivalent national currency. This differs from VAT charged: comparing the pilot's charged VAT input against these amounts would be an invalid eligibility conclusion and was removed.
- **These are application-level references; they do not establish any amount refundable to a particular business.**
- National expense restrictions, right to deduct, applicable national law and exceptions are **unverified**. The screen refuses same-country use of the Directive 2008/9 route and explicitly returns `NOT ASSESSED` for eligibility/recoverable VAT.

## Internal static security inspection

Confirmed in v0.3 source:
- No form, file input, live invoice intake, account login, server-side processing, tracking pixel, external script, network fetch/XHR, client-side storage or dynamic code execution.
- Scenario output is written with `textContent`, not `innerHTML`.
- Only outgoing contact action is a user-initiated `mailto:` link; official legal links open with `noopener noreferrer`.
- Pages `_headers` includes `X-Robots-Tag: noindex`, a restrictive `Content-Security-Policy` with `connect-src 'none'`, clickjacking and MIME-sniffing controls.
- HTML also uses `noindex,nofollow`; there are no cookie banners or tracking features because analytics is **disabled**.
- CSS and JavaScript have now been externalized to `assets/style.css` and `assets/app.js`. The CSP uses `script-src 'self'` and `style-src 'self'`, with no `unsafe-inline` directives. No external security audit has assessed this release.
- The browser suite loads the branch HTML locally; it does not prove that Cloudflare actually serves the correct `_headers` or production content.

## Commercial / admin boundaries

- No public admin portal without authenticated roles, privacy review and audit logging.
- Keep pilot feedback and leads in approved private tools; never commit names, documents or contact details to this public repo.
- Payhawk and Spendesk contacts were user-confirmed as sent; do not resend without explicit new reason. A lack of reply is not a refusal.
- Track `VERIFIED INTEREST → DISCOVERY → QUALIFIED NEED → PAID PILOT → NET REVENUE` separately from traffic.
- Do not market this UI as a VAT refund estimator or qualified country-by-country eligibility engine.

## Outstanding gates

1. PR #22 final HEAD automated CI + headless Chromium PASS.
2. Independent security/quality review or explicitly documented human release approval.
3. Explicit user authorization for any merge and **separate** authorization before touching Pages Production.
4. Production deployment of **CI-verified** Pages ZIP with root assets (`index.html`, `_headers`, `health.txt`, `assets/style.css`, `assets/app.js`) to existing project only. Do not upload the surrounding GitHub artifact ZIP; extract the inner `taxgenie-pages-v03.zip` first. Deployment is manual because no Cloudflare management connector is available.
5. Live custom-domain HTTP 200 and response-headers check, full functional desktop/Android QA.
6. Privacy-friendly analytics approval, `noindex` decision and B2B discovery testing.

The unrelated BUILD-021 research PR remains Draft, subject to external fixture review. Real invoices, country-specific VAT recovery claims, filings and paid services remain locked.
