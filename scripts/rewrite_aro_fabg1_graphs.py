#!/usr/bin/env python3
"""Ground FabG1 mycolic-acid resistance graphs.

The FabG1 graphs already avoid asserting an inhA-promoter mechanism that CARD
does not state. This updater keeps that conservative shape, grounds FabG1's
first-reduction node to GO:0004316, replaces the old fas_step placeholder with
that grounded activity, and fills out edge descriptions plus multi-source
evidence across the antibiotic-resistant FabG1 branch.

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
HISTORY_ACTION = "Grounded FabG1 mycolic-acid resistance graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

PARENT_IDENTIFIER = "ARO:3004887"

PARENT_DEFINITION = (
    "Mutations that occur in the fabg1 gene resulting in the inability for "
    "the antibiotic to inhibit mycolic acid biosynthesis."
)

ISONIAZID_FABG1_DEFINITION = (
    "fabG1 is involved in the fatty acid synthesis pathway, acting in the "
    "first reduction step for mycolic acid. It is associated with isoniazid "
    "resistance."
)

ETHIONAMIDE_FABG1_DEFINITION = (
    "fabG1 is involved in the fatty acid synthesis pathway, acting in the "
    "first reduction step for mycolic acid. It is associated with ethionamide "
    "resistance."
)

PARENT_EVIDENCE = {
    "reference": PARENT_IDENTIFIER,
    "snippet": PARENT_DEFINITION,
    "notes": "CARD definition for the antibiotic resistant FabG1 parent.",
}

ISONIAZID_FABG1_EVIDENCE = {
    "reference": "ARO:3004895",
    "snippet": ISONIAZID_FABG1_DEFINITION,
    "notes": "CARD definition for isoniazid resistant FabG1.",
}

ETHIONAMIDE_FABG1_EVIDENCE = {
    "reference": "ARO:3004888",
    "snippet": ETHIONAMIDE_FABG1_DEFINITION,
    "notes": "CARD definition for ethionamide resistant FabG1.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

FABG1_ACTIVITY_EVIDENCE = {
    "reference": "GO:0004316",
    "snippet": (
        "Catalysis of the reaction: (3R)-3-hydroxyacyl-[acyl-carrier protein] "
        "+ NADP+ = 3-oxoacyl-[acyl-carrier protein] + NADPH + H+."
    ),
    "notes": (
        "GO 3-oxoacyl-[acyl-carrier-protein] reductase activity term for the "
        "FabG1/MabA reduction step."
    ),
}

EC_EVIDENCE = {
    "reference": "EC:1.1.1.100",
    "snippet": (
        "Enzymatic activity — 3-oxoacyl-[acyl-carrier-protein] reductase "
        "(EC 1.1.1.100). Catalysed reaction: a (3R)-hydroxyacyl-[ACP] + "
        "NADP(+) = a 3-oxoacyl-[ACP] + NADPH + H(+)."
    ),
    "notes": "Local EC record mapped to GO:0004316.",
}

FABG1_FAMILY_EVIDENCE = {
    "reference": "NCBIfam:NF040605",
    "snippet": (
        "3-oxoacyl-ACP reductase FabG1 — a functionally conserved protein "
        "family grouped by the NCBIfam full-length profile-HMM NF040605 "
        "(exception); associated with mycolic acid biosynthetic process. "
        "Members occur in Actinomycetes."
    ),
    "notes": "Local NCBIfam FabG1 family record.",
}

MYCOLIC_EVIDENCE = {
    "reference": "GO:0071768",
    "snippet": (
        "The chemical reactions and pathways resulting in the formation of "
        "mycolic acids, beta-hydroxy fatty acids with a long alpha-alkyl side "
        "chain."
    ),
    "notes": "GO mycolic acid biosynthetic process term.",
}

DRUG_CLASS_EVIDENCE = {
    "ARO:3007152": {
        "reference": "ARO:3007152",
        "snippet": "isoniazid-like antibiotic",
        "notes": "ARO isoniazid-like antibiotic drug-class term.",
    },
    "ARO:3007156": {
        "reference": "ARO:3007156",
        "snippet": "thioamide antibiotic",
        "notes": "ARO thioamide antibiotic drug-class term.",
    },
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

FABG1_ACTIVITY_NODE = {
    "node_id": "fabg1_activity",
    "label": "3-oxoacyl-[acyl-carrier-protein] reductase (NADPH) activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004316",
    "description": (
        "The FabG1/MabA first reduction step in mycolic-acid synthesis, "
        "grounded to the corresponding NADPH-dependent 3-oxoacyl-ACP "
        "reductase GO molecular function."
    ),
}

MYCOLIC_NODE = {
    "node_id": "mycolic",
    "label": "mycolic acid biosynthetic process",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0071768",
}

INHIBITION_NODE = {
    "node_id": "inhibition",
    "label": "drug inhibition of mycolic acid synthesis",
    "node_type": "STATE",
    "description": (
        "Local state for inhibition of the FabG1-linked mycolic-acid "
        "biosynthetic process."
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

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
}

OLD_ACTIVITY_EDGE_KEYS = {
    ("determinant", "RO:0002327", "fas_step"),
    ("fas_step", "BFO:0000050", "mycolic"),
}

NEW_ACTIVITY_EDGE_KEYS = {
    ("determinant", "RO:0002327", "fabg1_activity"),
    ("fabg1_activity", "BFO:0000050", "mycolic"),
}

RESISTANCE_EDGE_KEYS = {
    ("determinant", "RO:0002212", "inhibition"),
}

DRUG_EDGE_KEYS = {
    ("determinant", "ARO:2000001", "drug0"),
    ("drug0", "RO:0002411", "inhibition"),
}

EXPECTED_PARENT_EDGE_KEYS = CORE_EDGE_KEYS | NEW_ACTIVITY_EDGE_KEYS | RESISTANCE_EDGE_KEYS
EXPECTED_CHILD_EDGE_KEYS = EXPECTED_PARENT_EDGE_KEYS | DRUG_EDGE_KEYS
INPUT_EDGE_KEYS = (
    CORE_EDGE_KEYS
    | OLD_ACTIVITY_EDGE_KEYS
    | NEW_ACTIVITY_EDGE_KEYS
    | RESISTANCE_EDGE_KEYS
    | DRUG_EDGE_KEYS
)

EDGE_DESCRIPTIONS = {
    ("determinant", "RO:0000056", "mech0"): (
        "ARO classifies FabG1 resistance records under mutation conferring "
        "antibiotic resistance."
    ),
    ("mech0", "RO:0002411", "resistance"): (
        "FabG1 mutations are a mutation-mediated mycolic-acid-synthesis "
        "resistance mechanism."
    ),
    ("determinant", "RO:0002411", "resistance"): (
        "FabG1 mutations raise resistance by preventing the relevant "
        "antibiotic from inhibiting mycolic-acid biosynthesis."
    ),
    ("determinant", "ARO:2000001", "drug0"): (
        "ARO maps this FabG1 branch to the asserted drug class."
    ),
    ("determinant", "RO:0002327", "fabg1_activity"): (
        "FabG1 normally enables the 3-oxoacyl-ACP reductase step of "
        "mycolic-acid biosynthesis."
    ),
    ("fabg1_activity", "BFO:0000050", "mycolic"): (
        "The FabG1 3-oxoacyl-ACP reductase activity is the first reduction "
        "step in mycolic-acid biosynthesis."
    ),
    ("drug0", "RO:0002411", "inhibition"): (
        "The asserted drug class inhibits FabG1-linked mycolic-acid "
        "biosynthesis in this local resistance model."
    ),
    ("determinant", "RO:0002212", "inhibition"): (
        "Resistance-conferring fabG1 mutations make the antibiotic unable to "
        "inhibit mycolic-acid biosynthesis."
    ),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    drug_identifier: str | None = None
    drug_label: str | None = None
    drug_relation_identifier: str | None = None

    @property
    def has_drug(self) -> bool:
        return self.drug_identifier is not None


TARGETS = {
    PARENT_IDENTIFIER: Target(
        identifier=PARENT_IDENTIFIER,
        filename="antibiotic-resistant-fabg1-aro3004887.yaml",
    ),
    "ARO:3004895": Target(
        identifier="ARO:3004895",
        filename="isoniazid-resistant-fabg1-aro3004895.yaml",
        drug_identifier="ARO:3007152",
        drug_label="isoniazid-like antibiotic",
        drug_relation_identifier="ARO:3004895",
    ),
    "ARO:3004922": Target(
        identifier="ARO:3004922",
        filename="mycobacterium-tuberculosis-fabg1-mutations-confer-resistance-to-isoniazid-aro3004922.yaml",
        drug_identifier="ARO:3007152",
        drug_label="isoniazid-like antibiotic",
        drug_relation_identifier="ARO:3004895",
    ),
    "ARO:3004888": Target(
        identifier="ARO:3004888",
        filename="ethionamide-resistant-fabg1-aro3004888.yaml",
        drug_identifier="ARO:3007156",
        drug_label="thioamide antibiotic",
        drug_relation_identifier="ARO:3004888",
    ),
    "ARO:3004933": Target(
        identifier="ARO:3004933",
        filename="mycobacterium-tuberculosis-fabg1-mutation-conferring-resistance-to-ethionamide-aro3004933.yaml",
        drug_identifier="ARO:3007156",
        drug_label="thioamide antibiotic",
        drug_relation_identifier="ARO:3004888",
    ),
    "ARO:3007841": Target(
        identifier="ARO:3007841",
        filename="prothionamide-resistant-fabg1-aro3007841.yaml",
        drug_identifier="ARO:3007156",
        drug_label="thioamide antibiotic",
        drug_relation_identifier="ARO:3007841",
    ),
    "ARO:3007811": Target(
        identifier="ARO:3007811",
        filename=(
            "mycobacterium-tuberculosis-fabg1-with-mutations-conferring-"
            "resistance-to-prothio-aro3007811.yaml"
        ),
        drug_identifier="ARO:3007156",
        drug_label="thioamide antibiotic",
        drug_relation_identifier="ARO:3007841",
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


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    if record["identifier"] == PARENT_IDENTIFIER:
        return PARENT_EVIDENCE
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_node(target: Target) -> dict[str, Any]:
    if not target.has_drug:
        raise ValueError(f"{target.identifier}: no drug mapping")
    return {
        "node_id": "drug0",
        "label": target.drug_label,
        "node_type": "CHEMICAL",
        "grounding": target.drug_identifier,
    }


def _drug_relation_evidence(target: Target) -> dict[str, str]:
    if not target.has_drug:
        raise ValueError(f"{target.identifier}: no drug mapping")

    assert target.drug_identifier is not None
    assert target.drug_label is not None
    assert target.drug_relation_identifier is not None

    if target.identifier == target.drug_relation_identifier:
        notes = (
            f"ARO drug-class relationship asserted directly on "
            f"{target.drug_relation_identifier}."
        )
    else:
        notes = (
            f"ARO drug-class relationship asserted on "
            f"{target.drug_relation_identifier} and inherited by "
            f"{target.identifier}."
        )
    return {
        "reference": target.drug_relation_identifier,
        "snippet": (
            f"relationship: confers_resistance_to_drug_class "
            f"{target.drug_identifier} ! {target.drug_label}"
        ),
        "notes": notes,
    }


def _unique_evidence(evidence: tuple[dict[str, str], ...]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in evidence:
        key = (item["reference"], " ".join(item.get("snippet", "").split()))
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


def _expected_edge_keys(target: Target) -> set[tuple[str, str, str]]:
    keys = set(EXPECTED_PARENT_EDGE_KEYS)
    if target.has_drug:
        keys.update(DRUG_EDGE_KEYS)
    return keys


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {"determinant", "mech0", "mycolic", "inhibition", "resistance"}
    if target.has_drug:
        required_nodes.add("drug0")
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)

    activity_edge = (
        ("determinant", "RO:0002327", "fas_step") in seen
        or ("determinant", "RO:0002327", "fabg1_activity") in seen
    )
    pathway_edge = (
        ("fas_step", "BFO:0000050", "mycolic") in seen
        or ("fabg1_activity", "BFO:0000050", "mycolic") in seen
    )
    required = CORE_EDGE_KEYS | RESISTANCE_EDGE_KEYS
    if target.has_drug:
        required.update(DRUG_EDGE_KEYS)
    missing_edges = required - seen
    if missing_edges or not activity_edge or not pathway_edge:
        if not activity_edge:
            missing_edges.add(("determinant", "RO:0002327", "fabg1_activity"))
        if not pathway_edge:
            missing_edges.add(("fabg1_activity", "BFO:0000050", "mycolic"))
        missing = ", ".join(
            f"{subject} -> {object_}"
            for subject, _, object_ in sorted(missing_edges)
        )
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")


def _canonical_graph(record: dict[str, Any], target: Target) -> dict[str, Any]:
    graph = record["causal_graphs"][0]
    _validate_graph(graph, target)
    nodes = _nodes_by_id(graph)
    target_evidence = _target_evidence(record)
    source_evidence = _source_evidence(record)

    mutation_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
        *source_evidence,
    )
    activity_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        ISONIAZID_FABG1_EVIDENCE,
        ETHIONAMIDE_FABG1_EVIDENCE,
        FABG1_ACTIVITY_EVIDENCE,
        EC_EVIDENCE,
        FABG1_FAMILY_EVIDENCE,
        *source_evidence,
    )
    pathway_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        ISONIAZID_FABG1_EVIDENCE,
        ETHIONAMIDE_FABG1_EVIDENCE,
        MYCOLIC_EVIDENCE,
        FABG1_FAMILY_EVIDENCE,
        *source_evidence,
    )
    inhibition_evidence = (
        target_evidence,
        PARENT_EVIDENCE,
        ISONIAZID_FABG1_EVIDENCE,
        ETHIONAMIDE_FABG1_EVIDENCE,
        *source_evidence,
    )

    node_list = [
        copy.deepcopy(nodes["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
    ]
    if target.has_drug:
        node_list.append(_drug_node(target))
    node_list.extend(
        [
            copy.deepcopy(FABG1_ACTIVITY_NODE),
            copy.deepcopy(MYCOLIC_NODE),
            copy.deepcopy(INHIBITION_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ]
    )

    edge_list = [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            mutation_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            mutation_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            inhibition_evidence,
        ),
    ]

    if target.has_drug:
        drug_evidence = (
            target_evidence,
            PARENT_EVIDENCE,
            _drug_relation_evidence(target),
            DRUG_CLASS_EVIDENCE[str(target.drug_identifier)],
            *source_evidence,
        )
        edge_list.extend(
            [
                _edge(
                    "determinant",
                    "confers resistance to",
                    "ARO:2000001",
                    "drug0",
                    drug_evidence,
                ),
                _edge(
                    "drug0",
                    "causally upstream of",
                    "RO:0002411",
                    "inhibition",
                    (*drug_evidence, *inhibition_evidence),
                ),
            ]
        )

    edge_list.extend(
        [
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "fabg1_activity",
                activity_evidence,
            ),
            _edge(
                "fabg1_activity",
                "part of",
                "BFO:0000050",
                "mycolic",
                pathway_evidence,
            ),
            _edge(
                "determinant",
                "negatively regulates",
                "RO:0002212",
                "inhibition",
                inhibition_evidence,
            ),
        ]
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → FabG1 mycolic-acid synthesis → resistance",
        "description": (
            "Conservative graph for FabG1-mediated mycolic-acid-synthesis "
            "resistance. The graph grounds the first reduction step to "
            "3-oxoacyl-[acyl-carrier-protein] reductase activity and models "
            "the resistance mutation as preventing drug inhibition of the "
            "mycolic-acid biosynthetic process."
        ),
        "nodes": node_list,
        "edges": edge_list,
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph_index = next(
        (index for index, item in enumerate(graphs) if item.get("graph_id") == "resistance"),
        None,
    )
    if graph_index is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    graphs[graph_index] = _canonical_graph(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a FabG1 target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(
        text,
        "causal_graphs",
        _dump({"causal_graphs": enriched["causal_graphs"]}),
    )
    if HISTORY_ACTION not in out:
        out = append_to_section(
            out,
            "curation_history",
            _dump({"curation_history": [HISTORY_EVENT]}),
        )
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
    parser.add_argument("--path", type=Path, default=ARO_DIR, help="ARO directory or exact FabG1 YAML")
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
