"""Historical Rhea lookup recovery must not repin or extract arbitrary files."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cross_mech_proteins as cm  # noqa: E402
import fetch_rhea_directions as fetcher  # noqa: E402
import stage_rhea_uniprot_grounding as stage  # noqa: E402

PAYLOAD = b"RHEA_ID_MASTER\tRHEA_ID_LR\tRHEA_ID_RL\tRHEA_ID_BI\n10000\t10001\t10002\t10003\n"
MEMBER = "141/tsv/rhea-directions.tsv"


def archive(tmp_path, names=(MEMBER,), kind=tarfile.REGTYPE):
    path = tmp_path / "141.tar.bz2"
    with tarfile.open(path, "w:bz2") as bundle:
        for name in names:
            member = tarfile.TarInfo(name)
            member.type = kind
            member.size = len(PAYLOAD) if kind == tarfile.REGTYPE else 0
            member.linkname = "../../outside.tsv" if kind == tarfile.SYMTYPE else ""
            bundle.addfile(member, io.BytesIO(PAYLOAD) if member.size else None)
    return path


def test_direction_pin_matches_both_consumers():
    assert fetcher.DIRECTIONS_SHA256 == cm.RHEA_DIRECTIONS_SHA256
    assert fetcher.DIRECTIONS_SHA256 == stage.CURRENT_SOURCE_SHA256["directions"]


def test_reads_verified_member_without_extracting_paths(tmp_path):
    result = fetcher.read_directions(archive(tmp_path), hashlib.sha256(PAYLOAD).hexdigest())
    assert result == (PAYLOAD, MEMBER)
    assert not (tmp_path / "141").exists()


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.DIRTYPE])
def test_nonregular_member_refused(tmp_path, kind):
    with pytest.raises(fetcher.fetch_source.FetchError, match="bounded regular"):
        fetcher.read_directions(archive(tmp_path, kind=kind))


def test_mismatching_member_refused(tmp_path):
    with pytest.raises(fetcher.fetch_source.FetchError, match="release-141 pin"):
        fetcher.read_directions(archive(tmp_path))


def test_duplicate_member_refused(tmp_path):
    with pytest.raises(fetcher.fetch_source.FetchError, match="duplicate"):
        fetcher.read_directions(archive(tmp_path, (MEMBER, MEMBER)), hashlib.sha256(PAYLOAD).hexdigest())


def test_missing_member_refused(tmp_path):
    with pytest.raises(fetcher.fetch_source.FetchError, match="no directions"):
        fetcher.read_directions(archive(tmp_path, ("../other.tsv",)))


def test_size_guard(tmp_path, monkeypatch):
    monkeypatch.setattr(fetcher, "MAX_MEMBER_BYTES", 1)
    with pytest.raises(fetcher.fetch_source.FetchError, match="bounded regular"):
        fetcher.read_directions(archive(tmp_path))


def test_bad_cache_receipt_preserves_existing_output(tmp_path):
    source = archive(tmp_path)
    Path(f"{source}.fetch.json").write_text(json.dumps({"requested_url": "https://wrong.example/"}))
    out = tmp_path / "directions.tsv"
    out.write_bytes(b"existing")
    with pytest.raises(fetcher.fetch_source.FetchError, match="wrong source"):
        fetcher.restore(source, out)
    assert out.read_bytes() == b"existing"


def test_bad_member_preserves_existing_output(tmp_path, monkeypatch):
    source = archive(tmp_path)
    receipt = {"requested_url": fetcher.ARCHIVE_URL, "sha256": "a" * 64, "bytes": 300_000_000}
    Path(f"{source}.fetch.json").write_text(json.dumps(receipt))
    monkeypatch.setattr(fetcher.fetch_source, "validate_download", lambda *a, **kw: (300_000_000, "a" * 64))
    out = tmp_path / "directions.tsv"
    out.write_bytes(b"existing")
    with pytest.raises(fetcher.fetch_source.FetchError, match="release-141 pin"):
        fetcher.restore(source, out)
    assert out.read_bytes() == b"existing"


def prepare_valid_cache(source, monkeypatch):
    receipt = {"requested_url": fetcher.ARCHIVE_URL, "sha256": "a" * 64, "bytes": 300_000_000}
    Path(f"{source}.fetch.json").write_text(json.dumps(receipt))
    monkeypatch.setattr(fetcher.fetch_source, "validate_download", lambda *a, **kw: (300_000_000, "a" * 64))
    reader = fetcher.read_directions
    monkeypatch.setattr(fetcher, "read_directions", lambda path: reader(path, hashlib.sha256(PAYLOAD).hexdigest()))


def test_restore_writes_payload_and_lookup_only_provenance(tmp_path, monkeypatch):
    source = archive(tmp_path)
    prepare_valid_cache(source, monkeypatch)
    out = tmp_path / "directions.tsv"
    result = fetcher.restore(source, out)
    assert out.read_bytes() == PAYLOAD
    assert json.loads(Path(f"{out}.source.json").read_text()) == result
    assert result["archive_sha256"] == "a" * 64
    assert result["archive_member"] == MEMBER
    assert result["evidence_role"] == "DIRECTION_LOOKUP_NOT_PROTEIN_TRAIT_EVIDENCE"


@pytest.mark.parametrize("alias", ["archive", "receipt", "sidecar_archive", "sidecar_receipt", "parent_symlink"])
def test_output_alias_refused_without_modifying_inputs(tmp_path, monkeypatch, alias):
    source = archive(tmp_path)
    if alias == "sidecar_archive":
        source = source.rename(tmp_path / "directions.tsv.source.json")
    prepare_valid_cache(source, monkeypatch)
    receipt = Path(f"{source}.fetch.json")
    out = tmp_path / "directions.tsv"
    if alias == "archive":
        out = source
    elif alias == "receipt":
        out = receipt
    elif alias == "sidecar_receipt":
        Path(f"{out}.source.json").symlink_to(receipt)
    elif alias == "parent_symlink":
        (tmp_path / "alias").symlink_to(tmp_path, target_is_directory=True)
        out = tmp_path / "alias" / source.name
    originals = {path: path.read_bytes() for path in (source, receipt)}
    with pytest.raises(fetcher.fetch_source.FetchError, match="distinct"):
        fetcher.restore(source, out)
    assert {path: path.read_bytes() for path in originals} == originals


@pytest.mark.parametrize("receipt", [
    [], None,
    {"requested_url": fetcher.ARCHIVE_URL, "sha256": None, "bytes": 300_000_000},
    {"requested_url": fetcher.ARCHIVE_URL, "sha256": 123, "bytes": 300_000_000},
    {"requested_url": fetcher.ARCHIVE_URL, "sha256": "z" * 64, "bytes": 300_000_000},
    {"requested_url": fetcher.ARCHIVE_URL, "sha256": "a" * 64, "bytes": True},
    {"requested_url": fetcher.ARCHIVE_URL, "sha256": "a" * 64, "bytes": -1},
    {"requested_url": fetcher.ARCHIVE_URL},
])
def test_malformed_cache_receipt_refused_cleanly(tmp_path, monkeypatch, receipt):
    source = archive(tmp_path)
    Path(f"{source}.fetch.json").write_text(json.dumps(receipt))
    out = tmp_path / "directions.tsv"
    out.write_bytes(b"existing")
    monkeypatch.setattr(fetcher.fetch_source, "validate_download", lambda *a, **kw: pytest.fail("invalid receipt must be rejected before validation"))
    with pytest.raises(fetcher.fetch_source.FetchError, match="receipt"):
        fetcher.restore(source, out)
    assert out.read_bytes() == b"existing"


def test_missing_archive_alias_refused_before_fetch(tmp_path, monkeypatch):
    source = tmp_path / "archive.tar.bz2"
    monkeypatch.setattr(fetcher.fetch_source, "fetch", lambda *a, **kw: pytest.fail("must reject alias before fetching"))
    with pytest.raises(fetcher.fetch_source.FetchError, match="distinct"):
        fetcher.restore(source, source)
    assert not source.exists()


def test_malformed_receipt_cli_has_no_traceback(tmp_path, capsys):
    source = archive(tmp_path)
    Path(f"{source}.fetch.json").write_text("null")
    with pytest.raises(SystemExit) as error:
        fetcher.main(["--archive", str(source), "--out", str(tmp_path / "out.tsv")])
    assert error.value.code == 1
    assert "receipt must be a JSON object" in capsys.readouterr().err
