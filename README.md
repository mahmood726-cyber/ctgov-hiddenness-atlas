# CT.gov Hiddenness Atlas

This project builds a full-registry ClinicalTrials.gov transparency analysis from the live v2 API. It is designed to move beyond small CT.gov search experiments and instead profile registry-visible non-disclosure patterns across the whole platform.

On March 29, 2026, the official API reported `578109` studies in total. The user request referred to roughly 550,000 records; this project is set up to use the current full registry size rather than a sample.

## What This Project Tries To Measure

This project treats "hiddenness" as objective information loss inside the registry record itself, for example:

- no posted results long after primary completion
- no actual primary or full completion date on closed studies
- no actual final enrollment on closed studies
- no reason given for terminated, withdrawn, or suspended studies
- no locations, no primary outcomes, no official title, or no detailed description
- no IPD sharing statement
- no linked publication references

It does not claim legal non-compliance. It measures registry-visible omission and non-disclosure patterns that make external scrutiny harder.

## Project Layout

- `scripts/fetch_registry_snapshot.py`: paginated full-registry pull from the live CT.gov API
- `scripts/analyze_hiddenness.py`: flattening, metric derivation, sponsor comparisons, and report generation
- `docs/metric_framework.md`: metric definitions and caveats
- `data/raw/`: raw JSONL snapshot plus fetch metadata
- `data/processed/`: parquet tables, CSV summaries, and Markdown findings

## Quick Start

Create the raw snapshot:

```bash
python scripts/fetch_registry_snapshot.py
```

Run the hiddenness analysis:

```bash
python scripts/analyze_hiddenness.py
```

## Main Outputs

- `data/raw/ctgov_registry_minimal.jsonl.gz`
- `data/raw/ctgov_registry_minimal_metadata.json`
- `data/processed/study_features.parquet`
- `data/processed/sponsor_class_summary_all.csv`
- `data/processed/sponsor_class_summary_closed_interventional.csv`
- `data/processed/lead_sponsor_summary_closed_interventional.csv`
- `data/processed/phase_summary_interventional.csv`
- `data/processed/hiddenness_findings.md`

## Data Source

- Official ClinicalTrials.gov API v2: `https://clinicaltrials.gov/api/v2/studies`

## Related Local Work

This project borrows the pragmatic API usage patterns from prior local CT.gov projects, especially:

- `C:\Users\user\africa_rct_efficiency_ctgov`
- `C:\Projects\ctgov-search-strategies`

But unlike those projects, this one is built for the full registry and explicitly focuses on sponsor-specific non-disclosure patterns.
