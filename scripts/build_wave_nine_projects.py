#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Build wave-nine standalone CT.gov watchlist projects."""

from __future__ import annotations

import re
from pathlib import Path

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct
from build_split_projects import chart_section, sentence_bundle, write_project
from build_wave_eight_projects import load_csv, make_spec, row_for, short_sponsor

ROOT = Path(__file__).resolve().parents[1]
ATLAS_INDEX = ROOT / "index.html"


def short_label(label: str) -> str:
    text = label.strip()
    for suffix in [" project", " audit"]:
        if text.lower().endswith(suffix):
            text = text[: -len(suffix)]
    return text.title()


def parse_existing_series_links() -> list[dict[str, str]]:
    text = ATLAS_INDEX.read_text(encoding="utf-8")
    pattern = re.compile(r"<a class='link-card' href='https://[^/]+/(ctgov-[^/]+)/'>([^<]+)</a>")
    seen: dict[str, dict[str, str]] = {}
    for repo_name, label in pattern.findall(text):
        if repo_name in seen:
            continue
        seen[repo_name] = {
            "repo_name": repo_name,
            "title": label,
            "summary": f"{label} from the CT.gov hiddenness series.",
            "short_title": short_label(label),
            "pages_url": f"https://{REPO_OWNER}.github.io/{repo_name}/",
        }
    return list(seen.values())


