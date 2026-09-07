from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_baha_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_baha_graph", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _node(node_id: str, node_type: str, grounding: str | None = None) -> dict:
    node = {
        "node_id": node_id,
        "label": node_id,
        "node_type": node_type,
    }
    if grounding:
        node["grounding"] = grounding
    return node


def _edge(
    subject: str,
    predicate_id: str,
    object_: str,
    predicate: str = "causally upstream of",
) -> dict:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [
            {
                "reference": R.TARGET_IDENTIFIER,
                "snippet": R.AMIDOHYDROLYSIS_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = R.TARGET_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "BahA",
        "definition": (
            "Bacitracin amidohydrolase found in Paenibacillus sp. LC231. "
            "Confers resistance by bacitracin inactivation through "
            "amidohydrolysis."
        ),
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3003985"),
                    _node("drug0", "CHEMICAL", "ARO:3000053"),
                    _node("transfer", "MOLECULAR_FUNCTION"),
                    _node("modified", "STATE"),
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                ],
                "edges": [
                    _edge(
                        "determinant",
                        "RO:0000056",
                        "mech0",
                        "participates in (resistance mechanism)",
                    ),
                    _edge("mech0", "RO:0002411", "resistance"),
                    _edge(
                        "determinant",
                        "RO:0000056",
                        "mech1",
                        "participates in (resistance mechanism)",
                    ),
                    _edge("mech1", "RO:0002411", "resistance"),
                    _edge("determinant", "RO:0002411", "resistance"),
                    _edge(
                        "determinant",
                        "ARO:2000001",
                        "drug0",
                        "confers resistance to (drug class)",
                    ),
                    _edge(
                        "determinant",
                        "RO:0002327",
                        "transfer",
                        "enables (modifies the drug)",
                    ),
                    _edge(
                        "transfer",
                        "RO:0002233",
                        "drug0",
                        "has input (the drug)",
                    ),
                    _edge(
                        "transfer",
                        "RO:0002411",
                        "modified",
                        "causally upstream of (inactivates the drug)",
                    ),
                ],
            }
        ],
    }


def _edge_pairs(record: dict) -> set[tuple[str, str]]:
    return {
        (edge["subject"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def test_target_is_exactly_baha() -> None:
    assert R.TARGET_IDENTIFIER == "ARO:3003984"
    assert R.TARGET_FILENAME == "baha-aro3003984.yaml"
    assert R.iter_target_paths(ARO_DIR) == [ARO_DIR / R.TARGET_FILENAME]


def test_rewrite_replaces_transfer_with_bacitracin_amidohydrolysis() -> None:
    out, changed = R.enrich_record(_record())
    graph = out["causal_graphs"][0]

    assert changed
    assert _edge_pairs(out) == {
        ("determinant", "mech0"),
        ("mech0", "resistance"),
        ("determinant", "resistance"),
        ("determinant", "drug0"),
        ("determinant", "modification"),
        ("modification", "drug0"),
        ("modification", "inactivated"),
        ("inactivated", "resistance"),
    }
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["modification"] == R.AMIDOHYDROLYSIS_NODE
    assert by_node["inactivated"] == R.INACTIVATED_NODE
    assert "transfer" not in by_node
    assert "modified" not in by_node


def test_all_non_state_nodes_are_grounded_and_all_edges_are_complete() -> None:
    out, changed = R.enrich_record(_record())
    graph = out["causal_graphs"][0]

    assert changed
    for node in graph["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")
        else:
            assert node.get("description")
    for edge in graph["edges"]:
        references = {item["reference"] for item in edge["evidence"]}
        assert edge["description"]
        assert len(references) > 1


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGET_FILENAME

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_CURATOR) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003984, found ARO:3004260"):
        R.enrich_record(_record("ARO:3004260"))


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] != "mech0"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): mech0"):
        R.enrich_record(record)


def test_missing_transfer_or_modification_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node
        for node in record["causal_graphs"][0]["nodes"]
        if node["node_id"] not in {"modification", "transfer"}
    ]

    with pytest.raises(ValueError, match="missing modification or transfer node"):
        R.enrich_record(record)


def test_unexpected_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        _edge("drug0", "RO:0002411", "resistance"),
    )

    with pytest.raises(ValueError, match="unexpected edge drug0 -> resistance"):
        R.enrich_record(record)


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_rewritten_in_memory() -> None:
    path = ARO_DIR / R.TARGET_FILENAME
    record = yaml.safe_load(path.read_text(encoding="utf-8"))

    out, changed = R.enrich_record(copy.deepcopy(record))

    assert changed or out == record
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])
