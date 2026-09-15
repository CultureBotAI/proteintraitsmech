"""Content-bound, atomically replaced text-embedding checkpoints.

A checkpoint is one NPZ containing both vectors and their identity. Legacy
standalone vectors/fingerprint files are never sufficient resume evidence.
NumPy is imported only by checkpoint I/O; corpus identity uses the standard
library and hashes every ordered identifier/document pair.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from zipfile import BadZipFile

SCHEMA_VERSION = 1


class CheckpointError(ValueError):
    """A checkpoint cannot prove it belongs to the requested embedding run."""


def corpus_identity(
    ids: Sequence[str],
    documents: Sequence[str],
    *,
    name: str,
    revision: str,
    text_mode: str,
    max_seq_length: int,
    normalized: bool,
    dtype: str,
) -> dict[str, Any]:
    """Hash the full ordered corpus and all settings that affect its vectors."""
    if not ids or len(ids) != len(documents):
        raise ValueError("ids and documents must have the same positive length")
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("record identifiers must be nonempty, unique strings")
    if any(not isinstance(doc, str) for doc in documents):
        raise ValueError("documents must be strings")
    if not isinstance(name, str) or not name:
        raise ValueError("model name is required")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("model revision must be a full lowercase 40-character commit")
    if not isinstance(text_mode, str) or not text_mode:
        raise ValueError("text mode is required")
    if type(max_seq_length) is not int or max_seq_length <= 0:
        raise ValueError("max_seq_length must be a positive integer")
    if type(normalized) is not bool or dtype not in {"float16", "float32"}:
        raise ValueError("normalization must be boolean and dtype float16 or float32")
    identity = {
        "schema_version": SCHEMA_VERSION,
        "count": len(ids),
        "text_mode": text_mode,
        "encoder": {
            "name": name, "revision": revision, "max_seq_length": max_seq_length,
            "normalized": normalized, "dtype": dtype,
        },
    }
    config = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256()
    for value in [config]:
        digest.update(len(value).to_bytes(8, "big"))
        digest.update(value)
    for identifier, document in zip(ids, documents, strict=True):
        for value in (identifier.encode("utf-8"), document.encode("utf-8")):
            digest.update(len(value).to_bytes(8, "big"))
            digest.update(value)
    return {**identity, "sha256": digest.hexdigest()}


def _validate_vectors(vectors: Any, identity: dict[str, Any], dimension: int) -> None:
    import numpy as np

    if not isinstance(vectors, np.ndarray) or vectors.ndim != 2:
        raise CheckpointError("checkpoint vectors must be a two-dimensional numeric array")
    if not 0 < vectors.shape[0] <= identity["count"] or vectors.shape[1] != dimension:
        raise CheckpointError("checkpoint vector dimensions or row count do not match the corpus")
    if vectors.dtype != np.dtype(identity["encoder"]["dtype"]):
        raise CheckpointError("checkpoint vector dtype does not match the encoder")
    # Bounded temporary arrays: the production checkpoint can be hundreds of MB.
    for start in range(0, len(vectors), 1024):
        chunk = vectors[start:start + 1024]
        if not np.isfinite(chunk).all():
            raise CheckpointError("checkpoint vectors contain non-finite values")
        if identity["encoder"]["normalized"]:
            lengths = np.linalg.norm(chunk.astype(np.float32), axis=1)
            if not np.allclose(lengths, 1.0, rtol=0, atol=0.005):
                raise CheckpointError("checkpoint vectors are not L2-normalized")


def load_checkpoint(path: Path, identity: dict[str, Any], dimension: int) -> Any | None:
    """Return a verified prefix (including complete runs), or None if absent.

    Invalid or mismatched checkpoints raise CheckpointError so callers can
    report why they restart. Loading never enables NumPy's pickle support.
    """
    import numpy as np

    try:
        with path.open("rb") as stream, np.load(stream, allow_pickle=False) as archive:
            if set(archive.files) != {"vectors", "metadata"}:
                raise CheckpointError("checkpoint has missing or unexpected members")
            metadata_array = archive["metadata"]
            if metadata_array.ndim != 0 or metadata_array.dtype.kind != "U":
                raise CheckpointError("checkpoint metadata must be a JSON string scalar")
            metadata = json.loads(metadata_array.item())
            if not isinstance(metadata, dict) or metadata.get("identity") != identity:
                raise CheckpointError("checkpoint corpus or encoder identity does not match")
            vectors = archive["vectors"]
            _validate_vectors(vectors, identity, dimension)
            if metadata.get("rows") != len(vectors) or metadata.get("dimension") != dimension:
                raise CheckpointError("checkpoint metadata does not match its vector array")
            return vectors
    except FileNotFoundError:
        return None
    except CheckpointError:
        raise
    except (OSError, ValueError, EOFError, BadZipFile, KeyError, TypeError) as exc:
        raise CheckpointError(f"unreadable checkpoint ({type(exc).__name__})") from exc


def save_checkpoint(path: Path, vectors: Any, identity: dict[str, Any]) -> None:
    """Replace one complete vector/metadata pair; failure preserves the old pair."""
    import numpy as np

    dimension = vectors.shape[1] if getattr(vectors, "ndim", None) == 2 else 0
    if dimension <= 0:
        raise CheckpointError("checkpoint vectors need a positive dimension")
    _validate_vectors(vectors, identity, dimension)
    metadata = json.dumps({
        "identity": identity, "rows": len(vectors), "dimension": dimension,
    }, sort_keys=True, separators=(",", ":"))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            np.savez(stream, vectors=vectors, metadata=np.array(metadata))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
