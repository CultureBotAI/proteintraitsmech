#!/usr/bin/env python3
"""Ground and complete DdlA cycloserine-resistance ARO graphs.

The DdlA records model cycloserine resistance through D-Ala-D-Ala ligase, the
D-alanine substrate that cycloserine resembles, and peptidoglycan biosynthesis.
This updater grounds those nodes to GO/ChEBI, adds the missing ligase-to-cell-
wall edge, describes every edge, and adds exact DdlA, mutation-mechanism, and
ontology evidence.

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
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Grounded DdlA ligase, D-alanine, and peptidoglycan-biosynthesis nodes; "
        "linked D-Ala-D-Ala ligase activity to peptidoglycan biosynthesis; and "
        "added exact DdlA, mutation-mechanism, GO, and ChEBI evidence"
    ),
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3004939"

DDL_PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": (
        "ddlA catalyzes the ATP-driven ligation of two D-alanine molecules to form "
        "the D-alanyl-D-alanine dipeptide, key in forming the cell wall. "
        "Cycloserine has a similar structure to d-alanine and inhibits the growth "
        "of the cell wall."
    ),
    "notes": "CARD definition for the cycloserine-resistant ddlA parent term.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance. Examples included modified antibiotic "
        "targets with lower binding affinities and the deactivation of repressors "
        "that result in increased expression of genes that inactivate or pump out "
        "antibiotics."
    ),
    "notes": "CARD definition for the broad mutation-conferring resistance mechanism.",
}

DDL_ACTIVITY_EVIDENCE = {
    "reference": "GO:0008716",
    "snippet": (
        "Catalysis of the reaction: 2 D-alanine + ATP = D-alanyl-D-alanine + ADP "
        "+ 2 H+ + phosphate."
    ),
    "notes": "GO definition for D-alanine-D-alanine ligase activity.",
}

D_ALANINE_EVIDENCE = {
    "reference": "CHEBI:15570",
    "snippet": "The D-enantiomer of alanine.",
    "notes": "ChEBI definition for D-alanine.",
}

PEPTIDOGLYCAN_BIOSYNTHESIS_EVIDENCE = {
    "reference": "GO:0009252",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "peptidoglycans, any of a class of glycoconjugates found in bacterial cell "
        "walls and consisting of long glycan strands of alternating residues of "
        "beta-(1,4) linked N-acetylglucosamine and N-acetylmuramic acid, "
        "cross-linked by short peptides."
    ),
    "notes": "GO definition for the peptidoglycan biosynthetic process.",
}

SHARED_NODE_UPDATES = {
    "ligation": {
        "node_id": "ligation",
        "label": "D-Ala-D-Ala ligase activity",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "GO:0008716",
        "description": (
            "Grounded to GO D-alanine-D-alanine ligase activity, matching CARD's "
            "ATP-driven ligation of two D-alanine molecules by DdlA."
        ),
    },
    "dala": {
        "node_id": "dala",
        "label": "D-alanine",
        "node_type": "CHEMICAL",
        "grounding": "CHEBI:15570",
        "description": "ChEBI-grounded D-alanine, the substrate that cycloserine resembles.",
    },
    "wall_growth": {
        "node_id": "wall_growth",
        "label": "peptidoglycan biosynthetic process",
        "node_type": "BIOLOGICAL_PROCESS",
        "grounding": "GO:0009252",
        "description": (
            "Grounded to peptidoglycan biosynthesis, the bacterial cell-wall "
            "formation process that depends on DdlA-produced D-Ala-D-Ala."
        ),
    },
}

LIGATION_WALL_EDGE = {
    "subject": "ligation",
    "predicate": "part of (peptidoglycan biosynthesis)",
    "predicate_id": "BFO:0000050",
    "object": "wall_growth",
}

EXPECTED_EDGES = {
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "drug0"),
    ("determinant", "ligation"),
    ("ligation", "dala"),
    ("drug0", "dala"),
    ("drug0", "wall_growth"),
    ("ligation", "wall_growth"),
}
LEGACY_EDGES = EXPECTED_EDGES - {("ligation", "wall_growth")}
EDGE_ORDER = (
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "drug0"),
    ("determinant", "ligation"),
    ("ligation", "dala"),
    ("drug0", "dala"),
    ("drug0", "wall_growth"),
    ("ligation", "wall_growth"),
)


@dataclass(frozen=True)
class EdgeUpdate:
    predicate: str
    predicate_id: str
    description: str
    evidence: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    snippet: str
    notes: str

    @property
    def evidence(self) -> dict[str, str]:
        return {
            "reference": self.identifier,
            "snippet": self.snippet,
            "notes": self.notes,
        }

    @property
    def ddl_evidence(self) -> tuple[dict[str, str], ...]:
        if self.identifier == PARENT_IDENTIFIER:
            return (self.evidence,)
        return (self.evidence, DDL_PARENT_EVIDENCE)

    @property
    def edge_updates(self) -> dict[tuple[str, str], EdgeUpdate]:
        ddl_evidence = self.ddl_evidence
        mutation = (*ddl_evidence, MUTATION_EVIDENCE)
        ddl_activity = (*ddl_evidence, DDL_ACTIVITY_EVIDENCE)
        wall_process = (*ddl_evidence, PEPTIDOGLYCAN_BIOSYNTHESIS_EVIDENCE)
        return {
            ("determinant", "mech0"): EdgeUpdate(
                predicate="participates in (resistance mechanism)",
                predicate_id="RO:0000056",
                description=(
                    "CARD classifies cycloserine-resistant ddlA variants under "
                    "mutation conferring antibiotic resistance."
                ),
                evidence=mutation,
            ),
            ("mech0", "resistance"): EdgeUpdate(
                predicate="causally upstream of",
                predicate_id="RO:0002411",
                description=(
                    "The broad mutation mechanism covers altered DdlA variants "
                    "associated with cycloserine resistance."
                ),
                evidence=mutation,
            ),
            ("determinant", "resistance"): EdgeUpdate(
                predicate="causally upstream of (confers resistance)",
                predicate_id="RO:0002411",
                description=(
                    "Resistant ddlA variants retain D-Ala-D-Ala ligase function in "
                    "the cycloserine-targeted cell-wall pathway."
                ),
                evidence=mutation,
            ),
            ("determinant", "drug0"): EdgeUpdate(
                predicate="confers resistance to",
                predicate_id="ARO:2000001",
                description=(
                    "CARD maps resistant ddlA variants to the cycloserine-like "
                    "antibiotic class."
                ),
                evidence=mutation,
            ),
            ("determinant", "ligation"): EdgeUpdate(
                predicate="enables",
                predicate_id="RO:0002327",
                description=(
                    "DdlA catalyzes ATP-driven ligation of two D-alanine molecules "
                    "to form D-Ala-D-Ala."
                ),
                evidence=ddl_activity,
            ),
            ("ligation", "dala"): EdgeUpdate(
                predicate="has input",
                predicate_id="RO:0002233",
                description=(
                    "D-alanine is the substrate used by D-Ala-D-Ala ligase activity."
                ),
                evidence=(DDL_ACTIVITY_EVIDENCE, D_ALANINE_EVIDENCE),
            ),
            ("drug0", "dala"): EdgeUpdate(
                predicate="molecularly similar to",
                predicate_id="RO:0002158",
                description=(
                    "The modeled drug class is related to D-alanine by "
                    "cycloserine's structural similarity to that substrate."
                ),
                evidence=(*ddl_evidence, D_ALANINE_EVIDENCE),
            ),
            ("drug0", "wall_growth"): EdgeUpdate(
                predicate="negatively regulates",
                predicate_id="RO:0002212",
                description=(
                    "Cycloserine-like antibiotics inhibit peptidoglycan "
                    "biosynthesis in the bacterial cell-wall pathway."
                ),
                evidence=wall_process,
            ),
            ("ligation", "wall_growth"): EdgeUpdate(
                predicate="part of (peptidoglycan biosynthesis)",
                predicate_id="BFO:0000050",
                description=(
                    "D-Ala-D-Ala ligase activity contributes to peptidoglycan "
                    "biosynthesis by producing the D-Ala-D-Ala dipeptide."
                ),
                evidence=(*ddl_activity, PEPTIDOGLYCAN_BIOSYNTHESIS_EVIDENCE),
            ),
        }


TARGETS = {
    "ARO:3004939": Target(
        identifier="ARO:3004939",
        filename="cycloserine-resistant-ddla-aro3004939.yaml",
        snippet=DDL_PARENT_EVIDENCE["snippet"],
        notes=DDL_PARENT_EVIDENCE["notes"],
    ),
    "ARO:3004941": Target(
        identifier="ARO:3004941",
        filename=(
            "mycobacterium-tuberculosis-ddla-mutations-confer-resistance-to-"
            "cycloserine-aro3004941.yaml"
        ),
        snippet=(
            "Point mutations that occur within Mycobacterium tuberculosis ddlA "
            "gene resulting in resistance to cycloserine."
        ),
        notes="CARD definition for the Mycobacterium tuberculosis ddlA mutant term.",
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str]:
    return edge.get("subject", ""), edge.get("object", "")


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


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    nodes = graph.get("nodes") or []
    found: set[str] = set()
    for index, node in enumerate(nodes):
        node_id = node.get("node_id")
        if node_id not in SHARED_NODE_UPDATES:
            continue
        nodes[index] = copy.deepcopy(SHARED_NODE_UPDATES[node_id])
        found.add(node_id)

    missing = sorted(set(SHARED_NODE_UPDATES) - found)
    if missing:
        missing_ids = ", ".join(missing)
        msg = f"{target.identifier}: missing node(s): {missing_ids}"
        raise ValueError(msg)


def _canonical_edges(target: Target) -> list[dict[str, Any]]:
    by_key = target.edge_updates
    return [
        _ordered_edge(
            {
                "subject": subject,
                "predicate": by_key[(subject, object_)].predicate,
                "predicate_id": by_key[(subject, object_)].predicate_id,
                "object": object_,
                "description": by_key[(subject, object_)].description,
                "evidence": [
                    copy.deepcopy(item) for item in by_key[(subject, object_)].evidence
                ],
            }
        )
        for subject, object_ in EDGE_ORDER
    ]


def _validate_and_complete_edges(graph: dict[str, Any], target: Target) -> None:
    edges = graph.setdefault("edges", [])
    if not any(_edge_key(edge) == ("ligation", "wall_growth") for edge in edges):
        edges.append(copy.deepcopy(LIGATION_WALL_EDGE))

    seen: set[tuple[str, str]] = set()
    for edge in edges:
        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        if key not in EXPECTED_EDGES:
            msg = f"{target.identifier}: unexpected edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        seen.add(key)

    if seen != EXPECTED_EDGES:
        missing_edges = sorted(EXPECTED_EDGES - seen)
        missing = ", ".join(f"{subject} -> {object_}" for subject, object_ in missing_edges)
        msg = f"{target.identifier}: missing edge(s): {missing}"
        raise ValueError(msg)


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        msg = f"expected {target.identifier}, found {record.get('identifier')}"
        raise ValueError(msg)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        msg = f"{target.identifier}: missing resistance causal graph"
        raise ValueError(msg)

    _enrich_nodes(graph, target)
    _validate_and_complete_edges(graph, target)
    graph["description"] = (
        "Curated resistance-causation graph for DdlA-mediated cycloserine "
        "resistance. The graph grounds D-Ala-D-Ala ligase, D-alanine, and "
        "peptidoglycan-biosynthesis nodes and connects DdlA ligase activity to "
        "bacterial cell-wall biosynthesis."
    )
    graph["edges"] = _canonical_edges(target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a DdlA cycloserine target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
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
        help="ARO directory or one of the two target YAML files",
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
