"""The 12 Stage 4 CDD scientific repairs and future seed generation must agree (#1171, #1172)."""

from __future__ import annotations

import gzip
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cdd_errata as errata
import repair_cdd_errata as repair
import seed_cdd as seeder
from record_io import merge_on_reseed
from yaml_emit import yaml_escape

ACCESSIONS = tuple(errata.ERRATA)


def seed(acc: str = "cd09530", description: str | None = None, **kwargs) -> str:
    item = errata.ERRATA[acc]
    args = dict(
        acc=acc,
        short=item.label,
        desc=item.source_description if description is None else description,
        category="SEQ_DOMAIN",
        parent=item.parent,
    )
    args.update(kwargs)
    return seeder.build_yaml(**args)


def make_seeded_record(acc: str = "cd09530") -> str:
    item = errata.ERRATA[acc]
    return (
        f"identifier: {item.identifier}\n"
        f"label: {yaml_escape(item.label)}\n"
        f"definition: >-\n  {item.source_description}\n"
        "definition_source: NCBI CDD\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "term_kind: CLASS\n"
        "mapping_status: SEEDED\n"
        f"parent_traits:\n  - CDD:{item.parent}\n"
        "trait_relations:\n"
        "  - predicate: biolink:member_of\n"
        f"    object: CDD:{item.parent}\n"
        "    relation_source: derived\n"
        "canonical_examples:\n"
        "  - protein_id: UniProtKB:Q9P1V8\n"
        "    protein_label: Example protein\n"
        "    taxon_id: NCBITaxon:9606\n"
        "    taxon_label: Homo sapiens\n"
        "    sequence_length: 674\n"
        "    reviewed: true\n"
        "    source: SWISSPROT_PROFILE\n"
        '    fetched_at: "2026-07-27"\n'
        "license: US Government public domain\n"
    )


@pytest.fixture
def original() -> str:
    return make_seeded_record("cd09530")


@pytest.mark.parametrize("acc", ACCESSIONS)
@pytest.mark.parametrize("variant", ["source", "corrected", "status_suffix"])
def test_seeder_repairs_only_the_reviewed_cdd_errata(acc: str, variant: str):
    item = errata.ERRATA[acc]
    if variant == "source":
        desc = item.source_description
    elif variant == "corrected":
        desc = item.corrected_description
    else:
        desc = item.source_description + "; Reviewed."
    text = seed(acc, desc)
    data = yaml.safe_load(text)
    assert data["definition"] == item.corrected_description
    assert data["definition_source"] == item.definition_source
    assert data["mapping_status"] == "PROPOSED"
    assert data["curation_history"][0]["llm_assisted"] is True
    assert data["curation_history"][0]["curator"] == "claude"
    assert data["curation_history"][0]["action"] == item.event_action
    assert len(data["evidence"]) == len(item.evidence)


def test_unrelated_cdd_seeding_is_byte_unchanged():
    assert seeder.build_yaml(
        "cd99999", "TEST_DOM", "A test domain; Reviewed.", "SEQ_DOMAIN", "cl99999"
    ) == (
        "identifier: CDD:cd99999\n"
        "label: TEST_DOM\n"
        "definition: >-\n"
        "  A test domain\n"
        "definition_source: NCBI CDD\n"
        "trait_axis: SEQUENCE\n"
        "trait_category: SEQ_DOMAIN\n"
        "term_kind: CLASS\n"
        "mapping_status: SEEDED\n"
        "parent_traits:\n"
        "  - CDD:cl99999\n"
        "license: US Government public domain\n"
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"description": "New upstream wording."},
        {"description": ""},
        {
            "description": errata.ERRATA["cd09530"].source_description
            + " Additional claim."
        },
        {"short": "WRONG_SHORT"},
        {"category": "SEQ_HOMOLOGOUS_SUPERFAMILY"},
        {"parent": "cl99999"},
    ],
)
def test_seeder_fails_closed_on_source_drift(kwargs):
    with pytest.raises(ValueError, match="re-review"):
        seed("cd09530", **kwargs)


@pytest.mark.parametrize("acc", ACCESSIONS)
def test_repair_is_minimal_and_idempotent(acc: str):
    item = errata.ERRATA[acc]
    raw = make_seeded_record(acc)
    out = repair.repair_record_text(raw)
    assert repair.repair_record_text(out) == out
    old, new = yaml.safe_load(raw), yaml.safe_load(out)
    changed = {key for key in old.keys() | new.keys() if old.get(key) != new.get(key)}
    assert changed == {
        "definition",
        "definition_source",
        "mapping_status",
        "evidence",
        "curation_history",
    }
    seeded = yaml.safe_load(seed(acc))
    for key in (
        "evidence",
        "curation_history",
        "definition",
        "definition_source",
        "mapping_status",
    ):
        assert new[key] == seeded[key]
    assert out.count(f"action: {item.event_action}") == 1
    assert f"label: {yaml_escape(item.label)}" in out


