#!/usr/bin/env python3
"""Rewrite CGA/CKO/CMA/CME/CMH beta-lactamase graphs.

This exact score-77 slice contains class A and class C serine
beta-lactamases. It reuses the canonical beta-lactamase graph builder and
excludes the interleaved CmeABC efflux complex.

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

HISTORY_ACTION = "Completed CGA-CMH beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


_TARGET_ROWS = """
CLASS_A ARO:3004765 cga-beta-lactamase-aro3004765.yaml
CLASS_A ARO:3004766 cga-1-aro3004766.yaml
CLASS_A ARO:3004772 cko-beta-lactamase-aro3004772.yaml
CLASS_A ARO:3004773 cko-1-aro3004773.yaml
CLASS_A ARO:3004229 class-a-bacillus-anthracis-bla-beta-lactamase-aro3004229.yaml
CLASS_C ARO:3005397 cma-beta-lactamase-aro3005397.yaml
CLASS_C ARO:3006922 cma-1-aro3006922.yaml
CLASS_C ARO:3006923 cma-2-aro3006923.yaml
CLASS_A ARO:3004774 cme-beta-lactamase-aro3004774.yaml
CLASS_A ARO:3004775 cme-1-aro3004775.yaml
CLASS_A ARO:3006155 cme-2-aro3006155.yaml
CLASS_A ARO:3008084 cme-3-aro3008084.yaml
CLASS_C ARO:3004776 cmh-beta-lactamase-aro3004776.yaml
CLASS_C ARO:3004777 cmh-1-aro3004777.yaml
CLASS_C ARO:3006854 cmh-2-aro3006854.yaml
CLASS_C ARO:3006855 cmh-3-aro3006855.yaml
CLASS_C ARO:3006856 cmh-4-aro3006856.yaml
CLASS_C ARO:3006857 cmh-5-aro3006857.yaml
CLASS_C ARO:3006858 cmh-6-aro3006858.yaml
CLASS_C ARO:3008108 cmh-7-aro3008108.yaml
CLASS_C ARO:3008109 cmh-8-aro3008109.yaml
CLASS_C ARO:3008110 cmh-9-aro3008110.yaml
CLASS_C ARO:3008085 cmh-10-aro3008085.yaml
CLASS_C ARO:3008086 cmh-11-aro3008086.yaml
CLASS_C ARO:3008087 cmh-12-aro3008087.yaml
CLASS_C ARO:3008088 cmh-13-aro3008088.yaml
CLASS_C ARO:3008089 cmh-14-aro3008089.yaml
CLASS_C ARO:3008090 cmh-15-aro3008090.yaml
CLASS_C ARO:3008091 cmh-16-aro3008091.yaml
CLASS_C ARO:3008092 cmh-17-aro3008092.yaml
CLASS_C ARO:3008093 cmh-18-aro3008093.yaml
CLASS_C ARO:3008094 cmh-19-aro3008094.yaml
CLASS_C ARO:3008095 cmh-20-aro3008095.yaml
CLASS_C ARO:3008096 cmh-21-aro3008096.yaml
CLASS_C ARO:3008097 cmh-24-aro3008097.yaml
CLASS_C ARO:3008098 cmh-25-aro3008098.yaml
CLASS_C ARO:3008099 cmh-26-aro3008099.yaml
CLASS_C ARO:3008100 cmh-27-aro3008100.yaml
CLASS_C ARO:3008101 cmh-28-aro3008101.yaml
CLASS_C ARO:3008102 cmh-29-aro3008102.yaml
CLASS_C ARO:3008103 cmh-30-aro3008103.yaml
CLASS_C ARO:3008104 cmh-31-aro3008104.yaml
CLASS_C ARO:3008105 cmh-32-aro3008105.yaml
CLASS_C ARO:3008106 cmh-33-aro3008106.yaml
CLASS_C ARO:3008107 cmh-34-aro3008107.yaml
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
        raise ValueError(f"{path}: not a CGA-CMH beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the 46 CGA-CMH beta-lactamase YAML files",
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
