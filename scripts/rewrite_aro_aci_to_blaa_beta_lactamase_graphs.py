#!/usr/bin/env python3
"""Rewrite ACI-to-BlaA beta-lactamase graphs.

This targets the next low-scoring ACI, AIM, AmpC, AMZ, AST, BcII, BIM, and BlaA
records.  They split across class A, class C, and class B metallo-beta-lactamase
families and can use the canonical beta-lactamase graph builder while
preserving their direct CARD drug-class edges.

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

HISTORY_ACTION = "Completed ACI-to-BlaA beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGETS: tuple[beta.Target, ...] = (
    beta.Target("ARO:3004358", "aci-beta-lactamase-aro3004358.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3004359", "aci-1-aro3004359.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3004216", "aim-beta-lactamase-aro3004216.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3000853", "aim-1-aro3000853.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3008073", "aim-2-aro3008073.yaml", beta.GraphKind.METALLO),
    beta.Target(
        "ARO:3004232",
        "ampc-type-beta-lactamase-aro3004232.yaml",
        beta.GraphKind.CLASS_C,
    ),
    beta.Target(
        "ARO:3003796",
        "acinetobacter-baumannii-ampc-beta-lactamase-aro3003796.yaml",
        beta.GraphKind.CLASS_C,
    ),
    beta.Target("ARO:3007693", "amz-beta-lactamase-aro3007693.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3007694", "amz-1-aro3007694.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3004741", "ast-beta-lactamase-aro3004741.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3004740", "ast-1-aro3004740.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3002878", "bcii-aro3002878.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3007858", "bim-beta-lactamase-aro3007858.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3007859", "bim-1-aro3007859.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3004190", "blaa-beta-lactamase-aro3004190.yaml", beta.GraphKind.CLASS_A),
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


def enrich_record(record: dict[str, Any], target: beta.Target) -> tuple[dict[str, Any], bool]:
    return beta.enrich_record(record, target)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an ACI-to-BlaA beta-lactamase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

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
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the 15 ACI-to-BlaA beta-lactamase YAML files",
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
