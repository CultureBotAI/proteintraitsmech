#!/usr/bin/env python3
"""Remove unsupported CARD tetracycline MFS-efflux causal graphs.

Two low-scoring ARO records carried generic MFS-efflux graphs that overstate
what can be asserted for the specific class:

* tet(U) is a historical negative control: CARD keeps the class but its own
  definition says the Enterococcus faecium pKQ10 determinant was later found to
  be a misannotated gene product not involved in tetracycline resistance.
* tetR(G) is the repressor from the class G tetracycline element, while CARD
  already has tet(G) as the MFS efflux pump.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_TIMESTAMP = "2026-09-11T00:00:00Z"

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")
_MAPPING_STATUS = re.compile(r"^mapping_status:[ \t]*(.+?)[ \t]*$", re.M)


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    history_action: str

    @property
    def path(self) -> Path:
        return ARO_DIR / self.filename


TETU_ACTION = "Removed unsupported tet(U) MFS-efflux causal graph; REVIEWED -> SEEDED"
TETRG_ACTION = "Removed unsupported tetR(G) MFS-efflux causal graph; REVIEWED -> SEEDED"

TARGETS = (
    Target(
        identifier="ARO:3004650",
        filename="tet-u-aro3004650.yaml",
        history_action=TETU_ACTION,
    ),
    Target(
        identifier="ARO:3004653",
        filename="tetr-g-aro3004653.yaml",
        history_action=TETRG_ACTION,
    ),
)


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def _history_event(target: Target) -> dict[str, Any]:
    return {
        "timestamp": HISTORY_TIMESTAMP,
        "curator": HISTORY_CURATOR,
        "action": target.history_action,
        "llm_assisted": True,
    }


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


def repair_text(text: str, target: Target, path: Path | None = None) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    found = record.get("identifier") if isinstance(record, dict) else None
    if found != target.identifier:
        path = path or target.path
        raise ValueError(f"{path}: expected {target.identifier}, found {found}")

    out = _set_mapping_status(text, "SEEDED")
    out = _remove_block(out, "causal_graphs")
    if target.history_action not in out:
        out = append_to_section(
            out,
            "curation_history",
            _dump({"curation_history": [_history_event(target)]}),
        )

    return out, out != text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the repair")
    args = parser.parse_args(argv)

    for target in TARGETS:
        text = target.path.read_text(encoding="utf-8")
        out, changed = repair_text(text, target, target.path)
        if not changed:
            print(f"unchanged {target.path.relative_to(ROOT)}")
            continue

        if args.apply:
            target.path.write_text(out, encoding="utf-8")
            print(f"repaired {target.path.relative_to(ROOT)}")
        else:
            print(f"would repair {target.path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
