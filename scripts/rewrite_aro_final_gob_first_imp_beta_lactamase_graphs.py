#!/usr/bin/env python3
"""Rewrite final GOB and first IMP beta-lactamase causal-graph records.

These score-79 metallo-beta-lactamase records still have old canonical
beta-lactamase graphs with sparse edge descriptions and single-reference
evidence. This batch finishes GOB and starts IMP.

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
    "action": "Completed final GOB and first IMP beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "gob-43-aro3005692.yaml",
    "gob-44-aro3005693.yaml",
    "gob-45-aro3005694.yaml",
    "gob-46-aro3005695.yaml",
    "gob-47-aro3008196.yaml",
    "gob-48-aro3005696.yaml",
    "gob-49-aro3005697.yaml",
    "gob-5-aro3004812.yaml",
    "gob-50-aro3005698.yaml",
    "gob-51-aro3005699.yaml",
    "gob-52-aro3008197.yaml",
    "gob-53-aro3008198.yaml",
    "gob-6-aro3004813.yaml",
    "gob-7-aro3004814.yaml",
    "gob-8-aro3004815.yaml",
    "gob-9-aro3004816.yaml",
    "gob-beta-lactamase-aro3004212.yaml",
    "imp-1-aro3002192.yaml",
    "imp-10-aro3002201.yaml",
    "imp-100-aro3008215.yaml",
    "imp-101-aro3008216.yaml",
    "imp-102-aro3008217.yaml",
    "imp-104-aro3008218.yaml",
    "imp-105-aro3008219.yaml",
    "imp-11-aro3002202.yaml",
    "imp-12-aro3002203.yaml",
    "imp-13-aro3002204.yaml",
    "imp-14-aro3002205.yaml",
    "imp-15-aro3002206.yaml",
    "imp-16-aro3002207.yaml",
    "imp-17-aro3002208.yaml",
    "imp-18-aro3002209.yaml",
    "imp-19-aro3002210.yaml",
    "imp-2-aro3002193.yaml",
    "imp-20-aro3002211.yaml",
    "imp-21-aro3002212.yaml",
    "imp-22-aro3002213.yaml",
    "imp-23-aro3002214.yaml",
    "imp-24-aro3002215.yaml",
    "imp-25-aro3002216.yaml",
    "imp-26-aro3002217.yaml",
    "imp-27-aro3002218.yaml",
    "imp-28-aro3002219.yaml",
    "imp-29-aro3002220.yaml",
    "imp-3-aro3002194.yaml",
    "imp-30-aro3002221.yaml",
    "imp-31-aro3002222.yaml",
    "imp-32-aro3002223.yaml",
    "imp-33-aro3002224.yaml",
    "imp-34-aro3002225.yaml",
    "imp-35-aro3002226.yaml",
    "imp-36-aro3002227.yaml",
    "imp-37-aro3002228.yaml",
    "imp-38-aro3002229.yaml",
    "imp-39-aro3002230.yaml",
    "imp-4-aro3002195.yaml",
    "imp-40-aro3002231.yaml",
    "imp-41-aro3002232.yaml",
    "imp-42-aro3002233.yaml",
    "imp-43-aro3002234.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(identifier_from_filename(filename), filename, beta.GraphKind.METALLO)
    for filename in TARGET_FILENAMES
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
        raise ValueError(f"{path}: not a final-GOB/first-IMP beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the final-GOB/first-IMP beta-lactamase YAML files",
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
