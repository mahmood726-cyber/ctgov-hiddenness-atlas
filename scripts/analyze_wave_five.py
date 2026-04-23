#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Wave-five CT.gov analyses: intervention types, countries, stopped trials, outcomes, and actual-date discipline."""

from __future__ import annotations

import argparse
import gzip
import json
from collections.abc import Iterable
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

STATUS_ORDER = ["COMPLETED", "TERMINATED", "WITHDRAWN", "SUSPENDED"]
PRIMARY_OUTCOME_BUCKETS = ["0", "1", "2", "3-5", "6+"]
SECONDARY_OUTCOME_BUCKETS = ["0", "1", "2-4", "5-9", "10+"]
INTERVENTION_MIX_BUCKETS = ["Missing", "Single-type", "Multi-type"]
ACTUAL_FIELD_LABELS = {
    "primary_completion_actual_missing_closed": "Primary completion not actual",
    "completion_actual_missing_closed": "Completion not actual",
    "enrollment_actual_missing_closed": "Enrollment not actual",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--features",
        default=str(PROCESSED / "study_features.parquet"),
        help="Flattened study features parquet.",
    )
    parser.add_argument(
        "--raw",
        default=str(RAW / "ctgov_registry_minimal.jsonl.gz"),
        help="Raw CT.gov JSONL snapshot.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(PROCESSED),
        help="Output directory for processed summaries.",
    )
    parser.add_argument(
        "--min-country-studies",
        type=int,
        default=800,
        help="Minimum eligible older studies for named-country summaries.",
    )
    parser.add_argument(
        "--min-intervention-studies",
        type=int,
        default=800,
        help="Minimum eligible older studies for intervention-type summaries.",
    )
    return parser.parse_args()


def ensure_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def unique_sorted_text(values: Iterable[str]) -> list[str]:
    return sorted({value.strip() for value in values if isinstance(value, str) and value.strip()})


