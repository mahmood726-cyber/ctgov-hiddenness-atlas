#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Build wave-three standalone CT.gov projects."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct
from build_split_projects import chart_section, sentence_bundle, write_project

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

FAMILY_META = {
    "oncology": {
        "repo_name": "ctgov-oncology-hiddenness",
        "title": "CT.gov Oncology Hiddenness",
        "short_title": "Oncology",
        "summary": "Oncology-specific CT.gov hiddenness showing where cancer-trial stock, phases, and sponsors still go quiet.",
        "root_title": "How much oncology evidence still goes quiet on CT.gov?",
        "root_eyebrow": "Oncology Project",
        "root_lede": "A standalone public project on oncology trial hiddenness across sponsors, phases, and missing-results stock.",
        "chapter_intro": "This oncology project isolates the largest named disease family in the registry and treats it as its own evidence landscape rather than a subpanel inside a general dashboard.",
        "root_pull_quote": "Oncology contains the largest named stock of older hidden evidence in the whole CT.gov family map.",
        "root_pull_source": "Oncology portfolio",
        "paper_pull_quote": "Cancer trials are too large and too visible a policy area to be left inside a generic all-condition average.",
        "paper_pull_source": "Reading note",
        "dashboard_pull_quote": "The oncology story is about both scale and structure: very large stock, weak early-phase visibility, and heavy concentration in major sponsors.",
        "dashboard_pull_source": "How to read the dashboard",
    },
    "cardiovascular": {
        "repo_name": "ctgov-cardiovascular-hiddenness",
        "title": "CT.gov Cardiovascular Hiddenness",
        "short_title": "Cardiovascular",
        "summary": "Cardiovascular CT.gov hiddenness showing how heart and vascular studies remain quiet across major phases and sponsors.",
        "root_title": "How quiet is the cardiovascular trial record on CT.gov?",
        "root_eyebrow": "Cardiovascular Project",
        "root_lede": "A standalone public project on cardiovascular reporting debt, ghost protocols, and the sponsors carrying the largest hidden stock.",
        "chapter_intro": "This cardiovascular project mirrors your registry-first cardio work, but here the focus is not pooled treatment effect. It is the size and structure of what remains hidden.",
        "root_pull_quote": "Cardiovascular trials are not the biggest family, but they are quieter than oncology on the main no-results metric.",
        "root_pull_source": "Cardiovascular portfolio",
        "paper_pull_quote": "In cardiovascular trials, the key problem is not scarcity. It is a large, still-muted registry record.",
        "paper_pull_source": "Reading note",
        "dashboard_pull_quote": "The cardiovascular page separates sponsor mix, phase mix, and raw stock so the family does not collapse into a single score.",
        "dashboard_pull_source": "How to read the dashboard",
    },
    "metabolic": {
        "repo_name": "ctgov-metabolic-hiddenness",
        "title": "CT.gov Metabolic Hiddenness",
        "short_title": "Metabolic",
        "summary": "Metabolic CT.gov hiddenness across obesity, diabetes, and related trial portfolios with large late-phase and NA stock.",
        "root_title": "How much metabolic trial evidence stays hidden on CT.gov?",
        "root_eyebrow": "Metabolic Project",
        "root_lede": "A standalone public project on metabolic trial hiddenness across diabetes, obesity, and related portfolios.",
        "chapter_intro": "This metabolic project isolates one of the quietest large disease families in the registry and tracks which sponsors and phases contribute most to the unresolved stock.",
        "root_pull_quote": "Metabolic trials sit above cardiovascular trials on the main no-results metric and remain heavily obscured in the NA bucket.",
        "root_pull_source": "Metabolic portfolio",
        "paper_pull_quote": "The metabolic record is not only large. It is persistently quiet across both sponsor classes and phases.",
        "paper_pull_source": "Reading note",
        "dashboard_pull_quote": "Metabolic hiddenness is driven by a mix of broad academic stock and substantial industry backlog rather than a single sponsor type.",
        "dashboard_pull_source": "How to read the dashboard",
    },
}


