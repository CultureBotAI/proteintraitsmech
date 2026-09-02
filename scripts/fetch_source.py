#!/usr/bin/env python3
"""Reliably download one source release and atomically replace its destination."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


class FetchError(RuntimeError):
    """The transfer or a post-download validation failed."""


DEFAULT_FILE_MODE = 0o644


# curl retries transient HTTP itself, but a transfer that dies mid-body is not in
# its retry set: a server closing early gives 18 (CURLE_PARTIAL_FILE) and a reset
# gives 56 (CURLE_RECV_ERROR). Measured before this: a mid-body close failed on
# the first attempt with --retries 2. `--retry-all-errors` is not the fix -- it
# would also retry the 404 this code deliberately does not (#545).
TRUNCATION_EXIT_CODES = frozenset({18, 56})

# Recorded in the sidecar since #530 and never asserted on, so a server answering
# 200 with an error page installed the page as the release. None of the migrated
# call sites fetch HTML, and eight have no other content check at all (#545).
REJECTED_CONTENT_TYPES = ("text/html", "application/xhtml+xml")


def _is_rejected_content_type(value: str) -> bool:
    """True for a Content-Type this fetcher will not install as a release.

    Matched on the media type only, so `text/html; charset=utf-8` is caught. A
    200 carrying an error page passes --min-bytes and --sha256 has nothing to
    compare against on a first fetch, so without this the page is installed
    atomically and correctly -- the #455 shape, where a cached null looked like
    an absent mapping.
    """
    media_type = value.split(";", 1)[0].strip().lower()
    return media_type in REJECTED_CONTENT_TYPES


def _temporary_path(directory: Path, name: str, suffix: str) -> Path:
    fd, raw_path = tempfile.mkstemp(prefix=f".{name}.", suffix=suffix, dir=directory)
    os.close(fd)
    return Path(raw_path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _last_header(raw_headers: str, name: str) -> str | None:
    prefix = name.lower() + ":"
    values = [
        line.split(":", 1)[1].strip()
        for line in raw_headers.splitlines()
        if line.lower().startswith(prefix)
    ]
    return values[-1] if values else None


def validate_download(
    path: Path,
    *,
    min_bytes: int = 1,
    expected_sha256: str | None = None,
    contains: Sequence[str] = (),
    prefix: bytes | None = None,
) -> tuple[int, str]:
    """Validate a completed temporary download and return its size and SHA-256."""
    size = path.stat().st_size
    if size < min_bytes:
        raise FetchError(f"download is {size:,} bytes; expected at least {min_bytes:,}")
    digest = _sha256(path)
    if expected_sha256 and digest.lower() != expected_sha256.lower():
        raise FetchError(f"SHA-256 mismatch: got {digest}, expected {expected_sha256.lower()}")
    if prefix:
        with path.open("rb") as stream:
            actual_prefix = stream.read(len(prefix))
        if actual_prefix != prefix:
            raise FetchError(
                f"content prefix mismatch: got {actual_prefix.hex()}, expected {prefix.hex()}"
            )
    if contains:
        content = path.read_bytes()
        for expected in contains:
            if expected.encode("utf-8") not in content:
                raise FetchError(f"download does not contain required text: {expected!r}")
    return size, digest


def _install_mode(path: Path) -> int:
    """Preserve an existing mode, otherwise use the public raw-release default."""
    try:
        return stat.S_IMODE(path.stat().st_mode)
    except FileNotFoundError:
        return DEFAULT_FILE_MODE


def _write_json_temp(destination: Path, payload: dict[str, object], mode: int) -> Path:
    temp = _temporary_path(destination.parent, destination.name, ".tmp")
    try:
        with temp.open("w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, mode)
        return temp
    except BaseException:
        temp.unlink(missing_ok=True)
        raise


def fetch(
    url: str,
    destination: Path,
    *,
    connect_timeout: int = 15,
    max_time: int = 300,
    retries: int = 4,
    retry_delay: int = 0,
    min_bytes: int = 1,
    expected_sha256: str | None = None,
    contains: Sequence[str] = (),
    prefix: bytes | None = None,
    headers: Sequence[str] = (),
    metadata_path: Path | None = None,
    allow_html: bool = False,
) -> dict[str, object]:
    """Fetch URL into a sibling temp file, validate, then atomically replace destination."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    metadata_path = metadata_path or Path(f"{destination}.fetch.json")
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    destination_mode = _install_mode(destination)
    metadata_mode = _install_mode(metadata_path)
    download_temp = _temporary_path(destination.parent, destination.name, ".part")
    header_temp = _temporary_path(destination.parent, destination.name, ".headers")
    metadata_temp: Path | None = None

    command = [
        "curl",
        "--fail",
        "--location",
        "--silent",
        "--show-error",
        "--connect-timeout",
        str(connect_timeout),
        "--max-time",
        str(max_time),
        "--retry",
        str(retries),
        "--retry-delay",
        str(retry_delay),
        "--retry-connrefused",
        "--dump-header",
        str(header_temp),
        "--output",
        str(download_temp),
        "--write-out",
        "%{url_effective}",
    ]
    for header in headers:
        command.extend(("--header", header))
    command.extend(("--", url))

    # One deadline for the whole operation, retries and backoff included, so
    # SKILL.md's "wall-clock deadline for the complete curl process" stays true.
    # Giving each attempt its own --max-time would multiply the documented
    # ceiling by retries+1 -- the defect #545 raises against curl's own
    # --retry-max-time, which would be no better for being reintroduced here.
    deadline = time.monotonic() + max_time
    try:
        for attempt in range(retries + 1):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise FetchError(f"total download timeout after {max_time} seconds")
            try:
                completed = subprocess.run(
                    command,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=remaining,
                )
            except subprocess.TimeoutExpired as exc:
                raise FetchError(f"total download timeout after {max_time} seconds") from exc
            if completed.returncode not in TRUNCATION_EXIT_CODES:
                break
            if attempt == retries:
                detail = completed.stderr.strip() or f"curl exited {completed.returncode}"
                attempts = retries + 1
                raise FetchError(
                    f"{detail} (after {attempts} truncated attempt{'s' if attempts != 1 else ''})"
                )
            # curl reopens --output in write mode, so a retry truncates rather
            # than appends; there is nothing to clean up between attempts. The
            # backoff is charged to the same deadline as the transfers.
            time.sleep(min(2**attempt, max(0.0, deadline - time.monotonic())))
        if completed.returncode:
            detail = completed.stderr.strip() or f"curl exited {completed.returncode}"
            raise FetchError(detail)

        size, digest = validate_download(
            download_temp,
            min_bytes=min_bytes,
            expected_sha256=expected_sha256,
            contains=contains,
            prefix=prefix,
        )
        raw_headers = header_temp.read_text(encoding="iso-8859-1", errors="replace")
        metadata: dict[str, object] = {
            "bytes": size,
            "destination": str(destination),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "requested_url": url,
            "resolved_url": completed.stdout.strip() or url,
            "sha256": digest,
        }
        for output_name, header_name in (
            ("etag", "etag"),
            ("last_modified", "last-modified"),
            ("content_type", "content-type"),
        ):
            value = _last_header(raw_headers, header_name)
            if value:
                metadata[output_name] = value

        content_type = str(metadata.get("content_type", ""))
        if not allow_html and _is_rejected_content_type(content_type):
            raise FetchError(
                f"server answered 200 with {content_type!r}, which is an error page rather "
                f"than a release; pass --allow-html if this source really serves HTML"
            )

        metadata_temp = _write_json_temp(metadata_path, metadata, metadata_mode)
        with download_temp.open("rb") as stream:
            os.fsync(stream.fileno())
        os.chmod(download_temp, destination_mode)
        os.replace(download_temp, destination)
        os.replace(metadata_temp, metadata_path)
        metadata_temp = None
        directory_fd = os.open(destination.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return metadata
    finally:
        download_temp.unlink(missing_ok=True)
        header_temp.unlink(missing_ok=True)
        if metadata_temp is not None:
            metadata_temp.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="source release URL")
    parser.add_argument("destination", type=Path, help="final local path")
    parser.add_argument("--connect-timeout", type=int, default=15)
    parser.add_argument(
        "--max-time", type=int, default=300, help="wall-clock limit for all attempts"
    )
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument(
        "--retry-delay",
        type=int,
        default=0,
        help="fixed delay; 0 uses curl's transient-error exponential backoff",
    )
    parser.add_argument("--min-bytes", type=int, default=1)
    parser.add_argument("--sha256", dest="expected_sha256")
    parser.add_argument("--contains", action="append", default=[])
    parser.add_argument("--prefix-hex", help="required leading bytes, written as hexadecimal")
    parser.add_argument("--header", action="append", default=[])
    parser.add_argument("--metadata", type=Path, help="metadata sidecar path")
    parser.add_argument(
        "--allow-html",
        action="store_true",
        help="accept an HTML Content-Type; by default a 200 carrying an error page "
        "is refused rather than installed as the release (#545)",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    for name in ("connect_timeout", "max_time"):
        if getattr(args, name) < 1:
            parser.error(f"--{name.replace('_', '-')} must be positive")
    for name in ("retries", "retry_delay", "min_bytes"):
        if getattr(args, name) < 0:
            parser.error(f"--{name.replace('_', '-')} must be non-negative")
    if args.expected_sha256 and (
        len(args.expected_sha256) != 64
        or any(char not in "0123456789abcdefABCDEF" for char in args.expected_sha256)
    ):
        parser.error("--sha256 must be exactly 64 hexadecimal characters")
    try:
        prefix = bytes.fromhex(args.prefix_hex) if args.prefix_hex else None
    except ValueError as exc:
        parser.error(f"--prefix-hex must be hexadecimal: {exc}")

    metadata = args.metadata or Path(f"{args.destination}.fetch.json")
    if args.dry_run:
        print(
            json.dumps(
                {
                    "destination": str(args.destination),
                    "metadata": str(metadata),
                    "requested_url": args.url,
                    "transport": {
                        "connect_timeout": args.connect_timeout,
                        "max_time": args.max_time,
                        "retries": args.retries,
                        "retry_delay": args.retry_delay,
                    },
                    "validation": {
                        "contains": args.contains,
                        "min_bytes": args.min_bytes,
                        "prefix_hex": args.prefix_hex,
                        "sha256": args.expected_sha256,
                    },
                },
                sort_keys=True,
            )
        )
        return 0

    print(f"fetch: {args.url} -> {args.destination}")
    try:
        result = fetch(
            args.url,
            args.destination,
            connect_timeout=args.connect_timeout,
            max_time=args.max_time,
            retries=args.retries,
            retry_delay=args.retry_delay,
            min_bytes=args.min_bytes,
            expected_sha256=args.expected_sha256,
            contains=args.contains,
            prefix=prefix,
            headers=args.header,
            metadata_path=metadata,
            allow_html=args.allow_html,
        )
    except (FetchError, OSError) as exc:
        parser.exit(1, f"fetch failed: {exc}\n")
    print(
        f"fetch: installed {result['bytes']:,} bytes (sha256 {result['sha256']}) "
        f"and metadata at {metadata}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
