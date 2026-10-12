# BUILD-002 — EU VAT source and evidence contract

**Pilot pair:** business established in Germany (DE), VAT incurred in France (FR). Target segment: international B2B / accountants. No Bulgarian commercial rollout.

## Source hierarchy
1. Binding law and official EU texts (Directive 2008/9/EC Article 15).
2. EU Your Europe business portal.
3. France's tax authority for foreign EU business VAT refund procedures.
4. Qualified local tax specialist for deductibility, exceptions, updated procedural details.

Reviewed **2026-10-09** for procedural discovery only. Not signed off by licensed tax adviser. Sources must be rechecked before production use. Never treat general EU guidance as a guarantee of French VAT deductibility.

- EU legal text: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32008L0009
- EU guidance: https://europa.eu/youreurope/business/taxation/vat/vat-refunds/index_en.htm
- French official guidance: https://www.impots.gouv.fr/international-professionnel/vat-refunds

## Required evidence before any eligibility opinion
- Company/VAT status, home-country establishment and authorization.
- Full source invoices and credit notes (kept **outside** GitHub).
- Expense code, French VAT amount, date, business purpose and mixed-use details.
- Taxable supplies / VAT registration in France during the claim period.
- Applicable expense-category deductibility and national exceptions.
- Refund period, previous applications, corrections, minimum claim values and deadline.
- Source record identifier, extracted field provenance and reviewer approval.

## Decision design
- NOT_ASSESSED: insufficient or unsupported evidence/country pair.
- REVIEW_REQUIRED: enough metadata to begin an expert review. **Does not mean eligible.**
- Never infer a refund, filing permission or recovered amount from a VAT invoice alone.
- Past ordinary deadlines should warn, not falsely rule out legal exceptions.
- No automatic submissions, client-bank details, success-fee payments or document uploads here.

## Gate to BUILD-003
Obtain qualified review of an explicit country-pair rule matrix (including expense category rules and claim thresholds); 50 labeled test cases, strictly partitioned synthetic vs consented real; privacy DPIA/legitimate basis and retention requirements; secure intake and audit model.
