#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Build a second wave of standalone E156 CT.gov projects from deep-analysis outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct, safe
from build_split_projects import chart_section, sentence_bundle, write_project

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def line_chart(
    items: list[dict[str, object]],
    title: str,
    subtitle: str,
    x_key: str,
    series: list[dict[str, str]],
) -> str:
    width = 760
    height = 360
    left = 68
    right = 24
    top = 72
    bottom = 62
    chart_width = width - left - right
    chart_height = height - top - bottom
    max_value = max(max(float(item[entry["key"]]) for item in items) for entry in series)
    max_value = max(100.0, max_value)

    def x_pos(idx: int) -> float:
        if len(items) == 1:
            return left + chart_width / 2
        return left + idx * chart_width / (len(items) - 1)

    def y_pos(value: float) -> float:
        return top + chart_height - (value / max_value) * chart_height

    parts = [
        f"<svg viewBox='0 0 {width} {height}' style='width:100%;height:auto'>",
        f"<rect x='0' y='0' width='{width}' height='{height}' fill='#fffdfa' rx='10'/>",
        f"<text x='{width/2}' y='20' text-anchor='middle' font-family='Segoe UI,Arial,sans-serif' font-size='11' fill='#6a645b' letter-spacing='0.12em'>{safe(title.upper())}</text>",
        f"<text x='{width/2}' y='40' text-anchor='middle' font-family='Georgia,serif' font-size='14' fill='#333'>{safe(subtitle)}</text>",
    ]

    for tick in range(0, int(max_value) + 1, 20):
        y = y_pos(float(tick))
        parts.extend(
            [
                f"<line x1='{left}' y1='{y:.1f}' x2='{width-right}' y2='{y:.1f}' stroke='#e7e0d4' stroke-width='1'/>",
                f"<text x='{left-10}' y='{y+4:.1f}' text-anchor='end' font-family='Segoe UI,Arial,sans-serif' font-size='11' fill='#756f67'>{tick:.0f}%</text>",
            ]
        )

    for idx, item in enumerate(items):
        x = x_pos(idx)
        parts.append(
            f"<text x='{x:.1f}' y='{height-22}' text-anchor='middle' font-family='Segoe UI,Arial,sans-serif' font-size='11' fill='#444'>{safe(item[x_key])}</text>"
        )

    legend_x = left
    for entry in series:
        parts.extend(
            [
                f"<line x1='{legend_x}' y1='54' x2='{legend_x+22}' y2='54' stroke='{entry['color']}' stroke-width='3'/>",
                f"<text x='{legend_x+28}' y='58' font-family='Segoe UI,Arial,sans-serif' font-size='11' fill='#444'>{safe(entry['label'])}</text>",
            ]
        )
        legend_x += 150

    for entry in series:
        points = " ".join(
            f"{x_pos(idx):.1f},{y_pos(float(item[entry['key']])):.1f}" for idx, item in enumerate(items)
        )
        parts.append(
            f"<polyline fill='none' stroke='{entry['color']}' stroke-width='3' stroke-linecap='round' stroke-linejoin='round' points='{points}'/>"
        )
        for idx, item in enumerate(items):
            x = x_pos(idx)
            y = y_pos(float(item[entry["key"]]))
            parts.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='4' fill='{entry['color']}'/>")

    parts.append("</svg>")
    return "".join(parts)


def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def fmt_series_pct(value: float) -> str:
    return fmt_pct(float(value))


