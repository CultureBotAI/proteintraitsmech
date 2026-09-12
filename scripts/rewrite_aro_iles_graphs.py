#!/usr/bin/env python3
"""Ground mupirocin-resistance isoleucyl-tRNA synthetase graphs.

The ARO ileS/mupirocin records model inhibition of isoleucyl-tRNA synthetase,
but leave the synthetase activity and downstream protein synthesis process
ungrounded. This updater grounds those nodes to GO:0004822 and GO:0006412,
describes every edge, changes the old activity-to-translation ``part_of`` edge
to a causal edge, and keeps the exact five-record branch idempotent.

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
HISTORY_ACTION = "Grounded mupirocin-resistance IleRS graphs"
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
        "targets with lower binding affinities and the deactivation of "
        "repressors that result in increased expression of genes that inactivate "
        "or pump out antibiotics."
    ),
    "notes": "CARD definition for the broad mutation-conferring resistance mechanism.",
}

TARGET_REPLACEMENT_EVIDENCE = {
    "reference": "ARO:3000381",
    "snippet": (
        "Alternate proteins that have the same functions as other antibiotic "
        "target proteins, but are structurally different and thus resistant to "
        "antibiotics. These can replace the activity of other "
        "antibiotic-sensitive proteins in the presence of antibiotics."
    ),
    "notes": "CARD definition for antibiotic target replacement proteins.",
}

ILES_PARENT_EVIDENCE = {
    "reference": "ARO:3000446",
    "snippet": (
        "Mupirocin inhibits protein synthesis by interfering with isoleucyl-tRNA "
        "synthetase (ileS). Mutations in ileS can confer low-level mupirocin "
        "resistance."
    ),
    "notes": "CARD definition for antibiotic-resistant isoleucyl-tRNA synthetase.",
}

GO_ILES_EVIDENCE = {
    "reference": "GO:0004822",
    "snippet": (
        "Catalysis of the reaction: ATP + L-isoleucine + tRNA(Ile) = "
        "AMP + diphosphate + L-isoleucyl-tRNA(Ile)."
    ),
    "notes": "GO definition for isoleucine-tRNA ligase activity.",
}

GO_TRANSLATION_EVIDENCE = {
    "reference": "GO:0006412",
    "snippet": (
        "The cellular metabolic process in which a protein is formed, using the "
        "sequence of a mature mRNA molecule to specify the sequence of amino "
        "acids in a polypeptide chain."
    ),
    "notes": "GO definition for translation.",
}

DRUG_NODE = {
    "node_id": "drug0",
    "label": "mupirocin-like antibiotic",
    "node_type": "CHEMICAL",
    "grounding": "ARO:3007151",
}

AMINOACYLATION_NODE = {
    "node_id": "aminoacylation",
    "label": "isoleucine-tRNA ligase activity",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "GO:0004822",
}

PROTEIN_SYNTHESIS_NODE = {
    "node_id": "protein_synthesis",
    "label": "translation",
    "node_type": "BIOLOGICAL_PROCESS",
    "grounding": "GO:0006412",
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

LEGACY_TRANSLATION_EDGE_KEY = (
    "aminoacylation",
    "BFO:0000050",
    "protein_synthesis",
)

CANONICAL_TRANSLATION_EDGE_KEY = (
    "aminoacylation",
    "RO:0002411",
    "protein_synthesis",
)

CORE_EDGE_KEYS = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "ARO:2000001", "drug0"),
    ("determinant", "RO:0002327", "aminoacylation"),
    ("drug0", "RO:0002212", "aminoacylation"),
}


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    replacement: bool = False

    @property
    def mechanism_grounding(self) -> str:
        return "ARO:0001002" if self.replacement else "ARO:3000212"

    @property
    def mechanism_label(self) -> str:
        if self.replacement:
            return "antibiotic target replacement"
        return "mutation conferring antibiotic resistance"

    @property
    def mechanism_evidence(self) -> dict[str, str]:
        return TARGET_REPLACEMENT_EVIDENCE if self.replacement else MUTATION_EVIDENCE


TARGETS = {
    "ARO:3000446": Target(
        identifier="ARO:3000446",
        filename="antibiotic-resistant-isoleucyl-trna-synthetase-iles-aro3000446.yaml",
    ),
    "ARO:3003730": Target(
        identifier="ARO:3003730",
        filename="bifidobacterium-bifidum-iles-conferring-resistance-to-mupirocin-aro3003730.yaml",
    ),
    "ARO:3003729": Target(
        identifier="ARO:3003729",
        filename=(
            "staphylococcus-aureus-iles-with-mutation-conferring-resistance-to-"
            "mupirocin-aro3003729.yaml"
        ),
    ),
    "ARO:3000521": Target(
        identifier="ARO:3000521",
        filename="staphylococcus-aureus-mupa-conferring-resistance-to-mupirocin-aro3000521.yaml",
        replacement=True,
    ),
    "ARO:3000510": Target(
        identifier="ARO:3000510",
        filename="staphylococcus-aureus-mupb-conferring-resistance-to-mupirocin-aro3000510.yaml",
        replacement=True,
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


def _canonical_edge_keys() -> set[tuple[str, str, str]]:
    return CORE_EDGE_KEYS | {CANONICAL_TRANSLATION_EDGE_KEY}


def _input_allowed_edges() -> set[tuple[str, str, str]]:
    return _canonical_edge_keys() | {LEGACY_TRANSLATION_EDGE_KEY}


def _target_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_evidence() -> dict[str, str]:
    return {
        "reference": "ARO:3000446",
        "snippet": (
            "relationship: confers_resistance_to_drug_class ARO:3007151 ! "
            "mupirocin-like antibiotic"
        ),
        "notes": (
            "ARO drug-class relationship on ARO:3000446; modeled here as a "
            "determinant-to-mupirocin-like-antibiotic edge and inherited by "
            "the ileS/mupA/mupB leaf records."
        ),
    }


def _source_evidence(record: dict[str, Any]) -> tuple[dict[str, str], ...]:
    out = []
    for item in record.get("evidence") or []:
        if not isinstance(item, dict) or not item.get("reference"):
            continue
        out.append(
            {
                "reference": str(item["reference"]),
                "notes": str(item.get("notes") or "ARO citation for this record."),
            }
        )
    return tuple(out)


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


def _validate_graph(graph: dict[str, Any], target: Target) -> None:
    nodes = _nodes_by_id(graph)
    missing_nodes = sorted(
        {
            "determinant",
            "mech0",
            "drug0",
            "aminoacylation",
            "protein_synthesis",
            "resistance",
        }
        - set(nodes)
    )
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")

    found_edges = set()
    seen: set[tuple[str, str, str]] = set()
    for edge in graph.get("edges") or []:
        key = _edge_key(edge)
        if key not in _input_allowed_edges():
            raise ValueError(f"{target.identifier}: unexpected edge {key[0]} -> {key[2]}")
        if key in seen:
            raise ValueError(f"{target.identifier}: duplicate edge {key[0]} -> {key[2]}")
        seen.add(key)
        found_edges.add(key)

    missing_core = sorted(CORE_EDGE_KEYS - found_edges)
    if missing_core:
        missing = ", ".join(f"{subject} -> {object_}" for subject, _, object_ in missing_core)
        raise ValueError(f"{target.identifier}: missing core edge(s): {missing}")

    has_legacy_edge = LEGACY_TRANSLATION_EDGE_KEY in found_edges
    has_canonical_edge = CANONICAL_TRANSLATION_EDGE_KEY in found_edges
    if not has_legacy_edge and not has_canonical_edge:
        raise ValueError(
            f"{target.identifier}: missing aminoacylation-to-translation edge"
        )


def _mechanism_node(target: Target) -> dict[str, str]:
    return {
        "node_id": "mech0",
        "label": target.mechanism_label,
        "node_type": "MOLECULAR_FUNCTION",
        "grounding": target.mechanism_grounding,
    }


def _canonical_nodes(graph: dict[str, Any], target: Target) -> list[dict[str, Any]]:
    nodes = _nodes_by_id(graph)
    return [
        copy.deepcopy(nodes["determinant"]),
        _mechanism_node(target),
        copy.deepcopy(DRUG_NODE),
        copy.deepcopy(AMINOACYLATION_NODE),
        copy.deepcopy(PROTEIN_SYNTHESIS_NODE),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _canonical_edges(
    record: dict[str, Any],
    target: Target,
) -> list[dict[str, Any]]:
    target_evidence = _target_evidence(record)
    source_evidence = _source_evidence(record)
    mechanism_evidence = (
        target_evidence,
        ILES_PARENT_EVIDENCE,
        target.mechanism_evidence,
        *source_evidence,
    )
    function_evidence = (
        target_evidence,
        ILES_PARENT_EVIDENCE,
        GO_ILES_EVIDENCE,
        *source_evidence,
    )
    translation_evidence = (
        ILES_PARENT_EVIDENCE,
        GO_ILES_EVIDENCE,
        GO_TRANSLATION_EVIDENCE,
        *source_evidence,
    )
    drug_evidence = (
        target_evidence,
        ILES_PARENT_EVIDENCE,
        _drug_evidence(),
        *source_evidence,
    )

    return [
        _edge(
            "determinant",
            "participates in (resistance mechanism)",
            "RO:0000056",
            "mech0",
            (
                "The determinant is modeled with the resistance mechanism "
                "supported by its ARO definition: mutation for ileS variants "
                "and target replacement for alternate Mup enzymes."
            ),
            mechanism_evidence,
        ),
        _edge(
            "mech0",
            "causally upstream of",
            "RO:0002411",
            "resistance",
            (
                "The modeled mechanism keeps isoleucyl-tRNA synthetase function "
                "available under mupirocin pressure."
            ),
            mechanism_evidence,
        ),
        _edge(
            "determinant",
            "causally upstream of (confers resistance)",
            "RO:0002411",
            "resistance",
            (
                "Mupirocin resistance is caused by an isoleucyl-tRNA synthetase "
                "that remains active when mupirocin targets this activity."
            ),
            mechanism_evidence,
        ),
        _edge(
            "determinant",
            "confers resistance to (drug class)",
            "ARO:2000001",
            "drug0",
            (
                "ARO links the antibiotic-resistant isoleucyl-tRNA synthetase "
                "parent to mupirocin-like antibiotics."
            ),
            drug_evidence,
        ),
        _edge(
            "determinant",
            "enables",
            "RO:0002327",
            "aminoacylation",
            (
                "The determinant is an isoleucyl-tRNA synthetase and catalyzes "
                "isoleucine charging of tRNA(Ile)."
            ),
            function_evidence,
        ),
        _edge(
            "drug0",
            "negatively regulates",
            "RO:0002212",
            "aminoacylation",
            (
                "Mupirocin-like antibiotics inhibit protein synthesis by "
                "interfering with isoleucyl-tRNA synthetase activity."
            ),
            function_evidence,
        ),
        _edge(
            "aminoacylation",
            "causally upstream of (charges tRNA for translation)",
            "RO:0002411",
            "protein_synthesis",
            (
                "Isoleucine-tRNA ligase activity supplies charged tRNA(Ile) "
                "needed by translation."
            ),
            translation_evidence,
        ),
    ]


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    if record.get("identifier") != target.identifier:
        raise ValueError(f"expected {target.identifier}, found {record.get('identifier')}")

    out = copy.deepcopy(record)
    before = copy.deepcopy(out.get("causal_graphs"))
    graphs = out.get("causal_graphs") or []
    graph = next((item for item in graphs if item.get("graph_id") == "resistance"), None)
    if graph is None:
        raise ValueError(f"{target.identifier}: missing resistance causal graph")

    _validate_graph(graph, target)
    graph["title"] = f"{record['label']} → isoleucyl-tRNA ligase → mupirocin resistance"
    graph["description"] = (
        "Conservative graph for mupirocin resistance through altered or "
        "alternative isoleucyl-tRNA synthetase activity. The graph grounds the "
        "synthetase activity to GO:0004822, grounds downstream translation to "
        "GO:0006412, and models aminoacylation as causally upstream of "
        "translation rather than part of translation."
    )
    graph["nodes"] = _canonical_nodes(graph, target)
    graph["edges"] = _canonical_edges(out, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an ileS/mupirocin target: {identifier}")
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
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the five target YAML files",
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
