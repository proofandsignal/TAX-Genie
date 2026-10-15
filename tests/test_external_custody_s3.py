import base64
import io
import json
import unittest
from datetime import datetime,timezone
from tax_genie.external_custody_s3 import S3ObjectLockCustody
from tax_genie.audit_custody import CustodyUnavailable

class FakeLockedS3:
    def __init__(self, *, locked=True):
        self.locked=locked
        self.records={}
    def put_object(self, **kw):
        self.records[(kw["Key"],"version-1")]=kw["Body"]
        return {"VersionId":"version-1"}
    def get_object_retention(self, **kw):
        return {"Retention":{"Mode":"COMPLIANCE" if self.locked else "GOVERNANCE",
                             "RetainUntilDate":datetime.now(timezone.utc)}}
    def get_object(self, **kw):
        return {"Body":io.BytesIO(self.records[(kw["Key"],kw["VersionId"])])}

class TestS3Custody(unittest.TestCase):
    def test_roundtrip_mock_s3(self):
        store=S3ObjectLockCustody(FakeLockedS3(),bucket="synthetic-only")
        payload={"synthetic":True,"seq":1}
        receipt=store.publish(payload)
        self.assertEqual(store.retrieve(receipt),payload)
        self.assertIn("version",json.loads(receipt))
    def test_reject_no_compliance_lock(self):
        store=S3ObjectLockCustody(FakeLockedS3(locked=False),bucket="synthetic-only")
        with self.assertRaises(CustodyUnavailable):
            store.publish({"synthetic":True})
    def test_detect_modified_remote_content(self):
        client=FakeLockedS3()
        store=S3ObjectLockCustody(client,bucket="synthetic-only")
        receipt=store.publish({"synthetic":True})
        marker=json.loads(receipt)
        client.records[(marker["key"],marker["version"])]=b'{"tampered":true}'
        with self.assertRaises(CustodyUnavailable):
            store.retrieve(receipt)
    def test_disabled_without_external_client(self):
        with self.assertRaises(ValueError):
            S3ObjectLockCustody(None,bucket="")
if __name__=="__main__": unittest.main()
