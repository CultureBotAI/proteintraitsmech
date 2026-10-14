"""Bounded chemistry acquisition; offline tests must never request real sources."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch_amino_acid_properties as fetcher


def test_registered_sources():
    rows = fetcher.sources()
    assert len(rows) == len({r["url"] for r in rows}) == 22
    assert sum(r["local_name"].endswith(".cif") for r in rows) == 20


def test_dry_run_does_not_write_or_fetch(tmp_path, monkeypatch):
    monkeypatch.setattr(fetcher, "RAW", tmp_path / "raw/chemistry")
    monkeypatch.setattr(fetcher, "fetch", lambda *a, **k: pytest.fail("network"))
    assert fetcher.acquire("dry-run")["request_limit"] == 22
    assert not fetcher.RAW.exists()


@pytest.mark.parametrize("name", ["", "../escape", "/tmp/out", "has space", "UPPER"])
def test_invalid_snapshot_name(name):
    with pytest.raises(ValueError, match="identifier"):
        fetcher.acquire(name)


def test_partial_failure_is_not_complete(tmp_path, monkeypatch):
    monkeypatch.setattr(fetcher, "RAW", tmp_path / "raw/chemistry")
    def fail(*args, **kwargs):
        raise RuntimeError("unavailable")
    monkeypatch.setattr(fetcher, "fetch", fail)
    with pytest.raises(RuntimeError, match="unavailable"):
        fetcher.acquire("partial", apply=True)
    assert not (fetcher.RAW / "partial/manifest.json").exists()
    with pytest.raises(ValueError, match="existing"):
        fetcher.acquire("partial")


def test_symlink_storage_rejected(tmp_path, monkeypatch):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    monkeypatch.setattr(fetcher, "RAW", link / "chemistry")
    with pytest.raises(ValueError, match="symlink"):
        fetcher.acquire("bad")
