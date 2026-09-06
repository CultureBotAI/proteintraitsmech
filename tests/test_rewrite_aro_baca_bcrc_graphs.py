from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_baca_bcrc_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_baca_bcrc_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


B = _load()


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
                "reference": B.BAC_A_IDENTIFIER,
                "snippet": B.BAC_A_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = B.BAC_A_IDENTIFIER) -> dict:
    target = B.TARGETS[identifier]
    return {
        "identifier": identifier,
        "label": target.filename,
        "definition": target.own_definition["snippet"],
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
                        "label": target.identifier,
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "restructuring of bacterial cell wall",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000213",
                    },
                    {
                        "node_id": "drug0",
                        "label": "peptide antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3000053",
                    },
                    {
                        "node_id": "upp",
                        "label": "undecaprenyl pyrophosphate",
                        "node_type": "CHEMICAL",
                        "description": "Ungrounded: no CHEBI id verified.",
                    },
                    {
                        "node_id": "recycling",
                        "label": "undecaprenyl pyrophosphate recycling / dephosphorylation",
                        "node_type": "MOLECULAR_FUNCTION",
                        "description": "Ungrounded: not looked up.",
                    },
                    {
                        "node_id": "wall",
                        "label": "peptidoglycan biosynthetic process",
                        "node_type": "BIOLOGICAL_PROCESS",
                        "grounding": "GO:0009252",
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
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge(
                        "determinant",
                        "recycling",
                        "enables (recycles the lipid carrier)",
                        "RO:0002327",
                    ),
                    _edge(
                        "recycling",
                        "upp",
                        "has input (the lipid carrier)",
                        "RO:0002233",
                    ),
                    _edge(
                        "recycling",
                        "wall",
                        "part of (cell wall biosynthesis)",
                        "BFO:0000050",
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


def test_target_set_matches_baca_bcrc_records() -> None:
    assert {target.identifier for target in B.TARGETS.values()} == {
        "ARO:3002986",
        "ARO:3003250",
    }
    assert {target.filename for target in B.TARGETS.values()} == {
        "baca-aro3002986.yaml",
        "bcrc-aro3003250.yaml",
    }


@pytest.mark.parametrize("target", B.TARGETS.values(), ids=lambda target: target.identifier)
def test_baca_bcrc_records_ground_recycling_and_remove_upp(
    target: B.Target,
) -> None:
    out, changed = B.enrich_record(_record(target.identifier), target)

    assert changed
    assert _edge_keys(out) == B.EXPECTED_EDGE_KEYS
    graph = out["causal_graphs"][0]
    assert [node["node_id"] for node in graph["nodes"]] == [
        "determinant",
        "mech0",
        "drug0",
        "recycling",
        "wall",
        "resistance",
    ]
    recycling = next(node for node in graph["nodes"] if node["node_id"] == "recycling")
    assert recycling["grounding"] == "GO:0050380"
    assert "node_id: upp" not in yaml.safe_dump(out)


def test_all_output_nodes_are_grounded_and_edges_described() -> None:
    for target in B.TARGETS.values():
        out, changed = B.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        assert all(node.get("grounding") for node in graph["nodes"])
        assert all(edge.get("description") for edge in graph["edges"])


def test_drug_edges_are_multi_evidenced() -> None:
    for target in B.TARGETS.values():
        out, changed = B.enrich_record(_record(target.identifier), target)

        assert changed
        drug_edge = next(
            edge
            for edge in out["causal_graphs"][0]["edges"]
            if edge["object"] == "drug0"
        )
        assert len({item["reference"] for item in drug_edge["evidence"]}) > 1


def test_recycling_edge_has_go_definition_evidence() -> None:
    out, changed = B.enrich_record(_record(), B.TARGETS[B.BAC_A_IDENTIFIER])

    assert changed
    recycling_edge = next(
        edge
        for edge in out["causal_graphs"][0]["edges"]
        if edge["object"] == "recycling"
    )
    assert "GO:0050380" in {item["reference"] for item in recycling_edge["evidence"]}


def test_enrich_record_is_idempotent() -> None:
    target = B.TARGETS[B.BAC_A_IDENTIFIER]
    once, changed = B.enrich_record(_record(target.identifier), target)
    twice, changed_again = B.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3002986, found ARO:3003250"):
        B.enrich_record(_record("ARO:3003250"), B.TARGETS["ARO:3002986"])


def test_unexpected_edges_are_refused() -> None:
    target = B.TARGETS[B.BAC_A_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "upp"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> upp"):
        B.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = B.TARGETS[B.BAC_A_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        B.enrich_record(record, target)


def test_missing_edges_are_refused() -> None:
    target = B.TARGETS[B.BAC_A_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "wall"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        B.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = B.TARGETS["ARO:3003250"]
    enriched, changed = B.enrich_record(_record(target.identifier), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = B.enrich_text(text, ARO_DIR / target.filename)
    again, changed_again = B.enrich_text(out, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(B.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
@pytest.mark.parametrize("target", B.TARGETS.values(), ids=lambda target: target.identifier)
def test_shipped_targets_are_enriched_in_memory_without_unexpected_edges(
    target: B.Target,
) -> None:
    path = ARO_DIR / target.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = B.enrich_record(record, target)

    assert changed or out == record
    assert _edge_keys(out) == B.EXPECTED_EDGE_KEYS
