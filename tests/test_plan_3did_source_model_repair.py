"""Fail-closed planning for the pinned 3did source-model repair."""

from __future__ import annotations

import gzip
import hashlib
import io
import pathlib
import sys
from collections.abc import Sequence

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import plan_3did_source_model_repair as repair  # noqa: E402


def _block(
    name_left: str,
    name_right: str,
    pfam_left: str,
    version_left: str,
    pfam_right: str,
    version_right: str,
    *,
    pdb_id: str,
) -> bytes:
    return (
        f"#=ID\t{name_left}\t{name_right}\t "
        f"({pfam_left}.{version_left}@Pfam\t{pfam_right}.{version_right}@Pfam)\n"
        f"#=3D\t{pdb_id}\tA:1-10\tA:20-30\t1.0\t2.0\t0:0\n"
        "A\tA\t1 \t20 \tmm\n"
        "C\tC\t2 \t21 \tss\n"
        "D\tD\t3 \t22 \tms\n"
        "E\tE\t4 \t23 \tsm\n"
        "F\tF\t5 \t24 \tmm\n"
        "//\n"
    ).encode()


FIXTURE_BLOCKS = (
    _block("Alpha", "Beta", "PF00001", "2", "PF00002", "3", pdb_id="1abc"),
    _block("HPF1", "HPF1", "PF10228", "14", "PF10228", "14", pdb_id="1abd"),
    _block(
        "UPF1_Zn_bind",
        "UPF1_Zn_bind",
        "PF09416",
        "15",
        "PF09416",
        "15",
        pdb_id="1abe",
    ),
    _block("6PF2K", "His_Phos_1", "PF01591", "23", "PF00300", "27", pdb_id="1abf"),
)


def _write_gzip(
    path: pathlib.Path,
    payload: bytes,
    *,
    original_name: str = "fixture_3did.dat",
    mtime: int = 1_700_000_000,
) -> dict[str, object]:
    buffer = io.BytesIO()
    with gzip.GzipFile(filename=original_name, mode="wb", fileobj=buffer, mtime=mtime) as handle:
        handle.write(payload)
    compressed = buffer.getvalue()
    path.write_bytes(compressed)
    return {
        "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
        "decompressed_sha256": hashlib.sha256(payload).hexdigest(),
        "compressed_size": len(compressed),
        "decompressed_size": len(payload),
        "original_name": original_name,
        "mtime": mtime,
    }


def _capture_kwargs(metadata: dict[str, object]) -> dict[str, object]:
    return {
        "expected_compressed_sha256": metadata["compressed_sha256"],
        "expected_decompressed_sha256": metadata["decompressed_sha256"],
        "expected_compressed_size": metadata["compressed_size"],
        "expected_decompressed_size": metadata["decompressed_size"],
        "expected_original_name": metadata["original_name"],
        "expected_mtime_utc": metadata["mtime"],
    }


def _source_records(path: pathlib.Path, metadata: dict[str, object]):
    with repair.capture_source(path, **_capture_kwargs(metadata)) as capture:
        return repair.parse_source(capture)


def _write_legacy_traits(traits: pathlib.Path, records: Sequence[repair.SourceRecord]) -> None:
    seen: set[tuple[str, str]] = set()
    for record in records:
        if record.legacy_pair in seen:
            continue
        seen.add(record.legacy_pair)
        path = traits / record.legacy_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(record.legacy_yaml())


