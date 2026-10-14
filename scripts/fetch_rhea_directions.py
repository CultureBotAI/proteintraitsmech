#!/usr/bin/env python3
"""Restore the existing Rhea-141 direction pin from its official release archive.

Transport is owned by fetch_source. Only a bounded, regular TSV member whose
bytes match the already-established pin is installed; no archive paths are
extracted onto disk. This is a lookup table, not a protein grounding receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tarfile
import tempfile

import fetch_source

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_URL = "https://ftp.expasy.org/databases/rhea/old_releases/141.tar.bz2"
DIRECTIONS_SHA256 = "0b62f0cd92991b89e7b6e05707e671e80787527c30192b3d44cf7fc05a5c748f"
MAX_MEMBER_BYTES = 5_000_000


def read_directions(archive: Path, expected_sha256: str = DIRECTIONS_SHA256) -> tuple[bytes, str]:
    found = None
    with tarfile.open(archive, "r|bz2") as bundle:
        for member in bundle:
            if not (member.name == "tsv/rhea-directions.tsv"
                    or member.name.endswith("/tsv/rhea-directions.tsv")):
                continue
            if found is not None:
                raise fetch_source.FetchError("duplicate directions members")
            if not member.isfile() or not 1 <= member.size <= MAX_MEMBER_BYTES:
                raise fetch_source.FetchError("directions member is not a bounded regular file")
            stream = bundle.extractfile(member)
            if stream is None:
                raise fetch_source.FetchError("directions member cannot be read")
            with stream:
                payload = stream.read(MAX_MEMBER_BYTES + 1)
            if hashlib.sha256(payload).hexdigest() != expected_sha256:
                raise fetch_source.FetchError("archived directions do not match the release-141 pin")
            found = payload, member.name
    if found is None:
        raise fetch_source.FetchError("archive has no directions member")
    return found


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
            os.chmod(temporary, 0o644)
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


def restore(archive: Path, out: Path) -> dict:
    receipt_path = Path(f"{archive}.fetch.json")
    source_path = Path(f"{out}.source.json")
    # Run before the shared fetcher can replace a missing/stale archive. Paths
    # supplied through symlinked directories must not disguise a collision.
    paths = [archive, receipt_path, out, source_path]
    for index, path in enumerate(paths):
        for other in paths[:index]:
            if (path.resolve() == other.resolve()
                    or (path.exists() and other.exists() and path.samefile(other))):
                raise fetch_source.FetchError("archive, receipts and output paths must be distinct")
    if archive.exists() or receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if not isinstance(receipt, dict):
            raise fetch_source.FetchError("cached archive receipt must be a JSON object")
        if receipt.get("requested_url") != ARCHIVE_URL:
            raise fetch_source.FetchError("cached archive receipt has the wrong source URL")
        recorded_hash = receipt.get("sha256")
        if (not isinstance(recorded_hash, str) or len(recorded_hash) != 64
                or any(char not in "0123456789abcdefABCDEF" for char in recorded_hash)):
            raise fetch_source.FetchError("cached archive receipt has an invalid SHA-256")
        recorded_bytes = receipt.get("bytes")
        if type(recorded_bytes) is not int or recorded_bytes < 300_000_000:
            raise fetch_source.FetchError("cached archive receipt has an invalid byte count")
        size, digest = fetch_source.validate_download(
            archive, min_bytes=300_000_000, expected_sha256=recorded_hash, prefix=b"BZh")
        if size != recorded_bytes:
            raise fetch_source.FetchError("cached archive size differs from its fetch receipt")
    else:
        receipt = fetch_source.fetch(ARCHIVE_URL, archive, min_bytes=300_000_000,
                                     prefix=b"BZh", max_time=600)
        digest = receipt["sha256"]
    payload, member = read_directions(archive)
    source = {"release": "141", "archive_url": ARCHIVE_URL,
              "archive_sha256": digest, "archive_member": member,
              "archive_fetch_receipt": str(receipt_path),
              "sha256": DIRECTIONS_SHA256, "bytes": len(payload),
              "evidence_role": "DIRECTION_LOOKUP_NOT_PROTEIN_TRAIT_EVIDENCE"}
    atomic_write(out, payload)
    atomic_write(source_path, (json.dumps(source, indent=2, sort_keys=True) + "\n").encode())
    return source


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--archive", type=Path, default=ROOT / "data/raw/rhea/141.tar.bz2")
    parser.add_argument("--out", type=Path, default=ROOT / "data/raw/rhea/rhea-directions.tsv")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(restore(args.archive, args.out), indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError, tarfile.TarError, fetch_source.FetchError) as error:
        parser.exit(1, f"Rhea directions restoration failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
