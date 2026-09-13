from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_rv0678_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_rv0678_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

LABELS = {
    "ARO:3007672": "antibiotic resistant Rv0678",
    "ARO:3007673": "bedaquiline resistant Rv0678",
    "ARO:3007674": "Mycobacterium tuberculosis Rv0678 with mutation conferring resistance to bedaquiline",
    "ARO:3007853": "clofazimine resistant Rv0678",
    "ARO:3007852": "Mycobacterium tuberculosis Rv0678 with mutation conferring resistance to clofazimine",
}


def _drug_node(identifier: str) -> dict:
    if identifier in {"ARO:3007673", "ARO:3007674"}:
        return {
            "node_id": "drug0",
            "label": "diarylquinoline antibiotic",
            "node_type": "CHEMICAL",
            "grounding": "ARO:3004491",
        }
    return {
        "node_id": "drug0",
        "label": "fluoroquinolone antibiotic",
        "node_type": "CHEMICAL",
        "grounding": "ARO:0000001",
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
        "evidence": [{"reference": R.PARENT_IDENTIFIER, "snippet": R.PARENT_EVIDENCE["snippet"]}],
    }


def _record(identifier: str = R.PARENT_IDENTIFIER) -> dict:
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
        {
            "node_id": "pump_expression",
            "label": "expression of the mmpS5/L5 efflux pump",
            "node_type": "BIOLOGICAL_PROCESS",
            "description": "What Rv0678 represses. Ungrounded.",
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
            "pump_expression",
            "negatively regulates (represses pump expression)",
            "RO:0002212",
        ),
    ]
    if identifier != R.PARENT_IDENTIFIER:
        nodes.insert(2, _drug_node(identifier))
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
        "label": LABELS[identifier],
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


def test_target_set_matches_exact_rv0678_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-rv0678-aro3007672.yaml",
        "bedaquiline-resistant-rv0678-aro3007673.yaml",
        "mycobacterium-tuberculosis-rv0678-with-mutation-conferring-resistance-to-bedaqui-aro3007674.yaml",
        "clofazimine-resistant-rv0678-aro3007853.yaml",
        "mycobacterium-tuberculosis-rv0678-with-mutation-conferring-resistance-to-clofazi-aro3007852.yaml",
    }


@pytest.mark.parametrize("target", R.TARGETS.values(), ids=lambda target: target.identifier)
def test_rv0678_records_keep_the_conservative_repression_shape(target: R.Target) -> None:
    out, changed = R.enrich_record(_record(target.identifier), target)

    assert changed
    assert _edge_keys(out) == R._expected_edge_keys(target)
    assert any(
        edge["object"] == "pump_expression" and edge["predicate_id"] == "RO:0002212"
        for edge in out["causal_graphs"][0]["edges"]
    )
    assert not any(
        edge["subject"] == "pump_expression" and edge["predicate_id"] == "RO:0002411"
        for edge in out["causal_graphs"][0]["edges"]
    )
    assert all(
        "Ungrounded" not in node.get("description", "")
        for node in out["causal_graphs"][0]["nodes"]
    )


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        for edge in out["causal_graphs"][0]["edges"]:
            assert edge["description"]
            assert len({item["reference"] for item in edge["evidence"]}) > 1
            assert any(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3007672, found ARO:3007673"):
        R.enrich_record(_record("ARO:3007673"), R.TARGETS["ARO:3007672"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("pump_expression", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge pump_expression -> resistance"):
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
        if edge["object"] != "pump_expression"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3007673"]
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
