"""Model downloads cannot silently broaden the panel or become functional evidence."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch_slc10_models as models


def test_registered_versioned_panel():
    rows = models.sources()
    assert len(rows) == 3
    assert all(row["url"].endswith("-model_v6.cif") for row in rows)


def test_models_dry_run_no_io(tmp_path, monkeypatch):
    monkeypatch.setattr(models, "ROOT", tmp_path)
    monkeypatch.setattr(models, "RAW", tmp_path / "data/raw/slc10")
    monkeypatch.setattr(models, "sources", lambda: [])
    monkeypatch.setattr(models, "fetch", lambda *a, **k: pytest.fail("network"))
    result = models.acquire("dry")
    assert result["qualification"] == "NONE_APO_PREDICTIONS_ONLY"
    assert not models.RAW.exists()


def test_models_partial_not_consumable(tmp_path, monkeypatch):
    monkeypatch.setattr(models, "ROOT", tmp_path)
    monkeypatch.setattr(models, "RAW", tmp_path / "data/raw/slc10")
    monkeypatch.setattr(models, "sources", lambda: [{"local_name": "AF-Q14973-F1-model_v6.cif", "url": "https://example.org"}])
    def fail(*a, **k):
        raise ValueError("source unavailable")
    monkeypatch.setattr(models, "fetch", fail)
    with pytest.raises(ValueError, match="unavailable"):
        models.acquire("partial", apply=True)
    assert not (models.RAW / "partial/manifest.json").exists()
    with pytest.raises(ValueError, match="existing"):
        models.acquire("partial")


@pytest.mark.parametrize("name", ["../escape", "/tmp/example", "", "has space"])
def test_bad_model_snapshot_names(name):
    with pytest.raises(ValueError):
        models.acquire(name)
