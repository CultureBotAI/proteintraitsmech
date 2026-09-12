#!/usr/bin/env python3
"""Rewrite MCR phosphoethanolamine-transferase graphs.

MCR records share a phosphoethanolamine-transferase mechanism: MCR modifies
lipid A, reducing the negative cell-surface charge used by cationic peptide
antibiotics for binding. This updater replaces the old single-reference graph
with a grounded PEtN-transfer/charge-alteration graph.

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

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

MCR_PARENT_IDENTIFIER = "ARO:3004268"
MCR_PARENT_FILENAME = "mcr-phosphoethanolamine-transferase-aro3004268.yaml"

HISTORY_ACTION = "Completed MCR phosphoethanolamine-transferase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MCR_FAMILY_EVIDENCE = {
    "reference": MCR_PARENT_IDENTIFIER,
    "snippet": (
        "A group of mobile colistin resistance genes encode the MCR family of "
        "phosphoethanolamine transferases, which catalyze the addition of "
        "phosphoethanolamine onto lipid A, thus interfering with the binding of "
        "colistin to the cell membrane."
    ),
    "notes": "CARD definition for MCR phosphoethanolamine transferase.",
}

PETN_TRANSFERASE_EVIDENCE = {
    "reference": "ARO:3004112",
    "snippet": (
        "This group of enzymes catalyzes the addition of a phosphoethanolamine group "
        "to another molecule. The addition of this moiety to lipid A in bacterial "
        "species is often associated with polymyxin (otherwise known as colistin) "
        "resistance."
    ),
    "notes": "CARD definition for phosphoethanolamine transferases conferring colistin resistance.",
}

CHARGE_ALTERATION_EVIDENCE = {
    "reference": "ARO:3003588",
    "snippet": (
        "The loss or reduction of the net negative charge within the cell wall of gram "
        "negative bacteria is a mechanism of resistance for cationic antimicrobials "
        "that depend on the negative charge for binding to the surface."
    ),
    "notes": "CARD definition for the shared charge-alteration resistance mechanism.",
}

GO_PETN_TRANSFER_EVIDENCE = {
    "reference": "GO:0043838",
    "snippet": (
        "Catalysis of the reaction: Kdo2-lipid A + phosphatidylethanolamine = "
        "phosphoethanolamine-Kdo2-lipid A + diacylglycerol."
    ),
    "notes": (
        "GO reaction definition for the exact phosphatidylethanolamine:Kdo2-lipid A "
        "phosphoethanolamine transferase activity."
    ),
}

DOMAIN_EVIDENCE = {
    "reference": "InterPro:IPR058130",
    "snippet": "Phosphoethanolamine transferase, C-terminal domain",
    "notes": "InterPro family for the MCR phosphoethanolamine-transferase catalytic domain.",
}

FOLD_EVIDENCE = {
    "reference": "CATH:3.40.720.10",
    "snippet": "Alkaline Phosphatase, subunit A",
    "notes": "CATH fold for the alkaline-phosphatase/sulfatase superfamily.",
}

DRUG_RELATION_EVIDENCE = {
    "reference": MCR_PARENT_IDENTIFIER,
    "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
    "notes": "ARO drug-class relationship asserted on the MCR family term.",
}

PEPTIDE_ANTIBIOTIC_EVIDENCE = {
    "reference": "ARO:3000053",
    "snippet": "peptide antibiotic",
    "notes": "ARO drug class asserted on the MCR family.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "charge alteration conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3003588",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "peptide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000053",
}

DOMAIN_NODE = {
    "node_id": "domain",
    "label": "phosphoethanolamine transferase C-terminal domain",
    "node_type": "DOMAIN",
    "grounding": "InterPro:IPR058130",
    "description": "Catalytic MCR phosphoethanolamine-transferase domain.",
}

FOLD_NODE = {
    "node_id": "fold",
    "label": "alkaline phosphatase / sulfatase superfamily fold",
    "node_type": "DOMAIN",
    "grounding": "CATH:3.40.720.10",
    "description": "Alkaline-phosphatase/sulfatase superfamily fold adopted by the catalytic domain.",
}

PETN_TRANSFER_NODE = {
    "node_id": "petn_transfer",
    "label": "phosphatidylethanolamine:Kdo2-lipid A phosphoethanolamine transferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0043838",
    "description": (
        "Grounded to the GO molecular-function class for transfer of phosphoethanolamine "
        "from phosphatidylethanolamine to Kdo2-lipid A."
    ),
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the nearest "
        "available superclass: ARO models determinants and mechanisms but has no term "
        "for the resistance phenotype itself."
    ),
}

EXPECTED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("domain", "BFO:0000050", "determinant"),
    ("determinant", "RO:0002350", "fold"),
    ("domain", "RO:0002327", "petn_transfer"),
    ("determinant", "RO:0002327", "petn_transfer"),
    ("petn_transfer", "RO:0002411", "mech0"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "CARD classifies MCR enzymes under charge alteration because PEtN addition "
        "to lipid A reduces the negative surface charge used by polymyxins for "
        "binding."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Charge alteration is the broad resistance mechanism reached by MCR-mediated "
        "PEtN transfer to lipid A."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "MCR enzymes confer peptide-antibiotic resistance by modifying lipid A and "
        "reducing cationic antimicrobial binding."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps the MCR family to peptide antibiotics."
    ),
    ("domain", "BFO:0000050", "determinant"): (
        "The phosphoethanolamine-transferase catalytic domain is part of the MCR "
        "determinant."
    ),
    ("determinant", "RO:0002350", "fold"): (
        "The MCR determinant adopts an alkaline-phosphatase/sulfatase fold."
    ),
    ("domain", "RO:0002327", "petn_transfer"): (
        "The MCR C-terminal domain enables lipid A phosphoethanolamine transfer."
    ),
    ("determinant", "RO:0002327", "petn_transfer"): (
        "The MCR determinant enables PEtN transfer to lipid A."
    ),
    ("petn_transfer", "RO:0002411", "mech0"): (
        "MCR-mediated PEtN transfer to lipid A reduces net negative bacterial surface "
        "charge, the charge-alteration mechanism that impedes cationic peptide "
        "antibiotic binding."
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


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in record.get("evidence") or []
        if isinstance(item, dict) and item.get("reference")
    )


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": " ".join(str(record["definition"]).split()),
        "notes": f"CARD definition for {record['label']}.",
    }


def _family_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == MCR_PARENT_IDENTIFIER:
        return ()
    return (MCR_FAMILY_EVIDENCE,)


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item.get("snippet", ""),
            item.get("notes", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": EDGE_DESCRIPTIONS[(subject, predicate_id, object_)],
        "evidence": _unique_evidence(evidence),
    }


def _canonical_nodes(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "node_id": "determinant",
            "label": str(record["label"]),
            "node_type": "PROTEIN",
            "grounding": str(record["identifier"]),
        },
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(DOMAIN_NODE),
        copy.deepcopy(FOLD_NODE),
        copy.deepcopy(PETN_TRANSFER_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    record_evidence = _record_evidence(record)
    source_evidence = _source_evidence(record)
    family_evidence = _family_evidence(record)

    mechanism_evidence = (
        record_evidence,
        *family_evidence,
        PETN_TRANSFERASE_EVIDENCE,
        CHARGE_ALTERATION_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        record_evidence,
        *family_evidence,
        DRUG_RELATION_EVIDENCE,
        PEPTIDE_ANTIBIOTIC_EVIDENCE,
        *source_evidence,
    )
    domain_evidence = (
        record_evidence,
        *family_evidence,
        DOMAIN_EVIDENCE,
        GO_PETN_TRANSFER_EVIDENCE,
        *source_evidence,
    )
    fold_evidence = (
        record_evidence,
        *family_evidence,
        FOLD_EVIDENCE,
        GO_PETN_TRANSFER_EVIDENCE,
        *source_evidence,
    )
    transfer_evidence = (
        record_evidence,
        *family_evidence,
        PETN_TRANSFERASE_EVIDENCE,
        GO_PETN_TRANSFER_EVIDENCE,
        *source_evidence,
    )
    charge_evidence = (
        record_evidence,
        *family_evidence,
        PETN_TRANSFERASE_EVIDENCE,
        CHARGE_ALTERATION_EVIDENCE,
        GO_PETN_TRANSFER_EVIDENCE,
        *source_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            mechanism_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            mechanism_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            charge_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to",
            "ARO:2000001",
            "drug0",
            drug_evidence,
        ),
        _edge(
            "domain",
            "part of",
            "BFO:0000050",
            "determinant",
            domain_evidence,
        ),
        _edge(
            "determinant",
            "member of",
            "RO:0002350",
            "fold",
            fold_evidence,
        ),
        _edge(
            "domain",
            "enables (lipid A phosphoethanolamine transfer)",
            "RO:0002327",
            "petn_transfer",
            transfer_evidence,
        ),
        _edge(
            "determinant",
            "enables (adds phosphoethanolamine)",
            "RO:0002327",
            "petn_transfer",
            transfer_evidence,
        ),
        _edge(
            "petn_transfer",
            "causally upstream of (charge alteration)",
            "RO:0002411",
            "mech0",
            charge_evidence,
        ),
    ]


def _validate_record(record: dict[str, Any]) -> None:
    identifier = record.get("identifier")
    if identifier != MCR_PARENT_IDENTIFIER and MCR_PARENT_IDENTIFIER not in (
        record.get("parent_traits") or []
    ):
        raise ValueError(f"not an MCR phosphoethanolamine-transferase target: {identifier}")
    if not record.get("label"):
        raise ValueError(f"{identifier}: missing label")
    if not record.get("definition"):
        raise ValueError(f"{identifier}: missing definition")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{identifier}: expected exactly one resistance graph")


def _validate_graph(graph: dict[str, Any]) -> None:
    nodes = {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }
    expected_nodes = {
        "determinant",
        "mech0",
        "drug0",
        "domain",
        "fold",
        "petn_transfer",
        "resistance",
    }
    missing_nodes = sorted(expected_nodes - set(nodes))
    if missing_nodes:
        raise ValueError(f"generated graph missing node(s): {', '.join(missing_nodes)}")

    seen: set[tuple[str, str, str]] = set()
    found_edges: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"generated graph has unexpected edge {key}")
        if key in seen:
            raise ValueError(f"generated graph has duplicate edge {key}")
        seen.add(key)
        found_edges.add(key)

    missing_edges = sorted(EXPECTED_EDGE_KEYS - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"generated graph missing edge(s): {missing}")


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    _validate_record(record)

    out = copy.deepcopy(record)
    graph = out["causal_graphs"][0]
    before = copy.deepcopy(graph)
    graph["title"] = f"{record['label']} → lipid A phosphoethanolamine transfer → resistance"
    graph["description"] = (
        "Curated MCR resistance graph. MCR phosphoethanolamine transferases modify lipid A, "
        "reduce the negative cell-surface charge required for cationic polymyxin binding, "
        "and thereby confer peptide-antibiotic resistance."
    )
    graph["nodes"] = _canonical_nodes(out)
    graph["edges"] = _canonical_edges(out)
    _validate_graph(graph)
    return out, graph != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    _validate_record(record)

    enriched, changed = enrich_record(record)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
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
    return sorted(
        candidate
        for candidate in path.glob("mcr*.yaml")
        if candidate.is_file() and not candidate.is_symlink()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory, MCR parent YAML file, or one MCR variant YAML file",
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
