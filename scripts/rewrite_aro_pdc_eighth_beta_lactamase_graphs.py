#!/usr/bin/env python3
"""Rewrite the eighth PDC beta-lactamase causal-graph batch.

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
    "action": "Completed eighth PDC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "pdc-441-aro3006809.yaml",
    "pdc-442-aro3006810.yaml",
    "pdc-443-aro3006811.yaml",
    "pdc-444-aro3006812.yaml",
    "pdc-445-aro3006813.yaml",
    "pdc-446-aro3006814.yaml",
    "pdc-447-aro3006815.yaml",
    "pdc-448-aro3006816.yaml",
    "pdc-449-aro3005313.yaml",
    "pdc-45-aro3005145.yaml",
    "pdc-450-aro3006817.yaml",
    "pdc-451-aro3006818.yaml",
    "pdc-452-aro3006819.yaml",
    "pdc-453-aro3006820.yaml",
    "pdc-454-aro3006821.yaml",
    "pdc-455-aro3006822.yaml",
    "pdc-456-aro3006823.yaml",
    "pdc-457-aro3006824.yaml",
    "pdc-458-aro3006825.yaml",
    "pdc-459-aro3006826.yaml",
    "pdc-46-aro3006827.yaml",
    "pdc-460-aro3006828.yaml",
    "pdc-461-aro3005294.yaml",
    "pdc-462-aro3006829.yaml",
    "pdc-463-aro3006830.yaml",
    "pdc-464-aro3005291.yaml",
    "pdc-465-aro3006831.yaml",
    "pdc-466-aro3006832.yaml",
    "pdc-467-aro3006833.yaml",
    "pdc-468-aro3006834.yaml",
    "pdc-469-aro3006835.yaml",
    "pdc-47-aro3005128.yaml",
    "pdc-470-aro3006836.yaml",
    "pdc-471-aro3006837.yaml",
    "pdc-472-aro3006838.yaml",
    "pdc-473-aro3006839.yaml",
    "pdc-474-aro3006840.yaml",
    "pdc-475-aro3006841.yaml",
    "pdc-476-aro3006842.yaml",
    "pdc-477-aro3008824.yaml",
    "pdc-478-aro3008825.yaml",
    "pdc-479-aro3008826.yaml",
    "pdc-48-aro3005148.yaml",
    "pdc-480-aro3008827.yaml",
    "pdc-481-aro3008828.yaml",
    "pdc-482-aro3008829.yaml",
    "pdc-483-aro3008830.yaml",
    "pdc-484-aro3008831.yaml",
    "pdc-485-aro3008832.yaml",
    "pdc-486-aro3008833.yaml",
    "pdc-487-aro3008834.yaml",
    "pdc-488-aro3008835.yaml",
    "pdc-489-aro3008836.yaml",
    "pdc-49-aro3005146.yaml",
    "pdc-490-aro3008837.yaml",
    "pdc-491-aro3008838.yaml",
    "pdc-492-aro3008839.yaml",
    "pdc-493-aro3008840.yaml",
    "pdc-494-aro3008841.yaml",
    "pdc-495-aro3008842.yaml",
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
        raise ValueError(f"{path}: not an eighth-PDC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the eighth-PDC beta-lactamase YAML files",
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
