#!/usr/bin/env python3
"""Build the public E156 bundle and NYT-style dashboard pages."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
SUBMISSION = ROOT / "e156-submission"
ASSETS = SUBMISSION / "assets"

REPO_NAME = "ctgov-hiddenness-atlas"
REPO_OWNER = "mahmood726-cyber"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
PAGES_URL = f"https://{REPO_OWNER}.github.io/{REPO_NAME}/"
AUTHOR = "Mahmood Ahmad"
AFFILIATION = "Tahir Heart Institute"
EMAIL = "author@example.com"
DATE = "2026-03-29"
VERSION = "1.0.0"

BODY = (
    "Which sponsor groups account for the largest registry-visible non-disclosure burden across ClinicalTrials.gov? "
    "We analysed 578,109 registry records downloaded on March 29, 2026, including 441,191 interventional studies and 290,524 closed interventional studies. "
    "We derived omission flags for missing results, missing actual completion dates, missing actual enrollment, absent IPD statements, absent publication links, sparse outcomes, and undisclosed stopping reasons, then summarized them by sponsor class, sponsor, and phase. "
    "Among closed interventional studies with primary completion at least two years earlier, 72.7 percent still had no posted results, with OTHER_GOV worst on rate at 95.7 percent and OTHER largest on volume at 127,704 studies. "
    "Industry still carried 44,007 two-year no-results studies, phase I had the highest non-reporting rate at 76.7 percent, and NIH had the highest average hiddenness score among named sponsor classes. "
    "Registry opacity is concentrated differently by class, so rates, volumes, and structural missingness must be read together. "
    "These measures capture registry-visible omission rather than legal violation."
)

SENTENCES = [
    {
        "role": "Question",
        "text": "Which sponsor groups account for the largest registry-visible non-disclosure burden across ClinicalTrials.gov?",
    },
    {
        "role": "Dataset",
        "text": "We analysed 578,109 registry records downloaded on March 29, 2026, including 441,191 interventional studies and 290,524 closed interventional studies.",
    },
    {
        "role": "Method",
        "text": "We derived omission flags for missing results, missing actual completion dates, missing actual enrollment, absent IPD statements, absent publication links, sparse outcomes, and undisclosed stopping reasons, then summarized them by sponsor class, sponsor, and phase.",
    },
    {
        "role": "Primary result",
        "text": "Among closed interventional studies with primary completion at least two years earlier, 72.7 percent still had no posted results, with OTHER_GOV worst on rate at 95.7 percent and OTHER largest on volume at 127,704 studies.",
    },
    {
        "role": "Robustness",
        "text": "Industry still carried 44,007 two-year no-results studies, phase I had the highest non-reporting rate at 76.7 percent, and NIH had the highest average hiddenness score among named sponsor classes.",
    },
    {
        "role": "Interpretation",
        "text": "Registry opacity is concentrated differently by class, so rates, volumes, and structural missingness must be read together.",
    },
    {
        "role": "Boundary",
        "text": "These measures capture registry-visible omission rather than legal violation.",
    },
]

AI_DISCLOSURE = (
    "This work represents a compiler-generated evidence micro-publication built from structured registry data and "
    "deterministic summary code. AI was used as a constrained coding and drafting assistant for interface generation, "
    "packaging, and prose refinement, not as an autonomous author. The analytical choices, interpretation, and final "
    "outputs were reviewed by the author, who takes responsibility for the content."
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def as_int(value: str | int | float | None) -> int:
    if value in (None, ""):
        return 0
    return int(float(value))


def as_float(value: str | int | float | None) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def fmt_int(value: int) -> str:
    return f"{value:,}"


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def safe(text: str) -> str:
    return html.escape(str(text))


def common_css() -> str:
    return """
    :root{
      --bg:#f8f5ef;
      --paper:#fffdfa;
      --ink:#111;
      --muted:#5d584f;
      --line:#ddd4c6;
      --line-strong:#b7ab99;
      --accent:#326891;
      --gold:#8b6914;
      --sans:"Segoe UI","Helvetica Neue",Arial,sans-serif;
      --serif:Georgia,"Times New Roman",serif;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family:var(--serif);
      background:
        radial-gradient(circle at top left, rgba(50,104,145,.10), transparent 28%),
        linear-gradient(180deg, #fcfbf7 0%, var(--bg) 100%);
      color:var(--ink);
      line-height:1.65;
      -webkit-font-smoothing:antialiased;
      text-rendering:optimizeLegibility;
    }
    a{color:var(--accent);text-decoration:none}
    .page{max-width:1120px;margin:0 auto;padding:20px 18px 48px}
    .masthead{
      display:flex;justify-content:space-between;gap:18px;align-items:end;
      border-top:1px solid var(--line-strong);border-bottom:3px double var(--line);
      padding:10px 0 18px;margin-bottom:24px
    }
    .brand{font-size:clamp(28px,4vw,42px);font-weight:700;letter-spacing:-.03em}
    .brand-meta{max-width:40ch;font:11px/1.6 var(--sans);text-transform:uppercase;letter-spacing:.16em;color:var(--muted);text-align:right}
    .hero{
      background:rgba(255,255,255,.92);border:1px solid var(--line);border-top:4px solid var(--ink);
      padding:32px clamp(18px,4vw,40px);margin-bottom:24px;box-shadow:0 16px 38px rgba(17,17,17,.045)
    }
    .eyebrow{font:700 11px var(--sans);letter-spacing:.18em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}
    h1{font-size:clamp(38px,6vw,68px);line-height:.98;letter-spacing:-.05em;margin:0 0 14px;max-width:13ch}
    .lede{font-size:clamp(18px,2.2vw,24px);line-height:1.62;color:#474037;max-width:60rem;margin:0}
    .hero-rail{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:24px;padding-top:16px;border-top:1px solid var(--line)}
    .hero-rail div{background:rgba(255,255,255,.7);border-top:1px solid var(--line-strong);padding:12px 14px;font:11px var(--sans);text-transform:uppercase;letter-spacing:.14em;color:var(--muted)}
    .grid{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(280px,.95fr);gap:24px}
    .card{background:rgba(255,255,255,.93);border:1px solid var(--line);padding:22px 22px 24px;box-shadow:0 14px 28px rgba(17,17,17,.04)}
    .section-title{font:700 11px var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--muted);padding-bottom:10px;border-bottom:1px solid var(--line);margin:0 0 16px}
    .body-copy{font-size:clamp(22px,2.1vw,30px);line-height:1.78;max-width:30ch;margin:0}
    .body-copy::first-letter{float:left;font-size:72px;line-height:.85;padding-right:10px;padding-top:8px;font-weight:700;color:var(--gold)}
    .metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:16px 0 24px}
    .metric{background:#fff;border:1px solid var(--line);border-top:3px solid var(--gold);padding:16px;border-radius:8px}
    .metric-label{font:700 10px var(--sans);letter-spacing:.15em;text-transform:uppercase;color:#777;margin-bottom:8px}
    .metric-value{font-size:30px;font-weight:700;line-height:1.05}
    .metric-note{font:12px var(--sans);color:#888;margin-top:6px}
    .note-grid{display:grid;grid-template-columns:auto 1fr;gap:6px 12px;font:13px var(--sans);color:#444}
    .note-grid dt{font-weight:700;color:#222}
    .bullet-list{display:grid;gap:10px;padding-left:18px}
    .links{display:grid;gap:12px}
    .link-card{display:block;padding:15px 16px;background:#fff;border:1px solid var(--line);border-left:4px solid var(--accent);font:600 15px var(--sans);color:#1b1b1b;border-radius:8px}
    .chart-wrap{margin:18px 0 26px}
    .chart-caption{font:12px var(--sans);color:#666;margin-top:10px}
    .kicker{font:700 11px var(--sans);letter-spacing:.2em;text-transform:uppercase;color:var(--gold);margin:0 0 8px}
    .story-block{margin-bottom:26px}
    .footer{margin-top:28px;padding-top:14px;border-top:1px solid var(--line);font:12px var(--sans);color:#8f887e}
    .footer a{color:var(--accent)}
    @media (max-width:900px){
      .grid{grid-template-columns:1fr}
      .hero-rail{grid-template-columns:repeat(2,minmax(0,1fr))}
      .brand-meta{text-align:left}
      .masthead{display:block}
    }
    @media (max-width:640px){
      .page{padding:14px 12px 40px}
      .hero{padding:24px 18px}
      .hero-rail{grid-template-columns:1fr}
      .body-copy{font-size:22px}
    }
    """


def bar_chart(items: list[dict[str, object]], title: str, subtitle: str, value_key: str, label_key: str, color: str, percent: bool) -> str:
    width = 760
    left = 210
    right = 110
    top = 56
    row = 40
    height = top + row * len(items) + 20
    max_value = max(float(item[value_key]) for item in items) or 1.0
    parts = [
        f"<svg viewBox='0 0 {width} {height}' style='width:100%;height:auto'>",
        f"<rect x='0' y='0' width='{width}' height='{height}' fill='#fffdfa' rx='10'/>",
        f"<text x='{width/2}' y='20' text-anchor='middle' font-family='Segoe UI,Arial,sans-serif' font-size='11' fill='#6a645b' letter-spacing='0.12em'>{safe(title.upper())}</text>",
        f"<text x='{width/2}' y='38' text-anchor='middle' font-family='Georgia,serif' font-size='14' fill='#333'>{safe(subtitle)}</text>",
    ]
    chart_width = width - left - right
    for idx, item in enumerate(items):
        y = top + idx * row
        value = float(item[value_key])
        label = safe(item[label_key])
        bar_width = 0 if max_value == 0 else (value / max_value) * chart_width
        value_text = f"{value:.1f}%" if percent else f"{int(round(value)):,}"
        parts.extend(
            [
                f"<text x='{left-10}' y='{y+20}' text-anchor='end' font-family='Segoe UI,Arial,sans-serif' font-size='12' fill='#333'>{label}</text>",
                f"<rect x='{left}' y='{y+8}' width='{chart_width}' height='18' fill='#eee8df' rx='5'/>",
                f"<rect x='{left}' y='{y+8}' width='{bar_width:.1f}' height='18' fill='{color}' rx='5' opacity='0.88'/>",
                f"<text x='{left+chart_width+10}' y='{y+21}' font-family='Georgia,serif' font-size='14' fill='#1a1a1a'>{safe(value_text)}</text>",
            ]
        )
    parts.append("</svg>")
    return "".join(parts)


def metric_cards(metrics: list[tuple[str, str, str]]) -> str:
    blocks = []
    for label, value, note in metrics:
        blocks.append(
            "<div class='metric'>"
            f"<div class='metric-label'>{safe(label)}</div>"
            f"<div class='metric-value'>{safe(value)}</div>"
            f"<div class='metric-note'>{safe(note)}</div>"
            "</div>"
        )
    return "<div class='metrics'>" + "".join(blocks) + "</div>"


def render_page(title: str, eyebrow: str, lede: str, rail: list[str], main: str, sidebar: str) -> str:
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
      <div class="brand">CT.gov Hiddenness Atlas</div>
      <div class="brand-meta">{safe(DATE)} | full-registry audit | plots, figures, and E156 bundle</div>
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
      <a href="{REPO_URL}">Source on GitHub</a> | <a href="{PAGES_URL}">Project home</a> | <a href="{PAGES_URL}e156-submission/assets/dashboard.html">Dashboard</a>
    </div>
  </div>
</body>
</html>"""


def build_config(summary: dict[str, object]) -> dict[str, object]:
    assert len(BODY.split()) == 156
    assert len(SENTENCES) == 7
    return {
        "title": "CT.gov Hiddenness Atlas: What Sponsors Still Do Not Show",
        "slug": "ctgov-hiddenness-atlas",
        "author": AUTHOR,
        "date": DATE,
        "path": str(ROOT),
        "type": "methods",
        "primary_estimand": "2-year no-results rate among eligible closed interventional studies",
        "summary": "A full-registry ClinicalTrials.gov audit of non-disclosure, sparse reporting, and sponsor-specific hiddenness patterns.",
        "body": BODY,
        "sentences": SENTENCES,
        "notes": {
            "app": "CT.gov Hiddenness Atlas dashboard",
            "data": f"{fmt_int(int(summary['total_studies']))} ClinicalTrials.gov records",
            "code": REPO_URL,
            "doi": "",
            "version": VERSION,
            "date": DATE,
            "validation": "FULL REGISTRY RUN",
        },
        "affiliation": AFFILIATION,
        "email": EMAIL,
        "references": [
            "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
            "Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. BMJ. 2021;372:n71.",
            "Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.",
        ],
    }


def build_paper_md(config: dict[str, object]) -> str:
    refs = "\n".join(f"{idx}. {ref}" for idx, ref in enumerate(config["references"], start=1))
    return f"""{AUTHOR}
{AFFILIATION}
{EMAIL}

{config["title"]}

{BODY}

Outside Notes

Type: methods
Primary estimand: {config["primary_estimand"]}
App: CT.gov Hiddenness Atlas
Data: {config["notes"]["data"]}
Code: {REPO_URL}
Version: {VERSION}
Validation: FULL REGISTRY RUN

References

{refs}

AI Disclosure

{AI_DISCLOSURE}
"""


def build_protocol_md(summary: dict[str, object]) -> str:
    refs = "\n".join(
        [
            "1. ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
            "2. Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. BMJ. 2021;372:n71.",
            "3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.",
        ]
    )
    return f"""{AUTHOR}
{AFFILIATION}
{EMAIL}

Protocol: CT.gov Hiddenness Atlas

This protocol describes a full-registry audit of ClinicalTrials.gov non-disclosure and sparse reporting patterns. The source universe is the live ClinicalTrials.gov API v2 snapshot captured on {DATE}, yielding {fmt_int(int(summary["total_studies"]))} total studies, {fmt_int(int(summary["interventional_studies"]))} interventional studies, and {fmt_int(int(summary["closed_interventional_studies"]))} closed interventional studies. The primary estimand is the 2-year no-results rate among closed interventional studies with a primary completion date at least two years before the reference date. Secondary estimands include missing actual primary completion date, missing actual completion date, missing actual enrollment, missing IPD sharing statement, missing linked publication references, sparse outcome reporting, and missing stopping reasons. All records are flattened into study-level features and summarized by sponsor class, lead sponsor, and phase. The main contrast of interest is whether hiddenness concentrates in industry, heterogeneous OTHER sponsors, government categories, or NIH-linked studies once both rates and absolute stocks are examined. Outputs include a public dashboard, E156 micro-paper bundle, protocol, and grouped CSV summaries suitable for GitHub Pages distribution.

Outside Notes

Type: protocol
Primary estimand: 2-year no-results rate among eligible closed interventional studies
App: CT.gov Hiddenness Atlas
Code: {REPO_URL}
Date: {DATE}
Validation: FULL REGISTRY RUN

References

{refs}

AI Disclosure

{AI_DISCLOSURE}
"""


def main() -> None:
    SUBMISSION.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    study_df = pd.read_parquet(PROCESSED / "study_features.parquet")
    sponsor_all = {row["lead_sponsor_class"]: row for row in read_csv(PROCESSED / "sponsor_class_summary_all.csv")}
    sponsor_closed_rows = read_csv(PROCESSED / "sponsor_class_summary_closed_interventional.csv")
    sponsor_closed = {row["lead_sponsor_class"]: row for row in sponsor_closed_rows}
    lead_rows = read_csv(PROCESSED / "lead_sponsor_summary_closed_interventional.csv")
    phase_rows = read_csv(PROCESSED / "phase_summary_interventional.csv")

    total_studies = len(study_df)
    interventional = int(study_df["is_interventional"].sum())
    closed = int(study_df["is_closed"].sum())
    closed_interventional_df = study_df[study_df["is_interventional"] & study_df["is_closed"]]
    older_2y_df = closed_interventional_df[closed_interventional_df["days_since_primary_completion"].fillna(-1) >= 730]

    summary = {
        "total_studies": total_studies,
        "interventional_studies": interventional,
        "closed_studies": closed,
        "closed_interventional_studies": len(closed_interventional_df),
        "older_2y_studies": len(older_2y_df),
        "no_ipd_rate": study_df["ipd_statement_missing"].mean() * 100,
        "no_publication_rate": study_df["publication_link_missing"].mean() * 100,
        "no_description_rate": study_df["detailed_description_missing"].mean() * 100,
        "no_locations_rate": study_df["location_missing"].mean() * 100,
        "two_year_no_results_rate": older_2y_df["results_gap_2y"].mean() * 100,
    }

    config = build_config(summary)

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

    structure_items = [
        {"label": "No publication link", "value": summary["no_publication_rate"]},
        {"label": "No IPD statement", "value": summary["no_ipd_rate"]},
        {"label": "No detailed description", "value": summary["no_description_rate"]},
        {"label": "No locations", "value": summary["no_locations_rate"]},
    ]

    industry_rows = [row for row in lead_rows if row["lead_sponsor_class"] == "INDUSTRY"]
    top_industry_by_count = sorted(
        industry_rows,
        key=lambda row: as_int(row["results_gap_2y_count"]),
        reverse=True,
    )[:10]
    top_industry_by_rate = [
        row for row in industry_rows if as_int(row["eligible_results_gap_2y_count"]) >= 50
    ]
    top_industry_by_rate = sorted(
        top_industry_by_rate,
        key=lambda row: (as_float(row["results_gap_2y_rate_eligible"]), as_int(row["eligible_results_gap_2y_count"])),
        reverse=True,
    )[:10]

    phase_items = []
    for row in sorted(phase_rows, key=lambda item: as_float(item["results_gap_2y_rate_eligible"]), reverse=True):
        if row["phase_label"] == "UNSPECIFIED":
            continue
        phase_items.append({"label": row["phase_label"], "value": as_float(row["results_gap_2y_rate_eligible"])})

    landing_links = """
      <div class="links">
        <a class="link-card" href="e156-submission/index.html">E156 micro-paper</a>
        <a class="link-card" href="e156-submission/assets/dashboard.html">Main dashboard</a>
        <a class="link-card" href="e156-submission/assets/industry.html">Industry story</a>
        <a class="link-card" href="e156-submission/assets/sponsor-classes.html">Sponsor-class story</a>
        <a class="link-card" href="e156-submission/assets/phases.html">Phase story</a>
        <a class="link-card" href="e156-submission/paper.md">Paper</a>
        <a class="link-card" href="e156-submission/protocol.md">Protocol</a>
      </div>
    """
    landing_main = (
        "<section class='card'>"
        "<h2 class='section-title'>Public Project Series</h2>"
        "<p class='body-copy'>This release packages the full ClinicalTrials.gov hiddenness audit as a public E156 bundle plus a small series of narrative dashboard pages. The design follows your existing project pattern, but the visuals are more information-dense and newspaper-like.</p>"
        + metric_cards(
            [
                ("Studies", fmt_int(total_studies), "Full registry"),
                ("Closed interventional", fmt_int(len(closed_interventional_df)), "Primary universe"),
                ("2-year no-results", fmt_pct(summary["two_year_no_results_rate"]), "Eligible older studies"),
                ("Industry stock", fmt_int(as_int(sponsor_closed["INDUSTRY"]["results_gap_2y_count"])), "2-year no-results"),
            ]
        )
        + "<div class='chart-wrap'>"
        + bar_chart(sponsor_stock_items, "Hidden results stock", "Absolute 2-year no-results counts by sponsor class", "value", "label", "#c3452f", percent=False)
        + "<div class='chart-caption'>OTHER holds the largest absolute stock, while industry still contributes a large unresolved block.</div></div>"
        "</section>"
    )
    landing_sidebar = (
        "<h2 class='section-title'>Project Notes</h2>"
        "<dl class='note-grid'>"
        f"<dt>Author</dt><dd>{safe(AUTHOR)}</dd>"
        f"<dt>Date</dt><dd>{safe(DATE)}</dd>"
        f"<dt>Repo</dt><dd><a href='{REPO_URL}'>{safe(REPO_URL)}</a></dd>"
        f"<dt>Pages</dt><dd><a href='{PAGES_URL}'>{safe(PAGES_URL)}</a></dd>"
        f"<dt>Primary estimand</dt><dd>{safe(config['primary_estimand'])}</dd>"
        "</dl>"
        "<h2 class='section-title'>Series</h2>"
        "<ul class='bullet-list'>"
        "<li>Main dashboard: full universe, main figures, and headline metrics.</li>"
        "<li>Industry story: biggest industry sponsors by absolute and rate-based disclosure gaps.</li>"
        "<li>Sponsor-class story: who is worst on rate, who is biggest on stock, and who is most structurally sparse.</li>"
        "<li>Phase story: where the registry goes quiet by phase, not just by sponsor.</li>"
        "</ul>"
    )

    reader_main = (
        "<article class='card'>"
        "<h2 class='section-title'>Paper</h2>"
        f"<p class='body-copy'>{safe(BODY)}</p>"
        + metric_cards(
            [
                ("Total studies", fmt_int(total_studies), "Live registry"),
                ("Interventional", fmt_int(interventional), "Study type"),
                ("OTHER stock", fmt_int(as_int(sponsor_closed['OTHER']['results_gap_2y_count'])), "2-year no-results"),
                ("Industry stock", fmt_int(as_int(sponsor_closed['INDUSTRY']['results_gap_2y_count'])), "2-year no-results"),
            ]
        )
        + "<div class='story-block'><div class='kicker'>Sentence Structure</div>"
        + "".join(f"<p><strong>{safe(item['role'])}:</strong> {safe(item['text'])}</p>" for item in SENTENCES)
        + "</div></article>"
    )
    reader_sidebar = (
        "<h2 class='section-title'>Outside Notes</h2>"
        "<dl class='note-grid'>"
        f"<dt>Type</dt><dd>{safe(config['type'])}</dd>"
        f"<dt>App</dt><dd>CT.gov Hiddenness Atlas dashboard</dd>"
        f"<dt>Data</dt><dd>{safe(config['notes']['data'])}</dd>"
        f"<dt>Code</dt><dd><a href='{REPO_URL}'>{safe(REPO_URL)}</a></dd>"
        f"<dt>Version</dt><dd>{safe(VERSION)}</dd>"
        "</dl>"
        "<h2 class='section-title'>Links</h2>"
        "<div class='links'>"
        "<a class='link-card' href='assets/dashboard.html'>Main dashboard</a>"
        "<a class='link-card' href='assets/industry.html'>Industry story</a>"
        "<a class='link-card' href='paper.md'>Paper markdown</a>"
        "<a class='link-card' href='protocol.md'>Protocol markdown</a>"
        "</div>"
    )

    dashboard_main = (
        "<article class='card'>"
        "<h2 class='section-title'>Main Dashboard</h2>"
        + metric_cards(
            [
                ("Registry size", fmt_int(total_studies), "All studies"),
                ("Closed interventional", fmt_int(len(closed_interventional_df)), "Primary comparison set"),
                ("Eligible older studies", fmt_int(len(older_2y_df)), "2-year denominator"),
                ("2-year no-results", fmt_pct(summary["two_year_no_results_rate"]), "Among eligible older studies"),
            ]
        )
        + "<div class='chart-wrap'>"
        + bar_chart(sponsor_rate_items, "No-results rate", "2-year no-results rate among eligible older closed interventional studies", "value", "label", "#326891", percent=True)
        + "<div class='chart-caption'>OTHER_GOV is worst on rate, OTHER is worst on total stock, and industry still carries a large unresolved block.</div></div>"
        + "<div class='chart-wrap'>"
        + bar_chart(sponsor_stock_items, "Hidden results stock", "Absolute 2-year no-results counts by sponsor class", "value", "label", "#c3452f", percent=False)
        + "<div class='chart-caption'>Volume matters. OTHER dominates absolute stock, but industry still contributes more than forty-four thousand long-past missing-results studies.</div></div>"
        + "<div class='chart-wrap'>"
        + bar_chart(structure_items, "Structural sparsity", "Global missingness rates across the full registry", "value", "label", "#8b6914", percent=True)
        + "<div class='chart-caption'>What disappears is not just results. Publication links, IPD statements, detailed descriptions, and even locations are often absent.</div></div>"
        "</article>"
    )
    dashboard_sidebar = (
        "<h2 class='section-title'>Read This First</h2>"
        "<ul class='bullet-list'>"
        "<li>Rates identify systematic opacity.</li>"
        "<li>Counts identify where the largest unseen stock sits.</li>"
        "<li>Industry is not the only problem category.</li>"
        "<li>NIH has the highest average hiddenness score among named sponsor classes.</li>"
        "</ul>"
        "<h2 class='section-title'>Jump</h2>"
        "<div class='links'>"
        "<a class='link-card' href='industry.html'>Industry story</a>"
        "<a class='link-card' href='sponsor-classes.html'>Sponsor-class story</a>"
        "<a class='link-card' href='phases.html'>Phase story</a>"
        "</div>"
    )

    industry_count_items = [{"label": row["lead_sponsor_name"], "value": as_int(row["results_gap_2y_count"])} for row in top_industry_by_count]
    industry_rate_items = [{"label": row["lead_sponsor_name"], "value": as_float(row["results_gap_2y_rate_eligible"])} for row in top_industry_by_rate]
    industry_main = (
        "<article class='card'><h2 class='section-title'>Industry Story</h2>"
        + metric_cards(
            [
                ("Industry studies", fmt_int(as_int(sponsor_all["INDUSTRY"]["studies"])), "All sponsor-class records"),
                ("Closed interventional", fmt_int(as_int(sponsor_closed["INDUSTRY"]["studies"])), "Industry only"),
                ("2-year stock", fmt_int(as_int(sponsor_closed["INDUSTRY"]["results_gap_2y_count"])), "Missing posted results"),
                ("Eligible rate", fmt_pct(as_float(sponsor_closed["INDUSTRY"]["results_gap_2y_rate_eligible"])), "Older closed studies"),
            ]
        )
        + "<div class='chart-wrap'>"
        + bar_chart(industry_count_items, "Industry by stock", "Largest industry sponsors by absolute 2-year no-results count", "value", "label", "#c3452f", percent=False)
        + "<div class='chart-caption'>The biggest unresolved industry blocks sit with large multinational portfolios such as GlaxoSmithKline, AstraZeneca, Boehringer Ingelheim, Sanofi, and Pfizer.</div></div>"
        + "<div class='chart-wrap'>"
        + bar_chart(industry_rate_items, "Industry by rate", "Highest industry 2-year no-results rates among sponsors with at least 50 eligible older studies", "value", "label", "#326891", percent=True)
        + "<div class='chart-caption'>Rate-based leaders are not always the biggest by count, which is why this project reports both views.</div></div>"
        "</article>"
    )
    industry_sidebar = (
        "<h2 class='section-title'>Industry Readout</h2>"
        "<ul class='bullet-list'>"
        f"<li>Industry still carries {fmt_int(as_int(sponsor_closed['INDUSTRY']['results_gap_2y_count']))} two-year no-results studies.</li>"
        f"<li>{fmt_pct(as_float(sponsor_closed['INDUSTRY']['detailed_description_missing_rate']))} of closed interventional industry studies have no detailed description.</li>"
        f"<li>{fmt_pct(as_float(sponsor_closed['INDUSTRY']['ipd_statement_missing_rate']))} have no IPD sharing statement.</li>"
        f"<li>{fmt_pct(as_float(sponsor_closed['INDUSTRY']['publication_link_missing_rate']))} have no linked publication reference.</li>"
        "</ul>"
    )

    sponsor_class_main = (
        "<article class='card'><h2 class='section-title'>Sponsor-Class Story</h2>"
        + metric_cards(
            [
                ("OTHER rate", fmt_pct(as_float(sponsor_closed["OTHER"]["results_gap_2y_rate_eligible"])), "Eligible older closed interventional"),
                ("OTHER stock", fmt_int(as_int(sponsor_closed["OTHER"]["results_gap_2y_count"])), "Largest absolute block"),
                ("OTHER_GOV rate", fmt_pct(as_float(sponsor_closed["OTHER_GOV"]["results_gap_2y_rate_eligible"])), "Worst rate"),
                ("NIH hiddenness", f"{as_float(sponsor_all['NIH']['mean_hiddenness_score']):.2f}", "Highest average named-class score"),
            ]
        )
        + "<div class='chart-wrap'>"
        + bar_chart(sponsor_rate_items, "Sponsor-class rate", "Eligible 2-year no-results rate by sponsor class", "value", "label", "#326891", percent=True)
        + "<div class='chart-caption'>OTHER_GOV is worst on rate, but OTHER and INDUSTRY dominate the raw stock of unresolved disclosure gaps.</div></div>"
        + "<div class='chart-wrap'>"
        + bar_chart(sponsor_stock_items, "Sponsor-class stock", "Absolute 2-year no-results counts by sponsor class", "value", "label", "#c3452f", percent=False)
        + "<div class='chart-caption'>The OTHER bucket is heterogeneous, but that is precisely why it matters: it contains the largest invisible stock.</div></div>"
        "</article>"
    )
    sponsor_class_sidebar = (
        "<h2 class='section-title'>Interpretation</h2>"
        "<ul class='bullet-list'>"
        "<li>Rate and stock do not point to the same class.</li>"
        "<li>OTHER_GOV is worst on rate.</li>"
        "<li>OTHER is worst on stock.</li>"
        "<li>INDUSTRY remains large enough that it cannot be treated as a secondary issue.</li>"
        "<li>NIH is comparatively sparse on several structural fields, which pushes its average hiddenness score up.</li>"
        "</ul>"
    )

    phase_main = (
        "<article class='card'><h2 class='section-title'>Phase Story</h2>"
        + metric_cards(
            [
                ("Phase I rate", fmt_pct(as_float(next(row["results_gap_2y_rate_eligible"] for row in phase_rows if row["phase_label"] == "PHASE1"))), "Highest phase-specific rate"),
                ("NA stock", fmt_int(as_int(next(row["results_gap_2y_count"] for row in phase_rows if row["phase_label"] == "NA"))), "Largest absolute count"),
                ("Phase III rate", fmt_pct(as_float(next(row["results_gap_2y_rate_eligible"] for row in phase_rows if row["phase_label"] == "PHASE3"))), "Late-stage benchmark"),
                ("Phase IV rate", fmt_pct(as_float(next(row["results_gap_2y_rate_eligible"] for row in phase_rows if row["phase_label"] == "PHASE4"))), "Post-marketing benchmark"),
            ]
        )
        + "<div class='chart-wrap'>"
        + bar_chart(phase_items[:8], "Phase rate", "Eligible 2-year no-results rate by phase label", "value", "label", "#8b6914", percent=True)
        + "<div class='chart-caption'>Phase I is the quietest major phase on a rate basis, while the NA bucket dominates by absolute count because of its scale.</div></div>"
        "</article>"
    )
    phase_sidebar = (
        "<h2 class='section-title'>Phase Notes</h2>"
        "<ul class='bullet-list'>"
        "<li>Phase I reaches 76.7 percent on the eligible 2-year no-results rate.</li>"
        "<li>The NA bucket still contains the largest absolute count of long-past missing results.</li>"
        "<li>Late-stage phases are better than phase I but remain far from transparent.</li>"
        "</ul>"
    )

    (ROOT / "index.html").write_text(render_page("A public series on what the CT.gov registry still does not show", "Project Series", "A full-registry audit turned into an E156 bundle plus three public NYT-style story pages: sponsor classes, industry, and phases.", [f"{fmt_int(total_studies)} studies", f"{fmt_int(len(closed_interventional_df))} closed interventional", f"{fmt_pct(summary['two_year_no_results_rate'])} 2-year no-results", "GitHub Pages ready"], landing_main, landing_sidebar + landing_links), encoding="utf-8")
    (SUBMISSION / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (SUBMISSION / "paper.md").write_text(build_paper_md(config), encoding="utf-8")
    (SUBMISSION / "protocol.md").write_text(build_protocol_md(summary), encoding="utf-8")
    (SUBMISSION / "index.html").write_text(render_page("CT.gov Hiddenness Atlas", "E156 Micro-Paper", "A 156-word account of where sponsor-specific opacity, missing results, and structural sparsity concentrate across the live ClinicalTrials.gov registry.", [f"{fmt_int(total_studies)} total studies", f"{fmt_int(len(older_2y_df))} eligible older studies", f"{fmt_pct(summary['two_year_no_results_rate'])} 2-year no-results", "Paper + dashboard + protocol"], reader_main, reader_sidebar), encoding="utf-8")
    (ASSETS / "dashboard.html").write_text(render_page("What the full CT.gov registry still does not show", "Main Dashboard", "This page combines rate, stock, and structural sparsity views so the disclosure burden is not mistaken for a single-sector problem.", ["Main figures", "Sponsor classes", "Absolute stock", "Structural gaps"], dashboard_main, dashboard_sidebar), encoding="utf-8")
    (ASSETS / "industry.html").write_text(render_page("Industry is not the only hiddenness problem, but it is still a large one", "Industry Story", "Industry contributes tens of thousands of long-past missing-results records and remains sparse on several explanatory fields.", ["Largest sponsors", "Absolute counts", "Rate leaders", "Field sparsity"], industry_main, industry_sidebar), encoding="utf-8")
    (ASSETS / "sponsor-classes.html").write_text(render_page("Rates and stock point to different sponsor classes", "Sponsor-Class Story", "OTHER_GOV is worst on rate, OTHER is worst on absolute stock, and industry remains too large to ignore.", ["Rate vs stock", "OTHER_GOV", "OTHER", "INDUSTRY"], sponsor_class_main, sponsor_class_sidebar), encoding="utf-8")
    (ASSETS / "phases.html").write_text(render_page("Phase matters: early studies go quiet most often", "Phase Story", "The phase gradient shows that non-disclosure is not just sponsor-specific. Phase I is worst on rate, while the NA bucket dominates by scale.", ["Phase I rate", "NA stock", "Late-stage benchmark", "Eligible 2-year gap"], phase_main, phase_sidebar), encoding="utf-8")
    print("Public pages built under e156-submission and root index.html")


if __name__ == "__main__":
    main()
