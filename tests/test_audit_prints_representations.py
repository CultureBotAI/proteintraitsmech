"""Focused tests for the pinned-KDAT PRINTS representation replay gate."""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import audit_prints_representations as audit  # noqa: E402
import prints_kdat  # noqa: E402

MOTIF_1 = (
    b"fc; TEST MOTIF 1\n"
    b"fl; 4\n"
    b"ft; test motif I\n"
    b"fd; ACDE PROT_A 1 1 **/R2**\n"
    b"fd; ACDF PROT_B 3 3\n"
    b"KD; INTER_MOTIF_DISTANCE REGION=0-1; MIN=1; MAX=3 /R\n"
)
MOTIF_2 = b"fc; TESTMOTIF2\nfl; 3\nft; test motif II\nfd; GHI PROT_A 7 2\nfd; GHJ PROT_B 5 -2\n"
KDAT = (
    b"gc; TESTPRINT\n"
    b"gx; PR00001\n"
    b"gn; COMPOUND(2)\n"
    b"gt; Test fingerprint\n"
    b"gd; Source-native description.\n"
    b"fm; FINAL MOTIF-SETS\n"
    b"fm; ----------------\n"
    b"bb;\n" + MOTIF_1 + b"bb;\n" + MOTIF_2 + b"bb;\n"
)


@dataclass(frozen=True)
class AuditFixture:
    traits: pathlib.Path
    trait: pathlib.Path
    kdat: pathlib.Path
    manifest: pathlib.Path
    representation: dict[str, Any]


def _write_trait(path: pathlib.Path, identifier: str, representations: Any) -> None:
    record = {
        "identifier": identifier,
        "label": "fixture",
        "sequence_fingerprint_representations": representations,
    }
    path.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")


def _manifest_payload(release: prints_kdat.PrintsRelease) -> dict[str, Any]:
    return {
        "schema_version": audit.SNAPSHOT_SCHEMA_VERSION,
        "kind": audit.MANIFEST_KIND,
        "artifacts": {
            "prints_kdat": {
                "path": audit.KDAT_ARTIFACT,
                "source": audit.KDAT_SOURCE,
                "sha256": release.source_artifact_sha256,
                "bytes": release.source_artifact_size,
                "record_count": len(release.fingerprints),
                "alternate_accession_count": 0,
                "motif_count": 2,
                "final_instance_count": 4,
            }
        },
        "release_evidence": {
            "prints_release": release.release,
            "prints_release_status": "DECLARED_BY_LOCAL_INTERPRO_XML_DBINFO",
        },
        "replay_evidence": {},
    }


