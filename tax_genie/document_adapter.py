"""Fail-closed OCR adapter boundary. No automatic external transfers."""
from dataclasses import dataclass
from typing import Protocol
from .invoice_evidence import extract_invoice_evidence

@dataclass(frozen=True)
class TextEvidence:
    text: str
    method: str
    page_count: int

class OCRProvider(Protocol):
    def extract(self, pdf_bytes: bytes) -> TextEvidence: ...

class DisabledOCR:
    def extract(self, pdf_bytes: bytes) -> TextEvidence:
        raise RuntimeError("OCR_DISABLED")

class DocumentIntelligence:
    def __init__(self, ocr: OCRProvider | None = None):
        self.ocr = ocr or DisabledOCR()

    def assess(self, selectable_text: str, pdf_bytes: bytes, pages: int) -> dict:
        if not isinstance(selectable_text, str) or pages < 1:
            raise ValueError("Invalid source")
        if selectable_text.strip():
            result = extract_invoice_evidence(selectable_text)
            result["document_source"] = {"method": "selectable_pdf_text", "pages": pages}
            return result
        try:
            evidence = self.ocr.extract(pdf_bytes)
        except RuntimeError:
            return {"method":"none", "fields":{}, "review_flags":["OCR_NOT_CONFIGURED"],
                    "review_status":"HUMAN_REVIEW_REQUIRED",
                    "refund_eligibility":"UNDETERMINED", "recoverable_amount":None,
                    "document_source":{"method":"no_selectable_text","pages":pages}}
        if not isinstance(evidence, TextEvidence) or not evidence.method.startswith("reviewed_"):
            raise ValueError("OCR provider must supply reviewed provenance")
        if evidence.page_count != pages or len(evidence.text)>250_000:
            raise ValueError("OCR page mismatch or size exceeded")
        result = extract_invoice_evidence(evidence.text)
        result["document_source"]={"method":evidence.method,"pages":pages}
        result["review_flags"]=sorted(set(result["review_flags"]+["OCR_UNVERIFIED"]))
        return result
