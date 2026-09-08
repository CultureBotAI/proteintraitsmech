#!/usr/bin/env python3
"""Rewrite CblA/CBP/CcrA/CDA/Cep/CFE/CfiA/CfxA beta-lactamase graphs.

This exact score-77 slice contains class A serine beta-lactamases, class C
serine beta-lactamases, and class B metallo-beta-lactamases. It reuses the
canonical beta-lactamase graph builder for all three enzyme classes.

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

HISTORY_ACTION = "Completed CblA-CfxA beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


_TARGET_ROWS = """
CLASS_A ARO:3002998 cbla-beta-lactamase-aro3002998.yaml
CLASS_A ARO:3002999 cbla-1-aro3002999.yaml
CLASS_A ARO:3004763 cbp-beta-lactamase-aro3004763.yaml
CLASS_A ARO:3004764 cbp-1-aro3004764.yaml
METALLO ARO:3000578 ccra-aro3000578.yaml
CLASS_C ARO:3007649 cda-beta-lactamase-aro3007649.yaml
CLASS_C ARO:3007650 cda-1-aro3007650.yaml
CLASS_A ARO:3004192 cepa-beta-lactamase-aro3004192.yaml
CLASS_A ARO:3003559 cepa-aro3003559.yaml
CLASS_A ARO:3006224 cepa-29-aro3006224.yaml
CLASS_A ARO:3006225 cepa-44-aro3006225.yaml
CLASS_A ARO:3006226 cepa-49-aro3006226.yaml
CLASS_C ARO:3004199 ceps-beta-lactamase-aro3004199.yaml
CLASS_C ARO:3003553 ceps-aro3003553.yaml
CLASS_C ARO:3001856 cfe-1-aro3001856.yaml
CLASS_C ARO:3004464 cfe-2-aro3004464.yaml
METALLO ARO:3004200 cfia-beta-lactamase-aro3004200.yaml
METALLO ARO:3006906 cfia10-aro3006906.yaml
METALLO ARO:3006907 cfia11-aro3006907.yaml
METALLO ARO:3006908 cfia14-aro3006908.yaml
METALLO ARO:3006909 cfia17-aro3006909.yaml
METALLO ARO:3006910 cfia18-aro3006910.yaml
METALLO ARO:3006911 cfia19-aro3006911.yaml
METALLO ARO:3006912 cfia2-aro3006912.yaml
METALLO ARO:3006913 cfia21-aro3006913.yaml
METALLO ARO:3006914 cfia22-aro3006914.yaml
METALLO ARO:3006915 cfia23-aro3006915.yaml
METALLO ARO:3006916 cfia24-aro3006916.yaml
METALLO ARO:3006917 cfia26-aro3006917.yaml
METALLO ARO:3006918 cfia27-aro3006918.yaml
METALLO ARO:3009098 cfia28-aro3009098.yaml
METALLO ARO:3009099 cfia29-aro3009099.yaml
METALLO ARO:3009100 cfia30-aro3009100.yaml
METALLO ARO:3009101 cfia31-aro3009101.yaml
METALLO ARO:3006919 cfia4-aro3006919.yaml
METALLO ARO:3006920 cfia8-aro3006920.yaml
METALLO ARO:3006921 cfia9-aro3006921.yaml
CLASS_A ARO:3003000 cfxa-beta-lactamase-aro3003000.yaml
CLASS_A ARO:3003001 cfxa-aro3003001.yaml
CLASS_A ARO:3003002 cfxa2-aro3003002.yaml
CLASS_A ARO:3003003 cfxa3-aro3003003.yaml
CLASS_A ARO:3003005 cfxa4-aro3003005.yaml
CLASS_A ARO:3003096 cfxa5-aro3003096.yaml
CLASS_A ARO:3003097 cfxa6-aro3003097.yaml
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
        raise ValueError(f"{path}: not a CblA-CfxA beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the 44 CblA-CfxA beta-lactamase YAML files",
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
