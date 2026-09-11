#!/usr/bin/env python3
"""Remove ARO auto-drafts that prior family curation deliberately refused.

These records were held back by evidence preconditions in earlier family rounds:
the almEFG term is an operon-level record, pgpB states no record-specific
resistance mechanism, and CARD states that YajC has an uncharacterized
AcrAB-TolC interaction rather than a curatable efflux role.

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

ALMEFG_ACTION = "Removed almEFG operon draft pending operon-level graph modelling"
PGPB_ACTION = "Removed pgpB draft with no record-specific resistance mechanism"
YAJC_ACTION = "Removed YajC draft with uncharacterized efflux-pump interaction"

_TOP_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    action: str


TARGETS = (
    Target("ARO:3007434", "almefg-aro3007434.yaml", ALMEFG_ACTION),
    Target("ARO:3003920", "pgpb-aro3003920.yaml", PGPB_ACTION),
    Target("ARO:3005040", "yajc-aro3005040.yaml", YAJC_ACTION),
)
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
        raise ValueError(f"{path}: not an unsupported ARO auto-draft target")

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
        help="ARO directory or one unsupported auto-draft YAML file",
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
