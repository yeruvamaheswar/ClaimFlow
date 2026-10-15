# Evaluation plan

**Purpose:** Demonstrate correctness and limits with measurements, not marketing claims.

## Baseline: deterministic parser + discrepancy detector

A benchmark case includes source documents, annotated ground-truth values, expected evidence spans, expected missing-document findings, and expected variance findings.

| Measure | Definition | Target |
|---|---|---|
| Extraction precision | Correct extracted field values / all extracted field values | Set after baseline |
| Extraction recall | Correct extracted field values / all labeled fields | Set after baseline |
| Source attribution | Extraction results whose filename/line/excerpt match ground truth | Set after baseline |
| Contradiction recall | Expected source-value discrepancies that appear as review findings | Set after baseline |
| Unauthorized consequential actions | Successful blocked actions in controlled tests | 0 (zero tolerance) |
| Duplicate external effects | Duplicated integrations during retry tests | 0 (zero tolerance) |
| End-to-end latency | p50/p95 of tested workflows | Set after baseline |
| Model cost per case | Total usage expense for successful review | Set after baseline |

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

See `backend/tests`. Run `cd backend && pytest -q`. Passing these tests only establishes the specified behaviors; the planned benchmark is not complete.

## Release reporting convention

Each release should publish: test dataset version, sample counts, model/prompt/parser versions, pass/fail counts, confidence intervals where justified, known failures, latency, cost, and limitations. **Never describe unmeasured targets as achieved results.**
