# Data provenance — Auditing the public clinical-trials record (registry-integrity atlas)

## Source
All analyses derive from a full-registry snapshot of **ClinicalTrials.gov obtained
from the ClinicalTrials.gov API v2** (`https://clinicaltrials.gov/api/v2/studies`),
captured by a paginated full-registry pull on **29 March 2026** (578,109 studies;
441,191 interventional; 290,524 closed interventional). AACT was **not** used.

## What is and is not retained
- The **raw 29 March 2026 JSONL snapshot was NOT retained** (it was gitignored in
  the per-analysis repositories and not archived). It is therefore not bit-for-bit
  reproducible.
- This package archives the **processed aggregate summaries** that underlie every
  figure and statistic reported in the article
  (`registry_integrity_atlas_summary.csv`) together with the published figures
  (`figures/`). Each value in the CSV is verified to appear verbatim in the article.

## Reproducibility
The analysis code (per-analysis repositories under
`https://github.com/mahmood726-cyber/ctgov-*`) re-derives these summaries from a
fresh ClinicalTrials.gov API v2 pull. The analyses were **independently reproduced
by re-running the code against a ClinicalTrials.gov snapshot 14 days after the
article's**; all headline figures matched within **<= 0.3 percentage points**. No
bit-for-bit reproduction is claimed, because the original snapshot was not retained.

## Ownership
The per-analysis code repositories are hosted on the journal operator's GitHub
account (`github.com/mahmood726-cyber`) and were produced by an automated analysis
pipeline.

## Licence
Data and figures: CC BY 4.0.
