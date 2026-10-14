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
