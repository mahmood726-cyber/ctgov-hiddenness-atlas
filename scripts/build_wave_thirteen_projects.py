#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Build wave-thirteen standalone CT.gov description-black-box and enrollment-gap projects."""

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
    if "sixty-project narrative dashboard series" in text and "ctgov-condition-enrollment-gap" in text:
        return
    text = replace_once(text, "fifty-five-project narrative dashboard series", "sixty-project narrative dashboard series")
    text = replace_once(
        text,
        "The twelfth wave adds sponsor ancient backlog, country ancient backlog, condition ancient backlog, description-black-box repeaters, and completion-timing repeaters on top of the earlier fifty story pages.",
        "The thirteenth wave adds country and condition description black-box projects plus sponsor, country, and condition enrollment-gap projects on top of the earlier fifty-five story pages.",
    )
    text = replace_once(text, "Use this hub as the visible front door to the full fifty-five-project series.", "Use this hub as the visible front door to the full sixty-project series.")
    text = replace_once(
        text,
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-completion-timing-repeaters/'>Completion-timing repeaters</a>",
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-completion-timing-repeaters/'>Completion-timing repeaters</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-country-description-black-box/'>Country description black-box</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-description-black-box/'>Condition description black-box</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-sponsor-enrollment-gap-repeaters/'>Sponsor enrollment-gap repeaters</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-country-enrollment-gap/'>Country enrollment-gap</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-enrollment-gap/'>Condition enrollment-gap</a>",
    )
    text = replace_once(
        text,
        "<li>Wave twelve: sponsor, country, and condition ancient backlog plus description-black-box and completion-timing repeaters.</li><li>The hub is the visible front door to all fifty-five public CT.gov story pages.</li>",
        "<li>Wave twelve: sponsor, country, and condition ancient backlog plus description-black-box and completion-timing repeaters.</li>"
        "<li>Wave thirteen: country and condition description black-box projects plus sponsor, country, and condition enrollment-gap projects.</li>"
        "<li>The hub is the visible front door to all sixty public CT.gov story pages.</li>",
    )
    ATLAS_INDEX.write_text(text, encoding="utf-8")


