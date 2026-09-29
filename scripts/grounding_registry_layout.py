#!/usr/bin/env python3
"""Sharded on-disk layout for the durable evidence and bindings registries (#801).

``occurrence_evidence.jsonl`` and ``qualified_record_bindings.jsonl`` grew toward
GitHub's 50 MB large-file warning (and its 100 MB hard limit), so each now lives in an
``X.jsonl.d`` directory:

* a row goes to ``evidence_id[12:14] + ".jsonl"``, the two hex digits after
  ``ug-evidence:``, so there are at most 256 shards and only non-empty ones exist;
* every line is the promoter's canonical JSON plus ``\\n``, rows strictly ascend by
  key, and joining the shards in name order reproduces the legacy flat file byte for
  byte, so a registry's *logical* sha256 equals the flat sha256 it replaces;
* ``manifest.json`` is a pure function of the shard bytes and is written last, so it
  is the commit marker: a torn, partial or hand-edited directory never verifies.

The layout is selected by the name alone. A ``.jsonl.d`` path is sharded; any other
path is a flat file read exactly as before. ``X.jsonl`` and ``X.jsonl.d`` must never
both exist.

This module is stdlib-only, imports neither the promoter nor the validator, and never
writes a registry file: it plans writes and the promoter's transaction installs them.
The one file it creates is the advisory lock beside the registries.
"""

from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import io
import json
import os
import re
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Literal, Mapping, Sequence

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = ROOT / "data" / "grounding"

SHARD_SUFFIX = ".jsonl.d"
MANIFEST_NAME = "manifest.json"
LAYOUT = "evidence-id-hex2"
LAYOUT_VERSION = 1
KEY_FIELD = "evidence_id"
KEY_RE = re.compile(r"ug-evidence:[0-9a-f]{64}")
SHARD_RE = re.compile(r"[0-9a-f]{2}\.jsonl")
# Finder litter, gitignored at the repo root; rejecting it would fail local validation
# on macOS for no integrity gain.
TOLERATED_ENTRIES = frozenset({".DS_Store"})
LOCK_NAME = ".grounding-registries.lock"
# Tripwire, not a limit anything relies on: 2x headroom below GitHub's 50 MB warning.
# A simulated 1M-row bindings registry peaks near 6 MB per shard.
MAX_SHARD_BYTES = 25_000_000

# The registries `check` verifies under --root, evidence first.
CHECKED_REGISTRIES = ("occurrence_evidence.jsonl.d", "qualified_record_bindings.jsonl.d")

_KEY_PREFIX_LENGTH = len("ug-evidence:")
# `_atomic_bytes` stages each target as `.<name>.XXXXXXXX` beside it, so a crash
# between mkstemp and os.replace leaves one of these behind.
_RESIDUE_RE = re.compile(r"\.(?:manifest\.json|[0-9a-f]{2}\.jsonl)\..+")


class RegistryLayoutError(ValueError):
    """A registry is not in a layout this module can read or write safely."""

    def __init__(self, code: str, message: str, path: Path | None = None) -> None:
        super().__init__(code, message, path)
        self.code = code
        self.message = message
        self.path = path

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


@dataclass(frozen=True)
class LayoutIssue:
    """One layout defect, located at a file and 1-based line (0 = the whole file)."""

    code: str
    message: str
    file: Path
    line: int


@dataclass(frozen=True)
class RegistryImage:
    """One read of a registry: every line comes from the bytes that were checked.

    ``kind`` is ``absent`` only when neither the path nor its twin exists; otherwise
    it follows the path's name. ``logical_sha256`` is the flat file's sha256, or for a
    sharded registry the sha256 of its shards joined in name order, set only when the
    directory has no layout issue. ``manifest`` is the parsed ``manifest.json`` when it
    parses as an object.
    """

    kind: Literal["absent", "flat", "sharded"]
    path: Path
    lines: tuple[tuple[Path, int, str], ...]
    issues: tuple[LayoutIssue, ...]
    logical_sha256: str | None
    manifest: dict[str, Any] | None


@dataclass(frozen=True)
class _Scan:
    image: RegistryImage
    keys: tuple[str, ...] = ()
    shard_bytes: Mapping[str, int] | None = None
    # (file, line) of rows that do not parse. They carry no layout issue because the
    # loaders already report them as *_json_error; sharded_digest still refuses them.
    unparseable: tuple[tuple[Path, int], ...] = ()


