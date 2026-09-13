#!/usr/bin/env python3
"""Rewrite rifampin ADP-ribosyltransferase ARR ARO causal graphs.

ARR enzymes inactivate rifamycin antibiotics by transferring ADP-ribose from
NAD+ to rifampin.  The existing promoted graphs capture that chemistry, but
leave the activity node ungrounded, stop at the modified-drug state, and have
sparse edge descriptions.  This updater grounds the transferase activity and
terminates the chemical-inactivation path at resistance.

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

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-07T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": "Completed ARR rifamycin ADP-ribosylation causal graphs",
    "llm_assisted": True,
}

INACTIVATION_EVIDENCE = {
    "reference": "ARO:3000576",
    "snippet": "Enzymes that inactivate rifampin antibiotics by chemical modification.",
    "notes": "CARD definition for the rifampin inactivation enzyme parent.",
}

ADP_RIBOSYLATION_EVIDENCE = {
    "reference": "ARO:3000266",
    "snippet": "The inactivation of antibiotics by the enzymatic addition of ADP-ribose from NAD+.",
    "notes": "CARD definition for ADP-ribosylation of antibiotic conferring resistance.",
}

ARR_PARENT_EVIDENCE = {
    "reference": "ARO:3000390",
    "snippet": (
        "Rifampin ADP-ribosyltransferases inactivate rifampin at the 23-OH "
        "position using NAD+."
    ),
    "notes": "CARD definition for rifampin ADP-ribosyltransferase ARR enzymes.",
}

QUAN_1997_EVIDENCE = {
    "reference": "DOI:10.1128/AAC.41.11.2456",
    "snippet": (
        "Quan et al. cloned the M. smegmatis rifampin-ribosylating gene and "
        "showed that disruption increased rifampin susceptibility."
    ),
    "notes": "CARD-cited arr-1 evidence linking ribosylation activity to resistance.",
}

QUAN_1999_EVIDENCE = {
    "reference": "DOI:10.1128/AAC.43.1.181",
    "snippet": (
        "Quan et al. determined that the rifampin inactivation intermediate "
        "RIP-TAs is 23-(O-ADP-ribosyl)rifampin."
    ),
    "notes": "CARD-cited chemical evidence for 23-OH ADP-ribosylation of rifampin.",
}

BAYSAROWICH_2008_EVIDENCE = {
    "reference": "DOI:10.1073/pnas.0711939105",
    "snippet": (
        "Baysarowich et al. biochemically characterized ARR-mediated "
        "rifamycin ADP-ribosylation and resistance capacity."
    ),
    "notes": "CARD-cited structural and biochemical evidence for ARR enzymes.",
}

GO_ACTIVITY_EVIDENCE = {
    "reference": "GO:0003950",
    "snippet": "Catalysis of NAD+-dependent ADP-ribosyl transferase activity.",
    "notes": "GO grounding for the ARR transferase activity node.",
}

RIFAMYCIN_RELATION_EVIDENCE = {
    "reference": "ARO:3000390",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000157 ! rifamycin antibiotic",
    "notes": "Rifamycin drug-class relation asserted on the ARR parent.",
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

RIFAMYCIN_NODE = {
    "node_id": "drug0",
    "label": "rifamycin antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000157",
}

ADP_RIBOSYLATION_ACTIVITY_NODE = {
    "node_id": "adp_ribosylation",
    "label": "NAD+ ADP-ribosyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0003950",
    "description": "Grounded to the broad GO NAD+ ADP-ribosyltransferase activity term.",
}

NAD_NODE = {
    "node_id": "nad",
    "label": "NAD+",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:15846",
}

MODIFIED_NODE = {
    "node_id": "modified",
    "label": "ADP-ribosylated inactive rifampin",
    "node_type": "STATE",
    "description": (
        "Local state for rifampin after ARR-mediated transfer of ADP-ribose "
        "from NAD+ to the drug."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000390", "rifampin-adp-ribosyltransferase-arr-aro3000390.yaml"),
    Target("ARO:3002846", "arr-1-aro3002846.yaml"),
    Target("ARO:3002847", "arr-2-aro3002847.yaml"),
    Target("ARO:3002848", "arr-3-aro3002848.yaml"),
    Target("ARO:3002849", "arr-4-aro3002849.yaml"),
    Target("ARO:3002850", "arr-5-aro3002850.yaml"),
    Target("ARO:3002852", "arr-7-aro3002852.yaml"),
    Target("ARO:3002853", "arr-8-aro3002853.yaml"),
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
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
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
    common_evidence = (
        record_evidence,
        ARR_PARENT_EVIDENCE,
        ADP_RIBOSYLATION_EVIDENCE,
        BAYSAROWICH_2008_EVIDENCE,
    )
    chemical_evidence = (
        record_evidence,
        ARR_PARENT_EVIDENCE,
        ADP_RIBOSYLATION_EVIDENCE,
        QUAN_1999_EVIDENCE,
        BAYSAROWICH_2008_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → rifamycin ADP-ribosylation",
        "description": (
            "Curated resistance-causation graph for ARR-mediated rifamycin "
            "ADP-ribosylation and inactivation."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic inactivation",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001004",
            },
            {
                "node_id": "mech1",
                "label": "ADP-ribosylation of antibiotic conferring resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000266",
            },
            copy.deepcopy(RIFAMYCIN_NODE),
            copy.deepcopy(ADP_RIBOSYLATION_ACTIVITY_NODE),
            copy.deepcopy(NAD_NODE),
            copy.deepcopy(MODIFIED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies ARR enzymes under the broad antibiotic "
                "inactivation resistance mechanism.",
                record_evidence,
                INACTIVATION_EVIDENCE,
                ARR_PARENT_EVIDENCE,
                BAYSAROWICH_2008_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "ARR antibiotic inactivation results from enzymatic rifamycin "
                "ADP-ribosylation.",
                INACTIVATION_EVIDENCE,
                ADP_RIBOSYLATION_EVIDENCE,
                ARR_PARENT_EVIDENCE,
                BAYSAROWICH_2008_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies ARR enzymes under ADP-ribosylation of "
                "antibiotic conferring resistance.",
                *common_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The ADP-ribosylation resistance mechanism inactivates "
                "rifamycins by chemical modification.",
                *chemical_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables (ADP-ribosylates the drug)",
                "RO:0002327",
                "adp_ribosylation",
                "ARR enzymes catalyze NAD+-dependent rifamycin ADP-ribosylation.",
                *chemical_evidence,
                GO_ACTIVITY_EVIDENCE,
            ),
            _edge(
                "adp_ribosylation",
                "has input (the ADP-ribose donor)",
                "RO:0002233",
                "nad",
                "NAD+ is the ADP-ribose donor consumed by the ARR transferase "
                "reaction.",
                *chemical_evidence,
            ),
            _edge(
                "adp_ribosylation",
                "has input (the drug)",
                "RO:0002233",
                "drug0",
                "Rifamycin antibiotics are substrates for the ARR "
                "ADP-ribosyltransferase reaction.",
                *chemical_evidence,
                RIFAMYCIN_RELATION_EVIDENCE,
            ),
            _edge(
                "adp_ribosylation",
                "causally upstream of (inactivates the drug)",
                "RO:0002411",
                "modified",
                "ARR transfers ADP-ribose to rifampin, producing an "
                "ADP-ribosylated inactive drug state.",
                *chemical_evidence,
            ),
            _edge(
                "modified",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "ADP-ribosylated rifampin is inactive, lowering effective "
                "rifamycin exposure and causing the resistance phenotype.",
                *chemical_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "ARR enzymes confer rifamycin resistance through "
                "NAD+-dependent ADP-ribosylation and drug inactivation.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
                QUAN_1997_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts a rifamycin antibiotic drug-class relation on "
                "the ARR family.",
                record_evidence,
                RIFAMYCIN_RELATION_EVIDENCE,
                BAYSAROWICH_2008_EVIDENCE,
            ),
        ],
    }


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{target.identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing = {
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "adp_ribosylation",
        "nad",
        "modified",
        "resistance",
    } - node_ids
    if missing:
        missing_ids = ", ".join(sorted(missing))
        raise ValueError(f"{target.identifier}: missing node(s): {missing_ids}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an ARR target: {identifier}")
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
        help="ARO directory or one ARR YAML file",
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
