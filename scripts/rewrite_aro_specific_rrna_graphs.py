#!/usr/bin/env python3
"""Rewrite specific 16S/23S rRNA ARO graphs to complete local causal chains.

The three records handled here sit directly below broader rRNA mutation and
rRNA methyltransferase parents.  This updater keeps their graphs specific to
16S or 23S rRNA while replacing weak or over-specific nodes with local states:

* 16S/23S mutation records:
    mutated rRNA → altered binding-site state → reduced antibiotic binding
* the generic 23S methyltransferase record:
    23S rRNA methyltransferase → methylated 23S rRNA site

Dry-run by default; pass ``--apply`` to write.
"""

from __future__ import annotations

import argparse
import copy
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from record_io import append_to_section, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ARO_DIR = ROOT / "data" / "traits" / "function" / "resistance" / "aro"

HISTORY_ACTION = "Rewrote specific 16S/23S rRNA mutation and methyltransferase graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_TARGET_ALTERATION_EVIDENCE = {
    "reference": "ARO:0001001",
    "snippet": (
        "Mutational alteration or enzymatic modification of antibiotic target "
        "which results in antibiotic resistance."
    ),
    "notes": "CARD definition for antibiotic target alteration.",
}

MUTATION_EVIDENCE = {
    "reference": "ARO:3000212",
    "snippet": (
        "Point mutations in the DNA may lead to an altered gene product that may "
        "result in antibiotic resistance."
    ),
    "notes": "CARD definition for mutation conferring antibiotic resistance.",
}

RIBOSOMAL_ALTERATION_EVIDENCE = {
    "reference": "ARO:3000211",
    "snippet": (
        "Chemical alteration of the ribosome results in modification of an "
        "antibiotic's target leading to resistance."
    ),
    "notes": "CARD definition for ribosomal alteration conferring antibiotic resistance.",
}

RRNA_METHYLTRANSFERASE_PARENT_EVIDENCE = {
    "reference": "ARO:3000164",
    "snippet": "Catalyzes methylation of rRNA.",
    "notes": "CARD definition for the rRNA methyltransferase parent term.",
}

RRNA_METHYLTRANSFERASE_EVIDENCE = {
    "reference": "GO:0008649",
    "snippet": (
        "Catalysis of the transfer of a methyl group from S-adenosyl-L-methionine "
        "to a nucleoside residue in an rRNA molecule. The methyl group can be "
        "transfered to the nucleobase or to the ribose group of the nucleoside."
    ),
    "notes": "GO definition for broad rRNA methyltransferase activity.",
}

RRNA_MUTATION_PARENT_EVIDENCE = {
    "reference": "ARO:3000328",
    "snippet": (
        "Single nucleotide polymorphisms (SNPs) in rRNA can confer antibiotic "
        "resistance to drugs that target the bacterial ribosome."
    ),
    "notes": "CARD definition for the rRNA mutation parent term.",
}

