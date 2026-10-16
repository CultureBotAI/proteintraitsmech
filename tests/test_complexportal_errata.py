"""The scientific repair and future seed generation must agree (#1114)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import complexportal_errata as errata
import repair_complexportal_errata as repair
import seed_complexportal as seeder
from record_io import merge_on_reseed

LABEL = "SOD1-CCS1 superoxide dismutase heterodimer"
GOS = [("GO:0019430", "superoxide removal"), ("GO:0006825", "copper ion transport"),
       ("GO:1902693", "SOD1-CCS1 complex"), ("GO:0016532", "superoxide dismutase copper chaperone activity")]


def seed(description=errata.SOURCE_DESCRIPTION, **kwargs):
    args = dict(ac=errata.ACCESSION, name=LABEL, taxon_name="",
                members=sorted(errata.MEMBERS), subparts=[], gos=GOS,
                description=description)
    args.update(kwargs)
    return seeder.build_yaml(**args)


@pytest.fixture
def original():
    return (
        f"identifier: {errata.IDENTIFIER}\n"
        f'label: "{LABEL}"\n'
        f"definition: >-\n  {errata.SOURCE_DESCRIPTION}{repair.TAIL}\n"
        "definition_source: Complex Portal\n"
        "trait_axis: FUNCTION\ntrait_category: FUNC_INTERACTION_PARTNER\n"
        "term_kind: CLASS\nmapping_status: SEEDED\n"
        "parent_traits:\n  - GO:1902693\n"
        "trait_relations:\n"
        "  - predicate: biolink:has_part\n    object: UniProtKB:P00445\n"
        "    relation_source: Complex Portal\n"
        "  - predicate: biolink:has_part\n    object: UniProtKB:P40202\n"
        "    relation_source: Complex Portal\n"
        "xrefs:\n  - GO:0019430\n  - GO:0006825\n  - GO:1902693\n  - GO:0016532\n"
        "license: CC0 (EBI Complex Portal)\n"
    )


@pytest.mark.parametrize("description", [errata.SOURCE_DESCRIPTION,
                                         errata.CORRECTED_DESCRIPTION,
                                         errata.SOURCE_DESCRIPTION.replace("insertion", " insertion")])
def test_seeder_repairs_only_the_reviewed_chemistry(description):
    text = seed(description)
    data = yaml.safe_load(text)
    assert data["definition"] == errata.CORRECTED_DESCRIPTION + repair.TAIL
    assert data["definition_source"] == errata.DEFINITION_SOURCE
    assert data["mapping_status"] == "PROPOSED"
    assert data["curation_history"][0]["llm_assisted"] is True
    assert data["curation_history"][0]["curator"] == "claude"
    assert "canonical_examples" not in data
    assert "H48F" in data["evidence"][1]["notes"]


def test_unrelated_seeding_is_byte_unchanged():
    assert seed("A test complex.", ac="CPX-9999", name="Example", members=[], gos=[]) == (
        "identifier: ComplexPortal:CPX-9999\nlabel: Example\ndefinition: >-\n"
        "  A test complex. A curated stable macromolecular complex (Complex Portal) with 0 subunits.\n"
        "definition_source: Complex Portal\ntrait_axis: FUNCTION\n"
        "trait_category: FUNC_INTERACTION_PARTNER\nterm_kind: CLASS\nmapping_status: SEEDED\n"
        "parent_traits:\n  - GO:0032991\nlicense: CC0 (EBI Complex Portal)\n"
    )


@pytest.mark.parametrize("kwargs", [
    {"description": "New upstream wording: water and hydrogen peroxide."},
    {"description": ""},
    {"description": errata.SOURCE_DESCRIPTION + " Additional claim."},
    {"members": ["UniProtKB:P00445"]},
    {"members": ["UniProtKB:P00445", "UniProtKB:P00445"]},
    {"subparts": ["ComplexPortal:CPX-2896"]},
])
def test_seeder_fails_closed_on_source_drift(kwargs):
    with pytest.raises(ValueError, match="re-review"):
        seed(**kwargs)


def test_repair_is_minimal_and_idempotent(original):
    out = repair.repair_record_text(original)
    assert repair.repair_record_text(out) == out
    old, new = yaml.safe_load(original), yaml.safe_load(out)
    changed = {key for key in old.keys() | new.keys() if old.get(key) != new.get(key)}
    assert changed == {"definition", "definition_source", "mapping_status", "evidence", "curation_history"}
    assert old["definition"].replace("water and hydrogen peroxide", "oxygen and hydrogen peroxide") == new["definition"]
    for key in ("evidence", "curation_history", "definition", "definition_source", "mapping_status"):
        assert new[key] == yaml.safe_load(seed())[key]
    assert out.count("action: source_erratum_cpx_2267") == 1
    assert 'label: "' + LABEL + '"' in out  # preserve original quoting


@pytest.mark.parametrize("old,new", [
    ("ComplexPortal:CPX-2267", "ComplexPortal:CPX-2896"),
    ("FUNC_INTERACTION_PARTNER", "FUNC_ENZYMATIC_ACTIVITY"),
    ("mapping_status: SEEDED", "mapping_status: REVIEWED"),
    ("definition_source: Complex Portal", "definition_source: another curator"),
    ("approximately 10 %", "approximately 20 %"),
    ("object: UniProtKB:P00445", "object: UniProtKB:P00441"),
])
def test_unexpected_or_curated_record_is_refused(original, old, new):
    with pytest.raises(ValueError):
        repair.repair_record_text(original.replace(old, new))


def test_existing_comment_and_evidence_preserved(original):
    extra = "# keep this comment\nevidence:\n  - reference: PMID:1\n    notes: Unrelated note\n"
    text = original.replace("license:", extra + "license:")
    out = repair.repair_record_text(text)
    assert extra in out
    assert yaml.safe_load(out)["evidence"][0]["notes"] == "Unrelated note"


@pytest.mark.parametrize("addition", [
    "evidence: []\n",
    "identifier: ComplexPortal:CPX-2267\n",
    'curation_history:\n  - timestamp: "2026-10-01T00:00:00Z"\n    curator: human\n',
])
def test_unspliceable_duplicate_and_history_inputs_refused(original, addition):
    with pytest.raises(ValueError):
        repair.repair_record_text(original + addition)


def test_partial_repair_is_not_reported_as_complete(original):
    partial = repair.repair_record_text(original).replace("llm_assisted: true", "llm_assisted: false")
    with pytest.raises(ValueError, match="curated"):
        repair.repair_record_text(partial)


def test_reseed_preserves_repair_and_human_curation(original):
    out = repair.repair_record_text(original)
    assert merge_on_reseed(out, seed()) == out
    curated = out.replace("mapping_status: PROPOSED", "mapping_status: REVIEWED")
    curated = curated.replace("oxygen and hydrogen peroxide", "oxygen plus hydrogen peroxide", 1)
    assert merge_on_reseed(curated, seed()) == curated


def test_main_dry_run_apply_and_repeat(tmp_path, monkeypatch, original):
    target = tmp_path / "target.yaml"
    target.write_text(original)
    monkeypatch.setattr(repair, "TARGET", target)
    assert repair.main([]) == 0
    assert target.read_text() == original
    assert repair.main(["--apply"]) == 0  # actual closed-mode atomic writer
    expected = repair.repair_record_text(original)
    assert target.read_text() == expected
    before = target.stat().st_mtime_ns
    assert repair.main(["--apply"]) == 0
    assert target.stat().st_mtime_ns == before


def test_main_refuses_invalid_record_without_replacing(tmp_path, monkeypatch, original):
    target = tmp_path / "target.yaml"
    invalid = original + "not_a_schema_field: value\n"
    target.write_text(invalid)
    monkeypatch.setattr(repair, "TARGET", target)
    assert repair.main(["--apply"]) == 1
    assert target.read_text() == invalid


def test_main_guard_refuses_curated_record(tmp_path, monkeypatch, original):
    target = tmp_path / "target.yaml"
    text = original.replace("mapping_status: SEEDED", "mapping_status: REVIEWED")
    target.write_text(text)
    monkeypatch.setattr(repair, "TARGET", target)
    assert repair.main(["--apply"]) == 1
    assert target.read_text() == text


@pytest.mark.parametrize("args", [[], ["--apply"]])
@pytest.mark.parametrize("corrected", [False, True])
def test_main_validates_even_dry_run_and_completed_records(
    tmp_path, monkeypatch, original, args, corrected
):
    text = repair.repair_record_text(original) if corrected else original
    invalid = text + "not_a_schema_field: value\n"
    target = tmp_path / "target.yaml"
    target.write_text(invalid)
    before = target.stat().st_mtime_ns
    monkeypatch.setattr(repair, "TARGET", target)
    assert repair.main(args) == 1
    assert target.read_text() == invalid
    assert target.stat().st_mtime_ns == before


@pytest.mark.parametrize("args", [[], ["--apply"]])
def test_main_rejects_malformed_completed_metadata_cleanly(
    tmp_path, monkeypatch, original, args
):
    text = repair.repair_record_text(original)
    from record_io import replace_block
    invalid = replace_block(text, "evidence", "evidence: invalid\n")
    target = tmp_path / "target.yaml"
    target.write_text(invalid)
    monkeypatch.setattr(repair, "TARGET", target)
    assert repair.main(args) == 1
    assert target.read_text() == invalid


def complex_tab_row(ac, name, description):
    return "\t".join([ac, name, "-", "559292", "P00445(1)|P40202(1)",
                      "-", "-", "GO:1902693(SOD1-CCS1 complex)", "-", description])


@pytest.mark.parametrize("args", [[], ["--apply"]])
@pytest.mark.parametrize("separate_files", [False, True])
@pytest.mark.parametrize("drift", ["description", "members"])
def test_seeder_source_drift_is_preflighted_before_any_write(
    tmp_path, monkeypatch, args, separate_files, drift
):
    raw = tmp_path / "raw"
    raw.mkdir()
    earlier = complex_tab_row("CPX-9999", "Earlier complex", "A different complex.") + "\n"
    later = complex_tab_row(errata.ACCESSION, LABEL, errata.SOURCE_DESCRIPTION) + "\n"
    if drift == "description":
        later = later.replace(errata.SOURCE_DESCRIPTION, "Unexpected upstream description.")
    else:
        later = later.replace("P00445(1)|P40202(1)", "P00441(1)|P40202(1)")
    if separate_files:
        (raw / "a.tsv").write_text(earlier)
        (raw / "b.tsv").write_text(later)
    else:
        (raw / "yeast.tsv").write_text(earlier + later)
    output = tmp_path / "output"
    monkeypatch.setattr(seeder, "RAW", raw)
    monkeypatch.setattr(seeder, "OUT_DIR", output)
    monkeypatch.setattr(sys, "argv", ["seed_complexportal.py", *args])
    assert seeder.main() == 1
    assert not output.exists(), "a drifted source must be rejected before installing earlier rows"


def test_seeder_cli_preview_apply_skip_and_curated_force(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    source = raw / "yeast.tsv"
    source.write_text(complex_tab_row(errata.ACCESSION, LABEL, errata.SOURCE_DESCRIPTION) + "\n")
    output = tmp_path / "output"
    target = output / f"{seeder.slug(LABEL)}-{errata.ACCESSION.lower()}.yaml"
    monkeypatch.setattr(seeder, "RAW", raw)
    monkeypatch.setattr(seeder, "OUT_DIR", output)
    monkeypatch.setattr(sys, "argv", ["seed_complexportal.py"])
    assert seeder.main() == 0
    assert not output.exists()
    monkeypatch.setattr(sys, "argv", ["seed_complexportal.py", "--apply"])
    assert seeder.main() == 0
    seeded = target.read_text()
    assert yaml.safe_load(seeded)["definition"] == errata.CORRECTED_DESCRIPTION + repair.TAIL
    before = target.stat().st_mtime_ns
    assert seeder.main() == 0
    assert target.stat().st_mtime_ns == before
    curated = seeded.replace("mapping_status: PROPOSED", "mapping_status: REVIEWED")
    curated = curated.replace("oxygen and hydrogen peroxide", "oxygen plus hydrogen peroxide", 1)
    target.write_text(curated)
    monkeypatch.setattr(sys, "argv", ["seed_complexportal.py", "--force"])
    assert seeder.main() == 0
    assert target.read_text() == curated
    monkeypatch.setattr(sys, "argv", ["seed_complexportal.py", "--force", "--apply"])
    assert seeder.main() == 0
    assert target.read_text() == curated
    source.write_text(complex_tab_row(errata.ACCESSION, LABEL, "Unexpected source drift.") + "\n")
    for args in ([], ["--apply"]):
        monkeypatch.setattr(sys, "argv", ["seed_complexportal.py", *args])
        assert seeder.main() == 0  # an existing, unselected target stays untouched
        assert target.read_text() == curated
        monkeypatch.setattr(sys, "argv", ["seed_complexportal.py", "--force", *args])
        assert seeder.main() == 1
        assert target.read_text() == curated
