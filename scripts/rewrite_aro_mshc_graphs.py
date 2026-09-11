#!/usr/bin/env python3
"""Ground mshC mycothiol-biosynthesis resistance graphs.

The ARO mshC branch has a broad parent that only states that mshC mutations
block antibiotic function, plus ethionamide- and isoniazid-specific children
that name the ATP-dependent GlcN-Ins/L-cysteine condensation in mycothiol
biosynthesis. This updater promotes the exact local branch and adds the
reaction side path only to records whose ARO definitions support it.

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
HISTORY_ACTION = "Grounded mshC mycothiol-biosynthesis resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
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

ISONIAZID_MSHC_EVIDENCE = {
    "reference": "ARO:3004904",
    "snippet": (
        "Mutations that occur on the mshC gene resulting in the inability for "
        "isoniazid to function. It catalyzes the ATP-dependent condensation of "
        "GlcN-Ins and L-cysteine to form L-Cys-GlcN-Ins."
    ),
    "notes": "CARD definition for the isoniazid-resistant mshC parent.",
}

ETHIONAMIDE_MSHC_EVIDENCE = {
    "reference": "ARO:3004890",
    "snippet": (
        "Mutations that occur in mshC which is involved in the third step of "
        "mycothiol biosynthesis. It catalyzes the ATP-dependent condensation "
        "of GlcN-Ins and L-cysteine to form L-Cys-GlcN-Ins. The gene exhibits "
        "resistance to ethionamide."
    ),
    "notes": "CARD definition for the ethionamide-resistant mshC parent.",
}

MSHC_LIGASE_EVIDENCE = {
    "reference": "GO:0035446",
    "snippet": (
        "Catalysis of the reaction: "
        "1-(2-amino-2-deoxy-alpha-D-glucopyranoside)-1D-myo-inositol + "
        "L-cysteine + ATP = "
        "1-D-myo-inosityl-2-L-cysteinylamido-2-deoxy-alpha-D-glucopyranoside "
        "+ AMP + diphosphate + 2 H+."
    ),
    "notes": "GO definition for cysteine-glucosaminylinositol ligase activity.",
}

CYS_GLCN_INS_EVIDENCE = {
    "reference": "RHEA:26177",
    "snippet": (
        "1D-myo-inositol 2-amino-2-deoxy-alpha-D-glucopyranoside + "
        "L-cysteine + ATP => "
        "1D-myo-inositol 2-(L-cysteinylamino)-2-deoxy-alpha-D-glucopyranoside "
        "+ AMP + diphosphate + H(+)"
    ),
    "notes": (
        "Rhea's left-to-right directional child of RHEA:26176 declares "
        "1D-myo-inositol 2-(L-cysteinylamino)-2-deoxy-alpha-D-glucopyranoside "
        "as a product grounded to CHEBI:58887."
    ),
}

MYCOTHIOL_BIOSYNTHESIS_EVIDENCE = {
    "reference": "GO:0010125",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "mycothiol, which consists of N-acetyl-L-cysteine linked to a "
        "pseudodisaccharide, D-glucosamine and myo-inositol."
    ),
    "notes": "GO definition for mycothiol biosynthetic process.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

MSHC_LIGASE_NODE = {
    "node_id": "mshc_ligase",
    "label": "cysteine-glucosaminylinositol ligase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0035446",
}

CYS_GLCN_INS_NODE = {
    "node_id": "cys_glcn_ins",
    "label": "L-Cys-GlcN-Ins",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:58887",
}

MYCOTHIOL_BIOSYNTHESIS_NODE = {
    "node_id": "mycothiol_biosynthesis",
    "label": "mycothiol biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0010125",
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
    graph_description: str
    drug_relation_reference: str | None = None
    drug_relation_object: str | None = None
    drug_relation_label: str | None = None
    inherited_reaction_evidence: tuple[dict[str, str], ...] = ()

    @property
    def has_drug(self) -> bool:
        return self.drug_relation_reference is not None

    @property
    def has_reaction(self) -> bool:
        return self.identifier in {"ARO:3004890", "ARO:3004904"} or bool(
            self.inherited_reaction_evidence
        )


TARGETS = {
    "ARO:3004889": Target(
        identifier="ARO:3004889",
        filename="antibiotic-resistant-mshc-aro3004889.yaml",
        graph_description=(
            "Conservative graph for the antibiotic-resistant mshC parent. "
            "The graph keeps only the broad mshC mutation-resistance claim "
            "because this ARO record does not identify a drug class or name "
            "MshC's mycothiol-biosynthesis reaction."
        ),
    ),
    "ARO:3004890": Target(
        identifier="ARO:3004890",
        filename="ethionamide-resistant-mshc-aro3004890.yaml",
        graph_description=(
            "Conservative graph for ethionamide-resistant mshC. The graph "
            "grounds the MshC ligase reaction and Cys-GlcN-Ins product named "
            "by ARO, keeps the thioamide drug-class edge, and does not add an "
            "unsupported ethionamide activation edge."
        ),
        drug_relation_reference="ARO:3004890",
        drug_relation_object="ARO:3007156",
        drug_relation_label="thioamide antibiotic",
    ),
    "ARO:3004904": Target(
        identifier="ARO:3004904",
        filename="isoniazid-resistant-mshc-aro3004904.yaml",
        graph_description=(
            "Conservative graph for isoniazid-resistant mshC. The graph "
            "grounds the MshC ligase reaction and Cys-GlcN-Ins product named "
            "by ARO, keeps the isoniazid-like drug-class edge, and does not "
            "add an unsupported isoniazid activation edge."
        ),
        drug_relation_reference="ARO:3004904",
        drug_relation_object="ARO:3007152",
        drug_relation_label="isoniazid-like antibiotic",
    ),
    "ARO:3004927": Target(
        identifier="ARO:3004927",
        filename="mycobacterium-tuberculosis-mshc-mutations-conferring-resistance-to-isoniazid-aro3004927.yaml",
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis mshC mutations "
            "conferring isoniazid resistance. The graph grounds the inherited "
            "MshC ligase reaction and Cys-GlcN-Ins product, and keeps the "
            "inherited isoniazid-like drug-class edge."
        ),
        drug_relation_reference="ARO:3004904",
        drug_relation_object="ARO:3007152",
        drug_relation_label="isoniazid-like antibiotic",
        inherited_reaction_evidence=(ISONIAZID_MSHC_EVIDENCE,),
    ),
    "ARO:3004934": Target(
        identifier="ARO:3004934",
        filename="mycobacterium-tuberculosis-mshc-mutations-conferring-resistance-to-ethionamide-aro3004934.yaml",
        graph_description=(
            "Conservative graph for Mycobacterium tuberculosis mshC mutations "
            "conferring ethionamide resistance. The graph grounds the "
            "inherited MshC ligase reaction and Cys-GlcN-Ins product, and "
            "keeps the inherited thioamide drug-class edge."
        ),
        drug_relation_reference="ARO:3004890",
        drug_relation_object="ARO:3007156",
        drug_relation_label="thioamide antibiotic",
        inherited_reaction_evidence=(ETHIONAMIDE_MSHC_EVIDENCE,),
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


def _drug_evidence(target: Target) -> dict[str, str]:
    if (
        target.drug_relation_reference is None
        or target.drug_relation_object is None
        or target.drug_relation_label is None
    ):
        raise ValueError(f"{target.identifier}: no drug relation configured")

    return {
        "reference": target.drug_relation_reference,
        "snippet": (
            "confers_resistance_to_drug_class "
            f"{target.drug_relation_object} ! {target.drug_relation_label}"
        ),
        "notes": (
            f"ARO drug-class relationship on {target.drug_relation_reference}; "
            f"modeled here as a determinant-to-{target.drug_relation_label} edge."
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


def _canonical_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    expected = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
    }
    if target.has_drug:
        expected.add(("determinant", "ARO:2000001", "drug0"))
    if target.has_reaction:
        expected.update(
            {
                ("determinant", "RO:0002327", "mshc_ligase"),
                ("mshc_ligase", "RO:0002234", "cys_glcn_ins"),
                ("mshc_ligase", "BFO:0000050", "mycothiol_biosynthesis"),
            }
        )
    return expected


def _input_allowed_edges(target: Target) -> set[tuple[str, str, str]]:
    allowed = _canonical_edge_keys(target)
    if target.has_reaction:
        allowed.update(
            {
                ("determinant", "RO:0002327", "condensation"),
                ("condensation", "RO:0002234", "cys_glcn_ins"),
            }
        )
    return allowed


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "resistance"}
    if target.has_drug:
        required_nodes.add("drug0")
    if "drug0" in nodes and not target.has_drug:
        raise ValueError(f"{target.identifier}: unexpected drug0 node")

    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    required_edges = {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
    }
    if target.has_drug:
        required_edges.add(("determinant", "ARO:2000001", "drug0"))

    found = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges(target):
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(required_edges - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_nodes(graph: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    ordered = [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
    ]
    if target.has_drug:
        ordered.append(
            {
                "node_id": "drug0",
                "label": target.drug_relation_label,
                "node_type": "CHEMICAL",
                "grounding": target.drug_relation_object,
            }
        )
    if target.has_reaction:
        ordered.extend(
            [
                copy.deepcopy(MSHC_LIGASE_NODE),
                copy.deepcopy(CYS_GLCN_INS_NODE),
                copy.deepcopy(MYCOTHIOL_BIOSYNTHESIS_NODE),
            ]
        )
    ordered.append(copy.deepcopy(RESISTANCE_NODE))
    return ordered


def _reaction_evidence(
    target_evidence: dict[str, str],
    target: Target,
) -> tuple[dict[str, str], ...]:
    return (
        target_evidence,
        *target.inherited_reaction_evidence,
        MSHC_LIGASE_EVIDENCE,
    )


def _canonical_edges(record: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    mutation_evidence = (target_evidence, MUTATION_EVIDENCE)
    if target.inherited_reaction_evidence:
        mutation_evidence = (
            target_evidence,
            *target.inherited_reaction_evidence,
            MUTATION_EVIDENCE,
        )

    edges = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            "The ARO hierarchy classifies resistant mshC variants under point mutations.",
            mutation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            "The inherited point-mutation mechanism links mshC determinants to resistance.",
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            "The local ARO definition states that mshC mutations confer antibiotic resistance.",
            mutation_evidence,
        ),
    ]

    if target.has_drug:
        edges.append(
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                "drug0",
                (
                    "The ARO hierarchy links this mshC determinant to the "
                    f"{target.drug_relation_label} resistance class."
                ),
                (
                    target_evidence,
                    *target.inherited_reaction_evidence,
                    _drug_evidence(target),
                    MUTATION_EVIDENCE,
                ),
            )
        )

    if target.has_reaction:
        reaction_evidence = _reaction_evidence(target_evidence, target)
        edges.extend(
            [
                _edge(
                    "determinant",
                    "enables",
                    "RO:0002327",
                    "mshc_ligase",
                    "ARO identifies MshC as the ligase that condenses GlcN-Ins and L-cysteine.",
                    reaction_evidence,
                ),
                _edge(
                    "mshc_ligase",
                    "has output (L-Cys-GlcN-Ins)",
                    "RO:0002234",
                    "cys_glcn_ins",
                    "MshC ligase activity forms Cys-GlcN-Ins.",
                    reaction_evidence + (CYS_GLCN_INS_EVIDENCE,),
                ),
                _edge(
                    "mshc_ligase",
                    "part of (mycothiol biosynthesis)",
                    "BFO:0000050",
                    "mycothiol_biosynthesis",
                    "ARO places the MshC ligase reaction in mycothiol biosynthesis.",
                    reaction_evidence + (MYCOTHIOL_BIOSYNTHESIS_EVIDENCE,),
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
    graph["title"] = f"{record['label']} → mshC mutation → resistance"
    graph["description"] = target.graph_description
    graph["nodes"] = _canonical_nodes(graph, target)
    graph["edges"] = _canonical_edges(out, target)
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
        raise ValueError(f"{path}: not an mshC target: {identifier}")
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
        help="ARO directory or one of the four target YAML files",
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
