import base64
import os
import tempfile
import unittest
from fastapi.testclient import TestClient
from tax_genie.api import create_app
from tax_genie.intake import IntakeStore
from tax_genie.security_controls import RateLimiter

TOKEN="0123456789abcdef0123456789abcdefA"

class TestAPISecurityBoundary(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=IntakeStore(self.temp.name+"/db.sqlite",os.urandom(32))
        self.headers={"Authorization":"Bearer "+TOKEN}
    def tearDown(self):
        self.temp.cleanup()
    def test_default_scanner_blocks_even_synthetic_upload(self):
        client=TestClient(create_app(store=self.store,tenant_tokens={"pilot":TOKEN}))
        case=client.post("/v1/cases",headers=self.headers).json()["id"]
        resp=client.post(f"/v1/cases/{case}/documents",headers=self.headers,json={"filename":"x.pdf","content_base64":base64.b64encode(b"%PDF-1.7\nsynthetic").decode()})
        self.assertEqual(resp.status_code,503)
        self.assertEqual(client.get(f"/v1/cases/{case}",headers=self.headers).json()["documents"],[])
    def test_rate_limiter_rejects_excess_requests(self):
        client=TestClient(create_app(store=self.store,tenant_tokens={"pilot":TOKEN},limiter=RateLimiter(limit=1)))
        self.assertEqual(client.post("/v1/cases",headers=self.headers).status_code,201)
        self.assertEqual(client.post("/v1/cases",headers=self.headers).status_code,429)
if __name__=="__main__":
    unittest.main()
