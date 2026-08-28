"""Tests for the cross-Mech trait-category vocabulary audit (#581)."""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "audit_cross_mech_categories.py"


def _load():
    spec = importlib.util.spec_from_file_location("audit_cross_mech_categories", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = _load()


def test_an_unknown_manifest_category_is_reported():
    """#581's literal defect: check_sources never looked at trait_categories at all."""
    results = AUDIT.findings(
        local={"SEQ_DOMAIN": "d"},
        pinned={},
        declared={"SEQ_NOT_A_REAL_CATEGORY": ["Some Source"]},
    )
    assert [kind for kind, _ in results] == ["MANIFEST_UNKNOWN_CATEGORY"]
    assert "Some Source" in results[0][1]


def test_a_known_manifest_category_is_not_reported():
    assert AUDIT.findings({"SEQ_DOMAIN": "d"}, {}, {"SEQ_DOMAIN": ["S"]}) == []


def test_a_shared_token_whose_meaning_diverged_is_reported():
    results = AUDIT.findings(
        local={"UPPER": "organises the hierarchy"},
        pinned={"UPPER": "quality, biological process"},
        declared={},
    )
    assert [kind for kind, _ in results] == ["SHARED_TOKEN_MEANING_DRIFT"]


def test_a_shared_token_that_agrees_is_not_reported():
    assert AUDIT.findings({"OTHER": None}, {"OTHER": None}, {}) == []


def test_values_unique_to_one_mech_are_not_drift():
    """The vocabularies are deliberately disjoint; only the shared surface is governed."""
    assert AUDIT.findings({"SEQ_DOMAIN": "protein"}, {"METABOLISM": "organism"}, {}) == []


def test_the_real_repository_has_no_unknown_manifest_category():
    """Pins #581's actual state: all 50 declared categories are permissible today."""
    local = AUDIT.local_vocabulary()
    declared = AUDIT.manifest_categories()
    unknown = sorted(value for value in declared if value not in local)
    assert not unknown, f"download.yaml declares categories outside the enum: {unknown}"


def test_the_pin_records_where_it_came_from():
    pinned, ref, _governed = AUDIT.pinned_vocabulary()
    assert pinned, "the pin lists no values"
    assert len(ref) >= 7, "the pin does not record a source ref"
    document = yaml.safe_load(AUDIT.PINNED.read_text(encoding="utf-8"))
    assert document["source_repository"].endswith("TraitMech")
    assert document["source_enum"] == "TraitCategoryEnum"


def test_an_empty_local_vocabulary_fails_rather_than_reporting_agreement(tmp_path):
    """A vocabulary audit that read no vocabulary must not report agreement.

    The #534 shape: a check that passes because it measured nothing.
    """
    empty = tmp_path / "schema.yaml"
    empty.write_text(yaml.safe_dump({"enums": {}}), encoding="utf-8")
    with pytest.raises(SystemExit, match="no permissible values"):
        AUDIT.local_vocabulary(empty)


def test_the_audit_is_advisory_by_default_and_blocking_on_request(capsys):
    assert AUDIT.main([]) == 0
    advisory = capsys.readouterr().out
    assert "Advisory run" in advisory or "OK:" in advisory
    # --fail-on any is what a future CI gate would pass; it must actually bite when
    # there is something to bite on.
    code = AUDIT.main(["--fail-on", "any"])
    strict = capsys.readouterr().out
    if "finding(s)" in strict:
        assert code == 1
    else:
        assert code == 0


def test_a_governed_token_dropped_from_this_mech_is_reported():
    """The class the docstring promised and the code did not emit (#583).

    "In the pin but not local" cannot mean dropped -- nine TraitMech values are
    legitimately absent here -- so the governed surface is read from the pin rather
    than computed as an intersection.
    """
    results = AUDIT.findings(
        local={"OTHER": None},
        pinned={"OTHER": None, "UPPER": "x"},
        declared={},
        governed={"OTHER", "UPPER"},
    )
    assert [kind for kind, _ in results] == ["SHARED_TOKEN_DROPPED"]
    assert "UPPER" in results[0][1]


def test_an_ungoverned_token_absent_here_is_not_a_drop():
    """METABOLISM is TraitMech's and was never shared; its absence is by design."""
    assert (
        AUDIT.findings(
            local={"SEQ_DOMAIN": "d"},
            pinned={"METABOLISM": "organism"},
            declared={},
            governed={"OTHER"} & set(),
        )
        == []
    )


def test_the_pin_records_its_governed_surface():
    _values, _ref, governed = AUDIT.pinned_vocabulary()
    assert governed, "the pin records no governed_tokens"
    local = AUDIT.local_vocabulary()
    assert governed <= set(local), "a governed token is missing from this Mech's enum"


def test_verify_pin_detects_a_stale_pin(tmp_path):
    """CI has only this repo, so pin staleness is otherwise invisible (#584)."""
    root = tmp_path / "TraitMech"
    (root / "src" / "traitmech" / "schema").mkdir(parents=True)
    (root / "src" / "traitmech" / "schema" / "traitmech.yaml").write_text(
        yaml.safe_dump(
            {
                "enums": {
                    "TraitCategoryEnum": {
                        "permissible_values": {"UPPER": {"description": "something else entirely"}}
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    assert AUDIT.verify_pin(root) == 1


def test_verify_pin_reports_a_missing_checkout(tmp_path):
    assert AUDIT.verify_pin(tmp_path / "not-a-checkout") == 2
