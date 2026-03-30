#!/usr/bin/env python3
"""Build wave-fifteen standalone CT.gov detailed-description-gap and text-asymmetry projects."""

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
    if "seventy-project narrative dashboard series" in text and "ctgov-country-text-asymmetry" in text:
        return
    text = replace_once(text, "sixty-five-project narrative dashboard series", "seventy-project narrative dashboard series")
    text = replace_once(
        text,
        "The fourteenth wave adds country and condition narrative-gap projects plus sponsor, country, and condition primary-outcome-gap projects on top of the earlier sixty story pages.",
        "The fifteenth wave adds sponsor, country, and condition detailed-description-gap projects plus sponsor and country text-asymmetry projects on top of the earlier sixty-five story pages.",
    )
    text = replace_once(text, "Use this hub as the visible front door to the full sixty-five-project series.", "Use this hub as the visible front door to the full seventy-project series.")
    text = replace_once(
        text,
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-primary-outcome-gap/'>Condition primary-outcome-gap</a>",
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-primary-outcome-gap/'>Condition primary-outcome-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-sponsor-detailed-description-gap/'>Sponsor detailed-description-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-country-detailed-description-gap/'>Country detailed-description-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-detailed-description-gap/'>Condition detailed-description-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-sponsor-text-asymmetry/'>Sponsor text asymmetry</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-country-text-asymmetry/'>Country text asymmetry</a>",
    )
    text = replace_once(
        text,
        "<li>Wave fourteen: country and condition narrative-gap projects plus sponsor, country, and condition primary-outcome-gap projects.</li><li>The hub is the visible front door to all sixty-five public CT.gov story pages.</li>",
        "<li>Wave fourteen: country and condition narrative-gap projects plus sponsor, country, and condition primary-outcome-gap projects.</li>"
        "<li>Wave fifteen: sponsor, country, and condition detailed-description-gap projects plus sponsor and country text-asymmetry projects.</li>"
        "<li>The hub is the visible front door to all seventy public CT.gov story pages.</li>",
    )
    ATLAS_INDEX.write_text(text, encoding="utf-8")


def detailed_gap_spec(
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
        primary_estimand="Detailed-description-gap stock among older studies missing the detailed description field",
        data_note="249,507 eligible older closed interventional studies with detailed-description-gap stock and rate summaries",
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
            "Detailed-description-gap stock",
            bar_chart(items(df, label_col, "detailed_gap_count", label_fn=label_fn), "Detailed-gap stock", "Top counts missing the detailed description field", "value", "label", "#c3452f", percent=False),
            "The stock table shows where the broad study narrative most often disappears on count.",
            "This field gap is wider than primary-outcome text alone because it removes the larger descriptive paragraph.",
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


def asymmetry_spec(
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
        primary_estimand="Net description-vs-endpoint asymmetry among older studies, defined as description-only gaps minus primary-only gaps",
        data_note="249,507 eligible older closed interventional studies with description-only, primary-only, and net text-asymmetry summaries",
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
            bar_chart(items(df, label_col, "text_asymmetry_net", label_fn=label_fn), "Net asymmetry", "Description-only minus primary-only gaps", "value", "label", "#c3452f", percent=False),
            "Net asymmetry shows where the broad study description disappears much more often than the endpoint sentence.",
            "Positive values mean description-only gaps outnumber primary-only gaps.",
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
                bar_chart(items(df, label_col, "text_asymmetry_net", label_fn=label_fn), "Net asymmetry", "Description-only minus primary-only gaps", "value", "label", "#c3452f", percent=False),
                "The leading net table shows where description-only gaps dominate most strongly on count.",
                "This isolates imbalance rather than simple missingness volume.",
            ),
            chart_section(
                "Asymmetry rate",
                bar_chart(rate_items(df, label_col, "text_asymmetry_rate", label_fn=label_fn), "Asymmetry rate", "Net asymmetry rate in percentage points", "value", "label", "#326891", percent=True),
                "Rate highlights where the imbalance is sharpest after portfolio size is accounted for.",
                "A high asymmetry rate means the larger narrative disappears far more often than the endpoint sentence.",
            ),
            chart_section(
                "Description-only stock",
                bar_chart(items(df.sort_values(["description_only_count", "text_asymmetry_net"], ascending=[False, False]), label_col, "description_only_count", label_fn=label_fn), "Description-only stock", "Missing detailed description while endpoint text remains", "value", "label", "#8b6914", percent=False),
                "Description-only stock shows the raw layer driving the asymmetry result.",
                "It makes clear that these projects are not about generic missing text alone but about one field disappearing more than the other.",
            ),
        ],
        sidebar_bullets=sidebar_bullets,
    )


