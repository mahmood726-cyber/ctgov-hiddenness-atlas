#!/usr/bin/env python3
"""Generate second-wave CT.gov hiddenness analyses from the full registry snapshot."""

from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

VISIBILITY_STATES = [
    ("no_results_no_pub", "No results + No publication"),
    ("no_results_pub", "No results + Publication"),
    ("results_no_pub", "Results + No publication"),
    ("results_pub", "Results + Publication"),
]

FAMILY_PATTERNS: list[tuple[str, list[str]]] = [
    (
        "oncology",
        [
            "cancer",
            "carcinoma",
            "tumor",
            "tumour",
            "neoplasm",
            "oncology",
            "leukemia",
            "lymphoma",
            "melanoma",
            "myeloma",
            "sarcoma",
            "glioma",
        ],
    ),
    (
        "cardiovascular",
        [
            "heart",
            "cardiac",
            "coronary",
            "atrial",
            "stroke",
            "vascular",
            "hypertension",
            "myocardial",
            "cardiovascular",
            "aortic",
            "thrombosis",
            "artery",
            "arterial",
            "venous",
            "fibrillation",
            "hfpef",
            "hfrEF".lower(),
        ],
    ),
    (
        "metabolic",
        [
            "diabetes",
            "obesity",
            "overweight",
            "metabolic",
            "cholesterol",
            "lipid",
            "hyperlipidemia",
            "dyslipidemia",
            "insulin",
            "thyroid",
        ],
    ),
    (
        "mental_health",
        [
            "depression",
            "anxiety",
            "schizophrenia",
            "bipolar",
            "autism",
            "adhd",
            "ptsd",
            "stress",
            "mental",
            "opioid",
            "alcohol",
            "substance",
            "addiction",
        ],
    ),
    (
        "neurology",
        [
            "alzheimer",
            "parkinson",
            "epilepsy",
            "migraine",
            "dementia",
            "cognitive",
            "multiple sclerosis",
            "neuropathy",
            "cerebral palsy",
            "spinal cord",
            "seizure",
        ],
    ),
    (
        "infectious",
        [
            "infection",
            "infectious",
            "covid",
            "hiv",
            "influenza",
            "hepatitis",
            "sepsis",
            "pneumonia",
            "tuberculosis",
            "malaria",
            "dengue",
            "virus",
            "viral",
            "bacterial",
            "leishman",
        ],
    ),
    (
        "respiratory_sleep",
        [
            "asthma",
            "copd",
            "pulmonary",
            "respiratory",
            "lung disease",
            "sleep apnea",
            "cystic fibrosis",
            "sleep",
        ],
    ),
    (
        "musculoskeletal_pain",
        [
            "pain",
            "arthritis",
            "osteoarthritis",
            "rheumatoid",
            "back pain",
            "fibromyalgia",
            "bone",
            "fracture",
            "osteoporosis",
            "tendon",
            "musculoskeletal",
        ],
    ),
    (
        "reproductive_maternal",
        [
            "pregnancy",
            "infertility",
            "endometriosis",
            "preeclampsia",
            "maternal",
            "obstetric",
            "menopause",
            "reproductive",
            "uterine",
            "ovarian",
            "cervical",
            "prostate",
        ],
    ),
    (
        "gastro_hepatic",
        [
            "crohn",
            "colitis",
            "bowel",
            "gastro",
            "hepatic",
            "liver",
            "pancrea",
            "colorectal",
            "gastric",
            "ulcerative colitis",
        ],
    ),
    (
        "immunology_derm",
        [
            "psoriasis",
            "eczema",
            "dermatitis",
            "lupus",
            "immune",
            "immunology",
            "inflammation",
            "autoimmune",
            "atopic",
        ],
    ),
    (
        "renal_urology",
        ["kidney", "renal", "neph", "dialysis", "bladder", "urolog", "urinary"],
    ),
    ("healthy_volunteer", ["healthy volunteers", "healthy"]),
]

