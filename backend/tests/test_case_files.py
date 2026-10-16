"""Lint the gold corpus (REQ-13, EVAL-11..16). Validation logic lives in evals/lint.py."""

import copy
from pathlib import Path

import pytest

from evals.lint import (
    CASES_DIR,
    case_dirs,
    is_todo,
    lint_case_dir,
    load_case,
    validate_case,
)

CASE_DIRS = case_dirs()


@pytest.mark.parametrize("case_dir", CASE_DIRS, ids=[d.name for d in CASE_DIRS])
def test_case_is_valid(case_dir: Path):
    errors = lint_case_dir(case_dir)
    assert errors == [], "\n".join(errors)


def test_case_ids_unique_and_match_folders():
    ids = [load_case(d)[0].get("case_id") for d in CASE_DIRS]
    assert len(ids) == len(set(ids))
    assert ids == [d.name for d in CASE_DIRS]


def test_split_counts():
    splits = [load_case(d)[0]["split"] for d in CASE_DIRS]
    assert len(splits) == 12
    assert splits.count("dev") == 8
    assert splits.count("holdout") == 4


def test_evals_never_import_extractor():
    for path in (CASES_DIR.parent).glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "app.evidence" not in text, path
        assert "extract_facts" not in text, path


def test_all_cases_labeled():
    pending = [d.name for d in CASE_DIRS if is_todo(load_case(d)[0])]
    if pending:
        pytest.skip("cases still marked todo (DEC-12): " + ", ".join(pending))


# --- Negative tests (EVAL-13): mutate an in-memory copy, expect the lint to fail.


def _labeled_case():
    case_dir = CASES_DIR / "syn-002-synonym-labels"
    case, doc_bytes = load_case(case_dir)
    assert validate_case(case, doc_bytes, case_dir.name) == []
    return case_dir.name, case, doc_bytes


def _first_present(case):
    return next(g for g in case["gold_facts"] if g["status"] == "present")


def test_lint_rejects_bad_quote():
    name, case, doc_bytes = _labeled_case()
    bad = copy.deepcopy(case)
    _first_present(bad)["mentions"][0]["quote"] = "September 19, 2026"
    errors = validate_case(bad, doc_bytes, name)
    assert any("quote is" in e for e in errors), errors


def test_lint_rejects_bad_offsets():
    name, case, doc_bytes = _labeled_case()
    bad = copy.deepcopy(case)
    bad["distractors"][0]["start"] += 1
    errors = validate_case(bad, doc_bytes, name)
    assert any(e.startswith("distractors[0]") for e in errors), errors


def test_lint_rejects_bad_hash():
    name, case, doc_bytes = _labeled_case()
    file = case["documents"][0]["file"]
    changed = dict(doc_bytes)
    changed[file] = doc_bytes[file] + b"extra line\n"
    errors = validate_case(case, changed, name)
    assert any("sha256 mismatch" in e for e in errors), errors


def test_lint_rejects_crlf_document():
    name, case, doc_bytes = _labeled_case()
    file = case["documents"][0]["file"]
    changed = dict(doc_bytes)
    changed[file] = doc_bytes[file].replace(b"\n", b"\r\n")
    errors = validate_case(case, changed, name)
    assert any("LF-only" in e for e in errors), errors


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("incident_date", "09/18/2026"),
        ("incident_date", "2026-02-30"),
        ("vehicle_vin", "2SYNHB4C8SL20002O"),
        ("estimate_total", "$1,600.25"),
        ("estimate_total", "1600.2"),
    ],
)
def test_lint_rejects_non_canonical_value(field, bad_value):
    name, case, doc_bytes = _labeled_case()
    bad = copy.deepcopy(case)
    cell = next(g for g in bad["gold_facts"] if g["field"] == field and g["status"] == "present")
    cell["value"] = bad_value
    errors = validate_case(bad, doc_bytes, name)
    assert any("not canonical" in e for e in errors), errors


def test_lint_rejects_missing_cell():
    name, case, doc_bytes = _labeled_case()
    bad = copy.deepcopy(case)
    bad["gold_facts"].pop()
    errors = validate_case(bad, doc_bytes, name)
    assert any("exactly one gold entry" in e for e in errors), errors


def test_lint_rejects_must_not_extract_equal_to_gold():
    name, case, doc_bytes = _labeled_case()
    bad = copy.deepcopy(case)
    bad["must_not_extract"] = [{"field": "estimate_total", "value": "1600.25", "why": "x"}]
    errors = validate_case(bad, doc_bytes, name)
    assert any("equals a gold value" in e for e in errors), errors


def test_lint_rejects_findings_that_do_not_follow_from_gold():
    name, case, doc_bytes = _labeled_case()
    bad = copy.deepcopy(case)
    bad["expected_findings"] = [{"code": "NO_EVIDENCE"}]
    errors = validate_case(bad, doc_bytes, name)
    assert any("do not follow" in e for e in errors), errors
