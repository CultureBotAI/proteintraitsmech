from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rnap_protection_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_rnap_protection_graphs",
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
    "ARO:3007207": "helicase-like RNA polymerase protection protein",
    "ARO:3007208": "HelR",
    "ARO:3004243": "RbpA bacterial RNA polymerase-binding protein",
    "ARO:3000245": "RbpA",
}


DEFINITIONS = {
    R.HEL_PARENT: R.HEL_PARENT_DEFINITION,
    R.HELR: R.HELR_DEFINITION,
    R.RBPA_PARENT: R.RBPA_PARENT_DEFINITION,
    R.RBPA: R.RBPA_DEFINITION,
}


def _stale_reference() -> str:
    return "PMID:" + "35907401"


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
                "reference": _stale_reference(),
                "snippet": "stale HelR-specific RNA-polymerase protection evidence",
            }
        ],
    }


def _record(identifier: str = R.HEL_PARENT) -> dict:
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
                        "label": "antibiotic target protection",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0001003",
                    },
                    {
                        "node_id": "drug0",
                        "label": "rifamycin antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3000157",
                    },
                    {
                        "node_id": "rnap",
                        "label": "bacterial RNA polymerase, the drug's target",
                        "node_type": "PROTEIN",
                    },
                    {
                        "node_id": "inhibited",
                        "label": "rifamycin-inhibited RNA polymerase",
                        "node_type": "STATE",
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
                        "drug0",
                        "confers resistance to",
                        "ARO:2000001",
                    ),
                    _edge(
                        "drug0",
                        "inhibited",
                        "causally upstream of (inhibits RNA polymerase)",
                    ),
                    _edge(
                        "determinant",
                        "rnap",
                        "molecularly interacts with",
                        "RO:0002436",
                    ),
                    _edge(
                        "determinant",
                        "inhibited",
                        "negatively regulates",
                        "RO:0002212",
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


def test_target_set_matches_exact_hidden_no_ignore_rnap_protection_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == {
        "helicase-like-rna-polymerase-protection-protein-aro3007207.yaml",
        "helr-aro3007208.yaml",
        "rbpa-bacterial-rna-polymerase-binding-protein-aro3004243.yaml",
        "rbpa-aro3000245.yaml",
    }


@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_rnap_protection_records_drop_ungrounded_rnap_node(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)
    nodes = _nodes_by_id(out)

    assert changed
    assert list(nodes) == [
        "determinant",
        "mech0",
        "drug0",
        "inhibited",
        "resistance",
    ]
    assert _edge_keys(out) == R.CORE_EDGE_KEYS
    assert "rnap" not in nodes
    assert R.REMOVED_EDGE_KEYS.isdisjoint(_edge_keys(out))
    assert nodes["inhibited"]["node_type"] == "STATE"
    assert nodes["inhibited"]["description"]


def test_rbpa_records_do_not_keep_helr_specific_evidence() -> None:
    for identifier in (R.RBPA_PARENT, R.RBPA):
        out, changed = R.enrich_record(_record(identifier), R.TARGETS[identifier])

        assert changed
        assert all(
            evidence["reference"] != _stale_reference()
            for edge in out["causal_graphs"][0]["edges"]
            for evidence in edge["evidence"]
        )


def test_helr_records_keep_helr_displacement_evidence() -> None:
    for identifier in (R.HEL_PARENT, R.HELR):
        out, changed = R.enrich_record(_record(identifier), R.TARGETS[identifier])

        assert changed
        references = {
            evidence["reference"]
            for edge in out["causal_graphs"][0]["edges"]
            for evidence in edge["evidence"]
        }
        assert R.HEL_DISPLACEMENT_EVIDENCE["reference"] in references


@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_edges_are_described_and_supported_by_multiple_references(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        references = {
            evidence["reference"]
            for evidence in edge["evidence"]
            if evidence.get("reference")
        }
        assert len(references) > 1
        assert target.identifier in references
        assert target.parent_identifier in references


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS[R.HELR]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3007207, found ARO:3007208"):
        R.enrich_record(_record(R.HELR), R.TARGETS[R.HEL_PARENT])


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("rnap", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge rnap -> unmodeled"):
        R.enrich_record(record, R.TARGETS[record["identifier"]])


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record, R.TARGETS[record["identifier"]])


def test_enrich_text_appends_history_once_and_is_idempotent(tmp_path: Path) -> None:
    target = R.TARGETS[R.HEL_PARENT]
    path = tmp_path / target.filename
    text = yaml.safe_dump(_record(target.identifier), sort_keys=False)

    out, changed = R.enrich_text(text, path)
    second, changed_again = R.enrich_text(out, path)

    assert changed
    assert not changed_again
    assert second == out
    assert out.count(R.HISTORY_ACTION) == 1
