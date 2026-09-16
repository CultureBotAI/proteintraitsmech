"""The sequence-embedding cache is keyed by sequence hash *and* model (#708).

Without the model check, a run with the 150M fallback model against a 650M
cache would take every sequence as a hit and assemble the wrong vectors under
the wrong name. numpy is enough to exercise this; no torch or model.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

np = pytest.importorskip("numpy")

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("embed_sequences",
                                              ROOT / "scripts" / "embed_sequences.py")
embed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(embed)  # type: ignore[union-attr]

M650, M150, REV = "facebook/esm2_t33_650M_UR50D", "facebook/esm2_t30_150M_UR50D", "abc123"


def test_save_then_load_round_trips_for_the_same_model(tmp_path):
    cache = {"h1": np.ones(4, dtype=np.float32), "h2": np.zeros(4, dtype=np.float32)}
    embed.save_cache(tmp_path, cache, M650, REV)
    assert json.loads((tmp_path / "cache_meta.json").read_text()) == {
        "model": M650, "revision": REV, "dim": 4}
    back = embed.load_cache(tmp_path, M650, REV)
    assert set(back) == {"h1", "h2"}
    assert back["h1"].tolist() == [1, 1, 1, 1]


def test_a_cache_from_another_model_or_revision_is_ignored(tmp_path, capsys):
    embed.save_cache(tmp_path, {"h1": np.ones(4, dtype=np.float32)}, M650, REV)
    assert embed.load_cache(tmp_path, M150, REV) == {}
    assert embed.load_cache(tmp_path, M650, "other") == {}
    assert "ignoring it" in capsys.readouterr().err


def test_a_cache_without_metadata_is_not_trusted(tmp_path):
    # a pre-#708 cache carries no model stamp; refusing it costs one re-embed,
    # trusting it could silently serve the wrong model's vectors
    embed.save_cache(tmp_path, {"h1": np.ones(4, dtype=np.float32)}, M650, REV)
    (tmp_path / "cache_meta.json").unlink()
    assert embed.load_cache(tmp_path, M650, REV) == {}


def test_no_temporary_files_survive_a_save(tmp_path):
    embed.save_cache(tmp_path, {"h1": np.ones(4, dtype=np.float32)}, M650, REV)
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "cache_hashes.json", "cache_meta.json", "cache_vectors.f32.npy"]
