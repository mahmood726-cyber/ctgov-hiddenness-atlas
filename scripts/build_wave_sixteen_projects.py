#!/usr/bin/env python3
"""Build wave-sixteen standalone CT.gov endpoint-only and text-balance projects."""

from __future__ import annotations

from pathlib import Path

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct
from build_split_projects import chart_section, write_project
from build_wave_eight_projects import load_csv, make_spec, row_for, short_sponsor
from build_wave_nine_projects import parse_existing_series_links
from build_wave_twelve_projects import exact_bundle, items, rate_items, replace_once

ROOT = Path(__file__).resolve().parents[1]
ATLAS_INDEX = ROOT / "index.html"


def refresh_atlas_index() -> None:
    text = ATLAS_INDEX.read_text(encoding="utf-8")
    if "seventy-five-project narrative dashboard series" in text and "ctgov-sponsor-class-primary-only-gap" in text:
        return
    text = replace_once(text, "seventy-project narrative dashboard series", "seventy-five-project narrative dashboard series")
    text = replace_once(
        text,
        "The fifteenth wave adds sponsor, country, and condition detailed-description-gap projects plus sponsor and country text-asymmetry projects on top of the earlier sixty-five story pages.",
        "The sixteenth wave adds sponsor, country, condition, and sponsor-class primary-only-gap projects plus a condition text-asymmetry project on top of the earlier seventy story pages.",
    )
    text = replace_once(text, "Use this hub as the visible front door to the full seventy-project series.", "Use this hub as the visible front door to the full seventy-five-project series.")
    text = replace_once(
        text,
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-country-text-asymmetry/'>Country text asymmetry</a>",
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-country-text-asymmetry/'>Country text asymmetry</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-sponsor-primary-only-gap/'>Sponsor primary-only-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-country-primary-only-gap/'>Country primary-only-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-primary-only-gap/'>Condition primary-only-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-text-asymmetry/'>Condition text asymmetry</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-sponsor-class-primary-only-gap/'>Sponsor-class primary-only-gap</a>",
    )
    text = replace_once(
        text,
        "<li>Wave fifteen: sponsor, country, and condition detailed-description-gap projects plus sponsor and country text-asymmetry projects.</li><li>The hub is the visible front door to all seventy public CT.gov story pages.</li>",
        "<li>Wave fifteen: sponsor, country, and condition detailed-description-gap projects plus sponsor and country text-asymmetry projects.</li>"
        "<li>Wave sixteen: sponsor, country, condition, and sponsor-class primary-only-gap projects plus a condition text-asymmetry project.</li>"
        "<li>The hub is the visible front door to all seventy-five public CT.gov story pages.</li>",
    )
    ATLAS_INDEX.write_text(text, encoding="utf-8")


def primary_only_spec(
    *,
    repo_name: str,
    title: str,
    summary: str,
    body_pairs: list[tuple[str, str]],
    protocol: str,
    label_col: str,
    df,
    root_title: str,
    root_eyebrow: str,
    root_lede: str,
    chapter_intro: str,
    root_pull_quote: str,
    paper_pull_quote: str,
    dashboard_pull_quote: str,
    root_rail: list[str],
    landing_metrics: list[tuple[str, str, str]],
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
    label_fn=None,
) -> dict[str, object]:
    body, sentences = exact_bundle(repo_name, body_pairs)
    return make_spec(
        repo_name=repo_name,
        title=title,
        summary=summary,
        body=body,
        sentences=sentences,
        primary_estimand="Primary-only-gap stock among older studies missing the primary outcome description field while retaining the detailed description field",
        data_note="249,507 eligible older closed interventional studies with primary-only-gap stock and rate summaries",
        references=references,
        protocol=protocol,
        root_title=root_title,
        root_eyebrow=root_eyebrow,
        root_lede=root_lede,
        chapter_intro=chapter_intro,
        root_pull_quote=root_pull_quote,
        paper_pull_quote=paper_pull_quote,
        dashboard_pull_quote=dashboard_pull_quote,
        root_rail=root_rail,
        landing_metrics=landing_metrics,
        landing_chart_html=chart_section(
            "Primary-only-gap stock",
            bar_chart(items(df, label_col, "primary_only_count", label_fn=label_fn), "Primary-only stock", "Top counts missing endpoint text while broad narrative remains", "value", "label", "#c3452f", percent=False),
            "The stock table shows where the endpoint sentence disappears even though the broader study description survives.",
            "This isolates endpoint-specific text gaps rather than general narrative blackout.",
        ),
        reader_lede=reader_lede,
        reader_rail=reader_rail,
        reader_metrics=reader_metrics,
        dashboard_title=dashboard_title,
        dashboard_eyebrow=dashboard_eyebrow,
        dashboard_lede=dashboard_lede,
        dashboard_rail=dashboard_rail,
        dashboard_metrics=dashboard_metrics,
        dashboard_sections=dashboard_sections,
        sidebar_bullets=sidebar_bullets,
    )


