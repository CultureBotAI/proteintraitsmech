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


def test_the_exit_contract_across_all_three_policies(capsys):
    """Default is no longer advisory (#585): it gates on what this repo can fix.

    Replaces an earlier test that asserted advisory-by-default, which is exactly the
    behaviour this change removes.
    """
    assert AUDIT.main(["--fail-on", "never"]) == 0
    capsys.readouterr()
    assert AUDIT.main([]) == 0  # today: one notice, nothing blocking
    default_out = capsys.readouterr().out
    assert "--fail-on error" in default_out
    assert AUDIT.main(["--fail-on", "any"]) == 1  # the notice blocks under 'any'
    capsys.readouterr()


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


def test_refresh_does_not_churn_the_ref_when_the_vocabulary_is_unchanged(tmp_path):
    """pinned_ref means "where these values came from", not "last ref seen".

    TraitMech commits for reasons that have nothing to do with its category enum.
    Rewriting a reviewed pin for each of those buries the refs that did change something.
    """
    root = tmp_path / "TraitMech"
    (root / "src" / "traitmech" / "schema").mkdir(parents=True)
    (root / "src" / "traitmech" / "schema" / "traitmech.yaml").write_text(
        yaml.safe_dump(
            {
                "enums": {
                    "TraitCategoryEnum": {"permissible_values": {"ALPHA": {"description": "a"}}}
                }
            }
        ),
        encoding="utf-8",
    )
    pin = tmp_path / "pin.yaml"
    pin.write_text(
        yaml.safe_dump(
            {
                "source_repository": "CultureBotAI/TraitMech",
                "source_path": "src/traitmech/schema/traitmech.yaml",
                "source_enum": "TraitCategoryEnum",
                "pinned_ref": "originalref0000",
                "governed_tokens": [],
                "permissible_values": {"ALPHA": {"description": "a"}},
            }
        ),
        encoding="utf-8",
    )
    before = pin.read_text(encoding="utf-8")
    assert AUDIT.refresh(root, pin) == 0
    assert pin.read_text(encoding="utf-8") == before, "unchanged vocabulary rewrote the pin"

    (root / "src" / "traitmech" / "schema" / "traitmech.yaml").write_text(
        yaml.safe_dump(
            {
                "enums": {
                    "TraitCategoryEnum": {
                        "permissible_values": {"ALPHA": {"description": "CHANGED"}}
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    assert AUDIT.refresh(root, pin) == 0
    assert "CHANGED" in pin.read_text(encoding="utf-8"), "a real change was not re-pinned"


# ---------------------------------------------------------------------------------------
# Promotion from advisory to a gate (#585). The point of the severity split is that the
# classes differ in WHO CAN FIX THEM, so they must differ in whether they block.
# ---------------------------------------------------------------------------------------


def test_every_finding_class_has_a_declared_severity():
    """A class with no entry defaults to error; make that a decision, not an accident."""
    emitted = {"MANIFEST_UNKNOWN_CATEGORY", "SHARED_TOKEN_MEANING_DRIFT", "SHARED_TOKEN_DROPPED"}
    assert emitted == set(AUDIT.SEVERITY), "a finding class has no declared severity"


def test_the_repo_fixable_classes_block_and_the_sibling_claim_does_not():
    assert AUDIT._blocks("MANIFEST_UNKNOWN_CATEGORY", "error") is True
    assert AUDIT._blocks("SHARED_TOKEN_DROPPED", "error") is True
    assert AUDIT._blocks("SHARED_TOKEN_MEANING_DRIFT", "error") is False


def test_fail_on_any_blocks_the_sibling_claim_too():
    assert AUDIT._blocks("SHARED_TOKEN_MEANING_DRIFT", "any") is True


def test_fail_on_never_blocks_nothing():
    for kind in AUDIT.SEVERITY:
        assert AUDIT._blocks(kind, "never") is False


def test_an_unknown_manifest_category_gates_by_default(tmp_path, monkeypatch, capsys):
    """The promotion itself: a category this repo can fix now fails the run."""
    manifest = tmp_path / "download.yaml"
    manifest.write_text(
        yaml.safe_dump([{"name": "X", "trait_categories": ["SEQ_NOT_A_REAL_CATEGORY"]}]),
        encoding="utf-8",
    )
    monkeypatch.setattr(AUDIT, "MANIFEST", manifest)
    assert AUDIT.main([]) == 1
    assert "ERROR MANIFEST_UNKNOWN_CATEGORY" in capsys.readouterr().out


def test_cross_mech_drift_alone_does_not_gate_by_default(capsys):
    """Today's real state: one notice, and CI stays green.

    If this ever fails, the pin and this Mech agree again -- delete the drift, not
    the test.
    """
    assert AUDIT.main([]) == 0
    out = capsys.readouterr().out
    assert "NOTICE SHARED_TOKEN_MEANING_DRIFT" in out
    assert "None blocking" in out


def test_ci_runs_the_audit_without_disabling_the_gate():
    """`just audit-cross-mech-categories --fail-on never` in CI would be a no-op gate."""
    workflow = (REPO / ".github" / "workflows" / "checks.yml").read_text(encoding="utf-8")
    invocation = [
        line
        for line in workflow.splitlines()
        if "audit-cross-mech-categories" in line and line.strip().startswith("- run:")
    ]
    assert len(invocation) == 1, invocation
    assert "--fail-on never" not in invocation[0]


@pytest.mark.parametrize(
    ("what", "attribute"),
    [
        ("the TraitMech category pin", "PINNED"),
        ("download.yaml", "MANIFEST"),
        ("the schema", "SCHEMA"),
    ],
)
def test_an_unreadable_input_fails_with_a_sentence_not_a_traceback(
    what, attribute, tmp_path, monkeypatch
):
    """This runs in a gate now; a traceback there reads as the audit having crashed (#589)."""
    monkeypatch.setattr(AUDIT, attribute, tmp_path / "absent.yaml")
    with pytest.raises(SystemExit, match=f"cannot read {what}"):
        AUDIT.main([])


def test_a_corrupt_pin_names_the_file_and_the_remedy(tmp_path, monkeypatch):
    bad = tmp_path / "pin.yaml"
    bad.write_text("permissible_values: [unclosed\n", encoding="utf-8")
    monkeypatch.setattr(AUDIT, "PINNED", bad)
    with pytest.raises(SystemExit, match="not valid YAML"):
        AUDIT.main([])
