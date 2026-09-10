#!/usr/bin/env python3
"""Rewrite VEB beta-lactamase causal graphs.

These score-78 class A beta-lactamase records still have old canonical class A
graphs with sparse edge descriptions and single-reference evidence.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402
from rewrite_aro_early_beta_lactamase_graphs import (  # noqa: E402
    GraphKind,
    Target,
    enrich_record,
)

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed VEB beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGETS: tuple[Target, ...] = (
    Target("ARO:3002370", "veb-1-aro3002370.yaml", GraphKind.CLASS_A),
    Target("ARO:3003146", "veb-10-aro3003146.yaml", GraphKind.CLASS_A),
    Target("ARO:3006208", "veb-11-aro3006208.yaml", GraphKind.CLASS_A),
    Target("ARO:3006209", "veb-12-aro3006209.yaml", GraphKind.CLASS_A),
    Target("ARO:3006210", "veb-13-aro3006210.yaml", GraphKind.CLASS_A),
    Target("ARO:3006211", "veb-14-aro3006211.yaml", GraphKind.CLASS_A),
    Target("ARO:3006212", "veb-15-aro3006212.yaml", GraphKind.CLASS_A),
    Target("ARO:3003712", "veb-16-aro3003712.yaml", GraphKind.CLASS_A),
    Target("ARO:3009078", "veb-16dep-aro3009078.yaml", GraphKind.CLASS_A),
    Target("ARO:3006213", "veb-17-aro3006213.yaml", GraphKind.CLASS_A),
    Target("ARO:3009079", "veb-18-aro3009079.yaml", GraphKind.CLASS_A),
    Target("ARO:3006214", "veb-19-aro3006214.yaml", GraphKind.CLASS_A),
    Target("ARO:3002371", "veb-2-aro3002371.yaml", GraphKind.CLASS_A),
    Target("ARO:3006215", "veb-20-aro3006215.yaml", GraphKind.CLASS_A),
    Target("ARO:3006216", "veb-21-aro3006216.yaml", GraphKind.CLASS_A),
    Target("ARO:3006217", "veb-22-aro3006217.yaml", GraphKind.CLASS_A),
    Target("ARO:3006218", "veb-23-aro3006218.yaml", GraphKind.CLASS_A),
    Target("ARO:3006219", "veb-24-aro3006219.yaml", GraphKind.CLASS_A),
    Target("ARO:3006220", "veb-25-aro3006220.yaml", GraphKind.CLASS_A),
    Target("ARO:3006221", "veb-26-aro3006221.yaml", GraphKind.CLASS_A),
    Target("ARO:3006222", "veb-27-aro3006222.yaml", GraphKind.CLASS_A),
    Target("ARO:3009080", "veb-28-aro3009080.yaml", GraphKind.CLASS_A),
    Target("ARO:3009081", "veb-29-aro3009081.yaml", GraphKind.CLASS_A),
    Target("ARO:3002372", "veb-3-aro3002372.yaml", GraphKind.CLASS_A),
    Target("ARO:3009082", "veb-30-aro3009082.yaml", GraphKind.CLASS_A),
    Target("ARO:3009083", "veb-31-aro3009083.yaml", GraphKind.CLASS_A),
    Target("ARO:3009084", "veb-32-aro3009084.yaml", GraphKind.CLASS_A),
    Target("ARO:3009085", "veb-33-aro3009085.yaml", GraphKind.CLASS_A),
    Target("ARO:3009086", "veb-34-aro3009086.yaml", GraphKind.CLASS_A),
    Target("ARO:3009087", "veb-35-aro3009087.yaml", GraphKind.CLASS_A),
    Target("ARO:3009088", "veb-36-aro3009088.yaml", GraphKind.CLASS_A),
    Target("ARO:3009089", "veb-37-aro3009089.yaml", GraphKind.CLASS_A),
    Target("ARO:3009090", "veb-38-aro3009090.yaml", GraphKind.CLASS_A),
    Target("ARO:3009091", "veb-39-aro3009091.yaml", GraphKind.CLASS_A),
    Target("ARO:3002373", "veb-4-aro3002373.yaml", GraphKind.CLASS_A),
    Target("ARO:3002375", "veb-5-aro3002375.yaml", GraphKind.CLASS_A),
    Target("ARO:3002374", "veb-6-aro3002374.yaml", GraphKind.CLASS_A),
    Target("ARO:3002376", "veb-7-aro3002376.yaml", GraphKind.CLASS_A),
    Target("ARO:3002377", "veb-8-aro3002377.yaml", GraphKind.CLASS_A),
    Target("ARO:3002378", "veb-9-aro3002378.yaml", GraphKind.CLASS_A),
    Target("ARO:3000043", "veb-beta-lactamase-aro3000043.yaml", GraphKind.CLASS_A),
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
        raise ValueError(f"{path}: not a VEB beta-lactamase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
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
        help="ARO directory or one of the VEB beta-lactamase YAML files",
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
