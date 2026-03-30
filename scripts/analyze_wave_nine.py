#!/usr/bin/env python3
"""Wave-nine CT.gov analyses: sponsor, country, condition, black-box, and strict-core watchlists."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from analyze_wave_eight import add_context_columns, fit_adjusted_probabilities

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

FEATURE_COLS = [
    "phase_bucket",
    "primary_purpose_bucket",
    "allocation_bucket",
    "status_bucket",
    "stopped_bucket",
    "enrollment_bucket",
    "arm_bucket",
    "intervention_bucket",
    "named_country_bucket",
    "location_bucket",
    "primary_outcome_bucket",
    "secondary_outcome_bucket",
    "age_bucket",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default=str(PROCESSED / "study_features.parquet"))
    parser.add_argument("--context", default=str(PROCESSED / "wave_five_study_context.parquet"))
    parser.add_argument("--conditions", default=str(PROCESSED / "study_condition_family.parquet"))
    parser.add_argument("--out-dir", default=str(PROCESSED))
    parser.add_argument("--min-sponsor-studies", type=int, default=100)
    parser.add_argument("--min-country-studies", type=int, default=500)
    parser.add_argument("--min-strict-sponsor-studies", type=int, default=50)
    parser.add_argument("--random-seed", type=int, default=20260330)
    return parser.parse_args()


def load_older_wide(features_path: Path, context_path: Path, conditions_path: Path) -> pd.DataFrame:
    features = pd.read_parquet(
        features_path,
        columns=[
            "nct_id",
            "lead_sponsor_name",
            "lead_sponsor_class",
            "phase_label",
            "primary_purpose",
            "allocation",
            "overall_status",
            "is_stopped",
            "primary_outcome_count",
            "secondary_outcome_count",
            "arm_group_count",
            "intervention_count",
            "country_count",
            "location_count",
            "enrollment_count",
            "days_since_primary_completion",
            "results_gap_2y",
            "publication_link_missing",
            "has_results",
            "results_reporting_lag_days",
            "primary_completion_date",
            "study_first_submit_date",
            "is_interventional",
            "is_closed",
            "detailed_description_missing",
            "primary_outcome_description_missing",
        ],
    )
    context = pd.read_parquet(context_path)
    conditions = pd.read_parquet(conditions_path)[["nct_id", "condition_family_label"]]

    older = features[
        features["is_interventional"]
        & features["is_closed"]
        & features["days_since_primary_completion"].fillna(-1).ge(730)
    ].copy()
    older = older.merge(context, on="nct_id", how="left")
    older["country_names_text"] = older["country_names_text"].fillna("")
    older["intervention_types_text"] = older["intervention_types_text"].fillna("")
    older["named_country_count"] = pd.to_numeric(older["named_country_count"], errors="coerce").fillna(0)
    older = add_context_columns(older)
    older = older.merge(conditions, on="nct_id", how="left")
    older["condition_family_label"] = older["condition_family_label"].fillna("Other")

    older["black_box"] = (
        older["results_gap_2y"]
        & older["publication_link_missing"]
        & older["detailed_description_missing"]
    )
    older["strict_proxy"] = older["us_presence"].astype(str).eq("Any US") & (
        (older["has_drug_bio"] & ~older["phase_is_phase1_only"]) | older["has_device"]
    )
    older["strict_proxy_no_results"] = older["strict_proxy"] & older["results_gap_2y"]
    older["strict_proxy_black_box"] = older["strict_proxy"] & older["black_box"]
    older["strict_proxy_int"] = older["strict_proxy"].astype(int)
    older["overdue_2y_years_unresolved_only"] = older["overdue_2y_years"].where(~older["has_results"])
    return older


def add_adjusted_expectations(older: pd.DataFrame, random_seed: int) -> pd.DataFrame:
    metrics: list[dict[str, float]] = []
    for target in ["results_gap_2y", "ghost_protocol"]:
        older[f"expected_{target}"], summary = fit_adjusted_probabilities(older, target, FEATURE_COLS, random_seed)
        metrics.append(summary)
    return pd.DataFrame(metrics).round(6)


def summarize_watchlist(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    grouped = (
        df.groupby(group_cols, observed=False)
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            expected_no_results_count=("expected_results_gap_2y", "sum"),
            expected_no_results_rate=("expected_results_gap_2y", "mean"),
            ghost_count=("ghost_protocol", "sum"),
            ghost_rate=("ghost_protocol", "mean"),
            expected_ghost_count=("expected_ghost_protocol", "sum"),
            expected_ghost_rate=("expected_ghost_protocol", "mean"),
            black_box_count=("black_box", "sum"),
            black_box_rate=("black_box", "mean"),
            visible_count=("results_publication_visible", "sum"),
            visible_rate=("results_publication_visible", "mean"),
            mean_overdue_2y_years_unresolved=("overdue_2y_years_unresolved_only", "mean"),
            strict_proxy_studies=("strict_proxy_int", "sum"),
            strict_proxy_no_results_count=("strict_proxy_no_results", "sum"),
            strict_proxy_black_box_count=("strict_proxy_black_box", "sum"),
        )
        .reset_index()
    )
    grouped["excess_no_results"] = grouped["no_results_count"] - grouped["expected_no_results_count"]
    grouped["excess_no_results_rate_points"] = (
        grouped["no_results_rate"] - grouped["expected_no_results_rate"]
    ) * 100
    grouped["excess_ghost"] = grouped["ghost_count"] - grouped["expected_ghost_count"]
    grouped["excess_ghost_rate_points"] = (grouped["ghost_rate"] - grouped["expected_ghost_rate"]) * 100
    grouped["strict_proxy_no_results_rate"] = np.where(
        grouped["strict_proxy_studies"] > 0,
        grouped["strict_proxy_no_results_count"] / grouped["strict_proxy_studies"] * 100,
        np.nan,
    )
    grouped["strict_proxy_black_box_rate"] = np.where(
        grouped["strict_proxy_studies"] > 0,
        grouped["strict_proxy_black_box_count"] / grouped["strict_proxy_studies"] * 100,
        np.nan,
    )

    percent_cols = [
        "no_results_rate",
        "expected_no_results_rate",
        "ghost_rate",
        "expected_ghost_rate",
        "black_box_rate",
        "visible_rate",
    ]
    grouped[percent_cols] = grouped[percent_cols].mul(100)

    round_cols = [
        "no_results_rate",
        "expected_no_results_rate",
        "ghost_rate",
        "expected_ghost_rate",
        "black_box_rate",
        "visible_rate",
        "expected_no_results_count",
        "expected_ghost_count",
        "excess_no_results",
        "excess_no_results_rate_points",
        "excess_ghost",
        "excess_ghost_rate_points",
        "mean_overdue_2y_years_unresolved",
        "strict_proxy_no_results_rate",
        "strict_proxy_black_box_rate",
    ]
    grouped[round_cols] = grouped[round_cols].round(3)
    return grouped


def make_country_long(older: pd.DataFrame) -> pd.DataFrame:
    country_long = older.copy()
    country_long["country_name"] = (
        country_long["country_names_text"]
        .fillna("")
        .astype(str)
        .str.split("|")
        .map(lambda items: [item.strip() for item in items if item.strip()])
    )
    country_long = country_long[country_long["country_name"].map(bool)].explode("country_name").reset_index(drop=True)
    return country_long


def write_findings(
    out_dir: Path,
    sponsor_watchlist: pd.DataFrame,
    country_watchlist: pd.DataFrame,
    condition_watchlist: pd.DataFrame,
    black_box_class: pd.DataFrame,
    strict_sponsor: pd.DataFrame,
) -> None:
    sponsor_top = sponsor_watchlist.sort_values("excess_no_results", ascending=False).iloc[0]
    country_top = country_watchlist.sort_values("excess_no_results", ascending=False).iloc[0]
    condition_top = condition_watchlist.sort_values("excess_no_results", ascending=False).iloc[0]
    condition_ghost = condition_watchlist.sort_values("excess_ghost", ascending=False).iloc[0]
    black_box_stock = black_box_class.sort_values("black_box_count", ascending=False).iloc[0]
    black_box_rate = black_box_class[black_box_class["studies"] >= 1000].sort_values("black_box_rate", ascending=False).iloc[0]
    strict_top = strict_sponsor.sort_values("no_results_count", ascending=False).iloc[0]

    lines = [
        "# Wave Nine Findings",
        "",
        f"- Largest sponsor adjusted excess no-results stock: {sponsor_top['lead_sponsor_name']} ({sponsor_top['lead_sponsor_class']}) at {sponsor_top['excess_no_results']:.0f} studies.",
        f"- Largest country-linked adjusted excess no-results stock: {country_top['country_name']} at {country_top['excess_no_results']:.0f} studies.",
        f"- Largest condition-family adjusted excess no-results stock: {condition_top['condition_family_label']} at {condition_top['excess_no_results']:.0f} studies.",
        f"- Largest condition-family adjusted ghost excess: {condition_ghost['condition_family_label']} at {condition_ghost['excess_ghost']:.0f} studies.",
        f"- Largest black-box stock by sponsor class: {black_box_stock['lead_sponsor_class']} with {int(black_box_stock['black_box_count']):,} studies.",
        f"- Highest large-class black-box rate: {black_box_rate['lead_sponsor_class']} at {black_box_rate['black_box_rate']:.1f}%.",
        f"- Largest strict-proxy sponsor no-results stock: {strict_top['lead_sponsor_name']} with {int(strict_top['no_results_count']):,} studies at a {strict_top['no_results_rate']:.1f}% rate.",
    ]
    (out_dir / "wave_nine_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    older = load_older_wide(Path(args.features), Path(args.context), Path(args.conditions))
    metrics = add_adjusted_expectations(older, args.random_seed)

    sponsor_watchlist = summarize_watchlist(older, ["lead_sponsor_name", "lead_sponsor_class"])
    sponsor_watchlist = sponsor_watchlist[sponsor_watchlist["studies"] >= args.min_sponsor_studies].copy()
    sponsor_watchlist = sponsor_watchlist.sort_values(["excess_no_results", "studies"], ascending=[False, False]).reset_index(drop=True)

    country_long = make_country_long(older)
    country_watchlist = summarize_watchlist(country_long, ["country_name"])
    country_watchlist = country_watchlist[country_watchlist["studies"] >= args.min_country_studies].copy()
    country_watchlist = country_watchlist.sort_values(["excess_no_results", "studies"], ascending=[False, False]).reset_index(drop=True)

    condition_watchlist = summarize_watchlist(older, ["condition_family_label"])
    condition_watchlist = condition_watchlist.sort_values(["excess_no_results", "studies"], ascending=[False, False]).reset_index(drop=True)

    black_box_class = summarize_watchlist(older, ["lead_sponsor_class"]).sort_values(
        ["black_box_count", "studies"], ascending=[False, False]
    )
    black_box_country = summarize_watchlist(country_long, ["country_name"])
    black_box_country = black_box_country[black_box_country["studies"] >= args.min_country_studies].copy()
    black_box_country = black_box_country.sort_values(["black_box_count", "studies"], ascending=[False, False]).reset_index(drop=True)
    black_box_condition = summarize_watchlist(older, ["condition_family_label"]).sort_values(
        ["black_box_count", "studies"], ascending=[False, False]
    )

    strict_only = older[older["strict_proxy"]].copy()
    strict_sponsor = summarize_watchlist(strict_only, ["lead_sponsor_name", "lead_sponsor_class"])
    strict_sponsor = strict_sponsor[strict_sponsor["studies"] >= args.min_strict_sponsor_studies].copy()
    strict_sponsor = strict_sponsor.sort_values(["no_results_count", "studies"], ascending=[False, False]).reset_index(drop=True)
    strict_condition = summarize_watchlist(strict_only, ["condition_family_label"]).sort_values(
        ["no_results_count", "studies"], ascending=[False, False]
    )
    strict_sponsor_class = summarize_watchlist(strict_only, ["lead_sponsor_class"]).sort_values(
        ["no_results_count", "studies"], ascending=[False, False]
    )

    metrics.to_csv(out_dir / "wave_nine_model_metrics.csv", index=False)
    sponsor_watchlist.to_csv(out_dir / "wave_nine_sponsor_watchlist.csv", index=False)
    country_watchlist.to_csv(out_dir / "wave_nine_country_watchlist.csv", index=False)
    condition_watchlist.to_csv(out_dir / "wave_nine_condition_watchlist.csv", index=False)
    black_box_class.to_csv(out_dir / "wave_nine_black_box_sponsor_class.csv", index=False)
    black_box_country.to_csv(out_dir / "wave_nine_black_box_country.csv", index=False)
    black_box_condition.to_csv(out_dir / "wave_nine_black_box_condition.csv", index=False)
    strict_sponsor.to_csv(out_dir / "wave_nine_strict_sponsor_watchlist.csv", index=False)
    strict_condition.to_csv(out_dir / "wave_nine_strict_condition_summary.csv", index=False)
    strict_sponsor_class.to_csv(out_dir / "wave_nine_strict_sponsor_class_summary.csv", index=False)

    write_findings(out_dir, sponsor_watchlist, country_watchlist, condition_watchlist, black_box_class, strict_sponsor)


if __name__ == "__main__":
    main()
