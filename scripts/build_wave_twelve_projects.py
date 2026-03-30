#!/usr/bin/env python3
"""Build wave-twelve standalone CT.gov ancient-backlog and component-gap projects."""

from __future__ import annotations

from pathlib import Path

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct
from build_split_projects import chart_section, sentence_bundle, write_project
from build_wave_eight_projects import load_csv, make_spec, row_for, short_sponsor
from build_wave_nine_projects import parse_existing_series_links

ROOT = Path(__file__).resolve().parents[1]
ATLAS_INDEX = ROOT / "index.html"


def exact_bundle(repo_name: str, pairs: list[tuple[str, str]]) -> tuple[str, list[dict[str, str]]]:
    body, sentences = sentence_bundle(pairs)
    count = len(body.split())
    if count != 156:
        raise ValueError(f"{repo_name} body has {count} words")
    return body, sentences


def items(df, label_col: str, value_col: str, *, limit: int = 10, label_fn=None) -> list[dict[str, float | str]]:
    mapper = label_fn or (lambda value: str(value))
    return [{"label": mapper(row[label_col]), "value": as_float(row[value_col])} for _, row in df.head(limit).iterrows()]


def rate_items(df, label_col: str, rate_col: str, *, limit: int = 10, label_fn=None) -> list[dict[str, float | str]]:
    mapper = label_fn or (lambda value: str(value))
    ordered = df.sort_values([rate_col, "studies"], ascending=[False, False]).head(limit)
    return [{"label": mapper(row[label_col]), "value": as_float(row[rate_col])} for _, row in ordered.iterrows()]


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"Could not find atlas fragment: {old[:80]}")
    return text.replace(old, new, 1)


def refresh_atlas_index() -> None:
    text = ATLAS_INDEX.read_text(encoding="utf-8")
    if "fifty-five-project narrative dashboard series" in text and "ctgov-completion-timing-repeaters" in text:
        return
    text = replace_once(text, "fifty-project narrative dashboard series", "fifty-five-project narrative dashboard series")
    text = replace_once(
        text,
        "The eleventh wave adds sponsor overdue debt, country overdue debt, condition overdue debt, narrative-gap repeaters, and actual-discipline repeaters on top of the earlier forty-five story pages.",
        "The twelfth wave adds sponsor ancient backlog, country ancient backlog, condition ancient backlog, description-black-box repeaters, and completion-timing repeaters on top of the earlier fifty story pages.",
    )
    text = replace_once(text, "Use this hub as the visible front door to the full fifty-project series.", "Use this hub as the visible front door to the full fifty-five-project series.")
    text = replace_once(
        text,
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-actual-discipline-repeaters/'>Actual-discipline repeaters</a>",
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-actual-discipline-repeaters/'>Actual-discipline repeaters</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-sponsor-ancient-backlog/'>Sponsor ancient backlog</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-country-ancient-backlog/'>Country ancient backlog</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-condition-ancient-backlog/'>Condition ancient backlog</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-description-black-box-repeaters/'>Description-black-box repeaters</a>"
        "<a class='link-card' href='https://mahmood726-cyber.github.io/ctgov-completion-timing-repeaters/'>Completion-timing repeaters</a>",
    )
    text = replace_once(
        text,
        "<li>Wave eleven: sponsor debt, country debt, condition debt, narrative-gap repeaters, and actual-discipline repeaters.</li><li>The hub is the visible front door to all fifty public CT.gov story pages.</li>",
        "<li>Wave eleven: sponsor debt, country debt, condition debt, narrative-gap repeaters, and actual-discipline repeaters.</li>"
        "<li>Wave twelve: sponsor, country, and condition ancient backlog plus description-black-box and completion-timing repeaters.</li>"
        "<li>The hub is the visible front door to all fifty-five public CT.gov story pages.</li>",
    )
    ATLAS_INDEX.write_text(text, encoding="utf-8")