CONDITION_FAMILY_LABELS = {
    "oncology": "Oncology",
    "cardiovascular": "Cardiovascular",
    "metabolic": "Metabolic",
    "mental_health": "Mental health",
    "neurology": "Neurology",
    "infectious": "Infectious disease",
    "respiratory_sleep": "Respiratory and sleep",
    "musculoskeletal_pain": "Musculoskeletal and pain",
    "reproductive_maternal": "Reproductive and maternal",
    "gastro_hepatic": "Gastrointestinal and hepatic",
    "immunology_derm": "Immunology and dermatology",
    "renal_urology": "Renal and urology",
    "healthy_volunteer": "Healthy volunteers",
    "other": "Other",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--features",
        default=str(PROCESSED / "study_features.parquet"),
        help="Path to flattened study features parquet.",
    )
    parser.add_argument(
        "--raw",
        default=str(RAW_DIR / "ctgov_registry_minimal.jsonl.gz"),
        help="Path to raw registry snapshot JSONL(.gz).",
    )
    parser.add_argument(
        "--out-dir",
        default=str(PROCESSED),
        help="Directory for deep-analysis outputs.",
    )
    return parser.parse_args()


def clean_text(value: str | None) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_condition_label(value: str | None) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip())
    return text


def classify_condition_family(text: str) -> tuple[str, list[str]]:
    scores: dict[str, int] = {}
    matches: dict[str, list[str]] = {}
    for family, keywords in FAMILY_PATTERNS:
        hits = [keyword for keyword in keywords if keyword in text]
        if hits:
            scores[family] = len(hits)
            matches[family] = hits
    if not scores:
        return "other", []
    top_score = max(scores.values())
    for family, _ in FAMILY_PATTERNS:
        if scores.get(family) == top_score:
            return family, matches.get(family, [])
    return "other", []


def state_code(has_results_posted: bool, has_publication: bool) -> str:
    if has_results_posted and has_publication:
        return "results_pub"
    if has_results_posted and not has_publication:
        return "results_no_pub"
    if not has_results_posted and has_publication:
        return "no_results_pub"
    return "no_results_no_pub"


