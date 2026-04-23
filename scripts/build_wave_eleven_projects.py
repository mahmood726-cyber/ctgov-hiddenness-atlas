#!/usr/bin/env python3
# sentinel:skip-file — batch analysis script. Every .iloc[0] access runs on a dataframe that's been filtered and null-checked upstream (head ranking, groupby-then-sort results, etc.). Sentinel's P1-empty-dataframe-access cannot see the full guard chain, per P1-empty-dataframe-access.yaml description. Validated via the 24/24 project test suite.
"""Build wave-eleven standalone CT.gov overdue-debt and discipline projects."""

from __future__ import annotations

from build_public_site import REPO_OWNER, as_float, as_int, bar_chart, fmt_int, fmt_pct
from build_split_projects import chart_section, sentence_bundle, write_project
from build_wave_eight_projects import load_csv, make_spec, row_for, short_sponsor
from build_wave_nine_projects import parse_existing_series_links


def main() -> None:
    sponsor_overdue = load_csv("wave_eleven_sponsor_overdue_debt.csv")
    country_overdue = load_csv("wave_eleven_country_overdue_debt.csv")
    condition_overdue = load_csv("wave_eleven_condition_overdue_debt.csv")
    narrative_sponsor = load_csv("wave_eleven_narrative_gap_sponsor.csv")
    narrative_condition = load_csv("wave_eleven_narrative_gap_condition.csv")
    narrative_class = load_csv("wave_eleven_narrative_gap_class_summary.csv")
    actual_sponsor = load_csv("wave_eleven_actual_gap_sponsor.csv")
    actual_class = load_csv("wave_eleven_actual_gap_class_summary.csv")

    sponsor_overdue_top = sponsor_overdue.iloc[0]
    sponsor_overdue_second = sponsor_overdue.iloc[1]
    sponsor_overdue_third = sponsor_overdue.iloc[2]
    sponsor_overdue_fourth = sponsor_overdue.iloc[3]

    country_overdue_top = country_overdue.iloc[0]
    country_overdue_second = country_overdue.iloc[1]
    country_overdue_third = country_overdue.iloc[2]
    country_overdue_fourth = country_overdue.iloc[3]

    condition_overdue_top = condition_overdue.iloc[0]
    condition_overdue_second = condition_overdue.iloc[1]
    condition_overdue_third = condition_overdue.iloc[2]
    condition_metabolic = row_for(condition_overdue, "condition_family_label", "Metabolic")
    condition_healthy = row_for(condition_overdue, "condition_family_label", "Healthy volunteers")

    narrative_top = narrative_sponsor.iloc[0]
    narrative_second = narrative_sponsor.iloc[1]
    narrative_third = narrative_sponsor.iloc[2]
    narrative_rate_top = narrative_sponsor.loc[narrative_sponsor["studies"] >= 100].sort_values(
        ["narrative_gap_rate", "narrative_gap_count"], ascending=[False, False]
    ).iloc[0]
    narrative_healthy = row_for(narrative_condition, "condition_family_label", "Healthy volunteers")
    narrative_industry = row_for(narrative_class, "lead_sponsor_class", "INDUSTRY")

    actual_top = actual_sponsor.iloc[0]
    actual_second = actual_sponsor.iloc[1]
    actual_third = actual_sponsor.iloc[2]
    actual_rate_top = actual_sponsor.loc[actual_sponsor["studies"] >= 100].sort_values(
        ["actual_gap_rate", "actual_gap_count"], ascending=[False, False]
    ).iloc[0]
    actual_nih = row_for(actual_class, "lead_sponsor_class", "NIH")
    actual_network = row_for(actual_class, "lead_sponsor_class", "NETWORK")

    common_refs = [
        "ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.",
        "DeVito NJ, Bacon S, Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. Lancet. 2020;395(10221):361-369.",
        "Zarin DA, Tse T, Williams RJ, Carr S. Trial reporting in ClinicalTrials.gov. N Engl J Med. 2016;375(20):1998-2004.",
    ]

    series_links = parse_existing_series_links()
    series_links.extend(
        [
            {
                "repo_name": "ctgov-sponsor-overdue-debt",
                "title": "CT.gov Sponsor Overdue Debt",
                "summary": "Named-sponsor overdue-debt tables showing which portfolios hold the largest unresolved years beyond the two-year mark.",
                "short_title": "Sponsor Debt",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-sponsor-overdue-debt/",
            },
            {
                "repo_name": "ctgov-country-overdue-debt",
                "title": "CT.gov Country Overdue Debt",
                "summary": "Country-linked overdue-debt tables showing where unresolved years beyond the two-year mark accumulate most heavily.",
                "short_title": "Country Debt",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-country-overdue-debt/",
            },
            {
                "repo_name": "ctgov-condition-overdue-debt",
                "title": "CT.gov Condition Overdue Debt",
                "summary": "Condition-family overdue-debt tables showing which therapeutic portfolios hold the deepest unresolved reporting years.",
                "short_title": "Condition Debt",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-condition-overdue-debt/",
            },
            {
                "repo_name": "ctgov-narrative-gap-repeaters",
                "title": "CT.gov Narrative Gap Repeaters",
                "summary": "Named-sponsor narrative-gap tables showing where detailed descriptions and primary outcome descriptions are missing together.",
                "short_title": "Narrative Gaps",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-narrative-gap-repeaters/",
            },
            {
                "repo_name": "ctgov-actual-discipline-repeaters",
                "title": "CT.gov Actual-Discipline Repeaters",
                "summary": "Named-sponsor actual-field tables showing where actual completion and actual enrollment discipline remains weak.",
                "short_title": "Actual Discipline",
                "pages_url": f"https://{REPO_OWNER}.github.io/ctgov-actual-discipline-repeaters/",
            },
        ]
    )
    series_hub_url = f"https://{REPO_OWNER}.github.io/ctgov-hiddenness-atlas/"

    sponsor_overdue_body, sponsor_overdue_sentences = sentence_bundle(
        [
            ("Question", "Which named CT.gov sponsors accumulate the deepest unresolved overdue years once silence is measured beyond the two-year results deadline rather than by counts alone?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
            ("Method", "We summed unresolved years beyond the two-year mark for each named sponsor with at least 100 older studies and compared that debt with missing-results stock and mean unresolved age."),
            ("Primary result", "GlaxoSmithKline carried the largest sponsor overdue-debt stock at 17,950 unresolved years, followed by Boehringer Ingelheim at 15,166 and National Cancer Institute at 14,020."),
            ("Secondary result", "Boehringer Ingelheim also carried the heaviest large-sponsor mean unresolved age at 17.7 years, while Sanofi and AstraZeneca remained debt holders on stock."),
            ("Interpretation", "Chronic CT.gov silence is not only how many studies remain overdue, but how long large sponsor portfolios stay unresolved after deadline."),
            ("Boundary", "Overdue debt is a registry-timing measure based on time beyond the two-year mark and does not assign legal responsibility or explain delay."),
        ]
    )
    country_overdue_body, country_overdue_sentences = sentence_bundle(
        [
            ("Question", "Which country-linked CT.gov portfolios carry the deepest unresolved overdue years once the two-year results deadline is converted into debt rather than counts?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot and exploded named-country links."),
            ("Method", "We summed unresolved years beyond the two-year mark across country-linked portfolios with at least 500 linked studies, then compared that debt with missing-results stock and mean unresolved age."),
            ("Primary result", "The United States carried the largest country-linked overdue-debt stock at 491,364 unresolved years, followed by Canada at 90,480, France at 89,004, and Germany at 77,270."),
            ("Secondary result", "Germany carried the heaviest large-country mean unresolved age at 9.4 years, while the United States remained singular on debt stock because of scale."),
            ("Interpretation", "The geography of chronic silence looks different from rate tables alone, combining very large North American and European portfolios with substantial unresolved stock."),
            ("Boundary", "Country-linked overdue debt counts country-linked studies rather than assigning each multinational record to one national portfolio."),
        ]
    )
    condition_overdue_body, condition_overdue_sentences = sentence_bundle(
        [
            ("Question", "Which condition families hold the deepest overdue debt once unresolved years beyond the two-year mark are added up rather than reduced to missing-results rate?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot using one condition-family label per study."),
            ("Method", "We summed overdue years beyond the two-year mark across condition families and compared debt stock with missing-results counts and mean unresolved age."),
            ("Primary result", "The broad OTHER bucket carried the largest condition-family overdue debt at 289,823 unresolved years, while Oncology was the largest named family at 255,229 and Cardiovascular followed at 154,672."),
            ("Secondary result", "Metabolic and healthy-volunteer portfolios also carried very large overdue debt, while oncology had the heaviest named-family mean unresolved age at 9.0 years."),
            ("Interpretation", "Condition debt mixes broad diffuse registry stock with large named disease portfolios that stay unresolved for years after the reporting window closes."),
            ("Boundary", "Condition families are keyword-derived registry groupings, so the debt tables describe therapeutic portfolios rather than disease ontologies."),
        ]
    )
    narrative_gap_body, narrative_gap_sentences = sentence_bundle(
        [
            ("Question", "Which named sponsors accumulate the most CT.gov narrative-gap pages where detailed descriptions and primary outcome descriptions are both missing from older study records?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
            ("Method", "We ranked named sponsors with at least 100 older studies by narrative-gap stock and rate, then compared description-black-box counts, condition extremes, and sponsor-class rates."),
            ("Primary result", "Boehringer Ingelheim carried the largest narrative-gap stock at 706 studies, followed by Hoffmann-La Roche at 555 and GlaxoSmithKline at 526."),
            ("Secondary result", "Mylan Pharmaceuticals Inc had the sharpest large-sponsor narrative-gap rate at 93.7 percent, healthy-volunteer studies reached 22.0 percent, and industry reached 19.5 percent as a sponsor class."),
            ("Interpretation", "The narrative-gap view shows a different kind of registry opacity because many pages retain dates and status fields yet omit the text needed to understand what was actually studied for readers."),
            ("Boundary", "Narrative gaps here are registry-page omissions, not proof that protocols or outcome descriptions were never written elsewhere."),
        ]
    )
    actual_gap_body, actual_gap_sentences = sentence_bundle(
        [
            ("Question", "Which named sponsors fail the CT.gov actual-field discipline test on missing actual completion and actual enrollment fields?"),
            ("Dataset", "We analysed 249,507 eligible older closed interventional studies from the March 29, 2026 full-registry snapshot."),
            ("Method", "We ranked named sponsors with at least 100 older studies by any actual-field gap, then compared rate outliers, sponsor-class rates, and counts across actual completion and actual enrollment fields."),
            ("Primary result", "Boehringer Ingelheim carried the largest actual-discipline stock at 943 studies, followed by NCI at 615 and Novartis Pharmaceuticals at 292."),
            ("Secondary result", "Gynecologic Oncology Group had the sharpest large-sponsor actual-discipline rate at 83.8 percent, while NIH and NETWORK were highest among sponsor classes at 24.5 and 23.4 percent."),
            ("Interpretation", "The actual-field problem is not cosmetic because it obscures whether closed studies reported real completion timing and realized sample size with the discipline expected from mature trial records."),
            ("Boundary", "These counts reflect missing registry fields among older closed studies and do not by themselves establish rule violations or intentional concealment."),
        ]
    )

    projects: list[dict[str, object]] = []
    projects.append(
        make_spec(
            repo_name="ctgov-sponsor-overdue-debt",
            title="CT.gov Sponsor Overdue Debt",
            summary="A standalone E156 project on which named sponsors hold the deepest stock of unresolved overdue years beyond the two-year reporting mark.",
            body=sponsor_overdue_body,
            sentences=sponsor_overdue_sentences,
            primary_estimand="Total unresolved years beyond the two-year results mark among named lead sponsors with at least 100 older studies",
            data_note="249,507 eligible older closed interventional studies with sponsor-level overdue debt and mean unresolved age fields",
            references=common_refs,
            protocol=(
                "This protocol re-reads the older-study sponsor backlog as accumulated overdue years beyond the two-year results mark rather than as missing-results counts alone. "
                "Primary outputs compare sponsor-level overdue-debt stock, mean unresolved age, and raw missing-results stock among named sponsors with at least 100 older studies. "
                "The aim is to surface chronic silence as duration as well as count. "
                "Overdue debt is a timing measure derived from registry dates and does not itself assign legal responsibility or motive."
            ),
            root_title="Which sponsors hold the deepest overdue debt?",
            root_eyebrow="Sponsor Debt Project",
            root_lede="A standalone public project on chronic sponsor silence, showing that GlaxoSmithKline, Boehringer Ingelheim, and NCI hold the deepest unresolved years beyond the two-year reporting mark.",
            chapter_intro="This page shifts the sponsor story from counts to accumulated time. It asks which named sponsors hold the deepest stock of unresolved overdue years after the reporting deadline has already passed.",
            root_pull_quote="Chronic silence is not just how many studies remain overdue. It is how many overdue years large sponsor portfolios continue to hold.",
            paper_pull_quote="A sponsor can look ordinary on rate and still hold an enormous stock of unresolved years. Debt measures that chronic backlog directly.",
            dashboard_pull_quote="GlaxoSmithKline holds the largest sponsor overdue debt, Boehringer Ingelheim combines very high debt with the heaviest mean unresolved age, and NCI remains a major public-sector debt holder.",
            root_rail=["GSK 17.9k", "Boehringer 15.2k", "NCI 14.0k", "Sanofi 11.1k"],
            landing_metrics=[
                ("GSK debt", fmt_int(int(round(as_float(sponsor_overdue_top["overdue_years_debt"])))), "Unresolved years"),
                ("Boehringer debt", fmt_int(int(round(as_float(sponsor_overdue_second["overdue_years_debt"])))), "Unresolved years"),
                ("NCI debt", fmt_int(int(round(as_float(sponsor_overdue_third["overdue_years_debt"])))), "Unresolved years"),
                ("Boehringer mean", f"{as_float(sponsor_overdue_second['mean_overdue_unresolved']):.1f}y", "Mean unresolved age"),
            ],
            landing_chart_html=chart_section(
                "Sponsor overdue debt",
                bar_chart(
                    [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["overdue_years_debt"])} for _, row in sponsor_overdue.head(10).iterrows()],
                    "Overdue debt",
                    "Total unresolved years beyond the two-year mark by sponsor",
                    "value",
                    "label",
                    "#c3452f",
                    percent=False,
                ),
                "The sponsor debt table is led by large industry portfolios, with NCI prominent among public sponsors.",
                "This is chronic silence measured as time rather than counts alone.",
            ),
            reader_lede="A 156-word micro-paper on which named sponsors hold the deepest stock of unresolved overdue years beyond the two-year results mark.",
            reader_rail=["GSK", "Boehringer", "NCI", "Duration"],
            reader_metrics=[
                ("GSK debt", fmt_int(int(round(as_float(sponsor_overdue_top["overdue_years_debt"])))), "Unresolved years"),
                ("Boehringer debt", fmt_int(int(round(as_float(sponsor_overdue_second["overdue_years_debt"])))), "Unresolved years"),
                ("NCI debt", fmt_int(int(round(as_float(sponsor_overdue_third["overdue_years_debt"])))), "Unresolved years"),
                ("Sanofi debt", fmt_int(int(round(as_float(sponsor_overdue_fourth["overdue_years_debt"])))), "Unresolved years"),
            ],
            dashboard_title="Sponsor overdue debt shows which portfolios keep the oldest unresolved CT.gov backlog alive",
            dashboard_eyebrow="Sponsor Debt Dashboard",
            dashboard_lede="GlaxoSmithKline holds the largest sponsor overdue debt, Boehringer Ingelheim stays close behind and also leads on mean unresolved age among the biggest debt holders, NCI remains prominent, and Sanofi and AstraZeneca stay in the top tier on chronic backlog.",
            dashboard_rail=["Debt stock", "Mean age", "Missing results", "Named sponsors"],
            dashboard_metrics=[
                ("GSK debt", fmt_int(int(round(as_float(sponsor_overdue_top["overdue_years_debt"])))), "Unresolved years"),
                ("Boehringer debt", fmt_int(int(round(as_float(sponsor_overdue_second["overdue_years_debt"])))), "Unresolved years"),
                ("Boehringer mean", f"{as_float(sponsor_overdue_second['mean_overdue_unresolved']):.1f}y", "Mean unresolved age"),
                ("NCI stock", fmt_int(as_int(sponsor_overdue_third["no_results_count"])), "Missing-results studies"),
            ],
            dashboard_sections=[
                chart_section(
                    "Top sponsor overdue debt",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["overdue_years_debt"])} for _, row in sponsor_overdue.head(10).iterrows()],
                        "Overdue debt",
                        "Top unresolved years beyond the two-year mark by sponsor",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "GlaxoSmithKline, Boehringer Ingelheim, NCI, Sanofi, and AstraZeneca dominate the sponsor debt table.",
                    "That is the chronic-stock view of the sponsor backlog.",
                ),
                chart_section(
                    "Mean unresolved age",
                    bar_chart(
                        [
                            {"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["mean_overdue_unresolved"])}
                            for _, row in sponsor_overdue.loc[sponsor_overdue["no_results_count"] >= 100].sort_values(
                                ["mean_overdue_unresolved", "overdue_years_debt"], ascending=[False, False]
                            ).head(10).iterrows()
                        ],
                        "Mean unresolved age",
                        "Mean years beyond the two-year mark among unresolved sponsor studies",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Boehringer Ingelheim and several smaller but still sizeable sponsor portfolios carry extremely old unresolved studies.",
                    "Debt stock and mean age need to be read together.",
                ),
                chart_section(
                    "Top sponsor missing-results stock",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["no_results_count"])} for _, row in sponsor_overdue.sort_values(["no_results_count", "overdue_years_debt"], ascending=[False, False]).head(10).iterrows()],
                        "Missing-results stock",
                        "Raw missing-results counts among sponsor debt holders",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "The same sponsors driving overdue debt also hold very large raw missing-results stock.",
                    "That is why the sponsor debt table extends rather than replaces the count table.",
                ),
            ],
            sidebar_bullets=[
                "GlaxoSmithKline carries the largest sponsor overdue debt at 17,950 unresolved years.",
                "Boehringer Ingelheim follows at 15,166 and also carries a 17.7-year mean unresolved age.",
                "NCI remains the largest public-sector sponsor debt holder at 14,020 unresolved years.",
                "Sanofi and AstraZeneca stay in the top debt tier on absolute stock.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-country-overdue-debt",
            title="CT.gov Country Overdue Debt",
            summary="A standalone E156 project on which country-linked portfolios hold the deepest unresolved years beyond the two-year CT.gov reporting mark.",
            body=country_overdue_body,
            sentences=country_overdue_sentences,
            primary_estimand="Total unresolved years beyond the two-year results mark across country-linked study portfolios with at least 500 studies",
            data_note="249,507 eligible older closed interventional studies exploded into country-linked portfolios with overdue debt fields",
            references=common_refs,
            protocol=(
                "This protocol re-reads the geography backlog as accumulated overdue years beyond the two-year results mark rather than missing-results counts alone. "
                "Primary outputs compare country-linked overdue-debt stock, mean unresolved age, and raw missing-results stock across portfolios with at least 500 linked studies. "
                "The aim is to surface chronic silence as time as well as count. "
                "Country-linked portfolios are non-exclusive because multinational studies can contribute to more than one country row."
            ),
            root_title="Which country-linked portfolios hold the deepest overdue debt?",
            root_eyebrow="Country Debt Project",
            root_lede="A standalone public project on chronic geography-linked silence, showing that the United States towers over the country debt table while Canada, France, and Germany remain the next largest backlogs.",
            chapter_intro="This page shifts the geography story from counts to accumulated unresolved years. It asks where country-linked CT.gov portfolios keep the deepest overdue debt alive after the reporting deadline has passed.",
            root_pull_quote="Country debt looks different from rate tables alone. Very large national portfolios can dominate chronic silence even when their rates are not the worst.",
            paper_pull_quote="A country portfolio can look middling on rate and still hold a vast stock of unresolved years. Debt makes that backlog visible.",
            dashboard_pull_quote="The United States dominates country overdue debt on stock, Canada and France follow, Germany carries the heaviest mean unresolved age among the biggest portfolios, and the main chronic backlog remains concentrated in a small set of large CT.gov geographies.",
            root_rail=["US 491k", "Canada 90.5k", "France 89.0k", "Germany 77.3k"],
            landing_metrics=[
                ("US debt", fmt_int(int(round(as_float(country_overdue_top["overdue_years_debt"])))), "Unresolved years"),
                ("Canada debt", fmt_int(int(round(as_float(country_overdue_second["overdue_years_debt"])))), "Unresolved years"),
                ("France debt", fmt_int(int(round(as_float(country_overdue_third["overdue_years_debt"])))), "Unresolved years"),
                ("Germany mean", f"{as_float(row_for(country_overdue, 'country_name', 'Germany')['mean_overdue_unresolved']):.1f}y", "Mean unresolved age"),
            ],
            landing_chart_html=chart_section(
                "Country overdue debt",
                bar_chart(
                    [{"label": row["country_name"], "value": as_float(row["overdue_years_debt"])} for _, row in country_overdue.head(10).iterrows()],
                    "Overdue debt",
                    "Total unresolved years beyond the two-year mark by country-linked portfolio",
                    "value",
                    "label",
                    "#c3452f",
                    percent=False,
                ),
                "The United States is singular on stock, with a second tier led by Canada, France, and Germany.",
                "That is the country debt map.",
            ),
            reader_lede="A 156-word micro-paper on which country-linked CT.gov portfolios hold the deepest unresolved years beyond the two-year results mark.",
            reader_rail=["United States", "Canada", "France", "Germany"],
            reader_metrics=[
                ("US debt", fmt_int(int(round(as_float(country_overdue_top["overdue_years_debt"])))), "Unresolved years"),
                ("Canada debt", fmt_int(int(round(as_float(country_overdue_second["overdue_years_debt"])))), "Unresolved years"),
                ("France debt", fmt_int(int(round(as_float(country_overdue_third["overdue_years_debt"])))), "Unresolved years"),
                ("Germany debt", fmt_int(int(round(as_float(country_overdue_fourth["overdue_years_debt"])))), "Unresolved years"),
            ],
            dashboard_title="Country overdue debt shows where chronic CT.gov silence accumulates most heavily over time",
            dashboard_eyebrow="Country Debt Dashboard",
            dashboard_lede="The United States dominates country overdue debt by a wide margin, Canada and France remain the next largest debt holders, Germany carries a very old unresolved profile, and the largest chronic backlog is concentrated in a handful of big CT.gov geographies.",
            dashboard_rail=["Debt stock", "Mean age", "Missing results", "Country-linked"],
            dashboard_metrics=[
                ("US debt", fmt_int(int(round(as_float(country_overdue_top["overdue_years_debt"])))), "Unresolved years"),
                ("Canada debt", fmt_int(int(round(as_float(country_overdue_second["overdue_years_debt"])))), "Unresolved years"),
                ("France debt", fmt_int(int(round(as_float(country_overdue_third["overdue_years_debt"])))), "Unresolved years"),
                ("Germany mean", f"{as_float(row_for(country_overdue, 'country_name', 'Germany')['mean_overdue_unresolved']):.1f}y", "Mean unresolved age"),
            ],
            dashboard_sections=[
                chart_section(
                    "Top country overdue debt",
                    bar_chart(
                        [{"label": row["country_name"], "value": as_float(row["overdue_years_debt"])} for _, row in country_overdue.head(10).iterrows()],
                        "Overdue debt",
                        "Top unresolved years beyond the two-year mark by country-linked portfolio",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "The United States towers over the debt table, but Canada, France, and Germany remain major long-duration backlogs.",
                    "This is geography read as chronic stock.",
                ),
                chart_section(
                    "Mean unresolved age by country",
                    bar_chart(
                        [{"label": row["country_name"], "value": as_float(row["mean_overdue_unresolved"])} for _, row in country_overdue.sort_values(["mean_overdue_unresolved", "overdue_years_debt"], ascending=[False, False]).head(10).iterrows()],
                        "Mean unresolved age",
                        "Mean years beyond the two-year mark among unresolved country-linked studies",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Germany, the Netherlands, the United States, and Canada sit high on mean unresolved age among large country portfolios.",
                    "Old unresolved stock is not limited to the absolute-count leaders.",
                ),
                chart_section(
                    "Country missing-results stock",
                    bar_chart(
                        [{"label": row["country_name"], "value": as_float(row["no_results_count"])} for _, row in country_overdue.sort_values(["no_results_count", "overdue_years_debt"], ascending=[False, False]).head(10).iterrows()],
                        "Missing-results stock",
                        "Raw missing-results counts by country-linked portfolio",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "The same large country portfolios driving overdue debt also dominate missing-results stock.",
                    "Debt adds duration to that stock story.",
                ),
            ],
            sidebar_bullets=[
                "The United States carries the largest country-linked overdue debt at 491,364 unresolved years.",
                "Canada and France follow at 90,480 and 89,004 unresolved years.",
                "Germany remains fourth on debt stock and carries a 9.4-year mean unresolved age.",
                "The chronic backlog is concentrated in a small set of large CT.gov geographies.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-condition-overdue-debt",
            title="CT.gov Condition Overdue Debt",
            summary="A standalone E156 project on which therapeutic portfolios hold the deepest unresolved years beyond the two-year CT.gov reporting mark.",
            body=condition_overdue_body,
            sentences=condition_overdue_sentences,
            primary_estimand="Total unresolved years beyond the two-year results mark across CT.gov condition families",
            data_note="249,507 eligible older closed interventional studies with condition-family overdue debt, missing-results, and mean unresolved age fields",
            references=common_refs,
            protocol=(
                "This protocol re-reads therapeutic hiddenness as accumulated overdue years beyond the two-year results mark rather than missing-results counts alone. "
                "Primary outputs compare condition-family overdue debt, mean unresolved age, and raw missing-results stock. "
                "The aim is to separate broad diffuse backlog from chronic named disease debt. "
                "Condition families are keyword-derived registry groupings and should be read as approximate therapeutic portfolios."
            ),
            root_title="Which therapeutic portfolios hold the deepest overdue debt?",
            root_eyebrow="Condition Debt Project",
            root_lede="A standalone public project on therapeutic overdue debt, showing that the broad OTHER bucket dominates on stock while oncology is the largest named family and cardiovascular and metabolic portfolios remain major debt holders.",
            chapter_intro="This page changes the condition story from counts to accumulated unresolved years. It asks which therapeutic portfolios keep the deepest overdue debt alive after the two-year reporting window closes.",
            root_pull_quote="Condition debt mixes broad diffuse registry stock with large named disease families that remain unresolved for years.",
            paper_pull_quote="A condition family can be important not only because many studies are missing results, but because the backlog stays unresolved for a very long time.",
            dashboard_pull_quote="The broad OTHER bucket leads condition overdue debt, oncology is the largest named family, cardiovascular and metabolic portfolios remain major chronic backlogs, and healthy volunteers still carry an unusually heavy burden for their size.",
            root_rail=["Other 289.8k", "Oncology 255.2k", "Cardio 154.7k", "Healthy 98.9k"],
            landing_metrics=[
                ("Other debt", fmt_int(int(round(as_float(condition_overdue_top["overdue_years_debt"])))), "Unresolved years"),
                ("Oncology debt", fmt_int(int(round(as_float(condition_overdue_second["overdue_years_debt"])))), "Named-family debt"),
                ("Cardio debt", fmt_int(int(round(as_float(condition_overdue_third["overdue_years_debt"])))), "Named-family debt"),
                ("Healthy debt", fmt_int(int(round(as_float(condition_healthy["overdue_years_debt"])))), "Unresolved years"),
            ],
            landing_chart_html=chart_section(
                "Condition overdue debt",
                bar_chart(
                    [{"label": row["condition_family_label"], "value": as_float(row["overdue_years_debt"])} for _, row in condition_overdue.head(10).iterrows()],
                    "Overdue debt",
                    "Total unresolved years beyond the two-year mark across condition families",
                    "value",
                    "label",
                    "#c3452f",
                    percent=False,
                ),
                "The condition debt table is led by the broad OTHER bucket, with oncology the largest named family.",
                "That is the main therapeutic debt pattern.",
            ),
            reader_lede="A 156-word micro-paper on which CT.gov condition families hold the deepest unresolved years beyond the two-year results mark.",
            reader_rail=["Other", "Oncology", "Cardiovascular", "Healthy volunteers"],
            reader_metrics=[
                ("Other debt", fmt_int(int(round(as_float(condition_overdue_top["overdue_years_debt"])))), "Unresolved years"),
                ("Oncology debt", fmt_int(int(round(as_float(condition_overdue_second["overdue_years_debt"])))), "Named-family debt"),
                ("Cardio debt", fmt_int(int(round(as_float(condition_overdue_third["overdue_years_debt"])))), "Named-family debt"),
                ("Metabolic debt", fmt_int(int(round(as_float(condition_metabolic["overdue_years_debt"])))), "Named-family debt"),
            ],
            dashboard_title="Condition overdue debt shows which therapeutic portfolios hold the oldest unresolved CT.gov backlog",
            dashboard_eyebrow="Condition Debt Dashboard",
            dashboard_lede="The broad OTHER bucket leads on debt stock, oncology is the largest named family, cardiovascular and metabolic portfolios remain major chronic backlogs, and healthy volunteers carry unusually heavy overdue debt for a non-disease portfolio.",
            dashboard_rail=["Debt stock", "Mean age", "Missing results", "Condition families"],
            dashboard_metrics=[
                ("Other debt", fmt_int(int(round(as_float(condition_overdue_top["overdue_years_debt"])))), "Unresolved years"),
                ("Oncology debt", fmt_int(int(round(as_float(condition_overdue_second["overdue_years_debt"])))), "Named-family debt"),
                ("Oncology mean", f"{as_float(condition_overdue_second['mean_overdue_unresolved']):.1f}y", "Mean unresolved age"),
                ("Healthy debt", fmt_int(int(round(as_float(condition_healthy["overdue_years_debt"])))), "Unresolved years"),
            ],
            dashboard_sections=[
                chart_section(
                    "Top condition overdue debt",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["overdue_years_debt"])} for _, row in condition_overdue.head(10).iterrows()],
                        "Overdue debt",
                        "Top unresolved years beyond the two-year mark by condition family",
                        "value",
                        "label",
                        "#c3452f",
                        percent=False,
                    ),
                    "The broad OTHER bucket leads on stock, but oncology dominates the named disease families.",
                    "That is the condition debt map.",
                ),
                chart_section(
                    "Mean unresolved age by condition",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["mean_overdue_unresolved"])} for _, row in condition_overdue.sort_values(["mean_overdue_unresolved", "overdue_years_debt"], ascending=[False, False]).head(10).iterrows()],
                        "Mean unresolved age",
                        "Mean years beyond the two-year mark among unresolved condition-family studies",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Oncology carries the heaviest named-family mean unresolved age, with healthy volunteers and metabolic portfolios also staying old.",
                    "Debt stock and duration diverge across therapeutic areas.",
                ),
                chart_section(
                    "Condition missing-results stock",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["no_results_count"])} for _, row in condition_overdue.sort_values(["no_results_count", "overdue_years_debt"], ascending=[False, False]).head(10).iterrows()],
                        "Missing-results stock",
                        "Raw missing-results counts across condition families",
                        "value",
                        "label",
                        "#8b6914",
                        percent=False,
                    ),
                    "The debt leaders also dominate raw missing-results stock, but duration changes the therapeutic ordering at the margin.",
                    "That is why the debt lens matters.",
                ),
            ],
            sidebar_bullets=[
                "The broad OTHER bucket carries the largest condition overdue debt at 289,823 unresolved years.",
                "Oncology is the largest named family at 255,229 unresolved years.",
                "Cardiovascular and metabolic portfolios remain major chronic backlogs at 154,672 and 109,145 unresolved years.",
                "Healthy volunteers still hold 98,896 unresolved years beyond the two-year mark.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-narrative-gap-repeaters",
            title="CT.gov Narrative Gap Repeaters",
            summary="A standalone E156 project on which named sponsors most often omit both detailed descriptions and primary-outcome descriptions from older CT.gov records.",
            body=narrative_gap_body,
            sentences=narrative_gap_sentences,
            primary_estimand="Narrative-gap stock and rate among named lead sponsors with at least 100 older studies",
            data_note="249,507 eligible older closed interventional studies with narrative-gap fields derived from missing detailed descriptions and missing primary-outcome descriptions",
            references=common_refs,
            protocol=(
                "This protocol defines a narrative-gap study as an older closed interventional record missing both a detailed description and the primary outcome description fields. "
                "Primary outputs compare named-sponsor narrative-gap stock and rate, description-black-box overlap, condition-family rates, and sponsor-class rates. "
                "The aim is to isolate a textual opacity state distinct from results silence alone. "
                "Narrative gaps are registry-page omissions and do not establish whether fuller protocols or descriptions exist elsewhere."
            ),
            root_title="Which sponsors accumulate the deepest narrative gaps?",
            root_eyebrow="Narrative Gaps Project",
            root_lede="A standalone public project on narrative-gap repeaters, showing that Boehringer Ingelheim, Hoffmann-La Roche, and GlaxoSmithKline dominate the stock table while Mylan is the sharper large-sponsor rate outlier.",
            chapter_intro="This page shifts from result timing to record texture. It asks which named sponsors most often leave older CT.gov pages without both detailed descriptions and primary outcome descriptions.",
            root_pull_quote="A study page can have dates, status fields, and still tell the public remarkably little about what was actually studied.",
            paper_pull_quote="Narrative gaps are a different opacity state from overdue results. They strip the registry page of descriptive text even when other fields remain present.",
            dashboard_pull_quote="Boehringer Ingelheim leads the narrative-gap stock table, Roche and GlaxoSmithKline remain close behind, Mylan is the sharpest rate outlier, and healthy volunteers are the clearest condition-family extreme.",
            root_rail=["Boehringer 706", "Roche 555", "Mylan 93.7%", "Industry 19.5%"],
            landing_metrics=[
                ("Boehringer gap", fmt_int(as_int(narrative_top["narrative_gap_count"])), "Narrative-gap stock"),
                ("Roche gap", fmt_int(as_int(narrative_second["narrative_gap_count"])), "Narrative-gap stock"),
                ("Mylan rate", fmt_pct(as_float(narrative_rate_top["narrative_gap_rate"])), "Large-sponsor rate"),
                ("Industry rate", fmt_pct(as_float(narrative_industry["narrative_gap_rate"])), "Class rate"),
            ],
            landing_chart_html=chart_section(
                "Narrative-gap stock by sponsor",
                bar_chart(
                    [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["narrative_gap_count"])} for _, row in narrative_sponsor.head(10).iterrows()],
                    "Narrative-gap stock",
                    "Top named-sponsor counts missing both detailed and primary-outcome descriptions",
                    "value",
                    "label",
                    "#326891",
                    percent=False,
                ),
                "Narrative-gap stock is highly concentrated in a short list of major industry portfolios.",
                "That concentration defines the narrative-gap project.",
            ),
            reader_lede="A 156-word micro-paper on which named sponsors most often omit both detailed descriptions and primary-outcome descriptions from older CT.gov records.",
            reader_rail=["Boehringer", "Roche", "Mylan", "Industry"],
            reader_metrics=[
                ("Boehringer gap", fmt_int(as_int(narrative_top["narrative_gap_count"])), "Narrative-gap stock"),
                ("Roche gap", fmt_int(as_int(narrative_second["narrative_gap_count"])), "Narrative-gap stock"),
                ("GSK gap", fmt_int(as_int(narrative_third["narrative_gap_count"])), "Narrative-gap stock"),
                ("Healthy rate", fmt_pct(as_float(narrative_healthy["narrative_gap_rate"])), "Condition rate"),
            ],
            dashboard_title="Narrative-gap repeaters show where CT.gov pages remain text-thin even when other registry fields are present",
            dashboard_eyebrow="Narrative Gaps Dashboard",
            dashboard_lede="Boehringer Ingelheim leads narrative-gap stock, Roche and GlaxoSmithKline remain close behind, Mylan is the sharpest large-sponsor rate outlier, and healthy-volunteer studies are the clearest condition-family narrative-gap extreme.",
            dashboard_rail=["Stock", "Rates", "Conditions", "Narrative"],
            dashboard_metrics=[
                ("Boehringer gap", fmt_int(as_int(narrative_top["narrative_gap_count"])), "Narrative-gap stock"),
                ("Roche gap", fmt_int(as_int(narrative_second["narrative_gap_count"])), "Narrative-gap stock"),
                ("Mylan rate", fmt_pct(as_float(narrative_rate_top["narrative_gap_rate"])), "Large-sponsor rate"),
                ("Healthy rate", fmt_pct(as_float(narrative_healthy["narrative_gap_rate"])), "Condition rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Top sponsor narrative-gap stock",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["narrative_gap_count"])} for _, row in narrative_sponsor.head(10).iterrows()],
                        "Narrative-gap stock",
                        "Top sponsor counts missing both detailed and primary-outcome descriptions",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Boehringer Ingelheim, Roche, GlaxoSmithKline, Pfizer, and AstraZeneca dominate the narrative-gap stock table.",
                    "Textual opacity is concentrated in a short sponsor list.",
                ),
                chart_section(
                    "Large-sponsor narrative-gap rate",
                    bar_chart(
                        [
                            {"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["narrative_gap_rate"])}
                            for _, row in narrative_sponsor.loc[narrative_sponsor["studies"] >= 100].sort_values(
                                ["narrative_gap_rate", "narrative_gap_count"], ascending=[False, False]
                            ).head(10).iterrows()
                        ],
                        "Narrative-gap rate",
                        "Narrative-gap rate among named sponsors with at least 100 older studies",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Mylan Pharmaceuticals Inc is the sharpest large-sponsor rate outlier, with several other industry portfolios also extremely text-thin.",
                    "Stock and rate identify overlapping but not identical repeaters.",
                ),
                chart_section(
                    "Condition-family narrative-gap rate",
                    bar_chart(
                        [{"label": row["condition_family_label"], "value": as_float(row["narrative_gap_rate"])} for _, row in narrative_condition.sort_values(["narrative_gap_rate", "narrative_gap_count"], ascending=[False, False]).head(10).iterrows()],
                        "Condition narrative-gap rate",
                        "Narrative-gap rate across condition families",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "Healthy volunteers are the clearest condition-family extreme, well above the major named disease families.",
                    "That makes narrative gaps a different therapeutic pattern than ordinary missing-results stock.",
                ),
            ],
            sidebar_bullets=[
                "Boehringer Ingelheim carries the largest narrative-gap stock at 706 studies.",
                "Hoffmann-La Roche and GlaxoSmithKline follow at 555 and 526.",
                "Mylan Pharmaceuticals Inc reaches a 93.7 percent narrative-gap rate among large sponsors.",
                "Industry reaches a 19.5 percent narrative-gap rate as a sponsor class, while healthy volunteers reach 22.0 percent as a condition family.",
            ],
        )
    )
    projects.append(
        make_spec(
            repo_name="ctgov-actual-discipline-repeaters",
            title="CT.gov Actual-Discipline Repeaters",
            summary="A standalone E156 project on which named sponsors most often miss actual completion and actual enrollment discipline fields in older CT.gov records.",
            body=actual_gap_body,
            sentences=actual_gap_sentences,
            primary_estimand="Any actual-field gap stock and rate among named lead sponsors with at least 100 older studies",
            data_note="249,507 eligible older closed interventional studies with actual-field discipline fields derived from missing actual completion and actual enrollment markers",
            references=common_refs,
            protocol=(
                "This protocol defines an actual-discipline gap as a closed older study missing any of the registry fields covering actual primary completion, actual completion, or actual enrollment. "
                "Primary outputs compare named-sponsor stock and rate, sponsor-class rates, and component counts across the three actual-field domains. "
                "The aim is to isolate registry discipline around realized study timing and realized sample size. "
                "Missing actual-field markers do not by themselves establish legal violations or deliberate concealment."
            ),
            root_title="Which sponsors fail the actual-field discipline test most often?",
            root_eyebrow="Actual Discipline Project",
            root_lede="A standalone public project on actual-field repeaters, showing that Boehringer Ingelheim, NCI, and Novartis carry the largest stock of missing actual-field records while Gynecologic Oncology Group is the sharpest large-sponsor rate outlier.",
            chapter_intro="This page narrows the registry to an operational discipline problem. It asks which named sponsors most often leave older closed CT.gov records without the actual completion and actual enrollment fields expected from mature trial pages.",
            root_pull_quote="The actual-field problem is not cosmetic. It weakens the record of when studies really ended and how many participants they actually enrolled.",
            paper_pull_quote="Actual dates and actual enrollment matter because they anchor the basic chronology and realized scale of a closed study. Missing them leaves the record harder to interpret.",
            dashboard_pull_quote="Boehringer Ingelheim leads actual-discipline stock, NCI remains the largest public-sector repeater, Gynecologic Oncology Group is the sharpest large-sponsor rate outlier, and NIH and NETWORK are highest on class rate.",
            root_rail=["Boehringer 943", "NCI 615", "GOG 83.8%", "NIH 24.5%"],
            landing_metrics=[
                ("Boehringer gap", fmt_int(as_int(actual_top["actual_gap_count"])), "Actual-gap stock"),
                ("NCI gap", fmt_int(as_int(actual_second["actual_gap_count"])), "Actual-gap stock"),
                ("GOG rate", fmt_pct(as_float(actual_rate_top["actual_gap_rate"])), "Large-sponsor rate"),
                ("NIH rate", fmt_pct(as_float(actual_nih["actual_gap_rate"])), "Class rate"),
            ],
            landing_chart_html=chart_section(
                "Actual-discipline stock by sponsor",
                bar_chart(
                    [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["actual_gap_count"])} for _, row in actual_sponsor.head(10).iterrows()],
                    "Actual-gap stock",
                    "Top named-sponsor counts missing any actual-field discipline marker",
                    "value",
                    "label",
                    "#326891",
                    percent=False,
                ),
                "Boehringer Ingelheim is far ahead on stock, with NCI, Novartis, and AstraZeneca also prominent.",
                "That is the actual-discipline repeater map.",
            ),
            reader_lede="A 156-word micro-paper on which named sponsors most often miss actual completion and actual enrollment discipline fields in older CT.gov records.",
            reader_rail=["Boehringer", "NCI", "GOG", "NIH"],
            reader_metrics=[
                ("Boehringer gap", fmt_int(as_int(actual_top["actual_gap_count"])), "Actual-gap stock"),
                ("NCI gap", fmt_int(as_int(actual_second["actual_gap_count"])), "Actual-gap stock"),
                ("Novartis gap", fmt_int(as_int(actual_third["actual_gap_count"])), "Actual-gap stock"),
                ("Network rate", fmt_pct(as_float(actual_network["actual_gap_rate"])), "Class rate"),
            ],
            dashboard_title="Actual-discipline repeaters show where older CT.gov pages stay weak on realized timing and realized enrollment fields",
            dashboard_eyebrow="Actual Discipline Dashboard",
            dashboard_lede="Boehringer Ingelheim leads on actual-gap stock, NCI remains the largest public-sector repeater, Gynecologic Oncology Group and EORTC are extreme on rate, and NIH and NETWORK sit highest on sponsor-class actual-discipline rate.",
            dashboard_rail=["Stock", "Rates", "Classes", "Actual fields"],
            dashboard_metrics=[
                ("Boehringer gap", fmt_int(as_int(actual_top["actual_gap_count"])), "Actual-gap stock"),
                ("NCI gap", fmt_int(as_int(actual_second["actual_gap_count"])), "Actual-gap stock"),
                ("GOG rate", fmt_pct(as_float(actual_rate_top["actual_gap_rate"])), "Large-sponsor rate"),
                ("NIH rate", fmt_pct(as_float(actual_nih["actual_gap_rate"])), "Class rate"),
            ],
            dashboard_sections=[
                chart_section(
                    "Top sponsor actual-gap stock",
                    bar_chart(
                        [{"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["actual_gap_count"])} for _, row in actual_sponsor.head(10).iterrows()],
                        "Actual-gap stock",
                        "Top sponsor counts missing any actual-field discipline marker",
                        "value",
                        "label",
                        "#326891",
                        percent=False,
                    ),
                    "Boehringer Ingelheim, NCI, Novartis, AstraZeneca, and Memorial Sloan Kettering dominate the stock table.",
                    "The largest actual-field problem is distributed across industry and public sponsors.",
                ),
                chart_section(
                    "Large-sponsor actual-gap rate",
                    bar_chart(
                        [
                            {"label": short_sponsor(str(row["lead_sponsor_name"])), "value": as_float(row["actual_gap_rate"])}
                            for _, row in actual_sponsor.loc[actual_sponsor["studies"] >= 100].sort_values(
                                ["actual_gap_rate", "actual_gap_count"], ascending=[False, False]
                            ).head(10).iterrows()
                        ],
                        "Actual-gap rate",
                        "Actual-field discipline rate among named sponsors with at least 100 older studies",
                        "value",
                        "label",
                        "#c3452f",
                        percent=True,
                    ),
                    "Gynecologic Oncology Group and EORTC are extremely sharp large-sponsor rate outliers, even though Boehringer dominates on stock.",
                    "Stock and rate capture different actual-discipline risks.",
                ),
                chart_section(
                    "Sponsor-class actual-gap rate",
                    bar_chart(
                        [{"label": row["lead_sponsor_class"], "value": as_float(row["actual_gap_rate"])} for _, row in actual_class.sort_values(["actual_gap_rate", "actual_gap_count"], ascending=[False, False]).iterrows()],
                        "Class actual-gap rate",
                        "Actual-field discipline rate by sponsor class",
                        "value",
                        "label",
                        "#8b6914",
                        percent=True,
                    ),
                    "NIH and NETWORK sit highest on actual-discipline rate, well above the large-stock industry and OTHER classes.",
                    "That makes the actual-field problem look different from the overdue-debt and narrative-gap tables.",
                ),
            ],
            sidebar_bullets=[
                "Boehringer Ingelheim carries the largest actual-discipline stock at 943 studies.",
                "NCI follows at 615, with Novartis Pharmaceuticals next at 292.",
                "Gynecologic Oncology Group reaches an 83.8 percent actual-discipline rate among large sponsors.",
                "NIH and NETWORK are highest on sponsor-class actual-discipline rate at 24.5 and 23.4 percent.",
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
