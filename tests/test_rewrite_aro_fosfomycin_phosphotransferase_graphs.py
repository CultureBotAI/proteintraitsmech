from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_fosfomycin_phosphotransferase_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_fosfomycin_phosphotransferase_graphs",
        SCRIPT,
    )
    assert spec is not None
    assert isinstance(spec.loader, SourceFileLoader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R = _load()


LABELS = {
    "ARO:3000359": "fosfomycin phosphotransferase",
    "ARO:3004245": "fosC phosphotransferase family",
    "ARO:3000380": "FosC",
    "ARO:3002874": "FosC2",
    "ARO:3004246": "Fom phosphotransferase family",
    "ARO:3000423": "FomA",
    "ARO:3000449": "FomB",
}


DEFINITIONS = {
    "ARO:3000359": R.PHOSPHOTRANSFERASE_DEFINITION,
    "ARO:3004245": R.FOSC_DEFINITION,
    "ARO:3000380": "FosC is an enzyme that phosphorylates fosfomycin to confer resistance.",
    "ARO:3002874": (
        "FosC2 is an enzyme that phosphorylates fosfomycin to confer resistance in "
        "Escherichia coli."
    ),
    "ARO:3004246": R.FOM_DEFINITION,
    "ARO:3000423": R.PHOSPHOTRANSFERASE_DEFINITION,
    "ARO:3000449": (
        "An enzyme which on its own cannot provide fosfomycin resistance, however "
        "in conjunction with FomA, it leads to the formation of fosfomycin with "
        "three phosphates total, which makes it inactive."
    ),
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
                "reference": "ARO:3000105",
                "snippet": R.PHOSPHORYLATION_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = R.PHOSPHOTRANSFERASE_PARENT) -> dict:
    target = R.TARGETS[identifier]
    nodes = [
        {
            "node_id": "determinant",
            "label": LABELS[identifier],
            "node_type": "PROTEIN",
            "grounding": identifier,
        },
        {
            "node_id": "mech0",
            "label": "antibiotic inactivation",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:0001004",
        },
        {
            "node_id": "mech1",
            "label": "phosphorylation of antibiotic conferring resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000105",
        },
        {
            "node_id": "transfer",
            "label": "antibiotic phosphotransferase activity",
            "node_type": "MOLECULAR_FUNCTION",
            "description": "Ungrounded.",
        },
        {
            "node_id": "modified",
            "label": "chemically modified, inactive antibiotic",
            "node_type": "STATE",
            "description": "The product state. Ungrounded.",
        },
        {
            "node_id": "resistance",
            "label": "antibiotic resistance phenotype",
            "node_type": "PHENOTYPE",
            "grounding": "GO:0046677",
        },
    ]
    edges = [
        _edge(
            "determinant",
            "mech0",
            "participates in (resistance mechanism)",
            "RO:0000056",
        ),
        _edge("mech0", "resistance"),
        _edge(
            "determinant",
            "mech1",
            "participates in (resistance mechanism)",
            "RO:0000056",
        ),
        _edge("mech1", "resistance"),
        _edge(
            "determinant",
            "resistance",
            "causally upstream of (confers resistance)",
        ),
        _edge(
            "determinant",
            "transfer",
            "enables (modifies the drug)",
            "RO:0002327",
        ),
        _edge(
            "transfer",
            "modified",
            "causally upstream of (inactivates the drug)",
        ),
    ]
    if target.has_drug:
        nodes.insert(3, R.DRUG_NODE)
        edges.insert(
            5,
            _edge(
                "determinant",
                "drug0",
                "confers resistance to (drug class)",
                "ARO:2000001",
            ),
        )
        edges.insert(
            7,
            _edge(
                "transfer",
                "drug0",
                "has input (the drug)",
                "RO:0002233",
            ),
        )

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
                "nodes": nodes,
                "edges": edges,
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


def test_target_set_matches_exact_hidden_no_ignore_phosphotransferase_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == {
        "fosfomycin-phosphotransferase-aro3000359.yaml",
        "fosc-phosphotransferase-family-aro3004245.yaml",
        "fosc-aro3000380.yaml",
        "fosc2-aro3002874.yaml",
        "fom-phosphotransferase-family-aro3004246.yaml",
        "foma-aro3000423.yaml",
        "fomb-aro3000449.yaml",
    }


@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_phosphotransferase_records_replace_transfer_with_grounded_mech1(
    target: R.Target,
) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)
    nodes = _nodes_by_id(out)

    assert changed
    assert _edge_keys(out) == R._expected_edge_keys(target)
    assert "transfer" not in nodes
    assert nodes["modified"]["node_type"] == "STATE"
    assert ("mech1", "RO:0002411", "modified") in _edge_keys(out)
    if target.has_drug:
        assert ("mech1", "RO:0002233", "drug0") in _edge_keys(out)
    else:
        assert "drug0" not in nodes


@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_edges_are_described_and_supported_by_multiple_references(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        references = {item["reference"] for item in edge["evidence"]}
        assert len(references) > 1
        assert target.identifier in references
        assert R.PHOSPHOTRANSFERASE_PARENT in references


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS["ARO:3000380"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000359, found ARO:3000380"):
        R.enrich_record(_record("ARO:3000380"), R.TARGETS[R.PHOSPHOTRANSFERASE_PARENT])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("transfer", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge transfer -> unmodeled"):
        R.enrich_record(record, R.TARGETS[R.PHOSPHOTRANSFERASE_PARENT])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record, R.TARGETS[R.PHOSPHOTRANSFERASE_PARENT])
