#!/usr/bin/env python3
"""Wave-three CT.gov analyses: policy eras, disease portfolios, and external publication audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
CACHE_DIR = ROOT / "cache" / "wave_three_pubmed"

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
SELECTED_FAMILIES = ["oncology", "cardiovascular", "metabolic"]
FAMILY_LABELS = {
    "oncology": "Oncology",
    "cardiovascular": "Cardiovascular",
    "metabolic": "Metabolic",
}
RULE_ERA_LABELS = [
    "Pre-FDAAA 801 (2000-2007)",
    "FDAAA 801 Era (2008-2016)",
    "Final Rule Era (2017-2020)",
    "Recent Eligible Era (2021-2024)",
]
SAMPLED_CLASSES = ["OTHER", "INDUSTRY", "OTHER_GOV", "NIH", "FED", "NETWORK", "INDIV"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--features",
        default=str(PROCESSED / "study_features.parquet"),
        help="Flattened study features parquet.",
    )
    parser.add_argument(
        "--families",
        default=str(PROCESSED / "study_condition_family.parquet"),
        help="Condition-family parquet.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(PROCESSED),
        help="Output directory for processed summaries.",
    )
    parser.add_argument(
        "--sample-per-class",
        type=int,
        default=150,
        help="Target publication-audit sample size per sponsor class.",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=20260329,
        help="Deterministic random seed for sampling.",
    )
    parser.add_argument(
        "--pubmed-api-key",
        default=os.getenv("NCBI_API_KEY") or os.getenv("ENTREZ_API_KEY") or "",
        help="Optional NCBI API key.",
    )
    return parser.parse_args()


class CachedPubMedClient:
    def __init__(self, cache_dir: Path, api_key: str = "") -> None:
        self.cache_dir = cache_dir
        self.api_key = api_key.strip()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self._last_request_ts = 0.0
        self._min_interval_seconds = 0.11 if self.api_key else 0.34

    def _wait_for_slot(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_request_ts
        if elapsed < self._min_interval_seconds:
            time.sleep(self._min_interval_seconds - elapsed)
        self._last_request_ts = time.monotonic()

    def _cache_path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def search_by_nct(self, nct_id: str, retmax: int = 20) -> list[str]:
        query = f"{nct_id}[si] OR {nct_id}[tiab] OR {nct_id}[tw]"
        cache_path = self._cache_path(f"pubmed:{query}:{retmax}")
        if cache_path.exists():
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            self._wait_for_slot()
            params: dict[str, Any] = {
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": str(retmax),
            }
            if self.api_key:
                params["api_key"] = self.api_key
            response = self.session.get(f"{PUBMED_BASE}/esearch.fcgi", params=params, timeout=30)
            response.raise_for_status()
            payload = response.json()
            cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        idlist = payload.get("esearchresult", {}).get("idlist", []) if isinstance(payload, dict) else []
        return [str(value) for value in idlist]


def load_older(features_path: Path, family_path: Path) -> pd.DataFrame:
    features = pd.read_parquet(
        features_path,
        columns=[
            "nct_id",
            "brief_title",
            "lead_sponsor_name",
            "lead_sponsor_class",
            "phase_label",
            "primary_completion_date",
            "study_first_submit_date",
            "publication_link_missing",
            "results_gap_2y",
            "hiddenness_score",
            "is_interventional",
            "is_closed",
            "days_since_primary_completion",
        ],
    )
    families = pd.read_parquet(family_path)[["nct_id", "condition_family", "condition_family_label"]]
    df = features.merge(families, on="nct_id", how="left")
    df["condition_family"] = df["condition_family"].fillna("other")
    df["condition_family_label"] = df["condition_family_label"].fillna("Other")
    older = df[
        df["is_interventional"] & df["is_closed"] & df["days_since_primary_completion"].fillna(-1).ge(730)
    ].copy()
    older["ghost_protocol"] = older["results_gap_2y"] & older["publication_link_missing"]
    older["results_publication_visible"] = (~older["results_gap_2y"]) & (~older["publication_link_missing"])
    older["completion_year"] = pd.to_datetime(older["primary_completion_date"], errors="coerce").dt.year
    older["rule_era"] = pd.cut(
        older["completion_year"],
        bins=[1999, 2007, 2016, 2020, 2024],
        labels=RULE_ERA_LABELS,
    )
    return older


def summarize_rule_eras(older: pd.DataFrame, out_dir: Path) -> None:
    summary = (
        older.groupby("rule_era", observed=False)
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
            no_publication_rate=("publication_link_missing", "mean"),
            results_publication_visible_rate=("results_publication_visible", "mean"),
            hiddenness_score_mean=("hiddenness_score", "mean"),
        )
        .reset_index()
    )
    rate_columns = [name for name in summary.columns if name.endswith("_rate")]
    summary[rate_columns] = summary[rate_columns].mul(100).round(3)
    summary["hiddenness_score_mean"] = summary["hiddenness_score_mean"].round(3)
    summary.to_csv(out_dir / "rule_era_visibility_older_2y.csv", index=False)


def summarize_selected_families(older: pd.DataFrame, out_dir: Path) -> None:
    selected = older[older["condition_family"].isin(SELECTED_FAMILIES)].copy()

    family_summary = (
        selected.groupby(["condition_family", "condition_family_label"])
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
            no_publication_rate=("publication_link_missing", "mean"),
            results_publication_visible_rate=("results_publication_visible", "mean"),
            hiddenness_score_mean=("hiddenness_score", "mean"),
        )
        .reset_index()
    )
    rate_columns = [name for name in family_summary.columns if name.endswith("_rate")]
    family_summary[rate_columns] = family_summary[rate_columns].mul(100).round(3)
    family_summary["hiddenness_score_mean"] = family_summary["hiddenness_score_mean"].round(3)
    family_summary.to_csv(out_dir / "selected_condition_family_summary_older_2y.csv", index=False)

    sponsor_class = (
        selected.groupby(["condition_family", "lead_sponsor_class"])
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
            results_publication_visible_rate=("results_publication_visible", "mean"),
        )
        .reset_index()
        .sort_values(["condition_family", "studies", "ghost_protocol_rate"], ascending=[True, False, False])
    )
    rate_columns = [name for name in sponsor_class.columns if name.endswith("_rate")]
    sponsor_class[rate_columns] = sponsor_class[rate_columns].mul(100).round(3)
    sponsor_class.to_csv(out_dir / "selected_condition_family_sponsor_class_older_2y.csv", index=False)

    phase = (
        selected.groupby(["condition_family", "phase_label"])
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
        )
        .reset_index()
        .sort_values(["condition_family", "studies", "ghost_protocol_rate"], ascending=[True, False, False])
    )
    rate_columns = [name for name in phase.columns if name.endswith("_rate")]
    phase[rate_columns] = phase[rate_columns].mul(100).round(3)
    phase.to_csv(out_dir / "selected_condition_family_phase_older_2y.csv", index=False)

    sponsor = (
        selected.groupby(["condition_family", "lead_sponsor_name", "lead_sponsor_class"])
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
        )
        .reset_index()
    )
    sponsor = sponsor[sponsor["studies"] >= 25].copy()
    rate_columns = [name for name in sponsor.columns if name.endswith("_rate")]
    sponsor[rate_columns] = sponsor[rate_columns].mul(100).round(3)
    sponsor = sponsor.sort_values(
        ["condition_family", "no_results_count", "ghost_protocol_count", "studies"],
        ascending=[True, False, False, False],
    )
    sponsor.to_csv(out_dir / "selected_condition_family_lead_sponsor_older_2y.csv", index=False)


def run_publication_audit(
    older: pd.DataFrame,
    out_dir: Path,
    cache_dir: Path,
    sample_per_class: int,
    random_seed: int,
    pubmed_api_key: str,
) -> None:
    eligible = older[older["publication_link_missing"] & older["lead_sponsor_class"].isin(SAMPLED_CLASSES)].copy()
    samples: list[pd.DataFrame] = []
    for idx, sponsor_class in enumerate(SAMPLED_CLASSES):
        subset = eligible[eligible["lead_sponsor_class"] == sponsor_class].copy()
        take = min(sample_per_class, len(subset))
        if take == 0:
            continue
        samples.append(subset.sample(n=take, random_state=random_seed + idx))
    sample = pd.concat(samples, ignore_index=True)
    sample = sample.sort_values(["lead_sponsor_class", "nct_id"]).reset_index(drop=True)

    client = CachedPubMedClient(cache_dir=cache_dir, api_key=pubmed_api_key)
    pmid_counts: list[int] = []
    pmid_values: list[str] = []
    for nct_id in sample["nct_id"]:
        pmids = client.search_by_nct(str(nct_id))
        pmid_counts.append(len(pmids))
        pmid_values.append(" | ".join(pmids))
    sample["pubmed_pmid_count"] = pmid_counts
    sample["pubmed_match_found"] = sample["pubmed_pmid_count"].gt(0)
    sample["pubmed_pmids"] = pmid_values
    sample["external_publication_only"] = sample["pubmed_match_found"] & sample["results_gap_2y"]
    sample["condition_family_label"] = sample["condition_family_label"].fillna("Other")
    sample.to_csv(out_dir / "pubmed_publication_audit_sample.csv", index=False)

    population = (
        eligible.groupby("lead_sponsor_class")
        .agg(population_no_link_studies=("nct_id", "size"))
        .reset_index()
    )
    summary = (
        sample.groupby("lead_sponsor_class")
        .agg(
            sample_studies=("nct_id", "size"),
            sample_pubmed_match_count=("pubmed_match_found", "sum"),
            sample_pubmed_match_rate=("pubmed_match_found", "mean"),
            sample_external_publication_only_count=("external_publication_only", "sum"),
            sample_external_publication_only_rate=("external_publication_only", "mean"),
            sample_ghost_protocol_count=("results_gap_2y", "sum"),
        )
        .reset_index()
        .merge(population, on="lead_sponsor_class", how="left")
        .sort_values("population_no_link_studies", ascending=False)
    )
    summary["population_weight"] = summary["population_no_link_studies"] / summary["population_no_link_studies"].sum()
    summary["weighted_pubmed_match_contribution"] = summary["population_weight"] * summary["sample_pubmed_match_rate"]
    summary["weighted_external_publication_only_contribution"] = (
        summary["population_weight"] * summary["sample_external_publication_only_rate"]
    )
    rate_columns = [name for name in summary.columns if name.endswith("_rate") or "weight" in name or "contribution" in name]
    summary[rate_columns] = summary[rate_columns].mul(100).round(3)

    overall = pd.DataFrame(
        [
            {
                "lead_sponsor_class": "ALL_WEIGHTED",
                "sample_studies": int(sample["nct_id"].size),
                "sample_pubmed_match_count": int(sample["pubmed_match_found"].sum()),
                "sample_pubmed_match_rate": round(float(sample["pubmed_match_found"].mean() * 100), 3),
                "sample_external_publication_only_count": int(sample["external_publication_only"].sum()),
                "sample_external_publication_only_rate": round(float(sample["external_publication_only"].mean() * 100), 3),
                "sample_ghost_protocol_count": int(sample["results_gap_2y"].sum()),
                "population_no_link_studies": int(eligible["nct_id"].size),
                "population_weight": 100.0,
                "weighted_pubmed_match_contribution": round(float(summary["weighted_pubmed_match_contribution"].sum()), 3),
                "weighted_external_publication_only_contribution": round(
                    float(summary["weighted_external_publication_only_contribution"].sum()),
                    3,
                ),
            }
        ]
    )
    combined = pd.concat([summary, overall], ignore_index=True)
    combined.to_csv(out_dir / "pubmed_publication_audit_summary.csv", index=False)


def write_findings(out_dir: Path) -> None:
    rule_era = pd.read_csv(out_dir / "rule_era_visibility_older_2y.csv")
    family = pd.read_csv(out_dir / "selected_condition_family_summary_older_2y.csv")
    pubmed = pd.read_csv(out_dir / "pubmed_publication_audit_summary.csv")

    recent = rule_era.iloc[-1]
    early = rule_era.iloc[1]
    oncology = family[family["condition_family"] == "oncology"].iloc[0]
    cardio = family[family["condition_family"] == "cardiovascular"].iloc[0]
    metabolic = family[family["condition_family"] == "metabolic"].iloc[0]
    weighted = pubmed[pubmed["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]
    industry = pubmed[pubmed["lead_sponsor_class"] == "INDUSTRY"].iloc[0]

    lines = [
        "# Wave Three Findings",
        "",
        "## Rule Eras",
        "",
        f"- FDAAA 801 era (2008-2016) no-results rate: {early['no_results_rate']:.1f}%.",
        f"- Recent eligible era (2021-2024) no-results rate: {recent['no_results_rate']:.1f}%.",
        f"- Recent eligible era ghost-protocol rate: {recent['ghost_protocol_rate']:.1f}%.",
        "",
        "## Disease Portfolios",
        "",
        f"- Oncology eligible older stock: {int(oncology['studies']):,} studies with {oncology['ghost_protocol_rate']:.1f}% ghost protocols.",
        f"- Cardiovascular no-results rate: {cardio['no_results_rate']:.1f}%.",
        f"- Metabolic no-results rate: {metabolic['no_results_rate']:.1f}%.",
        "",
        "## External Publication Audit",
        "",
        f"- Weighted PubMed NCT-match rate among sponsor-class-stratified no-link older studies: {weighted['weighted_pubmed_match_contribution']:.1f}%.",
        f"- Weighted external-publication-only rate among the same sample: {weighted['weighted_external_publication_only_contribution']:.1f}%.",
        f"- Industry sample PubMed NCT-match rate: {industry['sample_pubmed_match_rate']:.1f}%.",
        "",
    ]
    (out_dir / "wave_three_findings.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    older = load_older(Path(args.features), Path(args.families))
    summarize_rule_eras(older, out_dir)
    summarize_selected_families(older, out_dir)
    run_publication_audit(
        older=older,
        out_dir=out_dir,
        cache_dir=CACHE_DIR,
        sample_per_class=args.sample_per_class,
        random_seed=args.random_seed,
        pubmed_api_key=args.pubmed_api_key,
    )
    write_findings(out_dir)
    print(f"Wave-three outputs written to {out_dir}")


if __name__ == "__main__":
    main()
