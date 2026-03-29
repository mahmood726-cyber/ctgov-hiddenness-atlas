#!/usr/bin/env python3
"""Build multiple standalone E156-style CT.gov projects from the atlas outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from build_public_site import (
    AI_DISCLOSURE,
    AFFILIATION,
    AUTHOR,
    EMAIL,
    REPO_OWNER,
    as_float,
    as_int,
    bar_chart,
    common_css,
    fmt_int,
    fmt_pct,
    metric_cards,
    read_csv,
    safe,
)

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PROJECTS_ROOT = Path("C:/Projects")
DATE = "2026-03-29"


def render_project_page(
    spec: dict[str, object],
    title: str,
    eyebrow: str,
    lede: str,
    rail: list[str],
    main: str,
    sidebar: str,
) -> str:
    rail_html = "".join(f"<div>{safe(item)}</div>" for item in rail)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe(title)}</title>
  <style>{common_css()}</style>
</head>
<body>
  <div class="page">
    <div class="masthead">
      <div class="brand">{safe(spec["title"])}</div>
      <div class="brand-meta">{safe(DATE)} | full-registry ct.gov audit | plots, figures, and e156 bundle</div>
    </div>
    <section class="hero">
      <div class="eyebrow">{safe(eyebrow)}</div>
      <h1>{safe(title)}</h1>
      <p class="lede">{safe(lede)}</p>
      <div class="hero-rail">{rail_html}</div>
    </section>
    <div class="grid">
      <main>{main}</main>
      <aside class="card">{sidebar}</aside>
    </div>
    <div class="footer">
      <a href="{safe(spec["repo_url"])}">Source on GitHub</a> |
      <a href="{safe(spec["pages_url"])}">Project home</a> |
      <a href="{safe(spec["pages_url"])}e156-submission/assets/dashboard.html">Dashboard</a>
    </div>
  </div>
</body>
</html>
"""


def chart_section(kicker: str, chart_html: str, caption: str) -> str:
    return (
        "<div class='chart-wrap'>"
        f"<div class='kicker'>{safe(kicker)}</div>"
        + chart_html
        + f"<div class='chart-caption'>{safe(caption)}</div>"
        + "</div>"
    )


def sentence_bundle(pairs: list[tuple[str, str]]) -> tuple[str, list[dict[str, str]]]:
    sentences = [{"role": role, "text": text} for role, text in pairs]
    body = " ".join(text for _, text in pairs)
    return body, sentences


def make_config(spec: dict[str, object], repo_path: Path) -> dict[str, object]:
    body = spec["body"]
    sentences = spec["sentences"]
    assert len(str(body).split()) == 156, spec["repo_name"]
    assert len(sentences) == 7, spec["repo_name"]
    return {
        "title": spec["title"],
        "slug": spec["repo_name"],
        "author": AUTHOR,
        "date": DATE,
        "path": str(repo_path),
        "type": "methods",
        "primary_estimand": spec["primary_estimand"],
        "summary": spec["summary"],
        "body": body,
        "sentences": sentences,
        "notes": {
            "app": spec["title"] + " dashboard",
            "data": spec["data_note"],
            "code": spec["repo_url"],
            "doi": "",
            "version": "1.0.0",
            "date": DATE,
            "validation": "FULL REGISTRY RUN",
        },
        "affiliation": AFFILIATION,
        "email": EMAIL,
        "references": spec["references"],
    }


def make_paper(config: dict[str, object]) -> str:
    refs = "\n".join(f"{idx}. {ref}" for idx, ref in enumerate(config["references"], start=1))
    return f"""{AUTHOR}
{AFFILIATION}
{EMAIL}

{config["title"]}

{config["body"]}

Outside Notes

Type: methods
Primary estimand: {config["primary_estimand"]}
App: {config["notes"]["app"]}
Data: {config["notes"]["data"]}
Code: {config["notes"]["code"]}
Version: {config["notes"]["version"]}
Validation: {config["notes"]["validation"]}

References

{refs}

AI Disclosure

{AI_DISCLOSURE}
"""


def make_protocol(spec: dict[str, object]) -> str:
    refs = "\n".join(f"{idx}. {ref}" for idx, ref in enumerate(spec["references"], start=1))
    return f"""{AUTHOR}
{AFFILIATION}
{EMAIL}

Protocol: {spec["title"]}

{spec["protocol"]}

Outside Notes

Type: protocol
Primary estimand: {spec["primary_estimand"]}
App: {spec["title"]} dashboard
Code: {spec["repo_url"]}
Date: {DATE}
Validation: FULL REGISTRY RUN

References

{refs}

AI Disclosure

{AI_DISCLOSURE}
"""


def smoke_test_content() -> str:
    return """import json
from pathlib import Path


def test_repository_smoke():
    root = Path(__file__).resolve().parents[1]
    submission = root / 'e156-submission'
    assets = submission / 'assets'

    for name in ('config.json', 'paper.md', 'protocol.md', 'index.html'):
        assert (submission / name).exists(), name

    assert (assets / 'dashboard.html').exists()

    config = json.loads((submission / 'config.json').read_text(encoding='utf-8'))
    assert len(config.get('body', '').split()) == 156
    assert len(config.get('sentences', [])) == 7
    assert config.get('notes', {}).get('code')
"""


