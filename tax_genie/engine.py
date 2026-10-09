"""Conservative and explainable potential-recovery intake triage.

This module does NOT establish tax eligibility or calculate recoverable VAT.
There are deliberately no legal claims without a reviewed jurisdiction rule.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

_ALLOWED_CATEGORIES = {"travel", "accommodation", "conference", "fuel", "other"}


def assess_case(case: dict[str, Any]) -> dict[str, Any]:
    """Return an auditable intake status based only on submitted metadata.

    Sensitive fields (names, taxpayer identifiers, document contents) are not
    accepted, returned or logged.
    """
    if not isinstance(case, dict):
        raise ValueError("case must be an object")

    accepted = {"home_country", "expense_country", "expense_category", "invoice_date", "vat_amount", "currency", "business_use"}
    unknown = set(case) - accepted
    if unknown:
        raise ValueError("unsupported fields: " + ", ".join(sorted(unknown)))

    missing = sorted(k for k in accepted if case.get(k) is None or case.get(k) == "")
    flags: list[str] = []
    if missing:
        flags.append("MISSING_INPUT")

    home = case.get("home_country")
    foreign = case.get("expense_country")
    for key, value in (("home_country", home), ("expense_country", foreign)):
        if value is not None and (not isinstance(value, str) or len(value) != 2 or not value.isascii() or not value.isalpha()):
            flags.append("INVALID_" + key.upper())

    cat = case.get("expense_category")
    if cat is not None and cat not in _ALLOWED_CATEGORIES:
        flags.append("UNSUPPORTED_CATEGORY")

    inv_date = case.get("invoice_date")
    if inv_date is not None:
        try:
            parsed = date.fromisoformat(inv_date) if isinstance(inv_date, str) else None
            if parsed is None or parsed > date.today():
                flags.append("INVALID_INVOICE_DATE")
        except ValueError:
            flags.append("INVALID_INVOICE_DATE")

    amount = case.get("vat_amount")
    if amount is not None:
        try:
            if isinstance(amount, (bool, float)):
                raise InvalidOperation
            parsed_amount = Decimal(str(amount))
            if not parsed_amount.is_finite() or parsed_amount <= 0:
                flags.append("INVALID_VAT_AMOUNT")
        except (InvalidOperation, ValueError):
            flags.append("INVALID_VAT_AMOUNT")

    currency = case.get("currency")
    if currency is not None and (not isinstance(currency, str) or len(currency) != 3 or not currency.isascii() or not currency.isalpha()):
        flags.append("INVALID_CURRENCY")
    if case.get("business_use") is not None and not isinstance(case["business_use"], bool):
        flags.append("INVALID_BUSINESS_USE")

    if flags:
        status = "NOT_ASSESSED"
    else:
        status = "REVIEW_REQUIRED"
        if home.upper() == foreign.upper():
            flags.append("SAME_COUNTRY_CHECK")
        if not case["business_use"]:
            flags.append("BUSINESS_USE_NOT_CONFIRMED")

    return {
        "status": status,
        "review_flags": sorted(set(flags)),
        "recovery_amount": None,
        "eligibility": "UNDETERMINED",
        "legal_basis": None,
        "next_action": "Obtain complete valid metadata" if status == "NOT_ASSESSED" else "Qualified reviewer must verify jurisdiction-specific rules and evidence",
        "disclaimer": "Exploratory intake only; no refund eligibility or amount is determined.",
    }