def is_sharded(path: Path | str) -> bool:
    name = Path(path).name
    return name.endswith(SHARD_SUFFIX) and len(name) > len(SHARD_SUFFIX)


def sharded_ancestor(path: Path | str) -> Path | None:
    """``path`` or its nearest ancestor named like a sharded registry, in any case.

    The layout is still selected by the exact name. This is for the guards that keep
    foreign files out of a registry: APFS and other case-insensitive filesystems
    resolve ``X.jsonl.D`` to ``X.jsonl.d``, and ``Path.resolve()`` keeps the caller's
    spelling, so an exact-name check alone lets the alias through.
    """

    path = Path(path)
    for candidate in (path, *path.parents):
        if is_sharded(candidate.name.casefold()):
            return candidate
    return None


def legacy_twin(path: Path | str) -> Path | None:
    """``X.jsonl.d`` <-> ``X.jsonl``; ``None`` for a name with no twin."""

    path = Path(path)
    if is_sharded(path):
        return path.with_name(path.name[: -len(".d")])
    if path.name.endswith(".jsonl") and len(path.name) > len(".jsonl"):
        return path.with_name(path.name + ".d")
    return None


def registry_exists(path: Path | str) -> bool:
    """True when the path or its twin exists in either layout, dangling links included."""

    path = Path(path)
    twin = legacy_twin(path)
    return os.path.lexists(path) or (twin is not None and os.path.lexists(twin))


def shard_name(key: str) -> str:
    if not isinstance(key, str) or KEY_RE.fullmatch(key) is None:
        raise RegistryLayoutError("registry_row_misplaced", f"invalid {KEY_FIELD}: {key!r}")
    return key[_KEY_PREFIX_LENGTH : _KEY_PREFIX_LENGTH + 2] + ".jsonl"


def canonical_line(row: Any) -> str:
    """The promoter's ``_canonical_json`` plus the terminating newline."""

    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def _inspect_line(
    line: str, previous: str | None, expected_shard: str | None
) -> tuple[str | None, list[tuple[str, str]], bool]:
    """Return ``(key, problems, unparseable)`` for one registry line.

    ``problems`` are ``(code, message)`` pairs; placement is checked only when an
    ``expected_shard`` is given. A line that does not parse gets no problem here.
    """

    if not line.strip():
        return None, [("registry_row_noncanonical", "blank line")], False
    try:
        row = json.loads(line)
    except (ValueError, RecursionError):
        return None, [], True
    problems: list[tuple[str, str]] = []
    key = row.get(KEY_FIELD) if isinstance(row, dict) else None
    if not isinstance(key, str) or KEY_RE.fullmatch(key) is None:
        key = None
        problems.append(("registry_row_misplaced", f"row has no valid {KEY_FIELD}"))
    else:
        if expected_shard is not None and shard_name(key) != expected_shard:
            detail = f"{key} belongs in {shard_name(key)}, not {expected_shard}"
            problems.append(("registry_row_misplaced", detail))
        if previous is not None and key <= previous:
            detail = f"duplicate {key}" if key == previous else f"{key} sorts before {previous}"
            problems.append(("registry_row_unsorted", detail))
    if line != canonical_line(row):
        if not line.endswith("\n"):
            detail = "missing final newline"
        else:
            detail = "row is not canonical JSON (sorted keys, compact separators, raw UTF-8, LF)"
        problems.append(("registry_row_noncanonical", detail))
    return key, problems, False


def split_registry_text(text: str) -> dict[str, bytes]:
    """Split a whole registry's canonical text into ``{shard name: bytes}``.

    Refuses rather than normalizes: a bad key, unsorted or duplicate rows, a
    non-canonical or blank line, or a missing final newline raises
    ``RegistryLayoutError``, so no caller can plan a malformed image.
    """

    if not text:
        return {}
    if not text.endswith("\n"):
        raise RegistryLayoutError(
            "registry_row_noncanonical", "registry text lacks a final newline"
        )
    grouped: dict[str, list[str]] = {}
    previous: str | None = None
    for number, body in enumerate(text[:-1].split("\n"), 1):
        line = body + "\n"
        key, problems, unparseable = _inspect_line(line, previous, None)
        if unparseable:
            raise RegistryLayoutError(
                "registry_row_noncanonical", f"line {number}: row is not JSON"
            )
        if problems:
            code, message = problems[0]
            raise RegistryLayoutError(code, f"line {number}: {message}")
        grouped.setdefault(shard_name(key), []).append(line)
        previous = key
    try:
        return {name: "".join(rows).encode("utf-8") for name, rows in sorted(grouped.items())}
    except UnicodeEncodeError as error:
        raise RegistryLayoutError(
            "registry_row_noncanonical", f"registry text is not encodable as UTF-8: {error}"
        ) from error


