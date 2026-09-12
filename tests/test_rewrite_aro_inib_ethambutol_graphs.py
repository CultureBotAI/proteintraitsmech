from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_inib_ethambutol_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_inib_ethambutol_graphs",
        SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _edge(subject: str, predicate_id: str, object_: str, snippet: str = "") -> dict:
    return {
        "subject": subject,
        "predicate": "seeded predicate",
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [{"reference": "ARO:3004136", "snippet": snippet}],
    }


def _record(identifier: str = "ARO:3004136") -> dict:
    return {
        "identifier": identifier,
        "label": "Ethambutol resistant iniB",
        "definition": "Point mutations in M. tuberculosis iniB shown to confer resistance to ethambutol.",
        "mapping_status": "SEEDED",
        "evidence": [{"reference": "DOI:10.1128/AAC.44.2.326-336.2000"}],
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "nodes": [
                    {"node_id": "determinant"},
                    {"node_id": "mech0", "label": "antibiotic efflux"},
                    {"node_id": "mech1", "label": "mutation conferring antibiotic resistance"},
                    {"node_id": "drug0"},
                    {"node_id": "resistance"},
                ],
                "edges": [
                    _edge("determinant", "RO:0000056", "mech0"),
                    _edge("mech0", "RO:0002411", "resistance"),
                    _edge("determinant", "RO:0000056", "mech1"),
                    _edge("mech1", "RO:0002411", "resistance"),
                    _edge(
                        "determinant",
                        "RO:0002411",
                        "resistance",
                        "relationship: confers_resistance_to_antibiotic ARO:3000497 ! ethambutol",
                    ),
                    _edge(
                        "determinant",
                        "ARO:2000001",
                        "drug0",
                        "relationship: confers_resistance_to_drug_class "
                        "ARO:3000527 ! polyamine antibiotic",
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


def _broad_parent_text(identifier: str = "ARO:3004137") -> str:
    return f"""identifier: {identifier}
label: Antibiotic resistant iniB
definition: parent definition
mapping_status: SEEDED
causal_graphs:
- graph_id: resistance-draft
  nodes:
  - node_id: determinant
    label: determinant
    node_type: PROTEIN
  edges: []
license: CC-BY 4.0
"""


def _history_actions(text: str) -> list[str]:
    return [
        event["action"]
        for event in yaml.safe_load(text)["curation_history"]
    ]


def test_targets_are_exact_current_iniB_records() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004135",
        "ARO:3004136",
        "ARO:3004137",
    }


def test_broad_parent_draft_graph_is_removed() -> None:
    path = ARO_DIR / "antibiotic-resistant-inib-aro3004137.yaml"

    out, changed = R.enrich_text(_broad_parent_text(), path)

    assert changed
    assert "causal_graphs:" not in out
    assert R.BROAD_PARENT_ACTION in _history_actions(out)


def test_enrich_record_prunes_efflux_side_path() -> None:
    out, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    assert out["mapping_status"] == "REVIEWED"
    assert _edge_keys(out) == R.FINAL_EDGE_KEYS
    assert [node["node_id"] for node in out["causal_graphs"][0]["nodes"]] == [
        "determinant",
        "mech0",
        "drug0",
        "resistance",
    ]
    assert all(
        "efflux" not in str(node.get("label", "")).lower()
        for node in out["causal_graphs"][0]["nodes"]
    )


def test_child_keeps_direct_ethambutol_relationship() -> None:
    record = _record("ARO:3004135")

    out, changed = R.enrich_record(record, R.TARGETS[1])

    assert changed
    assert any(
        "ARO:3000497" in item.get("snippet", "")
        for edge in out["causal_graphs"][0]["edges"]
        for item in edge["evidence"]
    )


def test_enrich_record_is_idempotent() -> None:
    once, changed = R.enrich_record(_record(), R.TARGETS[0])
    twice, changed_again = R.enrich_record(once, R.TARGETS[0])

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)
    path = ARO_DIR / R.TARGETS[0].filename

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004136, found ARO:3004135"):
        R.enrich_record(_record("ARO:3004135"), R.TARGETS[0])
    with pytest.raises(ValueError, match="expected ARO:3004137, found ARO:3004136"):
        R.enrich_text(
            _broad_parent_text("ARO:3004136"),
            ARO_DIR / "antibiotic-resistant-inib-aro3004137.yaml",
        )


def test_missing_edge_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"] = record["causal_graphs"][0]["edges"][:2]

    with pytest.raises(ValueError, match="unexpected edge set"):
        R.enrich_record(record, R.TARGETS[0])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        text = path.read_text(encoding="utf-8")
        if target.remove_graph:
            out, changed = R.enrich_text(text, path)
            assert changed or out == text
            assert "causal_graphs:" not in out
            assert R.BROAD_PARENT_ACTION in _history_actions(out)
            continue

        record = yaml.safe_load(text)
        out, changed = R.enrich_record(copy.deepcopy(record), target)
        assert changed or out == record
        assert _edge_keys(out) == R.FINAL_EDGE_KEYS
