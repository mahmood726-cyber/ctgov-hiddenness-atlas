#!/usr/bin/env python3
"""Wave-ten CT.gov analyses: ghost and black-box repeater tables derived from wave-nine watchlists."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=str(PROCESSED))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)

    sponsor = pd.read_csv(out_dir / "wave_nine_sponsor_watchlist.csv")
    country = pd.read_csv(out_dir / "wave_nine_country_watchlist.csv")
    condition = pd.read_csv(out_dir / "wave_nine_condition_watchlist.csv")
    strict_sponsor = pd.read_csv(out_dir / "wave_nine_strict_sponsor_watchlist.csv")
    strict_class = pd.read_csv(out_dir / "wave_nine_strict_sponsor_class_summary.csv")

    sponsor_ghost = sponsor.sort_values(["excess_ghost", "ghost_count"], ascending=[False, False]).reset_index(drop=True)
    country_ghost = country.sort_values(["excess_ghost", "ghost_count"], ascending=[False, False]).reset_index(drop=True)
    condition_ghost = condition.sort_values(["excess_ghost", "ghost_count"], ascending=[False, False]).reset_index(drop=True)
    sponsor_black_box = sponsor.sort_values(["black_box_count", "black_box_rate"], ascending=[False, False]).reset_index(drop=True)
    strict_black_box = strict_sponsor.sort_values(["black_box_count", "black_box_rate"], ascending=[False, False]).reset_index(drop=True)
    strict_black_box_class = strict_class.sort_values(["black_box_count", "black_box_rate"], ascending=[False, False]).reset_index(drop=True)

    sponsor_ghost.to_csv(out_dir / "wave_ten_sponsor_ghost_watchlist.csv", index=False)
    country_ghost.to_csv(out_dir / "wave_ten_country_ghost_watchlist.csv", index=False)
    condition_ghost.to_csv(out_dir / "wave_ten_condition_ghost_watchlist.csv", index=False)
    sponsor_black_box.to_csv(out_dir / "wave_ten_black_box_sponsor_watchlist.csv", index=False)
    strict_black_box.to_csv(out_dir / "wave_ten_strict_black_box_watchlist.csv", index=False)
    strict_black_box_class.to_csv(out_dir / "wave_ten_strict_black_box_class_summary.csv", index=False)

    lines = [
        "# Wave Ten Findings",
        "",
        f"- Largest sponsor ghost excess: {sponsor_ghost.iloc[0]['lead_sponsor_name']} at {sponsor_ghost.iloc[0]['excess_ghost']:.0f} studies.",
        f"- Largest country ghost excess: {country_ghost.iloc[0]['country_name']} at {country_ghost.iloc[0]['excess_ghost']:.0f} studies.",
        f"- Largest condition-family ghost excess: {condition_ghost.iloc[0]['condition_family_label']} at {condition_ghost.iloc[0]['excess_ghost']:.0f} studies.",
        f"- Largest named black-box sponsor stock: {sponsor_black_box.iloc[0]['lead_sponsor_name']} at {int(sponsor_black_box.iloc[0]['black_box_count']):,} studies.",
        f"- Largest strict-core black-box sponsor stock: {strict_black_box.iloc[0]['lead_sponsor_name']} at {int(strict_black_box.iloc[0]['black_box_count']):,} studies.",
        f"- Largest strict-core black-box class stock: {strict_black_box_class.iloc[0]['lead_sponsor_class']} at {int(strict_black_box_class.iloc[0]['black_box_count']):,} studies.",
    ]
    (out_dir / "wave_ten_findings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
