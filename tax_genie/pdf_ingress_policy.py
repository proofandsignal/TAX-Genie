"""BUILD-020 PDF ingress preflight; no scanner or parser bypass.

Metadata-only checks that run before any parser execution.
These do not establish document safety and must never replace malware scanning.
"""
from __future__ import annotations

from dataclasses import dataclass

from .intake import MAX_BYTES


@dataclass(frozen=True)
class PdfIngressDecision:
    accepted_for_scan: bool
    reason: str


def preflight_pdf(filename: str, content: bytes) -> PdfIngressDecision:
    """Conservative size/signature validation before the mandatory malware scan."""
    if not isinstance(filename, str) or not filename or len(filename) > 120:
        return PdfIngressDecision(False, "invalid_filename")
    if "/" in filename or "\\" in filename or "\x00" in filename:
        return PdfIngressDecision(False, "invalid_filename")
    if filename in (".", "..") or not filename.lower().endswith(".pdf"):
        return PdfIngressDecision(False, "pdf_extension_required")
    if not isinstance(content, bytes) or not content:
        return PdfIngressDecision(False, "empty_or_invalid_content")
    if len(content) > MAX_BYTES:
        return PdfIngressDecision(False, "file_too_large")
    if not content.startswith(b"%PDF-"):
        return PdfIngressDecision(False, "pdf_signature_required")
    if len(content) < 9:
        return PdfIngressDecision(False, "truncated_header")
    if content[5:6] not in b"123456789" or content[6:7] != b"." or content[7:8] not in b"0123456789":
        return PdfIngressDecision(False, "malformed_pdf_version")
    return PdfIngressDecision(True, "requires_malware_scan")


def preflight_then_scan(filename: str, content: bytes, scanner) -> bool:
    """Fail closed: only explicit scanner True permits further processing."""
    decision = preflight_pdf(filename, content)
    if not decision.accepted_for_scan:
        return False
    from .security_controls import verified_scan
    return verified_scan(scanner, content)
