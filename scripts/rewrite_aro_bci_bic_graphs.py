#!/usr/bin/env python3
"""Rewrite Bc/BCL/BES/BIC class A beta-lactamase graphs.

These beta-lactamase records use the same canonical class A serine
beta-lactam hydrolysis graph as the earlier AER/AQU/ARL pass. This updater
reuses that builder but limits it to the exact Bc, BCL, BES, and BIC family
records so each run is deterministic and easy to audit.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rewrite_aro_early_beta_lactamase_graphs as beta  # noqa: E402
from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Completed Bc/BCL/BES/BIC class A beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}


_TARGET_ROWS = """
ARO:3007100 class-a-bacillus-cereus-bc-beta-lactamase-aro3007100.yaml
ARO:3002877 bci-aro3002877.yaml
ARO:3007101 bciii-aro3007101.yaml
ARO:3004748 bcl-beta-lactamase-aro3004748.yaml
ARO:3004749 bcl-1-aro3004749.yaml
ARO:3004750 bes-beta-lactamase-aro3004750.yaml
ARO:3004751 bes-1-aro3004751.yaml
ARO:3004752 bic-beta-lactamase-aro3004752.yaml
ARO:3004753 bic-1-aro3004753.yaml
ARO:3008080 bic-2-aro3008080.yaml
"""

TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(identifier, filename, beta.GraphKind.CLASS_A)
    for identifier, filename in (line.split() for line in _TARGET_ROWS.strip().splitlines())
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


def _dump(obj) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def enrich_record(record: dict, target: beta.Target) -> tuple[dict, bool]:
    return beta.enrich_record(record, target)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a Bc/BCL/BES/BIC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the ten Bc/BCL/BES/BIC beta-lactamase YAML files",
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
