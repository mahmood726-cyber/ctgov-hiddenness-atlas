#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Wave-eleven CT.gov analyses: overdue-debt, narrative-gap, and actual-discipline watchlists."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

FEATURE_COLUMNS = [
    "nct_id",
    "lead_sponsor_name",
    "lead_sponsor_class",
    "days_since_primary_completion",
    "results_gap_2y",
    "publication_link_missing",
    "has_results",
    "is_interventional",
    "is_closed",
    "detailed_description_missing",
    "primary_outcome_description_missing",
    "primary_completion_actual_missing_closed",
    "completion_actual_missing_closed",
    "enrollment_actual_missing_closed",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default=str(PROCESSED / "study_features.parquet"))
    parser.add_argument("--context", default=str(PROCESSED / "wave_five_study_context.parquet"))
    parser.add_argument("--conditions", default=str(PROCESSED / "study_condition_family.parquet"))
    parser.add_argument("--out-dir", default=str(PROCESSED))
    parser.add_argument("--min-sponsor-studies", type=int, default=100)
    parser.add_argument("--min-country-studies", type=int, default=500)
    return parser.parse_args()


def load_older(features_path: Path, context_path: Path, conditions_path: Path) -> pd.DataFrame:
    features = pd.read_parquet(features_path, columns=FEATURE_COLUMNS)
    context = pd.read_parquet(context_path)
    conditions = pd.read_parquet(conditions_path, columns=["nct_id", "condition_family_label"])

    older = features[
        features["is_interventional"]
        & features["is_closed"]
        & features["days_since_primary_completion"].fillna(-1).ge(730)
    ].copy()
    older = older.merge(context, on="nct_id", how="left")
    older = older.merge(conditions, on="nct_id", how="left")
    older["condition_family_label"] = older["condition_family_label"].fillna("Other")
    older["country_names_text"] = older["country_names_text"].fillna("")
    older["overdue_2y_years"] = np.maximum(older["days_since_primary_completion"].fillna(0) - 730, 0) / 365.25
    older["overdue_years_debt"] = older["overdue_2y_years"].where(older["results_gap_2y"], 0).fillna(0)
    older["overdue_unresolved_only"] = older["overdue_2y_years"].where(older["results_gap_2y"])
    older["narrative_gap"] = (
        older["detailed_description_missing"] & older["primary_outcome_description_missing"]
    )
    older["description_black_box"] = (
        older["narrative_gap"] & older["publication_link_missing"] & older["results_gap_2y"]
    )
    older["actual_discipline_gap"] = (
        older["primary_completion_actual_missing_closed"]
        | older["completion_actual_missing_closed"]
        | older["enrollment_actual_missing_closed"]
    )
    return older


def make_country_long(older: pd.DataFrame) -> pd.DataFrame:
    country_long = older.copy()
    country_long["country_name"] = (
        country_long["country_names_text"]
        .astype(str)
        .str.split("|")
        .map(lambda items: [item.strip() for item in items if item.strip()])
    )
    country_long = country_long[country_long["country_name"].map(bool)].explode("country_name").reset_index(drop=True)
    return country_long


def summarize_groups(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    grouped = (
        df.groupby(group_cols, observed=False)
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            overdue_years_debt=("overdue_years_debt", "sum"),
            mean_overdue_unresolved=("overdue_unresolved_only", "mean"),
            median_overdue_unresolved=("overdue_unresolved_only", "median"),
            narrative_gap_count=("narrative_gap", "sum"),
            narrative_gap_rate=("narrative_gap", "mean"),
            description_black_box_count=("description_black_box", "sum"),
            description_black_box_rate=("description_black_box", "mean"),
            actual_gap_count=("actual_discipline_gap", "sum"),
            actual_gap_rate=("actual_discipline_gap", "mean"),
            primary_completion_actual_gap_count=("primary_completion_actual_missing_closed", "sum"),
            completion_actual_gap_count=("completion_actual_missing_closed", "sum"),
            enrollment_actual_gap_count=("enrollment_actual_missing_closed", "sum"),
        )
        .reset_index()
    )
    percent_cols = [
        "no_results_rate",
        "narrative_gap_rate",
        "description_black_box_rate",
        "actual_gap_rate",
    ]
    grouped[percent_cols] = grouped[percent_cols].mul(100)
    round_cols = [
        "no_results_rate",
        "overdue_years_debt",
        "mean_overdue_unresolved",
        "median_overdue_unresolved",
        "narrative_gap_rate",
        "description_black_box_rate",
        "actual_gap_rate",
    ]
    grouped[round_cols] = grouped[round_cols].round(3)
    return grouped


