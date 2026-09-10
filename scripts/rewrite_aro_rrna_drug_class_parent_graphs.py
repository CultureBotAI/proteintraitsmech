#!/usr/bin/env python3
"""Rewrite 16S/23S rRNA drug-class mutation parent graphs.

These records sit below the broad 16S or 23S rRNA mutation parents and add a
single CARD drug-class edge.  They are still parent classes, not specific
species or nucleotide changes, so the graph keeps the mutated rRNA binding site
generic while preserving the direct drug-class assertion.

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

HISTORY_ACTION = "Completed 16S/23S rRNA drug-class mutation parent graphs"
HISTORY_EVENT = {
    "timestamp": "2026-09-09T00:00:00Z",
    "curator": "codex-causal-graph-quality",
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that "
        "may result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

RRNA_MUTATION_PARENT_EVIDENCE = {
    "reference": "ARO:3000328",
    "snippet": (
        "Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic "
        "resistance to drugs that target the bacterial ribosome."
    ),
    "notes": "CARD definition for the rRNA mutation parent term.",
}

SIXTEEN_S_PARENT_EVIDENCE = {
    "reference": "ARO:3003211",
    "snippet": (
        "Point mutations in the bacterial 16S ribosomal RNA in the small 30S "
        "subunit can confer resistance to antibiotics."
    ),
    "notes": "CARD definition for the 16S rRNA mutation term.",
}

SIXTEEN_S_BINDING_EVIDENCE = {
    "reference": "ARO:3003211",
    "snippet": (
        "The antibiotic-binding sites are located within functionally important "
        "structures in the ribosomal RNA. Antibiotic resistance is often "
        "conferred by base substitutions or methylations at these sites in "
        "the rRNA."
    ),
    "notes": "CARD support for 16S rRNA binding-site alteration.",
}

TWENTY_THREE_S_PARENT_EVIDENCE = {
    "reference": "ARO:3000336",
    "snippet": (
        "Point mutations in bacterial 23S rRNA from the large ribosomal "
        "subunit that confer resistance to antibiotics."
    ),
    "notes": "CARD definition for the 23S rRNA mutation term.",
}

TWENTY_THREE_S_BINDING_EVIDENCE = {
    "reference": "ARO:3000336",
    "snippet": (
        "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity "
        "at specific sites, conferring resistance."
    ),
    "notes": "CARD support for 23S rRNA binding-site alteration.",
}

RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide both "
        "structural scaffolding and catalytic activity."
    ),
    "notes": "Sequence Ontology definition for the broad rRNA superclass.",
}

GO_30S_EVIDENCE = {
    "reference": "GO:0015935",
    "snippet": "small ribosomal subunit",
    "notes": "GO grounding for the small ribosomal subunit.",
}

GO_50S_EVIDENCE = {
    "reference": "GO:0015934",
    "snippet": "large ribosomal subunit",
    "notes": "GO grounding for the large ribosomal subunit.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "mutation conferring antibiotic resistance",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:3000212",
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

DRUG_ID = re.compile(r"^drug\d+$")


@dataclass(frozen=True)
class GraphKind:
    binding_site_label: str
    subunit: dict[str, str]
    parent_evidence: dict[str, str]
    binding_evidence: dict[str, str]
    subunit_evidence: dict[str, str]


@dataclass(frozen=True)
class Target:
    identifier: str
    filename: str
    kind: GraphKind


SIXTEEN_S = GraphKind(
    binding_site_label="16S rRNA antibiotic-binding site",
    subunit={
        "node_id": "subunit",
        "label": "small ribosomal subunit (30S)",
        "node_type": "CELLULAR_LOCALIZATION",
        "grounding": "GO:0015935",
        "description": "The 30S subunit that contains bacterial 16S rRNA.",
    },
    parent_evidence=SIXTEEN_S_PARENT_EVIDENCE,
    binding_evidence=SIXTEEN_S_BINDING_EVIDENCE,
    subunit_evidence=GO_30S_EVIDENCE,
)

TWENTY_THREE_S = GraphKind(
    binding_site_label="23S rRNA antibiotic-binding site",
    subunit={
        "node_id": "subunit",
        "label": "large ribosomal subunit (50S)",
        "node_type": "CELLULAR_LOCALIZATION",
        "grounding": "GO:0015934",
        "description": "The 50S subunit that contains bacterial 23S rRNA.",
    },
    parent_evidence=TWENTY_THREE_S_PARENT_EVIDENCE,
    binding_evidence=TWENTY_THREE_S_BINDING_EVIDENCE,
    subunit_evidence=GO_50S_EVIDENCE,
)


TARGETS: tuple[Target, ...] = (
    Target(
        "ARO:3003666",
        "16s-rrna-with-mutation-conferring-resistance-to-aminoglycoside-antibiotics-"
        "aro3003666.yaml",
        SIXTEEN_S,
    ),
    Target(
        "ARO:3003976",
        "16s-rrna-with-mutation-conferring-resistance-to-pactamycin-aro3003976.yaml",
        SIXTEEN_S,
    ),
    Target(
        "ARO:3003667",
        "16s-rrna-with-mutation-conferring-resistance-to-peptide-antibiotics-"
        "aro3003667.yaml",
        SIXTEEN_S,
    ),
    Target(
        "ARO:3003668",
        "16s-rrna-with-mutation-conferring-resistance-to-polyamine-antibiotics-"
        "aro3003668.yaml",
        SIXTEEN_S,
    ),
    Target(
        "ARO:3003669",
        "16s-rrna-with-mutation-conferring-resistance-to-tetracycline-derivatives-"
        "aro3003669.yaml",
        SIXTEEN_S,
    ),
    Target(
        "ARO:3004936",
        "23s-rrna-with-mutation-conferring-resistance-to-aminoglycoside-antibiotics-"
        "aro3004936.yaml",
        TWENTY_THREE_S,
    ),
    Target(
        "ARO:3004187",
        "23s-rrna-with-mutation-conferring-resistance-to-lincosamide-antibiotics-"
        "aro3004187.yaml",
        TWENTY_THREE_S,
    ),
    Target(
        "ARO:3004172",
        "23s-rrna-with-mutation-conferring-resistance-to-oxazolidinone-antibiotics-"
        "aro3004172.yaml",
        TWENTY_THREE_S,
    ),
    Target(
        "ARO:3004188",
        "23s-rrna-with-mutation-conferring-resistance-to-phenicol-antibiotics-"
        "aro3004188.yaml",
        TWENTY_THREE_S,
    ),
    Target(
        "ARO:3004178",
        "23s-rrna-with-mutation-conferring-resistance-to-pleuromutilin-antibiotics-"
        "aro3004178.yaml",
        TWENTY_THREE_S,
    ),
    Target(
        "ARO:3004182",
        "23s-rrna-with-mutation-conferring-resistance-to-streptogramins-antibiotics-"
        "aro3004182.yaml",
        TWENTY_THREE_S,
    ),
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


def _is_drug_node_id(node_id: str) -> bool:
    return DRUG_ID.fullmatch(node_id) is not None


def _unique_evidence(*items: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (str(item["reference"]), str(item.get("snippet", "")))
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


def _record_evidence(record: dict[str, Any]) -> dict[str, str]:
    return {
        "reference": str(record["identifier"]),
        "snippet": str(record["definition"]),
        "notes": f"CARD definition for {record['label']}.",
    }


def _drug_node(graph: dict[str, Any], target: Target) -> dict[str, Any]:
    drug_nodes = [
        node
        for node in _dicts(graph.get("nodes"))
        if _is_drug_node_id(str(node.get("node_id", "")))
    ]
    if len(drug_nodes) != 1:
        raise ValueError(f"{target.identifier}: expected exactly one drug node")
    return copy.deepcopy(drug_nodes[0])


def _drug_relation_evidence(
    graph: dict[str, Any],
    drug_node: dict[str, Any],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for edge in _dicts(graph.get("edges")):
        if (
            edge.get("subject") == "determinant"
            and edge.get("predicate_id") == "ARO:2000001"
            and edge.get("object") == drug_node["node_id"]
        ):
            evidence.extend(
                item
                for item in _dicts(edge.get("evidence"))
                if str(item.get("snippet", "")).startswith(
                    "relationship: confers_resistance_to_drug_class "
                )
            )

    if not evidence:
        raise ValueError(f"missing direct drug-class evidence for {drug_node['node_id']}")
    return evidence


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "NUCLEIC_ACID",
        "grounding": str(record["identifier"]),
    }


def _binding_site_node(target: Target) -> dict[str, str]:
    return {
        "node_id": "binding_site",
        "label": target.kind.binding_site_label,
        "node_type": "NUCLEIC_ACID",
        "grounding": "SO:0000252",
        "description": (
            "Grounded to the broad Sequence Ontology rRNA term because no stable "
            "narrow term is available for a generic rRNA antibiotic-binding site."
        ),
    }


def _graph(record: dict[str, Any], old_graph: dict[str, Any], target: Target) -> dict[str, Any]:
    record_evidence = _record_evidence(record)
    drug_node = _drug_node(old_graph, target)
    relation_evidence = _drug_relation_evidence(old_graph, drug_node)
    mechanism_evidence = (
        record_evidence,
        target.kind.parent_evidence,
        RRNA_MUTATION_PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
    )
    site_evidence = (
        record_evidence,
        target.kind.binding_evidence,
        RRNA_MUTATION_PARENT_EVIDENCE,
        RRNA_EVIDENCE,
    )
    drug_evidence = (
        *relation_evidence,
        record_evidence,
        target.kind.binding_evidence,
        RRNA_MUTATION_PARENT_EVIDENCE,
        RRNA_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → rRNA antibiotic-binding-site alteration",
        "description": (
            "Curated resistance-causation graph for point mutations in a "
            "bacterial rRNA that alter a drug-class-linked ribosomal "
            "antibiotic-binding site."
        ),
        "nodes": [
            _determinant_node(record),
            copy.deepcopy(MECHANISM_NODE),
            drug_node,
            _binding_site_node(target),
            copy.deepcopy(target.kind.subunit),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this rRNA variant under mutation conferring "
                "antibiotic resistance.",
                *mechanism_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The inherited mutation mechanism captures rRNA sequence changes "
                "that alter ribosomal antibiotic-binding sites.",
                *mechanism_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The mutated rRNA determinant alters a ribosomal "
                "antibiotic-binding site and thereby confers resistance.",
                *mechanism_evidence,
                *relation_evidence,
            ),
            _edge(
                "determinant",
                "confers resistance to (drug class)",
                "ARO:2000001",
                str(drug_node["node_id"]),
                f"CARD asserts that this rRNA mutation class confers resistance to {drug_node['label']}.",
                *drug_evidence,
            ),
            _edge(
                "binding_site",
                "part of",
                "BFO:0000050",
                "determinant",
                "The antibiotic-binding site is modeled inside the mutated rRNA.",
                *site_evidence,
            ),
            _edge(
                "determinant",
                "part of",
                "BFO:0000050",
                "subunit",
                "The mutated rRNA is part of its bacterial ribosomal subunit.",
                record_evidence,
                target.kind.parent_evidence,
                target.kind.subunit_evidence,
                RRNA_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (alters antibiotic-binding site)",
                "RO:0002411",
                "binding_site",
                "Point mutations in the rRNA alter the local antibiotic-binding "
                "site that is linked to this drug class.",
                *site_evidence,
                *relation_evidence,
            ),
            _edge(
                str(drug_node["node_id"]),
                "molecularly interacts with",
                "RO:0002436",
                "binding_site",
                "CARD links this drug class to resistance-conferring rRNA "
                "binding-site mutations.",
                *drug_evidence,
            ),
            _edge(
                "binding_site",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Alteration of the rRNA antibiotic-binding site lowers effective "
                "drug binding and causes resistance.",
                *site_evidence,
                *relation_evidence,
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
    out["causal_graphs"] = [_graph(record, graphs[0], target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an rRNA drug-class parent target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
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
    return [path / target.filename for target in TARGETS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument(
        "--path",
        type=Path,
        default=ARO_DIR,
        help="ARO directory or one of the 11 16S/23S rRNA drug-class parent YAML files",
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
