"""Bounded PDF parsing in a spawned subprocess — prototype, NOT an OS sandbox.

The parent reads the bounded result before joining the worker to avoid a
multiprocessing.Queue feeder deadlock with large extracted-text responses.
This does not enforce memory, CPU, network or filesystem isolation.
"""
from __future__ import annotations
import multiprocessing as mp
import io
from pypdf import PdfReader

MAX_TEXT_CHARS = 250_000
MAX_PAGES = 20
MAX_INPUT_BYTES = 5 * 1024 * 1024


def _parse_worker(data: bytes, output):
    try:
        pdf = PdfReader(io.BytesIO(data), strict=True)
        if pdf.is_encrypted or len(pdf.pages) == 0 or len(pdf.pages) > MAX_PAGES:
            output.send(("error", "UNSUPPORTED_PDF"))
            return
        lines = []
        total_chars = 0
        for page in pdf.pages:
            text = page.extract_text() or ""
            total_chars += len(text)
            if total_chars > MAX_TEXT_CHARS:
                output.send(("error", "TEXT_TOO_LARGE"))
                return
            lines.append(text)
        output.send(("ok", {"text": "\n".join(lines), "pages": len(pdf.pages)}))
    except Exception:
        try:
            output.send(("error", "UNREADABLE_PDF"))
        except (OSError, BrokenPipeError):
            pass
    finally:
        output.close()


def parse_pdf_bounded(data: bytes, *, timeout: float = 3.0) -> dict:
    if not isinstance(data, bytes) or not data or len(data) > MAX_INPUT_BYTES or not data.startswith(b"%PDF-"):
        raise ValueError("PDF rejected")
    if not isinstance(timeout, (int, float)) or not (0.1 <= timeout <= 30):
        raise ValueError("Invalid timeout")
    ctx = mp.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_parse_worker, args=(data, child))
    try:
        proc.start()
        child.close()
        if not parent.poll(timeout):
            raise ValueError("PDF_PARSE_TIMEOUT")
        try:
            state, payload = parent.recv()
        except (EOFError, OSError, ValueError) as exc:
            raise ValueError("PDF_PARSE_NO_RESULT") from exc
        proc.join(1)
        if proc.is_alive():
            raise ValueError("PDF_PARSE_TIMEOUT")
        if proc.exitcode != 0:
            raise ValueError("PDF_PARSE_FAILED")
        if state != "ok":
            raise ValueError(payload)
        return payload
    finally:
        parent.close()
        child.close()
        if proc.pid is not None:
            if proc.is_alive():
                proc.terminate()
                proc.join(1)
            if proc.is_alive():
                proc.kill()
                proc.join()
            else:
                proc.join()
