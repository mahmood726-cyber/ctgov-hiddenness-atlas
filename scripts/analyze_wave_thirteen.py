#!/usr/bin/env python3
"""Wave-thirteen CT.gov analyses: description black-box geography and enrollment-gap discipline."""

from __future__ import annotations

import argparse
from pathlib import Path

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
    "is_interventional",
    "is_closed",
    "detailed_description_missing",
    "primary_outcome_description_missing",
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
    older["description_black_box"] = (
        older["results_gap_2y"]
        & older["publication_link_missing"]
        & older["detailed_description_missing"]
        & older["primary_outcome_description_missing"]
    )
    older["enrollment_gap"] = older["enrollment_actual_missing_closed"]
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


def summarize(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    grouped = (
        df.groupby(group_cols, observed=False)
        .agg(
            studies=("nct_id", "size"),
            description_black_box_count=("description_black_box", "sum"),
            description_black_box_rate=("description_black_box", "mean"),
            enrollment_gap_count=("enrollment_gap", "sum"),
            enrollment_gap_rate=("enrollment_gap", "mean"),
        )
        .reset_index()
    )
    grouped[["description_black_box_rate", "enrollment_gap_rate"]] = grouped[
        ["description_black_box_rate", "enrollment_gap_rate"]
    ].mul(100).round(3)
    return grouped


def write_findings(
    out_dir: Path,
    country_description: pd.DataFrame,
    condition_description: pd.DataFrame,
    sponsor_enrollment: pd.DataFrame,
    country_enrollment: pd.DataFrame,
    condition_enrollment: pd.DataFrame,
    class_enrollment: pd.DataFrame,
) -> None:
    country_desc_rate = country_description.sort_values(
        ["description_black_box_rate", "description_black_box_count"], ascending=[False, False]
    ).iloc[0]
    condition_desc_rate = condition_description.sort_values(
        ["description_black_box_rate", "description_black_box_count"], ascending=[False, False]
    ).iloc[0]
    sponsor_enrollment_rate = sponsor_enrollment.sort_values(
        ["enrollment_gap_rate", "enrollment_gap_count"], ascending=[False, False]
    ).iloc[0]
    country_enrollment_rate = country_enrollment.sort_values(
        ["enrollment_gap_rate", "enrollment_gap_count"], ascending=[False, False]
    ).iloc[0]
    condition_enrollment_rate = condition_enrollment.sort_values(
        ["enrollment_gap_rate", "enrollment_gap_count"], ascending=[False, False]
    ).iloc[0]
    class_enrollment_rate = class_enrollment.sort_values(
        ["enrollment_gap_rate", "enrollment_gap_count"], ascending=[False, False]
    ).iloc[0]

    lines = [
        "# Wave Thirteen Findings",
        "",
        f"- Largest country-linked description-black-box stock: {country_description.iloc[0]['country_name']} at {int(country_description.iloc[0]['description_black_box_count']):,} studies; highest large-country rate is {country_desc_rate['country_name']} at {country_desc_rate['description_black_box_rate']:.1f}%.",
        f"- Largest condition-family description-black-box stock: {condition_description.iloc[0]['condition_family_label']} at {int(condition_description.iloc[0]['description_black_box_count']):,} studies; highest large-family rate is {condition_desc_rate['condition_family_label']} at {condition_desc_rate['description_black_box_rate']:.1f}%.",
        f"- Largest sponsor enrollment-gap stock: {sponsor_enrollment.iloc[0]['lead_sponsor_name']} at {int(sponsor_enrollment.iloc[0]['enrollment_gap_count']):,} studies; highest large-sponsor rate is {sponsor_enrollment_rate['lead_sponsor_name']} at {sponsor_enrollment_rate['enrollment_gap_rate']:.1f}%.",
        f"- Largest country-linked enrollment-gap stock: {country_enrollment.iloc[0]['country_name']} at {int(country_enrollment.iloc[0]['enrollment_gap_count']):,} studies; highest large-country rate is {country_enrollment_rate['country_name']} at {country_enrollment_rate['enrollment_gap_rate']:.1f}%.",
        f"- Largest condition-family enrollment-gap stock: {condition_enrollment.iloc[0]['condition_family_label']} at {int(condition_enrollment.iloc[0]['enrollment_gap_count']):,} studies; highest large-family rate is {condition_enrollment_rate['condition_family_label']} at {condition_enrollment_rate['enrollment_gap_rate']:.1f}%.",
        f"- Highest sponsor-class enrollment-gap rate: {class_enrollment_rate['lead_sponsor_class']} at {class_enrollment_rate['enrollment_gap_rate']:.1f}%.",
    ]
    (out_dir / "wave_thirteen_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    older = load_older(Path(args.features), Path(args.context), Path(args.conditions))
    country_long = make_country_long(older)

    sponsor_summary = summarize(older, ["lead_sponsor_name", "lead_sponsor_class"])
    sponsor_summary = sponsor_summary[sponsor_summary["studies"] >= args.min_sponsor_studies].copy()

    country_summary = summarize(country_long, ["country_name"])
    country_summary = country_summary[country_summary["studies"] >= args.min_country_studies].copy()

    condition_summary = summarize(older, ["condition_family_label"])
    condition_summary = condition_summary[condition_summary["studies"] >= args.min_condition_studies].copy()

    class_summary = summarize(older, ["lead_sponsor_class"])

    country_description = country_summary.sort_values(
        ["description_black_box_count", "description_black_box_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    condition_description = condition_summary.sort_values(
        ["description_black_box_count", "description_black_box_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    sponsor_enrollment = sponsor_summary.sort_values(
        ["enrollment_gap_count", "enrollment_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    country_enrollment = country_summary.sort_values(
        ["enrollment_gap_count", "enrollment_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    condition_enrollment = condition_summary.sort_values(
        ["enrollment_gap_count", "enrollment_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    class_enrollment = class_summary.sort_values(
        ["enrollment_gap_count", "enrollment_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)

    country_description.to_csv(out_dir / "wave_thirteen_country_description_black_box.csv", index=False)
    condition_description.to_csv(out_dir / "wave_thirteen_condition_description_black_box.csv", index=False)
    sponsor_enrollment.to_csv(out_dir / "wave_thirteen_sponsor_enrollment_gap.csv", index=False)
    country_enrollment.to_csv(out_dir / "wave_thirteen_country_enrollment_gap.csv", index=False)
    condition_enrollment.to_csv(out_dir / "wave_thirteen_condition_enrollment_gap.csv", index=False)
    class_enrollment.to_csv(out_dir / "wave_thirteen_enrollment_gap_class_summary.csv", index=False)

    write_findings(
        out_dir,
        country_description=country_description,
        condition_description=condition_description,
        sponsor_enrollment=sponsor_enrollment,
        country_enrollment=country_enrollment,
        condition_enrollment=condition_enrollment,
        class_enrollment=class_enrollment,
    )


if __name__ == "__main__":
    main()
