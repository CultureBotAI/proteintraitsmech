from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rewrite_aro_role_only_graphs.py"


def _load():
    spec = importlib.util.spec_from_file_location("rewrite_aro_role_only_graphs", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


R = _load()
ARO_DIR = REPO / "data" / "traits" / "function" / "resistance" / "aro"


PGSA_DEFINITION = (
    "pgsA or phosphatidylglycerophosphate synthetase is an integral membrane protein "
    "involved in phospholipid biosynthesis. It is a "
    "CDP-diacylglycerol-glycerol-3-phosphate 3-phosphatidyltransferase."
)

RPOB_DEFINITION = (
    "RNA polymerase is a multisubunit enzyme that is necessary for transcription. The "
    "beta-subunit of RNA polymerase forms the active center of the enzyme and "
    "template/transcript binding sites. Mutations in rpoB gene confers antibiotic "
    "resistance."
)


def _edge(subject: str, predicate: str, predicate_id: str, object_: str) -> dict:
    return {
        "subject": subject,
        "predicate": predicate,
        "predicate_id": predicate_id,
        "object": object_,
        "evidence": [
            {
                "reference": "ARO:old",
                "snippet": "stale evidence",
            }
        ],
    }


def _pgsa_record(identifier: str = "ARO:3003420") -> dict:
    return {
        "identifier": identifier,
        "definition": PGSA_DEFINITION,
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "antibiotic resistant pgsA",
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
                        "node_id": "pgp_synthase",
                        "label": "CDP-diacylglycerol-glycerol-3-phosphate "
                        "3-phosphatidyltransferase activity",
                        "node_type": "MOLECULAR_FUNCTION",
                    },
                    {
                        "node_id": "phospholipid",
                        "label": "phospholipid biosynthesis",
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
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                        "mech0",
                    ),
                    _edge("mech0", "causally upstream of", "RO:0002411", "resistance"),
                    _edge(
                        "determinant",
                        "causally upstream of (confers resistance)",
                        "RO:0002411",
                        "resistance",
                    ),
                    _edge(
                        "determinant",
                        "enables (phosphatidylglycerophosphate synthesis)",
                        "RO:0002327",
                        "pgp_synthase",
                    ),
                    _edge(
                        "pgp_synthase",
                        "part of (phospholipid biosynthesis)",
                        "BFO:0000050",
                        "phospholipid",
                    ),
                ],
            }
        ],
    }


def _rpob_record(identifier: str = "ARO:3003276") -> dict:
    return {
        "identifier": identifier,
        "definition": RPOB_DEFINITION,
        "causal_graphs": [
            {
                "graph_id": "resistance",
                "nodes": [
                    {
                        "node_id": "determinant",
                        "label": "antibiotic resistant rpoB",
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
                        "node_id": "transcription",
                        "label": "transcription",
                        "node_type": "BIOLOGICAL_PROCESS",
                    },
                    {
                        "node_id": "active_center",
                        "label": "RNA polymerase active center and template/transcript binding sites",
                        "node_type": "PROTEIN",
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
                        "participates in (resistance mechanism)",
                        "RO:0000056",
                        "mech0",
                    ),
                    _edge("mech0", "causally upstream of", "RO:0002411", "resistance"),
                    _edge(
                        "determinant",
                        "causally upstream of (confers resistance)",
                        "RO:0002411",
                        "resistance",
                    ),
                    _edge(
                        "determinant",
                        "part of (the polymerase active center)",
                        "BFO:0000050",
                        "active_center",
                    ),
                    _edge(
                        "active_center",
                        "part of (transcription)",
                        "BFO:0000050",
                        "transcription",
                    ),
                ],
            }
        ],
    }


def test_target_filenames_are_exactly_the_expected_three():
    assert {target.filename for target in R.TARGETS.values()} == {
        "antibiotic-resistant-pgsa-aro3003420.yaml",
        "antibiotic-resistant-rpob-aro3003276.yaml",
        "antibiotic-resistant-rpoc-aro3003289.yaml",
    }


