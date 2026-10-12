"""Sourced EU VAT procedural triage (NOT a tax eligibility determination)."""
from __future__ import annotations

from datetime import date
from typing import Any
from .engine import assess_case

SUPPORTED_HOME = "DE"
SUPPORTED_EXPENSE = "FR"

SOURCES = (
    {"id": "EU-2008-9-ART15", "authority": "Council Directive 2008/9/EC, Article 15",
     "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32008L0009",
     "assertion": "Ordinary EU-established applicant deadline: 30 September following the refund period."},
    {"id": "EU-YOUR-EUROPE-2026", "authority": "European Commission / Your Europe",
     "url": "https://europa.eu/youreurope/business/taxation/vat/vat-refunds/index_en.htm",
     "assertion": "Submit through the applicant's establishment-country portal; expense restrictions vary."},
    {"id": "FR-FOREIGN-EU-REFUND", "authority": "French tax administration",
     "url": "https://www.impots.gouv.fr/international-professionnel/vat-refunds",
     "assertion": "Foreign EU businesses use the establishment state's electronic procedure for French VAT."},
)

def review_eu_vat(case: dict[str, Any], *, as_of: date | None = None) -> dict[str, Any]:
    """Run metadata checks then an explicitly non-binding procedural deadline screen.

    Dates are calendar-year simplifications; actual refund periods, exceptions,
    additional tax conditions and claim acceptance require expert verification.
    Never return recoverable amounts or eligibility claims.
    """
    base = assess_case(case)
    report: dict[str, Any] = {
        "status": "NOT_ASSESSED",
        "eligibility": "UNDETERMINED",
        "recovery_amount": None,
        "rule_pack": "eu-vat-de-fr-procedural-v0.1",
        "rule_pack_review_status": "REQUIRES_QUALIFIED_REVIEW",
        "source_ids": [s["id"] for s in SOURCES],
        "supporting_evidence": [],
        "missing_evidence": [
            "VAT invoice and line items", "business establishment and VAT status",
            "business purpose and expense category",
            "transactions/supplies in refund state", "refund period and earlier claim history",
            "deductibility under French domestic VAT rules",
        ],
        "deadline": None,
        "review_flags": list(base["review_flags"]),
        "next_action": base["next_action"],
    }
    if base["status"] == "NOT_ASSESSED":
        return report
    if case["home_country"].upper() != SUPPORTED_HOME or case["expense_country"].upper() != SUPPORTED_EXPENSE:
        report["review_flags"].append("UNSUPPORTED_COUNTRY_PAIR")
        report["next_action"] = "Route to a reviewed country-pair rule pack"
        return report
    current = as_of or date.today()
    if not isinstance(current, date):
        raise ValueError("as_of must be a date")
    year = date.fromisoformat(case["invoice_date"]).year
    # Article 15 ordinary time limit for a refund period in the calendar year.
    deadline = date(year + 1, 9, 30)
    report["deadline"] = {
        "ordinary_deadline": deadline.isoformat(),
        "as_of": current.isoformat(),
        "screen": "PAST_ORDINARY_DEADLINE" if current > deadline else "BEFORE_OR_ON_ORDINARY_DEADLINE",
        "source_id": "EU-2008-9-ART15",
        "note": "Procedural screen only. Invoice year may not equal refund period; corrections, exceptions and filings require human review.",
    }
    if current > deadline:
        report["review_flags"].append("CHECK_DEADLINE_OR_EXCEPTIONS")
    if case["expense_category"] in {"accommodation", "fuel", "other"}:
        report["review_flags"].append("VERIFY_FRANCE_EXPENSE_DEDUCTIBILITY")
    report["status"] = "REVIEW_REQUIRED"
    report["next_action"] = "Qualified reviewer to confirm claimant status, expense eligibility, refund period and source applicability"
    return report
