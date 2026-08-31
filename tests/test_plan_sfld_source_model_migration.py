"""Tests for the read-only SFLD source-model migration planner."""

from __future__ import annotations

import gzip
import hashlib
import json
import pathlib
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import plan_sfld_source_model_migration as planner  # noqa: E402
from sfld_release import (  # noqa: E402
    SfldHmmModel,
    SfldRelease,
    SfldSite,
    SfldSiteRule,
    build_sfld_release_manifest,
)


def _model(accession: str, level: str, digit: str, *, description: str) -> SfldHmmModel:
    return SfldHmmModel(
        accession=accession,
        native_classification_level=level,
        name=f"model_{accession}",
        description=description,
        model_length=4,
        gathering_sequence_score=10.5,
        gathering_domain_score=9.25,
        training_sequence_count=3,
        hmm_checksum=int(digit),
        source_record_sha256=digit * 64,
    )


def _snapshot() -> planner.SourceSnapshot:
    models = {
        "SFLDS00001": _model(
            "SFLDS00001",
            "SUPERFAMILY",
            "1",
            description="Root chemistry",
        ),
        "SFLDF00001": _model(
            "SFLDF00001",
            "FAMILY",
            "2",
            description="Specific reaction",
        ),
    }
    site_rules = {
        "SFLDS00001": SfldSiteRule("SFLDS00001", (), (), "3" * 64),
        "SFLDF00001": SfldSiteRule(
            "SFLDF00001",
            (
                SfldSite(1, 1, "nucleophile"),
                SfldSite(2, 4, None),
            ),
            ("DE", "DQ"),
            "4" * 64,
        ),
    }
    release = SfldRelease(
        release="4",
        hmm_path=pathlib.Path("captured.hmm"),
        hierarchy_path=pathlib.Path("captured.hierarchy"),
        sites_path=pathlib.Path("captured.sites"),
        hmm_sha256="5" * 64,
        hierarchy_sha256="6" * 64,
        sites_sha256="7" * 64,
        models=models,
        site_rules=site_rules,
        ancestors={"SFLDF00001": ("SFLDS00001",)},
        direct_parents={"SFLDF00001": "SFLDS00001"},
    )
    return planner.SourceSnapshot(
        release=release,
        manifest=build_sfld_release_manifest(release),
        interpro_types={"IPR000001": "family", "IPR000002": "domain"},
        interpro_xml_sha256="8" * 64,
    )


def _record(
    tmp_path: pathlib.Path,
    identifier: str,
    label: str,
    *,
    parent: str | None = None,
    interpro: str | None = None,
    generated: bool = False,
    path_directory: str = "data/traits/function/protein_family/sfld",
) -> planner.TraitCapture:
    path = tmp_path / path_directory / f"{identifier.split(':', 1)[1].lower()}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if generated:
        source = "SFLD signature name (composed; no curated InterPro abstract)"
    else:
        assert interpro is not None
        source = f"InterPro:{interpro} abstract (SFLD member signature)"
    record: dict[str, object] = {
        "identifier": identifier,
        "label": label,
        "definition": f"Definition for {identifier}",
        "definition_source": source,
        "trait_axis": "FUNCTION",
        "trait_category": "FUNC_PROTEIN_FAMILY",
        "term_kind": "CLASS",
    }
    if parent is not None:
        record["parent_traits"] = [parent]
    if interpro is not None:
        record["mapped_xrefs"] = [
            {
                "object": f"InterPro:{interpro}",
                "mapping_source": "interpro-member-list",
            }
        ]
    raw = yaml.safe_dump(record, sort_keys=False).encode()
    path.write_bytes(raw)
    return planner.TraitCapture(
        path=path,
        relative_to_traits=path.relative_to(tmp_path / "data/traits"),
        record=record,
        yaml_sha256=hashlib.sha256(raw).hexdigest(),
    )