def explode_condition_family_examples(
    raw_path: Path,
    title_map: dict[str, str],
    eligible_older_ids: set[str],
) -> tuple[pd.DataFrame, dict[str, Counter[str]]]:
    valid_ids = set(title_map)
    rows: list[dict[str, str]] = []
    family_examples: dict[str, Counter[str]] = {}
    for family, _ in FAMILY_PATTERNS:
        family_examples[family] = Counter()
    family_examples["other"] = Counter()

    opener = gzip.open if raw_path.suffix == ".gz" else open
    with opener(raw_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            study = json.loads(line)
            protocol = study.get("protocolSection", {})
            ident = protocol.get("identificationModule", {})
            nct_id = ident.get("nctId", "")
            if not nct_id or nct_id not in valid_ids:
                continue
            conditions = [
                clean_condition_label(value)
                for value in (protocol.get("conditionsModule", {}).get("conditions") or [])
                if clean_condition_label(value)
            ]
            text = clean_text(" ".join(conditions + [title_map.get(nct_id, "")]))
            family, matched_keywords = classify_condition_family(text)
            rows.append(
                {
                    "nct_id": nct_id,
                    "condition_family": family,
                    "condition_family_label": CONDITION_FAMILY_LABELS[family],
                    "matched_keywords": " | ".join(matched_keywords),
                    "raw_condition_count": str(len(conditions)),
                }
            )
            if nct_id in eligible_older_ids and conditions:
                family_examples[family].update(conditions)
    return pd.DataFrame(rows), family_examples


def add_state_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["has_publication"] = ~out["publication_link_missing"]
    out["has_results_posted"] = ~out["results_gap_2y"]
    out["ghost_protocol"] = out["results_gap_2y"] & out["publication_link_missing"]
    out["visibility_state"] = [
        state_code(has_results, has_pub)
        for has_results, has_pub in zip(out["has_results_posted"], out["has_publication"], strict=True)
    ]
    return out


def summarize_visibility_states(df: pd.DataFrame, out_dir: Path) -> None:
    state_labels = dict(VISIBILITY_STATES)

    overall = (
        df.groupby("visibility_state")
        .size()
        .rename("studies")
        .reset_index()
        .sort_values("studies", ascending=False)
    )
    overall["rate"] = overall["studies"] / len(df) * 100
    overall["visibility_state_label"] = overall["visibility_state"].map(state_labels)
    overall.to_csv(out_dir / "visibility_state_summary_older_2y.csv", index=False)

    def summarize_group(group_col: str, out_name: str) -> None:
        grouped = (
            df.groupby(group_col)
            .agg(
                studies=("nct_id", "size"),
                no_results_count=("results_gap_2y", "sum"),
                no_results_rate=("results_gap_2y", "mean"),
                no_publication_count=("publication_link_missing", "sum"),
                no_publication_rate=("publication_link_missing", "mean"),
                ghost_protocol_count=("ghost_protocol", "sum"),
                ghost_protocol_rate=("ghost_protocol", "mean"),
                hiddenness_score_mean=("hiddenness_score", "mean"),
            )
            .reset_index()
        )
        for state_code_value, _ in VISIBILITY_STATES:
            counts = (
                df.assign(_flag=df["visibility_state"].eq(state_code_value))
                .groupby(group_col)
                .agg(
                    **{
                        f"{state_code_value}_count": ("_flag", "sum"),
                        f"{state_code_value}_rate": ("_flag", "mean"),
                    }
                )
                .reset_index()
            )
            grouped = grouped.merge(counts, on=group_col, how="left")
        grouped["hiddenness_score_mean"] = grouped["hiddenness_score_mean"].round(3)
        rate_columns = [col for col in grouped.columns if col.endswith("_rate")]
        grouped[rate_columns] = grouped[rate_columns].mul(100).round(3)
        grouped = grouped.sort_values(["studies", "ghost_protocol_rate"], ascending=[False, False])
        grouped.to_csv(out_dir / out_name, index=False)

    summarize_group("lead_sponsor_class", "sponsor_class_visibility_older_2y.csv")
    summarize_group("phase_label", "phase_visibility_older_2y.csv")


def summarize_cohorts(df: pd.DataFrame, out_dir: Path) -> None:
    frame = df.copy()
    frame["primary_completion_year"] = pd.to_datetime(frame["primary_completion_date"], errors="coerce").dt.year
    frame["study_first_submit_year"] = pd.to_datetime(frame["study_first_submit_date"], errors="coerce").dt.year

    by_completion_year = (
        frame.groupby("primary_completion_year")
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            no_publication_rate=("publication_link_missing", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
            results_publication_visible_rate=("visibility_state", lambda s: float((s == "results_pub").mean())),
        )
        .reset_index()
        .sort_values("primary_completion_year")
    )
    by_completion_year[
        [
            "no_results_rate",
            "no_publication_rate",
            "ghost_protocol_rate",
            "results_publication_visible_rate",
        ]
    ] = by_completion_year[
        [
            "no_results_rate",
            "no_publication_rate",
            "ghost_protocol_rate",
            "results_publication_visible_rate",
        ]
    ].mul(100).round(3)
    by_completion_year.to_csv(out_dir / "completion_year_visibility_older_2y.csv", index=False)

    by_submit_year = (
        frame.groupby("study_first_submit_year")
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
        )
        .reset_index()
        .sort_values("study_first_submit_year")
    )
    by_submit_year[["no_results_rate", "ghost_protocol_rate"]] = by_submit_year[
        ["no_results_rate", "ghost_protocol_rate"]
    ].mul(100).round(3)
    by_submit_year.to_csv(out_dir / "submit_year_visibility_older_2y.csv", index=False)

    frame["completion_era"] = pd.cut(
        frame["primary_completion_year"],
        bins=[1999, 2007, 2012, 2017, 2020, 2024],
        labels=["2000-2007", "2008-2012", "2013-2017", "2018-2020", "2021-2024"],
    )
    by_era = (
        frame.groupby("completion_era", observed=False)
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            no_publication_rate=("publication_link_missing", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
            results_publication_visible_rate=("visibility_state", lambda s: float((s == "results_pub").mean())),
        )
        .reset_index()
    )
    by_era[
        [
            "no_results_rate",
            "no_publication_rate",
            "ghost_protocol_rate",
            "results_publication_visible_rate",
        ]
    ] = by_era[
        [
            "no_results_rate",
            "no_publication_rate",
            "ghost_protocol_rate",
            "results_publication_visible_rate",
        ]
    ].mul(100).round(3)
    by_era.to_csv(out_dir / "completion_era_visibility_older_2y.csv", index=False)


