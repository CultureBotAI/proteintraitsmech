#!/usr/bin/env python3
"""Plan or perform one receipt-bound acquisition of the six Rhea source files.

Default invocation prints one canonical, no-network/no-write execution plan.
Network access and installation require both ``--apply`` and the exact saved
``--execution-plan``.  Apply downloads all six bodies before writing anything,
validates a complete receipt in an automatically removed temporary repository,
accepts pre-existing source files only when their bytes equal the responses,
creates missing source files without replacement, and installs the receipt last.

This runner never writes traits or durable grounding.  Its receipt remains a
producer attestation that the standalone verifier cannot authenticate, and the
central grounding validator has no success branch for it.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import stage_rhea_uniprot_grounding as rhea_stage
import validate_rhea_acquisition_receipt as rhea_receipt


PLAN_SCHEMA_VERSION = 1
PLAN_KIND = "RHEA_PROVIDER_ACQUISITION_EXECUTION_PLAN"
PLAN_ID_PREFIX = "rhea-provider-acquisition-execution-plan:"
RUN_RESULT_KIND = "RHEA_PROVIDER_CONTROLLED_ACQUISITION_RESULT"
REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = Path(__file__).absolute()
TEMP_ROOT = Path(tempfile.gettempdir()).resolve()
DEFAULT_TIMEOUT_SECONDS = 120
_PLAN_MAX_BYTES = 16 * 1024 * 1024
_RUNNER_MAX_BYTES = 8 * 1024 * 1024
_READ_CHUNK_BYTES = 1024 * 1024
_ALLOWED_RESPONSE_HEADERS = frozenset(
    {
        "content-disposition",
        "content-length",
        "content-type",
        "date",
        "etag",
        "last-modified",
    }
)


class RheaAcquisitionRunError(RuntimeError):
    """A controlled Rhea acquisition plan or execution failed closed."""


class ResponseLike(Protocol):
    headers: Any
    status: int

    def __enter__(self) -> ResponseLike: ...

    def __exit__(self, *args: object) -> None: ...

    def geturl(self) -> str: ...

    def read(self, size: int = -1) -> bytes: ...


OpenUrl = Callable[..., ResponseLike]
Clock = Callable[[], str]
TestHook = Callable[[str], None]


@dataclass(slots=True)
class BoundDirectory:
    """One no-follow directory path held through component descriptors."""

    path: Path
    descriptors: list[int]
    bindings: list[tuple[int, str, tuple[int, int, int]]]

    @property
    def descriptor(self) -> int:
        return self.descriptors[-1]

    @property
    def identity(self) -> tuple[int, int, int]:
        metadata = os.fstat(self.descriptor)
        return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)

    def recheck(self) -> None:
        for parent, component, expected in self.bindings:
            try:
                live = os.stat(component, dir_fd=parent, follow_symlinks=False)
            except OSError as error:
                raise RheaAcquisitionRunError(
                    f"Rhea output directory component changed: {component!r}: {error}"
                ) from error
            if _entry_identity(live) != expected:
                raise RheaAcquisitionRunError(
                    f"Rhea output directory component changed: {component!r}"
                )

    def close(self) -> None:
        for descriptor in reversed(self.descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
        self.descriptors.clear()
        self.bindings.clear()

    def __enter__(self) -> BoundDirectory:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


@dataclass(frozen=True, slots=True)
class DownloadedResponse:
    role: str
    request_url: str
    response_url: str
    status: int
    received_at_utc: str
    header_projection: dict[str, str]
    raw: bytes

    def attestation(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "response_url": self.response_url,
            "response_status": self.status,
            "response_received_at_utc": self.received_at_utc,
            "response_header_projection": self.header_projection,
        }


def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _entry_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)


def _open_bound_directory(path: Path) -> BoundDirectory:
    no_follow = getattr(os, "O_NOFOLLOW", None)
    directory_only = getattr(os, "O_DIRECTORY", None)
    if (
        not isinstance(no_follow, int)
        or no_follow == 0
        or not isinstance(directory_only, int)
        or directory_only == 0
        or os.open not in getattr(os, "supports_dir_fd", set())
        or os.stat not in getattr(os, "supports_follow_symlinks", set())
    ):
        raise RheaAcquisitionRunError(
            "platform lacks descriptor-relative no-follow directory support"
        )
    lexical = _lexical_absolute(path)
    components = lexical.parts[1:]
    if not components or any(component in {"", ".", ".."} for component in components):
        raise RheaAcquisitionRunError(f"unsafe Rhea output directory path: {path}")
    flags = os.O_RDONLY | directory_only | no_follow | getattr(os, "O_CLOEXEC", 0)
    descriptors: list[int] = []
    bindings: list[tuple[int, str, tuple[int, int, int]]] = []
    try:
        current = os.open(lexical.anchor, flags)
        descriptors.append(current)
        for component in components:
            child = os.open(component, flags, dir_fd=current)
            metadata = os.fstat(child)
            bindings.append((current, component, _entry_identity(metadata)))
            descriptors.append(child)
            current = child
        bound = BoundDirectory(lexical, descriptors, bindings)
        bound.recheck()
        return bound
    except OSError as error:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise RheaAcquisitionRunError(
            f"cannot safely bind Rhea output directory {lexical}: {error}"
        ) from error
    except Exception:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise


def _target_paths(repo_root: Path) -> rhea_receipt.ReceiptPaths:
    root = _lexical_absolute(repo_root)
    by_role = {
        role: root / str(rhea_receipt.PLAN_ARTIFACTS[role]["target_path"])
        for role in rhea_receipt.SOURCE_ROLES
    }
    return rhea_receipt.ReceiptPaths(
        repo_root=root,
        receipt=root / rhea_receipt.DEFAULT_RECEIPT_RELATIVE,
        **by_role,
    )


def _assert_direct_targets(paths: rhea_receipt.ReceiptPaths) -> Path:
    parent = paths.repo_root / "data/raw/rhea"
    expected = {
        role: parent / Path(str(rhea_receipt.PLAN_ARTIFACTS[role]["target_path"])).name
        for role in rhea_receipt.SOURCE_ROLES
    }
    if (
        paths.source_paths() != expected
        or paths.receipt != parent / Path(rhea_receipt.DEFAULT_RECEIPT_RELATIVE).name
    ):
        raise RheaAcquisitionRunError("Rhea acquisition targets are not exact direct children")
    return parent


def _leaf_metadata(parent: BoundDirectory, name: str) -> os.stat_result | None:
    parent.recheck()
    try:
        return os.stat(name, dir_fd=parent.descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise RheaAcquisitionRunError(f"cannot inspect Rhea target {name!r}: {error}") from error


def _source_states(
    *, paths: rhea_receipt.ReceiptPaths, parent: BoundDirectory
) -> dict[str, dict[str, Any]]:
    states: dict[str, dict[str, Any]] = {}
    identities: set[tuple[int, int]] = set()
    for role, path in paths.source_paths().items():
        metadata = _leaf_metadata(parent, path.name)
        relative = str(rhea_receipt.PLAN_ARTIFACTS[role]["target_path"])
        if metadata is None:
            states[role] = {"path": relative, "state": "ABSENT"}
            continue
        try:
            capture = rhea_receipt._capture_regular_file(
                path,
                label=f"existing Rhea {role}",
                max_bytes=rhea_receipt._MAX_BYTES[role],
            )
        except (OSError, rhea_receipt.RheaAcquisitionReceiptError) as error:
            raise RheaAcquisitionRunError(str(error)) from error
        identity = capture.device, capture.inode
        if identity in identities:
            raise RheaAcquisitionRunError("existing Rhea source targets alias one another")
        identities.add(identity)
        states[role] = {
            "device": capture.device,
            "inode": capture.inode,
            "path": relative,
            "sha256": capture.sha256,
            "size_bytes": capture.size_bytes,
            "state": "PRESENT_BOUND_BYTES",
        }
    parent.recheck()
    return states


def _runner_projection() -> dict[str, Any]:
    try:
        capture = rhea_receipt._capture_regular_file(
            RUNNER_PATH, label="Rhea acquisition runner", max_bytes=_RUNNER_MAX_BYTES
        )
    except (OSError, rhea_receipt.RheaAcquisitionReceiptError) as error:
        raise RheaAcquisitionRunError(str(error)) from error
    return {
        "path": str(capture.path),
        "sha256": capture.sha256,
        "size_bytes": capture.size_bytes,
    }


def derive_execution_plan(
    *,
    repo_root: Path = REPO_ROOT,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    enforce_release_contract: bool = True,
) -> dict[str, Any]:
    """Derive one exact no-network/no-write execution plan."""

    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 3600:
        raise RheaAcquisitionRunError("timeout must be an integer from 1 through 3600 seconds")
    if type(enforce_release_contract) is not bool:
        raise RheaAcquisitionRunError("release-contract flag must be Boolean")
    paths = _target_paths(repo_root)
    parent_path = _assert_direct_targets(paths)
    runner = _runner_projection()
    with _open_bound_directory(parent_path) as parent:
        if _leaf_metadata(parent, paths.receipt.name) is not None:
            raise RheaAcquisitionRunError(
                "Rhea acquisition receipt already exists; first-generation runner refuses replacement"
            )
        states = _source_states(paths=paths, parent=parent)
        identity = parent.identity
        plan: dict[str, Any] = {
            "schema_version": PLAN_SCHEMA_VERSION,
            "kind": PLAN_KIND,
            "provider": "Rhea",
            "provider_acquisition_plan": rhea_receipt.ACQUISITION_PLAN,
            "provider_acquisition_plan_id": rhea_receipt.ACQUISITION_PLAN_ID,
            "provider_acquisition_plan_row_sha256": (rhea_receipt.ACQUISITION_PLAN_ROW_SHA256),
            "repo_root": str(paths.repo_root),
            "runner_artifact": runner,
            "network": {
                "accept_encoding": "identity",
                "method": "GET",
                "response_byte_limits": {
                    role: rhea_receipt._MAX_BYTES[role] for role in rhea_receipt.SOURCE_ROLES
                },
                "timeout_seconds": timeout_seconds,
            },
            "output_binding": {
                "parent": {
                    "device": identity[0],
                    "inode": identity[1],
                    "mode_type": identity[2],
                    "path": str(parent.path),
                },
                "receipt": {
                    "path": rhea_receipt.DEFAULT_RECEIPT_RELATIVE,
                    "state": "ABSENT_REQUIRED",
                },
                "sources": states,
                "write_policy": "CREATE_MISSING_SOURCES_WITHOUT_REPLACEMENT_AND_RECEIPT_LAST",
            },
            "release_141_contract_enforced": enforce_release_contract,
            "safety_boundary": {
                "apply_requires_exact_saved_plan": True,
                "downloads_complete_before_first_write": True,
                "durable_grounding_writes_authorized": False,
                "network_action_performed": False,
                "producer_authentication_claimed": False,
                "receipt_installed_last": True,
                "trait_writes_authorized": False,
                "write_action_performed": False,
            },
        }
        plan["plan_id"] = PLAN_ID_PREFIX + rhea_receipt.value_sha256(plan)
        parent.recheck()
        return plan


def render_execution_plan(plan: Mapping[str, Any]) -> str:
    return rhea_receipt.canonical_json(plan) + "\n"


def _load_saved_plan(path: Path) -> tuple[dict[str, Any], rhea_receipt.ArtifactCapture]:
    try:
        capture = rhea_receipt._capture_regular_file(
            path, label="Rhea saved execution plan", max_bytes=_PLAN_MAX_BYTES
        )
    except (OSError, rhea_receipt.RheaAcquisitionReceiptError) as error:
        raise RheaAcquisitionRunError(str(error)) from error
    try:
        text = capture.raw.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise RheaAcquisitionRunError("saved execution plan contains non-ASCII bytes") from error
    if not text.endswith("\n") or text.count("\n") != 1 or "\r" in text:
        raise RheaAcquisitionRunError(
            "saved execution plan must be one canonical LF-terminated JSON row"
        )
    try:
        value = json.loads(
            text[:-1],
            object_pairs_hook=rhea_receipt._unique_json_object,
            parse_constant=rhea_receipt._reject_json_constant,
        )
    except (ValueError, RecursionError, rhea_receipt.RheaAcquisitionReceiptError) as error:
        raise RheaAcquisitionRunError(f"saved execution plan is invalid JSON: {error}") from error
    if type(value) is not dict or render_execution_plan(value) != text:
        raise RheaAcquisitionRunError("saved execution plan is not exact canonical JSON")
    without_id = dict(value)
    observed = without_id.pop("plan_id", None)
    if observed != PLAN_ID_PREFIX + rhea_receipt.value_sha256(without_id):
        raise RheaAcquisitionRunError("saved execution plan content address is invalid")
    return value, capture


def _utc_second_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _header_projection(headers: Any, *, role: str) -> dict[str, str]:
    try:
        items = list(headers.items())
    except (AttributeError, TypeError, ValueError) as error:
        raise RheaAcquisitionRunError(f"{role} response headers are unavailable") from error
    projection: dict[str, str] = {}
    for raw_key, raw_value in items:
        if not isinstance(raw_key, str) or not isinstance(raw_value, str):
            raise RheaAcquisitionRunError(f"{role} response header is not text")
        key = raw_key.strip().lower()
        if key not in _ALLOWED_RESPONSE_HEADERS:
            continue
        value = raw_value.strip()
        if key in projection:
            raise RheaAcquisitionRunError(f"{role} response repeats projected header {key!r}")
        projection[key] = value
    if "date" not in projection:
        raise RheaAcquisitionRunError(f"{role} response lacks required HTTP Date")
    return dict(sorted(projection.items()))


def _read_bounded_response(response: ResponseLike, *, role: str, limit: int) -> bytes:
    chunks: list[bytes] = []
    captured = 0
    while True:
        try:
            chunk = response.read(min(_READ_CHUNK_BYTES, limit - captured + 1))
        except (OSError, ValueError) as error:
            raise RheaAcquisitionRunError(f"{role} response body read failed: {error}") from error
        if not isinstance(chunk, bytes):
            raise RheaAcquisitionRunError(f"{role} response body reader returned non-bytes")
        if not chunk:
            break
        chunks.append(chunk)
        captured += len(chunk)
        if captured > limit:
            raise RheaAcquisitionRunError(f"{role} response exceeds {limit} bytes")
    if captured < 1:
        raise RheaAcquisitionRunError(f"{role} response body is empty")
    return b"".join(chunks)


def _download_all(
    *,
    plan: Mapping[str, Any],
    opener: OpenUrl,
    clock: Clock,
    test_hook: TestHook | None,
) -> tuple[str, str, list[DownloadedResponse]]:
    timeout = plan["network"]["timeout_seconds"]
    started = clock()
    responses: list[DownloadedResponse] = []
    for role in rhea_receipt.SOURCE_ROLES:
        artifact = rhea_receipt.PLAN_ARTIFACTS[role]
        url = str(artifact["url"])
        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "Accept": "text/plain, text/tab-separated-values;q=0.9, */*;q=0.1",
                "Accept-Encoding": "identity",
                "User-Agent": "ProteinTraitsMech-Rhea-acquisition/1",
            },
        )
        try:
            with opener(request, timeout=timeout) as response:
                status = response.status
                final_url = response.geturl()
                headers = _header_projection(response.headers, role=role)
                raw = _read_bounded_response(
                    response,
                    role=role,
                    limit=plan["network"]["response_byte_limits"][role],
                )
        except RheaAcquisitionRunError:
            raise
        except (OSError, urllib.error.URLError, urllib.error.HTTPError) as error:
            raise RheaAcquisitionRunError(f"{role} HTTPS request failed: {error}") from error
        if type(status) is not int or status != 200:
            raise RheaAcquisitionRunError(f"{role} response status is not integer 200")
        if final_url != url:
            raise RheaAcquisitionRunError(f"{role} final response URL is not canonical")
        if "content-length" in headers and (
            not headers["content-length"].isdigit() or int(headers["content-length"]) != len(raw)
        ):
            raise RheaAcquisitionRunError(
                f"{role} Content-Length does not equal captured response bytes"
            )
        responses.append(
            DownloadedResponse(
                role=role,
                request_url=url,
                response_url=final_url,
                status=status,
                received_at_utc=clock(),
                header_projection=headers,
                raw=raw,
            )
        )
        if test_hook is not None:
            test_hook(f"RESPONSE_CAPTURED:{role}")
    completed = clock()
    return started, completed, responses


def _temporary_receipt(
    *,
    responses: Sequence[DownloadedResponse],
    started: str,
    completed: str,
    runner_projection: Mapping[str, Any],
    enforce_release_contract: bool,
) -> tuple[dict[str, Any], bytes]:
    by_role = {response.role: response for response in responses}
    if tuple(by_role) != rhea_receipt.SOURCE_ROLES:
        raise RheaAcquisitionRunError("downloaded responses do not cover exact Rhea role order")
    try:
        with tempfile.TemporaryDirectory(
            prefix=".ptm-rhea-acquisition-",
            dir=TEMP_ROOT,
        ) as temporary:
            root = Path(temporary)
            paths = _target_paths(root)
            paths.receipt.parent.mkdir(parents=True)
            for role, path in paths.source_paths().items():
                path.write_bytes(by_role[role].raw)
            value = rhea_receipt.build_receipt_value(
                paths=paths,
                acquisition_started_at_utc=started,
                acquisition_completed_at_utc=completed,
                response_attestations=[response.attestation() for response in responses],
                producer={
                    "implementation": (
                        "scripts/acquire_rhea_sources.py;"
                        "content-addressed-producer-attestation-only"
                    ),
                    "implementation_sha256": runner_projection["sha256"],
                },
                enforce_release_contract=enforce_release_contract,
            )
            raw = (rhea_receipt.canonical_json(value) + "\n").encode("ascii")
            paths.receipt.write_bytes(raw)
            verification = rhea_receipt.verify_receipt(
                paths=paths,
                enforce_release_contract=enforce_release_contract,
            )
            if (
                verification.get("status") != "PASS_RECEIPT_CONTENT_AND_SEMANTIC_BINDINGS_ONLY"
                or verification.get("central_grounding_eligible") is not False
            ):
                raise RheaAcquisitionRunError("temporary receipt verification was not fail-closed")
            return value, raw
    except RheaAcquisitionRunError:
        raise
    except (OSError, rhea_stage.RheaStageError, rhea_receipt.RheaAcquisitionReceiptError) as error:
        raise RheaAcquisitionRunError(f"downloaded Rhea bundle is invalid: {error}") from error


def _write_all(descriptor: int, raw: bytes) -> None:
    offset = 0
    while offset < len(raw):
        try:
            written = os.write(descriptor, raw[offset:])
        except OSError as error:
            raise RheaAcquisitionRunError(f"cannot write Rhea artifact: {error}") from error
        if written <= 0:
            raise RheaAcquisitionRunError("short write while creating Rhea artifact")
        offset += written


def _create_leaf(
    parent: BoundDirectory,
    *,
    name: str,
    raw: bytes,
    label: str,
) -> tuple[int, int]:
    parent.recheck()
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    descriptor: int | None = None
    try:
        descriptor = os.open(name, flags, 0o600, dir_fd=parent.descriptor)
        _write_all(descriptor, raw)
        os.fsync(descriptor)
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_nlink != 1
            or metadata.st_size != len(raw)
        ):
            raise RheaAcquisitionRunError(f"created {label} has invalid type/link/size")
        named = os.stat(name, dir_fd=parent.descriptor, follow_symlinks=False)
        if _entry_identity(named) != _entry_identity(metadata):
            raise RheaAcquisitionRunError(f"created {label} path does not bind its descriptor")
        os.fsync(parent.descriptor)
        parent.recheck()
        return metadata.st_dev, metadata.st_ino
    except RheaAcquisitionRunError:
        raise
    except OSError as error:
        raise RheaAcquisitionRunError(
            f"cannot create {label} without replacement: {error}"
        ) from error
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _assert_plan_parent(parent: BoundDirectory, plan: Mapping[str, Any]) -> None:
    expected = plan["output_binding"]["parent"]
    if str(parent.path) != expected["path"] or parent.identity != (
        expected["device"],
        expected["inode"],
        expected["mode_type"],
    ):
        raise RheaAcquisitionRunError("Rhea output parent does not match saved plan")
    parent.recheck()


def _capture_exact_sources(
    *, paths: rhea_receipt.ReceiptPaths, responses: Mapping[str, DownloadedResponse]
) -> None:
    identities: set[tuple[int, int]] = set()
    for role, path in paths.source_paths().items():
        try:
            capture = rhea_receipt._capture_regular_file(
                path,
                label=f"installed Rhea {role}",
                max_bytes=rhea_receipt._MAX_BYTES[role],
            )
        except (OSError, rhea_receipt.RheaAcquisitionReceiptError) as error:
            raise RheaAcquisitionRunError(str(error)) from error
        if capture.raw != responses[role].raw:
            raise RheaAcquisitionRunError(
                f"installed/pre-existing Rhea {role} bytes differ from HTTPS response"
            )
        identity = capture.device, capture.inode
        if identity in identities:
            raise RheaAcquisitionRunError("installed Rhea source files alias one another")
        identities.add(identity)


def _install_generation(
    *,
    paths: rhea_receipt.ReceiptPaths,
    plan: Mapping[str, Any],
    responses: Sequence[DownloadedResponse],
    receipt_raw: bytes,
    enforce_release_contract: bool,
    test_hook: TestHook | None,
) -> dict[str, Any]:
    response_by_role = {response.role: response for response in responses}
    parent_path = _assert_direct_targets(paths)
    with _open_bound_directory(parent_path) as parent:
        _assert_plan_parent(parent, plan)
        if _runner_projection() != plan["runner_artifact"]:
            raise RheaAcquisitionRunError("Rhea acquisition runner changed before installation")
        if _leaf_metadata(parent, paths.receipt.name) is not None:
            raise RheaAcquisitionRunError("Rhea receipt appeared before installation")

        # Validate the complete saved output state and every pre-existing body
        # before creating even the first missing source file.
        for role, path in paths.source_paths().items():
            planned = plan["output_binding"]["sources"][role]
            metadata = _leaf_metadata(parent, path.name)
            if planned["state"] == "ABSENT":
                if metadata is not None:
                    raise RheaAcquisitionRunError(f"Rhea {role} appeared after saved planning")
            elif planned["state"] == "PRESENT_BOUND_BYTES":
                if metadata is None:
                    raise RheaAcquisitionRunError(f"pre-existing Rhea {role} disappeared")
                try:
                    capture = rhea_receipt._capture_regular_file(
                        path,
                        label=f"pre-existing Rhea {role} install binding",
                        max_bytes=rhea_receipt._MAX_BYTES[role],
                    )
                except (OSError, rhea_receipt.RheaAcquisitionReceiptError) as error:
                    raise RheaAcquisitionRunError(str(error)) from error
                observed = {
                    "device": capture.device,
                    "inode": capture.inode,
                    "path": str(rhea_receipt.PLAN_ARTIFACTS[role]["target_path"]),
                    "sha256": capture.sha256,
                    "size_bytes": capture.size_bytes,
                    "state": "PRESENT_BOUND_BYTES",
                }
                if observed != planned:
                    raise RheaAcquisitionRunError(
                        f"pre-existing Rhea {role} no longer matches saved plan"
                    )
                if capture.raw != response_by_role[role].raw:
                    raise RheaAcquisitionRunError(
                        f"pre-existing Rhea {role} bytes differ from HTTPS response"
                    )
            else:  # pragma: no cover - exact saved/derived comparison guards this
                raise RheaAcquisitionRunError(f"unknown planned Rhea {role} state")

        for role, path in paths.source_paths().items():
            if plan["output_binding"]["sources"][role]["state"] != "ABSENT":
                continue
            _create_leaf(
                parent,
                name=path.name,
                raw=response_by_role[role].raw,
                label=f"Rhea {role}",
            )
            if test_hook is not None:
                test_hook(f"SOURCE_INSTALLED:{role}")

        if test_hook is not None:
            test_hook("SOURCES_READY_FOR_FINAL_RECHECK")
        _capture_exact_sources(paths=paths, responses=response_by_role)
        parent.recheck()
        _create_leaf(
            parent,
            name=paths.receipt.name,
            raw=receipt_raw,
            label="Rhea acquisition receipt",
        )
        if test_hook is not None:
            test_hook("RECEIPT_INSTALLED_LAST")

    try:
        verification = rhea_receipt.verify_receipt(
            paths=paths,
            enforce_release_contract=enforce_release_contract,
        )
    except (OSError, rhea_stage.RheaStageError, rhea_receipt.RheaAcquisitionReceiptError) as error:
        raise RheaAcquisitionRunError(
            f"installed Rhea receipt failed verification: {error}"
        ) from error
    if verification.get("central_grounding_eligible") is not False:
        raise RheaAcquisitionRunError("installed Rhea receipt unexpectedly claims grounding")
    return verification


def execute_saved_plan(
    *,
    execution_plan_path: Path,
    repo_root: Path = REPO_ROOT,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    enforce_release_contract: bool = True,
    opener: OpenUrl = urllib.request.urlopen,
    clock: Clock = _utc_second_now,
    test_hook: TestHook | None = None,
) -> dict[str, Any]:
    """Execute an exact saved plan, with all writes after complete validation."""

    supplied, plan_capture = _load_saved_plan(execution_plan_path)
    derived = derive_execution_plan(
        repo_root=repo_root,
        timeout_seconds=timeout_seconds,
        enforce_release_contract=enforce_release_contract,
    )
    if rhea_receipt.canonical_json(supplied) != rhea_receipt.canonical_json(derived):
        raise RheaAcquisitionRunError("saved execution plan does not match current inputs/options")
    if _lexical_absolute(execution_plan_path) in {
        *(_lexical_absolute(path) for path in _target_paths(repo_root).source_paths().values()),
        _lexical_absolute(_target_paths(repo_root).receipt),
    }:
        raise RheaAcquisitionRunError("saved execution plan collides with a Rhea output target")

    started, completed, responses = _download_all(
        plan=supplied,
        opener=opener,
        clock=clock,
        test_hook=test_hook,
    )
    receipt_value, receipt_raw = _temporary_receipt(
        responses=responses,
        started=started,
        completed=completed,
        runner_projection=supplied["runner_artifact"],
        enforce_release_contract=enforce_release_contract,
    )
    if test_hook is not None:
        test_hook("TEMPORARY_RECEIPT_VERIFIED")

    final_derived = derive_execution_plan(
        repo_root=repo_root,
        timeout_seconds=timeout_seconds,
        enforce_release_contract=enforce_release_contract,
    )
    if rhea_receipt.canonical_json(supplied) != rhea_receipt.canonical_json(final_derived):
        raise RheaAcquisitionRunError("Rhea inputs/output state changed after network capture")
    try:
        rhea_receipt._recheck_capture(
            plan_capture,
            label="Rhea saved execution plan final recheck",
            max_bytes=_PLAN_MAX_BYTES,
        )
    except (OSError, rhea_receipt.RheaAcquisitionReceiptError) as error:
        raise RheaAcquisitionRunError(str(error)) from error
    verification = _install_generation(
        paths=_target_paths(repo_root),
        plan=supplied,
        responses=responses,
        receipt_raw=receipt_raw,
        enforce_release_contract=enforce_release_contract,
        test_hook=test_hook,
    )
    return {
        "artifact_kind": RUN_RESULT_KIND,
        "central_grounding_eligible": False,
        "network_action_performed": True,
        "producer_authenticated": False,
        "provider": "Rhea",
        "provider_release": rhea_stage.EXPECTED_RHEA_RELEASE,
        "receipt_id": receipt_value["receipt_id"],
        "receipt_installed_last": True,
        "response_count": len(responses),
        "status": "COMPLETE_PRODUCER_ATTESTATION_INSTALLED_NOT_GROUNDING_ELIGIBLE",
        "verification_status": verification["status"],
        "writes_performed": True,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--execution-plan",
        type=Path,
        help="exact saved canonical dry plan; required with --apply",
    )
    parser.add_argument("--apply", action="store_true", help="perform HTTPS and install receipt")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if not args.apply:
            if args.execution_plan is not None:
                raise RheaAcquisitionRunError("--execution-plan is supplied only with --apply")
            plan = derive_execution_plan(
                repo_root=REPO_ROOT,
                timeout_seconds=args.timeout_seconds,
                enforce_release_contract=True,
            )
            sys.stdout.write(render_execution_plan(plan))
            return 0
        if args.execution_plan is None:
            raise RheaAcquisitionRunError("--apply requires an exact saved --execution-plan")
        result = execute_saved_plan(
            execution_plan_path=args.execution_plan,
            repo_root=REPO_ROOT,
            timeout_seconds=args.timeout_seconds,
            enforce_release_contract=True,
        )
        sys.stdout.write(rhea_receipt.canonical_json(result) + "\n")
        return 0
    except (
        OSError,
        RheaAcquisitionRunError,
        rhea_stage.RheaStageError,
        rhea_receipt.RheaAcquisitionReceiptError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
