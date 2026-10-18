# CT.gov Hiddenness Atlas

> **Reporting-gap methodology correction (18 October 2026):** The earlier age-eligible denominator could include non-eligible studies, and partial/estimated completion dates could be treated as exact. The calculation now requires a closed interventional study, day-precise ACTUAL primary completion, a known consistent `hasResults` status, and an elapsed calendar-year anniversary on the API dataset date. **The old published March 2026 figures have not yet been recomputed and must not be represented as corrected or independently validated.** See [Metric Framework](docs/metric_framework.md).

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

Run the hiddenness analysis against the downloaded release (the as-of date is taken from `api_data_timestamp` or legacy `fetched_at`, never the current wall clock):

```bash
python scripts/analyze_hiddenness.py
```

The analysis rejects an explicit mismatched `--as-of-date`, query-filtered source without `--allow-query-subset`, and partial snapshots without `--allow-partial`. These opt-ins support exploratory analyses only; they do not establish whole-registry representativeness.

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

- `africa_rct_efficiency_ctgov` (sibling working dir, user home)
- `ctgov-search-strategies` (sibling project under `Projects/`)

But unlike those projects, this one is built for the full registry and explicitly focuses on sponsor-specific non-disclosure patterns.

## Paper data (Synthesis Research Article)

The processed aggregate summaries and figures underlying the consolidated Research
Article "Auditing the public clinical-trials record: a registry-integrity atlas"
(Andrew Woo, Synthesis, 2026) are archived in [`paper_data/`](paper_data/):
summary CSV, the six published figures, data provenance, and Zenodo metadata.
Source: ClinicalTrials.gov API v2 snapshot of 29 March 2026 (raw snapshot not retained;
see paper_data/DATA_PROVENANCE.md).

## Registry snapshot integrity (October 2026)

The full-registry downloader now verifies the first-page API total, checks unique NCT identifiers across *every* page, rejects repeated cursors, and refuses to certify a truncated crawl. It writes a temporary gzip first and only replaces the canonical snapshot when pagination and count checks succeed. The accompanying metadata records `coverage`, `scope_complete`, query scope, record counts, and a SHA-256 checksum.

`python scripts/fetch_registry_snapshot.py --max-pages 3` is **deliberately partial**. Downstream `python scripts/analyze_hiddenness.py` refuses partial or checksum-mismatched snapshots by default; use `--allow-partial` only for exploratory analyses clearly labelled as non-generalizable. The same safeguards also check legacy metadata counts when older snapshots lack checksums.

These checks establish **export integrity**, not a legally meaningful results-reporting obligation or an atomic point-in-time snapshot: CT.gov is a live registry and records may change during pagination. Claims about FDAAA 801 applicability still require separate trial-level review.

### API release-pinning and live smoke validation

A full export now reads `https://clinicaltrials.gov/api/v2/version` **before and after pagination**, checking that both `apiVersion` and `dataTimestamp` match. If CT.gov refreshes its dataset during a long scan, the exporter aborts rather than certifying a mixed-release snapshot. The metadata records `api_version`, `api_data_timestamp`, and `api_epoch_stable` alongside the SHA-256 and count checks. This is release consistency checking, **not** a guarantee of an atomic individual-trial historical snapshot.

`python -m unittest discover -s tests -p 'test_live_api.py' -v` performs a real, one-trial, network-dependent API query for NCT02993146, verifies complete single-trial paging and SHA-256, then checks that the downstream atlas flattener preserves the posted-results status and primary outcome details. GitHub Actions runs this separately from the offline tests; when the public service is unavailable, the network check can fail despite correct local code.

The smoke test is a contract test, **not** a regeneration or confirmation of the previously published full-registry results.
