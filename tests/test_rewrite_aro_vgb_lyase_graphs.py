from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_vgb_lyase_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_vgb_lyase_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

LABELS = {
    "ARO:3000376": "streptogramin vgb lyase",
    "ARO:3001307": "vgbA",
    "ARO:3001308": "vgbB",
    "ARO:3003990": "vgbC",
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
                "snippet": R.VGB_PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = R.PARENT_IDENTIFIER) -> dict:
    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": R.VGB_PARENT_EVIDENCE["snippet"],
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
                        "label": "antibiotic inactivation",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0001004",
                    },
                    {
                        "node_id": "mech1",
                        "label": "linearization of antibiotic conferring resistance",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:3000338",
                    },
                    {
                        "node_id": "drug0",
                        "label": "streptogramin antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:0000026",
                    },
                    {
                        "node_id": "lyase",
                        "label": "streptogramin B lyase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "lactone",
                        "label": "streptogramin lactone ring (ester linkage)",
                        "node_type": "CHEMICAL",
                    },
                    {
                        "node_id": "linearized",
                        "label": "linearized, inactive streptogramin B",
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
                        "mech1",
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                    ),
                    _edge("mech1", "resistance"),
                    _edge("determinant", "resistance"),
                    _edge(
                        "determinant",
                        "drug0",
                        "confers resistance to (drug class)",
                        "ARO:2000001",
                    ),
                    _edge(
                        "determinant",
                        "lyase",
                        "enables (linearizes the drug)",
                        "RO:0002327",
                    ),
                    _edge(
                        "lactone",
                        "drug0",
                        "part of (the intact drug)",
                        "BFO:0000050",
                    ),
                    _edge(
                        "lyase",
                        "lactone",
                        "has input (the ester linkage)",
                        "RO:0002233",
                    ),
                    _edge(
                        "lyase",
                        "linearized",
                        "causally upstream of (inactivates the drug)",
                        "RO:0002411",
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


def test_target_set_matches_exact_hidden_no_ignore_vgb_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == {
        "streptogramin-vgb-lyase-aro3000376.yaml",
        "vgba-aro3001307.yaml",
        "vgbb-aro3001308.yaml",
        "vgbc-aro3003990.yaml",
    }


@pytest.mark.parametrize("identifier", sorted(LABELS))
def test_vgb_records_reuse_mech1_for_linearization(identifier: str) -> None:
    target = R.TARGETS[identifier]
    out, changed = R.enrich_record(_record(identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "linearized",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    assert "lyase" not in _node_ids(out)
    assert "lactone" not in _node_ids(out)


def test_all_non_state_nodes_are_grounded() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        for node in out["causal_graphs"][0]["nodes"]:
            if node["node_type"] != "STATE":
                assert node.get("grounding")


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
    with pytest.raises(ValueError, match="expected ARO:3000376, found ARO:3001307"):
        R.enrich_record(_record("ARO:3001307"), R.TARGETS["ARO:3000376"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("drug0", "linearized"))

    with pytest.raises(ValueError, match="unexpected edge drug0 -> linearized"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, target)


def test_missing_core_edge_is_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge for edge in record["causal_graphs"][0]["edges"] if edge["object"] != "mech0"
    ]

    with pytest.raises(ValueError, match="missing core edge"):
        R.enrich_record(record, target)


def test_missing_linearization_path_is_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if (edge["subject"], edge["object"]) not in {("lyase", "lactone")}
    ]

    with pytest.raises(ValueError, match="missing Vgb linearization path"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
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
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "linearized",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
