"""Integration test against current ClinicalTrials.gov API v2 (network required)."""
import argparse
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from scripts import fetch_registry_snapshot as fetcher
from scripts.analyze_hiddenness import flatten_study, read_jsonl
from scripts.snapshot_integrity import validate_snapshot_metadata, sha256_file


class LiveRegistryContract(unittest.TestCase):
    def test_actual_one_trial_full_query_and_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(
                page_size=2, sleep_seconds=0, max_pages=0,
                query_term="NCT02993146", output_stem="live_contract"
            )
            with patch.object(fetcher, "RAW_DIR", Path(directory)), patch.object(fetcher, "parse_args", return_value=args):
                fetcher.main()

            raw = Path(directory) / "live_contract.jsonl.gz"
            meta = json.loads((Path(directory) / "live_contract_metadata.json").read_text())
            validate_snapshot_metadata(meta, raw)
            self.assertTrue(meta["scope_complete"])
            self.assertTrue(meta["api_epoch_stable"])
            self.assertRegex(meta["api_data_timestamp"], r"^\d{4}-\d\d-\d\dT")
            self.assertEqual(meta["records_fetched"], 1)
            self.assertEqual(meta["total_count"], 1)
            self.assertEqual(meta["unique_nct_ids"], 1)
            self.assertEqual(meta["file_sha256"], sha256_file(raw))

            studies = list(read_jsonl(raw))
            self.assertEqual(len(studies), 1)
            features = flatten_study(studies[0], date(2026, 10, 15))
            self.assertEqual(features["nct_id"], "NCT02993146")
            self.assertEqual(features["study_type"], "INTERVENTIONAL")
            self.assertTrue(features["has_results"])
            self.assertGreater(features["primary_outcome_count"], 0)
            self.assertFalse(features["results_gap_2y"])
            print(json.dumps({
                "api_version": meta["api_version"],
                "data_timestamp": meta["api_data_timestamp"],
                "nct_id": features["nct_id"],
                "has_results": features["has_results"],
                "primary_outcomes": features["primary_outcome_count"],
                "snapshot_sha256": meta["file_sha256"],
            }))


if __name__ == "__main__":
    unittest.main()
