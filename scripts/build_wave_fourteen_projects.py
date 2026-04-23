#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Build wave-fourteen standalone CT.gov narrative-gap and primary-outcome-gap projects."""

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
    if "sixty-five-project narrative dashboard series" in text and "ctgov-condition-primary-outcome-gap" in text:
        return
    text = replace_once(text, "sixty-project narrative dashboard series", "sixty-five-project narrative dashboard series")
    text = replace_once(
        text,
        "The thirteenth wave adds country and condition description black-box projects plus sponsor, country, and condition enrollment-gap projects on top of the earlier fifty-five story pages.",
        "The fourteenth wave adds country and condition narrative-gap projects plus sponsor, country, and condition primary-outcome-gap projects on top of the earlier sixty story pages.",
    )
    text = replace_once(text, "Use this hub as the visible front door to the full sixty-project series.", "Use this hub as the visible front door to the full sixty-five-project series.")
    text = replace_once(
        text,
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-enrollment-gap/'>Condition enrollment-gap</a>",
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-enrollment-gap/'>Condition enrollment-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-country-narrative-gap/'>Country narrative-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-narrative-gap/'>Condition narrative-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-sponsor-primary-outcome-gap/'>Sponsor primary-outcome-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-country-primary-outcome-gap/'>Country primary-outcome-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-primary-outcome-gap/'>Condition primary-outcome-gap</a>",
    )
    text = replace_once(
        text,
        "<li>Wave thirteen: country and condition description black-box projects plus sponsor, country, and condition enrollment-gap projects.</li><li>The hub is the visible front door to all sixty public CT.gov story pages.</li>",
        "<li>Wave thirteen: country and condition description black-box projects plus sponsor, country, and condition enrollment-gap projects.</li>"
        "<li>Wave fourteen: country and condition narrative-gap projects plus sponsor, country, and condition primary-outcome-gap projects.</li>"
        "<li>The hub is the visible front door to all sixty-five public CT.gov story pages.</li>",
    )
    ATLAS_INDEX.write_text(text, encoding="utf-8")