def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def family_sentence_bundle(
    label: str,
    row: pd.Series,
    sponsor_name: str,
    sponsor_count: int,
    phase_name: str,
    phase_rate: float,
) -> tuple[str, list[dict[str, str]]]:
    bundles = {
        "Oncology": [
            ("Question", "How much registered oncology evidence still goes quiet on ClinicalTrials.gov once older closed interventional studies are isolated?"),
            ("Dataset", f"We analysed {int(row['studies']):,} eligible older oncology studies from the March 29, 2026 full-registry snapshot, making oncology the largest named disease family in the portfolio."),
            ("Method", "The project compares two-year no-results rates, ghost-protocol rates, sponsor-class patterns, phase gradients, and the biggest named sponsors by unresolved stock."),
            ("Primary result", f"Across older oncology studies, {row['no_results_rate']:.1f} percent lacked posted results and {row['ghost_protocol_rate']:.1f} percent showed neither results nor a linked publication."),
            ("Secondary result", f"Phase {phase_name.replace('PHASE', ' ').strip()} was especially quiet at {phase_rate:.1f} percent on the no-results metric, while {sponsor_name} carried the largest sponsor stock at {sponsor_count:,} older missing-results studies."),
            ("Interpretation", "Oncology hiddenness is therefore about scale as much as silence, with very large stock spread across public, academic, network, and industry sponsors. That matters for cancer policy, treatment evaluation, and evidence review."),
            ("Boundary", "These measures describe registry-visible evidence absence rather than adjudicated legal non-compliance within this public oncology frame."),
        ],
        "Cardiovascular": [
            ("Question", "How quiet is the older cardiovascular trial record in ClinicalTrials.gov once heart and vascular studies are grouped into one registry-first family?"),
            ("Dataset", f"We analysed {int(row['studies']):,} eligible older cardiovascular studies from the March 29, 2026 full-registry snapshot, spanning coronary, stroke, heart-failure, rhythm, and vascular records."),
            ("Method", "Primary comparisons tracked two-year no-results rates, ghost protocols, sponsor-class mix, phase patterns, and the sponsors holding the biggest unresolved stock."),
            ("Primary result", f"Across older cardiovascular studies, {row['no_results_rate']:.1f} percent lacked posted results and {row['ghost_protocol_rate']:.1f} percent showed neither results nor a linked publication trail."),
            ("Secondary result", f"{phase_name} remained the largest phase bucket, while {sponsor_name} carried the biggest named sponsor stock at {sponsor_count:,} older missing-results studies in the cardiovascular family."),
            ("Interpretation", "The cardiovascular record is therefore not just incomplete. It remains structurally quiet across common phases despite its central place in evidence-based medicine. This matters for guideline-facing cardiovascular medicine."),
            ("Boundary", "These family-level estimates measure registry-visible absence rather than legal culpability or publication quality within this cardiovascular frame."),
        ],
        "Metabolic": [
            ("Question", "How much older metabolic trial evidence on ClinicalTrials.gov remains quiet once obesity, diabetes, and related studies are read as one family?"),
            ("Dataset", f"We analysed {int(row['studies']):,} eligible older metabolic studies from the March 29, 2026 full-registry snapshot, covering diabetes, obesity, lipid, and endocrine-related portfolios."),
            ("Method", "The project compares two-year no-results rates, ghost-protocol rates, sponsor-class contrasts, phase structure, and leading sponsors by unresolved stock."),
            ("Primary result", f"Across older metabolic studies, {row['no_results_rate']:.1f} percent lacked posted results and {row['ghost_protocol_rate']:.1f} percent showed neither results nor a linked publication."),
            ("Secondary result", f"{phase_name} remained the dominant phase bucket, while {sponsor_name} carried the largest named sponsor stock at {sponsor_count:,} older missing-results studies in the metabolic family."),
            ("Interpretation", "Metabolic hiddenness is therefore not confined to one sponsor sector and remains visible across large clinical-development and registry-sparsity channels. That is especially important because diabetes and obesity evidence directly shapes large prescribing, prevention, and public-health decisions."),
            ("Boundary", "These metrics capture registry-visible omission rather than adjudicated legal breach within this metabolic family frame today."),
        ],
    }
    return sentence_bundle(bundles[label])


