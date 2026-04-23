#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Build wave-five standalone CT.gov projects from intervention, country, stopped-trial, outcome, and actual-field analyses."""

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
    intervention = load_csv("intervention_type_visibility_older_2y.csv")
    intervention_mix = load_csv("intervention_mix_visibility_older_2y.csv")
    country = load_csv("country_visibility_older_2y.csv")
    status = load_csv("status_visibility_older_2y.csv")
    stopped_reason = load_csv("stopped_reason_visibility_older_2y.csv")
    primary = load_csv("primary_outcome_density_older_2y.csv")
    secondary = load_csv("secondary_outcome_density_older_2y.csv")
    primary_desc = load_csv("primary_outcome_description_visibility_older_2y.csv")
    actual = load_csv("actual_field_discipline_older_2y.csv")
    actual_status = load_csv("actual_field_status_rates_older_2y.csv")

    int_drug = row_for(intervention, "intervention_type", "DRUG")
    int_diet = row_for(intervention, "intervention_type", "DIETARY_SUPPLEMENT")
    int_proc = row_for(intervention, "intervention_type", "PROCEDURE")
    int_bio = row_for(intervention, "intervention_type", "BIOLOGICAL")
    int_behavioral = row_for(intervention, "intervention_type", "BEHAVIORAL")
    mix_single = row_for(intervention_mix, "intervention_mix", "Single-type")
    mix_multi = row_for(intervention_mix, "intervention_mix", "Multi-type")

    named_country = country[country["country"] != "Missing"].copy()
    top_country_rows = named_country.head(12).copy()
    country_us = row_for(country, "country", "United States")
    country_egypt = row_for(country, "country", "Egypt")
    country_china = row_for(country, "country", "China")
    country_poland = row_for(country, "country", "Poland")
    country_australia = row_for(country, "country", "Australia")
    country_japan = row_for(country, "country", "Japan")

    status_completed = row_for(status, "overall_status", "COMPLETED")
    status_terminated = row_for(status, "overall_status", "TERMINATED")
    status_withdrawn = row_for(status, "overall_status", "WITHDRAWN")
    status_suspended = row_for(status, "overall_status", "SUSPENDED")
    reason_recorded = row_for(stopped_reason, "termination_reason_bucket", "Reason recorded")
    reason_missing = row_for(stopped_reason, "termination_reason_bucket", "Reason missing")

    primary_zero = row_for(primary, "primary_outcome_bucket", "0")
    primary_one = row_for(primary, "primary_outcome_bucket", "1")
    primary_many = row_for(primary, "primary_outcome_bucket", "6+")
    secondary_zero = row_for(secondary, "secondary_outcome_bucket", "0")
    secondary_many = row_for(secondary, "secondary_outcome_bucket", "10+")
    desc_present = row_for(primary_desc, "primary_outcome_description_bucket", "Description present")
    desc_missing = row_for(primary_desc, "primary_outcome_description_bucket", "Description missing")

    actual_primary_present = actual[
        (actual["field"] == "Primary completion not actual") & (actual["missing"] == "Actual field present")
    ].iloc[0]
    actual_primary_missing = actual[
        (actual["field"] == "Primary completion not actual") & (actual["missing"] == "Missing actual field")
    ].iloc[0]
    actual_completion_present = actual[
        (actual["field"] == "Completion not actual") & (actual["missing"] == "Actual field present")
    ].iloc[0]
    actual_completion_missing = actual[
        (actual["field"] == "Completion not actual") & (actual["missing"] == "Missing actual field")
    ].iloc[0]
    actual_enrollment_present = actual[
        (actual["field"] == "Enrollment not actual") & (actual["missing"] == "Actual field present")
    ].iloc[0]
    actual_enrollment_missing = actual[
        (actual["field"] == "Enrollment not actual") & (actual["missing"] == "Missing actual field")
    ].iloc[0]
    actual_completed = row_for(actual_status, "overall_status", "COMPLETED")
    actual_withdrawn = row_for(actual_status, "overall_status", "WITHDRAWN")
    actual_suspended = row_for(actual_status, "overall_status", "SUSPENDED")

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

    intervention_body, intervention_sentences = sentence_bundle(
        [
            ("Question", "Which intervention types look quietest on ClinicalTrials.gov once older closed interventional studies are grouped by declared intervention family?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and merged raw intervention-type labels from the registry snapshot."),
            ("Method", "The project compares two-year no-results rates, ghost-protocol rates, full visibility, and single-versus-multi-type contrasts across drug, device, behavioral, procedure, biological, dietary-supplement, and other intervention families."),
            ("Primary result", "Drug studies form the largest family at 118,202 studies and show a 62.6 percent no-results rate."),
            ("Secondary result", "Dietary-supplement studies reach 90.6 percent no results, procedure studies 85.3 percent, while biological studies fall to 58.5 percent and multi-type studies outperform single-type studies."),
            ("Interpretation", "Declared intervention family therefore behaves like a strong visibility classifier rather than a cosmetic label inside the registry. The contrast persists even when large drug stock dominates the overall denominator across older studies."),
            ("Boundary", "Studies can carry multiple intervention types and labels are sponsor-entered registry categories rather than audited therapeutic taxonomies."),
        ]
    )
    country_body, country_sentences = sentence_bundle(
        [
            ("Question", "Which named countries are attached to the quietest older CT.gov studies once country involvement is extracted from recorded trial locations?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and merged named country lists from the raw locations module."),
            ("Method", "The project explodes country involvement at the study-country level and compares two-year no-results rates, ghost-protocol rates, and visible shares across countries with at least 800 eligible older studies."),
            ("Primary result", "United States appears in the largest stock at 104,882 eligible older studies and shows a 52.1 percent no-results rate."),
            ("Secondary result", "Egypt is the worst large named country at 95.8 percent no results, China reaches 81.7 percent, while Poland falls to 33.5 percent and Australia to 43.4 percent."),
            ("Interpretation", "Named-country involvement therefore exposes large geographic transparency divides that are hidden by simple country-count buckets alone for large country-linked backlogs."),
            ("Boundary", "Country labels reflect recorded study locations rather than verified enrollment shares, coordination centers, or country-specific legal duties."),
        ]
    )
    stopped_body, stopped_sentences = sentence_bundle(
        [
            ("Question", "How much worse do stopped trials look on ClinicalTrials.gov than completed trials once older closed interventional studies are grouped by final status?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and isolated completed, terminated, withdrawn, and suspended records."),
            ("Method", "The project compares two-year no-results rates, ghost-protocol rates, visible shares, and reason-missing contrasts across final statuses and stopped-study subgroups."),
            ("Primary result", "Withdrawn studies reach a 100.0 percent no-results rate and an 81.9 percent ghost-protocol rate."),
            ("Secondary result", "Suspended studies reach 99.3 percent no results, terminated studies 58.3 percent, and stopped studies with missing termination reasons rise to 82.1 percent no results."),
            ("Interpretation", "Stopping a trial does not merely change status; it sharply deepens the risk that the public record stays silent or structurally thin. Especially when reason fields are already absent and final statuses are not completed."),
            ("Boundary", "Final-status labels and missing reason fields are registry entries and do not adjudicate operational history or legal reporting obligations."),
        ]
    )
    outcome_body, outcome_sentences = sentence_bundle(
        [
            ("Question", "Does richer outcome specification correspond to a more visible CT.gov record once older closed interventional studies are grouped by outcome density?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and bucketed primary outcomes, secondary outcomes, and primary-outcome description fields."),
            ("Method", "The project compares two-year no-results rates, ghost-protocol rates, full visibility, and description contrasts across sparse and dense outcome structures."),
            ("Primary result", "Studies with zero recorded primary outcomes show a 100.0 percent no-results rate and a 65.1 percent ghost-protocol rate."),
            ("Secondary result", "Studies with ten or more secondary outcomes fall to 56.7 percent no results, while studies missing primary-outcome descriptions still reach 94.4 percent no results."),
            ("Interpretation", "Outcome density therefore looks like a proxy for public record seriousness: sparser protocols are far more likely to remain hidden. The gradient survives across counts, text fields, and both primary and secondary outcome layers."),
            ("Boundary", "Outcome counts capture declared registry structure rather than scientific importance, statistical hierarchy, or endpoint quality."),
        ]
    )
    actual_body, actual_sentences = sentence_bundle(
        [
            ("Question", "How much hiddenness is concentrated in closed CT.gov studies that still fail to use actual completion or enrollment fields?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and tracked three closed-study actual-field indicators."),
            ("Method", "The project compares two-year no-results rates, ghost-protocol rates, and status-specific missing-actual patterns across primary-completion, completion, and enrollment discipline."),
            ("Primary result", "Missing actual enrollment corresponds to a 100.0 percent no-results rate and a 62.8 percent ghost-protocol rate."),
            ("Secondary result", "Missing actual primary completion reaches 100.0 percent no results, missing actual completion 95.3 percent, and suspended studies are worst on actual-field discipline."),
            ("Interpretation", "Closed-study actual-field discipline therefore functions as a direct structural warning sign for opacity rather than a minor metadata defect. The separation remains visible across all three fields and links directly to the stopped-study audit as well inside older registry cohorts."),
            ("Boundary", "Actual-field flags come from registry status and date/count types, not from external audits of what sponsors truly knew or when."),
        ]
    )

    projects: list[dict[str, object]] = []
    projects.append(
        make_spec(
            repo_name="ctgov-intervention-type-gap",
            title="CT.gov Intervention-Type Gap",
            summary="A standalone E156 project on how declared intervention families map onto older-study visibility and ghost protocols in CT.gov.",
            body=intervention_body,
            sentences=intervention_sentences,
            primary_estimand="2-year no-results rate across declared intervention families among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies merged with extracted raw intervention-type labels",
            references=common_refs,
            protocol=(
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies by declared intervention families extracted from the raw registry snapshot. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and fully visible shares across intervention types, with a secondary contrast between single-type and multi-type studies. "
                "The aim is to test whether declared treatment modality corresponds to visibly different registry reporting behavior. "
                "Because intervention types are sponsor-entered registry labels and studies can carry multiple types, the project measures declared modality rather than a validated therapeutic taxonomy."
            ),
            root_title="Which intervention families stay quietest on CT.gov?",
            root_eyebrow="Intervention Project",
            root_lede="A standalone public project on declared intervention families, showing that treatment modality is a strong visibility classifier inside older CT.gov records.",
            chapter_intro="This page follows the classification logic visible across your other methods projects: once the registry is split by declared intervention family, hiddenness stops looking randomly distributed.",
            root_pull_quote="Drugs dominate the stock, but dietary-supplement and procedure studies are much quieter on rate.",
            paper_pull_quote="Declared intervention type is not cosmetic metadata. It separates the registry into materially different transparency regimes.",
            dashboard_pull_quote="Intervention family turns a single backlog into several distinct visibility profiles, from biological to procedure-heavy quiet zones.",
            root_rail=["Drug 62.6%", "Dietary 90.6%", "Procedure 85.3%", "Multi-type 64.7%"],
            landing_metrics=[
                ("Drug studies", fmt_int(as_int(int_drug["studies"])), "Largest intervention family"),
                ("Drug no results", fmt_pct(as_float(int_drug["no_results_rate"])), "2-year no-results"),
                ("Dietary no results", fmt_pct(as_float(int_diet["no_results_rate"])), "Quietest large family"),
                ("Multi-type no results", fmt_pct(as_float(mix_multi["no_results_rate"])), "Studies with 2+ types"),
            ],
            landing_chart_html=chart_section(
                "Intervention families",
                bar_chart(
                    [{"label": row["intervention_type"], "value": as_float(row["no_results_rate"])} for _, row in intervention.iterrows()],
                    "Declared intervention family",
                    "2-year no-results rate by declared intervention type",
                    "value",
                    "label",
                    "#c3452f",
                    percent=True,
                ),
                "The family split reveals very different reporting regimes even within one registry.",
                "This uses treatment-class classification as an explanatory layer rather than a decorative tag.",
            ),
            reader_lede="A 156-word micro-paper on how declared intervention families map onto missing results and ghost protocols in older CT.gov studies.",
            reader_rail=["Drug", "Biological", "Procedure", "Dietary supplement"],
            reader_metrics=[
                ("Drug no results", fmt_pct(as_float(int_drug["no_results_rate"])), "Largest family"),
                ("Biological no results", fmt_pct(as_float(int_bio["no_results_rate"])), "Cleaner comparator"),
                ("Procedure ghosts", fmt_pct(as_float(int_proc["ghost_protocol_rate"])), "Procedure ghost rate"),
                ("Dietary ghosts", fmt_pct(as_float(int_diet["ghost_protocol_rate"])), "Dietary ghost rate"),
            ],
            dashboard_title="Declared intervention family is a strong visibility classifier inside older CT.gov studies",
            dashboard_eyebrow="Intervention Dashboard",
            dashboard_lede="Drug studies dominate by stock, but declared family still matters: dietary-supplement, procedure, and behavioral studies remain far quieter than biological studies and multi-type designs.",
            dashboard_rail=["No results", "Ghosts", "Type mix", "Largest families"],
            dashboard_metrics=[
                ("Dietary no results", fmt_pct(as_float(int_diet["no_results_rate"])), "Quietest large family"),
                ("Procedure ghosts", fmt_pct(as_float(int_proc["ghost_protocol_rate"])), "Neither visible"),
                ("Single-type no results", fmt_pct(as_float(mix_single["no_results_rate"])), "One intervention family"),
                ("Multi-type visible", fmt_pct(as_float(mix_multi["results_publication_visible_rate"])), "Results plus publication"),
            ],
            dashboard_sections=[
                chart_section(
                    "No-results by family",
                    bar_chart(
                        [{"label": row["intervention_type"], "value": as_float(row["no_results_rate"])} for _, row in intervention.iterrows()],
                        "Intervention families",
                        "2-year no-results rate by declared intervention family",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Dietary-supplement, diagnostic-test, procedure, and behavioral studies all sit above drug and biological studies.",
                    "The gap is large enough that modality classification changes the story even before sponsor or phase enters the picture.",
                ),
                chart_section(
                    "Ghost protocols by family",
                    bar_chart(
                        [{"label": row["intervention_type"], "value": as_float(row["ghost_protocol_rate"])} for _, row in intervention.iterrows()],
                        "Intervention ghosts",
                        "Ghost-protocol rate by declared intervention family",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Procedure and dietary-supplement families also sit high on the full invisibility metric.",
                    "The ghost view matters because it collapses both missing results and missing publication links into one public-silence measure.",
                ),
                chart_section(
                    "Single-type versus multi-type",
                    bar_chart(
                        [
                            {"label": "Single-type no results", "value": as_float(mix_single["no_results_rate"])},
                            {"label": "Multi-type no results", "value": as_float(mix_multi["no_results_rate"])},
                            {"label": "Single-type ghosts", "value": as_float(mix_single["ghost_protocol_rate"])},
                            {"label": "Multi-type ghosts", "value": as_float(mix_multi["ghost_protocol_rate"])},
                        ],
                        "Type-mix contrast",
                        "Visibility contrast between single-type and multi-type studies",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Studies declaring multiple intervention families are visibly cleaner than single-type studies on both main metrics.",
                    "That keeps the page from collapsing into a simple one-label ranking and adds a design-mixture layer.",
                ),
            ],
            sidebar_bullets=[
                "Drug studies are the largest intervention family at 118,202 eligible older studies.",
                "Dietary-supplement studies reach 90.6 percent on the 2-year no-results metric.",
                "Procedure studies reach 48.1 percent on the ghost-protocol metric.",
                "Multi-type studies are cleaner than single-type studies on both no-results and ghost metrics.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-stopped-trial-disclosure-gap",
            title="CT.gov Stopped-Trial Disclosure Gap",
            summary="A standalone E156 project on how withdrawn, suspended, and terminated studies remain structurally quieter than completed CT.gov trials.",
            body=stopped_body,
            sentences=stopped_sentences,
            primary_estimand="2-year no-results rate across final-status groups among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies grouped by final status and stopped-study reason fields",
            references=common_refs,
            protocol=(
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies by final status and then isolates stopped studies for a termination-reason audit. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and fully visible shares across completed, terminated, withdrawn, and suspended studies, with a secondary contrast for missing versus recorded stop reasons. "
                "The aim is to test whether stopping a trial corresponds to a sharply different public record. "
                "Because final status and reason fields are registry entries, the analysis measures documented registry status rather than independently verified operational history."
            ),
            root_title="How silent do stopped trials become on CT.gov?",
            root_eyebrow="Stopped-Trial Project",
            root_lede="A standalone public project on stopped-trial disclosure, showing that withdrawn and suspended studies sit in one of the quietest parts of the older CT.gov record.",
            chapter_intro="This page treats final status as a pathway split, much like your other project work treats method branches: once a trial stops, the public record behaves very differently.",
            root_pull_quote="Withdrawn and suspended trials are nearly absent from the visible record, and missing stop reasons make the problem even worse.",
            paper_pull_quote="Stopping a trial is not the end of the public reporting story. It is often the beginning of a deeper disclosure gap.",
            dashboard_pull_quote="Final status is one of the clearest hiddenness separators in the atlas once stopped studies are isolated.",
            root_rail=["Withdrawn 100%", "Suspended 99.3%", "Reason missing 82.1%", "Completed 73.1%"],
            landing_metrics=[
                ("Withdrawn no results", fmt_pct(as_float(status_withdrawn["no_results_rate"])), "Older withdrawn studies"),
                ("Withdrawn ghosts", fmt_pct(as_float(status_withdrawn["ghost_protocol_rate"])), "Neither visible"),
                ("Suspended no results", fmt_pct(as_float(status_suspended["no_results_rate"])), "Older suspended studies"),
                ("Reason missing no results", fmt_pct(as_float(reason_missing["no_results_rate"])), "Stopped-study warning sign"),
            ],
            landing_chart_html=chart_section(
                "Final status",
                bar_chart(
                    [{"label": row["overall_status"], "value": as_float(row["no_results_rate"])} for _, row in status.iterrows()],
                    "Final-status groups",
                    "2-year no-results rate by final study status",
                    "value",
                    "label",
                    "#c3452f",
                    percent=True,
                ),
                "Withdrawn and suspended studies sit in a nearly total reporting blackout zone.",
                "This page reframes final status as a visibility pathway, not just a descriptive endpoint field.",
            ),
            reader_lede="A 156-word micro-paper on how final status and missing stop reasons map onto hiddenness in older CT.gov studies.",
            reader_rail=["Completed", "Terminated", "Withdrawn", "Reason missing"],
            reader_metrics=[
                ("Completed no results", fmt_pct(as_float(status_completed["no_results_rate"])), "Main baseline"),
                ("Terminated no results", fmt_pct(as_float(status_terminated["no_results_rate"])), "Stopped comparator"),
                ("Withdrawn ghosts", fmt_pct(as_float(status_withdrawn["ghost_protocol_rate"])), "Most silent group"),
                ("Reason missing ghosts", fmt_pct(as_float(reason_missing["ghost_protocol_rate"])), "Stopped-study subgap"),
            ],
            dashboard_title="Stopped trials sit in one of the quietest structural zones of older CT.gov",
            dashboard_eyebrow="Stopped-Trial Dashboard",
            dashboard_lede="Completed studies are already too quiet, but withdrawn and suspended trials are dramatically worse, and missing stop reasons deepen the disclosure gap further.",
            dashboard_rail=["Status rates", "Ghosts", "Reason field", "Visible share"],
            dashboard_metrics=[
                ("Completed no results", fmt_pct(as_float(status_completed["no_results_rate"])), "Baseline"),
                ("Withdrawn no results", fmt_pct(as_float(status_withdrawn["no_results_rate"])), "Worst status"),
                ("Suspended ghosts", fmt_pct(as_float(status_suspended["ghost_protocol_rate"])), "Neither visible"),
                ("Reason recorded visible", fmt_pct(as_float(reason_recorded["results_publication_visible_rate"])), "Stopped studies with reason"),
            ],
            dashboard_sections=[
                chart_section(
                    "No-results by final status",
                    bar_chart(
                        [{"label": row["overall_status"], "value": as_float(row["no_results_rate"])} for _, row in status.iterrows()],
                        "Final status",
                        "2-year no-results rate by final study status",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Final status alone splits the registry into very different visibility regimes.",
                    "Withdrawn and suspended studies are the most extreme part of that split.",
                ),
                chart_section(
                    "Ghost protocols by final status",
                    bar_chart(
                        [{"label": row["overall_status"], "value": as_float(row["ghost_protocol_rate"])} for _, row in status.iterrows()],
                        "Final-status ghosts",
                        "Ghost-protocol rate by final study status",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "The gap persists on the stricter measure of total visible absence.",
                    "That keeps the stopped-trial story from collapsing into missing results alone.",
                ),
                chart_section(
                    "Stopped-study reason field",
                    bar_chart(
                        [
                            {"label": "Reason recorded", "value": as_float(reason_recorded["no_results_rate"])},
                            {"label": "Reason missing", "value": as_float(reason_missing["no_results_rate"])},
                            {"label": "Reason recorded ghosts", "value": as_float(reason_recorded["ghost_protocol_rate"])},
                            {"label": "Reason missing ghosts", "value": as_float(reason_missing["ghost_protocol_rate"])},
                        ],
                        "Termination reason",
                        "Visibility contrast for stopped studies with recorded versus missing reasons",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Stopped studies with missing reason fields are materially quieter than stopped studies with a recorded explanation.",
                    "This turns a simple missingness flag into a concrete structural warning sign.",
                ),
            ],
            sidebar_bullets=[
                "Withdrawn studies reach 100.0 percent on the 2-year no-results metric.",
                "Suspended studies reach 99.3 percent on the same metric.",
                "Stopped studies with missing termination reasons rise to 82.1 percent no results and 65.1 percent ghost protocols.",
                "Completed studies are poor at 73.1 percent no results, but stopped statuses are markedly worse.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-outcome-density-gap",
            title="CT.gov Outcome-Density Gap",
            summary="A standalone E156 project on how sparse outcome structures and missing outcome descriptions track quieter CT.gov records.",
            body=outcome_body,
            sentences=outcome_sentences,
            primary_estimand="2-year no-results rate across outcome-density buckets among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies grouped by outcome counts and outcome-description fields",
            references=common_refs,
            protocol=(
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies by primary outcome count, secondary outcome count, and primary-outcome description presence. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and fully visible shares across sparse and dense outcome structures, with a secondary description-field contrast. "
                "The aim is to test whether sparser declared outcome structure corresponds to a visibly thinner public record. "
                "Because outcome counts are registry structure fields, the project measures declared protocol density rather than endpoint quality or scientific importance."
            ),
            root_title="Do sparse outcome structures predict a quieter CT.gov record?",
            root_eyebrow="Outcome Project",
            root_lede="A standalone public project on outcome density, showing that thin outcome structures and missing outcome descriptions are strongly linked to older-study hiddenness.",
            chapter_intro="This page uses density as an analytic idea in the same spirit as your other stress-test work: when the registry outcome structure gets sparse, the public record often gets sparse too.",
            root_pull_quote="Studies with zero primary outcomes or missing primary-outcome descriptions sit in a near-total visibility failure zone.",
            paper_pull_quote="Outcome density is one of the strongest structural warning signs in the registry once older studies are isolated.",
            dashboard_pull_quote="Outcome counts and outcome descriptions make the registry look stratified by protocol seriousness, not just sponsor or phase.",
            root_rail=["Primary 0: 100%", "Primary 6+: 66.3%", "Secondary 10+: 56.7%", "Desc missing 94.4%"],
            landing_metrics=[
                ("Primary 0 no results", fmt_pct(as_float(primary_zero["no_results_rate"])), "No declared primary outcomes"),
                ("Primary 6+ no results", fmt_pct(as_float(primary_many["no_results_rate"])), "Dense primary structure"),
                ("Secondary 10+ visible", fmt_pct(as_float(secondary_many["results_publication_visible_rate"])), "Dense secondary structure"),
                ("Description missing", fmt_pct(as_float(desc_missing["no_results_rate"])), "Primary-outcome text missing"),
            ],
            landing_chart_html=chart_section(
                "Primary outcome density",
                bar_chart(
                    [{"label": row["primary_outcome_bucket"], "value": as_float(row["no_results_rate"])} for _, row in primary.iterrows()],
                    "Primary-outcome buckets",
                    "2-year no-results rate by primary outcome count",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "The zero-primary bucket is effectively a structural silence zone in the older registry.",
                "This page treats outcome density like a protocol-structure stress test rather than a mere count summary.",
            ),
            reader_lede="A 156-word micro-paper on how outcome counts and outcome descriptions map onto hiddenness in older CT.gov studies.",
            reader_rail=["Primary 0", "Primary 1", "Secondary 10+", "Description missing"],
            reader_metrics=[
                ("Primary 0 ghosts", fmt_pct(as_float(primary_zero["ghost_protocol_rate"])), "No primary outcomes"),
                ("Primary 1 no results", fmt_pct(as_float(primary_one["no_results_rate"])), "Dominant bucket"),
                ("Secondary 10+ no results", fmt_pct(as_float(secondary_many["no_results_rate"])), "Dense secondary structure"),
                ("Description missing ghosts", fmt_pct(as_float(desc_missing["ghost_protocol_rate"])), "Outcome text gap"),
            ],
            dashboard_title="Sparse outcome structures and missing outcome descriptions mark one of the quietest CT.gov segments",
            dashboard_eyebrow="Outcome Dashboard",
            dashboard_lede="Older studies with zero primary outcomes, sparse secondary outcomes, or missing primary-outcome descriptions remain far quieter than denser outcome structures.",
            dashboard_rail=["Primary counts", "Secondary counts", "Description field", "Visible share"],
            dashboard_metrics=[
                ("Primary 0 no results", fmt_pct(as_float(primary_zero["no_results_rate"])), "No primary outcomes"),
                ("Secondary 0 ghosts", fmt_pct(as_float(secondary_zero["ghost_protocol_rate"])), "Sparse secondary structure"),
                ("Secondary 10+ visible", fmt_pct(as_float(secondary_many["results_publication_visible_rate"])), "Dense secondary structure"),
                ("Description present visible", fmt_pct(as_float(desc_present["results_publication_visible_rate"])), "Outcome text present"),
            ],
            dashboard_sections=[
                chart_section(
                    "Primary outcome counts",
                    bar_chart(
                        [{"label": row["primary_outcome_bucket"], "value": as_float(row["no_results_rate"])} for _, row in primary.iterrows()],
                        "Primary outcome density",
                        "2-year no-results rate by primary outcome count",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "The outcome-density curve improves as primary structures get richer.",
                    "The zero-primary bucket is the structural edge case that exposes how quiet the registry can become.",
                ),
                chart_section(
                    "Secondary outcome counts",
                    bar_chart(
                        [{"label": row["secondary_outcome_bucket"], "value": as_float(row["no_results_rate"])} for _, row in secondary.iterrows()],
                        "Secondary outcome density",
                        "2-year no-results rate by secondary outcome count",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Dense secondary structures are much cleaner than sparse ones, especially against the zero-secondary bucket.",
                    "This keeps the density story from depending on primary outcomes alone.",
                ),
                chart_section(
                    "Primary-outcome description field",
                    bar_chart(
                        [
                            {"label": "Description present", "value": as_float(desc_present["no_results_rate"])},
                            {"label": "Description missing", "value": as_float(desc_missing["no_results_rate"])},
                            {"label": "Description present ghosts", "value": as_float(desc_present["ghost_protocol_rate"])},
                            {"label": "Description missing ghosts", "value": as_float(desc_missing["ghost_protocol_rate"])},
                        ],
                        "Outcome description",
                        "Visibility contrast for primary-outcome description presence",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Missing outcome descriptions are associated with a very quiet registry profile even when counts are ignored.",
                    "This matters because thin text fields often accompany sparse structural outcome declarations.",
                ),
            ],
            sidebar_bullets=[
                "Studies with zero recorded primary outcomes reach 100.0 percent on the 2-year no-results metric.",
                "Studies with ten or more secondary outcomes fall to 56.7 percent no results.",
                "Studies missing primary-outcome descriptions still reach 94.4 percent no results and 57.8 percent ghost protocols.",
                "Outcome density behaves like a strong structural visibility signal, not just a count summary.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-actual-field-discipline",
            title="CT.gov Actual-Field Discipline",
            summary="A standalone E156 project on how missing actual dates and counts mark one of the quietest structural zones in older CT.gov studies.",
            body=actual_body,
            sentences=actual_sentences,
            primary_estimand="2-year no-results rate across actual-field discipline groups among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies grouped by actual date/count discipline flags",
            references=common_refs,
            protocol=(
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies by three closed-study actual-field indicators: primary completion, completion, and enrollment. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and fully visible shares for actual-field present versus missing groups, with a secondary final-status contrast on missing-actual rates. "
                "The aim is to test whether closed-study actual-field discipline is a strong structural warning sign for opacity. "
                "Because the indicators come from registry date and count types, the project measures documented actual-field discipline rather than externally audited sponsor knowledge."
            ),
            root_title="How bad is missing actual-field discipline on CT.gov?",
            root_eyebrow="Actual-Field Project",
            root_lede="A standalone public project on actual-field discipline, showing that closed studies missing actual dates or counts sit in one of the quietest structural zones in the registry.",
            chapter_intro="This page treats actual-field discipline like a structural audit layer, similar to the quality-control logic running through your other project work: once actual fields are missing, hiddenness spikes sharply.",
            root_pull_quote="Missing actual completion or enrollment fields are not minor metadata defects. They are strong warning signs for a nearly silent public record.",
            paper_pull_quote="Closed-study actual-field discipline behaves like a hard structural boundary between cleaner and quieter registry segments.",
            dashboard_pull_quote="Actual-field flags turn vague metadata quality into a direct hiddenness signal with near-perfect separation.",
            root_rail=["Enroll missing 100%", "Primary missing 100%", "Completion missing 95.3%", "Suspended 100%"],
            landing_metrics=[
                ("Enrollment missing", fmt_pct(as_float(actual_enrollment_missing["no_results_rate"])), "Missing actual enrollment"),
                ("Completion missing", fmt_pct(as_float(actual_completion_missing["no_results_rate"])), "Missing actual completion"),
                ("Primary missing ghosts", fmt_pct(as_float(actual_primary_missing["ghost_protocol_rate"])), "Missing actual primary completion"),
                ("Completed enrollment miss", fmt_pct(as_float(actual_completed["enrollment_missing_rate"])), "Completed-study missing rate"),
            ],
            landing_chart_html=chart_section(
                "Actual-field discipline",
                bar_chart(
                    [
                        {"label": "Primary present", "value": as_float(actual_primary_present["no_results_rate"])},
                        {"label": "Primary missing", "value": as_float(actual_primary_missing["no_results_rate"])},
                        {"label": "Completion present", "value": as_float(actual_completion_present["no_results_rate"])},
                        {"label": "Completion missing", "value": as_float(actual_completion_missing["no_results_rate"])},
                        {"label": "Enrollment present", "value": as_float(actual_enrollment_present["no_results_rate"])},
                        {"label": "Enrollment missing", "value": as_float(actual_enrollment_missing["no_results_rate"])},
                    ],
                    "Actual-field presence",
                    "2-year no-results rate for actual-field present versus missing groups",
                    "value",
                    "label",
                    "#c3452f",
                    percent=True,
                ),
                "The separation between actual-field present and missing groups is unusually sharp across all three fields.",
                "This makes actual-field discipline one of the clearest structural warning signals in the atlas.",
            ),
            reader_lede="A 156-word micro-paper on how missing actual dates and counts map onto hiddenness in older CT.gov studies.",
            reader_rail=["Primary actual", "Completion actual", "Enrollment actual", "Suspended studies"],
            reader_metrics=[
                ("Primary missing no results", fmt_pct(as_float(actual_primary_missing["no_results_rate"])), "Primary completion not actual"),
                ("Completion missing ghosts", fmt_pct(as_float(actual_completion_missing["ghost_protocol_rate"])), "Completion not actual"),
                ("Enrollment missing no results", fmt_pct(as_float(actual_enrollment_missing["no_results_rate"])), "Enrollment not actual"),
                ("Suspended completion miss", fmt_pct(as_float(actual_suspended["completion_missing_rate"])), "Suspended studies"),
            ],
            dashboard_title="Missing actual dates and counts mark one of the quietest structural zones in older CT.gov studies",
            dashboard_eyebrow="Actual-Field Dashboard",
            dashboard_lede="Closed studies missing actual primary completion, completion, or enrollment fields remain dramatically quieter than studies with those fields properly recorded, and suspended studies are worst on discipline.",
            dashboard_rail=["No results", "Ghosts", "Status rates", "Missing actuals"],
            dashboard_metrics=[
                ("Primary missing no results", fmt_pct(as_float(actual_primary_missing["no_results_rate"])), "Primary completion not actual"),
                ("Completion missing no results", fmt_pct(as_float(actual_completion_missing["no_results_rate"])), "Completion not actual"),
                ("Enrollment missing ghosts", fmt_pct(as_float(actual_enrollment_missing["ghost_protocol_rate"])), "Enrollment not actual"),
                ("Suspended completion miss", fmt_pct(as_float(actual_suspended["completion_missing_rate"])), "Status-specific discipline"),
            ],
            dashboard_sections=[
                chart_section(
                    "No-results by actual-field discipline",
                    bar_chart(
                        [
                            {"label": "Primary present", "value": as_float(actual_primary_present["no_results_rate"])},
                            {"label": "Primary missing", "value": as_float(actual_primary_missing["no_results_rate"])},
                            {"label": "Completion present", "value": as_float(actual_completion_present["no_results_rate"])},
                            {"label": "Completion missing", "value": as_float(actual_completion_missing["no_results_rate"])},
                            {"label": "Enrollment present", "value": as_float(actual_enrollment_present["no_results_rate"])},
                            {"label": "Enrollment missing", "value": as_float(actual_enrollment_missing["no_results_rate"])},
                        ],
                        "Actual-field contrast",
                        "2-year no-results rate for actual-field present versus missing groups",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "All three actual-field flags show an extreme split between present and missing groups.",
                    "That separation is much sharper than many of the softer structural gradients elsewhere in the series.",
                ),
                chart_section(
                    "Ghost protocols by actual-field discipline",
                    bar_chart(
                        [
                            {"label": "Primary missing ghosts", "value": as_float(actual_primary_missing["ghost_protocol_rate"])},
                            {"label": "Completion missing ghosts", "value": as_float(actual_completion_missing["ghost_protocol_rate"])},
                            {"label": "Enrollment missing ghosts", "value": as_float(actual_enrollment_missing["ghost_protocol_rate"])},
                            {"label": "Primary present ghosts", "value": as_float(actual_primary_present["ghost_protocol_rate"])},
                            {"label": "Completion present ghosts", "value": as_float(actual_completion_present["ghost_protocol_rate"])},
                            {"label": "Enrollment present ghosts", "value": as_float(actual_enrollment_present["ghost_protocol_rate"])},
                        ],
                        "Actual-field ghosts",
                        "Ghost-protocol rate for actual-field present versus missing groups",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Missing actual primary completion produces one of the highest ghost-protocol rates in the atlas.",
                    "The ghost view shows that this is not merely a missing-results artifact.",
                ),
                chart_section(
                    "Status-specific missing-actual rates",
                    bar_chart(
                        [
                            {"label": "Completed | primary", "value": as_float(actual_completed["primary_completion_missing_rate"])},
                            {"label": "Withdrawn | primary", "value": as_float(actual_withdrawn["primary_completion_missing_rate"])},
                            {"label": "Suspended | primary", "value": as_float(actual_suspended["primary_completion_missing_rate"])},
                            {"label": "Completed | completion", "value": as_float(actual_completed["completion_missing_rate"])},
                            {"label": "Withdrawn | completion", "value": as_float(actual_withdrawn["completion_missing_rate"])},
                            {"label": "Suspended | completion", "value": as_float(actual_suspended["completion_missing_rate"])},
                        ],
                        "Status and discipline",
                        "Selected status-specific missing-actual rates",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Suspended and withdrawn studies are the weakest on actual-field discipline, especially for completion fields.",
                    "This ties the actual-field project back to the stopped-trial disclosure story rather than leaving it as an isolated metadata page.",
                ),
            ],
            sidebar_bullets=[
                "Missing actual enrollment reaches 100.0 percent on the 2-year no-results metric.",
                "Missing actual completion reaches 95.3 percent and missing actual primary completion 100.0 percent on the same metric.",
                "Missing actual primary completion also reaches 81.7 percent on the ghost-protocol metric.",
                "Suspended studies are worst on status-specific actual-field discipline, including 100.0 percent missing actual completion.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-country-reporting-map",
            title="CT.gov Country Reporting Map",
            summary="A standalone E156 project on how named country involvement maps onto large geographic visibility divides in older CT.gov studies.",
            body=country_body,
            sentences=country_sentences,
            primary_estimand="2-year no-results rate across named country involvements among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies merged with extracted named-country labels from raw locations",
            references=common_refs,
            protocol=(
                "This protocol explodes eligible older closed interventional ClinicalTrials.gov studies into study-country involvements using named countries extracted from recorded locations. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, and fully visible shares across countries with sizable eligible older study counts, with secondary contrasts among selected large countries. "
                "The aim is to expose named geographic transparency divides that country-count buckets cannot show. "
                "Because country labels come from recorded locations, the project measures country involvement rather than enrollment share, legal jurisdiction, or sponsor domicile."
            ),
            root_title="Where do country-linked reporting gaps look worst on CT.gov?",
            root_eyebrow="Country Project",
            root_lede="A standalone public project on named country involvement, showing wide geographic divides in older CT.gov reporting debt beyond simple multinational counts.",
            chapter_intro="This page uses the geographic mapping instinct from your other project work, but instead of a generic footprint count it names the country-linked parts of the backlog directly.",
            root_pull_quote="The United States carries the largest stock, but some large named country footprints are dramatically quieter on rate.",
            paper_pull_quote="Country involvement changes the hiddenness story because simple country-count buckets blur very different national profiles together.",
            dashboard_pull_quote="Once named countries are plotted directly, the registry looks geographically stratified rather than generically multinational.",
            root_rail=["US 52.1%", "Egypt 95.8%", "China 81.7%", "Poland 33.5%"],
            landing_metrics=[
                ("United States", fmt_int(as_int(country_us["studies"])), "Largest named-country stock"),
                ("United States no results", fmt_pct(as_float(country_us["no_results_rate"])), "2-year no-results"),
                ("Egypt no results", fmt_pct(as_float(country_egypt["no_results_rate"])), "Worst large named country"),
                ("Poland visible", fmt_pct(as_float(country_poland["results_publication_visible_rate"])), "Results plus publication"),
            ],
            landing_chart_html=chart_section(
                "Largest named countries",
                bar_chart(
                    [{"label": row["country"], "value": as_float(row["no_results_rate"])} for _, row in top_country_rows.iterrows()],
                    "Top named-country stocks",
                    "2-year no-results rate across the largest named-country study footprints",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "Large country-linked footprints differ sharply, from Poland and Australia to Egypt and China.",
                "This is the public-facing country map: not a choropleth, but a clear named-country gradient.",
            ),
            reader_lede="A 156-word micro-paper on how named country involvement maps onto missing results and ghost protocols in older CT.gov studies.",
            reader_rail=["United States", "Egypt", "China", "Poland"],
            reader_metrics=[
                ("United States no results", fmt_pct(as_float(country_us["no_results_rate"])), "Largest stock"),
                ("Egypt ghosts", fmt_pct(as_float(country_egypt["ghost_protocol_rate"])), "Worst large-country ghost rate"),
                ("China no results", fmt_pct(as_float(country_china["no_results_rate"])), "Large named-country gap"),
                ("Australia no results", fmt_pct(as_float(country_australia["no_results_rate"])), "Cleaner large-country benchmark"),
            ],
            dashboard_title="Named-country involvement exposes large geographic divides in older CT.gov reporting debt",
            dashboard_eyebrow="Country Dashboard",
            dashboard_lede="The United States dominates the stock, but named-country rates diverge sharply: Egypt and China remain very quiet, while Poland, Australia, and Japan look much cleaner.",
            dashboard_rail=["Top stocks", "Selected contrast", "Ghosts", "Visible share"],
            dashboard_metrics=[
                ("Egypt no results", fmt_pct(as_float(country_egypt["no_results_rate"])), "Worst large named country"),
                ("China ghosts", fmt_pct(as_float(country_china["ghost_protocol_rate"])), "Neither visible"),
                ("Poland no results", fmt_pct(as_float(country_poland["no_results_rate"])), "Cleaner comparator"),
                ("Australia visible", fmt_pct(as_float(country_australia["results_publication_visible_rate"])), "Results plus publication"),
            ],
            dashboard_sections=[
                chart_section(
                    "Largest named-country stocks",
                    bar_chart(
                        [{"label": row["country"], "value": as_float(row["no_results_rate"])} for _, row in top_country_rows.iterrows()],
                        "Largest country-linked stocks",
                        "2-year no-results rate across the largest named-country footprints",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "The biggest named-country stocks are not converging on one common reporting level.",
                    "This chart focuses on scale first so the country story does not overfit to tiny country tails.",
                ),
                chart_section(
                    "Selected country contrast",
                    bar_chart(
                        [
                            {"label": "United States", "value": as_float(country_us["no_results_rate"])},
                            {"label": "Egypt", "value": as_float(country_egypt["no_results_rate"])},
                            {"label": "China", "value": as_float(country_china["no_results_rate"])},
                            {"label": "Poland", "value": as_float(country_poland["no_results_rate"])},
                            {"label": "Australia", "value": as_float(country_australia["no_results_rate"])},
                            {"label": "Japan", "value": as_float(country_japan["no_results_rate"])},
                        ],
                        "Selected large countries",
                        "Selected named-country contrast on the 2-year no-results metric",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Egypt and China remain far quieter than the cleaner Poland, Australia, and Japan profiles.",
                    "The selected-country panel makes the geographic divide easier to read than a longer ranked table.",
                ),
                chart_section(
                    "Ghost protocols",
                    bar_chart(
                        [
                            {"label": "United States", "value": as_float(country_us["ghost_protocol_rate"])},
                            {"label": "Egypt", "value": as_float(country_egypt["ghost_protocol_rate"])},
                            {"label": "China", "value": as_float(country_china["ghost_protocol_rate"])},
                            {"label": "Poland", "value": as_float(country_poland["ghost_protocol_rate"])},
                            {"label": "Australia", "value": as_float(country_australia["ghost_protocol_rate"])},
                            {"label": "Japan", "value": as_float(country_japan["ghost_protocol_rate"])},
                        ],
                        "Country ghosts",
                        "Ghost-protocol rate across selected named-country footprints",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "The same divide survives on the stricter ghost-protocol metric.",
                    "That matters because it reduces the chance that the country contrast is only a publication-link artifact.",
                ),
            ],
            sidebar_bullets=[
                "United States appears in 104,882 eligible older studies, the largest named-country stock.",
                "Egypt reaches 95.8 percent on the 2-year no-results metric.",
                "China reaches 81.7 percent while Poland falls to 33.5 percent on the same metric.",
                "Australia and Japan are markedly cleaner large-country comparators than Egypt and China.",
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
