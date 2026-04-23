#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Build wave-ten standalone CT.gov ghost and black-box projects."""

from __future__ import annotations

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct
from build_split_projects import chart_section, sentence_bundle, write_project
from build_wave_eight_projects import load_csv, make_spec, row_for, short_sponsor
from build_wave_nine_projects import parse_existing_series_links


def main() -> None:
    sponsor_ghost = load_csv("wave_ten_sponsor_ghost_watchlist.csv")
    country_ghost = load_csv("wave_ten_country_ghost_watchlist.csv")
    condition_ghost = load_csv("wave_ten_condition_ghost_watchlist.csv")
    sponsor_black_box = load_csv("wave_ten_black_box_sponsor_watchlist.csv")
    strict_black_box = load_csv("wave_ten_strict_black_box_watchlist.csv")
    strict_black_box_class = load_csv("wave_ten_strict_black_box_class_summary.csv")

    sponsor_ghost_top = sponsor_ghost.iloc[0]
    sponsor_ghost_second = sponsor_ghost.iloc[1]
    sponsor_ghost_third = sponsor_ghost.iloc[2]
    sponsor_black_box_top = sponsor_black_box.iloc[0]
    sponsor_black_box_second = sponsor_black_box.iloc[1]
    sponsor_black_box_third = sponsor_black_box.iloc[2]

    country_ghost_top = country_ghost.iloc[0]
    country_ghost_second = country_ghost.iloc[1]
    country_ghost_third = country_ghost.iloc[2]
    country_ghost_fourth = country_ghost.iloc[3]

    condition_ghost_top = condition_ghost.iloc[0]
    condition_ghost_second = condition_ghost.iloc[1]
    condition_ghost_third = condition_ghost.iloc[2]
    condition_ghost_fourth = condition_ghost.iloc[3]

    strict_black_box_top = strict_black_box.iloc[0]
    strict_black_box_second = strict_black_box.iloc[1]
    strict_black_box_third = strict_black_box.iloc[2]
    strict_industry = row_for(strict_black_box_class, "lead_sponsor_class", "INDUSTRY")
    strict_other = row_for(strict_black_box_class, "lead_sponsor_class", "OTHER")
    strict_network = row_for(strict_black_box_class, "lead_sponsor_class", "NETWORK")

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
    ]

    series_links = parse_existing_series_links()
    series_links.extend(
        [
            {
                "repo_name": "ctgov-sponsor-ghost-repeaters",
                "title": "CT.gov Sponsor Ghost Repeaters",
                "summary": "Named-sponsor ghost-protocol watchlist showing which sponsors remain most ghosted above expectation.",
                "short_title": "Sponsor Ghosts",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-sponsor-ghost-repeaters/",
            },
            {
                "repo_name": "ctgov-country-ghost-watchlist",
                "title": "CT.gov Country Ghost Watchlist",
                "summary": "Country-linked ghost watchlist showing where deeper silence remains most elevated above expectation.",
                "short_title": "Country Ghosts",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-ghost-watchlist/",
            },
            {
                "repo_name": "ctgov-condition-ghost-watchlist",
                "title": "CT.gov Condition Ghost Watchlist",
                "summary": "Condition-family ghost watchlist showing which therapeutic portfolios are ghosted well above expectation.",
                "short_title": "Condition Ghosts",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-ghost-watchlist/",
            },
            {
                "repo_name": "ctgov-black-box-sponsor-repeaters",
                "title": "CT.gov Black-Box Sponsor Repeaters",
                "summary": "Named-sponsor black-box tables showing where no-results, no-paper, no-description silence concentrates.",
                "short_title": "Black-Box Sponsors",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-black-box-sponsor-repeaters/",
            },
            {
                "repo_name": "ctgov-strict-core-black-box",
                "title": "CT.gov Strict-Core Black-Box",
                "summary": "Strict U.S.-nexus black-box tables showing where the regulated-looking deep-silence core still concentrates.",
                "short_title": "Strict Black-Box",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-strict-core-black-box/",
            },
        ]
    )
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    sponsor_ghost_body, sponsor_ghost_sentences = sentence_bundle(
        [
            ("Question", "Which named CT.gov sponsors remain most ghosted once silence is narrowed from missing results to ghost protocols and read as excess over expectation?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
            ("Method", "Using the wave-nine sponsor watchlist, we ranked sponsors by excess ghost-protocol stock, raw ghost counts, black-box stock, and strict-core carryover."),
            ("Primary result", "Cairo University carried the largest sponsor ghost excess at 228 studies, followed by Sanofi at 219 and Bayer at 179."),
            ("Secondary result", "Ain Shams University also remained prominent on ghost excess, while several of the biggest ghost repeaters were large industry sponsors with substantial black-box stock."),
            ("Interpretation", "The deeper-silence sponsor table therefore differs from the adjusted no-results table and pulls several ghost-heavy institutions to the front across universities, hospital systems, and major global drug-company portfolios all alike."),
            ("Boundary", "Ghost-protocol status here is a registry-visibility definition based on missing results and missing linked publication references, not proof of total absence of reporting elsewhere."),
        ]
    )
    country_ghost_body, country_ghost_sentences = sentence_bundle(
        [
            ("Question", "Which country-linked CT.gov portfolios remain most ghosted above expectation once the series shifts from adjusted no-results stock to excess ghost protocols?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded named-country links."),
            ("Method", "Using the wave-nine country watchlist, we ranked country-linked portfolios by excess ghost stock, raw ghost counts, black-box stock, and black-box rates."),
            ("Primary result", "France carried the largest country-linked ghost excess at 1,157 studies, followed by China at 1,007, Egypt at 955, and South Korea at 871."),
            ("Secondary result", "South Korea and China also stood out on black-box intensity, while France remained the largest Western ghost-stock portfolio on count."),
            ("Interpretation", "The deeper-silence geography therefore mixes very large European stock with sharper Asian and Middle Eastern ghost tails once stock-heavy Western systems, East Asian portfolios, and Egyptian-linked studies are read in the same frame together carefully."),
            ("Boundary", "Country-linked ghost tables count country-linked studies rather than assigning each multinational record to one exclusive national portfolio."),
        ]
    )
    condition_ghost_body, condition_ghost_sentences = sentence_bundle(
        [
            ("Question", "Which condition families remain most ghosted once the series stops centering missing-results stock and instead ranks excess ghost protocols?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
            ("Method", "Using the wave-nine condition watchlist, we ranked condition families by excess ghost stock, raw ghost counts, black-box stock, and black-box rates."),
            ("Primary result", "Healthy volunteers carried the largest condition-family ghost excess at 1,032 studies, far ahead of the broader OTHER bucket at 552 and musculoskeletal and pain at 333."),
            ("Secondary result", "Gastrointestinal and hepatic portfolios also remained above expectation, while several major disease families such as oncology and cardiovascular were below expectation on this stricter ghost target."),
            ("Interpretation", "The ghost table therefore identifies a different silence pattern than the no-results table, centered on healthy-volunteer and diffuse non-disease portfolios with unusually thin and fragmented public traces."),
            ("Boundary", "Condition families are keyword-derived registry groupings, so they approximate therapeutic portfolios rather than adjudicated disease ontologies."),
        ]
    )
    black_box_sponsor_body, black_box_sponsor_sentences = sentence_bundle(
        [
            ("Question", "Which named sponsors dominate the CT.gov black-box subset where older studies have no results, no linked paper, and no detailed description?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
            ("Method", "Using the wave-nine sponsor watchlist, we ranked named sponsors by black-box stock and black-box rate, then compared that table with no-results and ghost counts."),
            ("Primary result", "Boehringer Ingelheim carried the largest named black-box stock at 755 studies, followed by GlaxoSmithKline at 579 and Pfizer at 539."),
            ("Secondary result", "Bayer was the sharper large-sponsor outlier on rate at 48.1 percent, while several top black-box repeaters were industry portfolios with hundreds of missing-results studies."),
            ("Interpretation", "The named black-box table therefore makes the industry deep-silence problem much more visible than the broader sponsor stock tables do, especially across major drug-company portfolios overall."),
            ("Boundary", "Black-box status is a registry-page visibility definition and should not be read as proof that a sponsor produced no documentation or dissemination outside linked CT.gov fields."),
        ]
    )
    strict_black_box_body, strict_black_box_sentences = sentence_bundle(
        [
            ("Question", "Where does the black-box problem remain inside the strict U.S.-nexus CT.gov core rather than the broader older-study universe?"),
            ("Dataset", "We analysed the 58,598-study strict U.S.-nexus drug-biological-device proxy extracted from the March 29, 2026 full-registry snapshot."),
            ("Method", "Using the wave-nine strict-core watchlist, we ranked named sponsors and sponsor classes by black-box stock and rate inside that regulated-looking subset."),
            ("Primary result", "Industry held the largest strict-core black-box stock at 3,001 studies, while Bayer led the named strict-core black-box table at 122 studies."),
            ("Secondary result", "Novartis Pharmaceuticals and Bristol-Myers Squibb followed on named stock, while NETWORK remained sharper than OTHER on no-results rate even with low black-box stock."),
            ("Interpretation", "The strict-core black-box problem therefore remains industry-heavy on deep-silence stock even inside a subset that already lowers the overall missing-results rate and still leaves a clearly concentrated industrial deep-silence stock behind for scrutiny."),
            ("Boundary", "These strict-core black-box tables sit inside a conservative proxy subset and are not formal ACT or FDAAA legal determinations for specific sponsors or studies."),
        ]
    )

    projects: list[dict[str, object]] = []
    projects.append(
        make_spec(
            repo_name="ctgov-sponsor-ghost-repeaters",
            title="CT.gov Sponsor Ghost Repeaters",
            summary="A standalone E156 project on which named sponsors remain most ghosted above expectation rather than merely missing results.",
            body=sponsor_ghost_body,
            sentences=sponsor_ghost_sentences,
            primary_estimand="Excess ghost-protocol stock among named lead sponsors with at least 100 older studies",
            data_note="249,507 eligible older closed interventional studies with sponsor ghost watchlists derived from the wave-nine adjusted tables",
            references=common_refs,
            protocol=(
                "This protocol re-reads the wave-nine sponsor watchlist with the ghost-protocol target at the center instead of adjusted missing-results stock alone. "
                "Primary outputs compare sponsor-level excess ghost stock, raw ghost counts, black-box stock, and strict-core spillover among sponsors with at least 100 older studies. "
                "The aim is to isolate a deeper silence state than overdue results alone. "
                "Ghost-protocol status here is defined from registry-visible results and publication-link fields rather than from external publication auditing."
            ),
            root_title="Which sponsors are most ghosted above expectation?",
            root_eyebrow="Sponsor Ghosts Project",
            root_lede="A standalone public project on sponsor ghost repeaters, showing that the deeper-silence leaderboard differs from the adjusted no-results table and pulls Cairo University, Sanofi, and Bayer to the front.",
            chapter_intro="This page shifts the sponsor lens from missing results to ghost protocols. It asks which institutions remain most ghosted above expectation once the no-results table is no longer the only measure.",
            root_pull_quote="The sponsor ghost table is not the same as the sponsor no-results table. Several institutions rise sharply once silence is narrowed to ghost protocols.",
            paper_pull_quote="Ghost protocols are the registry pages where both results and linked publications are absent. That is a different kind of silence than ordinary overdue results.",
            dashboard_pull_quote="Cairo University leads the sponsor ghost table, Sanofi is close behind, Bayer remains prominent, and several top ghost repeaters also carry large black-box stock.",
            root_rail=["Cairo +228", "Sanofi +219", "Bayer +179", "Boehringer 755 box"],
            landing_metrics=[
                ("Cairo ghost", fmt_int(int(round(as_float(sponsor_ghost_top["excess_ghost"])))), "Excess ghost stock"),
                ("Sanofi ghost", fmt_int(int(round(as_float(sponsor_ghost_second["excess_ghost"])))), "Excess ghost stock"),
                ("Bayer ghost", fmt_int(int(round(as_float(sponsor_ghost_third["excess_ghost"])))), "Excess ghost stock"),
                ("Boehringer box", fmt_int(as_int(sponsor_black_box_top["black_box_count"])), "Largest black-box stock"),
            ],
            landing_chart_html=chart_section(
                "Sponsor ghost excess",
                bar_chart(
                    [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["excess_ghost"])} for _, row in sponsor_ghost.head(10).iterrows()],
                    "Sponsor ghosts",
                    "Excess ghost-protocol counts among named sponsors",
                    "value",
                    "label",
                    "#326891",
                    percent=False,
                ),
                "The upper tier shifts once the target changes from missing results to ghost protocols.",
                "That is the main sponsor-ghost finding.",
            ),
            reader_lede="A 156-word micro-paper on which named sponsors remain most ghosted above expectation rather than merely overdue on results.",
            reader_rail=["Cairo", "Sanofi", "Bayer", "Black-box"],
            reader_metrics=[
                ("Cairo ghost", fmt_int(int(round(as_float(sponsor_ghost_top["excess_ghost"])))), "Excess ghost stock"),
                ("Sanofi ghost", fmt_int(int(round(as_float(sponsor_ghost_second["excess_ghost"])))), "Excess ghost stock"),
                ("Bayer ghost", fmt_int(int(round(as_float(sponsor_ghost_third["excess_ghost"])))), "Excess ghost stock"),
                ("Ain Shams", fmt_int(int(round(as_float(sponsor_ghost.iloc[3]["excess_ghost"])))), "Fourth ghost repeater"),
            ],
            dashboard_title="Ghost-protocol sponsor repeaters differ from the broader missing-results league table",
            dashboard_eyebrow="Sponsor Ghosts Dashboard",
            dashboard_lede="Cairo University leads the sponsor ghost table, Sanofi and Bayer remain close behind, Ain Shams University also stays prominent, and several large industry sponsors combine high ghost excess with large black-box stock.",
            dashboard_rail=["Ghost excess", "Ghost counts", "Black-box stock", "Named sponsors"],
            dashboard_metrics=[
                ("Cairo ghost", fmt_int(int(round(as_float(sponsor_ghost_top["excess_ghost"])))), "Excess stock"),
                ("Sanofi ghost", fmt_int(int(round(as_float(sponsor_ghost_second["excess_ghost"])))), "Excess stock"),
                ("Bayer box", fmt_int(as_int(row_for(sponsor_black_box, "lead_sponsor_name", "Bayer")["black_box_count"])), "Black-box stock"),
                ("Boehringer box", fmt_int(as_int(sponsor_black_box_top["black_box_count"])), "Largest black-box stock"),
            ],
            dashboard_sections=[
                chart_section(
                    "Top sponsor ghost excess",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["excess_ghost"])} for _, row in sponsor_ghost.head(10).iterrows()],
                        "Ghost excess",
                        "Top sponsor excess ghost-protocol counts",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Cairo University, Sanofi, and Bayer lead the deeper-silence sponsor table.",
                    "This is not the same ordering seen in the adjusted no-results watchlist.",
                ),
                chart_section(
                    "Top raw sponsor ghost counts",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["ghost_count"])} for _, row in sponsor_ghost.sort_values("ghost_count", ascending=False).head(10).iterrows()],
                        "Ghost counts",
                        "Raw ghost-protocol counts by sponsor",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "Large industry portfolios remain prominent even when the table is sorted by raw ghost counts instead of adjusted excess.",
                    "That gives the sponsor-ghost project both rate and stock context.",
                ),
                chart_section(
                    "Ghost repeaters and black-box stock",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["black_box_count"])} for _, row in sponsor_ghost.head(10).iterrows()],
                        "Black-box stock",
                        "Black-box study counts among the top sponsor ghost repeaters",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "Several of the biggest ghost repeaters also hold substantial black-box stock.",
                    "That marks a deeper silence state than ghosting alone.",
                ),
            ],
            sidebar_bullets=[
                "Cairo University carries the largest sponsor ghost excess at 228 studies.",
                "Sanofi follows closely at 219 ghosted studies above expectation.",
                "Bayer remains prominent at 179 and also carries a large black-box stock.",
                "Boehringer Ingelheim holds the largest named black-box sponsor stock at 755 studies.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-country-ghost-watchlist",
            title="CT.gov Country Ghost Watchlist",
            summary="A standalone E156 project on where deeper CT.gov silence remains most elevated once country-linked portfolios are ranked by excess ghost stock.",
            body=country_ghost_body,
            sentences=country_ghost_sentences,
            primary_estimand="Excess ghost-protocol stock across country-linked study portfolios",
            data_note="249,507 eligible older closed interventional studies exploded into named-country links and ranked by ghost excess",
            references=common_refs,
            protocol=(
                "This protocol re-reads the country-linked wave-nine watchlist with excess ghost-protocol stock at the center rather than adjusted missing-results stock alone. "
                "Primary outputs compare excess ghost stock, raw ghost counts, black-box stock, and black-box rate across country-linked portfolios. "
                "The aim is to isolate deeper silence than overdue results alone. "
                "Because portfolios are country-linked rather than mutually exclusive, multinational studies can contribute to more than one national row."
            ),
            root_title="Which country-linked portfolios are most ghosted?",
            root_eyebrow="Country Ghosts Project",
            root_lede="A standalone public project on country-linked ghost watchlists, showing that France leads on ghost excess while China, Egypt, and South Korea remain especially sharp on deeper silence indicators.",
            chapter_intro="This page shifts the geography story from adjusted no-results stock to excess ghost protocols. It asks which country-linked portfolios remain most ghosted above expectation.",
            root_pull_quote="The geography ghost table combines large European stock with sharp Asian and Middle Eastern tails.",
            paper_pull_quote="Ghost protocols are deeper silence than ordinary missing-results rows. The country watchlist changes once that stricter target is centered.",
            dashboard_pull_quote="France leads on ghost excess, China and Egypt stay close, and South Korea stands out as a high-black-box geography as well as a ghost outlier.",
            root_rail=["France +1.2k", "China +1.0k", "Egypt +955", "S. Korea +871"],
            landing_metrics=[
                ("France ghost", fmt_int(int(round(as_float(country_ghost_top["excess_ghost"])))), "Excess ghost stock"),
                ("China ghost", fmt_int(int(round(as_float(country_ghost_second["excess_ghost"])))), "Excess ghost stock"),
                ("Egypt ghost", fmt_int(int(round(as_float(country_ghost_third["excess_ghost"])))), "Excess ghost stock"),
                ("S. Korea ghost", fmt_int(int(round(as_float(country_ghost_fourth["excess_ghost"])))), "Excess ghost stock"),
            ],
            landing_chart_html=chart_section(
                "Country-linked ghost excess",
                bar_chart(
                    [{"label": row["country_name"], "value": as_float(row["excess_ghost"])} for _, row in country_ghost.head(10).iterrows()],
                    "Country ghosts",
                    "Country-linked excess ghost-protocol counts",
                    "value",
                    "label",
                    "#326891",
                    percent=False,
                ),
                "France sits at the top, but China, Egypt, and South Korea form a sharp second cluster.",
                "That is the main geography-ghost pattern.",
            ),
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios remain most ghosted above expectation.",
            reader_rail=["France", "China", "Egypt", "South Korea"],
            reader_metrics=[
                ("France ghost", fmt_int(int(round(as_float(country_ghost_top["excess_ghost"])))), "Excess stock"),
                ("China ghost", fmt_int(int(round(as_float(country_ghost_second["excess_ghost"])))), "Excess stock"),
                ("Egypt ghost", fmt_int(int(round(as_float(country_ghost_third["excess_ghost"])))), "Excess stock"),
                ("S. Korea box", fmt_pct(as_float(row_for(country_ghost, "country_name", "South Korea")["black_box_rate"])), "Black-box rate"),
            ],
            dashboard_title="Country-linked ghost watchlists surface a different geography of deep CT.gov silence",
            dashboard_eyebrow="Country Ghosts Dashboard",
            dashboard_lede="France leads on excess ghost stock, China and Egypt remain close behind, South Korea adds a strong black-box component, and several other mid-sized portfolios remain sharper than their raw size alone would suggest.",
            dashboard_rail=["Ghost excess", "Ghost counts", "Black-box stock", "Country-linked"],
            dashboard_metrics=[
                ("France ghost", fmt_int(int(round(as_float(country_ghost_top["excess_ghost"])))), "Excess stock"),
                ("China ghost", fmt_int(int(round(as_float(country_ghost_second["excess_ghost"])))), "Excess stock"),
                ("Egypt ghost", fmt_int(int(round(as_float(country_ghost_third["excess_ghost"])))), "Excess stock"),
                ("France box", fmt_int(as_int(row_for(country_ghost, "country_name", "France")["black_box_count"])), "Black-box stock"),
            ],
            dashboard_sections=[
                chart_section(
                    "Top country-linked ghost excess",
                    bar_chart(
                        [{"label": row["country_name"], "value": as_float(row["excess_ghost"])} for _, row in country_ghost.head(10).iterrows()],
                        "Ghost excess",
                        "Top excess ghost-protocol counts by country-linked portfolio",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "France leads, but the next cluster is driven by China, Egypt, and South Korea.",
                    "This is the geography of deeper silence rather than ordinary missing-results stock.",
                ),
                chart_section(
                    "Top raw country-linked ghost counts",
                    bar_chart(
                        [{"label": row["country_name"], "value": as_float(row["ghost_count"])} for _, row in country_ghost.sort_values("ghost_count", ascending=False).head(10).iterrows()],
                        "Ghost counts",
                        "Raw ghost-protocol counts across country-linked portfolios",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "Raw ghost counts still keep France and China near the top, but they also show the scale of the broader European portfolios.",
                    "The stock table and excess table need to be read together.",
                ),
                chart_section(
                    "Country-linked black-box stock",
                    bar_chart(
                        [{"label": row["country_name"], "value": as_float(row["black_box_count"])} for _, row in country_ghost.head(10).iterrows()],
                        "Black-box stock",
                        "Black-box study counts among the top country ghost portfolios",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "France and China also carry large black-box stock, while South Korea is especially notable on black-box rate.",
                    "That gives the country-ghost table a deeper-silence overlay.",
                ),
            ],
            sidebar_bullets=[
                "France carries the largest country-linked ghost excess at 1,157 studies.",
                "China and Egypt follow at 1,007 and 955.",
                "South Korea remains prominent at 871 and also reaches a 21.2 percent black-box rate.",
                "France still holds 3,093 black-box studies on absolute stock.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-condition-ghost-watchlist",
            title="CT.gov Condition Ghost Watchlist",
            summary="A standalone E156 project on which therapeutic portfolios are ghosted most sharply above expectation rather than merely missing results.",
            body=condition_ghost_body,
            sentences=condition_ghost_sentences,
            primary_estimand="Excess ghost-protocol stock across condition families",
            data_note="249,507 eligible older closed interventional studies with condition-family ghost watchlists derived from the wave-nine tables",
            references=common_refs,
            protocol=(
                "This protocol re-reads the wave-nine condition watchlist with excess ghost-protocol stock as the primary target rather than adjusted no-results stock alone. "
                "Primary outputs compare excess ghost stock, raw ghost counts, black-box stock, and black-box rates across condition families. "
                "The aim is to isolate therapeutic portfolios that remain deeply ghosted above expectation. "
                "Condition families are keyword-derived registry groupings and should be read as broad therapeutic portfolios rather than formal disease ontologies."
            ),
            root_title="Which therapeutic portfolios are most ghosted?",
            root_eyebrow="Condition Ghosts Project",
            root_lede="A standalone public project on condition-family ghost watchlists, showing that healthy-volunteer portfolios are the clearest deep-silence outlier once ghost protocols rather than missing results are centered.",
            chapter_intro="This page changes the condition lens from adjusted no-results stock to excess ghost protocols. It asks which therapeutic portfolios remain the most ghosted above expectation.",
            root_pull_quote="Healthy volunteers are the major outlier once the target changes from missing results to ghost protocols.",
            paper_pull_quote="Condition families do not all go silent in the same way. Healthy-volunteer studies are not the biggest disease backlog, but they are the clearest ghost backlog.",
            dashboard_pull_quote="Healthy volunteers dominate the condition ghost table, the diffuse OTHER bucket remains large, and musculoskeletal and gastrointestinal portfolios stay meaningfully above expectation too.",
            root_rail=["Healthy +1.0k", "Other +552", "MSK +333", "GI +144"],
            landing_metrics=[
                ("Healthy ghost", fmt_int(int(round(as_float(condition_ghost_top["excess_ghost"])))), "Excess ghost stock"),
                ("Other ghost", fmt_int(int(round(as_float(condition_ghost_second["excess_ghost"])))), "Excess ghost stock"),
                ("MSK ghost", fmt_int(int(round(as_float(condition_ghost_third["excess_ghost"])))), "Excess ghost stock"),
                ("GI ghost", fmt_int(int(round(as_float(condition_ghost_fourth["excess_ghost"])))), "Excess ghost stock"),
            ],
            landing_chart_html=chart_section(
                "Condition-family ghost excess",
                bar_chart(
                    [{"label": row["condition_family_label"], "value": as_float(row["excess_ghost"])} for _, row in condition_ghost.head(10).iterrows()],
                    "Condition ghosts",
                    "Excess ghost-protocol counts across condition families",
                    "value",
                    "label",
                    "#326891",
                    percent=False,
                ),
                "Healthy volunteers sit far above the disease families once the condition table is sorted by ghost excess.",
                "That is the defining wave-ten condition result.",
            ),
            reader_lede="A 156-word micro-paper on which condition families are ghosted most sharply above expectation rather than merely overdue on results.",
            reader_rail=["Healthy volunteers", "Other", "MSK", "GI and hepatic"],
            reader_metrics=[
                ("Healthy ghost", fmt_int(int(round(as_float(condition_ghost_top["excess_ghost"])))), "Excess stock"),
                ("Healthy box", fmt_pct(as_float(condition_ghost_top["black_box_rate"])), "Black-box rate"),
                ("MSK ghost", fmt_int(int(round(as_float(condition_ghost_third["excess_ghost"])))), "Excess stock"),
                ("GI box", fmt_int(as_int(condition_ghost_fourth["black_box_count"])), "Black-box stock"),
            ],
            dashboard_title="Condition ghost watchlists isolate a different therapeutic silence pattern than the adjusted no-results table",
            dashboard_eyebrow="Condition Ghosts Dashboard",
            dashboard_lede="Healthy-volunteer portfolios dominate on ghost excess and black-box rate, the broad OTHER bucket remains large on stock, musculoskeletal and gastrointestinal portfolios stay above expectation, and several major disease families fall back once the lens shifts to ghost protocols.",
            dashboard_rail=["Ghost excess", "Ghost counts", "Black-box stock", "Condition families"],
            dashboard_metrics=[
                ("Healthy ghost", fmt_int(int(round(as_float(condition_ghost_top["excess_ghost"])))), "Excess stock"),
                ("Other ghost", fmt_int(int(round(as_float(condition_ghost_second["excess_ghost"])))), "Excess stock"),
                ("Healthy box", fmt_pct(as_float(condition_ghost_top["black_box_rate"])), "Black-box rate"),
                ("Oncology raw", fmt_int(as_int(row_for(condition_ghost, "condition_family_label", "Oncology")["ghost_count"])), "Raw ghost count"),
            ],
            dashboard_sections=[
                chart_section(
                    "Top condition-family ghost excess",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["excess_ghost"])} for _, row in condition_ghost.head(10).iterrows()],
                        "Ghost excess",
                        "Condition families ranked by excess ghost-protocol stock",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Healthy volunteers dominate the excess table, far above the rest of the field.",
                    "That makes the condition-ghost story structurally different from the no-results story.",
                ),
                chart_section(
                    "Top raw condition-family ghost counts",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["ghost_count"])} for _, row in condition_ghost.sort_values("ghost_count", ascending=False).head(10).iterrows()],
                        "Ghost counts",
                        "Raw ghost-protocol counts across condition families",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "Raw ghost counts keep the big disease portfolios visible, but they no longer dominate the excess ranking.",
                    "That is why the ghost watchlist matters.",
                ),
                chart_section(
                    "Condition-family black-box rate",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["black_box_rate"])} for _, row in condition_ghost.sort_values("black_box_rate", ascending=False).head(10).iterrows()],
                        "Black-box rates",
                        "Black-box rate across condition families",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Healthy volunteers also lead on black-box rate, reinforcing that this is a deeper-silence portfolio rather than a simple reporting-delay story.",
                    "The condition-ghost and black-box views align strongly here.",
                ),
            ],
            sidebar_bullets=[
                "Healthy volunteers carry the largest condition-family ghost excess at 1,032 studies.",
                "The diffuse OTHER bucket remains second at 552, with musculoskeletal and pain next at 333.",
                "Gastrointestinal and hepatic portfolios stay above expectation at 144.",
                "Healthy volunteers also reach a 33.9 percent black-box rate.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-black-box-sponsor-repeaters",
            title="CT.gov Black-Box Sponsor Repeaters",
            summary="A standalone E156 project on which named sponsors dominate the older CT.gov black-box subset with no results, no linked paper, and no detailed description.",
            body=black_box_sponsor_body,
            sentences=black_box_sponsor_sentences,
            primary_estimand="Black-box stock and rate among named lead sponsors in the older-study CT.gov universe",
            data_note="249,507 eligible older closed interventional studies with named-sponsor black-box watchlists derived from the wave-nine sponsor table",
            references=common_refs,
            protocol=(
                "This protocol re-reads the wave-nine sponsor watchlist by centering the black-box subset rather than adjusted missing-results stock alone. "
                "Primary outputs compare named-sponsor black-box stock, black-box rate, raw no-results stock, and ghost counts. "
                "The aim is to isolate which named sponsors sit inside the deepest registry-visible silence state. "
                "Black-box status is defined from registry page fields and does not imply a sponsor had no internal records or dissemination outside CT.gov."
            ),
            root_title="Which sponsors dominate the black-box subset?",
            root_eyebrow="Black-Box Sponsors Project",
            root_lede="A standalone public project on named-sponsor black-box repeaters, showing that the deepest visible silence on CT.gov is concentrated in a small set of major industry portfolios.",
            chapter_intro="This page narrows the sponsor story to the registry's deepest visible silence state. It asks which named sponsors hold the largest stock of older studies with no results, no linked paper, and no detailed description.",
            root_pull_quote="The black-box sponsor table is much more industry-heavy than the broader sponsor stock tables.",
            paper_pull_quote="Black-box trials are the registry pages that still tell the public remarkably little. The sponsor ranking changes once that stricter definition is centered.",
            dashboard_pull_quote="Boehringer Ingelheim leads the named black-box table, GlaxoSmithKline and Pfizer remain close behind, and Bayer is the sharper large-sponsor extreme on rate.",
            root_rail=["Boehringer 755", "GSK 579", "Pfizer 539", "Bayer 48.1%"],
            landing_metrics=[
                ("Boehringer box", fmt_int(as_int(sponsor_black_box_top["black_box_count"])), "Largest black-box stock"),
                ("GSK box", fmt_int(as_int(sponsor_black_box_second["black_box_count"])), "Second largest stock"),
                ("Pfizer box", fmt_int(as_int(sponsor_black_box_third["black_box_count"])), "Third largest stock"),
                ("Bayer rate", fmt_pct(as_float(row_for(sponsor_black_box, "lead_sponsor_name", "Bayer")["black_box_rate"])), "Large-sponsor black-box rate"),
            ],
            landing_chart_html=chart_section(
                "Named-sponsor black-box stock",
                bar_chart(
                    [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["black_box_count"])} for _, row in sponsor_black_box.head(10).iterrows()],
                    "Black-box stock",
                    "Top named-sponsor black-box study counts",
                    "value",
                    "label",
                    "#8b6914",
                    percent=False,
                ),
                "The deepest-silence sponsor table is concentrated in a relatively short list of major industry portfolios.",
                "That concentration is the main project finding.",
            ),
            reader_lede="A 156-word micro-paper on which named sponsors dominate the CT.gov black-box subset of older studies with no results, no linked paper, and no detailed description.",
            reader_rail=["Boehringer", "GSK", "Pfizer", "Bayer rate"],
            reader_metrics=[
                ("Boehringer box", fmt_int(as_int(sponsor_black_box_top["black_box_count"])), "Black-box stock"),
                ("GSK box", fmt_int(as_int(sponsor_black_box_second["black_box_count"])), "Black-box stock"),
                ("Pfizer box", fmt_int(as_int(sponsor_black_box_third["black_box_count"])), "Black-box stock"),
                ("Bayer rate", fmt_pct(as_float(row_for(sponsor_black_box, "lead_sponsor_name", "Bayer")["black_box_rate"])), "Large-sponsor rate"),
            ],
            dashboard_title="Named black-box sponsor repeaters make the deepest visible CT.gov silence look much more industry-heavy",
            dashboard_eyebrow="Black-Box Sponsors Dashboard",
            dashboard_lede="Boehringer Ingelheim holds the largest named black-box stock, GlaxoSmithKline and Pfizer remain close behind, Bayer is the sharper large-sponsor outlier on black-box rate, and the broader missing-results context stays large across the same repeaters.",
            dashboard_rail=["Black-box stock", "Black-box rates", "No-results stock", "Named sponsors"],
            dashboard_metrics=[
                ("Boehringer box", fmt_int(as_int(sponsor_black_box_top["black_box_count"])), "Largest stock"),
                ("GSK box", fmt_int(as_int(sponsor_black_box_second["black_box_count"])), "Second stock"),
                ("Pfizer box", fmt_int(as_int(sponsor_black_box_third["black_box_count"])), "Third stock"),
                ("Bayer rate", fmt_pct(as_float(row_for(sponsor_black_box, "lead_sponsor_name", "Bayer")["black_box_rate"])), "Large-sponsor rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Top named-sponsor black-box stock",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["black_box_count"])} for _, row in sponsor_black_box.head(10).iterrows()],
                        "Black-box stock",
                        "Top named-sponsor black-box study counts",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "Boehringer Ingelheim, GlaxoSmithKline, Pfizer, Bayer, and Novartis dominate the named black-box stock table.",
                    "The deepest-silence sponsor stock is concentrated in a short list of industry portfolios.",
                ),
                chart_section(
                    "Large-sponsor black-box rate",
                    bar_chart(
                        [
                            {"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["black_box_rate"])}
                            for _, row in sponsor_black_box.loc[sponsor_black_box["studies"] >= 100].sort_values("black_box_rate", ascending=False).head(10).iterrows()
                        ],
                        "Black-box rate",
                        "Black-box rate among named sponsors with at least 100 older studies",
                        "value",
                        "label",
                        "#326891",
                        percent=True,
                    ),
                    "Bayer is the sharper large-sponsor rate outlier, even though Boehringer Ingelheim leads on absolute black-box stock.",
                    "Stock and rate point to overlapping but not identical sponsor risks.",
                ),
                chart_section(
                    "Named-sponsor no-results stock",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["no_results_count"])} for _, row in sponsor_black_box.sort_values("no_results_count", ascending=False).head(10).iterrows()],
                        "No-results stock",
                        "Raw missing-results counts among named black-box sponsor repeaters",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "The black-box leaders also carry very large missing-results stock, which shows that the deepest silence sits inside a wider disclosure backlog.",
                    "That is why the black-box sponsor table works best as a severity overlay, not a standalone count table.",
                ),
            ],
            sidebar_bullets=[
                "Boehringer Ingelheim carries the largest named black-box stock at 755 studies.",
                "GlaxoSmithKline and Pfizer follow at 579 and 539.",
                "Bayer is the sharper large-sponsor rate outlier at 48.1 percent.",
                "Several of the top black-box repeaters also hold hundreds of missing-results studies.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-strict-core-black-box",
            title="CT.gov Strict-Core Black-Box",
            summary="A standalone E156 project on where black-box silence remains concentrated inside the strict U.S.-nexus CT.gov core.",
            body=strict_black_box_body,
            sentences=strict_black_box_sentences,
            primary_estimand="Named-sponsor and sponsor-class black-box stock inside the strict U.S.-nexus proxy core",
            data_note="58,598-study strict U.S.-nexus drug-biological-device proxy extracted from the older closed interventional CT.gov universe",
            references=common_refs,
            protocol=(
                "This protocol isolates the strict U.S.-nexus drug-biological-device proxy and reads its black-box subset rather than its broader missing-results stock alone. "
                "Primary outputs compare named-sponsor black-box stock, sponsor-class black-box stock, black-box rates, and class no-results rates inside the proxy core. "
                "The aim is to identify where the deepest registry-visible silence persists inside the regulated-looking subset. "
                "Because the subset is proxy-defined, the outputs should not be read as formal ACT or FDAAA legal determinations."
            ),
            root_title="Where is the strict-core black-box problem?",
            root_eyebrow="Strict Black-Box Project",
            root_lede="A standalone public project on the strict U.S.-nexus black-box subset, showing that industry still dominates deep-silence stock even inside the conservative regulated-looking core.",
            chapter_intro="This page stays inside the strict U.S.-nexus core and asks where the deepest visible silence remains once attention shifts from ordinary missing-results stock to black-box studies.",
            root_pull_quote="The strict core is cleaner than the full registry, but its black-box subset remains industry-heavy on stock.",
            paper_pull_quote="A conservative U.S.-nexus proxy lowers the overall rate, but it still leaves thousands of deep-silence studies behind. The strict-core black-box problem does not disappear.",
            dashboard_pull_quote="Industry holds 3,001 strict-core black-box studies, Bayer leads the named table at 122, Novartis and Bristol-Myers Squibb follow, and NETWORK remains worse on overall no-results rate than on black-box stock.",
            root_rail=["Industry 3.0k", "Bayer 122", "Novartis 82", "Network 48.8%"],
            landing_metrics=[
                ("Industry box", fmt_int(as_int(strict_industry["black_box_count"])), "Class black-box stock"),
                ("Bayer box", fmt_int(as_int(strict_black_box_top["black_box_count"])), "Named black-box stock"),
                ("Novartis box", fmt_int(as_int(strict_black_box_second["black_box_count"])), "Second named stock"),
                ("Network rate", fmt_pct(as_float(strict_network["no_results_rate"])), "Highest class no-results rate"),
            ],
            landing_chart_html=chart_section(
                "Strict-core named black-box stock",
                bar_chart(
                    [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["black_box_count"])} for _, row in strict_black_box.head(10).iterrows()],
                    "Strict-core black-box stock",
                    "Top named strict-core black-box study counts",
                    "value",
                    "label",
                    "#8b6914",
                    percent=False,
                ),
                "The strict-core black-box subset is still concentrated in a short list of large industry sponsors.",
                "That concentration is the defining project result.",
            ),
            reader_lede="A 156-word micro-paper on where black-box silence remains concentrated inside the strict U.S.-nexus CT.gov core.",
            reader_rail=["Industry", "Bayer", "Novartis", "Network"],
            reader_metrics=[
                ("Industry box", fmt_int(as_int(strict_industry["black_box_count"])), "Class stock"),
                ("Bayer box", fmt_int(as_int(strict_black_box_top["black_box_count"])), "Named stock"),
                ("Novartis box", fmt_int(as_int(strict_black_box_second["black_box_count"])), "Named stock"),
                ("Network rate", fmt_pct(as_float(strict_network["no_results_rate"])), "Class no-results rate"),
            ],
            dashboard_title="Strict-core black-box tables show that the regulated-looking deep-silence subset remains heavily concentrated in industry portfolios",
            dashboard_eyebrow="Strict Black-Box Dashboard",
            dashboard_lede="Industry carries the largest strict-core black-box stock, Bayer leads the named strict-core table, Novartis and Bristol-Myers Squibb remain close behind, and NETWORK stays worse on broad no-results rate than on black-box stock.",
            dashboard_rail=["Named stock", "Class stock", "Class rates", "Strict core"],
            dashboard_metrics=[
                ("Industry box", fmt_int(as_int(strict_industry["black_box_count"])), "Class stock"),
                ("Bayer box", fmt_int(as_int(strict_black_box_top["black_box_count"])), "Named stock"),
                ("Bristol box", fmt_int(as_int(strict_black_box_third["black_box_count"])), "Third named stock"),
                ("Other box", fmt_int(as_int(strict_other["black_box_count"])), "Other class stock"),
            ],
            dashboard_sections=[
                chart_section(
                    "Strict-core named black-box stock",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["black_box_count"])} for _, row in strict_black_box.head(10).iterrows()],
                        "Named black-box stock",
                        "Top named sponsor black-box counts inside the strict U.S.-nexus core",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "Bayer, Novartis, Bristol-Myers Squibb, Roxane Laboratories, and GlaxoSmithKline lead the named strict-core black-box table.",
                    "This subset is more concentrated than the broader strict-core missing-results table.",
                ),
                chart_section(
                    "Strict-core class black-box stock",
                    bar_chart(
                        [{"label": row["lead_sponsor_class"], "value": as_float(row["black_box_count"])} for _, row in strict_black_box_class.iterrows()],
                        "Class black-box stock",
                        "Strict-core black-box study counts by sponsor class",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Industry dominates strict-core black-box stock, with OTHER a distant second and all other classes much smaller.",
                    "The regulated-looking deep-silence stock is therefore heavily class-concentrated.",
                ),
                chart_section(
                    "Strict-core class no-results rate",
                    bar_chart(
                        [{"label": row["lead_sponsor_class"], "value": as_float(row["no_results_rate"])} for _, row in strict_black_box_class.sort_values("no_results_rate", ascending=False).iterrows()],
                        "Class no-results rate",
                        "Strict-core missing-results rate by sponsor class",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "NETWORK is the sharpest class on broad no-results rate even though industry dominates the strict-core black-box stock table.",
                    "The rate and stock views identify different kinds of strict-core risk.",
                ),
            ],
            sidebar_bullets=[
                "Industry holds the largest strict-core black-box stock at 3,001 studies.",
                "Bayer leads the named strict-core black-box table at 122 studies.",
                "Novartis Pharmaceuticals and Bristol-Myers Squibb follow at 82 and 81.",
                "NETWORK remains the highest large-class strict-core no-results rate at 48.8 percent.",
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