@pytest.mark.parametrize(
    "old,new",
    [
        ("CDD:cd09530", "CDD:cd99999"),
        ("CDD:cd09530", "Pfam:PF00001"),
        ("SEQ_DOMAIN", "SEQ_HOMOLOGOUS_SUPERFAMILY"),
        ("label: SAM_Samd14", "label: OTHER_LABEL"),
        ("mapping_status: SEEDED", "mapping_status: REVIEWED"),
        ("definition_source: NCBI CDD", "definition_source: another curator"),
        ("SamD14 (or FAM15A)", "SamD14 (or FAM15B)"),
        ("CDD:cl15755", "CDD:cl99999"),
        (
            "source: SWISSPROT_PROFILE",
            "source: SWISSPROT_PROFILE\n    qualification_status: QUALIFIED",
        ),
        (
            "term_kind: CLASS",
            "term_kind: CLASS\nprotein_example_summary:\n  qualified_occurrence_count: 1",
        ),
    ],
)
def test_unexpected_curated_or_qualified_record_is_refused(original, old, new):
    with pytest.raises(ValueError):
        repair.repair_record_text(original.replace(old, new, 1))


def test_existing_comment_and_evidence_preserved(original):
    extra = (
        "# keep this comment\nevidence:\n  - reference: PMID:1\n    notes: Prior note\n"
    )
    text = original.replace("label: SAM_Samd14", 'label: "SAM_Samd14"').replace(
        "license:", extra + "license:"
    )
    out = repair.repair_record_text(text)
    assert extra in out
    assert 'label: "SAM_Samd14"' in out
    assert yaml.safe_load(out)["evidence"][0]["notes"] == "Prior note"


@pytest.mark.parametrize(
    "addition",
    [
        "evidence: []\n",
        "identifier: CDD:cd09530\n",
        'curation_history:\n  - timestamp: "2026-10-01T00:00:00Z"\n    curator: human\n',
    ],
)
def test_unspliceable_duplicate_and_history_inputs_refused(original, addition):
    with pytest.raises(ValueError):
        repair.repair_record_text(original + addition)


def test_partial_repair_is_not_reported_as_complete(original):
    partial = repair.repair_record_text(original).replace(
        "llm_assisted: true", "llm_assisted: false"
    )
    with pytest.raises(ValueError, match="curated"):
        repair.repair_record_text(partial)


def test_reseed_preserves_repair_and_human_curation(original):
    out = repair.repair_record_text(original)
    assert yaml.safe_load(merge_on_reseed(out, seed("cd09530"))) == yaml.safe_load(out)
    curated = out.replace("mapping_status: PROPOSED", "mapping_status: REVIEWED")
    curated = curated.replace(
        "SAMD15 (formerly FAM15A", "SAMD15 (legacy alias FAM15A", 1
    )
    assert yaml.safe_load(
        merge_on_reseed(curated, seed("cd09530"))
    ) == yaml.safe_load(curated)


def test_main_dry_run_apply_and_repeat(tmp_path, monkeypatch, original):
    target = tmp_path / "target.yaml"
    target.write_text(original)
    monkeypatch.setattr(repair, "TARGETS", {"cd09530": target})
    assert repair.main([]) == 0
    assert target.read_text() == original
    assert repair.main(["--apply"]) == 0
    expected = repair.repair_record_text(original)
    assert target.read_text() == expected
    before = target.stat().st_mtime_ns
    assert repair.main(["--apply"]) == 0
    assert target.stat().st_mtime_ns == before


def test_main_atomic_preflight_refuses_partial_batch_write(
    tmp_path, monkeypatch, original
):
    first = tmp_path / "first.yaml"
    second = tmp_path / "second.yaml"
    first.write_text(original)
    second.write_text(
        make_seeded_record("cd13344").replace("mapping_status: SEEDED", "mapping_status: REVIEWED")
    )
    monkeypatch.setattr(repair, "TARGETS", {"cd09530": first, "cd13344": second})
    assert repair.main(["--apply"]) == 1
    assert first.read_text() == original


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
    monkeypatch.setattr(repair, "TARGETS", {"cd09530": target})
    assert repair.main(args) == 1
    assert target.read_text() == invalid
    assert target.stat().st_mtime_ns == before


def test_qualified_record_requires_matching_durable_bindings(
    tmp_path, monkeypatch
):
    qualified = make_seeded_record("cd00104").replace(
        "source: SWISSPROT_PROFILE\n",
        "source: SWISSPROT_PROFILE\n"
        "    qualification_status: QUALIFIED\n"
        "    sequence_release: 2026_01\n"
        '    sequence_sha256: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n'
        "    trait_occurrences:\n"
        "      - source_evidence_id: ev:missing\n"
        "        qualification_status: QUALIFIED\n"
        "        scope: LOCALIZED\n"
        "        mapping_method: INTERPRO_MATCH\n"
        "        source_trait_id: CDD:cd00104\n"
        "        evidence_source: InterPro\n"
        '        source_release: "109.0"\n'
        '        sequence_sha256: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n'
        "        coordinate_frame: UNIPROT_CANONICAL\n"
        "        intervals:\n"
        "          - start: 1\n"
        "            end: 50\n",
    )
    with pytest.raises(ValueError, match="preimage re-binding"):
        repair.repair_record_text(qualified)
    repaired = repair.repair_record_text(qualified, allow_qualified=True)
    assert yaml.safe_load(repaired)["definition"] == errata.ERRATA["cd00104"].corrected_description

    target = tmp_path / "cd00104.yaml"
    target.write_text(qualified)
    monkeypatch.setattr(repair, "TARGETS", {"cd00104": target})
    assert repair.main(["--apply"]) == 1
    assert target.read_text() == qualified


