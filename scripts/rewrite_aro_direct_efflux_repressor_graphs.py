#!/usr/bin/env python3
"""Ground and complete direct efflux-repressor ARO graphs.

The records handled here are efflux-pump repressors whose CARD definitions name
a concrete pump or pump operon.  This updater grounds the named pump, grounds
broad transcriptional repression to GO, removes the obsolete wild-type
determinant-to-repression role edge from the loss-of-function path, adds the
missing pump-to-efflux edge, and replaces stale archetype evidence with exact
target/pump evidence.

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
    "timestamp": "2026-09-05T00:00:00Z",
    "curator": HISTORY_CURATOR,
    "action": (
        "Replaced stale archetype evidence on direct efflux-repressor graphs, "
        "grounded their named efflux pumps and transcriptional-repression nodes, "
        "removed the obsolete wild-type repressor edge, and linked pump expression "
        "to antibiotic efflux"
    ),
    "llm_assisted": True,
}

GO_NEGATIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045892",
    "snippet": (
        "Any process that stops, prevents, or reduces the frequency, rate or extent "
        "of cellular DNA-templated transcription."
    ),
    "notes": "GO definition for the broad transcriptional repression process.",
}

MECHANISM_NODE = {
    "node_id": "mech0",
    "label": "antibiotic efflux",
    "node_type": "MOLECULAR_FUNCTION",
    "grounding": "ARO:0010000",
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

PUMP_EFFLUX_EDGE = {
    "subject": "pump",
    "predicate": "enables (drug efflux)",
    "predicate_id": "RO:0002327",
    "object": "mech0",
}
PUMP_EFFLUX_FULL_EDGE = ("pump", "RO:0002327", "mech0")

OBSOLETE_EDGE = ("determinant", "RO:0002327", "repression")


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
    repressor_label: str
    pump_label: str
    pump_grounding: str
    repressed_process: str
    target_snippet: str
    target_notes: str
    pump_snippet: str
    pump_notes: str

    @property
    def target_evidence(self) -> dict[str, str]:
        return {
            "reference": self.identifier,
            "snippet": self.target_snippet,
            "notes": self.target_notes,
        }

    @property
    def pump_evidence(self) -> dict[str, str]:
        return {
            "reference": self.pump_grounding,
            "snippet": self.pump_snippet,
            "notes": self.pump_notes,
        }

    @property
    def pump_node(self) -> dict[str, str]:
        return {
            "node_id": "pump",
            "label": self.pump_label,
            "node_type": "PROTEIN",
            "grounding": self.pump_grounding,
            "description": (
                f"Grounded to CARD's {self.pump_label}, the pump repressed by "
                f"{self.repressor_label}."
            ),
        }

    @property
    def repression_node(self) -> dict[str, str]:
        return {
            "node_id": "repression",
            "label": f"negative regulation of {self.repressed_process}",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "GO:0045892",
            "description": (
                "Grounded to the broad GO DNA-templated transcriptional repression "
                f"process because {self.repressor_label} represses "
                f"{self.repressed_process}."
            ),
        }

    @property
    def edge_updates(self) -> dict[tuple[str, str], EdgeUpdate]:
        target = self.target_evidence
        pump = self.pump_evidence
        return {
            ("determinant", "mech0"): EdgeUpdate(
                predicate="participates in (resistance mechanism)",
                predicate_id="RO:0000056",
                description=(
                    "CARD classifies this repressor under antibiotic efflux because "
                    f"it regulates {self.pump_label}."
                ),
                evidence=(target, pump),
            ),
            ("mech0", "resistance"): EdgeUpdate(
                predicate="causally upstream of",
                predicate_id="RO:0002411",
                description=(
                    "The broad efflux mechanism represents elevated activity of the "
                    "regulated multidrug pump."
                ),
                evidence=(target, pump),
            ),
            ("determinant", "resistance"): EdgeUpdate(
                predicate="causally upstream of (confers resistance)",
                predicate_id="RO:0002411",
                description=(
                    "Loss of normal repressor activity is represented as raising "
                    f"{self.pump_label} and increasing antibiotic efflux."
                ),
                evidence=(target, pump),
            ),
            ("repression", "pump"): EdgeUpdate(
                predicate="negatively regulates (holds pump expression down)",
                predicate_id="RO:0002212",
                description=(
                    "Normal repressor-dependent transcriptional repression keeps "
                    f"{self.pump_label} expression low."
                ),
                evidence=(target, GO_NEGATIVE_TRANSCRIPTION_EVIDENCE),
            ),
            ("determinant", "repression"): EdgeUpdate(
                predicate="negatively regulates (loss lifts the repression)",
                predicate_id="RO:0002212",
                description=(
                    "Resistance-associated repressor loss is represented as loss of "
                    f"normal {self.pump_label} repression."
                ),
                evidence=(target, GO_NEGATIVE_TRANSCRIPTION_EVIDENCE),
            ),
            ("pump", "mech0"): EdgeUpdate(
                predicate="enables (drug efflux)",
                predicate_id="RO:0002327",
                description=(
                    f"{self.pump_label} is the multidrug pump whose derepressed "
                    "expression supplies antibiotic efflux."
                ),
                evidence=(target, pump),
            ),
        }

    @property
    def expected_edges(self) -> set[tuple[str, str]]:
        return set(self.edge_updates)


TARGETS = {
    "ARO:3000746": Target(
        identifier="ARO:3000746",
        filename="mepr-aro3000746.yaml",
        repressor_label="MepR",
        pump_label="MepA",
        pump_grounding="ARO:3000026",
        repressed_process="MepA transcription",
        target_snippet=(
            "MepR is an upstream repressor of MepA in Staphylococcus aureus. It is "
            "part of the mepRAB operon."
        ),
        target_notes="CARD definition for the mepR repressor determinant.",
        pump_snippet=(
            "MepA is an efflux protein regulated by MepR and part of the MepRAB "
            "cluster. Its presence in Staphylococcus aureus led to multidrug "
            "resistance, while it has also been shown to decrease tigecycline "
            "susceptibility."
        ),
        pump_notes="CARD definition for the MepA efflux pump regulated by MepR.",
    ),
    "ARO:3003710": Target(
        identifier="ARO:3003710",
        filename="mexl-aro3003710.yaml",
        repressor_label="MexL",
        pump_label="MexJK",
        pump_grounding="ARO:3009148",
        repressed_process="mexJK transcription",
        target_snippet=(
            "MexL is a specific repressor of mexJK transcription and autoregulates "
            "its own expression."
        ),
        target_notes="CARD definition for the MexL repressor determinant.",
        pump_snippet=(
            "MexJK is a multidrug efflux pump complex composed of MexJ and MexK as "
            "its primary components. This system serves as a core transport "
            "mechanism, working with outer membrane proteins to expel antibiotics "
            "and harmful compounds, thereby contributing to multidrug resistance."
        ),
        pump_notes="CARD definition for the MexJK efflux pump repressed by MexL.",
    ),
    "ARO:3003709": Target(
        identifier="ARO:3003709",
        filename="mexz-aro3003709.yaml",
        repressor_label="MexZ",
        pump_label="MexXY",
        pump_grounding="ARO:3009152",
        repressed_process="mexXY transcription",
        target_snippet=(
            "MexZ is a transcriptional regulator that downregulates the mexXY "
            "multidrug transporter operon, which confers to aminoglycoside "
            "resistance on Pseudomonas aeruginosa."
        ),
        target_notes="CARD definition for the MexZ repressor determinant.",
        pump_snippet=(
            "MexXY is a multidrug efflux pump complex consisting of MexX and MexY "
            "as its core components. This system serves as a key transport "
            "mechanism, interacting with outer membrane proteins to expel "
            "antibiotics and toxic compounds, contributing to multidrug resistance."
        ),
        pump_notes="CARD definition for the MexXY efflux pump repressed by MexZ.",
    ),
    "ARO:3000817": Target(
        identifier="ARO:3000817",
        filename="mtrr-aro3000817.yaml",
        repressor_label="MtrR",
        pump_label="MtrCDE",
        pump_grounding="ARO:3000369",
        repressed_process="mtrCDE expression",
        target_snippet=(
            "MtrR is a repressor of mtrCDE expression. Mutations in mtrR increase "
            "multidrug resistance."
        ),
        target_notes="CARD definition for the mtrR repressor determinant.",
        pump_snippet=(
            "The mtr (multiple transferable resistance) system of Neisseria "
            "gonorrhoeae confers resistance to many hydrophobic agents including "
            "antibiotics, fatty-acids and detergents. MtrCDE is homologous to "
            "AcrAB-TolC, where MtrC is the membrane fusion protein, MtrD is the "
            "inner membrane transporter, and MtrE is the outer membrane channel "
            "protein."
        ),
        pump_notes="CARD definition for the MtrCDE efflux pump repressed by MtrR.",
    ),
    "ARO:3004069": Target(
        identifier="ARO:3004069",
        filename="mvat-aro3004069.yaml",
        repressor_label="MvaT",
        pump_label="MexEF-OprN",
        pump_grounding="ARO:3000798",
        repressed_process="MexEF-OprN expression",
        target_snippet=(
            "MvaT, a global regulator of virulence genes in P. aeruginosa, has also "
            "shown to be able to repress the expression of the MexEF-OprN pump."
        ),
        target_notes="CARD definition for the MvaT repressor determinant.",
        pump_snippet=(
            "MexEF-OprN is a multidrug efflux protein expressed in the Gram-negative "
            "Pseudomonas aeruginosa. MexE is the membrane fusion protein; MexF is "
            "the inner membrane transporter; and OprN is the outer membrane "
            "channel. MexEF-OprN is associated with resistance to fluoroquinolones, "
            "chloramphenicol, and trimethoprim."
        ),
        pump_notes="CARD definition for the MexEF-OprN efflux pump repressed by MvaT.",
    ),
    "ARO:3000819": Target(
        identifier="ARO:3000819",
        filename="nald-aro3000819.yaml",
        repressor_label="NalD",
        pump_label="MexAB-OprM",
        pump_grounding="ARO:3000386",
        repressed_process="MexAB-OprM transcription",
        target_snippet=(
            "NalD is a repressor of MexAB-OprM. Mutations lead to multidrug "
            "resistance and MexAB-OprM overexpression."
        ),
        target_notes="CARD definition for the nalD repressor determinant.",
        pump_snippet=(
            "MexAB-OprM is a multidrug efflux protein expressed in the Gram-negative "
            "Pseudomonas aeruginosa. MexA is the membrane fusion protein; MexB is "
            "the inner membrane transporter; and OprM is the outer membrane "
            "channel. MexAB-OprM is associated with resistance to fluoroquinolones, "
            "chloramphenicol, erythromycin, azithromycin, novobiocin, and certain "
            "β-lactams and lastly over-expression is linked to colistin resistance."
        ),
        pump_notes="CARD definition for the MexAB-OprM efflux pump repressed by NalD.",
    ),
    "ARO:3000820": Target(
        identifier="ARO:3000820",
        filename="nfxb-aro3000820.yaml",
        repressor_label="NfxB",
        pump_label="MexCD-OprJ",
        pump_grounding="ARO:3000797",
        repressed_process="mexCD-oprJ transcription",
        target_snippet=(
            "NfxB is a repressor of the efflux pump mexCD-oprJ and itself (NfxB "
            "binds upstream of the nfxB gene and negatively regulates its own "
            "expression). Increased expression of MexCD–OprJ brought about by "
            "mutations in NfxB."
        ),
        target_notes="CARD definition for the NfxB repressor determinant.",
        pump_snippet=(
            "MexCD-OprJ is a multidrug efflux protein expressed in the Gram-negative "
            "Pseudomonas aeruginosa. MexC is the membrane fusion protein; MexD is "
            "the inner membrane transporter; and OprJ is the outer membrane "
            "channel. MexCD-OprJ is typically quiescent in wild-type cells, with "
            "expression following mutation of the nfxB gene that is divergently "
            "transcribed from the mexCD-oprJ operon and encodes a repressor of "
            "mexCD-oprJ expression."
        ),
        pump_notes="CARD definition for the MexCD-OprJ efflux pump repressed by NfxB.",
    ),
    "ARO:3000834": Target(
        identifier="ARO:3000834",
        filename="phop-aro3000834.yaml",
        repressor_label="PhoP",
        pump_label="MacAB-TolC",
        pump_grounding="ARO:3000545",
        repressed_process="macAB transcription",
        target_snippet="PhoP is a direct repressor of the macAB efflux genes.",
        target_notes="CARD definition for the phoP repressor determinant.",
        pump_snippet=(
            "MacAB-TolC is an ABC efflux pump complex expressed in E. coli and "
            "Salmonella enterica. It confers resistance to macrolides, including "
            "erythromycin."
        ),
        pump_notes="CARD definition for the MacAB-TolC pump repressed by PhoP.",
    ),
}

EXPECTED_INPUT_FULL_EDGES = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0002327", "repression"),
    ("repression", "RO:0002212", "pump"),
    ("determinant", "RO:0002212", "repression"),
    ("pump", "RO:0002327", "mech0"),
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
    by_id = {node.get("node_id"): node for node in nodes if isinstance(node, dict)}
    if "determinant" not in by_id:
        msg = f"{target.identifier}: missing node(s): determinant"
        raise ValueError(msg)

    graph["nodes"] = [
        copy.deepcopy(by_id["determinant"]),
        copy.deepcopy(MECHANISM_NODE),
        copy.deepcopy(target.pump_node),
        copy.deepcopy(target.repression_node),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _enrich_edges(graph: dict[str, Any], target: Target) -> None:
    edges = graph.setdefault("edges", [])
    if not any(_full_edge_key(edge) == PUMP_EFFLUX_FULL_EDGE for edge in edges):
        edges.append(copy.deepcopy(PUMP_EFFLUX_EDGE))

    seen_full: set[tuple[str, str, str]] = set()
    seen: set[tuple[str, str]] = set()
    enriched_edges: list[dict[str, Any]] = []
    for edge in edges:
        full_key = _full_edge_key(edge)
        if full_key in seen_full:
            msg = f"{target.identifier}: duplicate edge {full_key[0]} -> {full_key[2]}"
            raise ValueError(msg)
        seen_full.add(full_key)
        if full_key == OBSOLETE_EDGE:
            continue
        if full_key not in EXPECTED_INPUT_FULL_EDGES:
            msg = f"{target.identifier}: unexpected edge {full_key[0]} -> {full_key[2]}"
            raise ValueError(msg)

        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        update = target.edge_updates[key]
        enriched_edges.append(
            _ordered_edge(
                {
                    "subject": key[0],
                    "predicate": update.predicate,
                    "predicate_id": update.predicate_id,
                    "object": key[1],
                    "description": update.description,
                    "evidence": [copy.deepcopy(item) for item in update.evidence],
                }
            )
        )
        seen.add(key)

    missing_edges = sorted(target.expected_edges - seen)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, object_ in missing_edges)
        msg = f"{target.identifier}: missing edge(s): {missing}"
        raise ValueError(msg)

    graph["edges"] = enriched_edges


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

    graph["description"] = (
        "Curated resistance-causation graph for loss of efflux-pump repression. The "
        "graph replaces stale archetype evidence and grounds the named efflux pump "
        "and transcriptional repression nodes."
    )
    _enrich_nodes(graph, target)
    _enrich_edges(graph, target)
    return out, out.get("causal_graphs") != before


def enrich_text(text: str, path: Path) -> tuple[str, bool]:
    record = yaml.safe_load(text)
    if not isinstance(record, dict):
        raise ValueError(f"{path}: record is not a mapping")
    identifier = record.get("identifier")
    target = TARGETS.get(identifier)
    if target is None:
        raise ValueError(f"{path}: not a direct efflux-repressor target: {identifier}")
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
        help="ARO directory or one direct efflux-repressor target YAML file",
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
