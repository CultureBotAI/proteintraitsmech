"""The reviewed structural fields cannot bypass identity, drift or write guards."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import curate_structural_traits as editor
import structural_trait_curations as curations
from record_io import extract_block, merge_on_reseed

ORIGINAL = '''identifier: proteintraitsmech:TEST_MOTIF
label: "Preserve this label's quoting"
definition: >-
  An inspected stub.
definition_source: source
trait_axis: STRUCTURE
trait_category: STRUCT_SECONDARY
term_kind: CLASS
mapping_status: SEEDED
# preserve the unrelated tail
evidence:
  - reference: DOI:10.1/test
    notes: Existing unrelated evidence.
'''


@pytest.fixture
def entry():
    result = {
        "identifier": "proteintraitsmech:TEST_MOTIF",
        "path": "data/traits/structure/secondary/test.yaml",
        "trait_category": "STRUCT_SECONDARY",
        "input_sha256": curations.digest(ORIGINAL),
        "seed_preimages": {"seed_test": curations.digest(ORIGINAL)},
        "blocks": {
            "definition": "definition: >-\n  A source-supported topology.\n",
            "definition_source": "definition_source: DOI:10.1/source\n",
            "mapping_status": "mapping_status: PROPOSED\n",
            "curation_history": (
                'curation_history:\n  - timestamp: "2026-10-28T18:38:08Z"\n'
                "    curator: codex-gpt-6-astra\n    action: structural_trait_curation\n"
                "    changes: Correct definition.\n    llm_assisted: true\n"
            ),
        },
    }
    result["output_sha256"] = curations.digest(curations.apply_blocks(ORIGINAL, result))
    result["blocks_sha256"] = curations.blocks_digest(result["blocks"])
    result["seed_outputs"] = {"seed_test": result["output_sha256"]}
    return result


def test_changes_only_reviewed_fields_and_replay_has_no_history(entry):
    out = editor.curate_record_text(ORIGINAL, entry)
    assert editor.curate_record_text(out, entry) == out
    assert extract_block(ORIGINAL, "evidence") == extract_block(out, "evidence")
    assert extract_block(ORIGINAL, "label") == extract_block(out, "label")
    assert "# preserve the unrelated tail\n" in out
    old, new = yaml.safe_load(ORIGINAL), yaml.safe_load(out)
    assert {k for k in old.keys() | new.keys() if old.get(k) != new.get(k)} == set(entry["blocks"])
    assert new["mapping_status"] == "PROPOSED"
    assert new["curation_history"][0]["llm_assisted"]
    assert len(new["curation_history"]) == 1
    assert "canonical_examples" not in new


@pytest.mark.parametrize("old,new", [
    ("TEST_MOTIF", "DIFFERENT_MOTIF"),
    ("STRUCT_SECONDARY", "STRUCT_CAVITY"),
    ("inspected stub", "changed source"),
    ("mapping_status: SEEDED", "mapping_status: REVIEWED"),
    ("Existing unrelated evidence.", "Later curator's evidence."),
])
def test_unreviewed_or_changed_input_is_refused(entry, old, new):
    with pytest.raises(ValueError, match="re-review"):
        editor.curate_record_text(ORIGINAL.replace(old, new), entry)


def test_partial_repair_is_not_an_idempotent_success(entry):
    out = editor.curate_record_text(ORIGINAL, entry)
    with pytest.raises(ValueError, match="re-review"):
        editor.curate_record_text(out.replace("llm_assisted: true", "llm_assisted: false"), entry)


def test_completed_output_hash_does_not_bypass_identity(entry):
    out = editor.curate_record_text(ORIGINAL, entry)
    entry["identifier"] = "proteintraitsmech:DIFFERENT_TRAIT"
    with pytest.raises(ValueError, match="identity/scope"):
        editor.curate_record_text(out, entry)


def test_output_pin_detects_changed_curated_fields(entry):
    entry["blocks"]["definition"] = "definition: Changed after review.\n"
    with pytest.raises(ValueError, match="reviewed ledger"):
        editor.curate_record_text(ORIGINAL, entry)


@pytest.mark.parametrize("repin_blocks", [False, True])
def test_completed_output_rejects_stale_blocks(entry, repin_blocks):
    out = editor.curate_record_text(ORIGINAL, entry)
    entry["blocks"]["definition"] = "definition: Changed after review.\n"
    if repin_blocks:
        entry["blocks_sha256"] = curations.blocks_digest(entry["blocks"])
    with pytest.raises(ValueError, match="reviewed ledger"):
        editor.curate_record_text(out, entry)


def test_seed_output_pin_rejects_separately_repinned_blocks(entry, monkeypatch):
    entry["blocks"]["definition"] = "definition: Changed after review.\n"
    entry["blocks_sha256"] = curations.blocks_digest(entry["blocks"])
    monkeypatch.setattr(curations, "load_curations", lambda: {entry["identifier"]: entry})
    with pytest.raises(ValueError, match="seed_test output does not match reviewed ledger"):
        curations.curate_seed(ORIGINAL, "seed_test")


@pytest.mark.parametrize("outputs", [None, {}, {"seed_other": "0" * 64}, {"seed_test": "bad"}])
def test_ledger_requires_complete_valid_seed_output_pins(entry, outputs, tmp_path, monkeypatch):
    entry["seed_outputs"] = outputs
    ledger = tmp_path / "ledger.yaml"
    ledger.write_text(yaml.safe_dump({"version": 1, "records": [entry]}))
    monkeypatch.setattr(curations, "LEDGER", ledger)
    curations.load_curations.cache_clear()
    try:
        with pytest.raises(ValueError, match="seeder output pins"):
            curations.load_curations()
    finally:
        curations.load_curations.cache_clear()


def test_exact_reviewed_seeded_history_is_preserved(entry):
    old_event = {"timestamp": "2026-10-01T00:00:00Z", "curator": "claude",
                 "action": "earlier_curation", "llm_assisted": True}
    original = ORIGINAL + yaml.safe_dump({"curation_history": [old_event]}, sort_keys=False)
    last_event = yaml.safe_load(entry["blocks"]["curation_history"])["curation_history"][0]
    entry["blocks"]["curation_history"] = yaml.safe_dump(
        {"curation_history": [old_event, last_event]}, sort_keys=False)
    entry["input_sha256"] = curations.digest(original)
    entry["output_sha256"] = curations.digest(curations.apply_blocks(original, entry))
    entry["blocks_sha256"] = curations.blocks_digest(entry["blocks"])
    with pytest.raises(ValueError, match="curated input"):
        editor.curate_record_text(original, entry)
    entry["allow_seeded_history"] = True
    out = editor.curate_record_text(original, entry)
    assert yaml.safe_load(out)["curation_history"] == [old_event, last_event]
    assert editor.curate_record_text(out, entry) == out
    # Even a repinned REVIEWED record cannot use the SEEDED-history exception.
    reviewed = original.replace("mapping_status: SEEDED", "mapping_status: REVIEWED")
    entry["input_sha256"] = curations.digest(reviewed)
    with pytest.raises(ValueError, match="curated input"):
        editor.curate_record_text(reviewed, entry)
    entry["blocks"]["curation_history"] = yaml.safe_dump({"curation_history": [last_event]})
    with pytest.raises(ValueError, match="history must be preserved"):
        curations.apply_blocks(original, entry)


def test_existing_agent_event_cannot_substitute_for_a_new_change_event(entry):
    original = ORIGINAL + entry["blocks"]["curation_history"]
    entry["input_sha256"] = curations.digest(original)
    entry["allow_seeded_history"] = True
    entry["output_sha256"] = curations.digest(curations.apply_blocks(original, entry))
    entry["blocks_sha256"] = curations.blocks_digest(entry["blocks"])
    with pytest.raises(ValueError, match="exactly one history event"):
        editor.curate_record_text(original, entry)


def followup_entry(entry):
    previous = editor.curate_record_text(ORIGINAL, entry)
    revised = copy.deepcopy(entry)
    revised["allow_proposed_followup"] = True
    revised["input_sha256"] = revised["prior_output_sha256"] = curations.digest(previous)
    revised["blocks"]["definition"] = "definition: Independently corrected topology.\n"
    history = yaml.safe_load(previous)["curation_history"]
    history.append({"timestamp": "2026-10-28T19:00:00Z", "curator": "codex-gpt-6-astra",
                    "action": "EDIT", "changes": "Resolve independent review.", "llm_assisted": True})
    revised["blocks"]["curation_history"] = yaml.safe_dump({"curation_history": history})
    revised["output_sha256"] = curations.digest(curations.apply_blocks(previous, revised))
    revised["blocks_sha256"] = curations.blocks_digest(revised["blocks"])
    return previous, revised


def test_reviewed_followup_appends_event_and_replays(entry):
    previous, revised = followup_entry(entry)
    out = editor.curate_record_text(previous, revised)
    assert yaml.safe_load(out)["curation_history"][:-1] == yaml.safe_load(previous)["curation_history"]
    assert editor.curate_record_text(out, revised) == out
    assert extract_block(previous, "evidence") == extract_block(out, "evidence")


@pytest.mark.parametrize("change", ["flag", "prior_hash", "input_hash", "status", "actor", "assistance"])
def test_followup_never_bypasses_reviewed_status_or_other_actor(entry, change):
    previous, revised = followup_entry(entry)
    if change == "flag":
        revised["allow_proposed_followup"] = False
    elif change == "prior_hash":
        revised["prior_output_sha256"] = "0" * 64
    elif change == "input_hash":
        revised["input_sha256"] = "0" * 64
    else:
        data = yaml.safe_load(previous)
        if change == "status":
            data["mapping_status"] = "REVIEWED"
        elif change == "actor":
            data["curation_history"][-1]["curator"] = "another-curator"
        else:
            data["curation_history"][-1]["llm_assisted"] = False
        previous = yaml.safe_dump(data)
        revised["input_sha256"] = revised["prior_output_sha256"] = curations.digest(previous)
    with pytest.raises(ValueError, match="curated input"):
        editor.curate_record_text(previous, revised)


def test_seed_drift_and_unknown_owner_fail_closed(entry, monkeypatch):
    monkeypatch.setattr(curations, "load_curations", lambda: {entry["identifier"]: entry})
    out = curations.curate_seed(ORIGINAL, "seed_test")
    assert out == editor.curate_record_text(ORIGINAL, entry)
    assert merge_on_reseed(out, out) == out
    with pytest.raises(ValueError, match="source drift"):
        curations.curate_seed(ORIGINAL.replace("inspected stub", "new source"), "seed_test")
    with pytest.raises(ValueError, match="source drift"):
        curations.curate_seed(ORIGINAL, "seed_other")
    unrelated = ORIGINAL.replace("TEST_MOTIF", "UNRELATED")
    assert curations.curate_seed(unrelated, "seed_test") == unrelated


def test_ledger_refuses_status_promotion_and_qualification(entry, tmp_path, monkeypatch):
    ledger = tmp_path / "ledger.yaml"
    monkeypatch.setattr(curations, "LEDGER", ledger)
    for blocks in (
        {"mapping_status": "mapping_status: REVIEWED\n"},
        {"canonical_examples": "canonical_examples: []\n"},
    ):
        invalid = copy.deepcopy(entry)
        invalid["blocks"].update(blocks)
        ledger.write_text(yaml.safe_dump({"version": 1, "records": [invalid]}))
        curations.load_curations.cache_clear()
        with pytest.raises(ValueError):
            curations.load_curations()
    curations.load_curations.cache_clear()


def test_cli_dry_run_apply_and_replay(entry, tmp_path, monkeypatch):
    path = tmp_path / entry["path"]
    path.parent.mkdir(parents=True)
    path.write_text(ORIGINAL)
    monkeypatch.setattr(editor, "ROOT", tmp_path)
    monkeypatch.setattr(editor, "TRAITS_ROOT", tmp_path / "data/traits")
    monkeypatch.setattr(editor, "load_curations", lambda: {entry["identifier"]: entry})
    assert editor.main([]) == 0
    assert path.read_text() == ORIGINAL
    assert editor.main(["--only", "proteintraitsmech:MISSING", "--apply"]) == 1
    assert path.read_text() == ORIGINAL
    assert editor.main(["--apply"]) == 0
    out = path.read_text()
    assert out == editor.curate_record_text(ORIGINAL, entry)
    assert editor.main(["--apply"]) == 0
    assert path.read_text() == out


def test_invalid_candidate_blocks_all_corpus_writes(entry, tmp_path, monkeypatch):
    path = tmp_path / entry["path"]
    path.parent.mkdir(parents=True)
    path.write_text(ORIGINAL)
    entry["blocks"]["detection_methods"] = "detection_methods:\n  - unknown_field: bad\n"
    entry["output_sha256"] = curations.digest(curations.apply_blocks(ORIGINAL, entry))
    entry["blocks_sha256"] = curations.blocks_digest(entry["blocks"])
    monkeypatch.setattr(editor, "ROOT", tmp_path)
    monkeypatch.setattr(editor, "TRAITS_ROOT", tmp_path / "data/traits")
    monkeypatch.setattr(editor, "load_curations", lambda: {entry["identifier"]: entry})
    assert editor.main(["--apply"]) == 1
    assert path.read_text() == ORIGINAL
