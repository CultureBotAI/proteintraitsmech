from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_minimal_daptomycin_mutation_graphs.py"
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _load():
    spec = importlib.util.spec_from_file_location(
        "rewrite_aro_minimal_daptomycin_mutation_graphs",
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
                "reference": "ARO:3004263",
                "snippet": "relationship: confers_resistance_to_drug_class ARO:3000053 ! peptide antibiotic",
            }
        ],
    }


def _record(identifier: str = "ARO:3004263") -> dict:
    return {
        "identifier": identifier,
        "label": "daptomycin resistant liaR",
        "definition": "Mutations to the liaR response regulator that confer resistance to daptomycin.",
        "mapping_status": "SEEDED",
        "evidence": [{"reference": "DOI:test", "notes": "PMID:test (aro citation)"}],
        "causal_graphs": [
            {
                "graph_id": "resistance-draft",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "daptomycin resistant liaR",
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
                ],
            }
        ],
    }


def _edge_keys(record: dict) -> set[tuple[str, str, str]]:
    return {
        (edge["subject"], edge["predicate_id"], edge["object"])
        for edge in record["causal_graphs"][0]["edges"]
    }


def _target(identifier: str) -> object:
    return next(target for target in R.TARGETS if target.identifier == identifier)


def test_liafs_targets_are_in_minimal_daptomycin_batch() -> None:
    assert {
        "ARO:3004262",
        "ARO:3004263",
        "ARO:3004264",
    } <= {target.identifier for target in R.TARGETS}


def test_enrich_record_keeps_only_minimal_daptomycin_edges() -> None:
    target = _target("ARO:3004263")

    out, changed = R.enrich_record(_record(), target)

    assert changed
    assert out["mapping_status"] == "REVIEWED"
    assert _edge_keys(out) == R.EDGE_KEYS
    assert out["causal_graphs"][0]["nodes"] == [
        {
            "node_id": "determinant",
            "label": "daptomycin resistant liaR",
            "node_type": "PROTEIN",
            "grounding": "ARO:3004263",
        },
        R.MECHANISM_NODE,
        R.DRUG_NODE,
        R.RESISTANCE_NODE,
    ]


def test_all_output_edges_are_described_and_multi_evidenced() -> None:
    target = _target("ARO:3004263")

    out, changed = R.enrich_record(_record(), target)

    assert changed
    for edge in out["causal_graphs"][0]["edges"]:
        assert edge["description"]
        assert len({item["reference"] for item in edge["evidence"]}) > 1
        assert any(item.get("snippet") for item in edge["evidence"])


def test_identifier_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="expected ARO:3004263, found ARO:3004262"):
        R.enrich_record(_record("ARO:3004262"), _target("ARO:3004263"))


def test_missing_drug_relation_is_refused() -> None:
    record = _record()
    record["causal_graphs"][0]["edges"][3]["evidence"] = []

    with pytest.raises(ValueError, match="missing ARO drug-relation evidence"):
        R.enrich_record(record, _target("ARO:3004263"))


def test_enrich_record_is_idempotent() -> None:
    target = _target("ARO:3004263")

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_enrich_text_adds_history_once() -> None:
    target = _target("ARO:3004263")
    path = ARO_DIR / target.filename
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, path)
    twice, changed_again = R.enrich_text(once, path)

    assert changed
    assert not changed_again
    assert once == twice
    assert once.count(R.HISTORY_ACTION) == 1
    assert "&id" not in once
    assert "*id" not in once


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_liafs_records_rewrite_in_memory() -> None:
    for identifier in ("ARO:3004262", "ARO:3004263", "ARO:3004264"):
        target = _target(identifier)
        path = ARO_DIR / target.filename
        text = path.read_text(encoding="utf-8")

        out, changed = R.enrich_text(text, path)

        assert changed or R.HISTORY_ACTION in out
        assert "graph_id: resistance\n" in out
