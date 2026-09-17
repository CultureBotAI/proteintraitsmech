from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "repair_uniprot_durable_receipts.py"


def _load():
    spec = importlib.util.spec_from_file_location("repair_uniprot_durable_receipts", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_remove_top_level_block_removes_only_the_requested_block():
    repair = _load()
    text = (
        "identifier: x\n"
        "canonical_examples:\n"
        "- protein_id: UniProtKB:P12345\n"
        "  trait_occurrences:\n"
        "  - source_evidence_id: ug-evidence:abc\n"
        "license: CC0\n"
        "curation_history:\n"
        "- note: keep\n"
    )

    assert repair._remove_top_level_block(text, "canonical_examples") == (
        "identifier: x\n"
        "license: CC0\n"
        "curation_history:\n"
        "- note: keep\n"
    )


def test_candidate_for_evidence_derives_the_replay_candidate_id():
    repair = _load()
    evidence = {
        "trait_id": "HAMAP:MF_00025",
        "protein_id": "UniProtKB:O81098",
        "source_trait_id": "HAMAP:MF_00025",
        "mapping_method": "INTERPRO_MATCH",
        "evidence_source": "InterPro",
        "source_release": "109.0",
        "sequence_sha256": "4a2eb37fe01b93ebcf5a5da7354eab91e13b3ad675d63d19db2b7d0e8775aa2b",
        "scope": "WHOLE_PROTEIN",
    }
    protein = {"uniprot_release": "2026_02", "sequence_length": 205}
    intervals = [{"start": 1, "end": 205}]

    candidate = repair._candidate_for_evidence(evidence, protein, intervals)

    assert candidate["candidate_id"] == repair.ground.derive_candidate_id(candidate)
    assert candidate["sequence_length"] == 205
    assert candidate["intervals"] == intervals


def test_prune_invalid_examples_removes_empty_canonical_examples(tmp_path, monkeypatch):
    repair = _load()
    traits = tmp_path / "data" / "traits"
    target = traits / "sequence" / "family" / "panther" / "x.yaml"
    target.parent.mkdir(parents=True)
    evidence_id = next(iter(repair.PRUNED_EVIDENCE_IDS))
    target.write_text(
        "identifier: PANTHER:PTHR10352\n"
        "definition: x\n"
        "canonical_examples:\n"
        "- protein_id: UniProtKB:O75821\n"
        "  trait_occurrences:\n"
        f"  - source_evidence_id: {evidence_id}\n"
        "    protein_id: UniProtKB:O75821\n"
        "license: CC-BY 4.0\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        repair,
        "PRUNED_EVIDENCE_IDS",
        frozenset({evidence_id}),
    )

    texts = {}
    repair._prune_invalid_examples(
        texts,
        {
            evidence_id: {
                "trait_id": "PANTHER:PTHR10352",
                "protein_id": "UniProtKB:O75821",
            }
        },
        traits_root=traits,
    )

    assert "canonical_examples" not in yaml.safe_load(texts[target])