def ancient_spec(
    *,
    repo_name: str,
    title: str,
    summary: str,
    body_pairs: list[tuple[str, str]],
    protocol: str,
    label_col: str,
    top_df,
    rate_df,
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
    landing_chart_html = chart_section(
        "Ancient backlog stock",
        bar_chart(items(top_df, label_col, "ancient_10y_count", label_fn=label_fn), "Ancient stock", "Studies unresolved more than ten overdue years beyond the two-year mark", "value", "label", "#c3452f", percent=False),
        "Very old unresolved CT.gov stock is concentrated in a small slice of the table.",
        "Ancient backlog isolates studies still unresolved more than a decade after the reporting window closed.",
    )
    dashboard_sections = [
        chart_section(
            "Ancient backlog stock",
            bar_chart(items(top_df, label_col, "ancient_10y_count", label_fn=label_fn), "Ancient stock", "Top ancient-backlog counts", "value", "label", "#c3452f", percent=False),
            "Stock shows where the oldest unresolved studies accumulate most heavily.",
            "This is the oldest visible layer of the CT.gov reporting backlog.",
        ),
        chart_section(
            "Ancient backlog rate",
            bar_chart(rate_items(rate_df, label_col, "ancient_10y_rate", label_fn=label_fn), "Ancient rate", "Ancient-backlog rate among older studies", "value", "label", "#326891", percent=True),
            "Rate highlights a different outlier pattern from stock alone.",
            "Smaller portfolios can look ordinary on stock but much worse on ancient-backlog rate.",
        ),
        chart_section(
            "Overdue years inside ancient backlog",
            bar_chart(items(top_df.sort_values(["ancient_10y_overdue_years", "ancient_10y_count"], ascending=[False, False]), label_col, "ancient_10y_overdue_years", label_fn=label_fn), "Overdue years", "Duration-weighted ancient backlog", "value", "label", "#8b6914", percent=False),
            "Duration-weighted backlog shows how long these oldest unresolved studies have been sitting silent.",
            "That converts ancient backlog from a count into a chronic-silence duration measure.",
        ),
    ]
    return make_spec(
        repo_name=repo_name,
        title=title,
        summary=summary,
        body=body,
        sentences=sentences,
        primary_estimand="Ancient-backlog stock among older closed interventional studies unresolved at least ten overdue years beyond the two-year mark",
        data_note="249,507 eligible older closed interventional studies with ancient-backlog stock, rate, and overdue-years summaries",
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
        landing_chart_html=landing_chart_html,
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
    sponsor_ancient = load_csv("wave_twelve_sponsor_ancient_backlog.csv")
    country_ancient = load_csv("wave_twelve_country_ancient_backlog.csv")
    condition_ancient = load_csv("wave_twelve_condition_ancient_backlog.csv")
    description_sponsor = load_csv("wave_twelve_description_black_box_sponsor.csv")
    description_class = load_csv("wave_twelve_description_black_box_class_summary.csv")
    completion_sponsor = load_csv("wave_twelve_completion_timing_sponsor.csv")
    completion_class = load_csv("wave_twelve_completion_timing_class_summary.csv")

    sponsor_top = sponsor_ancient.iloc[0]
    sponsor_second = sponsor_ancient.iloc[1]
    sponsor_third = sponsor_ancient.iloc[2]
    sponsor_fourth = sponsor_ancient.iloc[3]
    sponsor_rate = sponsor_ancient.sort_values(["ancient_10y_rate", "ancient_10y_count"], ascending=[False, False])

    country_top = country_ancient.iloc[0]
    country_second = country_ancient.iloc[1]
    country_third = country_ancient.iloc[2]
    country_fourth = country_ancient.iloc[3]
    country_rate = country_ancient.sort_values(["ancient_10y_rate", "ancient_10y_count"], ascending=[False, False])

    condition_top = condition_ancient.iloc[0]
    condition_second = condition_ancient.iloc[1]
    condition_third = condition_ancient.iloc[2]
    condition_fourth = condition_ancient.iloc[3]
    condition_healthy = row_for(condition_ancient, "condition_family_label", "Healthy volunteers")
    condition_metabolic = row_for(condition_ancient, "condition_family_label", "Metabolic")

    description_top = description_sponsor.iloc[0]
    description_second = description_sponsor.iloc[1]
    description_third = description_sponsor.iloc[2]
    description_fourth = description_sponsor.iloc[3]
    description_rate = description_sponsor.sort_values(
        ["description_black_box_rate", "description_black_box_count"], ascending=[False, False]
    )
    description_industry = row_for(description_class, "lead_sponsor_class", "INDUSTRY")
    description_other = row_for(description_class, "lead_sponsor_class", "OTHER")

    completion_top = completion_sponsor.iloc[0]
    completion_second = completion_sponsor.iloc[1]
    completion_third = completion_sponsor.iloc[2]
    completion_fourth = completion_sponsor.iloc[3]
    completion_rate = completion_sponsor.sort_values(
        ["completion_timing_gap_rate", "completion_timing_gap_count"], ascending=[False, False]
    )
    completion_network = row_for(completion_class, "lead_sponsor_class", "NETWORK")
    completion_nih = row_for(completion_class, "lead_sponsor_class", "NIH")

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
    ]

    series_links = parse_existing_series_links()
    series_links.extend(
        [
            {
                "repo_name": "ctgov-sponsor-ancient-backlog",
                "title": "CT.gov Sponsor Ancient Backlog",
                "summary": "Named-sponsor tables showing which portfolios still hold the oldest unresolved CT.gov studies more than a decade past deadline.",
                "short_title": "Sponsor Ancient",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-sponsor-ancient-backlog/",
            },
            {
                "repo_name": "ctgov-country-ancient-backlog",
                "title": "CT.gov Country Ancient Backlog",
                "summary": "Country-linked tables showing where the oldest unresolved CT.gov stock still accumulates after the reporting window closed long ago.",
                "short_title": "Country Ancient",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-ancient-backlog/",
            },
            {
                "repo_name": "ctgov-condition-ancient-backlog",
                "title": "CT.gov Condition Ancient Backlog",
                "summary": "Condition-family tables showing which therapeutic portfolios still carry the oldest unresolved CT.gov studies.",
                "short_title": "Condition Ancient",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-ancient-backlog/",
            },
            {
                "repo_name": "ctgov-description-black-box-repeaters",
                "title": "CT.gov Description-Black-Box Repeaters",
                "summary": "Named-sponsor tables for overdue older studies that are unlinked and missing both detailed description and primary outcome description.",
                "short_title": "Description Black Box",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-description-black-box-repeaters/",
            },
            {
                "repo_name": "ctgov-completion-timing-repeaters",
                "title": "CT.gov Completion-Timing Repeaters",
                "summary": "Named-sponsor tables for older CT.gov studies missing actual primary completion or actual completion timing fields.",
                "short_title": "Completion Timing",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-completion-timing-repeaters/",
            },
        ]
    )
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    projects: list[dict[str, object]] = []
    projects.append(
        ancient_spec(
            repo_name="ctgov-sponsor-ancient-backlog",
            title="CT.gov Sponsor Ancient Backlog",
            summary="A standalone E156 project on which named sponsors still hold the deepest stock of CT.gov studies unresolved more than a decade beyond the reporting mark.",
            body_pairs=[
                ("Question", "Which named CT.gov sponsors still hold the largest stock of studies unresolved at least ten overdue years beyond the two-year reporting mark?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
                ("Method", "We defined ancient backlog as older studies with no posted results and at least ten overdue years beyond the two-year mark, then ranked sponsors with at least 100 studies."),
                ("Primary result", "GlaxoSmithKline led the named-sponsor table at 1,045 studies, followed by National Cancer Institute at 787 and Boehringer Ingelheim at 748."),
                ("Secondary result", "Sanofi remained high on stock at 650, while Ranbaxy Laboratories Limited reached 100.0 percent and Mylan Pharmaceuticals Inc reached 96.8 percent among large sponsors."),
                ("Interpretation", "Ancient backlog isolates a harder core of silence than ordinary missing-results counts because these records remained unresolved for more than a decade after deadline."),
                ("Boundary", "This registry-timing definition does not assign legal responsibility, explain delay, or prove total absence of dissemination outside linked CT.gov fields for readers."),
            ],
            protocol="This protocol isolates the oldest unresolved slice of the sponsor backlog. Ancient backlog is defined as an eligible older closed interventional study with no posted results and at least ten overdue years beyond the two-year mark. Primary outputs rank named sponsors with at least 100 older studies by ancient-backlog stock, ancient-backlog rate, and overdue-years depth.",
            label_col="lead_sponsor_name",
            top_df=sponsor_ancient,
            rate_df=sponsor_ancient,
            root_title="Which sponsors still carry the oldest CT.gov backlog?",
            root_eyebrow="Sponsor Ancient-Backlog Project",
            root_lede="A standalone public project on the oldest unresolved CT.gov studies, showing that GlaxoSmithKline, NCI, and Boehringer Ingelheim still carry the heaviest named-sponsor ancient backlog.",
            chapter_intro="This page narrows the backlog to a harder core of silence: studies still unresolved more than ten overdue years beyond the two-year reporting window.",
            root_pull_quote="Ancient backlog is the oldest visible CT.gov silence: not just overdue studies, but studies still unresolved for more than a decade after deadline.",
            paper_pull_quote="A sponsor can look large on ordinary backlog counts, but ancient backlog isolates the records that stayed unresolved for the longest time.",
            dashboard_pull_quote="GlaxoSmithKline holds the largest sponsor ancient backlog on stock, NCI and Boehringer Ingelheim follow, and the rate table is even harsher for smaller industrial portfolios.",
            root_rail=["GSK 1,045", "NCI 787", "Boehringer 748", "Sanofi 650"],
            landing_metrics=[
                ("GSK stock", fmt_int(as_int(sponsor_top["ancient_10y_count"])), "Ancient-backlog studies"),
                ("NCI stock", fmt_int(as_int(sponsor_second["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Boehringer stock", fmt_int(as_int(sponsor_third["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Ranbaxy rate", fmt_pct(as_float(sponsor_rate.iloc[0]["ancient_10y_rate"])), "Large-sponsor rate"),
            ],
            reader_lede="A 156-word micro-paper on which named sponsors still hold the oldest unresolved CT.gov studies more than a decade beyond the reporting window.",
            reader_rail=["GSK", "NCI", "Boehringer", "Ancient stock"],
            reader_metrics=[
                ("GSK stock", fmt_int(as_int(sponsor_top["ancient_10y_count"])), "Ancient-backlog studies"),
                ("NCI stock", fmt_int(as_int(sponsor_second["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Boehringer stock", fmt_int(as_int(sponsor_third["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Mylan rate", fmt_pct(as_float(sponsor_rate.iloc[1]["ancient_10y_rate"])), "Large-sponsor rate"),
            ],
            dashboard_title="Sponsor ancient backlog shows which named portfolios still carry CT.gov studies unresolved more than a decade after deadline",
            dashboard_eyebrow="Sponsor Ancient-Backlog Dashboard",
            dashboard_lede="GlaxoSmithKline leads the named-sponsor ancient-backlog stock, NCI remains the largest public-sector holder, Boehringer Ingelheim and Sanofi stay high on chronic backlog, and the rate table is even harsher for smaller industrial portfolios.",
            dashboard_rail=["Ancient stock", "Rate", "Overdue years", "Named sponsors"],
            dashboard_metrics=[
                ("GSK stock", fmt_int(as_int(sponsor_top["ancient_10y_count"])), "Ancient-backlog studies"),
                ("NCI stock", fmt_int(as_int(sponsor_second["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Boehringer stock", fmt_int(as_int(sponsor_third["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Sanofi stock", fmt_int(as_int(sponsor_fourth["ancient_10y_count"])), "Ancient-backlog studies"),
            ],
            sidebar_bullets=[
                "GlaxoSmithKline carries the largest named-sponsor ancient backlog at 1,045 studies.",
                "NCI follows at 787, with Boehringer Ingelheim next at 748 and Sanofi at 650.",
                "Ranbaxy reaches a 100.0 percent ancient-backlog rate among large sponsors, and Mylan is close behind at 96.8 percent.",
                "Ancient backlog isolates studies still unresolved more than ten overdue years beyond the two-year reporting mark.",
            ],
            references=common_refs,
            label_fn=lambda value: short_sponsor(str(value)),
        )
    )
    projects.append(
        ancient_spec(
            repo_name="ctgov-country-ancient-backlog",
            title="CT.gov Country Ancient Backlog",
            summary="A standalone E156 project on which country-linked portfolios still hold the deepest stock of unresolved CT.gov studies more than a decade beyond the reporting window.",
            body_pairs=[
                ("Question", "Which country-linked CT.gov portfolios still hold the largest stock of studies unresolved at least ten overdue years beyond the two-year reporting mark?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded country links."),
                ("Method", "We defined ancient backlog as older studies with no posted results and at least ten overdue years beyond the two-year mark, then ranked country-linked portfolios with at least 500 linked studies."),
                ("Primary result", "The United States led the country-linked table at 22,301 studies, followed by Canada at 4,055, Germany at 3,759, and France at 3,569."),
                ("Secondary result", "Iran had the highest large-country ancient-backlog rate at 46.4 percent, while Norway, India, and Finland also ranked sharply on rate."),
                ("Interpretation", "Ancient backlog shows that very old silence is not restricted to one geography, but remains concentrated in a small set of large country-linked portfolios."),
                ("Boundary", "Country-linked rows are non-exclusive because multinational studies can contribute to more than one national portfolio in the registry."),
            ],
            protocol="This protocol isolates the oldest unresolved slice of the geography-linked backlog. Ancient backlog is defined as an eligible older closed interventional study with no posted results and at least ten overdue years beyond the two-year mark. Primary outputs rank country-linked portfolios with at least 500 linked studies by ancient-backlog stock, ancient-backlog rate, and overdue-years depth.",
            label_col="country_name",
            top_df=country_ancient,
            rate_df=country_ancient,
            root_title="Which country-linked portfolios still hold the oldest CT.gov backlog?",
            root_eyebrow="Country Ancient-Backlog Project",
            root_lede="A standalone public project on geography-linked ancient backlog, showing that the United States, Canada, Germany, and France still hold the heaviest country-linked stock of very old unresolved CT.gov studies.",
            chapter_intro="This page asks where the oldest visible CT.gov silence sits once the geography table is narrowed to records still unresolved more than ten overdue years beyond the reporting mark.",
            root_pull_quote="The geography of ancient backlog mixes scale and severity: the largest stock sits in major countries, but some smaller portfolios are harsher on rate.",
            paper_pull_quote="Country-linked backlog counts do not assign each study to a single nation, but they do show where very old unresolved stock remains concentrated.",
            dashboard_pull_quote="The United States dominates country-linked ancient backlog on stock, Canada, Germany, and France follow, and Iran is the sharpest large-country rate outlier.",
            root_rail=["US 22,301", "Canada 4,055", "Germany 3,759", "France 3,569"],
            landing_metrics=[
                ("US stock", fmt_int(as_int(country_top["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Canada stock", fmt_int(as_int(country_second["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Germany stock", fmt_int(as_int(country_third["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Iran rate", fmt_pct(as_float(country_rate.iloc[0]["ancient_10y_rate"])), "Large-country rate"),
            ],
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios still carry the oldest unresolved studies more than a decade beyond the reporting window.",
            reader_rail=["United States", "Canada", "Germany", "France"],
            reader_metrics=[
                ("US stock", fmt_int(as_int(country_top["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Canada stock", fmt_int(as_int(country_second["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Germany stock", fmt_int(as_int(country_third["ancient_10y_count"])), "Ancient-backlog studies"),
                ("France stock", fmt_int(as_int(country_fourth["ancient_10y_count"])), "Ancient-backlog studies"),
            ],
            dashboard_title="Country ancient backlog shows where very old unresolved CT.gov studies still accumulate most heavily",
            dashboard_eyebrow="Country Ancient-Backlog Dashboard",
            dashboard_lede="The United States dominates country-linked ancient backlog by stock, Canada, Germany, and France remain the next largest portfolios, and Iran is the clearest rate outlier among large country-linked tables.",
            dashboard_rail=["Ancient stock", "Rate", "Overdue years", "Countries"],
            dashboard_metrics=[
                ("US stock", fmt_int(as_int(country_top["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Canada stock", fmt_int(as_int(country_second["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Germany stock", fmt_int(as_int(country_third["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Iran rate", fmt_pct(as_float(country_rate.iloc[0]["ancient_10y_rate"])), "Large-country rate"),
            ],
            sidebar_bullets=[
                "The United States carries the largest country-linked ancient backlog at 22,301 studies.",
                "Canada, Germany, and France remain the next biggest ancient-backlog portfolios on stock.",
                "Iran reaches the highest large-country ancient-backlog rate at 46.4 percent.",
                "Country-linked rows are non-exclusive because multinational studies can appear in more than one portfolio.",
            ],
            references=common_refs,
        )
    )
    projects.append(
        ancient_spec(
            repo_name="ctgov-condition-ancient-backlog",
            title="CT.gov Condition Ancient Backlog",
            summary="A standalone E156 project on which therapeutic portfolios still hold the deepest stock of unresolved CT.gov studies more than a decade beyond the reporting window.",
            body_pairs=[
                ("Question", "Which condition families still hold the largest stock of CT.gov studies unresolved at least ten overdue years beyond the two-year reporting mark?"),
                ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
                ("Method", "We defined ancient backlog as older studies with no posted results and at least ten overdue years beyond the two-year mark, then ranked large condition families."),
                ("Primary result", "Oncology led the named-family table at 11,369 studies, while the broad OTHER bucket held 10,899 and cardiovascular followed at 6,545."),
                ("Secondary result", "Metabolic remained high on stock at 4,693, while healthy volunteers reached the highest large-family ancient-backlog rate at 31.5 percent."),
                ("Interpretation", "Ancient backlog separates diffuse registry stock from large disease portfolios and shows that very old silence remains prominent in major therapeutic areas."),
                ("Boundary", "Condition families are keyword-derived registry groupings, so they approximate therapeutic portfolios rather than fixed clinical ontologies or mutually exclusive diagnoses within the registry as presented here."),
            ],
            protocol="This protocol isolates the oldest unresolved slice of the condition-family backlog. Ancient backlog is defined as an eligible older closed interventional study with no posted results and at least ten overdue years beyond the two-year mark. Primary outputs rank large condition families by ancient-backlog stock, ancient-backlog rate, and overdue-years depth using one condition-family label per study.",
            label_col="condition_family_label",
            top_df=condition_ancient,
            rate_df=condition_ancient,
            root_title="Which therapeutic portfolios still hold the oldest CT.gov backlog?",
            root_eyebrow="Condition Ancient-Backlog Project",
            root_lede="A standalone public project on therapeutic ancient backlog, showing that oncology, diffuse OTHER stock, cardiovascular, and metabolic portfolios still carry the heaviest old unresolved CT.gov burden.",
            chapter_intro="This page asks which therapeutic portfolios still hold the oldest unresolved CT.gov records once the backlog is narrowed to studies silent for more than ten overdue years past the reporting mark.",
            root_pull_quote="Ancient backlog is not just a sponsor story. Major disease portfolios and healthy-volunteer studies also carry very old unresolved CT.gov stock.",
            paper_pull_quote="The therapeutic view separates large named disease portfolios from the diffuse OTHER bucket and shows where very old silence persists.",
            dashboard_pull_quote="Oncology leads the named-family ancient backlog on stock, OTHER remains huge, cardiovascular and metabolic stay prominent, and healthy-volunteer studies are the sharpest large-family rate outlier.",
            root_rail=["Oncology 11,369", "Other 10,899", "Cardio 6,545", "Metabolic 4,693"],
            landing_metrics=[
                ("Oncology stock", fmt_int(as_int(condition_top["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Other stock", fmt_int(as_int(condition_second["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Cardio stock", fmt_int(as_int(condition_third["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Healthy-vol rate", fmt_pct(as_float(condition_healthy["ancient_10y_rate"])), "Large-family rate"),
            ],
            reader_lede="A 156-word micro-paper on which therapeutic portfolios still hold the oldest unresolved CT.gov studies more than a decade beyond the reporting window.",
            reader_rail=["Oncology", "Other", "Cardiovascular", "Metabolic"],
            reader_metrics=[
                ("Oncology stock", fmt_int(as_int(condition_top["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Other stock", fmt_int(as_int(condition_second["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Cardio stock", fmt_int(as_int(condition_third["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Metabolic stock", fmt_int(as_int(condition_fourth["ancient_10y_count"])), "Ancient-backlog studies"),
            ],
            dashboard_title="Condition ancient backlog shows which therapeutic CT.gov portfolios still hold the oldest unresolved studies",
            dashboard_eyebrow="Condition Ancient-Backlog Dashboard",
            dashboard_lede="Oncology leads the named-family ancient backlog, OTHER remains very large on stock, cardiovascular and metabolic stay prominent, and healthy-volunteer studies are worst on large-family rate.",
            dashboard_rail=["Ancient stock", "Rate", "Overdue years", "Conditions"],
            dashboard_metrics=[
                ("Oncology stock", fmt_int(as_int(condition_top["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Other stock", fmt_int(as_int(condition_second["ancient_10y_count"])), "Ancient-backlog studies"),
                ("Healthy-vol rate", fmt_pct(as_float(condition_healthy["ancient_10y_rate"])), "Large-family rate"),
                ("Metabolic rate", fmt_pct(as_float(condition_metabolic["ancient_10y_rate"])), "Large-family rate"),
            ],
            sidebar_bullets=[
                "Oncology holds the largest named-family ancient backlog at 11,369 studies.",
                "OTHER remains huge on stock at 10,899, with cardiovascular next at 6,545 and metabolic at 4,693.",
                "Healthy volunteers reach the highest large-family ancient-backlog rate at 31.5 percent.",
                "Ancient backlog shows that very old CT.gov silence persists across major therapeutic portfolios, not only isolated sponsor tables.",
            ],
            references=common_refs,
        )
    )
    description_body, description_sentences = exact_bundle(
        "ctgov-description-black-box-repeaters",
        [
            ("Question", "Which named sponsors accumulate the most CT.gov pages that are overdue, unlinked, and missing both detailed descriptions and primary outcome descriptions?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
            ("Method", "We defined a description black-box study as one with a two-year results gap, no linked publication, no detailed description, and no primary outcome description, then ranked sponsors with at least 100 studies."),
            ("Primary result", "Boehringer Ingelheim led the named-sponsor table at 661 studies, followed by Pfizer at 408, Hoffmann-La Roche at 383, and AstraZeneca at 357."),
            ("Secondary result", "Mylan Pharmaceuticals Inc reached the highest large-sponsor rate at 93.7 percent, while industry reached 13.6 percent and OTHER 4.2 percent as sponsor classes."),
            ("Interpretation", "This definition isolates a stricter narrative blackout where registry pages remain silent on descriptive text and dissemination, not only on results status."),
            ("Boundary", "Description black-box status is a registry visibility measure and does not prove the study lacked protocols, manuscripts, or documentation outside CT.gov."),
        ],
    )
    projects.append(
        make_spec(
            repo_name="ctgov-description-black-box-repeaters",
            title="CT.gov Description-Black-Box Repeaters",
            summary="A standalone E156 project on named sponsors whose older CT.gov records are overdue, unlinked, and missing both detailed descriptions and primary outcome descriptions.",
            body=description_body,
            sentences=description_sentences,
            primary_estimand="Description black-box stock among older studies with no results, no linked publication, no detailed description, and no primary outcome description",
            data_note="249,507 eligible older closed interventional studies with description-black-box sponsor and class summaries",
            references=common_refs,
            protocol="This protocol isolates a stricter narrative blackout inside older CT.gov records. A description black-box study is an eligible older closed interventional study with a two-year results gap, no linked publication reference, no detailed description, and no primary outcome description. Primary outputs rank named sponsors with at least 100 older studies by description-black-box stock and rate, then compare sponsor-class summaries.",
            root_title="Which sponsors create the strongest description black boxes on CT.gov?",
            root_eyebrow="Description-Black-Box Project",
            root_lede="A standalone public project on studies that are overdue, unlinked, and textually opaque, showing that Boehringer Ingelheim, Pfizer, and Hoffmann-La Roche dominate the named-sponsor table.",
            chapter_intro="This page isolates a strict description blackout: records that are not only overdue and unlinked, but also missing both the detailed description and the primary outcome description fields.",
            root_pull_quote="A description black box is more than a missing-results page. It is a page that withholds both outcome-linked reporting and the basic text needed to understand what was studied.",
            paper_pull_quote="This stricter definition finds narrative opacity where readers cannot recover the study story from the registry page itself.",
            dashboard_pull_quote="Boehringer Ingelheim leads the named-sponsor description-black-box stock, Pfizer and Roche follow, and industry dominates the sponsor-class rate table.",
            root_rail=["Boehringer 661", "Pfizer 408", "Roche 383", "AstraZeneca 357"],
            landing_metrics=[
                ("Boehringer stock", fmt_int(as_int(description_top["description_black_box_count"])), "Black-box studies"),
                ("Pfizer stock", fmt_int(as_int(description_second["description_black_box_count"])), "Black-box studies"),
                ("Roche stock", fmt_int(as_int(description_third["description_black_box_count"])), "Black-box studies"),
                ("Mylan rate", fmt_pct(as_float(description_rate.iloc[0]["description_black_box_rate"])), "Large-sponsor rate"),
            ],
            landing_chart_html=chart_section("Description black-box stock", bar_chart(items(description_sponsor, "lead_sponsor_name", "description_black_box_count", label_fn=lambda value: short_sponsor(str(value))), "Black-box stock", "Named-sponsor counts of overdue, unlinked, textually black-box studies", "value", "label", "#c3452f", percent=False), "Large industrial portfolios dominate the description-black-box stock table.", "These are older studies with no results, no linked publication, no detailed description, and no primary outcome description."),
            reader_lede="A 156-word micro-paper on which named sponsors accumulate the strongest description black boxes inside older CT.gov records.",
            reader_rail=["Boehringer", "Pfizer", "Roche", "Mylan"],
            reader_metrics=[
                ("Boehringer stock", fmt_int(as_int(description_top["description_black_box_count"])), "Black-box studies"),
                ("Pfizer stock", fmt_int(as_int(description_second["description_black_box_count"])), "Black-box studies"),
                ("Roche stock", fmt_int(as_int(description_third["description_black_box_count"])), "Black-box studies"),
                ("AstraZeneca stock", fmt_int(as_int(description_fourth["description_black_box_count"])), "Black-box studies"),
            ],
            dashboard_title="Description-black-box repeaters show where older CT.gov pages are both overdue and textually opaque",
            dashboard_eyebrow="Description-Black-Box Dashboard",
            dashboard_lede="Boehringer Ingelheim leads the named-sponsor description-black-box table, Pfizer and Roche follow, Mylan is the sharpest large-sponsor rate outlier, and industry dominates the sponsor-class rate comparison.",
            dashboard_rail=["Black-box stock", "Rate", "Class rates", "Named sponsors"],
            dashboard_metrics=[
                ("Boehringer stock", fmt_int(as_int(description_top["description_black_box_count"])), "Black-box studies"),
                ("Pfizer stock", fmt_int(as_int(description_second["description_black_box_count"])), "Black-box studies"),
                ("Mylan rate", fmt_pct(as_float(description_rate.iloc[0]["description_black_box_rate"])), "Large-sponsor rate"),
                ("Industry rate", fmt_pct(as_float(description_industry["description_black_box_rate"])), "Sponsor-class rate"),
            ],
            dashboard_sections=[
                chart_section("Top sponsor description-black-box stock", bar_chart(items(description_sponsor, "lead_sponsor_name", "description_black_box_count", label_fn=lambda value: short_sponsor(str(value))), "Black-box stock", "Top named-sponsor black-box counts", "value", "label", "#c3452f", percent=False), "Boehringer Ingelheim, Pfizer, Roche, and AstraZeneca lead the stock table.", "This isolates a stricter narrative blackout than missing-results counts alone."),
                chart_section("Description-black-box rate", bar_chart(rate_items(description_sponsor, "lead_sponsor_name", "description_black_box_rate", label_fn=lambda value: short_sponsor(str(value))), "Black-box rate", "Large-sponsor black-box rate", "value", "label", "#326891", percent=True), "Mylan, Sandoz, and legacy Wyeth/Pfizer portfolios are much harsher on rate than the stock table alone suggests.", "Rate and stock need to be read together."),
                chart_section("Sponsor-class rate", bar_chart(items(description_class.sort_values(["description_black_box_rate", "description_black_box_count"], ascending=[False, False]), "lead_sponsor_class", "description_black_box_rate"), "Class rate", "Description-black-box rate by sponsor class", "value", "label", "#8b6914", percent=True), "Industry is far above OTHER and the public-sector classes on this stricter black-box measure.", "The class view shows the description-black-box problem is especially industrial in this older-study slice."),
            ],
            sidebar_bullets=[
                "Boehringer Ingelheim leads the description-black-box table at 661 studies.",
                "Pfizer follows at 408, with Hoffmann-La Roche at 383 and AstraZeneca at 357.",
                "Mylan reaches a 93.7 percent description-black-box rate among large sponsors.",
                "Industry reaches a 13.6 percent sponsor-class rate, while OTHER is at 4.2 percent.",
            ],
        )
    )
    completion_body, completion_sentences = exact_bundle(
        "ctgov-completion-timing-repeaters",
        [
            ("Question", "Which named sponsors most often leave older CT.gov study pages without actual primary completion or actual completion timing fields?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
            ("Method", "We defined a completion-timing gap as missing actual primary completion or missing actual completion among older closed studies, then ranked sponsors with at least 100 studies."),
            ("Primary result", "Boehringer Ingelheim led the named-sponsor table at 930 studies, followed by National Cancer Institute at 601, Novartis Pharmaceuticals at 271, and EORTC at 166."),
            ("Secondary result", "Gynecologic Oncology Group had the highest large-sponsor completion-timing gap rate at 83.1 percent, while NETWORK reached 19.2 percent and NIH 17.2 percent as sponsor classes."),
            ("Interpretation", "Completion-timing gaps obscure when older studies truly finished, making the reporting window harder to read even before results, publications, or outcome text are evaluated."),
            ("Boundary", "These counts reflect missing registry timing fields among older closed studies and do not by themselves establish concealment, intent, or legal breach alone."),
        ],
    )
    projects.append(
        make_spec(
            repo_name="ctgov-completion-timing-repeaters",
            title="CT.gov Completion-Timing Repeaters",
            summary="A standalone E156 project on named sponsors whose older CT.gov records still omit actual primary completion or actual completion timing fields.",
            body=completion_body,
            sentences=completion_sentences,
            primary_estimand="Completion-timing gap stock among older studies missing actual primary completion or actual completion fields",
            data_note="249,507 eligible older closed interventional studies with completion-timing sponsor, component, and class summaries",
            references=common_refs,
            protocol="This protocol isolates missing actual timing discipline inside older closed CT.gov records. A completion-timing gap is an eligible older closed interventional study with either a missing actual primary completion date or a missing actual completion date. Primary outputs rank named sponsors with at least 100 older studies by completion-timing gap stock and rate, then compare sponsor-class patterns and timing components.",
            root_title="Which sponsors most often leave CT.gov without actual completion timing?",
            root_eyebrow="Completion-Timing Project",
            root_lede="A standalone public project on actual completion timing discipline, showing that Boehringer Ingelheim, NCI, and Novartis Pharmaceuticals dominate the named-sponsor completion-gap table while NETWORK is worst on class rate.",
            chapter_intro="This page narrows the actual-field problem to timing itself: missing actual primary completion dates or actual completion dates in older closed studies.",
            root_pull_quote="Without actual completion timing, readers cannot clearly place a closed study in the reporting window, even before asking whether results were posted.",
            paper_pull_quote="Completion-timing gaps are not cosmetic fields. They determine whether a mature CT.gov record can be placed on the reporting clock with confidence.",
            dashboard_pull_quote="Boehringer Ingelheim leads the named-sponsor completion-timing gap stock, NCI remains a major public-sector outlier, and NETWORK is the harshest sponsor class on rate.",
            root_rail=["Boehringer 930", "NCI 601", "Novartis 271", "EORTC 166"],
            landing_metrics=[
                ("Boehringer stock", fmt_int(as_int(completion_top["completion_timing_gap_count"])), "Timing-gap studies"),
                ("NCI stock", fmt_int(as_int(completion_second["completion_timing_gap_count"])), "Timing-gap studies"),
                ("Novartis stock", fmt_int(as_int(completion_third["completion_timing_gap_count"])), "Timing-gap studies"),
                ("GOG rate", fmt_pct(as_float(completion_rate.iloc[0]["completion_timing_gap_rate"])), "Large-sponsor rate"),
            ],
            landing_chart_html=chart_section("Completion-timing stock", bar_chart(items(completion_sponsor, "lead_sponsor_name", "completion_timing_gap_count", label_fn=lambda value: short_sponsor(str(value))), "Timing-gap stock", "Named-sponsor counts of older studies missing actual completion timing", "value", "label", "#c3452f", percent=False), "Boehringer Ingelheim, NCI, and Novartis Pharmaceuticals dominate the stock table.", "This slice focuses only on missing actual timing fields, not the broader actual-discipline bundle."),
            reader_lede="A 156-word micro-paper on which named sponsors most often omit actual completion timing in older CT.gov study records.",
            reader_rail=["Boehringer", "NCI", "Novartis", "NETWORK"],
            reader_metrics=[
                ("Boehringer stock", fmt_int(as_int(completion_top["completion_timing_gap_count"])), "Timing-gap studies"),
                ("NCI stock", fmt_int(as_int(completion_second["completion_timing_gap_count"])), "Timing-gap studies"),
                ("Novartis stock", fmt_int(as_int(completion_third["completion_timing_gap_count"])), "Timing-gap studies"),
                ("EORTC stock", fmt_int(as_int(completion_fourth["completion_timing_gap_count"])), "Timing-gap studies"),
            ],
            dashboard_title="Completion-timing repeaters show where older CT.gov records still obscure actual study finish dates",
            dashboard_eyebrow="Completion-Timing Dashboard",
            dashboard_lede="Boehringer Ingelheim leads completion-timing gap stock, NCI remains a major public-sector outlier, EORTC and Gynecologic Oncology Group are harsh on rate, and NETWORK is worst among sponsor classes.",
            dashboard_rail=["Timing-gap stock", "Rate", "Timing components", "Sponsor classes"],
            dashboard_metrics=[
                ("Boehringer stock", fmt_int(as_int(completion_top["completion_timing_gap_count"])), "Timing-gap studies"),
                ("NCI stock", fmt_int(as_int(completion_second["completion_timing_gap_count"])), "Timing-gap studies"),
                ("GOG rate", fmt_pct(as_float(completion_rate.iloc[0]["completion_timing_gap_rate"])), "Large-sponsor rate"),
                ("NETWORK rate", fmt_pct(as_float(completion_network["completion_timing_gap_rate"])), "Sponsor-class rate"),
            ],
            dashboard_sections=[
                chart_section("Top sponsor completion-timing stock", bar_chart(items(completion_sponsor, "lead_sponsor_name", "completion_timing_gap_count", label_fn=lambda value: short_sponsor(str(value))), "Timing-gap stock", "Top named-sponsor timing-gap counts", "value", "label", "#c3452f", percent=False), "Boehringer Ingelheim, NCI, Novartis Pharmaceuticals, and EORTC lead the timing-gap stock table.", "The timing-gap table is narrower than the full actual-discipline audit and easier to interpret against deadline logic."),
                chart_section("Completion-timing rate", bar_chart(rate_items(completion_sponsor, "lead_sponsor_name", "completion_timing_gap_rate", label_fn=lambda value: short_sponsor(str(value))), "Timing-gap rate", "Large-sponsor rate of missing actual timing", "value", "label", "#326891", percent=True), "Gynecologic Oncology Group, EORTC, and Eastern Cooperative Oncology Group are the sharpest rate outliers.", "Rate again tells a different story from stock."),
                chart_section("Missing actual completion dates", bar_chart(items(completion_sponsor.sort_values(["completion_actual_gap_count", "completion_timing_gap_count"], ascending=[False, False]), "lead_sponsor_name", "completion_actual_gap_count", label_fn=lambda value: short_sponsor(str(value))), "Completion-date gaps", "Named sponsors missing actual completion dates", "value", "label", "#8b6914", percent=False), "The completion-actual component accounts for almost all large sponsor timing gaps in this slice.", "That is why Boehringer, NCI, and EORTC stay high whichever timing component is read first."),
                chart_section("Sponsor-class timing-gap rate", bar_chart(items(completion_class.sort_values(["completion_timing_gap_rate", "completion_timing_gap_count"], ascending=[False, False]), "lead_sponsor_class", "completion_timing_gap_rate"), "Class timing-gap rate", "Completion-timing gap rate by sponsor class", "value", "label", "#5b4b8a", percent=True), "NETWORK and NIH are much harsher than INDUSTRY or OTHER on completion-timing rate.", "This component therefore has a different sponsor-class signature from description black-box opacity."),
            ],
            sidebar_bullets=[
                "Boehringer Ingelheim leads the completion-timing gap table at 930 studies.",
                "NCI follows at 601, with Novartis Pharmaceuticals at 271 and EORTC at 166.",
                "Gynecologic Oncology Group reaches an 83.1 percent completion-timing gap rate among large sponsors.",
                "NETWORK is worst on sponsor-class rate at 19.2 percent, with NIH next at 17.2 percent.",
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

    refresh_atlas_index()
    print(f"Updated {ATLAS_INDEX}")


if __name__ == "__main__":
    main()