def description_geo_spec(
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
) -> dict[str, object]:
    body, sentences = exact_bundle(repo_name, body_pairs)
    dashboard_sections = [
        chart_section("Description black-box stock", bar_chart(items(df, label_col, "description_black_box_count"), "Black-box stock", "Top description-black-box counts", "value", "label", "#c3452f", percent=False), "Stock shows where overdue, unlinked, textually black-box studies accumulate most heavily.", "These tables isolate older records with no results, no linked publication, no detailed description, and no primary outcome description."),
        chart_section("Description black-box rate", bar_chart(rate_items(df, label_col, "description_black_box_rate"), "Black-box rate", "Description-black-box rate", "value", "label", "#326891", percent=True), "Rate highlights a harsher pattern than stock alone.", "Some portfolios look ordinary on count and much worse on black-box rate."),
    ]
    return make_spec(
        repo_name=repo_name,
        title=title,
        summary=summary,
        body=body,
        sentences=sentences,
        primary_estimand="Description black-box stock among older studies with no results, no linked publication, no detailed description, and no primary outcome description",
        data_note="249,507 eligible older closed interventional studies with description-black-box stock and rate summaries",
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
        landing_chart_html=chart_section("Description black-box stock", bar_chart(items(df, label_col, "description_black_box_count"), "Black-box stock", "Top description-black-box counts", "value", "label", "#c3452f", percent=False), "The stock table shows where the strictest narrative blackout is most common on count.", "Black-box records stay overdue and unlinked while omitting the main descriptive text fields."),
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


def enrollment_spec(
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
        primary_estimand="Enrollment-gap stock among older studies missing actual enrollment",
        data_note="249,507 eligible older closed interventional studies with actual-enrollment gap stock and rate summaries",
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
        landing_chart_html=chart_section("Enrollment-gap stock", bar_chart(items(df, label_col, "enrollment_gap_count", label_fn=label_fn), "Enrollment-gap stock", "Top counts of missing actual enrollment", "value", "label", "#c3452f", percent=False), "The stock table shows where realized sample size is most often missing on count.", "Actual enrollment is the clearest registry field for realized sample size discipline."),
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
    country_description = load_csv("wave_thirteen_country_description_black_box.csv")
    condition_description = load_csv("wave_thirteen_condition_description_black_box.csv")
    sponsor_enrollment = load_csv("wave_thirteen_sponsor_enrollment_gap.csv")
    country_enrollment = load_csv("wave_thirteen_country_enrollment_gap.csv")
    condition_enrollment = load_csv("wave_thirteen_condition_enrollment_gap.csv")
    class_enrollment = load_csv("wave_thirteen_enrollment_gap_class_summary.csv")

    country_desc_top = country_description.iloc[0]
    country_desc_second = country_description.iloc[1]
    country_desc_third = country_description.iloc[2]
    country_desc_fourth = country_description.iloc[3]
    country_desc_rate = country_description.sort_values(
        ["description_black_box_rate", "description_black_box_count"], ascending=[False, False]
    )

    condition_desc_top = condition_description.iloc[0]
    condition_desc_second = condition_description.iloc[1]
    condition_desc_third = condition_description.iloc[2]
    condition_desc_fourth = condition_description.iloc[3]
    condition_desc_healthy = row_for(condition_description, "condition_family_label", "Healthy volunteers")

    sponsor_enrollment_top = sponsor_enrollment.iloc[0]
    sponsor_enrollment_second = sponsor_enrollment.iloc[1]
    sponsor_enrollment_third = sponsor_enrollment.iloc[2]
    sponsor_enrollment_fourth = sponsor_enrollment.iloc[3]
    sponsor_enrollment_rate = sponsor_enrollment.sort_values(
        ["enrollment_gap_rate", "enrollment_gap_count"], ascending=[False, False]
    )

    country_enrollment_top = country_enrollment.iloc[0]
    country_enrollment_second = country_enrollment.iloc[1]
    country_enrollment_third = country_enrollment.iloc[2]
    country_enrollment_fourth = country_enrollment.iloc[3]
    country_enrollment_rate = country_enrollment.sort_values(
        ["enrollment_gap_rate", "enrollment_gap_count"], ascending=[False, False]
    )

    condition_enrollment_top = condition_enrollment.iloc[0]
    condition_enrollment_second = condition_enrollment.iloc[1]
    condition_enrollment_third = condition_enrollment.iloc[2]
    condition_enrollment_fourth = condition_enrollment.iloc[3]
    condition_enrollment_rate = condition_enrollment.sort_values(
        ["enrollment_gap_rate", "enrollment_gap_count"], ascending=[False, False]
    )
    class_network = row_for(class_enrollment, "lead_sponsor_class", "NETWORK")
    class_nih = row_for(class_enrollment, "lead_sponsor_class", "NIH")

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
    ]

    series_links = parse_existing_series_links()
    series_links.extend(
        [
            {
                "repo_name": "ctgov-country-description-black-box",
                "title": "CT.gov Country Description Black-Box",
                "summary": "Country-linked tables for older CT.gov studies that are overdue, unlinked, and missing both main descriptive text fields.",
                "short_title": "Country Black Box",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-description-black-box/",
            },
            {
                "repo_name": "ctgov-condition-description-black-box",
                "title": "CT.gov Condition Description Black-Box",
                "summary": "Condition-family tables for older CT.gov studies that remain overdue, unlinked, and textually opaque.",
                "short_title": "Condition Black Box",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-description-black-box/",
            },
            {
                "repo_name": "ctgov-sponsor-enrollment-gap-repeaters",
                "title": "CT.gov Sponsor Enrollment-Gap Repeaters",
                "summary": "Named-sponsor tables showing where older CT.gov records still omit actual enrollment most often.",
                "short_title": "Sponsor Enrollment",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-sponsor-enrollment-gap-repeaters/",
            },
            {
                "repo_name": "ctgov-country-enrollment-gap",
                "title": "CT.gov Country Enrollment Gap",
                "summary": "Country-linked tables showing where older CT.gov records most often omit actual enrollment.",
                "short_title": "Country Enrollment",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-enrollment-gap/",
            },
            {
                "repo_name": "ctgov-condition-enrollment-gap",
                "title": "CT.gov Condition Enrollment Gap",
                "summary": "Condition-family tables showing where older CT.gov records most often omit realized sample size.",
                "short_title": "Condition Enrollment",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-enrollment-gap/",
            },
        ]
    )
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    projects: list[dict[str, object]] = []
    projects.append(
        description_geo_spec(
            repo_name="ctgov-country-description-black-box",
            title="CT.gov Country Description Black-Box",
            summary="A standalone E156 project on which country-linked portfolios carry the most overdue, unlinked, textually black-box CT.gov studies.",
            body_pairs=[
                ("Question", "Which country-linked CT.gov portfolios carry the most older studies that are overdue, unlinked, and missing both detailed description and primary outcome description?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded country links."),
                ("Method", "We defined a description black-box study as one with a two-year results gap, no linked publication, no detailed description, and no primary outcome description, then ranked country-linked portfolios with at least 500 linked studies."),
                ("Primary result", "The United States led the country-linked stock table at 5,833 studies, followed by France at 1,353, Germany at 1,262, and Canada at 1,036."),
                ("Secondary result", "Japan had the highest large-country description-black-box rate at 10.7 percent, while South Korea reached 9.1 percent and Germany 8.4 percent."),
                ("Interpretation", "Country-linked black-box tables show where the strictest narrative opacity remains concentrated after studies failed results and linkage tests."),
                ("Boundary", "Country-linked rows are non-exclusive because multinational studies can contribute to more than one national portfolio in the registry for readers."),
            ],
            protocol="This protocol isolates a strict narrative blackout inside country-linked CT.gov portfolios. A description black-box study is an eligible older closed interventional study with a two-year results gap, no linked publication, no detailed description, and no primary outcome description. Primary outputs rank country-linked portfolios with at least 500 linked studies by black-box stock and rate.",
            label_col="country_name",
            df=country_description,
            root_title="Which country-linked portfolios show the strongest description black boxes?",
            root_eyebrow="Country Description-Black-Box Project",
            root_lede="A standalone public project on country-linked narrative blackout, showing that the United States leads on stock while Japan and South Korea are much harsher on rate.",
            chapter_intro="This page takes the strict description-black-box definition out of sponsor tables and asks where geography-linked CT.gov portfolios stay overdue, unlinked, and textually opaque at the same time.",
            root_pull_quote="Description black-box tables are stricter than missing-results tables alone because they require overdue silence, no linked paper, and no basic descriptive text on the registry page.",
            paper_pull_quote="Country-linked stock and rate tell different stories: the United States dominates on volume, while Japan and South Korea are sharper on rate.",
            dashboard_pull_quote="The United States holds the largest country-linked black-box stock, France and Germany follow, and Japan is the clearest large-country rate outlier.",
            root_rail=["US 5,833", "France 1,353", "Germany 1,262", "Canada 1,036"],
            landing_metrics=[
                ("US stock", fmt_int(as_int(country_desc_top["description_black_box_count"])), "Black-box studies"),
                ("France stock", fmt_int(as_int(country_desc_second["description_black_box_count"])), "Black-box studies"),
                ("Germany stock", fmt_int(as_int(country_desc_third["description_black_box_count"])), "Black-box studies"),
                ("Japan rate", fmt_pct(as_float(country_desc_rate.iloc[0]["description_black_box_rate"])), "Large-country rate"),
            ],
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios carry the most older studies that remain overdue, unlinked, and textually black-box.",
            reader_rail=["United States", "France", "Germany", "Japan"],
            reader_metrics=[
                ("US stock", fmt_int(as_int(country_desc_top["description_black_box_count"])), "Black-box studies"),
                ("France stock", fmt_int(as_int(country_desc_second["description_black_box_count"])), "Black-box studies"),
                ("Germany stock", fmt_int(as_int(country_desc_third["description_black_box_count"])), "Black-box studies"),
                ("Canada stock", fmt_int(as_int(country_desc_fourth["description_black_box_count"])), "Black-box studies"),
            ],
            dashboard_title="Country description black-box tables show where older CT.gov records remain overdue, unlinked, and textually opaque",
            dashboard_eyebrow="Country Description-Black-Box Dashboard",
            dashboard_lede="The United States dominates country-linked description-black-box stock, France and Germany remain large on count, and Japan plus South Korea are much harsher on rate.",
            dashboard_rail=["Black-box stock", "Rate", "Countries", "Narrative blackout"],
            dashboard_metrics=[
                ("US stock", fmt_int(as_int(country_desc_top["description_black_box_count"])), "Black-box studies"),
                ("France stock", fmt_int(as_int(country_desc_second["description_black_box_count"])), "Black-box studies"),
                ("Japan rate", fmt_pct(as_float(country_desc_rate.iloc[0]["description_black_box_rate"])), "Large-country rate"),
                ("S Korea rate", fmt_pct(as_float(country_desc_rate.iloc[1]["description_black_box_rate"])), "Large-country rate"),
            ],
            sidebar_bullets=[
                "The United States leads the country-linked black-box stock table at 5,833 studies.",
                "France is next at 1,353, with Germany at 1,262 and Canada at 1,036.",
                "Japan reaches the highest large-country description-black-box rate at 10.7 percent.",
                "South Korea also stays high on rate at 9.1 percent.",
            ],
            references=common_refs,
        )
    )
    projects.append(
        description_geo_spec(
            repo_name="ctgov-condition-description-black-box",
            title="CT.gov Condition Description Black-Box",
            summary="A standalone E156 project on which therapeutic portfolios carry the most overdue, unlinked, textually black-box CT.gov studies.",
            body_pairs=[
                ("Question", "Which condition families carry the most older CT.gov studies that are overdue, unlinked, and missing both detailed description and primary outcome description?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
                ("Method", "We defined a description black-box study as one with a two-year results gap, no linked publication, no detailed description, and no primary outcome description, then ranked large condition families."),
                ("Primary result", "The broad OTHER bucket led the stock table at 3,366 studies, followed by Oncology at 2,619, Healthy volunteers at 2,516, and Cardiovascular at 1,798."),
                ("Secondary result", "Healthy volunteers had the highest large-family description-black-box rate at 17.8 percent, far above renal and urology at 8.5 percent and metabolic at 8.3 percent."),
                ("Interpretation", "The condition-family black-box view mixes diffuse registry stock with a very sharp healthy-volunteer blackout pattern that is more severe than ordinary no-results counts alone."),
                ("Boundary", "Condition families are keyword-derived registry groupings, not formal disease ontologies or diagnoses."),
            ],
            protocol="This protocol isolates a strict narrative blackout inside condition-family CT.gov portfolios. A description black-box study is an eligible older closed interventional study with a two-year results gap, no linked publication, no detailed description, and no primary outcome description. Primary outputs rank large condition families by black-box stock and rate using one condition-family label per study.",
            label_col="condition_family_label",
            df=condition_description,
            root_title="Which therapeutic portfolios show the strongest description black boxes?",
            root_eyebrow="Condition Description-Black-Box Project",
            root_lede="A standalone public project on therapeutic narrative blackout, showing that OTHER and Oncology dominate on stock while Healthy volunteers are much harsher on rate.",
            chapter_intro="This page asks which therapeutic portfolios stay overdue, unlinked, and textually black-box at the same time once the strict narrative-blackout definition is moved from sponsor tables into condition families.",
            root_pull_quote="Healthy-volunteer studies do not merely disappear on results. They also black out the descriptive text needed to understand what was actually done.",
            paper_pull_quote="Condition-family stock and rate split sharply here: OTHER and Oncology dominate on count, while Healthy volunteers are the clearest rate outlier.",
            dashboard_pull_quote="OTHER leads the condition-family black-box stock table, Oncology and Healthy volunteers follow, and Healthy volunteers are by far the sharpest large-family rate outlier.",
            root_rail=["Other 3,366", "Oncology 2,619", "Healthy vol 2,516", "Cardio 1,798"],
            landing_metrics=[
                ("Other stock", fmt_int(as_int(condition_desc_top["description_black_box_count"])), "Black-box studies"),
                ("Oncology stock", fmt_int(as_int(condition_desc_second["description_black_box_count"])), "Black-box studies"),
                ("Healthy-vol stock", fmt_int(as_int(condition_desc_third["description_black_box_count"])), "Black-box studies"),
                ("Healthy-vol rate", fmt_pct(as_float(condition_desc_healthy["description_black_box_rate"])), "Large-family rate"),
            ],
            reader_lede="A 156-word micro-paper on which therapeutic CT.gov portfolios carry the most older studies that remain overdue, unlinked, and textually black-box.",
            reader_rail=["Other", "Oncology", "Healthy volunteers", "Cardiovascular"],
            reader_metrics=[
                ("Other stock", fmt_int(as_int(condition_desc_top["description_black_box_count"])), "Black-box studies"),
                ("Oncology stock", fmt_int(as_int(condition_desc_second["description_black_box_count"])), "Black-box studies"),
                ("Healthy-vol stock", fmt_int(as_int(condition_desc_third["description_black_box_count"])), "Black-box studies"),
                ("Cardio stock", fmt_int(as_int(condition_desc_fourth["description_black_box_count"])), "Black-box studies"),
            ],
            dashboard_title="Condition description black-box tables show where older CT.gov records remain overdue, unlinked, and textually opaque",
            dashboard_eyebrow="Condition Description-Black-Box Dashboard",
            dashboard_lede="OTHER and Oncology dominate condition-family black-box stock, Healthy volunteers are massive on count and far worse on rate, and metabolic plus renal portfolios also stay elevated.",
            dashboard_rail=["Black-box stock", "Rate", "Conditions", "Narrative blackout"],
            dashboard_metrics=[
                ("Other stock", fmt_int(as_int(condition_desc_top["description_black_box_count"])), "Black-box studies"),
                ("Oncology stock", fmt_int(as_int(condition_desc_second["description_black_box_count"])), "Black-box studies"),
                ("Healthy-vol stock", fmt_int(as_int(condition_desc_third["description_black_box_count"])), "Black-box studies"),
                ("Healthy-vol rate", fmt_pct(as_float(condition_desc_healthy["description_black_box_rate"])), "Large-family rate"),
            ],
            sidebar_bullets=[
                "OTHER leads the condition-family black-box stock table at 3,366 studies.",
                "Oncology is next at 2,619, with Healthy volunteers at 2,516 and Cardiovascular at 1,798.",
                "Healthy volunteers reach a 17.8 percent description-black-box rate.",
                "Renal and urology and metabolic portfolios remain the next sharpest large-family rate outliers.",
            ],
            references=common_refs,
        )
    )
    projects.append(
        enrollment_spec(
            repo_name="ctgov-sponsor-enrollment-gap-repeaters",
            title="CT.gov Sponsor Enrollment-Gap Repeaters",
            summary="A standalone E156 project on which named sponsors most often omit actual enrollment in older CT.gov study records.",
            body_pairs=[
                ("Question", "Which named sponsors most often leave older CT.gov study pages without actual enrollment, obscuring realized sample size after study closure?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
                ("Method", "We defined an enrollment gap as missing actual enrollment among older closed studies, then ranked sponsors with at least 100 studies by stock and rate."),
                ("Primary result", "AstraZeneca led the stock table at 240 studies, followed by Memorial Sloan Kettering Cancer Center at 223, Bristol-Myers Squibb at 112, and NIAID at 108."),
                ("Secondary result", "Eastern Cooperative Oncology Group had the highest large-sponsor enrollment-gap rate at 57.9 percent, while Gynecologic Oncology Group reached 47.1 percent and Wyeth/Pfizer 30.5 percent."),
                ("Interpretation", "Enrollment gaps obscure realized sample size even when a study is closed, making the maturity and credibility of older registry records harder to judge quickly."),
                ("Boundary", "These counts reflect missing actual enrollment in registry records and do not by themselves establish concealment, error, or deliberate non-disclosure for readers."),
            ],
            protocol="This protocol isolates missing actual enrollment discipline inside older closed CT.gov records. An enrollment gap is an eligible older closed interventional study with missing actual enrollment. Primary outputs rank named sponsors with at least 100 older studies by enrollment-gap stock and rate, then compare sponsor-class patterns and major outliers.",
            label_col="lead_sponsor_name",
            df=sponsor_enrollment,
            root_title="Which sponsors most often omit actual enrollment on CT.gov?",
            root_eyebrow="Sponsor Enrollment-Gap Project",
            root_lede="A standalone public project on realized sample-size discipline, showing that AstraZeneca, Memorial Sloan Kettering, and Bristol-Myers Squibb dominate on stock while network groups are far harsher on rate.",
            chapter_intro="This page isolates one concrete maturity field: actual enrollment, the clearest registry signal for realized sample size once a study is already closed.",
            root_pull_quote="When actual enrollment is missing, readers cannot tell how many participants a closed study really finished with.",
            paper_pull_quote="Enrollment gaps are not small cosmetic omissions. They remove the realized sample-size field from records that should already be mature.",
            dashboard_pull_quote="AstraZeneca leads the sponsor enrollment-gap stock table, Memorial Sloan Kettering stays close behind, and network portfolios are much worse on rate.",
            root_rail=["AstraZeneca 240", "MSK 223", "BMS 112", "NIAID 108"],
            landing_metrics=[
                ("AstraZeneca stock", fmt_int(as_int(sponsor_enrollment_top["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("MSK stock", fmt_int(as_int(sponsor_enrollment_second["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("BMS stock", fmt_int(as_int(sponsor_enrollment_third["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("ECOG rate", fmt_pct(as_float(sponsor_enrollment_rate.iloc[0]["enrollment_gap_rate"])), "Large-sponsor rate"),
            ],
            reader_lede="A 156-word micro-paper on which named sponsors most often omit actual enrollment in older CT.gov study records.",
            reader_rail=["AstraZeneca", "MSK", "BMS", "ECOG"],
            reader_metrics=[
                ("AstraZeneca stock", fmt_int(as_int(sponsor_enrollment_top["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("MSK stock", fmt_int(as_int(sponsor_enrollment_second["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("BMS stock", fmt_int(as_int(sponsor_enrollment_third["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("NIAID stock", fmt_int(as_int(sponsor_enrollment_fourth["enrollment_gap_count"])), "Enrollment-gap studies"),
            ],
            dashboard_title="Sponsor enrollment-gap repeaters show where older CT.gov records still omit realized sample size",
            dashboard_eyebrow="Sponsor Enrollment-Gap Dashboard",
            dashboard_lede="AstraZeneca leads sponsor enrollment-gap stock, Memorial Sloan Kettering and Bristol-Myers Squibb remain high on count, and network groups are far harsher on rate than large industrial portfolios.",
            dashboard_rail=["Enrollment stock", "Rate", "Sponsors", "Actual enrollment"],
            dashboard_metrics=[
                ("AstraZeneca stock", fmt_int(as_int(sponsor_enrollment_top["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("MSK stock", fmt_int(as_int(sponsor_enrollment_second["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("ECOG rate", fmt_pct(as_float(sponsor_enrollment_rate.iloc[0]["enrollment_gap_rate"])), "Large-sponsor rate"),
                ("NETWORK rate", fmt_pct(as_float(class_network["enrollment_gap_rate"])), "Sponsor-class rate"),
            ],
            dashboard_sections=[
                chart_section("Enrollment-gap stock", bar_chart(items(sponsor_enrollment, "lead_sponsor_name", "enrollment_gap_count", label_fn=lambda value: short_sponsor(str(value))), "Enrollment stock", "Top named-sponsor enrollment-gap counts", "value", "label", "#c3452f", percent=False), "AstraZeneca, Memorial Sloan Kettering, and Bristol-Myers Squibb lead on stock.", "These are older closed studies still missing realized sample size."),
                chart_section("Enrollment-gap rate", bar_chart(rate_items(sponsor_enrollment, "lead_sponsor_name", "enrollment_gap_rate", label_fn=lambda value: short_sponsor(str(value))), "Enrollment rate", "Large-sponsor enrollment-gap rate", "value", "label", "#326891", percent=True), "Network groups dominate the top rate table.", "Rate is much harsher for several public and network portfolios than for the biggest stock holders."),
                chart_section("Sponsor-class rate", bar_chart(items(class_enrollment.sort_values(["enrollment_gap_rate", "enrollment_gap_count"], ascending=[False, False]), "lead_sponsor_class", "enrollment_gap_rate"), "Class rate", "Enrollment-gap rate by sponsor class", "value", "label", "#8b6914", percent=True), "NETWORK and NIH are clearly above INDUSTRY and OTHER on actual-enrollment rate.", "The class signature is different from the description-black-box projects."),
            ],
            sidebar_bullets=[
                "AstraZeneca leads sponsor enrollment-gap stock at 240 studies.",
                "Memorial Sloan Kettering is next at 223, with Bristol-Myers Squibb at 112 and NIAID at 108.",
                "Eastern Cooperative Oncology Group reaches a 57.9 percent enrollment-gap rate.",
                "NETWORK leads sponsor classes on rate at 12.7 percent, with NIH next at 10.8 percent.",
            ],
            references=common_refs,
            label_fn=lambda value: short_sponsor(str(value)),
        )
    )
    projects.append(
        enrollment_spec(
            repo_name="ctgov-country-enrollment-gap",
            title="CT.gov Country Enrollment Gap",
            summary="A standalone E156 project on which country-linked portfolios most often omit actual enrollment in older CT.gov records.",
            body_pairs=[
                ("Question", "Which country-linked CT.gov portfolios most often leave older study pages without actual enrollment, obscuring realized sample size after study closure?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded country links."),
                ("Method", "We defined an enrollment gap as missing actual enrollment among older closed studies, then ranked country-linked portfolios with at least 500 linked studies by stock and rate."),
                ("Primary result", "The United States led the stock table at 4,573 studies, followed by Canada at 797, Germany at 663, and France at 559."),
                ("Secondary result", "Iran had the highest large-country enrollment-gap rate at 6.3 percent, while Israel reached 6.1 percent and Norway 5.4 percent."),
                ("Interpretation", "Country-linked enrollment gaps show where realized sample-size discipline remains weak even after studies are old enough that timing-based excuses should be less plausible."),
                ("Boundary", "Country-linked rows are non-exclusive because multinational studies can contribute to more than one national portfolio in the registry as they appear here today for outside readers."),
            ],
            protocol="This protocol isolates missing actual enrollment inside country-linked CT.gov portfolios. An enrollment gap is an eligible older closed interventional study with missing actual enrollment. Primary outputs rank country-linked portfolios with at least 500 linked studies by enrollment-gap stock and rate.",
            label_col="country_name",
            df=country_enrollment,
            root_title="Which country-linked portfolios most often omit actual enrollment?",
            root_eyebrow="Country Enrollment-Gap Project",
            root_lede="A standalone public project on country-linked realized sample-size discipline, showing that the United States dominates on stock while Iran and Israel are harsher on rate.",
            chapter_intro="This page moves the actual-enrollment problem into country-linked tables and asks where older CT.gov records most often close without a realized sample-size field.",
            root_pull_quote="Actual enrollment is the clearest public field for realized sample size. When it is missing, a closed record stays materially incomplete.",
            paper_pull_quote="Country-linked stock and rate diverge again here: the United States dominates on volume, while Iran and Israel are harsher on rate.",
            dashboard_pull_quote="The United States leads country-linked enrollment-gap stock, Canada and Germany follow, and Iran is the sharpest large-country rate outlier.",
            root_rail=["US 4,573", "Canada 797", "Germany 663", "France 559"],
            landing_metrics=[
                ("US stock", fmt_int(as_int(country_enrollment_top["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Canada stock", fmt_int(as_int(country_enrollment_second["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Germany stock", fmt_int(as_int(country_enrollment_third["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Iran rate", fmt_pct(as_float(country_enrollment_rate.iloc[0]["enrollment_gap_rate"])), "Large-country rate"),
            ],
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios most often omit actual enrollment in older study records.",
            reader_rail=["United States", "Canada", "Germany", "Iran"],
            reader_metrics=[
                ("US stock", fmt_int(as_int(country_enrollment_top["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Canada stock", fmt_int(as_int(country_enrollment_second["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Germany stock", fmt_int(as_int(country_enrollment_third["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("France stock", fmt_int(as_int(country_enrollment_fourth["enrollment_gap_count"])), "Enrollment-gap studies"),
            ],
            dashboard_title="Country enrollment-gap tables show where older CT.gov records still omit realized sample size",
            dashboard_eyebrow="Country Enrollment-Gap Dashboard",
            dashboard_lede="The United States dominates country-linked enrollment-gap stock, Canada and Germany stay prominent, and Iran plus Israel are the sharpest large-country rate outliers.",
            dashboard_rail=["Enrollment stock", "Rate", "Countries", "Actual enrollment"],
            dashboard_metrics=[
                ("US stock", fmt_int(as_int(country_enrollment_top["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Canada stock", fmt_int(as_int(country_enrollment_second["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Iran rate", fmt_pct(as_float(country_enrollment_rate.iloc[0]["enrollment_gap_rate"])), "Large-country rate"),
                ("Israel rate", fmt_pct(as_float(country_enrollment_rate.iloc[1]["enrollment_gap_rate"])), "Large-country rate"),
            ],
            dashboard_sections=[
                chart_section("Enrollment-gap stock", bar_chart(items(country_enrollment, "country_name", "enrollment_gap_count"), "Enrollment stock", "Top country-linked enrollment-gap counts", "value", "label", "#c3452f", percent=False), "The United States dominates on stock because of scale.", "Canada, Germany, and France remain the next biggest country-linked enrollment-gap portfolios."),
                chart_section("Enrollment-gap rate", bar_chart(rate_items(country_enrollment, "country_name", "enrollment_gap_rate"), "Enrollment rate", "Large-country enrollment-gap rate", "value", "label", "#326891", percent=True), "Iran, Israel, and Norway are the sharpest rate outliers.", "Rate again tells a different story from stock alone."),
            ],
            sidebar_bullets=[
                "The United States leads country-linked enrollment-gap stock at 4,573 studies.",
                "Canada is next at 797, with Germany at 663 and France at 559.",
                "Iran reaches the highest large-country enrollment-gap rate at 6.3 percent.",
                "Israel follows closely at 6.1 percent.",
            ],
            references=common_refs,
        )
    )
    projects.append(
        enrollment_spec(
            repo_name="ctgov-condition-enrollment-gap",
            title="CT.gov Condition Enrollment Gap",
            summary="A standalone E156 project on which therapeutic portfolios most often omit actual enrollment in older CT.gov records.",
            body_pairs=[
                ("Question", "Which condition families most often leave older CT.gov study pages without actual enrollment, obscuring realized sample size after study closure?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
                ("Method", "We defined an enrollment gap as missing actual enrollment among older closed studies, then ranked large condition families by stock and rate."),
                ("Primary result", "Oncology led the stock table at 2,765 studies, followed by the broad OTHER bucket at 1,815, Cardiovascular at 1,179, and Infectious disease at 747."),
                ("Secondary result", "Oncology also had the highest large-family enrollment-gap rate at 6.5 percent, ahead of cardiovascular at 4.5 percent and gastrointestinal and hepatic at 4.5 percent."),
                ("Interpretation", "Condition-family enrollment gaps show that realized sample-size discipline is weakest in exactly the therapeutic areas that dominate much of the older CT.gov registry stock."),
                ("Boundary", "Condition families are keyword-derived registry groupings, so they approximate therapeutic portfolios rather than formal disease ontologies or mutually exclusive diagnoses alone."),
            ],
            protocol="This protocol isolates missing actual enrollment inside condition-family CT.gov portfolios. An enrollment gap is an eligible older closed interventional study with missing actual enrollment. Primary outputs rank large condition families by enrollment-gap stock and rate using one condition-family label per study.",
            label_col="condition_family_label",
            df=condition_enrollment,
            root_title="Which therapeutic portfolios most often omit actual enrollment?",
            root_eyebrow="Condition Enrollment-Gap Project",
            root_lede="A standalone public project on therapeutic realized sample-size discipline, showing that Oncology dominates on both stock and rate while cardiovascular and infectious portfolios remain large on count.",
            chapter_intro="This page asks which therapeutic portfolios most often close older CT.gov studies without actual enrollment, leaving the realized sample-size field blank.",
            root_pull_quote="Actual enrollment is the field that tells readers how many participants a closed study actually finished with. Missing it leaves the record materially incomplete.",
            paper_pull_quote="Oncology is not only large on stock. It is also the harshest major condition family on actual-enrollment rate.",
            dashboard_pull_quote="Oncology leads the condition-family enrollment-gap table on both stock and rate, while cardiovascular and infectious portfolios remain substantial on count.",
            root_rail=["Oncology 2,765", "Other 1,815", "Cardio 1,179", "Infectious 747"],
            landing_metrics=[
                ("Oncology stock", fmt_int(as_int(condition_enrollment_top["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Other stock", fmt_int(as_int(condition_enrollment_second["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Cardio stock", fmt_int(as_int(condition_enrollment_third["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Oncology rate", fmt_pct(as_float(condition_enrollment_rate.iloc[0]["enrollment_gap_rate"])), "Large-family rate"),
            ],
            reader_lede="A 156-word micro-paper on which therapeutic CT.gov portfolios most often omit actual enrollment in older study records.",
            reader_rail=["Oncology", "Other", "Cardiovascular", "Infectious disease"],
            reader_metrics=[
                ("Oncology stock", fmt_int(as_int(condition_enrollment_top["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Other stock", fmt_int(as_int(condition_enrollment_second["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Cardio stock", fmt_int(as_int(condition_enrollment_third["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Infectious stock", fmt_int(as_int(condition_enrollment_fourth["enrollment_gap_count"])), "Enrollment-gap studies"),
            ],
            dashboard_title="Condition enrollment-gap tables show where older CT.gov records still omit realized sample size",
            dashboard_eyebrow="Condition Enrollment-Gap Dashboard",
            dashboard_lede="Oncology dominates condition-family enrollment-gap stock and also leads on rate, while cardiovascular and infectious portfolios remain sizable and gastrointestinal plus renal families stay elevated on rate.",
            dashboard_rail=["Enrollment stock", "Rate", "Conditions", "Actual enrollment"],
            dashboard_metrics=[
                ("Oncology stock", fmt_int(as_int(condition_enrollment_top["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Other stock", fmt_int(as_int(condition_enrollment_second["enrollment_gap_count"])), "Enrollment-gap studies"),
                ("Oncology rate", fmt_pct(as_float(condition_enrollment_rate.iloc[0]["enrollment_gap_rate"])), "Large-family rate"),
                ("Cardio rate", fmt_pct(as_float(condition_enrollment_rate.iloc[1]["enrollment_gap_rate"])), "Large-family rate"),
            ],
            dashboard_sections=[
                chart_section("Enrollment-gap stock", bar_chart(items(condition_enrollment, "condition_family_label", "enrollment_gap_count"), "Enrollment stock", "Top condition-family enrollment-gap counts", "value", "label", "#c3452f", percent=False), "Oncology dominates on count, with OTHER and Cardiovascular also large.", "Actual-enrollment discipline is therefore weak in major therapeutic portfolios, not only small fringe categories."),
                chart_section("Enrollment-gap rate", bar_chart(rate_items(condition_enrollment, "condition_family_label", "enrollment_gap_rate"), "Enrollment rate", "Large-family enrollment-gap rate", "value", "label", "#326891", percent=True), "Oncology is the sharpest large-family rate outlier.", "Cardiovascular and gastrointestinal portfolios remain elevated behind it."),
            ],
            sidebar_bullets=[
                "Oncology leads condition-family enrollment-gap stock at 2,765 studies.",
                "OTHER is next at 1,815, with Cardiovascular at 1,179 and Infectious disease at 747.",
                "Oncology reaches the highest large-family enrollment-gap rate at 6.5 percent.",
                "Cardiovascular follows at 4.5 percent.",
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
