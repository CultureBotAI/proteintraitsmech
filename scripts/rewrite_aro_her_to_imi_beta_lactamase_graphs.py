#!/usr/bin/env python3
"""Rewrite low-score HER/HMB/IMI beta-lactamase graphs.

This targets the HER and IMI class A serine beta-lactamases plus the HMB
metallo-beta-lactamases. The lowercase imiH/imiS records are outside this exact
slice and are intentionally not matched by the ``imi-`` filename pattern.

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

import rewrite_aro_early_beta_lactamase_graphs as beta  # noqa: E402
from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed HER/HMB/IMI beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

CLASS_A_PREFIXES = ("her-", "imi-")
METALLO_PREFIXES = ("hmb-",)
TARGET_FILENAME = re.compile(
    r"^(?:"
    r"her-(?:\d+|beta-lactamase)|"
    r"hmb-(?:\d+|beta-lactamase)|"
    r"imi-(?:\d+|beta-lactamase)"
    r")-aro\d+\.yaml$"
)


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def is_target_path(path: Path) -> bool:
    return TARGET_FILENAME.fullmatch(path.name) is not None


def _kind_for_name(filename: str) -> beta.GraphKind:
    if filename.startswith(CLASS_A_PREFIXES):
        return beta.GraphKind.CLASS_A
    if filename.startswith(METALLO_PREFIXES):
        return beta.GraphKind.METALLO
    raise ValueError(f"{filename}: not a low-score HER/HMB/IMI beta-lactamase target")


def target_for_record(record: dict[str, Any], path: Path) -> beta.Target:
    if not is_target_path(path):
        raise ValueError(f"{path}: not a low-score HER/HMB/IMI beta-lactamase target")

    identifier = record.get("identifier")
    if not isinstance(identifier, str) or not identifier:
        raise ValueError(f"{path}: missing identifier")

    return beta.Target(identifier, path.name, _kind_for_name(path.name))


def _parts(target: beta.Target) -> beta.GraphParts:
    return beta._parts(target)


def enrich_record(record: dict[str, Any], target: beta.Target) -> tuple[dict[str, Any], bool]:
    return beta.enrich_record(record, target)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    target = target_for_record(record, path)
    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return sorted(child for child in path.iterdir() if child.is_file() and is_target_path(child))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the 38 low-score HER/HMB/IMI beta-lactamase YAML files",
    )
    args = parser.parse_args(argv)

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
