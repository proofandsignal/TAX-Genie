import unittest
from tax_genie.paper50 import evaluate
class TestPaper50(unittest.TestCase):
    def test_separate_datasets(self):
        rows=[{"id":"S1","dataset":"synthetic","text":"VAT Amount: 10.00","truth":{"vat_amount":"10.00"}},
              {"id":"R1","dataset":"consented_real","text":"VAT Amount: 50.00","truth":{"vat_amount":"20.00"}}]
        r=evaluate(rows)
        self.assertEqual(r["per_field"]["synthetic"]["vat_amount"]["precision"],1.0)
        self.assertEqual(r["per_field"]["consented_real"]["vat_amount"]["precision"],0.0)
    def test_false_positive(self):
        r=evaluate([{"id":"S","dataset":"synthetic","text":"VAT Amount: 1.00","truth":{}}])
        self.assertEqual(r["per_field"]["synthetic"]["vat_amount"]["fp"],1)
    def test_false_negative(self):
        r=evaluate([{"id":"S","dataset":"synthetic","text":"","truth":{"vat_amount":"1.00"}}])
        self.assertEqual(r["per_field"]["synthetic"]["vat_amount"]["fn"],1)
    def test_exact_50_gate(self):
        with self.assertRaises(ValueError): evaluate([],require_50=True)
    def test_duplicates(self):
        row={"id":"A","dataset":"synthetic","text":"","truth":{}}
        with self.assertRaises(ValueError): evaluate([row,row])
    def test_unclassified(self):
        with self.assertRaises(ValueError): evaluate([{"id":"A","dataset":"unknown","text":"","truth":{}}])
if __name__=="__main__": unittest.main()