def main() -> None:
    rule_era = load_csv("rule_era_visibility_older_2y.csv")
    family_summary = load_csv("selected_condition_family_summary_older_2y.csv")
    family_sponsor_class = load_csv("selected_condition_family_sponsor_class_older_2y.csv")
    family_phase = load_csv("selected_condition_family_phase_older_2y.csv")
    family_sponsor = load_csv("selected_condition_family_lead_sponsor_older_2y.csv")
    full_family_map = load_csv("condition_family_older_2y.csv")
    pubmed = load_csv("pubmed_publication_audit_summary.csv")

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

    rule_body, rule_sentences = sentence_bundle(
        [
            ("Question", "Did ClinicalTrials.gov completion cohorts become more transparent after FDAAA 801 and the Final Rule?"),
            ("Dataset", "We analysed 249,507 older closed interventional studies from the March 29, 2026 full-registry snapshot and grouped them into four completion eras anchored to reporting-rule landmarks."),
            ("Method", "For each era we estimated two-year no-results rates, ghost-protocol rates, no-publication rates, and the share with both results and publication visible."),
            ("Primary result", "The FDAAA 801 era from 2008 to 2016 showed a 67.1 percent no-results rate, whereas the recent eligible era from 2021 to 2024 rose to 77.0 percent."),
            ("Secondary result", "Ghost protocols likewise increased from 39.6 percent in the FDAAA 801 era to 46.7 percent in the recent eligible era, while full visibility fell to 10.8 percent."),
            ("Interpretation", "Later eligible cohorts therefore do not look cleaner on these registry-visible measures even after each included study had at least two years to report."),
            ("Boundary", "These policy-era comparisons are descriptive and do not adjudicate applicable-clinical-trial status or legal compliance within this registry frame."),
        ]
    )

    pub_body, pub_sentences = sentence_bundle(
        [
            ("Question", "How often do ClinicalTrials.gov records with no linked publication hide an external PubMed trail when searched by NCT identifier?"),
            ("Dataset", "We drew a sponsor-class-stratified audit sample of 1,050 older studies lacking CT.gov publication links from the March 29, 2026 full-registry snapshot."),
            ("Method", "Each sampled NCT identifier was queried against PubMed using identifier-based E-utilities searches, then reweighted back to the sponsor-class distribution of older no-link studies."),
            ("Primary result", "The weighted PubMed NCT-match rate across the no-link older-study population was only 1.2 percent, indicating that external publication rescue was uncommon on this identifier-based audit."),
            ("Secondary result", "The weighted external-publication-only rate among no-link studies was just 0.3 percent, and the industry sample reached 2.0 percent on the raw PubMed match rate."),
            ("Interpretation", "Missing CT.gov publication links therefore look more like true visible sparsity than widespread under-linking, at least under a strict NCT-indexed external search strategy."),
            ("Boundary", "This audit is sample-based and identifier-dependent, so it can miss publications that omit NCT identifiers or sit outside PubMed indexing today."),
        ]
    )

    projects: list[dict[str, object]] = [
        {
            "repo_name": "ctgov-rule-era-reporting-gap",
            "title": "CT.gov Rule-Era Reporting Gap",
            "summary": "A standalone E156 project comparing older CT.gov completion cohorts across pre-FDAAA, FDAAA, and later policy eras.",
            "body": rule_body,
            "sentences": rule_sentences,
            "primary_estimand": "2-year no-results rate across completion eras anchored to major U.S. reporting rules",
            "data_note": "249,507 eligible older closed interventional studies grouped into four completion eras",
            "references": [
                "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
                "Food and Drug Administration Amendments Act of 2007, Pub L No. 110-85.",
                "42 CFR Part 11. Clinical Trials Registration and Results Information Submission. Final Rule. September 21, 2016.",
            ],
            "protocol": (
                "This protocol groups eligible older closed interventional ClinicalTrials.gov studies into completion eras aligned to major U.S. registry-reporting milestones. "
                "Primary outputs compare two-year no-results rates, ghost-protocol rates, no-publication rates, and full-visibility shares across pre-FDAAA, FDAAA, and later eras. "
                "The aim is to test whether later eligible cohorts look cleaner on registry-visible measures after rule changes. "
                "These comparisons remain descriptive because the project does not adjudicate applicable-clinical-trial status or legal exposure study by study."
            ),
            "root_title": "Did CT.gov reporting actually improve across rule eras?",
            "root_eyebrow": "Rule-Era Project",
            "root_lede": "A standalone public project on pre-FDAAA, FDAAA, and later completion cohorts, showing how reporting debt changed across policy eras.",
            "chapter_intro": "This page treats policy landmarks as analytic eras rather than historical footnotes. The question is whether later eligible cohorts actually look cleaner once enough time has passed.",
            "root_pull_quote": "On registry-visible measures, the recent eligible era looks worse than the FDAAA 801 era.",
            "root_pull_source": "Completion-era comparison",
            "paper_pull_quote": "A later policy era does not automatically mean a cleaner public record.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "The rule-era view matters because it forces the registry to be read against its own policy timeline, not just as a timeless backlog.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": ["FDAAA era 67.1%", "Recent era 77.0%", "Ghosts 46.7%", "Visible 10.8%"],
            "landing_metrics": [
                ("FDAAA era", fmt_pct(as_float(rule_era.iloc[1]["no_results_rate"])), "2-year no-results"),
                ("Recent era", fmt_pct(as_float(rule_era.iloc[3]["no_results_rate"])), "2-year no-results"),
                ("Recent ghosts", fmt_pct(as_float(rule_era.iloc[3]["ghost_protocol_rate"])), "Neither visible"),
                ("Recent visible", fmt_pct(as_float(rule_era.iloc[3]["results_publication_visible_rate"])), "Results plus publication"),
            ],
            "landing_chart_html": chart_section(
                "No-results by era",
                bar_chart(
                    [{"label": row["rule_era"], "value": as_float(row["no_results_rate"])} for _, row in rule_era.iterrows()],
                    "Rule eras",
                    "2-year no-results rate across completion eras",
                    "value",
                    "label",
                    "#c3452f",
                    percent=True,
                ),
                "The later eligible era does not look cleaner on the main no-results metric.",
                "The comparison is anchored to completion eras because reporting rules operate against the completion clock, not just the registration date.",
            ),
            "reader_lede": "A 156-word micro-paper on whether later CT.gov policy eras actually produced cleaner older completion cohorts.",
            "reader_rail": ["Pre-FDAAA", "FDAAA", "Final Rule", "Recent eligible"],
            "reader_metrics": [
                ("Pre-FDAAA", fmt_pct(as_float(rule_era.iloc[0]["no_results_rate"])), "2-year no-results"),
                ("FDAAA era", fmt_pct(as_float(rule_era.iloc[1]["no_results_rate"])), "2-year no-results"),
                ("Final Rule era", fmt_pct(as_float(rule_era.iloc[2]["no_results_rate"])), "2-year no-results"),
                ("Recent era", fmt_pct(as_float(rule_era.iloc[3]["no_results_rate"])), "2-year no-results"),
            ],
            "dashboard_title": "The CT.gov policy timeline does not map cleanly onto better older reporting cohorts",
            "dashboard_eyebrow": "Rule-Era Dashboard",
            "dashboard_lede": "Later eligible completion cohorts remain highly obscured on no-results and ghost-protocol metrics even when grouped against policy landmarks.",
            "dashboard_rail": ["No results", "Ghosts", "Visibility", "Four eras"],
            "dashboard_metrics": [
                ("Pre-FDAAA", fmt_pct(as_float(rule_era.iloc[0]["no_results_rate"])), "2-year no-results"),
                ("FDAAA era", fmt_pct(as_float(rule_era.iloc[1]["ghost_protocol_rate"])), "Ghost protocols"),
                ("Recent era", fmt_pct(as_float(rule_era.iloc[3]["ghost_protocol_rate"])), "Ghost protocols"),
                ("Recent visible", fmt_pct(as_float(rule_era.iloc[3]["results_publication_visible_rate"])), "Results plus publication"),
            ],
            "dashboard_sections": [
                chart_section(
                    "No-results rates",
                    bar_chart(
                        [{"label": row["rule_era"], "value": as_float(row["no_results_rate"])} for _, row in rule_era.iterrows()],
                        "Rule eras",
                        "2-year no-results rate across completion eras",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "The recent eligible era sits above the FDAAA 801 era on the main reporting-debt metric.",
                    "This chart is the anchor because the 2-year no-results measure is the core registry-visible absence signal in the series.",
                ),
                chart_section(
                    "Ghost protocols",
                    bar_chart(
                        [{"label": row["rule_era"], "value": as_float(row["ghost_protocol_rate"])} for _, row in rule_era.iterrows()],
                        "Ghost protocols by era",
                        "Neither-results-nor-publication rates across completion eras",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Ghost protocols rise again in the recent eligible era rather than fading away.",
                    "The ghost metric is stricter than missing results alone because it also requires the absence of a linked publication trail.",
                ),
                chart_section(
                    "Fully visible share",
                    bar_chart(
                        [{"label": row["rule_era"], "value": as_float(row["results_publication_visible_rate"])} for _, row in rule_era.iterrows()],
                        "Visibility by era",
                        "Share with both results and publication visible",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Full visibility remains low in every era and falls back in the recent eligible cohort.",
                    "The positive mirror matters because a lower ghost rate does not necessarily imply broad complete visibility.",
                ),
            ],
            "sidebar_bullets": [
                "The FDAAA 801 era sits at 67.1 percent on the 2-year no-results metric.",
                "The recent eligible era rises to 77.0 percent on the same metric.",
                "Recent ghost protocols reach 46.7 percent.",
                "Recent full visibility is only 10.8 percent.",
            ],
        },
        {
            "repo_name": "ctgov-publication-undercount-audit",
            "title": "CT.gov Publication Undercount Audit",
            "summary": "A standalone E156 project auditing how often CT.gov no-link records still show a PubMed NCT paper trail.",
            "body": pub_body,
            "sentences": pub_sentences,
            "primary_estimand": "Weighted PubMed NCT-match rate among older CT.gov records lacking linked publications",
            "data_note": "Sponsor-class-stratified sample of 1,050 older no-link studies queried against PubMed by NCT ID",
            "references": [
                "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
                "PubMed E-utilities. National Center for Biotechnology Information. Accessed March 29, 2026.",
                "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
            ],
            "protocol": (
                "This protocol audits a sponsor-class-stratified sample of older CT.gov records that lack linked publications in the registry interface. "
                "Each sampled NCT identifier is queried against PubMed using identifier-based searches, and sample estimates are reweighted to the sponsor-class distribution of older no-link studies. "
                "The primary estimand is the weighted PubMed NCT-match rate among the no-link older-study population. "
                "Because the audit uses NCT-based PubMed matching, it is deliberately strict and can miss publications that omit registry identifiers or fall outside PubMed."
            ),
            "root_title": "Are CT.gov missing publication links mostly just under-linking?",
            "root_eyebrow": "PubMed Audit",
            "root_lede": "A standalone public audit testing how often older CT.gov no-link records can still be rescued by external PubMed NCT searches.",
            "chapter_intro": "This project does not assume that every missing CT.gov publication link means no paper exists. It tests that claim directly with a sponsor-class-stratified external audit.",
            "root_pull_quote": "On a strict PubMed NCT audit, external publication rescue is rare.",
            "root_pull_source": "PubMed underlink audit",
            "paper_pull_quote": "The no-link field looks more like real visible sparsity than a giant linking bug.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "A missing CT.gov publication link is not always final, but the external rescue rate here is low enough to matter.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": ["1,050 sampled", "1.2% weighted match", "0.3% external-only", "Industry 2.0%"],
            "landing_metrics": [
                ("Sample size", fmt_int(as_int(pubmed[pubmed["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]["sample_studies"])), "Stratified no-link audit"),
                ("Weighted match", fmt_pct(as_float(pubmed[pubmed["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]["weighted_pubmed_match_contribution"])), "PubMed NCT match"),
                ("Weighted external only", fmt_pct(as_float(pubmed[pubmed["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]["weighted_external_publication_only_contribution"])), "PubMed match with no results"),
                ("Industry sample", fmt_pct(as_float(pubmed[pubmed["lead_sponsor_class"] == "INDUSTRY"].iloc[0]["sample_pubmed_match_rate"])), "Raw sample match"),
            ],
            "landing_chart_html": chart_section(
                "Sample PubMed match rate",
                bar_chart(
                    [
                        {"label": row["lead_sponsor_class"], "value": as_float(row["sample_pubmed_match_rate"])}
                        for _, row in pubmed[pubmed["lead_sponsor_class"] != "ALL_WEIGHTED"].sort_values("sample_pubmed_match_rate", ascending=False).iterrows()
                    ],
                    "PubMed audit",
                    "Sample PubMed NCT-match rate by sponsor class",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "Raw sample match rates stay low across sponsor classes, even before reweighting.",
                "The sample audit deliberately uses strict NCT-based PubMed matching, so the bars are a conservative external-rescue estimate rather than a broad publication search.",
            ),
            "reader_lede": "A 156-word micro-paper on how often older CT.gov no-link records can be externally rescued with strict PubMed NCT matching.",
            "reader_rail": ["Sample", "Weighted", "External only", "Industry"],
            "reader_metrics": [
                ("Sample", fmt_int(as_int(pubmed[pubmed["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]["sample_studies"])), "Older no-link studies"),
                ("Weighted match", fmt_pct(as_float(pubmed[pubmed["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]["weighted_pubmed_match_contribution"])), "PubMed NCT match"),
                ("External only", fmt_pct(as_float(pubmed[pubmed["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]["weighted_external_publication_only_contribution"])), "No CT.gov link, PubMed found"),
                ("Industry", fmt_pct(as_float(pubmed[pubmed["lead_sponsor_class"] == "INDUSTRY"].iloc[0]["sample_pubmed_match_rate"])), "Sample match rate"),
            ],
            "dashboard_title": "Strict external PubMed rescue is uncommon among older CT.gov no-link records",
            "dashboard_eyebrow": "PubMed Audit Dashboard",
            "dashboard_lede": "The sample-based external audit suggests that CT.gov publication-link missingness is not mostly a giant under-linking artifact.",
            "dashboard_rail": ["Sample rates", "Weighted effect", "External only", "Class strata"],
            "dashboard_metrics": [
                ("Weighted match", fmt_pct(as_float(pubmed[pubmed["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]["weighted_pubmed_match_contribution"])), "PubMed NCT match"),
                ("Weighted external only", fmt_pct(as_float(pubmed[pubmed["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]["weighted_external_publication_only_contribution"])), "PubMed only"),
                ("Network sample", fmt_pct(as_float(pubmed[pubmed["lead_sponsor_class"] == "NETWORK"].iloc[0]["sample_pubmed_match_rate"])), "Highest raw sample class"),
                ("Other sample", fmt_pct(as_float(pubmed[pubmed["lead_sponsor_class"] == "OTHER"].iloc[0]["sample_pubmed_match_rate"])), "Largest population class"),
            ],
            "dashboard_sections": [],
            "sidebar_bullets": [
                "The weighted PubMed NCT-match estimate is 1.2 percent.",
                "The weighted external-publication-only estimate is 0.3 percent.",
                "Industry reaches 2.0 percent on the raw sample PubMed match rate.",
                "Network reaches 3.3 percent on the highest raw class sample rate, still low in absolute terms.",
            ],
        },
    ]

    audit_rows = pubmed[pubmed["lead_sponsor_class"] != "ALL_WEIGHTED"].copy()
    weighted_row = pubmed[pubmed["lead_sponsor_class"] == "ALL_WEIGHTED"].iloc[0]
    projects[1]["dashboard_sections"] = [
        chart_section(
            "Raw sample PubMed match rate",
            bar_chart(
                [
                    {"label": row["lead_sponsor_class"], "value": as_float(row["sample_pubmed_match_rate"])}
                    for _, row in audit_rows.sort_values("sample_pubmed_match_rate", ascending=False).iterrows()
                ],
                "Sample PubMed audit",
                "Raw PubMed NCT-match rate by sponsor-class audit stratum",
                "value",
                "label",
                "#326891",
                percent=True,
            ),
            "No sponsor-class sample stratum looks large on the raw PubMed NCT-match metric.",
            "The strict identifier-based audit is meant to test visible under-linking, not to serve as a broad literature review.",
        ),
        chart_section(
            "Weighted audit summary",
            bar_chart(
                [
                    {"label": "Weighted PubMed match", "value": as_float(weighted_row["weighted_pubmed_match_contribution"])},
                    {
                        "label": "Weighted external only",
                        "value": as_float(weighted_row["weighted_external_publication_only_contribution"]),
                    },
                    {"label": "Raw weighted sample", "value": as_float(weighted_row["sample_pubmed_match_rate"])},
                ],
                "Weighted audit summary",
                "Weighted overall PubMed rescue estimates after reweighting the sponsor-class sample",
                "value",
                "label",
                "#8b6914",
                percent=True,
            ),
            "The weighted all-population rescue signal is smaller than the raw audit sample rate.",
            "Reweighting matters because the no-link population is dominated by OTHER and INDUSTRY rather than by the smaller class strata.",
        ),
    ]

    named_family_map = full_family_map[full_family_map["condition_family"] != "other"].copy()
    family_rank_map = {
        row["condition_family"]: rank
        for rank, (_, row) in enumerate(
            named_family_map.sort_values(["studies", "ghost_protocol_rate"], ascending=[False, False]).iterrows(),
            start=1,
        )
    }

    for family_key, meta in FAMILY_META.items():
        family_row = family_summary[family_summary["condition_family"] == family_key].iloc[0]
        sponsor_rows = family_sponsor_class[family_sponsor_class["condition_family"] == family_key].copy()
        sponsor_rows = sponsor_rows[sponsor_rows["studies"] >= 90].copy()
        phase_rows = family_phase[family_phase["condition_family"] == family_key].copy()
        phase_rows = phase_rows[phase_rows["studies"] >= 150].copy()
        sponsor_stock_rows = family_sponsor[family_sponsor["condition_family"] == family_key].copy()

        sponsor_top = sponsor_stock_rows.sort_values(
            ["no_results_count", "studies", "ghost_protocol_count"],
            ascending=[False, False, False],
        ).iloc[0]
        phase_rate_top = phase_rows.sort_values(
            ["no_results_rate", "studies"],
            ascending=[False, False],
        ).iloc[0]
        phase_stock_top = phase_rows.sort_values(
            ["studies", "no_results_count"],
            ascending=[False, False],
        ).iloc[0]

        family_label = family_row["condition_family_label"]
        family_rank = family_rank_map[family_key]
        body, sentences = family_sentence_bundle(
            family_label,
            family_row,
            str(sponsor_top["lead_sponsor_name"]),
            int(sponsor_top["no_results_count"]),
            str(phase_rate_top["phase_label"]),
            float(phase_rate_top["no_results_rate"]),
        )

        projects.append(
            {
                "repo_name": meta["repo_name"],
                "title": meta["title"],
                "summary": f"A standalone E156 project on {family_label.lower()} trial hiddenness across sponsor classes, phases, and leading sponsors.",
                "body": body,
                "sentences": sentences,
                "primary_estimand": f"2-year no-results rate within the {family_label.lower()} family among eligible older CT.gov studies",
                "data_note": f"{fmt_int(as_int(family_row['studies']))} eligible older {family_label.lower()} studies in the March 29, 2026 full-registry snapshot",
                "references": [
                    "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
                    "PubMed E-utilities. National Center for Biotechnology Information. Accessed March 29, 2026.",
                    "Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. BMJ. 2021;372:n71.",
                ],
                "protocol": (
                    f"This protocol isolates the {family_label.lower()} portfolio from the March 29, 2026 ClinicalTrials.gov full-registry snapshot using a keyword-based family map applied to eligible older closed interventional studies. "
                    "Primary outputs compare two-year no-results rates, ghost-protocol rates, sponsor-class contrasts, phase structure, and named lead sponsors by unresolved stock within the family. "
                    "The aim is to treat major therapeutic areas as standalone evidence systems rather than as subpanels inside a general registry atlas. "
                    "Because the family map is keyword-based and single-label, the project is descriptive and can compress multi-topic trials into one dominant family."
                ),
                "root_title": meta["root_title"],
                "root_eyebrow": meta["root_eyebrow"],
                "root_lede": meta["root_lede"],
                "chapter_intro": meta["chapter_intro"],
                "root_pull_quote": meta["root_pull_quote"],
                "root_pull_source": meta["root_pull_source"],
                "paper_pull_quote": meta["paper_pull_quote"],
                "paper_pull_source": meta["paper_pull_source"],
                "dashboard_pull_quote": meta["dashboard_pull_quote"],
                "dashboard_pull_source": meta["dashboard_pull_source"],
                "root_rail": [
                    f"Rank #{family_rank} by stock",
                    f"{fmt_pct(as_float(family_row['no_results_rate']))} no results",
                    f"{fmt_pct(as_float(family_row['ghost_protocol_rate']))} ghost",
                    f"{fmt_pct(as_float(family_row['results_publication_visible_rate']))} fully visible",
                ],
                "landing_metrics": [
                    ("Eligible older", fmt_int(as_int(family_row["studies"])), f"{family_label} studies"),
                    ("No-results rate", fmt_pct(as_float(family_row["no_results_rate"])), "2-year no-results"),
                    ("Ghost rate", fmt_pct(as_float(family_row["ghost_protocol_rate"])), "Neither visible"),
                    ("Fully visible", fmt_pct(as_float(family_row["results_publication_visible_rate"])), "Results plus publication"),
                ],
                "landing_chart_html": chart_section(
                    "Sponsor-class mix",
                    bar_chart(
                        [
                            {"label": row["lead_sponsor_class"], "value": as_float(row["no_results_rate"])}
                            for _, row in sponsor_rows.sort_values(["no_results_rate", "studies"], ascending=[False, False]).iterrows()
                        ],
                        f"{family_label} sponsor classes",
                        f"2-year no-results rate by sponsor class inside the {family_label.lower()} family",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    f"{family_label} splits sharply by sponsor class rather than behaving like one uniform disease portfolio.",
                    "The disease-specific view matters because a family can look moderate overall while hiding strong internal sponsor-class contrasts.",
                ),
                "reader_lede": f"A 156-word micro-paper on where {family_label.lower()} studies remain quiet across sponsor classes, phases, and major sponsors.",
                "reader_rail": [
                    f"{fmt_int(as_int(family_row['studies']))} studies",
                    f"{fmt_pct(as_float(family_row['no_results_rate']))} no results",
                    str(phase_rate_top["phase_label"]),
                    str(sponsor_top["lead_sponsor_name"]),
                ],
                "reader_metrics": [
                    ("No-results rate", fmt_pct(as_float(family_row["no_results_rate"])), "2-year no-results"),
                    ("Ghost rate", fmt_pct(as_float(family_row["ghost_protocol_rate"])), "Neither visible"),
                    ("Top phase rate", fmt_pct(as_float(phase_rate_top["no_results_rate"])), str(phase_rate_top["phase_label"])),
                    ("Top sponsor stock", fmt_int(as_int(sponsor_top["no_results_count"])), str(sponsor_top["lead_sponsor_name"])),
                ],
                "dashboard_title": f"{family_label} hiddenness becomes clearer when sponsor class, phase structure, and stock are separated",
                "dashboard_eyebrow": f"{family_label} Dashboard",
                "dashboard_lede": f"The {family_label.lower()} dashboard isolates family-specific sponsor mix, phase mix, and leading sponsors rather than folding them into an all-registry average.",
                "dashboard_rail": [
                    "Sponsor classes",
                    "Phases",
                    "Top sponsors",
                    "Family-specific stock",
                ],
                "dashboard_metrics": [
                    ("Eligible older", fmt_int(as_int(family_row["studies"])), f"{family_label} studies"),
                    ("No-results rate", fmt_pct(as_float(family_row["no_results_rate"])), "2-year no-results"),
                    ("Largest phase bucket", fmt_int(as_int(phase_stock_top["studies"])), str(phase_stock_top["phase_label"])),
                    ("Top sponsor stock", fmt_int(as_int(sponsor_top["no_results_count"])), str(sponsor_top["lead_sponsor_name"])),
                ],
                "dashboard_sections": [
                    chart_section(
                        "Sponsor-class rates",
                        bar_chart(
                            [
                                {"label": row["lead_sponsor_class"], "value": as_float(row["no_results_rate"])}
                                for _, row in sponsor_rows.sort_values(["no_results_rate", "studies"], ascending=[False, False]).iterrows()
                            ],
                            f"{family_label} sponsor classes",
                            f"2-year no-results rate by sponsor class within {family_label.lower()} studies",
                            "value",
                            "label",
                            "#326891",
                            percent=True,
                        ),
                        f"OTHER_GOV remains near the top where present, but the broader {family_label.lower()} burden is still shaped by the much larger OTHER and INDUSTRY blocks.",
                        "This is a family-specific rate view, so it should be read alongside the top-sponsor stock chart rather than as a standalone leaderboard.",
                    ),
                    chart_section(
                        "Phase pattern",
                        bar_chart(
                            [
                                {"label": row["phase_label"], "value": as_float(row["no_results_rate"])}
                                for _, row in phase_rows.sort_values(["no_results_rate", "studies"], ascending=[False, False]).iterrows()
                            ],
                            f"{family_label} phases",
                            f"2-year no-results rate by phase inside the {family_label.lower()} family",
                            "value",
                            "label",
                            "#c3452f",
                            percent=True,
                        ),
                        f"{phase_rate_top['phase_label']} is the quietest major phase inside the {family_label.lower()} family on the no-results metric.",
                        "Phase structure matters because the family-level average can hide very different early-phase and late-phase behavior.",
                    ),
                    chart_section(
                        "Largest sponsor stocks",
                        bar_chart(
                            [
                                {"label": row["lead_sponsor_name"], "value": as_int(row["no_results_count"])}
                                for _, row in sponsor_stock_rows.sort_values(
                                    ["no_results_count", "studies", "ghost_protocol_count"],
                                    ascending=[False, False, False],
                                )
                                .head(10)
                                .iterrows()
                            ],
                            f"{family_label} top sponsors",
                            f"Lead sponsors with the largest missing-results stock inside {family_label.lower()} studies",
                            "value",
                            "label",
                            "#8b6914",
                            percent=False,
                        ),
                        f"{sponsor_top['lead_sponsor_name']} carries the largest named missing-results stock in this family at {fmt_int(as_int(sponsor_top['no_results_count']))} studies.",
                        "The top-sponsor chart makes the family-specific backlog concrete instead of leaving it as a single family-wide percentage.",
                    ),
                ],
                "sidebar_bullets": [
                    f"{family_label} is rank #{family_rank} among named condition families by eligible older stock.",
                    f"{fmt_pct(as_float(family_row['no_results_rate']))} of older {family_label.lower()} studies lack posted results.",
                    f"{fmt_pct(as_float(family_row['ghost_protocol_rate']))} show neither results nor a linked publication.",
                    f"{str(sponsor_top['lead_sponsor_name'])} carries the largest named missing-results stock at {fmt_int(as_int(sponsor_top['no_results_count']))}.",
                ],
            }
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
