"""Fill span offsets and document hashes in a case.json. See GUIDELINES.md.

Usage: python -m evals.anchor <case_id>

For each gold mention and distractor with a `quote`, find the quote in the
document text and write `start`/`end` (Python code-point offsets, end exclusive).
Use `occurrence` (0-based, default 0) to pick a later copy of the quote. If the
quote appears more than once, `occurrence` is required. Also writes each
document's sha256. Rewrites case.json with 2-space indentation.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from evals.lint import CASES_DIR


class AnchorError(Exception):
    pass


def _find(text: str, quote: str, occurrence: int | None, where: str) -> tuple[int, int]:
    positions = []
    i = text.find(quote)
    while i != -1:
        positions.append(i)
        i = text.find(quote, i + 1)
    if not positions:
        raise AnchorError(f"{where}: quote {quote!r} not found in document text")
    if occurrence is None:
        if len(positions) > 1:
            raise AnchorError(
                f"{where}: quote {quote!r} appears {len(positions)} times; "
                "add \"occurrence\" (0-based) to choose one"
            )
        occurrence = 0
    if not 0 <= occurrence < len(positions):
        raise AnchorError(
            f"{where}: occurrence {occurrence} requested, quote {quote!r} "
            f"appears {len(positions)} times"
        )
    start = positions[occurrence]
    return start, start + len(quote)


def _anchor_item(item: dict, text: str, where: str) -> dict:
    """Return the item with start/end filled, keys in a stable order."""
    quote = item.get("quote")
    if not isinstance(quote, str) or not quote:
        raise AnchorError(f"{where}: quote missing or empty")
    start, end = _find(text, quote, item.get("occurrence"), where)
    rest = {k: v for k, v in item.items() if k not in ("start", "end", "quote")}
    return {"start": start, "end": end, "quote": quote, **rest}


def anchor_case(case_dir: Path) -> dict:
    case_path = case_dir / "case.json"
    case = json.loads(case_path.read_text(encoding="utf-8"))
    texts: dict[str, str] = {}
    for doc in case.get("documents", []):
        raw = (case_dir / doc["file"]).read_bytes()
        if b"\r" in raw:
            raise AnchorError(f"{doc['file']}: contains CR characters; save it LF-only")
        doc["sha256"] = hashlib.sha256(raw).hexdigest()
        texts[doc["doc_id"]] = raw.decode("utf-8")

    def text_for(doc_id: str, where: str) -> str:
        if doc_id not in texts:
            raise AnchorError(f"{where}: unknown doc_id {doc_id!r}")
        return texts[doc_id]

    for g in case.get("gold_facts", []):
        where = f"gold_facts[{g.get('doc_id')}/{g.get('field')}]"
        mentions = g.get("mentions")
        if mentions:
            text = text_for(g.get("doc_id"), where)
            g["mentions"] = [
                _anchor_item(m, text, f"{where}.mentions[{j}]") for j, m in enumerate(mentions)
            ]
    case["distractors"] = [
        _anchor_item(d, text_for(d.get("doc_id"), f"distractors[{i}]"), f"distractors[{i}]")
        for i, d in enumerate(case.get("distractors", []))
    ]
    case_path.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return case


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m evals.anchor <case_id>", file=sys.stderr)
        return 2
    case_dir = CASES_DIR / argv[0]
    if not (case_dir / "case.json").is_file():
        print(f"error: no case.json in {case_dir}", file=sys.stderr)
        return 2
    try:
        anchor_case(case_dir)
    except AnchorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"anchored {argv[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