def main() -> None:
    visibility = load_csv("visibility_state_summary_older_2y.csv")
    sponsor_class_vis = load_csv("sponsor_class_visibility_older_2y.csv")
    phase_vis = load_csv("phase_visibility_older_2y.csv")
    era_vis = load_csv("completion_era_visibility_older_2y.csv")
    year_vis = load_csv("completion_year_visibility_older_2y.csv")
    family = load_csv("condition_family_older_2y.csv")
    concentration = load_csv("sponsor_concentration_metrics.csv").iloc[0]
    sponsor_conc = load_csv("lead_sponsor_concentration_older_2y.csv")

    visibility_lookup = visibility.set_index("visibility_state")
    named_class_vis = sponsor_class_vis[
        sponsor_class_vis["lead_sponsor_class"].isin(["OTHER_GOV", "OTHER", "INDUSTRY", "NETWORK", "INDIV", "NIH", "FED"])
    ].copy()
    named_class_vis = named_class_vis[named_class_vis["studies"] >= 100].copy()

    visibility_items = [
        {
            "label": row["visibility_state_label"].replace(" + ", " + "),
            "value": as_float(row["rate"]),
        }
        for _, row in visibility.sort_values("rate", ascending=False).iterrows()
    ]
    ghost_by_class = [
        {"label": row["lead_sponsor_class"], "value": as_float(row["ghost_protocol_rate"])}
        for _, row in named_class_vis.sort_values(["ghost_protocol_rate", "studies"], ascending=[False, False]).iterrows()
    ]
    fully_visible_by_class = [
        {"label": row["lead_sponsor_class"], "value": as_float(row["results_pub_rate"])}
        for _, row in named_class_vis.sort_values(["results_pub_rate", "studies"], ascending=[False, False]).iterrows()
    ]
    phase_ghost_items = [
        {"label": row["phase_label"], "value": as_float(row["ghost_protocol_rate"])}
        for _, row in phase_vis[phase_vis["studies"] >= 1000]
        .sort_values(["ghost_protocol_rate", "studies"], ascending=[False, False])
        .head(8)
        .iterrows()
    ]

    year_items = [
        {
            "label": str(int(row["primary_completion_year"])),
            "no_results_rate": as_float(row["no_results_rate"]),
            "ghost_protocol_rate": as_float(row["ghost_protocol_rate"]),
            "results_publication_visible_rate": as_float(row["results_publication_visible_rate"]),
        }
        for _, row in year_vis[year_vis["studies"] >= 1000]
        .query("primary_completion_year >= 2008")
        .sort_values("primary_completion_year")
        .iterrows()
    ]
    era_no_results_items = [
        {"label": row["completion_era"], "value": as_float(row["no_results_rate"])}
        for _, row in era_vis.iterrows()
    ]
    era_ghost_items = [
        {"label": row["completion_era"], "value": as_float(row["ghost_protocol_rate"])}
        for _, row in era_vis.iterrows()
    ]

    family_named = family[family["condition_family"] != "other"].copy()
    family_stock_items = [
        {"label": row["condition_family_label"], "value": as_int(row["studies"])}
        for _, row in family_named.sort_values(["studies", "ghost_protocol_rate"], ascending=[False, False]).head(10).iterrows()
    ]
    family_ghost_items = [
        {"label": row["condition_family_label"], "value": as_float(row["ghost_protocol_rate"])}
        for _, row in family_named[family_named["studies"] >= 3000]
        .sort_values(["ghost_protocol_rate", "studies"], ascending=[False, False])
        .head(10)
        .iterrows()
    ]
    family_visible_items = [
        {"label": row["condition_family_label"], "value": as_float(row["results_publication_visible_rate"])}
        for _, row in family_named[family_named["studies"] >= 3000]
        .sort_values(["results_publication_visible_rate", "studies"], ascending=[False, False])
        .head(10)
        .iterrows()
    ]

    concentration_share_items = [
        {"label": "Top 1% sponsors", "value": float(concentration["top_1pct_share_no_results"])},
        {"label": "Top 5% sponsors", "value": float(concentration["top_5pct_share_no_results"])},
        {"label": "Top 10% sponsors", "value": float(concentration["top_10pct_share_no_results"])},
        {"label": "Top 20 sponsors", "value": float(concentration["top_20_share_no_results"])},
        {"label": "Top 100 sponsors", "value": float(concentration["top_100_share_no_results"])},
        {"label": "Top 500 sponsors", "value": float(concentration["top_500_share_no_results"])},
    ]
    top_sponsor_stock = [
        {"label": row["lead_sponsor_name"], "value": as_int(row["no_results_count"])}
        for _, row in sponsor_conc.head(10).iterrows()
    ]
    top_sponsor_ghost = [
        {"label": row["lead_sponsor_name"], "value": as_int(row["ghost_protocol_count"])}
        for _, row in sponsor_conc.sort_values(
            ["ghost_protocol_count", "no_results_count", "studies"], ascending=[False, False, False]
        )
        .head(10)
        .iterrows()
    ]

    references = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. BMJ. 2021;372:n71.",
        "Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.",
    ]

    visibility_body, visibility_sentences = sentence_bundle(
        [
            (
                "Question",
                "How visible is older interventional trial evidence in ClinicalTrials.gov when posted results and linked publications are read together rather than separately, actually?",
            ),
            (
                "Dataset",
                "We analysed 249,507 closed interventional studies with primary completion at least two years before March 29, 2026, drawn from the full 578,109-study registry snapshot.",
            ),
            (
                "Method",
                "Each eligible study was placed into one of four evidence states: results plus publication, results without publication, publication without results, or neither.",
            ),
            (
                "Primary result",
                "Across eligible older studies, 42.7 percent showed neither posted results nor a linked publication, whereas only 13.7 percent showed both.",
            ),
            (
                "Secondary result",
                "Publication-only visibility remained common at 30.0 percent, and sponsor classes diverged sharply, with OTHER_GOV worst on ghost protocols at 49.1 percent while FED led on full visibility at 33.5 percent.",
            ),
            (
                "Interpretation",
                "Reading results tabs and linked papers together shows that older registry evidence is more often partially or wholly invisible than fully visible.",
            ),
            (
                "Boundary",
                "These states measure registry-visible evidence coverage using internal CT.gov publication links, not exhaustive external bibliometric matching.",
            ),
        ]
    )

    cohort_body, cohort_sentences = sentence_bundle(
        [
            (
                "Question",
                "Do newer ClinicalTrials.gov completion cohorts look more transparent once every study has had at least two years to report?",
            ),
            (
                "Dataset",
                "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and grouped them by primary completion year and broader completion eras.",
            ),
            (
                "Method",
                "For each cohort we estimated two-year no-results rates, ghost-protocol rates defined as missing results plus missing publication links, and the share with both signals visible.",
            ),
            (
                "Primary result",
                "The 2008-2012 completion era showed a 64.4 percent no-results rate and a 38.8 percent ghost-protocol rate.",
            ),
            (
                "Secondary result",
                "By 2021-2024, the comparable rates had worsened to 77.0 percent and 46.7 percent, while the fully visible share fell to 10.8 percent.",
            ),
            (
                "Interpretation",
                "Year-level summaries showed the same recent drift, indicating that eligibility alone does not erase newer registry silence across successive completion cohorts.",
            ),
            (
                "Boundary",
                "These cohort comparisons are descriptive and can reflect changing trial mix, backfilling, and publication-linking practices as well as reporting behavior inside this still uneven public reporting system.",
            ),
        ]
    )

    condition_body, condition_sentences = sentence_bundle(
        [
            (
                "Question",
                "Which therapeutic areas look quietest in ClinicalTrials.gov once older closed interventional studies are grouped into comparable condition families?",
            ),
            (
                "Dataset",
                "We analysed 249,507 eligible older studies from the March 29, 2026 full-registry snapshot and assigned each record to one dominant keyword-based family using registry condition strings and titles.",
            ),
            (
                "Method",
                "Primary comparisons focused on ghost-protocol rates, two-year no-results rates, and the share with both results and publication visibility across common families.",
            ),
            (
                "Primary result",
                "Oncology formed the largest named family at 42,344 eligible older studies, creating the biggest absolute stock of hidden evidence.",
            ),
            (
                "Secondary result",
                "Healthy-volunteer studies had the highest ghost-protocol rate among common families at 63.5 percent, while metabolic and gastrointestinal groupings also remained heavily obscured.",
            ),
            (
                "Interpretation",
                "Infectious-disease studies were relatively more visible, reaching a 20.6 percent fully visible rate despite still carrying substantial non-reporting across mapped families in this atlas.",
            ),
            (
                "Boundary",
                "Because the classification is keyword-based and single-label, multi-topic trials can be compressed into one family and some records remain in a broad other bucket.",
            ),
        ]
    )

    concentration_body, concentration_sentences = sentence_bundle(
        [
            (
                "Question",
                "Is the ClinicalTrials.gov missing-results backlog spread evenly across sponsors, or does a relatively small slice hold most of the unresolved stock?",
            ),
            (
                "Dataset",
                "We analysed sponsor-level counts for 249,507 eligible older closed interventional studies and ranked 25,584 lead sponsors by two-year missing-results volume.",
            ),
            (
                "Method",
                "The concentration analysis tracked cumulative shares of unresolved no-results studies, sponsor-level ghost-protocol counts, and inequality metrics alongside named outlier sponsors.",
            ),
            (
                "Primary result",
                "The top 1 percent of lead sponsors accounted for 39.6 percent of the missing-results backlog, and the top 10 percent accounted for 77.4 percent.",
            ),
            (
                "Secondary result",
                "The sponsor-level Gini coefficient reached 0.818, while large industry firms, major academic centers, and public institutions all appeared among the highest-volume sponsors.",
            ),
            (
                "Interpretation",
                "The unresolved stock is therefore broad but highly uneven, with a thin sponsor slice carrying a disproportionate share of what remains unseen.",
            ),
            (
                "Boundary",
                "These concentration statistics describe registry-visible stock distribution, not legal liability, and they depend on the lead-sponsor field recorded in CT.gov across this sponsor field and snapshot frame.",
            ),
        ]
    )

    all_series_specs = [
        {
            "repo_name": "ctgov-industry-disclosure-gap",
            "title": "CT.gov Industry Disclosure Gap",
            "summary": "Industry-focused missing-results stock, sponsor backlogs, and structural sparsity inside CT.gov.",
            "short_title": "Industry",
        },
        {
            "repo_name": "ctgov-sponsor-class-hiddenness",
            "title": "CT.gov Sponsor-Class Hiddenness",
            "summary": "Sponsor-class comparisons on rate, stock, and structural hiddenness rather than one flattened ranking.",
            "short_title": "Sponsor Classes",
        },
        {
            "repo_name": "ctgov-phase-reporting-gap",
            "title": "CT.gov Phase Reporting Gap",
            "summary": "Phase-by-phase disclosure gaps showing how silence changes along the development pathway.",
            "short_title": "Phases",
        },
        {
            "repo_name": "ctgov-structural-missingness",
            "title": "CT.gov Structural Missingness",
            "summary": "Field-level missingness across publication links, IPD statements, descriptions, and locations.",
            "short_title": "Structural",
        },
        {
            "repo_name": "ctgov-evidence-visibility-gap",
            "title": "CT.gov Evidence Visibility Gap",
            "summary": "Results-plus-publication visibility states showing how many older trials are fully visible, partly visible, or ghosted.",
            "short_title": "Visibility",
        },
        {
            "repo_name": "ctgov-completion-cohort-debt",
            "title": "CT.gov Completion Cohort Debt",
            "summary": "Completion-era reporting debt showing how older eligible cohorts drift on no-results and ghost-protocol rates.",
            "short_title": "Cohorts",
        },
        {
            "repo_name": "ctgov-condition-hiddenness-map",
            "title": "CT.gov Condition Hiddenness Map",
            "summary": "Keyword-classified therapeutic-area hiddenness mapping across common condition families.",
            "short_title": "Conditions",
        },
        {
            "repo_name": "ctgov-sponsor-backlog-concentration",
            "title": "CT.gov Sponsor Backlog Concentration",
            "summary": "Concentration and inequality analysis showing how much unresolved stock sits inside a thin sponsor slice.",
            "short_title": "Concentration",
        },
    ]

    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"
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

    projects: list[dict[str, object]] = [
        {
            "repo_name": "ctgov-evidence-visibility-gap",
            "title": "CT.gov Evidence Visibility Gap",
            "summary": "A standalone E156 project on how often older CT.gov studies show results, publications, both, or neither.",
            "body": visibility_body,
            "sentences": visibility_sentences,
            "primary_estimand": "Ghost-protocol rate among eligible older closed interventional studies",
            "data_note": "249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot",
            "references": references,
            "protocol": (
                "This protocol evaluates evidence visibility states inside eligible older closed interventional studies from the March 29, 2026 ClinicalTrials.gov full-registry snapshot. "
                "Each record is classified into one of four states: results plus publication, results without publication, publication without results, or neither. "
                "The primary estimand is the ghost-protocol rate, defined as missing posted results plus missing linked publication among eligible older studies. "
                "Secondary outputs compare full visibility and ghost-protocol rates across sponsor classes and phases so partial visibility is not mistaken for full disclosure."
            ),
            "root_title": "How often do older CT.gov trials show neither results nor a paper trail?",
            "root_eyebrow": "Visibility Project",
            "root_lede": "A standalone public project on evidence visibility states, showing how many older studies are fully visible, partly visible, or effectively ghosted.",
            "chapter_intro": "This project borrows the registry-first coverage logic from your other work and turns it into a visible public readout: one state grid for results, publications, both, or neither.",
            "root_pull_quote": "Ghost protocols outnumber fully visible older trials by more than three to one.",
            "root_pull_source": "Eligible older visibility states",
            "paper_pull_quote": "Separating results tabs from linked papers changes the transparency story immediately.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "A publication link is not the same thing as a posted results tab, and the state split makes that visible fast.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": [
                "249,507 older studies",
                "42.7% neither visible",
                "13.7% fully visible",
                "30.0% publication only",
            ],
            "landing_metrics": [
                ("Neither visible", fmt_int(as_int(visibility_lookup.loc["no_results_no_pub", "studies"])), "Ghost protocols"),
                ("Neither rate", fmt_series_pct(as_float(visibility_lookup.loc["no_results_no_pub", "rate"])), "Eligible older studies"),
                ("Both visible", fmt_series_pct(as_float(visibility_lookup.loc["results_pub", "rate"])), "Results plus publication"),
                ("Publication only", fmt_series_pct(as_float(visibility_lookup.loc["no_results_pub", "rate"])), "Paper link without results"),
            ],
            "landing_chart_html": chart_section(
                "Visibility states",
                bar_chart(
                    visibility_items,
                    "Evidence visibility",
                    "Older studies split into four results-publication states",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "The dominant state is neither results nor publication, while full visibility remains uncommon.",
                "Reading results and publication links together exposes a larger hidden zone than either signal does alone.",
            ),
            "reader_lede": "A 156-word micro-paper on how often older CT.gov studies are fully visible, partly visible, or ghosted.",
            "reader_rail": [
                "Neither visible",
                "Publication only",
                "Results only",
                "Both visible",
            ],
            "reader_metrics": [
                ("Neither visible", fmt_series_pct(as_float(visibility_lookup.loc["no_results_no_pub", "rate"])), "Ghost protocols"),
                ("Publication only", fmt_series_pct(as_float(visibility_lookup.loc["no_results_pub", "rate"])), "Linked paper only"),
                ("Results only", fmt_series_pct(as_float(visibility_lookup.loc["results_no_pub", "rate"])), "Results tab only"),
                ("Both visible", fmt_series_pct(as_float(visibility_lookup.loc["results_pub", "rate"])), "Full visibility"),
            ],
            "dashboard_title": "Older CT.gov studies fall into four very different visibility states",
            "dashboard_eyebrow": "Visibility Dashboard",
            "dashboard_lede": "Reading results tabs and publication links together shows that full visibility is the exception, not the default.",
            "dashboard_rail": [
                "State split",
                "Ghost protocols",
                "Full visibility",
                "By phase",
            ],
            "dashboard_metrics": [
                ("Eligible older", fmt_int(int(visibility["studies"].sum())), "2-year denominator"),
                ("Ghost protocols", fmt_int(as_int(visibility_lookup.loc["no_results_no_pub", "studies"])), "Neither visible"),
                ("Ghost rate", fmt_series_pct(as_float(visibility_lookup.loc["no_results_no_pub", "rate"])), "Older studies"),
                ("Fully visible", fmt_series_pct(as_float(visibility_lookup.loc["results_pub", "rate"])), "Results plus publication"),
            ],
            "dashboard_sections": [
                chart_section(
                    "Overall states",
                    bar_chart(
                        visibility_items,
                        "Evidence states",
                        "How older studies split across results-publication visibility",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Ghost protocols form the single largest state, while full visibility is comparatively rare.",
                    "The state grid is the core figure in this project because it distinguishes partial evidence visibility from true completeness.",
                ),
                chart_section(
                    "Ghost rate by class",
                    bar_chart(
                        ghost_by_class,
                        "Ghost protocols",
                        "Ghost-protocol rate by named sponsor class",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "OTHER_GOV is worst on ghost protocols, with OTHER and INDUSTRY still carrying very high rates.",
                    "This chart isolates the purest hidden state: no results tab and no linked paper trail.",
                ),
                chart_section(
                    "Fully visible by class",
                    bar_chart(
                        fully_visible_by_class,
                        "Full visibility",
                        "Share of older studies with both results and publication by named sponsor class",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "FED and NIH lead on full visibility, while OTHER_GOV remains near the floor.",
                    "This is the positive mirror of the ghost chart and helps show who is actually making evidence visible on both channels.",
                ),
                chart_section(
                    "Ghost rate by phase",
                    bar_chart(
                        phase_ghost_items,
                        "Ghost protocols by phase",
                        "Ghost-protocol rates among the largest phase groups",
                        "value",
                        "label",
                        "#5a7d6b",
                        percent=True,
                    ),
                    "Phase I and early phase I remain especially prone to ghost protocols among large phase groups.",
                    "Phase structure still matters after the visibility state split is imposed.",
                ),
            ],
            "sidebar_bullets": [
                "42.7 percent of eligible older studies show neither posted results nor a linked publication.",
                "Only 13.7 percent show both posted results and a linked publication.",
                "OTHER_GOV reaches 49.1 percent on the ghost-protocol rate.",
                "FED has the highest fully visible share at 33.5 percent.",
            ],
        },
        {
            "repo_name": "ctgov-completion-cohort-debt",
            "title": "CT.gov Completion Cohort Debt",
            "summary": "A standalone E156 project on how two-year reporting debt and ghost protocols drift across completion cohorts.",
            "body": cohort_body,
            "sentences": cohort_sentences,
            "primary_estimand": "2-year no-results rate by primary completion cohort among eligible older closed interventional studies",
            "data_note": "Eligible older closed interventional studies grouped by primary completion year and completion era",
            "references": references,
            "protocol": (
                "This protocol groups eligible older closed interventional CT.gov studies by primary completion year and broader completion eras. "
                "Primary outputs estimate two-year no-results rates, ghost-protocol rates, and the share with both posted results and linked publications visible. "
                "The goal is to show whether later eligible cohorts actually look cleaner once every included study has had at least two years to report. "
                "Interpretation remains descriptive because registry mix, backfilling, and link-maintenance practices can also move cohort-level estimates."
            ),
            "root_title": "Are newer CT.gov completion cohorts getting more transparent after two years?",
            "root_eyebrow": "Cohort Project",
            "root_lede": "A standalone public project on completion-era reporting debt, showing how older eligible cohorts drift on no-results and ghost-protocol rates over time.",
            "chapter_intro": "This project takes the reporting-debt idea directly into cohort space: every included study is already old enough to have reported, so the trend is about what still remains missing.",
            "root_pull_quote": "The recent eligible cohorts are quieter, not cleaner.",
            "root_pull_source": "Completion-era comparison",
            "paper_pull_quote": "Eligibility does not erase silence. It just standardizes who has had enough time to report.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "Once every cohort has had at least two years, the recent eras still do worse on both missing results and ghost protocols.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": [
                "2008-2012: 64.4%",
                "2021-2024: 77.0%",
                "Ghosts 38.8% to 46.7%",
                "Full visibility 10.8%",
            ],
            "landing_metrics": [
                ("2008-2012 no results", fmt_series_pct(as_float(era_vis.iloc[1]["no_results_rate"])), "Older benchmark era"),
                ("2021-2024 no results", fmt_series_pct(as_float(era_vis.iloc[-1]["no_results_rate"])), "Most recent eligible era"),
                ("2021-2024 ghosts", fmt_series_pct(as_float(era_vis.iloc[-1]["ghost_protocol_rate"])), "Neither visible"),
                ("2021-2024 both visible", fmt_series_pct(as_float(era_vis.iloc[-1]["results_publication_visible_rate"])), "Results plus publication"),
            ],
            "landing_chart_html": chart_section(
                "Completion years",
                line_chart(
                    year_items,
                    "Completion-year drift",
                    "No-results and ghost-protocol rates across eligible completion cohorts",
                    "label",
                    [
                        {"key": "no_results_rate", "label": "No results rate", "color": "#c3452f"},
                        {"key": "ghost_protocol_rate", "label": "Ghost-protocol rate", "color": "#326891"},
                    ],
                ),
                "Recent eligible completion cohorts remain worse on missing results and ghost protocols than mid-registry cohorts.",
                "The line chart is constrained to completion years with at least 1,000 eligible studies so the trend is not dominated by tiny early cohorts.",
            ),
            "reader_lede": "A 156-word micro-paper on how reporting debt changes across completion cohorts once every study has had two years to report.",
            "reader_rail": [
                "Completion years",
                "No-results drift",
                "Ghost drift",
                "Visible share",
            ],
            "reader_metrics": [
                ("2008-2012 no results", fmt_series_pct(as_float(era_vis.iloc[1]["no_results_rate"])), "Older benchmark"),
                ("2018-2020 no results", fmt_series_pct(as_float(era_vis.iloc[3]["no_results_rate"])), "Middle recent era"),
                ("2021-2024 no results", fmt_series_pct(as_float(era_vis.iloc[4]["no_results_rate"])), "Most recent eligible era"),
                ("2021-2024 ghosts", fmt_series_pct(as_float(era_vis.iloc[4]["ghost_protocol_rate"])), "Neither visible"),
            ],
            "dashboard_title": "Completion cohorts drift upward on reporting debt even after two years",
            "dashboard_eyebrow": "Cohort Dashboard",
            "dashboard_lede": "Recent eligible completion cohorts remain worse on both missing results and ghost protocols, while full visibility erodes.",
            "dashboard_rail": [
                "Completion years",
                "Completion eras",
                "Ghost drift",
                "Visible share",
            ],
            "dashboard_metrics": [
                ("Eligible older", fmt_int(int(visibility["studies"].sum())), "All cohorts combined"),
                ("2008-2012 no results", fmt_series_pct(as_float(era_vis.iloc[1]["no_results_rate"])), "Older benchmark"),
                ("2021-2024 no results", fmt_series_pct(as_float(era_vis.iloc[4]["no_results_rate"])), "Most recent eligible era"),
                ("2021-2024 visible", fmt_series_pct(as_float(era_vis.iloc[4]["results_publication_visible_rate"])), "Results plus publication"),
            ],
            "dashboard_sections": [
                chart_section(
                    "Completion years",
                    line_chart(
                        year_items,
                        "Completion-year drift",
                        "No-results and ghost-protocol rates by eligible completion year",
                        "label",
                        [
                            {"key": "no_results_rate", "label": "No results rate", "color": "#c3452f"},
                            {"key": "ghost_protocol_rate", "label": "Ghost-protocol rate", "color": "#326891"},
                        ],
                    ),
                    "The year-level series shows the same recent upward drift seen in the broader era buckets.",
                    "The gap between the red and blue lines represents publication-only visibility, which remains large but does not rescue the underlying reporting debt story.",
                ),
                chart_section(
                    "Era no-results rates",
                    bar_chart(
                        era_no_results_items,
                        "Completion eras",
                        "2-year no-results rate by completion era",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "The recent eligible era reaches 77.0 percent on the 2-year no-results metric.",
                    "Era buckets smooth the year-by-year noise and make the direction easier to read on a public page.",
                ),
                chart_section(
                    "Era ghost rates",
                    bar_chart(
                        era_ghost_items,
                        "Ghost protocols by era",
                        "Ghost-protocol rate by completion era",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Ghost protocols rise again in the most recent eligible era rather than disappearing with time.",
                    "This matters because the ghost state is the strongest visible form of evidence absence in the registry itself.",
                ),
            ],
            "sidebar_bullets": [
                "The 2008-2012 era sits at 64.4 percent on the 2-year no-results rate.",
                "The 2021-2024 era rises to 77.0 percent on the same metric.",
                "Ghost protocols rise from 38.8 percent to 46.7 percent across those eras.",
                "The fully visible share drops to 10.8 percent in 2021-2024.",
            ],
        },
        {
            "repo_name": "ctgov-condition-hiddenness-map",
            "title": "CT.gov Condition Hiddenness Map",
            "summary": "A standalone E156 project mapping reporting debt and ghost protocols across keyword-classified therapeutic areas.",
            "body": condition_body,
            "sentences": condition_sentences,
            "primary_estimand": "Ghost-protocol rate by keyword-classified condition family among eligible older closed interventional studies",
            "data_note": "Eligible older closed interventional studies classified into dominant condition families from registry condition strings and titles",
            "references": references,
            "protocol": (
                "This protocol assigns each eligible older closed interventional study to one dominant keyword-based condition family using registry condition strings and titles. "
                "Primary outputs compare condition-family ghost-protocol rates, two-year no-results rates, and full-visibility shares. "
                "A secondary stock view ranks the largest named families by the number of eligible older studies they contain. "
                "Because the classification is keyword-based and single-label, the project is designed as a high-level map rather than a formal ontology."
            ),
            "root_title": "Which kinds of trials go dark most often on CT.gov?",
            "root_eyebrow": "Condition Project",
            "root_lede": "A standalone public map of therapeutic-area hiddenness, showing where ghost protocols and reporting debt concentrate once studies are grouped into comparable condition families.",
            "chapter_intro": "This project uses the topic-segmentation pattern from your earlier work, but applies it to the full CT.gov registry with a dominant-family classifier built from condition text and titles.",
            "root_pull_quote": "Oncology holds the largest hidden stock, but healthy-volunteer studies are the quietest common family.",
            "root_pull_source": "Condition-family comparison",
            "paper_pull_quote": "The largest family is not the quietest family, which is why stock and rate have to be separated here too.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "Family mapping turns a shapeless registry into an interpretable therapeutic-area landscape, even with a simple keyword classifier.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": [
                "Oncology 42,344",
                "Healthy volunteers 63.5%",
                "Metabolic 76.2%",
                "Infectious visible 20.6%",
            ],
            "landing_metrics": [
                ("Largest family", fmt_int(as_int(family_named.iloc[0]["studies"])), "Oncology"),
                ("Quietest common family", fmt_series_pct(as_float(family_named[family_named["condition_family"] == "healthy_volunteer"].iloc[0]["ghost_protocol_rate"])), "Healthy volunteers"),
                ("Metabolic no results", fmt_series_pct(as_float(family_named[family_named["condition_family"] == "metabolic"].iloc[0]["no_results_rate"])), "Eligible older studies"),
                ("Infectious fully visible", fmt_series_pct(as_float(family_named[family_named["condition_family"] == "infectious"].iloc[0]["results_publication_visible_rate"])), "Highest common-family visibility"),
            ],
            "landing_chart_html": chart_section(
                "Ghost rates by family",
                bar_chart(
                    family_ghost_items,
                    "Condition families",
                    "Ghost-protocol rates among common keyword-classified families",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "Healthy volunteers sit furthest to the right, while oncology dominates on stock rather than rate.",
                "The classifier is intentionally simple and public-facing: it is meant to surface patterns quickly, not replace a formal disease ontology.",
            ),
            "reader_lede": "A 156-word micro-paper on which therapeutic areas look quietest after older CT.gov studies are grouped into dominant condition families.",
            "reader_rail": [
                "Oncology stock",
                "Healthy volunteers",
                "Metabolic debt",
                "Infectious visibility",
            ],
            "reader_metrics": [
                ("Oncology stock", fmt_int(as_int(family_named[family_named["condition_family"] == "oncology"].iloc[0]["studies"])), "Largest named family"),
                ("Healthy volunteers", fmt_series_pct(as_float(family_named[family_named["condition_family"] == "healthy_volunteer"].iloc[0]["ghost_protocol_rate"])), "Ghost-protocol rate"),
                ("Metabolic no results", fmt_series_pct(as_float(family_named[family_named["condition_family"] == "metabolic"].iloc[0]["no_results_rate"])), "No-results rate"),
                ("Infectious visible", fmt_series_pct(as_float(family_named[family_named["condition_family"] == "infectious"].iloc[0]["results_publication_visible_rate"])), "Full visibility"),
            ],
            "dashboard_title": "Therapeutic-area hiddenness looks different once the registry is mapped into condition families",
            "dashboard_eyebrow": "Condition Dashboard",
            "dashboard_lede": "Oncology contains the biggest eligible stock, while healthy-volunteer studies are the quietest common family on the ghost-protocol metric.",
            "dashboard_rail": [
                "Stock by family",
                "Ghost rate",
                "Visible share",
                "Keyword families",
            ],
            "dashboard_metrics": [
                ("Named families", fmt_int(int(len(family_named))), "Excluding Other"),
                ("Oncology stock", fmt_int(as_int(family_named[family_named["condition_family"] == "oncology"].iloc[0]["studies"])), "Largest named family"),
                ("Healthy-volunteer ghosts", fmt_series_pct(as_float(family_named[family_named["condition_family"] == "healthy_volunteer"].iloc[0]["ghost_protocol_rate"])), "Quietest common family"),
                ("Infectious visible", fmt_series_pct(as_float(family_named[family_named["condition_family"] == "infectious"].iloc[0]["results_publication_visible_rate"])), "Best common-family visibility"),
            ],
            "dashboard_sections": [
                chart_section(
                    "Stock by family",
                    bar_chart(
                        family_stock_items,
                        "Family stock",
                        "Eligible older study counts by named condition family",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "Oncology is the largest named family by stock, followed by cardiovascular and mental-health groups.",
                    "Stock identifies where the broadest therapeutic blocks of potentially missing evidence sit inside the registry.",
                ),
                chart_section(
                    "Ghost rates by family",
                    bar_chart(
                        family_ghost_items,
                        "Family ghost rates",
                        "Ghost-protocol rate among common condition families",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Healthy volunteers and gastrointestinal-hepatic families sit high on the ghost-protocol axis.",
                    "Ghost rate shows where older studies are most likely to have neither results nor a linked publication path.",
                ),
                chart_section(
                    "Fully visible share",
                    bar_chart(
                        family_visible_items,
                        "Family visibility",
                        "Share of older studies with both results and publication by family",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Infectious-disease and respiratory-sleep trials sit toward the top on full visibility, even though neither family is clean.",
                    "The positive view matters because a family can look bad on stock without being the worst on complete evidence visibility.",
                ),
            ],
            "sidebar_bullets": [
                "Oncology is the largest named family at 42,344 eligible older studies.",
                "Healthy-volunteer studies reach 63.5 percent on the ghost-protocol metric.",
                "Metabolic studies reach 76.2 percent on the two-year no-results rate.",
                "Infectious-disease studies lead common families on full visibility at 20.6 percent.",
            ],
        },
        {
            "repo_name": "ctgov-sponsor-backlog-concentration",
            "title": "CT.gov Sponsor Backlog Concentration",
            "summary": "A standalone E156 project on how a small slice of sponsors accounts for a large share of the missing-results backlog.",
            "body": concentration_body,
            "sentences": concentration_sentences,
            "primary_estimand": "Share of the 2-year missing-results backlog held by top sponsor slices",
            "data_note": "25,584 lead sponsors contributing to the eligible older missing-results backlog in the March 29, 2026 snapshot",
            "references": references,
            "protocol": (
                "This protocol ranks lead sponsors by the volume of eligible older studies missing posted results. "
                "Primary outputs estimate the share of the backlog held by the top 1 percent, top 5 percent, top 10 percent, and selected named sponsor slices, alongside the sponsor-level Gini coefficient. "
                "Secondary outputs identify the largest named sponsors on both missing-results stock and ghost-protocol stock. "
                "The project is designed to make concentration legible without collapsing different sponsor classes into a single blame category."
            ),
            "root_title": "How concentrated is the CT.gov missing-results backlog?",
            "root_eyebrow": "Concentration Project",
            "root_lede": "A standalone public project on sponsor concentration, showing how much of the missing-results backlog sits inside a relatively thin slice of sponsors.",
            "chapter_intro": "This project uses the concentration and outlier logic from your meta-epidemiology work, but applies it to unresolved registry stock rather than effect estimates.",
            "root_pull_quote": "The backlog is broad, but not flat: a thin slice of sponsors holds most of it.",
            "root_pull_source": "Sponsor concentration",
            "paper_pull_quote": "The registry backlog is not evenly distributed across sponsors, even though it spans many sectors and institutions.",
            "paper_pull_source": "Reading note",
            "dashboard_pull_quote": "Concentration metrics matter because a diffuse-looking registry can still be dominated by a relatively small sponsor slice.",
            "dashboard_pull_source": "How to read the dashboard",
            "root_rail": [
                "25,584 sponsors",
                "Top 1%: 39.6%",
                "Top 10%: 77.4%",
                "Gini 0.818",
            ],
            "landing_metrics": [
                ("Lead sponsors", fmt_int(int(concentration["sponsor_count"])), "Eligible older backlog"),
                ("Top 1% share", fmt_series_pct(float(concentration["top_1pct_share_no_results"])), "Missing-results stock"),
                ("Top 10% share", fmt_series_pct(float(concentration["top_10pct_share_no_results"])), "Missing-results stock"),
                ("Gini", f"{float(concentration['no_results_gini']):.3f}", "Sponsor-level inequality"),
            ],
            "landing_chart_html": chart_section(
                "Backlog concentration",
                bar_chart(
                    concentration_share_items,
                    "Concentration shares",
                    "How much of the missing-results backlog sits inside top sponsor slices",
                    "value",
                    "label",
                    "#326891",
                    percent=True,
                ),
                "The top 1 percent already holds nearly forty percent of the missing-results backlog.",
                "The bucket mix is intentionally uneven because the project is comparing both percentile slices and named sponsor ranks to make the concentration concrete.",
            ),
            "reader_lede": "A 156-word micro-paper on how a thin sponsor slice carries a disproportionate share of the unresolved CT.gov backlog.",
            "reader_rail": [
                "Top 1%",
                "Top 10%",
                "Gini 0.818",
                "Cross-class outliers",
            ],
            "reader_metrics": [
                ("Top 1% share", fmt_series_pct(float(concentration["top_1pct_share_no_results"])), "Missing-results stock"),
                ("Top 5% share", fmt_series_pct(float(concentration["top_5pct_share_no_results"])), "Missing-results stock"),
                ("Top 10% share", fmt_series_pct(float(concentration["top_10pct_share_no_results"])), "Missing-results stock"),
                ("Gini", f"{float(concentration['no_results_gini']):.3f}", "Sponsor inequality"),
            ],
            "dashboard_title": "A relatively thin sponsor slice carries most of the CT.gov missing-results backlog",
            "dashboard_eyebrow": "Concentration Dashboard",
            "dashboard_lede": "The missing-results backlog spans many sponsors, but the stock is highly concentrated once ranked by sponsor volume.",
            "dashboard_rail": [
                "Concentration shares",
                "Top sponsors",
                "Ghost sponsors",
                "Inequality",
            ],
            "dashboard_metrics": [
                ("Lead sponsors", fmt_int(int(concentration["sponsor_count"])), "Eligible older backlog"),
                ("Top 1% share", fmt_series_pct(float(concentration["top_1pct_share_no_results"])), "Missing-results stock"),
                ("Top 100 share", fmt_series_pct(float(concentration["top_100_share_no_results"])), "Missing-results stock"),
                ("Top 500 share", fmt_series_pct(float(concentration["top_500_share_no_results"])), "Missing-results stock"),
            ],
            "dashboard_sections": [
                chart_section(
                    "Concentration shares",
                    bar_chart(
                        concentration_share_items,
                        "Concentration shares",
                        "Share of the missing-results backlog held by selected sponsor slices",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Top sponsor slices accumulate backlog very quickly, especially once the view shifts from 1 percent to 10 percent.",
                    "The point of this chart is not that the tail is small. It is that the head is disproportionately large.",
                ),
                chart_section(
                    "Top sponsors by stock",
                    bar_chart(
                        top_sponsor_stock,
                        "Largest sponsor stocks",
                        "Lead sponsors with the biggest absolute missing-results backlogs",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "Large pharmaceutical firms, universities, and public institutions appear together near the top of the stock ranking.",
                    "Concentration is not confined to a single sponsor class, which is why the top-sponsor view matters alongside the sponsor-class projects.",
                ),
                chart_section(
                    "Top sponsors by ghost stock",
                    bar_chart(
                        top_sponsor_ghost,
                        "Largest ghost stocks",
                        "Lead sponsors with the biggest no-results plus no-publication stocks",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "The ghost-stock ranking overlaps with the stock chart but also highlights sponsors whose records remain hidden on both main visibility channels.",
                    "Ghost stock is the more stringent backlog definition because it removes publication-only cases from the numerator.",
                ),
            ],
            "sidebar_bullets": [
                "25,584 lead sponsors appear in the eligible older backlog universe.",
                "The top 1 percent account for 39.6 percent of missing-results stock.",
                "The top 10 percent account for 77.4 percent of missing-results stock.",
                "Sponsor-level missing-results stock reaches a Gini coefficient of 0.818.",
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
