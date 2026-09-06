from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_van_ligase_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_van_ligase_graph", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


V = _load()


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
                "reference": V.TARGET_IDENTIFIER,
                "snippet": V.VAN_LIGASE_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = V.TARGET_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "Van ligase",
        "definition": V.VAN_LIGASE_EVIDENCE["snippet"],
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
                        "label": "Van ligase",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "restructuring of bacterial cell wall conferring "
                        "antibiotic resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000213",
                    },
                    {
                        "node_id": "drug0",
                        "label": "glycopeptide antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3000081",
                    },
                    {
                        "node_id": "alt_precursor",
                        "label": "alternative peptidoglycan precursor",
                        "node_type": "CHEMICAL",
                    },
                    {
                        "node_id": "low_affinity",
                        "label": "reduced vancomycin binding affinity",
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
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge(
                        "determinant",
                        "alt_precursor",
                        "enables (synthesis of the alternative substrate)",
                        "RO:0002327",
                    ),
                    _edge(
                        "alt_precursor",
                        "low_affinity",
                        "causally upstream of (reduces drug binding)",
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


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_target_matches_exact_van_ligase_record() -> None:
    assert V.TARGET.identifier == "ARO:3002906"
    assert V.TARGET.filename == "van-ligase-aro3002906.yaml"


def test_van_ligase_rewrites_to_alternative_precursor_route() -> None:
    out, changed = V.enrich_record(_record())

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "alt_precursor",
        "low_affinity",
        "resistance",
    ]
    assert _edge_keys(out) == V.EXPECTED_EDGE_KEYS


def test_alt_precursor_and_low_affinity_are_described_states() -> None:
    out, changed = V.enrich_record(_record())

    assert changed
    graph = out["causal_graphs"][0]
    assert graph["nodes"][3]["node_id"] == "alt_precursor"
    assert graph["nodes"][3]["node_type"] == "STATE"
    assert graph["nodes"][3]["description"]
    assert graph["nodes"][4]["node_id"] == "low_affinity"
    assert graph["nodes"][4]["node_type"] == "STATE"
    assert graph["nodes"][4]["description"]


def test_old_enables_edge_becomes_causal_and_low_affinity_links_to_resistance() -> None:
    out, changed = V.enrich_record(_record())

    assert changed
    assert V.OLD_PRECURSOR_EDGE not in _edge_keys(out)
    assert ("determinant", "RO:0002411", "alt_precursor") in _edge_keys(out)
    assert ("low_affinity", "RO:0002411", "resistance") in _edge_keys(out)


def test_all_non_state_nodes_are_grounded_and_edges_described() -> None:
    out, changed = V.enrich_record(_record())

    assert changed
    graph = out["causal_graphs"][0]
    for node in graph["nodes"]:
        if node["node_type"] != "STATE":
            assert node.get("grounding")
    assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_are_multi_evidenced() -> None:
    out, changed = V.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_enrich_record_is_idempotent() -> None:
    once, changed = V.enrich_record(_record())
    twice, changed_again = V.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3002906, found ARO:3002907"):
        V.enrich_record(_record("ARO:3002907"))


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("low_affinity", "alt_precursor"))

    with pytest.raises(ValueError, match="unexpected edge low_affinity -> alt_precursor"):
        V.enrich_record(record)


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("mech0", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge mech0 -> resistance"):
        V.enrich_record(record)


def test_missing_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "drug0"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        V.enrich_record(record)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    enriched, changed = V.enrich_record(_record())
    assert changed

    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = V.enrich_text(text, ARO_DIR / V.TARGET.filename)
    again, changed_again = V.enrich_text(out, ARO_DIR / V.TARGET.filename)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(V.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_enriched_in_memory_without_unexpected_edges() -> None:
    path = ARO_DIR / V.TARGET.filename
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = V.enrich_record(record)

    assert changed or out == record
    assert _edge_keys(out) == V.EXPECTED_EDGE_KEYS