def _fixture(tmp_path: pathlib.Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    source = tmp_path / "3did_flat.gz"
    metadata = _write_gzip(source, b"".join(FIXTURE_BLOCKS))
    records = _source_records(source, metadata)
    traits = tmp_path / "data" / "traits"
    _write_legacy_traits(traits, records)
    return source, metadata, records, traits


def _fixture_plan(tmp_path: pathlib.Path):
    source, metadata, _records, traits = _fixture(tmp_path)
    return repair.plan_from_paths(source, traits, **_capture_kwargs(metadata))


def test_exact_id_parser_uses_only_anchored_pfam_fields():
    line = b"#=ID\t6PF2K\tUPF1_Zn_bind\t (PF01591.23@Pfam\tPF09416.15@Pfam)\n"
    left, right, legacy_hits = repair._parse_id_line(line, line_number=7)

    assert (left.name, right.name) == ("6PF2K", "UPF1_Zn_bind")
    assert (left.pfam_accession, right.pfam_accession) == ("PF01591", "PF09416")
    assert (left.versioned_token, right.versioned_token) == (
        "PF01591.23@Pfam",
        "PF09416.15@Pfam",
    )
    assert legacy_hits[:2] == ("PF2", "PF1")


@pytest.mark.parametrize(
    "line",
    [
        b"#=ID\tAlpha\tBeta\t(PF00001.1@Pfam\tPF00002.1@Pfam)\n",
        b"#=ID\tAlpha\tBeta\t (PF0001.1@Pfam\tPF00002.1@Pfam)\n",
        b"#=ID\t\tBeta\t (PF00001.1@Pfam\tPF00002.1@Pfam)\n",
        b"#=ID\tAlpha\tBeta\textra\t (PF00001.1@Pfam\tPF00002.1@Pfam)\n",
    ],
)
def test_id_parser_rejects_noncanonical_five_field_grammar(line: bytes):
    with pytest.raises(repair.ThreeDidRepairError):
        repair._parse_id_line(line, line_number=1)


def test_source_capture_pins_compressed_and_decompressed_bytes_and_header(tmp_path):
    source = tmp_path / "source.gz"
    payload = FIXTURE_BLOCKS[0]
    metadata = _write_gzip(source, payload)

    with repair.capture_source(source, **_capture_kwargs(metadata)) as capture:
        assert capture.compressed_sha256 == metadata["compressed_sha256"]
        assert capture.decompressed_sha256 == metadata["decompressed_sha256"]
        assert capture.decompressed_path.read_bytes() == payload
        assert capture.gzip_original_name == "fixture_3did.dat"
        assert capture.gzip_mtime_utc == 1_700_000_000

    wrong = dict(_capture_kwargs(metadata))
    wrong["expected_decompressed_sha256"] = "0" * 64
    with pytest.raises(repair.ThreeDidRepairError, match="decompressed source checksum"):
        with repair.capture_source(source, **wrong):
            pass


def test_source_capture_rejects_symlink(tmp_path):
    source = tmp_path / "source.gz"
    metadata = _write_gzip(source, FIXTURE_BLOCKS[0])
    alias = tmp_path / "alias.gz"
    alias.symlink_to(source)

    with pytest.raises(repair.ThreeDidRepairError, match="without following symlinks"):
        with repair.capture_source(alias, **_capture_kwargs(metadata)):
            pass


def test_source_capture_fails_closed_without_descriptor_safety(tmp_path, monkeypatch):
    source = tmp_path / "source.gz"
    metadata = _write_gzip(source, FIXTURE_BLOCKS[0])
    monkeypatch.setattr(repair.os, "O_NOFOLLOW", 0)

    with pytest.raises(repair.ThreeDidRepairError, match="platform lacks required"):
        with repair.capture_source(source, **_capture_kwargs(metadata)):
            pass


def _reject_external_source_reads(monkeypatch, external: pathlib.Path) -> list[int]:
    external_metadata = external.stat()
    external_identity = (external_metadata.st_dev, external_metadata.st_ino)
    external_reads: list[int] = []
    original_read = repair.os.read

    def audited_read(descriptor: int, size: int) -> bytes:
        metadata = repair.os.fstat(descriptor)
        if (metadata.st_dev, metadata.st_ino) == external_identity:
            external_reads.append(descriptor)
            raise AssertionError("descriptor-relative capture consumed external bytes")
        return original_read(descriptor, size)

    monkeypatch.setattr(repair.os, "read", audited_read)
    return external_reads


def test_source_capture_intermediate_swap_cannot_redirect_read(tmp_path, monkeypatch):
    source_directory = tmp_path / "bound" / "live"
    source_directory.mkdir(parents=True)
    source = source_directory / "source.gz"
    metadata = _write_gzip(source, FIXTURE_BLOCKS[0])

    external_directory = tmp_path / "external"
    external_directory.mkdir()
    external = external_directory / source.name
    _write_gzip(external, b"external bytes must never be captured")
    external_reads = _reject_external_source_reads(monkeypatch, external)
    detached = source_directory.with_name("detached")

    def swap_after_directory_binding(event: str) -> None:
        if event != "PARENT_DIRECTORIES_BOUND":
            return
        source_directory.rename(detached)
        source_directory.symlink_to(external_directory, target_is_directory=True)

    with pytest.raises(repair.ThreeDidRepairError, match="path binding changed after capture"):
        with repair.capture_source(
            source,
            _test_hook=swap_after_directory_binding,
            **_capture_kwargs(metadata),
        ):
            pass
    assert external_reads == []


def test_source_capture_final_swap_cannot_redirect_read(tmp_path, monkeypatch):
    source = tmp_path / "source.gz"
    metadata = _write_gzip(source, FIXTURE_BLOCKS[0])
    external = tmp_path / "external.gz"
    _write_gzip(external, b"external bytes must never be captured")
    external_reads = _reject_external_source_reads(monkeypatch, external)
    detached = tmp_path / "detached-source.gz"

    def swap_after_file_binding(event: str) -> None:
        if event != "SOURCE_FILE_BOUND":
            return
        source.rename(detached)
        source.symlink_to(external)

    with pytest.raises(repair.ThreeDidRepairError, match="path binding changed after capture"):
        with repair.capture_source(
            source,
            _test_hook=swap_after_file_binding,
            **_capture_kwargs(metadata),
        ):
            pass
    assert external_reads == []


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (
            FIXTURE_BLOCKS[0].replace(b"//\n", b""),
            "unterminated final",
        ),
        (
            FIXTURE_BLOCKS[0].replace(b"F\tF\t5 \t24 \tmm\n", b""),
            "fewer than five contacts",
        ),
        (
            FIXTURE_BLOCKS[0].replace(b"A:1-10", b"A:not-a-range"),
            "invalid PDB-native domain range",
        ),
    ],
)
def test_source_parser_fails_closed_on_block_drift(
    tmp_path: pathlib.Path, payload: bytes, message: str
):
    source = tmp_path / "source.gz"
    metadata = _write_gzip(source, payload)
    with repair.capture_source(source, **_capture_kwargs(metadata)) as capture:
        with pytest.raises(repair.ThreeDidRepairError, match=message):
            repair.parse_source(capture)


