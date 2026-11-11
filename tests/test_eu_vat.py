import unittest
from datetime import date
from tax_genie.eu_vat import review_eu_vat, SOURCES

CASE = {
    "home_country": "DE",
    "expense_country": "FR",
    "expense_category": "conference",
    "invoice_date": "2026-04-12",
    "vat_amount": "42.50",
    "currency": "EUR",
    "business_use": True,
}

class TestEUVatProceduralScreen(unittest.TestCase):
    def test_sources_have_https_primary_urls(self):
        self.assertEqual(len({x["id"] for x in SOURCES}), len(SOURCES))
        self.assertTrue(all(x["url"].startswith("https://") for x in SOURCES))

    def test_current_year_deadline_screen(self):
        result = review_eu_vat(CASE, as_of=date(2026, 10, 9))
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["deadline"]["ordinary_deadline"], "2027-09-30")
        self.assertEqual(result["deadline"]["screen"], "BEFORE_OR_ON_ORDINARY_DEADLINE")
        self.assertEqual(result["eligibility"], "UNDETERMINED")
        self.assertIsNone(result["recovery_amount"])

    def test_last_year_screen_is_past(self):
        result = review_eu_vat({**CASE, "invoice_date": "2025-04-12"}, as_of=date(2026, 10, 9))
        self.assertEqual(result["deadline"]["screen"], "PAST_ORDINARY_DEADLINE")
        self.assertIn("CHECK_DEADLINE_OR_EXCEPTIONS", result["review_flags"])

    def test_same_day_screen(self):
        result = review_eu_vat(CASE, as_of=date(2027, 9, 30))
        self.assertEqual(result["deadline"]["screen"], "BEFORE_OR_ON_ORDINARY_DEADLINE")

    def test_unsupported_pair_cannot_create_deadline(self):
        result = review_eu_vat({**CASE, "home_country": "NL"}, as_of=date(2026, 10, 9))
        self.assertEqual(result["status"], "NOT_ASSESSED")
        self.assertIsNone(result["deadline"])
        self.assertIn("UNSUPPORTED_COUNTRY_PAIR", result["review_flags"])

    def test_incomplete_case_cannot_create_deadline(self):
        result = review_eu_vat({"home_country": "DE"})
        self.assertEqual(result["status"], "NOT_ASSESSED")
        self.assertIsNone(result["deadline"])

    def test_restricted_categories_flag_review(self):
        result = review_eu_vat({**CASE, "expense_category": "fuel"}, as_of=date(2026, 10, 9))
        self.assertIn("VERIFY_FRANCE_EXPENSE_DEDUCTIBILITY", result["review_flags"])

    def test_no_claim_approval(self):
        result = review_eu_vat(CASE, as_of=date(2026, 10, 9))
        self.assertNotIn(result["status"], {"APPROVED", "ELIGIBLE"})
        self.assertIsNone(result["recovery_amount"])

if __name__ == "__main__":
    unittest.main()
