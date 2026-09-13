#!/usr/bin/env python3
"""Rewrite the first KPC beta-lactamase causal-graph record batch.

These score-80 class A beta-lactamase records still have old canonical graphs
with sparse edge descriptions and single-reference evidence.

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
    "action": "Completed first KPC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "kpc-10-aro3002320.yaml",
    "kpc-100-aro3007446.yaml",
    "kpc-101-aro3008231.yaml",
    "kpc-102-aro3008232.yaml",
    "kpc-103-aro3008233.yaml",
    "kpc-104-aro3008234.yaml",
    "kpc-105-aro3008235.yaml",
    "kpc-106-aro3008236.yaml",
    "kpc-107-aro3008237.yaml",
    "kpc-108-aro3008238.yaml",
    "kpc-109-aro3008239.yaml",
    "kpc-11-aro3002321.yaml",
    "kpc-110-aro3008240.yaml",
    "kpc-111-aro3008241.yaml",
    "kpc-112-aro3008242.yaml",
    "kpc-113-aro3008243.yaml",
    "kpc-114-aro3008244.yaml",
    "kpc-115-aro3008245.yaml",
    "kpc-116-aro3008246.yaml",
    "kpc-117-aro3008247.yaml",
    "kpc-118-aro3008248.yaml",
    "kpc-119-aro3008249.yaml",
    "kpc-12-aro3002322.yaml",
    "kpc-120-aro3008250.yaml",
    "kpc-121-aro3008251.yaml",
    "kpc-122-aro3008252.yaml",
    "kpc-123-aro3007196.yaml",
    "kpc-124-aro3008253.yaml",
    "kpc-125-aro3007633.yaml",
    "kpc-126-aro3008254.yaml",
    "kpc-127-aro3008255.yaml",
    "kpc-128-aro3008256.yaml",
    "kpc-129-aro3008257.yaml",
    "kpc-13-aro3002323.yaml",
    "kpc-130-aro3008258.yaml",
    "kpc-131-aro3008259.yaml",
    "kpc-132-aro3008260.yaml",
    "kpc-133-aro3008261.yaml",
    "kpc-134-aro3007857.yaml",
    "kpc-135-aro3007844.yaml",
    "kpc-136-aro3008262.yaml",
    "kpc-137-aro3008263.yaml",
    "kpc-138-aro3008264.yaml",
    "kpc-139-aro3008265.yaml",
    "kpc-14-aro3002324.yaml",
    "kpc-140-aro3008266.yaml",
    "kpc-141-aro3008267.yaml",
    "kpc-142-aro3008268.yaml",
    "kpc-143-aro3008269.yaml",
    "kpc-144-aro3008270.yaml",
    "kpc-145-aro3008271.yaml",
    "kpc-146-aro3008272.yaml",
    "kpc-147-aro3008273.yaml",
    "kpc-148-aro3008274.yaml",
    "kpc-149-aro3008275.yaml",
    "kpc-15-aro3002325.yaml",
    "kpc-150-aro3008276.yaml",
    "kpc-151-aro3008277.yaml",
    "kpc-152-aro3008278.yaml",
    "kpc-153-aro3008279.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(identifier_from_filename(filename), filename, beta.GraphKind.CLASS_A)
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
        raise ValueError(f"{path}: not a first KPC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the first KPC beta-lactamase YAML files",
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