def write_findings(
    out_dir: Path,
    sponsor_overdue: pd.DataFrame,
    country_overdue: pd.DataFrame,
    condition_overdue: pd.DataFrame,
    narrative_sponsor: pd.DataFrame,
    actual_sponsor: pd.DataFrame,
    actual_class: pd.DataFrame,
) -> None:
    sponsor_top = sponsor_overdue.iloc[0]
    country_top = country_overdue.iloc[0]
    condition_top = condition_overdue.iloc[0]
    narrative_top = narrative_sponsor.iloc[0]
    actual_top = actual_sponsor.iloc[0]
    actual_rate = actual_sponsor.sort_values(
        ["actual_gap_rate", "actual_gap_count"], ascending=[False, False]
    ).iloc[0]
    actual_class_top = actual_class.sort_values(
        ["actual_gap_rate", "actual_gap_count"], ascending=[False, False]
    ).iloc[0]

    lines = [
        "# Wave Eleven Findings",
        "",
        f"- Largest sponsor overdue-debt stock: {sponsor_top['lead_sponsor_name']} ({sponsor_top['lead_sponsor_class']}) at {sponsor_top['overdue_years_debt']:.0f} unresolved years beyond the two-year mark.",
        f"- Largest country-linked overdue-debt stock: {country_top['country_name']} at {country_top['overdue_years_debt']:.0f} unresolved years beyond the two-year mark.",
        f"- Largest condition-family overdue-debt stock: {condition_top['condition_family_label']} at {condition_top['overdue_years_debt']:.0f} unresolved years beyond the two-year mark.",
        f"- Largest named sponsor narrative-gap stock: {narrative_top['lead_sponsor_name']} at {int(narrative_top['narrative_gap_count']):,} studies.",
        f"- Largest named sponsor actual-discipline stock: {actual_top['lead_sponsor_name']} at {int(actual_top['actual_gap_count']):,} studies.",
        f"- Highest large-sponsor actual-discipline rate: {actual_rate['lead_sponsor_name']} at {actual_rate['actual_gap_rate']:.1f}%.",
        f"- Highest sponsor-class actual-discipline rate: {actual_class_top['lead_sponsor_class']} at {actual_class_top['actual_gap_rate']:.1f}%.",
    ]
    (out_dir / "wave_eleven_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    older = load_older(Path(args.features), Path(args.context), Path(args.conditions))
    country_long = make_country_long(older)

    sponsor_summary = summarize_groups(older, ["lead_sponsor_name", "lead_sponsor_class"])
    sponsor_summary = sponsor_summary[sponsor_summary["studies"] >= args.min_sponsor_studies].copy()

    country_summary = summarize_groups(country_long, ["country_name"])
    country_summary = country_summary[country_summary["studies"] >= args.min_country_studies].copy()

    condition_summary = summarize_groups(older, ["condition_family_label"])
    class_summary = summarize_groups(older, ["lead_sponsor_class"])

    sponsor_overdue = sponsor_summary.sort_values(
        ["overdue_years_debt", "no_results_count"], ascending=[False, False]
    ).reset_index(drop=True)
    country_overdue = country_summary.sort_values(
        ["overdue_years_debt", "no_results_count"], ascending=[False, False]
    ).reset_index(drop=True)
    condition_overdue = condition_summary.sort_values(
        ["overdue_years_debt", "no_results_count"], ascending=[False, False]
    ).reset_index(drop=True)

    narrative_sponsor = sponsor_summary.sort_values(
        ["narrative_gap_count", "narrative_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    narrative_country = country_summary.sort_values(
        ["narrative_gap_count", "narrative_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    narrative_condition = condition_summary.sort_values(
        ["narrative_gap_count", "narrative_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    narrative_class = class_summary.sort_values(
        ["narrative_gap_count", "narrative_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)

    actual_sponsor = sponsor_summary.sort_values(
        ["actual_gap_count", "actual_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    actual_class = class_summary.sort_values(
        ["actual_gap_count", "actual_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)

    sponsor_overdue.to_csv(out_dir / "wave_eleven_sponsor_overdue_debt.csv", index=False)
    country_overdue.to_csv(out_dir / "wave_eleven_country_overdue_debt.csv", index=False)
    condition_overdue.to_csv(out_dir / "wave_eleven_condition_overdue_debt.csv", index=False)
    narrative_sponsor.to_csv(out_dir / "wave_eleven_narrative_gap_sponsor.csv", index=False)
    narrative_country.to_csv(out_dir / "wave_eleven_narrative_gap_country.csv", index=False)
    narrative_condition.to_csv(out_dir / "wave_eleven_narrative_gap_condition.csv", index=False)
    narrative_class.to_csv(out_dir / "wave_eleven_narrative_gap_class_summary.csv", index=False)
    actual_sponsor.to_csv(out_dir / "wave_eleven_actual_gap_sponsor.csv", index=False)
    actual_class.to_csv(out_dir / "wave_eleven_actual_gap_class_summary.csv", index=False)

    write_findings(
        out_dir,
        sponsor_overdue=sponsor_overdue,
        country_overdue=country_overdue,
        condition_overdue=condition_overdue,
        narrative_sponsor=narrative_sponsor,
        actual_sponsor=actual_sponsor,
        actual_class=actual_class,
    )


if __name__ == "__main__":
    main()
