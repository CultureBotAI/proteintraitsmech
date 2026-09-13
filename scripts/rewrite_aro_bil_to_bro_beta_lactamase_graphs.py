#!/usr/bin/env python3
"""Rewrite BIL/BJP/BKC/Bla/BMHC/BOR/BRO beta-lactamase graphs.

This exact alphabetic score-77 slice contains class A serine beta-lactamases,
class C serine beta-lactamases, and class B metallo-beta-lactamases. It reuses
the canonical class A/metallo graph builder from the earlier beta-lactamase
pass and supplies a generic, non-ADC class C graph for BIL.

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

HISTORY_ACTION = "Completed BIL-BRO beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

_TARGET_ROWS = """
CLASS_C ARO:3004754 bil-beta-lactamase-aro3004754.yaml
CLASS_C ARO:3004755 bil-1-aro3004755.yaml
METALLO ARO:3004219 bjp-beta-lactamase-aro3004219.yaml
METALLO ARO:3000856 bjp-1-aro3000856.yaml
CLASS_A ARO:3004756 bkc-beta-lactamase-aro3004756.yaml
CLASS_A ARO:3004757 bkc-1-aro3004757.yaml
CLASS_A ARO:3006223 bkc-2-aro3006223.yaml
CLASS_A ARO:3000090 bla1-aro3000090.yaml
CLASS_A ARO:3004233 blaf-family-beta-lactamase-aro3004233.yaml
CLASS_A ARO:3003562 blaf-aro3003562.yaml
CLASS_A ARO:3004197 blaz-beta-lactamase-aro3004197.yaml
METALLO ARO:3007866 bmhc-beta-lactamase-aro3007866.yaml
METALLO ARO:3008081 bmhc-1-aro3008081.yaml
CLASS_A ARO:3007867 bor-beta-lactamase-aro3007867.yaml
CLASS_A ARO:3008082 bor-1-aro3008082.yaml
CLASS_A ARO:3004760 bro-beta-lactamase-aro3004760.yaml
CLASS_A ARO:3004761 bro-1-aro3004761.yaml
CLASS_A ARO:3004762 bro-2-aro3004762.yaml
"""

GraphKind = beta.GraphKind
Target = beta.Target

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
        raise ValueError(f"{path}: not a BIL-BRO beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the 18 BIL-BRO beta-lactamase YAML files",
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
