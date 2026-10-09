import base64
import os
import tempfile
import unittest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from tax_genie.api import create_app
from tax_genie.intake import IntakeStore

def pdf_bytes():
    from io import BytesIO
    buf=BytesIO()
    writer=PdfWriter()
    writer.add_blank_page(width=400,height=600)
    writer.write(buf)
    return buf.getvalue()

class TestSecureIntake(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=IntakeStore(self.tmp.name+"/pilot.db",os.urandom(32))
        self.client=TestClient(create_app(store=self.store,tenant_tokens={"a":"A"*48,"b":"B"*48}))
        self.a={"Authorization":"Bearer "+"A"*48}
        self.b={"Authorization":"Bearer "+"B"*48}
    def tearDown(self):
        self.tmp.cleanup()
    def new(self,headers):
        return self.client.post("/v1/cases",headers=headers)
    def test_auth_is_mandatory(self):
        self.assertEqual(self.new({}).status_code,401)
        self.assertEqual(self.new({"Authorization":"Bearer wrong"}).status_code,401)
    def test_isolated_case_access(self):
        c=self.new(self.a).json()["id"]
        self.assertEqual(self.client.get("/v1/cases/"+c,headers=self.a).status_code,200)
        self.assertEqual(self.client.get("/v1/cases/"+c,headers=self.b).status_code,404)
        self.assertEqual(self.client.delete("/v1/cases/"+c,headers=self.b).status_code,404)
    def test_encrypted_document_and_deletion(self):
        c=self.new(self.a).json()["id"]
        raw=pdf_bytes()
        result=self.client.post("/v1/cases/"+c+"/documents",headers=self.a,json={
            "filename":"invoice.pdf","content_base64":base64.b64encode(raw).decode()})
        self.assertEqual(result.status_code,201,result.text)
        self.assertTrue(result.json()["extraction"]["requires_human_review"])
        db=open(self.tmp.name+"/pilot.db","rb").read()
        self.assertNotIn(raw,db)
        self.assertEqual(self.client.get("/v1/cases/"+c,headers=self.a).json()["status"],"HUMAN_REVIEW_REQUIRED")
        self.assertEqual(self.client.delete("/v1/cases/"+c,headers=self.a).status_code,204)
        self.assertEqual(self.client.get("/v1/cases/"+c,headers=self.a).status_code,404)
    def test_cross_tenant_upload_blocked(self):
        c=self.new(self.a).json()["id"]
        payload={"filename":"x.pdf","content_base64":base64.b64encode(pdf_bytes()).decode()}
        self.assertEqual(self.client.post("/v1/cases/"+c+"/documents",headers=self.b,json=payload).status_code,404)
    def test_non_pdf_rejected(self):
        c=self.new(self.a).json()["id"]
        self.assertEqual(self.client.post("/v1/cases/"+c+"/documents",headers=self.a,json={
            "filename":"test.pdf","content_base64":base64.b64encode(b"not a pdf").decode()}).status_code,422)
    def test_reject_empty_or_weak_keys(self):
        with self.assertRaises(ValueError):
            create_app(store=self.store,tenant_tokens={"a":"weak"})
    def test_no_eligibility_in_case_api(self):
        c=self.new(self.a).json()["id"]
        body=self.client.get("/v1/cases/"+c,headers=self.a).json()
        self.assertNotIn("refund_approved",body)
        self.assertNotIn("recoverable_amount",body)

if __name__=="__main__":
    unittest.main()
