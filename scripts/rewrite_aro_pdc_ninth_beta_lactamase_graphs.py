#!/usr/bin/env python3
"""Rewrite the ninth PDC beta-lactamase causal-graph batch.

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
    "action": "Completed ninth PDC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "pdc-496-aro3008843.yaml",
    "pdc-497-aro3008844.yaml",
    "pdc-498-aro3008845.yaml",
    "pdc-499-aro3008846.yaml",
    "pdc-5-aro3002502.yaml",
    "pdc-50-aro3005147.yaml",
    "pdc-500-aro3008847.yaml",
    "pdc-501-aro3008848.yaml",
    "pdc-502-aro3008849.yaml",
    "pdc-503-aro3008850.yaml",
    "pdc-504-aro3008851.yaml",
    "pdc-505-aro3008852.yaml",
    "pdc-506-aro3008853.yaml",
    "pdc-507-aro3008854.yaml",
    "pdc-508-aro3008855.yaml",
    "pdc-509-aro3008856.yaml",
    "pdc-51-aro3005129.yaml",
    "pdc-510-aro3008857.yaml",
    "pdc-511-aro3008858.yaml",
    "pdc-512-aro3008859.yaml",
    "pdc-513-aro3008860.yaml",
    "pdc-514-aro3008861.yaml",
    "pdc-515-aro3008862.yaml",
    "pdc-516-aro3008863.yaml",
    "pdc-517-aro3008864.yaml",
    "pdc-518-aro3008865.yaml",
    "pdc-519-aro3008866.yaml",
    "pdc-52-aro3005141.yaml",
    "pdc-520-aro3008867.yaml",
    "pdc-521-aro3008868.yaml",
    "pdc-522-aro3008869.yaml",
    "pdc-523-aro3008870.yaml",
    "pdc-524-aro3008871.yaml",
    "pdc-525-aro3008872.yaml",
    "pdc-526-aro3008873.yaml",
    "pdc-527-aro3008874.yaml",
    "pdc-528-aro3008875.yaml",
    "pdc-529-aro3008876.yaml",
    "pdc-53-aro3005151.yaml",
    "pdc-530-aro3008877.yaml",
    "pdc-531-aro3008878.yaml",
    "pdc-532-aro3008879.yaml",
    "pdc-533-aro3008880.yaml",
    "pdc-534-aro3008881.yaml",
    "pdc-535-aro3008882.yaml",
    "pdc-536-aro3008883.yaml",
    "pdc-537-aro3008884.yaml",
    "pdc-538-aro3008885.yaml",
    "pdc-539-aro3008886.yaml",
    "pdc-54-aro3005135.yaml",
    "pdc-540-aro3008887.yaml",
    "pdc-541-aro3008888.yaml",
    "pdc-542-aro3008889.yaml",
    "pdc-543-aro3008890.yaml",
    "pdc-544-aro3008891.yaml",
    "pdc-545-aro3008892.yaml",
    "pdc-546-aro3008893.yaml",
    "pdc-547-aro3008894.yaml",
    "pdc-548-aro3008895.yaml",
    "pdc-549-aro3008896.yaml",
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
        raise ValueError(f"{path}: not a ninth-PDC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the ninth-PDC beta-lactamase YAML files",
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
