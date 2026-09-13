from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_fabg1_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_fabg1_graphs", SCRIPT)
    assert spec is not None
    assert isinstance(spec.loader, SourceFileLoader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


R = _load()

LABELS = {
    "ARO:3004887": "antibiotic resistant fabG1",
    "ARO:3004888": "ethionamide resistant fabG1",
    "ARO:3004895": "isoniazid resistant fabG1",
    "ARO:3004922": "Mycobacterium tuberculosis fabG1 mutations confer resistance to isoniazid",
    "ARO:3004933": "Mycobacterium tuberculosis fabG1 mutation conferring resistance to ethionamide",
    "ARO:3007811": "Mycobacterium tuberculosis fabG1 with mutations conferring resistance to prothionamide",
    "ARO:3007841": "prothionamide resistant fabG1",
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
                "reference": R.PARENT_IDENTIFIER,
                "snippet": R.PARENT_DEFINITION,
            }
        ],
    }


def _record(identifier: str = R.PARENT_IDENTIFIER) -> dict:
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
            "label": "mutation conferring antibiotic resistance",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:3000212",
        },
    ]
    if target.has_drug:
        nodes.append(
            {
                "node_id": "drug0",
                "label": target.drug_label,
                "node_type": "CHEMICAL",
                "grounding": target.drug_identifier,
            }
        )
    nodes.extend(
        [
            {
                "node_id": "fas_step",
                "label": "first reduction step of mycolic acid synthesis (FabG1/MabA)",
                "node_type": "MOLECULAR_FUNCTION",
            },
            {
                "node_id": "mycolic",
                "label": "mycolic acid biosynthetic process",
                "node_type": "BIOLOGICAL_PROCESS",
                "grounding": "GO:0071768",
            },
            {
                "node_id": "inhibition",
                "label": "drug inhibition of mycolic acid synthesis",
                "node_type": "STATE",
            },
            {
                "node_id": "resistance",
                "label": "antibiotic resistance phenotype",
                "node_type": "PHENOTYPE",
                "grounding": "GO:0046677",
            },
        ]
    )

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
            "resistance",
            "causally upstream of (confers resistance)",
        ),
    ]
    if target.has_drug:
        edges.extend(
            [
                _edge(
                    "determinant",
                    "drug0",
                    "confers resistance to",
                    "ARO:2000001",
                ),
                _edge(
                    "drug0",
                    "inhibition",
                    "causally upstream of",
                    "RO:0002411",
                ),
            ]
        )
    edges.extend(
        [
            _edge(
                "determinant",
                "fas_step",
                "enables (the first reduction step)",
                "RO:0002327",
            ),
            _edge(
                "fas_step",
                "mycolic",
                "part of (mycolic acid biosynthesis)",
                "BFO:0000050",
            ),
            _edge(
                "determinant",
                "inhibition",
                "negatively regulates",
                "RO:0002212",
            ),
        ]
    )

    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": R.PARENT_DEFINITION,
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


def test_target_set_matches_exact_hidden_no_ignore_fabg1_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-fabg1-aro3004887.yaml",
        "ethionamide-resistant-fabg1-aro3004888.yaml",
        "isoniazid-resistant-fabg1-aro3004895.yaml",
        "mycobacterium-tuberculosis-fabg1-mutation-conferring-resistance-to-ethionamide-aro3004933.yaml",
        "mycobacterium-tuberculosis-fabg1-mutations-confer-resistance-to-isoniazid-aro3004922.yaml",
        (
            "mycobacterium-tuberculosis-fabg1-with-mutations-conferring-"
            "resistance-to-prothio-aro3007811.yaml"
        ),
        "prothionamide-resistant-fabg1-aro3007841.yaml",
    }


@pytest.mark.parametrize("identifier", sorted(LABELS))
def test_fabg1_records_ground_first_reduction_step(identifier: str) -> None:
    target = R.TARGETS[identifier]
    out, changed = R.enrich_record(_record(identifier), target)
    nodes = _nodes_by_id(out)

    assert changed
    assert "fas_step" not in nodes
    assert nodes["fabg1_activity"]["grounding"] == "GO:0004316"
    assert nodes["inhibition"]["node_type"] == "STATE"
    assert _edge_keys(out) == R._expected_edge_keys(target)


@pytest.mark.parametrize("identifier", sorted(LABELS))
def test_fabg1_drug_nodes_are_conditional_and_specific(identifier: str) -> None:
    target = R.TARGETS[identifier]
    out, changed = R.enrich_record(_record(identifier), target)
    nodes = _nodes_by_id(out)

    assert changed
    if target.has_drug:
        assert nodes["drug0"]["grounding"] == target.drug_identifier
        assert ("determinant", "ARO:2000001", "drug0") in _edge_keys(out)
        assert ("drug0", "RO:0002411", "inhibition") in _edge_keys(out)
    else:
        assert "drug0" not in nodes
        assert ("determinant", "ARO:2000001", "drug0") not in _edge_keys(out)


def test_fabg1_graph_keeps_target_alteration_model() -> None:
    target = R.TARGETS["ARO:3004895"]
    out, changed = R.enrich_record(_record(target.identifier), target)
    graph = out["causal_graphs"][0]

    assert changed
    assert "fabg1_activity" in _nodes_by_id(out)
    assert "inha" not in yaml.safe_dump(graph).lower()
    assert {
        ("determinant", "RO:0002327", "fabg1_activity"),
        ("fabg1_activity", "BFO:0000050", "mycolic"),
        ("determinant", "RO:0002212", "inhibition"),
    } <= _edge_keys(out)


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
    record["causal_graphs"][0]["edges"].append(_edge("fabg1_activity", "unmodeled"))

    with pytest.raises(ValueError, match="unexpected edge fabg1_activity -> unmodeled"):
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
