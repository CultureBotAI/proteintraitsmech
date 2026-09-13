#!/usr/bin/env python3
"""Rewrite smaller score-78 PAM/YRC beta-lactamase causal graphs.

These class A, class C, and metallo-beta-lactamase records still have old
canonical beta-lactamase graphs with sparse edge descriptions and
single-reference evidence.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402
from rewrite_aro_early_beta_lactamase_graphs import (  # noqa: E402
    GraphKind,
    Target,
    enrich_record,
)

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed PAM/YRC beta-lactamase causal graphs",
    "llm_assisted": True,
}

TARGETS: tuple[Target, ...] = (
    Target("ARO:3007199", "pam-1-aro3007199.yaml", GraphKind.METALLO),
    Target("ARO:3007200", "pam-2-aro3007200.yaml", GraphKind.METALLO),
    Target("ARO:3007201", "pam-3-aro3007201.yaml", GraphKind.METALLO),
    Target("ARO:3008822", "pam-5-aro3008822.yaml", GraphKind.METALLO),
    Target("ARO:3007198", "pam-beta-lactamase-aro3007198.yaml", GraphKind.METALLO),
    Target("ARO:3006964", "pau-1-aro3006964.yaml", GraphKind.CLASS_A),
    Target("ARO:3005431", "pau-beta-lactamase-aro3005431.yaml", GraphKind.CLASS_A),
    Target("ARO:3006968", "pla-1-aro3006968.yaml", GraphKind.CLASS_A),
    Target("ARO:3006969", "pla-2a-aro3006969.yaml", GraphKind.CLASS_A),
    Target("ARO:3006970", "pla-3-aro3006970.yaml", GraphKind.CLASS_A),
    Target("ARO:3009030", "pla-4-aro3009030.yaml", GraphKind.CLASS_A),
    Target("ARO:3009031", "pla-5-aro3009031.yaml", GraphKind.CLASS_A),
    Target("ARO:3006971", "pla-6-aro3006971.yaml", GraphKind.CLASS_A),
    Target("ARO:3005433", "pla-beta-lactamase-aro3005433.yaml", GraphKind.CLASS_A),
    Target("ARO:3007085", "prc-1-aro3007085.yaml", GraphKind.CLASS_C),
    Target("ARO:3007084", "prc-beta-lactamase-aro3007084.yaml", GraphKind.CLASS_C),
    Target("ARO:3006978", "psv-1-aro3006978.yaml", GraphKind.CLASS_A),
    Target("ARO:3005438", "psv-beta-lactamase-aro3005438.yaml", GraphKind.CLASS_A),
    Target("ARO:3007648", "psz-1-aro3007648.yaml", GraphKind.CLASS_C),
    Target("ARO:3007647", "psz-beta-lactamase-aro3007647.yaml", GraphKind.CLASS_C),
    Target("ARO:3004291", "rhodobacter-sphaeroides-ampc-beta-lactamase-aro3004291.yaml", GraphKind.CLASS_C),
    Target("ARO:3002995", "rob-1-aro3002995.yaml", GraphKind.CLASS_A),
    Target("ARO:3005080", "rob-10-aro3005080.yaml", GraphKind.CLASS_A),
    Target("ARO:3007125", "rob-11-aro3007125.yaml", GraphKind.CLASS_A),
    Target("ARO:3007126", "rob-12-aro3007126.yaml", GraphKind.CLASS_A),
    Target("ARO:3005072", "rob-13-aro3005072.yaml", GraphKind.CLASS_A),
    Target("ARO:3005079", "rob-2-aro3005079.yaml", GraphKind.CLASS_A),
    Target("ARO:3005073", "rob-3-aro3005073.yaml", GraphKind.CLASS_A),
    Target("ARO:3005074", "rob-4-aro3005074.yaml", GraphKind.CLASS_A),
    Target("ARO:3005075", "rob-5-aro3005075.yaml", GraphKind.CLASS_A),
    Target("ARO:3005076", "rob-6-aro3005076.yaml", GraphKind.CLASS_A),
    Target("ARO:3005077", "rob-7-aro3005077.yaml", GraphKind.CLASS_A),
    Target("ARO:3005078", "rob-8-aro3005078.yaml", GraphKind.CLASS_A),
    Target("ARO:3002994", "rob-beta-lactamase-aro3002994.yaml", GraphKind.CLASS_A),
    Target("ARO:3004443", "rsa-beta-lactamase-aro3004443.yaml", GraphKind.CLASS_A),
    Target("ARO:3004444", "rsa1-1-aro3004444.yaml", GraphKind.CLASS_A),
    Target("ARO:3003557", "sfb-1-aro3003557.yaml", GraphKind.METALLO),
    Target("ARO:3007017", "shd-1-aro3007017.yaml", GraphKind.METALLO),
    Target("ARO:3007016", "shd-beta-lactamase-aro3007016.yaml", GraphKind.METALLO),
    Target("ARO:3003555", "shw-beta-lactamase-aro3003555.yaml", GraphKind.METALLO),
    Target("ARO:3007846", "sie-1-aro3007846.yaml", GraphKind.METALLO),
    Target("ARO:3007845", "sie-beta-lactamase-aro3007845.yaml", GraphKind.METALLO),
    Target("ARO:3003556", "slb-1-aro3003556.yaml", GraphKind.METALLO),
    Target("ARO:3007442", "ssa-aro3007442.yaml", GraphKind.CLASS_A),
    Target("ARO:3007439", "ssa-beta-lactamase-aro3007439.yaml", GraphKind.CLASS_A),
    Target("ARO:3000577", "subclass-b1-bacillus-cereus-bc-beta-lactamase-aro3000577.yaml", GraphKind.METALLO),
    Target("ARO:3004226", "subclass-b3-lra-beta-lactamase-aro3004226.yaml", GraphKind.METALLO),
    Target("ARO:3007001", "ter-1-aro3007001.yaml", GraphKind.CLASS_A),
    Target("ARO:3007007", "ter-2-aro3007007.yaml", GraphKind.CLASS_A),
    Target("ARO:3005453", "ter-beta-lactamase-aro3005453.yaml", GraphKind.CLASS_A),
    Target("ARO:3003202", "tla-1-aro3003202.yaml", GraphKind.CLASS_A),
    Target("ARO:3003203", "tla-2-aro3003203.yaml", GraphKind.CLASS_A),
    Target("ARO:3003204", "tla-3-aro3003204.yaml", GraphKind.CLASS_A),
    Target("ARO:3003201", "tla-beta-lactamase-aro3003201.yaml", GraphKind.CLASS_A),
    Target("ARO:3004105", "tmb-1-aro3004105.yaml", GraphKind.METALLO),
    Target("ARO:3004106", "tmb-2-aro3004106.yaml", GraphKind.METALLO),
    Target("ARO:3004104", "tmb-beta-lactamase-aro3004104.yaml", GraphKind.METALLO),
    Target("ARO:3004450", "tru-1-aro3004450.yaml", GraphKind.CLASS_C),
    Target("ARO:3004449", "tru-beta-lactamase-aro3004449.yaml", GraphKind.CLASS_C),
    Target("ARO:3000844", "tus-1-aro3000844.yaml", GraphKind.METALLO),
    Target("ARO:3004205", "tus-beta-lactamase-aro3004205.yaml", GraphKind.METALLO),
    Target("ARO:3007062", "vam-1-aro3007062.yaml", GraphKind.METALLO),
    Target("ARO:3007065", "vam-beta-lactamase-aro3007065.yaml", GraphKind.METALLO),
    Target("ARO:3007003", "vhh-1-aro3007003.yaml", GraphKind.CLASS_A),
    Target("ARO:3005455", "vhh-beta-lactamase-aro3005455.yaml", GraphKind.CLASS_A),
    Target("ARO:3007004", "vhw-1-aro3007004.yaml", GraphKind.CLASS_A),
    Target("ARO:3005456", "vhw-beta-lactamase-aro3005456.yaml", GraphKind.CLASS_A),
    Target("ARO:3007435", "wus-1-aro3007435.yaml", GraphKind.METALLO),
    Target("ARO:3007440", "wus-beta-lactamase-aro3007440.yaml", GraphKind.METALLO),
    Target("ARO:3003558", "y56-beta-lactamase-aro3003558.yaml", GraphKind.CLASS_A),
    Target("ARO:3005035", "yrc-1-aro3005035.yaml", GraphKind.CLASS_C),
    Target("ARO:3005034", "yrc-beta-lactamase-aro3005034.yaml", GraphKind.CLASS_C),
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
        raise ValueError(f"{path}: not a PAM/YRC beta-lactamase target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
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
        help="ARO directory or one of the PAM/YRC beta-lactamase YAML files",
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
