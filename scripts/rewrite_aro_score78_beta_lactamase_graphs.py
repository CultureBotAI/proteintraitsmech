#!/usr/bin/env python3
"""Rewrite score-78 beta-lactamase causal graphs.

These CAE, CAU, CHM, CIA, CIM, DIM, DYB, LRA, and Mycobacterium records have the
same old class A, class C, or metallo-beta-lactamase graph shape as the earlier
beta-lactamase curation targets, but still need edge descriptions and
multi-reference evidence.

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
    "action": "Completed score-78 beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGETS: tuple[Target, ...] = (
    Target("ARO:3007635", "cae-1-aro3007635.yaml", GraphKind.CLASS_A),
    Target("ARO:3007634", "cae-beta-lactamase-aro3007634.yaml", GraphKind.CLASS_A),
    Target("ARO:3000855", "cau-1-aro3000855.yaml", GraphKind.METALLO),
    Target("ARO:3004218", "cau-beta-lactamase-aro3004218.yaml", GraphKind.METALLO),
    Target("ARO:3007855", "chm-1-aro3007855.yaml", GraphKind.METALLO),
    Target("ARO:3007856", "chm-beta-lactamase-aro3007856.yaml", GraphKind.METALLO),
    Target("ARO:3004768", "cia-1-aro3004768.yaml", GraphKind.CLASS_A),
    Target("ARO:3004769", "cia-2-aro3004769.yaml", GraphKind.CLASS_A),
    Target("ARO:3004770", "cia-3-aro3004770.yaml", GraphKind.CLASS_A),
    Target("ARO:3004771", "cia-4-aro3004771.yaml", GraphKind.CLASS_A),
    Target("ARO:3004767", "cia-beta-lactamase-aro3004767.yaml", GraphKind.CLASS_A),
    Target("ARO:3007840", "cim-1-aro3007840.yaml", GraphKind.METALLO),
    Target("ARO:3007839", "cim-beta-lactamase-aro3007839.yaml", GraphKind.METALLO),
    Target("ARO:3004228", "class-a-lra-beta-lactamase-aro3004228.yaml", GraphKind.CLASS_A),
    Target(
        "ARO:3007179",
        "class-a-mycobacterium-abscessus-beta-lactamase-aro3007179.yaml",
        GraphKind.CLASS_A,
    ),
    Target(
        "ARO:3007181",
        "class-a-mycobacterium-tuberculosis-bla-beta-lactamase-aro3007181.yaml",
        GraphKind.CLASS_A,
    ),
    Target("ARO:3004231", "class-c-lra-beta-lactamase-aro3004231.yaml", GraphKind.CLASS_C),
    Target("ARO:3000848", "dim-1-aro3000848.yaml", GraphKind.METALLO),
    Target("ARO:3004208", "dim-beta-lactamase-aro3004208.yaml", GraphKind.METALLO),
    Target("ARO:3007861", "dyb-1-aro3007861.yaml", GraphKind.METALLO),
    Target("ARO:3007860", "dyb-beta-lactamase-aro3007860.yaml", GraphKind.METALLO),
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
        raise ValueError(f"{path}: not a score-78 beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the score-78 beta-lactamase YAML files",
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