RRNA_EVIDENCE = {
    "reference": "SO:0000252",
    "snippet": (
        "rRNA is an RNA component of a ribosome that can provide both structural "
        "scaffolding and catalytic activity."
    ),
    "notes": (
        "Sequence Ontology definition for the broad rRNA superclass used as a "
        "conservative grounding for local 16S/23S rRNA antibiotic-binding sites."
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


@dataclass(frozen=True)
class MutationTarget:
    identifier: str
    filename: str
    binding_site_label: str
    altered_site_label: str
    determinant_evidence: dict[str, str]
    subunit_node: dict[str, str]


@dataclass(frozen=True)
class MethyltransferaseTarget:
    identifier: str
    filename: str
    determinant_evidence: dict[str, str]


Target = MutationTarget | MethyltransferaseTarget

SIXTEEN_S = MutationTarget(
    identifier="ARO:3003211",
    filename="16s-rrna-with-mutation-conferring-antibiotic-resistance-aro3003211.yaml",
    binding_site_label="16S rRNA antibiotic-binding site",
    altered_site_label="altered 16S rRNA antibiotic-binding site",
    determinant_evidence={
        "reference": "ARO:3003211",
        "snippet": (
            "Point mutations in the bacterial 16S ribosomal RNA in the small 30S "
            "subunit can confer resistance to antibiotics."
        ),
        "notes": "CARD definition for the 16S rRNA mutation term.",
    },
    subunit_node={
        "node_id": "subunit",
        "label": "small ribosomal subunit (30S)",
        "node_type": "CELLULAR_LOCALIZATION",
        "grounding": "GO:0015935",
        "description": "The 30S subunit that contains bacterial 16S rRNA.",
    },
)

TWENTY_THREE_S_MUTATION = MutationTarget(
    identifier="ARO:3000336",
    filename="23s-rrna-with-mutation-conferring-antibiotic-resistance-aro3000336.yaml",
    binding_site_label="23S rRNA antibiotic-binding site",
    altered_site_label="reduced antibiotic binding affinity at the mutated 23S site",
    determinant_evidence={
        "reference": "ARO:3000336",
        "snippet": (
            "Mutations in the 23S rRNA subunit reduce antibiotic binding affinity "
            "at specific sites, conferring resistance."
        ),
        "notes": "CARD definition for the 23S rRNA mutation term.",
    },
    subunit_node={
        "node_id": "subunit",
        "label": "large ribosomal subunit (50S)",
        "node_type": "CELLULAR_LOCALIZATION",
        "grounding": "GO:0015934",
        "description": "The 50S subunit that contains bacterial 23S rRNA.",
    },
)

TWENTY_THREE_S_METHYLTRANSFERASE = MethyltransferaseTarget(
    identifier="ARO:3004274",
    filename="23s-ribosomal-rna-methyltransferase-aro3004274.yaml",
    determinant_evidence={
        "reference": "ARO:3004274",
        "snippet": (
            "Methyltransferases that modify the 23S rRNA of the 50S subunit of "
            "bacterial ribosomes, conferring resistance to drugs that target 23S "
            "rRNA."
        ),
        "notes": "CARD definition for the 23S ribosomal RNA methyltransferase term.",
    },
)

TARGETS: tuple[Target, ...] = (
    SIXTEEN_S,
    TWENTY_THREE_S_METHYLTRANSFERASE,
    TWENTY_THREE_S_MUTATION,
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


def _unique_evidence(*items: dict[str, str]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        reference = item["reference"]
        if reference in seen:
            continue
        seen.add(reference)
        evidence.append(copy.deepcopy(item))
    return evidence


def _edge(
    subject: str,
    predicate: str,
    predicate_id: str,
    object_: str,
    description: str,
    *evidence: dict[str, str],
) -> dict[str, Any]:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "description": description,
        "evidence": _unique_evidence(*evidence),
    }


def _determinant_node(record: dict[str, Any], node_type: str) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": node_type,
        "grounding": str(record["identifier"]),
    }


def _binding_site_node(target: MutationTarget) -> dict[str, str]:
    return {
        "node_id": "binding_site",
        "label": target.binding_site_label,
        "node_type": "NUCLEIC_ACID",
        "grounding": "SO:0000252",
        "description": (
            "Grounded to the broad Sequence Ontology rRNA term because no stable "
            "narrow term is available for the local 16S/23S rRNA "
            "antibiotic-binding site modeled here."
        ),
    }


def _altered_site_node(target: MutationTarget) -> dict[str, str]:
    return {
        "node_id": "altered_site",
        "label": target.altered_site_label,
        "node_type": "STATE",
        "description": (
            "Local state for an altered rRNA antibiotic-binding site produced by "
            "resistance-conferring point mutations."
        ),
    }


def _mutation_graph(record: dict[str, Any], target: MutationTarget) -> dict[str, Any]:
    evidence = (
        target.determinant_evidence,
        RRNA_MUTATION_PARENT_EVIDENCE,
        MUTATION_EVIDENCE,
    )
    site_evidence = (
        target.determinant_evidence,
        RRNA_MUTATION_PARENT_EVIDENCE,
        RRNA_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → altered rRNA binding site → resistance",
        "description": (
            "Curated resistance-causation graph for point mutations in a specific "
            "bacterial rRNA. The graph models mutation of the antibiotic-binding "
            "site as a local state that perturbs drug binding and causes resistance."
        ),
        "nodes": [
            _determinant_node(record, "NUCLEIC_ACID"),
            {
                "node_id": "mech0",
                "label": "mutation conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000212",
            },
            _binding_site_node(target),
            _altered_site_node(target),
            copy.deepcopy(target.subunit_node),
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
                *evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "The inherited mutation mechanism captures rRNA sequence changes "
                "that alter ribosomal antibiotic-binding sites.",
                *evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The mutated rRNA determinant alters antibiotic-binding sites in "
                "the ribosome and thereby confers resistance.",
                *evidence,
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
                target.determinant_evidence,
                RRNA_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (alters antibiotic-binding site)",
                "RO:0002411",
                "altered_site",
                "Point mutations in the rRNA produce an altered local "
                "antibiotic-binding-site state.",
                *site_evidence,
            ),
            _edge(
                "altered_site",
                "negatively regulates (reduces antibiotic binding)",
                "RO:0002212",
                "binding_site",
                "The altered rRNA site reduces antibiotic binding at the site.",
                *site_evidence,
            ),
            _edge(
                "altered_site",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Reduced binding at the altered rRNA site is the terminal modeled "
                "cause of resistance.",
                *site_evidence,
            ),
        ],
    }


def _methyltransferase_graph(
    record: dict[str, Any],
    target: MethyltransferaseTarget,
) -> dict[str, Any]:
    evidence = (
        target.determinant_evidence,
        RRNA_METHYLTRANSFERASE_PARENT_EVIDENCE,
        RIBOSOMAL_ALTERATION_EVIDENCE,
    )
    target_alteration_evidence = (
        target.determinant_evidence,
        RRNA_METHYLTRANSFERASE_PARENT_EVIDENCE,
        ANTIBIOTIC_TARGET_ALTERATION_EVIDENCE,
    )
    activity_evidence = (
        target.determinant_evidence,
        RRNA_METHYLTRANSFERASE_PARENT_EVIDENCE,
        RRNA_METHYLTRANSFERASE_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → methylated 23S rRNA binding site → resistance",
        "description": (
            "Curated resistance-causation graph for generic 23S rRNA "
            "methyltransferases. The graph models methylation of a 23S rRNA "
            "antibiotic-binding site without assuming a single nucleotide target "
            "or catalytic-domain architecture."
        ),
        "nodes": [
            _determinant_node(record, "PROTEIN"),
            {
                "node_id": "mech0",
                "label": "antibiotic target alteration",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001001",
            },
            {
                "node_id": "mech1",
                "label": "ribosomal alteration conferring antibiotic resistance",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:3000211",
            },
            {
                "node_id": "methyltransferase",
                "label": "23S rRNA methyltransferase activity",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "GO:0008649",
                "description": (
                    "Grounded to the broad GO rRNA methyltransferase activity "
                    "term because the ARO evidence scopes this local activity to "
                    "23S rRNA."
                ),
            },
            {
                "node_id": "target_site",
                "label": "23S rRNA antibiotic-binding site",
                "node_type": "NUCLEIC_ACID",
                "grounding": "SO:0000252",
                "description": (
                    "Grounded to the broad Sequence Ontology rRNA term because no "
                    "stable narrow term is available for a generic 23S rRNA "
                    "antibiotic-binding site."
                ),
            },
            {
                "node_id": "methylated",
                "label": "methylated 23S rRNA antibiotic-binding site",
                "node_type": "STATE",
                "grounding": "SO:0000252",
                "description": (
                    "Local state representing methylation of an "
                    "antibiotic-binding site in 23S rRNA. Grounded to broad rRNA "
                    "because no stable narrow term is available for a generic "
                    "methylated 23S rRNA antibiotic-binding site."
                ),
            },
            {
                "node_id": "subunit",
                "label": "large ribosomal subunit (50S)",
                "node_type": "CELLULAR_LOCALIZATION",
                "grounding": "GO:0015934",
                "description": "The 50S subunit that contains bacterial 23S rRNA.",
            },
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies 23S rRNA methyltransferases under antibiotic "
                "target alteration because they enzymatically modify the rRNA "
                "target.",
                *target_alteration_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Target alteration is the broad resistance mechanism represented "
                "by 23S rRNA methylation.",
                *target_alteration_evidence,
            ),
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech1",
                "CARD also classifies 23S rRNA methyltransferases under the "
                "ribosome-specific target-alteration mechanism.",
                *evidence,
            ),
            _edge(
                "mech1",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Chemical alteration of the ribosome is the ribosome-specific "
                "route represented by 23S rRNA methylation.",
                *evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "23S rRNA methyltransferases methylate the 23S rRNA target of "
                "ribosome-binding antibiotics.",
                target.determinant_evidence,
                RRNA_METHYLTRANSFERASE_PARENT_EVIDENCE,
                ANTIBIOTIC_TARGET_ALTERATION_EVIDENCE,
                RIBOSOMAL_ALTERATION_EVIDENCE,
            ),
            _edge(
                "determinant",
                "enables",
                "RO:0002327",
                "methyltransferase",
                "The determinant enables methyl transfer onto nucleoside residues "
                "in 23S rRNA.",
                *activity_evidence,
            ),
            _edge(
                "methyltransferase",
                "causally upstream of",
                "RO:0002411",
                "methylated",
                "23S rRNA methyltransferase activity yields a methylated 23S "
                "rRNA antibiotic-binding site.",
                *activity_evidence,
            ),
            _edge(
                "methylated",
                "negatively regulates (blocks antibiotic binding)",
                "RO:0002212",
                "target_site",
                "Methylation changes the 23S rRNA antibiotic-binding site and "
                "prevents normal drug binding.",
                target.determinant_evidence,
                RRNA_METHYLTRANSFERASE_PARENT_EVIDENCE,
                RRNA_METHYLTRANSFERASE_EVIDENCE,
                RRNA_EVIDENCE,
            ),
            _edge(
                "methylated",
                "causally upstream of (blocks antibiotic binding)",
                "RO:0002411",
                "resistance",
                "The methylated 23S rRNA antibiotic-binding site is the terminal "
                "modeled cause of the resistance phenotype.",
                *evidence,
            ),
            _edge(
                "target_site",
                "part of",
                "BFO:0000050",
                "subunit",
                "The methylated antibiotic target is a site in 23S rRNA in the "
                "50S ribosomal subunit.",
                target.determinant_evidence,
                RRNA_EVIDENCE,
            ),
        ],
    }