def _records(tmp_path: pathlib.Path) -> dict[str, planner.TraitCapture]:
    return {
        "SFLD:SFLDS00001": _record(
            tmp_path,
            "SFLD:SFLDS00001",
            "Root chemistry",
            interpro="IPR000001",
        ),
        "SFLD:SFLDF00001": _record(
            tmp_path,
            "SFLD:SFLDF00001",
            "Specific reaction",
            parent="SFLD:SFLDS00001",
            interpro="IPR000002",
        ),
        "SFLD:SFLDF99999": _record(
            tmp_path,
            "SFLD:SFLDF99999",
            "API-only signature",
            generated=True,
        ),
    }


def test_build_plan_partitions_executable_and_modelless_records_without_authorizing_writes(
    tmp_path,
):
    snapshot = _snapshot()
    records = _records(tmp_path)

    rows, summary = planner.build_plan(
        records=records,
        snapshot=snapshot,
        repo_root=tmp_path,
        expected_modelless_accessions=frozenset({"SFLDF99999"}),
    )

    assert [row["identifier"] for row in rows] == sorted(records)
    by_id = {row["identifier"]: row for row in rows}
    family = by_id["SFLD:SFLDF00001"]
    assert family["profile_status"] == "SOURCE_PROFILE_AVAILABLE_NOT_SERIALIZED"
    assert family["parent_status"] == "MATCHES_SOURCE_HIERARCHY"
    assert family["source_profile_projection"]["site_feature_patterns"] == ["DE", "DQ"]
    assert family["source_profile_projection_status"] == (
        "SOURCE_FACT_NOT_A_PROTEIN_MATCH_OR_MIGRATION_AUTHORIZATION"
    )
    assert family["definition_status"] == "INTERPRO_DOMAIN_ABSTRACT_GRANULARITY_REVIEW"
    assert family["definition_review_projection"]["definition"]["value"] == (
        "Definition for SFLD:SFLDF00001"
    )
    assert family["definition_review_projection_sha256"] == planner.value_sha256(
        family["definition_review_projection"]
    )
    assert "INTERPRO_DOMAIN_GRANULARITY_REVIEW" in family["review_requirements"]

    model_less = by_id["SFLD:SFLDF99999"]
    assert model_less["source_model"] is None
    assert model_less["source_profile_projection"] is None
    assert model_less["classification"] == ("NO_EXECUTABLE_MODEL_DISPOSITION_REVIEW_REQUIRED")
    assert not model_less["grounding_eligible"]

    assert summary["source_model_count"] == 2
    assert summary["current_record_count"] == 3
    assert summary["model_less_current_count"] == 1
    assert summary["definition_status_counts"] == {
        "GENERATED_SIGNATURE_RESTATEMENT": 1,
        "INTERPRO_DOMAIN_ABSTRACT_GRANULARITY_REVIEW": 1,
        "INTERPRO_FAMILY_ABSTRACT": 1,
    }
    assert summary["content_ready_count"] == 0
    assert summary["review_required_count"] == 3
    assert summary["serialization_status"] == "NOT_PERFORMED"
    assert not summary["writer_available"]
    assert not summary["apply_authorized"]


def test_build_plan_is_deterministic_and_binds_every_row(tmp_path):
    snapshot = _snapshot()
    records = _records(tmp_path)
    kwargs = {
        "records": records,
        "snapshot": snapshot,
        "repo_root": tmp_path,
        "expected_modelless_accessions": frozenset({"SFLDF99999"}),
    }

    first_rows, first_summary = planner.build_plan(**kwargs)
    second_rows, second_summary = planner.build_plan(**kwargs)

    assert first_rows == second_rows
    assert first_summary == second_summary
    assert first_summary["rows_sha256"] == planner.rows_sha256(first_rows)
    assert first_summary["plan_id"].startswith(planner.PLAN_ID_PREFIX)
    assert planner.dump_plan(first_rows, first_summary).endswith("\n")
    for row in first_rows:
        without_hash = {key: value for key, value in row.items() if key != "row_sha256"}
        assert row["row_sha256"] == planner.value_sha256(without_hash)


