"""Fail-closed tests for restoring member-signature InterPro abstracts."""

from __future__ import annotations

import importlib
import pathlib
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
repair = importlib.import_module("repair_interpro_member_truncations")


def _entry(full: str) -> dict:
    return {"name": "x", "abstract": full, "llm": False, "reviewed": False}


def _record(
    current: str,
    *,
    source: str = "InterPro:IPR013302 abstract (PRINTS PR01893 is a member signature)",
) -> str:
    return f"""identifier: PRINTS:PR01893
label: Wnt-10 protein signature
definition: >-
  {current}
definition_source: {source}
trait_axis: SEQUENCE
trait_category: SEQ_FAMILY
term_kind: CLASS
mapping_status: SEEDED
definitions:
  - kind: GENERAL
    text: >-
      {current}
    source: {source}
    method: SOURCED
license: CC0-1.0
"""


def test_exact_historical_slice_restores_both_definition_values(tmp_path):
    full = "A" * repair.OLD_CAP + " subtype-defining tail."
    old = repair._collapse(full[: repair.OLD_CAP])
    path = tmp_path / "record.yaml"
    status, planned = repair.plan_one(path, _record(old), {"IPR013302": _entry(full)})
    assert status == "REPAIR"
    assert planned is not None
    updated = yaml.safe_load(planned.text)
    assert updated["definition"] == full
    assert updated["definitions"][0]["text"] == full


def test_nonmatching_or_curated_records_are_protected(tmp_path):
    full = "A" * repair.OLD_CAP + " tail."
    entries = {"IPR013302": _entry(full)}
    status, planned = repair.plan_one(tmp_path / "x.yaml", _record("curator text"), entries)
    assert (status, planned) == ("PROTECTED_NONMATCHING_DEFINITION", None)

    curated = _record(repair._collapse(full[: repair.OLD_CAP])).replace(
        "mapping_status: SEEDED", "mapping_status: REVIEWED"
    )
    status, planned = repair.plan_one(tmp_path / "x.yaml", curated, entries)
    assert (status, planned) == ("PROTECTED_CURATED_RECORD", None)


def test_mismatched_definitions_array_fails_closed(tmp_path):
    full = "A" * repair.OLD_CAP + " tail."
    old = repair._collapse(full[: repair.OLD_CAP])
    text = _record(old).replace(f"      {old}", "      different text")
    try:
        repair.plan_one(tmp_path / "x.yaml", text, {"IPR013302": _entry(full)})
    except repair.RepairError as exc:
        assert "definition and matching definitions[] text disagree" in str(exc)
    else:
        raise AssertionError("inconsistent paired definitions were accepted")


def test_apply_is_retired_before_loading_sources(monkeypatch, capsys):
    def unexpected_source_load():
        raise AssertionError("an obsolete apply must stop before reading source inputs")

    monkeypatch.setattr(repair, "interpro_entries", unexpected_source_load)
    assert repair.main(["--apply"]) == 2
    error = capsys.readouterr().err
    assert "--apply is disabled" in error
    assert "source-native KDAT" in error
    assert "no files written" in error
