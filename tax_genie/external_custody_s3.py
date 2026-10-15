"""Optional S3-compatible checkpoint custody adapter. OFF unless explicitly configured.

Requires an independently governed Object Lock bucket and restricted IAM;
application-side code cannot establish immutable custody by itself.
No production credential values belong in source or test fixtures.
"""
from __future__ import annotations
import json
from .audit_custody import CustodyUnavailable

class S3ObjectLockCustody:
    def __init__(self, client, *, bucket: str, prefix: str = "tax-genie/audit/v1/"):
        if not bucket or not prefix.endswith("/") or ".." in prefix:
            raise ValueError("Invalid custody destination")
        self.client = client
        self.bucket = bucket
        self.prefix = prefix

    def publish(self, checkpoint: dict) -> str:
        """Require S3 service to acknowledge compliance retention on every write."""
        import hashlib
        body=json.dumps(checkpoint,sort_keys=True,separators=(",",":")).encode("utf-8")
        digest=hashlib.sha256(body).hexdigest()
        key=self.prefix+digest+".json"
        try:
            result=self.client.put_object(
                Bucket=self.bucket, Key=key, Body=body,
                ContentType="application/json",
                ChecksumSHA256=__import__("base64").b64encode(bytes.fromhex(digest)).decode(),
                ObjectLockMode="COMPLIANCE",
                ObjectLockRetainUntilDate=self._retention_date(),
            )
            version=result.get("VersionId")
            if not version:
                raise CustodyUnavailable("Object version acknowledgement missing")
            # Read back the exact version, checking current Object Lock retention.
            state=self.client.get_object_retention(Bucket=self.bucket,Key=key,VersionId=version)
            retention=state.get("Retention",{})
            if retention.get("Mode")!="COMPLIANCE" or not retention.get("RetainUntilDate"):
                raise CustodyUnavailable("Compliance retention not verified")
            return json.dumps({"key":key,"version":version,"sha256":digest},sort_keys=True)
        except CustodyUnavailable:
            raise
        except Exception as exc:
            raise CustodyUnavailable("External custody write or retention verification failed") from exc

    @staticmethod
    def _retention_date():
        from datetime import datetime,timedelta,timezone
        return datetime.now(timezone.utc)+timedelta(days=365)

    def retrieve(self, receipt: str) -> dict:
        import hashlib
        try:
            marker=json.loads(receipt)
            if set(marker)!={"key","version","sha256"}:
                raise ValueError("Invalid receipt")
            if not isinstance(marker["key"],str) or not marker["key"].startswith(self.prefix):
                raise ValueError("Invalid key prefix")
            if not isinstance(marker["version"],str) or not marker["version"]:
                raise ValueError("Missing object version")
            obj=self.client.get_object(Bucket=self.bucket,Key=marker["key"],VersionId=marker["version"])
            raw=obj["Body"].read()
            if len(raw)>64_000 or hashlib.sha256(raw).hexdigest()!=marker["sha256"]:
                raise ValueError("Custody digest mismatch")
            return json.loads(raw)
        except Exception as exc:
            raise CustodyUnavailable("External custody retrieval failed") from exc