def test_build_plan_refuses_an_open_ended_current_only_exception(tmp_path):
    records = _records(tmp_path)
    extra = _record(
        tmp_path,
        "SFLD:SFLDG99998",
        "Unexpected extra",
        generated=True,
    )
    records["SFLD:SFLDG99998"] = extra

    with pytest.raises(planner.SfldMigrationPlanError, match="current-only record set"):
        planner.build_plan(
            records=records,
            snapshot=_snapshot(),
            repo_root=tmp_path,
            expected_modelless_accessions=frozenset({"SFLDF99999"}),
        )


def test_build_plan_refuses_record_index_key_mismatch(tmp_path):
    records = _records(tmp_path)
    records["SFLD:SFLDF00002"] = records.pop("SFLD:SFLDF00001")

    with pytest.raises(planner.SfldMigrationPlanError, match="index key"):
        planner.build_plan(
            records=records,
            snapshot=_snapshot(),
            repo_root=tmp_path,
            expected_modelless_accessions=frozenset({"SFLDF99999"}),
        )


def test_plan_record_exposes_parent_profile_path_and_route_drift(tmp_path):
    snapshot = _snapshot()
    capture = _record(
        tmp_path,
        "SFLD:SFLDF00001",
        "Specific  reaction",
        parent="SFLD:SFLDS99999",
        interpro="IPR000002",
        path_directory="data/traits/sequence/domain/sfld",
    )
    changed = dict(capture.record)
    changed["trait_axis"] = "SEQUENCE"
    changed["trait_category"] = "SEQ_DOMAIN"
    changed["sequence_profile_representations"] = [{"unexpected": True}]
    capture = planner.TraitCapture(
        capture.path,
        capture.relative_to_traits,
        changed,
        capture.yaml_sha256,
    )

    row = planner.plan_record(
        capture=capture,
        release=snapshot.release,
        interpro_types=snapshot.interpro_types,
        repo_root=tmp_path,
    )

    assert row["parent_status"] == "HIERARCHY_REVIEW"
    assert row["profile_status"] == "SOURCE_PROFILE_SERIALIZATION_CONFLICT_REVIEW"
    assert row["path_status"] == "PATH_REVIEW"
    assert row["route_status"] == "CURRENT_ROUTE_DRIFT_REVIEW"
    assert row["source_label_status"] == ("SOURCE_DESCRIPTION_WHITESPACE_NORMALIZATION_REVIEW")
    assert {
        "HIERARCHY_REVIEW",
        "PROFILE_SERIALIZATION_CONFLICT_REVIEW",
        "PATH_REVIEW",
        "CURRENT_ROUTE_DRIFT_REVIEW",
        "LABEL_NORMALIZATION_REVIEW",
    }.issubset(row["review_requirements"])


def test_index_finds_sfld_record_outside_legacy_route(tmp_path):
    traits = tmp_path / "traits"
    path = traits / "somewhere" / "record.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(
        "identifier: SFLD:SFLDF00001\n"
        "label: test\n"
        "trait_axis: FUNCTION\n"
        "trait_category: FUNC_PROTEIN_FAMILY\n"
    )

    indexed = planner.index_sfld_records(traits)

    assert list(indexed) == ["SFLD:SFLDF00001"]
    assert indexed["SFLD:SFLDF00001"].relative_to_traits == pathlib.Path("somewhere/record.yaml")


def test_index_rejects_duplicate_yaml_keys_before_namespace_filter(tmp_path):
    traits = tmp_path / "traits"
    path = traits / "record.yaml"
    traits.mkdir()
    path.write_text("identifier: OTHER:x\nlabel: SFLD marker\nlabel: duplicate\n")

    with pytest.raises(planner.SfldMigrationPlanError, match="duplicate YAML key"):
        planner.index_sfld_records(traits)


