"""Encrypted local pilot intake. NOT a production deployment configuration."""
from __future__ import annotations
import hashlib
import hmac
import io
import json
import os
import secrets
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pypdf import PdfReader
from .invoice_evidence import extract_invoice_evidence

MAX_BYTES = 5 * 1024 * 1024
MAX_PDF_PAGES = 20

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def authentic_tenant(bearer: str | None, tenant_keys: dict[str,str]) -> str | None:
    if not bearer or not bearer.startswith("Bearer "):
        return None
    supplied = bearer[7:]
    matched = None
    # No untrusted tenant supplied in headers, route or query controls isolation.
    for tenant_id, expected in tenant_keys.items():
        if hmac.compare_digest(supplied, expected):
            matched = tenant_id
    return matched

class IntakeStore:
    def __init__(self, database: str, key: bytes):
        if len(key) not in (16, 24, 32):
            raise ValueError("AES-GCM key must be 16/24/32 bytes")
        self.database = database
        self.cipher = AESGCM(key)
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS cases
                (id TEXT PRIMARY KEY, tenant TEXT NOT NULL, created TEXT NOT NULL,
                 status TEXT NOT NULL, evidence TEXT NOT NULL)""")
            con.execute("""CREATE TABLE IF NOT EXISTS documents
                (id TEXT PRIMARY KEY, case_id TEXT NOT NULL, tenant TEXT NOT NULL,
                 created TEXT NOT NULL, sha256 TEXT NOT NULL, ciphertext BLOB NOT NULL,
                 nonce BLOB NOT NULL, extracted TEXT NOT NULL,
                 FOREIGN KEY(case_id) REFERENCES cases(id))""")
            con.execute("CREATE INDEX IF NOT EXISTS cases_tenant ON cases(tenant)")
            con.execute("CREATE INDEX IF NOT EXISTS docs_tenant_case ON documents(tenant,case_id)")

    def _db(self):
        con = sqlite3.connect(self.database)
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def new_case(self, tenant: str) -> dict:
        case_id = str(uuid.uuid4())
        created = utcnow()
        with self._db() as con:
            con.execute("INSERT INTO cases VALUES (?,?,?,?,?)",
                        (case_id,tenant,created,"HUMAN_REVIEW_REQUIRED","[]"))
        return {"id":case_id,"created":created,"status":"HUMAN_REVIEW_REQUIRED"}

    def case(self, tenant: str, case_id: str) -> dict | None:
        with self._db() as con:
            result=con.execute("SELECT id,created,status,evidence FROM cases WHERE id=? AND tenant=?",
                               (case_id,tenant)).fetchone()
            if not result: return None
            docs=con.execute("SELECT id,created,sha256,extracted FROM documents WHERE case_id=? AND tenant=?",
                             (case_id,tenant)).fetchall()
        return {"id":result[0],"created":result[1],"status":result[2],
                "evidence":json.loads(result[3]),
                "documents":[{"id":d[0],"created":d[1],"sha256":d[2], "extraction":json.loads(d[3])} for d in docs]}

    def add_pdf(self, tenant: str, case_id: str, content: bytes) -> dict | None:
        if not content or len(content)>MAX_BYTES: raise ValueError("PDF must be between 1 byte and 5 MiB")
        if not content.startswith(b"%PDF-"): raise ValueError("Only PDF files are permitted")
        try:
            pdf=PdfReader(io.BytesIO(content),strict=True)
            if pdf.is_encrypted or len(pdf.pages)>MAX_PDF_PAGES or not pdf.pages:
                raise ValueError("Encrypted, empty or oversized PDF not supported")
            # Pilot extraction uses only selectable PDF text, never OCR.
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as exc:
            raise ValueError("Unreadable or unsafe PDF") from exc
        # Do not echo invoice text or taxpayer identifiers into API responses or logs.
        extraction={"method":"pypdf_text","pages":len(pdf.pages),"text_present":bool(text.strip()),
                    "requires_human_review":True,
                    "evidence":extract_invoice_evidence(text)}
        doc_id=str(uuid.uuid4())
        nonce=os.urandom(12)
        encrypted=self.cipher.encrypt(nonce,content,(tenant+":"+case_id+":"+doc_id).encode())
        digest=hashlib.sha256(content).hexdigest()
        created=utcnow()
        with self._db() as con:
            if not con.execute("SELECT 1 FROM cases WHERE tenant=? AND id=?",(tenant,case_id)).fetchone():
                return None
            con.execute("INSERT INTO documents VALUES (?,?,?,?,?,?,?,?)",
                        (doc_id,case_id,tenant,created,digest,encrypted,nonce,json.dumps(extraction)))
        return {"id":doc_id,"sha256":digest, "extraction":extraction}

    def delete_case(self, tenant: str, case_id: str) -> bool:
        with self._db() as con:
            if not con.execute("SELECT 1 FROM cases WHERE tenant=? AND id=?",(tenant,case_id)).fetchone():
                return False
            con.execute("DELETE FROM documents WHERE tenant=? AND case_id=?",(tenant,case_id))
            con.execute("DELETE FROM cases WHERE tenant=? AND id=?",(tenant,case_id))
        return True