def _manifest(shards: Mapping[str, bytes]) -> dict[str, Any]:
    entries: dict[str, dict[str, Any]] = {}
    logical = hashlib.sha256()
    for name in sorted(shards):
        data = shards[name]
        if SHARD_RE.fullmatch(name) is None or not data:
            raise RegistryLayoutError(
                "registry_shard_unexpected", f"not a non-empty shard: {name!r}"
            )
        entries[name] = {
            "bytes": len(data),
            "rows": data.count(b"\n"),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        logical.update(data)
    return {
        "byte_count": sum(entry["bytes"] for entry in entries.values()),
        "key_field": KEY_FIELD,
        "layout": LAYOUT,
        "layout_version": LAYOUT_VERSION,
        "logical_sha256": logical.hexdigest(),
        "row_count": sum(entry["rows"] for entry in entries.values()),
        "shards": entries,
    }


def build_manifest_text(shards: Mapping[str, bytes]) -> str:
    """The one valid ``manifest.json`` for these shards: no path, name or timestamp."""

    return json.dumps(_manifest(shards), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _issue_text(issue: LayoutIssue) -> str:
    where = f"{issue.file}:{issue.line}" if issue.line else str(issue.file)
    return f"{where}: {issue.code}: {issue.message}"


def _twin_conflict(path: Path, twin: Path) -> str:
    if is_sharded(path):
        if os.path.lexists(path):
            return f"both layouts present: {path} and legacy flat {twin}"
        return (
            f"unmigrated legacy flat file {twin}; "
            "run `just migrate-grounding-registries --apply`"
        )
    both = "both layouts present; " if os.path.lexists(path) else ""
    return f"{both}registry migrated to {twin}"


def _list_directory(path: Path) -> tuple[list[str], bool, list[LayoutIssue]]:
    """Return ``(shard names, manifest present, issues)`` for one registry directory."""

    shards: list[str] = []
    manifest_present = False
    issues: list[LayoutIssue] = []
    with os.scandir(path) as scan:
        entries = sorted(scan, key=lambda entry: entry.name)
    for entry in entries:
        name = entry.name
        entry_path = path / name
        if name in TOLERATED_ENTRIES:
            continue
        if _RESIDUE_RE.fullmatch(name):
            message = (
                f"interrupted atomic write residue: {entry_path}; "
                "remove after confirming no writer is running"
            )
        elif entry.is_file(follow_symlinks=False) and name == MANIFEST_NAME:
            manifest_present = True
            continue
        elif entry.is_file(follow_symlinks=False) and SHARD_RE.fullmatch(name):
            if entry.stat(follow_symlinks=False).st_size:
                shards.append(name)
                continue
            message = f"empty shard file: {entry_path}; only non-empty shards may exist"
        elif entry.is_symlink():
            message = f"symlink in a sharded registry: {entry_path}"
        elif entry.is_dir(follow_symlinks=False):
            message = f"subdirectory in a sharded registry: {entry_path}"
        else:
            message = f"unexpected entry in a sharded registry: {entry_path}"
        issues.append(LayoutIssue("registry_shard_unexpected", message, entry_path, 0))
    return shards, manifest_present, issues


def _manifest_mismatch(recorded: Any, expected: dict[str, Any]) -> str:
    """Name up to five concrete differences between a manifest and the shards."""

    if not isinstance(recorded, dict):
        return f"{MANIFEST_NAME} is not a JSON object"
    problems: list[str] = []
    for field in ("layout", "layout_version", "key_field"):
        if field in recorded and recorded[field] == expected[field]:
            continue
        problems.append(f"unknown {field} {recorded.get(field)!r}, expected {expected[field]!r}")
    listed = recorded.get("shards")
    if not isinstance(listed, dict):
        problems.append("shards is not an object")
        listed = {}
    for name in sorted(set(listed) | set(expected["shards"])):
        if name not in expected["shards"]:
            problems.append(f"missing shard {name}")
        elif name not in listed:
            problems.append(f"extra shard {name}")
        elif listed[name] != expected["shards"][name]:
            problems.append(f"wrong shard {name}")
    if not problems:
        fields = sorted(
            field
            for field in set(recorded) | set(expected)
            if field not in expected or recorded.get(field) != expected[field]
        )
        problems = [f"wrong {field}" for field in fields] or [
            f"{MANIFEST_NAME} is not in canonical serialization"
        ]
    extra = f"; +{len(problems) - 5} more" if len(problems) > 5 else ""
    return "; ".join(problems[:5]) + extra


def _scan_flat(path: Path) -> _Scan:
    """Today's lenient reading: one read, UTF-8, universal newlines, no order checks."""

    if not path.is_file():
        issue = LayoutIssue(
            "registry_layout_conflict", f"flat registry path is not a file: {path}", path, 0
        )
        return _Scan(RegistryImage("flat", path, (), (issue,), None, None))
    data = path.read_bytes()
    lines = tuple(
        (path, number, line)
        for number, line in enumerate(io.StringIO(data.decode("utf-8"), newline=None), 1)
    )
    return _Scan(RegistryImage("flat", path, lines, (), hashlib.sha256(data).hexdigest(), None))


def _scan_sharded(path: Path) -> _Scan:
    """Read every shard once and check listing, rows and manifest, in that order."""

    if path.is_symlink() or not path.is_dir():
        issue = LayoutIssue(
            "registry_layout_conflict",
            f"sharded registry path is not a real directory: {path}",
            path,
            0,
        )
        return _Scan(RegistryImage("sharded", path, (), (issue,), None, None))
    names, manifest_present, issues = _list_directory(path)
    if not manifest_present:
        issues.append(
            LayoutIssue(
                "registry_manifest_missing",
                f"{MANIFEST_NAME} is missing: the registry was never committed "
                "or its install was interrupted",
                path,
                0,
            )
        )
    shards: dict[str, bytes] = {}
    lines: list[tuple[Path, int, str]] = []
    keys: list[str] = []
    unparseable: list[tuple[Path, int]] = []
    for name in names:
        source = path / name
        data = source.read_bytes()
        shards[name] = data
        # Split on LF only: U+2028 and CR are row content to json, not line breaks.
        pieces = data.split(b"\n")
        terminated = pieces[-1] == b""
        if terminated:
            pieces.pop()
        previous: str | None = None
        for index, piece in enumerate(pieces):
            number = index + 1
            newline = "\n" if terminated or number < len(pieces) else ""
            try:
                line = piece.decode("utf-8") + newline
            except UnicodeDecodeError as error:
                lines.append((source, number, piece.decode("utf-8", errors="replace") + newline))
                issues.append(
                    LayoutIssue(
                        "registry_row_noncanonical", f"row is not UTF-8: {error}", source, number
                    )
                )
                continue
            lines.append((source, number, line))
            key, problems, bad_json = _inspect_line(line, previous, name)
            if bad_json:
                unparseable.append((source, number))
            issues.extend(LayoutIssue(code, message, source, number) for code, message in problems)
            if key is not None:
                keys.append(key)
                previous = key
    manifest: dict[str, Any] | None = None
    if manifest_present:
        recorded_bytes = (path / MANIFEST_NAME).read_bytes()
        try:
            recorded = json.loads(recorded_bytes)
        except (ValueError, RecursionError):
            recorded = None
        manifest = recorded if isinstance(recorded, dict) else None
        expected = _manifest(shards)
        expected_text = json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if recorded_bytes != expected_text.encode("utf-8"):
            issues.append(
                LayoutIssue(
                    "registry_manifest_mismatch",
                    f"{MANIFEST_NAME} does not match the shards: "
                    f"{_manifest_mismatch(recorded, expected)}",
                    path / MANIFEST_NAME,
                    0,
                )
            )
    logical = None
    if not issues:
        digest = hashlib.sha256()
        for name in names:
            digest.update(shards[name])
        logical = digest.hexdigest()
    image = RegistryImage("sharded", path, tuple(lines), tuple(issues), logical, manifest)
    return _Scan(
        image,
        tuple(keys),
        {name: len(data) for name, data in shards.items()},
        tuple(unparseable),
    )


def _scan_registry(path: Path | str) -> _Scan:
    path = Path(path)
    kind: Literal["flat", "sharded"] = "sharded" if is_sharded(path) else "flat"
    twin = legacy_twin(path)
    if twin is not None and os.path.lexists(twin):
        issue = LayoutIssue("registry_layout_conflict", _twin_conflict(path, twin), path, 0)
        return _Scan(RegistryImage(kind, path, (), (issue,), None, None))
    if not os.path.lexists(path):
        return _Scan(RegistryImage("absent", path, (), (), None, None))
    return _scan_sharded(path) if kind == "sharded" else _scan_flat(path)


def read_registry(path: Path | str) -> RegistryImage:
    """Read a registry in whichever layout its name selects, reading each file once.

    Sharded checks run fail closed in this order: twin, absent, wrong type, listing,
    manifest present, per line (placement, order, canonical form), manifest match.
    A twin conflict or wrong type stops the read with no lines; every later defect is
    reported as an issue alongside the lines, so a validator can report both.
    """

    return _scan_registry(path).image


def sharded_digest(path: Path | str) -> str | None:
    """The verified logical sha256 of a sharded registry.

    ``None`` only when neither the directory nor its twin exists. Any layout issue, an
    unparseable row, or a non-sharded image raises ``RegistryLayoutError``, so a torn
    or hand-edited registry can never be hashed as if it were intact.
    """

    scan = _scan_registry(path)
    image = scan.image
    if image.kind == "absent":
        return None
    if image.issues:
        first = image.issues[0]
        more = f" (+{len(image.issues) - 1} more issue(s))" if len(image.issues) > 1 else ""
        raise RegistryLayoutError(first.code, _issue_text(first) + more, first.file)
    if image.kind != "sharded":
        raise RegistryLayoutError(
            "registry_layout_conflict", f"not a sharded registry: {image.path}", image.path
        )
    if scan.unparseable:
        source, number = scan.unparseable[0]
        raise RegistryLayoutError(
            "registry_row_noncanonical", f"{source}:{number}: row is not JSON", source
        )
    return image.logical_sha256


def plan_sharded_write(path: Path | str, text: str) -> list[tuple[Path, bytes | None]]:
    """Plan the writes that make ``path`` hold exactly ``text``.

    Returns ``(target, bytes)`` writes for new or changed shards in name order, then
    ``(target, None)`` deletes for shards that are now empty, then ``manifest.json``
    last. ``[]`` means the directory already holds this image. The twin is the
    caller's concern: the migration deletes it in the same transaction.
    """

    path = Path(path)
    if not is_sharded(path):
        raise RegistryLayoutError(
            "registry_layout_conflict", f"not a sharded registry path: {path}", path
        )
    shards = split_registry_text(text)
    current: dict[str, bytes] = {}
    recorded_manifest: bytes | None = None
    if os.path.lexists(path):
        if path.is_symlink() or not path.is_dir():
            raise RegistryLayoutError(
                "registry_layout_conflict",
                f"sharded registry path is not a real directory: {path}",
                path,
            )
        names, manifest_present, issues = _list_directory(path)
        if issues:
            raise RegistryLayoutError(issues[0].code, issues[0].message, issues[0].file)
        current = {name: (path / name).read_bytes() for name in names}
        if manifest_present:
            recorded_manifest = (path / MANIFEST_NAME).read_bytes()
    plan: list[tuple[Path, bytes | None]] = [
        (path / name, data) for name, data in shards.items() if current.get(name) != data
    ]
    plan.extend((path / name, None) for name in sorted(current) if name not in shards)
    manifest = build_manifest_text(shards).encode("utf-8")
    # Also rewritten when only the manifest is stale, so an empty plan always means
    # the directory already verifies as this exact image.
    if plan or recorded_manifest != manifest:
        plan.append((path / MANIFEST_NAME, manifest))
    return plan


def _lock_unavailable(lock_path: Path, action: str, error: OSError) -> RegistryLayoutError:
    code = errno.errorcode.get(error.errno or 0, "unknown errno")
    if action == "lock":
        hint = (
            "this filesystem may not support flock (some network filesystems do not); "
            "run the writer from a local checkout"
        )
    else:
        hint = (
            "it must be a regular file this user can open; if no writer is running, "
            "remove it (it holds only the last holder's pid)"
        )
    return RegistryLayoutError(
        "registry_lock_unavailable",
        f"cannot {action} {lock_path}: {error.strerror or error} ({code}); {hint}. "
        "Nothing was written",
        lock_path,
    )


def _open_lock_file(lock_path: Path) -> tuple[int, bool]:
    """Open the lock file, never through a symlink; return ``(descriptor, writable)``.

    ``flock`` needs only a descriptor, so a lock file this user may not write, such as
    one another user created with mode 0644, is opened read-only and still locks.
    """

    # O_NOFOLLOW: the pid is written into this file, so never through a symlink.
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    try:
        return os.open(lock_path, os.O_RDWR | os.O_CREAT | nofollow, 0o644), True
    except PermissionError as error:
        try:
            return os.open(lock_path, os.O_RDONLY | nofollow), False
        except OSError:
            raise _lock_unavailable(lock_path, "open", error) from error
    except OSError as error:
        raise _lock_unavailable(lock_path, "open", error) from error


@contextmanager
def registry_lock(directory: Path | str) -> Iterator[Path | None]:
    """Hold an exclusive advisory lock on the registries in ``directory``.

    Yields ``None`` without locking when ``directory`` does not exist, so a caller
    pointed at a missing root never creates it. The kernel drops a flock when its
    descriptor closes or the process dies, so a crashed holder never leaves the lock
    held; the lock file itself is never deleted. A lock file this user cannot write is
    locked read-only and its pid note is left alone. Any other failure to open or lock
    the file raises ``registry_lock_unavailable`` before the caller writes anything;
    only contention is ``registry_locked``.
    """

    directory = Path(directory)
    enclosing = sharded_ancestor(directory.resolve())
    if enclosing is not None:
        # The lock file would itself be an unexpected entry inside the registry.
        raise RegistryLayoutError(
            "registry_layout_conflict",
            f"refusing to lock inside the sharded registry {enclosing}: {directory}",
            directory,
        )
    if not directory.is_dir():
        yield None
        return
    lock_path = directory / LOCK_NAME
    descriptor, writable = _open_lock_file(lock_path)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            os.lseek(descriptor, 0, os.SEEK_SET)
            holder = os.read(descriptor, 64).decode("utf-8", errors="replace").strip()
            raise RegistryLayoutError(
                "registry_locked",
                f"another writer holds {lock_path} (pid {holder or 'unknown'}); "
                "wait for it to finish",
                lock_path,
            ) from error
        except OSError as error:
            raise _lock_unavailable(lock_path, "lock", error) from error
        if writable:
            try:
                os.ftruncate(descriptor, 0)
                os.lseek(descriptor, 0, os.SEEK_SET)
                os.write(descriptor, f"{os.getpid()}\n".encode("ascii"))
            except OSError as error:
                raise _lock_unavailable(lock_path, "record the pid in", error) from error
        yield lock_path
    finally:
        os.close(descriptor)


def _check(root: Path) -> int:
    failed = False
    key_sets: dict[str, frozenset[str]] = {}
    for name in CHECKED_REGISTRIES:
        path = root / name
        scan = _scan_registry(path)
        image = scan.image
        if image.kind == "absent":
            print(f"{path}: absent", file=sys.stderr)
            failed = True
            continue
        for issue in image.issues:
            print(_issue_text(issue), file=sys.stderr)
        for source, number in scan.unparseable:
            print(f"{source}:{number}: row is not JSON", file=sys.stderr)
        sizes = scan.shard_bytes or {}
        oversized = sorted(shard for shard, size in sizes.items() if size > MAX_SHARD_BYTES)
        for shard in oversized:
            print(
                f"{path / shard}: {sizes[shard]:,} bytes exceeds MAX_SHARD_BYTES "
                f"{MAX_SHARD_BYTES:,}",
                file=sys.stderr,
            )
        failed = failed or bool(image.issues or scan.unparseable or oversized)
        # Never print a digest for a registry the readers would refuse (#871).
        digest = None if scan.unparseable else image.logical_sha256
        print(
            f"{name}: kind={image.kind} rows={len(scan.keys)} shards={len(sizes)} "
            f"max_shard_bytes={max(sizes.values(), default=0)} "
            f"logical_sha256={digest or '-'}"
        )
        key_sets[name] = frozenset(scan.keys)
    if len(key_sets) == len(CHECKED_REGISTRIES):
        evidence, bindings = (key_sets[name] for name in CHECKED_REGISTRIES)
        if evidence != bindings:
            unbound = sorted(evidence - bindings)
            orphaned = sorted(bindings - evidence)
            print(
                f"evidence and bindings key sets differ: {len(unbound)} evidence row(s) "
                f"without a binding {unbound[:5]}, {len(orphaned)} binding(s) without "
                f"evidence {orphaned[:5]}",
                file=sys.stderr,
            )
            failed = True
    print(f"grounding registries: {'FAILED' if failed else 'OK'}")
    return 1 if failed else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser(
        "check",
        help="verify both sharded registries, their key parity and shard sizes (read-only)",
    )
    check.add_argument(
        "--root", type=Path, default=DEFAULT_ROOT, help="directory holding the registries"
    )
    args = parser.parse_args(argv)
    return _check(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
