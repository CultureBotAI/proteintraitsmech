#!/usr/bin/env python3
"""Rewrite the fifth PDC beta-lactamase causal-graph batch.

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
    "action": "Completed fifth PDC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "pdc-279-aro3006653.yaml",
    "pdc-28-aro3005156.yaml",
    "pdc-280-aro3006654.yaml",
    "pdc-281-aro3006655.yaml",
    "pdc-282-aro3006656.yaml",
    "pdc-283-aro3006657.yaml",
    "pdc-284-aro3005276.yaml",
    "pdc-285-aro3005287.yaml",
    "pdc-286-aro3006658.yaml",
    "pdc-287-aro3006659.yaml",
    "pdc-288-aro3006660.yaml",
    "pdc-289-aro3006661.yaml",
    "pdc-290-aro3006662.yaml",
    "pdc-291-aro3006663.yaml",
    "pdc-292-aro3005307.yaml",
    "pdc-293-aro3005298.yaml",
    "pdc-294-aro3006664.yaml",
    "pdc-295-aro3006665.yaml",
    "pdc-296-aro3006666.yaml",
    "pdc-297-aro3006667.yaml",
    "pdc-298-aro3006668.yaml",
    "pdc-299-aro3006669.yaml",
    "pdc-3-aro3002500.yaml",
    "pdc-30-aro3006670.yaml",
    "pdc-300-aro3006671.yaml",
    "pdc-301-aro3006672.yaml",
    "pdc-302-aro3006673.yaml",
    "pdc-303-aro3006674.yaml",
    "pdc-304-aro3006675.yaml",
    "pdc-305-aro3006676.yaml",
    "pdc-306-aro3005301.yaml",
    "pdc-307-aro3006677.yaml",
    "pdc-308-aro3006678.yaml",
    "pdc-309-aro3006679.yaml",
    "pdc-31-aro3006680.yaml",
    "pdc-310-aro3006681.yaml",
    "pdc-311-aro3006682.yaml",
    "pdc-312-aro3006683.yaml",
    "pdc-313-aro3005310.yaml",
    "pdc-314-aro3006684.yaml",
    "pdc-315-aro3006685.yaml",
    "pdc-316-aro3006686.yaml",
    "pdc-317-aro3006687.yaml",
    "pdc-318-aro3006688.yaml",
    "pdc-319-aro3006689.yaml",
    "pdc-32-aro3006690.yaml",
    "pdc-320-aro3006691.yaml",
    "pdc-321-aro3006692.yaml",
    "pdc-322-aro3006693.yaml",
    "pdc-323-aro3005280.yaml",
    "pdc-324-aro3005279.yaml",
    "pdc-325-aro3006694.yaml",
    "pdc-326-aro3006695.yaml",
    "pdc-327-aro3006696.yaml",
    "pdc-328-aro3006697.yaml",
    "pdc-329-aro3006698.yaml",
    "pdc-33-aro3006699.yaml",
    "pdc-330-aro3006700.yaml",
    "pdc-331-aro3006701.yaml",
    "pdc-332-aro3006702.yaml",
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
        raise ValueError(f"{path}: not a fifth-PDC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the fifth-PDC beta-lactamase YAML files",
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
