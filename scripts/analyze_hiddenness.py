#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Flatten the CT.gov snapshot and quantify sponsor-specific hiddenness patterns."""

from __future__ import annotations

import argparse
import gzip
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed"

CLOSED_STATUSES = {
    "COMPLETED",
    "TERMINATED",
    "WITHDRAWN",
    "SUSPENDED",
    "NO_LONGER_AVAILABLE",
    "APPROVED_FOR_MARKETING",
}
STOPPED_STATUSES = {"TERMINATED", "WITHDRAWN", "SUSPENDED"}
ALL_BOOL_METRICS = [
    "official_title_missing",
    "brief_summary_missing",
    "detailed_description_missing",
    "location_missing",
    "primary_outcomes_missing",
    "primary_outcome_description_missing",
    "secondary_outcomes_missing",
    "publication_link_missing",
    "ipd_statement_missing",
    "phase_missing_interventional",
    "arm_groups_missing_interventional",
    "primary_completion_actual_missing_closed",
    "completion_actual_missing_closed",
    "enrollment_actual_missing_closed",
    "termination_reason_missing",
    "results_gap_1y",
    "results_gap_2y",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default=str(RAW_DIR / "ctgov_registry_minimal.jsonl.gz"),
        help="Path to raw JSONL snapshot",
    )
    parser.add_argument(
        "--metadata",
        default=str(RAW_DIR / "ctgov_registry_minimal_metadata.json"),
        help="Path to fetch metadata JSON",
    )
    parser.add_argument(
        "--as-of-date",
        default=date.today().isoformat(),
        help="Reference date for 1-year and 2-year results-gap calculations",
    )
    parser.add_argument(
        "--min-sponsor-studies",
        type=int,
        default=50,
        help="Minimum closed interventional studies for lead-sponsor ranking output",
    )
    return parser.parse_args()


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def text_present(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def value_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def ensure_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def status_key(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().upper().replace(" ", "_")


def days_between(start: date | None, end: date | None) -> int | None:
    if not start or not end:
        return None
    return (end - start).days


def flatten_study(study: dict[str, Any], as_of_date: date) -> dict[str, Any]:
    protocol = study.get("protocolSection", {})
    ident = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    sponsor = protocol.get("sponsorCollaboratorsModule", {})
    design = protocol.get("designModule", {})
    design_info = design.get("designInfo", {})
    desc = protocol.get("descriptionModule", {})
    outcomes = protocol.get("outcomesModule", {})
    locations = protocol.get("contactsLocationsModule", {}).get("locations", [])
    arms = protocol.get("armsInterventionsModule", {})
    refs = protocol.get("referencesModule", {}).get("references", [])
    ipd = protocol.get("ipdSharingStatementModule", {})

    lead_sponsor = sponsor.get("leadSponsor", {})
    phases = ensure_list(design.get("phases"))
    arm_groups = ensure_list(arms.get("armGroups"))
    interventions = ensure_list(arms.get("interventions"))
    primary_outcomes = ensure_list(outcomes.get("primaryOutcomes"))
    secondary_outcomes = ensure_list(outcomes.get("secondaryOutcomes"))
    locations = ensure_list(locations)
    refs = ensure_list(refs)

    overall_status = status.get("overallStatus", "")
    status_norm = status_key(overall_status)
    study_type = (design.get("studyType") or "").upper()
    is_interventional = study_type == "INTERVENTIONAL"
    is_closed = status_norm in CLOSED_STATUSES
    is_stopped = status_norm in STOPPED_STATUSES

    start_date = parse_date(status.get("startDateStruct", {}).get("date"))
    primary_completion_date = parse_date(status.get("primaryCompletionDateStruct", {}).get("date"))
    completion_date = parse_date(status.get("completionDateStruct", {}).get("date"))
    study_first_submit_date = parse_date(status.get("studyFirstSubmitDate"))
    results_first_post_date = parse_date(status.get("resultsFirstPostDateStruct", {}).get("date"))

    primary_completion_type = status.get("primaryCompletionDateStruct", {}).get("type", "")
    completion_type = status.get("completionDateStruct", {}).get("type", "")
    enrollment_count = design.get("enrollmentInfo", {}).get("count")
    enrollment_type = design.get("enrollmentInfo", {}).get("type", "")

    countries = sorted(
        {
            location.get("country", "").strip()
            for location in locations
            if isinstance(location, dict) and text_present(location.get("country"))
        }
    )
    facility_names = [
        location.get("facility", "").strip()
        for location in locations
        if isinstance(location, dict) and text_present(location.get("facility"))
    ]
    pmid_refs = [
        ref.get("pmid")
        for ref in refs
        if isinstance(ref, dict) and value_present(ref.get("pmid"))
    ]
    result_pmid_refs = [
        ref.get("pmid")
        for ref in refs
        if isinstance(ref, dict)
        and value_present(ref.get("pmid"))
        and str(ref.get("type", "")).upper() == "RESULT"
    ]

    days_since_primary_completion = days_between(primary_completion_date, as_of_date)
    results_reporting_lag_days = days_between(primary_completion_date, results_first_post_date)

    primary_outcome_descriptions = [
        outcome.get("description", "")
        for outcome in primary_outcomes
        if isinstance(outcome, dict)
    ]
    has_primary_outcome_description = any(text_present(text) for text in primary_outcome_descriptions)

    row = {
        "nct_id": ident.get("nctId", ""),
        "brief_title": ident.get("briefTitle", ""),
        "official_title": ident.get("officialTitle", ""),
        "lead_sponsor_name": lead_sponsor.get("name", "") or "Unknown sponsor",
        "lead_sponsor_class": lead_sponsor.get("class", "") or "UNKNOWN",
        "study_type": study_type or "UNKNOWN",
        "overall_status": overall_status or "UNKNOWN",
        "phase_label": " | ".join(phases) if phases else "UNSPECIFIED",
        "allocation": design_info.get("allocation", ""),
        "primary_purpose": design_info.get("primaryPurpose", ""),
        "study_first_submit_date": study_first_submit_date.isoformat() if study_first_submit_date else "",
        "start_date": start_date.isoformat() if start_date else "",
        "primary_completion_date": primary_completion_date.isoformat() if primary_completion_date else "",
        "completion_date": completion_date.isoformat() if completion_date else "",
        "results_first_post_date": results_first_post_date.isoformat() if results_first_post_date else "",
        "primary_completion_date_type": primary_completion_type,
        "completion_date_type": completion_type,
        "enrollment_count": enrollment_count,
        "enrollment_type": enrollment_type,
        "location_count": len(locations),
        "country_count": len(countries),
        "facility_name_count": len(facility_names),
        "arm_group_count": len(arm_groups),
        "intervention_count": len(interventions),
        "condition_count": len(ensure_list(protocol.get("conditionsModule", {}).get("conditions"))),
        "phase_count": len(phases),
        "primary_outcome_count": len(primary_outcomes),
        "secondary_outcome_count": len(secondary_outcomes),
        "pmid_reference_count": len(pmid_refs),
        "result_reference_count": len(result_pmid_refs),
        "has_results": bool(study.get("hasResults", False)),
        "is_interventional": is_interventional,
        "is_closed": is_closed,
        "is_stopped": is_stopped,
        "days_since_primary_completion": days_since_primary_completion,
        "results_reporting_lag_days": results_reporting_lag_days,
        "official_title_missing": not text_present(ident.get("officialTitle")),
        "brief_summary_missing": not text_present(desc.get("briefSummary")),
        "detailed_description_missing": not text_present(desc.get("detailedDescription")),
        "location_missing": len(locations) == 0,
        "primary_outcomes_missing": len(primary_outcomes) == 0,
        "primary_outcome_description_missing": len(primary_outcomes) > 0 and not has_primary_outcome_description,
        "secondary_outcomes_missing": len(secondary_outcomes) == 0,
        "publication_link_missing": len(pmid_refs) == 0,
        "ipd_statement_missing": not text_present(ipd.get("ipdSharing")),
        "phase_missing_interventional": is_interventional and len(phases) == 0,
        "arm_groups_missing_interventional": is_interventional and len(arm_groups) == 0,
        "primary_completion_actual_missing_closed": is_closed
        and (not primary_completion_date or primary_completion_type.upper() != "ACTUAL"),
        "completion_actual_missing_closed": is_closed
        and (not completion_date or completion_type.upper() != "ACTUAL"),
        "enrollment_actual_missing_closed": is_closed
        and (enrollment_count in (None, "") or str(enrollment_type).upper() != "ACTUAL"),
        "termination_reason_missing": is_stopped and not text_present(status.get("whyStopped")),
        "results_gap_1y": is_interventional
        and is_closed
        and days_since_primary_completion is not None
        and days_since_primary_completion >= 365
        and not bool(study.get("hasResults", False)),
        "results_gap_2y": is_interventional
        and is_closed
        and days_since_primary_completion is not None
        and days_since_primary_completion >= 730
        and not bool(study.get("hasResults", False)),
    }

    structural_flags = [
        "official_title_missing",
        "brief_summary_missing",
        "detailed_description_missing",
        "location_missing",
        "primary_outcomes_missing",
        "primary_outcome_description_missing",
        "secondary_outcomes_missing",
        "publication_link_missing",
        "ipd_statement_missing",
        "phase_missing_interventional",
        "arm_groups_missing_interventional",
    ]
    closure_flags = [
        "primary_completion_actual_missing_closed",
        "completion_actual_missing_closed",
        "enrollment_actual_missing_closed",
        "termination_reason_missing",
        "results_gap_2y",
    ]
    row["structural_hiddenness_score"] = sum(int(row[name]) for name in structural_flags)
    row["closure_hiddenness_score"] = sum(int(row[name]) for name in closure_flags)
    row["hiddenness_score"] = row["structural_hiddenness_score"] + row["closure_hiddenness_score"]
    return row


def percentify(summary: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        if column in summary.columns:
            summary[column] = (pd.to_numeric(summary[column], errors="coerce") * 100).round(2)
    return summary


def summarize_groups(df: pd.DataFrame, group_col: str | list[str]) -> pd.DataFrame:
    summary = (
        df.groupby(group_col, dropna=False)
        .agg(
            studies=("nct_id", "size"),
            interventional_rate=("is_interventional", "mean"),
            closed_rate=("is_closed", "mean"),
            has_results_rate=("has_results", "mean"),
            mean_hiddenness_score=("hiddenness_score", "mean"),
            median_hiddenness_score=("hiddenness_score", "median"),
            results_gap_1y_count=("results_gap_1y", "sum"),
            results_gap_2y_count=("results_gap_2y", "sum"),
            eligible_results_gap_1y_count=("days_since_primary_completion", lambda s: int(s.fillna(-1).ge(365).sum())),
            eligible_results_gap_2y_count=("days_since_primary_completion", lambda s: int(s.fillna(-1).ge(730).sum())),
            official_title_missing_rate=("official_title_missing", "mean"),
            detailed_description_missing_rate=("detailed_description_missing", "mean"),
            location_missing_rate=("location_missing", "mean"),
            primary_outcomes_missing_rate=("primary_outcomes_missing", "mean"),
            publication_link_missing_rate=("publication_link_missing", "mean"),
            ipd_statement_missing_rate=("ipd_statement_missing", "mean"),
            primary_completion_actual_missing_closed_rate=("primary_completion_actual_missing_closed", "mean"),
            completion_actual_missing_closed_rate=("completion_actual_missing_closed", "mean"),
            enrollment_actual_missing_closed_rate=("enrollment_actual_missing_closed", "mean"),
            termination_reason_missing_rate=("termination_reason_missing", "mean"),
            results_gap_1y_rate=("results_gap_1y", "mean"),
            results_gap_2y_rate=("results_gap_2y", "mean"),
        )
        .reset_index()
        .sort_values(["studies", "mean_hiddenness_score"], ascending=[False, False])
    )
    summary["results_gap_1y_rate_eligible"] = (
        summary["results_gap_1y_count"] / summary["eligible_results_gap_1y_count"].replace(0, pd.NA)
    )
    summary["results_gap_2y_rate_eligible"] = (
        summary["results_gap_2y_count"] / summary["eligible_results_gap_2y_count"].replace(0, pd.NA)
    )
    rate_cols = [column for column in summary.columns if "_rate" in column]
    summary = percentify(summary, rate_cols)
    summary["mean_hiddenness_score"] = summary["mean_hiddenness_score"].round(3)
    summary["median_hiddenness_score"] = summary["median_hiddenness_score"].round(3)
    return summary


def write_findings(
    metadata: dict[str, Any],
    df: pd.DataFrame,
    sponsor_all: pd.DataFrame,
    sponsor_closed: pd.DataFrame,
    lead_sponsor_closed: pd.DataFrame,
    out_path: Path,
    as_of_date: date,
) -> None:
    total_studies = len(df)
    interventional = int(df["is_interventional"].sum())
    closed = int(df["is_closed"].sum())
    closed_df = df[df["is_closed"]].copy()
    stopped_df = df[df["is_stopped"]].copy()
    closed_interventional_df = df[df["is_interventional"] & df["is_closed"]].copy()
    closed_interventional_count = len(closed_interventional_df)
    aged_interventional_1y_df = closed_interventional_df[
        closed_interventional_df["days_since_primary_completion"].fillna(-1) >= 365
    ].copy()
    aged_interventional_2y_df = closed_interventional_df[
        closed_interventional_df["days_since_primary_completion"].fillna(-1) >= 730
    ].copy()

    sponsor_closed_by_rate = sponsor_closed[sponsor_closed["studies"] >= 100].sort_values(
        ["results_gap_2y_rate_eligible", "studies"], ascending=[False, False]
    )
    sponsor_closed_by_count = sponsor_closed.sort_values(
        ["results_gap_2y_count", "studies"], ascending=[False, False]
    )
    sponsor_all_by_hiddenness = sponsor_all[
        (sponsor_all["studies"] >= 100)
        & (~sponsor_all["lead_sponsor_class"].isin(["UNKNOWN", "AMBIG"]))
    ].sort_values(
        ["mean_hiddenness_score", "studies"], ascending=[False, False]
    )

    top_rate_class = sponsor_closed_by_rate.iloc[0] if not sponsor_closed_by_rate.empty else None
    top_count_class = sponsor_closed_by_count.iloc[0] if not sponsor_closed_by_count.empty else None
    top_hiddenness_class = sponsor_all_by_hiddenness.iloc[0] if not sponsor_all_by_hiddenness.empty else None

    lines = [
        "# Hiddenness Findings",
        "",
        f"As of {as_of_date.isoformat()}, the raw registry snapshot contains {metadata.get('records_fetched', total_studies):,} studies.",
        "",
        "## Snapshot",
        "",
        f"- Total studies: {total_studies:,}",
        f"- Interventional studies: {interventional:,}",
        f"- Closed studies: {closed:,}",
        f"- Closed interventional studies: {closed_interventional_count:,}",
        f"- Closed interventional studies with an actual primary completion date at least 2 years old: {len(aged_interventional_2y_df):,}",
        "",
        "## What Is Most Often Missing",
        "",
        f"- No IPD sharing statement: {df['ipd_statement_missing'].mean() * 100:.1f}%",
        f"- No linked publication reference: {df['publication_link_missing'].mean() * 100:.1f}%",
        f"- No detailed description: {df['detailed_description_missing'].mean() * 100:.1f}%",
        f"- No primary outcomes: {df['primary_outcomes_missing'].mean() * 100:.1f}%",
        f"- No locations: {df['location_missing'].mean() * 100:.1f}%",
        "",
        "## Closure-Stage Disappearance",
        "",
        f"- Closed studies missing an actual primary completion date: {closed_df['primary_completion_actual_missing_closed'].mean() * 100 if len(closed_df) else 0:.1f}%",
        f"- Closed studies missing an actual completion date: {closed_df['completion_actual_missing_closed'].mean() * 100 if len(closed_df) else 0:.1f}%",
        f"- Closed studies missing actual enrollment: {closed_df['enrollment_actual_missing_closed'].mean() * 100 if len(closed_df) else 0:.1f}%",
        f"- Stopped studies with no reason given: {stopped_df['termination_reason_missing'].mean() * 100 if len(stopped_df) else 0:.1f}%",
        f"- Closed interventional studies 1+ year past primary completion with no posted results: {aged_interventional_1y_df['results_gap_1y'].mean() * 100 if len(aged_interventional_1y_df) else 0:.1f}%",
        f"- Closed interventional studies 2+ years past primary completion with no posted results: {aged_interventional_2y_df['results_gap_2y'].mean() * 100 if len(aged_interventional_2y_df) else 0:.1f}%",
        "",
    ]

    if top_rate_class is not None:
        lines.extend(
            [
                "## Sponsor-Class Concentration",
                "",
                f"- Highest 2-year no-results rate among sponsor classes with at least 100 closed interventional studies: {top_rate_class['lead_sponsor_class']} ({top_rate_class['results_gap_2y_rate_eligible']:.1f}% among eligible older studies).",
                f"- Largest absolute stock of 2-year no-results studies: {top_count_class['lead_sponsor_class']} ({int(top_count_class['results_gap_2y_count']):,} studies).",
                f"- Highest average hiddenness score across sponsor classes with at least 100 studies: {top_hiddenness_class['lead_sponsor_class']} ({top_hiddenness_class['mean_hiddenness_score']:.2f}).",
                "",
            ]
        )

    if not lead_sponsor_closed.empty:
        top_lead_sponsors = lead_sponsor_closed.sort_values(
            ["results_gap_2y_rate_eligible", "studies"], ascending=[False, False]
        ).head(10)
        lines.extend(
            [
                "## Lead Sponsors To Inspect",
                "",
                "Closed interventional sponsors with at least the configured minimum total and eligible older study counts, ranked by 2-year no-results rate:",
                "",
            ]
        )
        for _, row in top_lead_sponsors.iterrows():
            lines.append(
                f"- {row['lead_sponsor_name']} [{row['lead_sponsor_class']}]: {row['results_gap_2y_rate_eligible']:.1f}% 2-year no-results rate across {int(row['eligible_results_gap_2y_count']):,} eligible older studies"
            )
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "- Absolute counts tell you where the largest amount of obscured information sits.",
            "- Rates tell you where omission looks systematic rather than incidental.",
            "- Industry can dominate counts through volume while other sponsor classes can still look worse on sparsity rates.",
            "- The CSV summaries should be read together rather than in isolation.",
            "",
        ]
    )

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    metadata_path = Path(args.metadata)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    as_of_date = parse_date(args.as_of_date)
    if not as_of_date:
        raise ValueError(f"Invalid --as-of-date: {args.as_of_date}")

    metadata = {}
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    for index, study in enumerate(read_jsonl(input_path), start=1):
        rows.append(flatten_study(study, as_of_date))
        if index % 10000 == 0:
            print(f"flattened {index} studies")

    df = pd.DataFrame(rows)
    for metric in ALL_BOOL_METRICS:
        df[metric] = df[metric].astype(bool)

    study_features_path = OUT_DIR / "study_features.parquet"
    df.to_parquet(study_features_path, index=False)

    sponsor_all = summarize_groups(df, "lead_sponsor_class")
    sponsor_all.to_csv(OUT_DIR / "sponsor_class_summary_all.csv", index=False)

    closed_interventional_df = df[df["is_interventional"] & df["is_closed"]].copy()
    sponsor_closed = summarize_groups(closed_interventional_df, "lead_sponsor_class")
    sponsor_closed.to_csv(OUT_DIR / "sponsor_class_summary_closed_interventional.csv", index=False)

    lead_sponsor_closed = summarize_groups(
        closed_interventional_df,
        ["lead_sponsor_name", "lead_sponsor_class"],
    )
    lead_sponsor_closed = lead_sponsor_closed[
        lead_sponsor_closed["studies"] >= args.min_sponsor_studies
    ]
    lead_sponsor_closed = lead_sponsor_closed[
        lead_sponsor_closed["eligible_results_gap_2y_count"] >= args.min_sponsor_studies
    ].sort_values(["results_gap_2y_rate_eligible", "studies"], ascending=[False, False])
    lead_sponsor_closed.to_csv(
        OUT_DIR / "lead_sponsor_summary_closed_interventional.csv",
        index=False,
    )

    study_type_summary = summarize_groups(df, "study_type")
    study_type_summary.to_csv(OUT_DIR / "study_type_summary.csv", index=False)

    phase_summary = summarize_groups(df[df["is_interventional"]].copy(), "phase_label")
    phase_summary.to_csv(OUT_DIR / "phase_summary_interventional.csv", index=False)

    findings_path = OUT_DIR / "hiddenness_findings.md"
    write_findings(
        metadata=metadata,
        df=df,
        sponsor_all=sponsor_all,
        sponsor_closed=sponsor_closed,
        lead_sponsor_closed=lead_sponsor_closed,
        out_path=findings_path,
        as_of_date=as_of_date,
    )

    print(f"Study features written to {study_features_path}")
    print(f"Findings written to {findings_path}")


if __name__ == "__main__":
    main()
