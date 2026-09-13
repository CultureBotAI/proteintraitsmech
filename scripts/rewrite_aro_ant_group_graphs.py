#!/usr/bin/env python3
"""Rewrite remaining ANT aminoglycoside nucleotidyltransferase ARO graphs.

The rank-77 ANT(2''), ANT(3''), ANT(4'), ANT(6), and ANT(9) group records still
have the old promoted aminoglycoside nucleotidyltransferase graph. Reuse the
ATP-dependent adenylylation model that already curates the aad ANT leaves.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rewrite_aro_aad_graphs as aad  # noqa: E402

ARO_DIR = aad.ARO_DIR

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed ANT aminoglycoside nucleotidyltransferase causal graphs",
    "llm_assisted": True,
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3004276", "ant-2-aro3004276.yaml"),
    Target("ARO:3007405", "ant-2-i-aro3007405.yaml"),
    Target("ARO:3000230", "ant-2-ia-aro3000230.yaml"),
    Target("ARO:3004275", "ant-3-aro3004275.yaml"),
    Target("ARO:3007407", "ant-3-i-aro3007407.yaml"),
    Target("ARO:3000232", "ant-3-ia-aro3000232.yaml"),
    Target("ARO:3005062", "ant-3-ib-aro3005062.yaml"),
    Target("ARO:3004089", "ant-3-iia-aro3004089.yaml"),
    Target("ARO:3004090", "ant-3-iib-aro3004090.yaml"),
    Target("ARO:3004091", "ant-3-iic-aro3004091.yaml"),
    Target("ARO:3000229", "ant-4-aro3000229.yaml"),
    Target("ARO:3007403", "ant-4-i-aro3007403.yaml"),
    Target("ARO:3002623", "ant-4-ia-aro3002623.yaml"),
    Target("ARO:3003905", "ant-4-ib-aro3003905.yaml"),
    Target("ARO:3007404", "ant-4-ii-aro3007404.yaml"),
    Target("ARO:3002624", "ant-4-iia-aro3002624.yaml"),
    Target("ARO:3002625", "ant-4-iib-aro3002625.yaml"),
    Target("ARO:3000225", "ant-6-aro3000225.yaml"),
    Target("ARO:3007399", "ant-6-i-aro3007399.yaml"),
    Target("ARO:3002626", "ant-6-ia-aro3002626.yaml"),
    Target("ARO:3002629", "ant-6-ib-aro3002629.yaml"),
    Target("ARO:3000228", "ant-9-aro3000228.yaml"),
    Target("ARO:3007400", "ant-9-i-aro3007400.yaml"),
    Target("ARO:3002630", "ant-9-ia-aro3002630.yaml"),
    Target("ARO:3007401", "ant-9-ib-aro3007401.yaml"),
    Target("ARO:3007515", "ant-9-ic-aro3007515.yaml"),
)
TARGET_BY_ID = {target.identifier: target for target in TARGETS}


def enrich_record(record: dict, target: Target) -> tuple[dict, bool]:
    return aad.enrich_record(record, target)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an ANT group target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = aad.replace_block(
        text,
        "causal_graphs",
        aad._dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_CURATOR not in out:
        out = aad.append_to_section(out, "curation_history", aad._dump({"curation_history": [HISTORY_EVENT]}))
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
        help="ARO directory or one of the 26 ANT group YAML files",
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
