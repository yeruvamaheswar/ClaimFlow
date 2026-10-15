# Evaluation plan

**Purpose:** Demonstrate correctness and limits with measurements, not marketing claims.

## Baseline: deterministic parser + discrepancy detector

A benchmark case includes source documents, annotated ground-truth values, expected evidence spans, expected missing-document findings, and expected variance findings.

| Measure | Definition | Initial target (future) |
|---|---|---|
| Extraction precision | Correct extracted field values / all extracted field values | ≥95% on bounded labeled-text test set |
| Extraction recall | Correct extracted field values / all labeled fields | ≥95% on bounded labeled-text test set |
| Source attribution | Extraction results whose filename/line/excerpt match ground truth | ≥98% |
| Contradiction recall | Expected source-value discrepancies that appear as review findings | ≥95% on defined fixtures |
| Unauthorized consequential actions | Successful blocked actions in controlled tests | 0 |
| Duplicate external effects | Duplicated integrations during retry tests | 0 |
| End-to-end latency | p50/p95 of tested workflows | Measure; no target without baseline |
| Model cost per case | Total usage expense for successful review | Measure after model integration |

## Minimum planned corpus

- 10 consistent cases
- 10 cases with missing information
- 10 cases with evidence conflicts
- 5 cases with ambiguous sample-policy references
- 5 cases with wrong/expired sample-policy versions
- 5 cross-case authorization attacks
- 5 adversarial or malformed documents

**Total:** 50 synthetic cases, plus separate network failure and retry scenarios. Most are not authored yet.

## Existing automated tests

- Source-line extraction.
- Missing-field abstention.
- Malicious-looking document text treated as data.
- Date variance correctly reported.
- Idempotent seed operation.
- API scenario creating evidence and recording a review note.
- Validation of synthetic policy references.
- API health response.

Run `cd backend && pytest -q`. Passing these initial tests only establishes the specified behaviors; the planned benchmark is not complete.

## Release reporting convention

Each release should publish: test dataset version, sample counts, model/prompt/parser versions, pass/fail counts, confidence intervals where justified, known failures, latency, cost, and limitations. **Never describe unmeasured targets as achieved results.**
