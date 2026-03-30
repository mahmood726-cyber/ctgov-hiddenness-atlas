#!/usr/bin/env python3
"""Build wave-seven standalone CT.gov projects from country repeaters, U.S. presence classes, and industry family audits."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct
from build_split_projects import chart_section, sentence_bundle, write_project

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

REPAIR_MAP = {
    "Assistance Publique - HÃ´pitaux de Paris": "Assistance Publique - Hôpitaux de Paris",
    "Assistance Publique - H�pitaux de Paris": "Assistance Publique - Hôpitaux de Paris",
    "SociÃ©tÃ© des Produits NestlÃ© (SPN)": "Société des Produits Nestlé (SPN)",
    "Soci�t� des Produits Nestl� (SPN)": "Société des Produits Nestlé (SPN)",
}

SPONSOR_SHORT = {
    "Mayo Clinic": "Mayo",
    "National Cancer Institute (NCI)": "NCI",
    "M.D. Anderson Cancer Center": "MD Anderson",
    "Memorial Sloan Kettering Cancer Center": "MSKCC",
    "University of California, San Francisco": "UCSF",
    "Massachusetts General Hospital": "MGH",
    "Sun Yat-sen University": "Sun Yat-sen",
    "Jiangsu HengRui Medicine Co., Ltd.": "Jiangsu HengRui",
    "Cairo University": "Cairo U",
    "Ain Shams University": "Ain Shams",
    "Assiut University": "Assiut",
    "Hoffmann-La Roche": "Roche",
    "Astellas Pharma Inc": "Astellas",
    "Novartis Pharmaceuticals": "Novartis",
    "Children's Oncology Group": "COG",
    "GlaxoSmithKline": "GSK",
    "Boehringer Ingelheim": "Boehringer",
    "AstraZeneca": "AstraZeneca",
    "Abbott Medical Devices": "Abbott",
    "Boston Scientific Corporation": "Boston Scientific",
    "Sanofi Pasteur, a Sanofi Company": "Sanofi Pasteur",
    "Merck Sharp & Dohme LLC": "MSD",
    "Société des Produits Nestlé (SPN)": "Nestlé SPN",
}

COUNTRY_SHORT = {
    "United States": "US",
    "Australia": "Australia",
    "China": "China",
    "Egypt": "Egypt",
    "Poland": "Poland",
    "Japan": "Japan",
    "Germany": "Germany",
    "United Kingdom": "UK",
    "Canada": "Canada",
    "France": "France",
}


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


def short_sponsor(name: str) -> str:
    clean_name = clean_text(name)
    return SPONSOR_SHORT.get(clean_name, clean_name)


def short_country(name: str) -> str:
    clean_name = clean_text(name)
    return COUNTRY_SHORT.get(clean_name, clean_name)


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
    country_repeaters = load_csv("selected_country_sponsor_repeaters_top_older_2y.csv")
    country_classes = load_csv("selected_country_sponsor_class_visibility_older_2y.csv")
    us_presence = load_csv("us_presence_visibility_older_2y.csv")
    us_presence_class = load_csv("us_presence_sponsor_class_visibility_older_2y.csv")
    industry_intervention = load_csv("industry_intervention_visibility_older_2y.csv")
    industry_repeaters = load_csv("industry_intervention_sponsor_top_backlog_older_2y.csv")
    industry_geo = load_csv("industry_geo_visibility_older_2y.csv")
    industry_country = load_csv("industry_country_visibility_older_2y.csv")

    us_top = row_for(country_repeaters, "country", "United States")
    china_top = row_for(country_repeaters, "country", "China")
    egypt_top = row_for(country_repeaters, "country", "Egypt")
    poland_top = row_for(country_repeaters, "country", "Poland")
    australia_top = row_for(country_repeaters, "country", "Australia")
    japan_top = row_for(country_repeaters, "country", "Japan")

    china_other = row_for_pair(country_classes, "country", "China", "lead_sponsor_class", "OTHER")
    china_industry = row_for_pair(country_classes, "country", "China", "lead_sponsor_class", "INDUSTRY")
    egypt_other = row_for_pair(country_classes, "country", "Egypt", "lead_sponsor_class", "OTHER")
    egypt_industry = row_for_pair(country_classes, "country", "Egypt", "lead_sponsor_class", "INDUSTRY")
    poland_other = row_for_pair(country_classes, "country", "Poland", "lead_sponsor_class", "OTHER")
    poland_industry = row_for_pair(country_classes, "country", "Poland", "lead_sponsor_class", "INDUSTRY")
    australia_other = row_for_pair(country_classes, "country", "Australia", "lead_sponsor_class", "OTHER")
    australia_industry = row_for_pair(country_classes, "country", "Australia", "lead_sponsor_class", "INDUSTRY")

    any_us = row_for(us_presence, "us_presence", "Any US")
    no_us = row_for(us_presence, "us_presence", "No US")
    no_country = row_for(us_presence, "us_presence", "No named country")
    any_us_industry = row_for_pair(us_presence_class, "us_presence", "Any US", "lead_sponsor_class", "INDUSTRY")
    no_us_industry = row_for_pair(us_presence_class, "us_presence", "No US", "lead_sponsor_class", "INDUSTRY")
    no_country_industry = row_for_pair(us_presence_class, "us_presence", "No named country", "lead_sponsor_class", "INDUSTRY")
    any_us_other = row_for_pair(us_presence_class, "us_presence", "Any US", "lead_sponsor_class", "OTHER")
    no_us_other = row_for_pair(us_presence_class, "us_presence", "No US", "lead_sponsor_class", "OTHER")
    any_us_nih = row_for_pair(us_presence_class, "us_presence", "Any US", "lead_sponsor_class", "NIH")
    no_us_nih = row_for_pair(us_presence_class, "us_presence", "No US", "lead_sponsor_class", "NIH")

    drug_family = row_for(industry_intervention, "intervention_type", "DRUG")
    dietary_family = row_for(industry_intervention, "intervention_type", "DIETARY_SUPPLEMENT")
    device_family = row_for(industry_intervention, "intervention_type", "DEVICE")
    procedure_family = row_for(industry_intervention, "intervention_type", "PROCEDURE")
    biological_family = row_for(industry_intervention, "intervention_type", "BIOLOGICAL")
    drug_rows = top_rows(industry_repeaters, "intervention_type", "DRUG", 6)
    device_rows = top_rows(industry_repeaters, "intervention_type", "DEVICE", 5)
    dietary_rows = top_rows(industry_repeaters, "intervention_type", "DIETARY_SUPPLEMENT", 5)
    mixed_industry = row_for(industry_geo, "geo_bucket", "US + non-US")
    no_us_industry_geo = row_for(industry_geo, "geo_bucket", "No US")
    us_only_industry_geo = row_for(industry_geo, "geo_bucket", "US only")
    top_industry_countries = industry_country.head(8).copy()

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
    ]

    series_seed = [
        ("ctgov-industry-disclosure-gap", "CT.gov Industry Disclosure Gap", "Industry-focused missing-results stock, sponsor backlogs, and structural sparsity inside CT.gov.", "Industry"),
        ("ctgov-sponsor-class-hiddenness", "CT.gov Sponsor-Class Hiddenness", "Sponsor-class comparisons on rate, stock, and structural hiddenness rather than one flattened ranking.", "Sponsor Classes"),
        ("ctgov-phase-reporting-gap", "CT.gov Phase Reporting Gap", "Phase-by-phase disclosure gaps showing how silence changes along the development pathway.", "Phases"),
        ("ctgov-structural-missingness", "CT.gov Structural Missingness", "Field-level missingness across publication links, IPD statements, descriptions, and locations.", "Structural"),
        ("ctgov-evidence-visibility-gap", "CT.gov Evidence Visibility Gap", "Results-plus-publication visibility states showing how many older trials are fully visible, partly visible, or ghosted.", "Visibility"),
        ("ctgov-completion-cohort-debt", "CT.gov Completion Cohort Debt", "Completion-era reporting debt showing how older eligible cohorts drift on no-results and ghost-protocol rates.", "Cohorts"),
        ("ctgov-condition-hiddenness-map", "CT.gov Condition Hiddenness Map", "Keyword-classified therapeutic-area hiddenness mapping across common condition families.", "Conditions"),
        ("ctgov-sponsor-backlog-concentration", "CT.gov Sponsor Backlog Concentration", "Concentration and inequality analysis showing how much unresolved stock sits inside a thin sponsor slice.", "Concentration"),
        ("ctgov-rule-era-reporting-gap", "CT.gov Rule-Era Reporting Gap", "Policy-era comparisons across pre-FDAAA, FDAAA, and later CT.gov completion cohorts.", "Rule Eras"),
        ("ctgov-publication-undercount-audit", "CT.gov Publication Undercount Audit", "Sample-based external PubMed NCT audit testing how often CT.gov no-link records hide an external paper trail.", "PubMed Audit"),
        ("ctgov-oncology-hiddenness", "CT.gov Oncology Hiddenness", "Oncology-specific CT.gov hiddenness showing where cancer-trial stock, phases, and sponsors still go quiet.", "Oncology"),
        ("ctgov-cardiovascular-hiddenness", "CT.gov Cardiovascular Hiddenness", "Cardiovascular CT.gov hiddenness showing how heart and vascular studies remain quiet across major phases and sponsors.", "Cardiovascular"),
        ("ctgov-metabolic-hiddenness", "CT.gov Metabolic Hiddenness", "Metabolic CT.gov hiddenness across obesity, diabetes, and related trial portfolios with large late-phase and NA stock.", "Metabolic"),
        ("ctgov-enrollment-size-gap", "CT.gov Enrollment-Size Gap", "Enrollment-size gradients showing how older small trials remain much quieter than larger registered studies.", "Size"),
        ("ctgov-geography-scale-visibility", "CT.gov Geography-Scale Visibility", "Site and country footprint analysis showing how larger trial geographies map onto much better public visibility.", "Geography"),
        ("ctgov-design-purpose-hiddenness", "CT.gov Design-Purpose Hiddenness", "Primary-purpose and allocation analysis showing which trial intents remain most obscured on CT.gov.", "Purpose"),
        ("ctgov-completion-delay-debt", "CT.gov Completion-Delay Debt", "Registration-to-completion delay analysis showing short-cycle studies carry the heaviest reporting debt.", "Delay"),
        ("ctgov-trial-architecture-gap", "CT.gov Trial-Architecture Gap", "Arm-count and intervention-count analysis showing simpler trial architectures are often the quietest.", "Architecture"),
        ("ctgov-intervention-type-gap", "CT.gov Intervention-Type Gap", "Intervention-family analysis showing which declared treatment modalities remain quietest on older CT.gov records.", "Interventions"),
        ("ctgov-country-reporting-map", "CT.gov Country Reporting Map", "Named-country visibility analysis showing large geographic divides in older CT.gov reporting debt.", "Countries"),
        ("ctgov-stopped-trial-disclosure-gap", "CT.gov Stopped-Trial Disclosure Gap", "Final-status analysis showing how withdrawn, suspended, and terminated studies remain structurally quieter than completed trials.", "Stopped"),
        ("ctgov-outcome-density-gap", "CT.gov Outcome-Density Gap", "Outcome-count and outcome-description analysis showing sparse protocols are often the quietest CT.gov segment.", "Outcomes"),
        ("ctgov-actual-field-discipline", "CT.gov Actual-Field Discipline", "Closed-study actual-field analysis showing missing actual dates and counts are a strong warning sign for opacity.", "Actual Fields"),
        ("ctgov-us-vs-global-gap", "CT.gov U.S. Versus Global Gap", "Geography-bucket analysis showing how U.S.-only, mixed, and non-U.S. portfolios diverge sharply on visibility.", "US vs Global"),
        ("ctgov-modality-sponsor-repeaters", "CT.gov Modality Sponsor Repeaters", "Intervention-family sponsor audit showing that repeat offenders change sharply once modality is held fixed.", "Modality Sponsors"),
        ("ctgov-country-condition-hiddenness", "CT.gov Country-Condition Hiddenness", "Country-by-condition splits showing how disease-specific visibility changes once specific national footprints are named.", "Country x Condition"),
        ("ctgov-disease-geography-gap", "CT.gov Disease Geography Gap", "Disease-family geography buckets showing how oncology, cardiovascular, and metabolic studies diverge by U.S. participation.", "Disease Geography"),
        ("ctgov-condition-sponsor-repeaters", "CT.gov Condition Sponsor Repeaters", "Condition-family sponsor audit showing who carries the biggest hiddenness stock within oncology, cardiovascular, and metabolic studies.", "Condition Sponsors"),
        ("ctgov-country-sponsor-repeaters", "CT.gov Country Sponsor Repeaters", "Country-linked sponsor audit showing how leading repeaters differ across U.S., China, Egypt, Poland, Australia, and Japan study footprints.", "Country Sponsors"),
        ("ctgov-us-vs-exus-sponsor-classes", "CT.gov U.S. Versus Ex-U.S. Sponsor Classes", "U.S.-presence sponsor-class analysis showing how any-U.S. and no-U.S. portfolios diverge sharply on hiddenness.", "US vs Ex-US"),
        ("ctgov-industry-family-repeaters", "CT.gov Industry Family Repeaters", "Industry-by-intervention audit showing that repeat-offender sponsors change sharply once modality and geography are held fixed.", "Industry Families"),
    ]
    series_links = [
        {"repo_name": repo_name, "title": title, "summary": summary, "short_title": short_title, "pages_url": f"https://{REPO_OWNER}.github.io/{repo_name}/"}
        for repo_name, title, summary, short_title in series_seed
    ]
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    country_body, country_sentences = sentence_bundle([
        ("Question", "Which sponsors hold the largest missing-results stock inside country-linked CT.gov portfolios?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and ranked lead sponsors within selected country-linked portfolios."),
        ("Method", "The project compares sponsor-level missing-results counts, no-results rates, ghost-protocol rates, and visible shares across United States, China, Egypt, Poland, Australia, and Japan footprints."),
        ("Primary result", "In United States-linked studies, Mayo Clinic carried the largest missing-results stock at 927 studies, while Sun Yat-sen University led China with 235 and Cairo University led Egypt with 968."),
        ("Secondary result", "Poland was cleaner, with Sanofi at 47.5 percent no results and Hoffmann-La Roche at only 59 missing-results studies, while Australia and Japan also sat below China or Egypt on rate."),
        ("Interpretation", "Country-linked sponsor repeaters therefore differ sharply across national footprints, meaning the same registry backlog resolves into different institutional stories once geography is named."),
        ("Boundary", "Country-linked sponsor tables reflect recorded study locations rather than sponsor domicile, enrollment shares, or national legal exposure."),
    ])
    us_body, us_sentences = sentence_bundle([
        ("Question", "How different do sponsor-class reporting gaps look once older CT.gov studies are collapsed into any-U.S., no-U.S., and no-country buckets instead of a longer geography table?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and grouped them by U.S. presence using recorded country locations."),
        ("Method", "The project compares two-year no-results rates, ghost-protocol rates, visible shares, and sponsor-class contrasts across any-U.S., no-U.S., and no-country portfolios."),
        ("Primary result", "Any-U.S. studies showed a 52.1 percent no-results rate, versus 88.7 percent for no-U.S. studies and 80.9 percent for studies with no named country."),
        ("Secondary result", "Within no-U.S. studies, OTHER reached 94.9 percent no results and industry 70.9 percent, while any-U.S. industry fell to 45.5 percent and any-U.S. NIH to 52.3 percent."),
        ("Interpretation", "U.S. presence therefore behaves like a divider across sponsor classes, and the ex-U.S. backlog is much quieter than the any-U.S. registry surface."),
        ("Boundary", "U.S.-presence buckets reflect recorded study locations rather than verified enrollment shares, sponsor domicile, or legal obligations."),
    ])
    industry_body, industry_sentences = sentence_bundle([
        ("Question", "Which industry sponsors keep reappearing once older CT.gov studies are split by intervention family rather than treated as one pooled industry backlog?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and isolated industry-sponsored records with intervention families and country locations."),
        ("Method", "The project compares sponsor-level missing-results counts, no-results rates, ghost-protocol rates, and geography contrasts across drug, device, procedure, biological, and dietary-supplement industry portfolios."),
        ("Primary result", "In drug studies, GlaxoSmithKline carried 1,033 missing-results studies, ahead of Boehringer Ingelheim at 847 and AstraZeneca at 845."),
        ("Secondary result", "Industry procedure studies were smaller but still uneven, while industry no-results rates rose from 27.3 percent in mixed U.S.-plus-non-U.S. portfolios to 70.9 percent in no-U.S. portfolios and 65.9 percent in selected no-country records."),
        ("Interpretation", "Industry hiddenness therefore depends strongly on modality and geography, so a pooled industry leaderboard understates where backlog concentrates most severely."),
        ("Boundary", "Industry, sponsor, and intervention labels are registry-entered fields rather than audited corporate, legal, or therapeutic classifications."),
    ])

    projects: list[dict[str, object]] = []
    projects.append(
        make_spec(
            repo_name="ctgov-country-sponsor-repeaters",
            title="CT.gov Country Sponsor Repeaters",
            summary="A standalone E156 project on how leading sponsor repeaters differ sharply across U.S., China, Egypt, Poland, Australia, and Japan study footprints.",
            body=country_body,
            sentences=country_sentences,
            primary_estimand="Sponsor-level missing-results counts within selected country-linked older CT.gov portfolios",
            data_note="249,507 eligible older closed interventional studies exploded into selected country-linked sponsor portfolios",
            references=common_refs,
            protocol=(
                "This protocol explodes eligible older closed interventional ClinicalTrials.gov studies into country-linked portfolios and ranks lead sponsors within selected national footprints. "
                "Primary outputs compare sponsor-level missing-results counts, no-results rates, ghost-protocol rates, and fully visible shares across United States, China, Egypt, Poland, Australia, and Japan-linked studies. "
                "The aim is to test whether the visible backlog resolves into different institutional repeater structures once country-linked portfolios are isolated. "
                "Because country links come from recorded study locations, the analysis measures country involvement rather than sponsor domicile, enrollment shares, or national legal exposure."
            ),
            root_title="Which sponsors dominate country-linked CT.gov backlogs?",
            root_eyebrow="Country Sponsor Project",
            root_lede="A standalone public project on country-linked sponsor repeaters, showing that the same registry backlog resolves into very different institutional stories once U.S., China, Egypt, Poland, Australia, and Japan footprints are separated.",
            chapter_intro="This page treats country-linked portfolios as their own sponsor universes rather than small notes under a global league table. Once country footprints are separated, the repeater list changes quickly.",
            root_pull_quote="Egypt and China are dominated by very different repeaters than the United States, and Poland is cleaner even at the top-sponsor level.",
            paper_pull_quote="Country-linked sponsor auditing changes the registry story because national study footprints do not share one common repeater list.",
            dashboard_pull_quote="A sponsor table without country context collapses together institutional stories that are genuinely different on both count and rate.",
            root_rail=["Egypt | Cairo 968", "US | Mayo 927", "China | Sun 235", "Poland | Sanofi 47.5%"],
            landing_metrics=[
                ("Egypt | Cairo", fmt_int(as_int(egypt_top["no_results_count"])), short_sponsor(str(egypt_top["lead_sponsor_name"]))),
                ("US | Mayo", fmt_int(as_int(us_top["no_results_count"])), short_sponsor(str(us_top["lead_sponsor_name"]))),
                ("China | Sun", fmt_int(as_int(china_top["no_results_count"])), short_sponsor(str(china_top["lead_sponsor_name"]))),
                ("Poland top rate", fmt_pct(as_float(poland_top["no_results_rate"])), short_sponsor(str(poland_top["lead_sponsor_name"]))),
            ],
            landing_chart_html=chart_section(
                "Top sponsor backlog by country",
                bar_chart(
                    [
                        {"label": "US | " + short_sponsor(str(us_top["lead_sponsor_name"])), "value": as_int(us_top["no_results_count"])},
                        {"label": "China | " + short_sponsor(str(china_top["lead_sponsor_name"])), "value": as_int(china_top["no_results_count"])},
                        {"label": "Egypt | " + short_sponsor(str(egypt_top["lead_sponsor_name"])), "value": as_int(egypt_top["no_results_count"])},
                        {"label": "Poland | " + short_sponsor(str(poland_top["lead_sponsor_name"])), "value": as_int(poland_top["no_results_count"])},
                        {"label": "Australia | " + short_sponsor(str(australia_top["lead_sponsor_name"])), "value": as_int(australia_top["no_results_count"])},
                        {"label": "Japan | " + short_sponsor(str(japan_top["lead_sponsor_name"])), "value": as_int(japan_top["no_results_count"])},
                    ],
                    "Country-linked sponsor repeaters",
                    "Top missing-results counts inside selected country-linked portfolios",
                    "value",
                    "label",
                    "#326891",
                    percent=False,
                ),
                "Egypt and the United States carry the largest top-sponsor stocks, but with very different institutions and visibility profiles.",
                "The count view makes clear that the country-linked repeater story is not a thin tail phenomenon.",
            ),
            reader_lede="A 156-word micro-paper on how sponsor repeaters differ across selected country-linked CT.gov portfolios.",
            reader_rail=["US", "China", "Egypt", "Poland"],
            reader_metrics=[
                ("China top rate", fmt_pct(as_float(china_top["no_results_rate"])), short_sponsor(str(china_top["lead_sponsor_name"]))),
                ("Egypt top rate", fmt_pct(as_float(egypt_top["no_results_rate"])), short_sponsor(str(egypt_top["lead_sponsor_name"]))),
                ("Australia top visible", fmt_pct(as_float(australia_top["results_publication_visible_rate"])), short_sponsor(str(australia_top["lead_sponsor_name"]))),
                ("Japan top visible", fmt_pct(as_float(japan_top["results_publication_visible_rate"])), short_sponsor(str(japan_top["lead_sponsor_name"]))),
            ],
            dashboard_title="Country-linked sponsor repeaters show very different institutional backlog structures across major study footprints",
            dashboard_eyebrow="Country Sponsor Dashboard",
            dashboard_lede="The leading repeaters in U.S., China, Egypt, Poland, Australia, and Japan-linked portfolios are not interchangeable, and their rates range from moderate to nearly total silence.",
            dashboard_rail=["Backlog counts", "Top rates", "Country classes", "Visible share"],
            dashboard_metrics=[
                ("US | Mayo", fmt_int(as_int(us_top["no_results_count"])), "Largest US-linked stock"),
                ("China | Sun", fmt_pct(as_float(china_top["no_results_rate"])), "Top China-linked rate"),
                ("Egypt | Cairo", fmt_pct(as_float(egypt_top["no_results_rate"])), "Top Egypt-linked rate"),
                ("Poland | Roche visible", fmt_pct(as_float(poland_industry["results_publication_visible_rate"])), "Country context"),
            ],
            dashboard_sections=[
                chart_section(
                    "Top sponsor stock by selected country",
                    bar_chart(
                        [
                            {"label": "US | " + short_sponsor(str(us_top["lead_sponsor_name"])), "value": as_int(us_top["no_results_count"])},
                            {"label": "China | " + short_sponsor(str(china_top["lead_sponsor_name"])), "value": as_int(china_top["no_results_count"])},
                            {"label": "Egypt | " + short_sponsor(str(egypt_top["lead_sponsor_name"])), "value": as_int(egypt_top["no_results_count"])},
                            {"label": "Poland | " + short_sponsor(str(poland_top["lead_sponsor_name"])), "value": as_int(poland_top["no_results_count"])},
                            {"label": "Australia | " + short_sponsor(str(australia_top["lead_sponsor_name"])), "value": as_int(australia_top["no_results_count"])},
                            {"label": "Japan | " + short_sponsor(str(japan_top["lead_sponsor_name"])), "value": as_int(japan_top["no_results_count"])},
                        ],
                        "Top sponsor count",
                        "Leading missing-results counts inside selected country-linked portfolios",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "The largest top-sponsor counts belong to Egypt and the United States, but the institutions are completely different.",
                    "That is why the project reads country-linked portfolios as separate sponsor ecosystems.",
                ),
                chart_section(
                    "Top sponsor rate by selected country",
                    bar_chart(
                        [
                            {"label": "US | " + short_sponsor(str(us_top["lead_sponsor_name"])), "value": as_float(us_top["no_results_rate"])},
                            {"label": "China | " + short_sponsor(str(china_top["lead_sponsor_name"])), "value": as_float(china_top["no_results_rate"])},
                            {"label": "Egypt | " + short_sponsor(str(egypt_top["lead_sponsor_name"])), "value": as_float(egypt_top["no_results_rate"])},
                            {"label": "Poland | " + short_sponsor(str(poland_top["lead_sponsor_name"])), "value": as_float(poland_top["no_results_rate"])},
                            {"label": "Australia | " + short_sponsor(str(australia_top["lead_sponsor_name"])), "value": as_float(australia_top["no_results_rate"])},
                            {"label": "Japan | " + short_sponsor(str(japan_top["lead_sponsor_name"])), "value": as_float(japan_top["no_results_rate"])},
                        ],
                        "Top sponsor rate",
                        "2-year no-results rate for the top-count sponsor inside each country-linked portfolio",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "China and Egypt sit near-total silence territory at the top-sponsor level, while Poland is materially cleaner.",
                    "The rate view keeps the project from collapsing into count alone.",
                ),
                chart_section(
                    "Industry versus other by selected country",
                    bar_chart(
                        [
                            {"label": "China | Industry", "value": as_float(china_industry["no_results_rate"])},
                            {"label": "China | Other", "value": as_float(china_other["no_results_rate"])},
                            {"label": "Egypt | Industry", "value": as_float(egypt_industry["no_results_rate"])},
                            {"label": "Egypt | Other", "value": as_float(egypt_other["no_results_rate"])},
                            {"label": "Poland | Industry", "value": as_float(poland_industry["no_results_rate"])},
                            {"label": "Poland | Other", "value": as_float(poland_other["no_results_rate"])},
                            {"label": "Australia | Industry", "value": as_float(australia_industry["no_results_rate"])},
                            {"label": "Australia | Other", "value": as_float(australia_other["no_results_rate"])},
                        ],
                        "Selected sponsor classes",
                        "No-results contrast for industry versus other inside selected countries",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Poland and Australia look cleaner partly because their industry-linked portfolios are far below the China and Egypt extremes.",
                    "This provides country context around the sponsor repeater tables rather than leaving them unanchored.",
                ),
            ],
            sidebar_bullets=[
                "Mayo Clinic carries the largest U.S.-linked missing-results stock at 927 studies in the wave-seven country repeater table.",
                "Sun Yat-sen University leads China at 235 studies, and Cairo University leads Egypt at 968.",
                "Poland is materially cleaner at the top-sponsor level than China or Egypt.",
                "Country-linked sponsor stories differ even before legal or national-policy layers are added.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-us-vs-exus-sponsor-classes",
            title="CT.gov U.S. Versus Ex-U.S. Sponsor Classes",
            summary="A standalone E156 project on how sponsor-class hiddenness changes once older studies are collapsed into any-U.S., no-U.S., and no-country buckets.",
            body=us_body,
            sentences=us_sentences,
            primary_estimand="2-year no-results rate across sponsor classes within any-U.S., no-U.S., and no-country older CT.gov portfolios",
            data_note="249,507 eligible older closed interventional studies grouped into any-U.S., no-U.S., and no-country buckets",
            references=common_refs,
            protocol=(
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies into any-U.S., no-U.S., and no-country buckets using recorded locations and then compares sponsor classes within each bucket. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and fully visible shares across sponsor classes, with a secondary contrast between industry, OTHER, and NIH portfolios. "
                "The aim is to test whether U.S. presence remains a strong structural divider after sponsor class is made explicit. "
                "Because the buckets come from recorded study locations, the project measures registry geography structure rather than sponsor domicile, verified enrollment shares, or legal exposure."
            ),
            root_title="How much does U.S. presence change sponsor-class hiddenness?",
            root_eyebrow="US Presence Project",
            root_lede="A standalone public project on U.S. versus ex-U.S. sponsor classes, showing that the no-U.S. backlog is much quieter than the any-U.S. registry surface across major sponsor classes.",
            chapter_intro="This page collapses the larger geography table into one structural question: does any U.S. presence materially change how sponsor classes look on the public registry surface?",
            root_pull_quote="No-U.S. studies are much quieter than any-U.S. studies, and the gap survives inside industry, OTHER, and NIH portfolios.",
            paper_pull_quote="U.S. presence is not a cosmetic bucket split. It changes the sponsor-class story in a large and durable way.",
            dashboard_pull_quote="The main break is not one sponsor class against another. It is the any-U.S. versus no-U.S. separation inside those classes.",
            root_rail=["Any US 52.1%", "No US 88.7%", "No-country 80.9%", "No US OTHER 94.9%"],
            landing_metrics=[
                ("Any-US no results", fmt_pct(as_float(any_us["no_results_rate"])), "All any-US studies"),
                ("No-US no results", fmt_pct(as_float(no_us["no_results_rate"])), "All no-US studies"),
                ("No-country ghosts", fmt_pct(as_float(no_country["ghost_protocol_rate"])), "Neither visible"),
                ("Any-US industry", fmt_pct(as_float(any_us_industry["no_results_rate"])), "Selected sponsor class"),
            ],
            landing_chart_html=chart_section(
                "U.S.-presence buckets",
                bar_chart(
                    [
                        {"label": "Any US", "value": as_float(any_us["no_results_rate"])},
                        {"label": "No US", "value": as_float(no_us["no_results_rate"])},
                        {"label": "No country", "value": as_float(no_country["no_results_rate"])},
                    ],
                    "U.S.-presence buckets",
                    "2-year no-results rate by U.S.-presence bucket",
                    "value",
                    "label",
                    "#c3452f",
                    percent=True,
                ),
                "The simple any-U.S. versus no-U.S. split already captures a large part of the registry visibility gradient.",
                "No-U.S. studies sit far above the any-U.S. portfolio even before sponsor class enters the picture.",
            ),
            reader_lede="A 156-word micro-paper on how sponsor classes separate once older CT.gov studies are collapsed into any-U.S., no-U.S., and no-country buckets.",
            reader_rail=["Any US", "No US", "Industry", "OTHER"],
            reader_metrics=[
                ("No-US OTHER", fmt_pct(as_float(no_us_other["no_results_rate"])), "Worst large sponsor-class cell"),
                ("No-US industry", fmt_pct(as_float(no_us_industry["no_results_rate"])), "Ex-US industry"),
                ("Any-US NIH", fmt_pct(as_float(any_us_nih["no_results_rate"])), "Any-US NIH"),
                ("No-US NIH visible", fmt_pct(as_float(no_us_nih["results_publication_visible_rate"])), "Ex-US NIH"),
            ],
            dashboard_title="Any-U.S. and no-U.S. buckets split sponsor classes into sharply different CT.gov visibility regimes",
            dashboard_eyebrow="US vs Ex-US Dashboard",
            dashboard_lede="Once older studies are collapsed into any-U.S., no-U.S., and no-country portfolios, the sponsor-class gap becomes much easier to read: no-U.S. OTHER and no-U.S. industry are far quieter than their any-U.S. counterparts.",
            dashboard_rail=["Bucket rates", "Sponsor classes", "Ghosts", "Visible share"],
            dashboard_metrics=[
                ("No-US OTHER", fmt_pct(as_float(no_us_other["no_results_rate"])), "Selected extreme"),
                ("Any-US OTHER", fmt_pct(as_float(any_us_other["no_results_rate"])), "Comparator"),
                ("No-US industry", fmt_pct(as_float(no_us_industry["no_results_rate"])), "Selected cell"),
                ("No-country industry", fmt_pct(as_float(no_country_industry["no_results_rate"])), "No-country cell"),
            ],
            dashboard_sections=[
                chart_section(
                    "No-results by U.S.-presence bucket",
                    bar_chart(
                        [
                            {"label": "Any US", "value": as_float(any_us["no_results_rate"])},
                            {"label": "No US", "value": as_float(no_us["no_results_rate"])},
                            {"label": "No country", "value": as_float(no_country["no_results_rate"])},
                        ],
                        "U.S.-presence buckets",
                        "2-year no-results rate by any-U.S., no-U.S., and no-country buckets",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "The main registry split is visible even before sponsor class enters the page.",
                    "No-U.S. and no-country portfolios both sit in much quieter territory than the any-U.S. surface.",
                ),
                chart_section(
                    "Selected sponsor-class cells",
                    bar_chart(
                        [
                            {"label": "Any US | Industry", "value": as_float(any_us_industry["no_results_rate"])},
                            {"label": "No US | Industry", "value": as_float(no_us_industry["no_results_rate"])},
                            {"label": "No country | Industry", "value": as_float(no_country_industry["no_results_rate"])},
                            {"label": "Any US | OTHER", "value": as_float(any_us_other["no_results_rate"])},
                            {"label": "No US | OTHER", "value": as_float(no_us_other["no_results_rate"])},
                            {"label": "Any US | NIH", "value": as_float(any_us_nih["no_results_rate"])},
                            {"label": "No US | NIH", "value": as_float(no_us_nih["no_results_rate"])},
                        ],
                        "Selected sponsor classes",
                        "Selected sponsor-class no-results rates across U.S.-presence buckets",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Industry, OTHER, and NIH all shift when U.S. presence drops out of the location profile.",
                    "That keeps the page from reading like a one-class problem or a geography-only problem.",
                ),
                chart_section(
                    "Ghost protocols by U.S.-presence bucket",
                    bar_chart(
                        [
                            {"label": "Any US", "value": as_float(any_us["ghost_protocol_rate"])},
                            {"label": "No US", "value": as_float(no_us["ghost_protocol_rate"])},
                            {"label": "No country", "value": as_float(no_country["ghost_protocol_rate"])},
                        ],
                        "Ghost protocols",
                        "Ghost-protocol rate by U.S.-presence bucket",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "The same ordering survives on the stricter ghost-protocol measure.",
                    "That reduces the chance that the U.S.-presence gap is only a posted-results artifact.",
                ),
            ],
            sidebar_bullets=[
                "Any-U.S. studies show a 52.1 percent no-results rate, versus 88.7 percent for no-U.S. studies.",
                "No-U.S. OTHER reaches 94.9 percent no results, while no-U.S. industry reaches 70.9 percent.",
                "Any-U.S. industry is materially cleaner at 45.5 percent no results.",
                "The U.S.-presence split remains visible across no-results, ghost-protocol, and visible-share metrics.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-industry-family-repeaters",
            title="CT.gov Industry Family Repeaters",
            summary="A standalone E156 project on how repeat-offender industry sponsors change once intervention family and geography are held fixed.",
            body=industry_body,
            sentences=industry_sentences,
            primary_estimand="Industry sponsor missing-results counts within intervention families among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies, with industry records grouped by intervention family and geography",
            references=common_refs,
            protocol=(
                "This protocol isolates industry-sponsored eligible older closed interventional ClinicalTrials.gov studies, explodes intervention families, and ranks sponsors within each family. "
                "Primary outputs compare sponsor-level missing-results counts, no-results rates, ghost-protocol rates, and fully visible shares across drug, device, procedure, biological, and dietary-supplement families, with a secondary geography contrast for industry portfolios. "
                "The aim is to test whether the pooled industry backlog hides distinct family-specific repeater structures and cross-border visibility gradients. "
                "Because sponsor, intervention, and country fields are registry-entered, the analysis measures registry-visible industry structure rather than audited corporate, therapeutic, or legal classifications."
            ),
            root_title="Where is the industry backlog really concentrated?",
            root_eyebrow="Industry Family Project",
            root_lede="A standalone public project on industry family repeaters, showing that drug, device, procedure, biological, and dietary-supplement portfolios do not share one common sponsor hierarchy or geography profile.",
            chapter_intro="This page narrows the industry question. Instead of one pooled sponsor leaderboard, it asks which sponsors dominate once treatment family and geography are held fixed.",
            root_pull_quote="Industry hiddenness is not one backlog. It breaks into different modality clusters, and those clusters shift again by geography.",
            paper_pull_quote="The pooled industry table hides where the backlog actually sits. Intervention family and geography both change the sponsor story.",
            dashboard_pull_quote="Drug stock dominates on count, dietary and device families dominate on rate, and the no-U.S. industry portfolio remains much quieter than mixed cross-border industry work.",
            root_rail=["Drug GSK 1,033", "Dietary 92.7%", "Mixed geo 27.3%", "No-US industry 70.9%"],
            landing_metrics=[
                ("Drug family", fmt_pct(as_float(drug_family["no_results_rate"])), "Largest industry family"),
                ("Dietary family", fmt_pct(as_float(dietary_family["no_results_rate"])), "Quietest industry family"),
                ("Mixed industry", fmt_pct(as_float(mixed_industry["no_results_rate"])), "US + non-US portfolio"),
                ("No-US industry", fmt_pct(as_float(no_us_industry_geo["no_results_rate"])), "Industry geography gap"),
            ],
            landing_chart_html=chart_section(
                "Industry families",
                bar_chart(
                    [{"label": row["intervention_type"], "value": as_float(row["no_results_rate"])} for _, row in industry_intervention.iterrows()],
                    "Industry intervention families",
                    "2-year no-results rate across industry intervention families",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "Industry hiddenness changes sharply once modality is fixed, from biological and procedure profiles to an extreme dietary-supplement tail.",
                "The family view matters because one industry leaderboard cannot explain these different patterns.",
            ),
            reader_lede="A 156-word micro-paper on how repeat-offender industry sponsors change once intervention family and geography are held fixed.",
            reader_rail=["Drug", "Device", "Dietary", "Industry geo"],
            reader_metrics=[
                ("GSK drug backlog", fmt_int(as_int(drug_rows.iloc[0]["no_results_count"])), "Largest drug-family stock"),
                ("Device top rate", fmt_pct(as_float(device_rows.iloc[0]["no_results_rate"])), short_sponsor(str(device_rows.iloc[0]["lead_sponsor_name"]))),
                ("Dietary top rate", fmt_pct(as_float(dietary_rows.iloc[0]["no_results_rate"])), short_sponsor(str(dietary_rows.iloc[0]["lead_sponsor_name"]))),
                ("US-only industry", fmt_pct(as_float(us_only_industry_geo["no_results_rate"])), "Industry geography bucket"),
            ],
            dashboard_title="Industry repeaters change once CT.gov studies are split by family and geography",
            dashboard_eyebrow="Industry Families Dashboard",
            dashboard_lede="Drug portfolios carry the biggest industry stock, dietary and some device pockets are far worse on rate, and industry studies become much quieter when the location profile shifts from mixed U.S.-global to no-U.S.",
            dashboard_rail=["Family rates", "Drug stack", "Industry geo", "Top countries"],
            dashboard_metrics=[
                ("Drug family", fmt_pct(as_float(drug_family["no_results_rate"])), "Largest family"),
                ("Dietary family", fmt_pct(as_float(dietary_family["no_results_rate"])), "Selected extreme"),
                ("Device family", fmt_pct(as_float(device_family["no_results_rate"])), "Device portfolio"),
                ("Biological family", fmt_pct(as_float(biological_family["no_results_rate"])), "Cleaner comparator"),
            ],
            dashboard_sections=[
                chart_section(
                    "Industry no-results by family",
                    bar_chart(
                        [{"label": row["intervention_type"], "value": as_float(row["no_results_rate"])} for _, row in industry_intervention.iterrows()],
                        "Industry families",
                        "2-year no-results rate by industry intervention family",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Dietary-supplement and diagnostic tails are much quieter than drug and biological portfolios, even within industry alone.",
                    "That is the first sign that the industry backlog is not structurally uniform.",
                ),
                chart_section(
                    "Top drug-family repeaters",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_int(row["no_results_count"])} for _, row in drug_rows.iterrows()],
                        "Drug-family repeaters",
                        "Top missing-results counts inside the industry drug family",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "The drug family contains a thick upper tier led by GSK, Boehringer, AstraZeneca, Sanofi, Pfizer, and Novartis.",
                    "This is the count-heavy center of the industry story.",
                ),
                chart_section(
                    "Industry geography buckets",
                    bar_chart(
                        [
                            {"label": "US only", "value": as_float(us_only_industry_geo["no_results_rate"])},
                            {"label": "US + non-US", "value": as_float(mixed_industry["no_results_rate"])},
                            {"label": "No US", "value": as_float(no_us_industry_geo["no_results_rate"])},
                        ],
                        "Industry geography",
                        "2-year no-results rate across industry geography buckets",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Industry studies look far cleaner in mixed U.S.-global portfolios than in no-U.S. portfolios.",
                    "The geography split matters even after industry sponsorship is already fixed.",
                ),
            ],
            sidebar_bullets=[
                "GSK carries the largest drug-family industry backlog at 1,033 studies.",
                "Dietary-supplement industry studies reach 92.7 percent no results, far above the drug-family rate.",
                "Mixed U.S.-plus-non-U.S. industry portfolios are much cleaner at 27.3 percent no results than no-U.S. industry portfolios at 70.9 percent.",
                "Industry backlog concentration depends on both intervention family and geography, not sponsor name alone.",
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
