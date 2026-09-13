#!/usr/bin/env python3
"""Rewrite PER beta-lactamase causal-graph records.

These score-80 class A beta-lactamase records still have old canonical graphs
with sparse edge descriptions and single-reference evidence.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rewrite_aro_early_beta_lactamase_graphs as beta  # noqa: E402
from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed PER beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGETS: tuple[beta.Target, ...] = (
    beta.Target("ARO:3002363", "per-1-aro3002363.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006131", "per-10-aro3006131.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006132", "per-11-aro3006132.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006133", "per-12-aro3006133.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006134", "per-13-aro3006134.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006135", "per-14-aro3006135.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006136", "per-15-aro3006136.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006137", "per-16-aro3006137.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009027", "per-17-aro3009027.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009028", "per-18-aro3009028.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002364", "per-2-aro3002364.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002365", "per-3-aro3002365.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002366", "per-4-aro3002366.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002367", "per-5-aro3002367.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002368", "per-6-aro3002368.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002369", "per-7-aro3002369.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3003184", "per-8-aro3003184.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006138", "per-9-aro3006138.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3000056", "per-beta-lactamase-aro3000056.yaml", beta.GraphKind.CLASS_A),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a PER beta-lactamase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = beta.enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
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
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the PER beta-lactamase YAML files",
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
