Mahmood Ahmad
Tahir Heart Institute
author@example.com

Protocol: CT.gov Hiddenness Atlas

This protocol describes a full-registry audit of ClinicalTrials.gov non-disclosure and sparse reporting patterns. The source universe is the live ClinicalTrials.gov API v2 snapshot captured on 2026-03-29, yielding 578,109 total studies, 441,191 interventional studies, and 290,524 closed interventional studies. The primary estimand is the 2-year no-results rate among closed interventional studies with a primary completion date at least two years before the reference date. Secondary estimands include missing actual primary completion date, missing actual completion date, missing actual enrollment, missing IPD sharing statement, missing linked publication references, sparse outcome reporting, and missing stopping reasons. All records are flattened into study-level features and summarized by sponsor class, lead sponsor, and phase. The main contrast of interest is whether hiddenness concentrates in industry, heterogeneous OTHER sponsors, government categories, or NIH-linked studies once both rates and absolute stocks are examined. Outputs include a public dashboard, E156 micro-paper bundle, protocol, and grouped CSV summaries suitable for GitHub Pages distribution.

Outside Notes

Type: protocol
Primary estimand: 2-year no-results rate among eligible closed interventional studies
App: CT.gov Hiddenness Atlas
Code: https://github.com/mahmood726-cyber/ctgov-hiddenness-atlas
Date: 2026-03-29
Validation: FULL REGISTRY RUN

References

1. ClinicalTrials.gov API v2. National Library of Medicine. Accessed March 29, 2026.
2. Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. BMJ. 2021;372:n71.
3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.

AI Disclosure

This work represents a compiler-generated evidence micro-publication built from structured registry data and deterministic summary code. AI was used as a constrained coding and drafting assistant for interface generation, packaging, and prose refinement, not as an autonomous author. The analytical choices, interpretation, and final outputs were reviewed by the author, who takes responsibility for the content.
