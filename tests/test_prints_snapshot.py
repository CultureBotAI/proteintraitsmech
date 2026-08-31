"""Content-address and replay gates for the four-file PRINTS raw snapshot."""

from __future__ import annotations

import gzip
import hashlib
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import fetch_interpro_members as fetch  # noqa: E402
import prints_snapshot as snapshot  # noqa: E402


KDAT = (
    b"gc; TESTPRINT\n"
    b"gx; PR00001\n"
    b"gn; COMPOUND(2)\n"
    b"gt; Test fingerprint\n"
    b"gd; Source-native description.\n"
    b"fm; FINAL MOTIF-SETS\n"
    b"fm; ----------------\n"
    b"fc; TEST1\n"
    b"fl; 3\n"
    b"ft; Test motif I\n"
    b"fd; ACD PROTEIN 1 1\n"
    b"fc; TEST2\n"
    b"fl; 3\n"
    b"ft; Test motif II\n"
    b"fd; EFG PROTEIN 5 1\n"
)
HIERARCHY_RAW = b"# Last update 21-02-2012\nTESTPRINT|PR00001|1e-04|0|*\n"
API_ROWS = [
    {
        "accession": "PR00001",
        "name": "TESTPRINT",
        "type": "family",
        "integrated": "IPR000001",
        "source_database": "prints",
    }
]
XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<interprodb>
<release>
  <dbinfo version="42.0" dbname="PRINTS" entry_count="1" file_date="14-JUN-12"/>
  <dbinfo version="109.0" dbname="INTERPRO" entry_count="1" file_date="11-JUN-26"/>
</release>
<interpro id="IPR000001" protein_count="1" short_name="Test" type="Family">
  <member_list>
    <db_xref protein_count="1" db="PRINTS" dbkey="PR00001" name="TESTPRINT"/>
  </member_list>
