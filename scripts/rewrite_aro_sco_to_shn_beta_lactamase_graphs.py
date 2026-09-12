#!/usr/bin/env python3
"""Rewrite SCO-through-SHN beta-lactamase graphs.

These exact score-77 S-series records still use the old beta-lactamase
archetype. SCO, SED, SFC, SFO, and SGM are class A serine beta-lactamases;
SFDC is a class C serine beta-lactamase; SFH and SHN are class B
metallo-beta-lactamases. The alphabetically interleaved sdrM efflux pump is
intentionally excluded from this beta-lactamase wrapper.

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

HISTORY_ACTION = "Completed SCO-to-SHN beta-lactamase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGETS = (
    beta.Target("ARO:3004856", "sco-1-aro3004856.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3004855", "sco-beta-lactamase-aro3004855.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3003561", "sed-1-aro3003561.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009044", "sed-2-aro3009044.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3007880", "sed-beta-lactamase-aro3007880.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006985", "sfc-1-aro3006985.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009045", "sfc-2-aro3009045.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005443", "sfc-beta-lactamase-aro3005443.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3009046", "sfdc-1-aro3009046.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3007881", "sfdc-beta-lactamase-aro3007881.yaml", beta.GraphKind.CLASS_C),
    beta.Target("ARO:3000849", "sfh-1-aro3000849.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3004210", "sfh-beta-lactamase-aro3004210.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3006986", "sfo-1-aro3006986.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005444", "sfo-beta-lactamase-aro3005444.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006987", "sgm-1-aro3006987.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006988", "sgm-2-aro3006988.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006989", "sgm-3-aro3006989.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006990", "sgm-4-aro3006990.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006991", "sgm-5-aro3006991.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006992", "sgm-6-aro3006992.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006993", "sgm-7-aro3006993.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3005445", "sgm-beta-lactamase-aro3005445.yaml", beta.GraphKind.CLASS_A),
    beta.Target("ARO:3006994", "shn-1-aro3006994.yaml", beta.GraphKind.METALLO),
    beta.Target("ARO:3005446", "shn-beta-lactamase-aro3005446.yaml", beta.GraphKind.METALLO),
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


def enrich_record(
    record: dict[str, Any],
    target: beta.Target,
) -> tuple[dict[str, Any], bool]:
    return beta.enrich_record(record, target)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a SCO-to-SHN beta-lactamase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    history = beta._dicts(record.get("curation_history"))
    if not any(item.get("action") == HISTORY_ACTION for item in history):
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
        help="ARO directory or one SCO-to-SHN beta-lactamase YAML file",
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
