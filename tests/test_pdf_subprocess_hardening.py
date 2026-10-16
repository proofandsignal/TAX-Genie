import unittest
from io import BytesIO
from pypdf import PdfWriter
from tax_genie.pdf_isolation import parse_pdf_bounded


def blank_pdf():
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(output)
    return output.getvalue()


class TestPdfSubprocessHardening(unittest.TestCase):
    def test_spawned_worker_returns_bounded_pdf(self):
        result = parse_pdf_bounded(blank_pdf(), timeout=10)
        self.assertEqual(result["pages"], 1)
        self.assertIn("text", result)

    def test_invalid_content_never_spawns(self):
        for content in (b"", b"not pdf", b"%PDF-", b"%PDF-" + b"x" * (5 * 1024 * 1024)):
            with self.subTest(content_length=len(content)):
                with self.assertRaises(ValueError):
                    parse_pdf_bounded(content)

    def test_timeout_bounds_are_enforced(self):
        valid = blank_pdf()
        for timeout in (0, 0.01, 31, "3"):
            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    parse_pdf_bounded(valid, timeout=timeout)

    def test_malformed_pdf_never_returns_extraction(self):
        with self.assertRaises(ValueError):
            parse_pdf_bounded(b"%PDF-1.7\nnot actually a PDF", timeout=10)


if __name__ == "__main__":
    unittest.main()
