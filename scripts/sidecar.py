#!/usr/bin/env python3
"""Provenance headers for the coordinate sidecars (issue #57, phase 13).

Three caches under `data/raw/align_cache/` feed the residue-frame alignment:

  residue_frame.json     UniProt sequences + FT intervals
  interpro_frame.json    InterPro member-DB matches with coordinates
  interpro_members.json  which Gene3D signatures each InterPro entry integrates

All three were plain `{key: value}` maps with no record of *when* they were built
or *which release* they came from. That matters more than it looks, because the
fetchers **resume** — they skip keys already present — so a stale entry is never
refreshed and the resumability that makes a crawl cheap also makes staleness
permanent. Signature boundaries move between releases, and a moved boundary flips
`part_of` / `overlaps` / `related_to` in the emitted overlay; the residue-set
identity call is exact, so a one-residue shift changes the answer.

Wrapped shape:

    {"_meta": {"schema": 1, "built": "2026-07-27", "source": "UniProt",
               "release": "2026_02", "count": 98922},
     "<payload_key>": { … }}

`read()` accepts the legacy headerless shape too, reporting `release: None`, so
an existing cache keeps working and simply cannot be release-checked until it is
rebuilt.

COMPLETENESS (issue #1070). A resumable crawl writes checkpoints, and a `--limit`
canary writes a few proteins, in exactly the shape of a finished crawl. A consumer
that reads *absence* from a frame (the grounding audit's NO_LOCAL_EXACT_TRAIT_MATCH)
must know the difference, so `_meta.completeness` records the target set and
whether every target was fetched:

    "completeness": {"complete": true, "basis": "crawl", "target_set": "…",
                     "targets": 41598, "targets_sha256": "…", "missing": 0}

`complete` is true only when every target is present. A frame without the key
predates the marker and counts as NOT complete, and so does a frame carrying only
the interim top-level `complete`/`targets` keys (no target-set identity); `fetch_interpro_frame.py --certify`
stamps such a frame offline after re-deriving its target set and checking coverage.

CONTENT DIGEST (issue #1071). The bytes embed `built` (the build date), so no
rebuild reproduces a byte pin. `content_sha256()` hashes the canonical JSON with
the volatile `_meta` keys (`built`, `completeness`, and the interim `complete`,
`targets`) removed: two frames with the
same payload, release and absent list have the same content digest whatever day
they were built or certified. It does not hide a different payload, so a rebuild
whose corpus-dependent top-up differs still has a different digest.

  python3 scripts/sidecar.py content-sha256 data/raw/align_cache/residue_frame.json

Stdlib-only.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 1
# `_meta` keys that describe *when* or *how* a frame was made, not what it holds.
# `complete` and `targets` are the interim top-level marker #1095's fetchers wrote
# briefly; it records no target-set identity and is superseded by `completeness`.
INTERIM_COMPLETENESS_KEYS = frozenset({"complete", "targets"})
VOLATILE_META_KEYS = frozenset({"built", "completeness"}) | INTERIM_COMPLETENESS_KEYS


def uniprot_release() -> str | None:
    """Current UniProtKB release, from the REST API's response header."""
    try:
        req = urllib.request.Request(
            "https://rest.uniprot.org/uniprotkb/search?query=accession:P00533"
            "&fields=accession&format=json&size=1",
            headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.headers.get("x-uniprot-release")
    except Exception:                                    # noqa: BLE001
        return None


def interpro_release() -> str | None:
    """Current InterPro release — the highest version in utils/release/."""
    try:
        req = urllib.request.Request(
            "https://www.ebi.ac.uk/interpro/api/utils/release/",
            headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
        if not isinstance(data, dict) or not data:
            return None
        return max(data, key=lambda v: [int(x) for x in v.split(".") if x.isdigit()] or [0])
    except Exception:                                    # noqa: BLE001
        return None


def wrap(payload_key: str, data: dict, source: str, release: str | None,
         completeness: dict | None = None) -> dict:
    meta = {"schema": SCHEMA,
            "built": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "source": source,
            "release": release,
            "count": len(data)}
    if completeness is not None:
        meta["completeness"] = completeness
    return {"_meta": meta, payload_key: data}


def targets_sha256(targets) -> str:
    """Digest of a target set: sorted unique accessions, one per line."""
    return hashlib.sha256("".join(f"{a}\n" for a in sorted(set(targets))).encode()).hexdigest()


def completeness(targets, present, *, target_set: str, basis: str = "crawl",
                 failed: int = 0) -> dict:
    """`_meta.completeness` for a frame meant to hold one entry per target.

    `present` is every container the targets must be in (a crawl writes the compact
    and grouped InterPro frames together, so a target counts only if it is in both).
    """
    targets = sorted(set(targets))
    missing = [a for a in targets if not all(a in container for container in present)]
    return {"complete": not missing and not failed,
            "basis": basis,
            "target_set": target_set,
            "targets": len(targets),
            "targets_sha256": targets_sha256(targets),
            "missing": len(missing)}


def is_complete(meta: dict | None) -> bool:
    """True only for a frame stamped complete. Unmarked (pre-#1070) frames are not."""
    stamp = (meta or {}).get("completeness")
    return isinstance(stamp, dict) and stamp.get("complete") is True


def content_sha256(blob) -> str:
    """SHA-256 of a frame's canonical JSON without the volatile `_meta` keys."""
    if isinstance(blob, dict) and isinstance(blob.get("_meta"), dict):
        blob = {**blob, "_meta": {key: value for key, value in blob["_meta"].items()
                                  if key not in VOLATILE_META_KEYS}}
    text = json.dumps(blob, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_atomic(path: Path, blob: dict) -> None:
    """Write compact JSON through a same-directory temporary file and replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(blob, stream, separators=(",", ":"))
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def read(path: Path, payload_key: str) -> tuple:
    """(data, meta). Legacy headerless files load with `meta['release'] = None`."""
    if not path.exists():
        return {}, {}
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return {}, {}
    if isinstance(blob, dict) and "_meta" in blob and payload_key in blob:
        return blob[payload_key], blob["_meta"]
    return blob, {"release": None, "built": None, "source": None, "legacy": True}


def check_release(meta: dict, current: str | None, path: Path,
                  allow_stale: bool = False) -> bool:
    """True if it is safe to resume from this cache.

    Refusing is the point: resuming across a release silently mixes coordinates
    from two versions of the same database into one overlay, and nothing
    downstream can tell.
    """
    cached = meta.get("release")
    if not meta:
        return True                                   # nothing cached yet
    if cached is None:
        print(f"warning: {path.name} predates release stamping — cannot tell "
              f"which release it came from. Rebuild it to get a stamp, or pass "
              f"--allow-stale to resume anyway.", file=sys.stderr)
        return allow_stale
    if current is None:
        print(f"warning: could not determine the current release; resuming from "
              f"{path.name} (built {meta.get('built')}, release {cached}) "
              f"unchecked.", file=sys.stderr)
        return True
    if cached != current:
        print(f"{path.name} was built against {meta.get('source')} release "
              f"{cached}; the current release is {current}. Resuming would mix "
              f"coordinates from two releases into one overlay. Delete the file "
              f"to rebuild, or pass --allow-stale to accept the mix.",
              file=sys.stderr)
        return allow_stale
    return True


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Print a sidecar's content digest.",
                                 allow_abbrev=False)
    ap.add_argument("command", choices=["content-sha256"])
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args(argv)
    for path in args.paths:
        blob = json.loads(path.read_text(encoding="utf-8"))
        print(f"{content_sha256(blob)}  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
