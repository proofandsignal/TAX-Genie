import unittest

from tax_genie.pdf_ingress_policy import preflight_pdf, preflight_then_scan
from tax_genie.intake import MAX_BYTES


class NeverCalled:
    def scan(self, _):
        raise AssertionError("scan should not be called for rejected preflight")


class TestPdfIngressPolicy(unittest.TestCase):
    def test_valid_synthetic_header_requires_scan(self):
        decision = preflight_pdf("example.PDF", b"%PDF-1.7\nsynthetic")
        self.assertTrue(decision.accepted_for_scan)
        self.assertEqual(decision.reason, "requires_malware_scan")

    def test_invalid_headers_are_rejected(self):
        for content in (b"", b"not_pdf", b"%PDF-", b"%PDF-x.y", b"%PDF-1x7", b"%PDF-1."):
            with self.subTest(content=content):
                self.assertFalse(preflight_pdf("file.pdf", content).accepted_for_scan)

    def test_filename_traversal_rejected(self):
        for name in ("", "readme.txt", "../x.pdf", "path/x.pdf", "path\\x.pdf", "x\x00.pdf"):
            with self.subTest(name=name):
                self.assertFalse(preflight_pdf(name, b"%PDF-1.7\n").accepted_for_scan)

    def test_oversized_file_rejected(self):
        self.assertEqual(preflight_pdf("f.pdf", b"%PDF-1.7\n" + b"x" * MAX_BYTES).reason, "file_too_large")

    def test_malware_scanner_is_mandatory(self):
        content = b"%PDF-1.7\nsynthetic"
        self.assertFalse(preflight_then_scan("f.pdf", content, None))
        class NotClean:
            def scan(self, _):
                return 1
        self.assertFalse(preflight_then_scan("f.pdf", content, NotClean()))
        class Clean:
            def scan(self, _):
                return True
        self.assertTrue(preflight_then_scan("f.pdf", content, Clean()))

    def test_bad_file_does_not_reach_scanner(self):
        self.assertFalse(preflight_then_scan("file.txt", b"%PDF-1.7\n", NeverCalled()))


if __name__ == "__main__":
    unittest.main()
