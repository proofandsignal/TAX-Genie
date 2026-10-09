"""Minimal, private-pilot-only API. No public filing, no eligibility claims."""
from __future__ import annotations
import base64
import json
import os
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field
from .intake import IntakeStore, authentic_tenant, MAX_BYTES

class DocumentInput(BaseModel):
    filename: str = Field(max_length=120)
    content_base64: str = Field(max_length=8_000_000)

def create_app(*, store: IntakeStore, tenant_tokens: dict[str,str]) -> FastAPI:
    app = FastAPI(title="Tax Genie Private Pilot", version="0.3.0", docs_url=None, redoc_url=None)
    if not tenant_tokens or any(not k or len(v)<32 for k,v in tenant_tokens.items()):
        raise ValueError("Configure tenant IDs and random API tokens >= 32 characters")
    if len(set(tenant_tokens.values())) != len(tenant_tokens):
        raise ValueError("Tenant tokens must be unique")

    def auth(authorization: str | None = Header(default=None)) -> str:
        tenant=authentic_tenant(authorization,tenant_tokens)
        if tenant is None:
            raise HTTPException(status_code=401,detail="Unauthorized")
        return tenant

    @app.post("/v1/cases",status_code=201)
    def new_case(tenant: str=Depends(auth)):
        return store.new_case(tenant)

    @app.get("/v1/cases/{case_id}")
    def get_case(case_id: str,tenant: str=Depends(auth)):
        result=store.case(tenant,case_id)
        if result is None: raise HTTPException(404,detail="Not found")
        return result

    @app.post("/v1/cases/{case_id}/documents",status_code=201)
    def upload(case_id: str,payload: DocumentInput,tenant: str=Depends(auth)):
        if not payload.filename.lower().endswith(".pdf"):
            raise HTTPException(415,detail="PDF required")
        if store.case(tenant,case_id) is None:
            raise HTTPException(404,detail="Not found")
        try:
            data=base64.b64decode(payload.content_base64,validate=True)
        except (ValueError,base64.binascii.Error):
            raise HTTPException(400,detail="Invalid file encoding")
        try:
            document=store.add_pdf(tenant,case_id,data)
        except ValueError:
            raise HTTPException(422,detail="PDF could not be accepted")
        return document

    @app.delete("/v1/cases/{case_id}",status_code=204)
    def delete_case(case_id: str,tenant: str=Depends(auth)):
        if not store.delete_case(tenant,case_id):
            raise HTTPException(404,detail="Not found")

    return app

def application_from_env() -> FastAPI:
    token_config=json.loads(os.environ["TAX_GENIE_TENANT_TOKENS_JSON"])
    key=base64.b64decode(os.environ["TAX_GENIE_AES_KEY_B64"],validate=True)
    return create_app(store=IntakeStore(os.environ["TAX_GENIE_DATABASE"],key),tenant_tokens=token_config)

# Run as: uvicorn tax_genie.api:application_from_env --factory --host 127.0.0.1