def _write_content_addressed_manifest(
    path: pathlib.Path,
    payload: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = dict(payload)
    manifest_id = audit.MANIFEST_ID_PREFIX + audit.value_sha256(payload)
    manifest["manifest_id"] = manifest_id
    path.write_bytes(audit.dump_manifest(manifest))
    monkeypatch.setattr(audit, "EXPECTED_PRINTS_SNAPSHOT_ID", manifest_id)


def _make_fixture(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> AuditFixture:
    tmp_path.mkdir(parents=True, exist_ok=True)
    kdat = tmp_path / "prints42_0.kdat"
    kdat.write_bytes(KDAT)
    digest = hashlib.sha256(KDAT).hexdigest()
    monkeypatch.setattr(audit, "PRINTS_42_0_SHA256", digest)
    monkeypatch.setattr(
        prints_kdat,
        "_CANONICAL_RELEASE_FINGERPRINTS",
        MappingProxyType({prints_kdat.PRINTS_42_0_RELEASE: digest}),
    )
    release = prints_kdat.parse_prints_kdat(kdat, digest)
    representation = prints_kdat.build_fingerprint_representation(
        release,
        release.fingerprints["PR00001"],
    )

    manifest = tmp_path / "prints_snapshot_manifest.json"
    _write_content_addressed_manifest(manifest, _manifest_payload(release), monkeypatch)
    traits = tmp_path / "traits"
    traits.mkdir()
    trait = traits / "test-print.yaml"
    _write_trait(trait, "PRINTS:PR00001", [representation])
    return AuditFixture(
        traits=traits,
        trait=trait,
        kdat=kdat,
        manifest=manifest,
        representation=representation,
    )


def _run(fixture: AuditFixture) -> dict[str, Any]:
    return audit.audit_prints_representations(
        traits_path=fixture.traits,
        kdat_path=fixture.kdat,
        manifest_path=fixture.manifest,
    )


def _mutate_path(value: dict[str, Any], path: str, replacement: Any) -> dict[str, Any]:
    result = copy.deepcopy(value)
    cursor: Any = result
    parts = path.split(".")
    for part in parts[:-1]:
        cursor = cursor[int(part)] if isinstance(cursor, list) else cursor[part]
    final = parts[-1]
    if isinstance(cursor, list):
        cursor[int(final)] = replacement
    else:
        cursor[final] = replacement
    return result


def test_exact_replay_is_deterministic_and_read_only(tmp_path, monkeypatch):
    fixture = _make_fixture(tmp_path, monkeypatch)
    before = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (fixture.trait, fixture.kdat, fixture.manifest)
    }

    first = _run(fixture)
    second = _run(fixture)

    assert first == second
    assert first["status"] == "PASS"
    assert first["record_count"] == first["representation_count"] == 1
    assert first["motif_count"] == 2
    assert first["source_artifact_sha256"] == hashlib.sha256(KDAT).hexdigest()
    assert first["audit_id"].startswith(audit.AUDIT_ID_PREFIX)
    assert before == {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (fixture.trait, fixture.kdat, fixture.manifest)
    }


@pytest.mark.parametrize(
    ("field_path", "replacement", "reported_path"),
    [
        ("source_accession", "PRINTS:PR00002", "$.source_accession"),
        ("source_release", "41.0", "$.source_release"),
        ("representation_type", "OTHER", "$.representation_type"),
        ("source_artifact", "other.kdat", "$.source_artifact"),
        ("source_artifact_sha256", "0" * 64, "$.source_artifact_sha256"),
        ("source_record_sha256", "0" * 64, "$.source_record_sha256"),
        ("compatible_derivation_tool_hint", "OTHER", "$.compatible_derivation_tool_hint"),
        ("motif_count", True, "$.motif_count"),
        ("motifs.0.ordinal", 2, "$.motifs[0].ordinal"),
        ("motifs.0.motif_code", "WRONG", "$.motifs[0].motif_code"),
        ("motifs.0.length", 5, "$.motifs[0].length"),
        ("motifs.0.description", "wrong", "$.motifs[0].description"),
        ("motifs.0.training_instance_count", 3, "$.motifs[0].training_instance_count"),
        ("motifs.0.source_motif_sha256", "0" * 64, "$.motifs[0].source_motif_sha256"),
        (
            "motifs.0.training_distance_from_previous_min",
            0,
            "$.motifs[0].training_distance_from_previous_min",
        ),
        (
            "motifs.0.training_distance_from_previous_max",
            4,
            "$.motifs[0].training_distance_from_previous_max",
        ),
        (
            "motifs.0.inter_motif_distance_constraint.region_start_ordinal",
            1,
            "$.motifs[0].inter_motif_distance_constraint.region_start_ordinal",
        ),
        (
            "motifs.0.inter_motif_distance_constraint.region_end_ordinal",
            2,
            "$.motifs[0].inter_motif_distance_constraint.region_end_ordinal",
        ),
        (
            "motifs.0.inter_motif_distance_constraint.minimum",
            0,
            "$.motifs[0].inter_motif_distance_constraint.minimum",
        ),
        (
            "motifs.0.inter_motif_distance_constraint.maximum",
            4,
            "$.motifs[0].inter_motif_distance_constraint.maximum",
        ),
        (
            "motifs.0.inter_motif_distance_constraint.repeat_qualified",
            1,
            "$.motifs[0].inter_motif_distance_constraint.repeat_qualified",
        ),
    ],
)
def test_every_global_motif_and_kd_field_is_replayed_exactly(
    tmp_path,
    monkeypatch,
    field_path,
    replacement,
    reported_path,
):
    fixture = _make_fixture(tmp_path, monkeypatch)
    changed = _mutate_path(fixture.representation, field_path, replacement)
    _write_trait(fixture.trait, "PRINTS:PR00001", [changed])

    with pytest.raises(
        audit.PrintsRepresentationAuditError, match="differs from pinned KDAT"
    ) as error:
        _run(fixture)

    assert reported_path in str(error.value)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda representation: [], "expected exactly one.*found 0"),
        (lambda representation: [representation, representation], "exactly one.*found 2"),
        (
            lambda representation: [dict(representation, unexpected=True)],
            "extra key 'unexpected'",
        ),
    ],
)
def test_missing_duplicate_and_extra_representations_fail(
    tmp_path,
    monkeypatch,
    change: Callable[[dict[str, Any]], list[dict[str, Any]]],
    message,
):
    fixture = _make_fixture(tmp_path, monkeypatch)
    _write_trait(
        fixture.trait,
        "PRINTS:PR00001",
        change(copy.deepcopy(fixture.representation)),
    )

    with pytest.raises(audit.PrintsRepresentationAuditError, match=message):
        _run(fixture)


def test_missing_field_and_duplicate_yaml_key_fail_closed(tmp_path, monkeypatch):
    fixture = _make_fixture(tmp_path, monkeypatch)
    missing = copy.deepcopy(fixture.representation)
    del missing["motifs"][0]["source_motif_sha256"]
    _write_trait(fixture.trait, "PRINTS:PR00001", [missing])
    with pytest.raises(audit.PrintsRepresentationAuditError, match="missing key"):
        _run(fixture)

    fixture.trait.write_text(
        "identifier: PRINTS:PR00001\n"
        "identifier: PRINTS:PR00001\n"
        "sequence_fingerprint_representations: []\n",
        encoding="utf-8",
    )
    with pytest.raises(audit.PrintsRepresentationAuditError, match="duplicate YAML key"):
        _run(fixture)


