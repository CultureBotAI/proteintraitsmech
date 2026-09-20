"""The sequence-embedding cache: keyed by what made it, and hard to destroy.

#708 keyed the cache by model; the review of #707 then found that a mismatch
*discarded* the cache and the next save overwrote it (#721), that dtype was not
part of the key (#722), and that the separate metadata file could fall out of
step or crash the loader (#726). numpy is enough to exercise all of it.
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
A = (M650, REV, "float32")


def _vec(v, dim=4):
    return np.full(dim, v, dtype=np.float32)


def test_save_then_load_round_trips_for_the_same_model_and_dtype(tmp_path):
    embed.save_cache(tmp_path, {"h1": _vec(1), "h2": _vec(0)}, *A)
    back = embed.load_cache(tmp_path, *A)
    assert list(back) == ["h1", "h2"]
    assert back["h1"].tolist() == [1, 1, 1, 1]


@pytest.mark.parametrize("other", [(M150, REV, "float32"), (M650, "other", "float32"),
                                   (M650, REV, "float16")])
def test_another_model_revision_or_dtype_neither_reads_nor_destroys_the_cache(tmp_path, other):
    big = {f"h{i}": _vec(i) for i in range(1000)}
    embed.save_cache(tmp_path, big, *A)
    assert embed.load_cache(tmp_path, *other) == {}
    # the #508 fallback canary: one row under the other key …
    embed.save_cache(tmp_path, {"x": _vec(9, dim=2)}, *other)
    # … must leave the 1,000-row cache exactly as it was
    assert len(embed.load_cache(tmp_path, *A)) == 1000
    assert list(embed.load_cache(tmp_path, *other)) == ["x"]


def test_metadata_lives_in_the_index_so_there_is_no_stamp_to_go_stale(tmp_path):
    embed.save_cache(tmp_path, {"h1": _vec(1)}, *A)
    index_p, vec_p = embed.cache_paths(tmp_path, *A)
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted([index_p.name, vec_p.name])
    meta = json.loads(index_p.read_text())["meta"]
    assert meta == {"model": M650, "revision": REV, "dtype": "float32", "dim": 4}


@pytest.mark.parametrize("garbage", ["", "{", "[]", '{"meta": {}}'])
def test_an_unreadable_index_is_ignored_not_fatal(tmp_path, garbage, capsys):
    embed.save_cache(tmp_path, {"h1": _vec(1)}, *A)
    embed.cache_paths(tmp_path, *A)[0].write_text(garbage)
    assert embed.load_cache(tmp_path, *A) == {}
    assert "ignoring it" in capsys.readouterr().err


def test_an_index_that_misdescribes_its_vectors_is_ignored(tmp_path):
    embed.save_cache(tmp_path, {"h1": _vec(1)}, *A)
    index_p = embed.cache_paths(tmp_path, *A)[0]
    index = json.loads(index_p.read_text())
    index["meta"]["dim"] = 1280
    index_p.write_text(json.dumps(index))
    assert embed.load_cache(tmp_path, *A) == {}


def test_a_crash_between_the_two_replaces_keeps_the_valid_prefix(tmp_path):
    # vectors are replaced first and the cache only appends, so an old index
    # over new vectors is a correct prefix — recover it rather than re-embed
    embed.save_cache(tmp_path, {"h1": _vec(1), "h2": _vec(2)}, *A)
    index_p, vec_p = embed.cache_paths(tmp_path, *A)
    old_index = index_p.read_text()
    embed.save_cache(tmp_path, {"h1": _vec(1), "h2": _vec(2), "h3": _vec(3)}, *A)
    index_p.write_text(old_index)                     # the index replace never happened
    back = embed.load_cache(tmp_path, *A)
    assert list(back) == ["h1", "h2"]
    assert back["h2"].tolist() == [2, 2, 2, 2]


def test_saving_an_empty_cache_removes_the_files(tmp_path):
    # what a failed --verify-cpu leaves when every cached vector came from that run
    embed.save_cache(tmp_path, {"h1": _vec(1)}, *A)
    embed.save_cache(tmp_path, {}, *A)
    assert list(tmp_path.iterdir()) == []
    assert embed.load_cache(tmp_path, *A) == {}


def test_no_temporary_files_survive_a_save(tmp_path):
    embed.save_cache(tmp_path, {"h1": _vec(1)}, *A)
    assert not [p for p in tmp_path.iterdir() if "tmp" in p.name]
