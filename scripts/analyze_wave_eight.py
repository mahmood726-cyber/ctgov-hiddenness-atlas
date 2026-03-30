#!/usr/bin/env python3
"""Wave-eight CT.gov analyses: risk-adjusted hiddenness, overdue clocks, external publication audit, and ACT-style proxy debt."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
CACHE_DIR = ROOT / "cache" / "wave_eight_epmc"

RULE_ERA_LABELS = [
    "Pre-FDAAA 801 (2000-2007)",
    "FDAAA 801 Era (2008-2016)",
    "Final Rule Era (2017-2020)",
    "Recent Eligible Era (2021-2024)",
]
US_PRESENCE_BUCKETS = ["Any US", "No US", "No named country"]
ACT_PROXY_ORDER = [
    "Broad US nexus",
    "Drug/Bio US non-phase1",
    "Drug/Bio/Device US strict",
]
LAG_BAND_ORDER = ["0-12 months", "13-24 months", "25-36 months", "37-60 months", "61+ months", "Still missing"]
SAMPLED_CLASSES = ["OTHER", "INDUSTRY", "OTHER_GOV", "NIH", "FED", "NETWORK", "INDIV"]
EPMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default=str(PROCESSED / "study_features.parquet"))
    parser.add_argument("--context", default=str(PROCESSED / "wave_five_study_context.parquet"))
    parser.add_argument("--pubmed-sample", default=str(PROCESSED / "pubmed_publication_audit_sample.csv"))
    parser.add_argument("--out-dir", default=str(PROCESSED))
    parser.add_argument("--min-sponsor-studies", type=int, default=100)
    parser.add_argument("--random-seed", type=int, default=20260330)
    return parser.parse_args()


def bucket_enrollment(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    labels = pd.Series("Missing", index=series.index, dtype="object")
    labels[values.between(0, 50, inclusive="both")] = "1-50"
    labels[values.between(51, 100, inclusive="both")] = "51-100"
    labels[values.between(101, 500, inclusive="both")] = "101-500"
    labels[values.between(501, 1000, inclusive="both")] = "501-1000"
    labels[values >= 1001] = "1001+"
    return labels


def bucket_small_count(series: pd.Series, one_label: str = "1") -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    labels = pd.Series("0", index=series.index, dtype="object")
    labels[values == 1] = one_label
    labels[values == 2] = "2"
    labels[values.between(3, 5, inclusive="both")] = "3-5"
    labels[values.between(6, 19, inclusive="both")] = "6-19"
    labels[values >= 20] = "20+"
    return labels


def bucket_primary(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    labels = pd.Series("0", index=series.index, dtype="object")
    labels[values == 1] = "1"
    labels[values == 2] = "2"
    labels[values.between(3, 5, inclusive="both")] = "3-5"
    labels[values >= 6] = "6+"
    return labels


def bucket_secondary(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    labels = pd.Series("0", index=series.index, dtype="object")
    labels[values == 1] = "1"
    labels[values.between(2, 4, inclusive="both")] = "2-4"
    labels[values.between(5, 9, inclusive="both")] = "5-9"
    labels[values >= 10] = "10+"
    return labels


def bucket_age(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    labels = pd.Series("2-3 years", index=series.index, dtype="object")
    labels[values.between(730, 1095, inclusive="both")] = "2-3 years"
    labels[values.between(1096, 1825, inclusive="both")] = "3-5 years"
    labels[values.between(1826, 3650, inclusive="both")] = "5-10 years"
    labels[values >= 3651] = "10+ years"
    return labels


def bucket_string(series: pd.Series, missing: str = "Missing") -> pd.Series:
    text = series.fillna("").astype(str).str.strip()
    return text.mask(text.eq(""), missing)


def make_us_presence(country_text: pd.Series, named_count: pd.Series) -> pd.Categorical:
    text = country_text.fillna("").astype(str)
    named = pd.to_numeric(named_count, errors="coerce").fillna(0)
    has_us = text.str.contains("United States", regex=False)
    labels = pd.Series("No named country", index=text.index, dtype="object")
    labels[named.ge(1) & ~has_us] = "No US"
    labels[has_us] = "Any US"
    return pd.Categorical(labels, categories=US_PRESENCE_BUCKETS, ordered=True)


def make_rule_era(series: pd.Series) -> pd.Categorical:
    years = pd.to_datetime(series, errors="coerce").dt.year
    return pd.cut(years, bins=[1999, 2007, 2016, 2020, 2024], labels=RULE_ERA_LABELS)


def lag_band(has_results: pd.Series, lag_days: pd.Series) -> pd.Categorical:
    results = has_results.fillna(False).astype(bool)
    lag = pd.to_numeric(lag_days, errors="coerce")
    labels = pd.Series("Still missing", index=results.index, dtype="object")
    labels[results & lag.le(365)] = "0-12 months"
    labels[results & lag.between(366, 730, inclusive="both")] = "13-24 months"
    labels[results & lag.between(731, 1095, inclusive="both")] = "25-36 months"
    labels[results & lag.between(1096, 1825, inclusive="both")] = "37-60 months"
    labels[results & lag.ge(1826)] = "61+ months"
    return pd.Categorical(labels, categories=LAG_BAND_ORDER, ordered=True)


def parse_intervention_set(text: str) -> set[str]:
    return {item.strip().upper() for item in str(text or "").split("|") if item.strip()}


def add_context_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["phase_bucket"] = bucket_string(out["phase_label"], "Missing phase")
    out["primary_purpose_bucket"] = bucket_string(out["primary_purpose"], "Missing purpose")
    out["allocation_bucket"] = bucket_string(out["allocation"], "Missing allocation")
    out["status_bucket"] = bucket_string(out["overall_status"], "Missing status")
    out["stopped_bucket"] = np.where(out["is_stopped"].fillna(False), "Stopped", "Not stopped")
    out["enrollment_bucket"] = bucket_enrollment(out["enrollment_count"])
    out["arm_bucket"] = bucket_small_count(out["arm_group_count"])
    out["intervention_bucket"] = bucket_small_count(out["intervention_count"])
    out["named_country_bucket"] = bucket_small_count(out["named_country_count"])
    out["location_bucket"] = bucket_small_count(out["location_count"])
    out["primary_outcome_bucket"] = bucket_primary(out["primary_outcome_count"])
    out["secondary_outcome_bucket"] = bucket_secondary(out["secondary_outcome_count"])
    out["age_bucket"] = bucket_age(out["days_since_primary_completion"])
    out["us_presence"] = make_us_presence(out["country_names_text"], out["named_country_count"])
    out["rule_era"] = make_rule_era(out["primary_completion_date"])
    out["ghost_protocol"] = out["results_gap_2y"] & out["publication_link_missing"]
    out["results_publication_visible"] = (~out["results_gap_2y"]) & (~out["publication_link_missing"])
    out["has_results"] = out["has_results"].fillna(False).astype(bool)
    out["has_publication_link"] = ~out["publication_link_missing"]
    out["overdue_1y_years"] = np.maximum(
        pd.to_numeric(out["days_since_primary_completion"], errors="coerce").fillna(0) - 365,
        0,
    ) / 365.25
    out["overdue_2y_years"] = np.maximum(
        pd.to_numeric(out["days_since_primary_completion"], errors="coerce").fillna(0) - 730,
        0,
    ) / 365.25
    out["lag_band"] = lag_band(out["has_results"], out["results_reporting_lag_days"])
    out["intervention_set"] = out["intervention_types_text"].map(parse_intervention_set)
    out["has_drug_bio"] = out["intervention_set"].map(lambda items: bool(items & {"DRUG", "BIOLOGICAL"}))
    out["has_device"] = out["intervention_set"].map(lambda items: "DEVICE" in items)
    out["phase_is_phase1_only"] = out["phase_label"].fillna("").astype(str).str.strip().eq("PHASE1")
    return out


def load_older(features_path: Path, context_path: Path) -> pd.DataFrame:
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
            "hiddenness_score",
            "structural_hiddenness_score",
            "closure_hiddenness_score",
            "has_results",
            "results_first_post_date",
            "results_reporting_lag_days",
            "primary_completion_date",
            "study_first_submit_date",
            "is_interventional",
            "is_closed",
        ],
    )
    context = pd.read_parquet(context_path)
    older = features[
        features["is_interventional"]
        & features["is_closed"]
        & features["days_since_primary_completion"].fillna(-1).ge(730)
    ].copy()
    older = older.merge(context, on="nct_id", how="left")
    older["country_names_text"] = older["country_names_text"].fillna("")
    older["intervention_types_text"] = older["intervention_types_text"].fillna("")
    older["named_country_count"] = pd.to_numeric(older["named_country_count"], errors="coerce").fillna(0)
    return add_context_columns(older)


def build_model_pipeline(feature_cols: list[str]) -> Pipeline:
    transformer = ColumnTransformer(
        [
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=True),
                feature_cols,
            )
        ]
    )
    return Pipeline(
        [
            ("transform", transformer),
            ("model", LogisticRegression(max_iter=400, solver="saga", random_state=20260330)),
        ]
    )


def fit_adjusted_probabilities(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
    random_seed: int,
) -> tuple[pd.Series, dict[str, float]]:
    X = df[feature_cols].astype(str)
    y = df[target_col].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=random_seed,
        stratify=y,
    )

    holdout_pipe = build_model_pipeline(feature_cols)
    holdout_pipe.fit(X_train, y_train)
    holdout_prob = holdout_pipe.predict_proba(X_test)[:, 1]

    full_pipe = build_model_pipeline(feature_cols)
    full_pipe.fit(X, y)
    full_prob = full_pipe.predict_proba(X)[:, 1]

    metrics = {
        "target": target_col,
        "study_count": float(len(df)),
        "positive_rate": float(y.mean() * 100),
        "holdout_auc": float(roc_auc_score(y_test, holdout_prob)),
        "holdout_brier": float(brier_score_loss(y_test, holdout_prob)),
    }
    return pd.Series(full_prob, index=df.index), metrics


def summarize_adjusted(df: pd.DataFrame, group_cols: list[str], target_col: str, expected_col: str) -> pd.DataFrame:
    grouped = (
        df.groupby(group_cols, observed=False)
        .agg(
            studies=("nct_id", "size"),
            observed_count=(target_col, "sum"),
            observed_rate=(target_col, "mean"),
            expected_count=(expected_col, "sum"),
            expected_rate=(expected_col, "mean"),
        )
        .reset_index()
    )
    grouped["excess_count"] = grouped["observed_count"] - grouped["expected_count"]
    grouped["excess_rate_points"] = (grouped["observed_rate"] - grouped["expected_rate"]) * 100
    grouped["observed_rate"] = grouped["observed_rate"] * 100
    grouped["expected_rate"] = grouped["expected_rate"] * 100
    for column in ["expected_count", "excess_count", "observed_rate", "expected_rate", "excess_rate_points"]:
        grouped[column] = grouped[column].round(3)
    grouped["target"] = target_col
    return grouped.sort_values(["excess_count", "studies"], ascending=[False, False]).reset_index(drop=True)


def run_risk_adjusted(older: pd.DataFrame, out_dir: Path, min_sponsor_studies: int, random_seed: int) -> None:
    feature_cols = [
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
    metrics_rows: list[dict[str, float]] = []
    sponsor_class_frames: list[pd.DataFrame] = []
    us_presence_frames: list[pd.DataFrame] = []
    phase_frames: list[pd.DataFrame] = []
    sponsor_frames: list[pd.DataFrame] = []

    for target in ["results_gap_2y", "ghost_protocol"]:
        expected_col = f"expected_{target}"
        older[expected_col], metrics = fit_adjusted_probabilities(older, target, feature_cols, random_seed)
        metrics_rows.append(metrics)

        sponsor_class_frames.append(summarize_adjusted(older, ["lead_sponsor_class"], target, expected_col))
        us_presence_frames.append(summarize_adjusted(older, ["us_presence"], target, expected_col))
        phase_frames.append(summarize_adjusted(older, ["phase_bucket"], target, expected_col))

        sponsor_summary = summarize_adjusted(older, ["lead_sponsor_name", "lead_sponsor_class"], target, expected_col)
        sponsor_summary = sponsor_summary[sponsor_summary["studies"] >= min_sponsor_studies].copy()
        sponsor_frames.append(sponsor_summary)

    pd.DataFrame(metrics_rows).round(6).to_csv(out_dir / "risk_adjusted_model_metrics.csv", index=False)
    pd.concat(sponsor_class_frames, ignore_index=True).to_csv(
        out_dir / "risk_adjusted_sponsor_class_summary.csv",
        index=False,
    )
    pd.concat(us_presence_frames, ignore_index=True).to_csv(
        out_dir / "risk_adjusted_us_presence_summary.csv",
        index=False,
    )
    pd.concat(phase_frames, ignore_index=True).to_csv(out_dir / "risk_adjusted_phase_summary.csv", index=False)
    pd.concat(sponsor_frames, ignore_index=True).to_csv(out_dir / "risk_adjusted_top_sponsors.csv", index=False)


def summarize_clock(group: pd.DataFrame, label_map: dict[str, object]) -> dict[str, object]:
    reported = group[group["has_results"]].copy()
    unresolved = group[~group["has_results"]].copy()
    row = dict(label_map)
    row["studies"] = int(len(group))
    row["reported_count"] = int(reported["nct_id"].size)
    row["reported_rate"] = round(float(group["has_results"].mean() * 100), 3)
    row["within_12m_rate"] = round(float(((group["has_results"]) & (group["results_reporting_lag_days"].fillna(10**9) <= 365)).mean() * 100), 3)
    row["within_24m_rate"] = round(float(((group["has_results"]) & (group["results_reporting_lag_days"].fillna(10**9) <= 730)).mean() * 100), 3)
    row["within_36m_rate"] = round(float(((group["has_results"]) & (group["results_reporting_lag_days"].fillna(10**9) <= 1095)).mean() * 100), 3)
    row["within_60m_rate"] = round(float(((group["has_results"]) & (group["results_reporting_lag_days"].fillna(10**9) <= 1825)).mean() * 100), 3)
    row["unresolved_count"] = int(unresolved["nct_id"].size)
    row["unresolved_rate"] = round(float((~group["has_results"]).mean() * 100), 3)
    row["median_lag_days_reported"] = round(float(reported["results_reporting_lag_days"].median()), 3) if not reported.empty else np.nan
    row["p90_lag_days_reported"] = round(float(reported["results_reporting_lag_days"].quantile(0.9)), 3) if not reported.empty else np.nan
    row["median_overdue_2y_years_unresolved"] = round(float(unresolved["overdue_2y_years"].median()), 3) if not unresolved.empty else np.nan
    row["mean_overdue_2y_years_unresolved"] = round(float(unresolved["overdue_2y_years"].mean()), 3) if not unresolved.empty else np.nan
    return row


def run_overdue_clock(older: pd.DataFrame, out_dir: Path) -> None:
    lag_summary = (
        older.groupby("lag_band", observed=False)
        .agg(studies=("nct_id", "size"))
        .reset_index()
    )
    lag_summary["rate"] = (lag_summary["studies"] / len(older) * 100).round(3)
    lag_summary.to_csv(out_dir / "overdue_lag_band_summary.csv", index=False)

    sponsor_rows = [summarize_clock(group, {"lead_sponsor_class": label}) for label, group in older.groupby("lead_sponsor_class", observed=False)]
    phase_rows = [summarize_clock(group, {"phase_bucket": label}) for label, group in older.groupby("phase_bucket", observed=False)]
    era_rows = [summarize_clock(group, {"rule_era": label}) for label, group in older.groupby("rule_era", observed=False)]

    pd.DataFrame(sponsor_rows).sort_values("unresolved_count", ascending=False).to_csv(
        out_dir / "overdue_sponsor_class_clock.csv",
        index=False,
    )
    pd.DataFrame(phase_rows).sort_values("unresolved_count", ascending=False).to_csv(
        out_dir / "overdue_phase_clock.csv",
        index=False,
    )
    pd.DataFrame(era_rows).to_csv(out_dir / "overdue_completion_era_clock.csv", index=False)


class CachedEuropePMCClient:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self._last_request_ts = 0.0
        self._min_interval_seconds = 0.12

    def _cache_path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def _wait_for_slot(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_request_ts
        if elapsed < self._min_interval_seconds:
            time.sleep(self._min_interval_seconds - elapsed)
        self._last_request_ts = time.monotonic()

    def search_by_nct(self, nct_id: str, page_size: int = 25) -> list[dict[str, str]]:
        cache_key = f"epmc:{nct_id}:{page_size}"
        cache_path = self._cache_path(cache_key)
        if cache_path.exists():
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
        else:
            self._wait_for_slot()
            params = {"query": nct_id, "format": "json", "pageSize": str(page_size)}
            response = self.session.get(EPMC_BASE, params=params, timeout=30)
            response.raise_for_status()
            payload = response.json()
            cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        results = payload.get("resultList", {}).get("result", []) if isinstance(payload, dict) else []
        return [
            {
                "id": str(item.get("id", "")),
                "source": str(item.get("source", "")),
                "title": str(item.get("title", "")),
            }
            for item in results
            if isinstance(item, dict)
        ]


def run_external_audit(older: pd.DataFrame, sample_path: Path, out_dir: Path, cache_dir: Path) -> None:
    sample = pd.read_csv(sample_path).copy()
    sample["pubmed_match_found"] = sample["pubmed_match_found"].fillna(False).astype(bool)
    sample["results_gap_2y"] = sample["results_gap_2y"].fillna(False).astype(bool)

    client = CachedEuropePMCClient(cache_dir)
    rescue_flags: list[bool] = []
    non_med_flags: list[bool] = []
    source_values: list[str] = []
    id_values: list[str] = []

    for _, row in sample.iterrows():
        if bool(row["pubmed_match_found"]):
            rescue_flags.append(False)
            non_med_flags.append(False)
            source_values.append("")
            id_values.append("")
            continue
        results = client.search_by_nct(str(row["nct_id"]))
        sources = sorted({item["source"] for item in results if item["source"]})
        ids = sorted({item["id"] for item in results if item["id"]})
        rescue = len(results) > 0
        rescue_flags.append(rescue)
        non_med_flags.append(any(source != "MED" for source in sources))
        source_values.append(" | ".join(sources))
        id_values.append(" | ".join(ids))

    sample["epmc_rescue_over_pubmed"] = rescue_flags
    sample["epmc_non_med_rescue_over_pubmed"] = non_med_flags
    sample["epmc_sources"] = source_values
    sample["epmc_ids"] = id_values
    sample["external_any_match_found"] = sample["pubmed_match_found"] | sample["epmc_rescue_over_pubmed"]
    sample["external_any_publication_only"] = sample["external_any_match_found"] & sample["results_gap_2y"]
    sample.to_csv(out_dir / "external_publication_audit_sample.csv", index=False)

    population = (
        older[older["publication_link_missing"] & older["lead_sponsor_class"].isin(SAMPLED_CLASSES)]
        .groupby("lead_sponsor_class", observed=False)
        .agg(population_no_link_studies=("nct_id", "size"))
        .reset_index()
    )
    summary = (
        sample.groupby("lead_sponsor_class", observed=False)
        .agg(
            sample_studies=("nct_id", "size"),
            sample_pubmed_match_count=("pubmed_match_found", "sum"),
            sample_pubmed_match_rate=("pubmed_match_found", "mean"),
            sample_epmc_rescue_count=("epmc_rescue_over_pubmed", "sum"),
            sample_epmc_rescue_rate=("epmc_rescue_over_pubmed", "mean"),
            sample_non_med_rescue_count=("epmc_non_med_rescue_over_pubmed", "sum"),
            sample_non_med_rescue_rate=("epmc_non_med_rescue_over_pubmed", "mean"),
            sample_external_any_match_count=("external_any_match_found", "sum"),
            sample_external_any_match_rate=("external_any_match_found", "mean"),
            sample_external_publication_only_count=("external_any_publication_only", "sum"),
            sample_external_publication_only_rate=("external_any_publication_only", "mean"),
        )
        .reset_index()
        .merge(population, on="lead_sponsor_class", how="left")
    )
    summary["population_weight"] = summary["population_no_link_studies"] / summary["population_no_link_studies"].sum()
    summary["weighted_pubmed_match_contribution"] = summary["population_weight"] * summary["sample_pubmed_match_rate"]
    summary["weighted_epmc_rescue_contribution"] = summary["population_weight"] * summary["sample_epmc_rescue_rate"]
    summary["weighted_non_med_rescue_contribution"] = summary["population_weight"] * summary["sample_non_med_rescue_rate"]
    summary["weighted_external_any_match_contribution"] = summary["population_weight"] * summary["sample_external_any_match_rate"]
    summary["weighted_external_publication_only_contribution"] = (
        summary["population_weight"] * summary["sample_external_publication_only_rate"]
    )
    rate_cols = [col for col in summary.columns if col.endswith("_rate") or "weight" in col or "contribution" in col]
    summary[rate_cols] = summary[rate_cols].mul(100).round(3)
    summary = summary.sort_values("population_no_link_studies", ascending=False)

    overall = pd.DataFrame(
        [
            {
                "lead_sponsor_class": "ALL_WEIGHTED",
                "sample_studies": int(sample["nct_id"].size),
                "sample_pubmed_match_count": int(sample["pubmed_match_found"].sum()),
                "sample_pubmed_match_rate": round(float(sample["pubmed_match_found"].mean() * 100), 3),
                "sample_epmc_rescue_count": int(sample["epmc_rescue_over_pubmed"].sum()),
                "sample_epmc_rescue_rate": round(float(sample["epmc_rescue_over_pubmed"].mean() * 100), 3),
                "sample_non_med_rescue_count": int(sample["epmc_non_med_rescue_over_pubmed"].sum()),
                "sample_non_med_rescue_rate": round(float(sample["epmc_non_med_rescue_over_pubmed"].mean() * 100), 3),
                "sample_external_any_match_count": int(sample["external_any_match_found"].sum()),
                "sample_external_any_match_rate": round(float(sample["external_any_match_found"].mean() * 100), 3),
                "sample_external_publication_only_count": int(sample["external_any_publication_only"].sum()),
                "sample_external_publication_only_rate": round(float(sample["external_any_publication_only"].mean() * 100), 3),
                "population_no_link_studies": int(population["population_no_link_studies"].sum()),
                "population_weight": 100.0,
                "weighted_pubmed_match_contribution": round(float(summary["weighted_pubmed_match_contribution"].sum()), 3),
                "weighted_epmc_rescue_contribution": round(float(summary["weighted_epmc_rescue_contribution"].sum()), 3),
                "weighted_non_med_rescue_contribution": round(float(summary["weighted_non_med_rescue_contribution"].sum()), 3),
                "weighted_external_any_match_contribution": round(float(summary["weighted_external_any_match_contribution"].sum()), 3),
                "weighted_external_publication_only_contribution": round(
                    float(summary["weighted_external_publication_only_contribution"].sum()),
                    3,
                ),
            }
        ]
    )
    pd.concat([summary, overall], ignore_index=True).to_csv(
        out_dir / "external_publication_audit_summary.csv",
        index=False,
    )


def summarize_proxy(group: pd.DataFrame, labels: dict[str, object]) -> dict[str, object]:
    unresolved = group[~group["has_results"]]
    return {
        **labels,
        "studies": int(len(group)),
        "no_results_count": int(group["results_gap_2y"].sum()),
        "no_results_rate": round(float(group["results_gap_2y"].mean() * 100), 3),
        "ghost_protocol_count": int(group["ghost_protocol"].sum()),
        "ghost_protocol_rate": round(float(group["ghost_protocol"].mean() * 100), 3),
        "results_publication_visible_rate": round(float(group["results_publication_visible"].mean() * 100), 3),
        "mean_overdue_1y_years_unresolved": round(float(unresolved["overdue_1y_years"].mean()), 3) if not unresolved.empty else np.nan,
        "mean_overdue_2y_years_unresolved": round(float(unresolved["overdue_2y_years"].mean()), 3) if not unresolved.empty else np.nan,
    }


def run_act_proxy(older: pd.DataFrame, out_dir: Path) -> None:
    flags = {
        "Broad US nexus": older["us_presence"].astype(str).eq("Any US") & ~older["phase_is_phase1_only"],
        "Drug/Bio US non-phase1": older["us_presence"].astype(str).eq("Any US") & older["has_drug_bio"] & ~older["phase_is_phase1_only"],
        "Drug/Bio/Device US strict": older["us_presence"].astype(str).eq("Any US") & (
            (older["has_drug_bio"] & ~older["phase_is_phase1_only"]) | older["has_device"]
        ),
    }

    exploded: list[pd.DataFrame] = []
    for label, mask in flags.items():
        subset = older[mask].copy()
        subset["proxy_layer"] = label
        exploded.append(subset)
    proxy = pd.concat(exploded, ignore_index=True)
    proxy["proxy_layer"] = pd.Categorical(proxy["proxy_layer"], categories=ACT_PROXY_ORDER, ordered=True)

    layer_rows = [summarize_proxy(group, {"proxy_layer": label}) for label, group in proxy.groupby("proxy_layer", observed=False)]
    class_rows = [
        summarize_proxy(group, {"proxy_layer": layer, "lead_sponsor_class": sponsor_class})
        for (layer, sponsor_class), group in proxy.groupby(["proxy_layer", "lead_sponsor_class"], observed=False)
    ]
    era_rows = [
        summarize_proxy(group, {"proxy_layer": layer, "rule_era": era})
        for (layer, era), group in proxy.groupby(["proxy_layer", "rule_era"], observed=False)
    ]

    pd.DataFrame(layer_rows).to_csv(out_dir / "act_proxy_layer_summary.csv", index=False)
    pd.DataFrame(class_rows).sort_values(["proxy_layer", "no_results_count"], ascending=[True, False]).to_csv(
        out_dir / "act_proxy_layer_sponsor_class_summary.csv",
        index=False,
    )
    pd.DataFrame(era_rows).to_csv(out_dir / "act_proxy_layer_completion_era_summary.csv", index=False)


def write_findings(out_dir: Path) -> None:
    metrics = pd.read_csv(out_dir / "risk_adjusted_model_metrics.csv")
    sponsor_class = pd.read_csv(out_dir / "risk_adjusted_sponsor_class_summary.csv")
    us_presence = pd.read_csv(out_dir / "risk_adjusted_us_presence_summary.csv")
    overdue = pd.read_csv(out_dir / "overdue_sponsor_class_clock.csv")
    external = pd.read_csv(out_dir / "external_publication_audit_summary.csv")
    act = pd.read_csv(out_dir / "act_proxy_layer_summary.csv")

    no_results_metrics = metrics[metrics["target"] == "results_gap_2y"].iloc[0]
    ghost_metrics = metrics[metrics["target"] == "ghost_protocol"].iloc[0]
    no_results_class = sponsor_class[sponsor_class["target"] == "results_gap_2y"].sort_values("excess_count", ascending=False).iloc[0]
    no_results_geo = us_presence[us_presence["target"] == "results_gap_2y"].sort_values("excess_count", ascending=False).iloc[0]
    valid_clock = overdue[overdue["studies"].fillna(0).ge(100)].copy()
    worst_clock = valid_clock.sort_values("unresolved_rate", ascending=False).iloc[0]
    weighted = external[external["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]
    strict_proxy = act[act["proxy_layer"] == "Drug/Bio/Device US strict"].iloc[0]

    lines = [
        "# Wave Eight Findings",
        "",
        "## Risk-Adjusted Hiddenness",
        "",
        f"- Holdout AUC for adjusted no-results model: {no_results_metrics['holdout_auc']:.3f}; for adjusted ghost-protocol model: {ghost_metrics['holdout_auc']:.3f}.",
        f"- Largest sponsor-class excess no-results stock after study-mix adjustment: {no_results_class['lead_sponsor_class']} at {no_results_class['excess_count']:.0f} studies.",
        f"- Largest geography-bucket excess no-results stock after adjustment: {no_results_geo['us_presence']} at {no_results_geo['excess_count']:.0f} studies.",
        "",
        "## Overdue Results Clock",
        "",
        f"- Worst sponsor class on unresolved older studies: {worst_clock['lead_sponsor_class']} at {worst_clock['unresolved_rate']:.1f}%.",
        f"- Mean overdue time beyond the two-year mark for unresolved studies in that class: {worst_clock['mean_overdue_2y_years_unresolved']:.2f} years.",
        "",
        "## External Publication Audit",
        "",
        f"- Weighted PubMed exact-ID match contribution across stratified no-link samples: {weighted['weighted_pubmed_match_contribution']:.1f}%.",
        f"- Europe PMC rescue beyond PubMed exact-ID matching adds {weighted['weighted_epmc_rescue_contribution']:.1f}% weighted match contribution.",
        f"- Non-MED rescue within that Europe PMC expansion is much smaller at {weighted['weighted_non_med_rescue_contribution']:.1f}%.",
        f"- Weighted external-publication-only contribution across the expanded audit is {weighted['weighted_external_publication_only_contribution']:.1f}%.",
        "",
        "## ACT-Style Proxy Debt",
        "",
        f"- The strict U.S.-nexus drug/bio/device proxy contains {int(strict_proxy['studies']):,} older studies with a {strict_proxy['no_results_rate']:.1f}% no-results rate.",
        f"- Mean unresolved overdue time beyond the two-year mark in that strict proxy is {strict_proxy['mean_overdue_2y_years_unresolved']:.2f} years.",
        "",
    ]
    (out_dir / "wave_eight_findings.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    older = load_older(Path(args.features), Path(args.context))
    run_risk_adjusted(older, out_dir, args.min_sponsor_studies, args.random_seed)
    run_overdue_clock(older, out_dir)
    run_external_audit(older, Path(args.pubmed_sample), out_dir, CACHE_DIR)
    run_act_proxy(older, out_dir)
    write_findings(out_dir)
    print(f"Wave-eight outputs written to {out_dir}")


if __name__ == "__main__":
    main()
