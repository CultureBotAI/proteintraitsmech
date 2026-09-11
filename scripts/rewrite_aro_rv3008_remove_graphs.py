#!/usr/bin/env python3
"""Remove unsupported Rv3008 causal-graph drafts.

Both Rv3008 records are too weak to carry a reviewed causal graph: the broad
antibiotic parent names neither a drug nor a specific molecular function, and
the pyrazinamide parent explicitly hedges both the function assignment and the
resistance contribution.

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


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    action: str

    @property
    def path(self) -> Path:
        return ARO_DIR / self.filename


BROAD_PARENT = Target(
    "ARO:3004988",
    "antibiotic-resistant-rv3008-aro3004988.yaml",
    "Removed generic Rv3008 parent mutation draft after holding the unsupported pyrazinamide graph",
)
PYRAZINAMIDE_PARENT = Target(
    "ARO:3004989",
    "pyrazinamide-resistant-rv3008-aro3004989.yaml",
    "Removed unsupported pyrazinamide Rv3008 draft; CARD hedges both function and resistance contribution",
)
TARGETS = (BROAD_PARENT, PYRAZINAMIDE_PARENT)

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")


def _dump(obj: Any) -> str:
    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=100)


def _remove_block(text: str, key: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.startswith(f"{key}:")), None)
    if start is None:
        return text

    end = start + 1
    while end < len(lines) and not (lines[end].strip() and _TOP_KEY.match(lines[end])):
        end += 1
    return "".join(lines[:start]) + "".join(lines[end:])


def _history_event(target: Target) -> dict[str, Any]:
    return {
        "timestamp": HISTORY_TIMESTAMP,
        "curator": HISTORY_CURATOR,
        "action": target.action,
        "llm_assisted": True,
    }


def _has_history_action(text: str, action: str) -> bool:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        return False
    history = record.get("curation_history")
    if not isinstance(history, list):
        return False
    return any(isinstance(event, dict) and event.get("action") == action for event in history)


def _append_history_once(text: str, target: Target) -> str:
    if _has_history_action(text, target.action):
        return text
    return append_to_section(
        text,
        "curation_history",
        _dump({"curation_history": [_history_event(target)]}),
    )


def _require_identifier(text: str, target: Target, path: Path) -> None:
    record = yaml.safe_load(text)
    found = record.get("identifier") if isinstance(record, dict) else None
    if found != target.identifier:
        raise ValueError(f"{path}: expected {target.identifier}, found {found}")


def remove_graph_text(text: str, target: Target, path: Path | None = None) -> tuple[str, bool]:
    _require_identifier(text, target, path or target.path)
    out = _remove_block(text, "causal_graphs")
    out = _append_history_once(out, target)
    return out, out != text


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    for target in TARGETS:
        if path.name == target.filename:
            return remove_graph_text(text, target, path)
    return text, False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the rewrite")
    args = parser.parse_args(argv)

    for target in TARGETS:
        text = target.path.read_text(encoding="utf-8")
        out, changed = enrich_text(text, target.path)
        if not changed:
            print(f"unchanged {target.path.relative_to(ROOT)}")
            continue
        if args.apply:
            target.path.write_text(out, encoding="utf-8")
            print(f"rewrote {target.path.relative_to(ROOT)}")
        else:
            print(f"would rewrite {target.path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