def condition_asymmetry_spec(
    *,
    repo_name: str,
    title: str,
    summary: str,
    body_pairs: list[tuple[str, str]],
    protocol: str,
    df,
    root_title: str,
    root_eyebrow: str,
    root_lede: str,
    chapter_intro: str,
    root_pull_quote: str,
    paper_pull_quote: str,
    dashboard_pull_quote: str,
    root_rail: list[str],
    landing_metrics: list[tuple[str, str, str]],
    reader_lede: str,
    reader_rail: list[str],
    reader_metrics: list[tuple[str, str, str]],
    dashboard_title: str,
    dashboard_eyebrow: str,
    dashboard_lede: str,
    dashboard_rail: list[str],
    dashboard_metrics: list[tuple[str, str, str]],
    sidebar_bullets: list[str],
    references: list[str],
) -> dict[str, object]:
    body, sentences = exact_bundle(repo_name, body_pairs)
    return make_spec(
        repo_name=repo_name,
        title=title,
        summary=summary,
        body=body,
        sentences=sentences,
        primary_estimand="Condition-family text asymmetry, defined as description-only gaps minus primary-only gaps",
        data_note="249,507 eligible older closed interventional studies with condition-family description-only, primary-only, and net text-balance summaries",
        references=references,
        protocol=protocol,
        root_title=root_title,
        root_eyebrow=root_eyebrow,
        root_lede=root_lede,
        chapter_intro=chapter_intro,
        root_pull_quote=root_pull_quote,
        paper_pull_quote=paper_pull_quote,
        dashboard_pull_quote=dashboard_pull_quote,
        root_rail=root_rail,
        landing_metrics=landing_metrics,
        landing_chart_html=chart_section(
            "Net text asymmetry",
            bar_chart(items(df, "condition_family_label", "text_asymmetry_net"), "Net asymmetry", "Description-only minus primary-only gaps", "value", "label", "#c3452f", percent=False),
            "Net asymmetry shows which therapeutic portfolios lose the broad study narrative much more often than the endpoint sentence.",
            "Positive values mean description-only gaps outnumber endpoint-only gaps.",
        ),
        reader_lede=reader_lede,
        reader_rail=reader_rail,
        reader_metrics=reader_metrics,
        dashboard_title=dashboard_title,
        dashboard_eyebrow=dashboard_eyebrow,
        dashboard_lede=dashboard_lede,
        dashboard_rail=dashboard_rail,
        dashboard_metrics=dashboard_metrics,
        dashboard_sections=[
            chart_section(
                "Net text asymmetry",
                bar_chart(items(df, "condition_family_label", "text_asymmetry_net"), "Net asymmetry", "Description-only minus primary-only gaps", "value", "label", "#c3452f", percent=False),
                "OTHER dominates on net asymmetry, but several named therapeutic portfolios still show large broad-narrative surpluses.",
                "This chart isolates imbalance, not just raw missingness.",
            ),
            chart_section(
                "Asymmetry rate",
                bar_chart(rate_items(df, "condition_family_label", "text_asymmetry_rate"), "Asymmetry rate", "Condition-family asymmetry rate", "value", "label", "#326891", percent=True),
                "Immunology and dermatology is the sharpest rate outlier, with healthy volunteers and neurology also high.",
                "Rate matters because count and severity diverge across therapeutic portfolios.",
            ),
            chart_section(
                "Primary-only stock",
                bar_chart(items(df.sort_values(["primary_only_count", "primary_only_rate"], ascending=[False, False]), "condition_family_label", "primary_only_count"), "Primary-only stock", "Endpoint-only text gaps across condition families", "value", "label", "#8b6914", percent=False),
                "Oncology dominates endpoint-only stock even though OTHER leads the net asymmetry table.",
                "That split is why the balance view changes the story.",
            ),
        ],
        sidebar_bullets=sidebar_bullets,
    )


