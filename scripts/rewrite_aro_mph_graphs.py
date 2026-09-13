#!/usr/bin/env python3
"""Ground and evidence macrolide phosphotransferase graphs.

The MPH graphs already include the grounded ARO node for phosphorylation of an
antibiotic. The previous drafts also carried an ungrounded duplicate kinase
node plus a non-causal binding-pocket side branch. This updater keeps the
phosphorylated-macrolide inactivation route, routes the output through the
grounded phosphorylation mechanism, and models the inactive phosphorylated
macrolide as a described local state because the exact product differs by drug.

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

HISTORY_ACTION = "Grounded macrolide phosphotransferase graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3000333"
PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "Macrolide phosphotransferases (MPH) are enzymes encoded by macrolide "
        "phosphotransferase genes (mph genes). These enzymes phosphorylate "
        "macrolides in GTP dependent manner at 2'-OH of desosamine sugar "
        "thereby inactivating them. Characterized MPH's are differentiated "
        "based on their substrate specificity."
    ),
    "notes": "CARD definition for the macrolide phosphotransferase parent.",
}

INACTIVATION_EVIDENCE = {
    "reference": "ARO:0001004",
    "snippet": "Enzymatic inactivation of antibiotic to confer drug resistance.",
    "notes": "CARD definition for antibiotic inactivation.",
}

PHOSPHORYLATION_EVIDENCE = {
    "reference": "ARO:3000105",
    "snippet": "Phosphorylation of antibiotic usually by ATP, sometimes GTP.",
    "notes": "CARD definition for phosphorylation of antibiotic conferring resistance.",
}

FONG_INACTIVATION_EVIDENCE = {
    "reference": "PMID:28416110",
    "snippet": (
        "The macrolides are a class of antibiotic, characterized by a large "
        "macrocyclic lactone ring that can be inactivated by macrolide "
        "phosphotransferase enzymes."
    ),
    "notes": "Fong et al. 2017; MPH enzymes inactivate macrolides.",
}

MACROLIDE_EVIDENCE = {
    "reference": "ARO:0000000",
    "snippet": "macrolide antibiotic",
    "notes": "ARO drug-class term inherited by MPH records.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic inactivation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0001004",
}

PHOSPHORYLATION_NODE = {
    "node_id": "mech1",
    "label": "phosphorylation of antibiotic conferring resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000105",
}

MACROLIDE_NODE = {
    "node_id": "drug0",
    "label": "macrolide antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000000",
}

PHOSPHO_MACROLIDE_NODE = {
    "node_id": "phospho_drug",
    "label": "phosphorylated inactive macrolide",
    "node_type": "STATE",
    "description": (
        "Local state for the phosphorylated, inactive macrolide produced by "
        "MPH enzymes; the exact chemical product differs by macrolide."
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

EXPECTED_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("mech1", "RO:0002234", "phospho_drug"),
    ("phospho_drug", "RO:0002212", "drug0"),
}

REMOVED_EDGE_KEYS = {
    ("determinant", "RO:0002327", "kinase"),
    ("pocket", "BFO:0000050", "determinant"),
    ("kinase", "RO:0002234", "phospho_drug"),
}

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies MPH determinants under antibiotic inactivation."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "Antibiotic inactivation is the broad resistance mechanism for MPH "
        "macrolide phosphorylation."
    ),
    ("determinant", "RO:0000056", "mech1"): (
        "ARO classifies MPH determinants under phosphorylation of antibiotic "
        "conferring resistance."
    ),
    ("mech1", "RO:0002411", "resistance"): (
        "MPH enzymes phosphorylate macrolides and thereby inactivate them."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "MPH determinants confer macrolide resistance by GTP-dependent "
        "phosphorylation and inactivation of macrolides."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps macrolide phosphotransferases to macrolide antibiotics."
    ),
    ("mech1", "RO:0002234", "phospho_drug"): (
        "MPH antibiotic phosphorylation produces a phosphorylated macrolide."
    ),
    ("phospho_drug", "RO:0002212", "drug0"): (
        "The phosphorylated macrolide state represents enzymatic drug "
        "inactivation by MPH proteins."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str

    @property
    def is_parent(self) -> bool:
        return self.identifier == PARENT_IDENTIFIER


TARGETS = {
    PARENT_IDENTIFIER: Target(
        identifier=PARENT_IDENTIFIER,
        filename="macrolide-phosphotransferase-mph-aro3000333.yaml",
    ),
    "ARO:3000316": Target(identifier="ARO:3000316", filename="mpha-aro3000316.yaml"),
    "ARO:3000318": Target(identifier="ARO:3000318", filename="mphb-aro3000318.yaml"),
    "ARO:3000319": Target(identifier="ARO:3000319", filename="mphc-aro3000319.yaml"),
    "ARO:3003741": Target(identifier="ARO:3003741", filename="mphe-aro3003741.yaml"),
    "ARO:3003071": Target(identifier="ARO:3003071", filename="mphf-aro3003071.yaml"),
    "ARO:3003742": Target(identifier="ARO:3003742", filename="mphg-aro3003742.yaml"),
    "ARO:3004539": Target(identifier="ARO:3004539", filename="mphh-aro3004539.yaml"),
    "ARO:3003991": Target(identifier="ARO:3003991", filename="mphi-aro3003991.yaml"),
    "ARO:3004544": Target(identifier="ARO:3004544", filename="mphj-aro3004544.yaml"),
    "ARO:3004541": Target(identifier="ARO:3004541", filename="mphk-aro3004541.yaml"),
    "ARO:3003072": Target(identifier="ARO:3003072", filename="mphl-aro3003072.yaml"),
    "ARO:3003767": Target(identifier="ARO:3003767", filename="mphm-aro3003767.yaml"),
    "ARO:3004542": Target(identifier="ARO:3004542", filename="mphn-aro3004542.yaml"),
    "ARO:3004543": Target(identifier="ARO:3004543", filename="mpho-aro3004543.yaml"),
    "ARO:3003839": Target(identifier="ARO:3003839", filename="mrx-aro3003839.yaml"),
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


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "reference": str(item["reference"]),
            "notes": str(item.get("notes") or "ARO citation for this record."),
        }
        for item in _dicts(record.get("evidence"))
        if item.get("reference")
    )


def _own_definition_evidence(record: dict[str, Any], target: Target) -> dict[str, str]:
    if target.is_parent:
        return PARENT_EVIDENCE
    return {
        "reference": target.identifier,
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


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


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    if target.is_parent:
        notes = "ARO drug-class relationship asserted directly on the MPH parent."
    else:
        notes = (
            "ARO drug-class relationship asserted on ARO:3000333 and inherited "
            f"by {target.identifier}."
        )
    return {
        "reference": PARENT_IDENTIFIER,
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:0000000 ! "
            "macrolide antibiotic"
        ),
        "notes": notes,
    }


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


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {"determinant", "mech0", "mech1", "drug0", "phospho_drug"} - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    all_edges = {_edge_key(edge) for edge in _dicts(graph.get("edges"))}
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key in REMOVED_EDGE_KEYS:
            continue
        if key not in EXPECTED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    if ("kinase", "RO:0002234", "phospho_drug") in all_edges:
        required_edges = EXPECTED_EDGE_KEYS - {("mech1", "RO:0002234", "phospho_drug")}
    else:
        required_edges = EXPECTED_EDGE_KEYS

    missing_edges = sorted(required_edges - found_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    own_evidence = _own_definition_evidence(record, target)
    source_evidence = _source_evidence(record)
    inactivation_evidence = (
        own_evidence,
        PARENT_EVIDENCE,
        INACTIVATION_EVIDENCE,
        FONG_INACTIVATION_EVIDENCE,
        *source_evidence,
    )
    phosphorylation_evidence = (
        own_evidence,
        PARENT_EVIDENCE,
        PHOSPHORYLATION_EVIDENCE,
        FONG_INACTIVATION_EVIDENCE,
        *source_evidence,
    )
    resistance_evidence = (
        own_evidence,
        PARENT_EVIDENCE,
        FONG_INACTIVATION_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        _drug_relation_evidence(target),
        MACROLIDE_EVIDENCE,
        PARENT_EVIDENCE,
        *source_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → macrolide phosphorylation → drug inactivation",
        "description": (
            "Conservative graph for MPH-mediated macrolide resistance. The "
            "graph routes macrolide inactivation through the grounded ARO "
            "phosphorylation mechanism and represents the phosphorylated, "
            "inactive macrolide as a local state because the exact product "
            "depends on the macrolide substrate."
        ),
        "nodes": [
            copy.deepcopy(nodes["determinant"]),
            copy.deepcopy(MECHANISM_NODE),
            copy.deepcopy(PHOSPHORYLATION_NODE),
            copy.deepcopy(MACROLIDE_NODE),
            copy.deepcopy(PHOSPHO_MACROLIDE_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                inactivation_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                inactivation_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                phosphorylation_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                phosphorylation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                resistance_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                drug_evidence,
            ),
            _edge(
                "mech1",
                "has output",
                "RO:0002234",
                "phospho_drug",
                phosphorylation_evidence,
            ),
            _edge(
                "phospho_drug",
                "negatively regulates",
                "RO:0002212",
                "drug0",
                resistance_evidence,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_canonical_graph(record, target)]
    return out, out != record


def enrich_text(text: str, path: Path, target: Target) -> tuple[str, bool]:
    if path.name != target.filename:
        raise ValueError(f"{target.identifier}: not the expected path: {path}")

    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))

    history = list(_dicts(enriched.get("curation_history")))
    if not any(item.get("action") == HISTORY_ACTION for item in history):
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
        changed = True

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--path", type=Path, default=ARO_DIR)
    args = parser.parse_args(argv)

    changed_count = 0
    for target in TARGETS.values():
        path = args.path / target.filename
        before = path.read_text(encoding="utf-8")
        after, changed = enrich_text(before, path, target)
        if not changed:
            continue
        changed_count += 1
        if args.apply:
            path.write_text(after, encoding="utf-8")
            print(f"  wrote {target.filename}")
        else:
            print(f"  would write {target.filename}")

    print(f"{'changed' if args.apply else 'would change'}: {changed_count}")
    if not changed_count:
        print(f"already enriched: {len(TARGETS)}")
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
