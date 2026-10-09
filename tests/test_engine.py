import unittest
from tax_genie import assess_case

CASE = {
    "home_country": "DE",
    "expense_country": "FR",
    "expense_category": "conference",
    "invoice_date": "2025-04-12",
    "vat_amount": "42.50",
    "currency": "EUR",
    "business_use": True,
}

class TestAssessment(unittest.TestCase):
    def test_complete_case_requires_review(self):
        result = assess_case(CASE)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["eligibility"], "UNDETERMINED")
        self.assertIsNone(result["recovery_amount"])
        self.assertIsNone(result["legal_basis"])

    def test_missing_data(self):
        result = assess_case({"home_country": "DE"})
        self.assertEqual(result["status"], "NOT_ASSESSED")
        self.assertIn("MISSING_INPUT", result["review_flags"])

    def test_reject_pii(self):
        with self.assertRaises(ValueError):
            assess_case({**CASE, "taxpayer_id": "example"})

    def test_reject_float_money(self):
        result = assess_case({**CASE, "vat_amount": 42.5})
        self.assertEqual(result["status"], "NOT_ASSESSED")
        self.assertIn("INVALID_VAT_AMOUNT", result["review_flags"])

    def test_negative_money(self):
        result = assess_case({**CASE, "vat_amount": "-1"})
        self.assertIn("INVALID_VAT_AMOUNT", result["review_flags"])

    def test_no_unverified_refund_claim_for_same_country(self):
        result = assess_case({**CASE, "expense_country": "DE"})
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertIn("SAME_COUNTRY_CHECK", result["review_flags"])

    def test_nonbusiness_use_requires_review(self):
        result = assess_case({**CASE, "business_use": False})
        self.assertIn("BUSINESS_USE_NOT_CONFIRMED", result["review_flags"])

if __name__ == "__main__":
    unittest.main()
