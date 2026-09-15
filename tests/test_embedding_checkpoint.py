"""Resume integrity and interruption tests; no model download or inference."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import embedding_checkpoint as checkpoint  # noqa: E402

REVISION = "d4aa6901d3a41ba39fb536a557fa166f842b0e09"


def identity(ids=None, documents=None, **kwargs):
    config = {
        "name": "BAAI/bge-large-en-v1.5", "revision": REVISION,
        "text_mode": "full", "max_seq_length": 512, "normalized": True, "dtype": "float16",
    }
    config.update(kwargs)
    return checkpoint.corpus_identity(
        ids or ["a", "b", "c"], documents or ["first", "middle", "last"], **config,
    )


@pytest.fixture
def np():
    return pytest.importorskip("numpy")


def test_middle_document_and_id_order_change_identity():
    original = identity()
    assert identity() == original
    assert identity(documents=["first", "changed middle", "last"]) != original
    assert identity(ids=["a", "changed-id", "c"]) != original
    assert identity(ids=["b", "a", "c"], documents=["middle", "first", "last"]) != original


@pytest.mark.parametrize("change", [
    {"name": "another/model"}, {"revision": "a" * 40}, {"text_mode": "definition"},
    {"max_seq_length": 256}, {"normalized": False}, {"dtype": "float32"},
])
def test_encoder_settings_are_in_identity(change):
    assert identity(**change) != identity()


def test_framing_has_no_separator_or_pair_boundary_collision():
    assert identity(documents=["a\x1fb", "c", "last"]) != identity(
        documents=["a", "b\x1fc", "last"],
    )
    assert identity(ids=["ab", "c", "d"], documents=["e", "f", "g"]) != identity(
        ids=["a", "c", "d"], documents=["be", "f", "g"],
    )


@pytest.mark.parametrize("ids,documents", [([], []), (["a"], []), (["a", "a"], ["x", "y"])])
def test_invalid_corpora_cannot_get_identity(ids, documents):
    with pytest.raises(ValueError):
        checkpoint.corpus_identity(
            ids, documents, name="x", revision=REVISION, text_mode="full",
            max_seq_length=512, normalized=True, dtype="float16",
        )


@pytest.mark.parametrize("rows", [1, 3])
def test_partial_and_complete_checkpoint_round_trip(tmp_path, np, rows):
    path = tmp_path / "checkpoint.npz"
    vectors = np.eye(3, dtype=np.float16)[:rows]
    checkpoint.save_checkpoint(path, vectors, identity())
    np.testing.assert_array_equal(checkpoint.load_checkpoint(path, identity(), 3), vectors)


def test_legacy_npy_and_fingerprint_do_not_authorize_resume(tmp_path, np):
    np.save(tmp_path / "vectors.f16.npy", np.eye(3, dtype=np.float16)[:1])
    (tmp_path / ".corpus_fingerprint").write_text("untrusted-legacy-fingerprint")
    assert checkpoint.load_checkpoint(tmp_path / "checkpoint.npz", identity(), 3) is None


def test_other_corpus_or_dimension_cannot_resume(tmp_path, np):
    path = tmp_path / "checkpoint.npz"
    checkpoint.save_checkpoint(path, np.eye(3, dtype=np.float16)[:1], identity())
    with pytest.raises(checkpoint.CheckpointError, match="identity"):
        checkpoint.load_checkpoint(path, identity(documents=["first", "changed", "last"]), 3)
    with pytest.raises(checkpoint.CheckpointError, match="dimensions"):
        checkpoint.load_checkpoint(path, identity(), 4)


@pytest.mark.parametrize("bad", ["dtype", "nan", "infinity", "zero", "rows", "one_dimensional"])
def test_invalid_vectors_are_rejected_before_write(tmp_path, np, bad):
    path = tmp_path / "checkpoint.npz"
    vectors = np.eye(3, dtype=np.float16)
    if bad == "dtype":
        vectors = vectors.astype(np.float32)
    elif bad == "nan":
        vectors[0, 0] = np.nan
    elif bad == "infinity":
        vectors[0, 0] = np.inf
    elif bad == "zero":
        vectors[0] = 0
    elif bad == "rows":
        vectors = np.vstack([vectors, vectors])
    else:
        vectors = vectors[0]
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.save_checkpoint(path, vectors, identity())
    assert not path.exists()


@pytest.mark.parametrize("bad", ["no_metadata", "malformed_metadata", "object_metadata",
                                  "object_vectors", "truncated", "npy_not_npz", "wrong_rows",
                                  "nonfinite_vectors"])
def test_untrusted_checkpoint_files_cannot_resume(tmp_path, np, bad):
    path = tmp_path / "checkpoint.npz"
    vectors = np.eye(3, dtype=np.float16)[:1]
    metadata = {"identity": identity(), "rows": 1, "dimension": 3}
    if bad == "truncated":
        checkpoint.save_checkpoint(path, vectors, identity())
        path.write_bytes(path.read_bytes()[:50])
    elif bad == "npy_not_npz":
        with path.open("wb") as stream:
            np.save(stream, vectors)
    elif bad == "no_metadata":
        np.savez(path, vectors=vectors)
    else:
        value = np.array(json.dumps(metadata))
        if bad == "malformed_metadata":
            value = np.array("not JSON")
        elif bad == "object_metadata":
            value = np.array(metadata, dtype=object)
        elif bad == "object_vectors":
            vectors = np.array([[object()]], dtype=object)
        elif bad == "wrong_rows":
            value = np.array(json.dumps({**metadata, "rows": 2}))
        else:
            vectors[0, 0] = np.nan
        np.savez(path, vectors=vectors, metadata=value)
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.load_checkpoint(path, identity(), 3)


def test_pickle_is_explicitly_disabled(tmp_path, np, monkeypatch):
    path = tmp_path / "checkpoint.npz"
    checkpoint.save_checkpoint(path, np.eye(3, dtype=np.float16)[:1], identity())
    original_load, calls = np.load, []

    def recording_load(*args, **kwargs):
        calls.append(kwargs)
        return original_load(*args, **kwargs)

    monkeypatch.setattr(np, "load", recording_load)
    checkpoint.load_checkpoint(path, identity(), 3)
    assert calls == [{"allow_pickle": False}]


@pytest.mark.parametrize("stage", ["serialize", "flush", "replace"])
def test_interrupted_save_preserves_matching_previous_pair(tmp_path, np, monkeypatch, stage):
    path = tmp_path / "checkpoint.npz"
    before_identity = identity()
    vectors = np.eye(3, dtype=np.float16)
    checkpoint.save_checkpoint(path, vectors[:1], before_identity)
    before = path.read_bytes()

    def fail(*args, **kwargs):
        if stage == "serialize":
            args[0].write(b"truncated write")
        raise OSError("simulated interruption")

    if stage == "serialize":
        monkeypatch.setattr(np, "savez", fail)
    elif stage == "flush":
        monkeypatch.setattr(checkpoint.os, "fsync", fail)
    else:
        monkeypatch.setattr(checkpoint.os, "replace", fail)
    new_identity = identity(documents=["first", "new middle", "last"])
    with pytest.raises(OSError, match="interruption"):
        checkpoint.save_checkpoint(path, vectors[:2], new_identity)
    assert path.read_bytes() == before
    assert set(tmp_path.iterdir()) == {path}
    np.testing.assert_array_equal(
        checkpoint.load_checkpoint(path, before_identity, 3), vectors[:1],
    )
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.load_checkpoint(path, new_identity, 3)


@pytest.fixture
def encoder(tmp_path, np, monkeypatch):
    spec = importlib.util.spec_from_file_location("checkpoint_test_embed_records", SCRIPTS / "embed_records.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO_ROOT = tmp_path
    module.OUT = tmp_path / "data" / "embeddings"
    module.load_corpus = lambda mode: (["a", "b", "c"], ["first", "middle", "last"])
    calls = {"constructed": [], "encoded": []}

    class FakeModel:
        def __init__(self, *args, **kwargs):
            calls["constructed"].append((args, kwargs))
            self.max_seq_length = None

        def get_sentence_embedding_dimension(self):
            return 2

        def encode(self, documents, **kwargs):
            assert self.max_seq_length == 512
            calls["encoded"].extend(documents)
            return np.tile(np.array([1.0, 0.0]), (len(documents), 1))

    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=FakeModel))
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(
        backends=SimpleNamespace(mps=SimpleNamespace(is_available=lambda: False)),
        cuda=SimpleNamespace(is_available=lambda: False),
    ))
    monkeypatch.setattr(sys, "argv", ["embed_records.py"])
    return module, calls


@pytest.mark.parametrize("rows", [1, 3])
def test_encoder_resumes_only_missing_rows_and_retries_complete_export(encoder, np, rows):
    module, calls = encoder
    checkpoint.save_checkpoint(
        module.OUT / "checkpoint.npz", np.tile(np.array([1, 0], dtype=np.float16), (rows, 1)), identity(),
    )
    assert module.main() == 0
    assert calls["encoded"] == ["first", "middle", "last"][rows:]
    assert calls["constructed"][0][1]["revision"] == REVISION
    metadata = json.loads((module.OUT / "meta.json").read_text())
    assert metadata["embedding_identity"] == identity()
    assert metadata["count"] == 3
    assert np.load(module.OUT / "vectors.f16.npy", allow_pickle=False).shape == (3, 2)


def test_encoder_rejects_legacy_and_changed_corpus_without_relabeling(encoder, np, capsys):
    module, calls = encoder
    module.OUT.mkdir(parents=True)
    np.save(module.OUT / "vectors.f16.npy", np.array([[0, 1]], dtype=np.float16))
    legacy = module.OUT / ".corpus_fingerprint"
    legacy.write_text("old-fingerprint")
    old_identity = identity(documents=["first", "old middle", "last"])
    checkpoint.save_checkpoint(
        module.OUT / "checkpoint.npz", np.array([[0, 1]], dtype=np.float16), old_identity,
    )
    assert module.main() == 0
    assert calls["encoded"] == ["first", "middle", "last"]
    assert "checkpoint rejected" in capsys.readouterr().err
    assert legacy.read_text() == "old-fingerprint"
    np.testing.assert_array_equal(
        checkpoint.load_checkpoint(module.OUT / "checkpoint.npz", identity(), 2),
        np.tile(np.array([1, 0], dtype=np.float16), (3, 1)),
    )


def test_custom_model_requires_explicit_revision_before_loading(encoder, monkeypatch):
    module, calls = encoder
    monkeypatch.setattr(sys, "argv", ["embed_records.py", "--model", "another/model"])
    with pytest.raises(SystemExit) as caught:
        module.main()
    assert caught.value.code == 2
    assert calls["constructed"] == []
