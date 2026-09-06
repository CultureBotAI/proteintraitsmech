#!/usr/bin/env python3
"""Describe and evidence ABC/MFS efflux and ABC-F protection ARO graphs.

The MFS and ABC efflux records handled here already have the right
domain/fold/efflux shape, but every edge is single-evidenced and lacks a
description. The ABC-F parent is different: CARD explicitly scopes it to
ribosomal protection instead of transport, so this updater rewrites that graph
around ribosome binding and antibiotic displacement.

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

HISTORY_ACTION = "Described ABC/MFS efflux and ABC-F target-protection causal graphs"
HISTORY_CURATOR = "codex-causal-graph-quality"
HISTORY_EVENT = {
    "timestamp": "2026-09-06T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": HISTORY_ACTION,
    "llm_assisted": True,
}

ANTIBIOTIC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010000",
    "snippet": "Antibiotic resistance via the transport of antibiotics out of the cell.",
    "notes": "CARD definition for the antibiotic efflux resistance mechanism.",
}

EFFLUX_PUMP_EVIDENCE = {
    "reference": "ARO:3000159",
    "snippet": "Efflux proteins that pump antibiotic out of a cell to confer resistance.",
    "notes": "CARD definition for efflux pump complexes and subunits.",
}

MFS_EVIDENCE = {
    "reference": "ARO:0010002",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. Major "
        "facilitator superfamily (MFS) transporters and ABC transporters "
        "comprise the two largest and most functionally diverse of the "
        "transporter superfamilies. However, MFS transporters are distinct from "
        "ABC transporters in both their primary sequence and structure and in "
        "the mechanism of energy coupling. As secondary transporters they are, "
        "like RND and SMR transporters, energized by the electrochemical proton "
        "gradient."
    ),
    "notes": "CARD definition for MFS antibiotic efflux pumps.",
}

ABC_EFFLUX_EVIDENCE = {
    "reference": "ARO:0010001",
    "snippet": (
        "Directed pumping of antibiotic out of a cell to confer resistance. "
        "ATP-binding cassette (ABC) transporters are present in all cells of all "
        "organisms and use the energy of ATP binding/hydrolysis to transport "
        "substrates across cell membranes."
    ),
    "notes": "CARD definition for ABC antibiotic efflux pumps.",
}

MFS_TRANSPORT_EVIDENCE = {
    "reference": "PMID:38974671",
    "snippet": (
        "The antimicrobial antiport transport cycle in bacteria is driven by the "
        "ion-motive force, an energy mode associated with changes in transporter "
        "conformations and gating during efflux across the membrane."
    ),
    "notes": "Evidence for ion-motive-force-driven MFS efflux.",
}

ABC_TRANSPORT_EVIDENCE = {
    "reference": "PMID:29892271",
    "snippet": (
        "Tripartite efflux pumps built around ATP-binding cassette (ABC) "
        "transporters are membrane protein machineries that perform vectorial "
        "export of drugs and virulence factors from Gram negative bacteria, "
        "using ATP-hydrolysis as energy source."
    ),
    "notes": "Evidence for ATP-hydrolysis-driven ABC drug efflux.",
}

TARGET_PROTECTION_EVIDENCE = {
    "reference": "ARO:0001003",
    "snippet": (
        "Protection of antibiotic action target from antibiotic binding, which "
        "process will result in antibiotic resistance."
    ),
    "notes": "CARD definition for the antibiotic target protection mechanism.",
}

TARGET_PROTECTION_PARENT_EVIDENCE = {
    "reference": "ARO:3000185",
    "snippet": (
        "These proteins confer antibiotic resistance by bind the antibiotic "
        "target to prevent antibiotic binding."
    ),
    "notes": "CARD definition for antibiotic target protection proteins.",
}

ABC_F_EVIDENCE = {
    "reference": "ARO:3004469",
    "snippet": (
        "ABC-F proteins confer antibiotic resistance via ribosomal protection "
        "and not antibiotic efflux as in other ABC proteins."
    ),
    "notes": "CARD definition for ABC-F ribosomal protection proteins.",
}

ABC_F_DISPLACEMENT_EVIDENCE = {
    "reference": "PMID:27006457",
    "snippet": "such proteins are capable of displacing antibiotic from the ribosome in vitro",
    "notes": "Experimental evidence for ABC-F antibiotic displacement from the ribosome.",
}

GO_RIBOSOME_EVIDENCE = {
    "reference": "GO:0005840",
    "snippet": (
        "It consists of two subunits, one large and one small, each containing "
        "only protein and RNA."
    ),
    "notes": "GO definition for the ribosome.",
}

MFS_DOMAIN_EVIDENCE = {
    "reference": "Pfam:PF07690",
    "snippet": "Major Facilitator Superfamily",
    "notes": "Pfam family for the MFS transporter domain.",
}

MFS_FOLD_EVIDENCE = {
    "reference": "CATH:1.20.1250.20",
    "snippet": "MFS general substrate transporter like domains",
    "notes": "CATH fold for MFS general substrate transporter-like domains.",
}

ABC_DOMAIN_EVIDENCE = {
    "reference": "Pfam:PF00005",
    "snippet": "ABC transporter",
    "notes": "Pfam family for the ABC transporter ATP-binding domain.",
}

ABC_FOLD_EVIDENCE = {
    "reference": "CATH:3.40.50.300",
    "snippet": "P-loop containing nucleotide triphosphate hydrolases",
    "notes": "CATH fold for ABC ATPase domains.",
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
class EffluxFamily:
    title: str
    family_evidence: dict[str, str]
    transport_evidence: dict[str, str]
    domain_node: dict[str, str]
    fold_node: dict[str, str]
    domain_evidence: dict[str, str]
    fold_evidence: dict[str, str]
    efflux_predicate: str
    graph_description: str


@dataclass(frozen=True)
class EffluxTarget:
    identifier: str
    filename: str
    determinant_evidence: dict[str, str]
    family: EffluxFamily


@dataclass(frozen=True)
class AbcFTarget:
    identifier: str
    filename: str
    determinant_evidence: dict[str, str]


Target = EffluxTarget | AbcFTarget

MFS_FAMILY = EffluxFamily(
    title="MFS antibiotic efflux",
    family_evidence=MFS_EVIDENCE,
    transport_evidence=MFS_TRANSPORT_EVIDENCE,
    domain_node={
        "node_id": "domain",
        "label": "major facilitator superfamily (MFS) transporter domain",
        "node_type": "DOMAIN",
        "grounding": "Pfam:PF07690",
        "description": "Transporter domain shared by MFS antibiotic efflux pumps.",
    },
    fold_node={
        "node_id": "fold",
        "label": "MFS general substrate transporter fold",
        "node_type": "DOMAIN",
        "grounding": "CATH:1.20.1250.20",
        "description": "Fold adopted by MFS general substrate transporter-like domains.",
    },
    domain_evidence=MFS_DOMAIN_EVIDENCE,
    fold_evidence=MFS_FOLD_EVIDENCE,
    efflux_predicate="enables (ion-motive-force-driven drug efflux)",
    graph_description=(
        "Curated resistance-causation graph for MFS antibiotic efflux pumps. "
        "The determinant enables ion-motive-force-driven export of antibiotics "
        "out of the cell, lowering intracellular drug exposure."
    ),
)

ABC_EFFLUX_FAMILY = EffluxFamily(
    title="ABC antibiotic efflux",
    family_evidence=ABC_EFFLUX_EVIDENCE,
    transport_evidence=ABC_TRANSPORT_EVIDENCE,
    domain_node={
        "node_id": "domain",
        "label": "ABC transporter ATP-binding domain",
        "node_type": "DOMAIN",
        "grounding": "Pfam:PF00005",
        "description": "ATP-binding domain shared by ABC antibiotic efflux pumps.",
    },
    fold_node={
        "node_id": "fold",
        "label": "P-loop NTPase fold (ABC ATPase nucleotide-binding domain)",
        "node_type": "DOMAIN",
        "grounding": "CATH:3.40.50.300",
        "description": "P-loop NTPase fold adopted by ABC ATPase domains.",
    },
    domain_evidence=ABC_DOMAIN_EVIDENCE,
    fold_evidence=ABC_FOLD_EVIDENCE,
    efflux_predicate="enables (ATP-driven drug efflux)",
    graph_description=(
        "Curated resistance-causation graph for ABC antibiotic efflux pumps. "
        "The determinant enables ATP-driven export of antibiotics across the "
        "cell membrane, lowering intracellular drug exposure."
    ),
)

EFFLUX_TARGETS: tuple[EffluxTarget, ...] = (
    EffluxTarget(
        identifier="ARO:3007669",
        filename="aadt-aro3007669.yaml",
        determinant_evidence={
            "reference": "ARO:3007669",
            "snippet": (
                "The AadT pump is a novel multidrug efflux pump from the proton "
                "antiporter 2 (DHA2) family and was discovered in Acinetobacter "
                "multidrug resistance plasmids."
            ),
            "notes": "CARD definition for aadT.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3003942",
        filename="abca-aro3003942.yaml",
        determinant_evidence={
            "reference": "ARO:3003942",
            "snippet": (
                "AbcA is a multidrug resistant ABC transporter that confers "
                "resistance to methicillin, daptomycin, cefotaxime, and moenomycin."
            ),
            "notes": "CARD definition for abcA.",
        },
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004573",
        filename="acinetobacter-baumannii-abaf-aro3004573.yaml",
        determinant_evidence={
            "reference": "ARO:3004573",
            "snippet": "Expression of abaF in E. coli resulted in increased resistance to fosfomycin.",
            "notes": "CARD definition for Acinetobacter baumannii AbaF.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:3004577",
        filename="acinetobacter-baumannii-amva-aro3004577.yaml",
        determinant_evidence={
            "reference": "ARO:3004577",
            "snippet": (
                "AmvA has 14 alpha-helical transmembrane segments, qualifying it "
                "as a member of the DHA2 transporter family of the major "
                "facilitator superfamily (MFS)."
            ),
            "notes": "CARD definition for Acinetobacter baumannii AmvA.",
        },
        family=MFS_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:0010001",
        filename="atp-binding-cassette-abc-antibiotic-efflux-pump-aro0010001.yaml",
        determinant_evidence=ABC_EFFLUX_EVIDENCE,
        family=ABC_EFFLUX_FAMILY,
    ),
    EffluxTarget(
        identifier="ARO:0010002",
        filename="major-facilitator-superfamily-mfs-antibiotic-efflux-pump-aro0010002.yaml",
        determinant_evidence=MFS_EVIDENCE,
        family=MFS_FAMILY,
    ),
)

ABC_F_TARGET = AbcFTarget(
    identifier="ARO:3004469",
    filename="abc-f-atp-binding-cassette-ribosomal-protection-protein-aro3004469.yaml",
    determinant_evidence=ABC_F_EVIDENCE,
)

TARGETS: tuple[Target, ...] = (
    EFFLUX_TARGETS[0],
    ABC_F_TARGET,
    *EFFLUX_TARGETS[1:],
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


def _determinant_node(record: dict[str, Any]) -> dict[str, str]:
    return {
        "node_id": "determinant",
        "label": str(record["label"]),
        "node_type": "PROTEIN",
        "grounding": str(record["identifier"]),
    }


def _efflux_graph(record: dict[str, Any], target: EffluxTarget) -> dict[str, Any]:
    family = target.family
    efflux_evidence = (
        target.determinant_evidence,
        family.family_evidence,
        EFFLUX_PUMP_EVIDENCE,
        ANTIBIOTIC_EFFLUX_EVIDENCE,
        family.transport_evidence,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → {family.title} → resistance",
        "description": family.graph_description,
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic efflux",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0010000",
            },
            copy.deepcopy(family.domain_node),
            copy.deepcopy(family.fold_node),
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies this transporter under the antibiotic efflux "
                "resistance mechanism.",
                *efflux_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic efflux confers resistance by transporting antibiotics "
                "out of the cell.",
                *efflux_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "The determinant exports antibiotic from the cell through its "
                "family-specific transport mechanism.",
                *efflux_evidence,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The transporter domain is part of the resistance determinant.",
                target.determinant_evidence,
                family.family_evidence,
                family.domain_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The determinant adopts the transporter fold associated with this "
                "efflux-pump family.",
                target.determinant_evidence,
                family.family_evidence,
                family.fold_evidence,
            ),
            _edge(
                "domain",
                family.efflux_predicate,
                "RO:0002327",
                "mech0",
                "The transporter domain enables family-specific antibiotic export.",
                target.determinant_evidence,
                family.family_evidence,
                family.domain_evidence,
                family.transport_evidence,
            ),
        ],
    }


def _abc_f_graph(record: dict[str, Any], target: AbcFTarget) -> dict[str, Any]:
    protection_evidence = (
        target.determinant_evidence,
        TARGET_PROTECTION_EVIDENCE,
        TARGET_PROTECTION_PARENT_EVIDENCE,
        ABC_F_DISPLACEMENT_EVIDENCE,
    )
    atpase_evidence = (
        target.determinant_evidence,
        ABC_DOMAIN_EVIDENCE,
        ABC_FOLD_EVIDENCE,
        ABC_F_DISPLACEMENT_EVIDENCE,
    )

    return {
        "graph_id": "resistance",
        "title": f"{record['label']} → ribosomal protection → resistance",
        "description": (
            "Curated resistance-causation graph for ABC-F ribosomal protection "
            "proteins. The graph models the ABC ATPase determinant binding the "
            "ribosome and displacing bound antibiotic instead of modeling ABC-F "
            "as an efflux transporter."
        ),
        "nodes": [
            _determinant_node(record),
            {
                "node_id": "mech0",
                "label": "antibiotic target protection",
                "node_type": "MOLECULAR_FUNCTION",
                "grounding": "ARO:0001003",
            },
            {
                "node_id": "domain",
                "label": "ABC transporter ATP-binding domain",
                "node_type": "DOMAIN",
                "grounding": "Pfam:PF00005",
                "description": "ATP-binding domain carried by ABC-F ribosomal protection proteins.",
            },
            {
                "node_id": "fold",
                "label": "P-loop NTPase fold (ABC ATPase nucleotide-binding domain)",
                "node_type": "DOMAIN",
                "grounding": "CATH:3.40.50.300",
                "description": "P-loop NTPase fold adopted by ABC-F ATPase domains.",
            },
            {
                "node_id": "ribosome",
                "label": "ribosome",
                "node_type": "CELLULAR_LOCALIZATION",
                "grounding": "GO:0005840",
            },
            {
                "node_id": "displaced_antibiotic",
                "label": "antibiotic displaced from the ribosome",
                "node_type": "STATE",
                "description": (
                    "Local state for antibiotic removal from the ribosome by an "
                    "ABC-F target-protection protein."
                ),
            },
            copy.deepcopy(RESISTANCE_NODE),
        ],
        "edges": [
            _edge(
                "determinant",
                "participates in (resistance mechanism)",
                "RO:0000056",
                "mech0",
                "CARD classifies ABC-F proteins under antibiotic target "
                "protection, not efflux.",
                *protection_evidence,
            ),
            _edge(
                "mech0",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Antibiotic target protection prevents antibiotics from binding "
                "or remaining bound to their target.",
                *protection_evidence,
            ),
            _edge(
                "determinant",
                "causally upstream of (confers resistance)",
                "RO:0002411",
                "resistance",
                "ABC-F proteins confer resistance through ribosomal target "
                "protection.",
                *protection_evidence,
            ),
            _edge(
                "domain",
                "part of",
                "BFO:0000050",
                "determinant",
                "The ABC ATP-binding domain is part of the ABC-F determinant.",
                *atpase_evidence,
            ),
            _edge(
                "determinant",
                "member of",
                "RO:0002350",
                "fold",
                "The ABC-F determinant adopts the P-loop NTPase fold used by ABC "
                "ATPase domains.",
                *atpase_evidence,
            ),
            _edge(
                "domain",
                "enables (ribosomal protection)",
                "RO:0002327",
                "mech0",
                "The ABC ATPase domain powers ribosomal target protection.",
                *atpase_evidence,
            ),
            _edge(
                "determinant",
                "molecularly interacts with",
                "RO:0002436",
                "ribosome",
                "ABC-F proteins protect the ribosome by binding it.",
                target.determinant_evidence,
                ABC_F_DISPLACEMENT_EVIDENCE,
                GO_RIBOSOME_EVIDENCE,
            ),
            _edge(
                "determinant",
                "causally upstream of (displaces antibiotic)",
                "RO:0002411",
                "displaced_antibiotic",
                "ABC-F proteins displace antibiotic from the ribosome.",
                *protection_evidence,
            ),
            _edge(
                "displaced_antibiotic",
                "negatively regulates (antibiotic occupancy)",
                "RO:0002212",
                "ribosome",
                "Displacement reduces antibiotic occupancy on the ribosome.",
                target.determinant_evidence,
                TARGET_PROTECTION_EVIDENCE,
                ABC_F_DISPLACEMENT_EVIDENCE,
                GO_RIBOSOME_EVIDENCE,
            ),
            _edge(
                "displaced_antibiotic",
                "causally upstream of",
                "RO:0002411",
                "resistance",
                "Removing antibiotic from the ribosome is the terminal modeled "
                "cause of ABC-F target-protection resistance.",
                *protection_evidence,
            ),
        ],
    }


REQUIRED_NODES: dict[type[Target], set[str]] = {
    EffluxTarget: {"determinant", "mech0", "domain", "fold", "resistance"},
    AbcFTarget: {"determinant", "mech0", "domain", "fold", "resistance"},
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

    if isinstance(target, EffluxTarget):
        graph = _efflux_graph(record, target)
    else:
        graph = _abc_f_graph(record, target)

    out = copy.deepcopy(record)
    out["causal_graphs"] = [graph]
    return out, out != record


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: expected a YAML mapping")

    identifier = record.get("identifier")
    target = TARGET_BY_ID.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not an ABC/MFS efflux or ABC-F target: {identifier}")
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
