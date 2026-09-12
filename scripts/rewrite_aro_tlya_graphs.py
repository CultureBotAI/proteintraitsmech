#!/usr/bin/env python3
"""Ground tlyA ribosomal-alteration resistance graphs.

The ARO tlyA branch contains an antibiotic-resistant parent and two
Mycobacterium tuberculosis mutation children. The records name TlyA's 2'-O
methylation sites in 16S and 23S rRNA, but the current graphs use a generic
acquired-aminoglycoside-resistance methyltransferase subgraph. This updater
rewrites the exact three-record branch to the grounded ARO mechanism routes,
the aminoglycoside drug-class edge, and two exact Rhea tlyA methylation leaves.

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import re
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
HISTORY_ACTION = "Grounded tlyA ribosomal-alteration resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TLYA_PARENT_EVIDENCE = {
    "reference": "ARO:3003443",
    "snippet": (
        "tlyA encodes for hemolysin. It Catalyzes the 2'-O-methylation at "
        "nucleotides C1409 in 16S rRNA and C1920 in 23S rRNA. Mutation that "
        "arise within this gene reduces the binding affinity of aminoglycosides "
        "to rRNA."
    ),
    "notes": "CARD definition for the antibiotic-resistant tlyA parent.",
}

MECHANISM_EVIDENCE = {
    "target_alteration": {
        "reference": "ARO:0001001",
        "snippet": (
            "Mutational alteration or enzymatic modification of antibiotic target "
            "which results in antibiotic resistance."
        ),
        "notes": "CARD definition for antibiotic target alteration.",
    },
    "ribosomal_alteration": {
        "reference": "ARO:3000211",
        "snippet": (
            "Chemical alteration of the ribosome results in modification of an "
            "antibiotic's target leading to resistance."
        ),
        "notes": "CARD definition for ribosomal alteration conferring antibiotic resistance.",
    },
    "mutation": {
        "reference": "ARO:3000212",
        "snippet": (
            "Point mutations in the DNA may lead to an altered gene product that "
            "may result in antibiotic resistance. Examples included modified "
            "antibiotic targets with lower binding affinities and the deactivation "
            "of repressors that result in increased expression of genes that "
            "inactivate or pump out antibiotics."
        ),
        "notes": "CARD definition for mutation conferring antibiotic resistance.",
    },
}

RHEA_16S_C1409_EVIDENCE = {
    "reference": "RHEA:43204",
    "snippet": (
        "cytidine(1409) in 16S rRNA + S-adenosyl-L-methionine = "
        "2'-O-methylcytidine(1409) in 16S rRNA + "
        "S-adenosyl-L-homocysteine + H(+)"
    ),
    "notes": "Rhea reaction for TlyA-catalyzed 16S rRNA C1409 2'-O-methylation.",
}

RHEA_23S_C1920_EVIDENCE = {
    "reference": "RHEA:43200",
    "snippet": (
        "cytidine(1920) in 23S rRNA + S-adenosyl-L-methionine = "
        "2'-O-methylcytidine(1920) in 23S rRNA + "
        "S-adenosyl-L-homocysteine + H(+)"
    ),
    "notes": "Rhea reaction for TlyA-catalyzed 23S rRNA C1920 2'-O-methylation.",
}

MECHANISM_NODES = [
    (
        "mech0",
        "target_alteration",
        {
            "node_id": "mech0",
            "label": "antibiotic target alteration",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:0001001",
        },
    ),
    (
        "mech1",
        "ribosomal_alteration",
        {
            "node_id": "mech1",
            "label": "ribosomal alteration conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000211",
        },
    ),
    (
        "mech2",
        "mutation",
        {
            "node_id": "mech2",
            "label": "mutation conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000212",
        },
    ),
]

DRUG_NODE = {
    "node_id": "drug0",
    "label": "aminoglycoside antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:0000016",
}

C1409_METHYLATION_NODE = {
    "node_id": "c1409_2o_methylation",
    "label": "TlyA 16S rRNA C1409 2'-O-methylation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "RHEA:43204",
}

C1920_METHYLATION_NODE = {
    "node_id": "c1920_2o_methylation",
    "label": "TlyA 23S rRNA C1920 2'-O-methylation",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "RHEA:43200",
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

DRUG_RELATION_REFERENCE = "ARO:3003443"
DRUG_RELATION_OBJECT = "ARO:0000016"
DRUG_RELATION_LABEL = "aminoglycoside antibiotic"

LEGACY_METHYLATION_EDGE_KEYS = {
    ("determinant", "RO:0002327", "methyltransferase"),
    ("methyltransferase", "RO:0002411", "methylated"),
    ("methylated", "RO:0002212", "decoding_site"),
    ("drug0", "RO:0002436", "decoding_site"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    graph_title: str
    graph_description: str


TARGETS = {
    "ARO:3003443": Target(
        identifier="ARO:3003443",
        filename="antibiotic-resistant-tlya-aro3003443.yaml",
        graph_title="Antibiotic resistant tlyA → ribosomal alteration → resistance",
        graph_description=(
            "Conservative graph for the antibiotic-resistant tlyA parent. The "
            "graph keeps the ARO target-alteration, ribosomal-alteration, "
            "mutation, and aminoglycoside drug-class routes and grounds the two "
            "2'-O-methylation reactions named by ARO without asserting the "
            "former generic decoding-site methylation chain."
        ),
    ),
    "ARO:3003445": Target(
        identifier="ARO:3003445",
        filename=(
            "mycobacterium-tuberculosis-tlya-mutations-conferring-resistance-to-"
            "aminoglycosid-aro3003445.yaml"
        ),
        graph_title=(
            "Mycobacterium tuberculosis tlyA aminoglycoside mutations → "
            "ribosomal alteration → resistance"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis tlyA mutations "
            "conferring aminoglycoside resistance. The graph keeps the inherited "
            "ARO mechanism and drug-class routes and grounds the two "
            "tlyA-family 2'-O-methylation reactions without adding an unsupported "
            "direct binding-site edge."
        ),
    ),
    "ARO:3007805": Target(
        identifier="ARO:3007805",
        filename=(
            "mycobacterium-tuberculosis-tlya-mutations-conferring-resistance-to-"
            "capreomycin-aro3007805.yaml"
        ),
        graph_title=(
            "Mycobacterium tuberculosis tlyA capreomycin mutations → "
            "ribosomal alteration → resistance"
        ),
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis tlyA mutations "
            "conferring capreomycin resistance. The graph keeps the inherited "
            "ARO mechanism and drug-class routes and grounds the two "
            "tlyA-family 2'-O-methylation reactions without adding an unsupported "
            "direct binding-site edge."
        ),
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _tlya_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    if record["identifier"] == TLYA_PARENT_EVIDENCE["reference"]:
        return (_target_evidence(record),)
    return (_target_evidence(record), TLYA_PARENT_EVIDENCE)


def _mechanism_evidence(
    record: dict[str, Any],
    mechanism_key: str,
) -> tuple[dict[str, str], ...]:
    return _tlya_evidence(record) + (MECHANISM_EVIDENCE[mechanism_key],)


def _drug_evidence() -> dict[str, str]:
    return {
        "reference": DRUG_RELATION_REFERENCE,
        "snippet": f"confers_resistance_to_drug_class {DRUG_RELATION_OBJECT} ! {DRUG_RELATION_LABEL}",
        "notes": (
            "ARO drug-class relationship on ARO:3003443; modeled here as a "
            "determinant-to-aminoglycoside-antibiotic edge and inherited by "
            "the Mycobacterium tuberculosis tlyA children."
        ),
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in evidence:
        key = (
            item["reference"],
            item["snippet"],
            item.get("notes", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(copy.deepcopy(item))
    return unique


def _ordered_edge(edge: dict[str, Any]) -> dict[str, Any]:
    ordered = {
        "subject": edge["subject"],
        "predicate": edge["predicate"],
        "predicate_id": edge["predicate_id"],
        "object": edge["object"],
        "description": edge["description"],
        "evidence": edge["evidence"],
    }
    for key, value in edge.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return _ordered_edge(
        {
            "subject": subject,
            "predicate": predicate,
            "predicate_id": predicate_id,
            "object": object_,
            "description": description,
            "evidence": _unique_evidence(evidence),
        }
    )


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and "node_id" in node
    }


def _canonical_edge_keys() -> set[tuple[str, str, str]]:
    keys = {
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
        ("determinant", "RO:0002327", "c1409_2o_methylation"),
        ("determinant", "RO:0002327", "c1920_2o_methylation"),
    }
    for node_id, _, _ in MECHANISM_NODES:
        keys.add(("determinant", "RO:0000056", node_id))
        keys.add((node_id, "RO:0002411", "resistance"))
    return keys


def _input_allowed_edges() -> set[tuple[str, str, str]]:
    return _canonical_edge_keys() | LEGACY_METHYLATION_EDGE_KEYS


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "mech1", "mech2", "drug0", "resistance"}
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    required_edges = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "mech1"),
        ("mech1", "RO:0002411", "resistance"),
        ("determinant", "RO:0000056", "mech2"),
        ("mech2", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
    }

    found = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges():
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(required_edges - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        *(copy.deepcopy(node) for _, _, node in MECHANISM_NODES),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(C1409_METHYLATION_NODE),
        copy.deepcopy(C1920_METHYLATION_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(record: dict[str, Any]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for node_id, mechanism_key, node in MECHANISM_NODES:
        edges.extend(
            [
                _edge(
                    "determinant",
                    "participates in (resistance mechanism)",
                    "RO:0000056",
                    node_id,
                    f"The ARO hierarchy classifies tlyA determinants under {node['label']}.",
                    _mechanism_evidence(record, mechanism_key),
                ),
                _edge(
                    node_id,
                    "causally upstream of",
                    "RO:0002411",
                    "resistance",
                    f"The inherited {node['label']} mechanism links tlyA to resistance.",
                    _mechanism_evidence(record, mechanism_key),
                ),
            ]
        )

    drug_evidence = _tlya_evidence(record) + (_drug_evidence(), MECHANISM_EVIDENCE["mutation"])
    edges.extend(
        [
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The ARO hierarchy links tlyA mutations to aminoglycoside resistance.",
                drug_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                "The ARO hierarchy links this tlyA determinant to aminoglycoside antibiotics.",
                drug_evidence,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "c1409_2o_methylation",
                "ARO identifies TlyA as catalyzing C1409 2'-O-methylation in 16S rRNA.",
                _tlya_evidence(record) + (RHEA_16S_C1409_EVIDENCE,),
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "c1920_2o_methylation",
                "ARO identifies TlyA as catalyzing C1920 2'-O-methylation in 23S rRNA.",
                _tlya_evidence(record) + (RHEA_23S_C1920_EVIDENCE,),
            ),
        ]
    )
    return edges


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next(
        (item for item in graphs if item.get("graph_id") in {"resistance", "resistance-draft"}),
        None,
    )
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    graph["graph_id"] = "resistance"
    graph["title"] = target.graph_title
    graph["description"] = target.graph_description
    graph["nodes"] = _canonical_nodes(graph)
    graph["edges"] = _canonical_edges(out)
    return out, out.get("causal_graphs") != before


def _promote_to_reviewed(text: str) -> str:
    return re.sub(r"^mapping_status:\s*SEEDED\s*$", "mapping_status: REVIEWED", text, count=1, flags=re.M)


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a tlyA target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases and record.get("mapping_status") == "REVIEWED":
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    out = _promote_to_reviewed(out)
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
    return out, True


def iter_target_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path} is neither a file nor a directory")
    return [path / target.filename for target in TARGETS.values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the three target YAML files",
    )
    args = parser.parse_args()

    changed = unchanged = 0
    problems: list[str] = []
    for path in iter_target_paths(args.path):
        if not path.exists():
            problems.append(f"{path}: missing")
            continue
        try:
            text = path.read_text(encoding="utf-8")
            out, did_change = enrich_text(text, path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            problems.append(str(exc))
            continue
        if not did_change:
            unchanged += 1
            continue
        changed += 1
        print(f"  {'wrote' if args.apply else 'would write'} {path.name}")
        if args.apply:
            path.write_text(out, encoding="utf-8")

    print(f"{'changed' if args.apply else 'would change'}: {changed}")
    print(f"already enriched: {unchanged}")
    for problem in problems:
        print(f"PROBLEM: {problem}", file=sys.stderr)
    if not args.apply:
        print("dry run -- pass --apply to write")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
