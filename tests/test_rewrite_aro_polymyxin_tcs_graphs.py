from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_polymyxin_tcs_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_polymyxin_tcs_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


def _record(identifier: str = "ARO:3003896") -> dict:
    return {
        "identifier": identifier,
        "definition": (
            "Mutations in Pseudomonas aeruginosa PhoQ of the two-component PhoPQ "
            "regulatory system. Presence of mutation confers resistance to colistin."
        ),
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "Pseudomonas mutant PhoQ conferring resistance to colistin",
                        "node_type": "PROTEIN",
                        "grounding": identifier,
                    },
                    {
                        "node_id": "lipid_a_mod",
                        "label": "lipid A modification gene expression",
                        "node_type": "BIOLOGICAL_PROCESS",
                    },
                    {
                        "node_id": "surface_charge",
                        "label": "reduced net negative charge of the envelope",
                        "node_type": "QUALITY",
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
                        "predicate": "participates in (resistance mechanism)",
                        "predicate_id": "RO:0000056",
                        "object": "mech0",
                        "evidence": [
                            {
                                "reference": "ARO:3003583",
                                "snippet": "sensor kinase archetype",
                                "notes": "Family mechanism ARO:0010000.",
                            }
                        ],
                    },
                    {
                        "subject": "determinant",
                        "predicate": "positively regulates",
                        "predicate_id": "RO:0002213",
                        "object": "lipid_a_mod",
                        "evidence": [
                            {
                                "reference": "ARO:3003583",
                                "snippet": "sensor kinase archetype",
                            }
                        ],
                    },
                    {
                        "subject": "lipid_a_mod",
                        "predicate": "causally upstream of",
                        "predicate_id": "RO:0002411",
                        "object": "surface_charge",
                        "evidence": [
                            {
                                "reference": "ARO:3003588",
                                "snippet": "charge alteration",
                            }
                        ],
                    },
                ],
            }
        ],
    }


def test_target_filenames_are_exactly_the_expected_six():
    assert {target.filename for target in R.TARGETS.values()} == {
        "basr-aro3003582.yaml",
        "bass-aro3003583.yaml",
        "klebsiella-mutant-phop-conferring-antibiotic-resistance-to-colistin-"
        "aro3003585.yaml",
        "pseudomonas-mutant-phop-conferring-resistance-to-colistin-aro3003895.yaml",
        "pseudomonas-mutant-phoq-conferring-resistance-to-colistin-aro3003896.yaml",
        "klebsiella-pneumoniae-mutant-phoq-conferring-resistance-to-colistin-"
        "aro3007203.yaml",
    }


def test_enrich_record_adds_descriptions_pubmed_and_terminal_charge_edge():
    target = R.TARGETS["ARO:3003896"]

    out, changed = R.enrich_record(_record(), target)

    assert changed
    graph = out["causal_graphs"][0]
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}
    lipid_a_mod = next(node for node in graph["nodes"] if node["node_id"] == "lipid_a_mod")
    assert lipid_a_mod == R.LIPID_A_MOD_NODE
    assert ("surface_charge", "resistance") in by_pair
    assert by_pair[("surface_charge", "resistance")]["predicate_id"] == "RO:0002411"
    for edge in graph["edges"]:
        assert edge["description"]
        assert len(edge["evidence"]) == 2
    assert by_pair[("determinant", "lipid_a_mod")]["evidence"] == [
        {
            "reference": "ARO:3003896",
            "snippet": _record()["definition"],
            "notes": "Exact ARO definition of this determinant.",
        },
        target.literature,
    ]


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3003896"]

    once, changed = R.enrich_record(_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3003583, found ARO:3003896"):
        R.enrich_record(_record(), R.TARGETS["ARO:3003583"])


def test_unexpected_edges_are_refused():
    record = _record()
    record["causal_graphs"][0]["edges"].append(
        {
            "subject": "surface_charge",
            "predicate": "causally upstream of",
            "predicate_id": "RO:0002411",
            "object": "unmodeled",
            "evidence": [],
        }
    )

    with pytest.raises(ValueError, match="unexpected edge surface_charge -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3003896"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3003896"]
    text = yaml.safe_dump(_record(), sort_keys=False)

    once, changed = R.enrich_text(text, ARO_DIR / target.filename)
    twice, changed_again = R.enrich_text(once, ARO_DIR / target.filename)

    assert changed
    assert not changed_again
    assert once == twice
    assert "&id" not in once
    assert "*id" not in once
    assert once.count("codex-causal-graph-quality") == 1
    assert "curation_history:" in once


def test_enrich_text_rewrites_yaml_aliases_without_duplicating_history():
    target = R.TARGETS["ARO:3003896"]
    enriched, changed = R.enrich_record(_record(), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    charge_edge = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("lipid_a_mod", "surface_charge")
    )
    terminal_edge = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("surface_charge", "resistance")
    )
    terminal_edge["evidence"] = charge_edge["evidence"]
    text = yaml.safe_dump(enriched, sort_keys=False)
    assert "&id" in text
    text += "\ncuration_history:\n"
    text += "- timestamp: '2026-09-05T00:00:00Z'\n"
    text += "  curator: codex-causal-graph-quality\n"
    text += "  action: already enriched\n"
    text += "  llm_assisted: true\n"

    out, changed = R.enrich_text(text, ARO_DIR / target.filename)

    assert changed
    assert "&id" not in out
    assert "*id" not in out
    assert out.count("codex-causal-graph-quality") == 1


@pytest.mark.skipif(not ARO_DIR.is_dir(), reason="ARO records absent")
def test_all_shipped_targets_are_enriched_in_memory_without_unexpected_edges():
    for target in R.TARGETS.values():
        path = ARO_DIR / target.filename
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        out, changed = R.enrich_record(copy.deepcopy(record), target)
        assert changed or out == record
        for graph in out["causal_graphs"]:
            if graph["graph_id"] != "resistance":
                continue
            for edge in graph["edges"]:
                assert edge["description"]
                assert len(edge["evidence"]) == 2
