#!/usr/bin/env python3
"""Rewrite lincosamide nucleotidyltransferase LNU ARO causal graphs.

LNU enzymes confer resistance by ATP-dependent nucleotidylation of
lincosamide antibiotics.  The existing promoted graphs leave the local
transferase node ungrounded, omit the ATP input, stop at the modified-drug
state, and have sparse edge descriptions.  This updater grounds the broad
nucleotidyltransferase activity, adds ATP, and terminates the inactivation path
at resistance.

The CARD lin record is intentionally excluded despite its inherited LNU parent:
its own definition describes an ABC-F ribosomal-protection protein.

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
    "action": "Completed LNU lincosamide nucleotidylation causal graphs",
    "llm_assisted": True,
}

INACTIVATION_EVIDENCE = {
    "reference": "ARO:3000557",
    "snippet": (
        "Enzyme that catalyzes the inactivation of an antibiotic resulting in "
        "resistance."
    ),
    "notes": "CARD definition for antibiotic inactivation enzymes.",
}

NUCLEOTIDYLATION_EVIDENCE = {
    "reference": "ARO:3000107",
    "snippet": "Modification by NMP, usually AMP.",
    "notes": "CARD definition for nucleotidylation of antibiotic conferring resistance.",
}

LNU_PARENT_EVIDENCE = {
    "reference": "ARO:3000221",
    "snippet": (
        "LNU enzymes confer lincosamide resistance by ATP-dependent "
        "modification of the 3' and/or 4'-hydroxyl groups of the "
        "methylthiolincosamide sugar."
    ),
    "notes": "CARD definition for lincosamide nucleotidyltransferases.",
}

LECLERCQ_EVIDENCE = {
    "reference": "DOI:10.1086/324626",
    "snippet": (
        "Leclercq reviewed lincosamide resistance mechanisms, including "
        "enzymatic drug inactivation."
    ),
    "notes": "CARD-cited review evidence for lincosamide resistance mechanisms.",
}

GO_TRANSFER_EVIDENCE = {
    "reference": "GO:0016779",
    "snippet": "Catalysis of the transfer of a nucleotidyl group to a reactant.",
    "notes": "GO grounding for the broad nucleotidyltransferase activity node.",
}

ATP_EVIDENCE = {
    "reference": "CHEBI:15422",
    "snippet": "ATP is an adenosine 5'-phosphate with a triphosphate at the 5'-phosphate.",
    "notes": "ChEBI grounding for the ATP input.",
}

LINCOSAMIDE_RELATION_EVIDENCE = {
    "reference": "ARO:3000221",
    "snippet": "relationship: confers_resistance_to_drug_class ARO:0000017 ! lincosamide antibiotic",
    "notes": "Lincosamide drug-class relation asserted on the LNU parent.",
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

LINCOSAMIDE_NODE = {
    "node_id": "drug0",
    "label": "lincosamide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000017",
}

TRANSFER_NODE = {
    "node_id": "transfer",
    "label": "nucleotidyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0016779",
    "description": (
        "Grounded to the broad GO nucleotidyltransferase activity term and "
        "scoped here to ATP-dependent lincosamide modification."
    ),
}

ATP_NODE = {
    "node_id": "atp",
    "label": "ATP",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:15422",
}

MODIFIED_NODE = {
    "node_id": "modified",
    "label": "nucleotidylated inactive lincosamide",
    "node_type": "STATE",
    "description": (
        "Local state for a lincosamide antibiotic after ATP-dependent "
        "nucleotidylation of its methylthiolincosamide sugar."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS: tuple[Target, ...] = (
    Target("ARO:3000221", "lincosamide-nucleotidyltransferase-lnu-aro3000221.yaml"),
    Target("ARO:3002879", "ling-aro3002879.yaml"),
    Target("ARO:3002835", "lnua-aro3002835.yaml"),
    Target("ARO:3002836", "lnub-aro3002836.yaml"),
    Target("ARO:3002837", "lnuc-aro3002837.yaml"),
    Target("ARO:3002838", "lnud-aro3002838.yaml"),
    Target("ARO:3003762", "lnue-aro3003762.yaml"),
    Target("ARO:3002839", "lnuf-aro3002839.yaml"),
    Target("ARO:3004085", "lnug-aro3004085.yaml"),
    Target("ARO:3004600", "lnuh-aro3004600.yaml"),
    Target("ARO:3004601", "lnup-aro3004601.yaml"),
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
        LNU_PARENT_EVIDENCE,
        NUCLEOTIDYLATION_EVIDENCE,
        LECLERCQ_EVIDENCE,
    )
    reaction_evidence = (
        record_evidence,
        LNU_PARENT_EVIDENCE,
        NUCLEOTIDYLATION_EVIDENCE,
        GO_TRANSFER_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → lincosamide nucleotidylation",
        "description": (
            "Curated resistance-causation graph for LNU-mediated "
            "ATP-dependent lincosamide nucleotidylation and inactivation."
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
                "label": "nucleotidylation of antibiotic conferring resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000107",
            },
            copy.deepcopy(LINCOSAMIDE_NODE),
            copy.deepcopy(TRANSFER_NODE),
            copy.deepcopy(ATP_NODE),
            copy.deepcopy(MODIFIED_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies LNU enzymes under the broad antibiotic "
                "inactivation resistance mechanism.",
                record_evidence,
                INACTIVATION_EVIDENCE,
                LNU_PARENT_EVIDENCE,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "LNU antibiotic inactivation results from ATP-dependent "
                "nucleotidylation of the lincosamide drug.",
                INACTIVATION_EVIDENCE,
                NUCLEOTIDYLATION_EVIDENCE,
                LNU_PARENT_EVIDENCE,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD classifies LNU enzymes under nucleotidylation of "
                "antibiotic conferring resistance.",
                *common_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The nucleotidylation resistance mechanism inactivates "
                "lincosamides by chemical modification.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables (modifies the drug)",
                "RO:0002327",
                "transfer",
                "LNU enzymes catalyze ATP-dependent lincosamide "
                "nucleotidylation.",
                *reaction_evidence,
            ),
            _edge(
                "transfer",
                "has input (the nucleotidyl donor)",
                "RO:0002233",
                "atp",
                "ATP is the donor used for LNU-mediated lincosamide "
                "nucleotidylation.",
                *reaction_evidence,
                ATP_EVIDENCE,
            ),
            _edge(
                "transfer",
                "has input (the drug)",
                "RO:0002233",
                "drug0",
                "Lincosamide antibiotics are substrates for the LNU "
                "nucleotidyltransferase reaction.",
                *reaction_evidence,
                LINCOSAMIDE_RELATION_EVIDENCE,
            ),
            _edge(
                "transfer",
                "causally upstream of (inactivates the drug)",
                "RO:0002411",
                "modified",
                "LNU activity modifies the methylthiolincosamide sugar to "
                "produce an inactive nucleotidylated lincosamide state.",
                *reaction_evidence,
            ),
            _edge(
                "modified",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Nucleotidylated lincosamides are inactive, lowering effective "
                "lincosamide exposure and causing the resistance phenotype.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "LNU enzymes confer lincosamide resistance through "
                "ATP-dependent nucleotidylation and drug inactivation.",
                *common_evidence,
                INACTIVATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "CARD asserts a lincosamide antibiotic drug-class relation on "
                "the LNU family.",
                record_evidence,
                LNU_PARENT_EVIDENCE,
                LINCOSAMIDE_RELATION_EVIDENCE,
                LECLERCQ_EVIDENCE,
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
        "transfer",
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
        raise ValueError(f"{path}: not an LNU target: {identifier}")
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
        help="ARO directory or one LNU YAML file",
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
