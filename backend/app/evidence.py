"""Evidence extraction and conservative, review-only rules.

No LLM calls occur here. Each fact has an exact source line; absence stays absent.
Rules are a DEMONSTRATION protocol, not genuine insurance coverage guidance.
"""

import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation

FIELD_PATTERNS = {
    "incident_date": re.compile(r"^\s*Incident Date\s*:\s*(\d{4}-\d{2}-\d{2})\s*$", re.IGNORECASE),
    # VINs never contain I, O, or Q.
    "vehicle_vin": re.compile(
        r"^\s*(?:Vehicle )?VIN\s*:\s*([A-HJ-NPR-Z0-9]{17})\s*$", re.IGNORECASE
    ),
    "estimate_total": re.compile(
        r"^\s*Estimate Total\s*:\s*\$?([\d,]+\.\d{2})\s*$", re.IGNORECASE
    ),
}

REQUIRED_TYPES = {"claim_form", "police_report", "repair_estimate"}


def extract_facts(text: str) -> dict:
    """First occurrence is the fact; later differing values are kept under "conflicts"."""
    facts: dict = {}
    for lineno, line in enumerate(text.splitlines(), start=1):
        for field, pattern in FIELD_PATTERNS.items():
            match = pattern.match(line)
            if match is None:
                continue
            value = match.group(1).strip()
            if field == "vehicle_vin":
                value = value.upper()
            elif field == "estimate_total":
                try:
                    value = str(Decimal(value.replace(",", "")))
                except InvalidOperation:
                    continue
            occurrence = {"value": value, "line": lineno, "excerpt": line.strip()}
            if field not in facts:
                facts[field] = occurrence
                continue
            primary = facts[field]
            seen = {primary["value"]} | {c["value"] for c in primary.get("conflicts", [])}
            if value not in seen:
                primary.setdefault("conflicts", []).append(occurrence)
    return facts


def generate_findings(claim) -> list[dict]:
    """Return review prompts, never payment decisions or fraud determinations."""
    findings: list[dict] = []
    types = {doc.document_type for doc in claim.documents}
    missing = sorted(REQUIRED_TYPES - types)
    if missing:
        findings.append({
            "code": "MISSING_DOCUMENTS", "severity": "attention",
            "title": "Documents required by demo checklist",
            "description": "Missing sample workflow document types: " + ", ".join(missing),
            "evidence": [],
        })

    by_field: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    by_field["incident_date"][claim.incident_date].append({
        "document_id": None, "filename": "Claim intake", "line": None,
        "excerpt": "Incident Date: " + claim.incident_date, "value": claim.incident_date,
    })
    for doc in claim.documents:
        for field, fact in doc.extracted_facts.items():
            for occurrence in [fact, *fact.get("conflicts", [])]:
                by_field[field][occurrence["value"]].append({
                    "document_id": doc.id, "filename": doc.filename,
                    "line": occurrence["line"], "excerpt": occurrence["excerpt"],
                    "value": occurrence["value"],
                })

    for field, label in (("incident_date", "Incident dates"),
                         ("vehicle_vin", "Vehicle identifiers"),
                         ("estimate_total", "Repair estimate totals")):
        values = by_field[field]
        if len(values) > 1:
            evidence = [source for occurrences in values.values() for source in occurrences]
            findings.append({
                "code": field.upper() + "_VARIANCE", "severity": "attention",
                "title": label + " differ across sources",
                "description": (
                    "Review different quoted estimates; a difference is not itself an error."
                    if field == "estimate_total" else
                    "Sources disagree. The system does not select a preferred value."
                ),
                "evidence": evidence,
            })

    if not claim.documents:
        findings.append({
            "code": "NO_EVIDENCE", "severity": "attention",
            "title": "No evidence uploaded",
            "description": "Add synthetic evidence documents to inspect this case.",
            "evidence": [],
        })
    return findings
