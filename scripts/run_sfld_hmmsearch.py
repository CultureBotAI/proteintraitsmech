#!/usr/bin/env python3
"""Plan and execute one receipt-bound SFLD ``hmmsearch --cut_ga`` selection.

The default mode is a no-persistent-write, no-execution dry plan printed as one
canonical JSON row.  Execution requires both ``--apply`` and the exact saved
``--execution-plan``.  Apply writes only into a brand-new staging directory,
never replaces an existing path, captures ``hmmsearch -h`` and one complete
search, and installs the selected-domain receipt last.

This runner does not write trait records or durable grounding.  A completed
receipt remains non-grounding until the independent provider, migration,
qualified-record, and review gates named by the receipt are satisfied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from sfld_match import SfldMatchError
from sfld_release import SfldReleaseError
from validate_sfld_hmmsearch_receipt import (
    DEFAULT_HIERARCHY,
    DEFAULT_HMM,
    DEFAULT_REGISTRY,
    DEFAULT_SITES,
    EMPTY_SHA256,
    ReceiptPaths,
    SFLD_4_HIERARCHY_SHA256,
    SFLD_4_HMM_SHA256,
    SFLD_4_SITES_SHA256,
    SUPPORTED_HMMER_VERSION,
    SfldHmmsearchReceiptError,
    _absolute_lexical,
    _capture_regular_file,
    _exact_lf_text,
    _hmmer_version,
    _load_registry,
    _load_release_from_captures,
    _MAX_BYTES,
    _reject_json_constant,
    _unique_json_object,
    build_receipt_value,
    canonical_json,
    canonical_registry_fasta,
    parse_domtblout,
    value_sha256,
    verify_receipt,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_ROOT = REPO_ROOT / "reports"
TEMP_ROOT = Path(tempfile.gettempdir()).resolve()

PLAN_SCHEMA_VERSION = 1
PLAN_KIND = "SFLD_HMMSEARCH_CUT_GA_EXECUTION_PLAN"
PLAN_ID_PREFIX = "sfld-hmmsearch-execution-plan:"
RUN_RESULT_KIND = "SFLD_HMMSEARCH_CONTROLLED_RUN_RESULT"
STARTED_KIND = "SFLD_HMMSEARCH_CONTROLLED_RUN_STARTED"

_PLAN_MAX_BYTES = 8 * 1024 * 1024
_RUNNER_MAX_BYTES = 8 * 1024 * 1024
_DEFAULT_TIMEOUT_SECONDS = 6 * 60 * 60
_FIXED_OUTPUT_NAMES = {
    "started": "run.started.json",
    "execution_plan": "execution-plan.json",
    "executable": "hmmsearch",
    "hmm": "sfld.hmm",
    "hierarchy": "sfld_hierarchy_flat.txt",
    "sites": "sfld_sites.annot",
    "registry": "protein_registry.jsonl",
    "runner": "run_sfld_hmmsearch.py",
    "fasta": "targets.fasta",
    "version_stdout": "hmmsearch-version.stdout",
    "version_stderr": "hmmsearch-version.stderr",
    "main_output": "hmmsearch.stdout",
    "stderr_output": "hmmsearch.stderr",
    "alignment_output": "hits.sto",
    "domtblout": "hits.domtblout",
    "receipt_candidate": "selected-domain.receipt.candidate.json",
    "receipt": "selected-domain.receipt.json",
}
_SOURCE_ROLES = ("executable", "hmm", "hierarchy", "sites", "registry", "runner")


class SfldHmmsearchRunError(RuntimeError):
    """A controlled-run plan or execution failed closed."""


@dataclass(frozen=True, slots=True)
class SourcePaths:
    executable: Path
    hmm: Path
    hierarchy: Path
    sites: Path
    registry: Path
    runner: Path

    def as_dict(self) -> dict[str, Path]:
        return {role: getattr(self, role) for role in _SOURCE_ROLES}


@dataclass(slots=True)
class BoundDirectory:
    """A component-relative no-follow directory binding held by descriptors."""

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
                raise SfldHmmsearchRunError(
                    f"directory path component changed: {component!r}: {error}"
                ) from error
            observed = live.st_dev, live.st_ino, stat.S_IFMT(live.st_mode)
            if observed != expected:
                raise SfldHmmsearchRunError(f"directory path component changed: {component!r}")

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


def _entry_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)


def _open_bound_directory(path: Path, *, label: str) -> BoundDirectory:
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
        raise SfldHmmsearchRunError(
            f"{label}: platform lacks descriptor-relative no-follow support"
        )
    lexical = _absolute_lexical(path)
    components = lexical.parts[1:]
    if not components or any(component in {"", ".", ".."} for component in components):
        raise SfldHmmsearchRunError(f"{label}: unsafe directory path {path}")

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
        bound = BoundDirectory(path=lexical, descriptors=descriptors, bindings=bindings)
        bound.recheck()
        return bound
    except OSError as error:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise SfldHmmsearchRunError(
            f"{label}: cannot safely bind directory {path}: {error}"
        ) from error
    except Exception:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise


def _path_is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _validate_staging_output_path(output_dir: Path) -> tuple[Path, Path, str]:
    lexical = _absolute_lexical(output_dir)
    leaf = lexical.name
    if not leaf or leaf in {".", ".."}:
        raise SfldHmmsearchRunError("output directory must have a safe leaf name")
    try:
        resolved_parent = lexical.parent.resolve(strict=True)
    except OSError as error:
        raise SfldHmmsearchRunError(f"output parent does not exist: {lexical.parent}") from error
    allowed_reports = REPORTS_ROOT.resolve(strict=True)
    if not (
        _path_is_within(resolved_parent, allowed_reports)
        or _path_is_within(resolved_parent, TEMP_ROOT)
    ):
        raise SfldHmmsearchRunError(
            "output directory must be beneath reports/ or the system temporary directory"
        )
    return lexical, lexical.parent, leaf


def _assert_leaf_absent(parent: BoundDirectory, leaf: str) -> None:
    try:
        metadata = os.stat(leaf, dir_fd=parent.descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return
    except OSError as error:
        raise SfldHmmsearchRunError(
            f"cannot inspect output directory leaf {leaf!r}: {error}"
        ) from error
    kind = stat.S_IFMT(metadata.st_mode)
    raise SfldHmmsearchRunError(
        f"output directory already exists or is occupied: {parent.path / leaf} (mode {kind:o})"
    )


def _projection(capture: Any, *, include_mode: bool = False) -> dict[str, Any]:
    value = {
        "path": str(capture.path),
        "sha256": capture.sha256,
        "size_bytes": capture.size_bytes,
    }
    if include_mode:
        value["mode_bits"] = capture.mode_bits
    return value


def _validate_sha256(value: str, *, label: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise SfldHmmsearchRunError(f"{label} must be one lowercase SHA-256 digest")


def _capture_sources(paths: SourcePaths) -> dict[str, Any]:
    limits = {
        "executable": _MAX_BYTES["executable"],
        "hmm": _MAX_BYTES["hmm"],
        "hierarchy": _MAX_BYTES["hierarchy"],
        "sites": _MAX_BYTES["sites"],
        "registry": _MAX_BYTES["registry"],
        "runner": _RUNNER_MAX_BYTES,
    }
    captures = {
        role: _capture_regular_file(path, label=role, max_bytes=limits[role])
        for role, path in paths.as_dict().items()
    }
    lexical = [str(capture.path) for capture in captures.values()]
    if len(set(lexical)) != len(lexical):
        raise SfldHmmsearchRunError("source paths must be pairwise distinct")
    inodes = [(capture.device, capture.inode) for capture in captures.values()]
    if len(set(inodes)) != len(inodes):
        raise SfldHmmsearchRunError("source files must not be hard-link aliases")
    if captures["executable"].mode_bits & 0o111 == 0:
        raise SfldHmmsearchRunError("hmmsearch executable has no execute permission bit")
    return captures


def _output_paths(output_dir: Path) -> dict[str, Path]:
    return {role: output_dir / name for role, name in _FIXED_OUTPUT_NAMES.items()}


def derive_execution_plan(
    *,
    paths: SourcePaths,
    output_dir: Path,
    model_accession: str,
    target_protein_id: str,
    domain_number: int,
    timeout_seconds: int,
    approved_executable_sha256: str,
    expected_hmm_sha256: str = SFLD_4_HMM_SHA256,
    expected_hierarchy_sha256: str = SFLD_4_HIERARCHY_SHA256,
    expected_sites_sha256: str = SFLD_4_SITES_SHA256,
    enforce_release_contract: bool = True,
) -> dict[str, Any]:
    """Derive the exact no-execution plan from current immutable inputs."""

    if type(domain_number) is not int or domain_number < 1:
        raise SfldHmmsearchRunError("domain number must be a positive integer")
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 24 * 60 * 60:
        raise SfldHmmsearchRunError("timeout seconds must be in 1..86400")
    if not isinstance(model_accession, str) or not model_accession:
        raise SfldHmmsearchRunError("model accession must be a nonempty string")
    if not isinstance(target_protein_id, str) or not target_protein_id:
        raise SfldHmmsearchRunError("target protein identifier must be a nonempty string")
    _validate_sha256(
        approved_executable_sha256,
        label="approved executable SHA-256",
    )

    lexical_output, output_parent, output_leaf = _validate_staging_output_path(output_dir)
    captures = _capture_sources(paths)
    if captures["executable"].sha256 != approved_executable_sha256:
        raise SfldHmmsearchRunError(
            "hmmsearch executable does not match the explicitly approved SHA-256"
        )
    try:
        registry_rows = _load_registry(captures["registry"])
        release = _load_release_from_captures(
            captures,
            expected_hmm_sha256=expected_hmm_sha256,
            expected_hierarchy_sha256=expected_hierarchy_sha256,
            expected_sites_sha256=expected_sites_sha256,
            enforce_release_contract=enforce_release_contract,
        )
    except (SfldHmmsearchReceiptError, SfldReleaseError) as error:
        raise SfldHmmsearchRunError(f"source preflight failed: {error}") from error
    model = release.models.get(model_accession)
    if model is None:
        raise SfldHmmsearchRunError(f"selected model is absent from pinned SFLD: {model_accession}")
    registry_by_id = {row["protein_id"]: row for row in registry_rows}
    target = registry_by_id.get(target_protein_id)
    if target is None:
        raise SfldHmmsearchRunError(
            f"selected target is absent from the canonical registry: {target_protein_id}"
        )
    fasta = canonical_registry_fasta(registry_rows)
    outputs = _output_paths(lexical_output)

    with _open_bound_directory(output_parent, label="output parent") as parent:
        _assert_leaf_absent(parent, output_leaf)
        parent_identity = parent.identity
        parent.recheck()

    source_projection = {
        role: _projection(
            capture,
            include_mode=role in {"executable", "runner"},
        )
        for role, capture in captures.items()
    }
    plan: dict[str, Any] = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "plan_kind": PLAN_KIND,
        "inputs": source_projection,
        "source_binding": {
            "executable_policy": {
                "approval_basis": "OPERATOR_SUPPLIED_EXACT_SHA256",
                "approved_sha256": approved_executable_sha256,
                "approval_is_not_producer_authentication": True,
            },
            "hmmer_required_version": SUPPORTED_HMMER_VERSION,
            "model_count": len(release.models),
            "source_release": release.release,
        },
        "target_registry_projection": {
            "canonical_fasta_sha256": hashlib.sha256(fasta).hexdigest(),
            "canonical_fasta_size_bytes": len(fasta),
            "protein_count": len(registry_rows),
            "uniprot_release": registry_rows[0]["uniprot_release"],
        },
        "selector": {
            "domain_number": domain_number,
            "model_accession": model_accession,
            "model_name": model.name,
            "target_protein_id": target_protein_id,
            "target_sequence_sha256": target["sequence_sha256"],
        },
        "execution": {
            "argv": [
                str(outputs["executable"]),
                "--cut_ga",
                "--cpu",
                "0",
                "--seed",
                "42",
                "--tformat",
                "fasta",
                "-A",
                str(outputs["alignment_output"]),
                "--domtblout",
                str(outputs["domtblout"]),
                str(outputs["hmm"]),
                str(outputs["fasta"]),
            ],
            "environment": {"LC_ALL": "C"},
            "stdin_sha256": EMPTY_SHA256,
            "timeout_seconds": timeout_seconds,
            "version_argv": [str(outputs["executable"]), "-h"],
            "version_capability_status": "NOT_EXECUTED_DRY_PLAN_REQUIRES_APPLY_PREFLIGHT",
            "working_directory": str(lexical_output),
        },
        "output_binding": {
            "directory": str(lexical_output),
            "directory_must_be_absent": True,
            "files": {role: str(path) for role, path in outputs.items()},
            "parent": {
                "device": parent_identity[0],
                "inode": parent_identity[1],
                "mode_type": parent_identity[2],
                "path": str(_absolute_lexical(output_parent)),
            },
            "replacement_policy": "CREATE_NEW_DIRECTORY_AND_FILES_ONLY",
        },
        "safety_boundary": {
            "apply_requires_exact_saved_plan": True,
            "durable_grounding_writes_authorized": False,
            "network_action_planned": False,
            "receipt_installed_last": True,
            "trait_writes_authorized": False,
        },
    }
    plan["plan_id"] = PLAN_ID_PREFIX + value_sha256(plan)
    return plan


def _load_saved_plan(path: Path) -> dict[str, Any]:
    capture = _capture_regular_file(path, label="execution plan", max_bytes=_PLAN_MAX_BYTES)
    text = _exact_lf_text(capture.raw, label="execution plan")
    if text.count("\n") != 1:
        raise SfldHmmsearchRunError("execution plan must be one canonical JSON row")
    try:
        value = json.loads(
            text[:-1],
            object_pairs_hook=_unique_json_object,
            parse_constant=_reject_json_constant,
        )
    except (ValueError, RecursionError, SfldHmmsearchReceiptError) as error:
        raise SfldHmmsearchRunError(f"execution plan is invalid JSON: {error}") from error
    if type(value) is not dict:
        raise SfldHmmsearchRunError("execution plan is not a JSON object")
    try:
        canonical = canonical_json(value)
    except (TypeError, ValueError, RecursionError) as error:
        raise SfldHmmsearchRunError(f"execution plan cannot be canonicalized: {error}") from error
    if canonical + "\n" != text:
        raise SfldHmmsearchRunError("execution plan is not exact canonical JSON")
    expected_fields = {
        "execution",
        "inputs",
        "output_binding",
        "plan_id",
        "plan_kind",
        "safety_boundary",
        "schema_version",
        "selector",
        "source_binding",
        "target_registry_projection",
    }
    if set(value) != expected_fields:
        raise SfldHmmsearchRunError("execution plan does not have the exact v1 field set")
    if value.get("schema_version") != PLAN_SCHEMA_VERSION or value.get("plan_kind") != PLAN_KIND:
        raise SfldHmmsearchRunError("execution plan version or kind is invalid")
    payload = dict(value)
    supplied_id = payload.pop("plan_id", None)
    expected_id = PLAN_ID_PREFIX + value_sha256(payload)
    if supplied_id != expected_id:
        raise SfldHmmsearchRunError("execution plan content address is invalid")
    return value


def _write_all(descriptor: int, raw: bytes) -> None:
    offset = 0
    while offset < len(raw):
        written = os.write(descriptor, raw[offset:])
        if written <= 0:
            raise SfldHmmsearchRunError("short write while creating run artifact")
        offset += written


def _create_file(
    directory_descriptor: int,
    name: str,
    *,
    raw: bytes = b"",
    mode: int = 0o600,
) -> tuple[int, int]:
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    try:
        descriptor = os.open(name, flags, mode, dir_fd=directory_descriptor)
        metadata = os.fstat(descriptor)
        _write_all(descriptor, raw)
        os.fsync(descriptor)
        return metadata.st_dev, metadata.st_ino
    except OSError as error:
        raise SfldHmmsearchRunError(f"cannot create run artifact {name!r}: {error}") from error
    finally:
        if "descriptor" in locals():
            os.close(descriptor)


def _open_capture_output(directory_descriptor: int, name: str) -> int:
    flags = os.O_WRONLY | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        return os.open(name, flags, dir_fd=directory_descriptor)
    except OSError as error:
        raise SfldHmmsearchRunError(f"cannot open run capture {name!r}: {error}") from error


def _run_process(
    argv: list[str],
    *,
    working_directory: Path,
    stdout_descriptor: int,
    stderr_descriptor: int,
    timeout_seconds: int,
) -> int:
    try:
        completed = subprocess.run(
            argv,
            check=False,
            close_fds=True,
            cwd=working_directory,
            env={"LC_ALL": "C"},
            stdin=subprocess.DEVNULL,
            stdout=stdout_descriptor,
            stderr=stderr_descriptor,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise SfldHmmsearchRunError(f"controlled process failed to complete: {error}") from error
    return completed.returncode


def _validate_version_preflight(stdout_path: Path, stderr_path: Path) -> None:
    stdout_capture = _capture_regular_file(
        stdout_path,
        label="controlled-run version stdout",
        max_bytes=_MAX_BYTES["version_stdout"],
    )
    stderr_capture = _capture_regular_file(
        stderr_path,
        label="controlled-run version stderr",
        max_bytes=_MAX_BYTES["version_stderr"],
        allow_empty=True,
    )
    stdout = _exact_lf_text(stdout_capture.raw, label="controlled-run version stdout")
    stderr = _exact_lf_text(
        stderr_capture.raw,
        label="controlled-run version stderr",
        allow_empty=True,
    )
    version = _hmmer_version(stdout, label="controlled-run version stdout")
    if version != SUPPORTED_HMMER_VERSION:
        raise SfldHmmsearchRunError(
            f"unsupported HMMER version {version!r}; required {SUPPORTED_HMMER_VERSION}"
        )
    if (
        "Usage:" not in stdout
        or "--cut_ga" not in stdout
        or "--cpu" not in stdout
        or "--seed" not in stdout
        or "--tformat" not in stdout
    ):
        raise SfldHmmsearchRunError("hmmsearch -h did not advertise the exact required capability")
    if stderr:
        raise SfldHmmsearchRunError("successful hmmsearch -h wrote unexpected stderr")


def _assert_file_identity(
    directory_descriptor: int,
    name: str,
    expected: tuple[int, int],
) -> None:
    try:
        metadata = os.stat(name, dir_fd=directory_descriptor, follow_symlinks=False)
    except OSError as error:
        raise SfldHmmsearchRunError(f"run artifact disappeared: {name}: {error}") from error
    if not stat.S_ISREG(metadata.st_mode) or (metadata.st_dev, metadata.st_ino) != expected:
        raise SfldHmmsearchRunError(f"run artifact identity changed: {name}")


def _fsync_existing_file(directory_descriptor: int, name: str) -> None:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(name, flags, dir_fd=directory_descriptor)
        os.fsync(descriptor)
    except OSError as error:
        raise SfldHmmsearchRunError(f"cannot fsync run artifact {name!r}: {error}") from error
    finally:
        if "descriptor" in locals():
            os.close(descriptor)


def _install_verified_receipt(
    directory_descriptor: int,
    *,
    candidate_name: str,
    final_name: str,
) -> None:
    """Install without overwrite after candidate-path verification."""

    try:
        os.link(
            candidate_name,
            final_name,
            src_dir_fd=directory_descriptor,
            dst_dir_fd=directory_descriptor,
            follow_symlinks=False,
        )
        os.fsync(directory_descriptor)
        os.unlink(candidate_name, dir_fd=directory_descriptor)
        os.fsync(directory_descriptor)
    except OSError as error:
        raise SfldHmmsearchRunError(f"cannot install verified receipt last: {error}") from error


def _selected_line_number(domtblout_path: Path, selector: Mapping[str, Any]) -> int:
    capture = _capture_regular_file(
        domtblout_path,
        label="controlled-run domtblout",
        max_bytes=_MAX_BYTES["domtblout"],
    )
    text = _exact_lf_text(capture.raw, label="controlled-run domtblout")
    rows = parse_domtblout(text)
    matches = [
        row.line_number
        for row in rows.values()
        if row.query_accession == selector["model_accession"]
        and row.target_name == selector["target_protein_id"]
        and row.domain_number == selector["domain_number"]
    ]
    if len(matches) != 1:
        raise SfldHmmsearchRunError(
            "controlled search emitted "
            f"{len(matches)} rows for the exact model/target/domain selector; expected 1"
        )
    return matches[0]


def _utc_second_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def execute_saved_plan(
    *,
    execution_plan_path: Path,
    paths: SourcePaths,
    output_dir: Path,
    model_accession: str,
    target_protein_id: str,
    domain_number: int,
    timeout_seconds: int,
    approved_executable_sha256: str,
    expected_hmm_sha256: str = SFLD_4_HMM_SHA256,
    expected_hierarchy_sha256: str = SFLD_4_HIERARCHY_SHA256,
    expected_sites_sha256: str = SFLD_4_SITES_SHA256,
    enforce_release_contract: bool = True,
    captured_at_utc: str | None = None,
) -> dict[str, Any]:
    """Execute only an exact saved plan and install its verified receipt last."""

    supplied = _load_saved_plan(execution_plan_path)
    derived = derive_execution_plan(
        paths=paths,
        output_dir=output_dir,
        model_accession=model_accession,
        target_protein_id=target_protein_id,
        domain_number=domain_number,
        timeout_seconds=timeout_seconds,
        approved_executable_sha256=approved_executable_sha256,
        expected_hmm_sha256=expected_hmm_sha256,
        expected_hierarchy_sha256=expected_hierarchy_sha256,
        expected_sites_sha256=expected_sites_sha256,
        enforce_release_contract=enforce_release_contract,
    )
    if canonical_json(supplied) != canonical_json(derived):
        raise SfldHmmsearchRunError(
            "saved execution plan does not match current inputs and options"
        )

    source_captures = _capture_sources(paths)
    current_source_projection = {
        role: _projection(
            capture,
            include_mode=role in {"executable", "runner"},
        )
        for role, capture in source_captures.items()
    }
    if current_source_projection != supplied["inputs"]:
        raise SfldHmmsearchRunError("source inputs changed after saved-plan replay")
    fasta_rows = _load_registry(source_captures["registry"])
    fasta = canonical_registry_fasta(fasta_rows)
    if (
        hashlib.sha256(fasta).hexdigest()
        != supplied["target_registry_projection"]["canonical_fasta_sha256"]
        or len(fasta) != supplied["target_registry_projection"]["canonical_fasta_size_bytes"]
    ):
        raise SfldHmmsearchRunError("canonical FASTA projection changed after saved-plan replay")

    lexical_output, output_parent, output_leaf = _validate_staging_output_path(output_dir)
    outputs = _output_paths(lexical_output)
    with _open_bound_directory(output_parent, label="output parent apply") as parent:
        expected_parent = supplied["output_binding"]["parent"]
        if str(parent.path) != expected_parent["path"] or parent.identity != (
            expected_parent["device"],
            expected_parent["inode"],
            expected_parent["mode_type"],
        ):
            raise SfldHmmsearchRunError("output parent no longer matches the saved plan")
        _assert_leaf_absent(parent, output_leaf)
        try:
            os.mkdir(output_leaf, mode=0o700, dir_fd=parent.descriptor)
            generation_descriptor = os.open(
                output_leaf,
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY")
                | getattr(os, "O_NOFOLLOW")
                | getattr(os, "O_CLOEXEC", 0),
                dir_fd=parent.descriptor,
            )
        except OSError as error:
            raise SfldHmmsearchRunError(
                f"cannot create new run directory {lexical_output}: {error}"
            ) from error
        try:
            generation_metadata = os.fstat(generation_descriptor)
            generation_identity = generation_metadata.st_dev, generation_metadata.st_ino
            parent.recheck()
            live_generation = os.stat(
                output_leaf,
                dir_fd=parent.descriptor,
                follow_symlinks=False,
            )
            if (
                not stat.S_ISDIR(live_generation.st_mode)
                or (live_generation.st_dev, live_generation.st_ino) != generation_identity
            ):
                raise SfldHmmsearchRunError("new run directory identity changed after creation")

            started = {
                "schema_version": 1,
                "artifact_kind": STARTED_KIND,
                "completion_status": "RUN_STARTED_RECEIPT_ABSENT",
                "execution_plan_id": supplied["plan_id"],
            }
            started_raw = (canonical_json(started) + "\n").encode("ascii")
            started_identity = _create_file(
                generation_descriptor,
                _FIXED_OUTPUT_NAMES["started"],
                raw=started_raw,
            )
            saved_plan_raw = (canonical_json(supplied) + "\n").encode("ascii")
            saved_plan_identity = _create_file(
                generation_descriptor,
                _FIXED_OUTPUT_NAMES["execution_plan"],
                raw=saved_plan_raw,
            )
            copied_source_identities = {
                role: _create_file(
                    generation_descriptor,
                    _FIXED_OUTPUT_NAMES[role],
                    raw=source_captures[role].raw,
                    mode=0o700 if role == "executable" else 0o600,
                )
                for role in _SOURCE_ROLES
            }
            fasta_identity = _create_file(
                generation_descriptor,
                _FIXED_OUTPUT_NAMES["fasta"],
                raw=fasta,
            )
            empty_roles = (
                "version_stdout",
                "version_stderr",
                "main_output",
                "stderr_output",
                "alignment_output",
                "domtblout",
            )
            output_identities = (
                {
                    "started": started_identity,
                    "execution_plan": saved_plan_identity,
                }
                | copied_source_identities
                | {
                    "fasta": fasta_identity,
                }
                | {
                    role: _create_file(generation_descriptor, _FIXED_OUTPUT_NAMES[role])
                    for role in empty_roles
                }
            )
            os.fsync(generation_descriptor)

            version_stdout = _open_capture_output(
                generation_descriptor, _FIXED_OUTPUT_NAMES["version_stdout"]
            )
            version_stderr = _open_capture_output(
                generation_descriptor, _FIXED_OUTPUT_NAMES["version_stderr"]
            )
            try:
                version_exit = _run_process(
                    list(supplied["execution"]["version_argv"]),
                    working_directory=lexical_output,
                    stdout_descriptor=version_stdout,
                    stderr_descriptor=version_stderr,
                    timeout_seconds=timeout_seconds,
                )
            finally:
                os.close(version_stdout)
                os.close(version_stderr)
            if version_exit != 0:
                raise SfldHmmsearchRunError(f"hmmsearch -h exited {version_exit}; receipt absent")
            _validate_version_preflight(
                outputs["version_stdout"],
                outputs["version_stderr"],
            )

            main_stdout = _open_capture_output(
                generation_descriptor, _FIXED_OUTPUT_NAMES["main_output"]
            )
            main_stderr = _open_capture_output(
                generation_descriptor, _FIXED_OUTPUT_NAMES["stderr_output"]
            )
            try:
                search_exit = _run_process(
                    list(supplied["execution"]["argv"]),
                    working_directory=lexical_output,
                    stdout_descriptor=main_stdout,
                    stderr_descriptor=main_stderr,
                    timeout_seconds=timeout_seconds,
                )
            finally:
                os.close(main_stdout)
                os.close(main_stderr)
            if search_exit != 0:
                raise SfldHmmsearchRunError(f"hmmsearch exited {search_exit}; receipt absent")

            for role, identity in output_identities.items():
                _assert_file_identity(
                    generation_descriptor,
                    _FIXED_OUTPUT_NAMES[role],
                    identity,
                )
                _fsync_existing_file(generation_descriptor, _FIXED_OUTPUT_NAMES[role])
            os.fsync(generation_descriptor)

            for role in _SOURCE_ROLES:
                copied = _capture_regular_file(
                    outputs[role],
                    label=f"controlled-run copied {role}",
                    max_bytes=(
                        _RUNNER_MAX_BYTES
                        if role == "runner"
                        else _MAX_BYTES.get(role, _PLAN_MAX_BYTES)
                    ),
                )
                expected = supplied["inputs"][role]
                if (
                    copied.sha256 != expected["sha256"]
                    or copied.size_bytes != expected["size_bytes"]
                ):
                    raise SfldHmmsearchRunError(
                        f"controlled process changed copied source artifact {role}"
                    )
            copied_fasta = _capture_regular_file(
                outputs["fasta"],
                label="controlled-run copied FASTA",
                max_bytes=_MAX_BYTES["fasta"],
            )
            if (
                copied_fasta.sha256
                != supplied["target_registry_projection"]["canonical_fasta_sha256"]
                or copied_fasta.size_bytes
                != supplied["target_registry_projection"]["canonical_fasta_size_bytes"]
            ):
                raise SfldHmmsearchRunError("controlled process changed the canonical FASTA")
            copied_started = _capture_regular_file(
                outputs["started"],
                label="controlled-run started marker",
                max_bytes=_PLAN_MAX_BYTES,
            )
            if copied_started.raw != started_raw:
                raise SfldHmmsearchRunError("controlled process changed the run-started marker")
            copied_plan = _capture_regular_file(
                outputs["execution_plan"],
                label="controlled-run saved execution plan",
                max_bytes=_PLAN_MAX_BYTES,
            )
            if copied_plan.raw != saved_plan_raw:
                raise SfldHmmsearchRunError("controlled process changed the saved execution plan")

            line_number = _selected_line_number(outputs["domtblout"], supplied["selector"])
            receipt_paths = ReceiptPaths(
                receipt=outputs["receipt_candidate"],
                executable=outputs["executable"],
                version_stdout=outputs["version_stdout"],
                version_stderr=outputs["version_stderr"],
                hmm=outputs["hmm"],
                hierarchy=outputs["hierarchy"],
                sites=outputs["sites"],
                registry=outputs["registry"],
                fasta=outputs["fasta"],
                main_output=outputs["main_output"],
                stderr_output=outputs["stderr_output"],
                alignment_output=outputs["alignment_output"],
                domtblout=outputs["domtblout"],
            )
            timestamp = captured_at_utc if captured_at_utc is not None else _utc_second_now()
            runner_capture = _capture_regular_file(
                outputs["runner"],
                label="runner final binding",
                max_bytes=_RUNNER_MAX_BYTES,
            )
            expected_runner = supplied["inputs"]["runner"]
            if (
                runner_capture.sha256 != expected_runner["sha256"]
                or runner_capture.size_bytes != expected_runner["size_bytes"]
            ):
                raise SfldHmmsearchRunError("runner implementation changed after planning")
            receipt_value = build_receipt_value(
                paths=receipt_paths,
                selected_domtblout_line_number=line_number,
                captured_at_utc=timestamp,
                producer={
                    "implementation": str(runner_capture.path),
                    "implementation_sha256": runner_capture.sha256,
                },
                expected_hmm_sha256=expected_hmm_sha256,
                expected_hierarchy_sha256=expected_hierarchy_sha256,
                expected_sites_sha256=expected_sites_sha256,
                enforce_release_contract=enforce_release_contract,
            )
            parent.recheck()
            live_generation = os.stat(
                output_leaf,
                dir_fd=parent.descriptor,
                follow_symlinks=False,
            )
            if (live_generation.st_dev, live_generation.st_ino) != generation_identity:
                raise SfldHmmsearchRunError("run directory changed before receipt installation")
            _create_file(
                generation_descriptor,
                _FIXED_OUTPUT_NAMES["receipt_candidate"],
                raw=(canonical_json(receipt_value) + "\n").encode("ascii"),
            )
            os.fsync(generation_descriptor)
            verify_receipt(
                paths=receipt_paths,
                expected_hmm_sha256=expected_hmm_sha256,
                expected_hierarchy_sha256=expected_hierarchy_sha256,
                expected_sites_sha256=expected_sites_sha256,
                enforce_release_contract=enforce_release_contract,
            )
            _install_verified_receipt(
                generation_descriptor,
                candidate_name=_FIXED_OUTPUT_NAMES["receipt_candidate"],
                final_name=_FIXED_OUTPUT_NAMES["receipt"],
            )
            receipt_paths = replace(receipt_paths, receipt=outputs["receipt"])
            verification = verify_receipt(
                paths=receipt_paths,
                expected_hmm_sha256=expected_hmm_sha256,
                expected_hierarchy_sha256=expected_hierarchy_sha256,
                expected_sites_sha256=expected_sites_sha256,
                enforce_release_contract=enforce_release_contract,
            )
        finally:
            os.close(generation_descriptor)

    return {
        "schema_version": 1,
        "artifact_kind": RUN_RESULT_KIND,
        "execution_plan_id": supplied["plan_id"],
        "grounding_eligible": False,
        "hmmer_executable_build_or_acquisition_receipt_verified": False,
        "output_directory": str(lexical_output),
        "receipt_installed_last": True,
        "receipt_verification": verification,
        "status": "PASS_CONTROLLED_RUN_AND_RECEIPT_CONTENT_SEMANTIC_REPLAY",
        "trait_or_durable_grounding_writes_performed": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--hmm", type=Path, default=DEFAULT_HMM)
    parser.add_argument("--hierarchy", type=Path, default=DEFAULT_HIERARCHY)
    parser.add_argument("--sites", type=Path, default=DEFAULT_SITES)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-accession", required=True)
    parser.add_argument("--target-protein-id", required=True)
    parser.add_argument("--domain-number", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=int, default=_DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--approved-executable-sha256", required=True)
    parser.add_argument("--execution-plan", type=Path)
    parser.add_argument("--apply", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    paths = SourcePaths(
        executable=args.executable,
        hmm=args.hmm,
        hierarchy=args.hierarchy,
        sites=args.sites,
        registry=args.registry,
        runner=Path(__file__),
    )
    try:
        if args.apply:
            if args.execution_plan is None:
                raise SfldHmmsearchRunError("--apply requires --execution-plan")
            result = execute_saved_plan(
                execution_plan_path=args.execution_plan,
                paths=paths,
                output_dir=args.output_dir,
                model_accession=args.model_accession,
                target_protein_id=args.target_protein_id,
                domain_number=args.domain_number,
                timeout_seconds=args.timeout_seconds,
                approved_executable_sha256=args.approved_executable_sha256,
            )
        else:
            if args.execution_plan is not None:
                raise SfldHmmsearchRunError("--execution-plan is valid only with --apply")
            result = derive_execution_plan(
                paths=paths,
                output_dir=args.output_dir,
                model_accession=args.model_accession,
                target_protein_id=args.target_protein_id,
                domain_number=args.domain_number,
                timeout_seconds=args.timeout_seconds,
                approved_executable_sha256=args.approved_executable_sha256,
            )
    except (
        SfldHmmsearchRunError,
        SfldHmmsearchReceiptError,
        SfldMatchError,
        SfldReleaseError,
    ) as error:
        print(f"SFLD controlled hmmsearch failed: {error}", file=sys.stderr)
        return 1
    print(canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