def test_index_rejects_noncanonical_sfld_namespace_spelling(tmp_path):
    traits = tmp_path / "traits"
    path = traits / "record.yaml"
    traits.mkdir()
    path.write_text("identifier: sfld:SFLDF00001\nlabel: test\n")

    with pytest.raises(planner.SfldMigrationPlanError, match="noncanonical SFLD namespace"):
        planner.index_sfld_records(traits)


def test_manifest_loader_requires_exact_canonical_bytes_and_unique_keys():
    expected = {"manifest_sha256": "0" * 64, "schema_version": 1}
    canonical = (planner.canonical_json(expected) + "\n").encode()

    assert planner._load_exact_manifest(canonical, expected) == expected
    with pytest.raises(planner.SfldMigrationPlanError, match="exact canonical projection"):
        planner._load_exact_manifest(canonical.replace(b":1", b": 1"), expected)
    with pytest.raises(planner.SfldMigrationPlanError, match="duplicate JSON key"):
        planner._load_exact_manifest(
            b'{"manifest_sha256":"' + b"0" * 64 + b'","schema_version":1,"schema_version":1}\n',
            expected,
        )


def test_source_snapshot_parses_only_immutable_checksum_bound_captures(tmp_path, monkeypatch):
    hmm_raw = b"captured HMM bytes\n"
    hierarchy_raw = b"captured hierarchy bytes\n"
    sites_raw = b"captured sites bytes\n"
    interpro_raw = gzip.compress(b'<interpro id="IPR000001" type="Family">\n')
    hmm_path = tmp_path / "source" / "sfld.hmm"
    hierarchy_path = tmp_path / "source" / "sfld_hierarchy_flat.txt"
    sites_path = tmp_path / "source" / "sfld_sites.annot"
    manifest_path = tmp_path / "source" / "sfld_release_manifest.json"
    interpro_path = tmp_path / "source" / "interpro.xml.gz"
    hmm_path.parent.mkdir()
    hmm_path.write_bytes(hmm_raw)
    hierarchy_path.write_bytes(hierarchy_raw)
    sites_path.write_bytes(sites_raw)
    interpro_path.write_bytes(interpro_raw)

    base = _snapshot().release
    release = SfldRelease(
        release=base.release,
        hmm_path=pathlib.Path("immutable-capture.hmm"),
        hierarchy_path=pathlib.Path("immutable-capture.hierarchy"),
        sites_path=pathlib.Path("immutable-capture.sites"),
        hmm_sha256=hashlib.sha256(hmm_raw).hexdigest(),
        hierarchy_sha256=hashlib.sha256(hierarchy_raw).hexdigest(),
        sites_sha256=hashlib.sha256(sites_raw).hexdigest(),
        models=base.models,
        site_rules=base.site_rules,
        ancestors=base.ancestors,
        direct_parents=base.direct_parents,
    )
    manifest = build_sfld_release_manifest(release)
    manifest_path.write_bytes((planner.canonical_json(manifest) + "\n").encode())

    def fake_load(captured_hmm, captured_hierarchy, captured_sites, **kwargs):
        # Replace the original after capture. The parser must still receive the
        # immutable temporary copy, never a reopened original path.
        hmm_path.write_bytes(b"replacement after verified capture\n")
        assert pathlib.Path(captured_hmm).read_bytes() == hmm_raw
        assert pathlib.Path(captured_hierarchy).read_bytes() == hierarchy_raw
        assert pathlib.Path(captured_sites).read_bytes() == sites_raw
        assert kwargs["expected_hmm_sha256"] == release.hmm_sha256
        assert not kwargs["enforce_release_contract"]
        return release

    monkeypatch.setattr(planner, "load_sfld_release", fake_load)

    snapshot = planner.load_verified_source_snapshot(
        hmm_path=hmm_path,
        hierarchy_path=hierarchy_path,
        sites_path=sites_path,
        manifest_path=manifest_path,
        interpro_path=interpro_path,
        expected_hmm_sha256=release.hmm_sha256,
        expected_hierarchy_sha256=release.hierarchy_sha256,
        expected_sites_sha256=release.sites_sha256,
        expected_interpro_sha256=hashlib.sha256(interpro_raw).hexdigest(),
        enforce_release_contract=False,
    )

    assert snapshot.release is release
    assert snapshot.manifest == manifest
    assert snapshot.interpro_types == {"IPR000001": "family"}
    assert hmm_path.read_bytes() == b"replacement after verified capture\n"


