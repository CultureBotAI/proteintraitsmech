#!/usr/bin/env python3
"""Ground and complete direct efflux-activator ARO graphs.

The records handled here are efflux-pump activators whose CARD definitions name
a concrete pump or pump operon.  This updater grounds the named pump, grounds
broad transcriptional activation to GO, adds the missing pump-to-efflux edge,
and replaces stale archetype evidence with exact target/pump evidence.

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
        "Replaced stale archetype evidence on direct efflux-activator graphs, "
        "grounded their named efflux pumps and transcriptional-activation nodes, "
        "and linked pump expression to antibiotic efflux"
    ),
    "llm_assisted": True,
}

GO_POSITIVE_TRANSCRIPTION_EVIDENCE = {
    "reference": "GO:0045893",
    "snippet": (
        "Any process that activates or increases the frequency, rate or extent of "
        "cellular DNA-templated transcription."
    ),
    "notes": "GO definition for the broad transcriptional activation process.",
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

DEFAULT_INFERRED_EDGES = frozenset({("pump", "mech0")})

LEGACY_REPRESSOR_INPUT_FULL_EDGES = frozenset(
    {
        ("determinant", "RO:0002327", "repression"),
        ("repression", "RO:0002212", "pump"),
        ("determinant", "RO:0002212", "repression"),
    }
)

LEGACY_REPRESSOR_INFERRED_EDGES = frozenset(
    {
        ("determinant", "activation"),
        ("activation", "pump"),
        ("pump", "mech0"),
    }
)

EDGE_ORDER = (
    ("determinant", "mech0"),
    ("mech0", "resistance"),
    ("determinant", "resistance"),
    ("determinant", "activation"),
    ("activation", "pump"),
    ("pump", "mech0"),
)


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
    activator_label: str
    pump_label: str
    pump_grounding: str
    activated_process: str
    target_snippet: str
    target_notes: str
    pump_snippet: str
    pump_notes: str
    obsolete_input_full_edges: frozenset[tuple[str, str, str]] = frozenset()
    inferred_edges: frozenset[tuple[str, str]] = DEFAULT_INFERRED_EDGES

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
                f"Grounded to CARD's {self.pump_label}, the pump activated by "
                f"{self.activator_label}."
            ),
        }

    @property
    def activation_node(self) -> dict[str, str]:
        return {
            "node_id": "activation",
            "label": f"positive regulation of {self.activated_process}",
            "node_type": "BIOLOGICAL_PROCESS",
            "grounding": "GO:0045893",
            "description": (
                "Grounded to the broad GO DNA-templated transcriptional activation "
                f"process because {self.activator_label} promotes "
                f"{self.activated_process}."
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
                    "CARD classifies this activator under antibiotic efflux because "
                    f"it promotes {self.pump_label} expression."
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
                    f"{self.activator_label}-mediated activation raises "
                    f"{self.pump_label} expression and increases antibiotic efflux."
                ),
                evidence=(target, pump),
            ),
            ("determinant", "activation"): EdgeUpdate(
                predicate="enables (activates pump transcription)",
                predicate_id="RO:0002327",
                description=(
                    f"{self.activator_label} participates in positive regulation of "
                    f"{self.activated_process}."
                ),
                evidence=(target, GO_POSITIVE_TRANSCRIPTION_EVIDENCE),
            ),
            ("activation", "pump"): EdgeUpdate(
                predicate="positively regulates (raises pump expression)",
                predicate_id="RO:0002213",
                description=(
                    "Transcriptional activation raises expression of "
                    f"{self.pump_label}."
                ),
                evidence=(target, GO_POSITIVE_TRANSCRIPTION_EVIDENCE),
            ),
            ("pump", "mech0"): EdgeUpdate(
                predicate="enables (drug efflux)",
                predicate_id="RO:0002327",
                description=(
                    f"{self.pump_label} is the multidrug pump whose activated "
                    "expression supplies antibiotic efflux."
                ),
                evidence=(target, pump),
            ),
        }

    @property
    def expected_edges(self) -> set[tuple[str, str]]:
        return set(self.edge_updates)


ACRAB_TOLC_DEFINITION = (
    "AcrAB-TolC is a tripartite RND efflux system that confers resistance to "
    "tetracycline, chloramphenicol, ampicillin, nalidixic acid, and rifampin in "
    "Gram-negative bacteria. The system spans the cell membrane (AcrB) and the "
    "outer-membrane (TolC), and is linked together in the periplasm by AcrA."
)

MDTEF_TOLC_DEFINITION = (
    "MdtEF-TolC is a multidrug efflux complex in Gram-negative bacteria, "
    "including E. coli. MdtE is the membrane fusion protein, MdtF is the inner "
    "membrane transporter, while TolC is the outer membrane channel."
)

TARGETS = {
    "ARO:3004108": Target(
        identifier="ARO:3004108",
        filename="enterobacter-cloacae-rob-aro3004108.yaml",
        activator_label="rob",
        pump_label="AcrAB-TolC",
        pump_grounding="ARO:3000384",
        activated_process="acrAB transcription",
        target_snippet=(
            "rob is a positive regulator for the acrAB efflux genes, and is "
            "structurally similar to SoxS and MarA."
        ),
        target_notes="CARD definition for the Enterobacter cloacae rob activator.",
        pump_snippet=ACRAB_TOLC_DEFINITION,
        pump_notes=(
            "CARD definition for the AcrAB-TolC efflux pump activated through acrAB "
            "efflux genes."
        ),
    ),
    "ARO:3004109": Target(
        identifier="ARO:3004109",
        filename="escherichia-coli-rob-aro3004109.yaml",
        activator_label="rob",
        pump_label="AcrAB-TolC",
        pump_grounding="ARO:3000384",
        activated_process="acrAB transcription",
        target_snippet=(
            "rob is a positive regulator for the acrAB efflux genes, and is "
            "structurally similar to SoxS and MarA."
        ),
        target_notes="CARD definition for the Escherichia coli rob activator.",
        pump_snippet=ACRAB_TOLC_DEFINITION,
        pump_notes=(
            "CARD definition for the AcrAB-TolC efflux pump activated through acrAB "
            "efflux genes."
        ),
    ),
    "ARO:3000825": Target(
        identifier="ARO:3000825",
        filename="rob-aro3000825.yaml",
        activator_label="robA",
        pump_label="AcrAB-TolC",
        pump_grounding="ARO:3000384",
        activated_process="acrAB transcription",
        target_snippet=(
            "The robA protein is a positive regulator for the acrAB efflux genes, "
            "and is structurally similar to SoxS and MarA."
        ),
        target_notes="CARD definition for the rob activator.",
        pump_snippet=ACRAB_TOLC_DEFINITION,
        pump_notes=(
            "CARD definition for the AcrAB-TolC efflux pump activated through acrAB "
            "efflux genes."
        ),
    ),
    "ARO:3000508": Target(
        identifier="ARO:3000508",
        filename="gadx-aro3000508.yaml",
        activator_label="GadX",
        pump_label="MdtEF-TolC",
        pump_grounding="ARO:3000788",
        activated_process="mdtEF transcription",
        target_snippet=(
            "GadX is an AraC-family regulator that promotes mdtEF expression to "
            "confer multidrug resistance."
        ),
        target_notes="CARD definition for the gadX activator.",
        pump_snippet=MDTEF_TOLC_DEFINITION,
        pump_notes="CARD definition for the MdtEF-TolC efflux pump activated by GadX.",
    ),
    "ARO:3003838": Target(
        identifier="ARO:3003838",
        filename="gadw-aro3003838.yaml",
        activator_label="GadW",
        pump_label="MdtEF-TolC",
        pump_grounding="ARO:3000788",
        activated_process="mdtEF transcription",
        target_snippet=(
            "GadW is an AraC-family regulator that promotes mdtEF expression to "
            "confer multidrug resistance. GadW inhibits GadX-dependent activation. "
            "GadW clearly represses gadX and, in situations where GadX is missing, "
            "activates gadA and gadBC."
        ),
        target_notes="CARD definition for the gadW activator.",
        pump_snippet=MDTEF_TOLC_DEFINITION,
        pump_notes="CARD definition for the MdtEF-TolC efflux pump activated by GadW.",
        obsolete_input_full_edges=LEGACY_REPRESSOR_INPUT_FULL_EDGES,
        inferred_edges=LEGACY_REPRESSOR_INFERRED_EDGES,
    ),
    "ARO:3000504": Target(
        identifier="ARO:3000504",
        filename="gols-aro3000504.yaml",
        activator_label="GolS",
        pump_label="MdsABC",
        pump_grounding="ARO:3000786",
        activated_process="MdsABC expression",
        target_snippet=(
            "GolS is a regulator activated by the presence of golD, and promotes "
            "the expression of the MdsABC efflux pump."
        ),
        target_notes="CARD definition for the golS activator.",
        pump_snippet=(
            "MdsABC, or GesABC, is a RND-type efflux complex found in Salmonella. "
            "In addition to its metal-efflux system, GesABC is also capable of "
            "exporting beta-lactams, chloramphenicol, and thiamphenicol. GesB is "
            "the inner membrane transporter and is similar to MexF; GesA is the "
            "membrane-fusion protein, and GesC is the outer membrane factor."
        ),
        pump_notes="CARD definition for the MdsABC efflux pump activated by GolS.",
    ),
    "ARO:3003843": Target(
        identifier="ARO:3003843",
        filename="leuo-aro3003843.yaml",
        activator_label="LeuO",
        pump_label="MdtNOP",
        pump_grounding="ARO:3004101",
        activated_process="MdtNOP expression",
        target_snippet=(
            "leuO, a LysR family transcription factor, exists in a wide variety of "
            "bacteria of the family Enterobacteriaceae and is involved in the "
            "regulation of as yet unidentified genes affecting the stress response "
            "and pathogenesis expression. LeuO is also an activator of the MdtNOP "
            "efflux pump."
        ),
        target_notes="CARD definition for the leuO activator.",
        pump_snippet=(
            "MdtNOP is a MFS efflux pump protein found in E. coli. The deletion of "
            "mdtP from strain W3110 resulted in increased susceptibility to "
            "acriflavin, puromycin, and tetraphenylarsonium chloride. An E. coli "
            "mdtN null mutant is more sensitive to sulfur drugs than wild type."
        ),
        pump_notes="CARD definition for the MdtNOP efflux pump activated by LeuO.",
    ),
    "ARO:3000814": Target(
        identifier="ARO:3000814",
        filename="mext-aro3000814.yaml",
        activator_label="MexT",
        pump_label="MexEF-OprN",
        pump_grounding="ARO:3000798",
        activated_process="MexEF-OprN expression",
        target_snippet=(
            "MexT is a LysR-type transcriptional activator that positively "
            "regulates the expression of MexEF-OprN, OprD, and MexS."
        ),
        target_notes="CARD definition for the MexT activator.",
        pump_snippet=(
            "MexEF-OprN is a multidrug efflux protein expressed in the Gram-negative "
            "Pseudomonas aeruginosa. MexE is the membrane fusion protein; MexF is "
            "the inner membrane transporter; and OprN is the outer membrane "
            "channel. MexEF-OprN is associated with resistance to fluoroquinolones, "
            "chloramphenicol, and trimethoprim."
        ),
        pump_notes="CARD definition for the MexEF-OprN pump activated by MexT.",
    ),
    "ARO:3000816": Target(
        identifier="ARO:3000816",
        filename="mtra-aro3000816.yaml",
        activator_label="MtrA",
        pump_label="MtrCDE",
        pump_grounding="ARO:3000369",
        activated_process="MtrCDE expression",
        target_snippet=(
            "MtrA is a transcriptional activator of the MtrCDE multidrug efflux "
            "pump of Neisseria gonorrhoeae."
        ),
        target_notes="CARD definition for the mtrA activator.",
        pump_snippet=(
            "The mtr (multiple transferable resistance) system of Neisseria "
            "gonorrhoeae confers resistance to many hydrophobic agents including "
            "antibiotics, fatty-acids and detergents. MtrCDE is homologous to "
            "AcrAB-TolC, where MtrC is the membrane fusion protein, MtrD is the "
            "inner membrane transporter, and MtrE is the outer membrane channel "
            "protein."
        ),
        pump_notes="CARD definition for the MtrCDE pump activated by MtrA.",
    ),
    "ARO:3000823": Target(
        identifier="ARO:3000823",
        filename="rama-aro3000823.yaml",
        activator_label="RamA",
        pump_label="AcrAB-TolC",
        pump_grounding="ARO:3000384",
        activated_process="AcrAB-TolC expression",
        target_snippet=(
            "RamA (resistance antibiotic multiple) is a positive regulator of "
            "AcrAB-TolC and leads to high level multidrug resistance in Klebsiella "
            "pneumoniae, Salmonella enterica, and Enterobacter aerugenes, "
            "increasing the expression of both the mar operon as well as AcrAB. "
            "RamA also decreases OmpF expression."
        ),
        target_notes="CARD definition for the ramA activator.",
        pump_snippet=ACRAB_TOLC_DEFINITION,
        pump_notes="CARD definition for the AcrAB-TolC pump activated by RamA.",
    ),
}

EXPECTED_INPUT_FULL_EDGES = {
    ("determinant", "RO:0000056", "mech0"),
    ("mech0", "RO:0002411", "resistance"),
    ("determinant", "RO:0002411", "resistance"),
    ("determinant", "RO:0002327", "activation"),
    ("activation", "RO:0002213", "pump"),
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
        copy.deepcopy(target.activation_node),
        copy.deepcopy(RESISTANCE_NODE),
    ]


def _enrich_edges(graph: dict[str, Any], target: Target) -> None:
    edges = graph.setdefault("edges", [])

    seen: set[tuple[str, str]] = set()
    for edge in edges:
        full_key = _full_edge_key(edge)
        if full_key in target.obsolete_input_full_edges:
            continue
        if full_key not in EXPECTED_INPUT_FULL_EDGES:
            msg = f"{target.identifier}: unexpected edge {full_key[0]} -> {full_key[2]}"
            raise ValueError(msg)

        key = _edge_key(edge)
        if key in seen:
            msg = f"{target.identifier}: duplicate edge {key[0]} -> {key[1]}"
            raise ValueError(msg)
        seen.add(key)

    missing_edges = sorted(target.expected_edges - seen - target.inferred_edges)
    if missing_edges:
        missing = ", ".join(f"{subject} -> {object_}" for subject, object_ in missing_edges)
        msg = f"{target.identifier}: missing edge(s): {missing}"
        raise ValueError(msg)

    updates = target.edge_updates
    graph["edges"] = [
        _ordered_edge(
            {
                "subject": subject,
                "predicate": updates[(subject, object_)].predicate,
                "predicate_id": updates[(subject, object_)].predicate_id,
                "object": object_,
                "description": updates[(subject, object_)].description,
                "evidence": [
                    copy.deepcopy(item) for item in updates[(subject, object_)].evidence
                ],
            }
        )
        for subject, object_ in EDGE_ORDER
    ]


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
        "Curated resistance-causation graph for efflux-pump activation. The graph "
        "replaces stale archetype evidence and grounds the named efflux pump and "
        "transcriptional activation nodes."
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
        raise ValueError(f"{path}: not a direct efflux-activator target: {identifier}")
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
        help="ARO directory or one direct efflux-activator target YAML file",
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
