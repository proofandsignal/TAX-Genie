"""Conservative invoice field candidate extraction with line provenance.

Only explicit labeled values are considered. No AI guesses, no legal conclusion,
no automatic transfer of raw invoice text to external services.
"""
from __future__ import annotations
import re
from datetime import date
from decimal import Decimal, InvalidOperation

PATTERNS = {
    "invoice_number": re.compile(r"^\s*(?:Invoice\s*(?:No\.?|Number|#)|Facture\s*(?:n[o°]?|num[eé]ro))\s*[:#-]?\s*([A-Za-z0-9][A-Za-z0-9/_-]{1,39})\s*$", re.I),
    "invoice_date": re.compile(r"^\s*(?:Invoice\s*Date|Date\s*de\s*facture)\s*:\s*(\d{4}-\d{2}-\d{2})\s*$", re.I),
    "vat_id": re.compile(r"^\s*(?:Supplier\s*VAT\s*(?:ID|No\.?|Number)|VAT\s*(?:ID|Number)|TVA\s*intracommunautaire)\s*:\s*([A-Z]{2}[A-Z0-9]{6,13})\s*$", re.I),
    "currency": re.compile(r"^\s*(?:Currency|Devise)\s*:\s*([A-Z]{3})\s*$", re.I),
    "vat_amount": re.compile(r"^\s*(?:VAT\s*(?:Amount|Total)|TVA\s*(?:montant|totale))\s*:\s*([0-9]{1,10}(?:\.[0-9]{1,2})?)\s*$", re.I),
    "total_amount": re.compile(r"^\s*(?:Grand\s*Total|Invoice\s*Total|Total\s*TTC)\s*:\s*([0-9]{1,10}(?:\.[0-9]{1,2})?)\s*$", re.I),
    "country": re.compile(r"^\s*(?:Supplier\s*Country|Pays\s*du\s*fournisseur)\s*:\s*(DE|FR|NL|BE|IT|ES|AT)\s*$", re.I),
}
FIELDS = tuple(PATTERNS)
def extract_invoice_evidence(text: str) -> dict:
    """Extract candidates from labeled synthetic/selectable invoice text.

    Never retain original lines or full text in API results. Line ordinal
    provides provenance without exposing surrounding sensitive content.
    """
    if not isinstance(text,str) or len(text)>250_000:
        raise ValueError("invalid text")
    matches = {key: [] for key in FIELDS}
    for line_number,line in enumerate(text.splitlines(),1):
        if len(line)>500: continue
        for key,pattern in PATTERNS.items():
            m=pattern.fullmatch(line)
            if m:
                value=m.group(1).upper() if key in {"currency","vat_id","country"} else m.group(1)
                matches[key].append({"value":value,"line":line_number,"method":"labeled_regex"})
    fields={}
    flags=[]
    for key,items in matches.items():
        unique={x["value"] for x in items}
        if len(unique)>1:
            flags.append("CONFLICTING_"+key.upper())
        elif len(unique)==1:
            item=items[0]
            value=item["value"]
            if key=="invoice_date":
                try:
                    if date.fromisoformat(value)>date.today(): raise ValueError
                except ValueError:
                    flags.append("INVALID_INVOICE_DATE")
                    continue
            if key in {"vat_amount","total_amount"}:
                try:
                    d=Decimal(value)
                    if not d.is_finite() or d<0: raise InvalidOperation
                except InvalidOperation:
                    flags.append("INVALID_"+key.upper())
                    continue
            fields[key]=item
        else:
            flags.append("MISSING_"+key.upper())
    if "vat_amount" in fields and "total_amount" in fields:
        if Decimal(fields["vat_amount"]["value"])>Decimal(fields["total_amount"]["value"]):
            flags.append("VAT_EXCEEDS_TOTAL")
    return {
        "method":"labeled_regex_v0.1",
        "fields":fields,
        "review_flags":sorted(set(flags)),
        "review_status":"HUMAN_REVIEW_REQUIRED",
        "refund_eligibility":"UNDETERMINED",
        "recoverable_amount":None,
        "notes":"Extracted values are unverified candidates, not established invoice facts.",
    }
