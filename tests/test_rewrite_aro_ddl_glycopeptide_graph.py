from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_ddl_glycopeptide_graph.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_ddl_glycopeptide_graph", SCRIPT)
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
                "reference": R.TARGET_IDENTIFIER,
                "snippet": R.DDL_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = R.TARGET_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": "D-Ala-D-Ala ligase",
        "definition": R.DDL_EVIDENCE["snippet"],
        "mapping_status": "REVIEWED",
        "evidence": [
            {
                "reference": "DOI:10.1110/ps.39101",
                "notes": "PMID:11274474 (aro citation)",
            },
            {
                "reference": "DOI:10.1086/491711",
                "notes": "PMID:16323116 (aro citation)",
            },
        ],
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "D-Ala-D-Ala ligase",
                        "node_type": "PROTEIN",
                        "grounding": R.TARGET_IDENTIFIER,
                    },
                    {
                        "node_id": "mech0",
                        "label": (
                            "restructuring of bacterial cell wall conferring "
                            "antibiotic resistance"
                        ),
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
                        "node_id": "dala_dala_synthesis",
                        "label": "D-Ala-D-Ala ligase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "susceptible_precursor",
                        "label": "D-Ala-D-Ala, the precursor glycopeptides bind",
                        "node_type": "CHEMICAL",
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
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "drug0",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge(
                        "determinant",
                        "dala_dala_synthesis",
                        "enables (D-Ala-D-Ala synthesis)",
                        "RO:0002327",
                    ),
                    _edge(
                        "dala_dala_synthesis",
                        "susceptible_precursor",
                        "has output (the susceptible precursor)",
                        "RO:0002234",
                    ),
                    _edge(
                        "susceptible_precursor",
                        "drug0",
                        "molecularly interacts with (the drug binds this precursor)",
                        "RO:0002436",
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


def test_target_is_exactly_the_ddl_parent() -> None:
    assert R.TARGET_IDENTIFIER == "ARO:3003970"
    assert R.TARGET_FILENAME == "d-ala-d-ala-ligase-aro3003970.yaml"
    assert R.iter_target_paths(ARO_DIR) == [ARO_DIR / R.TARGET_FILENAME]


def test_ddl_parent_grounds_ligase_activity_and_product() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "dala_dala_synthesis",
        "susceptible_precursor",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS

    by_node = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}
    assert by_node["dala_dala_synthesis"] == R.LIGATION_NODE
    assert by_node["susceptible_precursor"] == R.SUSCEPTIBLE_PRECURSOR_NODE


def test_all_nodes_are_grounded() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    for node in out["causal_graphs"][0]["nodes"]:
        assert node.get("grounding")


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    out, changed = R.enrich_record(_record())

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert any(item.get("snippet") for item in edge["evidence"])


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record())
    twice, changed_again = R.enrich_record(once)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003970, found ARO:3004939"):
        R.enrich_record(_record("ARO:3004939"))


def test_unexpected_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "susceptible_precursor"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> susceptible_precursor"):
        R.enrich_record(record)


def test_duplicate_edges_are_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record)


def test_missing_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = [
        edge for edge in record["causal_graphs"][0]["edges"] if edge["object"] != "mech0"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record)


def test_missing_susceptible_precursor_node_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["nodes"] = [
        node for node in record["causal_graphs"][0]["nodes"] if node["node_id"] != "susceptible_precursor"
    ]

    with pytest.raises(ValueError, match="missing node"):
        R.enrich_record(record)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    enriched, changed = R.enrich_record(_record())
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    edges[1]["evidence"] = edges[0]["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text

    out, changed = R.enrich_text(text, ARO_DIR / R.TARGET_FILENAME)
    again, changed_again = R.enrich_text(out, ARO_DIR / R.TARGET_FILENAME)

    assert changed
    assert not changed_again
    assert "&id" not in out
    assert "*id" not in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert again == out


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_shipped_target_is_enriched_in_memory_without_unexpected_edges() -> None:
    path = ARO_DIR / R.TARGET_FILENAME
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    out, changed = R.enrich_record(record)

    assert changed or out == record
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "dala_dala_synthesis",
        "susceptible_precursor",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
