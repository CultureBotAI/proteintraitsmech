#!/usr/bin/env python3
"""Remove unsupported molecular-bypass/glycopeptide-cluster parent drafts.

The molecular-bypass parent spans several unrelated mechanisms, and the
glycopeptide-cluster parent says only that Van genes confer glycopeptide
resistance.  Prior curation split their concrete descendants into specific Van,
Lpx, BacA/BcrC, and ddl models; these two abstract parents should not retain a
single auto-scaffolded causal graph.

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

HISTORY_TIMESTAMP = "2026-09-11T00:00:00Z"
HISTORY_CURATOR = "codex-causal-graph-quality"

BYPASS_ACTION = (
    "Removed broad molecular-bypass parent draft that mixes Van, Lpx, ddl, and "
    "undecaprenyl-pyrophosphate mechanisms"
)
GLYCOPEPTIDE_ACTION = (
    "Removed broad glycopeptide resistance-cluster parent draft that abstracts over "
    "multiple Van gene roles"
)

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    action: str


BYPASS_PARENT = Target(
    "ARO:3000012",
    "protein-s-conferring-antibiotic-resistance-via-molecular-bypass-aro3000012.yaml",
    BYPASS_ACTION,
)
GLYCOPEPTIDE_PARENT = Target(
    "ARO:3002976",
    "gene-s-or-protein-s-associated-with-a-glycopeptide-resistance-cluster-aro3002976.yaml",
    GLYCOPEPTIDE_ACTION,
)
TARGETS = (BYPASS_PARENT, GLYCOPEPTIDE_PARENT)
TARGET_BY_FILENAME = {target.filename: target for target in TARGETS}


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


def _history_event(action: str) -> dict[str, Any]:
    return {
        "timestamp": HISTORY_TIMESTAMP,
        "curator": HISTORY_CURATOR,
        "action": action,
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
        _dump({"curation_history": [_history_event(target.action)]}),
    )


def _require_identifier(text: str, target: Target, path: Path) -> None:
    record = yaml.safe_load(text)
    found = record.get("identifier") if isinstance(record, dict) else None
    if found != target.identifier:
        raise ValueError(f"{path}: expected {target.identifier}, found {found}")


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    target = TARGET_BY_FILENAME.get(path.name)
    if target is None:
        raise ValueError(f"{path}: not a broad bypass/glycopeptide target")

    _require_identifier(text, target, path)
    out = _remove_block(text, "causal_graphs")
    out = _append_history_once(out, target)
    return out, out != text


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one broad bypass/glycopeptide YAML file",
    )
    args = parser.parse_args()

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            before = path.read_text(encoding="utf-8")
            after, did_change = enrich_text(before, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue

        if not did_change:
            unchanged += 1
            continue

        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(after, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
