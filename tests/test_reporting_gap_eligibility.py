"""Scientific regression tests: who actually enters a results-gap denominator."""
import unittest
from datetime import date

from scripts.analyze_hiddenness import (
    flatten_study, parse_exact_day, resolve_snapshot_as_of,
    summarize_groups, years_elapsed,
)


AS_OF = date(2026, 3, 29)


def study(nct_id="NCT00000001", *, primary="2024-03-29", pcd_type="ACTUAL",
          status="COMPLETED", study_type="INTERVENTIONAL",
          has_results=False, results_date=None, sponsor="INDUSTRY"):
    status_module = {
        "overallStatus": status,
        "primaryCompletionDateStruct": {"date": primary, "type": pcd_type},
    }
    if results_date is not None:
        status_module["resultsFirstPostDateStruct"] = {"date": results_date}
    trial = {
        "protocolSection": {
            "identificationModule": {"nctId": nct_id},
            "statusModule": status_module,
            "designModule": {"studyType": study_type},
            "sponsorCollaboratorsModule": {
                "leadSponsor": {"name": "Example sponsor", "class": sponsor}
            },
        },
    }
    if has_results is not None:
        trial["hasResults"] = has_results
    return trial


class ReportingGapEligibilityTests(unittest.TestCase):
    def test_actual_day_precise_closed_interventional_enters_both_denominators(self):
        row = flatten_study(study(primary="2024-03-29"), AS_OF)
        self.assertTrue(row["eligible_results_gap_1y"])
        self.assertTrue(row["eligible_results_gap_2y"])
        self.assertTrue(row["results_gap_1y"])
        self.assertTrue(row["results_gap_2y"])
        self.assertEqual(row["primary_completion_date_precision"], "DAY")
        self.assertEqual(row["days_since_primary_completion"], 730)

    def test_month_only_or_year_only_date_does_not_invent_first_of_month(self):
        for value in ["2024-03", "2024", "2024-02-30"]:
            with self.subTest(value=value):
                row = flatten_study(study(primary=value), AS_OF)
                self.assertEqual(row["primary_completion_date"], value)
                self.assertFalse(row["eligible_results_gap_1y"])
                self.assertFalse(row["eligible_results_gap_2y"])
                self.assertIsNone(row["days_since_primary_completion"])
                self.assertIsNone(parse_exact_day(value))

    def test_estimated_primary_completion_is_not_actual_eligible(self):
        row = flatten_study(study(primary="2021-03-01", pcd_type="ESTIMATED"), AS_OF)
        self.assertFalse(row["eligible_results_gap_2y"])
        self.assertFalse(row["results_gap_2y"])

    def test_observational_or_ongoing_trials_do_not_enter_denominator(self):
        trials = [
            study(status="RECRUITING", primary="2020-01-01"),
            study(study_type="OBSERVATIONAL", primary="2020-01-01"),
        ]
        for x in trials:
            row = flatten_study(x, AS_OF)
            self.assertFalse(row["eligible_results_gap_1y"])
            self.assertFalse(row["results_gap_1y"])

    def test_unknown_or_inconsistent_posting_status_never_implies_no_results(self):
        unknown = flatten_study(study(has_results=None), AS_OF)
        self.assertFalse(unknown["results_status_known"])
        self.assertFalse(unknown["results_gap_2y"])
        self.assertFalse(unknown["eligible_results_gap_2y"])

        conflict = flatten_study(study(results_date="2024-05-01"), AS_OF)
        self.assertTrue(conflict["results_status_conflict"])
        self.assertFalse(conflict["eligible_results_gap_2y"])

        posted = flatten_study(study(has_results=True, results_date="2024-05-01"), AS_OF)
        self.assertTrue(posted["eligible_results_gap_2y"])
        self.assertFalse(posted["results_gap_2y"])
        self.assertEqual(posted["results_reporting_lag_days"], 33)

    def test_leap_anniversary_is_calendar_based(self):
        self.assertFalse(years_elapsed(date(2024, 2, 29), date(2025, 2, 28), 1))
        self.assertTrue(years_elapsed(date(2024, 2, 29), date(2025, 3, 1), 1))
        self.assertFalse(years_elapsed(date(2024, 2, 29), date(2026, 2, 28), 2))
        self.assertTrue(years_elapsed(date(2024, 2, 29), date(2026, 3, 1), 2))

    def test_denominator_matches_exact_population_used_for_numerator(self):
        import pandas as pd
        studies = [
            study("NCT00000001", primary="2023-01-01", has_results=False),
            study("NCT00000002", primary="2023-01-01", has_results=True),
            study("NCT00000003", primary="2023-01", has_results=False),
            study("NCT00000004", primary="2023-01-01", study_type="OBSERVATIONAL"),
            study("NCT00000005", primary="2023-01-01", status="RECRUITING"),
            study("NCT00000006", primary="2023-01-01", pcd_type="ESTIMATED"),
        ]
        df = pd.DataFrame([flatten_study(t, AS_OF) for t in studies])
        result = summarize_groups(df, "lead_sponsor_class").iloc[0]
        self.assertEqual(int(result["studies"]), 6)
        self.assertEqual(int(result["eligible_results_gap_1y_count"]), 2)
        self.assertEqual(int(result["eligible_results_gap_2y_count"]), 2)
        self.assertEqual(int(result["results_gap_1y_count"]), 1)
        self.assertEqual(int(result["results_gap_2y_count"]), 1)
        self.assertAlmostEqual(float(result["results_gap_2y_rate_eligible"]), 50.0)

    def test_snapshot_date_must_match_source_epoch_not_wall_clock(self):
        meta = {"api_data_timestamp": "2026-03-29T08:30:00Z",
                "fetched_at": "2026-03-30T00:01:00+00:00"}
        self.assertEqual(resolve_snapshot_as_of(meta), date(2026, 3, 29))
        self.assertEqual(resolve_snapshot_as_of(meta, "2026-03-29"), date(2026, 3, 29))
        with self.assertRaisesRegex(ValueError, "differing"):
            resolve_snapshot_as_of(meta, "2026-10-18")
        with self.assertRaisesRegex(ValueError, "lacks a valid"):
            resolve_snapshot_as_of({})
        self.assertEqual(
            resolve_snapshot_as_of({"fetched_at": "2026-03-29T15:00:00+00:00"}),
            date(2026, 3, 29),
        )


if __name__ == "__main__":
    unittest.main()
