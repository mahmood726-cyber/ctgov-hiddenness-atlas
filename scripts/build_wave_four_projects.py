#!/usr/bin/env python3
"""Build wave-four standalone CT.gov projects from design, scale, and delay analyses."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct
from build_split_projects import chart_section, sentence_bundle, write_project

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name, keep_default_na=False)


def row_for(df: pd.DataFrame, column: str, value: str) -> pd.Series:
    return df[df[column] == value].iloc[0]


def main() -> None:
    size = load_csv("enrollment_size_visibility_older_2y.csv")
    size_sponsor = load_csv("enrollment_size_sponsor_class_older_2y.csv")
    purpose_size = load_csv("primary_purpose_size_older_2y.csv")
    location = load_csv("location_footprint_visibility_older_2y.csv")
    country = load_csv("country_footprint_visibility_older_2y.csv")
    phase_location = load_csv("phase_location_footprint_older_2y.csv")
    purpose = load_csv("primary_purpose_visibility_older_2y.csv")
    allocation = load_csv("allocation_visibility_older_2y.csv")
    delay = load_csv("completion_delay_visibility_older_2y.csv")
    delay_purpose = load_csv("completion_delay_purpose_older_2y.csv")
    arm = load_csv("arm_group_visibility_older_2y.csv")
    intervention = load_csv("intervention_count_visibility_older_2y.csv")
    phase_arm = load_csv("phase_arm_group_older_2y.csv")

    size_small = row_for(size, "size_bucket", "1-50")
    size_mid = row_for(size, "size_bucket", "101-500")
    size_large = row_for(size, "size_bucket", "1001-5000")
    size_other_large = size_sponsor[
        (size_sponsor["size_bucket"] == "1001-5000") & (size_sponsor["lead_sponsor_class"] == "OTHER")
    ].iloc[0]
    size_industry_large = size_sponsor[
        (size_sponsor["size_bucket"] == "1001-5000") & (size_sponsor["lead_sponsor_class"] == "INDUSTRY")
    ].iloc[0]
    treatment_small = purpose_size[
        (purpose_size["primary_purpose"] == "TREATMENT") & (purpose_size["size_bucket"] == "1-50")
    ].iloc[0]
    treatment_large = purpose_size[
        (purpose_size["primary_purpose"] == "TREATMENT") & (purpose_size["size_bucket"] == "1001-5000")
    ].iloc[0]

    location_single = row_for(location, "location_bucket", "Single-site")
    location_large = row_for(location, "location_bucket", "20+ sites")
    country_single = row_for(country, "country_bucket", "Single-country")
    country_large = row_for(country, "country_bucket", "20+ countries")
    phase3_single = phase_location[
        (phase_location["phase_label"] == "PHASE3") & (phase_location["location_bucket"] == "Single-site")
    ].iloc[0]
    phase3_large = phase_location[
        (phase_location["phase_label"] == "PHASE3") & (phase_location["location_bucket"] == "20+ sites")
    ].iloc[0]

    purpose_treatment = row_for(purpose, "primary_purpose", "TREATMENT")
    purpose_na = row_for(purpose, "primary_purpose", "NA")
    purpose_device = row_for(purpose, "primary_purpose", "DEVICE_FEASIBILITY")
    purpose_diag = row_for(purpose, "primary_purpose", "DIAGNOSTIC")
    alloc_random = row_for(allocation, "allocation", "RANDOMIZED")
    alloc_nonrandom = row_for(allocation, "allocation", "NON_RANDOMIZED")
    alloc_na = row_for(allocation, "allocation", "NA")

    delay_zero = row_for(delay, "delay_bucket", "0 years")
    delay_one = row_for(delay, "delay_bucket", "1 year")
    delay_23 = row_for(delay, "delay_bucket", "2-3 years")
    delay_610 = row_for(delay, "delay_bucket", "6-10 years")
    delay_11 = row_for(delay, "delay_bucket", "11+ years")
    delay_treatment_zero = delay_purpose[
        (delay_purpose["delay_bucket"] == "0 years") & (delay_purpose["primary_purpose"] == "TREATMENT")
    ].iloc[0]
    delay_treatment_610 = delay_purpose[
        (delay_purpose["delay_bucket"] == "6-10 years") & (delay_purpose["primary_purpose"] == "TREATMENT")
    ].iloc[0]
    delay_na_zero = delay_purpose[
        (delay_purpose["delay_bucket"] == "0 years") & (delay_purpose["primary_purpose"] == "NA")
    ].iloc[0]
    delay_na_610 = delay_purpose[
        (delay_purpose["delay_bucket"] == "6-10 years") & (delay_purpose["primary_purpose"] == "NA")
    ].iloc[0]

    arm_one = row_for(arm, "arm_bucket", "1 arm")
    arm_two = row_for(arm, "arm_bucket", "2 arms")
    arm_many = row_for(arm, "arm_bucket", "10+ arms")
    intervention_one = row_for(intervention, "intervention_bucket", "1 intervention")
    phase1_one = phase_arm[(phase_arm["phase_label"] == "PHASE1") & (phase_arm["arm_bucket"] == "1 arm")].iloc[0]
    phase1_many = phase_arm[(phase_arm["phase_label"] == "PHASE1") & (phase_arm["arm_bucket"] == "10+ arms")].iloc[0]
    phase3_one = phase_arm[(phase_arm["phase_label"] == "PHASE3") & (phase_arm["arm_bucket"] == "1 arm")].iloc[0]
    phase3_many = phase_arm[(phase_arm["phase_label"] == "PHASE3") & (phase_arm["arm_bucket"] == "10+ arms")].iloc[0]

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
    ]
    series_links = [
        {
            "repo_name": item["repo_name"],
            "title": item["title"],
            "summary": item["summary"],
            "short_title": item["short_title"],
            "pages_url": f"https://{REPO_OWNER}.github.io/{item['repo_name']}/",
        }
        for item in all_series_specs
    ]
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    size_body, size_sentences = sentence_bundle(
        [
            ("Question", "How much of ClinicalTrials.gov hiddenness tracks trial enrollment size once older closed interventional studies are grouped into comparable size buckets?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and binned them by recorded enrollment."),
            ("Method", "The project compares two-year no-results rates, ghost-protocol rates, full visibility, and sponsor-class contrasts across enrollment buckets from 1-50 through 5,001+ participants."),
            ("Primary result", "Studies enrolling 1 to 50 participants showed a 73.2 percent no-results rate and a 47.6 percent ghost-protocol rate."),
            ("Secondary result", "Studies enrolling 1,001 to 5,000 participants fell to 62.4 percent no results and 18.7 percent ghost protocols, while large OTHER-sponsored studies still remained highly obscured."),
            ("Interpretation", "Trial scale therefore matters, but size alone does not erase sponsor-driven reporting debt within the public registry surface. That pattern persists across tiny studies and surprisingly large nonindustry backlogs alike."),
            ("Boundary", "Enrollment is registry-recorded and can be missing, estimated, or misclassified, so these buckets describe visible scale rather than adjudicated participant counts."),
        ]
    )
    geography_body, geography_sentences = sentence_bundle(
        [
            ("Question", "How much more visible are larger multi-site and multinational trials on ClinicalTrials.gov than single-site studies once older closed interventional records are isolated?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and grouped them by site and country footprint."),
            ("Method", "The project compares two-year no-results rates, ghost-protocol rates, full visibility, and phase-specific contrasts across location and country buckets."),
            ("Primary result", "Single-site studies showed a 79.5 percent no-results rate, whereas studies with 20 or more sites fell to 31.7 percent."),
            ("Secondary result", "Among phase III trials, single-site studies reached 76.3 percent no results while 20-plus-site trials fell to 25.7 percent on the same metric."),
            ("Interpretation", "Geography footprint therefore behaves like a strong visibility gradient rather than a decorative field count inside the registry. The gap survives even within late-phase trials that should be easiest to see."),
            ("Boundary", "Site and country counts come from sponsor-entered location metadata and may not capture every participating site or all multinational operational detail."),
        ]
    )
    purpose_body, purpose_sentences = sentence_bundle(
        [
            ("Question", "Which primary purposes look quietest on ClinicalTrials.gov once older closed interventional studies are grouped by stated design intent?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and compared sponsor-entered purpose and allocation fields."),
            ("Method", "The project estimates two-year no-results rates, ghost-protocol rates, full visibility, and allocation contrasts across treatment, prevention, diagnostic, supportive-care, and unlabeled purpose groups."),
            ("Primary result", "Treatment trials showed a 68.3 percent no-results rate and a 40.5 percent ghost-protocol rate."),
            ("Secondary result", "Trials with no recorded primary purpose rose to 86.4 percent no results and 59.2 percent ghost protocols, while device-feasibility studies also remained highly obscured."),
            ("Interpretation", "Design intent therefore matters, and blank or underspecified purpose fields mark especially quiet registry segments. Unlabeled intent behaves like a durable warning sign for weak public documentation and low disclosure across sponsors and phases alike."),
            ("Boundary", "Primary-purpose and allocation fields are sponsor-entered labels rather than externally audited design adjudications, so the analysis remains registry-structural rather than legal."),
        ]
    )
    delay_body, delay_sentences = sentence_bundle(
        [
            ("Question", "Does ClinicalTrials.gov hiddenness fall as trials take longer from first submission to completion, or do short-cycle studies report just as well?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and calculated submission-to-completion delay buckets."),
            ("Method", "The project compares two-year no-results rates, ghost-protocol rates, full visibility, and purpose-specific contrasts across registration-to-completion intervals."),
            ("Primary result", "Studies completed in the same calendar year they were first submitted showed an 85.7 percent no-results rate and a 54.1 percent ghost-protocol rate."),
            ("Secondary result", "Studies with a 6 to 10 year delay fell to 57.6 percent no results and 28.8 percent ghost protocols, with long-lag treatment studies also looking substantially cleaner."),
            ("Interpretation", "Fast-cycle studies therefore look most hidden, suggesting short operational timelines are not translating into faster public reporting. The contrast remains visible across treatment studies and other major purpose groups."),
            ("Boundary", "Submission-to-completion lag is a registry proxy for operational duration and can reflect backfilled dates, protocol amendments, or changing trial mix."),
        ]
    )
    architecture_body, architecture_sentences = sentence_bundle(
        [
            ("Question", "How much does trial architecture shape ClinicalTrials.gov hiddenness once older closed interventional studies are grouped by arms and intervention counts?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and grouped them by arm-group and intervention counts."),
            ("Method", "The project compares two-year no-results rates, ghost-protocol rates, hiddenness scores, and phase-specific contrasts across simple and complex trial architectures."),
            ("Primary result", "One-arm studies showed a 72.8 percent no-results rate, a 48.5 percent ghost-protocol rate, and a hiddenness score of 3.44."),
            ("Secondary result", "Studies with 10 or more arms fell to 55.3 percent no results, while one-intervention studies remained quieter than trials with larger intervention counts."),
            ("Interpretation", "Simpler-looking architectures are therefore not more transparent and often sit inside much quieter registry segments. That pattern holds in both early-phase work and later confirmatory programs with broader designs in practice today."),
            ("Boundary", "Arm and intervention counts are registry structure fields and do not capture protocol nuance, adaptive features, or downstream analytic complexity."),
        ]
    )

    projects: list[dict[str, object]] = [
        {
            "repo_name": "ctgov-enrollment-size-gap",
            "title": "CT.gov Enrollment-Size Gap",
            "summary": "A standalone E156 project on how enrollment size maps onto older-study visibility, ghost protocols, and sponsor-class contrasts.",
            "body": size_body,
            "sentences": size_sentences,
            "primary_estimand": "2-year no-results rate across enrollment-size buckets among eligible older CT.gov studies",
            "data_note": "249,507 eligible older closed interventional studies grouped into enrollment-size buckets",
            "references": common_refs,
            "protocol": (
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies into enrollment-size buckets using recorded registry enrollment counts. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and fully visible shares across size buckets, with secondary contrasts by sponsor class and treatment-purpose studies. "
                "The aim is to test whether public visibility changes with visible trial scale rather than treating all older studies as exchangeable. "
                "Because enrollment is a registry field that can be missing or estimated, the project describes recorded scale rather than adjudicated final participant counts."
            ),
            "root_title": "Are smaller registered trials much quieter on CT.gov?",
            "root_eyebrow": "Enrollment Project",
            "root_lede": "A standalone public project on how enrollment size maps onto missing results, ghost protocols, and the visibility gap between small and large older studies.",
            "chapter_intro": "This page borrows the cohort-taxonomy logic from your small-sample methods work and applies it to CT.gov: not effect heterogeneity, but visibility heterogeneity by recorded trial scale.",
            "root_pull_quote": "Small registered studies remain far quieter than larger trials, but size does not fully rescue the biggest sponsor-class backlogs.",
            "root_pull_source": "Enrollment-size comparison",
            "paper_pull_quote": "Trial scale matters, but size alone does not solve the registry's hiddenness problem.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "Enrollment size is one of the clearest structural gradients in the registry once older studies are isolated.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": ["1-50: 73.2%", "1001-5000: 62.4%", "Ghosts 47.6%", "Large OTHER 81.5%"],
            "landing_metrics": [
                ("1-50 studies", fmt_int(as_int(size_small["studies"])), "Smallest common bucket"),
                ("1-50 no results", fmt_pct(as_float(size_small["no_results_rate"])), "2-year no-results"),
                ("1001-5000 no results", fmt_pct(as_float(size_large["no_results_rate"])), "Large-study benchmark"),
                ("1001-5000 ghosts", fmt_pct(as_float(size_large["ghost_protocol_rate"])), "Ghost-protocol rate"),
            ],
            "landing_chart_html": chart_section(
                "No-results by size",
                bar_chart(
                    [{"label": row["size_bucket"], "value": as_float(row["no_results_rate"])} for _, row in size[size["size_bucket"] != "Missing"].iterrows()],
                    "Enrollment-size buckets",
                    "2-year no-results rate by recorded enrollment size",
                    "value",
                    "label",
                    "#c3452f",
                    percent=True,
                ),
                "The main size gradient runs downward as trials get larger, though the largest bucket does not fully flatten the problem.",
                "Size behaves like a visibility axis here, similar to how small-k analyses expose instability in your other methods projects.",
            ),
            "reader_lede": "A 156-word micro-paper on how recorded enrollment size maps onto missing results and ghost protocols in older CT.gov studies.",
            "reader_rail": ["1-50", "101-500", "1001-5000", "Size still not enough"],
            "reader_metrics": [
                ("1-50 no results", fmt_pct(as_float(size_small["no_results_rate"])), "Small-study bucket"),
                ("101-500 no results", fmt_pct(as_float(size_mid["no_results_rate"])), "Middle benchmark"),
                ("1001-5000 no results", fmt_pct(as_float(size_large["no_results_rate"])), "Large benchmark"),
                ("OTHER 1001-5000", fmt_pct(as_float(size_other_large["no_results_rate"])), "Large OTHER studies"),
            ],
            "dashboard_title": "Visibility improves with trial scale, but large size does not erase every sponsor backlog",
            "dashboard_eyebrow": "Enrollment Dashboard",
            "dashboard_lede": "Recorded enrollment size is a strong visibility gradient in CT.gov, yet large OTHER-sponsored studies remain heavily obscured despite scale.",
            "dashboard_rail": ["No results", "Ghosts", "Treatment only", "Sponsor contrast"],
            "dashboard_metrics": [
                ("1-50 no results", fmt_pct(as_float(size_small["no_results_rate"])), "Small-study bucket"),
                ("1001-5000 ghosts", fmt_pct(as_float(size_large["ghost_protocol_rate"])), "Large-study ghost rate"),
                ("Treatment 1-50", fmt_pct(as_float(treatment_small["no_results_rate"])), "Treatment-only small bucket"),
                ("Treatment 1001-5000", fmt_pct(as_float(treatment_large["no_results_rate"])), "Treatment-only large bucket"),
            ],
            "dashboard_sections": [
                chart_section(
                    "No-results by size",
                    bar_chart(
                        [{"label": row["size_bucket"], "value": as_float(row["no_results_rate"])} for _, row in size[size["size_bucket"] != "Missing"].iterrows()],
                        "Enrollment-size buckets",
                        "2-year no-results rate by recorded enrollment size",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Older studies get materially quieter as recorded enrollment falls.",
                    "This is the public-facing version of a scale gradient: the smallest studies carry the heaviest reporting debt.",
                ),
                chart_section(
                    "Ghost protocols by size",
                    bar_chart(
                        [{"label": row["size_bucket"], "value": as_float(row["ghost_protocol_rate"])} for _, row in size[size["size_bucket"] != "Missing"].iterrows()],
                        "Ghost-protocol rates",
                        "Share of older studies with neither results nor publication by size bucket",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "The ghost-protocol gradient is steeper than the no-results gradient and collapses among larger studies.",
                    "Publication-only visibility explains some of the gap, but the combined ghost metric keeps the hidden zone visible.",
                ),
                chart_section(
                    "Treatment and sponsor contrast",
                    bar_chart(
                        [
                            {"label": "Treatment | 1-50", "value": as_float(treatment_small["no_results_rate"])},
                            {"label": "Treatment | 1001-5000", "value": as_float(treatment_large["no_results_rate"])},
                            {"label": "INDUSTRY | 1001-5000", "value": as_float(size_industry_large["no_results_rate"])},
                            {"label": "OTHER | 1001-5000", "value": as_float(size_other_large["no_results_rate"])},
                        ],
                        "Within-bucket contrast",
                        "Large-size treatment and sponsor-class contrasts inside the size gradient",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "The size effect remains within treatment trials, but large OTHER-sponsored studies still look far worse than large industry studies.",
                    "This panel matters because pure size could otherwise be mistaken for a sponsor-mix artifact.",
                ),
            ],
            "sidebar_bullets": [
                "Studies enrolling 1 to 50 participants reach 73.2 percent on the 2-year no-results metric.",
                "The same metric falls to 62.4 percent in the 1,001 to 5,000 bucket.",
                "Ghost protocols drop from 47.6 percent to 18.7 percent across those buckets.",
                "Large OTHER-sponsored studies still sit at 81.5 percent on the no-results metric.",
            ],
        },
        {
            "repo_name": "ctgov-geography-scale-visibility",
            "title": "CT.gov Geography-Scale Visibility",
            "summary": "A standalone E156 project on how site and country footprint map onto older-study visibility and phase-specific reporting gaps.",
            "body": geography_body,
            "sentences": geography_sentences,
            "primary_estimand": "2-year no-results rate across site-footprint buckets among eligible older CT.gov studies",
            "data_note": "249,507 eligible older closed interventional studies grouped by site and country footprint",
            "references": common_refs,
            "protocol": (
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies by recorded site and country footprint. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and fully visible shares across single-site through 20-plus-site buckets, with secondary country-footprint and phase-specific contrasts. "
                "The aim is to test whether larger trial geographies map onto a more visible public record. "
                "Because site and country counts are registry-entered metadata, the project measures visible footprint rather than verified operational complexity."
            ),
            "root_title": "Does a larger trial geography make CT.gov more visible?",
            "root_eyebrow": "Geography Project",
            "root_lede": "A standalone public project on site and country footprint, showing how much older single-site trials differ from large multi-site and multinational studies.",
            "chapter_intro": "This page uses the footprint logic from your pathway and cohort work, but here the question is public visibility: whether broader operational scale leaves a clearer record behind.",
            "root_pull_quote": "Single-site trials are dramatically quieter than large multi-site studies, even within the same major phases.",
            "root_pull_source": "Site-footprint comparison",
            "paper_pull_quote": "Geography acts like a structural visibility gradient, not just a descriptive location field.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "Once site footprint is plotted, the registry stops looking flat and starts looking stratified by operational scale.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": ["Single-site 79.5%", "20+ sites 31.7%", "Phase III 76.3% to 25.7%", "20+ countries 11.7%"],
            "landing_metrics": [
                ("Single-site", fmt_int(as_int(location_single["studies"])), "Older studies"),
                ("Single-site no results", fmt_pct(as_float(location_single["no_results_rate"])), "2-year no-results"),
                ("20+ sites no results", fmt_pct(as_float(location_large["no_results_rate"])), "Large-footprint benchmark"),
                ("20+ sites visible", fmt_pct(as_float(location_large["results_publication_visible_rate"])), "Results plus publication"),
            ],
            "landing_chart_html": chart_section(
                "Site footprint",
                bar_chart(
                    [{"label": row["location_bucket"], "value": as_float(row["no_results_rate"])} for _, row in location.iterrows()],
                    "Site footprint",
                    "2-year no-results rate by recorded site footprint",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "The drop from single-site to 20-plus-site studies is one of the sharpest gradients in the atlas.",
                "Geography scale is doing real analytic work here, not just describing trial logistics.",
            ),
            "reader_lede": "A 156-word micro-paper on how site and country footprint map onto missing results and visibility in older CT.gov studies.",
            "reader_rail": ["Single-site", "20+ sites", "Single-country", "Phase III contrast"],
            "reader_metrics": [
                ("Single-site no results", fmt_pct(as_float(location_single["no_results_rate"])), "Site-footprint baseline"),
                ("20+ sites no results", fmt_pct(as_float(location_large["no_results_rate"])), "Large site footprint"),
                ("Single-country no results", fmt_pct(as_float(country_single["no_results_rate"])), "Country-footprint baseline"),
                ("20+ countries no results", fmt_pct(as_float(country_large["no_results_rate"])), "Large country footprint"),
            ],
            "dashboard_title": "Geography scale maps onto a much more visible registry record",
            "dashboard_eyebrow": "Geography Dashboard",
            "dashboard_lede": "Older multi-site and multinational studies look far more visible than single-site trials, and the gap remains visible within major phases.",
            "dashboard_rail": ["Site footprint", "Country footprint", "Full visibility", "Within phase"],
            "dashboard_metrics": [
                ("Single-site no results", fmt_pct(as_float(location_single["no_results_rate"])), "Older single-site studies"),
                ("20+ sites no results", fmt_pct(as_float(location_large["no_results_rate"])), "Large site-footprint studies"),
                ("Phase III single-site", fmt_pct(as_float(phase3_single["no_results_rate"])), "Phase III baseline"),
                ("Phase III 20+ sites", fmt_pct(as_float(phase3_large["no_results_rate"])), "Phase III large-footprint"),
            ],
            "dashboard_sections": [
                chart_section(
                    "Site footprint",
                    bar_chart(
                        [{"label": row["location_bucket"], "value": as_float(row["no_results_rate"])} for _, row in location.iterrows()],
                        "Site footprint",
                        "2-year no-results rate by recorded site footprint",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Single-site and missing-location studies sit in the quietest part of the registry.",
                    "The 20-plus-site bucket looks very different because large operational footprints also carry much higher full-visibility rates.",
                ),
                chart_section(
                    "Country footprint",
                    bar_chart(
                        [{"label": row["country_bucket"], "value": as_float(row["no_results_rate"])} for _, row in country.iterrows()],
                        "Country footprint",
                        "2-year no-results rate by recorded country footprint",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "The multinational gradient is even steeper at the high end, with the 20-plus-country bucket far more visible than single-country studies.",
                    "Country footprint is a simpler public proxy for operational reach, and it tells the same story as site footprint.",
                ),
                chart_section(
                    "Within-phase contrast",
                    bar_chart(
                        [
                            {"label": "PHASE1 | single", "value": as_float(phase_location[(phase_location["phase_label"] == "PHASE1") & (phase_location["location_bucket"] == "Single-site")].iloc[0]["no_results_rate"])},
                            {"label": "PHASE1 | 20+", "value": as_float(phase_location[(phase_location["phase_label"] == "PHASE1") & (phase_location["location_bucket"] == "20+ sites")].iloc[0]["no_results_rate"])},
                            {"label": "PHASE3 | single", "value": as_float(phase3_single["no_results_rate"])},
                            {"label": "PHASE3 | 20+", "value": as_float(phase3_large["no_results_rate"])},
                            {"label": "NA | single", "value": as_float(phase_location[(phase_location["phase_label"] == "NA") & (phase_location["location_bucket"] == "Single-site")].iloc[0]["no_results_rate"])},
                            {"label": "NA | 20+", "value": as_float(phase_location[(phase_location["phase_label"] == "NA") & (phase_location["location_bucket"] == "20+ sites")].iloc[0]["no_results_rate"])},
                        ],
                        "Phase and footprint",
                        "Selected within-phase no-results rates for single-site versus 20-plus-site studies",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "The site-footprint advantage survives inside the major phases rather than disappearing as pure phase mix.",
                    "That makes the geography signal harder to dismiss as a compositional artifact.",
                ),
            ],
            "sidebar_bullets": [
                "Single-site studies reach 79.5 percent on the 2-year no-results metric.",
                "Studies with 20 or more sites fall to 31.7 percent on the same metric.",
                "Phase III single-site studies sit at 76.3 percent versus 25.7 percent for phase III studies with 20 or more sites.",
                "Studies spanning 20 or more countries fall to 11.7 percent on the no-results metric.",
            ],
        },
        {
            "repo_name": "ctgov-design-purpose-hiddenness",
            "title": "CT.gov Design-Purpose Hiddenness",
            "summary": "A standalone E156 project on which trial purposes and allocation labels remain most obscured in older CT.gov studies.",
            "body": purpose_body,
            "sentences": purpose_sentences,
            "primary_estimand": "2-year no-results rate across primary-purpose groups among eligible older CT.gov studies",
            "data_note": "249,507 eligible older closed interventional studies grouped by primary purpose and allocation",
            "references": common_refs,
            "protocol": (
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies by sponsor-entered primary-purpose and allocation fields. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and full visibility across major purpose buckets, with a secondary allocation contrast and size-within-purpose view. "
                "The aim is to test whether design intent corresponds to different public visibility profiles rather than treating all interventional studies as one bucket. "
                "Because purpose and allocation are sponsor-entered labels, the project measures registry-design labeling rather than externally audited trial design."
            ),
            "root_title": "Which kinds of trials stay quietest on CT.gov?",
            "root_eyebrow": "Purpose Project",
            "root_lede": "A standalone public project on design purpose and allocation, showing which trial intents remain most hidden in older ClinicalTrials.gov records.",
            "chapter_intro": "This project applies the classification logic from your broader methods work to a simple registry question: which sponsor-entered trial purposes correspond to the quietest public record.",
            "root_pull_quote": "Treatment trials are quieter than they should be, but unlabeled and device-feasibility studies are quieter still.",
            "root_pull_source": "Purpose comparison",
            "paper_pull_quote": "Blank or underspecified purpose fields are one of the clearest structural warning signs in the registry.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "Purpose labels are not just metadata; they split the registry into visibly different transparency regimes.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": ["Treatment 68.3%", "NA 86.4%", "Device 84.1%", "Non-randomized ghosts 47.3%"],
            "landing_metrics": [
                ("Treatment no results", fmt_pct(as_float(purpose_treatment["no_results_rate"])), "Largest purpose group"),
                ("Treatment ghosts", fmt_pct(as_float(purpose_treatment["ghost_protocol_rate"])), "Neither visible"),
                ("NA no results", fmt_pct(as_float(purpose_na["no_results_rate"])), "No recorded purpose"),
                ("Device ghosts", fmt_pct(as_float(purpose_device["ghost_protocol_rate"])), "Device-feasibility ghost rate"),
            ],
            "landing_chart_html": chart_section(
                "No-results by purpose",
                bar_chart(
                    [{"label": row["primary_purpose"], "value": as_float(row["no_results_rate"])} for _, row in purpose.iterrows()],
                    "Primary purpose",
                    "2-year no-results rate by sponsor-entered primary purpose",
                    "value",
                    "label",
                    "#c3452f",
                    percent=True,
                ),
                "Treatment dominates by stock, but several less-common purpose buckets look visibly quieter on rate.",
                "The unlabeled NA bucket matters because it marks both weak design labeling and very poor visibility at the same time.",
            ),
            "reader_lede": "A 156-word micro-paper on how primary purpose and allocation map onto missing results and ghost protocols in older CT.gov studies.",
            "reader_rail": ["Treatment", "Diagnostic", "Device feasibility", "No purpose field"],
            "reader_metrics": [
                ("Treatment no results", fmt_pct(as_float(purpose_treatment["no_results_rate"])), "Largest purpose group"),
                ("Diagnostic ghosts", fmt_pct(as_float(purpose_diag["ghost_protocol_rate"])), "Diagnostic ghost rate"),
                ("Device no results", fmt_pct(as_float(purpose_device["no_results_rate"])), "Device-feasibility"),
                ("NA ghosts", fmt_pct(as_float(purpose_na["ghost_protocol_rate"])), "No recorded purpose"),
            ],
            "dashboard_title": "Design intent and missing design labels split the registry into different hiddenness regimes",
            "dashboard_eyebrow": "Purpose Dashboard",
            "dashboard_lede": "Older CT.gov studies differ sharply by sponsor-entered purpose fields, and blank purpose labels are among the quietest segments in the registry.",
            "dashboard_rail": ["Purpose rates", "Ghosts", "Allocation", "Treatment scale"],
            "dashboard_metrics": [
                ("Treatment no results", fmt_pct(as_float(purpose_treatment["no_results_rate"])), "Largest purpose group"),
                ("NA no results", fmt_pct(as_float(purpose_na["no_results_rate"])), "No recorded purpose"),
                ("Non-randomized ghosts", fmt_pct(as_float(alloc_nonrandom["ghost_protocol_rate"])), "Allocation contrast"),
                ("Randomized visible", fmt_pct(as_float(alloc_random["results_publication_visible_rate"])), "Results plus publication"),
            ],
            "dashboard_sections": [
                chart_section(
                    "No-results by purpose",
                    bar_chart(
                        [{"label": row["primary_purpose"], "value": as_float(row["no_results_rate"])} for _, row in purpose.iterrows()],
                        "Primary purpose",
                        "2-year no-results rate by sponsor-entered primary purpose",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "The treatment bucket is large and still poor, but the unlabeled NA group is quieter still.",
                    "This page is designed to separate common high-stock purposes from smaller but more extreme purpose buckets.",
                ),
                chart_section(
                    "Ghost protocols by purpose",
                    bar_chart(
                        [{"label": row["primary_purpose"], "value": as_float(row["ghost_protocol_rate"])} for _, row in purpose.iterrows()],
                        "Purpose ghosts",
                        "Ghost-protocol rate by primary purpose",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Diagnostic, basic-science, device-feasibility, and unlabeled studies sit high on the ghost metric.",
                    "The ghost view matters because a purpose bucket can have some publication rescue without looking truly transparent.",
                ),
                chart_section(
                    "Allocation and treatment scale",
                    bar_chart(
                        [
                            {"label": "Randomized", "value": as_float(alloc_random["no_results_rate"])},
                            {"label": "Non-randomized", "value": as_float(alloc_nonrandom["no_results_rate"])},
                            {"label": "Allocation NA", "value": as_float(alloc_na["no_results_rate"])},
                            {"label": "Treatment | 1-50", "value": as_float(treatment_small["no_results_rate"])},
                            {"label": "Treatment | 1001-5000", "value": as_float(treatment_large["no_results_rate"])},
                        ],
                        "Allocation and size",
                        "Allocation labels and treatment-size contrasts",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Non-randomized studies and missing allocation labels are both quieter than randomized studies, while treatment trials still improve with size.",
                    "This keeps the purpose page tied to a concrete within-purpose structural gradient rather than a flat list of labels.",
                ),
            ],
            "sidebar_bullets": [
                "Treatment trials reach 68.3 percent on the 2-year no-results metric.",
                "Trials with no recorded primary purpose rise to 86.4 percent and 59.2 percent ghost protocols.",
                "Device-feasibility trials reach 84.1 percent on the no-results metric.",
                "Non-randomized studies reach 47.3 percent on the ghost-protocol metric.",
            ],
        },
        {
            "repo_name": "ctgov-completion-delay-debt",
            "title": "CT.gov Completion-Delay Debt",
            "summary": "A standalone E156 project on how registration-to-completion timing maps onto older-study hiddenness and fast-cycle reporting debt.",
            "body": delay_body,
            "sentences": delay_sentences,
            "primary_estimand": "2-year no-results rate across registration-to-completion delay buckets among eligible older CT.gov studies",
            "data_note": "249,507 eligible older closed interventional studies grouped by submission-to-completion delay",
            "references": common_refs,
            "protocol": (
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies by the delay between study first submission and primary completion. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and full visibility across delay buckets, with a secondary contrast for treatment and unlabeled-purpose studies. "
                "The aim is to test whether shorter operational cycles also correspond to faster public reporting. "
                "Because submission and completion dates can be backfilled or revised, the delay measure is a registry-timing proxy rather than a validated operational duration audit."
            ),
            "root_title": "Do short-cycle trials actually report faster on CT.gov?",
            "root_eyebrow": "Delay Project",
            "root_lede": "A standalone public project on registration-to-completion timing, showing that fast-cycle studies can carry the heaviest reporting debt.",
            "chapter_intro": "This page takes the temporal-trend logic from your evidence-decay work and turns it into an operational timing question: what happens when a trial moves from first submission to completion very quickly.",
            "root_pull_quote": "The shortest submission-to-completion intervals are the quietest part of the older CT.gov record.",
            "root_pull_source": "Completion-delay comparison",
            "paper_pull_quote": "A fast study cycle does not translate into a fast public record.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "Delay buckets make the registry look less like one backlog and more like a timing-stratified reporting system.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": ["0 years 85.7%", "6-10 years 57.6%", "Ghosts 54.1%", "Treatment improves with lag"],
            "landing_metrics": [
                ("0 years", fmt_int(as_int(delay_zero["studies"])), "Fast-cycle studies"),
                ("0-year no results", fmt_pct(as_float(delay_zero["no_results_rate"])), "2-year no-results"),
                ("6-10-year no results", fmt_pct(as_float(delay_610["no_results_rate"])), "Longer-cycle benchmark"),
                ("11+ visible", fmt_pct(as_float(delay_11["results_publication_visible_rate"])), "Small long-lag tail"),
            ],
            "landing_chart_html": chart_section(
                "No-results by delay",
                bar_chart(
                    [{"label": row["delay_bucket"], "value": as_float(row["no_results_rate"])} for _, row in delay.iterrows()],
                    "Submission-to-completion delay",
                    "2-year no-results rate by registration-to-completion interval",
                    "value",
                    "label",
                    "#c3452f",
                    percent=True,
                ),
                "The same-year bucket is visibly worse than every longer-delay bucket in the series.",
                "This is the operational mirror of evidence-decay work: not older evidence rotting, but fast-cycle studies failing to become visible quickly.",
            ),
            "reader_lede": "A 156-word micro-paper on how submission-to-completion delay maps onto older-study missing results and ghost protocols on CT.gov.",
            "reader_rail": ["0 years", "1 year", "2-3 years", "6-10 years"],
            "reader_metrics": [
                ("0-year no results", fmt_pct(as_float(delay_zero["no_results_rate"])), "Fast-cycle bucket"),
                ("1-year no results", fmt_pct(as_float(delay_one["no_results_rate"])), "Near-fast bucket"),
                ("2-3-year no results", fmt_pct(as_float(delay_23["no_results_rate"])), "Middle benchmark"),
                ("6-10-year ghosts", fmt_pct(as_float(delay_610["ghost_protocol_rate"])), "Longer-cycle ghost rate"),
            ],
            "dashboard_title": "Fast-cycle trials carry the heaviest reporting debt in older CT.gov cohorts",
            "dashboard_eyebrow": "Delay Dashboard",
            "dashboard_lede": "Submission-to-completion timing is a strong visibility gradient: studies completed in the same year they are first submitted are the quietest older bucket in the registry.",
            "dashboard_rail": ["No results", "Ghosts", "Visible share", "Purpose contrast"],
            "dashboard_metrics": [
                ("0-year no results", fmt_pct(as_float(delay_zero["no_results_rate"])), "Fast-cycle studies"),
                ("0-year ghosts", fmt_pct(as_float(delay_zero["ghost_protocol_rate"])), "Neither visible"),
                ("6-10-year no results", fmt_pct(as_float(delay_610["no_results_rate"])), "Longer-cycle benchmark"),
                ("6-10-year visible", fmt_pct(as_float(delay_610["results_publication_visible_rate"])), "Results plus publication"),
            ],
            "dashboard_sections": [
                chart_section(
                    "No-results by delay",
                    bar_chart(
                        [{"label": row["delay_bucket"], "value": as_float(row["no_results_rate"])} for _, row in delay.iterrows()],
                        "Delay buckets",
                        "2-year no-results rate by submission-to-completion interval",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "The fastest operational bucket is the worst reporting bucket in the series.",
                    "The main comparison is across delay buckets because it turns dates into a clear operational-timing signal.",
                ),
                chart_section(
                    "Ghost protocols by delay",
                    bar_chart(
                        [{"label": row["delay_bucket"], "value": as_float(row["ghost_protocol_rate"])} for _, row in delay.iterrows()],
                        "Delay ghosts",
                        "Ghost-protocol rate by submission-to-completion interval",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Ghost protocols decline steadily as delay lengthens, suggesting fast-cycle studies are not simply publishing elsewhere.",
                    "The ghost metric keeps the focus on total visible absence rather than missing results alone.",
                ),
                chart_section(
                    "Purpose contrast",
                    bar_chart(
                        [
                            {"label": "Treatment | 0", "value": as_float(delay_treatment_zero["no_results_rate"])},
                            {"label": "Treatment | 6-10", "value": as_float(delay_treatment_610["no_results_rate"])},
                            {"label": "NA | 0", "value": as_float(delay_na_zero["no_results_rate"])},
                            {"label": "NA | 6-10", "value": as_float(delay_na_610["no_results_rate"])},
                        ],
                        "Purpose within delay",
                        "Selected purpose contrasts inside the delay gradient",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Treatment studies improve sharply as delay lengthens, while unlabeled-purpose studies stay poor even with longer lag.",
                    "This keeps the delay page tied to design structure rather than leaving it as a pure date story.",
                ),
            ],
            "sidebar_bullets": [
                "Studies completed in the same year they were first submitted reach 85.7 percent on the 2-year no-results metric.",
                "That bucket also reaches 54.1 percent on the ghost-protocol metric.",
                "Studies with 6 to 10 years of delay fall to 57.6 percent no results and 28.8 percent ghost protocols.",
                "Longer lag improves treatment trials much more than unlabeled-purpose studies.",
            ],
        },
        {
            "repo_name": "ctgov-trial-architecture-gap",
            "title": "CT.gov Trial-Architecture Gap",
            "summary": "A standalone E156 project on how arm count and intervention count map onto older-study hiddenness in CT.gov.",
            "body": architecture_body,
            "sentences": architecture_sentences,
            "primary_estimand": "2-year no-results rate across arm-group buckets among eligible older CT.gov studies",
            "data_note": "249,507 eligible older closed interventional studies grouped by arm-group and intervention-count architecture",
            "references": common_refs,
            "protocol": (
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies by arm-group count and intervention count. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and hiddenness scores across simple and complex architectures, with a secondary phase-specific arm-count contrast. "
                "The aim is to test whether simpler protocol structure corresponds to a more visible public record. "
                "Because arm and intervention counts are registry structure fields, the project measures declared architecture rather than full protocol complexity."
            ),
            "root_title": "Are simpler trial architectures actually more visible on CT.gov?",
            "root_eyebrow": "Architecture Project",
            "root_lede": "A standalone public project on arm counts and intervention counts, showing that simpler-looking older studies are often the quietest registry segment.",
            "chapter_intro": "This page uses the design-structure logic from your methods work and applies it to CT.gov architecture fields: how many arms and interventions a trial declares, and what that predicts about visibility.",
            "root_pull_quote": "One-arm and one-intervention studies are not cleaner registry citizens. They are often the quietest.",
            "root_pull_source": "Architecture comparison",
            "paper_pull_quote": "Simple protocol structure should not be mistaken for transparent public reporting.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "Arm counts and intervention counts expose a structural quiet zone that would be invisible in a sponsor-only reading.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": ["1 arm 72.8%", "10+ arms 55.3%", "1 intervention 78.7%", "PHASE1 one-arm 88.5%"],
            "landing_metrics": [
                ("1-arm studies", fmt_int(as_int(arm_one["studies"])), "Largest architecture bucket"),
                ("1-arm no results", fmt_pct(as_float(arm_one["no_results_rate"])), "2-year no-results"),
                ("10+ arms no results", fmt_pct(as_float(arm_many["no_results_rate"])), "Complex-arm benchmark"),
                ("1-arm hiddenness", f"{as_float(arm_one['hiddenness_score_mean']):.2f}", "Mean hiddenness score"),
            ],
            "landing_chart_html": chart_section(
                "No-results by arm count",
                bar_chart(
                    [{"label": row["arm_bucket"], "value": as_float(row["no_results_rate"])} for _, row in arm.iterrows()],
                    "Arm-group architecture",
                    "2-year no-results rate by arm-group count",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "The architecture gradient runs in the opposite direction from a naive simplicity story: fewer arms often means less visibility.",
                "This makes arm count a useful structural marker rather than a cosmetic protocol field.",
            ),
            "reader_lede": "A 156-word micro-paper on how arm counts and intervention counts map onto missing results and hiddenness in older CT.gov studies.",
            "reader_rail": ["1 arm", "2 arms", "10+ arms", "1 intervention"],
            "reader_metrics": [
                ("1-arm no results", fmt_pct(as_float(arm_one["no_results_rate"])), "Smallest architecture"),
                ("2-arm no results", fmt_pct(as_float(arm_two["no_results_rate"])), "Largest common architecture"),
                ("10+ arms no results", fmt_pct(as_float(arm_many["no_results_rate"])), "Large architecture"),
                ("1-intervention no results", fmt_pct(as_float(intervention_one["no_results_rate"])), "Single intervention"),
            ],
            "dashboard_title": "Simpler-looking trial architectures often sit in the quietest registry segments",
            "dashboard_eyebrow": "Architecture Dashboard",
            "dashboard_lede": "Older one-arm and one-intervention studies remain much quieter than more elaborate architectures, and the pattern persists within major phases.",
            "dashboard_rail": ["Arm counts", "Interventions", "Phase contrast", "Hiddenness score"],
            "dashboard_metrics": [
                ("1-arm no results", fmt_pct(as_float(arm_one["no_results_rate"])), "Smallest architecture"),
                ("10+ arms no results", fmt_pct(as_float(arm_many["no_results_rate"])), "Largest architecture"),
                ("1-intervention ghosts", fmt_pct(as_float(intervention_one["ghost_protocol_rate"])), "Single intervention"),
                ("PHASE1 one-arm", fmt_pct(as_float(phase1_one["no_results_rate"])), "Within-phase architecture"),
            ],
            "dashboard_sections": [
                chart_section(
                    "Arm-group architecture",
                    bar_chart(
                        [{"label": row["arm_bucket"], "value": as_float(row["no_results_rate"])} for _, row in arm.iterrows()],
                        "Arm buckets",
                        "2-year no-results rate by arm-group count",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "One-arm studies are not the clean edge case of the registry. They are one of its quietest structural segments.",
                    "The architecture page starts with arm count because it is the clearest public marker of protocol simplicity.",
                ),
                chart_section(
                    "Intervention count",
                    bar_chart(
                        [{"label": row["intervention_bucket"], "value": as_float(row["no_results_rate"])} for _, row in intervention.iterrows()],
                        "Intervention buckets",
                        "2-year no-results rate by intervention count",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Single-intervention studies are also much quieter than more complex intervention structures.",
                    "The intervention count chart keeps the architecture story from depending on arm groups alone.",
                ),
                chart_section(
                    "Within-phase architecture",
                    bar_chart(
                        [
                            {"label": "PHASE1 | 1 arm", "value": as_float(phase1_one["no_results_rate"])},
                            {"label": "PHASE1 | 10+ arms", "value": as_float(phase1_many["no_results_rate"])},
                            {"label": "PHASE3 | 1 arm", "value": as_float(phase3_one["no_results_rate"])},
                            {"label": "PHASE3 | 10+ arms", "value": as_float(phase3_many["no_results_rate"])},
                        ],
                        "Phase and arm count",
                        "Selected within-phase no-results rates for one-arm and 10-plus-arm studies",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "The architecture gap remains visible inside both early and later phases rather than collapsing into pure phase mix.",
                    "That makes the architecture signal a real structural layer in the registry rather than just a side effect of phase.",
                ),
            ],
            "sidebar_bullets": [
                "One-arm studies reach 72.8 percent on the 2-year no-results metric.",
                "Studies with 10 or more arms fall to 55.3 percent on the same metric.",
                "Single-intervention studies reach 78.7 percent on the no-results metric.",
                "Within phase I, one-arm studies sit at 88.5 percent versus 65.6 percent for studies with 10 or more arms.",
            ],
        },
    ]

    for spec in projects:
        spec["repo_url"] = f"https://github.com/{REPO_OWNER}/{spec['repo_name']}"
        spec["pages_url"] = f"https://{REPO_OWNER}.github.io/{spec['repo_name']}/"
        spec["series_hub_url"] = series_hub_url
        spec["series_links"] = series_links
        path = write_project(spec)
        print(f"Built {path}")


if __name__ == "__main__":
    main()
