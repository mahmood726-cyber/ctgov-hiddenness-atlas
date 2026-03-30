#!/usr/bin/env python3
"""Wave-twelve CT.gov analyses: ancient backlog, description black-box, and completion-timing repeaters."""

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
    parser.add_argument("--min-condition-studies", type=int, default=1000)
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
    older["ancient_5y"] = older["results_gap_2y"] & older["overdue_2y_years"].ge(5)
    older["ancient_10y"] = older["results_gap_2y"] & older["overdue_2y_years"].ge(10)
    older["ancient_10y_overdue_years"] = older["overdue_2y_years"].where(older["ancient_10y"], 0).fillna(0)
    older["ancient_10y_overdue_unresolved"] = older["overdue_2y_years"].where(older["ancient_10y"])
    older["description_black_box"] = (
        older["results_gap_2y"]
        & older["publication_link_missing"]
        & older["detailed_description_missing"]
        & older["primary_outcome_description_missing"]
    )
    older["completion_timing_gap"] = (
        older["primary_completion_actual_missing_closed"] | older["completion_actual_missing_closed"]
    )
    older["primary_completion_gap"] = older["primary_completion_actual_missing_closed"]
    older["completion_actual_gap"] = older["completion_actual_missing_closed"]
    return older


def make_country_long(older: pd.DataFrame) -> pd.DataFrame:
    country_long = older.copy()
    country_long["country_name"] = (
        country_long["country_names_text"]
        .astype(str)
        .str.split("|")
        .map(lambda items: [item.strip() for item in items if item.strip()])
    )
    return country_long[country_long["country_name"].map(bool)].explode("country_name").reset_index(drop=True)


def summarize_groups(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    grouped = (
        df.groupby(group_cols, observed=False)
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            ancient_5y_count=("ancient_5y", "sum"),
            ancient_5y_rate=("ancient_5y", "mean"),
            ancient_10y_count=("ancient_10y", "sum"),
            ancient_10y_rate=("ancient_10y", "mean"),
            ancient_10y_overdue_years=("ancient_10y_overdue_years", "sum"),
            mean_ancient_10y_overdue=("ancient_10y_overdue_unresolved", "mean"),
            median_ancient_10y_overdue=("ancient_10y_overdue_unresolved", "median"),
            description_black_box_count=("description_black_box", "sum"),
            description_black_box_rate=("description_black_box", "mean"),
            completion_timing_gap_count=("completion_timing_gap", "sum"),
            completion_timing_gap_rate=("completion_timing_gap", "mean"),
            primary_completion_gap_count=("primary_completion_gap", "sum"),
            primary_completion_gap_rate=("primary_completion_gap", "mean"),
            completion_actual_gap_count=("completion_actual_gap", "sum"),
            completion_actual_gap_rate=("completion_actual_gap", "mean"),
        )
        .reset_index()
    )
    percent_cols = [
        "no_results_rate",
        "ancient_5y_rate",
        "ancient_10y_rate",
        "description_black_box_rate",
        "completion_timing_gap_rate",
        "primary_completion_gap_rate",
        "completion_actual_gap_rate",
    ]
    grouped[percent_cols] = grouped[percent_cols].mul(100)
    round_cols = [
        "no_results_rate",
        "ancient_5y_rate",
        "ancient_10y_rate",
        "ancient_10y_overdue_years",
        "mean_ancient_10y_overdue",
        "median_ancient_10y_overdue",
        "description_black_box_rate",
        "completion_timing_gap_rate",
        "primary_completion_gap_rate",
        "completion_actual_gap_rate",
    ]
    grouped[round_cols] = grouped[round_cols].round(3)
    return grouped


