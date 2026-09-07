from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_thya_pas_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_thya_pas_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

LABELS = {
    "ARO:3004152": "aminosalicylate resistant thymidylate synthase",
    "ARO:3004153": (
        "Mycobacterium tuberculosis thyA with mutation conferring resistance "
        "to para-aminosalicylic acid"
    ),
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
                "snippet": R.PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = R.PARENT_IDENTIFIER) -> dict:
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
                "nodes": [
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
                        "node_id": "drug0",
                        "label": "salicylic acid antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3007159",
                    },
                    {
                        "node_id": "ts_activity",
                        "label": "thymidylate synthase activity (dUMP to dTMP)",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "defect",
                        "label": "disrupted substrate binding and catalysis",
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
                        "ts_activity",
                        "enables (dUMP to dTMP conversion)",
                        "RO:0002327",
                    ),
                    _edge(
                        "determinant",
                        "defect",
                        "has quality (disrupted binding and catalysis)",
                        "RO:0000086",
                    ),
                    _edge(
                        "defect",
                        "ts_activity",
                        "negatively regulates (the enzyme stops working)",
                        "RO:0002212",
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


def test_target_set_matches_exact_hidden_no_ignore_thya_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == {
        "aminosalicylate-resistant-thymidylate-synthase-aro3004152.yaml",
        (
            "mycobacterium-tuberculosis-thya-with-mutation-conferring-"
            "resistance-to-para-amin-aro3004153.yaml"
        ),
    }


@pytest.mark.parametrize("identifier", sorted(LABELS))
def test_thya_pas_records_ground_thymidylate_synthase_activity(
    identifier: str,
) -> None:
    target = R.TARGETS[identifier]
    out, changed = R.enrich_record(_record(identifier), target)

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "ts_activity",
        "defect",
        "resistance",
    ]
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
    ts_activity = next(
        node for node in out["causal_graphs"][0]["nodes"] if node["node_id"] == "ts_activity"
    )
    assert ts_activity["grounding"] == "GO:0004799"


def test_all_non_state_nodes_are_grounded_and_edges_described() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        graph = out["causal_graphs"][0]
        for node in graph["nodes"]:
            if node["node_type"] != "STATE":
                assert node.get("grounding")
        assert all(edge.get("description") for edge in graph["edges"])


def test_all_output_edges_are_multi_evidenced() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        for edge in out["causal_graphs"][0]["edges"]:
            assert len({item["reference"] for item in edge["evidence"]}) > 1


def test_ts_activity_edges_have_go_evidence() -> None:
    for target in R.TARGETS.values():
        out, changed = R.enrich_record(_record(target.identifier), target)

        assert changed
        ts_edges = [
            edge
            for edge in out["causal_graphs"][0]["edges"]
            if "ts_activity" in {edge["subject"], edge["object"]}
        ]
        assert ts_edges
        for edge in ts_edges:
            assert "GO:0004799" in {item["reference"] for item in edge["evidence"]}


def test_enrich_record_is_idempotent() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004152, found ARO:3004153"):
        R.enrich_record(_record("ARO:3004153"), R.TARGETS[R.PARENT_IDENTIFIER])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS[R.PARENT_IDENTIFIER]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("defect", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge defect -> resistance"):
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
        edge for edge in record["causal_graphs"][0]["edges"] if edge["object"] != "drug0"
    ]

    with pytest.raises(ValueError, match="missing edge"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3004153"]
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
    out, changed = R.enrich_record(copy.deepcopy(record), target)

    assert changed or out == record
    assert _edge_keys(out) == R.EXPECTED_EDGE_KEYS
