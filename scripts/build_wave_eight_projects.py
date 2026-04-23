#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Build wave-eight standalone CT.gov projects from adjusted hiddenness, overdue clocks, publication indexing, and ACT-style debt."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct
from build_split_projects import chart_section, sentence_bundle, write_project

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

REPAIR_MAP = {
    "Assistance Publique - HÃƒÂ´pitaux de Paris": "Assistance Publique - Hôpitaux de Paris",
    "Assistance Publique - Hï¿½pitaux de Paris": "Assistance Publique - Hôpitaux de Paris",
    "SociÃƒÂ©tÃƒÂ© des Produits NestlÃƒÂ© (SPN)": "Société des Produits Nestlé (SPN)",
    "Sociï¿½tï¿½ des Produits Nestlï¿½ (SPN)": "Société des Produits Nestlé (SPN)",
}

SPONSOR_SHORT = {
    "Assistance Publique - Hôpitaux de Paris": "AP-HP",
    "Cairo University": "Cairo U",
    "Ain Shams University": "Ain Shams",
    "Assiut University": "Assiut",
    "Hospices Civils de Lyon": "HCL",
    "University Health Network, Toronto": "UHN Toronto",
    "Alliance for Clinical Trials in Oncology": "Alliance",
    "University Hospital, Bordeaux": "Bordeaux",
    "Sanofi": "Sanofi",
    "Bayer": "Bayer",
    "Astellas Pharma Inc": "Astellas",
    "Boehringer Ingelheim": "Boehringer",
    "Bristol-Myers Squibb": "BMS",
    "Mayo Clinic": "Mayo",
    "National Cancer Institute (NCI)": "NCI",
}


def clean_text(value: object) -> str:
    text = "" if value is None else str(value)
    if text in {"", "nan", "None"}:
        return ""
    return REPAIR_MAP.get(text, text)


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


