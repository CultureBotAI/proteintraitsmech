#!/usr/bin/env python3
"""Rewrite OKP/ORN beta-lactamase causal graphs.

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
    "action": "Completed OKP/ORN beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGETS: tuple[Target, ...] = (
    Target("ARO:3002418", "okp-a-1-aro3002418.yaml", GraphKind.CLASS_A),
    Target("ARO:3002427", "okp-a-10-aro3002427.yaml", GraphKind.CLASS_A),
    Target("ARO:3002428", "okp-a-11-aro3002428.yaml", GraphKind.CLASS_A),
    Target("ARO:3002429", "okp-a-12-aro3002429.yaml", GraphKind.CLASS_A),
    Target("ARO:3002430", "okp-a-13-aro3002430.yaml", GraphKind.CLASS_A),
    Target("ARO:3002431", "okp-a-14-aro3002431.yaml", GraphKind.CLASS_A),
    Target("ARO:3002432", "okp-a-15-aro3002432.yaml", GraphKind.CLASS_A),
    Target("ARO:3002433", "okp-a-16-aro3002433.yaml", GraphKind.CLASS_A),
    Target("ARO:3006141", "okp-a-17-aro3006141.yaml", GraphKind.CLASS_A),
    Target("ARO:3002419", "okp-a-2-aro3002419.yaml", GraphKind.CLASS_A),
    Target("ARO:3002420", "okp-a-3-aro3002420.yaml", GraphKind.CLASS_A),
    Target("ARO:3002421", "okp-a-4-aro3002421.yaml", GraphKind.CLASS_A),
    Target("ARO:3002422", "okp-a-5-aro3002422.yaml", GraphKind.CLASS_A),
    Target("ARO:3002423", "okp-a-6-aro3002423.yaml", GraphKind.CLASS_A),
    Target("ARO:3002424", "okp-a-7-aro3002424.yaml", GraphKind.CLASS_A),
    Target("ARO:3002425", "okp-a-8-aro3002425.yaml", GraphKind.CLASS_A),
    Target("ARO:3002426", "okp-a-9-aro3002426.yaml", GraphKind.CLASS_A),
    Target("ARO:3002434", "okp-b-1-aro3002434.yaml", GraphKind.CLASS_A),
    Target("ARO:3002443", "okp-b-10-aro3002443.yaml", GraphKind.CLASS_A),
    Target("ARO:3002444", "okp-b-11-aro3002444.yaml", GraphKind.CLASS_A),
    Target("ARO:3002445", "okp-b-12-aro3002445.yaml", GraphKind.CLASS_A),
    Target("ARO:3002446", "okp-b-13-aro3002446.yaml", GraphKind.CLASS_A),
    Target("ARO:3002447", "okp-b-14-aro3002447.yaml", GraphKind.CLASS_A),
    Target("ARO:3006142", "okp-b-16-aro3006142.yaml", GraphKind.CLASS_A),
    Target("ARO:3002450", "okp-b-17-aro3002450.yaml", GraphKind.CLASS_A),
    Target("ARO:3002451", "okp-b-18-aro3002451.yaml", GraphKind.CLASS_A),
    Target("ARO:3002452", "okp-b-19-aro3002452.yaml", GraphKind.CLASS_A),
    Target("ARO:3002435", "okp-b-2-aro3002435.yaml", GraphKind.CLASS_A),
    Target("ARO:3002453", "okp-b-20-aro3002453.yaml", GraphKind.CLASS_A),
    Target("ARO:3006143", "okp-b-21-aro3006143.yaml", GraphKind.CLASS_A),
    Target("ARO:3006144", "okp-b-22-aro3006144.yaml", GraphKind.CLASS_A),
    Target("ARO:3006145", "okp-b-23-aro3006145.yaml", GraphKind.CLASS_A),
    Target("ARO:3006146", "okp-b-24-aro3006146.yaml", GraphKind.CLASS_A),
    Target("ARO:3002436", "okp-b-3-aro3002436.yaml", GraphKind.CLASS_A),
    Target("ARO:3006147", "okp-b-34-aro3006147.yaml", GraphKind.CLASS_A),
    Target("ARO:3006148", "okp-b-36-aro3006148.yaml", GraphKind.CLASS_A),
    Target("ARO:3002437", "okp-b-4-aro3002437.yaml", GraphKind.CLASS_A),
    Target("ARO:3006149", "okp-b-40-aro3006149.yaml", GraphKind.CLASS_A),
    Target("ARO:3006150", "okp-b-41-aro3006150.yaml", GraphKind.CLASS_A),
    Target("ARO:3006151", "okp-b-45-aro3006151.yaml", GraphKind.CLASS_A),
    Target("ARO:3002438", "okp-b-5-aro3002438.yaml", GraphKind.CLASS_A),
    Target("ARO:3002439", "okp-b-6-aro3002439.yaml", GraphKind.CLASS_A),
    Target("ARO:3002440", "okp-b-7-aro3002440.yaml", GraphKind.CLASS_A),
    Target("ARO:3002441", "okp-b-8-aro3002441.yaml", GraphKind.CLASS_A),
    Target("ARO:3002442", "okp-b-9-aro3002442.yaml", GraphKind.CLASS_A),
    Target("ARO:3002417", "okp-beta-lactamase-aro3002417.yaml", GraphKind.CLASS_A),
    Target("ARO:3006152", "okp-c-1-aro3006152.yaml", GraphKind.CLASS_A),
    Target("ARO:3006153", "okp-d-1-aro3006153.yaml", GraphKind.CLASS_A),
    Target("ARO:3006957", "orn-1-aro3006957.yaml", GraphKind.CLASS_A),
    Target("ARO:3006958", "orn-2-aro3006958.yaml", GraphKind.CLASS_A),
    Target("ARO:3006959", "orn-3-aro3006959.yaml", GraphKind.CLASS_A),
    Target("ARO:3006960", "orn-4-aro3006960.yaml", GraphKind.CLASS_A),
    Target("ARO:3006961", "orn-5-aro3006961.yaml", GraphKind.CLASS_A),
    Target("ARO:3006962", "orn-6-aro3006962.yaml", GraphKind.CLASS_A),
    Target("ARO:3005429", "orn-beta-lactamase-aro3005429.yaml", GraphKind.CLASS_A),
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
        raise ValueError(f"{path}: not an OKP/ORN beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the OKP/ORN beta-lactamase YAML files",
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
