"""Dry-run-only exact-state planning for the PRINTS source-model migration."""

from __future__ import annotations

import hashlib
import gzip
import json
import pathlib
import sys
from types import MappingProxyType

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import migrate_prints_source_model as migration  # noqa: E402
import prints_kdat  # noqa: E402
import validate_strict  # noqa: E402
from prints_kdat import build_fingerprint_representation, parse_prints_kdat  # noqa: E402
from prints_snapshot import load_hierarchy_jsonl  # noqa: E402
from validate_strict import validate_one  # noqa: E402

KDAT = (
    b"gc; TESTPRINT\n"
    b"gx; PR00001\n"
    b"gn; COMPOUND(2)\n"
    b"gt; Test fingerprint family signature\n"
    b"gd; Source-native fingerprint definition.\n"
    b"fm; FINAL MOTIF-SETS\n"
    b"fm; ----------------\n"
    b"fc; TEST1\n"
    b"fl; 3\n"
    b"ft; first motif\n"
    b"fd; ACD PROT1 1 1\n"
    b"fc; TEST2\n"
    b"fl; 2\n"
    b"ft; second motif\n"
    b"fd; EF PROT1 7 3\n"
)


@pytest.fixture
def source(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
    path = tmp_path / "prints.kdat"
    path.write_bytes(KDAT)
    fixture_sha256 = hashlib.sha256(KDAT).hexdigest()
    # These tests exercise planner state transitions with a compact synthetic
    # fingerprint while strict record validation intentionally pins the
    # parsed artifact digest.  Authenticate only these exact fixture bytes in
    # the test-scoped allowlist; test_prints_kdat.py separately proves that a
    # public wrapper or reparented release cannot cross the production guard.
    monkeypatch.setattr(
        prints_kdat,
        "_CANONICAL_RELEASE_FINGERPRINTS",
        MappingProxyType({prints_kdat.PRINTS_42_0_RELEASE: fixture_sha256}),
    )
    monkeypatch.setattr(validate_strict, "PRINTS_42_0_SHA256", fixture_sha256)
    release = parse_prints_kdat(path, fixture_sha256)
    signature = {
        "accession": "PR00001",
        "name": "TESTPRINT",
        "type": "family",
        "integrated": "IPR000001",
        "source_database": "prints",
    }
    entry = {
        "name": "Integrating family",
        "abstract": "An integrating InterPro abstract.",
        "llm": False,
        "reviewed": False,
    }
    fingerprint = release.fingerprints["PR00001"]
    legacy = migration.legacy_record(signature, entry, fingerprint)
    return release, signature, entry, fingerprint, legacy


def _plan(
    source,
    record,
    *,
    interpro_type="family",
    path=REPO / "data/traits/sequence/family/prints/test-pr00001.yaml",
    repo_root=REPO,
    legacy_generated_parent=None,
    normalized_hierarchy_domain_flag=False,
    normalized_hierarchy_row=None,
):
    release, signature, entry, fingerprint, _legacy = source
    hierarchy_row = normalized_hierarchy_row or {
        "accession": fingerprint.accession,
        "code": fingerprint.code,
        "domain_flag": normalized_hierarchy_domain_flag,
        "evalue_cutoff": "1e-04",
        "hierarchical_relations": [],
        "minimum_motif_count": 0,
    }
    return migration.plan_record(
        path=path,
        current_record_yaml_sha256="a" * 64,
        record=record,
        signature=signature,
        entry=entry,
        interpro_type=interpro_type,
        release=release,
        fingerprint=fingerprint,
        normalized_hierarchy_row=hierarchy_row,
        legacy_generated_parent=legacy_generated_parent,
        repo_root=repo_root,
    )


def test_exact_legacy_plan_is_source_native_and_idempotent(source, tmp_path):
    release, signature, entry, fingerprint, legacy = source
    row = _plan(source, legacy)

    assert row["record_state"] == "EXACT_LEGACY"
    assert row["classification"] == "CONTENT_MIGRATION_READY"
    assert row["changed_fields"] == [
        "definition",
        "definition_source",
        "definitions",
        "sequence_fingerprint_representations",
    ]
    representation = row["replacement_fields"]["sequence_fingerprint_representations"][0]
    assert representation["source_record_sha256"] == fingerprint.source_record_sha256
    assert [motif["length"] for motif in representation["motifs"]] == [3, 2]

    proposed = migration.apply_replacements(legacy, row["replacement_fields"], row["remove_fields"])
    second = _plan(source, proposed)
    assert second["record_state"] == "EXACT_SOURCE_NATIVE"
    assert second["classification"] == "ALREADY_SOURCE_NATIVE"
    assert second["changed_fields"] == []
    assert second["current_record_hash_domain"] == "EXACT_YAML_BYTES"
    assert second["content_proposal_hash_domain"] == "CANONICAL_JSON_SEMANTIC_OBJECT"
    assert second["proposed_record_sha256"] is None

    out = tmp_path / "proposed.yaml"
    out.write_text(yaml.safe_dump(proposed, sort_keys=False), encoding="utf-8")
    assert validate_one(out) == []


def test_unmanaged_content_is_preserved_but_nonlegacy_record_is_review_only(source):
    legacy = source[-1]
    changed = dict(legacy)
    changed["curation_notes"] = ["manual note"]
    row = _plan(source, changed)
    proposed = migration.apply_replacements(
        changed, row["replacement_fields"], row["remove_fields"]
    )

    assert row["record_state"] == "REVIEW_ONLY"
    assert row["classification"] == "RECORD_REVIEW_ONLY"
    assert row["legacy_mismatch_fields"] == ["curation_notes"]
    assert proposed["curation_notes"] == ["manual note"]
    assert row["record_review_value_projections"] == {
        "curation_notes": {
            "current": {"present": True, "value": ["manual note"]},
            "legacy_expected": {"present": False, "value": None},
            "proposed": {"present": True, "value": ["manual note"]},
        }
    }
    assert row["record_review_value_projections_sha256"] == migration.value_sha256(
        row["record_review_value_projections"]
    )


def test_record_review_projection_distinguishes_missing_from_explicit_null(source):
    changed = dict(source[-1])
    changed["curation_notes"] = None

    row = _plan(source, changed)

    assert row["legacy_mismatch_fields"] == ["curation_notes"]
    assert row["record_review_value_projections"]["curation_notes"] == {
        "current": {"present": True, "value": None},
        "legacy_expected": {"present": False, "value": None},
        "proposed": {"present": True, "value": None},
    }


def test_normalized_hierarchy_row_and_member_domain_alignment_are_bound(source):
    agrees = _plan(source, source[-1])
    disagrees = _plan(
        source,
        source[-1],
        normalized_hierarchy_domain_flag=True,
    )

    assert agrees["normalized_hierarchy_row"] == {
        "accession": "PR00001",
        "code": "TESTPRINT",
        "domain_flag": False,
        "evalue_cutoff": "1e-04",
        "hierarchical_relations": [],
        "minimum_motif_count": 0,
    }
    assert agrees["normalized_hierarchy_row_sha256"] == migration.value_sha256(
        agrees["normalized_hierarchy_row"]
    )
    assert agrees["normalized_hierarchy_domain_flag"] is False
    assert agrees["member_type_is_domain"] is False
    assert agrees["member_hierarchy_domain_alignment"] == "AGREES"
    assert disagrees["normalized_hierarchy_domain_flag"] is True
    assert disagrees["member_hierarchy_domain_alignment"] == "DISAGREES"


def test_normalized_hierarchy_binding_requires_exact_kdat_identity(source):
    wrong = {
        "accession": "PR00002",
        "code": "OTHER",
        "domain_flag": False,
        "evalue_cutoff": "1e-04",
        "hierarchical_relations": [],
        "minimum_motif_count": 0,
    }

    with pytest.raises(migration.PrintsMigrationError, match="disagrees with KDAT"):
        _plan(source, source[-1], normalized_hierarchy_row=wrong)


def test_legacy_parent_relation_is_a_blocked_deletion_candidate(source):
    legacy = dict(source[-1])
    legacy["parent_traits"] = ["PRINTS:PR00002"]
    row = _plan(
        source,
        legacy,
        interpro_type="domain",
        legacy_generated_parent="PR00002",
    )

    assert row["record_state"] == "EXACT_LEGACY"
    assert row["route_status"] == "ROUTING_REVIEW"
    assert row["hierarchy_status"] == "CONFIRMED_LEGACY_GENERATED_PARENT"
    assert row["classification"] == "ROUTING_AND_HIERARCHY_REPAIR_REQUIRED"
    assert row["review_requirements"] == ["ROUTING_REVIEW", "HIERARCHY_REPAIR"]
    assert "parent_traits" not in row["replacement_fields"]
    assert "parent_traits" in row["remove_fields"]
    assert row["proposed_record_sha256"] is None


def test_trailing_legacy_emitter_whitespace_is_the_only_ignored_difference(source):
    legacy = source[-1]
    legacy["definition"] += " "
    legacy["definitions"][0]["text"] += " "
    assert _plan(source, legacy)["record_state"] == "EXACT_LEGACY"

    legacy["label"] += " "
    assert _plan(source, legacy)["record_state"] == "REVIEW_ONLY"


def test_semantic_comparison_is_type_strict_and_distinguishes_missing_from_null(source):
    legacy = source[-1]
    initial = _plan(source, legacy)
    proposed = migration.apply_replacements(
        legacy, initial["replacement_fields"], initial["remove_fields"]
    )
    proposed["sequence_fingerprint_representations"][0]["motifs"][0]["ordinal"] = True
    row = _plan(source, proposed)
    assert row["record_state"] == "REVIEW_ONLY"
    assert "sequence_fingerprint_representations" in row["legacy_mismatch_fields"]
    assert migration._differing_fields({"field": None}, {}) == ["field"]


def test_build_plan_requires_exact_sets_and_is_byte_deterministic(source):
    release, signature, entry, _fingerprint, legacy = source
    records = {
        "PRINTS:PR00001": (
            REPO / "data/traits/sequence/family/prints/test-pr00001.yaml",
            legacy,
            "b" * 64,
        )
    }
    kwargs = {
        "records": records,
        "signatures": [signature],
        "entries": {"IPR000001": entry},
        "interpro_types": {"IPR000001": "family"},
        "release": release,
        "normalized_hierarchy_rows": [
            {
                "accession": "PR00001",
                "code": "TESTPRINT",
                "domain_flag": False,
                "evalue_cutoff": "1e-04",
                "hierarchical_relations": [],
                "minimum_motif_count": 0,
            }
        ],
        "legacy_generated_parents": {},
        "manifest_id": "prints-snapshot:" + "c" * 64,
    }
    rows_a, summary_a = migration.build_plan(**kwargs)
    rows_b, summary_b = migration.build_plan(**kwargs)
    assert migration.canonical_json(rows_a) == migration.canonical_json(rows_b)
    assert summary_a == summary_b
    assert summary_a["normalized_hierarchy_row_count"] == 1
    assert summary_a["normalized_hierarchy_domain_count"] == 0
    assert summary_a["member_hierarchy_domain_alignment_counts"] == {"AGREES": 1}
    assert summary_a["routing_review_member_hierarchy_domain_alignment_counts"] == {}
    assert (
        summary_a["rows_sha256"]
        == hashlib.sha256((migration.canonical_json(rows_a[0]) + "\n").encode()).hexdigest()
    )

    with pytest.raises(migration.PrintsMigrationError, match="identifier sets differ"):
        migration.build_plan(**{**kwargs, "records": {}})
    with pytest.raises(migration.PrintsMigrationError, match="duplicate source signature"):
        migration.build_plan(**{**kwargs, "signatures": [signature, signature]})
    with pytest.raises(migration.PrintsMigrationError, match="normalized hierarchy identifier"):
        migration.build_plan(**{**kwargs, "normalized_hierarchy_rows": []})


def test_record_index_rejects_duplicates(tmp_path):
    for name in ("one.yaml", "two.yaml"):
        (tmp_path / name).write_text(
            "identifier: PRINTS:PR00001\nlabel: duplicate\n", encoding="utf-8"
        )
    with pytest.raises(migration.PrintsMigrationError, match="duplicate PRINTS identifier"):
        migration.index_prints_records(tmp_path)


def test_record_index_rejects_duplicate_yaml_keys_before_namespace_filter(tmp_path):
    (tmp_path / "shadow.yaml").write_text(
        "identifier: PRINTS:PR00001\nlabel: first\nlabel: ambiguous\n",
        encoding="utf-8",
    )
    with pytest.raises(migration.PrintsMigrationError, match="duplicate YAML key"):
        migration.index_prints_records(tmp_path)


def test_record_index_rejects_escaped_flow_shadow_before_filter(tmp_path):
    (tmp_path / "legitimate.yaml").write_text(
        "identifier: PRINTS:PR00001\nlabel: legitimate\n", encoding="utf-8"
    )
    (tmp_path / "shadow.yaml").write_text(
        '{"identi\\u0066ier":"\\u0050\\u0052\\u0049\\u004e\\u0054\\u0053'
        '\\u003a\\u0050\\u0052\\u0030\\u0030\\u0030\\u0030\\u0031",'
        '"label":"shadow"}\n',
        encoding="utf-8",
    )
    with pytest.raises(migration.PrintsMigrationError, match="duplicate PRINTS identifier"):
        migration.index_prints_records(tmp_path)


@pytest.mark.parametrize(
    "shadow",
    [
        '# comment\n---\n"identifier": PRINTS:PR00001\nlabel: shadow\n',
        "identifier: !!str PRINTS:PR00001\nlabel: shadow\n",
        "identifier: >-\n  PRINTS:PR00001\nlabel: shadow\n",
        "identifier: PRINTS:PR00001 # inline comment\nlabel: shadow\n",
    ],
)
def test_record_index_rejects_noncanonical_but_valid_yaml_shadows(tmp_path, shadow):
    (tmp_path / "legitimate.yaml").write_text(
        "identifier: PRINTS:PR00001\nlabel: legitimate\n", encoding="utf-8"
    )
    (tmp_path / "shadow.yaml").write_text(shadow, encoding="utf-8")
    with pytest.raises(migration.PrintsMigrationError, match="duplicate PRINTS identifier"):
        migration.index_prints_records(tmp_path)


@pytest.mark.parametrize("suffix", [".yml", ".YML", ".YAML", ".yMl"])
def test_record_index_rejects_prints_shadows_with_noncanonical_suffix(tmp_path, suffix):
    shadow = tmp_path / f"shadow{suffix}"
    shadow.write_text("identifier: PRINTS:PR00001\nlabel: shadow\n", encoding="utf-8")

    with pytest.raises(migration.PrintsMigrationError, match="exact lowercase .yaml suffix"):
        migration.index_prints_records(tmp_path)


@pytest.mark.parametrize("namespace", ["prints", "Prints", "PrInTs"])
def test_record_index_rejects_mixed_case_prints_namespace(tmp_path, namespace):
    (tmp_path / "shadow.yaml").write_text(
        f"identifier: {namespace}:PR00001\nlabel: shadow\n",
        encoding="utf-8",
    )

    with pytest.raises(migration.PrintsMigrationError, match="noncanonical PRINTS namespace"):
        migration.index_prints_records(tmp_path)


def test_ripgrep_config_cannot_hide_a_prints_semantic_shadow(tmp_path, monkeypatch):
    hostile_config = tmp_path / "hostile-ripgreprc"
    hostile_config.write_text("--max-filesize=1\n", encoding="utf-8")
    monkeypatch.setenv("RIPGREP_CONFIG_PATH", str(hostile_config))
    for name in ("legitimate.yaml", "shadow.yaml"):
        (tmp_path / name).write_text(
            "identifier: PRINTS:PR00001\nlabel: duplicate\n",
            encoding="utf-8",
        )

    with pytest.raises(migration.PrintsMigrationError, match="duplicate PRINTS identifier"):
        migration.index_prints_records(tmp_path)


def test_record_index_refuses_utf16_shadow(tmp_path):
    (tmp_path / "legitimate.yaml").write_text(
        "identifier: PRINTS:PR00001\nlabel: legitimate\n", encoding="utf-8"
    )
    (tmp_path / "shadow.yaml").write_text(
        "identifier: PRINTS:PR00001\nlabel: shadow\n", encoding="utf-16"
    )
    with pytest.raises(migration.PrintsMigrationError, match="cannot load trait record"):
        migration.index_prints_records(tmp_path)


@pytest.mark.parametrize(
    "extra_yaml",
    [
        "updated: 2026-08-24\n",
        "members: !!set {one: null}\n",
        "1: non-string-key\n",
    ],
)
def test_record_index_refuses_safe_loader_values_outside_json_shape(tmp_path, extra_yaml):
    (tmp_path / "record.yaml").write_text(
        "identifier: PRINTS:PR00001\n" + extra_yaml,
        encoding="utf-8",
    )
    with pytest.raises(migration.PrintsMigrationError, match="not JSON-shaped"):
        migration.index_prints_records(tmp_path)


def test_record_index_refuses_yaml_alias_cycle(tmp_path):
    (tmp_path / "record.yaml").write_text(
        "identifier: PRINTS:PR00001\ncycle: &self [*self]\n",
        encoding="utf-8",
    )
    with pytest.raises(migration.PrintsMigrationError, match="YAML alias cycle"):
        migration.index_prints_records(tmp_path)


def test_record_index_refuses_candidate_set_drift(tmp_path, monkeypatch):
    path = tmp_path / "record.yaml"
    path.write_text("identifier: PRINTS:PR00001\nlabel: fixture\n", encoding="utf-8")
    calls = iter([[path], []])
    monkeypatch.setattr(migration, "_candidate_prints_paths", lambda _traits: next(calls))
    with pytest.raises(migration.PrintsMigrationError, match="candidate set changed"):
        migration.index_prints_records(tmp_path)


def test_record_index_refuses_nonprints_candidate_that_mutates_in_place(tmp_path, monkeypatch):
    path = tmp_path / "record.yaml"
    path.write_text(
        "identifier: OTHER:00001\nnote: PRINTS prefilter candidate\n",
        encoding="utf-8",
    )
    calls = 0

    def candidate_paths(_traits):
        nonlocal calls
        calls += 1
        if calls == 2:
            path.write_text("identifier: PRINTS:PR00001\nlabel: late shadow\n", encoding="utf-8")
        return [path]

    monkeypatch.setattr(migration, "_candidate_prints_paths", candidate_paths)
    with pytest.raises(migration.PrintsMigrationError, match="trait candidate changed"):
        migration.index_prints_records(tmp_path)


def test_record_index_refuses_external_directory_symlink_before_read(tmp_path, monkeypatch):
    traits = tmp_path / "traits"
    traits.mkdir()
    (traits / "legitimate.yaml").write_text(
        "identifier: PRINTS:PR00001\nlabel: legitimate\n", encoding="utf-8"
    )
    external = tmp_path / "external"
    external.mkdir()
    external_record = external / "other.yaml"
    external_record.write_text(
        "identifier: OTHER:00001\nnote: PRINTS prefilter candidate\n", encoding="utf-8"
    )
    (traits / "external-link").symlink_to(external, target_is_directory=True)

    original_read_bytes = pathlib.Path.read_bytes

    def guarded_read_bytes(path):
        if path == external_record:
            pytest.fail("external candidate was read before symlink rejection")
        return original_read_bytes(path)

    monkeypatch.setattr(pathlib.Path, "read_bytes", guarded_read_bytes)
    with pytest.raises(migration.PrintsMigrationError, match="symlink below trait directory"):
        migration.index_prints_records(traits)


def test_record_index_refuses_outside_candidate_before_read(tmp_path, monkeypatch):
    traits = tmp_path / "traits"
    traits.mkdir()
    outside = tmp_path / "outside.yaml"
    outside.write_text(
        "identifier: OTHER:00001\nnote: PRINTS prefilter candidate\n", encoding="utf-8"
    )
    monkeypatch.setattr(migration, "_candidate_prints_paths", lambda _traits: [outside])

    original_read_bytes = pathlib.Path.read_bytes

    def guarded_read_bytes(path):
        if path == outside:
            pytest.fail("outside candidate was read before containment rejection")
        return original_read_bytes(path)

    monkeypatch.setattr(pathlib.Path, "read_bytes", guarded_read_bytes)
    with pytest.raises(migration.PrintsMigrationError, match="escapes trait directory before read"):
        migration.index_prints_records(traits)


def test_record_index_no_follow_open_blocks_swap_to_external_symlink(tmp_path, monkeypatch):
    traits = tmp_path / "traits"
    traits.mkdir()
    candidate = traits / "record.yaml"
    candidate.write_text(
        "identifier: OTHER:00001\nnote: PRINTS prefilter candidate\n", encoding="utf-8"
    )
    external = tmp_path / "external.yaml"
    external.write_text("identifier: PRINTS:PR00001\nlabel: external\n", encoding="utf-8")
    monkeypatch.setattr(migration, "_candidate_prints_paths", lambda _traits: [candidate])

    original_open = migration.os.open
    original_supports_dir_fd = set(migration.os.supports_dir_fd)
    swapped = False

    def swapping_open(path, flags, mode=0o777, *, dir_fd=None):
        nonlocal swapped
        if path == candidate.name and dir_fd is not None and not swapped:
            swapped = True
            candidate.unlink()
            candidate.symlink_to(external)
        return original_open(path, flags, mode, dir_fd=dir_fd)

    monkeypatch.setattr(migration.os, "open", swapping_open)
    monkeypatch.setattr(
        migration.os,
        "supports_dir_fd",
        original_supports_dir_fd | {swapping_open},
    )
    monkeypatch.setattr(
        migration.os,
        "read",
        lambda *_args, **_kwargs: pytest.fail("external bytes were read after symlink swap"),
    )
    with pytest.raises(migration.PrintsMigrationError, match="without following symlinks"):
        migration.index_prints_records(traits)
    assert swapped


def test_record_index_fails_if_descriptor_safety_is_unavailable(tmp_path, monkeypatch):
    monkeypatch.setattr(migration.os, "supports_dir_fd", set())
    with pytest.raises(migration.PrintsMigrationError, match="platform lacks required"):
        migration.index_prints_records(tmp_path)


def test_wrong_route_is_not_ready_and_outside_repo_is_refused(source, tmp_path):
    legacy = source[-1]
    wrong_path = REPO / "data/traits/sequence/domain/prints/test-pr00001.yaml"
    row = _plan(source, legacy, path=wrong_path)
    assert row["path_status"] == "WRONG_MEMBER_ROUTE"
    assert row["classification"] == "PATH_REVIEW_REQUIRED"

    with pytest.raises(migration.PrintsMigrationError, match="escapes repository root"):
        _plan(source, legacy, path=tmp_path / "outside.yaml")


def test_symlinked_expected_route_is_review_only(source, tmp_path):
    legacy = source[-1]
    target = tmp_path / "outside-route"
    target.mkdir()
    route_parent = tmp_path / "data/traits/sequence/family"
    route_parent.mkdir(parents=True)
    (route_parent / "prints").symlink_to(target, target_is_directory=True)
    path = route_parent / "prints/test-pr00001.yaml"

    row = _plan(source, legacy, path=path, repo_root=tmp_path)

    assert row["record_path"] == "data/traits/sequence/family/prints/test-pr00001.yaml"
    assert row["expected_record_directory"] == "data/traits/sequence/family/prints"
    assert row["path_status"] == "WRONG_MEMBER_ROUTE"
    assert row["classification"] == "PATH_REVIEW_REQUIRED"


def test_symlink_loop_in_record_route_is_review_only(source, tmp_path):
    route_parent = tmp_path / "data/traits/sequence/family"
    route_parent.mkdir(parents=True)
    (route_parent / "prints").symlink_to("prints", target_is_directory=True)

    row = _plan(
        source,
        source[-1],
        path=route_parent / "prints/test-pr00001.yaml",
        repo_root=tmp_path,
    )

    assert row["path_status"] == "WRONG_MEMBER_ROUTE"
    assert row["classification"] == "PATH_REVIEW_REQUIRED"


def test_unproven_prints_parent_is_preserved_for_review(source):
    record = dict(source[-1])
    record["parent_traits"] = ["PRINTS:PR99999"]
    row = _plan(source, record, legacy_generated_parent="PR00002")
    assert row["record_state"] == "REVIEW_ONLY"
    assert row["hierarchy_status"] == "UNSUPPORTED_PRINTS_PARENT_REVIEW"
    assert row["review_requirements"] == ["RECORD_REVIEW", "HIERARCHY_REVIEW"]
    assert row["classification"] == "RECORD_REVIEW_AND_HIERARCHY_REVIEW_REQUIRED"
    assert "parent_traits" not in row["remove_fields"]


def test_record_drift_does_not_mask_parent_or_path_review(source):
    record = dict(source[-1])
    record["label"] = "manual drift"
    record["parent_traits"] = ["PRINTS:PR00002"]
    wrong_path = REPO / "data/traits/sequence/domain/prints/test-pr00001.yaml"
    row = _plan(
        source,
        record,
        path=wrong_path,
        legacy_generated_parent="PR00002",
    )
    assert row["review_requirements"] == [
        "RECORD_REVIEW",
        "HIERARCHY_REPAIR",
        "PATH_REVIEW",
    ]
    assert row["classification"] == ("RECORD_REVIEW_AND_HIERARCHY_REPAIR_AND_PATH_REVIEW_REQUIRED")


def test_source_capture_is_bounded_and_byte_exact(tmp_path):
    source_path = tmp_path / "source.bin"
    source_path.write_bytes(b"bound source bytes")

    assert (
        migration._capture_regular_source(
            source_path,
            label="fixture source",
            max_bytes=1024,
        )
        == b"bound source bytes"
    )

    with pytest.raises(migration.PrintsMigrationError, match="outside 1..4 bytes"):
        migration._capture_regular_source(
            source_path,
            label="fixture source",
            max_bytes=4,
        )


def test_source_capture_refuses_file_and_component_symlinks(tmp_path):
    external = tmp_path / "external.bin"
    external.write_bytes(b"external")
    file_link = tmp_path / "file-link.bin"
    file_link.symlink_to(external)

    with pytest.raises(migration.PrintsMigrationError, match="cannot safely open regular file"):
        migration._capture_regular_source(
            file_link,
            label="fixture source",
            max_bytes=1024,
        )

    external_directory = tmp_path / "external-directory"
    external_directory.mkdir()
    (external_directory / "source.bin").write_bytes(b"external")
    directory_link = tmp_path / "directory-link"
    directory_link.symlink_to(external_directory, target_is_directory=True)
    with pytest.raises(migration.PrintsMigrationError, match="directory component"):
        migration._capture_regular_source(
            directory_link / "source.bin",
            label="fixture source",
            max_bytes=1024,
        )


def test_source_capture_refuses_fifo_without_blocking(tmp_path):
    fifo = tmp_path / "source.fifo"
    migration.os.mkfifo(fifo)

    with pytest.raises(migration.PrintsMigrationError, match="not a regular file"):
        migration._capture_regular_source(
            fifo,
            label="fixture source",
            max_bytes=1024,
        )


def test_source_capture_refuses_path_swap_after_open(tmp_path, monkeypatch):
    source_path = tmp_path / "source.bin"
    source_path.write_bytes(b"captured source")
    replacement = tmp_path / "replacement.bin"
    replacement.write_bytes(b"replacement source")
    original_read = migration.os.read
    swapped = False

    def swapping_read(descriptor, count):
        nonlocal swapped
        chunk = original_read(descriptor, count)
        if not swapped:
            swapped = True
            source_path.rename(tmp_path / "opened-source.bin")
            replacement.rename(source_path)
        return chunk

    monkeypatch.setattr(migration.os, "read", swapping_read)
    with pytest.raises(migration.PrintsMigrationError, match="changed during capture"):
        migration._capture_regular_source(
            source_path,
            label="fixture source",
            max_bytes=1024,
        )
    assert swapped


def test_apply_refuses_before_reading_any_source(monkeypatch, capsys):
    monkeypatch.setattr(
        migration,
        "load_verified_prints_snapshot",
        lambda *_args, **_kwargs: pytest.fail("source read before --apply refusal"),
    )
    assert migration.main(["--apply"]) == 2
    assert "refusing --apply" in capsys.readouterr().err


def test_missing_snapshot_fails_closed(tmp_path, capsys):
    assert migration.main(["--manifest", str(tmp_path / "missing.json")]) == 2
    assert "missing PRINTS snapshot manifest" in capsys.readouterr().err


@pytest.mark.parametrize("mutated_source", ["api", "hierarchy", "interpro"])
def test_main_consumes_verified_snapshot_after_captured_path_mutation(
    tmp_path,
    monkeypatch,
    capsys,
    mutated_source,
):
    """A post-verification temp-path mutation cannot alter planned source state."""

    source_paths = {}
    for name in (
        "manifest",
        "api",
        "kdat",
        "hierarchy",
        "interpro",
        "legacy_hierarchy_source",
    ):
        path = tmp_path / name
        path.write_bytes(f"placeholder {name}".encode())
        source_paths[name] = path
    traits = tmp_path / "traits"
    traits.mkdir()

    release = object()
    signatures = [{"accession": "PR00001"}]
    hierarchy_rows = [{"accession": "PR00001", "domain_flag": False}]
    interpro_bytes = gzip.compress(b'<interpro id="IPR000001" type="Family">\n')
    entries = {"IPR000001": {"name": "captured"}}
    manifest_id = "prints-snapshot:" + "a" * 64

    class VerifiedFixture:
        kdat_release = release
        interpro_xml_bytes = interpro_bytes

        @property
        def manifest_id(self):
            return manifest_id

        def load_api_rows(self):
            return signatures

        def load_hierarchy_rows(self):
            return hierarchy_rows

    captured_path_was_mutated = False

    def verified_then_mutated(_manifest_path, **kwargs):
        nonlocal captured_path_was_mutated
        capture_argument = (
            "interpro_xml_path" if mutated_source == "interpro" else f"{mutated_source}_path"
        )
        kwargs[capture_argument].write_bytes(b"invalid bytes installed after verification")
        captured_path_was_mutated = True
        return VerifiedFixture()

    def captured_interpro_entries(path=None, *, captured_gzip=None):
        assert path is None
        assert captured_gzip == interpro_bytes
        return entries

    def checked_build_plan(**kwargs):
        assert kwargs["release"] is release
        assert kwargs["signatures"] is signatures
        assert kwargs["normalized_hierarchy_rows"] is hierarchy_rows
        assert kwargs["entries"] is entries
        assert kwargs["interpro_types"] == {"IPR000001": "family"}
        assert kwargs["manifest_id"] == manifest_id
        return [], {"kind": migration.SUMMARY_KIND, "status": "CAPTURE_BOUND"}

    monkeypatch.setattr(migration, "load_verified_prints_snapshot", verified_then_mutated)
    monkeypatch.setattr(migration.seeder, "interpro_entries", captured_interpro_entries)
    monkeypatch.setattr(migration, "load_legacy_generated_parents", lambda _path: {})
    monkeypatch.setattr(migration, "index_prints_records", lambda _traits: {})
    monkeypatch.setattr(migration, "build_plan", checked_build_plan)

    assert (
        migration.main(
            [
                "--manifest",
                str(source_paths["manifest"]),
                "--api",
                str(source_paths["api"]),
                "--kdat",
                str(source_paths["kdat"]),
                "--hierarchy",
                str(source_paths["hierarchy"]),
                "--interpro",
                str(source_paths["interpro"]),
                "--legacy-hierarchy-source",
                str(source_paths["legacy_hierarchy_source"]),
                "--traits",
                str(traits),
                "--summary-only",
            ]
        )
        == 0
    )
    assert captured_path_was_mutated
    assert json.loads(capsys.readouterr().out) == {
        "kind": migration.SUMMARY_KIND,
        "status": "CAPTURE_BOUND",
    }


@pytest.mark.skipif(
    not migration.DEFAULT_HIERARCHY.is_file() or not migration.DEFAULT_HIERARCHY_SOURCE.is_file(),
    reason="ignored pinned PRINTS production snapshot is absent",
)
def test_pinned_production_hierarchy_repair_partition_is_exact():
    hierarchy = load_hierarchy_jsonl(migration.DEFAULT_HIERARCHY)
    assert len(hierarchy) == 2106
    assert sum(row["domain_flag"] for row in hierarchy) == 97
    assert sum(row["minimum_motif_count"] != 0 for row in hierarchy) == 31
    assert sum(bool(row["hierarchical_relations"]) for row in hierarchy) == 1026
    assert sum(len(row["hierarchical_relations"]) for row in hierarchy) == 2546

    historical = migration.load_legacy_generated_parents(migration.DEFAULT_HIERARCHY_SOURCE)
    records = migration.index_prints_records(migration.DEFAULT_TRAITS)
    current: dict[str, str] = {}
    for identifier, (_path, record, _sha) in records.items():
        parents = record.get("parent_traits")
        if parents is None:
            continue
        assert isinstance(parents, list) and len(parents) == 1
        current[identifier.split(":", 1)[1]] = parents[0].split(":", 1)[1]

    assert len(records) == 2106
    assert len(historical) == 1026
    assert current == historical
    reciprocal_pairs = {
        tuple(sorted((child, parent)))
        for child, parent in current.items()
        if current.get(parent) == child
    }
    assert len(reciprocal_pairs) == 233
    assert all(
        migration._hierarchy_projection(record, historical.get(identifier.split(":", 1)[1]))[0]
        == (
            "CONFIRMED_LEGACY_GENERATED_PARENT"
            if identifier.split(":", 1)[1] in historical
            else "NONE"
        )
        for identifier, (_path, record, _sha) in records.items()
    )


@pytest.mark.skipif(
    not all(
        path.is_file()
        for path in (
            migration.DEFAULT_API,
            migration.DEFAULT_KDAT,
            migration.DEFAULT_HIERARCHY,
            migration.DEFAULT_HIERARCHY_SOURCE,
            migration.DEFAULT_MANIFEST,
            migration.DEFAULT_INTERPRO,
        )
    ),
    reason="ignored pinned PRINTS production snapshot is absent",
)
def test_pinned_production_full_plan_matches_golden_source_replay(capsys):
    assert migration.main([]) == 0
    stdout = capsys.readouterr().out
    payloads = [json.loads(line) for line in stdout.splitlines()]
    rows, summary = payloads[:-1], payloads[-1]

    assert len(rows) == 2106
    assert summary["record_count"] == 2106
    assert summary["record_state_counts"] == {"EXACT_LEGACY": 2103, "REVIEW_ONLY": 3}
    assert summary["classification_counts"] == {
        "CONTENT_MIGRATION_READY": 989,
        "HIERARCHY_REPAIR_REQUIRED": 1005,
        "RECORD_REVIEW_AND_HIERARCHY_REPAIR_REQUIRED": 1,
        "RECORD_REVIEW_ONLY": 2,
        "ROUTING_AND_HIERARCHY_REPAIR_REQUIRED": 20,
        "ROUTING_REVIEW_REQUIRED": 89,
    }
    assert summary["route_status_counts"] == {
        "AGREES": 1828,
        "ROUTING_REVIEW": 109,
        "UNINTEGRATED": 169,
    }
    assert summary["normalized_hierarchy_row_count"] == 2106
    assert summary["normalized_hierarchy_domain_count"] == 97
    assert summary["normalized_hierarchy_projection_sha256"] == (
        "fa21deb29c23f39f01acd8f85fd4319ef40af7700a5e221d6fd80b4b6343d665"
    )
    assert summary["member_hierarchy_domain_alignment_counts"] == {
        "AGREES": 2087,
        "DISAGREES": 19,
    }
    assert summary["routing_review_member_hierarchy_domain_alignment_counts"] == {
        "AGREES": 102,
        "DISAGREES": 7,
    }
    assert summary["path_status_counts"] == {"EXPECTED_MEMBER_ROUTE": 2106}
    assert summary["rows_sha256"] == (
        "b36ad35933fa3408fb6cc4c0eacf26eef1bafafe7140da259a889365a4d66d49"
    )
    assert summary["plan_id"] == (
        "prints-migration-plan:fcce6d6d5ecb5443ca1eb659e35bfce5a424a9e621662b15b5a3febc9b8e6fbf"
    )
    assert hashlib.sha256(stdout.encode("utf-8")).hexdigest() == (
        "011a373efd2e2d901b42ca02c15e0114ad778a625cf7a577bc993f91bc470308"
    )
    assert {
        row["identifier"]
        for row in rows
        if row["route_status"] == "ROUTING_REVIEW"
        and row["member_hierarchy_domain_alignment"] == "DISAGREES"
    } == {
        "PRINTS:PR00163",
        "PRINTS:PR00205",
        "PRINTS:PR00379",
        "PRINTS:PR00929",
        "PRINTS:PR01021",
        "PRINTS:PR01452",
        "PRINTS:PR01542",
    }

    release = parse_prints_kdat(migration.DEFAULT_KDAT, prints_kdat.PRINTS_42_0_SHA256)
    for row in rows:
        accession = row["identifier"].split(":", 1)[1]
        expected = build_fingerprint_representation(
            release,
            release.fingerprints[accession],
        )
        assert row["replacement_fields"]["sequence_fingerprint_representations"] == [expected]
        assert row["normalized_hierarchy_row_sha256"] == migration.value_sha256(
            row["normalized_hierarchy_row"]
        )
        assert set(row["record_review_value_projections"]) == set(row["legacy_mismatch_fields"])
        assert row["record_review_value_projections_sha256"] == migration.value_sha256(
            row["record_review_value_projections"]
        )
        assert row["proposed_record_sha256"] is None
        row_sha256 = row.pop("row_sha256")
        assert row_sha256 == migration.value_sha256(row)


def test_symlink_loop_classification_survives_a_resolve_that_raises(source, tmp_path, monkeypatch):
    """Pins #611 on an interpreter that does not exhibit the bug.

    Non-strict `Path.resolve()` disagrees across supported versions on a symlink
    loop: 3.13 returns the path unchanged, 3.12 raises RuntimeError. The test
    above therefore passes on 3.13 whether or not the planner depends on that,
    and it was CI on 3.12 that showed the whole plan aborting for one bad record.

    Making `Path.resolve` raise for the looping path reproduces 3.12's behaviour
    here. The planner must still classify, which it can only do by not going
    through `resolve()` for this.
    """
    route_parent = tmp_path / "data/traits/sequence/family"
    route_parent.mkdir(parents=True)
    (route_parent / "prints").symlink_to("prints", target_is_directory=True)

    original = pathlib.Path.resolve

    def resolve_like_python_312(self, *args, **kwargs):
        if "prints" in self.parts and str(self).startswith(str(tmp_path)):
            raise RuntimeError(f"Symlink loop from {str(self)!r}")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, "resolve", resolve_like_python_312)

    row = _plan(
        source,
        source[-1],
        path=route_parent / "prints/test-pr00001.yaml",
        repo_root=tmp_path,
    )
    assert row["path_status"] == "WRONG_MEMBER_ROUTE"
    assert row["classification"] == "PATH_REVIEW_REQUIRED"