def test_pgsa_enrichment_adds_go_groundings_descriptions_and_role_evidence():
    out, changed = R.enrich_record(_pgsa_record(), R.TARGETS["ARO:3003420"])

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["pgp_synthase"] == R.PGSA_NODES["pgp_synthase"]
    assert by_node["phospholipid"] == R.PGSA_NODES["phospholipid"]
    for edge in graph["edges"]:
        assert edge["description"]
    assert by_pair[("determinant", "mech0")]["evidence"] == [
        {
            "reference": "ARO:3003420",
            "snippet": PGSA_DEFINITION,
            "notes": "Exact ARO definition of this role-only parent determinant.",
        }
    ]
    assert by_pair[("determinant", "pgp_synthase")]["evidence"][-1] == (
        R.GO_PGP_SYNTHASE_EVIDENCE
    )
    assert by_pair[("pgp_synthase", "phospholipid")]["evidence"][-1] == (
        R.GO_PHOSPHOLIPID_EVIDENCE
    )


def test_rpo_enrichment_grounds_transcription_and_leaves_active_center_label_only():
    out, changed = R.enrich_record(_rpob_record(), R.TARGETS["ARO:3003276"])

    assert changed
    graph = out["causal_graphs"][0]
    by_node = {node["node_id"]: node for node in graph["nodes"]}
    by_pair = {(edge["subject"], edge["object"]): edge for edge in graph["edges"]}

    assert by_node["transcription"] == R.RNA_TRANSCRIPTION_NODE
    assert by_node["active_center"] == R.ACTIVE_CENTER_NODES["ARO:3003276"]
    assert "grounding" not in by_node["active_center"]
    assert by_pair[("active_center", "transcription")]["evidence"] == [
        {
            "reference": "ARO:3003276",
            "snippet": RPOB_DEFINITION,
            "notes": "Exact ARO definition of this role-only parent determinant.",
        },
        R.GO_TRANSCRIPTION_EVIDENCE,
    ]


def test_enrich_record_is_idempotent():
    target = R.TARGETS["ARO:3003420"]

    once, changed = R.enrich_record(_pgsa_record(), target)
    twice, changed_again = R.enrich_record(once, target)

    assert changed
    assert not changed_again
    assert twice == once


def test_wrong_identifier_is_refused():
    with pytest.raises(ValueError, match="expected ARO:3003420, found ARO:3003276"):
        R.enrich_record(_rpob_record(), R.TARGETS["ARO:3003420"])


def test_unexpected_edges_are_refused():
    record = _pgsa_record()
    record["causal_graphs"][0]["edges"].append(
        _edge("phospholipid", "causally upstream of", "RO:0002411", "unmodeled")
    )

    with pytest.raises(ValueError, match="unexpected edge phospholipid -> unmodeled"):
        R.enrich_record(record, R.TARGETS["ARO:3003420"])


def test_missing_expected_edges_are_refused():
    record = _pgsa_record()
    record["causal_graphs"][0]["edges"].pop()

    with pytest.raises(ValueError, match="missing edge\\(s\\): pgp_synthase -> phospholipid"):
        R.enrich_record(record, R.TARGETS["ARO:3003420"])


def test_enrich_text_adds_history_once():
    target = R.TARGETS["ARO:3003420"]
    text = yaml.safe_dump(_pgsa_record(), sort_keys=False)

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
    target = R.TARGETS["ARO:3003420"]
    enriched, changed = R.enrich_record(_pgsa_record(), target)
    assert changed
    edges = enriched["causal_graphs"][0]["edges"]
    pgp_edge = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("determinant", "pgp_synthase")
    )
    phospholipid_edge = next(
        edge for edge in edges if (edge["subject"], edge["object"]) == ("pgp_synthase", "phospholipid")
    )
    phospholipid_edge["evidence"] = pgp_edge["evidence"]
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