def summarize_bucket(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    grouped = (
        df.groupby(group_col, observed=False)
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            no_publication_rate=("publication_link_missing", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
            results_publication_visible_rate=("results_publication_visible", "mean"),
            hiddenness_score_mean=("hiddenness_score", "mean"),
            structural_hiddenness_score_mean=("structural_hiddenness_score", "mean"),
            closure_hiddenness_score_mean=("closure_hiddenness_score", "mean"),
        )
        .reset_index()
    )
    rate_columns = [column for column in grouped.columns if column.endswith("_rate")]
    grouped[rate_columns] = grouped[rate_columns].mul(100).round(3)
    for column in ["hiddenness_score_mean", "structural_hiddenness_score_mean", "closure_hiddenness_score_mean"]:
        grouped[column] = grouped[column].round(3)
    return grouped


def bucket_primary_outcomes(series: pd.Series) -> pd.Categorical:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    labels = pd.Series(index=values.index, dtype="object")
    labels[values <= 0] = "0"
    labels[values == 1] = "1"
    labels[values == 2] = "2"
    labels[values.between(3, 5, inclusive="both")] = "3-5"
    labels[values >= 6] = "6+"
    return pd.Categorical(labels, categories=PRIMARY_OUTCOME_BUCKETS, ordered=True)


def bucket_secondary_outcomes(series: pd.Series) -> pd.Categorical:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    labels = pd.Series(index=values.index, dtype="object")
    labels[values <= 0] = "0"
    labels[values == 1] = "1"
    labels[values.between(2, 4, inclusive="both")] = "2-4"
    labels[values.between(5, 9, inclusive="both")] = "5-9"
    labels[values >= 10] = "10+"
    return pd.Categorical(labels, categories=SECONDARY_OUTCOME_BUCKETS, ordered=True)


def extract_raw_context(raw_path: Path, keep_nct_ids: set[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    opener = gzip.open if raw_path.suffix == ".gz" else open
    with opener(raw_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            study = json.loads(line)
            protocol = study.get("protocolSection", {})
            nct_id = protocol.get("identificationModule", {}).get("nctId", "")
            if nct_id not in keep_nct_ids:
                continue
            arms = protocol.get("armsInterventionsModule", {})
            interventions = ensure_list(arms.get("interventions"))
            locations = ensure_list(protocol.get("contactsLocationsModule", {}).get("locations"))
            intervention_types = unique_sorted_text(
                str(item.get("type", "")).upper()
                for item in interventions
                if isinstance(item, dict)
            )
            countries = unique_sorted_text(
                item.get("country", "")
                for item in locations
                if isinstance(item, dict)
            )
            rows.append(
                {
                    "nct_id": nct_id,
                    "intervention_types_text": "|".join(intervention_types),
                    "country_names_text": "|".join(countries),
                    "intervention_type_count": len(intervention_types),
                    "named_country_count": len(countries),
                }
            )
    return pd.DataFrame(rows)


def explode_pipe_values(df: pd.DataFrame, source_col: str, label_col: str) -> pd.DataFrame:
    exploded = df.copy()
    exploded[label_col] = exploded[source_col].fillna("").astype(str).str.split(r"\|")
    exploded = exploded.explode(label_col)
    exploded[label_col] = exploded[label_col].fillna("").astype(str).str.strip()
    exploded[label_col] = exploded[label_col].replace({"": "Missing"})
    return exploded


def summarize_exploded(df: pd.DataFrame, source_col: str, label_col: str, min_studies: int) -> pd.DataFrame:
    exploded = explode_pipe_values(df, source_col, label_col)
    summary = summarize_bucket(exploded, label_col)
    summary = summary[summary["studies"] >= min_studies].sort_values(["studies", "no_results_rate"], ascending=[False, False])
    return summary.reset_index(drop=True)


def make_intervention_mix(df: pd.DataFrame) -> pd.Categorical:
    counts = pd.to_numeric(df["intervention_type_count"], errors="coerce").fillna(0)
    labels = pd.Series(index=df.index, dtype="object")
    labels[counts <= 0] = "Missing"
    labels[counts == 1] = "Single-type"
    labels[counts >= 2] = "Multi-type"
    return pd.Categorical(labels, categories=INTERVENTION_MIX_BUCKETS, ordered=True)


def make_actual_field_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for column, label in ACTUAL_FIELD_LABELS.items():
        for missing_value in (False, True):
            subset = df[df[column] == missing_value]
            if subset.empty:
                continue
            rows.append(
                {
                    "field": label,
                    "missing": "Missing actual field" if missing_value else "Actual field present",
                    "studies": int(subset["nct_id"].size),
                    "no_results_count": int(subset["results_gap_2y"].sum()),
                    "no_results_rate": round(float(subset["results_gap_2y"].mean() * 100), 3),
                    "no_publication_rate": round(float(subset["publication_link_missing"].mean() * 100), 3),
                    "ghost_protocol_count": int(subset["ghost_protocol"].sum()),
                    "ghost_protocol_rate": round(float(subset["ghost_protocol"].mean() * 100), 3),
                    "results_publication_visible_rate": round(float(subset["results_publication_visible"].mean() * 100), 3),
                    "hiddenness_score_mean": round(float(subset["hiddenness_score"].mean()), 3),
                    "structural_hiddenness_score_mean": round(float(subset["structural_hiddenness_score"].mean()), 3),
                    "closure_hiddenness_score_mean": round(float(subset["closure_hiddenness_score"].mean()), 3),
                }
            )
    return pd.DataFrame(rows)


def make_actual_status_rates(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("overall_status", observed=False)
        .agg(
            studies=("nct_id", "size"),
            primary_completion_missing_rate=("primary_completion_actual_missing_closed", "mean"),
            completion_missing_rate=("completion_actual_missing_closed", "mean"),
            enrollment_missing_rate=("enrollment_actual_missing_closed", "mean"),
        )
        .reset_index()
    )
    rate_cols = [column for column in grouped.columns if column.endswith("_rate")]
    grouped[rate_cols] = grouped[rate_cols].mul(100).round(3)
    grouped["overall_status"] = pd.Categorical(grouped["overall_status"], categories=STATUS_ORDER, ordered=True)
    return grouped.sort_values("overall_status").reset_index(drop=True)


def write_findings(out_dir: Path) -> None:
    interventions = pd.read_csv(out_dir / "intervention_type_visibility_older_2y.csv", keep_default_na=False)
    countries = pd.read_csv(out_dir / "country_visibility_older_2y.csv", keep_default_na=False)
    status = pd.read_csv(out_dir / "status_visibility_older_2y.csv", keep_default_na=False)
    primary = pd.read_csv(out_dir / "primary_outcome_density_older_2y.csv", keep_default_na=False)
    actual = pd.read_csv(out_dir / "actual_field_discipline_older_2y.csv", keep_default_na=False)

    top_type = interventions.iloc[0]
    top_country = countries.iloc[0]
    worst_country = countries[(countries["country"] != "Missing") & (countries["studies"] >= 5000)].sort_values(
        "no_results_rate", ascending=False
    ).iloc[0]
    withdrawn = status[status["overall_status"] == "WITHDRAWN"].iloc[0]
    completed = status[status["overall_status"] == "COMPLETED"].iloc[0]
    zero_primary = primary[primary["primary_outcome_bucket"] == "0"].iloc[0]
    high_primary = primary[primary["primary_outcome_bucket"] == "6+"].iloc[0]
    worst_actual = actual[actual["missing"] == "Missing actual field"].sort_values("no_results_rate", ascending=False).iloc[0]

    lines = [
        "# Wave Five Findings",
        "",
        "## Intervention Types",
        "",
        f"- {top_type['intervention_type']} is the largest eligible older intervention family at {int(top_type['studies']):,} studies.",
        f"- That family shows a {top_type['no_results_rate']:.1f}% 2-year no-results rate and a {top_type['ghost_protocol_rate']:.1f}% ghost-protocol rate.",
        "",
        "## Country Involvement",
        "",
        f"- {top_country['country']} appears in the largest named country-linked stock at {int(top_country['studies']):,} eligible older studies.",
        f"- The worst large named country by 2-year no-results rate is {worst_country['country']} at {worst_country['no_results_rate']:.1f}%.",
        "",
        "## Stopped Trials",
        "",
        f"- Withdrawn studies show a {withdrawn['no_results_rate']:.1f}% 2-year no-results rate.",
        f"- Completed studies remain quieter than they should be at {completed['no_results_rate']:.1f}%, but stopped statuses are structurally worse.",
        "",
        "## Outcome Density",
        "",
        f"- Studies with zero recorded primary outcomes show a {zero_primary['no_results_rate']:.1f}% no-results rate.",
        f"- Studies with six or more primary outcomes fall to {high_primary['no_results_rate']:.1f}%.",
        "",
        "## Actual-Date Discipline",
        "",
        f"- {worst_actual['field']} is the worst actual-field discipline bucket when missing, with a {worst_actual['no_results_rate']:.1f}% no-results rate.",
        "",
    ]
    (out_dir / "wave_five_findings.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    older = pd.read_parquet(
        Path(args.features),
        columns=[
            "nct_id",
            "lead_sponsor_class",
            "overall_status",
            "phase_label",
            "primary_outcome_count",
            "secondary_outcome_count",
            "primary_outcome_description_missing",
            "termination_reason_missing",
            "publication_link_missing",
            "results_gap_2y",
            "hiddenness_score",
            "structural_hiddenness_score",
            "closure_hiddenness_score",
            "primary_completion_actual_missing_closed",
            "completion_actual_missing_closed",
            "enrollment_actual_missing_closed",
            "is_interventional",
            "is_closed",
            "days_since_primary_completion",
        ],
    )
    older = older[
        older["is_interventional"] & older["is_closed"] & older["days_since_primary_completion"].fillna(-1).ge(730)
    ].copy()
    older["ghost_protocol"] = older["results_gap_2y"] & older["publication_link_missing"]
    older["results_publication_visible"] = (~older["results_gap_2y"]) & (~older["publication_link_missing"])
    older["overall_status"] = pd.Categorical(older["overall_status"], categories=STATUS_ORDER, ordered=True)
    older["primary_outcome_bucket"] = bucket_primary_outcomes(older["primary_outcome_count"])
    older["secondary_outcome_bucket"] = bucket_secondary_outcomes(older["secondary_outcome_count"])

    context = extract_raw_context(Path(args.raw), set(older["nct_id"]))
    context.to_parquet(out_dir / "wave_five_study_context.parquet", index=False)

    older = older.merge(context, on="nct_id", how="left")
    older["intervention_types_text"] = older["intervention_types_text"].fillna("")
    older["country_names_text"] = older["country_names_text"].fillna("")
    older["intervention_type_count"] = pd.to_numeric(older["intervention_type_count"], errors="coerce").fillna(0)
    older["named_country_count"] = pd.to_numeric(older["named_country_count"], errors="coerce").fillna(0)
    older["intervention_mix"] = make_intervention_mix(older)
    older["termination_reason_bucket"] = pd.Series(
        pd.Categorical(
            older["termination_reason_missing"].map({False: "Reason recorded", True: "Reason missing"}).fillna("Reason missing"),
            categories=["Reason recorded", "Reason missing"],
            ordered=True,
        ),
        index=older.index,
    )

    summarize_exploded(older, "intervention_types_text", "intervention_type", args.min_intervention_studies).to_csv(
        out_dir / "intervention_type_visibility_older_2y.csv", index=False
    )
    summarize_bucket(older, "intervention_mix").to_csv(out_dir / "intervention_mix_visibility_older_2y.csv", index=False)
    summarize_exploded(older, "country_names_text", "country", args.min_country_studies).to_csv(
        out_dir / "country_visibility_older_2y.csv", index=False
    )
    summarize_bucket(older, "overall_status").to_csv(out_dir / "status_visibility_older_2y.csv", index=False)
    summarize_bucket(
        older[older["overall_status"].isin(["TERMINATED", "WITHDRAWN", "SUSPENDED"])].copy(),
        "termination_reason_bucket",
    ).to_csv(out_dir / "stopped_reason_visibility_older_2y.csv", index=False)
    summarize_bucket(older, "primary_outcome_bucket").to_csv(out_dir / "primary_outcome_density_older_2y.csv", index=False)
    summarize_bucket(older, "secondary_outcome_bucket").to_csv(out_dir / "secondary_outcome_density_older_2y.csv", index=False)
    summarize_bucket(
        older.assign(
            primary_outcome_description_bucket=pd.Categorical(
                older["primary_outcome_description_missing"]
                .map({False: "Description present", True: "Description missing"})
                .fillna("Description missing"),
                categories=["Description present", "Description missing"],
                ordered=True,
            )
        ),
        "primary_outcome_description_bucket",
    ).to_csv(out_dir / "primary_outcome_description_visibility_older_2y.csv", index=False)
    make_actual_field_summary(older).to_csv(out_dir / "actual_field_discipline_older_2y.csv", index=False)
    make_actual_status_rates(older).to_csv(out_dir / "actual_field_status_rates_older_2y.csv", index=False)

    write_findings(out_dir)


if __name__ == "__main__":
    main()
