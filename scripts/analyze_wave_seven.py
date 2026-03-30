#!/usr/bin/env python3
"""Wave-seven CT.gov analyses: country sponsor repeaters, U.S. presence sponsor classes, and industry family audits."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

SELECTED_COUNTRIES = ["United States", "China", "Egypt", "Poland", "Australia", "Japan"]
US_PRESENCE_BUCKETS = ["Any US", "No US", "No named country"]
GEO_BUCKETS = ["US only", "US + non-US", "No US", "No named country"]

REPAIR_MAP = {
    "Assistance Publique - HÃ´pitaux de Paris": "Assistance Publique - Hôpitaux de Paris",
    "Assistance Publique - H�pitaux de Paris": "Assistance Publique - Hôpitaux de Paris",
    "SociÃ©tÃ© des Produits NestlÃ© (SPN)": "Société des Produits Nestlé (SPN)",
    "Soci�t� des Produits Nestl� (SPN)": "Société des Produits Nestlé (SPN)",
    "Turkey (TÃ¼rkiye)": "Turkey (Türkiye)",
    "Turkey (T�rkiye)": "Turkey (Türkiye)",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default=str(PROCESSED / "study_features.parquet"))
    parser.add_argument("--context", default=str(PROCESSED / "wave_five_study_context.parquet"))
    parser.add_argument("--out-dir", default=str(PROCESSED))
    parser.add_argument("--min-sponsor-studies", type=int, default=25)
    parser.add_argument("--min-country-studies", type=int, default=500)
    return parser.parse_args()


def clean_text(value: object) -> str:
    text = "" if value is None else str(value)
    if text in {"", "nan", "None"}:
        return ""
    repaired = text
    if any(marker in repaired for marker in ("Ã", "Â", "â")):
        try:
            repaired = repaired.encode("latin-1").decode("utf-8")
        except UnicodeError:
            repaired = text
    return REPAIR_MAP.get(repaired, REPAIR_MAP.get(text, repaired))


def clean_object_columns(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for column in cleaned.columns:
        if pd.api.types.is_object_dtype(cleaned[column]):
            cleaned[column] = cleaned[column].map(clean_text)
    return cleaned


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
        )
        .reset_index()
    )
    rate_columns = [column for column in grouped.columns if column.endswith("_rate")]
    grouped[rate_columns] = grouped[rate_columns].mul(100).round(3)
    grouped["hiddenness_score_mean"] = grouped["hiddenness_score_mean"].round(3)
    return grouped


def summarize_multi(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    grouped = (
        df.groupby(group_cols, observed=False)
        .agg(
            studies=("nct_id", "size"),
            no_results_count=("results_gap_2y", "sum"),
            no_results_rate=("results_gap_2y", "mean"),
            no_publication_rate=("publication_link_missing", "mean"),
            ghost_protocol_count=("ghost_protocol", "sum"),
            ghost_protocol_rate=("ghost_protocol", "mean"),
            results_publication_visible_rate=("results_publication_visible", "mean"),
            hiddenness_score_mean=("hiddenness_score", "mean"),
        )
        .reset_index()
    )
    rate_columns = [column for column in grouped.columns if column.endswith("_rate")]
    grouped[rate_columns] = grouped[rate_columns].mul(100).round(3)
    grouped["hiddenness_score_mean"] = grouped["hiddenness_score_mean"].round(3)
    return grouped


def with_us_presence(df: pd.DataFrame) -> pd.DataFrame:
    country_text = df["country_names_text"].fillna("").astype(str)
    named_country_count = pd.to_numeric(df["named_country_count"], errors="coerce").fillna(0)
    us = country_text.str.contains("United States", regex=False)

    labels = pd.Series("No named country", index=df.index)
    labels[named_country_count.ge(1) & ~us] = "No US"
    labels[us] = "Any US"
    updated = df.copy()
    updated["us_presence"] = pd.Categorical(labels, categories=US_PRESENCE_BUCKETS, ordered=True)
    return updated


def with_geo_bucket(df: pd.DataFrame) -> pd.DataFrame:
    country_text = df["country_names_text"].fillna("").astype(str)
    named_country_count = pd.to_numeric(df["named_country_count"], errors="coerce").fillna(0)
    us = country_text.str.contains("United States", regex=False)

    labels = pd.Series("No named country", index=df.index)
    labels[us & country_text.eq("United States")] = "US only"
    labels[us & ~country_text.eq("United States")] = "US + non-US"
    labels[named_country_count.ge(1) & ~us] = "No US"
    updated = df.copy()
    updated["geo_bucket"] = pd.Categorical(labels, categories=GEO_BUCKETS, ordered=True)
    return updated


def explode_nonempty(df: pd.DataFrame, source_col: str, label_col: str) -> pd.DataFrame:
    exploded = df.copy()
    exploded[label_col] = exploded[source_col].fillna("").astype(str).str.split("|")
    exploded = exploded.explode(label_col)
    exploded[label_col] = exploded[label_col].fillna("").astype(str).str.strip()
    return exploded[exploded[label_col].ne("")]


def write_findings(out_dir: Path) -> None:
    us_presence = pd.read_csv(out_dir / "us_presence_visibility_older_2y.csv", keep_default_na=False)
    sponsor_class = pd.read_csv(out_dir / "us_presence_sponsor_class_visibility_older_2y.csv", keep_default_na=False)
    country_repeaters = pd.read_csv(out_dir / "selected_country_sponsor_repeaters_top_older_2y.csv", keep_default_na=False)
    industry_repeaters = pd.read_csv(out_dir / "industry_intervention_sponsor_top_backlog_older_2y.csv", keep_default_na=False)
    industry_geo = pd.read_csv(out_dir / "industry_geo_visibility_older_2y.csv", keep_default_na=False)

    any_us = us_presence[us_presence["us_presence"] == "Any US"].iloc[0]
    no_us = us_presence[us_presence["us_presence"] == "No US"].iloc[0]
    no_country = us_presence[us_presence["us_presence"] == "No named country"].iloc[0]
    no_us_other = sponsor_class[
        (sponsor_class["us_presence"] == "No US") & (sponsor_class["lead_sponsor_class"] == "OTHER")
    ].iloc[0]
    no_us_industry = sponsor_class[
        (sponsor_class["us_presence"] == "No US") & (sponsor_class["lead_sponsor_class"] == "INDUSTRY")
    ].iloc[0]
    us_industry = sponsor_class[
        (sponsor_class["us_presence"] == "Any US") & (sponsor_class["lead_sponsor_class"] == "INDUSTRY")
    ].iloc[0]
    china_top = country_repeaters[country_repeaters["country"] == "China"].iloc[0]
    egypt_top = country_repeaters[country_repeaters["country"] == "Egypt"].iloc[0]
    us_top = country_repeaters[country_repeaters["country"] == "United States"].iloc[0]
    drug_top = industry_repeaters[industry_repeaters["intervention_type"] == "DRUG"].iloc[0]
    mixed_industry = industry_geo[industry_geo["geo_bucket"] == "US + non-US"].iloc[0]
    no_us_industry_geo = industry_geo[industry_geo["geo_bucket"] == "No US"].iloc[0]

    def as_float(value: object) -> float:
        return float(value)

    def as_int(value: object) -> int:
        return int(float(value))

    lines = [
        "# Wave Seven Findings",
        "",
        "## Country Sponsor Repeaters",
        "",
        f"- In United States-linked studies, {us_top['lead_sponsor_name']} carries the largest missing-results stock at {as_int(us_top['no_results_count']):,} studies.",
        f"- In China-linked studies, {china_top['lead_sponsor_name']} leads at {as_int(china_top['no_results_count']):,} studies; in Egypt-linked studies, {egypt_top['lead_sponsor_name']} leads at {as_int(egypt_top['no_results_count']):,}.",
        "",
        "## U.S. Versus Ex-U.S. Sponsor Classes",
        "",
        f"- Any-U.S. studies show a {as_float(any_us['no_results_rate']):.1f}% 2-year no-results rate, versus {as_float(no_us['no_results_rate']):.1f}% for no-U.S. studies and {as_float(no_country['no_results_rate']):.1f}% for no-country studies.",
        f"- Within no-U.S. studies, OTHER reaches {as_float(no_us_other['no_results_rate']):.1f}% no results and INDUSTRY reaches {as_float(no_us_industry['no_results_rate']):.1f}%, versus {as_float(us_industry['no_results_rate']):.1f}% for any-U.S. industry.",
        "",
        "## Industry Family Audit",
        "",
        f"- In drug studies, {drug_top['lead_sponsor_name']} carries the largest industry missing-results stock at {as_int(drug_top['no_results_count']):,} studies.",
        f"- Industry no-results rates rise from {as_float(mixed_industry['no_results_rate']):.1f}% in mixed U.S.-plus-non-U.S. portfolios to {as_float(no_us_industry_geo['no_results_rate']):.1f}% in no-U.S. portfolios.",
        "",
    ]
    (out_dir / "wave_seven_findings.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    features = pd.read_parquet(
        Path(args.features),
        columns=[
            "nct_id",
            "lead_sponsor_name",
            "lead_sponsor_class",
            "results_gap_2y",
            "publication_link_missing",
            "hiddenness_score",
            "is_interventional",
            "is_closed",
            "days_since_primary_completion",
        ],
    )
    context = pd.read_parquet(Path(args.context))
    context = clean_object_columns(context)

    older = features[
        features["is_interventional"] & features["is_closed"] & features["days_since_primary_completion"].fillna(-1).ge(730)
    ].copy()
    older["ghost_protocol"] = older["results_gap_2y"] & older["publication_link_missing"]
    older["results_publication_visible"] = (~older["results_gap_2y"]) & (~older["publication_link_missing"])
    older = older.merge(
        context[["nct_id", "country_names_text", "named_country_count", "intervention_types_text"]],
        on="nct_id",
        how="left",
    )
    older = clean_object_columns(older)
    older = with_us_presence(older)
    older = with_geo_bucket(older)

    summarize_bucket(older, "us_presence").to_csv(out_dir / "us_presence_visibility_older_2y.csv", index=False)
    summarize_multi(older, ["us_presence", "lead_sponsor_class"]).to_csv(
        out_dir / "us_presence_sponsor_class_visibility_older_2y.csv", index=False
    )

    exploded_country = explode_nonempty(older, "country_names_text", "country")
    selected_country = exploded_country[exploded_country["country"].isin(SELECTED_COUNTRIES)].copy()
    summarize_multi(selected_country, ["country", "lead_sponsor_class"]).to_csv(
        out_dir / "selected_country_sponsor_class_visibility_older_2y.csv",
        index=False,
    )
    country_sponsor = summarize_multi(selected_country, ["country", "lead_sponsor_name"])
    country_sponsor = country_sponsor[country_sponsor["studies"] >= args.min_sponsor_studies].copy()
    country_sponsor = country_sponsor.sort_values(["country", "no_results_count", "studies"], ascending=[True, False, False])
    country_sponsor.to_csv(out_dir / "selected_country_sponsor_repeaters_older_2y.csv", index=False)
    country_sponsor.groupby("country", group_keys=False).head(10).to_csv(
        out_dir / "selected_country_sponsor_repeaters_top_older_2y.csv",
        index=False,
    )

    industry = older[older["lead_sponsor_class"] == "INDUSTRY"].copy()
    summarize_bucket(industry, "geo_bucket").to_csv(out_dir / "industry_geo_visibility_older_2y.csv", index=False)
    industry_country = explode_nonempty(industry, "country_names_text", "country")
    industry_country = summarize_multi(industry_country, ["country"])
    industry_country = industry_country[industry_country["studies"] >= args.min_country_studies].copy()
    industry_country = industry_country.sort_values(["studies", "no_results_rate"], ascending=[False, False])
    industry_country.to_csv(out_dir / "industry_country_visibility_older_2y.csv", index=False)

    industry_intervention = explode_nonempty(industry, "intervention_types_text", "intervention_type")
    summarize_bucket(industry_intervention, "intervention_type").to_csv(
        out_dir / "industry_intervention_visibility_older_2y.csv",
        index=False,
    )
    industry_sponsor = summarize_multi(industry_intervention, ["intervention_type", "lead_sponsor_name"])
    industry_sponsor = industry_sponsor[industry_sponsor["studies"] >= args.min_sponsor_studies].copy()
    industry_sponsor = industry_sponsor.sort_values(
        ["intervention_type", "no_results_count", "studies"], ascending=[True, False, False]
    )
    industry_sponsor.to_csv(out_dir / "industry_intervention_sponsor_backlog_older_2y.csv", index=False)
    industry_sponsor.groupby("intervention_type", group_keys=False).head(10).to_csv(
        out_dir / "industry_intervention_sponsor_top_backlog_older_2y.csv",
        index=False,
    )

    write_findings(out_dir)


if __name__ == "__main__":
    main()