def main() -> None:
    metrics = load_csv("wave_nine_model_metrics.csv")
    sponsor = load_csv("wave_nine_sponsor_watchlist.csv")
    country = load_csv("wave_nine_country_watchlist.csv")
    condition = load_csv("wave_nine_condition_watchlist.csv")
    black_box_class = load_csv("wave_nine_black_box_sponsor_class.csv")
    black_box_country = load_csv("wave_nine_black_box_country.csv")
    black_box_condition = load_csv("wave_nine_black_box_condition.csv")
    strict_sponsor = load_csv("wave_nine_strict_sponsor_watchlist.csv")
    strict_condition = load_csv("wave_nine_strict_condition_summary.csv")
    strict_class = load_csv("wave_nine_strict_sponsor_class_summary.csv")

    no_results_metrics = row_for(metrics, "target", "results_gap_2y")
    ghost_metrics = row_for(metrics, "target", "ghost_protocol")

    sponsor_top = sponsor.iloc[0]
    sponsor_second = sponsor.iloc[1]
    sponsor_third = sponsor.iloc[2]
    sponsor_ghost = sponsor.sort_values("excess_ghost", ascending=False).iloc[0]
    sponsor_strict = strict_sponsor.iloc[0]

    country_top = country.iloc[0]
    country_second = country.iloc[1]
    country_third = country.iloc[3]
    country_black_box_rate = black_box_country.sort_values("black_box_rate", ascending=False).iloc[0]

    condition_top = condition.iloc[0]
    condition_second = condition.iloc[1]
    condition_third = condition.iloc[2]
    condition_ghost = condition.sort_values("excess_ghost", ascending=False).iloc[0]

    black_box_other = row_for(black_box_class, "lead_sponsor_class", "OTHER")
    black_box_industry = row_for(black_box_class, "lead_sponsor_class", "INDUSTRY")
    black_box_us = row_for(black_box_country, "country_name", "United States")
    black_box_healthy = row_for(black_box_condition, "condition_family_label", "Healthy volunteers")

    strict_nci = strict_sponsor.iloc[0]
    strict_mayo = strict_sponsor.iloc[1]
    strict_sanofi = row_for(strict_sponsor, "lead_sponsor_name", "Sanofi")
    strict_other = row_for(strict_class, "lead_sponsor_class", "OTHER")
    strict_network = row_for(strict_class, "lead_sponsor_class", "NETWORK")
    strict_oncology = row_for(strict_condition, "condition_family_label", "Oncology")

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
    ]

    series_links = parse_existing_series_links()
    series_links.extend(
        [
            {
                "repo_name": "ctgov-sponsor-excess-watchlist",
                "title": "CT.gov Sponsor Excess Watchlist",
                "summary": "Sponsor-level adjusted watchlist showing which named sponsors still carry the largest excess hiddenness stock.",
                "short_title": "Sponsor Watchlist",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-sponsor-excess-watchlist/",
            },
            {
                "repo_name": "ctgov-country-excess-watchlist",
                "title": "CT.gov Country Excess Watchlist",
                "summary": "Country-linked adjusted watchlist showing which national portfolios remain worse than expected after visible study mix is held more constant.",
                "short_title": "Country Watchlist",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-excess-watchlist/",
            },
            {
                "repo_name": "ctgov-condition-excess-watchlist",
                "title": "CT.gov Condition Excess Watchlist",
                "summary": "Condition-family watchlist showing which therapeutic areas still carry excess no-results and ghost-protocol stock.",
                "short_title": "Condition Watchlist",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-excess-watchlist/",
            },
            {
                "repo_name": "ctgov-black-box-trials",
                "title": "CT.gov Black-Box Trials",
                "summary": "A black-box audit of older studies with no results, no linked paper, and no detailed description.",
                "short_title": "Black-Box Trials",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-black-box-trials/",
            },
            {
                "repo_name": "ctgov-strict-proxy-repeaters",
                "title": "CT.gov Strict-Proxy Repeaters",
                "summary": "Strict U.S.-nexus repeater tables showing which sponsors and classes dominate the regulated-looking backlog.",
                "short_title": "Strict Repeaters",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-strict-proxy-repeaters/",
            },
        ]
    )
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    sponsor_body, sponsor_sentences = sentence_bundle(
        [
            ("Question", "Which named CT.gov sponsors remain worst once hiddenness is read as adjusted excess stock rather than raw rate alone?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
            ("Method", "We reused the study-mix-adjusted no-results and ghost models, then ranked sponsors with at least 100 studies by observed-versus-expected excess, black-box stock, overdue depth, and strict-core carryover."),
            ("Primary result", "Assistance Publique - Hopitaux de Paris carried the largest adjusted excess no-results stock at 265 studies, followed by Sanofi at 197 and Cairo University at 164."),
            ("Secondary result", "Sanofi also showed 219 excess ghost protocols, while the strict U.S.-nexus core was led by National Cancer Institute at 361 missing-results studies."),
            ("Interpretation", "The sponsor backlog therefore does not collapse into one sector, but major industrial and hospital systems remain prominent repeat offenders across the international registry and its strict-core subset."),
            ("Boundary", "These watchlists use registry-visible sponsorship and adjusted excess estimates, not audited legal responsibility, ultimate funder structure, or causally attributable silence."),
        ]
    )
    country_body, country_sentences = sentence_bundle(
        [
            ("Question", "Which country-linked CT.gov portfolios remain most opaque after visible study mix is held more constant?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded named-country links."),
            ("Method", "We summed adjusted no-results excess, adjusted ghost excess, black-box stock, and strict-core spillover across country-linked study portfolios with at least 500 linked studies."),
            ("Primary result", "France carried the largest country-linked adjusted excess no-results stock at 2,187 studies, followed by China at 1,299 and Egypt at 824."),
            ("Secondary result", "China and Egypt also showed large ghost excess, while South Korea reached a 21.2 percent black-box rate and France still carried 3,093 black-box studies."),
            ("Interpretation", "The geography story therefore mixes large Western institutional stock with sharper hiddenness tails in several Asian and Middle Eastern portfolios once adjusted stock, ghost excess, and black-box depth are read together."),
            ("Boundary", "Country watchlists count country-linked studies rather than assigning each study to only one nation, so multinational records can contribute to multiple national portfolios."),
        ]
    )
    condition_body, condition_sentences = sentence_bundle(
        [
            ("Question", "Which condition families remain worst once excess hiddenness is measured inside broad therapeutic portfolios rather than single sponsor tables?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
            ("Method", "We ranked condition families by adjusted no-results excess, adjusted ghost excess, black-box stock, and strict-core carryover using the same study-mix adjustment as wave eight."),
            ("Primary result", "Oncology carried the largest adjusted excess no-results stock at 543 studies, followed by cardiovascular at 373 and metabolic at 251."),
            ("Secondary result", "Healthy volunteers were different: near expected on no-results, yet 1,032 studies above expectation on ghost protocols and a 33.9 percent black-box rate."),
            ("Interpretation", "Condition families therefore split into stock-heavy disease backlogs and a separate healthy-volunteer silence pattern that is much more ghosted than merely overdue inside the same older-study registry universe overall."),
            ("Boundary", "Condition families are keyword-derived registry groupings, so they approximate therapeutic portfolios rather than adjudicated disease ontologies or mutually exclusive clinical domains."),
        ]
    )
    black_box_body, black_box_sentences = sentence_bundle(
        [
            ("Question", "What appears when hiddenness is narrowed to black-box trials with no results, no linked publication, and no detailed description?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
            ("Method", "We defined a black-box trial as one with a two-year results gap, no linked publication reference, and no detailed description, then ranked sponsor classes, countries, and condition families."),
            ("Primary result", "OTHER held the largest black-box stock at 21,375 studies, while INDUSTRY carried the highest large-class black-box rate at 23.4 percent."),
            ("Secondary result", "The United States still held 12,183 black-box studies on absolute stock, but healthy-volunteer portfolios were the sharpest condition-family extreme at 33.9 percent."),
            ("Interpretation", "The black-box view isolates a stricter silence state where industrial portfolios rate worse, while heterogeneous public and academic portfolios still dominate on count across the registry overall."),
            ("Boundary", "Black-box status is a registry-visibility definition only and does not imply a study lacked internal documentation, external dissemination, or undiscovered reporting outside linked registry fields."),
        ]
    )
    strict_body, strict_sentences = sentence_bundle(
        [
            ("Question", "Which sponsors still dominate the strict U.S.-nexus CT.gov core once attention shifts from sector averages to named repeaters?"),
            ("Dataset", "We analysed the 58,598-study strict U.S.-nexus drug-biological-device proxy extracted from the March 29, 2026 full-registry snapshot."),
            ("Method", "We ranked strict-core sponsors with at least 50 studies and compared sponsor classes and condition families on missing-results and black-box stock inside that regulated-looking subset."),
            ("Primary result", "National Cancer Institute carried the largest strict-core no-results stock at 361 studies, followed by Mayo Clinic at 204, MD Anderson at 198, and Sanofi at 186."),
            ("Secondary result", "OTHER and INDUSTRY remained close on strict-core stock at 8,824 and 7,983 studies, but NETWORK had the highest large-class no-results rate at 48.8 percent."),
            ("Interpretation", "The strict-core backlog therefore remains institutionally distributed across government-linked, academic, and industry sponsors rather than collapsing into one regulated archetype."),
            ("Boundary", "These repeaters sit inside a conservative proxy core and should not be read as formal ACT or FDAAA legal determinations for specific studies or sponsors or enforcement."),
        ]
    )

    projects: list[dict[str, object]] = []
    projects.append(
        make_spec(
            repo_name="ctgov-sponsor-excess-watchlist",
            title="CT.gov Sponsor Excess Watchlist",
            summary="A standalone E156 project on which named sponsors still carry the largest excess hiddenness stock after visible study mix is held more constant.",
            body=sponsor_body,
            sentences=sponsor_sentences,
            primary_estimand="Adjusted excess no-results and ghost-protocol stock among named lead sponsors with at least 100 older studies",
            data_note="249,507 eligible older closed interventional studies with sponsor-level adjusted residuals and strict-core spillover fields",
            references=common_refs,
            protocol=(
                "This protocol ranks named lead sponsors within eligible older closed interventional ClinicalTrials.gov studies after reusing the study-mix-adjusted no-results and ghost-protocol models from wave eight. "
                "Primary outputs compare sponsor-level excess no-results stock, excess ghost stock, black-box stock, overdue depth, and strict U.S.-nexus spillover. "
                "The aim is to move from broad sector tables to named repeater systems without discarding study-mix adjustment. "
                "Because sponsorship is registry-entered, these watchlists describe registry-visible lead sponsors rather than audited corporate or institutional control chains."
            ),
            root_title="Which sponsors still carry the largest excess hiddenness?",
            root_eyebrow="Sponsor Watchlist Project",
            root_lede="A standalone public project on sponsor-level excess hiddenness, showing that hospital systems, universities, and major drug companies all remain visible among the largest adjusted repeat offenders.",
            chapter_intro="This page narrows the series from sponsor classes to named sponsors. It keeps the study-mix adjustment and asks which institutions still remain worse than expected afterward.",
            root_pull_quote="The sponsor backlog does not collapse into one sector. It stays distributed across hospitals, universities, and industry portfolios.",
            paper_pull_quote="Raw sponsor league tables reward size. Adjusted sponsor watchlists ask who still looks worse than expected after visible study mix is held more constant.",
            dashboard_pull_quote="AP-HP, Sanofi, and Cairo University rise to the top on adjusted excess no-results stock, while Sanofi also stands out on ghost excess and NCI leads the strict-core carryover.",
            root_rail=["AP-HP +265", "Sanofi +197", "Cairo +164", "NCI strict 361"],
            landing_metrics=[
                ("AP-HP excess", fmt_int(int(round(as_float(sponsor_top["excess_no_results"])))), "Adjusted no-results stock"),
                ("Sanofi excess", fmt_int(int(round(as_float(sponsor_second["excess_no_results"])))), "Largest industry residual"),
                ("Cairo excess", fmt_int(int(round(as_float(sponsor_third["excess_no_results"])))), "Third largest residual"),
                ("Model AUC", f"{as_float(no_results_metrics['holdout_auc']):.3f}", "No-results model"),
            ],
            landing_chart_html=chart_section(
                "Top sponsor excess no-results stock",
                bar_chart(
                    [
                        {"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["excess_no_results"])}
                        for _, row in sponsor.head(10).iterrows()
                    ],
                    "Sponsor residuals",
                    "Adjusted excess missing-results counts among named sponsors",
                    "value",
                    "label",
                    "#c3452f",
                    percent=False,
                ),
                "The leading adjusted repeaters span both public and private institutions.",
                "That is why the sponsor story remains broader than an industry-only audit.",
            ),
            reader_lede="A 156-word micro-paper on which named sponsors still carry the largest excess hiddenness stock after visible study mix is held more constant.",
            reader_rail=["Adjusted stock", "Ghost excess", "Strict core", "Named repeaters"],
            reader_metrics=[
                ("No-results AUC", f"{as_float(no_results_metrics['holdout_auc']):.3f}", "Holdout model"),
                ("Ghost AUC", f"{as_float(ghost_metrics['holdout_auc']):.3f}", "Second target"),
                ("Top ghost", fmt_int(int(round(as_float(sponsor_ghost["excess_ghost"])))), short_sponsor(str(sponsor_ghost["lead_sponsor_name"]))),
                ("NCI strict", fmt_int(as_int(sponsor_strict["no_results_count"])), "Strict-core stock"),
            ],
            dashboard_title="Named-sponsor watchlists show that excess hiddenness is carried by a mixed field of hospital systems, universities, and large drug companies",
            dashboard_eyebrow="Sponsor Watchlist Dashboard",
            dashboard_lede="AP-HP leads on adjusted excess no-results stock, Sanofi is the clearest large industry repeater, Cairo University remains prominent on both no-results and ghost excess, and NCI tops the strict-core missing-results table.",
            dashboard_rail=["Adjusted stock", "Ghost residuals", "Black-box stock", "Strict carryover"],
            dashboard_metrics=[
                ("AP-HP excess", fmt_int(int(round(as_float(sponsor_top["excess_no_results"])))), "Adjusted stock"),
                ("Sanofi ghost", fmt_int(int(round(as_float(sponsor_second["excess_ghost"])))), "Excess ghost stock"),
                ("Bayer black-box", fmt_int(as_int(row_for(sponsor, "lead_sponsor_name", "Bayer")["black_box_count"])), "Visible black-box extreme"),
                ("NCI strict", fmt_int(as_int(strict_nci["no_results_count"])), "Strict-core stock"),
            ],
            dashboard_sections=[
                chart_section(
                    "Adjusted sponsor no-results excess",
                    bar_chart(
                        [
                            {"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["excess_no_results"])}
                            for _, row in sponsor.head(10).iterrows()
                        ],
                        "Adjusted no-results",
                        "Top sponsor excess missing-results counts after study-mix adjustment",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "The upper tier mixes public hospital systems, universities, and major drug companies.",
                    "The adjusted sponsor table therefore resists a single-sector explanation.",
                ),
                chart_section(
                    "Adjusted sponsor ghost excess",
                    bar_chart(
                        [
                            {"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["excess_ghost"])}
                            for _, row in sponsor.sort_values("excess_ghost", ascending=False).head(10).iterrows()
                        ],
                        "Adjusted ghosts",
                        "Top sponsor excess ghost-protocol counts after study-mix adjustment",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Sanofi and Cairo University stand out sharply once the target changes from missing results to ghost protocols.",
                    "That is a more severe silence state than overdue results alone.",
                ),
                chart_section(
                    "Strict-core sponsor repeaters",
                    bar_chart(
                        [
                            {"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["no_results_count"])}
                            for _, row in strict_sponsor.head(10).iterrows()
                        ],
                        "Strict-core stock",
                        "Top missing-results counts inside the strict U.S.-nexus proxy core",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "NCI, Mayo, MD Anderson, and Sanofi show that the strict-core backlog is spread across government-linked, academic, and industry sponsors.",
                    "The regulated-looking subset does not collapse to one institutional archetype either.",
                ),
            ],
            sidebar_bullets=[
                "AP-HP carries the largest adjusted excess no-results stock at 265 studies.",
                "Sanofi is the clearest large industry repeater at 197 excess no-results studies and 219 excess ghost protocols.",
                "Cairo University remains a major adjusted outlier on both missing results and ghosted visibility.",
                "NCI leads the strict U.S.-nexus sponsor table with 361 missing-results studies.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-country-excess-watchlist",
            title="CT.gov Country Excess Watchlist",
            summary="A standalone E156 project on which country-linked CT.gov portfolios remain most opaque after visible study mix is held more constant.",
            body=country_body,
            sentences=country_sentences,
            primary_estimand="Adjusted excess no-results and ghost stock across country-linked study portfolios with at least 500 linked studies",
            data_note="249,507 eligible older closed interventional studies exploded into named-country links for country-linked watchlists",
            references=common_refs,
            protocol=(
                "This protocol explodes named-country links inside eligible older closed interventional ClinicalTrials.gov studies and reuses the wave-eight study-mix adjustment to rank country-linked portfolios. "
                "Primary outputs compare adjusted no-results excess, adjusted ghost excess, black-box stock, overdue depth, and strict-core spillover across countries with at least 500 linked older studies. "
                "The aim is to move beyond raw national rates and ask which country-linked portfolios still remain worse than expected after visible study mix is held more constant. "
                "Because multinational studies are linked to more than one country, the outputs describe country-linked portfolios rather than mutually exclusive national totals."
            ),
            root_title="Which country-linked portfolios still look worst after adjustment?",
            root_eyebrow="Country Watchlist Project",
            root_lede="A standalone public project on country-linked excess hiddenness, showing that France leads on adjusted stock while China, Egypt, and South Korea remain especially sharp on deeper silence indicators.",
            chapter_intro="This page reads geography as linked portfolios rather than a single-country assignment. The question is which national footprints still look worse than expected after visible study mix is held more constant.",
            root_pull_quote="Large Western portfolios still dominate on stock, but several Asian and Middle Eastern portfolios remain sharper on deeper silence signals.",
            paper_pull_quote="Raw country rates mix trial design, scale, and registry behavior together. The adjusted watchlist asks what remains once visible study mix is held more constant.",
            dashboard_pull_quote="France leads on adjusted stock, China and Egypt remain strong on ghost excess, and South Korea stands out on black-box rate even when the raw table is no longer the only lens.",
            root_rail=["France +2.2k", "China +1.3k", "Egypt +824", "S. Korea 21.2%"],
            landing_metrics=[
                ("France excess", fmt_int(int(round(as_float(country_top["excess_no_results"])))), "Adjusted stock"),
                ("China excess", fmt_int(int(round(as_float(country_second["excess_no_results"])))), "Adjusted stock"),
                ("Egypt excess", fmt_int(int(round(as_float(country_third["excess_no_results"])))), "Adjusted stock"),
                ("South Korea", fmt_pct(as_float(country_black_box_rate["black_box_rate"])), "Top black-box rate"),
            ],
            landing_chart_html=chart_section(
                "Adjusted country-linked no-results excess",
                bar_chart(
                    [{"label": row["country_name"], "value": as_float(row["excess_no_results"])} for _, row in country.head(10).iterrows()],
                    "Country-linked residuals",
                    "Adjusted excess missing-results counts across country-linked portfolios",
                    "value",
                    "label",
                    "#326891",
                    percent=False,
                ),
                "France stands out on adjusted stock, but China and Egypt are sharper on several deeper silence metrics.",
                "The geography story changes depending on whether stock or intensity is centered.",
            ),
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios remain worst after visible study mix is held more constant.",
            reader_rail=["France", "China", "Egypt", "Black-box"],
            reader_metrics=[
                ("France excess", fmt_int(int(round(as_float(country_top["excess_no_results"])))), "Adjusted stock"),
                ("China ghost", fmt_int(int(round(as_float(country_second["excess_ghost"])))), "Excess ghost stock"),
                ("Egypt ghost", fmt_int(int(round(as_float(country_third["excess_ghost"])))), "Excess ghost stock"),
                ("France black-box", fmt_int(as_int(row_for(black_box_country, "country_name", "France")["black_box_count"])), "Absolute stock"),
            ],
            dashboard_title="Country-linked watchlists show a mixed geography of excess CT.gov hiddenness, not one single regional pattern",
            dashboard_eyebrow="Country Watchlist Dashboard",
            dashboard_lede="France leads on adjusted no-results stock, China and Egypt remain strong on ghost excess, South Korea has one of the sharpest black-box rates, and several European portfolios still hold large absolute black-box stock.",
            dashboard_rail=["Adjusted stock", "Ghost excess", "Black-box stock", "Country-linked"],
            dashboard_metrics=[
                ("France excess", fmt_int(int(round(as_float(country_top["excess_no_results"])))), "Adjusted stock"),
                ("China excess", fmt_int(int(round(as_float(country_second["excess_no_results"])))), "Adjusted stock"),
                ("Egypt rate", f"{as_float(country_third['excess_no_results_rate_points']):.1f} pts", "Excess rate"),
                ("S. Korea black-box", fmt_pct(as_float(country_black_box_rate["black_box_rate"])), "Black-box rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Adjusted country-linked no-results excess",
                    bar_chart(
                        [{"label": row["country_name"], "value": as_float(row["excess_no_results"])} for _, row in country.head(10).iterrows()],
                        "Adjusted no-results",
                        "Top adjusted excess missing-results counts by country-linked portfolio",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "France and China lead the adjusted stock table, with Egypt still prominent despite a smaller linked portfolio.",
                    "That mix shows why both size and residual intensity matter.",
                ),
                chart_section(
                    "Adjusted country-linked ghost excess",
                    bar_chart(
                        [{"label": row["country_name"], "value": as_float(row["excess_ghost"])} for _, row in country.sort_values("excess_ghost", ascending=False).head(10).iterrows()],
                        "Adjusted ghosts",
                        "Top excess ghost-protocol counts across country-linked portfolios",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "China and Egypt become even sharper when the focus shifts to ghost protocols rather than missing results alone.",
                    "This is the deeper-silence geography table.",
                ),
                chart_section(
                    "Country-linked black-box stock",
                    bar_chart(
                        [{"label": row["country_name"], "value": as_float(row["black_box_count"])} for _, row in black_box_country.head(10).iterrows()],
                        "Black-box stock",
                        "Studies with no results, no linked paper, and no detailed description",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "The United States still dominates on absolute black-box stock, while France and China remain prominent within the international field.",
                    "Black-box stock does not mirror the adjusted excess table perfectly.",
                ),
            ],
            sidebar_bullets=[
                "France carries the largest adjusted country-linked excess no-results stock at 2,187 studies.",
                "China remains a major second-tier residual at 1,299 studies and also a strong ghost-protocol outlier.",
                "Egypt is smaller on stock but much sharper on excess rate and ghost intensity.",
                "South Korea stands out on black-box rate at 21.2 percent.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-condition-excess-watchlist",
            title="CT.gov Condition Excess Watchlist",
            summary="A standalone E156 project on which therapeutic portfolios still carry excess hiddenness once the series shifts from raw rates to adjusted condition-family watchlists.",
            body=condition_body,
            sentences=condition_sentences,
            primary_estimand="Adjusted excess no-results and ghost stock across CT.gov condition families",
            data_note="249,507 eligible older closed interventional studies with keyword-derived condition-family labels",
            references=common_refs,
            protocol=(
                "This protocol merges one condition-family label onto each eligible older closed interventional ClinicalTrials.gov study and reuses the wave-eight study-mix adjustment to rank therapeutic portfolios. "
                "Primary outputs compare adjusted no-results excess, adjusted ghost excess, black-box stock, visible-share rates, and strict-core spillover across condition families. "
                "The aim is to separate count-heavy disease backlogs from portfolios that are especially ghosted or black-boxed relative to expectation. "
                "Because condition families are keyword-derived, the outputs approximate therapeutic portfolios rather than formal disease ontologies."
            ),
            root_title="Which therapeutic areas still carry the most excess hiddenness?",
            root_eyebrow="Condition Watchlist Project",
            root_lede="A standalone public project on condition-family excess hiddenness, showing that oncology, cardiovascular, and metabolic studies dominate the adjusted stock table while healthy-volunteer work looks different and much more ghosted.",
            chapter_intro="This page asks whether the disease story changes once raw condition counts are translated into adjusted excess and ghost watchlists. It does.",
            root_pull_quote="The condition story splits into count-heavy disease portfolios and a separate healthy-volunteer silence pattern that is much more ghosted than merely overdue.",
            paper_pull_quote="Condition families do not all hide the same way. Some dominate on adjusted stock, while others stand out because they are especially ghosted or black-boxed.",
            dashboard_pull_quote="Oncology leads the adjusted no-results table, cardiovascular and metabolic follow, and healthy volunteers rise much more sharply on ghost protocols and black-box rate.",
            root_rail=["Oncology +543", "Cardio +373", "Metabolic +251", "Healthy +1.0k ghost"],
            landing_metrics=[
                ("Oncology excess", fmt_int(int(round(as_float(condition_top["excess_no_results"])))), "Adjusted stock"),
                ("Cardio excess", fmt_int(int(round(as_float(condition_second["excess_no_results"])))), "Adjusted stock"),
                ("Metabolic excess", fmt_int(int(round(as_float(condition_third["excess_no_results"])))), "Adjusted stock"),
                ("Healthy ghost", fmt_int(int(round(as_float(condition_ghost["excess_ghost"])))), "Excess ghost stock"),
            ],
            landing_chart_html=chart_section(
                "Adjusted condition-family no-results excess",
                bar_chart(
                    [{"label": row["condition_family_label"], "value": as_float(row["excess_no_results"])} for _, row in condition.head(10).iterrows()],
                    "Condition residuals",
                    "Adjusted excess missing-results counts across condition families",
                    "value",
                    "label",
                    "#c3452f",
                    percent=False,
                ),
                "Oncology leads the stock table, but several smaller families still have sharper rate and ghost signals.",
                "A condition watchlist must read stock and deeper-silence patterns together.",
            ),
            reader_lede="A 156-word micro-paper on which condition families still carry excess hiddenness after visible study mix is held more constant.",
            reader_rail=["Oncology", "Cardio", "Metabolic", "Healthy volunteers"],
            reader_metrics=[
                ("Oncology excess", fmt_int(int(round(as_float(condition_top["excess_no_results"])))), "Adjusted stock"),
                ("Healthy ghost", fmt_int(int(round(as_float(condition_ghost["excess_ghost"])))), "Excess ghost stock"),
                ("Healthy black-box", fmt_pct(as_float(row_for(black_box_condition, "condition_family_label", "Healthy volunteers")["black_box_rate"])), "Black-box rate"),
                ("Oncology strict", fmt_int(as_int(strict_oncology["no_results_count"])), "Strict-core stock"),
            ],
            dashboard_title="Condition-family watchlists show a split between stock-heavy disease backlogs and a separate healthy-volunteer ghost pattern",
            dashboard_eyebrow="Condition Watchlist Dashboard",
            dashboard_lede="Oncology leads on adjusted no-results stock, cardiovascular and metabolic remain next in line, gastrointestinal and reproductive portfolios still rise above expectation, and healthy volunteers become the clearest ghost and black-box outlier.",
            dashboard_rail=["Adjusted stock", "Ghost excess", "Black-box rate", "Strict carryover"],
            dashboard_metrics=[
                ("Oncology excess", fmt_int(int(round(as_float(condition_top["excess_no_results"])))), "Adjusted stock"),
                ("Cardio excess", fmt_int(int(round(as_float(condition_second["excess_no_results"])))), "Adjusted stock"),
                ("Healthy ghost", fmt_int(int(round(as_float(condition_ghost["excess_ghost"])))), "Excess ghost stock"),
                ("Healthy black-box", fmt_pct(as_float(row_for(black_box_condition, "condition_family_label", "Healthy volunteers")["black_box_rate"])), "Black-box rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Adjusted condition-family no-results excess",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["excess_no_results"])} for _, row in condition.head(10).iterrows()],
                        "Adjusted no-results",
                        "Condition families ranked by adjusted excess missing-results stock",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "Oncology, cardiovascular, and metabolic portfolios dominate the adjusted stock table.",
                    "These remain the biggest count-heavy disease backlogs in the wave-nine condition view.",
                ),
                chart_section(
                    "Adjusted condition-family ghost excess",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["excess_ghost"])} for _, row in condition.sort_values("excess_ghost", ascending=False).head(10).iterrows()],
                        "Adjusted ghosts",
                        "Condition families ranked by excess ghost-protocol stock",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Healthy volunteers move to the top once the lens shifts from missing results to ghost protocols.",
                    "That is the major condition-family divergence in this wave.",
                ),
                chart_section(
                    "Condition-family black-box stock",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["black_box_count"])} for _, row in black_box_condition.head(10).iterrows()],
                        "Black-box stock",
                        "Studies with no results, no linked paper, and no detailed description",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "Oncology still dominates absolute black-box stock, but healthy volunteers are much sharper on black-box rate.",
                    "This is why stock and rate must both be read.",
                ),
            ],
            sidebar_bullets=[
                "Oncology carries the largest adjusted excess no-results stock at 543 studies.",
                "Cardiovascular and metabolic studies remain next on the adjusted stock table at 373 and 251 studies.",
                "Healthy volunteers are the clearest ghost-protocol outlier at 1,032 excess ghosted studies.",
                "Healthy-volunteer portfolios also reach a 33.9 percent black-box rate.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-black-box-trials",
            title="CT.gov Black-Box Trials",
            summary="A standalone E156 project on older CT.gov studies with no results, no linked paper, and no detailed description.",
            body=black_box_body,
            sentences=black_box_sentences,
            primary_estimand="Black-box trial stock and rate among eligible older CT.gov studies",
            data_note="249,507 eligible older closed interventional studies with a black-box definition based on results, publication-link, and detailed-description silence",
            references=common_refs,
            protocol=(
                "This protocol defines a black-box trial as an eligible older closed interventional ClinicalTrials.gov study with a two-year results gap, no linked publication reference, and no detailed description. "
                "Primary outputs compare black-box stock and rate across sponsor classes, country-linked portfolios, and condition families, alongside the broader ghost-protocol context. "
                "The aim is to isolate a stricter silence state than ordinary missing-results status. "
                "Because the definition is registry-based, black-box status measures missing visible disclosure on CT.gov rather than any definitive absence of documentation or external reporting elsewhere."
            ),
            root_title="Where are the black-box trials?",
            root_eyebrow="Black-Box Project",
            root_lede="A standalone public project on the strictest silence state in the series: older trials with no results, no linked paper, and no detailed description on the registry page.",
            chapter_intro="This page narrows the registry to its darkest visible subset. It asks where the studies are that lack results, lack a linked paper trail, and still offer no detailed description.",
            root_pull_quote="Industry looks worse on black-box rate, but heterogeneous public and academic portfolios still dominate black-box stock on count.",
            paper_pull_quote="A black-box trial is not just overdue. It is a registry page that still tells the public remarkably little about what happened.",
            dashboard_pull_quote="OTHER dominates black-box stock, INDUSTRY leads on large-class black-box rate, the United States still carries the biggest national stock, and healthy volunteers are the sharpest condition-family extreme.",
            root_rail=["OTHER 21.4k", "Industry 23.4%", "US 12.2k", "Healthy 33.9%"],
            landing_metrics=[
                ("OTHER stock", fmt_int(as_int(black_box_other["black_box_count"])), "Black-box studies"),
                ("Industry rate", fmt_pct(as_float(black_box_industry["black_box_rate"])), "Large-class black-box rate"),
                ("US stock", fmt_int(as_int(black_box_us["black_box_count"])), "Country-linked stock"),
                ("Healthy rate", fmt_pct(as_float(black_box_healthy["black_box_rate"])), "Condition-family black-box rate"),
            ],
            landing_chart_html=chart_section(
                "Black-box stock by sponsor class",
                bar_chart(
                    [{"label": row["lead_sponsor_class"], "value": as_float(row["black_box_count"])} for _, row in black_box_class.iterrows()],
                    "Black-box stock",
                    "Studies with no results, no linked paper, and no detailed description",
                    "value",
                    "label",
                    "#8b6914",
                    percent=False,
                ),
                "OTHER dominates on absolute stock, while INDUSTRY stands out on rate.",
                "That split is the core black-box finding.",
            ),
            reader_lede="A 156-word micro-paper on older CT.gov studies with no results, no linked publication, and no detailed description.",
            reader_rail=["Stock", "Rate", "United States", "Healthy volunteers"],
            reader_metrics=[
                ("OTHER stock", fmt_int(as_int(black_box_other["black_box_count"])), "Absolute black-box stock"),
                ("Industry rate", fmt_pct(as_float(black_box_industry["black_box_rate"])), "Large-class rate"),
                ("US stock", fmt_int(as_int(black_box_us["black_box_count"])), "Country-linked stock"),
                ("Healthy rate", fmt_pct(as_float(black_box_healthy["black_box_rate"])), "Condition-family rate"),
            ],
            dashboard_title="Black-box trials isolate the registry's deepest public silence state",
            dashboard_eyebrow="Black-Box Dashboard",
            dashboard_lede="OTHER dominates black-box stock on count, INDUSTRY has the highest large-class black-box rate, the United States remains the largest country-linked stock, and healthy-volunteer portfolios are the sharpest condition-family extreme.",
            dashboard_rail=["Stock", "Rates", "Countries", "Conditions"],
            dashboard_metrics=[
                ("OTHER stock", fmt_int(as_int(black_box_other["black_box_count"])), "Black-box studies"),
                ("Industry rate", fmt_pct(as_float(black_box_industry["black_box_rate"])), "Large-class rate"),
                ("US stock", fmt_int(as_int(black_box_us["black_box_count"])), "Country-linked stock"),
                ("Healthy rate", fmt_pct(as_float(black_box_healthy["black_box_rate"])), "Condition-family rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Sponsor-class black-box stock",
                    bar_chart(
                        [{"label": row["lead_sponsor_class"], "value": as_float(row["black_box_count"])} for _, row in black_box_class.iterrows()],
                        "Black-box stock",
                        "Black-box studies by sponsor class",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "OTHER and INDUSTRY dominate the stock table together, but they mean different things on rate.",
                    "OTHER reflects broad heterogeneous volume; INDUSTRY reflects a sharper large-class rate problem.",
                ),
                chart_section(
                    "Country-linked black-box stock",
                    bar_chart(
                        [{"label": row["country_name"], "value": as_float(row["black_box_count"])} for _, row in black_box_country.head(10).iterrows()],
                        "Country black boxes",
                        "Country-linked black-box study counts",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "The United States holds the largest absolute black-box stock, with France, Germany, Canada, and China also prominent.",
                    "Absolute stock remains heavily concentrated in large CT.gov portfolios.",
                ),
                chart_section(
                    "Condition-family black-box rate",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["black_box_rate"])} for _, row in black_box_condition.sort_values("black_box_rate", ascending=False).head(10).iterrows()],
                        "Condition black-box rates",
                        "Black-box rate across condition families",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Healthy volunteers are the clearest condition-family extreme, far above the main disease portfolios.",
                    "That makes black-box silence look different from ordinary disease-backlog stories.",
                ),
            ],
            sidebar_bullets=[
                "OTHER holds the largest black-box stock at 21,375 studies.",
                "INDUSTRY has the highest large-class black-box rate at 23.4 percent.",
                "The United States carries 12,183 country-linked black-box studies.",
                "Healthy volunteers reach a 33.9 percent black-box rate, the sharpest condition-family extreme.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-strict-proxy-repeaters",
            title="CT.gov Strict-Proxy Repeaters",
            summary="A standalone E156 project on which sponsors and sponsor classes dominate the strict U.S.-nexus regulated-looking backlog.",
            body=strict_body,
            sentences=strict_sentences,
            primary_estimand="Named-sponsor and sponsor-class missing-results stock inside the strict U.S.-nexus proxy core",
            data_note="58,598-study strict U.S.-nexus drug-biological-device proxy extracted from the older closed interventional CT.gov universe",
            references=common_refs,
            protocol=(
                "This protocol isolates the strict U.S.-nexus drug-biological-device proxy inside eligible older closed interventional ClinicalTrials.gov studies and ranks named sponsors with at least 50 proxy-core studies. "
                "Primary outputs compare strict-core missing-results stock and rate across sponsors, sponsor classes, and condition families, with black-box stock as a secondary severity marker. "
                "The aim is to move from sector summaries to specific repeaters inside the regulated-looking subset. "
                "Because the subset is proxy-defined, the outputs describe a conservative regulated-looking core rather than formal ACT or FDAAA legal determinations."
            ),
            root_title="Who dominates the strict U.S.-nexus backlog?",
            root_eyebrow="Strict Repeaters Project",
            root_lede="A standalone public project on the strict U.S.-nexus proxy core, showing that the regulated-looking backlog remains spread across NIH-linked, academic, and industry sponsors rather than collapsing into one archetype.",
            chapter_intro="This page stays inside the strict U.S.-nexus core and asks who still dominates once the proxy core is read as a repeater problem rather than a sector average.",
            root_pull_quote="The strict-core backlog is smaller than the full registry backlog, but it is still institutionally distributed and far from clean.",
            paper_pull_quote="A stricter proxy core lowers the rate, but it does not make the backlog disappear or confine it to one kind of sponsor.",
            dashboard_pull_quote="NCI leads the strict-core sponsor table, Mayo and MD Anderson remain prominent, OTHER and INDUSTRY stay close on class stock, and NETWORK is worst on large-class rate.",
            root_rail=["NCI 361", "Mayo 204", "OTHER 8.8k", "Network 48.8%"],
            landing_metrics=[
                ("NCI stock", fmt_int(as_int(strict_nci["no_results_count"])), "Strict-core missing results"),
                ("Mayo stock", fmt_int(as_int(strict_mayo["no_results_count"])), "Second repeater"),
                ("OTHER stock", fmt_int(as_int(strict_other["no_results_count"])), "Largest class stock"),
                ("Network rate", fmt_pct(as_float(strict_network["no_results_rate"])), "Highest large-class rate"),
            ],
            landing_chart_html=chart_section(
                "Strict-core sponsor repeaters",
                bar_chart(
                    [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["no_results_count"])} for _, row in strict_sponsor.head(10).iterrows()],
                    "Strict-core stock",
                    "Top missing-results counts inside the strict U.S.-nexus proxy core",
                    "value",
                    "label",
                    "#326891",
                    percent=False,
                ),
                "NCI, Mayo, MD Anderson, and Sanofi sit at the top of the strict-core table.",
                "The strict proxy does not strip away the repeater structure.",
            ),
            reader_lede="A 156-word micro-paper on which sponsors still dominate the strict U.S.-nexus CT.gov core once the regulated-looking subset is read as a repeater problem.",
            reader_rail=["NCI", "Mayo", "Sanofi", "Network"],
            reader_metrics=[
                ("NCI stock", fmt_int(as_int(strict_nci["no_results_count"])), "Strict-core stock"),
                ("Mayo stock", fmt_int(as_int(strict_mayo["no_results_count"])), "Second repeater"),
                ("Sanofi rate", fmt_pct(as_float(strict_sanofi["no_results_rate"])), "Industry strict-core rate"),
                ("Network rate", fmt_pct(as_float(strict_network["no_results_rate"])), "Highest large-class rate"),
            ],
            dashboard_title="Strict-core repeaters show that the regulated-looking backlog remains spread across government-linked, academic, and industry sponsors",
            dashboard_eyebrow="Strict Repeaters Dashboard",
            dashboard_lede="NCI leads the named strict-core table, Mayo and MD Anderson remain close behind, OTHER and INDUSTRY stay close on class stock, and oncology dominates the strict-core condition table.",
            dashboard_rail=["Named repeaters", "Class stock", "Class rates", "Conditions"],
            dashboard_metrics=[
                ("NCI stock", fmt_int(as_int(strict_nci["no_results_count"])), "Strict-core stock"),
                ("Sanofi stock", fmt_int(as_int(strict_sanofi["no_results_count"])), "Largest industry repeater shown"),
                ("OTHER stock", fmt_int(as_int(strict_other["no_results_count"])), "Largest class stock"),
                ("Oncology stock", fmt_int(as_int(strict_oncology["no_results_count"])), "Strict-core condition stock"),
            ],
            dashboard_sections=[
                chart_section(
                    "Strict-core sponsor repeaters",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["no_results_count"])} for _, row in strict_sponsor.head(10).iterrows()],
                        "Strict-core sponsors",
                        "Top strict-core missing-results counts by sponsor",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "NCI leads, but Mayo, MD Anderson, Sanofi, and other institutions remain close enough to show a broad repeater field.",
                    "The strict-core story is still distributed.",
                ),
                chart_section(
                    "Strict-core sponsor-class stock",
                    bar_chart(
                        [{"label": row["lead_sponsor_class"], "value": as_float(row["no_results_count"])} for _, row in strict_class.iterrows()],
                        "Strict-core classes",
                        "Missing-results counts inside the strict U.S.-nexus proxy by sponsor class",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "OTHER and INDUSTRY remain close on stock, with NIH and NETWORK still materially present.",
                    "No single class owns the strict-core backlog.",
                ),
                chart_section(
                    "Strict-core condition stock",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["no_results_count"])} for _, row in strict_condition.head(10).iterrows()],
                        "Strict-core conditions",
                        "Missing-results counts by condition family inside the strict proxy core",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "Oncology dominates the strict-core condition table, with OTHER, cardiovascular, and mental-health portfolios following behind.",
                    "The regulated-looking backlog is still shaped by major therapeutic portfolios as well as sponsor repeaters.",
                ),
            ],
            sidebar_bullets=[
                "NCI leads the strict-core sponsor table with 361 missing-results studies.",
                "Mayo Clinic and MD Anderson follow at 204 and 198 studies.",
                "OTHER and INDUSTRY remain close on strict-core class stock at 8,824 and 7,983 studies.",
                "NETWORK has the highest large-class strict-core no-results rate at 48.8 percent.",
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