def test_source_parser_rejects_duplicate_corrected_identity(tmp_path):
    payload = FIXTURE_BLOCKS[0] + FIXTURE_BLOCKS[0].replace(b"1abc", b"1abd")
    source = tmp_path / "source.gz"
    metadata = _write_gzip(source, payload)
    with repair.capture_source(source, **_capture_kwargs(metadata)) as capture:
        with pytest.raises(
            repair.ThreeDidRepairError, match="duplicate corrected source identifier"
        ):
            repair.parse_source(capture)


def test_fixture_plan_partitions_exact_missing_spurious_and_collapse(tmp_path):
    current_rows, source_rows, summary = _fixture_plan(tmp_path)

    assert len(current_rows) == 3
    assert len(source_rows) == 4
    assert summary["exact_source_native_count"] == 1
    assert summary["corrected_trait_missing_count"] == 3
    assert summary["spurious_current_trait_count"] == 2
    assert summary["direct_repair_source_count"] == 1
    assert summary["legacy_collision_key_count"] == 1
    assert summary["legacy_collapsed_extra_source_count"] == 1
    assert summary["source_classification_counts"] == {
        "COLLAPSE_PRIMARY_REPAIR_PROPOSAL": 1,
        "COLLAPSE_SUPPRESSED_REPAIR_PROPOSAL": 1,
        "DIRECT_REPAIR_PROPOSAL": 1,
        "EXACT_SOURCE_NATIVE": 1,
    }
    assert summary["current_classification_counts"] == {
        "EXACT_SOURCE_NATIVE_CURRENT": 1,
        "SPURIOUS_LEGACY_MISPARSE_CURRENT": 2,
    }
    assert summary["grounding_gate"] == repair.GROUNDING_GATE
    assert summary["writes_performed"] is False
    assert summary["writer_available"] is False
    assert summary["apply_supported"] is False
    assert summary["delete_supported"] is False
    assert summary["fetch_supported"] is False

    proposals = [row["corrected_proposal"] for row in source_rows]
    assert len({row["identifier"] for row in proposals}) == 4
    assert len({row["label"] for row in proposals}) == 4
    assert len({row["record_path"] for row in proposals}) == 4
    hp_rows = [row for row in source_rows if row["legacy_identifier"].endswith("PF1_PF1")]
    assert [row["legacy_collision_group_ordinal"] for row in hp_rows] == [1, 2]
    assert hp_rows[1]["legacy_collision_primary_source_record_id"] == hp_rows[0]["source_record_id"]

    for row in [*current_rows, *source_rows]:
        row_without_hash = dict(row)
        row_sha256 = row_without_hash.pop("row_sha256")
        assert row_sha256 == repair.value_sha256(row_without_hash)