def main() -> None:
    sponsor_primary = load_csv("wave_sixteen_sponsor_primary_only_gap.csv")
    country_primary = load_csv("wave_sixteen_country_primary_only_gap.csv")
    condition_primary = load_csv("wave_sixteen_condition_primary_only_gap.csv")
    condition_asymmetry = load_csv("wave_sixteen_condition_text_asymmetry.csv")
    class_summary = load_csv("wave_sixteen_text_asymmetry_class_summary.csv")

    sponsor_top = sponsor_primary.iloc[0]
    sponsor_second = sponsor_primary.iloc[1]
    sponsor_third = sponsor_primary.iloc[2]
    sponsor_fourth = sponsor_primary.iloc[3]
    sponsor_rate = sponsor_primary.sort_values(["primary_only_rate", "primary_only_count"], ascending=[False, False])

    country_top = country_primary.iloc[0]
    country_second = country_primary.iloc[1]
    country_third = country_primary.iloc[2]
    country_fourth = country_primary.iloc[3]
    country_rate = country_primary.sort_values(["primary_only_rate", "primary_only_count"], ascending=[False, False])

    condition_top = condition_primary.iloc[0]
    condition_second = condition_primary.iloc[1]
    condition_third = condition_primary.iloc[2]
    condition_fourth = condition_primary.iloc[3]
    condition_rate = condition_primary.sort_values(["primary_only_rate", "primary_only_count"], ascending=[False, False])

    condition_asym_top = condition_asymmetry.iloc[0]
    condition_asym_second = condition_asymmetry.iloc[1]
    condition_asym_third = condition_asymmetry.iloc[2]
    condition_asym_fourth = condition_asymmetry.iloc[3]
    condition_asym_rate = condition_asymmetry.sort_values(["text_asymmetry_rate", "text_asymmetry_net"], ascending=[False, False])

    class_primary_rate = class_summary[class_summary["studies"] >= 100].sort_values(["primary_only_rate", "primary_only_count"], ascending=[False, False]).reset_index(drop=True)
    class_primary_stock = class_summary[class_summary["studies"] >= 100].sort_values(["primary_only_count", "primary_only_rate"], ascending=[False, False]).reset_index(drop=True)
    class_industry = row_for(class_summary, "lead_sponsor_class", "INDUSTRY")
    class_nih = row_for(class_summary, "lead_sponsor_class", "NIH")

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
    ]

    series_links = parse_existing_series_links()
    series_links.extend(
        [
            {"repo_name": "ctgov-sponsor-primary-only-gap", "title": "CT.gov Sponsor Primary-Only Gap", "summary": "Named-sponsor tables showing where endpoint text disappears while the broad study narrative remains.", "short_title": "Sponsor Primary-Only", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-sponsor-primary-only-gap/"},
            {"repo_name": "ctgov-country-primary-only-gap", "title": "CT.gov Country Primary-Only Gap", "summary": "Country-linked tables showing where endpoint text disappears while the broad study narrative remains.", "short_title": "Country Primary-Only", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-primary-only-gap/"},
            {"repo_name": "ctgov-condition-primary-only-gap", "title": "CT.gov Condition Primary-Only Gap", "summary": "Condition-family tables showing where endpoint text disappears while the broad study narrative remains.", "short_title": "Condition Primary-Only", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-primary-only-gap/"},
            {"repo_name": "ctgov-condition-text-asymmetry", "title": "CT.gov Condition Text Asymmetry", "summary": "Condition-family tables showing where broad study narratives disappear much more often than endpoint-only text.", "short_title": "Condition Asymmetry", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-text-asymmetry/"},
            {"repo_name": "ctgov-sponsor-class-primary-only-gap", "title": "CT.gov Sponsor-Class Primary-Only Gap", "summary": "Sponsor-class tables showing where endpoint text disappears while the broad study narrative remains.", "short_title": "Class Primary-Only", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-sponsor-class-primary-only-gap/"},
        ]
    )
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    projects: list[dict[str, object]] = []
    projects.append(
        primary_only_spec(
            repo_name="ctgov-sponsor-primary-only-gap",
            title="CT.gov Sponsor Primary-Only Gap",
            summary="A standalone E156 project on which named sponsors most often omit endpoint text while the broad study narrative remains on older CT.gov records.",
            body_pairs=[
                ("Question", "Which named sponsors most often leave older CT.gov study pages without the primary outcome description while keeping the broader detailed-description field?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and ranked sponsors with at least 100 studies."),
                ("Method", "We defined a primary-only gap as missing primary outcome description with detailed description still present, then compared stock, rate, and class patterns."),
                ("Primary result", "AP-HP led the sponsor primary-only-gap stock table at 421 studies, followed by the National Cancer Institute at 402, NIAID at 351, and Sanofi at 299."),
                ("Secondary result", "Ranbaxy Laboratories Limited had the highest large-sponsor primary-only-gap rate at 98.0 percent, while Dr. Reddys Laboratories reached 82.9 percent and Alliance Oncology reached 60.5 percent."),
                ("Interpretation", "This endpoint-only gap removes the sentence naming the main outcome even when the broader study narrative remains visible for readers."),
                ("Boundary", "These counts describe missing registry text fields and do not by themselves establish legal non-compliance, concealment, or absent materials elsewhere."),
            ],
            protocol="This protocol isolates endpoint-only text gaps inside named-sponsor CT.gov portfolios. A primary-only gap is an eligible older closed interventional study missing the primary outcome description while retaining the detailed description field. Primary outputs rank named sponsors with at least 100 studies by stock and rate and compare sponsor-class patterns.",
            label_col="lead_sponsor_name",
            df=sponsor_primary,
            root_title="Which sponsors most often omit endpoint text while keeping the broad study narrative?",
            root_eyebrow="Sponsor Primary-Only-Gap Project",
            root_lede="A standalone public project on endpoint-only text gaps, showing that AP-HP, NCI, and NIAID dominate on stock while Ranbaxy and Dr. Reddys are much harsher on rate.",
            chapter_intro="This page isolates a specific text imbalance: the detailed-description paragraph remains, but the primary-outcome sentence disappears from older CT.gov records.",
            root_pull_quote="A study page can keep the broad narrative and still omit the single sentence that tells readers what the main endpoint actually was.",
            paper_pull_quote="Primary-only gaps are narrower than general endpoint-text gaps because they require the larger study narrative to remain present.",
            dashboard_pull_quote="AP-HP leads sponsor primary-only-gap stock, NCI and NIAID follow, and Ranbaxy is the sharpest large-sponsor rate outlier.",
            root_rail=["AP-HP 421", "NCI 402", "NIAID 351", "Ranbaxy 98.0%"],
            landing_metrics=[
                ("AP-HP gap", fmt_int(as_int(sponsor_top["primary_only_count"])), "Primary-only gaps"),
                ("NCI gap", fmt_int(as_int(sponsor_second["primary_only_count"])), "Primary-only gaps"),
                ("NIAID gap", fmt_int(as_int(sponsor_third["primary_only_count"])), "Primary-only gaps"),
                ("Ranbaxy rate", fmt_pct(as_float(sponsor_rate.iloc[0]["primary_only_rate"])), "Large-sponsor rate"),
            ],
            reader_lede="A 156-word micro-paper on which named sponsors most often omit endpoint text while the broad study narrative remains on older CT.gov records.",
            reader_rail=["AP-HP", "NCI", "NIAID", "Ranbaxy"],
            reader_metrics=[
                ("AP-HP gap", fmt_int(as_int(sponsor_top["primary_only_count"])), "Primary-only gaps"),
                ("NCI gap", fmt_int(as_int(sponsor_second["primary_only_count"])), "Primary-only gaps"),
                ("NIAID gap", fmt_int(as_int(sponsor_third["primary_only_count"])), "Primary-only gaps"),
                ("Sanofi gap", fmt_int(as_int(sponsor_fourth["primary_only_count"])), "Primary-only gaps"),
            ],
            dashboard_title="Sponsor primary-only-gap tables show where endpoint text disappears while the broad study narrative survives",
            dashboard_eyebrow="Sponsor Primary-Only-Gap Dashboard",
            dashboard_lede="AP-HP leads sponsor primary-only-gap stock, NCI and NIAID remain close behind, Ranbaxy and Dr. Reddys are extreme on rate, and NIH stands far above Industry on class rate.",
            dashboard_rail=["Primary-only stock", "Rate", "Classes", "Endpoints"],
            dashboard_metrics=[
                ("AP-HP gap", fmt_int(as_int(sponsor_top["primary_only_count"])), "Primary-only gaps"),
                ("NCI gap", fmt_int(as_int(sponsor_second["primary_only_count"])), "Primary-only gaps"),
                ("Ranbaxy rate", fmt_pct(as_float(sponsor_rate.iloc[0]["primary_only_rate"])), "Large-sponsor rate"),
                ("NIH rate", fmt_pct(as_float(class_nih["primary_only_rate"])), "Class rate"),
            ],
            dashboard_sections=[
                chart_section("Primary-only-gap stock", bar_chart(items(sponsor_primary, "lead_sponsor_name", "primary_only_count", label_fn=lambda value: short_sponsor(str(value))), "Primary-only stock", "Top sponsor counts missing endpoint text while narrative remains", "value", "label", "#c3452f", percent=False), "AP-HP, NCI, NIAID, and Sanofi dominate the endpoint-only stock table.", "That makes the primary-only gap a mix of major public and industry portfolios."),
                chart_section("Primary-only-gap rate", bar_chart(rate_items(sponsor_primary, "lead_sponsor_name", "primary_only_rate", label_fn=lambda value: short_sponsor(str(value))), "Primary-only rate", "Large-sponsor primary-only-gap rate", "value", "label", "#326891", percent=True), "Ranbaxy and Dr. Reddys are extreme on rate, with Alliance Oncology and NIDA also high.", "Stock and rate again point to overlapping but different repeaters."),
                chart_section("Sponsor-class rate", bar_chart([{"label": row["lead_sponsor_class"], "value": as_float(row["primary_only_rate"])} for _, row in class_primary_rate.iterrows()], "Class rate", "Primary-only-gap rate by sponsor class", "value", "label", "#8b6914", percent=True), "NIH has the highest substantive sponsor-class primary-only rate, with Network and Indiv also elevated.", "Industry is lower on rate but still large on absolute endpoint-only stock."),
            ],
            sidebar_bullets=[
                "AP-HP leads sponsor primary-only-gap stock at 421 studies.",
                "NCI is next at 402, with NIAID at 351 and Sanofi at 299.",
                "Ranbaxy Laboratories Limited reaches a 98.0 percent primary-only-gap rate among large sponsors.",
                "NIH reaches a 29.4 percent primary-only-gap rate as a sponsor class.",
            ],
            references=common_refs,
            label_fn=lambda value: short_sponsor(str(value)),
        )
    )
    projects.append(
        primary_only_spec(
            repo_name="ctgov-country-primary-only-gap",
            title="CT.gov Country Primary-Only Gap",
            summary="A standalone E156 project on which country-linked portfolios most often omit endpoint text while the broad study narrative remains on older CT.gov records.",
            body_pairs=[
                ("Question", "Which country-linked CT.gov portfolios most often leave older study pages without the primary outcome description while keeping the broader detailed-description field?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded country links."),
                ("Method", "We defined a primary-only gap as missing primary outcome description with detailed description still present, then ranked country-linked portfolios with at least 500 linked studies."),
                ("Primary result", "The United States led the country-linked primary-only-gap stock table at 13,662 studies, followed by Canada at 2,381, France at 2,233, and Germany at 1,629."),
                ("Secondary result", "Iran had the highest large-country primary-only-gap rate at 18.4 percent, while India reached 15.1 percent and Canada 13.8 percent."),
                ("Interpretation", "Country-linked primary-only gaps show where the endpoint sentence disappears even though the broader study narrative remains visible in older registry records."),
                ("Boundary", "Country-linked rows are non-exclusive because multinational studies can contribute to more than one national portfolio in registry link tables. They reflect registry link geography rather than jurisdiction."),
            ],
            protocol="This protocol isolates endpoint-only text gaps inside country-linked CT.gov portfolios. A primary-only gap is an eligible older closed interventional study missing the primary outcome description while retaining the detailed description field. Primary outputs rank country-linked portfolios with at least 500 linked studies by stock and rate.",
            label_col="country_name",
            df=country_primary,
            root_title="Which country-linked portfolios most often omit endpoint text while keeping the broad study narrative?",
            root_eyebrow="Country Primary-Only-Gap Project",
            root_lede="A standalone public project on country-linked endpoint-only gaps, showing that the United States dominates on stock while Iran, India, and Canada are harsher on rate.",
            chapter_intro="This page moves the endpoint-only gap into geography and asks where country-linked CT.gov portfolios most often keep the broad narrative paragraph but lose the endpoint sentence.",
            root_pull_quote="Keeping the study narrative but dropping the endpoint sentence leaves readers with context but weakens their grasp of what the study treated as its main outcome.",
            paper_pull_quote="Country-linked stock and rate split again here: the United States dominates on volume, while Iran, India, and Canada are sharper on endpoint-only rate.",
            dashboard_pull_quote="The United States leads country-linked primary-only-gap stock, Canada and France follow, and Iran is the sharpest large-country rate outlier.",
            root_rail=["US 13,662", "Canada 2,381", "France 2,233", "Iran 18.4%"],
            landing_metrics=[
                ("US gap", fmt_int(as_int(country_top["primary_only_count"])), "Primary-only gaps"),
                ("Canada gap", fmt_int(as_int(country_second["primary_only_count"])), "Primary-only gaps"),
                ("France gap", fmt_int(as_int(country_third["primary_only_count"])), "Primary-only gaps"),
                ("Iran rate", fmt_pct(as_float(country_rate.iloc[0]["primary_only_rate"])), "Large-country rate"),
            ],
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios most often omit endpoint text while the broad study narrative remains.",
            reader_rail=["United States", "Canada", "France", "Iran"],
            reader_metrics=[
                ("US gap", fmt_int(as_int(country_top["primary_only_count"])), "Primary-only gaps"),
                ("Canada gap", fmt_int(as_int(country_second["primary_only_count"])), "Primary-only gaps"),
                ("France gap", fmt_int(as_int(country_third["primary_only_count"])), "Primary-only gaps"),
                ("Germany gap", fmt_int(as_int(country_fourth["primary_only_count"])), "Primary-only gaps"),
            ],
            dashboard_title="Country primary-only-gap tables show where endpoint text disappears while the broad study narrative survives",
            dashboard_eyebrow="Country Primary-Only-Gap Dashboard",
            dashboard_lede="The United States dominates country-linked primary-only-gap stock, Canada and France remain large on count, and Iran, India, and Canada are the clearest rate outliers.",
            dashboard_rail=["Primary-only stock", "Rate", "Countries", "Endpoints"],
            dashboard_metrics=[
                ("US gap", fmt_int(as_int(country_top["primary_only_count"])), "Primary-only gaps"),
                ("Canada gap", fmt_int(as_int(country_second["primary_only_count"])), "Primary-only gaps"),
                ("Iran rate", fmt_pct(as_float(country_rate.iloc[0]["primary_only_rate"])), "Large-country rate"),
                ("India rate", fmt_pct(as_float(country_rate.iloc[1]["primary_only_rate"])), "Large-country rate"),
            ],
            dashboard_sections=[
                chart_section("Primary-only-gap stock", bar_chart(items(country_primary, "country_name", "primary_only_count"), "Primary-only stock", "Top country-linked counts missing endpoint text while narrative remains", "value", "label", "#c3452f", percent=False), "The United States dominates on stock, with Canada, France, and Germany also carrying large endpoint-only portfolios.", "Stock alone does not capture how much harsher some smaller national portfolios are on rate."),
                chart_section("Primary-only-gap rate", bar_chart(rate_items(country_primary, "country_name", "primary_only_rate"), "Primary-only rate", "Large-country primary-only-gap rate", "value", "label", "#326891", percent=True), "Iran is the sharpest large-country rate outlier, while India, Canada, and Norway stay high.", "That rate order looks different from the stock table."),
                chart_section("Description-only stock", bar_chart(items(country_primary.sort_values(["description_only_count", "primary_only_count"], ascending=[False, False]), "country_name", "description_only_count"), "Description-only stock", "Broad narrative gaps where endpoint text remains", "value", "label", "#8b6914", percent=False), "Country-linked description-only stock is much larger than primary-only stock in many portfolios.", "That is why the primary-only project is analytically distinct from the broader text-balance map."),
            ],
            sidebar_bullets=[
                "The United States leads country-linked primary-only-gap stock at 13,662 studies.",
                "Canada is next at 2,381, with France at 2,233 and Germany at 1,629.",
                "Iran reaches the highest large-country primary-only-gap rate at 18.4 percent.",
                "India and Canada follow at 15.1 percent and 13.8 percent.",
            ],
            references=common_refs,
        )
    )
    projects.append(
        primary_only_spec(
            repo_name="ctgov-condition-primary-only-gap",
            title="CT.gov Condition Primary-Only Gap",
            summary="A standalone E156 project on which therapeutic portfolios most often omit endpoint text while the broad study narrative remains on older CT.gov records.",
            body_pairs=[
                ("Question", "Which condition families most often leave older CT.gov study pages without the primary outcome description while keeping the broader detailed-description field?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
                ("Method", "We defined a primary-only gap as missing primary outcome description with detailed description still present, then ranked large condition families by stock and rate."),
                ("Primary result", "Oncology led the condition-family primary-only-gap stock table at 7,102 studies, followed by Other at 5,818, Cardiovascular at 3,766, and Infectious disease at 2,584."),
                ("Secondary result", "Oncology also had the highest large-family primary-only-gap rate at 16.8 percent, ahead of Cardiovascular at 14.5 percent and Infectious disease at 14.3 percent."),
                ("Interpretation", "Condition-family primary-only gaps show where the endpoint sentence disappears most often even though the broader study narrative remains on the page."),
                ("Boundary", "Condition families are keyword-derived registry groupings rather than formal disease ontologies or mutually exclusive diagnoses across all studies. They simplify diagnoses for readers."),
            ],
            protocol="This protocol isolates endpoint-only text gaps inside condition-family CT.gov portfolios. A primary-only gap is an eligible older closed interventional study missing the primary outcome description while retaining the detailed description field. Primary outputs rank large condition families by stock and rate using one condition-family label per study.",
            label_col="condition_family_label",
            df=condition_primary,
            root_title="Which therapeutic portfolios most often omit endpoint text while keeping the broad study narrative?",
            root_eyebrow="Condition Primary-Only-Gap Project",
            root_lede="A standalone public project on therapeutic endpoint-only gaps, showing that Oncology dominates on both stock and rate while Cardiovascular and Infectious disease remain large on count.",
            chapter_intro="This page asks which therapeutic portfolios most often keep the broad study narrative but lose the endpoint sentence once the primary-only gap is moved from sponsors and countries into condition families.",
            root_pull_quote="If the endpoint sentence disappears while the narrative remains, readers can still grasp the study topic but not the main outcome it was built to measure.",
            paper_pull_quote="Oncology dominates the primary-only map on both stock and rate, making endpoint-only text loss a central oncology registry problem rather than a fringe issue.",
            dashboard_pull_quote="Oncology leads condition-family primary-only-gap stock and also leads on rate, while Cardiovascular and Infectious disease remain substantial on count.",
            root_rail=["Oncology 7,102", "Other 5,818", "Cardio 3,766", "Oncology 16.8%"],
            landing_metrics=[
                ("Oncology gap", fmt_int(as_int(condition_top["primary_only_count"])), "Primary-only gaps"),
                ("Other gap", fmt_int(as_int(condition_second["primary_only_count"])), "Primary-only gaps"),
                ("Cardio gap", fmt_int(as_int(condition_third["primary_only_count"])), "Primary-only gaps"),
                ("Oncology rate", fmt_pct(as_float(condition_rate.iloc[0]["primary_only_rate"])), "Large-family rate"),
            ],
            reader_lede="A 156-word micro-paper on which therapeutic CT.gov portfolios most often omit endpoint text while the broad study narrative remains.",
            reader_rail=["Oncology", "Other", "Cardiovascular", "Infectious disease"],
            reader_metrics=[
                ("Oncology gap", fmt_int(as_int(condition_top["primary_only_count"])), "Primary-only gaps"),
                ("Other gap", fmt_int(as_int(condition_second["primary_only_count"])), "Primary-only gaps"),
                ("Cardio gap", fmt_int(as_int(condition_third["primary_only_count"])), "Primary-only gaps"),
                ("Infectious gap", fmt_int(as_int(condition_fourth["primary_only_count"])), "Primary-only gaps"),
            ],
            dashboard_title="Condition primary-only-gap tables show where endpoint text disappears while the broad study narrative survives",
            dashboard_eyebrow="Condition Primary-Only-Gap Dashboard",
            dashboard_lede="Oncology dominates condition-family primary-only-gap stock and rate, while Cardiovascular, Infectious disease, and Metabolic remain large on count and Renal portfolios stay elevated on rate.",
            dashboard_rail=["Primary-only stock", "Rate", "Conditions", "Endpoints"],
            dashboard_metrics=[
                ("Oncology gap", fmt_int(as_int(condition_top["primary_only_count"])), "Primary-only gaps"),
                ("Other gap", fmt_int(as_int(condition_second["primary_only_count"])), "Primary-only gaps"),
                ("Oncology rate", fmt_pct(as_float(condition_rate.iloc[0]["primary_only_rate"])), "Large-family rate"),
                ("Cardio rate", fmt_pct(as_float(condition_rate.iloc[1]["primary_only_rate"])), "Large-family rate"),
            ],
            dashboard_sections=[
                chart_section("Primary-only-gap stock", bar_chart(items(condition_primary, "condition_family_label", "primary_only_count"), "Primary-only stock", "Top condition-family counts missing endpoint text while narrative remains", "value", "label", "#c3452f", percent=False), "Oncology dominates on count, with Other and Cardiovascular also carrying large endpoint-only portfolios.", "This field gap therefore sits in major therapeutic areas, not only small fringe categories."),
                chart_section("Primary-only-gap rate", bar_chart(rate_items(condition_primary, "condition_family_label", "primary_only_rate"), "Primary-only rate", "Large-family primary-only-gap rate", "value", "label", "#326891", percent=True), "Oncology is the sharpest large-family rate outlier, with Cardiovascular and Infectious disease just behind.", "Rate confirms the endpoint-only problem is concentrated in major disease areas."),
                chart_section("Description-only stock", bar_chart(items(condition_primary.sort_values(["description_only_count", "primary_only_count"], ascending=[False, False]), "condition_family_label", "description_only_count"), "Description-only stock", "Broad narrative gaps while endpoint text remains", "value", "label", "#8b6914", percent=False), "Description-only stock remains even larger in several therapeutic portfolios than primary-only stock.", "That broader text imbalance is why the companion condition asymmetry project matters."),
            ],
            sidebar_bullets=[
                "Oncology leads condition-family primary-only-gap stock at 7,102 studies.",
                "Other is next at 5,818, with Cardiovascular at 3,766 and Infectious disease at 2,584.",
                "Oncology reaches the highest large-family primary-only-gap rate at 16.8 percent.",
                "Cardiovascular and Infectious disease follow at 14.5 percent and 14.3 percent.",
            ],
            references=common_refs,
        )
    )
    projects.append(
        condition_asymmetry_spec(
            repo_name="ctgov-condition-text-asymmetry",
            title="CT.gov Condition Text Asymmetry",
            summary="A standalone E156 project on which therapeutic portfolios show the biggest imbalance between missing broad narratives and missing endpoint-only text.",
            body_pairs=[
                ("Question", "Which condition families show the biggest imbalance between missing detailed descriptions and missing primary-outcome-only text in older CT.gov records?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
                ("Method", "We compared description-only gaps against primary-only gaps and defined net text asymmetry as description-only minus primary-only counts and rates."),
                ("Primary result", "Other led the condition-family text-asymmetry table at 7,699 net description-only gaps, followed by Musculoskeletal and pain at 2,521, Healthy volunteers at 2,134, and Cardiovascular at 1,802."),
                ("Secondary result", "Immunology and dermatology had the highest condition asymmetry rate at 19.7 percentage points, while Healthy volunteers reached 15.1 points and Neurology 15.0 points."),
                ("Interpretation", "The asymmetry lens shows which therapeutic portfolios lose the broader study narrative much more often than the endpoint sentence, changing how text opacity is distributed for readers."),
                ("Boundary", "Positive asymmetry does not by itself prove concealment; it shows which field disappears more often inside mature public registry records overall."),
            ],
            protocol="This protocol isolates description-vs-endpoint text imbalance inside condition-family CT.gov portfolios. A description-only gap is a study missing the detailed description while retaining the primary outcome description, and a primary-only gap is the reverse. Net text asymmetry is description-only minus primary-only counts and rates. Primary outputs rank large condition families by net asymmetry and asymmetry rate.",
            df=condition_asymmetry,
            root_title="Which therapeutic portfolios show the largest description-vs-endpoint text asymmetry?",
            root_eyebrow="Condition Text-Asymmetry Project",
            root_lede="A standalone public project on therapeutic text imbalance, showing that Other dominates on net asymmetry while Immunology and dermatology is much harsher on rate.",
            chapter_intro="This page is not about missing text in general. It asks where therapeutic portfolios most often lose the broad study narrative while the endpoint sentence survives.",
            root_pull_quote="Text asymmetry changes the reading of registry opacity because it asks which field disappears more often when the two descriptive layers split apart.",
            paper_pull_quote="Condition asymmetry separates broad-narrative loss from endpoint loss and shows that the therapeutic ranking changes once those two text layers are compared directly.",
            dashboard_pull_quote="Other leads condition-family net text asymmetry, Musculoskeletal and Healthy volunteers follow, and Immunology and dermatology is the sharpest rate outlier.",
            root_rail=["Other 7,699", "MSK 2,521", "Healthy 2,134", "Immunology 19.7"],
            landing_metrics=[
                ("Other net", fmt_int(as_int(condition_asym_top["text_asymmetry_net"])), "Net asymmetry"),
                ("MSK net", fmt_int(as_int(condition_asym_second["text_asymmetry_net"])), "Net asymmetry"),
                ("Healthy net", fmt_int(as_int(condition_asym_third["text_asymmetry_net"])), "Net asymmetry"),
                ("Immunology rate", fmt_pct(as_float(condition_asym_rate.iloc[0]["text_asymmetry_rate"])), "Rate points"),
            ],
            reader_lede="A 156-word micro-paper on which therapeutic CT.gov portfolios show the largest imbalance between missing broad narratives and missing endpoint-only text.",
            reader_rail=["Other", "Musculoskeletal", "Healthy volunteers", "Immunology"],
            reader_metrics=[
                ("Other net", fmt_int(as_int(condition_asym_top["text_asymmetry_net"])), "Net asymmetry"),
                ("MSK net", fmt_int(as_int(condition_asym_second["text_asymmetry_net"])), "Net asymmetry"),
                ("Healthy net", fmt_int(as_int(condition_asym_third["text_asymmetry_net"])), "Net asymmetry"),
                ("Cardio net", fmt_int(as_int(condition_asym_fourth["text_asymmetry_net"])), "Net asymmetry"),
            ],
            dashboard_title="Condition text-asymmetry tables show where broad narratives disappear much more often than endpoint text",
            dashboard_eyebrow="Condition Text-Asymmetry Dashboard",
            dashboard_lede="Other dominates condition-family net text asymmetry, Musculoskeletal and Healthy volunteers stay large on count, and Immunology and dermatology is the clearest rate outlier.",
            dashboard_rail=["Net asymmetry", "Rate", "Conditions", "Text balance"],
            dashboard_metrics=[
                ("Other net", fmt_int(as_int(condition_asym_top["text_asymmetry_net"])), "Net asymmetry"),
                ("MSK net", fmt_int(as_int(condition_asym_second["text_asymmetry_net"])), "Net asymmetry"),
                ("Immunology rate", fmt_pct(as_float(condition_asym_rate.iloc[0]["text_asymmetry_rate"])), "Rate points"),
                ("Healthy rate", fmt_pct(as_float(condition_asym_rate.iloc[1]["text_asymmetry_rate"])), "Rate points"),
            ],
            sidebar_bullets=[
                "Other leads condition-family net text asymmetry at 7,699.",
                "Musculoskeletal and pain is next at 2,521, with Healthy volunteers at 2,134 and Cardiovascular at 1,802.",
                "Immunology and dermatology reaches the highest condition asymmetry rate at 19.7 percentage points.",
                "Healthy volunteers and Neurology follow at 15.1 and 15.0 points.",
            ],
            references=common_refs,
        )
    )
    projects.append(
        primary_only_spec(
            repo_name="ctgov-sponsor-class-primary-only-gap",
            title="CT.gov Sponsor-Class Primary-Only Gap",
            summary="A standalone E156 project on which sponsor classes most often omit endpoint text while the broad study narrative remains on older CT.gov records.",
            body_pairs=[
                ("Question", "Which sponsor classes most often leave older CT.gov study pages without the primary outcome description while keeping the broader detailed-description field?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and grouped them by lead sponsor class."),
                ("Method", "We defined a primary-only gap as missing primary outcome description with detailed description still present, then compared sponsor-class stock, rate, and text-balance context."),
                ("Primary result", "The Other class led sponsor-class primary-only-gap stock at 21,381 studies, followed by Industry at 7,906, NIH at 1,258, and Other Gov at 729."),
                ("Secondary result", "NIH had the highest substantive sponsor-class primary-only-gap rate at 29.4 percent, while Network reached 21.2 percent and Indiv 20.5 percent."),
                ("Interpretation", "The sponsor-class view shows that endpoint-only text gaps are not spread evenly: NIH and network portfolios are much sharper on rate, while Other and Industry dominate on stock."),
                ("Boundary", "Sponsor classes are broad registry buckets and should be read as portfolio patterns rather than judgments about single studies."),
            ],
            protocol="This protocol isolates endpoint-only text gaps inside sponsor-class CT.gov portfolios. A primary-only gap is an eligible older closed interventional study missing the primary outcome description while retaining the detailed description field. Primary outputs compare sponsor-class stock, rate, and companion text-balance measures.",
            label_col="lead_sponsor_class",
            df=class_primary_stock,
            root_title="Which sponsor classes most often omit endpoint text while keeping the broad study narrative?",
            root_eyebrow="Sponsor-Class Primary-Only-Gap Project",
            root_lede="A standalone public project on sponsor-class endpoint-only gaps, showing that Other and Industry dominate on stock while NIH is much harsher on rate.",
            chapter_intro="This page steps back from named entities and asks how the endpoint-only gap sorts across the sponsor classes used in the CT.gov registry.",
            root_pull_quote="The class view matters because high-stock classes and high-rate classes are not the same thing in this endpoint-only map.",
            paper_pull_quote="Other and Industry dominate endpoint-only stock, but NIH and Network are much sharper on rate once class size is taken into account.",
            dashboard_pull_quote="Other leads sponsor-class primary-only stock, Industry follows, and NIH is the clearest substantive rate outlier.",
            root_rail=["Other 21,381", "Industry 7,906", "NIH 1,258", "NIH 29.4%"],
            landing_metrics=[
                ("Other gap", fmt_int(as_int(class_primary_stock.iloc[0]["primary_only_count"])), "Primary-only gaps"),
                ("Industry gap", fmt_int(as_int(class_primary_stock.iloc[1]["primary_only_count"])), "Primary-only gaps"),
                ("NIH gap", fmt_int(as_int(class_primary_stock.iloc[2]["primary_only_count"])), "Primary-only gaps"),
                ("NIH rate", fmt_pct(as_float(class_nih["primary_only_rate"])), "Substantive class rate"),
            ],
            reader_lede="A 156-word micro-paper on which sponsor classes most often omit endpoint text while the broad study narrative remains on older CT.gov records.",
            reader_rail=["Other", "Industry", "NIH", "Network"],
            reader_metrics=[
                ("Other gap", fmt_int(as_int(class_primary_stock.iloc[0]["primary_only_count"])), "Primary-only gaps"),
                ("Industry gap", fmt_int(as_int(class_primary_stock.iloc[1]["primary_only_count"])), "Primary-only gaps"),
                ("NIH gap", fmt_int(as_int(class_primary_stock.iloc[2]["primary_only_count"])), "Primary-only gaps"),
                ("Network gap", fmt_int(as_int(class_primary_stock.iloc[4]["primary_only_count"])), "Primary-only gaps"),
            ],
            dashboard_title="Sponsor-class primary-only-gap tables show where endpoint text disappears while the broad study narrative survives",
            dashboard_eyebrow="Sponsor-Class Primary-Only-Gap Dashboard",
            dashboard_lede="Other and Industry dominate sponsor-class primary-only stock, NIH is the clearest substantive rate outlier, and class balance changes sharply once text asymmetry is considered.",
            dashboard_rail=["Primary-only stock", "Rate", "Text balance", "Classes"],
            dashboard_metrics=[
                ("Other gap", fmt_int(as_int(class_primary_stock.iloc[0]["primary_only_count"])), "Primary-only gaps"),
                ("Industry gap", fmt_int(as_int(class_primary_stock.iloc[1]["primary_only_count"])), "Primary-only gaps"),
                ("NIH rate", fmt_pct(as_float(class_nih["primary_only_rate"])), "Substantive class rate"),
                ("Industry net", fmt_int(as_int(class_industry["text_asymmetry_net"])), "Net asymmetry"),
            ],
            dashboard_sections=[
                chart_section("Primary-only-gap stock", bar_chart(items(class_primary_stock, "lead_sponsor_class", "primary_only_count"), "Primary-only stock", "Primary-only-gap stock by sponsor class", "value", "label", "#c3452f", percent=False), "Other and Industry dominate on stock because they cover much of the mature registry.", "NIH is smaller on stock but much sharper on rate."),
                chart_section("Primary-only-gap rate", bar_chart([{"label": row["lead_sponsor_class"], "value": as_float(row["primary_only_rate"])} for _, row in class_primary_rate.iterrows()], "Primary-only rate", "Primary-only-gap rate by sponsor class", "value", "label", "#326891", percent=True), "NIH leads the substantive class rate table, with Network and Indiv also elevated.", "That rate ranking differs sharply from the stock order."),
                chart_section("Description-only rate", bar_chart([{"label": row["lead_sponsor_class"], "value": as_float(row["description_only_rate"])} for _, row in class_primary_rate.iterrows()], "Description-only rate", "Description-only rate by sponsor class", "value", "label", "#8b6914", percent=True), "Industry is much higher than NIH on description-only rate, which explains why the two classes look so different on the broader text-balance map.", "The class project therefore connects the primary-only layer to the larger asymmetry story."),
            ],
            sidebar_bullets=[
                "Other leads sponsor-class primary-only stock at 21,381 studies.",
                "Industry is next at 7,906, with NIH at 1,258 and Other Gov at 729.",
                "NIH reaches the highest substantive sponsor-class primary-only rate at 29.4 percent.",
                "Industry still carries the largest positive class text asymmetry at 18,009.",
            ],
            references=common_refs,
        )
    )
    for spec in projects:
        spec["repo_url"] = f"https://github.com/{REPO_OWNER}/{spec['repo_name']}"
        spec["pages_url"] = f"https://{REPO_OWNER}.github.io/{spec['repo_name']}/"
        spec["series_hub_url"] = series_hub_url
        spec["series_links"] = series_links
        path = write_project(spec)
        print(f"Built {path}")

    refresh_atlas_index()
    print(f"Updated {ATLAS_INDEX}")


if __name__ == "__main__":
    main()
