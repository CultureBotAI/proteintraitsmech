from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_type_nfxb_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_type_nfxb_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _record(
    identifier: str = "ARO:3004059",
    label: str = "Type A NfxB",
    definition: str | None = None,
) -> dict:
    return {
        "identifier": identifier,
        "label": label,
        "definition": definition
        or (
            f"{label} mutants derepress MexCD-OprJ and cause "
            "multidrug resistance."
        ),
        "mapping_status": "SEEDED",
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "title": "old",
                "description": "old",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": label,
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "mech0",
                        "label": "antibiotic efflux",
                        "node_type": "MOLECULAR_FUNCTION",
                        "grounding": "ARO:0010000",
                    },
                    {
                        "node_id": "resistance",
                        "label": "antibiotic resistance phenotype",
                        "node_type": "PHENOTYPE",
                        "grounding": "GO:0046677",
                    },
                ],
                "edges": [
                    {
                        "subject": "determinant",
                        "predicate": "causally upstream of",
                        "predicate_id": "RO:0002411",
                        "object": "resistance",
                        "evidence": [{"reference": identifier, "snippet": "old"}],
                    }
                ],
            }
        ],
    }


def _edge_keys(graph: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in graph["edges"]
    }


def test_targets_are_the_type_a_and_b_nfxb_terms() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004059",
        "ARO:3004060",
    }


def test_enrich_record_models_type_a_nfxb_as_repressor_loss() -> None:
    enriched, changed = R.enrich_record(_record(), R.TARGETS[0])

    assert changed
    assert enriched["mapping_status"] == "REVIEWED"
    graph = enriched["causal_graphs"][0]
    assert graph["graph_id"] == "resistance"
    assert "repressor subclasses" in graph["description"]

    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["determinant"]["grounding"] == "ARO:3004059"
    assert by_node["mech0"]["grounding"] == "ARO:0010000"
    assert by_node["pump"]["grounding"] == "ARO:3000797"
    assert by_node["repression"]["grounding"] == "GO:0045892"
    assert "drug0" not in by_node

    assert _edge_keys(graph) == {
        ("determinant", "RO:0000056", "mech0"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "RO:0002212", "repression"),
        ("repression", "RO:0002212", "pump"),
        ("pump", "RO:0002327", "mech0"),
        ("mech0", "RO:0002411", "resistance"),
    }

    for edge in graph["edges"]:
        assert edge["description"]
        assert len({evidence["reference"] for evidence in edge["evidence"]}) > 1
        assert all(evidence["snippet"] for evidence in edge["evidence"])


def test_type_b_keeps_its_oprj_overproduction_evidence() -> None:
    record = _record(
        identifier="ARO:3004060",
        label="Type B NfxB",
        definition=(
            "The mutation at the 46th amino acid position is sufficient for "
            "overproduction of OprJ and the multidrug resistance."
        ),
    )

    enriched, _ = R.enrich_record(record, R.TARGETS[1])

    determinant_to_repression = next(
        edge
        for edge in enriched["causal_graphs"][0]["edges"]
        if edge["subject"] == "determinant" and edge["object"] == "repression"
    )
    assert any(
        "46th amino acid position is sufficient" in item["snippet"]
        for item in determinant_to_repression["evidence"]
    )


def test_enrich_text_is_idempotent() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    out, changed = R.enrich_text(text, pathlib.Path(R.TARGETS[0].filename))
    again, changed_again = R.enrich_text(out, pathlib.Path(R.TARGETS[0].filename))

    assert changed
    assert not changed_again
    assert again == out
    assert "mapping_status: REVIEWED" in out
    assert out.count(R.HISTORY_ACTION) == 1
    assert "&id" not in out
    assert "*id" not in out


def test_rejects_wrong_identifier() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004059"):
        R.enrich_record(_record("ARO:3004060", "Type B NfxB"), R.TARGETS[0])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert out["mapping_status"] == "REVIEWED"
        assert out["causal_graphs"][0]["graph_id"] == "resistance"
