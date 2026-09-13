from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_dnaa_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_dnaa_graphs", SCRIPT)
    assert spec is not None
    assert isinstance(spec.loader, SourceFileLoader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R = _load()

LABELS = {
    "ARO:3000248": "DnaA",
    "ARO:3004244": "DnaA chromosomal replication initiation protein",
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
                "snippet": "stale unrelated RNA-polymerase target-protection evidence",
            }
        ],
    }


def _record(identifier: str = R.PARENT_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": (
            R.PARENT_DEFINITION
            if identifier == R.PARENT_IDENTIFIER
            else R.CHILD_DEFINITION
        ),
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
                        "label": "bacterial RNA polymerase",
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
                        "causally upstream of (inhibits transcription)",
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


def test_target_set_matches_exact_hidden_no_ignore_dnaa_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == {
        "dnaa-aro3000248.yaml",
        "dnaa-chromosomal-replication-initiation-protein-aro3004244.yaml",
    }


@pytest.mark.parametrize("identifier", sorted(LABELS))
def test_dnaa_records_replace_helr_seed_with_dnaa_graph(identifier: str) -> None:
    target = R.TARGETS[identifier]
    out, changed = R.enrich_record(_record(identifier), target)
    graph = out["causal_graphs"][0]
    nodes = _nodes_by_id(out)

    assert changed
    assert list(nodes) == [
        "determinant",
        "mech0",
        "drug0",
        "dna_replication",
        "rnap_binding",
        "surplus",
        "inhibited",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    assert "rnap" not in nodes
    assert nodes["dna_replication"]["grounding"] == "GO:0006270"
    assert nodes["rnap_binding"]["grounding"] == "GO:0043175"
    assert all(
        evidence["reference"] != _stale_reference()
        for edge in graph["edges"]
        for evidence in edge["evidence"]
    )


def test_dnaa_graph_keeps_surplus_and_binding_causally_explicit() -> None:
    target = R.TARGETS[R.CHILD_IDENTIFIER]
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert {
        ("determinant", "RO:0002327", "dna_replication"),
        ("determinant", "RO:0002327", "rnap_binding"),
        ("determinant", "RO:0000086", "surplus"),
        ("rnap_binding", "RO:0002212", "inhibited"),
        ("surplus", "RO:0002212", "inhibited"),
        ("surplus", "RO:0002411", "resistance"),
    } <= _edge_keys(out)
    assert "origin" in _nodes_by_id(out)["surplus"]["description"]


def test_all_non_state_nodes_are_grounded_and_edges_described() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        for node in graph["nodes"]:
            if node["node_type"] != "STATE":
                assert node.get("grounding")
        assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_have_snippets_and_multiple_references() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        for edge in out["causal_graphs"][0]["edges"]:
            references = {
                evidence["reference"]
                for evidence in edge["evidence"]
                if evidence.get("reference")
            }
            assert len(references) > 1
            assert any(evidence.get("snippet") for evidence in edge["evidence"])


def test_rejects_unexpected_edges() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("surplus", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge surplus -> unmodeled"):
        R.enrich_record(record, R.TARGETS[record["identifier"]])


def test_enrich_text_appends_history_once_and_is_idempotent(tmp_path: Path) -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    path = tmp_path / target.filename
    text = yaml.safe_dump(_record(target.identifier), sort_keys=False)

    out, changed = R.enrich_text(text, path)
    second, changed_again = R.enrich_text(out, path)

    assert changed
    assert not changed_again
    assert second == out
    assert out.count(R.HISTORY_ACTION) == 1
