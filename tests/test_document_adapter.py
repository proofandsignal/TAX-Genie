import unittest
from tax_genie.document_adapter import DocumentIntelligence, TextEvidence
class TestAdapter(unittest.TestCase):
    def test_selectable_text_offline(self):
        x=DocumentIntelligence().assess("VAT Amount: 23.00",b"never sent",1)
        self.assertEqual(x["fields"]["vat_amount"]["value"],"23.00")
    def test_ocr_disabled(self):
        x=DocumentIntelligence().assess(" ",b"scanned",2)
        self.assertEqual(x["review_flags"],["OCR_NOT_CONFIGURED"])
    def test_unreviewed_provider_rejected(self):
        class Fake:
            def extract(self,pdf): return TextEvidence("VAT Amount: 99.00","external_unsafe",1)
        with self.assertRaises(ValueError): DocumentIntelligence(Fake()).assess("",b"private",1)
    def test_reviewed_provider_remains_unverified(self):
        class Fake:
            def extract(self,pdf): return TextEvidence("VAT Amount: 10.00","reviewed_local_ocr",1)
        x=DocumentIntelligence(Fake()).assess("",b"synthetic",1)
        self.assertIn("OCR_UNVERIFIED",x["review_flags"])
    def test_page_mismatch(self):
        class Fake:
            def extract(self,pdf): return TextEvidence("", "reviewed_local_ocr",99)
        with self.assertRaises(ValueError): DocumentIntelligence(Fake()).assess("",b"x",1)
if __name__=="__main__": unittest.main()