def test_fixture_plan_is_byte_deterministic(tmp_path):
    first = _fixture_plan(tmp_path / "first")
    second = _fixture_plan(tmp_path / "second")

    assert first == second
    assert first[2]["rows_sha256"] == repair.rows_sha256([*first[0], *first[1]])
    summary_without_id = dict(first[2])
    plan_id = summary_without_id.pop("plan_id")
    assert plan_id == repair.PLAN_ID_PREFIX + repair.value_sha256(summary_without_id)


def test_current_index_rejects_duplicate_yaml_key_even_before_namespace_filter(tmp_path):
    traits = tmp_path / "traits"
    path = traits / "sequence" / "other.yaml"
    path.parent.mkdir(parents=True)
    path.write_text('identifier: "OTHER:1\\n"\nidentifier: OTHER:2\n')

    with pytest.raises(repair.ThreeDidRepairError, match="duplicate YAML key"):
        repair.index_current_traits(traits)


def test_current_index_rejects_symlink_anywhere_below_trait_root(tmp_path):
    traits = tmp_path / "traits"
    traits.mkdir()
    external = tmp_path / "external.yaml"
    external.write_text("identifier: OTHER:1\n")
    (traits / "alias.yaml").symlink_to(external)

    with pytest.raises(repair.ThreeDidRepairError, match="symlink below trait directory"):
        repair.index_current_traits(traits)


def test_current_index_rejects_3did_record_outside_exact_route(tmp_path):
    source, metadata, records, traits = _fixture(tmp_path)
    del source, metadata
    record = records[0]
    expected = traits / record.legacy_path
    wrong = traits / "structure" / "fold" / expected.name
    wrong.parent.mkdir(parents=True)
    expected.rename(wrong)

    with pytest.raises(repair.ThreeDidRepairError, match="outside its exact route"):
        repair.index_current_traits(traits)


def test_plan_rejects_semantic_and_byte_drift_in_legacy_envelope(tmp_path):
    source, metadata, records, traits = _fixture(tmp_path)
    path = traits / records[0].legacy_path
    path.write_bytes(
        path.read_bytes().replace(b"mapping_status: SEEDED", b"mapping_status: REVIEWED")
    )

    with pytest.raises(repair.ThreeDidRepairError, match="legacy YAML envelope drift"):
        repair.plan_from_paths(source, traits, **_capture_kwargs(metadata))


def test_plan_rejects_missing_current_legacy_identity(tmp_path):
    source, metadata, records, traits = _fixture(tmp_path)
    (traits / records[0].legacy_path).unlink()

    with pytest.raises(repair.ThreeDidRepairError, match="identity set drifted"):
        repair.plan_from_paths(source, traits, **_capture_kwargs(metadata))


def test_index_rechecks_candidate_set_for_quiescence(tmp_path, monkeypatch):
    _source, _metadata, _records, traits = _fixture(tmp_path)
    original = repair._candidate_3did_paths
    calls = 0

    def changing_candidates(root: pathlib.Path):
        nonlocal calls
        calls += 1
        found = original(root)
        if calls == 2:
            added = root / repair.THREEDID_ROUTE / "late.yaml"
            added.write_text(
                "identifier: proteintraitsmech:INTERFACE_PF99998_PF99999\ndefinition_source: 3did\n"
            )
            return original(root)
        return found

    monkeypatch.setattr(repair, "_candidate_3did_paths", changing_candidates)
    with pytest.raises(repair.ThreeDidRepairError, match="candidate set changed"):
        repair.index_current_traits(traits)


