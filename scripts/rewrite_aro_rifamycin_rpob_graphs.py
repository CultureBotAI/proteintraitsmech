#!/usr/bin/env python3
"""Rewrite rifamycin-resistant rpoB causal graphs.

The rifamycin rpoB branch already models the core mechanism, the RpoB domain,
RNA polymerase activity, and rifamycin binding. These records were left at a
low score because most edges lacked descriptions and the RRDR was represented
as an ungrounded MOTIF. This updater keeps the grounded domain/activity/drug
context but collapses the organism-frame-dependent RRDR into a local
rifamycin-binding-pocket state.

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
HISTORY_ACTION = "Grounded rifamycin rpoB target-replacement graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-08T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

TARGET_REPLACEMENT_EVIDENCE = {
    "reference": "ARO:0001002",
    "snippet": (
        "Replacement or substitution of antibiotic action target, which "
        "process will result in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target replacement.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

RPOB_PARENT_EVIDENCE = {
    "reference": "ARO:3000210",
    "snippet": (
        "Rifampin resistant RNA polymerases include amino acids substitutions "
        "which disrupt the affinity of rifampin for its binding site."
    ),
    "notes": (
        "CARD definition for rifamycin-resistant beta-subunit of RNA "
        "polymerase (rpoB)."
    ),
}

PFAM_RPB2_EVIDENCE = {
    "reference": "Pfam:PF04563",
    "snippet": "This domain forms one of the two distinctive lobes of the Rpb2 structure.",
    "notes": "KB trait record for the RNA polymerase beta subunit domain.",
}

RNAP_ACTIVITY_EVIDENCE = {
    "reference": "GO:0003899",
    "snippet": (
        "Catalysis of the reaction: nucleoside triphosphate + RNA(n) = "
        "diphosphate + RNA(n+1)."
    ),
    "notes": "Gene Ontology definition for DNA-directed RNA polymerase activity.",
}

CAMPBELL_BINDING_EVIDENCE = {
    "reference": "PMID:11290327",
    "snippet": "The inhibitor binds in a pocket of the RNAP beta subunit",
    "notes": (
        "Campbell et al. 2001 resolved rifampicin binding in the RNA "
        "polymerase beta-subunit pocket."
    ),
}

CAMPBELL_BLOCK_EVIDENCE = {
    "reference": "PMID:11290327",
    "snippet": "directly blocking the path of the elongating RNA",
    "notes": (
        "Campbell et al. 2001 showed how rifampicin blocks extension of the "
        "nascent RNA transcript."
    ),
}

RIFAMYCIN_EVIDENCE = {
    "reference": "ARO:3000157",
    "snippet": "rifamycin antibiotic",
    "notes": "ARO drug-class term for rifamycin antibiotics.",
}

MECHANISM_NODES = [
    {
        "node_id": "mech0",
        "label": "antibiotic target replacement",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "ARO:0001002",
    },
    {
        "node_id": "mech1",
        "label": "mutation conferring antibiotic resistance",
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": "ARO:3000212",
    },
]

DRUG_CLASS_NODE = {
    "node_id": "drug0",
    "label": "rifamycin antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3000157",
}

DOMAIN_NODE = {
    "node_id": "domain",
    "label": "RNA polymerase beta subunit domain",
    "node_type": "DOMAIN",
    "grounding": "Pfam:PF04563",
    "description": "RpoB beta-subunit domain carrying rifamycin-resistance substitutions.",
}

RNAP_ACTIVITY_NODE = {
    "node_id": "rnap_activity",
    "label": "DNA-directed RNA polymerase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0003899",
}

RIFAMPICIN_NODE = {
    "node_id": "rif",
    "label": "rifampicin",
    "node_type": "CHEMICAL",
    "grounding": "CHEBI:28077",
}

RIF_POCKET_NODE = {
    "node_id": "rif_pocket",
    "label": "rifamycin binding to the RpoB pocket",
    "node_type": "STATE",
    "description": (
        "Local state for rifampicin binding in the beta-subunit pocket whose "
        "affinity is disrupted by resistance substitutions."
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

CORE_INPUT_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0000056", "mech1"),
    ("mech1", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("domain", "BFO:0000050", "determinant"),
    ("domain", "RO:0002327", "rnap_activity"),
    ("rif", "RO:0002436", "rif_pocket"),
    ("rif_pocket", "RO:0002212", "rnap_activity"),
}

OLD_RRDR_EDGE_KEYS = {
    ("rrdr", "BFO:0000050", "domain"),
    ("rrdr", "RO:0002212", "rif_pocket"),
}

NEW_POCKET_EDGE_KEY = ("determinant", "RO:0002212", "rif_pocket")

INPUT_ALLOWED_EDGE_KEYS = {
    *CORE_INPUT_EDGE_KEYS,
    *OLD_RRDR_EDGE_KEYS,
    NEW_POCKET_EDGE_KEY,
}

OUTPUT_EDGE_KEYS = {
    *CORE_INPUT_EDGE_KEYS,
    NEW_POCKET_EDGE_KEY,
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str


_TARGET_ROWS = """
ARO:3000210 rifamycin-resistant-beta-subunit-of-rna-polymerase-rpob-aro3000210.yaml
ARO:3000501 rpob2-aro3000501.yaml
ARO:3003283 mycobacterium-tuberculosis-rpob-with-mutations-conferring-resistance-to-rifampic-aro3003283.yaml
ARO:3003284 mycobacterium-leprae-rpob-mutations-conferring-resistance-to-rifampicin-aro3003284.yaml
ARO:3003285 staphylococcus-aureus-rpob-mutants-conferring-resistance-to-rifampicin-aro3003285.yaml
ARO:3003288 escherichia-coli-rpob-mutants-conferring-resistance-to-rifampicin-aro3003288.yaml
ARO:3004480 bifidobacterium-adolescentis-rpob-mutants-conferring-resistance-to-rifampicin-aro3004480.yaml
ARO:3004563 clostridioides-difficile-rpob-with-mutation-conferring-resistance-to-rifampicin-aro3004563.yaml
ARO:3007051 helicobacter-pylori-rpob-mutation-conferring-resistance-to-rifampicin-aro3007051.yaml
ARO:3007073 bacillus-subtilis-rpob-mutants-conferring-resistance-to-rifampin-aro3007073.yaml
ARO:3007794 vibrio-vulnificus-rpob-mutants-conferring-resistance-to-rifampin-aro3007794.yaml
"""

TARGETS: tuple[Target, ...] = tuple(
    Target(identifier, filename)
    for identifier, filename in (line.split() for line in _TARGET_ROWS.strip().splitlines())
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


def _edge_key(edge: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(edge.get("subject", "")),
        str(edge.get("predicate_id", "")),
        str(edge.get("object", "")),
    )


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (
            str(item["reference"]),
            str(item.get("snippet", "")),
            str(item.get("notes", "")),
        )
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
    *evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _edge_evidence(
    graph: dict[str, Any],
    *keys: tuple[str, str, str],
) -> list[dict[str, Any]]:
    wanted = set(keys)
    for edge in _dicts(graph.get("edges")):
        if _edge_key(edge) in wanted:
            evidence = _dicts(edge.get("evidence"))
            if evidence:
                return copy.deepcopy(evidence)
    labels = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in keys)
    raise ValueError(f"missing edge evidence for {labels}")


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _nodes_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(node["node_id"]): node
        for node in _dicts(graph.get("nodes"))
        if "node_id" in node
    }


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _drug_relation_evidence(graph: dict[str, Any]) -> list[dict[str, Any]]:
    relation_evidence: list[dict[str, Any]] = []
    for edge in _dicts(graph.get("edges")):
        if _edge_key(edge) != ("determinant", "ARO:2000001", "drug0"):
            continue
        relation_evidence.extend(
            item
            for item in _dicts(edge.get("evidence"))
            if str(item.get("snippet", "")).startswith(
                "relationship: confers_resistance_to_drug_class "
            )
        )
    if not relation_evidence:
        raise ValueError("missing drug relationship evidence")
    return copy.deepcopy(relation_evidence)


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    required_nodes = {
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "domain",
        "rnap_activity",
        "rif",
        "rif_pocket",
        "resistance",
    }
    missing_nodes = sorted(required_nodes - set(nodes))
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in _dicts(graph.get("edges")):
        key = _edge_key(edge)
        if key not in INPUT_ALLOWED_EDGE_KEYS:
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found.add(key)

    missing_edges = sorted(CORE_INPUT_EDGE_KEYS - found)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{target.identifier}: missing edge(s): {missing}")

    if NEW_POCKET_EDGE_KEY not in found and ("rrdr", "RO:0002212", "rif_pocket") not in found:
        raise ValueError(f"{target.identifier}: missing rifamycin-pocket alteration edge")


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
    _validate_graph(graphs[0], target)


def _graph(record: dict[str, Any], old_graph: dict[str, Any]) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    replacement_evidence = (
        record_evidence,
        RPOB_PARENT_EVIDENCE,
        TARGET_REPLACEMENT_EVIDENCE,
    )
    mutation_evidence = (
        record_evidence,
        RPOB_PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → altered RpoB rifamycin binding → resistance",
        "description": (
            "Conservative graph for rifamycin-resistant RpoB beta-subunit "
            "variants. The graph keeps the grounded RpoB domain and RNA "
            "polymerase activity, but models resistance-conferring changes to "
            "the rifamycin-binding pocket as a local state so it does not need "
            "organism-specific residue coordinates."
        ),
        "nodes": [
            _determinant_node(record),
            *(copy.deepcopy(node) for node in MECHANISM_NODES),
            copy.deepcopy(DRUG_CLASS_NODE),
            copy.deepcopy(DOMAIN_NODE),
            copy.deepcopy(RNAP_ACTIVITY_NODE),
            copy.deepcopy(RIFAMPICIN_NODE),
            copy.deepcopy(RIF_POCKET_NODE),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (target replacement mechanism)",
                "RO:0000056",
                "mech0",
                "ARO classifies rifamycin-resistant RpoB under antibiotic target replacement.",
                *replacement_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Substitution of the rifampicin action target results in rifamycin resistance.",
                *replacement_evidence,
            ),
            _edge(
                "determinant",
                "participates in (mutation mechanism)",
                "RO:0000056",
                "mech1",
                "The resistance-conferring RpoB variants are amino-acid substitutions.",
                *mutation_evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "RpoB point mutations alter the gene product and confer rifamycin resistance.",
                *mutation_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "Mutated RpoB beta subunits disrupt rifampicin binding and confer resistance.",
                record_evidence,
                RPOB_PARENT_EVIDENCE,
                TARGET_REPLACEMENT_EVIDENCE,
                MUTATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "confers resistance to",
                "ARO:2000001",
                "drug0",
                "ARO maps rifamycin-resistant rpoB to rifamycin antibiotics.",
                *_drug_relation_evidence(old_graph),
                record_evidence,
                RIFAMYCIN_EVIDENCE,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The RpoB domain is part of the resistance determinant.",
                *_edge_evidence(old_graph, ("domain", "BFO:0000050", "determinant")),
                record_evidence,
                PFAM_RPB2_EVIDENCE,
            ),
            _edge(
                "domain",
                "enables",
                "RO:0002327",
                "rnap_activity",
                "RpoB beta-subunit structure contributes to DNA-directed RNA polymerase activity.",
                PFAM_RPB2_EVIDENCE,
                RNAP_ACTIVITY_EVIDENCE,
            ),
            _edge(
                "rif",
                "molecularly interacts with",
                "RO:0002436",
                "rif_pocket",
                "Rifampicin binds in the RNA polymerase beta-subunit pocket.",
                CAMPBELL_BINDING_EVIDENCE,
                RPOB_PARENT_EVIDENCE,
            ),
            _edge(
                "rif_pocket",
                "negatively regulates",
                "RO:0002212",
                "rnap_activity",
                "Rifampicin binding to the beta-subunit pocket blocks nascent transcript extension.",
                CAMPBELL_BINDING_EVIDENCE,
                CAMPBELL_BLOCK_EVIDENCE,
                RNAP_ACTIVITY_EVIDENCE,
            ),
            _edge(
                "determinant",
                "negatively regulates",
                "RO:0002212",
                "rif_pocket",
                "RpoB substitutions reduce rifampicin affinity for the beta-subunit binding site.",
                record_evidence,
                RPOB_PARENT_EVIDENCE,
                TARGET_REPLACEMENT_EVIDENCE,
            ),
        ],
    }


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [_graph(record, record["causal_graphs"][0])]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a rifamycin rpoB target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, _ = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_ACTION not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))

    if "&id" in out or "*id" in out:
        raise ValueError(f"{path}: YAML anchors leaked into output")
    return out, out != text


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
        help="ARO directory or one of the eleven rifamycin rpoB YAML files",
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
