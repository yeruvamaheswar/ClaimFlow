# Gold corpus guideline (corpus v0, format `case/1`)

## Purpose

The gold corpus says what a careful human reads in each synthetic document. We score extractors against it. Gold must not copy any extractor's behavior. All cases are synthetic and for demonstration only.

## Fields (v0)

v0 covers three fields only.

| Field | Definition | Canonical form |
|---|---|---|
| `incident_date` | The date of loss. Not the report date, estimate date, letter date, or filing date. | `YYYY-MM-DD` |
| `vehicle_vin` | The VIN of the insured vehicle only. Another party's VIN is a distractor. | Uppercase, 17 characters, no `I`, `O`, or `Q` |
| `estimate_total` | The final total the estimate states, as written. Include tax if the total includes tax. | Decimal string with exactly 2 places, no `$`, no commas, e.g. `1600.25` |

Rules:

- Numeric slash dates are US order: `MM/DD/YYYY`. So `09/03/2026` is 2026-09-03.
- Record the value as written. If a document has a typo in a VIN, gold keeps the typo. The finding then shows the variance.
- A subtotal or pre-tax total is not the final total.

## Cells and statuses

A cell is one (document, field) pair. Every document has exactly 3 cells. Each cell has exactly one entry in `gold_facts`.

| Status | Meaning | Required keys |
|---|---|---|
| `present` | The document states one value for the field. | `value` (canonical), `form`, at least 1 mention |
| `absent` | The document does not state the field. | no `value`, no mentions |
| `indeterminate` | The text gives no single value. Examples: "sometime last week"; two different dates of loss in one document; two unlabeled totals with no way to tell the final one. | `reason`; optional mentions; no cell `value` |
| `todo` | Not labeled yet. | nothing else |

In an `indeterminate` cell, a mention may carry its own canonical `value`. Use this when the text states several definite candidates, such as a within-document conflict.

## Form tags

Each `present` cell has one `form` tag. Pick the first that fits:

| Form | Use when |
|---|---|
| `table` | The value sits in a text table row or column. |
| `narrative` | The value sits inside a sentence with no label. |
| `synonym_label` | A label other than the standard one, e.g. "Date of Loss", "Vehicle ID No.", "Grand Total", "Unit 1 (insured)". |
| `labeled_nonstandard` | The standard label ("Incident Date", "VIN", "Estimate Total") with a non-ISO value, e.g. `Incident Date: 09/18/2026`. |
| `labeled_iso` | The standard label with an ISO date, a bare VIN, or a plain amount (optional `$` and commas). |

## Mentions and spans

- A mention marks where the value appears: `{start, end, quote}`.
- The span covers the value text only. Do not include the label. Do not include the currency sign.
- `start` and `end` are Python code-point offsets into the `.txt` file. `end` is exclusive. So `text[start:end] == quote`.
- List every place in the document that states the cell's value.
- If the quote appears more than once in the document, add `occurrence` (0-based).
- Do not type offsets by hand. Run the anchor helper (below).

## Distractors

A distractor is a value that looks like the field but is not it. Examples: the report date next to the date of loss, the other party's VIN, a subtotal. Record each as `{doc_id, field, start, end, quote, why}`.

## must_not_extract

List values that a correct system must never output for a field. Use this for injected instructions and other-party VINs. A `must_not_extract` value must never equal a gold value.

## Expected findings

Expected findings follow from the gold facts plus the claim intake, using the current finding codes:

- `MISSING_DOCUMENTS` with `missing_types` (sorted) when any of `claim_form`, `police_report`, `repair_estimate` is missing.
- `<FIELD>_VARIANCE` with `field` and `values` when the field has more than one distinct value. Values come from `present` cells, mention values in `indeterminate` cells, and, for `incident_date`, the claim intake date. `values` are canonical and sorted as strings.
- `NO_EVIDENCE` when the case has no documents.

Order: `MISSING_DOCUMENTS`, then variances in field order (`incident_date`, `vehicle_vin`, `estimate_total`), then `NO_EVIDENCE`. The lint recomputes this list from gold and fails on any difference.

## Case format `case/1`

One folder per case: `backend/evals/cases/<case_id>/`. It holds `case.json` and one UTF-8, LF-only `.txt` file per document.

`case.json` keys: `schema_version`, `case_id` (equals the folder name), `revision`, `split` (`dev` or `holdout`), `tags`, `authoring {author, reviewed_by, parser_consulted, notes}`, `claim {policy_ref, incident_date}`, `documents [{doc_id, file, filename, document_type, sha256}]`, `gold_facts`, `distractors`, `must_not_extract`, `expected_findings` (a list, or `"todo"`).

Document types: `claim_form`, `police_report`, `repair_estimate`, `policy_excerpt`, `other`.

## Authoring rules

1. Write gold first. Read the documents and this guideline only.
2. Never run, import, or read an extractor while you write gold. Set `parser_consulted` to `false`.
3. A gold edit never shares a commit with an extractor change.
4. Keep everything synthetic: "SYNTHETIC ... demonstration only" headers, `SYN-` policy references, invented VINs, fictional names and shops.
5. Holdout cases stay frozen. Do not tune prompts or rules on them.
6. Bump `revision` when you change a case after it was committed. Record it in `CHANGELOG.md`.

## How to label a `todo` case

Run commands from `backend/`.

1. Open each `.txt` file in the case folder.
2. For each cell in `gold_facts`, change `status` from `todo` to `present`, `absent`, or `indeterminate`.
3. For `present`, add `value` (canonical), `form`, and `mentions: [{"quote": "..."}]`. Quote the value text only.
4. Add distractors as `{"doc_id", "field", "quote", "why"}`. Add `must_not_extract` entries if needed.
5. Replace `"expected_findings": "todo"` with the list. If unsure, run the lint: it prints the derived list.
6. Run `.venv/bin/python -m evals.anchor <case_id>`. It fills `start`, `end`, and `sha256`. It stops with an error if a quote is not found or is ambiguous.
7. Run `.venv/bin/python -m evals.lint` and `.venv/bin/pytest -q tests/test_case_files.py`.
8. Remove the `todo` tag from `tags`. Update `authoring.author` and `authoring.notes`.

When no `todo` cases remain, `test_all_cases_labeled` passes instead of skipping.
