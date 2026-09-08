from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_enterococcus_liafsr_daptomycin_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_enterococcus_liafsr_daptomycin_graphs",
        SCRIPT,
    )
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
                "reference": "ARO:3004262",
                "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
            }
        ],
    }


def _record(identifier: str = "ARO:3003077") -> dict:
    return {
        "identifier": identifier,
        "label": "Enterococcus faecalis liaF mutant conferring daptomycin resistance",
        "definition": (
            "liaF is an accessory protein that acts as a negative regulator of "
            "liaRS signal transduction pathway. Mutations confer daptomycin resistance."
        ),
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
                    {
                        "node_id": "determinant",
                        "label": "Enterococcus faecalis liaF mutant conferring daptomycin resistance",
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
                        "node_id": "drug0",
                        "label": "peptide antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3000053",
                    },
                    {
                        "node_id": "lipid_ii_stress",
                        "label": "envelope stress from lipid II-inhibiting antibiotics",
                        "node_type": "STATE",
                    },
                    {
                        "node_id": "stress_response",
                        "label": "cell envelope stress response",
                        "node_type": "BIOLOGICAL_PROCESS",
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
                        "drug0",
                        "lipid_ii_stress",
                        "causally upstream of (creates envelope stress)",
                    ),
                    _edge(
                        "lipid_ii_stress",
                        "determinant",
                        "causally upstream of (activates the liaFSR system)",
                    ),
                    _edge(
                        "determinant",
                        "stress_response",
                        "regulates (the cell envelope stress response)",
                        "RO:0002211",
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


def test_target_set_is_exactly_enterococcus_liafsr_children() -> None:
    assert [target.identifier for target in R.TARGETS] == [
        "ARO:3003077",
        "ARO:3003792",
        "ARO:3003791",
        "ARO:3003790",
        "ARO:3003078",
        "ARO:3003079",
    ]


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_target_discovery_finds_current_enterococcus_liafsr_slice() -> None:
    paths = R.iter_target_paths(ARO_DIR)

    assert len(paths) == 6
    assert {path.name for path in paths} == {target.filename for target in R.TARGETS}


def test_enrich_record_removes_lipid_ii_induction_and_keeps_drug_edge() -> None:
    out, changed = R.enrich_record(
        _record(),
        R.TARGETS[0],
    )

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "stress_response",
        "resistance",
    ]
    assert _edge_keys(out) == R.CORE_EDGE_KEYS
    assert ("lipid_ii_stress", "RO:0002411", "determinant") not in _edge_keys(out)
    by_node = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}
    assert by_node["drug0"] == R.DAPTOMYCIN_DRUG_NODE
    assert by_node["stress_response"] == R.liafsr.STRESS_RESPONSE_NODE


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert any(item.get("snippet") for item in edge["evidence"])


def test_wrong_path_is_refused() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    with pytest.raises(ValueError, match="not an Enterococcus LiaFSR daptomycin target"):
        R.enrich_text(text, ARO_DIR / "daptomycin-resistant-liaf-aro3004262.yaml")


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3003077, found ARO:unexpected"):
        R.enrich_record(_record("ARO:unexpected"), R.TARGETS[0])


def test_unexpected_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"].append(_edge("stress_response", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge stress_response -> resistance"):
        R.enrich_record(record, R.TARGETS[0])


def test_missing_drug_relation_evidence_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"][3]["evidence"] = []

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
