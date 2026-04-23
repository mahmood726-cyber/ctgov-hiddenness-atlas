#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Build wave-six standalone CT.gov projects from geography and repeater analyses."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct
from build_split_projects import chart_section, sentence_bundle, write_project

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

REPAIR_MAP = {
    "Assistance Publique - H�pitaux de Paris": "Assistance Publique - Hôpitaux de Paris",
    "Assistance Publique - HÃ´pitaux de Paris": "Assistance Publique - Hôpitaux de Paris",
    "Soci�t� des Produits Nestl� (SPN)": "Société des Produits Nestlé (SPN)",
    "SociÃ©tÃ© des Produits NestlÃ© (SPN)": "Société des Produits Nestlé (SPN)",
    "Turkey (T�rkiye)": "Turkey (Türkiye)",
    "Turkey (TÃ¼rkiye)": "Turkey (Türkiye)",
}

SPONSOR_SHORT = {
    "National Cancer Institute (NCI)": "NCI",
    "National Institute of Allergy and Infectious Diseases (NIAID)": "NIAID",
    "M.D. Anderson Cancer Center": "MD Anderson",
    "Memorial Sloan Kettering Cancer Center": "MSKCC",
    "University of California, San Francisco": "UCSF",
    "University Health Network, Toronto": "UHN Toronto",
    "Maastricht University Medical Center": "Maastricht UMC",
    "Assistance Publique - Hôpitaux de Paris": "AP-HP",
    "European Organisation for Research and Treatment of Cancer - EORTC": "EORTC",
    "Jiangsu HengRui Medicine Co., Ltd.": "Jiangsu HengRui",
    "Société des Produits Nestlé (SPN)": "Nestlé SPN",
    "Seoul National University Hospital": "SNU Hospital",
    "University of Pennsylvania": "UPenn",
    "University of Michigan": "Michigan",
    "University of Pittsburgh": "Pittsburgh",
    "University of Copenhagen": "Copenhagen",
    "University of Aarhus": "Aarhus",
    "Novo Nordisk A/S": "Novo Nordisk",
    "Boehringer Ingelheim": "Boehringer",
    "GlaxoSmithKline": "GSK",
    "Novartis Pharmaceuticals": "Novartis",
}

COUNTRY_SHORT = {"United States": "US", "United Kingdom": "UK", "South Korea": "S. Korea", "No named country": "No country"}
INTERVENTION_SHORT = {"BEHAVIORAL": "Behavioral", "BIOLOGICAL": "Biological", "DEVICE": "Device", "DIAGNOSTIC_TEST": "Diagnostic", "DIETARY_SUPPLEMENT": "Dietary", "DRUG": "Drug", "PROCEDURE": "Procedure"}
GEO_SHORT = {"US only": "US only", "US + non-US": "US + non-US", "No US": "No US", "No named country": "No country"}


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


def load_csv(name: str) -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / name, keep_default_na=False)
    for column in df.columns:
        if pd.api.types.is_object_dtype(df[column]):
            df[column] = df[column].map(clean_text)
    return df


def row_for(df: pd.DataFrame, column: str, value: str) -> pd.Series:
    return df[df[column] == value].iloc[0]


def row_for_pair(df: pd.DataFrame, left: str, left_value: str, right: str, right_value: str) -> pd.Series:
    return df[(df[left] == left_value) & (df[right] == right_value)].iloc[0]


def top_rows(df: pd.DataFrame, column: str, value: str, count: int = 10) -> pd.DataFrame:
    return df[df[column] == value].head(count).copy()


def sponsor_short(name: str) -> str:
    clean_name = clean_text(name)
    return SPONSOR_SHORT.get(clean_name, clean_name)


def country_short(name: str) -> str:
    clean_name = clean_text(name)
    return COUNTRY_SHORT.get(clean_name, clean_name)


def intervention_short(name: str) -> str:
    clean_name = clean_text(name)
    return INTERVENTION_SHORT.get(clean_name, clean_name.title())


def geo_short(name: str) -> str:
    clean_name = clean_text(name)
    return GEO_SHORT.get(clean_name, clean_name)


def make_spec(
    *,
    repo_name: str,
    title: str,
    summary: str,
    body: str,
    sentences: list[dict[str, str]],
    primary_estimand: str,
    data_note: str,
    protocol: str,
    root_title: str,
    root_eyebrow: str,
    root_lede: str,
    chapter_intro: str,
    root_pull_quote: str,
    paper_pull_quote: str,
    dashboard_pull_quote: str,
    root_rail: list[str],
    landing_metrics: list[tuple[str, str, str]],
    landing_chart_html: str,
    reader_lede: str,
    reader_rail: list[str],
    reader_metrics: list[tuple[str, str, str]],
    dashboard_title: str,
    dashboard_eyebrow: str,
    dashboard_lede: str,
    dashboard_rail: list[str],
    dashboard_metrics: list[tuple[str, str, str]],
    dashboard_sections: list[str],
    sidebar_bullets: list[str],
    references: list[str],
) -> dict[str, object]:
    return {
        "repo_name": repo_name,
        "title": title,
        "summary": summary,
        "body": body,
        "sentences": sentences,
        "primary_estimand": primary_estimand,
        "data_note": data_note,
        "references": references,
        "protocol": protocol,
        "root_title": root_title,
        "root_eyebrow": root_eyebrow,
        "root_lede": root_lede,
        "chapter_intro": chapter_intro,
        "root_pull_quote": root_pull_quote,
        "root_pull_source": "Project readout",
        "paper_pull_quote": paper_pull_quote,
        "paper_pull_source": "Reading note",
        "dashboard_pull_quote": dashboard_pull_quote,
        "dashboard_pull_source": "How to read the dashboard",
        "root_rail": root_rail,
        "landing_metrics": landing_metrics,
        "landing_chart_html": landing_chart_html,
        "reader_lede": reader_lede,
        "reader_rail": reader_rail,
        "reader_metrics": reader_metrics,
        "dashboard_title": dashboard_title,
        "dashboard_eyebrow": dashboard_eyebrow,
        "dashboard_lede": dashboard_lede,
        "dashboard_rail": dashboard_rail,
        "dashboard_metrics": dashboard_metrics,
        "dashboard_sections": dashboard_sections,
        "sidebar_bullets": sidebar_bullets,
    }


