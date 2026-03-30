#!/usr/bin/env python3
"""Wave-fourteen CT.gov analyses: narrative-gap geography and primary-outcome text gaps."""

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
    "is_interventional",
    "is_closed",
    "detailed_description_missing",
    "primary_outcome_description_missing",
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
    older["country_names_text"] = older["country_names_text"].fillna("")
    older["condition_family_label"] = older["condition_family_label"].fillna("Other")
    older["narrative_gap"] = older["detailed_description_missing"] & older["primary_outcome_description_missing"]
    older["primary_outcome_gap"] = older["primary_outcome_description_missing"]
    older["detailed_description_gap"] = older["detailed_description_missing"]
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
            narrative_gap_count=("narrative_gap", "sum"),
            narrative_gap_rate=("narrative_gap", "mean"),
            primary_outcome_gap_count=("primary_outcome_gap", "sum"),
            primary_outcome_gap_rate=("primary_outcome_gap", "mean"),
            detailed_description_gap_count=("detailed_description_gap", "sum"),
            detailed_description_gap_rate=("detailed_description_gap", "mean"),
        )
        .reset_index()
    )
    rate_cols = [
        "narrative_gap_rate",
        "primary_outcome_gap_rate",
        "detailed_description_gap_rate",
    ]
    grouped[rate_cols] = grouped[rate_cols].mul(100).round(3)
    return grouped


def write_findings(
    out_dir: Path,
    country_narrative: pd.DataFrame,
    condition_narrative: pd.DataFrame,
    sponsor_primary: pd.DataFrame,
    country_primary: pd.DataFrame,
    condition_primary: pd.DataFrame,
    primary_class: pd.DataFrame,
) -> None:
    country_narrative_rate = country_narrative.sort_values(
        ["narrative_gap_rate", "narrative_gap_count"], ascending=[False, False]
    ).iloc[0]
    condition_narrative_rate = condition_narrative.sort_values(
        ["narrative_gap_rate", "narrative_gap_count"], ascending=[False, False]
    ).iloc[0]
    sponsor_primary_rate = sponsor_primary.sort_values(
        ["primary_outcome_gap_rate", "primary_outcome_gap_count"], ascending=[False, False]
    ).iloc[0]
    country_primary_rate = country_primary.sort_values(
        ["primary_outcome_gap_rate", "primary_outcome_gap_count"], ascending=[False, False]
    ).iloc[0]
    condition_primary_rate = condition_primary.sort_values(
        ["primary_outcome_gap_rate", "primary_outcome_gap_count"], ascending=[False, False]
    ).iloc[0]
    primary_class_rate = primary_class.sort_values(
        ["primary_outcome_gap_rate", "primary_outcome_gap_count"], ascending=[False, False]
    ).iloc[0]

    lines = [
        "# Wave Fourteen Findings",
        "",
        f"- Largest country-linked narrative-gap stock: {country_narrative.iloc[0]['country_name']} at {int(country_narrative.iloc[0]['narrative_gap_count']):,} studies; highest large-country narrative-gap rate is {country_narrative_rate['country_name']} at {country_narrative_rate['narrative_gap_rate']:.1f}%.",
        f"- Largest condition-family narrative-gap stock: {condition_narrative.iloc[0]['condition_family_label']} at {int(condition_narrative.iloc[0]['narrative_gap_count']):,} studies; highest large-family narrative-gap rate is {condition_narrative_rate['condition_family_label']} at {condition_narrative_rate['narrative_gap_rate']:.1f}%.",
        f"- Largest sponsor primary-outcome-gap stock: {sponsor_primary.iloc[0]['lead_sponsor_name']} at {int(sponsor_primary.iloc[0]['primary_outcome_gap_count']):,} studies; highest large-sponsor rate is {sponsor_primary_rate['lead_sponsor_name']} at {sponsor_primary_rate['primary_outcome_gap_rate']:.1f}%.",
        f"- Largest country-linked primary-outcome-gap stock: {country_primary.iloc[0]['country_name']} at {int(country_primary.iloc[0]['primary_outcome_gap_count']):,} studies; highest large-country rate is {country_primary_rate['country_name']} at {country_primary_rate['primary_outcome_gap_rate']:.1f}%.",
        f"- Largest condition-family primary-outcome-gap stock: {condition_primary.iloc[0]['condition_family_label']} at {int(condition_primary.iloc[0]['primary_outcome_gap_count']):,} studies; highest large-family rate is {condition_primary_rate['condition_family_label']} at {condition_primary_rate['primary_outcome_gap_rate']:.1f}%.",
        f"- Highest sponsor-class primary-outcome-gap rate: {primary_class_rate['lead_sponsor_class']} at {primary_class_rate['primary_outcome_gap_rate']:.1f}%.",
    ]
    (out_dir / "wave_fourteen_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    country_narrative = country_summary.sort_values(
        ["narrative_gap_count", "narrative_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    condition_narrative = condition_summary.sort_values(
        ["narrative_gap_count", "narrative_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    sponsor_primary = sponsor_summary.sort_values(
        ["primary_outcome_gap_count", "primary_outcome_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    country_primary = country_summary.sort_values(
        ["primary_outcome_gap_count", "primary_outcome_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    condition_primary = condition_summary.sort_values(
        ["primary_outcome_gap_count", "primary_outcome_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    primary_class = class_summary.sort_values(
        ["primary_outcome_gap_count", "primary_outcome_gap_rate"], ascending=[False, False]
    ).reset_index(drop=True)

    country_narrative.to_csv(out_dir / "wave_fourteen_country_narrative_gap.csv", index=False)
    condition_narrative.to_csv(out_dir / "wave_fourteen_condition_narrative_gap.csv", index=False)
    sponsor_primary.to_csv(out_dir / "wave_fourteen_sponsor_primary_outcome_gap.csv", index=False)
    country_primary.to_csv(out_dir / "wave_fourteen_country_primary_outcome_gap.csv", index=False)
    condition_primary.to_csv(out_dir / "wave_fourteen_condition_primary_outcome_gap.csv", index=False)
    primary_class.to_csv(out_dir / "wave_fourteen_primary_outcome_gap_class_summary.csv", index=False)

    write_findings(
        out_dir,
        country_narrative=country_narrative,
        condition_narrative=condition_narrative,
        sponsor_primary=sponsor_primary,
        country_primary=country_primary,
        condition_primary=condition_primary,
        primary_class=primary_class,
    )


if __name__ == "__main__":
    main()
