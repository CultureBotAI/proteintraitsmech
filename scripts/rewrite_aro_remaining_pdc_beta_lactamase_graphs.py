#!/usr/bin/env python3
"""Rewrite the remaining PDC beta-lactamase causal-graph records.

These score-79 class C beta-lactamase records still have old canonical graphs
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
    "action": "Completed remaining PDC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "pdc-603-aro3008950.yaml",
    "pdc-604-aro3008951.yaml",
    "pdc-605-aro3008952.yaml",
    "pdc-606-aro3008953.yaml",
    "pdc-607-aro3008954.yaml",
    "pdc-608-aro3008955.yaml",
    "pdc-609-aro3008956.yaml",
    "pdc-61-aro3005144.yaml",
    "pdc-610-aro3008957.yaml",
    "pdc-611-aro3008958.yaml",
    "pdc-612-aro3008959.yaml",
    "pdc-613-aro3008960.yaml",
    "pdc-614-aro3008961.yaml",
    "pdc-615-aro3008962.yaml",
    "pdc-616-aro3008963.yaml",
    "pdc-617-aro3008964.yaml",
    "pdc-618-aro3008965.yaml",
    "pdc-619-aro3008966.yaml",
    "pdc-62-aro3005133.yaml",
    "pdc-620-aro3008967.yaml",
    "pdc-621-aro3008968.yaml",
    "pdc-622-aro3008969.yaml",
    "pdc-623-aro3008970.yaml",
    "pdc-624-aro3008971.yaml",
    "pdc-625-aro3008972.yaml",
    "pdc-626-aro3008973.yaml",
    "pdc-627-aro3008974.yaml",
    "pdc-628-aro3008975.yaml",
    "pdc-629-aro3008976.yaml",
    "pdc-63-aro3005124.yaml",
    "pdc-630-aro3008977.yaml",
    "pdc-631-aro3008978.yaml",
    "pdc-632-aro3008979.yaml",
    "pdc-633-aro3008980.yaml",
    "pdc-634-aro3008981.yaml",
    "pdc-635-aro3008982.yaml",
    "pdc-636-aro3008983.yaml",
    "pdc-637-aro3008984.yaml",
    "pdc-638-aro3008985.yaml",
    "pdc-639-aro3008986.yaml",
    "pdc-64-aro3006845.yaml",
    "pdc-640-aro3008987.yaml",
    "pdc-65-aro3005038.yaml",
    "pdc-66-aro3005126.yaml",
    "pdc-67-aro3005139.yaml",
    "pdc-68-aro3005122.yaml",
    "pdc-69-aro3005153.yaml",
    "pdc-7-aro3002506.yaml",
    "pdc-70-aro3005123.yaml",
    "pdc-71-aro3006846.yaml",
    "pdc-72-aro3005152.yaml",
    "pdc-73-aro3004336.yaml",
    "pdc-74-aro3004337.yaml",
    "pdc-75-aro3004338.yaml",
    "pdc-76-aro3004339.yaml",
    "pdc-77-aro3004340.yaml",
    "pdc-78-aro3004341.yaml",
    "pdc-79-aro3004342.yaml",
    "pdc-8-aro3002507.yaml",
    "pdc-80-aro3004343.yaml",
    "pdc-81-aro3004344.yaml",
    "pdc-82-aro3004345.yaml",
    "pdc-83-aro3004346.yaml",
    "pdc-84-aro3004347.yaml",
    "pdc-85-aro3004348.yaml",
    "pdc-86-aro3004349.yaml",
    "pdc-87-aro3004350.yaml",
    "pdc-88-aro3004351.yaml",
    "pdc-89-aro3004352.yaml",
    "pdc-9-aro3002508.yaml",
    "pdc-90-aro3004353.yaml",
    "pdc-91-aro3004354.yaml",
    "pdc-92-aro3004355.yaml",
    "pdc-93-aro3004356.yaml",
    "pdc-94-aro3006847.yaml",
    "pdc-95-aro3006848.yaml",
    "pdc-96-aro3006849.yaml",
    "pdc-97-aro3006850.yaml",
    "pdc-98-aro3006851.yaml",
    "pdc-99-aro3006852.yaml",
    "pdc-beta-lactamase-aro3000098.yaml",
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
        raise ValueError(f"{path}: not a remaining PDC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the remaining PDC beta-lactamase YAML files",
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