def test_source_snapshot_rejects_noncanonical_manifest_before_planning(tmp_path, monkeypatch):
    raw = {"hmm": b"hmm\n", "hierarchy": b"hierarchy\n", "sites": b"sites\n"}
    source = tmp_path / "source"
    source.mkdir()
    for name, payload in raw.items():
        (source / name).write_bytes(payload)
    interpro_raw = gzip.compress(b'<interpro id="IPR000001" type="Family">\n')
    interpro = source / "interpro.xml.gz"
    interpro.write_bytes(interpro_raw)

    base = _snapshot().release
    release = SfldRelease(
        release=base.release,
        hmm_path=source / "hmm",
        hierarchy_path=source / "hierarchy",
        sites_path=source / "sites",
        hmm_sha256=hashlib.sha256(raw["hmm"]).hexdigest(),
        hierarchy_sha256=hashlib.sha256(raw["hierarchy"]).hexdigest(),
        sites_sha256=hashlib.sha256(raw["sites"]).hexdigest(),
        models=base.models,
        site_rules=base.site_rules,
        ancestors=base.ancestors,
        direct_parents=base.direct_parents,
    )
    expected_manifest = build_sfld_release_manifest(release)
    manifest_path = source / "manifest.json"
    # Semantically equal JSON is insufficient: the installed contract is exact
    # canonical bytes plus one LF.
    manifest_path.write_text(json.dumps(expected_manifest, indent=2) + "\n")
    monkeypatch.setattr(planner, "load_sfld_release", lambda *_args, **_kwargs: release)

    with pytest.raises(planner.SfldMigrationPlanError, match="exact canonical projection"):
        planner.load_verified_source_snapshot(
            hmm_path=source / "hmm",
            hierarchy_path=source / "hierarchy",
            sites_path=source / "sites",
            manifest_path=manifest_path,
            interpro_path=interpro,
            expected_hmm_sha256=release.hmm_sha256,
            expected_hierarchy_sha256=release.hierarchy_sha256,
            expected_sites_sha256=release.sites_sha256,
            expected_interpro_sha256=hashlib.sha256(interpro_raw).hexdigest(),
            enforce_release_contract=False,
        )


def test_interpro_type_parser_uses_captured_gzip_and_rejects_duplicates():
    payload = gzip.compress(
        b'<interpro id="IPR000001" type="Family">\n'
        b'<interpro id="IPR000002" type="Homologous_superfamily">\n'
    )
    assert planner.parse_interpro_entry_types(payload) == {
        "IPR000001": "family",
        "IPR000002": "homologous_superfamily",
    }

    duplicate = gzip.compress(
        b'<interpro id="IPR000001" type="Family">\n<interpro id="IPR000001" type="Domain">\n'
    )
    with pytest.raises(planner.SfldMigrationPlanError, match="duplicate entry IPR000001"):
        planner.parse_interpro_entry_types(duplicate)


def test_cli_surface_has_no_apply_output_or_writer_option():
    option_strings = {
        option for action in planner._parser()._actions for option in action.option_strings
    }
    assert "--apply" not in option_strings
    assert "--output" not in option_strings
    assert "--write" not in option_strings
