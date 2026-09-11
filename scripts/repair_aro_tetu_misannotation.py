#!/usr/bin/env python3
"""Remove the unsupported CARD tet(U) resistance causal graph.

The tet(U) ARO record is a historical negative control: CARD keeps the class but
its own definition says the Enterococcus faecium pKQ10 determinant was later
found to be a misannotated gene product not involved in tetracycline
resistance.  The promoted MFS-efflux graph therefore overstates a resistance
mechanism that CARD itself no longer supports.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TARGET = (
    ROOT
    / "data"
    / "traits"
    / "function"
    / "resistance"
    / "aro"
    / "tet-u-aro3004650.yaml"
)
TARGET_ID = "ARO:3004650"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_ACTION = (
    "Removed unsupported tet(U) MFS-efflux causal graph; REVIEWED -> SEEDED"
)
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")
_MAPPING_STATUS = re.compile(r"^mapping_status:[ \t]*(.+?)[ \t]*$", re.M)


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def _remove_block(text: str, key: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.startswith(f"{key}:")), None)
    if start is None:
        return text

    end = start + 1
    while end < len(lines) and not (lines[end].strip() and _TOP_KEY.match(lines[end])):
        end += 1
    return "".join(lines[:start]) + "".join(lines[end:])


def _set_mapping_status(text: str, status: str) -> str:
    out, count = _MAPPING_STATUS.subn(f"mapping_status: {status}", text, count=1)
    if count != 1:
        raise ValueError("expected exactly one top-level mapping_status")
    return out


def repair_text(text: str, path: Path = TARGET) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    found = record.get("identifier") if isinstance(record, dict) else None
    if found != TARGET_ID:
        raise ValueError(f"{path}: expected {TARGET_ID}, found {found}")

    out = _set_mapping_status(text, "SEEDED")
    out = _remove_block(out, "causal_graphs")
    if HISTORY_ACTION not in out:
        out = append_to_section(
            out,
            "curation_history",
            _dump({"curation_history": [HISTORY_EVENT]}),
        )

    return out, out != text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the repair")
    args = parser.parse_args(argv)

    text = TARGET.read_text(encoding="utf-8")
    out, changed = repair_text(text, TARGET)
    if not changed:
        print(f"unchanged {TARGET.relative_to(ROOT)}")
        return 0

    if args.apply:
        TARGET.write_text(out, encoding="utf-8")
        print(f"repaired {TARGET.relative_to(ROOT)}")
    else:
        print(f"would repair {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
