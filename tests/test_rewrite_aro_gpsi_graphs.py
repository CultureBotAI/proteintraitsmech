from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_gpsi_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_gpsi_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()


def _record(
    identifier: str = "ARO:3004880",
    label: str = "pyrazinamide resistant gpsI",
) -> dict:
    return {
        "identifier": identifier,
        "label": label,
        "definition": (
            "gpsI codes for polyribonucleotide nucleotidyltransferase which is "
            "a protein involved in mRNA degradation."
        ),
        "mapping_status": "SEEDED",
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": label,
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
        (edge["subject"], edge["predicate_id"], edge["object"]) for edge in graph["edges"]
    }


def test_targets_are_exact_gpsi_hierarchy() -> None:
    assert {target.identifier for target in R.TARGETS} == {
        "ARO:3004879",
        "ARO:3004880",
        "ARO:3004977",
    }


def test_drug_class_child_keeps_poa_binding_and_pnpase_evidence() -> None:
    enriched, changed = R.enrich_record(_record(), R.TARGETS[1])

    assert changed
    assert enriched["mapping_status"] == "REVIEWED"
    graph = enriched["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    assert by_node["determinant"]["grounding"] == "ARO:3004880"
    assert by_node["poa_binding"]["node_type"] == "STATE"
    assert by_node["pnpase"]["grounding"] == "GO:0004654"
    assert by_node["drug0"]["grounding"] == "ARO:3007155"
    assert _edge_keys(graph) == {
        ("determinant", "RO:0000056", "mech0"),
        ("determinant", "RO:0002411", "poa_binding"),
        ("poa_binding", "RO:0002411", "pnpase"),
        ("pnpase", "RO:0002411", "resistance"),
        ("mech0", "RO:0002411", "resistance"),
        ("determinant", "RO:0002411", "resistance"),
        ("determinant", "ARO:2000001", "drug0"),
    }

    pnpase_edge = next(edge for edge in graph["edges"] if edge["object"] == "pnpase")
    assert any("bound pyrazinoic acid" in item["snippet"] for item in pnpase_edge["evidence"])
    assert any("RNA polymerization" in item["snippet"] for item in pnpase_edge["evidence"])


def test_generic_parent_has_no_drug_edge() -> None:
    record = _record(
        identifier="ARO:3004879",
        label="antibiotic resistant gpsI",
    )

    enriched, _ = R.enrich_record(record, R.TARGETS[0])

    graph = enriched["causal_graphs"][0]
    assert "drug0" not in {node["node_id"] for node in graph["nodes"]}
    assert ("determinant", "ARO:2000001", "drug0") not in _edge_keys(graph)


def test_mycobacterium_leaf_keeps_direct_pyrazinamide_relation() -> None:
    record = _record(
        identifier="ARO:3004977",
        label="Mycobacterium tuberculosis gpsI with mutations conferring resistance to pyrazinamide",
    )

    enriched, _ = R.enrich_record(record, R.TARGETS[2])

    resistance_edge = next(
        edge
        for edge in enriched["causal_graphs"][0]["edges"]
        if edge["subject"] == "determinant" and edge["object"] == "resistance"
    )
    assert any(
        "confers_resistance_to_antibiotic ARO:3003413" in item["snippet"]
        for item in resistance_edge["evidence"]
    )


def test_enrich_text_is_idempotent() -> None:
    text = yaml.safe_dump(_record(), sort_keys=False)

    out, changed = R.enrich_text(text, R.TARGETS[1])
    again, changed_again = R.enrich_text(out, R.TARGETS[1])

    assert changed
    assert not changed_again
    assert again == out
    assert out.count(R.HISTORY_ACTION) == 1
    assert "&id" not in out
    assert "*id" not in out


def test_rejects_wrong_identifier() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004880"):
        R.enrich_record(_record("ARO:3004879"), R.TARGETS[1])


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_rewritten_in_memory() -> None:
    for target in R.TARGETS:
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))

        out, changed = R.enrich_record(copy.deepcopy(record), target)

        assert changed or out == record
        assert out["mapping_status"] == "REVIEWED"
        assert out["causal_graphs"][0]["graph_id"] == "resistance"