</interpro>
</interprodb>
"""


def _fixture(tmp_path: pathlib.Path, monkeypatch):
    tmp_path.mkdir(parents=True, exist_ok=True)
    api = tmp_path / "prints.jsonl"
    kdat = tmp_path / "prints42_0.kdat"
    hierarchy = tmp_path / snapshot.HIERARCHY_NAME
    xml = tmp_path / "interpro.xml.gz"
    manifest_path = tmp_path / snapshot.MANIFEST_NAME

    api.write_bytes(fetch._api_jsonl(API_ROWS))
    kdat.write_bytes(KDAT)
    hierarchy.write_bytes(
        snapshot.dump_hierarchy_jsonl(snapshot.parse_hierarchy_source(HIERARCHY_RAW))
    )
    with gzip.open(xml, "wb") as handle:
        handle.write(XML)
    monkeypatch.setattr(snapshot, "PRINTS_42_0_SHA256", hashlib.sha256(KDAT).hexdigest())
    paths = {
        "api_path": api,
        "kdat_path": kdat,
        "hierarchy_path": hierarchy,
        "interpro_xml_path": xml,
    }
    manifest = snapshot.build_prints_manifest(**paths)
    manifest_path.write_bytes(snapshot.dump_manifest(manifest))
    return manifest_path, paths, manifest


def test_manifest_carries_hashes_counts_releases_and_exact_integration_replay(
    tmp_path, monkeypatch
):
    manifest_path, paths, manifest = _fixture(tmp_path, monkeypatch)
    assert (
        snapshot.verify_prints_manifest(
            manifest_path, expected_manifest_id=manifest["manifest_id"], **paths
        )
        == manifest
    )
    assert manifest["manifest_id"].startswith("prints-snapshot:")
    assert set(manifest["artifacts"]) == {
        "prints_api",
        "prints_kdat",
        "prints_hierarchy",
        "interpro_xml",
    }
    for artifact in manifest["artifacts"].values():
        assert len(artifact["sha256"]) == 64
        assert artifact["bytes"] > 0

    release = manifest["release_evidence"]
    assert release["prints_release"] == "42.0"
    assert release["interpro_release"] == "109.0"
    assert release["api_declared_release"] is None
    assert release["api_release_status"] == "NOT_DECLARED_IN_CAPTURED_API_PAYLOAD"
    assert (
        release["api_consistency_inference"]["status"]
        == "INFERRED_FROM_CONTENT_EQUALITY_NOT_API_RELEASE_METADATA"
    )
    integrations = manifest["replay_evidence"]["integrations"]
    assert integrations["api_integrated_count"] == 1
    assert integrations["api_unintegrated_count"] == 0
    assert integrations["exact_mapping_match_count"] == 1
    assert integrations["mismatch_count"] == 0
    assert integrations["api_projection_sha256"] == integrations["xml_projection_sha256"]


def test_hierarchy_columns_preserve_postprocessing_semantics_without_parent_inference():
    raw = (
        b"DOMAIN|PR00001|1e-04|3|*\n"
        b"SIBLINGA|PR00002|1e-07|0|SIBLINGB\n"
        b"SIBLINGB|PR00003|1e-07|0|SIBLINGA\n"
    )
    rows = snapshot.parse_hierarchy_source(raw)

    assert rows == [
        {
            "accession": "PR00001",
            "code": "DOMAIN",
            "domain_flag": True,
            "evalue_cutoff": "1e-04",
            "hierarchical_relations": [],
            "minimum_motif_count": 3,
        },
        {
            "accession": "PR00002",
            "code": "SIBLINGA",
            "domain_flag": False,
            "evalue_cutoff": "1e-07",
            "hierarchical_relations": ["SIBLINGB"],
            "minimum_motif_count": 0,
        },
        {
            "accession": "PR00003",
            "code": "SIBLINGB",
            "domain_flag": False,
            "evalue_cutoff": "1e-07",
            "hierarchical_relations": ["SIBLINGA"],
            "minimum_motif_count": 0,
        },
    ]


@pytest.mark.parametrize("cutoff", ["", "banana", "NaN", "Infinity", "-1e-4"])
def test_hierarchy_rejects_nonfinite_or_negative_evalue_cutoffs(cutoff):
    raw = f"TESTPRINT|PR00001|{cutoff}|0|*\n".encode()
    with pytest.raises(snapshot.PrintsSnapshotError, match="e-value"):
        snapshot.parse_hierarchy_source(raw)


def test_normalized_hierarchy_rejects_domain_flag_with_relations():
    row = {
        "accession": "PR00001",
        "code": "TESTPRINT",
        "domain_flag": True,
        "evalue_cutoff": "1e-4",
        "hierarchical_relations": ["TESTPRINT"],
        "minimum_motif_count": 0,
    }
    with pytest.raises(snapshot.PrintsSnapshotError, match="domain flag"):
        snapshot.dump_hierarchy_jsonl([row])


@pytest.mark.parametrize("minimum_motif_count", [False, True])
def test_normalized_hierarchy_rejects_boolean_minimum_motif_count(minimum_motif_count):
    row = {
        "accession": "PR00001",
        "code": "TESTPRINT",
        "domain_flag": False,
        "evalue_cutoff": "1e-4",
        "hierarchical_relations": [],
        "minimum_motif_count": minimum_motif_count,
    }
    with pytest.raises(snapshot.PrintsSnapshotError, match="minimum motif count"):
        snapshot.dump_hierarchy_jsonl([row])


@pytest.mark.parametrize(
    "artifact", ["api_path", "kdat_path", "hierarchy_path", "interpro_xml_path"]
)
def test_verifier_rejects_any_changed_artifact(tmp_path, monkeypatch, artifact):
    manifest_path, paths, manifest = _fixture(tmp_path, monkeypatch)
    paths[artifact].write_bytes(paths[artifact].read_bytes() + b"\n")
    with pytest.raises(snapshot.PrintsSnapshotError):
        snapshot.verify_prints_manifest(
            manifest_path, expected_manifest_id=manifest["manifest_id"], **paths
        )


@pytest.mark.parametrize(
    ("artifact", "manifest_key"),
    [
        ("api_path", "prints_api"),
        ("hierarchy_path", "prints_hierarchy"),
        ("interpro_xml_path", "interpro_xml"),
    ],
)
def test_manifest_parse_hash_and_size_share_one_immutable_capture(
    tmp_path, monkeypatch, artifact, manifest_key
):
    _, paths, _ = _fixture(tmp_path, monkeypatch)
    target = paths[artifact]
    original_bytes = target.read_bytes()
    if artifact == "api_path":
        replacement = original_bytes.replace(b"TESTPRINT", b"OTHERNAME")
    elif artifact == "hierarchy_path":
        replacement = original_bytes.replace(b"1e-04", b"1e-05")
    else:
        replacement = gzip.compress(XML.replace(b"14-JUN-12", b"15-JUN-12"), mtime=0)
    assert replacement != original_bytes

    original_capture = snapshot._capture_artifact
    swapped = False

    def capture_then_swap(path, label):
        nonlocal swapped
        capture = original_capture(path, label)
        if path == target and not swapped:
            target.write_bytes(replacement)
            swapped = True
        return capture

    monkeypatch.setattr(snapshot, "_capture_artifact", capture_then_swap)
    manifest = snapshot.build_prints_manifest(**paths)
    artifact_receipt = manifest["artifacts"][manifest_key]

    assert swapped is True
    assert target.read_bytes() == replacement
    assert artifact_receipt["sha256"] == hashlib.sha256(original_bytes).hexdigest()
    assert artifact_receipt["bytes"] == len(original_bytes)
    if artifact == "interpro_xml_path":
        assert manifest["release_evidence"]["prints_file_date"] == "14-JUN-12"


def test_manifest_content_address_and_canonical_bytes_are_enforced(tmp_path, monkeypatch):
    manifest_path, paths, manifest = _fixture(tmp_path, monkeypatch)
    expected_manifest_id = manifest["manifest_id"]
    manifest["release_evidence"]["api_declared_release"] = "42.0"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(snapshot.PrintsSnapshotError, match="canonical|content-address"):
        snapshot.verify_prints_manifest(
            manifest_path, expected_manifest_id=expected_manifest_id, **paths
        )


def test_verifier_rejects_a_different_self_consistent_snapshot_before_artifact_replay(
    tmp_path, monkeypatch
):
    manifest_path, paths, manifest = _fixture(tmp_path, monkeypatch)
    assert manifest["manifest_id"] != snapshot.EXPECTED_PRINTS_SNAPSHOT_ID
    monkeypatch.setattr(
        snapshot,
        "build_prints_manifest",
        lambda **_kwargs: pytest.fail("source artifacts replayed before allowlist rejection"),
    )

    with pytest.raises(snapshot.PrintsSnapshotError, match="not the pinned production snapshot"):
        snapshot.verify_prints_manifest(
            manifest_path,
            expected_manifest_id=snapshot.EXPECTED_PRINTS_SNAPSHOT_ID,
            **paths,
        )


def test_fetch_install_stages_all_sources_and_installs_the_manifest_last(tmp_path, monkeypatch):
    _, paths, expected = _fixture(tmp_path / "fixture", monkeypatch)
    out = tmp_path / "installed"
    monkeypatch.setattr(fetch, "OUT_DIR", out)
    monkeypatch.setattr(fetch, "INTERPRO_XML", paths["interpro_xml_path"])
    monkeypatch.setattr(fetch, "EXPECTED_PRINTS_SNAPSHOT_ID", expected["manifest_id"])

    installed = fetch._install_prints_snapshot(
        API_ROWS,
        {
            "prints42_0.kdat": KDAT,
            "FingerPRINTShierarchy21Feb2012": HIERARCHY_RAW,
        },
    )
    assert installed["manifest_id"] == expected["manifest_id"]
    final_paths = {
        "api_path": out / "prints.jsonl",
        "kdat_path": out / "prints42_0.kdat",
        "hierarchy_path": out / snapshot.HIERARCHY_NAME,
        "interpro_xml_path": paths["interpro_xml_path"],
    }
    assert (
        snapshot.verify_prints_manifest(
            out / snapshot.MANIFEST_NAME,
            expected_manifest_id=expected["manifest_id"],
            **final_paths,
        )
        == installed
    )


def test_fetch_rejects_a_different_self_consistent_snapshot_before_install(tmp_path, monkeypatch):
    _, paths, manifest = _fixture(tmp_path / "fixture", monkeypatch)
    assert manifest["manifest_id"] != snapshot.EXPECTED_PRINTS_SNAPSHOT_ID
    out = tmp_path / "installed"
    out.mkdir()
    sentinel = out / "prints.jsonl"
    sentinel.write_bytes(b"existing approved snapshot\n")
    monkeypatch.setattr(fetch, "OUT_DIR", out)
    monkeypatch.setattr(fetch, "INTERPRO_XML", paths["interpro_xml_path"])

    with pytest.raises(snapshot.PrintsSnapshotError, match="not the pinned production snapshot"):
        fetch._install_prints_snapshot(
            API_ROWS,
            {
                "prints42_0.kdat": KDAT,
                "FingerPRINTShierarchy21Feb2012": HIERARCHY_RAW,
            },
        )
    assert sentinel.read_bytes() == b"existing approved snapshot\n"
    assert not (out / snapshot.MANIFEST_NAME).exists()


def test_failed_fetch_staging_does_not_replace_an_existing_snapshot(tmp_path, monkeypatch):
    _, paths, expected = _fixture(tmp_path / "fixture", monkeypatch)
    out = tmp_path / "installed"
    out.mkdir()
    old_api = out / "prints.jsonl"
    old_api.write_bytes(b"old snapshot\n")
    monkeypatch.setattr(fetch, "OUT_DIR", out)
    monkeypatch.setattr(fetch, "INTERPRO_XML", paths["interpro_xml_path"])
    monkeypatch.setattr(fetch, "EXPECTED_PRINTS_SNAPSHOT_ID", expected["manifest_id"])

    with pytest.raises(snapshot.PrintsSnapshotError):
        fetch._install_prints_snapshot(
            API_ROWS,
            {
                "prints42_0.kdat": KDAT + b"tampered",
                "FingerPRINTShierarchy21Feb2012": HIERARCHY_RAW,
            },
        )
    assert old_api.read_bytes() == b"old snapshot\n"
    assert not (out / snapshot.MANIFEST_NAME).exists()


def test_local_materializer_is_dry_run_by_default_and_installs_replayable_files(
    tmp_path, monkeypatch
):
    fixture_dir = tmp_path / "fixture"
    _, paths, expected = _fixture(fixture_dir, monkeypatch)
    hierarchy_source = fixture_dir / "FingerPRINTShierarchy21Feb2012"
    hierarchy_source.write_bytes(HIERARCHY_RAW)
    output_dir = tmp_path / "derived"
    hierarchy_output = output_dir / snapshot.HIERARCHY_NAME
    manifest_output = output_dir / snapshot.MANIFEST_NAME

    dry_run = snapshot.materialize_local_snapshot(
        expected_manifest_id=expected["manifest_id"],
        api_path=paths["api_path"],
        kdat_path=paths["kdat_path"],
        hierarchy_source_path=hierarchy_source,
        hierarchy_path=hierarchy_output,
        interpro_xml_path=paths["interpro_xml_path"],
        manifest_path=manifest_output,
        apply=False,
    )
    assert dry_run["manifest_id"] == expected["manifest_id"]
    assert not output_dir.exists()
    assert not hierarchy_output.exists()
    assert not manifest_output.exists()

    installed = snapshot.materialize_local_snapshot(
        expected_manifest_id=expected["manifest_id"],
        api_path=paths["api_path"],
        kdat_path=paths["kdat_path"],
        hierarchy_source_path=hierarchy_source,
        hierarchy_path=hierarchy_output,
        interpro_xml_path=paths["interpro_xml_path"],
        manifest_path=manifest_output,
        apply=True,
    )
    assert installed["manifest_id"] == expected["manifest_id"]
    assert (
        snapshot.verify_prints_manifest(
            manifest_output,
            expected_manifest_id=expected["manifest_id"],
            api_path=paths["api_path"],
            kdat_path=paths["kdat_path"],
            hierarchy_path=hierarchy_output,
            interpro_xml_path=paths["interpro_xml_path"],
        )
        == installed
    )


def test_local_materializer_rejects_a_different_self_consistent_snapshot_before_install(
    tmp_path, monkeypatch
):
    fixture_dir = tmp_path / "fixture"
    _, paths, manifest = _fixture(fixture_dir, monkeypatch)
    assert manifest["manifest_id"] != snapshot.EXPECTED_PRINTS_SNAPSHOT_ID
    hierarchy_source = fixture_dir / "FingerPRINTShierarchy21Feb2012"
    hierarchy_source.write_bytes(HIERARCHY_RAW)
    output_dir = tmp_path / "derived"
    hierarchy_output = output_dir / snapshot.HIERARCHY_NAME
    manifest_output = output_dir / snapshot.MANIFEST_NAME

    with pytest.raises(snapshot.PrintsSnapshotError, match="not the pinned production snapshot"):
        snapshot.materialize_local_snapshot(
            expected_manifest_id=snapshot.EXPECTED_PRINTS_SNAPSHOT_ID,
            api_path=paths["api_path"],
            kdat_path=paths["kdat_path"],
            hierarchy_source_path=hierarchy_source,
            hierarchy_path=hierarchy_output,
            interpro_xml_path=paths["interpro_xml_path"],
            manifest_path=manifest_output,
            apply=True,
        )
    assert not hierarchy_output.exists()
    assert not manifest_output.exists()


@pytest.mark.parametrize("collision", ["same_output", "api", "kdat", "source", "xml"])
def test_local_materializer_refuses_output_aliases_before_writing(tmp_path, monkeypatch, collision):
    fixture_dir = tmp_path / "fixture"
    _, paths, expected = _fixture(fixture_dir, monkeypatch)
    hierarchy_source = fixture_dir / "FingerPRINTShierarchy21Feb2012"
    hierarchy_source.write_bytes(HIERARCHY_RAW)
    output_dir = tmp_path / "derived"
    hierarchy_output = output_dir / snapshot.HIERARCHY_NAME
    manifest_output = output_dir / snapshot.MANIFEST_NAME
    if collision == "same_output":
        manifest_output = hierarchy_output
    elif collision == "api":
        hierarchy_output = paths["api_path"]
    elif collision == "kdat":
        hierarchy_output = paths["kdat_path"]
    elif collision == "source":
        hierarchy_output = hierarchy_source
    elif collision == "xml":
        hierarchy_output = paths["interpro_xml_path"]

    before = {path: path.read_bytes() for path in [*paths.values(), hierarchy_source]}
    with pytest.raises(snapshot.PrintsSnapshotError, match="distinct|aliases|canonical names"):
        snapshot.materialize_local_snapshot(
            expected_manifest_id=expected["manifest_id"],
            api_path=paths["api_path"],
            kdat_path=paths["kdat_path"],
            hierarchy_source_path=hierarchy_source,
            hierarchy_path=hierarchy_output,
            interpro_xml_path=paths["interpro_xml_path"],
            manifest_path=manifest_output,
            apply=True,
        )
    assert {path: path.read_bytes() for path in before} == before
