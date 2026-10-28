"""Maintained seeders preserve reviewed fields and reject changed source emissions."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import seed_foundational_traits as foundational
import seed_localstructuralfeature as local_structural
import seed_secondary_structure as secondary
import structural_trait_curations as curations


SEEDERS = [
    (secondary, "emit", secondary.build_records, "seed_secondary_structure"),
    (local_structural, "yaml_for", lambda: local_structural.TERMS, "seed_localstructuralfeature"),
    (foundational, "emit_record", lambda: foundational.SPECS, "seed_foundational_traits"),
]


@pytest.mark.parametrize("module,emit_name,items,owner", SEEDERS, ids=[row[3] for row in SEEDERS])
def test_original_emissions_are_pinned_and_unrelated_records_are_unchanged(
    module, emit_name, items, owner, monkeypatch
):
    emit = getattr(module, emit_name)
    with monkeypatch.context() as original:
        original.setattr(module, "curate_seed", lambda text, _owner: text)
        raw = [(item, emit(item)) for item in items()]

    ledger = curations.load_curations()
    seen = set()
    unrelated = 0
    for item, original_text in raw:
        identifier = yaml.safe_load(original_text)["identifier"]
        emitted = emit(item)
        entry = ledger.get(identifier)
        if entry is None:
            assert emitted == original_text, identifier
            unrelated += 1
            continue
        assert curations.digest(original_text) == entry["seed_preimages"][owner], identifier
        expected = curations.apply_blocks(original_text, entry)
        assert emitted == expected, identifier
        data = yaml.safe_load(emitted)
        assert data["mapping_status"] == "PROPOSED"
        assert data["curation_history"][-1]["curator"] == "codex-gpt-6-astra"
        seen.add(identifier)

    assert seen == {identifier for identifier, entry in ledger.items()
                    if owner in entry["seed_preimages"]}
    assert seen and unrelated, "Exercise both reviewed and unrelated source emissions"


@pytest.mark.parametrize("module,emit_name,items,owner", SEEDERS, ids=[row[3] for row in SEEDERS])
def test_seeder_source_change_requires_new_review(module, emit_name, items, owner, monkeypatch):
    emit = getattr(module, emit_name)
    ledger = curations.load_curations()
    with monkeypatch.context() as original:
        original.setattr(module, "curate_seed", lambda text, _owner: text)
        selected = next(item for item in items()
                        if yaml.safe_load(emit(item))["identifier"] in ledger)
    if isinstance(selected, dict):
        changed = dict(selected, definition=selected["definition"] + " Unreviewed source change.")
    else:
        changed = replace(selected, definition=selected.definition + " Unreviewed source change.")
    with pytest.raises(ValueError, match=f"{owner} source drift"):
        emit(changed)
