import unittest
from tax_genie.invoice_evidence import extract_invoice_evidence

SAMPLE = """Invoice Number: INV-402
Invoice Date: 2026-03-17
Supplier VAT ID: FR12345678901
Supplier Country: FR
Currency: EUR
VAT Amount: 20.00
Invoice Total: 120.00"""

class TestEvidence(unittest.TestCase):
    def test_labeled_fields_with_provenance(self):
        r=extract_invoice_evidence(SAMPLE)
        self.assertEqual(r["fields"]["vat_amount"],{"value":"20.00","line":6,"method":"labeled_regex"})
        self.assertEqual(r["fields"]["country"]["value"],"FR")
        self.assertEqual(r["refund_eligibility"],"UNDETERMINED")
        self.assertIsNone(r["recoverable_amount"])
    def test_missing_fields_and_review(self):
        r=extract_invoice_evidence("Invoice Number: ABC123")
        self.assertIn("MISSING_VAT_AMOUNT",r["review_flags"])
        self.assertEqual(r["review_status"],"HUMAN_REVIEW_REQUIRED")
    def test_conflicting_amounts_do_not_pass(self):
        r=extract_invoice_evidence("VAT Amount: 20.00\nVAT Amount: 40.00")
        self.assertIn("CONFLICTING_VAT_AMOUNT",r["review_flags"])
        self.assertNotIn("vat_amount",r["fields"])
    def test_vat_cannot_exceed_total(self):
        r=extract_invoice_evidence("VAT Amount: 30.00\nInvoice Total: 20.00")
        self.assertIn("VAT_EXCEEDS_TOTAL",r["review_flags"])
    def test_unlabeled_amount_is_not_assumed(self):
        r=extract_invoice_evidence("EUR 500.00\nFR12345678901")
        self.assertNotIn("vat_amount",r["fields"])
        self.assertNotIn("vat_id",r["fields"])
    def test_future_dates_not_accepted(self):
        r=extract_invoice_evidence("Invoice Date: 2099-01-01")
        self.assertIn("INVALID_INVOICE_DATE",r["review_flags"])
    def test_no_raw_lines_stored(self):
        r=extract_invoice_evidence(SAMPLE+"\nPrivate client note: secret")
        self.assertNotIn("secret",str(r))
    def test_reject_large_input(self):
        with self.assertRaises(ValueError):
            extract_invoice_evidence("x"*250001)

if __name__=="__main__":
    unittest.main()
