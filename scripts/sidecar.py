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

Stdlib-only.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 1


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


def wrap(payload_key: str, data: dict, source: str, release: str | None) -> dict:
    return {"_meta": {"schema": SCHEMA,
                      "built": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                      "source": source,
                      "release": release,
                      "count": len(data)},
            payload_key: data}


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