def push_script(repo_name: str) -> str:
    return f"""#!/bin/bash
# Quick push - run after editing the public pages

MSG="${{1:-Update {repo_name}}}"

git add -A
git commit -m "$MSG"
git push origin master 2>/dev/null || git push origin main 2>/dev/null

echo ""
echo "Pushed to GitHub. View at:"
echo "  https://github.com/{REPO_OWNER}/{repo_name}"
echo "  https://{REPO_OWNER}.github.io/{repo_name}/"
"""


def write_project(spec: dict[str, object]) -> Path:
    repo_name = str(spec["repo_name"])
    repo_path = PROJECTS_ROOT / repo_name
    submission = repo_path / "e156-submission"
    assets = submission / "assets"
    tests = repo_path / "tests"
    assets.mkdir(parents=True, exist_ok=True)
    tests.mkdir(parents=True, exist_ok=True)

    config = make_config(spec, repo_path)
    links = (
        "<div class='links'>"
        "<a class='link-card' href='e156-submission/index.html'>E156 micro-paper</a>"
        "<a class='link-card' href='e156-submission/assets/dashboard.html'>Dashboard</a>"
        "<a class='link-card' href='e156-submission/paper.md'>Paper</a>"
        "<a class='link-card' href='e156-submission/protocol.md'>Protocol</a>"
        "</div>"
    )
    root_main = (
        "<section class='card'>"
        "<h2 class='section-title'>Project</h2>"
        f"<p class='body-copy'>{safe(spec['summary'])}</p>"
        + metric_cards(spec["landing_metrics"])
        + spec["landing_chart_html"]
        + "</section>"
    )
    root_sidebar = (
        "<h2 class='section-title'>Notes</h2>"
        "<dl class='note-grid'>"
        f"<dt>Author</dt><dd>{safe(AUTHOR)}</dd>"
        f"<dt>Date</dt><dd>{safe(DATE)}</dd>"
        f"<dt>Repo</dt><dd><a href='{safe(spec['repo_url'])}'>{safe(spec['repo_url'])}</a></dd>"
        f"<dt>Pages</dt><dd><a href='{safe(spec['pages_url'])}'>{safe(spec['pages_url'])}</a></dd>"
        f"<dt>Primary estimand</dt><dd>{safe(spec['primary_estimand'])}</dd>"
        "</dl>"
        + links
    )
    reader_main = (
        "<article class='card'><h2 class='section-title'>Paper</h2>"
        f"<p class='body-copy'>{safe(config['body'])}</p>"
        + metric_cards(spec["reader_metrics"])
        + "</article>"
    )
    reader_sidebar = (
        "<h2 class='section-title'>Outside Notes</h2>"
        "<dl class='note-grid'>"
        f"<dt>App</dt><dd>{safe(config['notes']['app'])}</dd>"
        f"<dt>Data</dt><dd>{safe(config['notes']['data'])}</dd>"
        f"<dt>Code</dt><dd><a href='{safe(spec['repo_url'])}'>{safe(spec['repo_url'])}</a></dd>"
        f"<dt>Version</dt><dd>{safe(config['notes']['version'])}</dd>"
        "</dl>"
        "<div class='links'><a class='link-card' href='assets/dashboard.html'>Dashboard</a><a class='link-card' href='paper.md'>Paper markdown</a><a class='link-card' href='protocol.md'>Protocol markdown</a></div>"
    )
    dashboard_main = (
        "<article class='card'><h2 class='section-title'>Dashboard</h2>"
        + metric_cards(spec["dashboard_metrics"])
        + "".join(spec["dashboard_sections"])
        + "</article>"
    )
    dashboard_sidebar = "<h2 class='section-title'>Readout</h2><ul class='bullet-list'>" + "".join(
        f"<li>{safe(item)}</li>" for item in spec["sidebar_bullets"]
    ) + "</ul>"

    (repo_path / ".gitignore").write_text("__pycache__/\n*.pyc\n.pytest_cache/\n", encoding="utf-8")
    (repo_path / ".nojekyll").write_text("", encoding="utf-8")
    (repo_path / "README.md").write_text(f"# {spec['title']}\n\n{spec['summary']}\n", encoding="utf-8")
    (repo_path / "push.sh").write_text(push_script(repo_name), encoding="utf-8")
    (tests / "test_smoke.py").write_text(smoke_test_content(), encoding="utf-8")
    (repo_path / "index.html").write_text(
        render_project_page(
            spec,
            spec["root_title"],
            spec["root_eyebrow"],
            spec["root_lede"],
            spec["root_rail"],
            root_main,
            root_sidebar,
        ),
        encoding="utf-8",
    )
    (submission / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (submission / "paper.md").write_text(make_paper(config), encoding="utf-8")
    (submission / "protocol.md").write_text(make_protocol(spec), encoding="utf-8")
    (submission / "index.html").write_text(
        render_project_page(
            spec,
            spec["title"],
            "E156 Micro-Paper",
            spec["reader_lede"],
            spec["reader_rail"],
            reader_main,
            reader_sidebar,
        ),
        encoding="utf-8",
    )
    (assets / "dashboard.html").write_text(
        render_project_page(
            spec,
            spec["dashboard_title"],
            spec["dashboard_eyebrow"],
            spec["dashboard_lede"],
            spec["dashboard_rail"],
            dashboard_main,
            dashboard_sidebar,
        ),
        encoding="utf-8",
    )
    return repo_path


def main() -> None:
    sponsor_all = {row["lead_sponsor_class"]: row for row in read_csv(PROCESSED / "sponsor_class_summary_all.csv")}
    sponsor_closed = {
        row["lead_sponsor_class"]: row for row in read_csv(PROCESSED / "sponsor_class_summary_closed_interventional.csv")
    }
    lead_rows = read_csv(PROCESSED / "lead_sponsor_summary_closed_interventional.csv")
    phase_rows = read_csv(PROCESSED / "phase_summary_interventional.csv")

    study_df = pd.read_parquet(
        PROCESSED / "study_features.parquet",
        columns=[
            "is_interventional",
            "is_closed",
            "days_since_primary_completion",
            "results_gap_2y",
            "publication_link_missing",
            "ipd_statement_missing",
            "detailed_description_missing",
            "location_missing",
            "primary_outcomes_missing",
        ],
    )
    older_2y = (
        study_df["is_interventional"] & study_df["is_closed"] & study_df["days_since_primary_completion"].fillna(-1).ge(730)
    )
    older_2y_no_results = older_2y & study_df["results_gap_2y"]
    summary = {
        "total_studies": len(study_df),
        "interventional_studies": int(study_df["is_interventional"].sum()),
        "closed_interventional_studies": int((study_df["is_interventional"] & study_df["is_closed"]).sum()),
        "older_2y_studies": int(older_2y.sum()),
        "older_2y_no_results": int(older_2y_no_results.sum()),
        "two_year_no_results_rate": float(older_2y_no_results.sum() * 100 / older_2y.sum()) if int(older_2y.sum()) else 0.0,
        "no_publication_rate": float(study_df["publication_link_missing"].mean() * 100),
        "no_ipd_rate": float(study_df["ipd_statement_missing"].mean() * 100),
        "no_description_rate": float(study_df["detailed_description_missing"].mean() * 100),
        "no_locations_rate": float(study_df["location_missing"].mean() * 100),
        "no_primary_outcomes_rate": float(study_df["primary_outcomes_missing"].mean() * 100),
    }

    sponsor_rate_items = []
    for code in ["OTHER_GOV", "OTHER", "INDUSTRY", "NETWORK", "INDIV", "NIH", "FED"]:
        row = sponsor_closed.get(code)
        if row:
            sponsor_rate_items.append({"label": code, "value": as_float(row["results_gap_2y_rate_eligible"])})

    sponsor_stock_items = []
    for code in ["OTHER", "INDUSTRY", "OTHER_GOV", "NIH", "NETWORK", "FED", "INDIV"]:
        row = sponsor_closed.get(code)
        if row:
            sponsor_stock_items.append({"label": code, "value": as_int(row["results_gap_2y_count"])})

    phase_rate_items = [
        {"label": row["phase_label"], "value": as_float(row["results_gap_2y_rate_eligible"])}
        for row in sorted(phase_rows, key=lambda item: as_float(item["results_gap_2y_rate_eligible"]), reverse=True)
        if row["phase_label"] != "UNSPECIFIED"
    ]
    phase_stock_items = [
        {"label": row["phase_label"], "value": as_int(row["results_gap_2y_count"])}
        for row in sorted(phase_rows, key=lambda item: as_int(item["results_gap_2y_count"]), reverse=True)
        if row["phase_label"] != "UNSPECIFIED"
    ]

    named_classes = ["OTHER", "INDUSTRY", "OTHER_GOV", "NIH", "NETWORK", "FED", "INDIV"]
    ipd_by_class = [
        {"label": code, "value": as_float(sponsor_all[code]["ipd_statement_missing_rate"])}
        for code in sorted(named_classes, key=lambda item: as_float(sponsor_all[item]["ipd_statement_missing_rate"]), reverse=True)
    ]
    pubs_by_class = [
        {"label": code, "value": as_float(sponsor_all[code]["publication_link_missing_rate"])}
        for code in sorted(named_classes, key=lambda item: as_float(sponsor_all[item]["publication_link_missing_rate"]), reverse=True)
    ]

    industry_rows = [row for row in lead_rows if row["lead_sponsor_class"] == "INDUSTRY"]
    top_industry_by_count = sorted(
        industry_rows,
        key=lambda row: (as_int(row["results_gap_2y_count"]), as_int(row["studies"])),
        reverse=True,
    )[:10]
    top_industry_by_rate = sorted(
        industry_rows,
        key=lambda row: (as_float(row["results_gap_2y_rate_eligible"]), as_int(row["eligible_results_gap_2y_count"])),
        reverse=True,
    )[:10]
    industry_count_items = [
        {"label": row["lead_sponsor_name"], "value": as_int(row["results_gap_2y_count"])} for row in top_industry_by_count
    ]
    industry_rate_items = [
        {"label": row["lead_sponsor_name"], "value": as_float(row["results_gap_2y_rate_eligible"])}
        for row in top_industry_by_rate
    ]

    structure_items = [
        {"label": "No publication link", "value": summary["no_publication_rate"]},
        {"label": "No IPD statement", "value": summary["no_ipd_rate"]},
        {"label": "No detailed description", "value": summary["no_description_rate"]},
        {"label": "No locations", "value": summary["no_locations_rate"]},
    ]

    references = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. BMJ. 2021;372:n71.",
        "Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.",
    ]

    industry_body, industry_sentences = sentence_bundle(
        [
            ("Question", "How large is the industry-specific disclosure gap inside the live ClinicalTrials.gov registry?"),
            (
                "Dataset",
                "We analysed the March 29, 2026 full-registry snapshot, focusing on 128,464 industry-linked studies and 87,296 closed interventional industry studies.",
            ),
            (
                "Method",
                "We derived sponsor-level omission flags for missing results, missing actual dates, missing actual enrollment, missing IPD statements, missing publication links, and missing detailed descriptions, while preserving sponsor-level counts so absolute backlog and rate-based silence could be read together across named firms globally.",
            ),
            (
                "Primary result",
                "Among eligible older closed interventional industry studies, 58.1 percent still had no posted results, leaving 44,007 unresolved two-year no-results records in the industry bucket alone.",
            ),
            (
                "Secondary result",
                "The biggest absolute backlogs sat with GlaxoSmithKline, AstraZeneca, Boehringer Ingelheim, Sanofi, and Pfizer, while several smaller sponsors exceeded 95 percent on the same rate metric.",
            ),
            (
                "Interpretation",
                "Industry records were also structurally sparse, with 63.2 percent lacking IPD statements, 66.6 percent lacking publication links, and 53.8 percent lacking detailed descriptions.",
            ),
            ("Boundary", "These estimates identify registry-visible non-disclosure rather than adjudicated legal breach."),
        ]
    )

    sponsor_body, sponsor_sentences = sentence_bundle(
        [
            ("Question", "Which sponsor classes account for the biggest and worst ClinicalTrials.gov disclosure failures?"),
            (
                "Dataset",
                "We analysed 578,109 registry records captured on March 29, 2026, with particular attention to 290,524 closed interventional studies and 249,507 eligible older studies.",
            ),
            (
                "Method",
                "We summarized two-year no-results gaps, structural missingness, and composite hiddenness scores by sponsor class using the full flattened study-level feature set, deliberately separating rates, stocks, and missing-field patterns instead of collapsing everything into one composite leaderboard for public interpretation and oversight.",
            ),
            (
                "Primary result",
                "OTHER_GOV had the worst eligible two-year no-results rate at 95.7 percent, whereas OTHER held the largest absolute stock at 127,704 missing-results studies.",
            ),
            (
                "Secondary result",
                "Industry remained too large to dismiss, contributing 44,007 two-year no-results studies, while NIH had the highest average hiddenness score among named sponsor classes.",
            ),
            (
                "Interpretation",
                "The class pattern therefore changes depending on whether one prioritizes rates, absolute stock, or structural sparsity, which means a single leaderboard is misleading.",
            ),
            ("Boundary", "These estimates capture observable registry omission rather than motive or legal culpability."),
        ]
    )

    phase_body, phase_sentences = sentence_bundle(
        [
            ("Question", "Does reporting failure in ClinicalTrials.gov differ systematically by trial phase?"),
            (
                "Dataset",
                "We analysed the March 29, 2026 full-registry snapshot and grouped interventional studies by reported phase before calculating eligible two-year no-results rates and absolute missing-results stock.",
            ),
            (
                "Method",
                "The analysis used 441,191 interventional studies overall, with 290,524 closed interventional studies and 249,507 eligible older studies driving the primary comparisons.",
            ),
            (
                "Primary result",
                "Phase I had the highest eligible two-year no-results rate at 76.7 percent, followed by the large NA phase bucket at 65.5 percent and early phase I at 64.3 percent.",
            ),
            (
                "Secondary result",
                "By absolute count, the NA bucket contributed 96,605 unresolved two-year no-results studies, far exceeding later phases because of its scale, which shows phase structure shapes reporting behavior even before sponsor mix and therapeutic area are considered jointly.",
            ),
            (
                "Interpretation",
                "Phase III and phase IV performed better than phase I, but still remained far from transparent at 45.5 percent and 52.4 percent respectively.",
            ),
            ("Boundary", "These phase estimates describe registry-visible non-disclosure rather than confirmed regulatory violation."),
        ]
    )

    structural_body, structural_sentences = sentence_bundle(
        [
            (
                "Question",
                "What information disappears from ClinicalTrials.gov even before one asks whether results were posted?",
            ),
            (
                "Dataset",
                "We analysed the March 29, 2026 full-registry snapshot and quantified structural missingness in publication links, IPD statements, detailed descriptions, locations, and outcome fields across sponsor groups.",
            ),
            (
                "Method",
                "The source universe included 578,109 studies, allowing field-level omission rates and sponsor-specific sparsity patterns to be estimated without sampling.",
            ),
            (
                "Primary result",
                "Across the full registry, 63.4 percent of records lacked publication links, 48.3 percent lacked IPD sharing statements, 32.7 percent lacked detailed descriptions, and 10.2 percent lacked locations.",
            ),
            (
                "Secondary result",
                "Structural sparsity was not evenly distributed: industry remained heavily affected, NIH had the highest average hiddenness score among named sponsor classes, and UNKNOWN mostly reflected malformed metadata.",
            ),
            (
                "Interpretation",
                "Missingness therefore extends beyond results reporting into the descriptive fields needed for interpretation, replication, and scrutiny, with the loss being less context for appraisal, replication, accountability, and public scrutiny across therapeutic areas.",
            ),
            ("Boundary", "These metrics capture registry-visible information loss rather than proven intent to conceal."),
        ]
    )

    projects: list[dict[str, object]] = [
        {
            "repo_name": "ctgov-industry-disclosure-gap",
            "title": "CT.gov Industry Disclosure Gap",
            "summary": "A standalone E156 project on how much long-past non-disclosure and structural sparsity remain inside industry-linked ClinicalTrials.gov records.",
            "body": industry_body,
            "sentences": industry_sentences,
            "primary_estimand": "2-year no-results rate among eligible older closed interventional industry studies",
            "data_note": "128,464 industry-linked studies from the March 29, 2026 full-registry snapshot",
            "references": references,
            "protocol": (
                "This protocol isolates the industry-linked segment of the March 29, 2026 ClinicalTrials.gov full-registry snapshot. "
                "The source universe includes 128,464 industry-linked studies, including 87,296 closed interventional industry studies. "
                "The primary estimand is the 2-year no-results rate among eligible older closed interventional industry studies, with secondary estimates for missing actual dates, missing actual enrollment, absent IPD statements, absent linked publication references, and absent detailed descriptions. "
                "Outputs emphasize both absolute sponsor backlogs and rate-based sponsor silence so large multinational portfolios are not conflated with smaller sponsors showing near-complete non-reporting."
            ),
            "root_title": "How much of the CT.gov disclosure gap sits inside industry?",
            "root_eyebrow": "Industry Project",
            "root_lede": "A standalone public project focused on the size, shape, and leading sponsors of the industry disclosure backlog.",
            "root_rail": ["Industry only", "44,007 hidden results", "58.1% eligible rate", "Top sponsors"],
            "landing_metrics": [
                ("Industry studies", fmt_int(as_int(sponsor_all["INDUSTRY"]["studies"])), "All industry-linked records"),
                ("Closed interventional", fmt_int(as_int(sponsor_closed["INDUSTRY"]["studies"])), "Industry only"),
                ("2-year stock", fmt_int(as_int(sponsor_closed["INDUSTRY"]["results_gap_2y_count"])), "Older studies with no results"),
                ("Eligible rate", fmt_pct(as_float(sponsor_closed["INDUSTRY"]["results_gap_2y_rate_eligible"])), "Older closed interventional"),
            ],
            "landing_chart_html": chart_section(
                "Top sponsors",
                bar_chart(
                    industry_count_items[:8],
                    "Industry by stock",
                    "Largest industry sponsors by absolute 2-year no-results count",
                    "value",
                    "label",
                    "#c3452f",
                    percent=False,
                ),
                "The largest unresolved industry blocks sit with GlaxoSmithKline, AstraZeneca, Boehringer Ingelheim, Sanofi, and Pfizer.",
            ),
            "reader_lede": "A 156-word micro-paper on how much of the public CT.gov silence still sits inside industry-linked records.",
            "reader_rail": ["Industry only", "44,007 stock", "58.1% rate", "Field sparsity"],
            "reader_metrics": [
                ("Industry studies", fmt_int(as_int(sponsor_all["INDUSTRY"]["studies"])), "Full industry universe"),
                ("No IPD statement", fmt_pct(as_float(sponsor_closed["INDUSTRY"]["ipd_statement_missing_rate"])), "Closed interventional"),
                ("No publication link", fmt_pct(as_float(sponsor_closed["INDUSTRY"]["publication_link_missing_rate"])), "Closed interventional"),
                ("No description", fmt_pct(as_float(sponsor_closed["INDUSTRY"]["detailed_description_missing_rate"])), "Closed interventional"),
            ],
            "dashboard_title": "Inside the industry CT.gov disclosure backlog",
            "dashboard_eyebrow": "Industry Dashboard",
            "dashboard_lede": "Industry is not the only hiddenness category, but it still carries a large unresolved stock and substantial structural sparsity.",
            "dashboard_rail": ["Absolute stock", "Eligible rates", "Top sponsors", "Structural gaps"],
            "dashboard_metrics": [
                ("Industry studies", fmt_int(as_int(sponsor_all["INDUSTRY"]["studies"])), "All industry-linked records"),
                ("Closed interventional", fmt_int(as_int(sponsor_closed["INDUSTRY"]["studies"])), "Industry only"),
                ("2-year stock", fmt_int(as_int(sponsor_closed["INDUSTRY"]["results_gap_2y_count"])), "No posted results"),
                ("Eligible rate", fmt_pct(as_float(sponsor_closed["INDUSTRY"]["results_gap_2y_rate_eligible"])), "Older closed studies"),
            ],
            "dashboard_sections": [
                chart_section(
                    "Absolute stock",
                    bar_chart(
                        industry_count_items,
                        "Industry by stock",
                        "Largest industry sponsors by absolute 2-year no-results count",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "The biggest absolute backlogs sit with large multinational portfolios rather than obscure sponsors.",
                ),
                chart_section(
                    "Rate leaders",
                    bar_chart(
                        industry_rate_items,
                        "Industry by rate",
                        "Highest industry 2-year no-results rates among sponsors with at least 50 eligible older studies",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Rate-based leaders are not always the same firms that dominate the raw count of unresolved studies.",
                ),
                chart_section(
                    "Field sparsity",
                    bar_chart(
                        [
                            {"label": "No publication link", "value": as_float(sponsor_closed["INDUSTRY"]["publication_link_missing_rate"])},
                            {"label": "No IPD statement", "value": as_float(sponsor_closed["INDUSTRY"]["ipd_statement_missing_rate"])},
                            {"label": "No detailed description", "value": as_float(sponsor_closed["INDUSTRY"]["detailed_description_missing_rate"])},
                            {"label": "No locations", "value": as_float(sponsor_closed["INDUSTRY"]["location_missing_rate"])},
                        ],
                        "Industry structure",
                        "Structural missingness rates in closed interventional industry studies",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "The disclosure gap is not limited to results posting; explanatory fields are often sparse as well.",
                ),
            ],
            "sidebar_bullets": [
                "Industry contributes 44,007 two-year no-results studies.",
                "58.1 percent of eligible older closed interventional industry studies still have no posted results.",
                "63.2 percent of closed interventional industry studies lack an IPD sharing statement.",
                "66.6 percent lack a linked publication reference.",
            ],
        },
        {
            "repo_name": "ctgov-sponsor-class-hiddenness",
            "title": "CT.gov Sponsor-Class Hiddenness",
            "summary": "A standalone E156 project comparing sponsor classes on rate, stock, and structural sparsity rather than flattening everything into one leaderboard.",
            "body": sponsor_body,
            "sentences": sponsor_sentences,
            "primary_estimand": "Sponsor-class comparison of eligible 2-year no-results rate and absolute missing-results stock",
            "data_note": "Full March 29, 2026 ClinicalTrials.gov snapshot grouped by sponsor class",
            "references": references,
            "protocol": (
                "This protocol compares sponsor classes across the full March 29, 2026 ClinicalTrials.gov registry snapshot rather than focusing on one sector. "
                "The main comparison set is the 290,524 closed interventional studies, with the 249,507 studies at least two years past primary completion driving the primary estimand. "
                "The project estimates rate-based 2-year no-results gaps, absolute missing-results stock, and structural sparsity indicators by sponsor class. "
                "Interpretation is explicitly multi-axis, because the class with the worst rate is not the same as the class with the largest unresolved stock."
            ),
            "root_title": "Which sponsor classes are worst on rate, and which are biggest on stock?",
            "root_eyebrow": "Sponsor-Class Project",
            "root_lede": "A standalone public comparison of sponsor classes that separates rate-based failure from absolute disclosure burden.",
            "root_rail": ["Sponsor classes", "95.7% worst rate", "127,704 largest stock", "NIH highest named-class score"],
            "landing_metrics": [
                ("Worst rate", fmt_pct(as_float(sponsor_closed["OTHER_GOV"]["results_gap_2y_rate_eligible"])), "OTHER_GOV"),
                ("Largest stock", fmt_int(as_int(sponsor_closed["OTHER"]["results_gap_2y_count"])), "OTHER"),
                ("Industry stock", fmt_int(as_int(sponsor_closed["INDUSTRY"]["results_gap_2y_count"])), "Still material"),
                ("NIH score", f"{as_float(sponsor_all['NIH']['mean_hiddenness_score']):.2f}", "Highest named-class mean"),
            ],
            "landing_chart_html": chart_section(
                "Rate versus stock",
                bar_chart(
                    sponsor_stock_items,
                    "Sponsor-class stock",
                    "Absolute 2-year no-results counts by sponsor class",
                    "value",
                    "label",
                    "#c3452f",
                    percent=False,
                ),
                "OTHER dominates by unresolved stock, but OTHER_GOV is worse on the eligible rate metric.",
            ),
            "reader_lede": "A 156-word sponsor-class comparison that separates systematic silence from absolute hidden stock.",
            "reader_rail": ["OTHER_GOV rate", "OTHER stock", "Industry burden", "NIH score"],
            "reader_metrics": [
                ("OTHER_GOV rate", fmt_pct(as_float(sponsor_closed["OTHER_GOV"]["results_gap_2y_rate_eligible"])), "Worst eligible rate"),
                ("OTHER stock", fmt_int(as_int(sponsor_closed["OTHER"]["results_gap_2y_count"])), "Largest unresolved block"),
                ("Industry stock", fmt_int(as_int(sponsor_closed["INDUSTRY"]["results_gap_2y_count"])), "Still large"),
                ("NIH hiddenness", f"{as_float(sponsor_all['NIH']['mean_hiddenness_score']):.2f}", "Named-class peak"),
            ],
            "dashboard_title": "Sponsor classes split the disclosure problem in different ways",
            "dashboard_eyebrow": "Sponsor-Class Dashboard",
            "dashboard_lede": "OTHER_GOV is worst on rate, OTHER is worst on stock, and industry remains too large to dismiss.",
            "dashboard_rail": ["Rate vs stock", "OTHER_GOV", "OTHER", "Industry still large"],
            "dashboard_metrics": [
                ("Closed interventional", fmt_int(summary["closed_interventional_studies"]), "All sponsor classes"),
                ("Eligible older", fmt_int(summary["older_2y_studies"]), "2-year denominator"),
                ("Worst rate", fmt_pct(as_float(sponsor_closed["OTHER_GOV"]["results_gap_2y_rate_eligible"])), "OTHER_GOV"),
                ("Largest stock", fmt_int(as_int(sponsor_closed["OTHER"]["results_gap_2y_count"])), "OTHER"),
            ],
            "dashboard_sections": [
                chart_section(
                    "Rates",
                    bar_chart(
                        sponsor_rate_items,
                        "Sponsor-class rate",
                        "Eligible 2-year no-results rate by sponsor class",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Rate identifies systematic opacity. OTHER_GOV is the standout class on this axis.",
                ),
                chart_section(
                    "Stock",
                    bar_chart(
                        sponsor_stock_items,
                        "Sponsor-class stock",
                        "Absolute 2-year no-results counts by sponsor class",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "Absolute stock identifies where the largest unseen block sits, and that block belongs to OTHER.",
                ),
            ],
            "sidebar_bullets": [
                "OTHER_GOV is worst on the eligible 2-year no-results rate.",
                "OTHER contains the largest absolute stock of unresolved missing-results studies.",
                "INDUSTRY still contributes 44,007 long-past missing-results records.",
                "NIH has the highest average hiddenness score among named sponsor classes.",
            ],
        },
        {
            "repo_name": "ctgov-phase-reporting-gap",
            "title": "CT.gov Phase Reporting Gap",
            "summary": "A standalone E156 project on how reporting gaps change by trial phase, showing that phase structure matters alongside sponsor class.",
            "body": phase_body,
            "sentences": phase_sentences,
            "primary_estimand": "Eligible 2-year no-results rate by reported trial phase",
            "data_note": "441,191 interventional studies from the March 29, 2026 full-registry snapshot grouped by phase",
            "references": references,
            "protocol": (
                "This protocol groups interventional ClinicalTrials.gov studies by reported phase using the March 29, 2026 full-registry snapshot. "
                "The main comparison set includes 441,191 interventional studies, with 290,524 closed interventional studies and 249,507 eligible older studies driving the primary estimand. "
                "Primary outputs compare eligible 2-year no-results rates and unresolved missing-results stock across phase labels, including the large NA bucket. "
                "The aim is to show how reporting silence changes across the development pathway rather than treating sponsor class as the only structural explanation."
            ),
            "root_title": "Where do trial phases go quiet in CT.gov?",
            "root_eyebrow": "Phase Project",
            "root_lede": "A standalone public project on how much registry silence concentrates in phase I, early phase I, the NA bucket, and later phases.",
            "root_rail": ["Phase I 76.7%", "NA 96,605 stock", "Phase III 45.5%", "Phase IV 52.4%"],
            "landing_metrics": [
                ("Interventional", fmt_int(summary["interventional_studies"]), "All phase-labelled studies"),
                ("Closed interventional", fmt_int(summary["closed_interventional_studies"]), "Primary set"),
                ("Phase I rate", fmt_pct(as_float(next(row["results_gap_2y_rate_eligible"] for row in phase_rows if row["phase_label"] == "PHASE1"))), "Highest phase-specific rate"),
                ("NA stock", fmt_int(as_int(next(row["results_gap_2y_count"] for row in phase_rows if row["phase_label"] == "NA"))), "Largest unresolved count"),
            ],
            "landing_chart_html": chart_section(
                "Phase rate",
                bar_chart(
                    phase_rate_items[:8],
                    "Phase rate",
                    "Eligible 2-year no-results rate by reported phase",
                    "value",
                    "label",
                    "#8b6914",
                    percent=True,
                ),
                "Phase I is worst on rate, while the large NA bucket remains close behind and dominates by scale.",
            ),
            "reader_lede": "A 156-word phase-based account of where CT.gov reporting silence is most concentrated across the development pathway.",
            "reader_rail": ["Phase I", "NA bucket", "Phase III", "Phase IV"],
            "reader_metrics": [
                ("Phase I rate", fmt_pct(as_float(next(row["results_gap_2y_rate_eligible"] for row in phase_rows if row["phase_label"] == "PHASE1"))), "Highest rate"),
                ("NA stock", fmt_int(as_int(next(row["results_gap_2y_count"] for row in phase_rows if row["phase_label"] == "NA"))), "Largest count"),
                ("Phase III rate", fmt_pct(as_float(next(row["results_gap_2y_rate_eligible"] for row in phase_rows if row["phase_label"] == "PHASE3"))), "Later-stage benchmark"),
                ("Phase IV rate", fmt_pct(as_float(next(row["results_gap_2y_rate_eligible"] for row in phase_rows if row["phase_label"] == "PHASE4"))), "Post-marketing benchmark"),
            ],
            "dashboard_title": "Phase matters: early studies go quiet most often",
            "dashboard_eyebrow": "Phase Dashboard",
            "dashboard_lede": "The phase gradient shows that non-disclosure is not just sponsor-specific. Phase I is worst on rate, while the NA bucket dominates by scale.",
            "dashboard_rail": ["Phase I rate", "NA stock", "Later phases", "Eligible 2-year gap"],
            "dashboard_metrics": [
                ("Interventional", fmt_int(summary["interventional_studies"]), "All phase-labelled studies"),
                ("Eligible older", fmt_int(summary["older_2y_studies"]), "2-year denominator"),
                ("Phase I rate", fmt_pct(as_float(next(row["results_gap_2y_rate_eligible"] for row in phase_rows if row["phase_label"] == "PHASE1"))), "Highest phase-specific rate"),
                ("NA stock", fmt_int(as_int(next(row["results_gap_2y_count"] for row in phase_rows if row["phase_label"] == "NA"))), "Largest unresolved block"),
            ],
            "dashboard_sections": [
                chart_section(
                    "Rates",
                    bar_chart(
                        phase_rate_items[:8],
                        "Phase rate",
                        "Eligible 2-year no-results rate by phase label",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Phase I is the quietest major phase on a rate basis, with early phase I and NA also notably opaque.",
                ),
                chart_section(
                    "Stock",
                    bar_chart(
                        phase_stock_items[:8],
                        "Phase stock",
                        "Absolute 2-year no-results counts by phase label",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "The NA bucket overwhelms all later phases on raw unresolved stock because of its size.",
                ),
            ],
            "sidebar_bullets": [
                "Phase I reaches 76.7 percent on the eligible 2-year no-results rate.",
                "The NA bucket contains 96,605 unresolved two-year no-results studies.",
                "Early phase I also performs poorly at 64.3 percent.",
                "Phase III and phase IV remain far from transparent despite better rates than phase I.",
            ],
        },
        {
            "repo_name": "ctgov-structural-missingness",
            "title": "CT.gov Structural Missingness",
            "summary": "A standalone E156 project on the descriptive fields that disappear from ClinicalTrials.gov even before results reporting is considered.",
            "body": structural_body,
            "sentences": structural_sentences,
            "primary_estimand": "Field-level structural missingness across the full registry",
            "data_note": "578,109 ClinicalTrials.gov records from the March 29, 2026 full-registry snapshot",
            "references": references,
            "protocol": (
                "This protocol quantifies field-level structural missingness across the March 29, 2026 ClinicalTrials.gov full-registry snapshot. "
                "The full 578,109-study universe is used to estimate missingness in publication links, IPD statements, detailed descriptions, locations, and outcome fields. "
                "Secondary outputs compare structural sparsity across sponsor classes so descriptive loss is not mistaken for a uniform registry problem. "
                "The project is designed to surface information loss that occurs even when results-reporting rules are not the direct analytic target."
            ),
            "root_title": "What disappears from CT.gov before results are even considered?",
            "root_eyebrow": "Structural Project",
            "root_lede": "A standalone public project on missing publication links, IPD statements, detailed descriptions, locations, and other structural fields.",
            "root_rail": ["63.4% no publication link", "48.3% no IPD statement", "32.7% no description", "10.2% no locations"],
            "landing_metrics": [
                ("Registry size", fmt_int(summary["total_studies"]), "All studies"),
                ("No publication link", fmt_pct(summary["no_publication_rate"]), "Full registry"),
                ("No IPD statement", fmt_pct(summary["no_ipd_rate"]), "Full registry"),
                ("No description", fmt_pct(summary["no_description_rate"]), "Full registry"),
            ],
            "landing_chart_html": chart_section(
                "Global gaps",
                bar_chart(
                    structure_items,
                    "Structural sparsity",
                    "Global missingness rates across the full registry",
                    "value",
                    "label",
                    "#8b6914",
                    percent=True,
                ),
                "Publication links and IPD statements disappear far more often than primary outcomes or location fields.",
            ),
            "reader_lede": "A 156-word micro-paper on what disappears from the registry before results reporting is even considered.",
            "reader_rail": ["Publication links", "IPD statements", "Descriptions", "Locations"],
            "reader_metrics": [
                ("No publication link", fmt_pct(summary["no_publication_rate"]), "All studies"),
                ("No IPD statement", fmt_pct(summary["no_ipd_rate"]), "All studies"),
                ("No description", fmt_pct(summary["no_description_rate"]), "All studies"),
                ("No locations", fmt_pct(summary["no_locations_rate"]), "All studies"),
            ],
            "dashboard_title": "What disappears from CT.gov before results are even considered",
            "dashboard_eyebrow": "Structural Dashboard",
            "dashboard_lede": "Results reporting is only one layer of hiddenness. Publication links, IPD statements, descriptions, and locations disappear at scale too.",
            "dashboard_rail": ["Global gaps", "By sponsor class", "IPD", "Publication links"],
            "dashboard_metrics": [
                ("Registry size", fmt_int(summary["total_studies"]), "All studies"),
                ("No publication link", fmt_pct(summary["no_publication_rate"]), "Largest global field gap"),
                ("No IPD statement", fmt_pct(summary["no_ipd_rate"]), "Second-largest global field gap"),
                ("No locations", fmt_pct(summary["no_locations_rate"]), "Smaller but still material"),
            ],
            "dashboard_sections": [
                chart_section(
                    "Global view",
                    bar_chart(
                        structure_items,
                        "Structural sparsity",
                        "Global missingness rates across the full registry",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "The largest structural gaps are publication links and IPD statements rather than outcomes or titles.",
                ),
                chart_section(
                    "IPD by class",
                    bar_chart(
                        ipd_by_class,
                        "IPD statement gaps",
                        "Missing IPD statement rate by named sponsor class",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "NIH is the highest named sponsor class on IPD statement missingness, with industry also heavily affected.",
                ),
                chart_section(
                    "Publications by class",
                    bar_chart(
                        pubs_by_class,
                        "Publication-link gaps",
                        "Missing linked publication rate by named sponsor class",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Industry leads the major named classes on publication-link missingness, while NIH is much lower on this field.",
                ),
            ],
            "sidebar_bullets": [
                "63.4 percent of records lack a linked publication reference.",
                "48.3 percent lack an IPD sharing statement.",
                "32.7 percent lack a detailed description.",
                "UNKNOWN mostly reflects malformed metadata rather than a large substantive sponsor group.",
            ],
        },
    ]

    for spec in projects:
        spec["repo_url"] = f"https://github.com/{REPO_OWNER}/{spec['repo_name']}"
        spec["pages_url"] = f"https://{REPO_OWNER}.github.io/{spec['repo_name']}/"
        path = write_project(spec)
        print(f"Built {path}")


if __name__ == "__main__":
    main()
