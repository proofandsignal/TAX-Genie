"""Synthetic route tests: no real documents or persistence."""
import base64
import unittest
from fastapi.testclient import TestClient
from tax_genie.api import create_app


class FakeStore:
    def __init__(self):
        self.parse_calls = 0

    def case(self, tenant, case_id):
        return {"id":case_id} if tenant == "tenant-a" and case_id == "case-001" else None

    def add_pdf(self, tenant, case_id, data):
        self.parse_calls += 1
        return {"id":"synthetic-document"}


class FakeScanner:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def scan(self, data):
        self.calls += 1
        return self.result


class TestPdfApiIngress(unittest.TestCase):
    def setUp(self):
        self.store = FakeStore()
        self.scanner = FakeScanner(False)
        self.token = "0123456789abcdef0123456789abcdefA"
        self.client = TestClient(create_app(
            store=self.store, tenant_tokens={"tenant-a":self.token}, scanner=self.scanner
        ))

    def upload(self, name, data):
        return self.client.post("/v1/cases/case-001/documents",
            headers={"Authorization":"Bearer " + self.token},
            json={"filename":name,"content_base64":base64.b64encode(data).decode()})

    def test_bad_header_does_not_call_scanner_or_parser(self):
        response = self.upload("invoice.pdf", b"not-a-pdf")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.scanner.calls, 0)
        self.assertEqual(self.store.parse_calls, 0)

    def test_traversal_filename_does_not_call_scanner_or_parser(self):
        response = self.upload("../invoice.pdf", b"%PDF-1.7\nsynthetic")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.scanner.calls, 0)
        self.assertEqual(self.store.parse_calls, 0)

    def test_rejected_scanner_never_reaches_parser(self):
        response = self.upload("invoice.pdf", b"%PDF-1.7\nsynthetic")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(self.scanner.calls, 1)
        self.assertEqual(self.store.parse_calls, 0)

    def test_explicit_clean_scanner_allows_store_call_in_synthetic_test(self):
        self.scanner.result = True
        response = self.upload("invoice.pdf", b"%PDF-1.7\nsynthetic")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.scanner.calls, 1)
        self.assertEqual(self.store.parse_calls, 1)

    def test_unauthenticated_request_does_not_scan_or_parse(self):
        response = self.client.post("/v1/cases/case-001/documents",
            json={"filename":"invoice.pdf","content_base64":base64.b64encode(b"%PDF-1.7\n").decode()})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.scanner.calls, 0)
        self.assertEqual(self.store.parse_calls, 0)


if __name__ == "__main__":
    unittest.main()
