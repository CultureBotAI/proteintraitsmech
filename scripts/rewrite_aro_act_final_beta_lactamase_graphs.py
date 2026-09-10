#!/usr/bin/env python3
"""Rewrite the final ACT class C beta-lactamase causal-graph batch.

These score-79 beta-lactamase records still have old canonical class C graphs
with sparse edge descriptions and single-reference evidence.  This batch
finishes the remaining ACT records after the first two ACC/ACT wrappers.

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
    "action": "Completed final ACT beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "act-40-aro3006235.yaml",
    "act-41-aro3006236.yaml",
    "act-42-aro3006237.yaml",
    "act-43-aro3006238.yaml",
    "act-44-aro3006239.yaml",
    "act-45-aro3006240.yaml",
    "act-46-aro3006241.yaml",
    "act-47-aro3006242.yaml",
    "act-48-aro3006243.yaml",
    "act-49-aro3006244.yaml",
    "act-5-aro3001824.yaml",
    "act-50-aro3006245.yaml",
    "act-51-aro3006246.yaml",
    "act-52-aro3006247.yaml",
    "act-53-aro3006248.yaml",
    "act-54-aro3006249.yaml",
    "act-55-aro3006250.yaml",
    "act-56-aro3006251.yaml",
    "act-57-aro3006252.yaml",
    "act-58-aro3006253.yaml",
    "act-59-aro3006254.yaml",
    "act-6-aro3001825.yaml",
    "act-60-aro3006255.yaml",
    "act-61-aro3006256.yaml",
    "act-62-aro3006257.yaml",
    "act-63-aro3006258.yaml",
    "act-64-aro3006259.yaml",
    "act-65-aro3006260.yaml",
    "act-66-aro3006261.yaml",
    "act-67-aro3006262.yaml",
    "act-68-aro3006263.yaml",
    "act-69-aro3006264.yaml",
    "act-7-aro3001830.yaml",
    "act-70-aro3006265.yaml",
    "act-72-aro3006266.yaml",
    "act-73-aro3006267.yaml",
    "act-74-aro3006268.yaml",
    "act-75-aro3006269.yaml",
    "act-76-aro3006270.yaml",
    "act-77-aro3006271.yaml",
    "act-78-aro3006272.yaml",
    "act-79-aro3006273.yaml",
    "act-8-aro3001831.yaml",
    "act-80-aro3006274.yaml",
    "act-81-aro3006275.yaml",
    "act-82-aro3006276.yaml",
    "act-83-aro3006277.yaml",
    "act-84-aro3006278.yaml",
    "act-85-aro3007958.yaml",
    "act-86-aro3007959.yaml",
    "act-87-aro3006279.yaml",
    "act-88-aro3007960.yaml",
    "act-89-aro3007961.yaml",
    "act-9-aro3001826.yaml",
    "act-90-aro3007962.yaml",
    "act-91-aro3007963.yaml",
    "act-92-aro3007964.yaml",
    "act-93-aro3007965.yaml",
    "act-94-aro3007966.yaml",
    "act-95-aro3007967.yaml",
    "act-96-aro3007968.yaml",
    "act-97-aro3007969.yaml",
    "act-98-aro3007970.yaml",
    "act-99-aro3007971.yaml",
    "act-beta-lactamase-aro3000072.yaml",
    "act-gc1-aro3007972.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(identifier_from_filename(filename), filename, beta.GraphKind.CLASS_C)
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
        raise ValueError(f"{path}: not a final ACT beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the final ACT beta-lactamase YAML files",
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
