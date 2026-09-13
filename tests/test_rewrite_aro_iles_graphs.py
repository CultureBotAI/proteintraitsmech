from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_iles_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_iles_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()

LABELS = {
    "ARO:3000446": "antibiotic-resistant isoleucyl-tRNA synthetase (ileS)",
    "ARO:3003730": "Bifidobacterium bifidum ileS conferring resistance to mupirocin",
    "ARO:3003729": "Staphylococcus aureus ileS with mutation conferring resistance to mupirocin",
    "ARO:3000521": "Staphylococcus aureus mupA conferring resistance to mupirocin",
    "ARO:3000510": "Staphylococcus aureus mupB conferring resistance to mupirocin",
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
                "reference": "ARO:3000446",
                "snippet": R.ILES_PARENT_EVIDENCE["snippet"],
            }
        ],
    }


def _record(identifier: str = "ARO:3000446") -> dict:
    return {
        "identifier": identifier,
        "label": LABELS[identifier],
        "definition": f"{LABELS[identifier]} confers resistance to mupirocin.",
        "mapping_status": "REVIEWED",
        "evidence": [
            {
                "reference": "PMID:test",
                "notes": "ARO citation for this record.",
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
                        "label": "mupirocin-like antibiotic",
                        "node_type": "CHEMICAL",
                        "grounding": "ARO:3007151",
                    },
                    {
                        "node_id": "aminoacylation",
                        "label": "isoleucyl-tRNA synthetase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "protein_synthesis",
                        "label": "protein synthesis",
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
                        "determinant",
                        "aminoacylation",
                        "enables (isoleucyl-tRNA charging)",
                        "RO:0002327",
                    ),
                    _edge(
                        "drug0",
                        "aminoacylation",
                        "negatively regulates (interferes with the synthetase)",
                        "RO:0002212",
                    ),
                    _edge(
                        "aminoacylation",
                        "protein_synthesis",
                        "part of (protein synthesis)",
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


def _node_ids(record: dict) -> list[str]:
    return [node["node_id"] for node in record["causal_graphs"][0]["nodes"]]


def test_target_set_matches_exact_hidden_no_ignore_iles_branch() -> None:
    assert {target.identifier for target in R.TARGETS.values()} == set(LABELS)
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-isoleucyl-trna-synthetase-iles-aro3000446.yaml",
        "bifidobacterium-bifidum-iles-conferring-resistance-to-mupirocin-aro3003730.yaml",
        "staphylococcus-aureus-iles-with-mutation-conferring-resistance-to-mupirocin-aro3003729.yaml",
        "staphylococcus-aureus-mupa-conferring-resistance-to-mupirocin-aro3000521.yaml",
        "staphylococcus-aureus-mupb-conferring-resistance-to-mupirocin-aro3000510.yaml",
    }


@pytest.mark.parametrize("identifier", sorted(LABELS))
def test_iles_records_ground_activity_and_translation(identifier: str) -> None:
    out, changed = R.enrich_record(_record(identifier), R.TARGETS[identifier])

    assert changed
    assert _node_ids(out) == [
        "determinant",
        "mech0",
        "drug0",
        "aminoacylation",
        "protein_synthesis",
        "resistance",
    ]
    assert _edge_keys(out) == R._canonical_edge_keys()
    by_node = {node["node_id"]: node for node in out["causal_graphs"][0]["nodes"]}
    assert by_node["aminoacylation"]["grounding"] == "GO:0004822"
    assert by_node["protein_synthesis"]["grounding"] == "GO:0006412"


def test_mupa_and_mupb_are_modeled_as_target_replacement() -> None:
    for identifier in ["ARO:3000510", "ARO:3000521"]:
        out, changed = R.enrich_record(_record(identifier), R.TARGETS[identifier])

        assert changed
        assert out["causal_graphs"][0]["nodes"][1] == {
            "node_id": "mech0",
            "label": "antibiotic target replacement",
            "node_type": "MOLECULAR_FUNCTION",
            "grounding": "ARO:0001002",
        }


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
    target = R.TARGETS["ARO:3000446"]

    once, changed = R.enrich_record(_record(target.identifier), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3000446, found ARO:3003730"):
        R.enrich_record(_record("ARO:3003730"), R.TARGETS["ARO:3000446"])


def test_unexpected_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3000446"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("aminoacylation", "resistance"))

    with pytest.raises(ValueError, match="unexpected edge aminoacylation -> resistance"):
        R.enrich_record(record, target)


def test_duplicate_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3000446"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"].append(_edge("determinant", "resistance"))

    with pytest.raises(ValueError, match="duplicate edge determinant -> resistance"):
        R.enrich_record(record, target)


def test_missing_core_edge_is_refused() -> None:
    target = R.TARGETS["ARO:3000446"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "mech0"
    ]

    with pytest.raises(ValueError, match="missing core edge"):
        R.enrich_record(record, target)


def test_missing_legacy_and_canonical_translation_edges_are_refused() -> None:
    target = R.TARGETS["ARO:3000446"]
    record = _record(target.identifier)
    record["causal_graphs"][0]["edges"] = [
        edge
        for edge in record["causal_graphs"][0]["edges"]
        if edge["object"] != "protein_synthesis"
    ]

    with pytest.raises(ValueError, match="missing aminoacylation-to-translation edge"):
        R.enrich_record(record, target)


def test_enrich_text_rewrites_yaml_aliases_and_adds_history_once() -> None:
    target = R.TARGETS["ARO:3000446"]
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
def test_all_shipped_targets_are_enriched_in_memory_without_unexpected_edges() -> None:
    for target in R.TARGETS.values():
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        out, changed = R.enrich_record(record, target)

        assert changed or out == record
        assert _node_ids(out) == [
            "determinant",
            "mech0",
            "drug0",
            "aminoacylation",
            "protein_synthesis",
            "resistance",
        ]
        assert _edge_keys(out) == R._canonical_edge_keys()
