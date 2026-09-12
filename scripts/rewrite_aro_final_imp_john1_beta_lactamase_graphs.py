#!/usr/bin/env python3
"""Rewrite final IMP and JOHN-1 beta-lactamase causal-graph records.

These score-79 metallo-beta-lactamase records still have old canonical
beta-lactamase graphs with sparse edge descriptions and single-reference
evidence. This batch finishes IMP and includes JOHN-1.

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
    "action": "Completed final IMP and JOHN-1 beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "imp-44-aro3002235.yaml",
    "imp-45-aro3002236.yaml",
    "imp-46-aro3002237.yaml",
    "imp-48-aro3002239.yaml",
    "imp-49-aro3003657.yaml",
    "imp-5-aro3002196.yaml",
    "imp-50-aro3003658.yaml",
    "imp-51-aro3003659.yaml",
    "imp-52-aro3004823.yaml",
    "imp-53-aro3005463.yaml",
    "imp-54-aro3005464.yaml",
    "imp-55-aro3004494.yaml",
    "imp-56-aro3004495.yaml",
    "imp-58-aro3005465.yaml",
    "imp-59-aro3005466.yaml",
    "imp-6-aro3002197.yaml",
    "imp-60-aro3005467.yaml",
    "imp-61-aro3005468.yaml",
    "imp-62-aro3005469.yaml",
    "imp-63-aro3005470.yaml",
    "imp-64-aro3005471.yaml",
    "imp-65-aro3005472.yaml",
    "imp-66-aro3005473.yaml",
    "imp-67-aro3005474.yaml",
    "imp-68-aro3005019.yaml",
    "imp-69-aro3005475.yaml",
    "imp-7-aro3002198.yaml",
    "imp-70-aro3005476.yaml",
    "imp-71-aro3005477.yaml",
    "imp-73-aro3005478.yaml",
    "imp-74-aro3005479.yaml",
    "imp-75-aro3005480.yaml",
    "imp-76-aro3005481.yaml",
    "imp-77-aro3005482.yaml",
    "imp-78-aro3005483.yaml",
    "imp-79-aro3005484.yaml",
    "imp-8-aro3002199.yaml",
    "imp-80-aro3005485.yaml",
    "imp-81-aro3005486.yaml",
    "imp-82-aro3005487.yaml",
    "imp-83-aro3005488.yaml",
    "imp-84-aro3005489.yaml",
    "imp-85-aro3005490.yaml",
    "imp-86-aro3008220.yaml",
    "imp-87-aro3008221.yaml",
    "imp-88-aro3005491.yaml",
    "imp-89-aro3005492.yaml",
    "imp-9-aro3002200.yaml",
    "imp-90-aro3008222.yaml",
    "imp-91-aro3007460.yaml",
    "imp-92-aro3007462.yaml",
    "imp-93-aro3007463.yaml",
    "imp-94-aro3007464.yaml",
    "imp-95-aro3007465.yaml",
    "imp-96-aro3007461.yaml",
    "imp-97-aro3008223.yaml",
    "imp-98-aro3008224.yaml",
    "imp-99-aro3008225.yaml",
    "imp-beta-lactamase-aro3000020.yaml",
    "john-1-aro3000840.yaml",
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
        raise ValueError(f"{path}: not a final-IMP/JOHN-1 beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the final-IMP/JOHN-1 beta-lactamase YAML files",
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
