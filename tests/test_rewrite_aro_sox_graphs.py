from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_sox_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_sox_graphs", SCRIPT)
    assert spec is not None
    assert isinstance(spec.loader, SourceFileLoader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R = _load()


LABELS = {
    "ARO:3000836": "soxR",
    "ARO:3000837": "soxS",
    "ARO:3003381": "Escherichia coli soxR with mutation conferring antibiotic resistance",
    "ARO:3003382": "Salmonella enterica soxR with mutation conferring antibiotic resistance",
    "ARO:3003383": "Salmonella serovars soxS with mutation conferring antibiotic resistance",
    "ARO:3003511": "Escherichia coli soxS with mutation conferring antibiotic resistance",
    "ARO:3004107": "Pseudomonas aeruginosa soxR",
}


DEFINITIONS = {
    "ARO:3000836": R.SOXR_DEFINITION,
    "ARO:3003381": (
        "SoxR is a sensory protein that upregulates soxS expression in the presence "
        "of redox-cycling drugs. This stress response leads to the expression many "
        "multidrug efflux pumps."
    ),
    "ARO:3003382": (
        "SoxR is a sensory protein that upregulates soxS expression in the presence "
        "of redox-cycling drugs. This stress response leads to the expression of many "
        "multidrug efflux pumps."
    ),
    "ARO:3004107": (
        "SoxR is a redox-sensitive transcriptional activator that induces expression "
        "of a small regulon that includes the RND efflux pump-encoding operon "
        "mexGHI-opmD. SoxR was shown to be activated by pyocyanin."
    ),
    "ARO:3000837": R.SOXS_DEFINITION,
    "ARO:3003383": R.SOXS_DEFINITION,
    "ARO:3003511": R.SOXS_DEFINITION,
}


def _edge(
    subject: str,
    object_: str,
    predicate: str = "causally upstream of",
    predicate_id: str = "RO:0002411",
) -> dict:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [
            {
                "reference": "ARO:3000219",
                "snippet": R.MUTANT_REGULATOR_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = "ARO:3000836") -> dict:
    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": DEFINITIONS[identifier],
        "mapping_status": "REVIEWED",
        "evidence": [
            {
                "reference": "DOI:test",
                "notes": "PMID:test (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": LABELS[identifier],
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "mutation conferring antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000212",
                    },
                    {
                        "node_id": "pump_expression",
                        "label": "expression of efflux pump proteins",
                        "node_type": "BIOLOGICAL_PROCESS",
                        "description": "The regulated quantity. Ungrounded.",
                    },
                    {
                        "node_id": "efflux_process",
                        "label": "antibiotic efflux",
                        "node_type": "BIOLOGICAL_PROCESS",
                        "grounding": "ARO:0010000",
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
                ],
                "edges": [
                    _edge(
                        "determinant",
                        "mech0",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech0", "resistance"),
                    _edge(
                        "determinant",
                        "resistance",
                        "causally upstream of (confers resistance)",
                    ),
                    _edge(
                        "determinant",
                        "pump_expression",
                        "positively regulates (mutation raises pump expression)",
                        "RO:0002213",
                    ),
                    _edge(
                        "pump_expression",
                        "efflux_process",
                        "causally upstream of (more pump, more efflux)",
                    ),
                    _edge(
                        "efflux_process",
                        "resistance",
                        "causally upstream of (confers resistance)",
                    ),
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _nodes_by_id(record: dict) -> dict[str, dict]:
    return {node["node_id"]: node for node in record["causal_graphs"][0]["nodes"]}


def test_target_set_matches_exact_hidden_no_ignore_sox_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == {
        "soxr-aro3000836.yaml",
        "soxs-aro3000837.yaml",
        "escherichia-coli-soxr-with-mutation-conferring-antibiotic-resistance-aro3003381.yaml",
        "escherichia-coli-soxs-with-mutation-conferring-antibiotic-resistance-aro3003511.yaml",
        "salmonella-enterica-soxr-with-mutation-conferring-antibiotic-resistance-aro3003382.yaml",
        "salmonella-serovars-soxs-with-mutation-conferring-antibiotic-resistance-aro3003383.yaml",
        "pseudomonas-aeruginosa-soxr-aro3004107.yaml",
    }


@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_sox_records_keep_efflux_chain_with_a_described_local_state(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)
    nodes = _nodes_by_id(out)

    assert changed
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    assert list(nodes) == [
        "determinant",
        "mech0",
        "pump_expression",
        "efflux_process",
        "resistance",
    ]
    assert nodes["pump_expression"] == target.pump_expression_node
    assert nodes["efflux_process"]["grounding"] == "ARO:0010000"


@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_edges_are_described_and_supported_by_exact_sox_evidence(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        references = {item["reference"] for item in edge["evidence"]}
        assert len(references) > 1
        assert target.identifier in references
        assert target.parent_identifier in references
        assert "ARO:3000702" not in references


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS["ARO:3004107"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000836, found ARO:3000837"):
        R.enrich_record(_record("ARO:3000837"), R.TARGETS["ARO:3000836"])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("pump_expression", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge pump_expression -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3000836"])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record, R.TARGETS["ARO:3000836"])