def main() -> None:
    sponsor_detailed = load_csv("wave_fifteen_sponsor_detailed_description_gap.csv")
    country_detailed = load_csv("wave_fifteen_country_detailed_description_gap.csv")
    condition_detailed = load_csv("wave_fifteen_condition_detailed_description_gap.csv")
    sponsor_asymmetry = load_csv("wave_fifteen_sponsor_text_asymmetry.csv")
    country_asymmetry = load_csv("wave_fifteen_country_text_asymmetry.csv")
    detailed_class = load_csv("wave_fifteen_detailed_description_gap_class_summary.csv")
    asymmetry_class = load_csv("wave_fifteen_text_asymmetry_class_summary.csv")

    sponsor_detailed_top = sponsor_detailed.iloc[0]
    sponsor_detailed_second = sponsor_detailed.iloc[1]
    sponsor_detailed_third = sponsor_detailed.iloc[2]
    sponsor_detailed_fourth = sponsor_detailed.iloc[3]
    sponsor_detailed_rate = sponsor_detailed.sort_values(["detailed_gap_rate", "detailed_gap_count"], ascending=[False, False])

    country_detailed_top = country_detailed.iloc[0]
    country_detailed_second = country_detailed.iloc[1]
    country_detailed_third = country_detailed.iloc[2]
    country_detailed_fourth = country_detailed.iloc[3]
    country_detailed_rate = country_detailed.sort_values(["detailed_gap_rate", "detailed_gap_count"], ascending=[False, False])

    condition_detailed_top = condition_detailed.iloc[0]
    condition_detailed_second = condition_detailed.iloc[1]
    condition_detailed_third = condition_detailed.iloc[2]
    condition_detailed_fourth = condition_detailed.iloc[3]
    condition_detailed_healthy = row_for(condition_detailed, "condition_family_label", "Healthy volunteers")
    condition_detailed_rate = condition_detailed.sort_values(["detailed_gap_rate", "detailed_gap_count"], ascending=[False, False])

    sponsor_asymmetry_top = sponsor_asymmetry.iloc[0]
    sponsor_asymmetry_second = sponsor_asymmetry.iloc[1]
    sponsor_asymmetry_third = sponsor_asymmetry.iloc[2]
    sponsor_asymmetry_fourth = sponsor_asymmetry.iloc[3]
    sponsor_asymmetry_rate = sponsor_asymmetry.sort_values(["text_asymmetry_rate", "text_asymmetry_net"], ascending=[False, False])

    country_asymmetry_top = country_asymmetry.iloc[0]
    country_asymmetry_second = country_asymmetry.iloc[1]
    country_asymmetry_third = country_asymmetry.iloc[2]
    country_asymmetry_fourth = country_asymmetry.iloc[3]
    country_asymmetry_rate = country_asymmetry.sort_values(["text_asymmetry_rate", "text_asymmetry_net"], ascending=[False, False])

    industry_detailed = row_for(detailed_class, "lead_sponsor_class", "INDUSTRY")
    industry_asymmetry = row_for(asymmetry_class, "lead_sponsor_class", "INDUSTRY")
    nih_asymmetry = row_for(asymmetry_class, "lead_sponsor_class", "NIH")

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
    ]

    series_links = parse_existing_series_links()
    series_links.extend(
        [
            {"repo_name": "ctgov-sponsor-detailed-description-gap", "title": "CT.gov Sponsor Detailed-Description Gap", "summary": "Named-sponsor tables showing where older CT.gov records most often omit the broad detailed-description field.", "short_title": "Sponsor Description", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-sponsor-detailed-description-gap/"},
            {"repo_name": "ctgov-country-detailed-description-gap", "title": "CT.gov Country Detailed-Description Gap", "summary": "Country-linked tables showing where older CT.gov records most often omit the detailed-description field.", "short_title": "Country Description", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-detailed-description-gap/"},
            {"repo_name": "ctgov-condition-detailed-description-gap", "title": "CT.gov Condition Detailed-Description Gap", "summary": "Condition-family tables showing where older CT.gov records most often omit the detailed-description field.", "short_title": "Condition Description", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-detailed-description-gap/"},
            {"repo_name": "ctgov-sponsor-text-asymmetry", "title": "CT.gov Sponsor Text Asymmetry", "summary": "Named-sponsor tables showing where detailed-description gaps greatly outnumber primary-outcome-only gaps.", "short_title": "Sponsor Asymmetry", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-sponsor-text-asymmetry/"},
            {"repo_name": "ctgov-country-text-asymmetry", "title": "CT.gov Country Text Asymmetry", "summary": "Country-linked tables showing where detailed-description gaps greatly outnumber primary-outcome-only gaps.", "short_title": "Country Asymmetry", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-text-asymmetry/"},
        ]
    )
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    projects: list[dict[str, object]] = []
    projects.append(
        detailed_gap_spec(
            repo_name="ctgov-sponsor-detailed-description-gap",
            title="CT.gov Sponsor Detailed-Description Gap",
            summary="A standalone E156 project on which named sponsors most often omit the broad detailed-description field from older CT.gov study records.",
            body_pairs=[
                ("Question", "Which named sponsors most often leave older CT.gov study pages without detailed descriptions, removing the broad paragraph that explains what was actually studied?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and ranked sponsors with at least 100 studies."),
                ("Method", "We defined a detailed-description gap as a missing detailed description field, then compared sponsor stock, rate, and class patterns."),
                ("Primary result", "GlaxoSmithKline led the sponsor detailed-description-gap stock table at 1,826 studies, followed by Boehringer Ingelheim at 1,600, Pfizer at 1,593, and Hoffmann-La Roche at 1,326."),
                ("Secondary result", "Novo Nordisk A/S had the highest large-sponsor detailed-description-gap rate at 97.4 percent, while Boehringer Ingelheim reached 96.0 percent and Industry reached 53.7 percent as a sponsor class."),
                ("Interpretation", "The detailed-description gap removes the larger narrative paragraph from mature registry pages, leaving readers with less context before asking about results."),
                ("Boundary", "These counts describe missing registry text fields and do not by themselves establish legal non-compliance, concealment, or absent materials."),
            ],
            protocol="This protocol isolates missing detailed-description fields inside named-sponsor CT.gov portfolios. A detailed-description gap is an eligible older closed interventional study missing the detailed description field. Primary outputs rank named sponsors with at least 100 studies by stock and rate and compare sponsor-class patterns.",
            label_col="lead_sponsor_name",
            df=sponsor_detailed,
            root_title="Which sponsors most often omit the detailed-description field?",
            root_eyebrow="Sponsor Detailed-Description-Gap Project",
            root_lede="A standalone public project on the broad narrative field, showing that GlaxoSmithKline, Boehringer Ingelheim, and Pfizer dominate on stock while Novo Nordisk is sharper on rate.",
            chapter_intro="This page isolates the largest text field on the CT.gov record: the detailed description. It asks which named sponsors most often leave that narrative paragraph blank in older closed study records.",
            root_pull_quote="If the detailed-description field is missing, the public loses the broadest plain-language narrative of what the study was about.",
            paper_pull_quote="Detailed-description gaps are wider than endpoint-text gaps because they remove the larger paragraph that frames the study for readers.",
            dashboard_pull_quote="GlaxoSmithKline leads sponsor detailed-description-gap stock, Boehringer Ingelheim and Pfizer follow, and Novo Nordisk is the sharpest large-sponsor rate outlier.",
            root_rail=["GSK 1,826", "Boehringer 1,600", "Pfizer 1,593", "Novo 97.4%"],
            landing_metrics=[
                ("GSK gap", fmt_int(as_int(sponsor_detailed_top["detailed_gap_count"])), "Detailed-gap studies"),
                ("Boehringer gap", fmt_int(as_int(sponsor_detailed_second["detailed_gap_count"])), "Detailed-gap studies"),
                ("Pfizer gap", fmt_int(as_int(sponsor_detailed_third["detailed_gap_count"])), "Detailed-gap studies"),
                ("Novo rate", fmt_pct(as_float(sponsor_detailed_rate.iloc[0]["detailed_gap_rate"])), "Large-sponsor rate"),
            ],
            reader_lede="A 156-word micro-paper on which named sponsors most often omit the broad detailed-description field from older CT.gov study records.",
            reader_rail=["GlaxoSmithKline", "Boehringer", "Pfizer", "Novo Nordisk"],
            reader_metrics=[
                ("GSK gap", fmt_int(as_int(sponsor_detailed_top["detailed_gap_count"])), "Detailed-gap studies"),
                ("Boehringer gap", fmt_int(as_int(sponsor_detailed_second["detailed_gap_count"])), "Detailed-gap studies"),
                ("Pfizer gap", fmt_int(as_int(sponsor_detailed_third["detailed_gap_count"])), "Detailed-gap studies"),
                ("Roche gap", fmt_int(as_int(sponsor_detailed_fourth["detailed_gap_count"])), "Detailed-gap studies"),
            ],
            dashboard_title="Sponsor detailed-description-gap tables show where older CT.gov pages lose the broad study narrative",
            dashboard_eyebrow="Sponsor Detailed-Description-Gap Dashboard",
            dashboard_lede="GlaxoSmithKline leads sponsor detailed-description-gap stock, Boehringer Ingelheim and Pfizer remain close behind, and Novo Nordisk plus Boehringer are extreme on rate while Industry dominates the class table.",
            dashboard_rail=["Description stock", "Rate", "Classes", "Narrative"],
            dashboard_metrics=[
                ("GSK gap", fmt_int(as_int(sponsor_detailed_top["detailed_gap_count"])), "Detailed-gap studies"),
                ("Boehringer gap", fmt_int(as_int(sponsor_detailed_second["detailed_gap_count"])), "Detailed-gap studies"),
                ("Novo rate", fmt_pct(as_float(sponsor_detailed_rate.iloc[0]["detailed_gap_rate"])), "Large-sponsor rate"),
                ("Industry rate", fmt_pct(as_float(industry_detailed["detailed_gap_rate"])), "Class rate"),
            ],
            dashboard_sections=[
                chart_section("Detailed-description-gap stock", bar_chart(items(sponsor_detailed, "lead_sponsor_name", "detailed_gap_count", label_fn=lambda value: short_sponsor(str(value))), "Detailed-gap stock", "Top sponsor counts missing detailed descriptions", "value", "label", "#c3452f", percent=False), "GlaxoSmithKline, Boehringer Ingelheim, Pfizer, and Roche dominate the stock table.", "Large mature sponsor portfolios therefore drive much of the missing broad narrative layer."),
                chart_section("Detailed-description-gap rate", bar_chart(rate_items(sponsor_detailed, "lead_sponsor_name", "detailed_gap_rate", label_fn=lambda value: short_sponsor(str(value))), "Detailed-gap rate", "Large-sponsor detailed-description-gap rate", "value", "label", "#326891", percent=True), "Novo Nordisk, Boehringer Ingelheim, Roche, and Mylan are the sharpest rate outliers.", "Stock and rate identify overlapping but not identical sponsor repeaters."),
                chart_section("Sponsor-class rate", bar_chart([{"label": row["lead_sponsor_class"], "value": as_float(row["detailed_gap_rate"])} for _, row in detailed_class[detailed_class["studies"] >= 100].sort_values(["detailed_gap_rate", "detailed_gap_count"], ascending=[False, False]).iterrows()], "Class rate", "Detailed-description-gap rate by sponsor class", "value", "label", "#8b6914", percent=True), "Industry stands far above the major non-industry classes on detailed-description rate.", "That class table shows the broad narrative field is especially thin in industry portfolios."),
            ],
            sidebar_bullets=[
                "GlaxoSmithKline leads sponsor detailed-description-gap stock at 1,826 studies.",
                "Boehringer Ingelheim is next at 1,600, with Pfizer at 1,593 and Roche at 1,326.",
                "Novo Nordisk A/S reaches a 97.4 percent detailed-description-gap rate among large sponsors.",
                "Industry reaches a 53.7 percent detailed-description-gap rate as a sponsor class.",
            ],
            references=common_refs,
            label_fn=lambda value: short_sponsor(str(value)),
        )
    )
    projects.append(
        detailed_gap_spec(
            repo_name="ctgov-country-detailed-description-gap",
            title="CT.gov Country Detailed-Description Gap",
            summary="A standalone E156 project on which country-linked portfolios most often omit the broad detailed-description field from older CT.gov records.",
            body_pairs=[
                ("Question", "Which country-linked CT.gov portfolios most often leave older study pages without detailed descriptions, removing the broad paragraph that explains what was studied?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded country links."),
                ("Method", "We defined a detailed-description gap as a missing detailed description field, then ranked country-linked portfolios with at least 500 linked studies by stock and rate."),
                ("Primary result", "The United States led the country-linked detailed-description-gap stock table at 32,378 studies, followed by France at 8,095, Germany at 7,976, and Canada at 6,834."),
                ("Secondary result", "Japan had the highest large-country detailed-description-gap rate at 63.3 percent, while Slovakia reached 58.1 percent and Romania 56.3 percent."),
                ("Interpretation", "Country-linked detailed-description gaps show where the broad registry narrative disappears most often even when the record still carries dates and status fields."),
                ("Boundary", "Country-linked rows are non-exclusive because multinational studies can contribute to more than one national portfolio in registry link tables. They describe registry link geography only."),
            ],
            protocol="This protocol isolates missing detailed-description fields inside country-linked CT.gov portfolios. A detailed-description gap is an eligible older closed interventional record missing the detailed description field. Primary outputs rank country-linked portfolios with at least 500 linked studies by stock and rate.",
            label_col="country_name",
            df=country_detailed,
            root_title="Which country-linked portfolios most often omit the detailed-description field?",
            root_eyebrow="Country Detailed-Description-Gap Project",
            root_lede="A standalone public project on country-linked broad narrative gaps, showing that the United States dominates on stock while Japan, Slovakia, and Romania are harsher on rate.",
            chapter_intro="This page moves the broad narrative field into geography and asks where country-linked CT.gov portfolios most often leave older study pages without the detailed-description paragraph.",
            root_pull_quote="The detailed-description field is the registry's largest narrative paragraph. When it disappears, readers lose context fast.",
            paper_pull_quote="Country-linked stock and rate split again here: the United States dominates on volume, while Japan, Slovakia, and Romania are harsher on detailed-description rate.",
            dashboard_pull_quote="The United States leads country-linked detailed-description-gap stock, France and Germany follow, and Japan is the sharpest large-country rate outlier.",
            root_rail=["US 32,378", "France 8,095", "Germany 7,976", "Japan 63.3%"],
            landing_metrics=[
                ("US gap", fmt_int(as_int(country_detailed_top["detailed_gap_count"])), "Detailed-gap studies"),
                ("France gap", fmt_int(as_int(country_detailed_second["detailed_gap_count"])), "Detailed-gap studies"),
                ("Germany gap", fmt_int(as_int(country_detailed_third["detailed_gap_count"])), "Detailed-gap studies"),
                ("Japan rate", fmt_pct(as_float(country_detailed_rate.iloc[0]["detailed_gap_rate"])), "Large-country rate"),
            ],
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios most often omit the broad detailed-description field from older study records.",
            reader_rail=["United States", "France", "Germany", "Japan"],
            reader_metrics=[
                ("US gap", fmt_int(as_int(country_detailed_top["detailed_gap_count"])), "Detailed-gap studies"),
                ("France gap", fmt_int(as_int(country_detailed_second["detailed_gap_count"])), "Detailed-gap studies"),
                ("Germany gap", fmt_int(as_int(country_detailed_third["detailed_gap_count"])), "Detailed-gap studies"),
                ("Canada gap", fmt_int(as_int(country_detailed_fourth["detailed_gap_count"])), "Detailed-gap studies"),
            ],
            dashboard_title="Country detailed-description-gap tables show where older CT.gov pages lose the broad study narrative",
            dashboard_eyebrow="Country Detailed-Description-Gap Dashboard",
            dashboard_lede="The United States dominates country-linked detailed-description-gap stock, France and Germany remain large on count, and Japan, Slovakia, and Romania are the clearest rate outliers.",
            dashboard_rail=["Description stock", "Rate", "Countries", "Narrative"],
            dashboard_metrics=[
                ("US gap", fmt_int(as_int(country_detailed_top["detailed_gap_count"])), "Detailed-gap studies"),
                ("France gap", fmt_int(as_int(country_detailed_second["detailed_gap_count"])), "Detailed-gap studies"),
                ("Japan rate", fmt_pct(as_float(country_detailed_rate.iloc[0]["detailed_gap_rate"])), "Large-country rate"),
                ("Slovakia rate", fmt_pct(as_float(country_detailed_rate.iloc[1]["detailed_gap_rate"])), "Large-country rate"),
            ],
            dashboard_sections=[
                chart_section("Detailed-description-gap stock", bar_chart(items(country_detailed, "country_name", "detailed_gap_count"), "Detailed-gap stock", "Top country-linked counts missing detailed descriptions", "value", "label", "#c3452f", percent=False), "The United States dominates on stock because scale is large, but France, Germany, Canada, and the United Kingdom also carry major broad-narrative gaps.", "Stock and rate need to be read together because national scale and severity diverge sharply."),
                chart_section("Detailed-description-gap rate", bar_chart(rate_items(country_detailed, "country_name", "detailed_gap_rate"), "Detailed-gap rate", "Large-country detailed-description-gap rate", "value", "label", "#326891", percent=True), "Japan is the sharpest large-country rate outlier, while Slovakia and Romania also remain very high.", "That rate pattern looks different from the stock table."),
                chart_section("Description-only stock", bar_chart(items(country_detailed.sort_values(["description_only_count", "detailed_gap_count"], ascending=[False, False]), "country_name", "description_only_count"), "Description-only stock", "Missing detailed description while endpoint text remains", "value", "label", "#8b6914", percent=False), "The description-only table shows how much of the broad narrative field disappears even when the endpoint sentence stays present.", "That is one reason detailed-description gaps deserve their own wave rather than being folded into endpoint gaps."),
            ],
            sidebar_bullets=[
                "The United States leads country-linked detailed-description-gap stock at 32,378 studies.",
                "France is next at 8,095, with Germany at 7,976 and Canada at 6,834.",
                "Japan reaches the highest large-country detailed-description-gap rate at 63.3 percent.",
                "Slovakia and Romania also stay high at 58.1 percent and 56.3 percent.",
            ],
            references=common_refs,
        )
    )
    projects.append(
        detailed_gap_spec(
            repo_name="ctgov-condition-detailed-description-gap",
            title="CT.gov Condition Detailed-Description Gap",
            summary="A standalone E156 project on which therapeutic portfolios most often omit the broad detailed-description field from older CT.gov records.",
            body_pairs=[
                ("Question", "Which condition families most often leave older CT.gov study pages without detailed descriptions, removing the broad narrative paragraph for readers?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
                ("Method", "We defined a detailed-description gap as a missing detailed description field, then ranked large condition families by stock and rate."),
                ("Primary result", "The broad OTHER bucket led the condition-family detailed-description-gap stock table at 18,641 studies, followed by Oncology at 12,321, Cardiovascular at 8,808, and Healthy volunteers at 7,082."),
                ("Secondary result", "Healthy volunteers had the highest large-family detailed-description-gap rate at 50.2 percent, ahead of Immunology and dermatology at 41.7 percent and Renal and urology at 38.3 percent."),
                ("Interpretation", "Condition-family detailed-description gaps show where the broad study narrative disappears most often in major therapeutic areas, not only fringe portfolios."),
                ("Boundary", "Condition families are keyword-derived registry groupings, not formal disease ontologies or mutually exclusive diagnoses across all studies. They simplify diagnoses into public buckets."),
            ],
            protocol="This protocol isolates missing detailed-description fields inside condition-family CT.gov portfolios. A detailed-description gap is an eligible older closed interventional record missing the detailed description field. Primary outputs rank large condition families by stock and rate using one condition-family label per study.",
            label_col="condition_family_label",
            df=condition_detailed,
            root_title="Which therapeutic portfolios most often omit the detailed-description field?",
            root_eyebrow="Condition Detailed-Description-Gap Project",
            root_lede="A standalone public project on therapeutic broad narrative gaps, showing that OTHER and Oncology dominate on stock while Healthy volunteers are much harsher on rate.",
            chapter_intro="This page asks which therapeutic portfolios most often leave older CT.gov records without the broad detailed-description paragraph once the field is moved from sponsors and countries into condition families.",
            root_pull_quote="The detailed-description field is the public study narrative. Losing it makes the record thinner even when many other fields remain present.",
            paper_pull_quote="OTHER and Oncology dominate condition-family stock, but Healthy volunteers are far harsher on detailed-description rate than the major named disease portfolios.",
            dashboard_pull_quote="OTHER leads condition-family detailed-description-gap stock, Oncology and Cardiovascular follow, and Healthy volunteers are the clearest large-family rate outlier.",
            root_rail=["Other 18,641", "Oncology 12,321", "Cardio 8,808", "Healthy 50.2%"],
            landing_metrics=[
                ("Other gap", fmt_int(as_int(condition_detailed_top["detailed_gap_count"])), "Detailed-gap studies"),
                ("Oncology gap", fmt_int(as_int(condition_detailed_second["detailed_gap_count"])), "Detailed-gap studies"),
                ("Cardio gap", fmt_int(as_int(condition_detailed_third["detailed_gap_count"])), "Detailed-gap studies"),
                ("Healthy rate", fmt_pct(as_float(condition_detailed_healthy["detailed_gap_rate"])), "Large-family rate"),
            ],
            reader_lede="A 156-word micro-paper on which therapeutic CT.gov portfolios most often omit the broad detailed-description field from older study records.",
            reader_rail=["Other", "Oncology", "Cardiovascular", "Healthy volunteers"],
            reader_metrics=[
                ("Other gap", fmt_int(as_int(condition_detailed_top["detailed_gap_count"])), "Detailed-gap studies"),
                ("Oncology gap", fmt_int(as_int(condition_detailed_second["detailed_gap_count"])), "Detailed-gap studies"),
                ("Cardio gap", fmt_int(as_int(condition_detailed_third["detailed_gap_count"])), "Detailed-gap studies"),
                ("Healthy gap", fmt_int(as_int(condition_detailed_fourth["detailed_gap_count"])), "Detailed-gap studies"),
            ],
            dashboard_title="Condition detailed-description-gap tables show where older CT.gov pages lose the broad study narrative",
            dashboard_eyebrow="Condition Detailed-Description-Gap Dashboard",
            dashboard_lede="OTHER and Oncology dominate condition-family detailed-description-gap stock, Cardiovascular remains large on count, and Healthy volunteers are far harsher on rate than the major named disease families.",
            dashboard_rail=["Description stock", "Rate", "Conditions", "Narrative"],
            dashboard_metrics=[
                ("Other gap", fmt_int(as_int(condition_detailed_top["detailed_gap_count"])), "Detailed-gap studies"),
                ("Oncology gap", fmt_int(as_int(condition_detailed_second["detailed_gap_count"])), "Detailed-gap studies"),
                ("Healthy rate", fmt_pct(as_float(condition_detailed_healthy["detailed_gap_rate"])), "Large-family rate"),
                ("Immunology rate", fmt_pct(as_float(condition_detailed_rate.iloc[1]["detailed_gap_rate"])), "Large-family rate"),
            ],
            dashboard_sections=[
                chart_section("Detailed-description-gap stock", bar_chart(items(condition_detailed, "condition_family_label", "detailed_gap_count"), "Detailed-gap stock", "Top condition-family counts missing detailed descriptions", "value", "label", "#c3452f", percent=False), "OTHER and Oncology dominate on count, while Cardiovascular and Healthy volunteers remain very large.", "The broad study narrative is therefore missing in major therapeutic portfolios, not only obscure ones."),
                chart_section("Detailed-description-gap rate", bar_chart(rate_items(condition_detailed, "condition_family_label", "detailed_gap_rate"), "Detailed-gap rate", "Large-family detailed-description-gap rate", "value", "label", "#326891", percent=True), "Healthy volunteers are the sharpest rate outlier, with immunology, renal, and respiratory portfolios also high.", "That rate pattern is harsher than the stock table alone suggests."),
                chart_section("Description-only stock", bar_chart(items(condition_detailed.sort_values(["description_only_count", "detailed_gap_count"], ascending=[False, False]), "condition_family_label", "description_only_count"), "Description-only stock", "Missing detailed description while endpoint text remains", "value", "label", "#8b6914", percent=False), "Description-only stock remains especially large in OTHER, Oncology, and Cardiovascular portfolios.", "That means the broad narrative often disappears even when the endpoint line is still present."),
            ],
            sidebar_bullets=[
                "OTHER leads condition-family detailed-description-gap stock at 18,641 studies.",
                "Oncology is next at 12,321, with Cardiovascular at 8,808 and Healthy volunteers at 7,082.",
                "Healthy volunteers reach the highest large-family detailed-description-gap rate at 50.2 percent.",
                "Immunology and dermatology and Renal and urology follow at 41.7 percent and 38.3 percent.",
            ],
            references=common_refs,
        )
    )
    projects.append(
        asymmetry_spec(
            repo_name="ctgov-sponsor-text-asymmetry",
            title="CT.gov Sponsor Text Asymmetry",
            summary="A standalone E156 project on which named sponsors show the biggest imbalance between missing broad study narratives and missing endpoint-only text.",
            body_pairs=[
                ("Question", "Which named sponsors show the biggest imbalance between missing detailed descriptions and missing primary-outcome-only text in older CT.gov records?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and ranked sponsors with at least 100 studies."),
                ("Method", "We compared description-only gaps against primary-only gaps and defined net text asymmetry as description-only minus primary-only counts."),
                ("Primary result", "Eli Lilly and Company led the sponsor text-asymmetry table at 1,021 net description-only gaps, followed by GlaxoSmithKline at 1,006, Pfizer at 948, and Boehringer Ingelheim at 841."),
                ("Secondary result", "Johnson and Johnson Vision Care had the highest large-sponsor asymmetry rate at 93.4 percentage points, while Industry reached 18,009 net description-only gaps and NIH flipped negative at minus 1,189."),
                ("Interpretation", "The asymmetry lens shows where the broad study narrative disappears much more often than the endpoint sentence, producing text-thin registry pages."),
                ("Boundary", "Positive asymmetry does not by itself prove concealment; it shows which field disappears more often inside public registry records overall."),
            ],
            protocol="This protocol isolates description-vs-endpoint text imbalance inside named-sponsor CT.gov portfolios. A description-only gap is a study missing the detailed description field while retaining the primary outcome description, and a primary-only gap is the reverse. Net text asymmetry is description-only minus primary-only counts and rates. Primary outputs rank named sponsors with at least 100 studies by net asymmetry and asymmetry rate.",
            label_col="lead_sponsor_name",
            df=sponsor_asymmetry,
            root_title="Which sponsors show the largest description-vs-endpoint text asymmetry?",
            root_eyebrow="Sponsor Text-Asymmetry Project",
            root_lede="A standalone public project on sponsor text imbalance, showing that Eli Lilly, GlaxoSmithKline, and Pfizer carry the biggest net description-only surpluses while Industry dominates the class table.",
            chapter_intro="This page is not about missing text in general. It asks where the broad study narrative disappears much more often than the shorter endpoint sentence on older CT.gov records.",
            root_pull_quote="A page can keep the endpoint sentence but still lose the larger study narrative. That imbalance is a different registry pattern from generic missingness.",
            paper_pull_quote="Text asymmetry separates broad-narrative loss from endpoint loss. It shows which portfolios are especially likely to keep the endpoint line while dropping the larger description field.",
            dashboard_pull_quote="Eli Lilly leads sponsor net text asymmetry, GlaxoSmithKline and Pfizer follow, Industry dominates the class table, and NIH flips negative because endpoint-only gaps exceed description-only gaps.",
            root_rail=["Lilly 1,021", "GSK 1,006", "Pfizer 948", "Industry 18,009"],
            landing_metrics=[
                ("Lilly net", fmt_int(as_int(sponsor_asymmetry_top["text_asymmetry_net"])), "Net asymmetry"),
                ("GSK net", fmt_int(as_int(sponsor_asymmetry_second["text_asymmetry_net"])), "Net asymmetry"),
                ("Pfizer net", fmt_int(as_int(sponsor_asymmetry_third["text_asymmetry_net"])), "Net asymmetry"),
                ("Industry net", fmt_int(as_int(industry_asymmetry["text_asymmetry_net"])), "Class net"),
            ],
            reader_lede="A 156-word micro-paper on which named sponsors show the largest imbalance between missing broad narratives and missing endpoint-only text in older CT.gov records.",
            reader_rail=["Eli Lilly", "GSK", "Pfizer", "Industry"],
            reader_metrics=[
                ("Lilly net", fmt_int(as_int(sponsor_asymmetry_top["text_asymmetry_net"])), "Net asymmetry"),
                ("GSK net", fmt_int(as_int(sponsor_asymmetry_second["text_asymmetry_net"])), "Net asymmetry"),
                ("Pfizer net", fmt_int(as_int(sponsor_asymmetry_third["text_asymmetry_net"])), "Net asymmetry"),
                ("Boehringer net", fmt_int(as_int(sponsor_asymmetry_fourth["text_asymmetry_net"])), "Net asymmetry"),
            ],
            dashboard_title="Sponsor text-asymmetry tables show where broad study narratives disappear much more often than endpoint text",
            dashboard_eyebrow="Sponsor Text-Asymmetry Dashboard",
            dashboard_lede="Eli Lilly leads sponsor net text asymmetry, GlaxoSmithKline and Pfizer remain close behind, Johnson and Johnson Vision Care is extreme on rate, and Industry strongly outweighs every other sponsor class.",
            dashboard_rail=["Net asymmetry", "Rate", "Classes", "Text balance"],
            dashboard_metrics=[
                ("Lilly net", fmt_int(as_int(sponsor_asymmetry_top["text_asymmetry_net"])), "Net asymmetry"),
                ("GSK net", fmt_int(as_int(sponsor_asymmetry_second["text_asymmetry_net"])), "Net asymmetry"),
                ("Top rate", fmt_pct(as_float(sponsor_asymmetry_rate.iloc[0]["text_asymmetry_rate"])), "Rate points"),
                ("Industry net", fmt_int(as_int(industry_asymmetry["text_asymmetry_net"])), "Class net"),
            ],
            sidebar_bullets=[
                "Eli Lilly and Company leads sponsor net text asymmetry at 1,021.",
                "GlaxoSmithKline and Pfizer follow at 1,006 and 948, with Boehringer Ingelheim at 841.",
                "Industry carries 18,009 net description-only gaps as a sponsor class.",
                "NIH flips negative at minus 1,189, meaning endpoint-only gaps exceed description-only gaps there.",
            ],
            references=common_refs,
            label_fn=lambda value: short_sponsor(str(value)),
        )
    )
    projects.append(
        asymmetry_spec(
            repo_name="ctgov-country-text-asymmetry",
            title="CT.gov Country Text Asymmetry",
            summary="A standalone E156 project on which country-linked portfolios show the biggest imbalance between missing broad study narratives and missing endpoint-only text.",
            body_pairs=[
                ("Question", "Which country-linked CT.gov portfolios show the biggest imbalance between missing detailed descriptions and missing primary-outcome-only text in older records?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded country links."),
                ("Method", "We compared description-only gaps against primary-only gaps and defined net text asymmetry as description-only minus primary-only counts and rates."),
                ("Primary result", "The United States led the country-linked text-asymmetry table at 9,667 net description-only gaps, followed by Germany at 3,909, Spain at 3,571, and France at 3,442."),
                ("Secondary result", "Slovakia had the highest large-country asymmetry rate at 40.9 percentage points, while Romania reached 39.3 points and Poland 36.6 points."),
                ("Interpretation", "Country-linked text asymmetry shows where the broad study narrative disappears much more often than the endpoint sentence across national registry portfolios. It separates portfolios where the larger study narrative disappears while the endpoint line survives."),
                ("Boundary", "Country-linked rows are non-exclusive because multinational studies can contribute to more than one national portfolio in registry link tables."),
            ],
            protocol="This protocol isolates description-vs-endpoint text imbalance inside country-linked CT.gov portfolios. A description-only gap is a study missing the detailed description field while retaining the primary outcome description, and a primary-only gap is the reverse. Net text asymmetry is description-only minus primary-only counts and rates. Primary outputs rank country-linked portfolios with at least 500 linked studies by net asymmetry and asymmetry rate.",
            label_col="country_name",
            df=country_asymmetry,
            root_title="Which country-linked portfolios show the largest description-vs-endpoint text asymmetry?",
            root_eyebrow="Country Text-Asymmetry Project",
            root_lede="A standalone public project on country-linked text imbalance, showing that the United States dominates on net asymmetry while Slovakia, Romania, and Poland are sharper on rate.",
            chapter_intro="This page asks where country-linked CT.gov portfolios most often keep the endpoint sentence but lose the broader study narrative, producing a distinctive imbalance between the two text fields.",
            root_pull_quote="Text asymmetry is not ordinary missingness. It asks which field disappears more often when the two descriptive layers split apart.",
            paper_pull_quote="Country-linked stock and rate diverge again here: the United States dominates on net count, while Slovakia, Romania, and Poland are harsher on asymmetry rate.",
            dashboard_pull_quote="The United States leads country-linked net text asymmetry, Germany and Spain follow, and Slovakia is the sharpest large-country rate outlier.",
            root_rail=["US 9,667", "Germany 3,909", "Spain 3,571", "Slovakia 40.9"],
            landing_metrics=[
                ("US net", fmt_int(as_int(country_asymmetry_top["text_asymmetry_net"])), "Net asymmetry"),
                ("Germany net", fmt_int(as_int(country_asymmetry_second["text_asymmetry_net"])), "Net asymmetry"),
                ("Spain net", fmt_int(as_int(country_asymmetry_third["text_asymmetry_net"])), "Net asymmetry"),
                ("Slovakia rate", fmt_pct(as_float(country_asymmetry_rate.iloc[0]["text_asymmetry_rate"])), "Rate points"),
            ],
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios show the largest imbalance between missing broad narratives and missing endpoint-only text.",
            reader_rail=["United States", "Germany", "Spain", "Slovakia"],
            reader_metrics=[
                ("US net", fmt_int(as_int(country_asymmetry_top["text_asymmetry_net"])), "Net asymmetry"),
                ("Germany net", fmt_int(as_int(country_asymmetry_second["text_asymmetry_net"])), "Net asymmetry"),
                ("Spain net", fmt_int(as_int(country_asymmetry_third["text_asymmetry_net"])), "Net asymmetry"),
                ("France net", fmt_int(as_int(country_asymmetry_fourth["text_asymmetry_net"])), "Net asymmetry"),
            ],
            dashboard_title="Country text-asymmetry tables show where broad study narratives disappear much more often than endpoint text",
            dashboard_eyebrow="Country Text-Asymmetry Dashboard",
            dashboard_lede="The United States dominates country-linked net text asymmetry, Germany and Spain remain large on count, and Slovakia, Romania, and Poland are the clearest large-country rate outliers.",
            dashboard_rail=["Net asymmetry", "Rate", "Countries", "Text balance"],
            dashboard_metrics=[
                ("US net", fmt_int(as_int(country_asymmetry_top["text_asymmetry_net"])), "Net asymmetry"),
                ("Germany net", fmt_int(as_int(country_asymmetry_second["text_asymmetry_net"])), "Net asymmetry"),
                ("Slovakia rate", fmt_pct(as_float(country_asymmetry_rate.iloc[0]["text_asymmetry_rate"])), "Rate points"),
                ("Romania rate", fmt_pct(as_float(country_asymmetry_rate.iloc[1]["text_asymmetry_rate"])), "Rate points"),
            ],
            sidebar_bullets=[
                "The United States leads country-linked net text asymmetry at 9,667.",
                "Germany is next at 3,909, with Spain at 3,571 and France at 3,442.",
                "Slovakia reaches the highest large-country asymmetry rate at 40.9 percentage points.",
                "Romania and Poland follow at 39.3 and 36.6 points.",
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
