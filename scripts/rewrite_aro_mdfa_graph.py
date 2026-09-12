#!/usr/bin/env python3
"""Supplement the Escherichia coli MdfA efflux graph.

The existing MdfA graph already has the right determinant/domain/fold/efflux
shape and described edges, but every edge is single-evidenced. This updater
retains that record-specific graph and adds complementary CARD, MFS-family,
Pfam, CATH, and chloramphenicol-export evidence.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rewrite_aro_pump_and_abcf_graphs as pump  # noqa: E402
from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

TARGET_ID = "ARO:3001328"
TARGET_FILENAME = "escherichia-coli-mdfa-aro3001328.yaml"

HISTORY_ACTION = "Supplemented Escherichia coli MdfA efflux graph evidence"
HISTORY_EVENT = {
    "timestamp": "2026-09-10T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MDF_A_EVIDENCE = {
    "reference": TARGET_ID,
    "snippet": (
        "Multidrug efflux pump in E. coli. This multidrug efflux system was "
        "originally identified as the Cmr/CmlA chloramphenicol exporter."
    ),
    "notes": "CARD definition for Escherichia coli MdfA.",
}

MDF_A_CHLORAMPHENICOL_EVIDENCE = {
    "reference": "PMID:9811673",
    "snippet": (
        "Multidrug efflux pump in E. coli. This multidrug efflux system was "
        "originally identified as the Cmr/CmlA chloramphenicol exporter."
    ),
    "notes": "ARO-cited evidence that MdfA was originally identified as Cmr/CmlA.",
}

MFS_MEMBERSHIP_EVIDENCE = (
    MDF_A_EVIDENCE,
    pump.MFS_EVIDENCE,
)

MFS_MECHANISM_EVIDENCE = (
    MDF_A_EVIDENCE,
    pump.ANTIBIOTIC_EFFLUX_EVIDENCE,
    pump.EFFLUX_PUMP_EVIDENCE,
    pump.MFS_EVIDENCE,
    pump.MFS_TRANSPORT_EVIDENCE,
)

DOMAIN_EVIDENCE = (
    MDF_A_EVIDENCE,
    pump.MFS_EVIDENCE,
    pump.MFS_DOMAIN_EVIDENCE,
)

FOLD_EVIDENCE = (
    MDF_A_EVIDENCE,
    pump.MFS_EVIDENCE,
    pump.MFS_DOMAIN_EVIDENCE,
    pump.MFS_FOLD_EVIDENCE,
)

EDGE_EVIDENCE_BY_KEY = {
    ("mdfa", "RO:0002350", "mfs_family"): MFS_MEMBERSHIP_EVIDENCE,
    ("mdfa", "RO:0002327", "efflux"): MFS_MECHANISM_EVIDENCE,
    ("efflux", "RO:0002233", "chloramphenicol"): (
        MDF_A_EVIDENCE,
        MDF_A_CHLORAMPHENICOL_EVIDENCE,
        pump.MFS_TRANSPORT_EVIDENCE,
    ),
    ("efflux", "RO:0002411", "resistance"): MFS_MECHANISM_EVIDENCE,
    ("mdfa", "RO:0002411", "resistance"): MFS_MECHANISM_EVIDENCE,
    ("mfs_domain", "BFO:0000050", "mdfa"): DOMAIN_EVIDENCE,
    ("mdfa", "RO:0002350", "mfs_fold"): FOLD_EVIDENCE,
    ("mfs_domain", "RO:0002327", "efflux"): DOMAIN_EVIDENCE + (
        pump.MFS_TRANSPORT_EVIDENCE,
    ),
}


def _dump(obj: Any) -> str:
    return yaml.safe_dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )


def _dicts(value: Any, *, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"expected {label} to be a list")
    if not all(isinstance(item, dict) for item in value):
        raise ValueError(f"expected every {label} item to be a mapping")
    return value


def _append_unique_evidence(
    edge: dict[str, Any],
    evidence_items: tuple[dict[str, str], ...],
) -> bool:
    evidence = _dicts(edge.setdefault("evidence", []), label="edge evidence")
    seen = {item.get("reference") for item in evidence}

    changed = False
    for item in evidence_items:
        if item["reference"] in seen:
            continue
        evidence.append(copy.deepcopy(item))
        seen.add(item["reference"])
        changed = True
    return changed


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != TARGET_ID:
        raise ValueError(f"expected {TARGET_ID}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    graphs = _dicts(out.get("causal_graphs"), label="causal_graphs")
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError("expected exactly one resistance causal graph")

    edges = _dicts(graphs[0].get("edges"), label="causal_graphs.edges")
    seen_edges: set[tuple[str, str, str]] = set()
    changed = False
    for edge in edges:
        key = (
            str(edge.get("subject")),
            str(edge.get("predicate_id")),
            str(edge.get("object")),
        )
        if key not in EDGE_EVIDENCE_BY_KEY:
            continue

        seen_edges.add(key)
        changed |= _append_unique_evidence(edge, EDGE_EVIDENCE_BY_KEY[key])

    missing_edges = sorted(set(EDGE_EVIDENCE_BY_KEY) - seen_edges)
    if missing_edges:
        missing = ", ".join(" → ".join(key) for key in missing_edges)
        raise ValueError(f"missing expected edge(s): {missing}")

    return out, changed


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    if path.name != TARGET_FILENAME:
        raise ValueError(f"{path}: target {TARGET_ID} must be in {TARGET_FILENAME}")

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    history = _dicts(record.get("curation_history"), label="curation_history")
    if not any(item.get("action") == HISTORY_ACTION for item in history):
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
    return [path / TARGET_FILENAME]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or the Escherichia coli MdfA YAML file",
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
