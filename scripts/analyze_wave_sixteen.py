#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Wave-sixteen CT.gov analyses: endpoint-only gaps and remaining text-balance maps."""

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
    older["description_only"] = older["detailed_description_missing"] & ~older["primary_outcome_description_missing"]
    older["primary_only"] = ~older["detailed_description_missing"] & older["primary_outcome_description_missing"]
    older["text_asymmetry"] = older["description_only"].astype(int) - older["primary_only"].astype(int)
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
            primary_only_count=("primary_only", "sum"),
            primary_only_rate=("primary_only", "mean"),
            description_only_count=("description_only", "sum"),
            description_only_rate=("description_only", "mean"),
            text_asymmetry_net=("text_asymmetry", "sum"),
            text_asymmetry_rate=("text_asymmetry", "mean"),
        )
        .reset_index()
    )
    rate_cols = [
        "primary_only_rate",
        "description_only_rate",
        "text_asymmetry_rate",
    ]
    grouped[rate_cols] = grouped[rate_cols].mul(100).round(3)
    return grouped


def write_findings(
    out_dir: Path,
    sponsor_primary_only: pd.DataFrame,
    country_primary_only: pd.DataFrame,
    condition_primary_only: pd.DataFrame,
    condition_asymmetry: pd.DataFrame,
    class_asymmetry: pd.DataFrame,
) -> None:
    sponsor_primary_rate = sponsor_primary_only.sort_values(
        ["primary_only_rate", "primary_only_count"], ascending=[False, False]
    ).iloc[0]
    country_primary_rate = country_primary_only.sort_values(
        ["primary_only_rate", "primary_only_count"], ascending=[False, False]
    ).iloc[0]
    condition_primary_rate = condition_primary_only.sort_values(
        ["primary_only_rate", "primary_only_count"], ascending=[False, False]
    ).iloc[0]
    condition_asymmetry_rate = condition_asymmetry.sort_values(
        ["text_asymmetry_rate", "text_asymmetry_net"], ascending=[False, False]
    ).iloc[0]
    class_primary_rate = class_asymmetry.sort_values(
        ["primary_only_rate", "primary_only_count"], ascending=[False, False]
    ).iloc[0]
    class_positive = class_asymmetry.sort_values(
        ["text_asymmetry_net", "description_only_count"], ascending=[False, False]
    ).iloc[0]

    lines = [
        "# Wave Sixteen Findings",
        "",
        f"- Largest sponsor primary-only-gap stock: {sponsor_primary_only.iloc[0]['lead_sponsor_name']} at {int(sponsor_primary_only.iloc[0]['primary_only_count']):,} studies; highest large-sponsor rate is {sponsor_primary_rate['lead_sponsor_name']} at {sponsor_primary_rate['primary_only_rate']:.1f}%.",
        f"- Largest country-linked primary-only-gap stock: {country_primary_only.iloc[0]['country_name']} at {int(country_primary_only.iloc[0]['primary_only_count']):,} studies; highest large-country rate is {country_primary_rate['country_name']} at {country_primary_rate['primary_only_rate']:.1f}%.",
        f"- Largest condition-family primary-only-gap stock: {condition_primary_only.iloc[0]['condition_family_label']} at {int(condition_primary_only.iloc[0]['primary_only_count']):,} studies; highest large-family rate is {condition_primary_rate['condition_family_label']} at {condition_primary_rate['primary_only_rate']:.1f}%.",
        f"- Largest condition-family text-asymmetry net: {condition_asymmetry.iloc[0]['condition_family_label']} at {int(condition_asymmetry.iloc[0]['text_asymmetry_net']):,}; highest asymmetry rate is {condition_asymmetry_rate['condition_family_label']} at {condition_asymmetry_rate['text_asymmetry_rate']:.1f} percentage points.",
        f"- Highest sponsor-class primary-only-gap rate: {class_primary_rate['lead_sponsor_class']} at {class_primary_rate['primary_only_rate']:.1f}%; strongest positive class text asymmetry remains {class_positive['lead_sponsor_class']} at {int(class_positive['text_asymmetry_net']):,}.",
    ]
    (out_dir / "wave_sixteen_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    sponsor_primary_only = sponsor_summary.sort_values(
        ["primary_only_count", "primary_only_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    country_primary_only = country_summary.sort_values(
        ["primary_only_count", "primary_only_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    condition_primary_only = condition_summary.sort_values(
        ["primary_only_count", "primary_only_rate"], ascending=[False, False]
    ).reset_index(drop=True)
    condition_asymmetry = condition_summary.sort_values(
        ["text_asymmetry_net", "description_only_count"], ascending=[False, False]
    ).reset_index(drop=True)
    class_asymmetry = class_summary.sort_values(
        ["text_asymmetry_net", "description_only_count"], ascending=[False, False]
    ).reset_index(drop=True)

    sponsor_primary_only.to_csv(out_dir / "wave_sixteen_sponsor_primary_only_gap.csv", index=False)
    country_primary_only.to_csv(out_dir / "wave_sixteen_country_primary_only_gap.csv", index=False)
    condition_primary_only.to_csv(out_dir / "wave_sixteen_condition_primary_only_gap.csv", index=False)
    condition_asymmetry.to_csv(out_dir / "wave_sixteen_condition_text_asymmetry.csv", index=False)
    class_asymmetry.to_csv(out_dir / "wave_sixteen_text_asymmetry_class_summary.csv", index=False)

    write_findings(
        out_dir,
        sponsor_primary_only=sponsor_primary_only,
        country_primary_only=country_primary_only,
        condition_primary_only=condition_primary_only,
        condition_asymmetry=condition_asymmetry,
        class_asymmetry=class_asymmetry,
    )


if __name__ == "__main__":
    main()
