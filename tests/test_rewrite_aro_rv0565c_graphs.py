from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rv0565c_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_rv0565c_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


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
                "snippet": R.PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = R.PARENT_IDENTIFIER) -> dict:
    target = R.TARGETS[identifier]
    nodes = [
        {
            "node_id": "determinant",
            "label": target.identifier,
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
            "node_id": "activity",
            "label": "monooxygenase activity",
            "node_type": "MOLECULAR_FUNCTION",
            "description": (
                "The one functional fact CARD's naming supplies. Ungrounded: "
                "not looked up rather than guessed."
            ),
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
            "resistance",
            "causally upstream of (confers resistance)",
        ),
        _edge(
            "determinant",
            "activity",
            "enables (monooxygenase activity)",
            "RO:0002327",
        ),
    ]
    if target.has_drug:
        nodes.insert(
            2,
            {
                "node_id": "drug0",
                "label": "thioamide antibiotic",
                "node_type": "CHEMICAL",
                "grounding": "ARO:3007156",
            },
        )
        edges.insert(
            3,
            _edge(
                "determinant",
                "drug0",
                "confers resistance to (drug class)",
                "ARO:2000001",
            ),
        )

    return {
        "identifier": identifier,
        "label": "Rv0565c",
        "definition": R.PARENT_EVIDENCE["snippet"],
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


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_target_set_matches_exact_rv0565c_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == {
        "ARO:3004953",
        "ARO:3004954",
        "ARO:3004955",
    }
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-rv0565c-aro3004953.yaml",
        "ethionamide-resistant-rv0565c-aro3004954.yaml",
        "mycobacterium-tuberculosis-rv0565c-mutation-conferring-resistance-to-ethionamide-aro3004955.yaml",
    }


@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_rv0565c_records_ground_monooxygenase_without_new_resistance_route(
    target: R.Target,
) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _edge_keys(out) == R._expected_edge_keys(target)
    assert _node_ids(out) == (
        ["determinant", "mech0", "drug0", "activity", "resistance"]
        if target.has_drug
        else ["determinant", "mech0", "activity", "resistance"]
    )
    graph = out["causal_graphs"][0]
    activity = next(node for node in graph["nodes"] if node["node_id"] == "activity")
    assert activity["grounding"] == "GO:0004497"
    assert {
        (edge["subject"], edge["object"])
        for edge in graph["edges"]
        if edge["subject"] == "activity" or edge["object"] == "activity"
    } == {("determinant", "activity")}


def test_all_output_nodes_are_grounded_and_edges_described() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        assert all(node.get("grounding") for node in graph["nodes"])
        assert all(edge.get("description") for edge in graph["edges"])


def test_mutation_edges_inherit_broad_aro_mutation_evidence() -> None:
    out, changed = R.enrich_record(_record(R.PARENT_IDENTIFIER), R.TARGETS[R.PARENT_IDENTIFIER])

    assert changed
    for edge in out["causal_graphs"][0]["edges"][:3]:
        assert "ARO:3000212" in {item["reference"] for item in edge["evidence"]}


def test_drug_edges_are_multi_evidenced() -> None:
    for identifier in ("ARO:3004954", "ARO:3004955"):
        out, changed = R.enrich_record(_record(identifier), R.TARGETS[identifier])

        assert changed
        drug_edge = next(
            edge
            for edge in out["causal_graphs"][0]["edges"]
            if edge["object"] == "drug0"
        )
        assert len({item["reference"] for item in drug_edge["evidence"]}) > 1


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004953, found ARO:3004954"):
        R.enrich_record(_record("ARO:3004954"), R.TARGETS["ARO:3004953"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("activity", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge activity -> resistance"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        R.enrich_record(record, target)


def test_missing_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "activity"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3004954"]
    enriched, changed = R.enrich_record(_record(target.identifier), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)
    again, changed_again = R.enrich_text(out, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(
    target: R.Target,
) -> None:
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(record, target)

    assert changed or out == record
    assert _edge_keys(out) == R._expected_edge_keys(target)