def summarize_sponsor_concentration(df: pd.DataFrame, out_dir: Path) -> None:
    sponsor = (
        df.groupby(["lead_sponsor_name", "lead_sponsor_class"])
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
            no_publication_rate=("publication_link_missing", "mean"),
            hiddenness_score_mean=("hiddenness_score", "mean"),
        )
        .reset_index()
        .sort_values(["no_results_count", "ghost_protocol_count", "studies"], ascending=[False, False, False])
        .reset_index(drop=True)
    )
    sponsor["rank_by_no_results_count"] = np.arange(1, len(sponsor) + 1)
    sponsor["cumulative_no_results_count"] = sponsor["no_results_count"].cumsum()
    sponsor["cumulative_no_results_share"] = sponsor["cumulative_no_results_count"] / sponsor["no_results_count"].sum() * 100
    sponsor["cumulative_ghost_protocol_count"] = sponsor["ghost_protocol_count"].cumsum()
    sponsor["cumulative_ghost_protocol_share"] = (
        sponsor["cumulative_ghost_protocol_count"] / sponsor["ghost_protocol_count"].sum() * 100
    )
    rate_columns = [col for col in sponsor.columns if col.endswith("_rate") or col.endswith("_share")]
    sponsor[rate_columns] = sponsor[rate_columns].round(3)
    sponsor["hiddenness_score_mean"] = sponsor["hiddenness_score_mean"].round(3)
    sponsor.to_csv(out_dir / "lead_sponsor_concentration_older_2y.csv", index=False)

    shares = sponsor["no_results_count"] / sponsor["no_results_count"].sum()
    values = np.sort(sponsor["no_results_count"].to_numpy(dtype=float))
    n = len(values)
    gini = float((2 * np.arange(1, n + 1) - n - 1).dot(values) / (n * values.sum()))
    hhi = float((shares.pow(2).sum()) * 10000)

    metrics = {
        "eligible_older_studies": int(len(df)),
        "eligible_older_no_results_count": int(df["results_gap_2y"].sum()),
        "eligible_older_ghost_protocol_count": int(df["ghost_protocol"].sum()),
        "sponsor_count": int(len(sponsor)),
        "top_1pct_share_no_results": float(
            sponsor.head(max(1, int(np.ceil(len(sponsor) * 0.01))))["no_results_count"].sum()
            / sponsor["no_results_count"].sum()
            * 100
        ),
        "top_5pct_share_no_results": float(
            sponsor.head(max(1, int(np.ceil(len(sponsor) * 0.05))))["no_results_count"].sum()
            / sponsor["no_results_count"].sum()
            * 100
        ),
        "top_10pct_share_no_results": float(
            sponsor.head(max(1, int(np.ceil(len(sponsor) * 0.10))))["no_results_count"].sum()
            / sponsor["no_results_count"].sum()
            * 100
        ),
        "top_20_share_no_results": float(sponsor.head(20)["no_results_count"].sum() / sponsor["no_results_count"].sum() * 100),
        "top_100_share_no_results": float(
            sponsor.head(100)["no_results_count"].sum() / sponsor["no_results_count"].sum() * 100
        ),
        "top_500_share_no_results": float(
            sponsor.head(500)["no_results_count"].sum() / sponsor["no_results_count"].sum() * 100
        ),
        "no_results_gini": round(gini, 6),
        "no_results_hhi": round(hhi, 6),
    }
    pd.DataFrame([metrics]).to_csv(out_dir / "sponsor_concentration_metrics.csv", index=False)


