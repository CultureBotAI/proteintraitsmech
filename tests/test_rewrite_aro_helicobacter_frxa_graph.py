from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_helicobacter_frxa_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_helicobacter_frxa_graph", SCRIPT)
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
    object_: str,
    predicate: str = "causally upstream of",
    predicate_id: str = "RO:0002411",
) -> dict:
    if predicate_id == "ARO:2000001":
        evidence = [
            {
                "reference": "ARO:3007056",
                "snippet": (
                    "relationship: confers_resistance_to_drug_class "
                    "ARO:3004115 ! nitroimidazole antibiotic"
                ),
            }
        ]
    else:
        evidence = [
            {
                "reference": "ARO:test",
                "snippet": "Test H. pylori frxA evidence.",
            }
        ]

    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": evidence,
    }


def _record(identifier: str = R.TARGET_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "Helicobacter pylori frxA mutation conferring resistance to metronidazole",
        "definition": (
            "FrxA encodes an NADH-flavin oxidoreductase in Helicobacter pylori. "
            "Mutations in this gene confer resistance to nitrofuran antibiotics "
            "and metronidazole."
        ),
        "evidence": [
            {
                "reference": "DOI:10.2147/IDR.S235615",
                "notes": "PMID:32099422 (aro citation)",
            }
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:3000212"),
                    _node("drug0", "CHEMICAL", "ARO:3004115"),
                    _node("activity", "MOLECULAR_FUNCTION"),
                    _node("resistance", "PHENOTYPE", "GO:0046677"),
                ],
                "edges": [
                    _edge(
                        "determinant",
                        "mech0",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech0", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "drug0",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge("determinant", "activity", "enables", "RO:0002327"),
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
    return {
        node["node_id"]: node
        for node in record["causal_graphs"][0]["nodes"]
    }


def test_iter_target_paths_is_exact_frxa_target() -> None:
    assert R.iter_target_paths(ARO_DIR) == [ARO_DIR / R.TARGET_FILENAME]
    assert R.iter_target_paths(ARO_DIR / R.TARGET_FILENAME) == [ARO_DIR / R.TARGET_FILENAME]


def test_rewrite_removes_ungrounded_activity_node() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    assert _edge_keys(out) == R.CORE_EDGE_KEYS
    assert "activity" not in _nodes_by_id(out)
    assert all(edge.get("description") for edge in out["causal_graphs"][0]["edges"])


def test_record_specific_aro_citation_is_preserved() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert {
            "reference": "DOI:10.2147/IDR.S235615",
            "notes": "PMID:32099422 (aro citation)",
        } in edge["evidence"]


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3007059, found ARO:3000000"):
        R.enrich_record(_record("ARO:3000000"))


def test_missing_required_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node for node in record["causal_graphs"][0]["nodes"] if node["node_id"] != "mech0"
    ]

    with pytest.raises(ValueError, match="missing node\\(s\\): mech0"):
        R.enrich_record(record)


def test_missing_aro_drug_relation_evidence_is_refused() -> None:
    record = _record()
    for edge in record["causal_graphs"][0]["edges"]:
        if edge["predicate_id"] == "ARO:2000001":
            edge["evidence"] = []

    with pytest.raises(ValueError, match="missing ARO drug-relation evidence"):
        R.enrich_record(record)


def test_wrong_path_is_refused() -> None:
    with pytest.raises(ValueError, match="not the H. pylori frxA metronidazole target"):
        R.enrich_text(yaml.safe_dump(_record(), sort_keys=False), ARO_DIR / "rdxa-aro3000000.yaml")


def test_enrich_text_adds_history_once() -> None:
    path = ARO_DIR / R.TARGET_FILENAME
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once