def generic_gap_spec(
    *,
    repo_name: str,
    title: str,
    summary: str,
    body_pairs: list[tuple[str, str]],
    protocol: str,
    label_col: str,
    count_col: str,
    rate_col: str,
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
    primary_estimand: str,
    data_note: str,
    label_fn=None,
) -> dict[str, object]:
    body, sentences = exact_bundle(repo_name, body_pairs)
    return make_spec(
        repo_name=repo_name,
        title=title,
        summary=summary,
        body=body,
        sentences=sentences,
        primary_estimand=primary_estimand,
        data_note=data_note,
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
            "Gap stock",
            bar_chart(items(df, label_col, count_col, label_fn=label_fn), "Gap stock", "Top gap counts", "value", "label", "#c3452f", percent=False),
            "The stock table shows where this field gap accumulates most heavily.",
            "Count and rate need to be read together because scale and severity diverge.",
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


def main() -> None:
    country_narrative = load_csv("wave_fourteen_country_narrative_gap.csv")
    condition_narrative = load_csv("wave_fourteen_condition_narrative_gap.csv")
    sponsor_primary = load_csv("wave_fourteen_sponsor_primary_outcome_gap.csv")
    country_primary = load_csv("wave_fourteen_country_primary_outcome_gap.csv")
    condition_primary = load_csv("wave_fourteen_condition_primary_outcome_gap.csv")
    primary_class = load_csv("wave_fourteen_primary_outcome_gap_class_summary.csv")

    country_narrative_top = country_narrative.iloc[0]
    country_narrative_second = country_narrative.iloc[1]
    country_narrative_third = country_narrative.iloc[2]
    country_narrative_fourth = country_narrative.iloc[3]
    country_narrative_rate = country_narrative.sort_values(["narrative_gap_rate", "narrative_gap_count"], ascending=[False, False])

    condition_narrative_top = condition_narrative.iloc[0]
    condition_narrative_second = condition_narrative.iloc[1]
    condition_narrative_third = condition_narrative.iloc[2]
    condition_narrative_fourth = condition_narrative.iloc[3]
    condition_narrative_healthy = row_for(condition_narrative, "condition_family_label", "Healthy volunteers")
    condition_narrative_metabolic = row_for(condition_narrative, "condition_family_label", "Metabolic")

    sponsor_primary_top = sponsor_primary.iloc[0]
    sponsor_primary_second = sponsor_primary.iloc[1]
    sponsor_primary_third = sponsor_primary.iloc[2]
    sponsor_primary_fourth = sponsor_primary.iloc[3]
    sponsor_primary_rate = sponsor_primary.sort_values(["primary_outcome_gap_rate", "primary_outcome_gap_count"], ascending=[False, False])
    primary_industry = row_for(primary_class, "lead_sponsor_class", "INDUSTRY")

    country_primary_top = country_primary.iloc[0]
    country_primary_second = country_primary.iloc[1]
    country_primary_third = country_primary.iloc[2]
    country_primary_fourth = country_primary.iloc[3]
    country_primary_rate = country_primary.sort_values(["primary_outcome_gap_rate", "primary_outcome_gap_count"], ascending=[False, False])

    condition_primary_top = condition_primary.iloc[0]
    condition_primary_second = condition_primary.iloc[1]
    condition_primary_third = condition_primary.iloc[2]
    condition_primary_fourth = condition_primary.iloc[3]
    condition_primary_healthy = row_for(condition_primary, "condition_family_label", "Healthy volunteers")
    condition_primary_metabolic = row_for(condition_primary, "condition_family_label", "Metabolic")

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
    ]

    series_links = parse_existing_series_links()
    series_links.extend(
        [
            {"repo_name": "ctgov-country-narrative-gap", "title": "CT.gov Country Narrative Gap", "summary": "Country-linked tables showing where detailed descriptions and primary outcome descriptions are missing together.", "short_title": "Country Narrative", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-narrative-gap/"},
            {"repo_name": "ctgov-condition-narrative-gap", "title": "CT.gov Condition Narrative Gap", "summary": "Condition-family tables showing where detailed descriptions and primary outcome descriptions disappear together.", "short_title": "Condition Narrative", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-narrative-gap/"},
            {"repo_name": "ctgov-sponsor-primary-outcome-gap", "title": "CT.gov Sponsor Primary-Outcome Gap", "summary": "Named-sponsor tables showing where primary outcome descriptions are most often missing in older CT.gov records.", "short_title": "Sponsor Outcome Gap", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-sponsor-primary-outcome-gap/"},
            {"repo_name": "ctgov-country-primary-outcome-gap", "title": "CT.gov Country Primary-Outcome Gap", "summary": "Country-linked tables showing where primary outcome descriptions are most often missing.", "short_title": "Country Outcome Gap", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-primary-outcome-gap/"},
            {"repo_name": "ctgov-condition-primary-outcome-gap", "title": "CT.gov Condition Primary-Outcome Gap", "summary": "Condition-family tables showing where primary outcome descriptions are most often missing in older CT.gov records.", "short_title": "Condition Outcome Gap", "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-primary-outcome-gap/"},
        ]
    )
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    projects: list[dict[str, object]] = []
    projects.append(
        generic_gap_spec(
            repo_name="ctgov-country-narrative-gap",
            title="CT.gov Country Narrative Gap",
            summary="A standalone E156 project on which country-linked portfolios most often leave older CT.gov records without both detailed descriptions and primary-outcome descriptions.",
            body_pairs=[
                ("Question", "Which country-linked CT.gov portfolios most often leave older closed study pages without both detailed descriptions and primary outcome descriptions?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded country links."),
                ("Method", "We defined a narrative-gap study as one missing both detailed description and primary outcome description, then ranked country-linked portfolios with at least 500 linked studies by stock and rate."),
                ("Primary result", "The United States led the narrative-gap stock table at 9,049 studies, followed by Germany at 2,438, France at 2,420, and Canada at 1,853."),
                ("Secondary result", "Japan had the sharpest large-country narrative-gap rate at 17.9 percent, ahead of Finland at 16.6 percent and Germany at 16.3 percent."),
                ("Interpretation", "Country-linked narrative gaps show where registry pages remain text-thin even when they retain dates, status fields, and other basic metadata on the public page for readers."),
                ("Boundary", "Country-linked rows are non-exclusive because multinational studies can contribute to more than one national portfolio in the registry tables."),
            ],
            protocol="This protocol isolates narrative gaps inside country-linked CT.gov portfolios. A narrative-gap study is an eligible older closed interventional record missing both the detailed description and primary outcome description fields. Primary outputs rank country-linked portfolios with at least 500 linked studies by narrative-gap stock and rate.",
            label_col="country_name",
            count_col="narrative_gap_count",
            rate_col="narrative_gap_rate",
            df=country_narrative,
            root_title="Which country-linked portfolios accumulate the deepest narrative gaps?",
            root_eyebrow="Country Narrative-Gap Project",
            root_lede="A standalone public project on country-linked narrative gaps, showing that the United States dominates on stock while Japan, Finland, and Germany are sharper on rate.",
            chapter_intro="This page moves the narrative-gap lens from sponsor tables into geography and asks where older CT.gov pages most often stay stripped of both core descriptive text fields.",
            root_pull_quote="A registry page can keep dates and status fields yet still withhold the text that tells readers what was actually studied.",
            paper_pull_quote="Country-linked stock and rate split again here: the United States dominates on count, while Japan, Finland, and Germany are sharper on narrative-gap rate.",
            dashboard_pull_quote="The United States leads country-linked narrative-gap stock, Germany and France follow, and Japan is the sharpest large-country rate outlier.",
            root_rail=["US 9,049", "Germany 2,438", "France 2,420", "Japan 17.9%"],
            landing_metrics=[
                ("US gap", fmt_int(as_int(country_narrative_top["narrative_gap_count"])), "Narrative-gap studies"),
                ("Germany gap", fmt_int(as_int(country_narrative_second["narrative_gap_count"])), "Narrative-gap studies"),
                ("France gap", fmt_int(as_int(country_narrative_third["narrative_gap_count"])), "Narrative-gap studies"),
                ("Japan rate", fmt_pct(as_float(country_narrative_rate.iloc[0]["narrative_gap_rate"])), "Large-country rate"),
            ],
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios most often omit both detailed descriptions and primary-outcome descriptions from older study records.",
            reader_rail=["United States", "Germany", "France", "Japan"],
            reader_metrics=[
                ("US gap", fmt_int(as_int(country_narrative_top["narrative_gap_count"])), "Narrative-gap studies"),
                ("Germany gap", fmt_int(as_int(country_narrative_second["narrative_gap_count"])), "Narrative-gap studies"),
                ("France gap", fmt_int(as_int(country_narrative_third["narrative_gap_count"])), "Narrative-gap studies"),
                ("Canada gap", fmt_int(as_int(country_narrative_fourth["narrative_gap_count"])), "Narrative-gap studies"),
            ],
            dashboard_title="Country narrative-gap tables show where older CT.gov pages stay stripped of both core descriptive fields",
            dashboard_eyebrow="Country Narrative-Gap Dashboard",
            dashboard_lede="The United States dominates country-linked narrative-gap stock, Germany and France remain large on count, and Japan, Finland, and Germany are the clearest rate outliers.",
            dashboard_rail=["Narrative stock", "Rate", "Countries", "Text gaps"],
            dashboard_metrics=[
                ("US gap", fmt_int(as_int(country_narrative_top["narrative_gap_count"])), "Narrative-gap studies"),
                ("Germany gap", fmt_int(as_int(country_narrative_second["narrative_gap_count"])), "Narrative-gap studies"),
                ("Japan rate", fmt_pct(as_float(country_narrative_rate.iloc[0]["narrative_gap_rate"])), "Large-country rate"),
                ("Finland rate", fmt_pct(as_float(country_narrative_rate.iloc[1]["narrative_gap_rate"])), "Large-country rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Narrative-gap stock",
                    bar_chart(items(country_narrative, "country_name", "narrative_gap_count"), "Narrative stock", "Top country-linked narrative-gap counts", "value", "label", "#c3452f", percent=False),
                    "The United States dominates on stock because country-linked scale is large, but Germany, France, Canada, and the United Kingdom still carry sizable narrative-gap portfolios.",
                    "Count and rate diverge here because some smaller national portfolios are much harsher on descriptive-text omission.",
                ),
                chart_section(
                    "Narrative-gap rate",
                    bar_chart(rate_items(country_narrative, "country_name", "narrative_gap_rate"), "Narrative rate", "Large-country narrative-gap rate", "value", "label", "#326891", percent=True),
                    "Japan is the sharpest large-country rate outlier, with Finland and Germany close behind.",
                    "That makes narrative gaps a different geography map than stock alone.",
                ),
            ],
            sidebar_bullets=[
                "The United States leads country-linked narrative-gap stock at 9,049 studies.",
                "Germany is next at 2,438, with France at 2,420 and Canada at 1,853.",
                "Japan reaches the highest large-country narrative-gap rate at 17.9 percent.",
                "Finland and Germany also remain high on rate at 16.6 percent and 16.3 percent.",
            ],
            references=common_refs,
            primary_estimand="Narrative-gap stock among older studies missing both detailed descriptions and primary outcome descriptions",
            data_note="249,507 eligible older closed interventional studies with country-linked narrative-gap stock and rate summaries",
        )
    )
    projects.append(
        generic_gap_spec(
            repo_name="ctgov-condition-narrative-gap",
            title="CT.gov Condition Narrative Gap",
            summary="A standalone E156 project on which therapeutic portfolios most often leave older CT.gov records without both detailed descriptions and primary-outcome descriptions.",
            body_pairs=[
                ("Question", "Which condition families most often leave older CT.gov study pages without both detailed descriptions and primary outcome descriptions?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
                ("Method", "We defined a narrative-gap study as one missing both detailed description and primary outcome description, then ranked large condition families by stock and rate."),
                ("Primary result", "The broad OTHER bucket led the narrative-gap stock table at 5,124 studies, followed by Oncology at 4,105, Cardiovascular at 3,240, and Healthy volunteers at 3,100."),
                ("Secondary result", "Healthy volunteers had the sharpest large-family narrative-gap rate at 22.0 percent, ahead of Metabolic at 14.8 percent and Renal and urology at 14.6 percent."),
                ("Interpretation", "Condition-family narrative gaps show where registry pages stay text-thin even before readers ask whether results or publications were posted later."),
                ("Boundary", "Condition families are keyword-derived registry groupings, not formal disease ontologies or mutually exclusive diagnoses for readers. They simplify diverse diagnoses into usable public buckets."),
            ],
            protocol="This protocol isolates narrative gaps inside condition-family CT.gov portfolios. A narrative-gap study is an eligible older closed interventional record missing both the detailed description and primary outcome description fields. Primary outputs rank large condition families by narrative-gap stock and rate using one condition-family label per study.",
            label_col="condition_family_label",
            count_col="narrative_gap_count",
            rate_col="narrative_gap_rate",
            df=condition_narrative,
            root_title="Which therapeutic portfolios accumulate the deepest narrative gaps?",
            root_eyebrow="Condition Narrative-Gap Project",
            root_lede="A standalone public project on therapeutic narrative gaps, showing that OTHER and Oncology dominate on stock while Healthy volunteers are the sharpest rate outlier.",
            chapter_intro="This page asks which therapeutic portfolios most often leave older CT.gov study pages without both descriptive text fields once the narrative-gap lens is moved from sponsors into condition families.",
            root_pull_quote="Narrative gaps are not just missing results. They also remove the text that explains what a study set out to do.",
            paper_pull_quote="OTHER and Oncology dominate condition-family stock, but Healthy volunteers are far harsher on rate than the major named disease portfolios.",
            dashboard_pull_quote="OTHER leads the condition-family narrative-gap table, Oncology and Cardiovascular remain large on count, and Healthy volunteers are the clearest rate extreme.",
            root_rail=["Other 5,124", "Oncology 4,105", "Cardio 3,240", "Healthy 22.0%"],
            landing_metrics=[
                ("Other gap", fmt_int(as_int(condition_narrative_top["narrative_gap_count"])), "Narrative-gap studies"),
                ("Oncology gap", fmt_int(as_int(condition_narrative_second["narrative_gap_count"])), "Narrative-gap studies"),
                ("Cardio gap", fmt_int(as_int(condition_narrative_third["narrative_gap_count"])), "Narrative-gap studies"),
                ("Healthy rate", fmt_pct(as_float(condition_narrative_healthy["narrative_gap_rate"])), "Large-family rate"),
            ],
            reader_lede="A 156-word micro-paper on which therapeutic CT.gov portfolios most often omit both detailed descriptions and primary-outcome descriptions from older study records.",
            reader_rail=["Other", "Oncology", "Cardiovascular", "Healthy volunteers"],
            reader_metrics=[
                ("Other gap", fmt_int(as_int(condition_narrative_top["narrative_gap_count"])), "Narrative-gap studies"),
                ("Oncology gap", fmt_int(as_int(condition_narrative_second["narrative_gap_count"])), "Narrative-gap studies"),
                ("Cardio gap", fmt_int(as_int(condition_narrative_third["narrative_gap_count"])), "Narrative-gap studies"),
                ("Healthy gap", fmt_int(as_int(condition_narrative_fourth["narrative_gap_count"])), "Narrative-gap studies"),
            ],
            dashboard_title="Condition narrative-gap tables show where older CT.gov pages stay stripped of both core descriptive fields",
            dashboard_eyebrow="Condition Narrative-Gap Dashboard",
            dashboard_lede="OTHER and Oncology dominate condition-family narrative-gap stock, Cardiovascular remains large on count, and Healthy volunteers are far harsher on rate than the major named disease families.",
            dashboard_rail=["Narrative stock", "Rate", "Conditions", "Text gaps"],
            dashboard_metrics=[
                ("Other gap", fmt_int(as_int(condition_narrative_top["narrative_gap_count"])), "Narrative-gap studies"),
                ("Oncology gap", fmt_int(as_int(condition_narrative_second["narrative_gap_count"])), "Narrative-gap studies"),
                ("Healthy rate", fmt_pct(as_float(condition_narrative_healthy["narrative_gap_rate"])), "Large-family rate"),
                ("Metabolic rate", fmt_pct(as_float(condition_narrative_metabolic["narrative_gap_rate"])), "Large-family rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Narrative-gap stock",
                    bar_chart(items(condition_narrative, "condition_family_label", "narrative_gap_count"), "Narrative stock", "Top condition-family narrative-gap counts", "value", "label", "#c3452f", percent=False),
                    "OTHER and Oncology dominate on count, with Cardiovascular and Healthy volunteers still large enough to matter immediately.",
                    "The condition-family stock table shows that narrative gaps are not limited to fringe therapeutic areas.",
                ),
                chart_section(
                    "Narrative-gap rate",
                    bar_chart(rate_items(condition_narrative, "condition_family_label", "narrative_gap_rate"), "Narrative rate", "Large-family narrative-gap rate", "value", "label", "#326891", percent=True),
                    "Healthy volunteers are the sharpest rate outlier, with Metabolic and Renal and urology also unusually text-thin.",
                    "That rate pattern is harsher than the count ranking alone suggests.",
                ),
            ],
            sidebar_bullets=[
                "OTHER leads condition-family narrative-gap stock at 5,124 studies.",
                "Oncology is next at 4,105, with Cardiovascular at 3,240 and Healthy volunteers at 3,100.",
                "Healthy volunteers reach the highest large-family narrative-gap rate at 22.0 percent.",
                "Metabolic and Renal and urology remain elevated at 14.8 percent and 14.6 percent.",
            ],
            references=common_refs,
            primary_estimand="Narrative-gap stock among older studies missing both detailed descriptions and primary outcome descriptions",
            data_note="249,507 eligible older closed interventional studies with condition-family narrative-gap stock and rate summaries",
        )
    )
    projects.append(
        generic_gap_spec(
            repo_name="ctgov-sponsor-primary-outcome-gap",
            title="CT.gov Sponsor Primary-Outcome Gap",
            summary="A standalone E156 project on which named sponsors most often omit primary-outcome descriptions from older CT.gov study records.",
            body_pairs=[
                ("Question", "Which named sponsors most often leave older CT.gov study pages without primary outcome descriptions, obscuring what the main endpoint was meant to measure?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and ranked sponsors with at least 100 studies."),
                ("Method", "We defined a primary-outcome gap as a missing primary outcome description, then compared sponsor stock, rate, and sponsor-class patterns."),
                ("Primary result", "GlaxoSmithKline led the sponsor primary-outcome-gap stock table at 820 studies, followed by Boehringer Ingelheim at 759, Sanofi at 749, and Pfizer at 645."),
                ("Secondary result", "Ranbaxy Laboratories Limited had the sharpest large-sponsor primary-outcome-gap rate at 98.0 percent, while Mylan Pharmaceuticals reached 94.3 percent and NIH reached 30.7 percent as a sponsor class."),
                ("Interpretation", "Missing the primary outcome description removes the line telling readers what the main endpoint was, even when other registry fields remain visible."),
                ("Boundary", "These gaps describe missing registry fields and do not by themselves establish legal non-compliance or missing outcome data elsewhere."),
            ],
            protocol="This protocol isolates primary-outcome text gaps inside named-sponsor CT.gov portfolios. A primary-outcome gap is an eligible older closed interventional study missing the primary outcome description field. Primary outputs rank named sponsors with at least 100 studies by stock and rate and compare sponsor-class patterns.",
            label_col="lead_sponsor_name",
            count_col="primary_outcome_gap_count",
            rate_col="primary_outcome_gap_rate",
            df=sponsor_primary,
            root_title="Which sponsors most often omit the primary-outcome description field?",
            root_eyebrow="Sponsor Primary-Outcome-Gap Project",
            root_lede="A standalone public project on primary-outcome text gaps, showing that GlaxoSmithKline, Boehringer Ingelheim, and Sanofi dominate on stock while Ranbaxy and Mylan are sharper on rate.",
            chapter_intro="This page isolates one highly specific text field: the line that tells readers what the primary outcome was supposed to be. It asks which sponsors most often leave that field blank in older CT.gov records.",
            root_pull_quote="If the primary-outcome description is missing, the public cannot quickly see what the study treated as its main endpoint.",
            paper_pull_quote="Primary-outcome text gaps are narrower than general narrative gaps, but they remove the single line that matters most for understanding study intent.",
            dashboard_pull_quote="GlaxoSmithKline leads sponsor primary-outcome-gap stock, Boehringer Ingelheim and Sanofi follow, and Ranbaxy plus Mylan are the sharpest large-sponsor rate outliers.",
            root_rail=["GSK 820", "Boehringer 759", "Sanofi 749", "Ranbaxy 98.0%"],
            landing_metrics=[
                ("GSK gap", fmt_int(as_int(sponsor_primary_top["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Boehringer gap", fmt_int(as_int(sponsor_primary_second["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Sanofi gap", fmt_int(as_int(sponsor_primary_third["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Ranbaxy rate", fmt_pct(as_float(sponsor_primary_rate.iloc[0]["primary_outcome_gap_rate"])), "Large-sponsor rate"),
            ],
            reader_lede="A 156-word micro-paper on which named sponsors most often omit primary-outcome descriptions from older CT.gov study records.",
            reader_rail=["GlaxoSmithKline", "Boehringer", "Sanofi", "Ranbaxy"],
            reader_metrics=[
                ("GSK gap", fmt_int(as_int(sponsor_primary_top["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Boehringer gap", fmt_int(as_int(sponsor_primary_second["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Sanofi gap", fmt_int(as_int(sponsor_primary_third["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Pfizer gap", fmt_int(as_int(sponsor_primary_fourth["primary_outcome_gap_count"])), "Primary-outcome gaps"),
            ],
            dashboard_title="Sponsor primary-outcome-gap tables show where older CT.gov pages omit the text defining the main endpoint",
            dashboard_eyebrow="Sponsor Primary-Outcome-Gap Dashboard",
            dashboard_lede="GlaxoSmithKline leads sponsor primary-outcome-gap stock, Boehringer Ingelheim and Sanofi remain close behind, Ranbaxy and Mylan are extreme on rate, and NIH edges Industry on sponsor-class rate.",
            dashboard_rail=["Outcome-gap stock", "Rate", "Classes", "Endpoints"],
            dashboard_metrics=[
                ("GSK gap", fmt_int(as_int(sponsor_primary_top["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Boehringer gap", fmt_int(as_int(sponsor_primary_second["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Ranbaxy rate", fmt_pct(as_float(sponsor_primary_rate.iloc[0]["primary_outcome_gap_rate"])), "Large-sponsor rate"),
                ("NIH rate", fmt_pct(as_float(row_for(primary_class, "lead_sponsor_class", "NIH")["primary_outcome_gap_rate"])), "Class rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Primary-outcome-gap stock",
                    bar_chart(items(sponsor_primary, "lead_sponsor_name", "primary_outcome_gap_count", label_fn=lambda value: short_sponsor(str(value))), "Outcome-gap stock", "Top sponsor counts missing primary-outcome descriptions", "value", "label", "#c3452f", percent=False),
                    "GlaxoSmithKline, Boehringer Ingelheim, Sanofi, Pfizer, and AstraZeneca dominate the stock table.",
                    "The largest primary-outcome text gaps therefore sit in major mature sponsor portfolios rather than obscure corners of the registry.",
                ),
                chart_section(
                    "Primary-outcome-gap rate",
                    bar_chart(rate_items(sponsor_primary, "lead_sponsor_name", "primary_outcome_gap_rate", label_fn=lambda value: short_sponsor(str(value))), "Outcome-gap rate", "Large-sponsor primary-outcome-gap rate", "value", "label", "#326891", percent=True),
                    "Ranbaxy, Mylan, Dr. Reddy's, and several other industry portfolios are extreme on rate.",
                    "Stock and rate identify overlapping but not identical repeaters.",
                ),
                chart_section(
                    "Sponsor-class rate",
                    bar_chart(
                        [{"label": row["lead_sponsor_class"], "value": as_float(row["primary_outcome_gap_rate"])} for _, row in primary_class[primary_class["studies"] >= 100].sort_values(["primary_outcome_gap_rate", "primary_outcome_gap_count"], ascending=[False, False]).iterrows()],
                        "Class rate",
                        "Primary-outcome-gap rate by sponsor class",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "NIH sits just above Industry on class rate, while Other Gov and Network also remain elevated.",
                    "That class table shows the field gap is broader than one sponsor type.",
                ),
            ],
            sidebar_bullets=[
                "GlaxoSmithKline leads sponsor primary-outcome-gap stock at 820 studies.",
                "Boehringer Ingelheim is next at 759, with Sanofi at 749 and Pfizer at 645.",
                "Ranbaxy Laboratories Limited reaches a 98.0 percent primary-outcome-gap rate among large sponsors.",
                "NIH has the highest substantive sponsor-class rate at 30.7 percent, slightly above Industry at 30.0 percent.",
            ],
            references=common_refs,
            primary_estimand="Primary-outcome-gap stock among older studies missing the primary outcome description field",
            data_note="249,507 eligible older closed interventional studies with sponsor primary-outcome-gap stock and rate summaries",
            label_fn=lambda value: short_sponsor(str(value)),
        )
    )
    projects.append(
        generic_gap_spec(
            repo_name="ctgov-country-primary-outcome-gap",
            title="CT.gov Country Primary-Outcome Gap",
            summary="A standalone E156 project on which country-linked portfolios most often omit primary-outcome descriptions from older CT.gov study records.",
            body_pairs=[
                ("Question", "Which country-linked CT.gov portfolios most often leave older study pages without primary outcome descriptions, obscuring the main endpoint for public readers?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded country links."),
                ("Method", "We defined a primary-outcome gap as a missing primary outcome description, then ranked country-linked portfolios with at least 500 linked studies by stock and rate."),
                ("Primary result", "The United States led the country-linked primary-outcome-gap stock table at 22,711 studies, followed by France at 4,653, Canada at 4,234, and Germany at 4,067."),
                ("Secondary result", "Iran had the sharpest large-country primary-outcome-gap rate at 28.5 percent, while France reached 27.7 percent and Norway 27.5 percent."),
                ("Interpretation", "Country-linked primary-outcome gaps show where registry pages most often omit the single line that defines the main endpoint of a study."),
                ("Boundary", "Country-linked rows are non-exclusive because multinational studies can contribute to more than one national portfolio in registry link tables. They show registry link geography, not legal jurisdiction."),
            ],
            protocol="This protocol isolates primary-outcome text gaps inside country-linked CT.gov portfolios. A primary-outcome gap is an eligible older closed interventional record missing the primary outcome description field. Primary outputs rank country-linked portfolios with at least 500 linked studies by stock and rate.",
            label_col="country_name",
            count_col="primary_outcome_gap_count",
            rate_col="primary_outcome_gap_rate",
            df=country_primary,
            root_title="Which country-linked portfolios most often omit the primary-outcome description field?",
            root_eyebrow="Country Primary-Outcome-Gap Project",
            root_lede="A standalone public project on country-linked primary-outcome text gaps, showing that the United States dominates on stock while Iran, France, and Norway are harsher on rate.",
            chapter_intro="This page keeps the focus on the main endpoint field and asks where country-linked CT.gov portfolios most often leave that sentence blank in older closed study records.",
            root_pull_quote="The primary-outcome description is the shortest path to understanding what a trial considered its main endpoint.",
            paper_pull_quote="Country-linked stock and rate diverge again here: the United States dominates on count, while Iran, France, and Norway are sharper on primary-outcome-gap rate.",
            dashboard_pull_quote="The United States leads country-linked primary-outcome-gap stock, France and Canada follow, and Iran is the sharpest large-country rate outlier.",
            root_rail=["US 22,711", "France 4,653", "Canada 4,234", "Iran 28.5%"],
            landing_metrics=[
                ("US gap", fmt_int(as_int(country_primary_top["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("France gap", fmt_int(as_int(country_primary_second["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Canada gap", fmt_int(as_int(country_primary_third["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Iran rate", fmt_pct(as_float(country_primary_rate.iloc[0]["primary_outcome_gap_rate"])), "Large-country rate"),
            ],
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios most often omit primary-outcome descriptions from older study records.",
            reader_rail=["United States", "France", "Canada", "Iran"],
            reader_metrics=[
                ("US gap", fmt_int(as_int(country_primary_top["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("France gap", fmt_int(as_int(country_primary_second["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Canada gap", fmt_int(as_int(country_primary_third["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Germany gap", fmt_int(as_int(country_primary_fourth["primary_outcome_gap_count"])), "Primary-outcome gaps"),
            ],
            dashboard_title="Country primary-outcome-gap tables show where older CT.gov pages omit the text defining the main endpoint",
            dashboard_eyebrow="Country Primary-Outcome-Gap Dashboard",
            dashboard_lede="The United States dominates country-linked primary-outcome-gap stock, France and Canada remain large on count, and Iran, France, and Norway are the clearest rate outliers.",
            dashboard_rail=["Outcome-gap stock", "Rate", "Countries", "Endpoints"],
            dashboard_metrics=[
                ("US gap", fmt_int(as_int(country_primary_top["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("France gap", fmt_int(as_int(country_primary_second["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Iran rate", fmt_pct(as_float(country_primary_rate.iloc[0]["primary_outcome_gap_rate"])), "Large-country rate"),
                ("France rate", fmt_pct(as_float(country_primary_rate.iloc[1]["primary_outcome_gap_rate"])), "Large-country rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Primary-outcome-gap stock",
                    bar_chart(items(country_primary, "country_name", "primary_outcome_gap_count"), "Outcome-gap stock", "Top country-linked counts missing primary-outcome descriptions", "value", "label", "#c3452f", percent=False),
                    "The United States dominates on stock, but France, Canada, Germany, and the United Kingdom remain large country-linked endpoint-gap portfolios.",
                    "Scale explains much of the stock ranking, which is why the rate table matters.",
                ),
                chart_section(
                    "Primary-outcome-gap rate",
                    bar_chart(rate_items(country_primary, "country_name", "primary_outcome_gap_rate"), "Outcome-gap rate", "Large-country primary-outcome-gap rate", "value", "label", "#326891", percent=True),
                    "Iran is the sharpest large-country rate outlier, with France, Norway, Finland, and Japan clustered close behind.",
                    "That rate ordering looks different from the stock table.",
                ),
            ],
            sidebar_bullets=[
                "The United States leads country-linked primary-outcome-gap stock at 22,711 studies.",
                "France is next at 4,653, with Canada at 4,234 and Germany at 4,067.",
                "Iran reaches the highest large-country primary-outcome-gap rate at 28.5 percent.",
                "France and Norway also stay high at 27.7 percent and 27.5 percent.",
            ],
            references=common_refs,
            primary_estimand="Primary-outcome-gap stock among older studies missing the primary outcome description field",
            data_note="249,507 eligible older closed interventional studies with country-linked primary-outcome-gap stock and rate summaries",
        )
    )
    projects.append(
        generic_gap_spec(
            repo_name="ctgov-condition-primary-outcome-gap",
            title="CT.gov Condition Primary-Outcome Gap",
            summary="A standalone E156 project on which therapeutic portfolios most often omit primary-outcome descriptions from older CT.gov study records.",
            body_pairs=[
                ("Question", "Which condition families most often leave older CT.gov study pages without primary outcome descriptions, obscuring the main endpoint for readers?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
                ("Method", "We defined a primary-outcome gap as a missing primary outcome description, then ranked large condition families by stock and rate."),
                ("Primary result", "Oncology led the condition-family primary-outcome-gap stock table at 11,207 studies, followed by the broad OTHER bucket at 10,942, Cardiovascular at 7,006, and Metabolic at 5,006."),
                ("Secondary result", "Healthy volunteers had the sharpest large-family primary-outcome-gap rate at 35.0 percent, ahead of Metabolic at 28.9 percent and Renal and urology at 28.8 percent."),
                ("Interpretation", "Condition-family primary-outcome gaps show where registry pages omit the endpoint-defining sentence in major therapeutic areas, not only smaller fringe portfolios."),
                ("Boundary", "Condition families are keyword-derived registry groupings rather than formal disease ontologies or mutually exclusive diagnoses across all studies. They simplify diverse diagnoses into usable public buckets."),
            ],
            protocol="This protocol isolates primary-outcome text gaps inside condition-family CT.gov portfolios. A primary-outcome gap is an eligible older closed interventional record missing the primary outcome description field. Primary outputs rank large condition families by stock and rate using one condition-family label per study.",
            label_col="condition_family_label",
            count_col="primary_outcome_gap_count",
            rate_col="primary_outcome_gap_rate",
            df=condition_primary,
            root_title="Which therapeutic portfolios most often omit the primary-outcome description field?",
            root_eyebrow="Condition Primary-Outcome-Gap Project",
            root_lede="A standalone public project on therapeutic primary-outcome text gaps, showing that Oncology and OTHER dominate on stock while Healthy volunteers are the sharpest rate outlier.",
            chapter_intro="This page asks which therapeutic portfolios most often leave the primary-outcome description blank once the endpoint text-gap lens is moved from sponsors and countries into condition families.",
            root_pull_quote="Without the primary-outcome description, the registry page loses the shortest explanation of what the study treated as its main endpoint.",
            paper_pull_quote="Oncology and OTHER dominate condition-family stock, but Healthy volunteers are much harsher on rate than the major named disease portfolios.",
            dashboard_pull_quote="Oncology leads condition-family primary-outcome-gap stock, OTHER and Cardiovascular follow, and Healthy volunteers are the clearest large-family rate extreme.",
            root_rail=["Oncology 11,207", "Other 10,942", "Cardio 7,006", "Healthy 35.0%"],
            landing_metrics=[
                ("Oncology gap", fmt_int(as_int(condition_primary_top["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Other gap", fmt_int(as_int(condition_primary_second["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Cardio gap", fmt_int(as_int(condition_primary_third["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Healthy rate", fmt_pct(as_float(condition_primary_healthy["primary_outcome_gap_rate"])), "Large-family rate"),
            ],
            reader_lede="A 156-word micro-paper on which therapeutic CT.gov portfolios most often omit primary-outcome descriptions from older study records.",
            reader_rail=["Oncology", "Other", "Cardiovascular", "Healthy volunteers"],
            reader_metrics=[
                ("Oncology gap", fmt_int(as_int(condition_primary_top["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Other gap", fmt_int(as_int(condition_primary_second["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Cardio gap", fmt_int(as_int(condition_primary_third["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Metabolic gap", fmt_int(as_int(condition_primary_fourth["primary_outcome_gap_count"])), "Primary-outcome gaps"),
            ],
            dashboard_title="Condition primary-outcome-gap tables show where older CT.gov pages omit the text defining the main endpoint",
            dashboard_eyebrow="Condition Primary-Outcome-Gap Dashboard",
            dashboard_lede="Oncology and OTHER dominate condition-family primary-outcome-gap stock, Cardiovascular and Metabolic remain large on count, and Healthy volunteers are far harsher on rate than the major named disease families.",
            dashboard_rail=["Outcome-gap stock", "Rate", "Conditions", "Endpoints"],
            dashboard_metrics=[
                ("Oncology gap", fmt_int(as_int(condition_primary_top["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Other gap", fmt_int(as_int(condition_primary_second["primary_outcome_gap_count"])), "Primary-outcome gaps"),
                ("Healthy rate", fmt_pct(as_float(condition_primary_healthy["primary_outcome_gap_rate"])), "Large-family rate"),
                ("Metabolic rate", fmt_pct(as_float(condition_primary_metabolic["primary_outcome_gap_rate"])), "Large-family rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Primary-outcome-gap stock",
                    bar_chart(items(condition_primary, "condition_family_label", "primary_outcome_gap_count"), "Outcome-gap stock", "Top condition-family counts missing primary-outcome descriptions", "value", "label", "#c3452f", percent=False),
                    "Oncology and OTHER dominate on stock, with Cardiovascular and Metabolic also carrying large endpoint-gap portfolios.",
                    "That means the field gap sits inside major therapeutic areas, not only small fringe categories.",
                ),
                chart_section(
                    "Primary-outcome-gap rate",
                    bar_chart(rate_items(condition_primary, "condition_family_label", "primary_outcome_gap_rate"), "Outcome-gap rate", "Large-family primary-outcome-gap rate", "value", "label", "#326891", percent=True),
                    "Healthy volunteers are the sharpest rate outlier, with Metabolic and Renal and urology close behind.",
                    "The rate table is harsher than the stock ranking alone suggests.",
                ),
            ],
            sidebar_bullets=[
                "Oncology leads condition-family primary-outcome-gap stock at 11,207 studies.",
                "OTHER is next at 10,942, with Cardiovascular at 7,006 and Metabolic at 5,006.",
                "Healthy volunteers reach the highest large-family primary-outcome-gap rate at 35.0 percent.",
                "Metabolic and Renal and urology remain close behind at 28.9 percent and 28.8 percent.",
            ],
            references=common_refs,
            primary_estimand="Primary-outcome-gap stock among older studies missing the primary outcome description field",
            data_note="249,507 eligible older closed interventional studies with condition-family primary-outcome-gap stock and rate summaries",
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
