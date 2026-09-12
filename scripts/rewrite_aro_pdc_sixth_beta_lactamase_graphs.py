#!/usr/bin/env python3
"""Rewrite the sixth PDC beta-lactamase causal-graph batch.

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
    "action": "Completed sixth PDC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGET_FILENAMES: tuple[str, ...] = (
    "pdc-333-aro3006703.yaml",
    "pdc-334-aro3006704.yaml",
    "pdc-335-aro3006705.yaml",
    "pdc-336-aro3006706.yaml",
    "pdc-337-aro3005288.yaml",
    "pdc-338-aro3006707.yaml",
    "pdc-339-aro3006708.yaml",
    "pdc-34-aro3006709.yaml",
    "pdc-340-aro3006710.yaml",
    "pdc-341-aro3006711.yaml",
    "pdc-342-aro3006712.yaml",
    "pdc-343-aro3006713.yaml",
    "pdc-344-aro3006714.yaml",
    "pdc-345-aro3006715.yaml",
    "pdc-346-aro3005286.yaml",
    "pdc-347-aro3006716.yaml",
    "pdc-348-aro3006717.yaml",
    "pdc-349-aro3006718.yaml",
    "pdc-35-aro3006719.yaml",
    "pdc-350-aro3006720.yaml",
    "pdc-351-aro3006721.yaml",
    "pdc-352-aro3005290.yaml",
    "pdc-353-aro3006722.yaml",
    "pdc-354-aro3006723.yaml",
    "pdc-355-aro3006724.yaml",
    "pdc-356-aro3006725.yaml",
    "pdc-357-aro3006726.yaml",
    "pdc-358-aro3006727.yaml",
    "pdc-359-aro3006728.yaml",
    "pdc-36-aro3006729.yaml",
    "pdc-360-aro3006730.yaml",
    "pdc-361-aro3006731.yaml",
    "pdc-362-aro3006732.yaml",
    "pdc-363-aro3006733.yaml",
    "pdc-364-aro3006734.yaml",
    "pdc-365-aro3006735.yaml",
    "pdc-366-aro3006736.yaml",
    "pdc-367-aro3006737.yaml",
    "pdc-368-aro3006738.yaml",
    "pdc-369-aro3006739.yaml",
    "pdc-37-aro3006740.yaml",
    "pdc-370-aro3006741.yaml",
    "pdc-371-aro3006742.yaml",
    "pdc-372-aro3006743.yaml",
    "pdc-373-aro3006744.yaml",
    "pdc-374-aro3006745.yaml",
    "pdc-375-aro3006746.yaml",
    "pdc-376-aro3005302.yaml",
    "pdc-377-aro3006747.yaml",
    "pdc-378-aro3006748.yaml",
    "pdc-379-aro3006749.yaml",
    "pdc-38-aro3006750.yaml",
    "pdc-380-aro3005293.yaml",
    "pdc-381-aro3006751.yaml",
    "pdc-382-aro3006752.yaml",
    "pdc-383-aro3006753.yaml",
    "pdc-384-aro3005283.yaml",
    "pdc-385-aro3006754.yaml",
    "pdc-386-aro3006755.yaml",
    "pdc-387-aro3006756.yaml",
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
        raise ValueError(f"{path}: not a sixth-PDC beta-lactamase target: {identifier}")
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
        help="ARO directory or one of the sixth-PDC beta-lactamase YAML files",
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