def test_cli_exposes_no_writer_apply_delete_or_fetch_mode():
    parser = repair._parser()
    destinations = {action.dest for action in parser._actions}
    assert "apply" not in destinations
    assert "out" not in destinations
    assert "output" not in destinations
    assert "delete" not in destinations
    assert "fetch" not in destinations
    with pytest.raises(SystemExit):
        parser.parse_args(["--apply"])


PRODUCTION_GOLDEN = {
    "source_record_count": 20_644,
    "source_occurrence_count": 1_038_439,
    "source_contact_count": 37_507_421,
    "source_distinct_block_pdb_count": 391_338,
    "current_trait_count": 20_638,
    "exact_source_native_count": 20_591,
    "corrected_trait_missing_count": 53,
    "spurious_current_trait_count": 47,
    "direct_repair_source_count": 42,
    "collapse_primary_source_count": 5,
    "collapse_suppressed_source_count": 6,
    "legacy_collision_key_count": 5,
    "legacy_collapsed_extra_source_count": 6,
    "corrected_pair_set_sha256": (
        "986a7b567e36381679b7daddfada68b9cb3fdc5a6863d59fc92566b3c2764185"
    ),
    "legacy_pair_set_sha256": ("5e144abb42a94abfae96fa9fe7cf600e0c05761e1d790c934e826ae576c0b2bd"),
    "missing_corrected_pair_set_sha256": (
        "c947201fe2df34758bb7a2631140494127d8852cda426956ab71922dd7b09a25"
    ),
    "spurious_legacy_pair_set_sha256": (
        "e05a831d703f9ea0dc51772bd83f90385c9ba3601e73ca3b27c19cee8f126da6"
    ),
    "source_block_index_sha256": (
        "f7556c6bf5859bb17d9bd68d6f6bd9ffa1c51a95068a7cde740add3615011690"
    ),
    "current_trait_byte_index_sha256": (
        "3b7aef732375a21c9eaeeb4974959d9afea79d026343d201299f875f34286062"
    ),
    "source_repair_rows_sha256": (
        "2e35bc93745fc358dc28943b38a1f57e8a0c531a0e64ca4ca9f04d50193ca04a"
    ),
    "collapse_provenance_sha256": (
        "e0b72b8007e8dd1f1e71c1e1d45ae98cc9111aa53b1106081b282e2b84e009a2"
    ),
    "rows_sha256": "ecfbca83d54c2669b37a61de448b553ed0d60e10ca9a0dc920aebf68ad02dfed",
    "plan_id": (
        "3did-source-model-repair-plan:"
        "9467cbed048ff0e904895b84519095745934758a6d9029230690e409a32d980b"
    ),
}


@pytest.mark.skipif(
    not repair.DEFAULT_SOURCE.is_file(),
    reason="ignored pinned 3did production artifact is absent",
)
def test_pinned_production_plan_matches_full_golden_replay():
    current_rows, source_rows, summary = repair.plan_from_paths(
        repair.DEFAULT_SOURCE,
        repair.DEFAULT_TRAITS,
    )

    for field, expected in PRODUCTION_GOLDEN.items():
        assert summary[field] == expected
    assert summary["source_classification_counts"] == {
        "COLLAPSE_PRIMARY_REPAIR_PROPOSAL": 5,
        "COLLAPSE_SUPPRESSED_REPAIR_PROPOSAL": 6,
        "DIRECT_REPAIR_PROPOSAL": 42,
        "EXACT_SOURCE_NATIVE": 20_591,
    }
    assert summary["current_classification_counts"] == {
        "EXACT_SOURCE_NATIVE_CURRENT": 20_591,
        "SPURIOUS_LEGACY_MISPARSE_CURRENT": 47,
    }
    assert summary["source_compressed_sha256"] == repair.SOURCE_GZIP_SHA256
    assert summary["source_decompressed_sha256"] == repair.SOURCE_DECOMPRESSED_SHA256
    assert summary["source_gzip_original_name"] == repair.SOURCE_RELEASE
    assert summary["grounding_gate"] == repair.GROUNDING_GATE
    assert len(current_rows) == 20_638
    assert len(source_rows) == 20_644
    for row in (current_rows[0], current_rows[-1], source_rows[0], source_rows[-1]):
        row_without_hash = dict(row)
        row_sha256 = row_without_hash.pop("row_sha256")
        assert row_sha256 == repair.value_sha256(row_without_hash)
