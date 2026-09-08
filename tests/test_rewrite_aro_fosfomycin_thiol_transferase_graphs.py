from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_fosfomycin_thiol_transferase_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_fosfomycin_thiol_transferase_graphs",
        SCRIPT,
    )
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
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [
            {
                "reference": "ARO:3000133",
                "snippet": R.DRUG_RELATION_SNIPPET,
            }
        ],
    }


def _record(identifier: str = "ARO:3000149") -> dict:
    return {
        "identifier": identifier,
        "label": "FosA",
        "definition": "FosA breaks the epoxide ring of fosfomycin.",
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
                "nodes": [
                    _node("determinant", "PROTEIN", identifier),
                    _node("mech0", "MOLECULAR_FUNCTION", "ARO:0001004"),
                    _node("mech1", "MOLECULAR_FUNCTION", "ARO:3000125"),
                    _node("drug0", "CHEMICAL", "ARO:3007149"),
                    _node("domain", "DOMAIN", "Pfam:PF00903"),
                    _node("fold", "DOMAIN", "CATH:3.10.180"),
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
                        "domain",
                        "determinant",
                        "part of (catalytic domain of the protein)",
                        "BFO:0000050",
                    ),
                    _edge("determinant", "fold", "member of", "RO:0002350"),
                    _edge(
                        "domain",
                        "mech1",
                        "enables (fosfomycin epoxide opening)",
                        "RO:0002327",
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


def test_target_set_is_exactly_fosfomycin_thiol_transferase_branch() -> None:
    target_filenames = {target.filename for target in R.TARGETS}

    assert len(R.TARGETS) == 30
    assert "fosfomycin-thiol-transferase-aro3000133.yaml" in target_filenames
    assert "fosa-aro3000149.yaml" in target_filenames
    assert "fosxcc-aro3003208.yaml" in target_filenames
    assert "fosc-aro3000380.yaml" not in target_filenames
    assert "fosfomycin-phosphotransferase-aro3000359.yaml" not in target_filenames


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_target_discovery_finds_current_fosfomycin_thiol_transferase_slice() -> None:
    paths = R.iter_target_paths(ARO_DIR)

    assert len(paths) == 30
    assert {path.name for path in paths} == {target.filename for target in R.TARGETS}


def test_enrich_record_replaces_domain_fold_with_modified_state() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "mech1",
        "drug0",
        "modified",
        "resistance",
    ]
    assert _edge_keys(out) == R.CORE_EDGE_KEYS
    assert ("domain", "BFO:0000050", "determinant") not in _edge_keys(out)
    by_node = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}
    assert by_node["mech1"] == R.EPOXIDE_OPENING_NODE
    assert by_node["modified"] == R.MODIFIED_NODE


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert any(item.get("snippet") for item in edge["evidence"])


def test_wrong_path_is_refused() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    with pytest.raises(ValueError, match="not a fosfomycin thiol-transferase target"):
        R.enrich_text(text, ARO_DIR / "fosc-aro3000380.yaml")


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000149, found ARO:unexpected"):
        R.enrich_record(_record("ARO:unexpected"), R.TARGETS[0])


def test_unexpected_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("fold", "mech1"))

    with pytest.raises(ValueError, match="unexpected edge fold -> mech1"):
        R.enrich_record(record, R.TARGETS[0])


def test_missing_drug_relation_evidence_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"][5]["evidence"] = []

    with pytest.raises(ValueError, match="missing ARO drug-relation evidence"):
        R.enrich_record(record, R.TARGETS[0])


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS[0]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    path = ARO_DIR / R.TARGETS[0].filename
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once
