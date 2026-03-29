# Metric Framework

## Core Idea

The project uses registry-visible omissions as proxies for what is being hidden, blurred, or made hard to inspect.

This is not a legal adjudication. A study can be missing information for benign reasons, legacy schema reasons, or because the field is not applicable. The value of the analysis is comparative: it shows where omission concentrates by sponsor class, study type, phase, and lead sponsor.

## Hiddenness Domains

### Structural omission

- missing official title
- missing detailed description
- missing location records
- missing primary outcome entries
- primary outcomes present but without descriptions
- missing IPD sharing statement
- no linked publication references
- missing phase on interventional studies
- missing arm groups on interventional studies

### Closure-stage non-disclosure

- closed study without an actual primary completion date
- closed study without an actual full completion date
- closed study without actual enrollment
- terminated, withdrawn, or suspended study without `whyStopped`
- interventional study with an actual primary completion date at least 2 years old and still no posted results

## Why A 2-Year Results Gap

This project reports both 1-year and 2-year no-results gaps, but uses the 2-year gap in the composite score. That makes the signal more conservative and reduces the risk of treating borderline cases as clear non-disclosure.

## Composite Score

The `hiddenness_score` is a simple count of omission flags. It is not intended as a regulatory scorecard. It is a compact way to compare sponsor classes and large sponsor organizations on overall information loss.

## Interpretation

- High absolute counts show where the largest volume of obscured information sits.
- High rates show where omission is systematically concentrated.
- Industry may dominate counts because it registers many studies.
- Other classes may dominate rates because their records are structurally sparse.

Both views matter and are reported separately.
