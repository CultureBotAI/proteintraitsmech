#!/usr/bin/env python3
"""Rewrite MIR/MOX beta-lactamase causal graphs.

These score-78 class C beta-lactamase records still have old canonical class C
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
    "action": "Completed MIR/MOX beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGETS: tuple[Target, ...] = (
    Target("ARO:3002166", "mir-1-aro3002166.yaml", GraphKind.CLASS_C),
    Target("ARO:3002175", "mir-10-aro3002175.yaml", GraphKind.CLASS_C),
    Target("ARO:3002176", "mir-11-aro3002176.yaml", GraphKind.CLASS_C),
    Target("ARO:3002177", "mir-12-aro3002177.yaml", GraphKind.CLASS_C),
    Target("ARO:3002178", "mir-13-aro3002178.yaml", GraphKind.CLASS_C),
    Target("ARO:3002179", "mir-14-aro3002179.yaml", GraphKind.CLASS_C),
    Target("ARO:3002180", "mir-15-aro3002180.yaml", GraphKind.CLASS_C),
    Target("ARO:3002181", "mir-16-aro3002181.yaml", GraphKind.CLASS_C),
    Target("ARO:3003173", "mir-17-aro3003173.yaml", GraphKind.CLASS_C),
    Target("ARO:3003139", "mir-18-aro3003139.yaml", GraphKind.CLASS_C),
    Target("ARO:3006859", "mir-19-aro3006859.yaml", GraphKind.CLASS_C),
    Target("ARO:3002168", "mir-2-aro3002168.yaml", GraphKind.CLASS_C),
    Target("ARO:3006860", "mir-20-aro3006860.yaml", GraphKind.CLASS_C),
    Target("ARO:3006861", "mir-21-aro3006861.yaml", GraphKind.CLASS_C),
    Target("ARO:3006862", "mir-22-aro3006862.yaml", GraphKind.CLASS_C),
    Target("ARO:3004745", "mir-23-aro3004745.yaml", GraphKind.CLASS_C),
    Target("ARO:3008373", "mir-24-aro3008373.yaml", GraphKind.CLASS_C),
    Target("ARO:3008374", "mir-25-aro3008374.yaml", GraphKind.CLASS_C),
    Target("ARO:3008375", "mir-27-aro3008375.yaml", GraphKind.CLASS_C),
    Target("ARO:3008376", "mir-28-aro3008376.yaml", GraphKind.CLASS_C),
    Target("ARO:3002169", "mir-3-aro3002169.yaml", GraphKind.CLASS_C),
    Target("ARO:3008377", "mir-30-aro3008377.yaml", GraphKind.CLASS_C),
    Target("ARO:3008378", "mir-31-aro3008378.yaml", GraphKind.CLASS_C),
    Target("ARO:3008379", "mir-32-aro3008379.yaml", GraphKind.CLASS_C),
    Target("ARO:3008380", "mir-33-aro3008380.yaml", GraphKind.CLASS_C),
    Target("ARO:3008381", "mir-34-aro3008381.yaml", GraphKind.CLASS_C),
    Target("ARO:3008382", "mir-35-aro3008382.yaml", GraphKind.CLASS_C),
    Target("ARO:3002167", "mir-4-aro3002167.yaml", GraphKind.CLASS_C),
    Target("ARO:3002170", "mir-5-aro3002170.yaml", GraphKind.CLASS_C),
    Target("ARO:3002171", "mir-6-aro3002171.yaml", GraphKind.CLASS_C),
    Target("ARO:3002172", "mir-7-aro3002172.yaml", GraphKind.CLASS_C),
    Target("ARO:3002174", "mir-9-aro3002174.yaml", GraphKind.CLASS_C),
    Target("ARO:3000058", "mir-beta-lactamase-aro3000058.yaml", GraphKind.CLASS_C),
    Target("ARO:3002182", "mox-1-aro3002182.yaml", GraphKind.CLASS_C),
    Target("ARO:3003140", "mox-10-aro3003140.yaml", GraphKind.CLASS_C),
    Target("ARO:3003141", "mox-11-aro3003141.yaml", GraphKind.CLASS_C),
    Target("ARO:3006477", "mox-12-aro3006477.yaml", GraphKind.CLASS_C),
    Target("ARO:3006478", "mox-13-aro3006478.yaml", GraphKind.CLASS_C),
    Target("ARO:3006479", "mox-14-aro3006479.yaml", GraphKind.CLASS_C),
    Target("ARO:3008383", "mox-15-aro3008383.yaml", GraphKind.CLASS_C),
    Target("ARO:3008384", "mox-16-aro3008384.yaml", GraphKind.CLASS_C),
    Target("ARO:3008385", "mox-17-aro3008385.yaml", GraphKind.CLASS_C),
    Target("ARO:3008386", "mox-18-aro3008386.yaml", GraphKind.CLASS_C),
    Target("ARO:3008387", "mox-19-aro3008387.yaml", GraphKind.CLASS_C),
    Target("ARO:3002183", "mox-2-aro3002183.yaml", GraphKind.CLASS_C),
    Target("ARO:3008388", "mox-20-aro3008388.yaml", GraphKind.CLASS_C),
    Target("ARO:3008389", "mox-21-aro3008389.yaml", GraphKind.CLASS_C),
    Target("ARO:3008390", "mox-22-aro3008390.yaml", GraphKind.CLASS_C),
    Target("ARO:3008391", "mox-23-aro3008391.yaml", GraphKind.CLASS_C),
    Target("ARO:3008392", "mox-24-aro3008392.yaml", GraphKind.CLASS_C),
    Target("ARO:3008393", "mox-25-aro3008393.yaml", GraphKind.CLASS_C),
    Target("ARO:3002186", "mox-3-aro3002186.yaml", GraphKind.CLASS_C),
    Target("ARO:3002184", "mox-4-aro3002184.yaml", GraphKind.CLASS_C),
    Target("ARO:3002188", "mox-5-aro3002188.yaml", GraphKind.CLASS_C),
    Target("ARO:3002185", "mox-6-aro3002185.yaml", GraphKind.CLASS_C),
    Target("ARO:3002189", "mox-7-aro3002189.yaml", GraphKind.CLASS_C),
    Target("ARO:3002190", "mox-8-aro3002190.yaml", GraphKind.CLASS_C),
    Target("ARO:3002191", "mox-9-aro3002191.yaml", GraphKind.CLASS_C),
    Target("ARO:3000083", "mox-beta-lactamase-aro3000083.yaml", GraphKind.CLASS_C),
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
        raise ValueError(f"{path}: not a MIR/MOX beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the MIR/MOX beta-lactamase YAML files",
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