def write_findings(
    out_dir: Path,
    older: pd.DataFrame,
    sponsor_ancient: pd.DataFrame,
    country_ancient: pd.DataFrame,
    condition_ancient: pd.DataFrame,
    description_sponsor: pd.DataFrame,
    description_class: pd.DataFrame,
    completion_sponsor: pd.DataFrame,
    completion_class: pd.DataFrame,
) -> None:
    ancient_total = int(older["ancient_10y"].sum())
    description_total = int(older["description_black_box"].sum())
    completion_total = int(older["completion_timing_gap"].sum())

    sponsor_ancient_top = sponsor_ancient.iloc[0]
    sponsor_ancient_rate = sponsor_ancient.sort_values(
        ["ancient_10y_rate", "ancient_10y_count"], ascending=[False, False]
    ).iloc[0]
    country_ancient_top = country_ancient.iloc[0]
    country_ancient_rate = country_ancient.sort_values(
        ["ancient_10y_rate", "ancient_10y_count"], ascending=[False, False]
    ).iloc[0]
    condition_ancient_top = condition_ancient.iloc[0]
    condition_ancient_rate = condition_ancient.sort_values(
        ["ancient_10y_rate", "ancient_10y_count"], ascending=[False, False]
    ).iloc[0]
    description_top = description_sponsor.iloc[0]
    description_rate = description_sponsor.sort_values(
        ["description_black_box_rate", "description_black_box_count"], ascending=[False, False]
    ).iloc[0]
    description_class_top = description_class.sort_values(
        ["description_black_box_rate", "description_black_box_count"], ascending=[False, False]
    ).iloc[0]
    completion_top = completion_sponsor.iloc[0]
    completion_rate = completion_sponsor.sort_values(
        ["completion_timing_gap_rate", "completion_timing_gap_count"], ascending=[False, False]
    ).iloc[0]
    completion_class_top = completion_class.sort_values(
        ["completion_timing_gap_rate", "completion_timing_gap_count"], ascending=[False, False]
    ).iloc[0]

    lines = [
        "# Wave Twelve Findings",
        "",
        f"- Ancient backlog stock: {ancient_total:,} older studies remain unresolved at least ten years beyond the two-year results mark.",
        f"- Largest named sponsor ancient-backlog stock: {sponsor_ancient_top['lead_sponsor_name']} ({sponsor_ancient_top['lead_sponsor_class']}) at {int(sponsor_ancient_top['ancient_10y_count']):,} studies, while {sponsor_ancient_rate['lead_sponsor_name']} has the highest large-sponsor rate at {sponsor_ancient_rate['ancient_10y_rate']:.1f}%.",
        f"- Largest country-linked ancient-backlog stock: {country_ancient_top['country_name']} at {int(country_ancient_top['ancient_10y_count']):,} studies, while {country_ancient_rate['country_name']} has the highest large-country rate at {country_ancient_rate['ancient_10y_rate']:.1f}%.",
        f"- Largest condition-family ancient-backlog stock: {condition_ancient_top['condition_family_label']} at {int(condition_ancient_top['ancient_10y_count']):,} studies, while {condition_ancient_rate['condition_family_label']} has the highest large-family rate at {condition_ancient_rate['ancient_10y_rate']:.1f}%.",
        f"- Description black-box stock: {description_total:,} studies, led by {description_top['lead_sponsor_name']} at {int(description_top['description_black_box_count']):,}; highest large-sponsor rate is {description_rate['lead_sponsor_name']} at {description_rate['description_black_box_rate']:.1f}%, and highest sponsor-class rate is {description_class_top['lead_sponsor_class']} at {description_class_top['description_black_box_rate']:.1f}%.",
        f"- Completion-timing gap stock: {completion_total:,} studies, led by {completion_top['lead_sponsor_name']} at {int(completion_top['completion_timing_gap_count']):,}; highest large-sponsor rate is {completion_rate['lead_sponsor_name']} at {completion_rate['completion_timing_gap_rate']:.1f}%, and highest sponsor-class rate is {completion_class_top['lead_sponsor_class']} at {completion_class_top['completion_timing_gap_rate']:.1f}%.",
    ]
    (out_dir / "wave_twelve_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    condition_summary = condition_summary[condition_summary["studies"] >= args.min_condition_studies].copy()

    class_summary = summarize_groups(older, ["lead_sponsor_class"])

    sponsor_ancient = sponsor_summary.sort_values(
        ["ancient_10y_count", "ancient_10y_overdue_years", "ancient_10y_rate"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    country_ancient = country_summary.sort_values(
        ["ancient_10y_count", "ancient_10y_overdue_years", "ancient_10y_rate"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    condition_ancient = condition_summary.sort_values(
        ["ancient_10y_count", "ancient_10y_overdue_years", "ancient_10y_rate"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    description_sponsor = sponsor_summary.sort_values(
        ["description_black_box_count", "description_black_box_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    description_class = class_summary.sort_values(
        ["description_black_box_count", "description_black_box_rate"], ascending=[False, False]
    ).reset_index(drop=True)

    completion_sponsor = sponsor_summary.sort_values(
        ["completion_timing_gap_count", "completion_timing_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    completion_class = class_summary.sort_values(
        ["completion_timing_gap_count", "completion_timing_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)

    sponsor_ancient.to_csv(out_dir / "wave_twelve_sponsor_ancient_backlog.csv", index=False)
    country_ancient.to_csv(out_dir / "wave_twelve_country_ancient_backlog.csv", index=False)
    condition_ancient.to_csv(out_dir / "wave_twelve_condition_ancient_backlog.csv", index=False)
    description_sponsor.to_csv(out_dir / "wave_twelve_description_black_box_sponsor.csv", index=False)
    description_class.to_csv(out_dir / "wave_twelve_description_black_box_class_summary.csv", index=False)
    completion_sponsor.to_csv(out_dir / "wave_twelve_completion_timing_sponsor.csv", index=False)
    completion_class.to_csv(out_dir / "wave_twelve_completion_timing_class_summary.csv", index=False)

    write_findings(
        out_dir,
        older=older,
        sponsor_ancient=sponsor_ancient,
        country_ancient=country_ancient,
        condition_ancient=condition_ancient,
        description_sponsor=description_sponsor,
        description_class=description_class,
        completion_sponsor=completion_sponsor,
        completion_class=completion_class,
    )


if __name__ == "__main__":
    main()