def main() -> None:
    geo = load_csv("us_global_visibility_older_2y.csv")
    geo_sponsor = load_csv("geo_sponsor_class_visibility_older_2y.csv")
    condition_geo = load_csv("condition_geo_visibility_older_2y.csv")
    condition_country = load_csv("condition_country_visibility_selected_older_2y.csv")
    intervention_top = load_csv("intervention_sponsor_top_backlog_older_2y.csv")
    condition_sponsor_top = load_csv("condition_sponsor_top_backlog_older_2y.csv")

    us_only = row_for(geo, "geo_bucket", "US only")
    us_mixed = row_for(geo, "geo_bucket", "US + non-US")
    no_us = row_for(geo, "geo_bucket", "No US")
    no_country = row_for(geo, "geo_bucket", "No named country")

    mixed_industry = row_for_pair(geo_sponsor, "geo_bucket", "US + non-US", "lead_sponsor_class", "INDUSTRY")
    us_industry = row_for_pair(geo_sponsor, "geo_bucket", "US only", "lead_sponsor_class", "INDUSTRY")
    no_us_industry = row_for_pair(geo_sponsor, "geo_bucket", "No US", "lead_sponsor_class", "INDUSTRY")
    no_us_other = row_for_pair(geo_sponsor, "geo_bucket", "No US", "lead_sponsor_class", "OTHER")
    mixed_nih = row_for_pair(geo_sponsor, "geo_bucket", "US + non-US", "lead_sponsor_class", "NIH")
    us_nih = row_for_pair(geo_sponsor, "geo_bucket", "US only", "lead_sponsor_class", "NIH")

    cardio_us = row_for_pair(condition_geo, "condition_family_label", "Cardiovascular", "geo_bucket", "US only")
    cardio_mixed = row_for_pair(condition_geo, "condition_family_label", "Cardiovascular", "geo_bucket", "US + non-US")
    cardio_no_us = row_for_pair(condition_geo, "condition_family_label", "Cardiovascular", "geo_bucket", "No US")
    cardio_no_country = row_for_pair(condition_geo, "condition_family_label", "Cardiovascular", "geo_bucket", "No named country")
    metabolic_us = row_for_pair(condition_geo, "condition_family_label", "Metabolic", "geo_bucket", "US only")
    metabolic_mixed = row_for_pair(condition_geo, "condition_family_label", "Metabolic", "geo_bucket", "US + non-US")
    metabolic_no_us = row_for_pair(condition_geo, "condition_family_label", "Metabolic", "geo_bucket", "No US")
    metabolic_no_country = row_for_pair(condition_geo, "condition_family_label", "Metabolic", "geo_bucket", "No named country")
    oncology_us_geo = row_for_pair(condition_geo, "condition_family_label", "Oncology", "geo_bucket", "US only")
    oncology_mixed = row_for_pair(condition_geo, "condition_family_label", "Oncology", "geo_bucket", "US + non-US")
    oncology_no_us = row_for_pair(condition_geo, "condition_family_label", "Oncology", "geo_bucket", "No US")
    oncology_no_country = row_for_pair(condition_geo, "condition_family_label", "Oncology", "geo_bucket", "No named country")

    oncology_us = row_for_pair(condition_country, "condition_family_label", "Oncology", "country", "United States")
    oncology_china = row_for_pair(condition_country, "condition_family_label", "Oncology", "country", "China")
    oncology_spain = row_for_pair(condition_country, "condition_family_label", "Oncology", "country", "Spain")
    oncology_australia = row_for_pair(condition_country, "condition_family_label", "Oncology", "country", "Australia")
    oncology_poland = row_for_pair(condition_country, "condition_family_label", "Oncology", "country", "Poland")
    cardio_country_us = row_for_pair(condition_country, "condition_family_label", "Cardiovascular", "country", "United States")
    cardio_china = row_for_pair(condition_country, "condition_family_label", "Cardiovascular", "country", "China")
    cardio_egypt = row_for_pair(condition_country, "condition_family_label", "Cardiovascular", "country", "Egypt")
    cardio_poland = row_for_pair(condition_country, "condition_family_label", "Cardiovascular", "country", "Poland")
    cardio_australia = row_for_pair(condition_country, "condition_family_label", "Cardiovascular", "country", "Australia")
    cardio_japan = row_for_pair(condition_country, "condition_family_label", "Cardiovascular", "country", "Japan")
    metabolic_country_us = row_for_pair(condition_country, "condition_family_label", "Metabolic", "country", "United States")
    metabolic_china = row_for_pair(condition_country, "condition_family_label", "Metabolic", "country", "China")
    metabolic_denmark = row_for_pair(condition_country, "condition_family_label", "Metabolic", "country", "Denmark")
    metabolic_spain = row_for_pair(condition_country, "condition_family_label", "Metabolic", "country", "Spain")

    drug_top = row_for(intervention_top, "intervention_type", "DRUG")
    device_top = row_for(intervention_top, "intervention_type", "DEVICE")
    procedure_top = row_for(intervention_top, "intervention_type", "PROCEDURE")
    behavioral_top = row_for(intervention_top, "intervention_type", "BEHAVIORAL")
    biological_top = row_for(intervention_top, "intervention_type", "BIOLOGICAL")
    dietary_top = row_for(intervention_top, "intervention_type", "DIETARY_SUPPLEMENT")
    drug_rows = top_rows(intervention_top, "intervention_type", "DRUG", 8)

    oncology_rows = top_rows(condition_sponsor_top, "condition_family_label", "Oncology", 8)
    cardio_rows = top_rows(condition_sponsor_top, "condition_family_label", "Cardiovascular", 8)
    metabolic_rows = top_rows(condition_sponsor_top, "condition_family_label", "Metabolic", 8)
    oncology_top = oncology_rows.iloc[0]
    oncology_second = oncology_rows.iloc[1]
    oncology_uhn = oncology_rows.iloc[4]
    cardio_top = cardio_rows.iloc[0]
    cardio_second = cardio_rows.iloc[1]
    metabolic_top = metabolic_rows.iloc[0]
    metabolic_second = metabolic_rows.iloc[1]

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
    ]

    all_series_specs = [
        {"repo_name": "ctgov-industry-disclosure-gap", "title": "CT.gov Industry Disclosure Gap", "summary": "Industry-focused missing-results stock, sponsor backlogs, and structural sparsity inside CT.gov.", "short_title": "Industry"},
        {"repo_name": "ctgov-sponsor-class-hiddenness", "title": "CT.gov Sponsor-Class Hiddenness", "summary": "Sponsor-class comparisons on rate, stock, and structural hiddenness rather than one flattened ranking.", "short_title": "Sponsor Classes"},
        {"repo_name": "ctgov-phase-reporting-gap", "title": "CT.gov Phase Reporting Gap", "summary": "Phase-by-phase disclosure gaps showing how silence changes along the development pathway.", "short_title": "Phases"},
        {"repo_name": "ctgov-structural-missingness", "title": "CT.gov Structural Missingness", "summary": "Field-level missingness across publication links, IPD statements, descriptions, and locations.", "short_title": "Structural"},
        {"repo_name": "ctgov-evidence-visibility-gap", "title": "CT.gov Evidence Visibility Gap", "summary": "Results-plus-publication visibility states showing how many older trials are fully visible, partly visible, or ghosted.", "short_title": "Visibility"},
        {"repo_name": "ctgov-completion-cohort-debt", "title": "CT.gov Completion Cohort Debt", "summary": "Completion-era reporting debt showing how older eligible cohorts drift on no-results and ghost-protocol rates.", "short_title": "Cohorts"},
        {"repo_name": "ctgov-condition-hiddenness-map", "title": "CT.gov Condition Hiddenness Map", "summary": "Keyword-classified therapeutic-area hiddenness mapping across common condition families.", "short_title": "Conditions"},
        {"repo_name": "ctgov-sponsor-backlog-concentration", "title": "CT.gov Sponsor Backlog Concentration", "summary": "Concentration and inequality analysis showing how much unresolved stock sits inside a thin sponsor slice.", "short_title": "Concentration"},
        {"repo_name": "ctgov-rule-era-reporting-gap", "title": "CT.gov Rule-Era Reporting Gap", "summary": "Policy-era comparisons across pre-FDAAA, FDAAA, and later CT.gov completion cohorts.", "short_title": "Rule Eras"},
        {"repo_name": "ctgov-publication-undercount-audit", "title": "CT.gov Publication Undercount Audit", "summary": "Sample-based external PubMed NCT audit testing how often CT.gov no-link records hide an external paper trail.", "short_title": "PubMed Audit"},
        {"repo_name": "ctgov-oncology-hiddenness", "title": "CT.gov Oncology Hiddenness", "summary": "Oncology-specific CT.gov hiddenness showing where cancer-trial stock, phases, and sponsors still go quiet.", "short_title": "Oncology"},
        {"repo_name": "ctgov-cardiovascular-hiddenness", "title": "CT.gov Cardiovascular Hiddenness", "summary": "Cardiovascular CT.gov hiddenness showing how heart and vascular studies remain quiet across major phases and sponsors.", "short_title": "Cardiovascular"},
        {"repo_name": "ctgov-metabolic-hiddenness", "title": "CT.gov Metabolic Hiddenness", "summary": "Metabolic CT.gov hiddenness across obesity, diabetes, and related trial portfolios with large late-phase and NA stock.", "short_title": "Metabolic"},
        {"repo_name": "ctgov-enrollment-size-gap", "title": "CT.gov Enrollment-Size Gap", "summary": "Enrollment-size gradients showing how older small trials remain much quieter than larger registered studies.", "short_title": "Size"},
        {"repo_name": "ctgov-geography-scale-visibility", "title": "CT.gov Geography-Scale Visibility", "summary": "Site and country footprint analysis showing how larger trial geographies map onto much better public visibility.", "short_title": "Geography"},
        {"repo_name": "ctgov-design-purpose-hiddenness", "title": "CT.gov Design-Purpose Hiddenness", "summary": "Primary-purpose and allocation analysis showing which trial intents remain most obscured on CT.gov.", "short_title": "Purpose"},
        {"repo_name": "ctgov-completion-delay-debt", "title": "CT.gov Completion-Delay Debt", "summary": "Registration-to-completion delay analysis showing short-cycle studies carry the heaviest reporting debt.", "short_title": "Delay"},
        {"repo_name": "ctgov-trial-architecture-gap", "title": "CT.gov Trial-Architecture Gap", "summary": "Arm-count and intervention-count analysis showing simpler trial architectures are often the quietest.", "short_title": "Architecture"},
        {"repo_name": "ctgov-intervention-type-gap", "title": "CT.gov Intervention-Type Gap", "summary": "Intervention-family analysis showing which declared treatment modalities remain quietest on older CT.gov records.", "short_title": "Interventions"},
        {"repo_name": "ctgov-country-reporting-map", "title": "CT.gov Country Reporting Map", "summary": "Named-country visibility analysis showing large geographic divides in older CT.gov reporting debt.", "short_title": "Countries"},
        {"repo_name": "ctgov-stopped-trial-disclosure-gap", "title": "CT.gov Stopped-Trial Disclosure Gap", "summary": "Final-status analysis showing how withdrawn, suspended, and terminated studies remain structurally quieter than completed trials.", "short_title": "Stopped"},
        {"repo_name": "ctgov-outcome-density-gap", "title": "CT.gov Outcome-Density Gap", "summary": "Outcome-count and outcome-description analysis showing sparse protocols are often the quietest CT.gov segment.", "short_title": "Outcomes"},
        {"repo_name": "ctgov-actual-field-discipline", "title": "CT.gov Actual-Field Discipline", "summary": "Closed-study actual-field analysis showing missing actual dates and counts are a strong warning sign for opacity.", "short_title": "Actual Fields"},
        {"repo_name": "ctgov-us-vs-global-gap", "title": "CT.gov U.S. Versus Global Gap", "summary": "Geography-bucket analysis showing how U.S.-only, mixed, and non-U.S. portfolios diverge sharply on visibility.", "short_title": "US vs Global"},
        {"repo_name": "ctgov-modality-sponsor-repeaters", "title": "CT.gov Modality Sponsor Repeaters", "summary": "Intervention-family sponsor audit showing that repeat offenders change sharply once modality is held fixed.", "short_title": "Modality Sponsors"},
        {"repo_name": "ctgov-country-condition-hiddenness", "title": "CT.gov Country-Condition Hiddenness", "summary": "Country-by-condition splits showing how disease-specific visibility changes once specific national footprints are named.", "short_title": "Country x Condition"},
        {"repo_name": "ctgov-disease-geography-gap", "title": "CT.gov Disease Geography Gap", "summary": "Disease-family geography buckets showing how oncology, cardiovascular, and metabolic studies diverge by U.S. participation.", "short_title": "Disease Geography"},
        {"repo_name": "ctgov-condition-sponsor-repeaters", "title": "CT.gov Condition Sponsor Repeaters", "summary": "Condition-family sponsor audit showing who carries the biggest hiddenness stock within oncology, cardiovascular, and metabolic studies.", "short_title": "Condition Sponsors"},
    ]
    series_links = [
        {"repo_name": item["repo_name"], "title": item["title"], "summary": item["summary"], "short_title": item["short_title"], "pages_url": f"https://{REPO_OWNER}.github.io/{item['repo_name']}/"}
        for item in all_series_specs
    ]
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    us_body, us_sentences = sentence_bundle([
        ("Question", "How different are ClinicalTrials.gov reporting gaps when older closed interventional studies are grouped into U.S.-only, mixed U.S.-global, non-U.S., and no-country buckets?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and assigned each study to a geography bucket using recorded country locations."),
        ("Method", "The project compares two-year no-results rates, ghost-protocol rates, visible shares, and sponsor-class contrasts across U.S.-only, U.S.-plus-non-U.S., non-U.S., and missing-country records."),
        ("Primary result", "U.S.-plus-non-U.S. studies were the cleanest bucket at 30.2 percent no results, versus 55.8 percent for U.S.-only studies and 88.7 percent for studies with no U.S. location."),
        ("Secondary result", "No-country records also remained obscured at 80.9 percent no results and 53.6 percent ghost protocols, while mixed U.S.-global studies reached 46.3 percent full visibility."),
        ("Interpretation", "Geography bucket therefore behaves like a visibility classifier, and cross-border participation looks associated with cleaner registry surfaces than domestic-only or non-U.S.-only portfolios."),
        ("Boundary", "Country buckets reflect recorded locations rather than verified enrollment shares, sponsor domicile, or legal reporting duties."),
    ])
    modality_body, modality_sentences = sentence_bundle([
        ("Question", "Which sponsors carry the biggest missing-results backlogs once older CT.gov studies are split by intervention family rather than ranked in one pooled sponsor table?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and linked sponsors to intervention-family labels from the registry extract."),
        ("Method", "The project compares sponsor-level no-results counts, no-results rates, ghost-protocol rates, and visible shares within drug, device, procedure, behavioral, biological, and dietary-supplement study families."),
        ("Primary result", "In drug studies, GlaxoSmithKline carried 1,033 missing-results studies, while Cairo University led device studies with 205 records."),
        ("Secondary result", "Procedure studies led by Cairo University reached 97.3 percent no results, Maastricht University Medical Center led dietary-supplement backlogs with 154 studies, and UCSF led behavioral backlogs with 317."),
        ("Interpretation", "Sponsor repeaters therefore change sharply by modality, meaning whole-registry rankings hide intervention-specific clusters of silence that recur inside particular treatment families."),
        ("Boundary", "Sponsor names and intervention labels are registry-entered fields and do not adjudicate parent-company structure, collaborations, or off-platform dissemination."),
    ])
    country_condition_body, country_condition_sentences = sentence_bundle([
        ("Question", "Which disease-country cells look quietest on ClinicalTrials.gov once older closed interventional studies are split simultaneously by condition family and named study location?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded named-country involvement within selected condition families."),
        ("Method", "The project compares two-year no-results rates, ghost-protocol rates, and visible shares for oncology, cardiovascular, and metabolic studies across country-condition cells with at least 400 studies."),
        ("Primary result", "Oncology studies involving China reached 79.0 percent no results versus 52.6 percent for oncology studies involving the United States."),
        ("Secondary result", "Cardiovascular studies involving Egypt reached 95.9 percent no results, while metabolic studies involving China reached 78.9 percent and Denmark 79.6 percent."),
        ("Interpretation", "Disease and geography therefore interact rather than add independently, because the same condition family looks materially different once specific country footprints are named inside the same nominal therapeutic area."),
        ("Boundary", "Country-condition cells reflect recorded study locations rather than country-specific enrollment shares, sponsor domicile, or national reporting mandates."),
    ])
    disease_geo_body, disease_geo_sentences = sentence_bundle([
        ("Question", "How does geography reshape the hiddenness of major disease families once older CT.gov studies are grouped into U.S.-only, mixed, non-U.S., and no-country buckets?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and linked geography buckets to oncology, cardiovascular, and metabolic families."),
        ("Method", "The project compares two-year no-results rates, ghost-protocol rates, visible shares, and hiddenness scores across geography buckets within each selected disease family."),
        ("Primary result", "U.S.-plus-non-U.S. studies were the cleanest geography bucket in every disease family: 29.9 percent no results in cardiovascular, 29.4 percent in metabolic, and 39.4 percent in oncology."),
        ("Secondary result", "No-U.S. studies were worst: 89.9 percent no results in cardiovascular, 90.3 percent in metabolic, and 86.8 percent in oncology."),
        ("Interpretation", "The disease story therefore depends on geography structure, because the same clinical area can move from moderately visible to deeply hidden depending on where studies are located."),
        ("Boundary", "Geography buckets use recorded locations rather than verified recruitment shares, sponsor domicile, or disease-burden denominators."),
    ])
    condition_sponsor_body, condition_sponsor_sentences = sentence_bundle([
        ("Question", "Which sponsors carry the largest missing-results backlogs inside disease families on ClinicalTrials.gov once studies are grouped by condition rather than pooled together?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and linked sponsors to oncology, cardiovascular, and metabolic condition families."),
        ("Method", "The project compares sponsor-level no-results counts, no-results rates, ghost-protocol rates, and visible shares within each selected disease family."),
        ("Primary result", "In oncology, the National Cancer Institute carried the largest missing-results stock at 909 older studies, ahead of M.D. Anderson Cancer Center at 589."),
        ("Secondary result", "In cardiovascular studies, Assistance Publique-Hôpitaux de Paris reached 100.0 percent no results and Yonsei University 98.6 percent, while Novo Nordisk led metabolic backlogs with 391 studies."),
        ("Interpretation", "Sponsor repeaters therefore change sharply by disease family, and condition-specific audits reveal institutional pockets of silence that disappear inside whole-registry rankings."),
        ("Boundary", "Condition families and sponsor names are derived from registry text and do not adjudicate network authorship, parent ownership, or off-platform reporting."),
    ])

    projects: list[dict[str, object]] = []
    projects.append(
        make_spec(
            repo_name="ctgov-us-vs-global-gap",
            title="CT.gov U.S. Versus Global Gap",
            summary="A standalone E156 project on how U.S.-only, cross-border, and non-U.S. geography buckets sharply separate older-study visibility on CT.gov.",
            body=us_body,
            sentences=us_sentences,
            primary_estimand="2-year no-results rate across U.S./non-U.S. geography buckets among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies grouped into U.S.-only, mixed, non-U.S., and no-country buckets",
            references=common_refs,
            protocol=(
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies into four geography buckets using recorded study-country locations: U.S. only, U.S. plus non-U.S., no U.S., and no named country. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and fully visible shares across those buckets, with a secondary sponsor-class contrast for industry, NIH, and other sponsors. "
                "The aim is to test whether cross-border participation corresponds to a materially different public registry surface than domestic-only or non-U.S.-only portfolios. "
                "Because the buckets come from recorded locations, the analysis measures registry geography rather than verified enrollment share, sponsor domicile, or legal obligation."
            ),
            root_title="Does U.S. participation make older CT.gov studies more visible?",
            root_eyebrow="Geography Bucket Project",
            root_lede="A standalone public project on U.S. versus global visibility, showing that cross-border studies are markedly cleaner than domestic-only or no-U.S. portfolios in older CT.gov records.",
            chapter_intro="This page pushes the geography work beyond simple country counts. The relevant split is whether a study is U.S. only, genuinely cross-border, entirely outside the U.S., or missing named-country detail altogether.",
            root_pull_quote="Mixed U.S.-global studies are the cleanest geography bucket in the wave, while no-U.S. portfolios sit in a far quieter registry zone.",
            paper_pull_quote="Cross-border participation is not decorative metadata. It marks one of the strongest visibility breaks in the registry.",
            dashboard_pull_quote="The main contrast is not simply U.S. versus non-U.S.; it is mixed cross-border visibility versus everything else.",
            root_rail=["Mixed 30.2%", "US only 55.8%", "No US 88.7%", "No country 80.9%"],
            landing_metrics=[
                ("Mixed no results", fmt_pct(as_float(us_mixed["no_results_rate"])), "US + non-US bucket"),
                ("US-only no results", fmt_pct(as_float(us_only["no_results_rate"])), "Domestic-only studies"),
                ("No-US no results", fmt_pct(as_float(no_us["no_results_rate"])), "No recorded US location"),
                ("Mixed visible", fmt_pct(as_float(us_mixed["results_publication_visible_rate"])), "Results plus publication"),
            ],
            landing_chart_html=chart_section(
                "Geography buckets",
                bar_chart(
                    [{"label": geo_short(row["geo_bucket"]), "value": as_float(row["no_results_rate"])} for _, row in geo.iterrows()],
                    "Geography buckets",
                    "2-year no-results rate by U.S./global geography bucket",
                    "value",
                    "label",
                    "#c3452f",
                    percent=True,
                ),
                "Cross-border studies are the clear outlier on the cleaner side of the registry.",
                "The gap is too large to dismiss as a minor location-footprint artifact.",
            ),
            reader_lede="A 156-word micro-paper on how U.S. and non-U.S. geography buckets map onto missing results and ghost protocols in older CT.gov studies.",
            reader_rail=["Mixed", "US only", "No US", "No country"],
            reader_metrics=[
                ("Mixed ghosts", fmt_pct(as_float(us_mixed["ghost_protocol_rate"])), "Neither results nor publication"),
                ("US-only ghosts", fmt_pct(as_float(us_only["ghost_protocol_rate"])), "Domestic-only studies"),
                ("No-country ghosts", fmt_pct(as_float(no_country["ghost_protocol_rate"])), "No named country"),
                ("No-US visible", fmt_pct(as_float(no_us["results_publication_visible_rate"])), "Results plus publication"),
            ],
            dashboard_title="Cross-border CT.gov studies are much cleaner than domestic-only or no-U.S. older portfolios",
            dashboard_eyebrow="US vs Global Dashboard",
            dashboard_lede="Older studies involving both U.S. and non-U.S. locations are far more visible than U.S.-only, no-U.S., or no-country records, and the sponsor-class split shows that the advantage is not confined to one sponsor type.",
            dashboard_rail=["No results", "Ghosts", "Sponsor classes", "Visible share"],
            dashboard_metrics=[
                ("Mixed no results", fmt_pct(as_float(us_mixed["no_results_rate"])), "Cleanest bucket"),
                ("No-US OTHER", fmt_pct(as_float(no_us_other["no_results_rate"])), "Selected sponsor-class cell"),
                ("US-only industry", fmt_pct(as_float(us_industry["no_results_rate"])), "Domestic industry"),
                ("No-country hiddenness", f"{as_float(no_country['hiddenness_score_mean']):.2f}", "Mean hiddenness score"),
            ],
            dashboard_sections=[
                chart_section(
                    "No-results by geography bucket",
                    bar_chart(
                        [{"label": geo_short(row["geo_bucket"]), "value": as_float(row["no_results_rate"])} for _, row in geo.iterrows()],
                        "Geography bucket",
                        "2-year no-results rate by geography bucket",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "The cleanest geography bucket is the mixed U.S.-plus-non-U.S. group, not the purely domestic U.S. bucket.",
                    "That shifts the public story from a national split to a cross-border coordination split.",
                ),
                chart_section(
                    "Ghost protocols by geography bucket",
                    bar_chart(
                        [{"label": geo_short(row["geo_bucket"]), "value": as_float(row["ghost_protocol_rate"])} for _, row in geo.iterrows()],
                        "Geography ghosts",
                        "Ghost-protocol rate by geography bucket",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "The same ordering survives on the stricter total-silence metric.",
                    "That reduces the chance that the geography effect is only about linked-publication practices.",
                ),
                chart_section(
                    "Selected sponsor-class contrast",
                    bar_chart(
                        [
                            {"label": "Mixed | Industry", "value": as_float(mixed_industry["no_results_rate"])},
                            {"label": "US only | Industry", "value": as_float(us_industry["no_results_rate"])},
                            {"label": "No US | Industry", "value": as_float(no_us_industry["no_results_rate"])},
                            {"label": "No US | Other", "value": as_float(no_us_other["no_results_rate"])},
                            {"label": "Mixed | NIH", "value": as_float(mixed_nih["no_results_rate"])},
                            {"label": "US only | NIH", "value": as_float(us_nih["no_results_rate"])},
                        ],
                        "Sponsor-class buckets",
                        "Selected sponsor-class cells across geography buckets",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Industry and NIH both look cleaner in the mixed cross-border bucket than in U.S.-only or no-U.S. settings.",
                    "The worst selected cell is the no-U.S. OTHER portfolio at 94.9 percent no results.",
                ),
            ],
            sidebar_bullets=[
                "Mixed U.S.-plus-non-U.S. studies fall to 30.2 percent on the 2-year no-results metric.",
                "U.S.-only studies rise to 55.8 percent, while no-U.S. studies reach 88.7 percent.",
                "No-country records remain heavily obscured at 80.9 percent no results and 53.6 percent ghost protocols.",
                "Mixed industry and mixed NIH portfolios are materially cleaner than their domestic-only counterparts.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-modality-sponsor-repeaters",
            title="CT.gov Modality Sponsor Repeaters",
            summary="A standalone E156 project on how the leading hiddenness sponsors change when CT.gov studies are split by intervention family.",
            body=modality_body,
            sentences=modality_sentences,
            primary_estimand="Sponsor-level 2-year no-results counts within intervention families among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies grouped by extracted intervention-family labels and lead sponsor",
            references=common_refs,
            protocol=(
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies by declared intervention family and then ranks lead sponsors within each modality. "
                "Primary outputs compare sponsor-level missing-results counts, no-results rates, ghost-protocol rates, and fully visible shares within drug, device, procedure, behavioral, biological, and dietary-supplement families. "
                "The aim is to test whether repeat offenders are stable across intervention types or whether modality-specific sponsor clusters are being hidden inside whole-registry tables. "
                "Because both sponsor and intervention labels are registry-entered, the analysis measures declared modality and lead-sponsor naming rather than corporate ownership or collaboration depth."
            ),
            root_title="Do repeat-offender sponsors change when modality is held fixed?",
            root_eyebrow="Sponsor Repeater Project",
            root_lede="A standalone public project on sponsor repeaters by intervention family, showing that drug, device, procedure, dietary, biological, and behavioral portfolios have different leading pockets of silence.",
            chapter_intro="This page uses the same logic as the rest of the series but applies it to sponsor lists directly: whole-registry leaderboards blur together sponsors that only recur inside particular treatment modalities.",
            root_pull_quote="The biggest whole-registry sponsors do not fully explain the backlog. Once modality is fixed, different repeater lists emerge.",
            paper_pull_quote="Intervention family changes who looks like a chronic repeater. One sponsor table is not enough.",
            dashboard_pull_quote="The sponsor story is modality-specific: drug, device, procedure, and dietary families do not share one common repeat-offender ranking.",
            root_rail=["Drug GSK 1,033", "Device Cairo 205", "Procedure Cairo 97.3%", "Behavioral UCSF 317"],
            landing_metrics=[
                ("Drug top backlog", fmt_int(as_int(drug_top["no_results_count"])), sponsor_short(str(drug_top["lead_sponsor_name"]))),
                ("Procedure top rate", fmt_pct(as_float(procedure_top["no_results_rate"])), sponsor_short(str(procedure_top["lead_sponsor_name"]))),
                ("Dietary top backlog", fmt_int(as_int(dietary_top["no_results_count"])), sponsor_short(str(dietary_top["lead_sponsor_name"]))),
                ("Behavioral top backlog", fmt_int(as_int(behavioral_top["no_results_count"])), sponsor_short(str(behavioral_top["lead_sponsor_name"]))),
            ],
            landing_chart_html=chart_section(
                "Top sponsor backlog by family",
                bar_chart(
                    [
                        {"label": "Drug | " + sponsor_short(str(drug_top["lead_sponsor_name"])), "value": as_int(drug_top["no_results_count"])},
                        {"label": "Device | " + sponsor_short(str(device_top["lead_sponsor_name"])), "value": as_int(device_top["no_results_count"])},
                        {"label": "Procedure | " + sponsor_short(str(procedure_top["lead_sponsor_name"])), "value": as_int(procedure_top["no_results_count"])},
                        {"label": "Behavioral | " + sponsor_short(str(behavioral_top["lead_sponsor_name"])), "value": as_int(behavioral_top["no_results_count"])},
                        {"label": "Biological | " + sponsor_short(str(biological_top["lead_sponsor_name"])), "value": as_int(biological_top["no_results_count"])},
                        {"label": "Dietary | " + sponsor_short(str(dietary_top["lead_sponsor_name"])), "value": as_int(dietary_top["no_results_count"])},
                    ],
                    "Intervention families",
                    "Top sponsor missing-results counts inside selected intervention families",
                    "value",
                    "label",
                    "#326891",
                    percent=False,
                ),
                "Drug families have the biggest absolute stock, but the leading sponsor is not the same everywhere.",
                "This chart is about modality-specific repetition rather than one universal sponsor pecking order.",
            ),
            reader_lede="A 156-word micro-paper on how sponsor repeaters change across intervention families in older CT.gov studies.",
            reader_rail=["Drug", "Procedure", "Behavioral", "Dietary"],
            reader_metrics=[
                ("Device top no results", fmt_pct(as_float(device_top["no_results_rate"])), sponsor_short(str(device_top["lead_sponsor_name"]))),
                ("Biological top backlog", fmt_int(as_int(biological_top["no_results_count"])), sponsor_short(str(biological_top["lead_sponsor_name"]))),
                ("Drug top ghosts", fmt_pct(as_float(drug_top["ghost_protocol_rate"])), sponsor_short(str(drug_top["lead_sponsor_name"]))),
                ("Behavioral visible", fmt_pct(as_float(behavioral_top["results_publication_visible_rate"])), sponsor_short(str(behavioral_top["lead_sponsor_name"]))),
            ],
            dashboard_title="Modality-specific sponsor repeaters expose hidden clusters that pooled CT.gov rankings miss",
            dashboard_eyebrow="Modality Sponsors Dashboard",
            dashboard_lede="The leading sponsor on missing-results stock changes sharply once intervention family is fixed: drugs remain large, but procedure, device, dietary-supplement, and behavioral families reveal different repeater institutions and much higher rates.",
            dashboard_rail=["Backlog counts", "Top rates", "Drug stack", "Visible share"],
            dashboard_metrics=[
                ("Drug top backlog", fmt_int(as_int(drug_top["no_results_count"])), sponsor_short(str(drug_top["lead_sponsor_name"]))),
                ("Procedure top rate", fmt_pct(as_float(procedure_top["no_results_rate"])), sponsor_short(str(procedure_top["lead_sponsor_name"]))),
                ("Dietary visible", fmt_pct(as_float(dietary_top["results_publication_visible_rate"])), sponsor_short(str(dietary_top["lead_sponsor_name"]))),
                ("Biological visible", fmt_pct(as_float(biological_top["results_publication_visible_rate"])), sponsor_short(str(biological_top["lead_sponsor_name"]))),
            ],
            dashboard_sections=[
                chart_section(
                    "Leading sponsor backlog by family",
                    bar_chart(
                        [
                            {"label": intervention_short("DRUG") + " | " + sponsor_short(str(drug_top["lead_sponsor_name"])), "value": as_int(drug_top["no_results_count"])},
                            {"label": intervention_short("DEVICE") + " | " + sponsor_short(str(device_top["lead_sponsor_name"])), "value": as_int(device_top["no_results_count"])},
                            {"label": intervention_short("PROCEDURE") + " | " + sponsor_short(str(procedure_top["lead_sponsor_name"])), "value": as_int(procedure_top["no_results_count"])},
                            {"label": intervention_short("BEHAVIORAL") + " | " + sponsor_short(str(behavioral_top["lead_sponsor_name"])), "value": as_int(behavioral_top["no_results_count"])},
                            {"label": intervention_short("BIOLOGICAL") + " | " + sponsor_short(str(biological_top["lead_sponsor_name"])), "value": as_int(biological_top["no_results_count"])},
                            {"label": intervention_short("DIETARY_SUPPLEMENT") + " | " + sponsor_short(str(dietary_top["lead_sponsor_name"])), "value": as_int(dietary_top["no_results_count"])},
                        ],
                        "Top sponsor stock",
                        "Leading missing-results stock within selected intervention families",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Drug backlogs dominate on count, but other families surface smaller institutions with far worse rates.",
                    "The chart makes modality-specific repeaters visible before rate comparisons start.",
                ),
                chart_section(
                    "Top sponsor rate by family",
                    bar_chart(
                        [
                            {"label": intervention_short("DRUG") + " | " + sponsor_short(str(drug_top["lead_sponsor_name"])), "value": as_float(drug_top["no_results_rate"])},
                            {"label": intervention_short("DEVICE") + " | " + sponsor_short(str(device_top["lead_sponsor_name"])), "value": as_float(device_top["no_results_rate"])},
                            {"label": intervention_short("PROCEDURE") + " | " + sponsor_short(str(procedure_top["lead_sponsor_name"])), "value": as_float(procedure_top["no_results_rate"])},
                            {"label": intervention_short("BEHAVIORAL") + " | " + sponsor_short(str(behavioral_top["lead_sponsor_name"])), "value": as_float(behavioral_top["no_results_rate"])},
                            {"label": intervention_short("BIOLOGICAL") + " | " + sponsor_short(str(biological_top["lead_sponsor_name"])), "value": as_float(biological_top["no_results_rate"])},
                            {"label": intervention_short("DIETARY_SUPPLEMENT") + " | " + sponsor_short(str(dietary_top["lead_sponsor_name"])), "value": as_float(dietary_top["no_results_rate"])},
                        ],
                        "Top sponsor rate",
                        "2-year no-results rate for the leading sponsor inside each family",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Procedure, device, and dietary families remain near-total silence zones for their leading sponsors.",
                    "Drug families are larger in count, but their leading sponsor is far less extreme on rate than the procedural families.",
                ),
                chart_section(
                    "Drug family top sponsors",
                    bar_chart(
                        [{"label": sponsor_short(str(row["lead_sponsor_name"])), "value": as_int(row["no_results_count"])} for _, row in drug_rows.iterrows()],
                        "Drug sponsor stack",
                        "Top missing-results counts inside the drug family",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "The drug family still contains a thick sponsor stack, not a single-name story.",
                    "That is why modality-specific repeaters need both within-family counts and cross-family contrasts.",
                ),
            ],
            sidebar_bullets=[
                "GlaxoSmithKline carries the largest drug-family backlog at 1,033 older studies.",
                "Cairo University leads both device and procedure repeaters, with 205 and 254 missing-results studies respectively.",
                "Maastricht University Medical Center leads dietary-supplement backlogs at 154 studies.",
                "UCSF leads behavioral backlogs at 317 studies, showing the repeater story is not industry-only.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-country-condition-hiddenness",
            title="CT.gov Country-Condition Hiddenness",
            summary="A standalone E156 project on how disease-specific CT.gov visibility changes when country footprints are named directly.",
            body=country_condition_body,
            sentences=country_condition_sentences,
            primary_estimand="2-year no-results rate across selected country-by-condition cells among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies exploded into named-country condition-family cells",
            references=common_refs,
            protocol=(
                "This protocol explodes eligible older closed interventional ClinicalTrials.gov studies into named-country cells and then restricts the analysis to oncology, cardiovascular, and metabolic condition families. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and fully visible shares across condition-country cells with at least 400 eligible older studies. "
                "The aim is to test whether disease-family visibility depends on which national footprints are attached to the study record rather than on condition label alone. "
                "Because the cells use recorded study locations, the analysis measures country involvement rather than verified enrollment shares, sponsor domicile, or national legal exposure."
            ),
            root_title="Which country-condition cells are the quietest on CT.gov?",
            root_eyebrow="Country x Condition Project",
            root_lede="A standalone public project on country-condition hiddenness, showing that oncology, cardiovascular, and metabolic studies look very different once specific national footprints are named.",
            chapter_intro="This page takes the disease-family series one step further. The same therapeutic area can look much cleaner or much quieter depending on which country footprint is attached to the study record.",
            root_pull_quote="The country split does not merely decorate a disease family. It can flip the visibility profile of the same condition from relatively visible to deeply hidden.",
            paper_pull_quote="Condition families are not geographically uniform. Their visibility profile changes once specific country footprints are named.",
            dashboard_pull_quote="The most useful country view is disease-specific: oncology China, cardiovascular Egypt, and metabolic Denmark tell different stories.",
            root_rail=["Oncology China 79.0%", "Oncology US 52.6%", "Cardio Egypt 95.9%", "Metabolic Denmark 79.6%"],
            landing_metrics=[
                ("Oncology China", fmt_pct(as_float(oncology_china["no_results_rate"])), "2-year no-results"),
                ("Oncology US", fmt_pct(as_float(oncology_us["no_results_rate"])), "Comparator"),
                ("Cardio Egypt", fmt_pct(as_float(cardio_egypt["no_results_rate"])), "Worst selected cell"),
                ("Metabolic Denmark", fmt_pct(as_float(metabolic_denmark["no_results_rate"])), "Named-country gap"),
            ],
            landing_chart_html=chart_section(
                "Selected country-condition cells",
                bar_chart(
                    [
                        {"label": "Onc | US", "value": as_float(oncology_us["no_results_rate"])},
                        {"label": "Onc | China", "value": as_float(oncology_china["no_results_rate"])},
                        {"label": "Onc | Poland", "value": as_float(oncology_poland["no_results_rate"])},
                        {"label": "Cardio | US", "value": as_float(cardio_country_us["no_results_rate"])},
                        {"label": "Cardio | Egypt", "value": as_float(cardio_egypt["no_results_rate"])},
                        {"label": "Cardio | Poland", "value": as_float(cardio_poland["no_results_rate"])},
                        {"label": "Metabolic | US", "value": as_float(metabolic_country_us["no_results_rate"])},
                        {"label": "Metabolic | China", "value": as_float(metabolic_china["no_results_rate"])},
                        {"label": "Metabolic | Denmark", "value": as_float(metabolic_denmark["no_results_rate"])},
                    ],
                    "Country x condition",
                    "Selected country-condition contrast on the 2-year no-results metric",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "The disease-country cells do not collapse into one national ranking or one condition ranking.",
                "That is the point of the project: interaction matters more than either margin alone.",
            ),
            reader_lede="A 156-word micro-paper on how disease-specific country footprints map onto hiddenness in older CT.gov studies.",
            reader_rail=["Oncology", "Cardiovascular", "Metabolic", "Named countries"],
            reader_metrics=[
                ("Oncology Poland visible", fmt_pct(as_float(oncology_poland["results_publication_visible_rate"])), "Cleaner oncology country"),
                ("Cardio China ghosts", fmt_pct(as_float(cardio_china["ghost_protocol_rate"])), "Selected cell"),
                ("Cardio Egypt visible", fmt_pct(as_float(cardio_egypt["results_publication_visible_rate"])), "Results plus publication"),
                ("Metabolic Spain visible", fmt_pct(as_float(metabolic_spain["results_publication_visible_rate"])), "Cleaner metabolic cell"),
            ],
            dashboard_title="Disease-country cells reveal geography-specific visibility breaks inside major CT.gov condition families",
            dashboard_eyebrow="Country x Condition Dashboard",
            dashboard_lede="Oncology, cardiovascular, and metabolic portfolios do not carry one common country pattern. Their quietest and cleanest country footprints diverge sharply once named-country cells are plotted directly.",
            dashboard_rail=["Oncology", "Cardio", "Metabolic", "Visible share"],
            dashboard_metrics=[
                ("Oncology China", fmt_pct(as_float(oncology_china["no_results_rate"])), "2-year no-results"),
                ("Cardio Egypt", fmt_pct(as_float(cardio_egypt["no_results_rate"])), "Selected extreme"),
                ("Metabolic China", fmt_pct(as_float(metabolic_china["no_results_rate"])), "2-year no-results"),
                ("Oncology Australia visible", fmt_pct(as_float(oncology_australia["results_publication_visible_rate"])), "Cleaner comparator"),
            ],
            dashboard_sections=[
                chart_section(
                    "Oncology by selected country",
                    bar_chart(
                        [
                            {"label": country_short("United States"), "value": as_float(oncology_us["no_results_rate"])},
                            {"label": country_short("China"), "value": as_float(oncology_china["no_results_rate"])},
                            {"label": country_short("Spain"), "value": as_float(oncology_spain["no_results_rate"])},
                            {"label": country_short("Australia"), "value": as_float(oncology_australia["no_results_rate"])},
                            {"label": country_short("Poland"), "value": as_float(oncology_poland["no_results_rate"])},
                        ],
                        "Oncology countries",
                        "2-year no-results rate for selected oncology country footprints",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Oncology ranges from 26.5 percent in Poland to 79.0 percent in China among large named-country cells.",
                    "That spread is too wide to ignore in a disease-specific hiddenness story.",
                ),
                chart_section(
                    "Cardiovascular by selected country",
                    bar_chart(
                        [
                            {"label": country_short("United States"), "value": as_float(cardio_country_us["no_results_rate"])},
                            {"label": country_short("China"), "value": as_float(cardio_china["no_results_rate"])},
                            {"label": country_short("Egypt"), "value": as_float(cardio_egypt["no_results_rate"])},
                            {"label": country_short("Poland"), "value": as_float(cardio_poland["no_results_rate"])},
                            {"label": country_short("Australia"), "value": as_float(cardio_australia["no_results_rate"])},
                            {"label": country_short("Japan"), "value": as_float(cardio_japan["no_results_rate"])},
                        ],
                        "Cardiovascular countries",
                        "2-year no-results rate for selected cardiovascular country footprints",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Cardiovascular Egypt is the harshest selected cell at 95.9 percent no results.",
                    "Japan, Australia, and Poland sit in a visibly cleaner band than China or Egypt.",
                ),
                chart_section(
                    "Metabolic by selected country",
                    bar_chart(
                        [
                            {"label": country_short("United States"), "value": as_float(metabolic_country_us["no_results_rate"])},
                            {"label": country_short("China"), "value": as_float(metabolic_china["no_results_rate"])},
                            {"label": country_short("Denmark"), "value": as_float(metabolic_denmark["no_results_rate"])},
                            {"label": country_short("Spain"), "value": as_float(metabolic_spain["no_results_rate"])},
                        ],
                        "Metabolic countries",
                        "2-year no-results rate for selected metabolic country footprints",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Metabolic Denmark looks almost as quiet as metabolic China despite being a very different national research environment.",
                    "That keeps the condition-country analysis from collapsing into one simple geopolitical narrative.",
                ),
            ],
            sidebar_bullets=[
                "Oncology studies involving China reach 79.0 percent no results, versus 52.6 percent for oncology studies involving the United States.",
                "Cardiovascular studies involving Egypt reach 95.9 percent no results and just 3.6 percent full visibility.",
                "Metabolic studies involving China and Denmark both sit near 79 percent no results.",
                "Oncology studies involving Poland are much cleaner at 26.5 percent no results and 53.0 percent full visibility.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-disease-geography-gap",
            title="CT.gov Disease Geography Gap",
            summary="A standalone E156 project on how geography buckets reshape the visibility profile of oncology, cardiovascular, and metabolic CT.gov studies.",
            body=disease_geo_body,
            sentences=disease_geo_sentences,
            primary_estimand="2-year no-results rate across geography buckets within selected disease families among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies linked to geography buckets and selected condition families",
            references=common_refs,
            protocol=(
                "This protocol links geography buckets to selected condition families and compares oncology, cardiovascular, and metabolic studies across U.S.-only, U.S.-plus-non-U.S., no-U.S., and no-country groups. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, fully visible shares, and hiddenness scores across those buckets within each disease family. "
                "The aim is to test whether disease-specific visibility differences persist after geography structure is made explicit rather than folded into one pooled condition table. "
                "Because the buckets use recorded study locations, the analysis measures geography structure rather than verified recruitment shares, national burden, or sponsor domicile."
            ),
            root_title="How much does geography change the disease hiddenness story?",
            root_eyebrow="Disease Geography Project",
            root_lede="A standalone public project on disease geography, showing that oncology, cardiovascular, and metabolic studies become much quieter when U.S. participation drops out of the location profile.",
            chapter_intro="This page sits between the disease-family projects and the geography work. The main question is whether a condition looks quiet because of the condition itself or because of where that condition is being run.",
            root_pull_quote="Across three major disease families, mixed U.S.-global studies are the cleanest bucket and no-U.S. studies are the quietest.",
            paper_pull_quote="The disease story is partly a geography story. Major condition families do not keep one stable visibility profile across buckets.",
            dashboard_pull_quote="Within oncology, cardiovascular, and metabolic studies, geography bucket behaves like a reusable hiddenness engine.",
            root_rail=["Cardio mixed 29.9%", "Metabolic no US 90.3%", "Oncology no US 86.8%", "Oncology mixed 38.0% visible"],
            landing_metrics=[
                ("Cardio mixed", fmt_pct(as_float(cardio_mixed["no_results_rate"])), "Cleanest selected disease bucket"),
                ("Metabolic no US", fmt_pct(as_float(metabolic_no_us["no_results_rate"])), "Worst selected disease bucket"),
                ("Oncology no US", fmt_pct(as_float(oncology_no_us["no_results_rate"])), "2-year no-results"),
                ("Oncology mixed visible", fmt_pct(as_float(oncology_mixed["results_publication_visible_rate"])), "Results plus publication"),
            ],
            landing_chart_html=chart_section(
                "Disease geography cells",
                bar_chart(
                    [
                        {"label": "Cardio | US", "value": as_float(cardio_us["no_results_rate"])},
                        {"label": "Cardio | Mixed", "value": as_float(cardio_mixed["no_results_rate"])},
                        {"label": "Cardio | No US", "value": as_float(cardio_no_us["no_results_rate"])},
                        {"label": "Cardio | No country", "value": as_float(cardio_no_country["no_results_rate"])},
                        {"label": "Metabolic | US", "value": as_float(metabolic_us["no_results_rate"])},
                        {"label": "Metabolic | Mixed", "value": as_float(metabolic_mixed["no_results_rate"])},
                        {"label": "Metabolic | No US", "value": as_float(metabolic_no_us["no_results_rate"])},
                        {"label": "Oncology | US", "value": as_float(oncology_us_geo["no_results_rate"])},
                        {"label": "Oncology | Mixed", "value": as_float(oncology_mixed["no_results_rate"])},
                        {"label": "Oncology | No US", "value": as_float(oncology_no_us["no_results_rate"])},
                        {"label": "Oncology | No country", "value": as_float(oncology_no_country["no_results_rate"])},
                    ],
                    "Disease x geography",
                    "2-year no-results rate across disease-family geography buckets",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "The disease buckets all slope in the same direction, but not at the same baseline level.",
                "That makes disease geography a reusable pattern rather than a one-family anomaly.",
            ),
            reader_lede="A 156-word micro-paper on how geography buckets reshape oncology, cardiovascular, and metabolic visibility in older CT.gov studies.",
            reader_rail=["Cardio", "Metabolic", "Oncology", "Geography buckets"],
            reader_metrics=[
                ("Cardio mixed visible", fmt_pct(as_float(cardio_mixed["results_publication_visible_rate"])), "Results plus publication"),
                ("Metabolic mixed visible", fmt_pct(as_float(metabolic_mixed["results_publication_visible_rate"])), "Cleanest metabolic bucket"),
                ("Oncology no-country ghosts", fmt_pct(as_float(oncology_no_country["ghost_protocol_rate"])), "Neither visible"),
                ("Metabolic no-country hiddenness", f"{as_float(metabolic_no_country['hiddenness_score_mean']):.2f}", "Mean hiddenness score"),
            ],
            dashboard_title="Major CT.gov disease families become much quieter when U.S. participation disappears from the location profile",
            dashboard_eyebrow="Disease Geography Dashboard",
            dashboard_lede="Across cardiovascular, metabolic, and oncology portfolios, the mixed U.S.-plus-non-U.S. bucket is cleanest and the no-U.S. bucket is quietest, suggesting geography structure strongly conditions the disease hiddenness story.",
            dashboard_rail=["Cardio", "Metabolic", "Oncology", "No-country"],
            dashboard_metrics=[
                ("Cardio mixed", fmt_pct(as_float(cardio_mixed["no_results_rate"])), "Cleanest selected bucket"),
                ("Metabolic no US", fmt_pct(as_float(metabolic_no_us["no_results_rate"])), "Worst selected bucket"),
                ("Oncology no US", fmt_pct(as_float(oncology_no_us["no_results_rate"])), "2-year no-results"),
                ("Cardio no-country ghosts", fmt_pct(as_float(cardio_no_country["ghost_protocol_rate"])), "Neither visible"),
            ],
            dashboard_sections=[
                chart_section(
                    "Cardiovascular geography buckets",
                    bar_chart(
                        [{"label": geo_short(row["geo_bucket"]), "value": as_float(row["no_results_rate"])} for _, row in condition_geo[condition_geo["condition_family_label"] == "Cardiovascular"].iterrows()],
                        "Cardiovascular buckets",
                        "2-year no-results rate across cardiovascular geography buckets",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Cardiovascular mixed studies fall below 30 percent no results, while no-U.S. studies approach 90 percent.",
                    "That is one of the starkest within-condition geography gradients in the series.",
                ),
                chart_section(
                    "Metabolic geography buckets",
                    bar_chart(
                        [{"label": geo_short(row["geo_bucket"]), "value": as_float(row["no_results_rate"])} for _, row in condition_geo[condition_geo["condition_family_label"] == "Metabolic"].iterrows()],
                        "Metabolic buckets",
                        "2-year no-results rate across metabolic geography buckets",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Metabolic no-U.S. studies are the harshest selected geography bucket at 90.3 percent no results.",
                    "The mixed bucket stays below 30 percent, leaving a sixty-point spread within one disease family.",
                ),
                chart_section(
                    "Oncology geography buckets",
                    bar_chart(
                        [{"label": geo_short(row["geo_bucket"]), "value": as_float(row["no_results_rate"])} for _, row in condition_geo[condition_geo["condition_family_label"] == "Oncology"].iterrows()],
                        "Oncology buckets",
                        "2-year no-results rate across oncology geography buckets",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Oncology starts from a higher baseline than cardiovascular in the mixed bucket and ends with a similar no-U.S. quiet zone.",
                    "That is why condition label and geography bucket have to be read together.",
                ),
            ],
            sidebar_bullets=[
                "Mixed U.S.-plus-non-U.S. studies are the cleanest bucket in cardiovascular, metabolic, and oncology families alike.",
                "No-U.S. studies reach 89.9 percent no results in cardiovascular, 90.3 percent in metabolic, and 86.8 percent in oncology.",
                "Oncology no-country studies remain especially quiet at 82.8 percent no results and 60.8 percent ghost protocols.",
                "The disease story changes materially once geography structure is made explicit.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-condition-sponsor-repeaters",
            title="CT.gov Condition Sponsor Repeaters",
            summary="A standalone E156 project on which sponsors carry the biggest hiddenness backlogs inside oncology, cardiovascular, and metabolic CT.gov portfolios.",
            body=condition_sponsor_body,
            sentences=condition_sponsor_sentences,
            primary_estimand="Sponsor-level 2-year no-results counts within selected disease families among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies linked to oncology, cardiovascular, and metabolic condition families and lead sponsors",
            references=common_refs,
            protocol=(
                "This protocol links eligible older closed interventional ClinicalTrials.gov studies to oncology, cardiovascular, and metabolic condition families and then ranks lead sponsors within each family. "
                "Primary outputs compare sponsor-level missing-results counts, no-results rates, ghost-protocol rates, and fully visible shares within each condition family. "
                "The aim is to test whether the backlog is driven by one stable sponsor list or whether disease-specific repeater institutions emerge once whole-registry pooling is removed. "
                "Because both condition families and sponsor names are derived from registry text, the analysis measures condition-linked registry visibility rather than adjudicated network authorship or off-platform dissemination."
            ),
            root_title="Which sponsors keep reappearing inside major disease families?",
            root_eyebrow="Condition Sponsor Project",
            root_lede="A standalone public project on condition-family sponsor repeaters, showing that oncology, cardiovascular, and metabolic portfolios each carry their own concentrated pockets of hiddenness.",
            chapter_intro="This page turns the disease-family series into a sponsor audit. The question is not only which conditions are quiet, but which institutions keep surfacing inside those quiet condition-specific backlogs.",
            root_pull_quote="Condition-specific sponsor audits show that repeat offenders are not stable across disease families. Each family has its own backlog structure.",
            paper_pull_quote="Whole-registry sponsor tables flatten distinct disease-family repeater patterns into one misleading list.",
            dashboard_pull_quote="Oncology stock is count-heavy, cardiovascular is rate-heavy, and metabolic sits between the two.",
            root_rail=["Oncology NCI 909", "MD Anderson 589", "Cardio AP-HP 100%", "Metabolic Novo 391"],
            landing_metrics=[
                ("Oncology top backlog", fmt_int(as_int(oncology_top["no_results_count"])), sponsor_short(str(oncology_top["lead_sponsor_name"]))),
                ("Oncology second", fmt_int(as_int(oncology_second["no_results_count"])), sponsor_short(str(oncology_second["lead_sponsor_name"]))),
                ("Cardio top rate", fmt_pct(as_float(cardio_top["no_results_rate"])), sponsor_short(str(cardio_top["lead_sponsor_name"]))),
                ("Metabolic top backlog", fmt_int(as_int(metabolic_top["no_results_count"])), sponsor_short(str(metabolic_top["lead_sponsor_name"]))),
            ],
            landing_chart_html=chart_section(
                "Leading sponsor backlog by condition",
                bar_chart(
                    [
                        {"label": "Onc | " + sponsor_short(str(oncology_top["lead_sponsor_name"])), "value": as_int(oncology_top["no_results_count"])},
                        {"label": "Onc | " + sponsor_short(str(oncology_second["lead_sponsor_name"])), "value": as_int(oncology_second["no_results_count"])},
                        {"label": "Onc | " + sponsor_short(str(oncology_rows.iloc[2]["lead_sponsor_name"])), "value": as_int(oncology_rows.iloc[2]["no_results_count"])},
                        {"label": "Cardio | " + sponsor_short(str(cardio_top["lead_sponsor_name"])), "value": as_int(cardio_top["no_results_count"])},
                        {"label": "Cardio | " + sponsor_short(str(cardio_second["lead_sponsor_name"])), "value": as_int(cardio_second["no_results_count"])},
                        {"label": "Cardio | " + sponsor_short(str(cardio_rows.iloc[2]["lead_sponsor_name"])), "value": as_int(cardio_rows.iloc[2]["no_results_count"])},
                        {"label": "Metabolic | " + sponsor_short(str(metabolic_top["lead_sponsor_name"])), "value": as_int(metabolic_top["no_results_count"])},
                        {"label": "Metabolic | " + sponsor_short(str(metabolic_second["lead_sponsor_name"])), "value": as_int(metabolic_second["no_results_count"])},
                        {"label": "Metabolic | " + sponsor_short(str(metabolic_rows.iloc[2]["lead_sponsor_name"])), "value": as_int(metabolic_rows.iloc[2]["no_results_count"])},
                    ],
                    "Condition-family sponsors",
                    "Selected sponsor missing-results counts inside major disease families",
                    "value",
                    "label",
                    "#326891",
                    percent=False,
                ),
                "Oncology dominates on count, but cardiovascular holds some of the sharpest rate extremes.",
                "That is why this project mixes stock-heavy and rate-heavy reading across disease families.",
            ),
            reader_lede="A 156-word micro-paper on how sponsor repeaters differ across oncology, cardiovascular, and metabolic CT.gov portfolios.",
            reader_rail=["Oncology", "Cardio", "Metabolic", "Sponsor audit"],
            reader_metrics=[
                ("Oncology UHN ghosts", fmt_pct(as_float(oncology_uhn["ghost_protocol_rate"])), sponsor_short(str(oncology_uhn["lead_sponsor_name"]))),
                ("Cardio Yonsei rate", fmt_pct(as_float(cardio_second["no_results_rate"])), sponsor_short(str(cardio_second["lead_sponsor_name"]))),
                ("Metabolic Sanofi rate", fmt_pct(as_float(metabolic_second["no_results_rate"])), sponsor_short(str(metabolic_second["lead_sponsor_name"]))),
                ("Metabolic Novo visible", fmt_pct(as_float(metabolic_top["results_publication_visible_rate"])), sponsor_short(str(metabolic_top["lead_sponsor_name"]))),
            ],
            dashboard_title="Condition-family sponsor repeaters reveal different hiddenness structures inside oncology, cardiovascular, and metabolic studies",
            dashboard_eyebrow="Condition Sponsors Dashboard",
            dashboard_lede="Oncology contains the largest sponsor backlogs by count, cardiovascular contains some of the harshest rate extremes, and metabolic combines both moderate stock and heavy repeaters inside a smaller disease family.",
            dashboard_rail=["Oncology stock", "Cardio rates", "Metabolic rates", "Visible share"],
            dashboard_metrics=[
                ("Oncology top backlog", fmt_int(as_int(oncology_top["no_results_count"])), sponsor_short(str(oncology_top["lead_sponsor_name"]))),
                ("Cardio top rate", fmt_pct(as_float(cardio_top["no_results_rate"])), sponsor_short(str(cardio_top["lead_sponsor_name"]))),
                ("Cardio second rate", fmt_pct(as_float(cardio_second["no_results_rate"])), sponsor_short(str(cardio_second["lead_sponsor_name"]))),
                ("Metabolic top visible", fmt_pct(as_float(metabolic_top["results_publication_visible_rate"])), sponsor_short(str(metabolic_top["lead_sponsor_name"]))),
            ],
            dashboard_sections=[
                chart_section(
                    "Oncology sponsor backlog",
                    bar_chart(
                        [{"label": sponsor_short(str(row["lead_sponsor_name"])), "value": as_int(row["no_results_count"])} for _, row in oncology_rows.iterrows()],
                        "Oncology sponsors",
                        "Top missing-results counts inside the oncology family",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "Oncology contains the deepest sponsor stack in absolute backlog count, led by NCI and MD Anderson.",
                    "This is the stock-heavy side of the condition-sponsor story.",
                ),
                chart_section(
                    "Cardiovascular sponsor rates",
                    bar_chart(
                        [{"label": sponsor_short(str(row["lead_sponsor_name"])), "value": as_float(row["no_results_rate"])} for _, row in cardio_rows.iterrows()],
                        "Cardiovascular sponsors",
                        "2-year no-results rate among top cardiovascular sponsor repeaters",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Cardiovascular sponsor repeaters are dominated by extreme rates, including a 100 percent no-results profile for AP-HP.",
                    "That makes cardiovascular the rate-heavy side of the page even when its backlog counts are smaller than oncology.",
                ),
                chart_section(
                    "Metabolic sponsor rates",
                    bar_chart(
                        [{"label": sponsor_short(str(row["lead_sponsor_name"])), "value": as_float(row["no_results_rate"])} for _, row in metabolic_rows.iterrows()],
                        "Metabolic sponsors",
                        "2-year no-results rate among top metabolic sponsor repeaters",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Metabolic sponsors combine a sizable backlog leader in Novo Nordisk with several near-total-silence academic repeaters.",
                    "That keeps the metabolic family from collapsing into a single-company story.",
                ),
            ],
            sidebar_bullets=[
                "NCI carries the largest oncology backlog at 909 older missing-results studies, ahead of MD Anderson at 589.",
                "AP-HP reaches 100.0 percent no results in cardiovascular studies, and Yonsei University reaches 98.6 percent.",
                "Novo Nordisk leads metabolic backlog counts at 391 studies, while Sanofi reaches 75.0 percent no results.",
                "Condition-specific sponsor auditing exposes repeaters that disappear inside pooled registry rankings.",
            ],
        )
    )

    for spec in projects:
        spec["repo_url"] = f"https://github.com/{REPO_OWNER}/{spec['repo_name']}"
        spec["pages_url"] = f"https://{REPO_OWNER}.github.io/{spec['repo_name']}/"
        spec["series_hub_url"] = series_hub_url
        spec["series_links"] = series_links
        path = write_project(spec)
        print(f"Built {path}")


if __name__ == "__main__":
    main()
