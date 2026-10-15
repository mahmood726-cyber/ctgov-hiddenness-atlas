import tempfile
import unittest
from pathlib import Path

from scripts.snapshot_integrity import SnapshotAudit, sha256_file, validate_snapshot_metadata
from scripts.fetch_registry_snapshot import assert_stable_epoch


def page(ids, next_token=None, total=2):
    payload = {
        "studies": [
            {"protocolSection": {"identificationModule": {"nctId": nct_id}}}
            for nct_id in ids
        ],
        "totalCount": total,
    }
    if next_token is not None:
        payload["nextPageToken"] = next_token
    return payload


class TestSnapshotIntegrity(unittest.TestCase):
    def test_complete_two_page_snapshot(self):
        audit = SnapshotAudit()
        self.assertEqual(audit.register_page(page(["NCT00000001"], "cursor"), None)[1], "cursor")
        self.assertIsNone(audit.register_page(page(["NCT00000002"]), "cursor")[1])
        self.assertEqual(audit.finish(complete=True)["coverage"], "complete")
        self.assertEqual(audit.records_fetched, 2)

    def test_duplicate_id_fails(self):
        audit = SnapshotAudit()
        audit.register_page(page(["NCT00000001"], "cursor"), None)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            audit.register_page(page(["NCT00000001"]), "cursor")

    def test_repeated_cursor_fails(self):
        audit = SnapshotAudit()
        with self.assertRaisesRegex(ValueError, "Unexpected pagination"):
            audit.register_page(page(["NCT00000001"], "cursor"), "cursor")
        audit.register_page(page(["NCT00000001"], "cursor"), None)
        with self.assertRaisesRegex(ValueError, "Repeated"):
            audit.register_page(page(["NCT00000002"], "cursor"), "cursor")

    def test_missing_total_and_id_fail(self):
        with self.assertRaisesRegex(ValueError, "totalCount"):
            SnapshotAudit().register_page({"studies": []}, None)
        with self.assertRaisesRegex(ValueError, "NCT"):
            SnapshotAudit().register_page(page(["invalid"], total=1), None)

    def test_premature_end_fails(self):
        audit = SnapshotAudit()
        audit.register_page(page(["NCT00000001"]), None)
        with self.assertRaisesRegex(ValueError, "cannot mark"):
            audit.finish(complete=True)
        self.assertEqual(audit.finish(complete=False)["coverage"], "partial")

    def test_validation_rejects_partial_unless_overridden(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.gz"
            path.write_bytes(b"test")
            meta = {"records_fetched": 1, "total_count": 2, "coverage": "partial", "unique_nct_ids": 1}
            with self.assertRaisesRegex(ValueError, "partial"):
                validate_snapshot_metadata(meta, path)
            validate_snapshot_metadata(meta, path, allow_partial=True)

    def test_checksum_and_legacy_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.gz"
            path.write_bytes(b"correct")
            meta = {"records_fetched": 2, "total_count": 2, "file_sha256": sha256_file(path)}
            validate_snapshot_metadata(meta, path)
            path.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                validate_snapshot_metadata(meta, path)

    def test_change_in_api_timestamp_is_detected(self):
        first = {"apiVersion": "2.0.5", "dataTimestamp": "2026-10-14T09:00:05"}
        assert_stable_epoch(first, dict(first))
        with self.assertRaisesRegex(RuntimeError, "changed during pagination"):
            assert_stable_epoch(first, {**first, "dataTimestamp": "2026-10-15T09:00:05"})

    def test_claimed_complete_with_wrong_counts_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.gz"
            path.write_bytes(b"test")
            with self.assertRaisesRegex(ValueError, "labelled complete"):
                validate_snapshot_metadata({"records_fetched": 1, "total_count": 2, "coverage": "complete"}, path)


if __name__ == "__main__":
    unittest.main()
