#!/usr/bin/env python3
"""Ground and complete the MexS-mediated MexEF-OprN derepression graph.

MexS mutations derepress MexT, a positive regulator of the MexEF-OprN pump.
The existing seed used a direct activator scaffold copied from AdeR; this
updater replaces that scaffold with a MexS -> MexT -> MexEF-OprN path, grounds
the MexT, MexEF-OprN, suppression, and activation nodes, and replaces stale
archetype evidence with exact CARD evidence.

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
TARGET_IDENTIFIER = "ARO:3000813"
TARGET_FILENAME = "mexs-aro3000813.yaml"

HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Replaced the stale MexS direct-activation scaffold with MexS loss, "
        "MexT derepression, MexEF-OprN activation, and exact target/activator/"
        "pump evidence"
    ),
    "llm_assisted": True,
}

MEXS_EVIDENCE = {
    "reference": TARGET_IDENTIFIER,
    "snippet": (
        "MexS is a suppressor of MexT, which is an activator of the multidrug pump "
        "MexEF-OprN. Mutations in MexS lead to multidrug resistance."
    ),
    "notes": "CARD definition for the MexS suppressor determinant.",
}

MEXT_EVIDENCE = {
    "reference": "ARO:3000814",
    "snippet": (
        "MexT is a LysR-type transcriptional activator that positively regulates "
        "the expression of MexEF-OprN, OprD, and MexS."
    ),
    "notes": "CARD definition for the MexT activator.",
}

MEXEF_OPRN_EVIDENCE = {
    "reference": "ARO:3000798",
    "snippet": (
        "MexEF-OprN is a multidrug efflux protein expressed in the Gram-negative "
        "Pseudomonas aeruginosa. MexE is the membrane fusion protein; MexF is the "
        "inner membrane transporter; and OprN is the outer membrane channel. "
        "MexEF-OprN is associated with resistance to fluoroquinolones, "
        "chloramphenicol, and trimethoprim."
    ),
    "notes": "CARD definition for the MexEF-OprN pump activated by MexT.",
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

GO_POSITIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045893",
    "snippet": (
        "Any process that activates or increases the frequency, rate or extent of "
        "cellular DNA-templated transcription."
    ),
    "notes": "GO definition for the broad transcriptional activation process.",
}

GO_NEGATIVE_MOLECULAR_FUNCTION_EVIDENCE = {
    "reference": "GO:0044092",
    "snippet": (
        "Any process that stops or reduces the rate or extent of a molecular "
        "function, an elemental biological activity occurring at the molecular level."
    ),
    "notes": "GO definition for the broad negative regulation of molecular function.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
}

MUTATION_NODE = {
    "node_id": "mech1",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
}

ACTIVATOR_NODE = {
    "node_id": "activator",
    "label": "MexT",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000814",
    "description": (
        "Grounded to CARD's MexT activator, the MexEF-OprN positive regulator "
        "normally suppressed by MexS."
    ),
}

SUPPRESSION_NODE = {
    "node_id": "suppression",
    "label": "negative regulation of MexT molecular function",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0044092",
    "description": (
        "Grounded to broad negative regulation of molecular function because MexS "
        "suppresses the MexT activator."
    ),
}

ACTIVATION_NODE = {
    "node_id": "activation",
    "label": "positive regulation of MexEF-OprN expression",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0045893",
    "description": (
        "Grounded to the broad GO DNA-templated transcriptional activation process "
        "because MexT activates MexEF-OprN expression."
    ),
}

PUMP_NODE = {
    "node_id": "pump",
    "label": "MexEF-OprN",
    "node_type": "PROTEIN",
    "grounding": "ARO:3000798",
    "description": "Grounded to CARD's MexEF-OprN efflux pump.",
}

RESISTANCE_NODE = {
    "node_id": "resistance",
    "label": "antibiotic resistance phenotype",
    "node_type": "PHENOTYPE",
    "grounding": "GO:0046677",
    "description": (
        "Resistance phenotype conferred by this determinant. Grounded to the "
        "nearest available superclass: ARO models determinants and mechanisms but "
        "has no term for the resistance phenotype itself."
    ),
}

NODE_ORDER = (
    "determinant",
    "mech0",
    "mech1",
    "activator",
    "suppression",
    "activation",
    "pump",
    "resistance",
)

SHARED_NODE_UPDATES = {
    "mech0": MECHANISM_NODE,
    "mech1": MUTATION_NODE,
    "activator": ACTIVATOR_NODE,
    "suppression": SUPPRESSION_NODE,
    "activation": ACTIVATION_NODE,
    "pump": PUMP_NODE,
    "resistance": RESISTANCE_NODE,
}


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    evidence: tuple[dict[str, str], ...],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": [copy.deepcopy(item) for item in evidence],
    }


EDGE_UPDATES = {
    ("determinant", "mech0"): _edge(
        "determinant",
        "participates in (resistance mechanism)",
        "RO:0000056",
        "mech0",
        (
            "CARD classifies MexS under antibiotic efflux because MexS normally "
            "suppresses the MexT activator of the MexEF-OprN pump."
        ),
        (MEXS_EVIDENCE, MEXT_EVIDENCE, MEXEF_OPRN_EVIDENCE),
    ),
    ("mech0", "resistance"): _edge(
        "mech0",
        "causally upstream of",
        "RO:0002411",
        "resistance",
        "The broad efflux mechanism represents elevated MexEF-OprN activity.",
        (MEXS_EVIDENCE, MEXT_EVIDENCE, MEXEF_OPRN_EVIDENCE),
    ),
    ("determinant", "mech1"): _edge(
        "determinant",
        "participates in (mutation mechanism)",
        "RO:0000056",
        "mech1",
        "CARD explicitly describes MexS mutations as causing multidrug resistance.",
        (MEXS_EVIDENCE, MUTATION_EVIDENCE),
    ),
    ("mech1", "resistance"): _edge(
        "mech1",
        "causally upstream of",
        "RO:0002411",
        "resistance",
        "The inherited mutation mechanism links MexS variants to resistance.",
        (MEXS_EVIDENCE, MUTATION_EVIDENCE),
    ),
    ("determinant", "resistance"): _edge(
        "determinant",
        "causally upstream of (confers resistance)",
        "RO:0002411",
        "resistance",
        (
            "MexS mutations derepress MexT, increasing MexEF-OprN pump expression "
            "and driving efflux-mediated resistance."
        ),
        (MEXS_EVIDENCE, MEXT_EVIDENCE, MEXEF_OPRN_EVIDENCE),
    ),
    ("determinant", "suppression"): _edge(
        "determinant",
        "negatively regulates (loss lifts suppression)",
        "RO:0002212",
        "suppression",
        (
            "Resistance-associated MexS mutations are represented as loss of normal "
            "MexT suppression."
        ),
        (MEXS_EVIDENCE, GO_NEGATIVE_MOLECULAR_FUNCTION_EVIDENCE),
    ),
    ("suppression", "activator"): _edge(
        "suppression",
        "negatively regulates (suppresses MexT)",
        "RO:0002212",
        "activator",
        "Normal MexS-dependent suppression keeps MexT activity low.",
        (MEXS_EVIDENCE, GO_NEGATIVE_MOLECULAR_FUNCTION_EVIDENCE),
    ),
    ("activator", "activation"): _edge(
        "activator",
        "enables (activates MexEF-OprN expression)",
        "RO:0002327",
        "activation",
        "MexT participates in positive regulation of MexEF-OprN expression.",
        (MEXT_EVIDENCE, GO_POSITIVE_TRANSCRIPTION_EVIDENCE),
    ),
    ("activation", "pump"): _edge(
        "activation",
        "positively regulates (raises MexEF-OprN expression)",
        "RO:0002213",
        "pump",
        "MexT-mediated transcriptional activation raises MexEF-OprN expression.",
        (MEXT_EVIDENCE, GO_POSITIVE_TRANSCRIPTION_EVIDENCE, MEXEF_OPRN_EVIDENCE),
    ),
    ("pump", "mech0"): _edge(
        "pump",
        "enables (drug efflux)",
        "RO:0002327",
        "mech0",
        "MexEF-OprN is the efflux pump whose activated expression supplies antibiotic efflux.",
        (MEXS_EVIDENCE, MEXT_EVIDENCE, MEXEF_OPRN_EVIDENCE),
    ),
}

EDGE_ORDER = tuple(EDGE_UPDATES)
EXPECTED_EDGES = frozenset(EDGE_UPDATES)
EXPECTED_FULL_EDGES = frozenset(
    (edge["subject"], edge["predicate_id"], edge["object"])
    for edge in EDGE_UPDATES.values()
)
LEGACY_DIRECT_ACTIVATOR_FULL_EDGES = frozenset(
    {
        ("determinant", "RO:0000056", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "RO:0002327", "activation"),
        ("activation", "RO:0002213", "pump"),
    }
)
ALLOWED_FULL_EDGES = EXPECTED_FULL_EDGES | LEGACY_DIRECT_ACTIVATOR_FULL_EDGES


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


def _required_full_edges(full_edges: set[tuple[str, str, str]]) -> frozenset[tuple[str, str, str]]:
    if ("determinant", "RO:0002327", "activation") in full_edges:
        return LEGACY_DIRECT_ACTIVATOR_FULL_EDGES
    return EXPECTED_FULL_EDGES


def _enrich_nodes(graph: dict[str, Any]) -> None:
    nodes = graph.get("nodes") or []
    by_id = {node.get("node_id"): node for node in nodes if isinstance(node, dict)}
    if "determinant" not in by_id:
        raise ValueError(f"{TARGET_IDENTIFIER}: missing node(s): determinant")

    graph["nodes"] = [
        copy.deepcopy(by_id["determinant"])
        if node_id == "determinant"
        else copy.deepcopy(SHARED_NODE_UPDATES[node_id])
        for node_id in NODE_ORDER
    ]


def _validate_edges(graph: dict[str, Any]) -> None:
    seen: set[tuple[str, str]] = set()
    full_edges: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        full_key = _full_edge_key(edge)
        full_edges.add(full_key)
        if full_key not in ALLOWED_FULL_EDGES:
            msg = f"{TARGET_IDENTIFIER}: unexpected edge {full_key[0]} -> {full_key[2]}"
            raise ValueError(msg)
        if full_key == ("determinant", "RO:0002327", "activation"):
            continue

        key = _edge_key(edge)
        if key in seen:
            msg = f"{TARGET_IDENTIFIER}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        seen.add(key)

    missing_edges = sorted(_required_full_edges(full_edges) - full_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_edges)
        raise ValueError(f"{TARGET_IDENTIFIER}: missing edge(s): {missing}")


def _enrich_edges(graph: dict[str, Any]) -> None:
    _validate_edges(graph)
    graph["edges"] = [
        _ordered_edge(copy.deepcopy(EDGE_UPDATES[key])) for key in EDGE_ORDER
    ]


def enrich_record(record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != TARGET_IDENTIFIER:
        msg = f"expected {TARGET_IDENTIFIER}, found {record.get('identifier')}"
        raise ValueError(msg)

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        raise ValueError(f"{TARGET_IDENTIFIER}: missing resistance causal graph")

    graph["description"] = (
        "Curated resistance-causation graph for MexS loss derepressing MexT and "
        "activating MexEF-OprN efflux. The graph replaces the stale AdeR direct-"
        "activation scaffold with exact MexS, MexT, and MexEF-OprN evidence."
    )
    _enrich_nodes(graph)
    _enrich_edges(graph)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    if record.get("identifier") != TARGET_IDENTIFIER:
        msg = f"{path}: not the MexS target: {record.get('identifier')}"
        raise ValueError(msg)
    if path.name != TARGET_FILENAME:
        msg = f"{path}: target {TARGET_IDENTIFIER} must be in {TARGET_FILENAME}"
        raise ValueError(msg)

    enriched, changed = enrich_record(record)
    normalize_aliases = "&id" in text or "*id" in text
    if not changed and not normalize_aliases:
        return text, False

    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
        out = append_to_section(out, "curation_history", _dump({"curation_history": [HISTORY_EVENT]}))
    return out, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR / TARGET_FILENAME,
        help=f"MexS YAML file to rewrite; default: {TARGET_FILENAME}",
    )
    args = parser.parse_args()

    if not args.path.exists():
        print(f"PROBLEM: {args.path}: missing", file=sys.stderr)
        return 1

    try:
        text = args.path.read_text(encoding="utf-8")
        out, did_change = enrich_text(text, args.path)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"PROBLEM: {exc}", file=sys.stderr)
        return 1

    if did_change:
        print(f"{'wrote' if args.apply else 'would write'} {args.path.name}")
        if args.apply:
            args.path.write_text(out, encoding="utf-8")
    else:
        print(f"already enriched: {args.path.name}")

    if not args.apply:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
