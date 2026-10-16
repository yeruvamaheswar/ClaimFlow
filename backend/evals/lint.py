"""Validate gold case folders (format `case/1`). See GUIDELINES.md.

Usage: python -m evals.lint            # lint every case, exit 1 on any error

This module never imports or runs the extractor. Expected findings are derived
from gold facts and claim intake only.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

CASES_DIR = Path(__file__).resolve().parent / "cases"

SCHEMA_VERSION = "case/1"
FIELDS = ("incident_date", "vehicle_vin", "estimate_total")
DOC_TYPES = {"claim_form", "police_report", "repair_estimate", "policy_excerpt", "other"}
REQUIRED_DOC_TYPES = ("claim_form", "police_report", "repair_estimate")
STATUSES = {"present", "absent", "indeterminate", "todo"}
FORMS = {"labeled_iso", "labeled_nonstandard", "synonym_label", "narrative", "table"}
SPLITS = {"dev", "holdout"}
FINDING_CODES = {
    "MISSING_DOCUMENTS",
    "INCIDENT_DATE_VARIANCE",
    "VEHICLE_VIN_VARIANCE",
    "ESTIMATE_TOTAL_VARIANCE",
    "NO_EVIDENCE",
}

_VIN_RE = re.compile(r"[A-HJ-NPR-Z0-9]{17}")
_MONEY_RE = re.compile(r"(0|[1-9][0-9]*)\.[0-9]{2}")
_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def is_canonical(field: str, value: object) -> bool:
    """True when value is in the canonical form for its field."""
    if not isinstance(value, str):
        return False
    if field == "incident_date":
        if not _DATE_RE.fullmatch(value):
            return False
        try:
            dt.date.fromisoformat(value)
        except ValueError:
            return False
        return True
    if field == "vehicle_vin":
        return bool(_VIN_RE.fullmatch(value))
    if field == "estimate_total":
        return bool(_MONEY_RE.fullmatch(value))
    return False


def is_todo(case: dict) -> bool:
    """True while the case still has unlabeled cells or unlabeled findings."""
    if case.get("expected_findings") == "todo":
        return True
    return any(g.get("status") == "todo" for g in case.get("gold_facts", []))


def derive_expected_findings(case: dict) -> list[dict]:
    """Findings implied by gold facts plus claim intake, per current finding codes.

    Order matches the app: MISSING_DOCUMENTS, variances in field order, NO_EVIDENCE.
    """
    findings: list[dict] = []
    docs = case.get("documents", [])
    types = {d.get("document_type") for d in docs}
    missing = sorted(set(REQUIRED_DOC_TYPES) - types)
    if missing:
        findings.append({"code": "MISSING_DOCUMENTS", "missing_types": missing})

    values: dict[str, set[str]] = {f: set() for f in FIELDS}
    intake_date = case.get("claim", {}).get("incident_date")
    if isinstance(intake_date, str):
        values["incident_date"].add(intake_date)
    for g in case.get("gold_facts", []):
        field = g.get("field")
        if field not in values:
            continue
        if g.get("status") == "present" and isinstance(g.get("value"), str):
            values[field].add(g["value"])
        elif g.get("status") == "indeterminate":
            for m in g.get("mentions", []):
                if isinstance(m.get("value"), str):
                    values[field].add(m["value"])
    for field in FIELDS:
        if len(values[field]) > 1:
            findings.append({
                "code": field.upper() + "_VARIANCE",
                "field": field,
                "values": sorted(values[field]),
            })
    if not docs:
        findings.append({"code": "NO_EVIDENCE"})
    return findings


def _check_span(where: str, item: dict, text: str | None, errors: list[str]) -> None:
    start, end, quote = item.get("start"), item.get("end"), item.get("quote")
    if not isinstance(quote, str) or not quote:
        errors.append(f"{where}: quote missing or empty")
        return
    if not isinstance(start, int) or not isinstance(end, int):
        errors.append(f"{where}: start/end missing (run python -m evals.anchor)")
        return
    if text is None:
        return
    if not 0 <= start < end <= len(text):
        errors.append(f"{where}: offsets {start}:{end} out of range")
        return
    if text[start:end] != quote:
        errors.append(
            f"{where}: text[{start}:{end}] is {text[start:end]!r}, quote is {quote!r}"
        )


def validate_case(
    case: dict, doc_bytes: dict[str, bytes], folder_name: str | None = None
) -> list[str]:
    """Return a list of human-readable errors. Empty list means the case is valid.

    doc_bytes maps each document's `file` name to the raw bytes on disk.
    """
    errors: list[str] = []
    cid = case.get("case_id")

    if case.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    if not isinstance(cid, str) or not cid:
        errors.append("case_id missing")
    elif folder_name is not None and cid != folder_name:
        errors.append(f"case_id {cid!r} does not equal folder name {folder_name!r}")
    if not isinstance(case.get("revision"), int) or case["revision"] < 1:
        errors.append("revision must be an integer >= 1")
    if case.get("split") not in SPLITS:
        errors.append(f"split must be one of {sorted(SPLITS)}")
    tags = case.get("tags")
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        errors.append("tags must be a list of strings")

    authoring = case.get("authoring") or {}
    if authoring.get("parser_consulted") is not False:
        errors.append("authoring.parser_consulted must be false")
    if not authoring.get("author"):
        errors.append("authoring.author missing")

    claim = case.get("claim") or {}
    if not str(claim.get("policy_ref", "")).startswith("SYN-"):
        errors.append("claim.policy_ref must start with 'SYN-'")
    if not is_canonical("incident_date", claim.get("incident_date")):
        errors.append(f"claim.incident_date not canonical: {claim.get('incident_date')!r}")

    # Documents
    texts: dict[str, str | None] = {}
    for i, doc in enumerate(case.get("documents", [])):
        where = f"documents[{i}]"
        did, fname = doc.get("doc_id"), doc.get("file")
        if not did or did in texts:
            errors.append(f"{where}: doc_id missing or duplicate: {did!r}")
            continue
        texts[did] = None
        if doc.get("document_type") not in DOC_TYPES:
            errors.append(f"{where}: unknown document_type {doc.get('document_type')!r}")
        if not doc.get("filename"):
            errors.append(f"{where}: filename missing")
        if not isinstance(fname, str) or not fname.endswith(".txt"):
            errors.append(f"{where}: file must be a .txt name")
            continue
        raw = doc_bytes.get(fname)
        if raw is None:
            errors.append(f"{where}: file {fname!r} not found")
            continue
        if b"\r" in raw:
            errors.append(f"{where}: {fname} contains CR characters; documents must be LF-only")
        if hashlib.sha256(raw).hexdigest() != doc.get("sha256"):
            errors.append(f"{where}: sha256 mismatch for {fname} (run python -m evals.anchor)")
        try:
            texts[did] = raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{where}: {fname} is not UTF-8")

    # Gold facts: exactly one entry per (doc_id, field) cell.
    seen: dict[tuple[str, str], int] = {}
    present_values: dict[str, set[str]] = {f: set() for f in FIELDS}
    for i, g in enumerate(case.get("gold_facts", [])):
        where = f"gold_facts[{i}]"
        did, field, status = g.get("doc_id"), g.get("field"), g.get("status")
        if did not in texts:
            errors.append(f"{where}: unknown doc_id {did!r}")
            continue
        if field not in FIELDS:
            errors.append(f"{where}: unknown field {field!r}")
            continue
        where = f"gold_facts[{did}/{field}]"
        seen[(did, field)] = seen.get((did, field), 0) + 1
        if status not in STATUSES:
            errors.append(f"{where}: unknown status {status!r}")
            continue
        mentions = g.get("mentions", [])
        if not isinstance(mentions, list):
            errors.append(f"{where}: mentions must be a list")
            continue
        if status == "present":
            if not is_canonical(field, g.get("value")):
                errors.append(f"{where}: value not canonical: {g.get('value')!r}")
            else:
                present_values[field].add(g["value"])
            if g.get("form") not in FORMS:
                errors.append(f"{where}: form must be one of {sorted(FORMS)}")
            if not mentions:
                errors.append(f"{where}: present cell needs at least one mention")
        elif "value" in g:
            errors.append(f"{where}: status {status!r} must not carry a value")
        if status == "indeterminate" and not g.get("reason"):
            errors.append(f"{where}: indeterminate cell needs a reason")
        if status in ("absent", "todo") and mentions:
            errors.append(f"{where}: status {status!r} must not carry mentions")
        for j, m in enumerate(mentions):
            _check_span(f"{where}.mentions[{j}]", m, texts.get(did), errors)
            if "value" in m:
                if status != "indeterminate":
                    errors.append(f"{where}.mentions[{j}]: mention value only allowed "
                                  "in indeterminate cells")
                elif not is_canonical(field, m["value"]):
                    errors.append(f"{where}.mentions[{j}]: value not canonical: "
                                  f"{m['value']!r}")
                else:
                    present_values[field].add(m["value"])
    for did in texts:
        for field in FIELDS:
            count = seen.get((did, field), 0)
            if count != 1:
                errors.append(f"cell {did}/{field}: needs exactly one gold entry, has {count}")

    for i, d in enumerate(case.get("distractors", [])):
        where = f"distractors[{i}]"
        if d.get("doc_id") not in texts:
            errors.append(f"{where}: unknown doc_id {d.get('doc_id')!r}")
            continue
        if d.get("field") not in FIELDS:
            errors.append(f"{where}: unknown field {d.get('field')!r}")
        if not d.get("why"):
            errors.append(f"{where}: why missing")
        _check_span(where, d, texts.get(d["doc_id"]), errors)

    for i, m in enumerate(case.get("must_not_extract", [])):
        where = f"must_not_extract[{i}]"
        field = m.get("field")
        if field not in FIELDS:
            errors.append(f"{where}: unknown field {field!r}")
            continue
        if not is_canonical(field, m.get("value")):
            errors.append(f"{where}: value not canonical: {m.get('value')!r}")
        if m.get("value") in present_values[field]:
            errors.append(f"{where}: value {m.get('value')!r} equals a gold value")
        if not m.get("why"):
            errors.append(f"{where}: why missing")

    expected = case.get("expected_findings")
    if expected == "todo":
        pass
    elif not isinstance(expected, list):
        errors.append("expected_findings must be a list or the string 'todo'")
    else:
        for i, f in enumerate(expected):
            if f.get("code") not in FINDING_CODES:
                errors.append(f"expected_findings[{i}]: unknown code {f.get('code')!r}")
            for v in f.get("values", []):
                if not is_canonical(f.get("field", ""), v):
                    errors.append(f"expected_findings[{i}]: value not canonical: {v!r}")
        if not is_todo(case) and expected != derive_expected_findings(case):
            errors.append(
                "expected_findings do not follow from gold facts and claim intake; "
                f"derived: {json.dumps(derive_expected_findings(case))}"
            )
    return errors


def load_case(case_dir: Path) -> tuple[dict, dict[str, bytes]]:
    """Read case.json and the raw bytes of every document file it names."""
    case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    doc_bytes: dict[str, bytes] = {}
    for doc in case.get("documents", []):
        fname = doc.get("file")
        if isinstance(fname, str) and "/" not in fname and (case_dir / fname).is_file():
            doc_bytes[fname] = (case_dir / fname).read_bytes()
    return case, doc_bytes


def lint_case_dir(case_dir: Path) -> list[str]:
    case, doc_bytes = load_case(case_dir)
    return validate_case(case, doc_bytes, folder_name=case_dir.name)


def case_dirs(root: Path = CASES_DIR) -> list[Path]:
    return sorted(p for p in root.iterdir() if (p / "case.json").is_file())


def main() -> int:
    failed = 0
    for case_dir in case_dirs():
        errors = lint_case_dir(case_dir)
        case, _ = load_case(case_dir)
        state = "todo" if is_todo(case) else "labeled"
        print(f"{case_dir.name}: {'ok' if not errors else 'FAIL'} ({state})")
        for e in errors:
            print(f"  - {e}")
        failed += bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
