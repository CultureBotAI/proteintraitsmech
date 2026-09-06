#!/usr/bin/env python3
"""Ground and complete MprF electrostatic-repulsion graphs.

MprF lysinylates phosphatidylglycerol to produce cationic lysyl-PG, lowering
the membrane's net negative charge and repelling cationic peptide antibiotics.
The existing graphs captured that topology but left lysyl-PG and the membrane
charge state ungrounded. This updater adds a grounded GO activity node, grounds
the lysyl-PG product to ChEBI, keeps the reduced-charge state explicitly local,
and adds exact CARD, Rhea/GO/ChEBI, and literature evidence to each edge.

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
        "Grounded MprF electrostatic-repulsion graphs with GO "
        "phosphatidylglycerol lysyltransferase and ChEBI lysyl-PG terms and "
        "added exact CARD, Rhea/GO/ChEBI, and literature evidence"
    ),
    "llm_assisted": True,
}


MPRF_PARENT_EVIDENCE = {
    "reference": "ARO:3003421",
    "snippet": (
        "Catalyzes the transfer of a lysyl group from L-lysyl-tRNA(Lys) to "
        "membrane-bound phosphatidylglycerol (PG), which produces "
        "lysylphosphatidylglycerol (LPG), a major component of the bacterial "
        "membrane with a positive net charge. LPG synthesis contributes to "
        "bacterial virulence as it is involved in the resistance mechanism "
        "against cationic antimicrobial peptides (CAMP) produces by the host's "
        "immune system (defensins, cathelicidins) and by the competing "
        "microorganisms (bacteriocins)."
    ),
    "notes": "CARD definition for the antibiotic-resistant mprF parent term.",
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

PESCHEL_RESISTANCE_EVIDENCE = {
    "reference": "PMID:11342591",
    "snippet": (
        "We describe a novel staphylococcal gene, mprF, which determines "
        "resistance to several host defense peptides such as defensins and "
        "protegrins."
    ),
    "notes": (
        "Peschel et al. 2001 identified the gene by the resistance it confers "
        "to defensins and protegrins."
    ),
}

PESCHEL_MUTANT_EVIDENCE = {
    "reference": "PMID:11342591",
    "snippet": (
        "Analysis of membrane lipids demonstrated that the mprF mutant no longer "
        "modifies phosphatidylglycerol with l-lysine."
    ),
    "notes": "Peschel et al. 2001 showed that mprF loss prevents lysyl-PG production.",
}

STAUBITZ_REPULSION_EVIDENCE = {
    "reference": "PMID:14769468",
    "snippet": (
        "Staphylococcus aureus achieves CAM resistance by modifying anionic "
        "phosphatidylglycerol with positively charged L-lysine, resulting in "
        "repulsion of the peptides."
    ),
    "notes": (
        "Staubitz et al. 2004 connected anionic PG modification to cationic "
        "antimicrobial molecule repulsion."
    ),
}

STAUBITZ_ACTIVITY_EVIDENCE = {
    "reference": "PMID:14769468",
    "snippet": (
        "We demonstrate here that expression of mprF is sufficient to confer L-PG "
        "production in Escherichia coli, which indicates that MprF represents "
        "the L-PG synthase."
    ),
    "notes": "Staubitz et al. 2004 showed that MprF is sufficient for lysyl-PG synthesis.",
}

RHEA_ACTIVITY_EVIDENCE = {
    "reference": "RHEA:10668",
    "snippet": (
        "L-lysyl-tRNA(Lys) + a 1,2-diacyl-sn-glycero-3-phospho-(1'-sn-glycerol) "
        "= a 1,2-diacyl-sn-glycero-3-phospho-1'-(3'-O-L-lysyl)-sn-glycerol + "
        "tRNA(Lys)"
    ),
    "notes": (
        "Rhea reaction cross-referenced to GO:0050071 phosphatidylglycerol "
        "lysyltransferase activity."
    ),
}

GO_ACTIVITY_EVIDENCE = {
    "reference": "GO:0050071",
    "snippet": (
        "Catalysis of the reaction: L-lysyl-tRNA + phosphatidylglycerol = tRNA + "
        "3-phosphatidyl-1'-(3'-O-L-lysyl)glycerol."
    ),
    "notes": "GO definition for phosphatidylglycerol lysyltransferase activity.",
}

CHEBI_LYSYL_PG_EVIDENCE = {
    "reference": "CHEBI:75792",
    "snippet": (
        "An organic cation obtained by protonation of the amino groups and "
        "deprotonation of the phosphate group of any "
        "1,2-diacyl-sn-glycero-3-phospho-1ʼ-(3ʼ-O-L-lysyl)-sn-glycerol."
    ),
    "notes": "ChEBI definition for the protonated generic lysyl-PG product.",
}

MPRF_ACTIVITY_NODE = {
    "node_id": "mprf_activity",
    "label": "phosphatidylglycerol lysyltransferase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0050071",
    "description": (
        "Grounded to the GO molecular-function term for transfer of lysine from "
        "L-lysyl-tRNA to phosphatidylglycerol."
    ),
}

LYSYL_PG_NODE = {
    "node_id": "lysyl_pg",
    "label": "1,2-diacyl-sn-glycero-3-phospho-1'-(3'-O-L-lysyl)-sn-glycerol(1+)",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:75792",
    "description": (
        "Grounded to ChEBI's protonated generic 1,2-diacyl lysyl-PG term, the "
        "cationic product of phosphatidylglycerol lysyltransferase activity."
    ),
}

SURFACE_CHARGE_NODE = {
    "node_id": "surface_charge",
    "label": "reduced net negative charge of the membrane surface",
    "node_type": "QUALITY",
    "grounding": "PATO:0002193",
    "description": (
        "Grounded to broad PATO electric charge; this local node narrows it to "
        "the less-anionic envelope state produced by cationic lysyl-PG."
    ),
}

SHARED_NODE_UPDATES = {
    "mprf_activity": MPRF_ACTIVITY_NODE,
    "lysyl_pg": LYSYL_PG_NODE,
    "surface_charge": SURFACE_CHARGE_NODE,
}

LEGACY_SYNTHESIS_EDGE = ("determinant", "RO:0002411", "lysyl_pg")
CANONICAL_SYNTHESIS_EDGES = (
    ("determinant", "RO:0002327", "mprf_activity"),
    ("mprf_activity", "RO:0002234", "lysyl_pg"),
)
SURFACE_TO_RESISTANCE_EDGE = ("surface_charge", "RO:0002411", "resistance")


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


TARGETS = {
    "ARO:3003421": Target(
        identifier="ARO:3003421",
        filename="antibiotic-resistant-mprf-aro3003421.yaml",
    ),
    "ARO:3000863": Target(
        identifier="ARO:3000863",
        filename="defensin-resistant-mprf-aro3000863.yaml",
    ),
    "ARO:3003091": Target(
        identifier="ARO:3003091",
        filename="daptomycin-resistant-mprf-aro3003091.yaml",
    ),
    "ARO:3003769": Target(
        identifier="ARO:3003769",
        filename="staphylococcus-aureus-mprf-aro3003769.yaml",
    ),
    "ARO:3003319": Target(
        identifier="ARO:3003319",
        filename="staphylococcus-aureus-mprf-with-mutation-conferring-resistance-to-daptomycin-aro3003319.yaml",
    ),
    "ARO:3003324": Target(
        identifier="ARO:3003324",
        filename="bacillus-subtilis-mprf-aro3003324.yaml",
    ),
    "ARO:3003770": Target(
        identifier="ARO:3003770",
        filename="listeria-monocytogenes-mprf-aro3003770.yaml",
    ),
    "ARO:3003772": Target(
        identifier="ARO:3003772",
        filename="brucella-suis-mprf-aro3003772.yaml",
    ),
    "ARO:3003773": Target(
        identifier="ARO:3003773",
        filename="clostridium-perfringens-mprf-aro3003773.yaml",
    ),
    "ARO:3003774": Target(
        identifier="ARO:3003774",
        filename="streptococcus-agalactiae-mprf-aro3003774.yaml",
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


def _full_edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return edge.get("subject", ""), edge.get("predicate_id", ""), edge.get("object", "")


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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _has_node(graph: dict[str, Any], node_id: str) -> bool:
    return any(node.get("node_id") == node_id for node in graph.get("nodes") or [])


def _drug_edge(graph: dict[str, Any]) -> dict[str, Any] | None:
    return next(
        (
            edge
            for edge in graph.get("edges") or []
            if edge.get("subject") == "determinant" and edge.get("object") == "drug0"
        ),
        None,
    )


def _is_mutation_mechanism(node: dict[str, Any]) -> bool:
    return node.get("grounding") == "ARO:3000212"


def _is_charge_mechanism(node: dict[str, Any]) -> bool:
    return node.get("grounding") == "ARO:3003588"


def _mechanism_nodes(graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        node
        for node in graph.get("nodes") or []
        if isinstance(node, dict) and str(node.get("node_id", "")).startswith("mech")
    ]


def _nodes(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node.get("node_id")): node
        for node in graph.get("nodes") or []
        if isinstance(node, dict)
    }


def _enrich_nodes(graph: dict[str, Any], target: Target) -> None:
    by_id = _nodes(graph)
    missing = sorted({"determinant", "lysyl_pg", "surface_charge", "resistance"} - set(by_id))
    if missing:
        missing_ids = ", ".join(missing)
        raise ValueError(f"{target.identifier}: missing node(s): {missing_ids}")

    node_order = [
        "determinant",
        *[node["node_id"] for node in _mechanism_nodes(graph)],
    ]
    if _has_node(graph, "drug0"):
        node_order.append("drug0")
    node_order += ["mprf_activity", "lysyl_pg", "surface_charge", "resistance"]

    graph["nodes"] = [
        copy.deepcopy(SHARED_NODE_UPDATES[node_id])
        if node_id in SHARED_NODE_UPDATES
        else copy.deepcopy(by_id[node_id])
        for node_id in node_order
    ]


def _legacy_required_edges(graph: dict[str, Any]) -> set[tuple[str, str, str]]:
    required = {
        ("determinant", "RO:0002411", "resistance"),
        LEGACY_SYNTHESIS_EDGE,
        ("lysyl_pg", "RO:0002411", "surface_charge"),
    }
    for node in _mechanism_nodes(graph):
        node_id = str(node["node_id"])
        required.add(("determinant", "RO:0000056", node_id))
        required.add((node_id, "RO:0002411", "resistance"))
    if _has_node(graph, "drug0"):
        required.add(("determinant", "ARO:2000001", "drug0"))
        required.add(("surface_charge", "RO:0002212", "drug0"))
    else:
        required.add(("determinant", "RO:0002411", "resistance"))
    return required


def _canonical_expected_edges(graph: dict[str, Any]) -> set[tuple[str, str, str]]:
    expected = set(_legacy_required_edges(graph))
    expected.discard(LEGACY_SYNTHESIS_EDGE)
    expected.update(CANONICAL_SYNTHESIS_EDGES)
    if not _has_node(graph, "drug0"):
        expected.add(SURFACE_TO_RESISTANCE_EDGE)
    return expected


def _validate_edges(graph: dict[str, Any], target: Target) -> None:
    legacy = _legacy_required_edges(graph)
    canonical = _canonical_expected_edges(graph)
    allowed = legacy | canonical

    full_edges = set()
    seen: set[tuple[str, str]] = set()
    for edge in graph.get("edges") or []:
        full_key = _full_edge_key(edge)
        if full_key not in allowed:
            raise ValueError(f"{target.identifier}: unexpected edge {full_key[0]} -> {full_key[2]}")
        if full_key == LEGACY_SYNTHESIS_EDGE:
            full_edges.update(CANONICAL_SYNTHESIS_EDGES)
            if not _has_node(graph, "drug0"):
                full_edges.add(SURFACE_TO_RESISTANCE_EDGE)
        else:
            full_edges.add(full_key)

        key = _edge_key(edge)
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}")
        seen.add(key)

    missing_edges = sorted(canonical - full_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


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


def _mechanism_edge_evidence(
    node: dict[str, Any],
    target_evidence: dict[str, str],
) -> tuple[dict[str, str], ...]:
    parent_evidence = _parent_evidence(target_evidence)
    if _is_mutation_mechanism(node):
        return (target_evidence, *parent_evidence, MUTATION_EVIDENCE)
    if _is_charge_mechanism(node):
        return (target_evidence, *parent_evidence, STAUBITZ_REPULSION_EVIDENCE)
    return (target_evidence, *parent_evidence, PESCHEL_RESISTANCE_EVIDENCE)


def _parent_evidence(
    target_evidence: dict[str, str],
) -> tuple[dict[str, str], ...]:
    if target_evidence["reference"] == MPRF_PARENT_EVIDENCE["reference"]:
        return ()
    return (MPRF_PARENT_EVIDENCE,)


def _canonical_edges(
    graph: dict[str, Any],
    record: dict[str, Any],
) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    parent_evidence = _parent_evidence(target_evidence)
    drug_edge = _drug_edge(graph)
    edges: list[dict[str, Any]] = []

    for node in _mechanism_nodes(graph):
        node_id = str(node["node_id"])
        evidence = _mechanism_edge_evidence(node, target_evidence)
        edges.extend(
            [
                _edge(
                    "determinant",
                    "participates in (resistance mechanism)",
                    "RO:0000056",
                    node_id,
                    "CARD classifies this MprF determinant under this resistance mechanism.",
                    evidence,
                ),
                _edge(
                    node_id,
                    "causally upstream of",
                    "RO:0002411",
                    "resistance",
                    (
                        "MprF-mediated phosphatidylglycerol lysinylation lowers "
                        "the membrane's net negative charge and supports "
                        "electrostatic peptide resistance."
                    ),
                    (*evidence, PESCHEL_RESISTANCE_EVIDENCE),
                ),
            ]
        )

    edges.append(
        _edge(
            "determinant",
            "causally upstream of (confers electrostatic peptide resistance)",
            "RO:0002411",
            "resistance",
            (
                "MprF produces cationic lysyl-PG, reducing envelope anionic "
                "charge and conferring resistance by cationic peptide repulsion."
            ),
            (target_evidence, *parent_evidence, PESCHEL_RESISTANCE_EVIDENCE),
        )
    )

    if drug_edge is not None:
        drug_evidence = tuple(drug_edge.get("evidence") or ())
        edges.append(
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                (
                    "CARD maps this MprF determinant to the peptide-antibiotic "
                    "class; the mechanistic route is cationic peptide repulsion "
                    "after lysyl-PG synthesis."
                ),
                (
                    target_evidence,
                    *parent_evidence,
                    STAUBITZ_REPULSION_EVIDENCE,
                    *drug_evidence,
                ),
            )
        )

    edges.extend(
        [
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "mprf_activity",
                (
                    "MprF is the phosphatidylglycerol lysyltransferase that "
                    "transfers L-lysine from L-lysyl-tRNA to phosphatidylglycerol."
                ),
                (
                    target_evidence,
                    *parent_evidence,
                    STAUBITZ_ACTIVITY_EVIDENCE,
                    GO_ACTIVITY_EVIDENCE,
                ),
            ),
            _edge(
                "mprf_activity",
                "has output (lysyl-PG)",
                "RO:0002234",
                "lysyl_pg",
                (
                    "Phosphatidylglycerol lysyltransferase activity produces "
                    "the generic lysyl-phosphatidylglycerol product."
                ),
                (
                    MPRF_PARENT_EVIDENCE,
                    GO_ACTIVITY_EVIDENCE,
                    RHEA_ACTIVITY_EVIDENCE,
                    CHEBI_LYSYL_PG_EVIDENCE,
                ),
            ),
            _edge(
                "lysyl_pg",
                "causally upstream of (lowers the net negative charge)",
                "RO:0002411",
                "surface_charge",
                (
                    "Lysinylation of anionic phosphatidylglycerol adds a "
                    "positively charged headgroup and reduces the membrane's "
                    "net negative charge."
                ),
                (
                    MPRF_PARENT_EVIDENCE,
                    PESCHEL_MUTANT_EVIDENCE,
                    STAUBITZ_REPULSION_EVIDENCE,
                    CHEBI_LYSYL_PG_EVIDENCE,
                ),
            ),
        ]
    )

    if drug_edge is not None:
        edges.append(
            _edge(
                "surface_charge",
                "negatively regulates (repels the cationic peptide)",
                "RO:0002212",
                "drug0",
                (
                    "Reduced net negative membrane charge repels cationic "
                    "peptide antibiotics rather than destroying, modifying, "
                    "displacing, or exporting them."
                ),
                (
                    target_evidence,
                    *parent_evidence,
                    PESCHEL_RESISTANCE_EVIDENCE,
                    STAUBITZ_REPULSION_EVIDENCE,
                ),
            )
        )
    else:
        edges.append(
            _edge(
                "surface_charge",
                "causally upstream of (enables peptide resistance)",
                "RO:0002411",
                "resistance",
                (
                    "The less-anionic membrane state provides MprF-mediated "
                    "resistance to cationic antimicrobial peptides."
                ),
                (
                    target_evidence,
                    *parent_evidence,
                    PESCHEL_RESISTANCE_EVIDENCE,
                    STAUBITZ_REPULSION_EVIDENCE,
                ),
            )
        )

    return edges


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

    _validate_edges(graph, target)
    _enrich_nodes(graph, target)
    graph["description"] = (
        "Curated resistance-causation graph for MprF-mediated electrostatic "
        "repulsion. The graph grounds MprF phosphatidylglycerol "
        "lysyltransferase activity to GO and the cationic lysyl-PG product to "
        "ChEBI, while retaining the local reduced-membrane-charge state that "
        "repels cationic peptide antibiotics."
    )
    graph["edges"] = _canonical_edges(graph, out)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an MprF target: {identifier}")
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
        help="ARO directory or one of the ten target YAML files",
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
