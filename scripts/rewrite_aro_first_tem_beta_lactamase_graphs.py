#!/usr/bin/env python3
"""Rewrite the first TEM beta-lactamase causal-graph records.

These score-79 class A TEM beta-lactamase records still have old canonical
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

import rewrite_aro_early_beta_lactamase_graphs as beta  # noqa: E402
from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed first TEM beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "tem-1-aro3000873.yaml",
    "tem-10-aro3000882.yaml",
    "tem-100-aro3001366.yaml",
    "tem-101-aro3000964.yaml",
    "tem-102-aro3000965.yaml",
    "tem-103-aro3000966.yaml",
    "tem-104-aro3000967.yaml",
    "tem-105-aro3000968.yaml",
    "tem-106-aro3000969.yaml",
    "tem-107-aro3000970.yaml",
    "tem-108-aro3000971.yaml",
    "tem-109-aro3000972.yaml",
    "tem-11-aro3000883.yaml",
    "tem-110-aro3000973.yaml",
    "tem-111-aro3000974.yaml",
    "tem-112-aro3000975.yaml",
    "tem-113-aro3000976.yaml",
    "tem-114-aro3000977.yaml",
    "tem-115-aro3000978.yaml",
    "tem-116-aro3000979.yaml",
    "tem-117-aro3000980.yaml",
    "tem-118-aro3000981.yaml",
    "tem-119-aro3001367.yaml",
    "tem-12-aro3000884.yaml",
    "tem-120-aro3000982.yaml",
    "tem-121-aro3000983.yaml",
    "tem-122-aro3000984.yaml",
    "tem-123-aro3000985.yaml",
    "tem-124-aro3000986.yaml",
    "tem-125-aro3000987.yaml",
    "tem-126-aro3000988.yaml",
    "tem-127-aro3000989.yaml",
    "tem-128-aro3000990.yaml",
    "tem-129-aro3000993.yaml",
    "tem-13-aro3000885.yaml",
    "tem-130-aro3000994.yaml",
    "tem-131-aro3000995.yaml",
    "tem-132-aro3000996.yaml",
    "tem-133-aro3000997.yaml",
    "tem-134-aro3000998.yaml",
    "tem-135-aro3000999.yaml",
    "tem-136-aro3001000.yaml",
    "tem-137-aro3001001.yaml",
    "tem-138-aro3001002.yaml",
    "tem-139-aro3001003.yaml",
    "tem-140-aro3001368.yaml",
    "tem-141-aro3001004.yaml",
    "tem-142-aro3001005.yaml",
    "tem-143-aro3001006.yaml",
    "tem-144-aro3001007.yaml",
    "tem-145-aro3001012.yaml",
    "tem-146-aro3001013.yaml",
    "tem-147-aro3001014.yaml",
    "tem-148-aro3001015.yaml",
    "tem-149-aro3001016.yaml",
    "tem-15-aro3000886.yaml",
    "tem-150-aro3001017.yaml",
    "tem-151-aro3001018.yaml",
    "tem-152-aro3001019.yaml",
    "tem-153-aro3001369.yaml",
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
        raise ValueError(f"{path}: not a first TEM beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the first TEM beta-lactamase YAML files",
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
