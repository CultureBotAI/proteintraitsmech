#!/usr/bin/env python3
"""Rewrite CphA/CPS/CRD3/CRH/CRP/crxA/CSA/CSP beta-lactamase graphs.

This exact score-77 slice contains class A serine beta-lactamases, class C
serine beta-lactamases, and class B metallo-beta-lactamases. It reuses the
canonical beta-lactamase graph builder and excludes the interleaved CRP efflux
regulator.

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

HISTORY_ACTION = "Completed CphA-CSP beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


_TARGET_ROWS = """
METALLO ARO:3000581 cpha-beta-lactamase-aro3000581.yaml
METALLO ARO:3003099 cpha2-aro3003099.yaml
METALLO ARO:3003093 cpha3-aro3003093.yaml
METALLO ARO:3003100 cpha4-aro3003100.yaml
METALLO ARO:3003101 cpha5-aro3003101.yaml
METALLO ARO:3003102 cpha6-aro3003102.yaml
METALLO ARO:3003103 cpha7-aro3003103.yaml
METALLO ARO:3003104 cpha8-aro3003104.yaml
METALLO ARO:3003716 cps-1-aro3003716.yaml
METALLO ARO:3004221 cps-beta-lactamase-aro3004221.yaml
METALLO ARO:3006864 crd3-1-aro3006864.yaml
METALLO ARO:3005398 crd3-beta-lactamase-aro3005398.yaml
CLASS_A ARO:3006865 crh-1-aro3006865.yaml
CLASS_A ARO:3006866 crh-2-aro3006866.yaml
CLASS_A ARO:3006867 crh-3-aro3006867.yaml
CLASS_A ARO:3005399 crh-beta-lactamase-aro3005399.yaml
CLASS_A ARO:3006868 crp-1-aro3006868.yaml
CLASS_A ARO:3005400 crp-beta-lactamase-aro3005400.yaml
METALLO ARO:3007118 crxa-aro3007118.yaml
CLASS_C ARO:3006869 csa-1-aro3006869.yaml
CLASS_C ARO:3006870 csa-2-aro3006870.yaml
CLASS_C ARO:3005401 csa-beta-lactamase-aro3005401.yaml
CLASS_A ARO:3006871 csp-1-aro3006871.yaml
CLASS_A ARO:3005402 csp-beta-lactamase-aro3005402.yaml
"""

TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(identifier, filename, beta.GraphKind(kind))
    for kind, identifier, filename in (
        line.split() for line in _TARGET_ROWS.strip().splitlines()
    )
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


def _parts(target: beta.Target) -> beta.GraphParts:
    return beta._parts(target)


def enrich_record(record: dict[str, Any], target: beta.Target) -> tuple[dict[str, Any], bool]:
    return beta.enrich_record(record, target)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a CphA-CSP beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the 24 CphA-CSP beta-lactamase YAML files",
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
