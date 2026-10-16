import base64
import os
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from tax_genie.api import create_app
from tax_genie.intake import IntakeStore

KEY="0123456789abcdef0123456789abcdefA"

class CleanSyntheticScanner:
    def scan(self, data): return True

class TestBoundedIntake(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=IntakeStore(self.temp.name+"/db.sqlite",os.urandom(32))
        self.client=TestClient(create_app(store=self.store,tenant_tokens={"pilot":KEY},scanner=CleanSyntheticScanner()))
        self.headers={"Authorization":"Bearer "+KEY}
    def tearDown(self):
        self.temp.cleanup()
    def test_parser_failure_does_not_store_document(self):
        case=self.client.post("/v1/cases",headers=self.headers).json()["id"]
        with patch("tax_genie.intake.parse_pdf_bounded",side_effect=ValueError("PDF_PARSE_TIMEOUT")):
            response=self.client.post("/v1/cases/"+case+"/documents",headers=self.headers,
                json={"filename":"synthetic.pdf","content_base64":base64.b64encode(b"%PDF-1.7\nsynthetic-but-parser-mocked").decode()})
        self.assertEqual(response.status_code,422)
        self.assertEqual(self.client.get("/v1/cases/"+case,headers=self.headers).json()["documents"],[])
if __name__=="__main__": unittest.main()
