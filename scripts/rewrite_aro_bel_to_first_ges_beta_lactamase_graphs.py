#!/usr/bin/env python3
"""Rewrite BEL through first GES beta-lactamase causal-graph records.

These score-79 class A and metallo-beta-lactamase records still have old
canonical beta-lactamase graphs with sparse edge descriptions and
single-reference evidence. This batch covers BEL, Bla2, CAM, CGB, EBR, FEZ,
and the first group of GES records.

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
    "action": "Completed BEL through first GES beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "bel-1-aro3002385.yaml",
    "bel-2-aro3002386.yaml",
    "bel-3-aro3002387.yaml",
    "bel-4-aro3006154.yaml",
    "bel-beta-lactamase-aro3002384.yaml",
    "bla2-aro3004189.yaml",
    "cam-1-aro3004559.yaml",
    "cam-2-aro3008083.yaml",
    "cam-beta-lactamase-aro3004558.yaml",
    "cgb-1-aro3000841.yaml",
    "cgb-beta-lactamase-aro3004203.yaml",
    "ebr-1-aro3000842.yaml",
    "ebr-2-aro3004463.yaml",
    "ebr-3-aro3005461.yaml",
    "ebr-4-aro3005462.yaml",
    "ebr-5-aro3007437.yaml",
    "ebr-beta-lactamase-aro3004204.yaml",
    "fez-1-aro3000606.yaml",
    "fez-beta-lactamase-aro3004211.yaml",
    "ges-1-aro3002330.yaml",
    "ges-10-aro3002339.yaml",
    "ges-11-aro3002340.yaml",
    "ges-12-aro3002341.yaml",
    "ges-13-aro3002342.yaml",
    "ges-14-aro3002343.yaml",
    "ges-15-aro3002344.yaml",
    "ges-16-aro3002345.yaml",
    "ges-17-aro3002346.yaml",
    "ges-18-aro3002347.yaml",
    "ges-19-aro3002348.yaml",
    "ges-2-aro3002331.yaml",
    "ges-20-aro3002349.yaml",
    "ges-21-aro3002350.yaml",
    "ges-22-aro3002351.yaml",
    "ges-23-aro3002352.yaml",
    "ges-24-aro3002353.yaml",
    "ges-25-aro3003185.yaml",
    "ges-26-aro3003181.yaml",
    "ges-27-aro3006156.yaml",
    "ges-28-aro3006157.yaml",
    "ges-29-aro3006158.yaml",
    "ges-3-aro3002332.yaml",
    "ges-30-aro3006159.yaml",
    "ges-31-aro3006160.yaml",
    "ges-32-aro3006161.yaml",
    "ges-33-aro3006162.yaml",
    "ges-34-aro3006163.yaml",
    "ges-35-aro3006164.yaml",
    "ges-36-aro3006165.yaml",
    "ges-37-aro3006166.yaml",
    "ges-38-aro3006167.yaml",
    "ges-39-aro3006168.yaml",
    "ges-4-aro3002333.yaml",
    "ges-40-aro3006169.yaml",
    "ges-41-aro3006170.yaml",
    "ges-42-aro3006171.yaml",
    "ges-43-aro3006172.yaml",
    "ges-44-aro3006173.yaml",
    "ges-45-aro3006174.yaml",
    "ges-46-aro3006175.yaml",
)


def identifier_from_filename(filename: str) -> str:
    aro_number = filename.rsplit("-aro", maxsplit=1)[1].removesuffix(".yaml")
    return f"ARO:{aro_number}"


def graph_kind_from_filename(filename: str) -> beta.GraphKind:
    if filename.startswith(("bel-", "ges-")):
        return beta.GraphKind.CLASS_A
    if filename.startswith(("bla2-", "cam-", "cgb-", "ebr-", "fez-")):
        return beta.GraphKind.METALLO
    raise ValueError(f"no beta-lactamase graph kind is configured for {filename}")


TARGETS: tuple[beta.Target, ...] = tuple(
    beta.Target(
        identifier_from_filename(filename),
        filename,
        graph_kind_from_filename(filename),
    )
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
        raise ValueError(f"{path}: not a BEL/first-GES beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the BEL/first-GES beta-lactamase YAML files",
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
