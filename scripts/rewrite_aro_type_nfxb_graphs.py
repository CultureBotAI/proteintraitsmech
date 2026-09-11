#!/usr/bin/env python3
"""Curate Type A/B NfxB efflux-repressor graphs.

These records are subclasses of the NfxB repressor determinant rather than
MexCD-OprJ pump-complex records. Rewrite their stale efflux skeletons to the
curated NfxB regulatory model: NfxB mutation derepresses the mexCD-oprJ operon,
whose MexCD-OprJ product enables antibiotic efflux.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Curated Type A/B NfxB efflux-repressor graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-11T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

NFXB_PARENT_EVIDENCE = {
    "reference": "ARO:3000820",
    "snippet": (
        "NfxB is a repressor of the efflux pump mexCD-oprJ and itself (NfxB "
        "binds upstream of the nfxB gene and negatively regulates its own "
        "expression). Increased expression of MexCD–OprJ brought about by "
        "mutations in NfxB."
    ),
    "notes": "CARD definition for the NfxB repressor parent.",
}

MEXCD_OPRJ_EVIDENCE = {
    "reference": "ARO:3000797",
    "snippet": (
        "MexCD-OprJ is a multidrug efflux protein expressed in the Gram-negative "
        "Pseudomonas aeruginosa. MexC is the membrane fusion protein; MexD is "
        "the inner membrane transporter; and OprJ is the outer membrane "
        "channel. MexCD-OprJ is typically quiescent in wild-type cells, with "
        "expression following mutation of the nfxB gene that is divergently "
        "transcribed from the mexCD-oprJ operon and encodes a repressor of "
        "mexCD-oprJ expression."
    ),
    "notes": "CARD definition for the MexCD-OprJ efflux pump repressed by NfxB.",
}

GO_NEGATIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045892",
    "snippet": (
        "Any process that stops, prevents, or reduces the frequency, rate or extent "
        "of cellular DNA-templated transcription."
    ),
    "notes": "GO definition for the broad transcriptional repression process.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

PUMP_NODE = {
    "node_id": "pump",
    "label": "MexCD-OprJ",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000797",
    "description": "Grounded to CARD's MexCD-OprJ, the pump repressed by NfxB.",
}

REPRESSION_NODE = {
    "node_id": "repression",
    "label": "negative regulation of mexCD-oprJ transcription",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045892",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional repression "
        "process because NfxB represses mexCD-oprJ transcription."
    ),
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms "
        "but has no term for the resistance phenotype itself."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = (
    Target("ARO:3004059", "type-a-nfxb-aro3004059.yaml"),
    Target("ARO:3004060", "type-b-nfxb-aro3004060.yaml"),
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


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (item["reference"], item["snippet"])
        if key in seen:
            continue
        seen.add(key)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _graph(record: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    core_evidence = (
        record_evidence,
        NFXB_PARENT_EVIDENCE,
        MEXCD_OPRJ_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
    )
    regulation_evidence = (
        record_evidence,
        NFXB_PARENT_EVIDENCE,
        GO_NEGATIVE_TRANSCRIPTION_EVIDENCE,
    )
    pump_evidence = (
        record_evidence,
        NFXB_PARENT_EVIDENCE,
        MEXCD_OPRJ_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → MexCD-OprJ antibiotic efflux → resistance",
        "description": (
            "Curated resistance-causation graph for Type A/B NfxB repressor "
            "subclasses. The graph models NfxB mutation as loss of mexCD-oprJ "
            "transcriptional repression, derepressing the MexCD-OprJ efflux pump."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(PUMP_NODE),
            copy.deepcopy(REPRESSION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies these NfxB repressor subclasses under antibiotic efflux.",
                *core_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "NfxB mutation derepresses MexCD-OprJ to increase antibiotic efflux.",
                *core_evidence,
            ),
            _edge(
                "determinant",
                "negatively regulates (loss lifts the repression)",
                "RO:0002212",
                "repression",
                "Resistance-associated NfxB mutation is represented as loss of normal "
                "MexCD-OprJ repression.",
                *regulation_evidence,
            ),
            _edge(
                "repression",
                "negatively regulates (holds pump expression down)",
                "RO:0002212",
                "pump",
                "Normal NfxB-dependent transcriptional repression keeps MexCD-OprJ "
                "expression low.",
                *regulation_evidence,
            ),
            _edge(
                "pump",
                "enables (drug efflux)",
                "RO:0002327",
                "mech0",
                "MexCD-OprJ is the multidrug pump whose derepressed expression supplies "
                "antibiotic efflux.",
                *pump_evidence,
                ANTIBIOTIC_EFFLUX_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Derepressed MexCD-OprJ efflux confers the modeled antibiotic "
                "resistance phenotype.",
                *core_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"{target.filename}: expected {target.identifier}, found {record.get('identifier')}")
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")
    if len(_dicts(record.get("causal_graphs"))) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one causal graph")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out["causal_graphs"])
    out["mapping_status"] = "REVIEWED"
    out["causal_graphs"] = [_graph(out)]
    return out, out["causal_graphs"] != before or out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a Type A/B NfxB target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = text.replace("mapping_status: SEEDED", "mapping_status: REVIEWED", 1)
    out = replace_block(out, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed or out != text


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
        help="ARO directory or one Type A/B NfxB YAML file",
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