def test_wrong_duplicate_and_nonprints_accessions_fail(tmp_path, monkeypatch):
    fixture = _make_fixture(tmp_path, monkeypatch)
    _write_trait(fixture.trait, "PRINTS:PR00002", [fixture.representation])
    with pytest.raises(audit.PrintsRepresentationAuditError, match="has no canonical KDAT"):
        _run(fixture)

    _write_trait(fixture.trait, "PRINTS:PR00001", [fixture.representation])
    duplicate = fixture.traits / "duplicate.yaml"
    _write_trait(duplicate, "PRINTS:PR00001", [fixture.representation])
    with pytest.raises(audit.PrintsRepresentationAuditError, match="duplicate PRINTS identifier"):
        _run(fixture)

    duplicate.unlink()
    _write_trait(fixture.trait, "OTHER:X", [fixture.representation])
    with pytest.raises(audit.PrintsRepresentationAuditError, match="non-PRINTS trait"):
        _run(fixture)


def test_missing_source_or_source_set_member_fails(tmp_path, monkeypatch):
    fixture = _make_fixture(tmp_path, monkeypatch)
    fixture.kdat.unlink()
    with pytest.raises(audit.PrintsRepresentationAuditError, match="missing pinned PRINTS source"):
        _run(fixture)

    fixture = _make_fixture(tmp_path / "second", monkeypatch)
    fixture.trait.unlink()
    with pytest.raises(audit.PrintsRepresentationAuditError, match="missing PRINTS trait"):
        _run(fixture)


def test_checksum_and_private_canonical_parser_provenance_are_required(tmp_path, monkeypatch):
    fixture = _make_fixture(tmp_path, monkeypatch)
    fixture.kdat.write_bytes(KDAT + b"\n")
    with pytest.raises(audit.PrintsRepresentationAuditError, match="checksum mismatch"):
        _run(fixture)

    fixture.kdat.write_bytes(KDAT)
    monkeypatch.setattr(
        prints_kdat,
        "_CANONICAL_RELEASE_FINGERPRINTS",
        MappingProxyType({prints_kdat.PRINTS_42_0_RELEASE: "f" * 64}),
    )
    with pytest.raises(prints_kdat.PrintsKdatError, match="requires the canonical"):
        _run(fixture)


def test_manifest_is_content_addressed_and_replays_exact_kdat_receipt(tmp_path, monkeypatch):
    fixture = _make_fixture(tmp_path, monkeypatch)
    manifest = json.loads(fixture.manifest.read_bytes())
    manifest["artifacts"]["prints_kdat"]["motif_count"] = 3
    payload = {key: value for key, value in manifest.items() if key != "manifest_id"}
    _write_content_addressed_manifest(fixture.manifest, payload, monkeypatch)

    with pytest.raises(audit.PrintsRepresentationAuditError, match="receipt does not replay"):
        _run(fixture)

    fixture.manifest.write_bytes(fixture.manifest.read_bytes() + b" ")
    with pytest.raises(audit.PrintsRepresentationAuditError, match="not canonical JSON"):
        _run(fixture)


@pytest.mark.parametrize("drift_target", ["kdat", "trait", "manifest"])
def test_live_source_and_record_drift_fails_closed(
    tmp_path,
    monkeypatch,
    drift_target,
):
    fixture = _make_fixture(tmp_path, monkeypatch)
    original_verify = audit._verify_records

    def verify_then_drift(records, release):
        result = original_verify(records, release)
        target = getattr(fixture, drift_target)
        target.write_bytes(target.read_bytes() + b"\n")
        return result

    monkeypatch.setattr(audit, "_verify_records", verify_then_drift)
    with pytest.raises(audit.PrintsRepresentationAuditError, match="changed during the audit"):
        _run(fixture)


def test_cli_emits_one_deterministic_json_summary_and_status(tmp_path, monkeypatch, capsys):
    fixture = _make_fixture(tmp_path, monkeypatch)
    args = [
        "--traits",
        str(fixture.traits),
        "--kdat",
        str(fixture.kdat),
        "--manifest",
        str(fixture.manifest),
    ]

    assert audit.main(args) == 0
    first = capsys.readouterr().out
    assert json.loads(first)["status"] == "PASS"
    assert audit.main(args) == 0
    assert capsys.readouterr().out == first

    fixture.kdat.unlink()
    assert audit.main(args) == 2
    failure = json.loads(capsys.readouterr().out)
    assert failure["status"] == "FAIL"
    assert "missing pinned PRINTS source" in failure["error"]