GraphBuilder = Callable[[dict[str, Any], Any], dict[str, Any]]

GRAPH_BUILDERS: dict[type[Target], GraphBuilder] = {
    MutationTarget: _mutation_graph,
    MethyltransferaseTarget: _methyltransferase_graph,
}

REQUIRED_NODES: dict[type[Target], set[str]] = {
    MutationTarget: {"determinant", "mech0", "binding_site", "subunit", "resistance"},
    MethyltransferaseTarget: {"determinant", "mech0", "mech1", "resistance"},
}


def _validate_record(record: dict[str, Any], target: Target) -> None:
    if record.get("identifier") != target.identifier:
        raise ValueError(
            f"{target.filename}: expected {target.identifier}, "
            f"found {record.get('identifier')}"
        )
    if not record.get("label"):
        raise ValueError(f"{target.identifier}: missing label")

    graphs = _dicts(record.get("causal_graphs"))
    if len(graphs) != 1 or graphs[0].get("graph_id") != "resistance":
        raise ValueError(f"{target.identifier}: expected exactly one resistance graph")

    node_ids = {
        str(node.get("node_id"))
        for node in _dicts(graphs[0].get("nodes"))
        if node.get("node_id")
    }
    missing_nodes = sorted(REQUIRED_NODES[type(target)] - node_ids)
    if missing_nodes:
        missing = ", ".join(missing_nodes)
        raise ValueError(f"{target.identifier}: missing node(s): {missing}")


def enrich_record(record: dict[str, Any], target: Target) -> tuple[dict[str, Any], bool]:
    _validate_record(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [GRAPH_BUILDERS[type(target)](record, target)]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a specific 16S/23S rRNA target: {identifier}")
    if path.name != target.filename:
        raise ValueError(f"{path}: target {identifier} must be in {target.filename}")

    enriched, changed = enrich_record(record, target)
    out = replace_block(text, "causal_graphs", _dump({"causal_graphs": enriched["causal_graphs"]}))
    if HISTORY_CURATOR not in out:
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
        help="ARO directory or one of the target YAML files",
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