def summarize_condition_families(
    df: pd.DataFrame,
    family_examples: dict[str, Counter[str]],
    out_dir: Path,
) -> None:
    family = (
        df.groupby(["condition_family", "condition_family_label"])
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            no_publication_rate=("publication_link_missing", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
            results_publication_visible_rate=("visibility_state", lambda s: float((s == "results_pub").mean())),
            hiddenness_score_mean=("hiddenness_score", "mean"),
        )
        .reset_index()
        .sort_values(["studies", "ghost_protocol_rate"], ascending=[False, False])
    )
    family["top_conditions"] = family["condition_family"].map(
        lambda key: " | ".join(name for name, _ in family_examples.get(key, Counter()).most_common(5))
    )
    rate_columns = [col for col in family.columns if col.endswith("_rate")]
    family[rate_columns] = family[rate_columns].mul(100).round(3)
    family["hiddenness_score_mean"] = family["hiddenness_score_mean"].round(3)
    family.to_csv(out_dir / "condition_family_older_2y.csv", index=False)


def write_findings(
    visibility: pd.DataFrame,
    sponsor_class: pd.DataFrame,
    completion_era: pd.DataFrame,
    sponsor_metrics: pd.DataFrame,
    family: pd.DataFrame,
    out_path: Path,
) -> None:
    state_lookup = visibility.set_index("visibility_state")
    named_classes = sponsor_class[sponsor_class["lead_sponsor_class"].isin(["INDUSTRY", "OTHER", "OTHER_GOV", "NIH", "FED", "NETWORK", "INDIV"])].copy()
    worst_ghost = named_classes.sort_values(["ghost_protocol_rate", "studies"], ascending=[False, False]).iloc[0]
    best_both = named_classes.sort_values(["results_pub_rate", "studies"], ascending=[False, False]).iloc[0]
    latest_era = completion_era.iloc[-1]
    family_named = family[family["condition_family"] != "other"].copy()
    largest_family = family_named.sort_values("studies", ascending=False).iloc[0]
    highest_family_rate = family_named[family_named["studies"] >= 3000].sort_values(
        ["ghost_protocol_rate", "studies"], ascending=[False, False]
    ).iloc[0]
    concentration = sponsor_metrics.iloc[0]

    lines = [
        "# Deep Hiddenness Findings",
        "",
        "## Evidence Visibility States",
        "",
        f"- Eligible older closed interventional studies with neither posted results nor a linked publication: {int(state_lookup.loc['no_results_no_pub', 'studies']):,} ({state_lookup.loc['no_results_no_pub', 'rate']:.1f}%).",
        f"- Eligible older closed interventional studies with both posted results and a linked publication: {int(state_lookup.loc['results_pub', 'studies']):,} ({state_lookup.loc['results_pub', 'rate']:.1f}%).",
        f"- Publication-only visibility remains common: {int(state_lookup.loc['no_results_pub', 'studies']):,} ({state_lookup.loc['no_results_pub', 'rate']:.1f}%).",
        "",
        "## Sponsor-Class Contrast",
        "",
        f"- Worst ghost-protocol rate among named sponsor classes: {worst_ghost['lead_sponsor_class']} ({worst_ghost['ghost_protocol_rate']:.1f}%).",
        f"- Highest fully visible rate among named sponsor classes: {best_both['lead_sponsor_class']} ({best_both['results_pub_rate']:.1f}%).",
        "",
        "## Completion Cohorts",
        "",
        f"- Most recent eligible completion-era bucket ({latest_era['completion_era']}) no-results rate: {latest_era['no_results_rate']:.1f}%.",
        f"- Most recent eligible completion-era bucket ({latest_era['completion_era']}) ghost-protocol rate: {latest_era['ghost_protocol_rate']:.1f}%.",
        "",
        "## Therapeutic Areas",
        "",
        f"- Largest named condition family among eligible older studies: {largest_family['condition_family_label']} ({int(largest_family['studies']):,} studies).",
        f"- Highest ghost-protocol rate among common named condition families: {highest_family_rate['condition_family_label']} ({highest_family_rate['ghost_protocol_rate']:.1f}%).",
        "",
        "## Concentration",
        "",
        f"- Top 1 percent of lead sponsors account for {concentration['top_1pct_share_no_results']:.1f}% of the 2-year missing-results backlog.",
        f"- Top 10 percent of lead sponsors account for {concentration['top_10pct_share_no_results']:.1f}% of the 2-year missing-results backlog.",
        f"- Gini coefficient for sponsor-level missing-results stock: {concentration['no_results_gini']:.3f}.",
        "",
        "## Caveats",
        "",
        "- Visibility states use ClinicalTrials.gov linked publication references rather than external publication matching.",
        "- Condition families are keyword-based and assign each study to one dominant family, which can compress multi-topic records.",
        "- These summaries measure registry-visible absence, not adjudicated legal non-compliance.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    features = pd.read_parquet(
        Path(args.features),
        columns=[
            "nct_id",
            "brief_title",
            "official_title",
            "lead_sponsor_name",
            "lead_sponsor_class",
            "study_type",
            "phase_label",
            "primary_completion_date",
            "study_first_submit_date",
            "is_interventional",
            "is_closed",
            "days_since_primary_completion",
            "results_gap_2y",
            "publication_link_missing",
            "hiddenness_score",
        ],
    )

    eligible_older = features[
        features["is_interventional"]
        & features["is_closed"]
        & features["days_since_primary_completion"].fillna(-1).ge(730)
    ].copy()
    eligible_older_ids = set(eligible_older["nct_id"])
    title_map = {
        row["nct_id"]: " ".join(
            part for part in [str(row["brief_title"] or ""), str(row["official_title"] or "")] if part.strip()
        )
        for _, row in features[["nct_id", "brief_title", "official_title"]].iterrows()
    }

    family_df, family_examples = explode_condition_family_examples(Path(args.raw), title_map, eligible_older_ids)
    family_df.to_parquet(out_dir / "study_condition_family.parquet", index=False)

    deep = features.merge(family_df[["nct_id", "condition_family", "condition_family_label"]], on="nct_id", how="left")
    deep["condition_family"] = deep["condition_family"].fillna("other")
    deep["condition_family_label"] = deep["condition_family_label"].fillna(CONDITION_FAMILY_LABELS["other"])

    older = add_state_columns(
        deep[
            deep["is_interventional"]
            & deep["is_closed"]
            & deep["days_since_primary_completion"].fillna(-1).ge(730)
        ].copy()
    )

    summarize_visibility_states(older, out_dir)
    summarize_cohorts(older, out_dir)
    summarize_sponsor_concentration(older, out_dir)
    summarize_condition_families(older, family_examples, out_dir)

    visibility = pd.read_csv(out_dir / "visibility_state_summary_older_2y.csv")
    sponsor_class = pd.read_csv(out_dir / "sponsor_class_visibility_older_2y.csv")
    completion_era = pd.read_csv(out_dir / "completion_era_visibility_older_2y.csv")
    sponsor_metrics = pd.read_csv(out_dir / "sponsor_concentration_metrics.csv")
    family = pd.read_csv(out_dir / "condition_family_older_2y.csv")
    write_findings(
        visibility=visibility,
        sponsor_class=sponsor_class,
        completion_era=completion_era,
        sponsor_metrics=sponsor_metrics,
        family=family,
        out_path=out_dir / "deep_hiddenness_findings.md",
    )

    print(f"Deep-analysis outputs written to {out_dir}")


if __name__ == "__main__":
    main()