def _write_raw_cdd(
    raw: Path, rows: list[tuple[str, str, str]], links: list[tuple[str, str]]
) -> None:
    raw.mkdir(parents=True, exist_ok=True)
    with gzip.open(raw / "cddid_all.tbl.gz", "wt", encoding="utf-8") as fh:
        for idx, (acc, short, desc) in enumerate(rows, start=100000):
            fh.write(f"{idx}\t{acc}\t{short}\t{desc}\t100\n")
    (raw / "family_superfamily_links").write_text(
        "".join(f"{acc}\t1\t{parent}\t2\n" for acc, parent in links),
        encoding="utf-8",
    )


@pytest.mark.parametrize("args", [[], ["--apply"]])
@pytest.mark.parametrize("drift", ["description", "parent"])
def test_seeder_source_drift_is_preflighted_before_any_write(
    tmp_path, monkeypatch, args, drift
):
    item = errata.ERRATA["cd09530"]
    raw = tmp_path / "raw"
    desc = (
        "Unexpected upstream description."
        if drift == "description"
        else item.source_description
    )
    parent = "cl99999" if drift == "parent" else item.parent
    _write_raw_cdd(
        raw,
        [
            ("cl15755", "SAM_SF", "SAM superfamily"),
            ("cl99999", "OTHER_SF", "Other superfamily"),
            ("cd00001", "EARLIER_DOM", "Earlier domain"),
            ("cd09530", item.label, desc),
        ],
        [("cd00001", "cl15755"), ("cd09530", parent)],
    )
    traits = tmp_path / "traits"
    monkeypatch.setattr(seeder, "RAW", raw)
    monkeypatch.setattr(seeder, "CDDID", raw / "cddid_all.tbl.gz")
    monkeypatch.setattr(seeder, "LINKS", raw / "family_superfamily_links")
    monkeypatch.setattr(seeder, "OUT_DIR", traits / "structure")
    monkeypatch.setattr(sys, "argv", ["seed_cdd.py", *args])
    assert seeder.main() == 1
    assert not traits.exists()


def test_seeder_cli_preview_apply_skip_and_curated_force(tmp_path, monkeypatch):
    item = errata.ERRATA["cd09530"]
    raw = tmp_path / "raw"
    _write_raw_cdd(
        raw,
        [
            (item.parent, "SAM_SF", "SAM superfamily"),
            (item.accession, item.label, item.source_description + "; Reviewed."),
        ],
        [(item.accession, item.parent)],
    )
    traits = tmp_path / "traits"
    target = traits / item.rel_path
    monkeypatch.setattr(seeder, "RAW", raw)
    monkeypatch.setattr(seeder, "CDDID", raw / "cddid_all.tbl.gz")
    monkeypatch.setattr(seeder, "LINKS", raw / "family_superfamily_links")
    monkeypatch.setattr(seeder, "OUT_DIR", traits / "structure")
    monkeypatch.setattr(sys, "argv", ["seed_cdd.py"])
    assert seeder.main() == 0
    assert not target.exists()
    monkeypatch.setattr(sys, "argv", ["seed_cdd.py", "--apply"])
    assert seeder.main() == 0
    seeded = target.read_text()
    assert yaml.safe_load(seeded)["definition"] == item.corrected_description
    before = target.stat().st_mtime_ns
    assert seeder.main() == 0
    assert target.stat().st_mtime_ns == before
    curated = seeded.replace("mapping_status: PROPOSED", "mapping_status: REVIEWED")
    curated = curated.replace("SAMD15 (formerly FAM15A", "SAMD15 (legacy alias FAM15A", 1)
    target.write_text(curated)
    monkeypatch.setattr(sys, "argv", ["seed_cdd.py", "--force", "--apply"])
    assert seeder.main() == 0
    assert target.read_text() == curated
    _write_raw_cdd(
        raw,
        [
            (item.parent, "SAM_SF", "SAM superfamily"),
            (item.accession, item.label, "Unexpected upstream drift."),
        ],
        [(item.accession, item.parent)],
    )
    for args in ([], ["--apply"]):
        monkeypatch.setattr(sys, "argv", ["seed_cdd.py", *args])
        assert seeder.main() == 0
        assert target.read_text() == curated
        monkeypatch.setattr(sys, "argv", ["seed_cdd.py", "--force", *args])
        assert seeder.main() == 1
        assert target.read_text() == curated