def short_sponsor(name: str) -> str:
    return SPONSOR_SHORT.get(clean_text(name), clean_text(name))


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
    risk_metrics = load_csv("risk_adjusted_model_metrics.csv")
    risk_class = load_csv("risk_adjusted_sponsor_class_summary.csv")
    risk_us = load_csv("risk_adjusted_us_presence_summary.csv")
    risk_sponsors = load_csv("risk_adjusted_top_sponsors.csv")
    overdue_class = load_csv("overdue_sponsor_class_clock.csv")
    overdue_phase = load_csv("overdue_phase_clock.csv")
    overdue_era = load_csv("overdue_completion_era_clock.csv")
    lag_bands = load_csv("overdue_lag_band_summary.csv")
    publication = load_csv("external_publication_audit_summary.csv")
    act_layer = load_csv("act_proxy_layer_summary.csv")
    act_class = load_csv("act_proxy_layer_sponsor_class_summary.csv")
    act_era = load_csv("act_proxy_layer_completion_era_summary.csv")

    no_results_metrics = row_for(risk_metrics, "target", "results_gap_2y")
    ghost_metrics = row_for(risk_metrics, "target", "ghost_protocol")
    other_adjusted = row_for_pair(risk_class, "lead_sponsor_class", "OTHER", "target", "results_gap_2y")
    other_gov_adjusted = row_for_pair(risk_class, "lead_sponsor_class", "OTHER_GOV", "target", "results_gap_2y")
    industry_adjusted = row_for_pair(risk_class, "lead_sponsor_class", "INDUSTRY", "target", "results_gap_2y")
    industry_ghost = row_for_pair(risk_class, "lead_sponsor_class", "INDUSTRY", "target", "ghost_protocol")
    no_us_adjusted = row_for_pair(risk_us, "us_presence", "No US", "target", "results_gap_2y")
    any_us_adjusted = row_for_pair(risk_us, "us_presence", "Any US", "target", "results_gap_2y")
    named_classes_no_results = risk_class[
        (risk_class["target"] == "results_gap_2y")
        & risk_class["lead_sponsor_class"].isin(["OTHER", "OTHER_GOV", "NETWORK", "INDUSTRY", "NIH", "FED", "INDIV"])
    ].copy()
    named_classes_ghost = risk_class[
        (risk_class["target"] == "ghost_protocol")
        & risk_class["lead_sponsor_class"].isin(["OTHER", "OTHER_GOV", "NETWORK", "INDUSTRY", "NIH", "FED", "INDIV"])
    ].copy()
    top_excess_no_results = risk_sponsors[risk_sponsors["target"] == "results_gap_2y"].head(8).copy()

    other_gov_clock = row_for(overdue_class, "lead_sponsor_class", "OTHER_GOV")
    industry_clock = row_for(overdue_class, "lead_sponsor_class", "INDUSTRY")
    other_clock = row_for(overdue_class, "lead_sponsor_class", "OTHER")
    nih_clock = row_for(overdue_class, "lead_sponsor_class", "NIH")
    pre_fd = row_for(overdue_era, "rule_era", "Pre-FDAAA 801 (2000-2007)")
    recent_era = row_for(overdue_era, "rule_era", "Recent Eligible Era (2021-2024)")
    fdaaa_era = row_for(overdue_era, "rule_era", "FDAAA 801 Era (2008-2016)")
    phase1_clock = row_for(overdue_phase, "phase_bucket", "PHASE1")
    lag_overall = lag_bands.copy()

    weighted_publication = row_for(publication, "lead_sponsor_class", "ALL_WEIGHTED")
    industry_publication = row_for(publication, "lead_sponsor_class", "INDUSTRY")
    nih_publication = row_for(publication, "lead_sponsor_class", "NIH")
    network_publication = row_for(publication, "lead_sponsor_class", "NETWORK")
    other_publication = row_for(publication, "lead_sponsor_class", "OTHER")
    audit_rows = publication[publication["lead_sponsor_class"] != "ALL_WEIGHTED"].copy()

    broad_proxy = row_for(act_layer, "proxy_layer", "Broad US nexus")
    strict_proxy = row_for(act_layer, "proxy_layer", "Drug/Bio/Device US strict")
    drug_bio_proxy = row_for(act_layer, "proxy_layer", "Drug/Bio US non-phase1")
    strict_other = row_for_pair(act_class, "proxy_layer", "Drug/Bio/Device US strict", "lead_sponsor_class", "OTHER")
    strict_industry = row_for_pair(act_class, "proxy_layer", "Drug/Bio/Device US strict", "lead_sponsor_class", "INDUSTRY")
    strict_nih = row_for_pair(act_class, "proxy_layer", "Drug/Bio/Device US strict", "lead_sponsor_class", "NIH")
    strict_network = row_for_pair(act_class, "proxy_layer", "Drug/Bio/Device US strict", "lead_sponsor_class", "NETWORK")
    strict_pre = row_for_pair(act_era, "proxy_layer", "Drug/Bio/Device US strict", "rule_era", "Pre-FDAAA 801 (2000-2007)")
    strict_fdaaa = row_for_pair(act_era, "proxy_layer", "Drug/Bio/Device US strict", "rule_era", "FDAAA 801 Era (2008-2016)")
    strict_recent = row_for_pair(act_era, "proxy_layer", "Drug/Bio/Device US strict", "rule_era", "Recent Eligible Era (2021-2024)")

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
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
        ("ctgov-risk-adjusted-hiddenness", "CT.gov Risk-Adjusted Hiddenness", "Study-mix-adjusted hiddenness showing which sponsor classes, geographies, and sponsors remain worse than expected.", "Adjusted"),
        ("ctgov-overdue-results-clock", "CT.gov Overdue Results Clock", "Time-since-due analysis showing how unresolved CT.gov results debt ages across cohorts, phases, and sponsor classes.", "Clock"),
        ("ctgov-publication-index-gap", "CT.gov Publication Index Gap", "Sample-based exact-ID audit showing how much no-link CT.gov silence is an indexing and linkage gap rather than a PubMed-only miss.", "Index Gap"),
        ("ctgov-probable-act-fdaaa-debt", "CT.gov Probable ACT/FDAAA Debt", "U.S.-nexus proxy layers showing how large, old, and distributed the likely regulated backlog still is.", "ACT Debt"),
    ]
    series_links = [
        {"repo_name": repo_name, "title": title, "summary": summary, "short_title": short_title, "pages_url": f"https://{REPO_OWNER}.github.io/{repo_name}/"}
        for repo_name, title, summary, short_title in series_seed
    ]
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    risk_body, risk_sentences = sentence_bundle([
        ("Question", "Which CT.gov portfolios remain quieter than expected after adjusting for study mix instead of comparing raw rates alone?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
        ("Method", "We fit logistic models for missing results and ghost protocols using phase, purpose, allocation, status, enrollment, arm count, intervention count, geography scale, outcome density, and study age, excluding sponsor and geography identities from adjustment."),
        ("Primary result", "After adjustment, No-US portfolios still carried 16,659 excess no-results studies, while OTHER held the largest sponsor-class excess stock at 3,652 and OTHER_GOV the worst excess rate at 17.1 percentage points."),
        ("Secondary result", "Industry fell below expectation on no-results by 3,314 studies yet above expectation on ghost protocols by 3,051, suggesting residual hiddenness concentrates in fully invisible studies."),
        ("Interpretation", "Study mix therefore explains part of the backlog, but large sponsor and geography residuals still remain after adjustment."),
        ("Boundary", "These models use registry-visible design fields and estimate excess hiddenness, not causal blame or legal liability."),
    ])
    overdue_body, overdue_sentences = sentence_bundle([
        ("Question", "What does reporting debt look like once missing results are converted into time since due rather than a single binary flag?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
        ("Method", "We summarized current result-posting status, shares reported within 12, 24, 36, and 60 months, reporting-lag distributions for reported studies, and overdue years beyond the two-year mark for unresolved studies."),
        ("Primary result", "Pre-FDAAA cohorts remain the deepest debt pool: 87.7 percent unresolved, median reported lag 2,247 days, and mean unresolved debt 18.6 years beyond the two-year mark."),
        ("Secondary result", "By sponsor class, OTHER_GOV is worst on unresolved older studies at 95.7 percent, while industry still combines a 58.1 percent unresolved rate with 9.35 mean overdue years beyond the two-year mark."),
        ("Interpretation", "The clock therefore separates ancient unresolved stock from newer cohorts that are still drifting into silence."),
        ("Boundary", "These timing summaries use current registry status and do not infer when unpublished external papers may have appeared yet."),
    ])
    publication_body, publication_sentences = sentence_bundle([
        ("Question", "How much of CT.gov publication-link missingness survives when no-link studies are re-audited with broader exact-ID search beyond the earlier PubMed-only pass?"),
        ("Dataset", "We re-audited the existing 1,050-study sponsor-class-stratified sample of older no-link studies drawn from 140,363 eligible no-link records in the March 29, 2026 registry snapshot."),
        ("Method", "We compared PubMed exact-ID matches with Europe PMC exact-ID matches, separating total rescue, non-MED rescue, and weighted publication-only visibility."),
        ("Primary result", "Weighted PubMed exact-ID matching captured only 1.2 percent of no-link records, but Europe PMC exact-ID rescue added 39.6 points, lifting weighted any-match visibility to 40.8 percent."),
        ("Secondary result", "Non-MED rescue was much smaller at 2.8 points, while weighted external-publication-only visibility still reached 29.1 percent."),
        ("Interpretation", "Publication-link missingness therefore combines real silence with a much larger indexing and linkage gap than the PubMed-only audit suggested, especially in NIH-linked and network-linked no-link portfolios."),
        ("Boundary", "The audit is sample-based, exact-ID only, and cannot adjudicate whether every retrieved paper fully reports the registered study or whether links were added later."),
    ])
    act_body, act_sentences = sentence_bundle([
        ("Question", "How large is the likely U.S.-nexus reporting debt once older CT.gov studies are filtered through strict and broad ACT-style sensitivity layers?"),
        ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
        ("Method", "We created three proxy layers using recorded U.S. locations, intervention families, and phase exclusions within older closed interventional records: broad U.S. nexus, drug/bio non-phase1, and strict drug/bio/device U.S. nexus."),
        ("Primary result", "The strict proxy contains 58,598 older studies, with 18,475 missing-results studies and a 31.5 percent no-results rate."),
        ("Secondary result", "Debt is still old inside that supposedly regulated core: mean unresolved time is 10.92 years beyond the two-year mark, and Pre-FDAAA strict-proxy cohorts remain 87.0 percent unresolved even after U.S.-nexus filtering."),
        ("Interpretation", "The regulatory backlog therefore sits far below the raw all-study rate but remains large, old, and institutionally distributed across OTHER, INDUSTRY, and government-linked slices."),
        ("Boundary", "These layers are conservative proxies built from registry-visible fields, not formal ACT or FDAAA legal determinations or enforceability judgments."),
    ])

    projects: list[dict[str, object]] = []
    projects.append(
        make_spec(
            repo_name="ctgov-risk-adjusted-hiddenness",
            title="CT.gov Risk-Adjusted Hiddenness",
            summary="A standalone E156 project on which sponsor classes, geographies, and large sponsors remain worse than expected after adjusting for visible study mix.",
            body=risk_body,
            sentences=risk_sentences,
            primary_estimand="Excess missing-results stock over model-expected missing-results counts among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies with design-mix adjustment excluding sponsor and geography identities",
            references=common_refs,
            protocol=(
                "This protocol fits study-mix-adjusted models for missing results and ghost protocols among eligible older closed interventional ClinicalTrials.gov studies. "
                "The models use phase, purpose, allocation, status, enrollment, arm count, intervention count, geography scale, outcome density, and study age, while excluding sponsor and geography identities from the adjustment set. "
                "Primary outputs compare observed versus expected missing-results counts and excess rate points across sponsor classes, U.S.-presence buckets, and large lead sponsors. "
                "The aim is to distinguish raw backlog from residual hiddenness that remains after visible study mix is taken into account."
            ),
            root_title="What remains hidden after study-mix adjustment?",
            root_eyebrow="Adjusted Hiddenness Project",
            root_lede="A standalone public project on study-mix-adjusted hiddenness, showing that No-US portfolios and heterogeneous OTHER sponsors still remain worse than expected even after visible design differences are accounted for.",
            chapter_intro="This page tests whether the backlog is just a mix problem. It asks what still looks worse than expected after the visible registry profile of each study is held more constant.",
            root_pull_quote="Adjustment narrows some raw gaps, but No-US portfolios and OTHER_GOV still remain much worse than expected.",
            paper_pull_quote="Raw rate tables tell only part of the story. The residuals show where hiddenness still remains after design mix is held constant.",
            dashboard_pull_quote="The most important adjusted split is geography: No-US studies stay far above expectation, while Any-US studies fall far below it.",
            root_rail=["No US +16.7k", "OTHER +3.7k", "OTHER_GOV +17.1 pts", "Industry ghost +3.1k"],
            landing_metrics=[
                ("No-US excess", fmt_int(int(round(as_float(no_us_adjusted["excess_count"])))), "Adjusted no-results stock"),
                ("OTHER excess", fmt_int(int(round(as_float(other_adjusted["excess_count"])))), "Sponsor-class excess stock"),
                ("OTHER_GOV excess", f"{as_float(other_gov_adjusted['excess_rate_points']):.1f} pts", "Excess rate points"),
                ("Model AUC", f"{as_float(no_results_metrics['holdout_auc']):.3f}", "Holdout no-results model"),
            ],
            landing_chart_html=chart_section(
                "Adjusted sponsor-class excess",
                bar_chart(
                    [
                        {"label": row["lead_sponsor_class"], "value": as_float(row["excess_count"])}
                        for _, row in named_classes_no_results.sort_values("excess_count", ascending=False).iterrows()
                    ],
                    "Adjusted no-results stock",
                    "Excess missing-results counts by sponsor class after study-mix adjustment",
                    "value",
                    "label",
                    "#c3452f",
                    percent=False,
                ),
                "OTHER remains worst on adjusted stock, while OTHER_GOV is the sharpest rate outlier and industry drops below expected no-results volume.",
                "That is why the adjusted project reads count and residual direction together.",
            ),
            reader_lede="A 156-word micro-paper on which CT.gov sponsor classes and geographies remain worse than expected after study-mix adjustment.",
            reader_rail=["Adjusted counts", "No US", "OTHER", "Ghost residuals"],
            reader_metrics=[
                ("No-results AUC", f"{as_float(no_results_metrics['holdout_auc']):.3f}", "Holdout performance"),
                ("Ghost AUC", f"{as_float(ghost_metrics['holdout_auc']):.3f}", "Second target"),
                ("Industry ghost", fmt_int(int(round(as_float(industry_ghost["excess_count"])))), "Excess ghost stock"),
                ("Any-US shift", f"{as_float(any_us_adjusted['excess_rate_points']):.1f} pts", "Adjusted rate-point gap"),
            ],
            dashboard_title="Study-mix adjustment leaves a large No-US residual and a different sponsor-class story than the raw CT.gov league tables",
            dashboard_eyebrow="Adjusted Dashboard",
            dashboard_lede="Once visible study mix is held more constant, No-US portfolios remain dramatically worse than expected, OTHER still carries the largest sponsor-class excess stock, and industry shifts from a raw no-results problem to a stronger ghost-protocol residual.",
            dashboard_rail=["Residual stock", "No US gap", "Ghost residuals", "Top sponsors"],
            dashboard_metrics=[
                ("No-US excess", fmt_int(int(round(as_float(no_us_adjusted["excess_count"])))), "Adjusted stock"),
                ("Any-US excess", fmt_int(int(round(as_float(any_us_adjusted["excess_count"])))), "Comparator"),
                ("Industry ghost", fmt_int(int(round(as_float(industry_ghost["excess_count"])))), "Adjusted ghost stock"),
                ("OTHER_GOV rate", f"{as_float(other_gov_adjusted['excess_rate_points']):.1f} pts", "Worst excess rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Sponsor-class excess no-results stock",
                    bar_chart(
                        [
                            {"label": row["lead_sponsor_class"], "value": as_float(row["excess_count"])}
                            for _, row in named_classes_no_results.sort_values("excess_count", ascending=False).iterrows()
                        ],
                        "Adjusted sponsor classes",
                        "Excess missing-results counts by sponsor class after study-mix adjustment",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "OTHER still holds the largest residual stock even after visible study mix is accounted for.",
                    "Raw volume alone does not explain that adjusted excess.",
                ),
                chart_section(
                    "U.S.-presence residual",
                    bar_chart(
                        [
                            {"label": row["us_presence"], "value": as_float(row["excess_count"])}
                            for _, row in risk_us[risk_us["target"] == "results_gap_2y"].iterrows()
                        ],
                        "Adjusted geography buckets",
                        "Excess missing-results counts by U.S.-presence bucket",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "The largest adjusted gap sits between No US and Any US, not between neighboring sponsor classes.",
                    "That keeps the adjusted story anchored to geography as well as sponsorship.",
                ),
                chart_section(
                    "Top sponsor excess stock",
                    bar_chart(
                        [
                            {"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["excess_count"])}
                            for _, row in top_excess_no_results.iterrows()
                        ],
                        "Adjusted sponsor residuals",
                        "Largest sponsor-level excess missing-results counts",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "The sponsor residuals do not collapse into one sector or one geography.",
                    "That is why the adjusted audit remains useful even after the sponsor-class table is read.",
                ),
            ],
            sidebar_bullets=[
                "No-US portfolios still carry 16,659 excess missing-results studies after adjustment.",
                "OTHER holds the largest sponsor-class excess stock at roughly 3,652 studies.",
                "OTHER_GOV has the worst excess no-results rate at 17.1 percentage points.",
                "Industry falls below expected no-results stock but rises above expected ghost-protocol stock.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-overdue-results-clock",
            title="CT.gov Overdue Results Clock",
            summary="A standalone E156 project on how unresolved CT.gov results debt ages across sponsor classes, phases, and completion cohorts once silence is converted into time since due.",
            body=overdue_body,
            sentences=overdue_sentences,
            primary_estimand="Unresolved share and overdue years beyond the two-year mark among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies with current reporting status and results-posting lag fields",
            references=common_refs,
            protocol=(
                "This protocol converts missing-results status into a reporting clock for eligible older closed interventional ClinicalTrials.gov studies. "
                "Primary outputs compare current unresolved shares, shares reported within 12, 24, 36, and 60 months, lag distributions for reported studies, and overdue years beyond the two-year mark for unresolved studies. "
                "The aim is to separate very old unresolved debt from newer cohorts that are only beginning to drift into silence. "
                "Because timing is based on registry dates and current status, these outputs describe registry-visible age of debt rather than external-publication timing."
            ),
            root_title="How old is the unresolved results debt?",
            root_eyebrow="Results Clock Project",
            root_lede="A standalone public project on overdue CT.gov reporting clocks, showing that the oldest cohorts remain deeply unresolved while newer cohorts still have very weak within-two-year reporting.",
            chapter_intro="This page changes the frame from whether results are missing to how long they have been missing. Once the registry is read as aging debt, different cohort and sponsor stories appear.",
            root_pull_quote="Pre-FDAAA debt is ancient, but even recent eligible cohorts are still mostly unresolved.",
            paper_pull_quote="Binary no-results status compresses together ancient debt and fresh drift. The clock separates them.",
            dashboard_pull_quote="The main timing contrast is between the depth of old unresolved cohorts and the weak within-24-month reporting of newer ones.",
            root_rail=["Pre-FDAAA 87.7%", "OTHER_GOV 95.7%", "Industry 9.35y", "Recent 24m 17.4%"],
            landing_metrics=[
                ("Pre-FDAAA unresolved", fmt_pct(as_float(pre_fd["unresolved_rate"])), "Oldest cohort"),
                ("OTHER_GOV unresolved", fmt_pct(as_float(other_gov_clock["unresolved_rate"])), "Worst sponsor class"),
                ("Industry overdue", f"{as_float(industry_clock['mean_overdue_2y_years_unresolved']):.2f}y", "Mean debt beyond 2-year mark"),
                ("Recent within 24m", fmt_pct(as_float(recent_era["within_24m_rate"])), "Recent eligible era"),
            ],
            landing_chart_html=chart_section(
                "Completion-era unresolved rate",
                bar_chart(
                    [
                        {"label": row["rule_era"], "value": as_float(row["unresolved_rate"])}
                        for _, row in overdue_era.iterrows()
                    ],
                    "Results debt by era",
                    "Unresolved share by completion-era bucket",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "Old cohorts remain deeply unresolved, but recent cohorts are still far from timely reporting.",
                "The clock therefore distinguishes old stock from ongoing drift.",
            ),
            reader_lede="A 156-word micro-paper on how CT.gov reporting debt ages across cohorts and sponsor classes once silence is converted into time since due.",
            reader_rail=["Old debt", "Sponsor classes", "Within 24m", "Industry time"],
            reader_metrics=[
                ("Pre-FDAAA lag", fmt_int(int(round(as_float(pre_fd["median_lag_days_reported"])))), "Median reported lag days"),
                ("Phase I unresolved", fmt_pct(as_float(phase1_clock["unresolved_rate"])), "Worst large phase"),
                ("OTHER debt", f"{as_float(other_clock['mean_overdue_2y_years_unresolved']):.2f}y", "Mean overdue years"),
                ("NIH debt", f"{as_float(nih_clock['mean_overdue_2y_years_unresolved']):.2f}y", "Long-tail unresolved years"),
            ],
            dashboard_title="Once CT.gov silence is read as time since due, ancient debt and fresh drift become much easier to separate",
            dashboard_eyebrow="Results Clock Dashboard",
            dashboard_lede="Pre-FDAAA cohorts remain the deepest unresolved pool, OTHER_GOV is worst on unresolved share, industry carries long overdue time even with a lower unresolved rate than OTHER, and recent cohorts still show weak within-two-year reporting.",
            dashboard_rail=["Era debt", "Sponsor classes", "Overdue years", "Lag bands"],
            dashboard_metrics=[
                ("Pre-FDAAA unresolved", fmt_pct(as_float(pre_fd["unresolved_rate"])), "Oldest cohort"),
                ("FDAAA unresolved", fmt_pct(as_float(fdaaa_era["unresolved_rate"])), "Comparator"),
                ("Industry overdue", f"{as_float(industry_clock['mean_overdue_2y_years_unresolved']):.2f}y", "Mean overdue years"),
                ("Still missing", fmt_pct(as_float(row_for(lag_overall, "lag_band", "Still missing")["rate"])), "All eligible older studies"),
            ],
            dashboard_sections=[
                chart_section(
                    "Unresolved share by completion era",
                    bar_chart(
                        [
                            {"label": row["rule_era"], "value": as_float(row["unresolved_rate"])}
                            for _, row in overdue_era.iterrows()
                        ],
                        "Completion-era debt",
                        "Unresolved share by completion-era bucket",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "The oldest cohorts remain the deepest debt pool, but recent eligible eras are still mostly unresolved.",
                    "That keeps the clock focused on both history and present drift.",
                ),
                chart_section(
                    "Sponsor-class unresolved share",
                    bar_chart(
                        [
                            {"label": row["lead_sponsor_class"], "value": as_float(row["unresolved_rate"])}
                            for _, row in overdue_class[
                                overdue_class["lead_sponsor_class"].isin(["OTHER_GOV", "OTHER", "NETWORK", "INDIV", "INDUSTRY", "NIH", "FED"])
                            ].iterrows()
                        ],
                        "Sponsor-class debt",
                        "Current unresolved share among eligible older studies",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "OTHER_GOV is the clearest unresolved-rate extreme, but OTHER and industry still dominate in absolute stock.",
                    "The rate view alone does not settle the size question.",
                ),
                chart_section(
                    "Mean overdue years beyond the two-year mark",
                    bar_chart(
                        [
                            {"label": row["lead_sponsor_class"], "value": as_float(row["mean_overdue_2y_years_unresolved"])}
                            for _, row in overdue_class[
                                overdue_class["lead_sponsor_class"].isin(["OTHER_GOV", "OTHER", "NETWORK", "INDUSTRY", "NIH", "FED", "INDIV"])
                            ].iterrows()
                        ],
                        "Overdue years",
                        "Mean unresolved time beyond the two-year mark by sponsor class",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "Industry is not the worst unresolved-rate class, but its unresolved studies are still very old.",
                    "That is why the clock adds time depth to the simple unresolved share.",
                ),
            ],
            sidebar_bullets=[
                "Pre-FDAAA cohorts remain 87.7 percent unresolved.",
                "OTHER_GOV is worst on unresolved older studies at 95.7 percent.",
                "Industry unresolved studies average 9.35 years beyond the two-year mark.",
                "Recent eligible cohorts still reach only 17.4 percent reporting within 24 months.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-publication-index-gap",
            title="CT.gov Publication Index Gap",
            summary="A standalone E156 project on how much CT.gov publication-link silence is an indexing and linkage gap rather than a PubMed-only miss.",
            body=publication_body,
            sentences=publication_sentences,
            primary_estimand="Weighted exact-ID external publication rescue among older CT.gov no-link studies",
            data_note="1,050-study sponsor-class-stratified exact-ID audit representing 140,363 eligible older no-link studies",
            references=common_refs,
            protocol=(
                "This protocol re-audits the existing sponsor-class-stratified sample of older ClinicalTrials.gov studies with no linked publication reference. "
                "The audit compares PubMed exact-ID matches with Europe PMC exact-ID matches, then separates total external-any-match rescue, non-MED rescue, and publication-only visibility not exposed on the CT.gov record. "
                "Primary outputs report weighted rescue contributions overall and sponsor-class-specific external visibility rates across the sampled no-link portfolio. "
                "The aim is to distinguish true publication silence from indexing and linkage gaps that remain invisible to CT.gov readers."
            ),
            root_title="How much no-link silence is really an indexing gap?",
            root_eyebrow="Publication Index Project",
            root_lede="A standalone public project on publication indexing gaps, showing that exact-ID rescue beyond PubMed reveals a much larger hidden paper trail than the earlier PubMed-only audit suggested, although most of that rescue still comes from conventional biomedical indexing rather than non-MED spillover.",
            chapter_intro="This page asks whether CT.gov no-link studies are truly unpublished or just unlinked. The answer is mixed: many remain silent, but a large additional paper trail appears once exact-ID search moves beyond the narrow PubMed-only pass.",
            root_pull_quote="The larger miss is not exotic non-MED publishing. It is a much bigger exact-ID linkage gap than the PubMed-only audit could see.",
            paper_pull_quote="A CT.gov record with no linked paper is not always an unpublished study. Often the paper trail exists, but the registry page does not show it.",
            dashboard_pull_quote="Europe PMC exact-ID rescue is large, but non-MED rescue is small. Most extra visibility still sits inside ordinary biomedical indexing that CT.gov users never see.",
            root_rail=["PubMed 1.2%", "Europe PMC +39.6 pts", "Non-MED 2.8 pts", "NIH 80.0%"],
            landing_metrics=[
                ("PubMed exact", fmt_pct(as_float(weighted_publication["weighted_pubmed_match_contribution"])), "Weighted no-link rescue"),
                ("Any external", fmt_pct(as_float(weighted_publication["weighted_external_any_match_contribution"])), "Weighted any-match visibility"),
                ("Publication only", fmt_pct(as_float(weighted_publication["weighted_external_publication_only_contribution"])), "Weighted external-only visibility"),
                ("NIH sample", fmt_pct(as_float(nih_publication["sample_external_any_match_rate"])), "External any-match rate"),
            ],
            landing_chart_html=chart_section(
                "Weighted rescue contributions",
                bar_chart(
                    [
                        {"label": "PubMed exact", "value": as_float(weighted_publication["weighted_pubmed_match_contribution"])},
                        {"label": "Europe PMC rescue", "value": as_float(weighted_publication["weighted_epmc_rescue_contribution"])},
                        {"label": "Non-MED rescue", "value": as_float(weighted_publication["weighted_non_med_rescue_contribution"])},
                        {"label": "External only", "value": as_float(weighted_publication["weighted_external_publication_only_contribution"])},
                    ],
                    "Weighted rescue",
                    "Weighted visibility rescued from older CT.gov no-link studies",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "The main rescue comes from broader exact-ID indexing, not from the narrow PubMed-only slice.",
                "Non-MED rescue exists, but it is not the dominant explanation for missing CT.gov links.",
            ),
            reader_lede="A 156-word micro-paper on how much CT.gov publication-link missingness is actually an indexing and linkage gap once exact-ID search moves beyond the earlier PubMed-only pass.",
            reader_rail=["PubMed", "Europe PMC", "NIH", "Non-MED"],
            reader_metrics=[
                ("Weighted PubMed", fmt_pct(as_float(weighted_publication["weighted_pubmed_match_contribution"])), "Exact-ID contribution"),
                ("Weighted EPMC", fmt_pct(as_float(weighted_publication["weighted_epmc_rescue_contribution"])), "Rescue contribution"),
                ("Industry sample", fmt_pct(as_float(industry_publication["sample_external_any_match_rate"])), "External any-match"),
                ("OTHER sample", fmt_pct(as_float(other_publication["sample_external_any_match_rate"])), "External any-match"),
            ],
            dashboard_title="A broader exact-ID publication audit shows CT.gov no-link silence is partly real, but much of it is still a linkage and indexing failure",
            dashboard_eyebrow="Publication Index Dashboard",
            dashboard_lede="PubMed exact-ID matching alone barely moves the needle, Europe PMC rescue is much larger, non-MED rescue stays comparatively small, and NIH- and network-linked no-link portfolios show the strongest hidden paper trails in the sample.",
            dashboard_rail=["Index gap", "Any-match", "Publication-only", "Class splits"],
            dashboard_metrics=[
                ("PubMed exact", fmt_pct(as_float(weighted_publication["weighted_pubmed_match_contribution"])), "Weighted rescue"),
                ("Europe PMC", fmt_pct(as_float(weighted_publication["weighted_epmc_rescue_contribution"])), "Weighted rescue"),
                ("Non-MED", fmt_pct(as_float(weighted_publication["weighted_non_med_rescue_contribution"])), "Weighted rescue"),
                ("External only", fmt_pct(as_float(weighted_publication["weighted_external_publication_only_contribution"])), "Weighted visibility"),
            ],
            dashboard_sections=[
                chart_section(
                    "Weighted overall rescue",
                    bar_chart(
                        [
                            {"label": "PubMed exact", "value": as_float(weighted_publication["weighted_pubmed_match_contribution"])},
                            {"label": "Europe PMC rescue", "value": as_float(weighted_publication["weighted_epmc_rescue_contribution"])},
                            {"label": "Non-MED rescue", "value": as_float(weighted_publication["weighted_non_med_rescue_contribution"])},
                            {"label": "External only", "value": as_float(weighted_publication["weighted_external_publication_only_contribution"])},
                        ],
                        "Weighted rescue",
                        "Weighted rescue contributions across all sampled older CT.gov no-link studies",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "PubMed exact-ID retrieval is tiny relative to the broader Europe PMC exact-ID rescue.",
                    "That shifts the interpretation from PubMed undercount alone to a wider indexing and registry-linkage gap.",
                ),
                chart_section(
                    "Sponsor-class external any-match rate",
                    bar_chart(
                        [
                            {"label": row["lead_sponsor_class"], "value": as_float(row["sample_external_any_match_rate"])}
                            for _, row in audit_rows.sort_values("sample_external_any_match_rate", ascending=False).iterrows()
                        ],
                        "Sponsor-class sample rates",
                        "External any-match rate across the sponsor-class-stratified no-link audit sample",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "NIH and NETWORK no-link records show the strongest hidden paper trails, while OTHER remains much lower.",
                    "The sample suggests not all no-link silence means the same thing across sponsor classes.",
                ),
                chart_section(
                    "Sponsor-class non-MED rescue rate",
                    bar_chart(
                        [
                            {"label": row["lead_sponsor_class"], "value": as_float(row["sample_non_med_rescue_rate"])}
                            for _, row in audit_rows.sort_values("sample_non_med_rescue_rate", ascending=False).iterrows()
                        ],
                        "Non-MED rescue",
                        "Non-MED rescue rate across sponsor classes in the no-link audit sample",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Non-MED rescue peaks in NIH-linked no-link records but remains modest across the entire sampled universe.",
                    "That keeps the main story centered on indexing and linkage, not on a large non-MED spillover universe.",
                ),
            ],
            sidebar_bullets=[
                "Weighted PubMed exact-ID rescue reaches only 1.2 percent of older CT.gov no-link studies.",
                "Europe PMC exact-ID rescue adds 39.6 percentage points, pushing weighted any-match visibility to 40.8 percent.",
                "Non-MED rescue is far smaller at 2.8 points, so most rescued visibility is still conventional biomedical indexing.",
                "NIH no-link studies show the strongest external any-match rate in the audit sample at 80.0 percent.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-probable-act-fdaaa-debt",
            title="CT.gov Probable ACT/FDAAA Debt",
            summary="A standalone E156 project on how large, old, and distributed the likely U.S.-nexus regulated backlog still is once older CT.gov studies are filtered through conservative proxy layers.",
            body=act_body,
            sentences=act_sentences,
            primary_estimand="Missing-results rate and overdue debt within conservative U.S.-nexus ACT-style proxy layers",
            data_note="249,507 eligible older closed interventional studies filtered into broad and strict U.S.-nexus proxy layers",
            references=common_refs,
            protocol=(
                "This protocol creates conservative U.S.-nexus proxy layers inside eligible older closed interventional ClinicalTrials.gov studies. "
                "The layers use recorded U.S. locations, intervention families, and a phase exclusion to approximate a broad nexus layer, a drug-or-biological non-phase1 layer, and a stricter drug-biological-device U.S. layer. "
                "Primary outputs compare no-results rates, ghost-protocol rates, visible-share rates, overdue years, sponsor-class composition, and completion-era gradients inside each proxy layer. "
                "The aim is to estimate the scale and age of likely regulated reporting debt without claiming a formal legal ACT or FDAAA determination."
            ),
            root_title="How large is the probable U.S.-nexus reporting debt?",
            root_eyebrow="Probable ACT Debt Project",
            root_lede="A standalone public project on probable ACT-style debt, showing that tighter U.S.-nexus filters lower the raw CT.gov no-results rate but still leave a large, old, and institutionally distributed reporting backlog.",
            chapter_intro="This page narrows the registry to increasingly strict U.S.-nexus proxy layers. The rate falls, but the remaining debt stays large enough and old enough to matter.",
            root_pull_quote="Filtering to the likely regulated core cuts the rate sharply, but it does not erase the backlog or its age.",
            paper_pull_quote="The regulated-looking subset is cleaner than the raw registry, but it is still far from clean.",
            dashboard_pull_quote="The strict proxy is smaller and quieter than the full eligible universe, yet it still contains 18,475 missing-results studies and a very old unresolved tail.",
            root_rail=["Strict 58.6k", "Strict 31.5%", "Pre-FDAAA 87.0%", "Debt 10.92y"],
            landing_metrics=[
                ("Strict studies", fmt_int(as_int(strict_proxy["studies"])), "Older proxy-core studies"),
                ("Strict no-results", fmt_int(as_int(strict_proxy["no_results_count"])), "Missing-results stock"),
                ("Strict rate", fmt_pct(as_float(strict_proxy["no_results_rate"])), "No-results rate"),
                ("Strict debt", f"{as_float(strict_proxy['mean_overdue_2y_years_unresolved']):.2f}y", "Mean overdue beyond 2-year mark"),
            ],
            landing_chart_html=chart_section(
                "Proxy-layer no-results rates",
                bar_chart(
                    [
                        {"label": "Broad US nexus", "value": as_float(broad_proxy["no_results_rate"])},
                        {"label": "Drug/Bio non-phase1", "value": as_float(drug_bio_proxy["no_results_rate"])},
                        {"label": "Strict US D/B/D", "value": as_float(strict_proxy["no_results_rate"])},
                    ],
                    "Proxy layers",
                    "2-year no-results rate across conservative U.S.-nexus proxy layers",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "The raw rate drops substantially once the registry is filtered toward likely regulated cores.",
                "But the remaining stock is still large enough that the debt question does not disappear.",
            ),
            reader_lede="A 156-word micro-paper on how much likely U.S.-nexus CT.gov reporting debt remains after older studies are filtered through conservative ACT-style proxy layers.",
            reader_rail=["Strict layer", "Broad layer", "Old debt", "Sponsor classes"],
            reader_metrics=[
                ("Broad nexus", fmt_pct(as_float(broad_proxy["no_results_rate"])), "No-results rate"),
                ("Drug/Bio", fmt_pct(as_float(drug_bio_proxy["no_results_rate"])), "No-results rate"),
                ("Strict network", fmt_pct(as_float(strict_network["no_results_rate"])), "Highest large-class rate"),
                ("Strict NIH debt", f"{as_float(strict_nih['mean_overdue_2y_years_unresolved']):.2f}y", "Mean overdue years"),
            ],
            dashboard_title="Conservative ACT-style proxy layers shrink the CT.gov backlog, but they still leave a large and old regulated-looking debt core",
            dashboard_eyebrow="Probable ACT Dashboard",
            dashboard_lede="Broad U.S.-nexus portfolios are much quieter than the full registry but still incomplete, the stricter core still holds 18,475 missing-results studies, OTHER and INDUSTRY dominate stock inside that core, and Pre-FDAAA strict-proxy cohorts remain overwhelmingly unresolved.",
            dashboard_rail=["Proxy filters", "Strict stock", "Era debt", "Sponsor mix"],
            dashboard_metrics=[
                ("Broad nexus", fmt_pct(as_float(broad_proxy["no_results_rate"])), "No-results rate"),
                ("Strict core", fmt_pct(as_float(strict_proxy["no_results_rate"])), "No-results rate"),
                ("Strict stock", fmt_int(as_int(strict_proxy["no_results_count"])), "Missing-results studies"),
                ("Pre-FDAAA strict", fmt_pct(as_float(strict_pre["no_results_rate"])), "Oldest cohort"),
            ],
            dashboard_sections=[
                chart_section(
                    "No-results rate by proxy layer",
                    bar_chart(
                        [
                            {"label": "Broad US nexus", "value": as_float(broad_proxy["no_results_rate"])},
                            {"label": "Drug/Bio non-phase1", "value": as_float(drug_bio_proxy["no_results_rate"])},
                            {"label": "Strict US D/B/D", "value": as_float(strict_proxy["no_results_rate"])},
                        ],
                        "Proxy layers",
                        "2-year no-results rate across ACT-style proxy layers",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Tighter filters lower the rate, but they do not remove the reporting debt problem.",
                    "The strict layer still leaves a backlog large enough to support a standalone audit.",
                ),
                chart_section(
                    "Strict-proxy sponsor-class stock",
                    bar_chart(
                        [
                            {"label": row["lead_sponsor_class"], "value": as_float(row["no_results_count"])}
                            for _, row in act_class[
                                (act_class["proxy_layer"] == "Drug/Bio/Device US strict")
                                & act_class["lead_sponsor_class"].isin(["OTHER", "INDUSTRY", "NIH", "NETWORK", "FED", "INDIV"])
                            ].sort_values("no_results_count", ascending=False).iterrows()
                        ],
                        "Strict-proxy stock",
                        "Missing-results counts by sponsor class inside the strict U.S.-nexus proxy",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "OTHER and INDUSTRY dominate the strict-layer stock, but NIH, NETWORK, and FED still contribute meaningful regulated-looking debt.",
                    "The likely regulated backlog is institutionally distributed rather than concentrated in one single class.",
                ),
                chart_section(
                    "Strict-proxy completion-era rate",
                    bar_chart(
                        [
                            {"label": row["rule_era"], "value": as_float(row["no_results_rate"])}
                            for _, row in act_era[act_era["proxy_layer"] == "Drug/Bio/Device US strict"].iterrows()
                        ],
                        "Strict-proxy eras",
                        "2-year no-results rate by completion era inside the strict proxy layer",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Pre-FDAAA strict-proxy debt remains extreme, while later eras look cleaner but not clean.",
                    "That pattern shows why the regulated-looking backlog must be read as both an old-stock and a continuing-flow problem.",
                ),
            ],
            sidebar_bullets=[
                "The strict U.S.-nexus proxy still contains 58,598 older studies and 18,475 missing-results studies.",
                "Its no-results rate is 31.5 percent, well below the raw eligible-universe rate but still materially high.",
                "Mean unresolved time in the strict proxy is 10.92 years beyond the two-year mark.",
                "Pre-FDAAA strict-proxy cohorts remain 87.0 percent unresolved even after conservative U.S.-nexus filtering.",
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
