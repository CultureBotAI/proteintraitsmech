#!/usr/bin/env python3
"""Prepare or validate a review ledger for the pinned 3did repair plan.

This command replays :mod:`plan_3did_source_model_repair` from the pinned local
source and the current trait tree.  Without ``--ledger`` it emits a complete,
canonical JSONL review template for every proposed corrected-trait addition and
every spurious legacy-trait removal.  With ``--ledger`` it validates a completed
copy against a fresh replay and emits one content-addressed review receipt.

The command is deliberately stdout-only.  Even an accepted receipt is semantic
review state only: it cannot serialize, add, remove, or otherwise modify a trait,
and it does not lift the independent 3did provider/license and residue-level
SIFTS grounding gates.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import stat
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import plan_3did_source_model_repair as repair

SCHEMA_VERSION = 1
DECISION_ROW_KIND = "THREEDID_SOURCE_MODEL_REPAIR_REVIEW_DECISION"
TEMPLATE_SUMMARY_KIND = "THREEDID_SOURCE_MODEL_REPAIR_REVIEW_TEMPLATE_SUMMARY"
RECEIPT_KIND = "THREEDID_SOURCE_MODEL_REPAIR_REVIEW_RECEIPT"
TEMPLATE_ID_PREFIX = "3did-source-model-repair-review-template:"
REVIEW_ITEM_ID_PREFIX = "3did-source-model-repair-review-item:"
REVIEW_SET_ID_PREFIX = "3did-source-model-repair-review-set:"
MAX_LEDGER_BYTES = 32 * 1024 * 1024
_READ_CHUNK_BYTES = 1024 * 1024

ADD_DIMENSION = "ADD_CORRECTED_TRAIT"
REMOVE_DIMENSION = "REMOVE_SPURIOUS_LEGACY_TRAIT"
DECISION_OPTIONS: dict[str, tuple[str, ...]] = {
    ADD_DIMENSION: (
        "APPROVE_CORRECTED_TRAIT_ADDITION",
        "BLOCK_CORRECTED_TRAIT_ADDITION",
        "REQUEST_SOURCE_MODEL_REPLAN",
    ),
    REMOVE_DIMENSION: (
        "APPROVE_SPURIOUS_LEGACY_TRAIT_REMOVAL",
        "KEEP_LEGACY_TRAIT",
        "REQUEST_SOURCE_MODEL_REPLAN",
    ),
}
COMPATIBLE_DECISIONS = {
    ADD_DIMENSION: "APPROVE_CORRECTED_TRAIT_ADDITION",
    REMOVE_DIMENSION: "APPROVE_SPURIOUS_LEGACY_TRAIT_REMOVAL",
}

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_PLAN_ID = re.compile(r"^3did-source-model-repair-plan:[0-9a-f]{64}$")
_REVIEWED_AT = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
_ROW_FIELDS = frozenset(
    {
        "schema_version",
        "kind",
        "review_item_id",
        "binding",
        "binding_sha256",
        "decision",
    }
)
_DECISION_FIELDS = frozenset({"action", "reviewer", "reviewed_at", "comment"})
_AFFECTED_SOURCE_CLASSIFICATIONS = frozenset(
    {
        "DIRECT_REPAIR_PROPOSAL",
        "COLLAPSE_PRIMARY_REPAIR_PROPOSAL",
        "COLLAPSE_SUPPRESSED_REPAIR_PROPOSAL",
    }
)


class ThreeDidRepairReviewError(ValueError):
    """The review template or completed ledger is not exactly replayable."""


def canonical_json(value: Any) -> str:
    return repair.canonical_json(value)


def value_sha256(value: Any) -> str:
    return repair.value_sha256(value)


def rows_sha256(rows: Iterable[Mapping[str, Any]]) -> str:
    return repair.rows_sha256(rows)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ThreeDidRepairReviewError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _load_canonical_json_line(line: str, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(line, object_pairs_hook=_unique_json_object)
    except (ValueError, RecursionError, ThreeDidRepairReviewError) as error:
        raise ThreeDidRepairReviewError(f"{label}: invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise ThreeDidRepairReviewError(f"{label}: expected a JSON object")
    try:
        canonical = canonical_json(value)
    except (TypeError, ValueError, RecursionError) as error:
        raise ThreeDidRepairReviewError(f"{label}: value is not canonical JSON data") from error
    if canonical != line:
        raise ThreeDidRepairReviewError(f"{label}: JSON is not canonical")
    return value


def _exact_lf_lines(text: str, *, label: str) -> list[str]:
    forbidden = {
        "\r": "CR/CRLF",
        "\u0085": "U+0085",
        "\u2028": "U+2028",
        "\u2029": "U+2029",
    }
    for character, name in forbidden.items():
        if character in text:
            raise ThreeDidRepairReviewError(f"{label}: forbidden {name} line separator")
    if not text or not text.endswith("\n"):
        raise ThreeDidRepairReviewError(f"{label}: must be non-empty and LF-terminated")
    lines = text[:-1].split("\n")
    if any(not line for line in lines):
        raise ThreeDidRepairReviewError(f"{label}: blank lines are forbidden")
    return lines


def _entry_identity(metadata: os.stat_result) -> tuple[int, int, int]:
    return metadata.st_dev, metadata.st_ino, stat.S_IFMT(metadata.st_mode)


def _content_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        stat.S_IFMT(metadata.st_mode),
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _capture_regular_file(path: Path, *, label: str, max_bytes: int) -> bytes:
    """Capture one bounded regular file through a stable no-follow descriptor chain."""

    if max_bytes < 1:
        raise ThreeDidRepairReviewError(f"{label}: invalid capture byte limit")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ThreeDidRepairReviewError(
            f"{label}: platform lacks descriptor-relative no-follow support"
        )
    lexical = Path(os.path.abspath(path)) if path.is_absolute() else path
    parts = lexical.parts
    if lexical.is_absolute():
        component_names = parts[1:]
        start = lexical.anchor
    else:
        component_names = parts
        start = "."
    if not component_names or any(component in {"", ".", ".."} for component in component_names):
        raise ThreeDidRepairReviewError(f"{label}: path must have ordinary components: {path}")

    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
    close_on_exec = getattr(os, "O_CLOEXEC", 0)
    directory_flags |= close_on_exec
    file_flags |= close_on_exec
    descriptors: list[int] = []
    bindings: list[tuple[int, str, tuple[int, int, int]]] = []
    try:
        try:
            current = os.open(start, directory_flags)
        except OSError as error:
            raise ThreeDidRepairReviewError(
                f"{label}: cannot open path root for {path}: {error}"
            ) from error
        descriptors.append(current)
        for component in component_names[:-1]:
            try:
                child = os.open(component, directory_flags, dir_fd=current)
                descriptors.append(child)
                child_metadata = os.fstat(child)
            except OSError as error:
                raise ThreeDidRepairReviewError(
                    f"{label}: cannot safely open directory component {component!r}: {error}"
                ) from error
            bindings.append((current, component, _entry_identity(child_metadata)))
            current = child

        final_name = component_names[-1]
        try:
            descriptor = os.open(final_name, file_flags, dir_fd=current)
            descriptors.append(descriptor)
            before = os.fstat(descriptor)
        except OSError as error:
            raise ThreeDidRepairReviewError(
                f"{label}: cannot safely open regular file {path}: {error}"
            ) from error
        bindings.append((current, final_name, _entry_identity(before)))
        if not stat.S_ISREG(before.st_mode):
            raise ThreeDidRepairReviewError(f"{label}: input is not a regular file: {path}")
        if before.st_size < 1 or before.st_size > max_bytes:
            raise ThreeDidRepairReviewError(
                f"{label}: input size {before.st_size} is outside 1..{max_bytes} bytes"
            )

        chunks: list[bytes] = []
        captured = 0
        while True:
            try:
                chunk = os.read(descriptor, min(_READ_CHUNK_BYTES, max_bytes - captured + 1))
            except OSError as error:
                raise ThreeDidRepairReviewError(f"{label}: read failed: {error}") from error
            if not chunk:
                break
            chunks.append(chunk)
            captured += len(chunk)
            if captured > max_bytes:
                raise ThreeDidRepairReviewError(
                    f"{label}: input exceeds the {max_bytes}-byte limit"
                )
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        if len(raw) != before.st_size or _content_identity(after) != _content_identity(before):
            raise ThreeDidRepairReviewError(f"{label}: input changed during capture")

        for parent_descriptor, component, expected_identity in bindings:
            try:
                live = os.stat(component, dir_fd=parent_descriptor, follow_symlinks=False)
            except OSError as error:
                raise ThreeDidRepairReviewError(
                    f"{label}: path component changed during capture: {component!r}: {error}"
                ) from error
            if _entry_identity(live) != expected_identity:
                raise ThreeDidRepairReviewError(
                    f"{label}: path component changed during capture: {component!r}"
                )
        return raw
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _require_sha256(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ThreeDidRepairReviewError(f"{label} is not a lower-case SHA-256")
    return value


def _require_hashed_planner_row(
    row: Mapping[str, Any],
    *,
    kind: str,
    label: str,
) -> dict[str, Any]:
    value = copy.deepcopy(dict(row))
    if value.get("schema_version") != repair.SCHEMA_VERSION or value.get("kind") != kind:
        raise ThreeDidRepairReviewError(f"{label}: planner row version/kind mismatch")
    observed = _require_sha256(value.pop("row_sha256", None), label=f"{label}.row_sha256")
    expected = value_sha256(value)
    if observed != expected:
        raise ThreeDidRepairReviewError(
            f"{label}: planner row hash mismatch; expected {expected}, found {observed}"
        )
    value["row_sha256"] = observed
    return value


def _validated_repair_partition(
    current_rows: Sequence[Mapping[str, Any]],
    source_rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if summary.get("schema_version") != repair.SCHEMA_VERSION:
        raise ThreeDidRepairReviewError("planner summary schema version mismatch")
    if summary.get("kind") != repair.SUMMARY_KIND or summary.get("plan_kind") != repair.PLAN_KIND:
        raise ThreeDidRepairReviewError("planner summary kind mismatch")
    plan_id = summary.get("plan_id")
    if not isinstance(plan_id, str) or _PLAN_ID.fullmatch(plan_id) is None:
        raise ThreeDidRepairReviewError("planner plan_id is malformed")
    summary_without_id = copy.deepcopy(dict(summary))
    summary_without_id.pop("plan_id")
    expected_plan_id = repair.PLAN_ID_PREFIX + value_sha256(summary_without_id)
    if plan_id != expected_plan_id:
        raise ThreeDidRepairReviewError(
            f"planner plan_id content address mismatch; expected {expected_plan_id}"
        )
    _require_sha256(summary.get("rows_sha256"), label="planner summary rows_sha256")
    if summary.get("current_trait_count") != len(current_rows):
        raise ThreeDidRepairReviewError("planner current-trait count mismatch")
    if summary.get("source_record_count") != len(source_rows):
        raise ThreeDidRepairReviewError("planner source-record count mismatch")

    checked_current = [
        _require_hashed_planner_row(
            row,
            kind=repair.CURRENT_ROW_KIND,
            label=f"current row {index}",
        )
        for index, row in enumerate(current_rows, 1)
    ]
    checked_source = [
        _require_hashed_planner_row(
            row,
            kind=repair.SOURCE_ROW_KIND,
            label=f"source row {index}",
        )
        for index, row in enumerate(source_rows, 1)
    ]
    if rows_sha256([*checked_current, *checked_source]) != summary["rows_sha256"]:
        raise ThreeDidRepairReviewError("planner combined row digest mismatch")
    if rows_sha256(checked_current) != summary.get("current_trait_byte_index_sha256"):
        raise ThreeDidRepairReviewError("planner current-row digest mismatch")
    if rows_sha256(checked_source) != summary.get("source_repair_rows_sha256"):
        raise ThreeDidRepairReviewError("planner source-row digest mismatch")

    current_by_id: dict[str, dict[str, Any]] = {}
    spurious: list[dict[str, Any]] = []
    for row in checked_current:
        identifier = row.get("identifier")
        if not isinstance(identifier, str) or identifier in current_by_id:
            raise ThreeDidRepairReviewError("planner current identities are malformed or duplicate")
        current_by_id[identifier] = row
        classification = row.get("classification")
        if classification == "SPURIOUS_LEGACY_MISPARSE_CURRENT":
            spurious.append(row)
        elif classification != "EXACT_SOURCE_NATIVE_CURRENT":
            raise ThreeDidRepairReviewError(
                f"planner current row has unsupported classification {classification!r}"
            )

    affected: list[dict[str, Any]] = []
    corrected_ids: set[str] = set()
    bound_spurious_ids: set[str] = set()
    for row in checked_source:
        classification = row.get("classification")
        if classification == "EXACT_SOURCE_NATIVE":
            continue
        if classification not in _AFFECTED_SOURCE_CLASSIFICATIONS:
            raise ThreeDidRepairReviewError(
                f"planner source row has unsupported classification {classification!r}"
            )
        if row.get("source_state") != "CORRECTED_TRAIT_MISSING":
            raise ThreeDidRepairReviewError("repair proposal is not marked corrected-trait missing")
        proposal = row.get("corrected_proposal")
        binding = row.get("current_binding")
        if not isinstance(proposal, dict) or not isinstance(binding, dict):
            raise ThreeDidRepairReviewError("repair proposal/current binding is malformed")
        corrected_identifier = proposal.get("identifier")
        if not isinstance(corrected_identifier, str) or corrected_identifier in corrected_ids:
            raise ThreeDidRepairReviewError(
                "corrected proposal identities are malformed or duplicate"
            )
        corrected_ids.add(corrected_identifier)
        legacy_identifier = binding.get("identifier")
        current = current_by_id.get(legacy_identifier)
        if current is None or current.get("classification") != "SPURIOUS_LEGACY_MISPARSE_CURRENT":
            raise ThreeDidRepairReviewError(
                "repair proposal is not bound to a spurious current row"
            )
        expected_binding = {
            "identifier": current["identifier"],
            "record_path": current["record_path"],
            "current_record_yaml_sha256": current["current_record_yaml_sha256"],
        }
        if binding != expected_binding:
            raise ThreeDidRepairReviewError("repair proposal current binding disagrees with index")
        bound_spurious_ids.add(legacy_identifier)
        affected.append(row)

    spurious_ids = {row["identifier"] for row in spurious}
    if bound_spurious_ids != spurious_ids:
        raise ThreeDidRepairReviewError("repair proposals do not exhaustively bind spurious rows")
    expected_counts = {
        "corrected_trait_missing_count": len(affected),
        "spurious_current_trait_count": len(spurious),
        "direct_repair_source_count": sum(
            row["classification"] == "DIRECT_REPAIR_PROPOSAL" for row in affected
        ),
        "collapse_primary_source_count": sum(
            row["classification"] == "COLLAPSE_PRIMARY_REPAIR_PROPOSAL" for row in affected
        ),
        "collapse_suppressed_source_count": sum(
            row["classification"] == "COLLAPSE_SUPPRESSED_REPAIR_PROPOSAL" for row in affected
        ),
    }
    for field, expected in expected_counts.items():
        if summary.get(field) != expected:
            raise ThreeDidRepairReviewError(f"planner {field} mismatch")
    return sorted(spurious, key=lambda row: row["identifier"]), sorted(
        affected,
        key=lambda row: (row["corrected_proposal"]["identifier"], row["source_record_id"]),
    )


def _plan_context(summary: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "plan_id",
        "rows_sha256",
        "current_trait_byte_index_sha256",
        "source_repair_rows_sha256",
        "source_compressed_sha256",
        "source_decompressed_sha256",
        "source_release",
        "source_release_semantics",
        "source_license",
        "source_license_status",
        "grounding_gate",
    )
    context = {field: copy.deepcopy(summary.get(field)) for field in fields}
    for field in (
        "rows_sha256",
        "current_trait_byte_index_sha256",
        "source_repair_rows_sha256",
        "source_compressed_sha256",
        "source_decompressed_sha256",
    ):
        _require_sha256(context[field], label=f"planner summary {field}")
    if context["grounding_gate"] != repair.GROUNDING_GATE:
        raise ThreeDidRepairReviewError("planner grounding gate mismatch")
    return context


def _decision_row(binding: dict[str, Any]) -> dict[str, Any]:
    binding_hash = value_sha256(binding)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": DECISION_ROW_KIND,
        "review_item_id": REVIEW_ITEM_ID_PREFIX + binding_hash,
        "binding": binding,
        "binding_sha256": binding_hash,
        "decision": {
            "action": None,
            "reviewer": None,
            "reviewed_at": None,
            "comment": None,
        },
    }


def build_review_template(
    current_rows: Sequence[Mapping[str, Any]],
    source_rows: Sequence[Mapping[str, Any]],
    planner_summary: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build the exhaustive no-decision template from one fresh repair replay."""

    spurious, affected = _validated_repair_partition(current_rows, source_rows, planner_summary)
    context = _plan_context(planner_summary)
    affected_by_current: dict[str, list[str]] = defaultdict(list)
    for row in affected:
        affected_by_current[row["current_binding"]["identifier"]].append(row["source_record_id"])

    rows: list[dict[str, Any]] = []
    for row in affected:
        rows.append(
            _decision_row(
                {
                    "review_dimension": ADD_DIMENSION,
                    "target_identifier": row["corrected_proposal"]["identifier"],
                    "bound_legacy_current_identifier": row["current_binding"]["identifier"],
                    "planner_source_row": copy.deepcopy(row),
                    "planner_context": copy.deepcopy(context),
                    "decision_options": list(DECISION_OPTIONS[ADD_DIMENSION]),
                }
            )
        )
    for row in spurious:
        rows.append(
            _decision_row(
                {
                    "review_dimension": REMOVE_DIMENSION,
                    "target_identifier": row["identifier"],
                    "dependent_source_record_ids": sorted(affected_by_current[row["identifier"]]),
                    "planner_current_row": copy.deepcopy(row),
                    "planner_context": copy.deepcopy(context),
                    "decision_options": list(DECISION_OPTIONS[REMOVE_DIMENSION]),
                }
            )
        )
    rows.sort(
        key=lambda row: (
            row["binding"]["review_dimension"],
            row["binding"]["target_identifier"],
            row["review_item_id"],
        )
    )

    dimensions = Counter(row["binding"]["review_dimension"] for row in rows)
    source_classes = Counter(row["classification"] for row in affected)
    bindings = [
        {
            "review_item_id": row["review_item_id"],
            "binding_sha256": row["binding_sha256"],
        }
        for row in rows
    ]
    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": TEMPLATE_SUMMARY_KIND,
        "planner_schema_version": repair.SCHEMA_VERSION,
        "planner_plan_id": planner_summary["plan_id"],
        "planner_rows_sha256": planner_summary["rows_sha256"],
        "review_item_count": len(rows),
        "review_dimension_counts": dict(sorted(dimensions.items())),
        "source_proposal_classification_counts": dict(sorted(source_classes.items())),
        "legacy_collision_key_count": planner_summary.get("legacy_collision_key_count"),
        "legacy_collapsed_extra_source_count": planner_summary.get(
            "legacy_collapsed_extra_source_count"
        ),
        "decision_options": {
            dimension: list(options) for dimension, options in sorted(DECISION_OPTIONS.items())
        },
        "bindings_sha256": rows_sha256(bindings),
        "template_rows_sha256": rows_sha256(rows),
        "review_scope": (
            "SEMANTIC_SOURCE_MODEL_REPAIR_ONLY_NO_SERIALIZATION_OR_GROUNDING_AUTHORIZATION"
        ),
        "writes_performed": False,
        "writer_available": False,
        "apply_authorized": False,
        "serialization_status": "NOT_PERFORMED",
        "grounding_gate": repair.GROUNDING_GATE,
    }
    summary["template_id"] = TEMPLATE_ID_PREFIX + value_sha256(summary)
    return rows, summary


def dump_review_template(rows: Iterable[Mapping[str, Any]], summary: Mapping[str, Any]) -> str:
    return "".join(canonical_json(row) + "\n" for row in [*rows, summary])


def _read_completed_ledger(
    path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any], bytes]:
    raw = _capture_regular_file(
        path, label="3did completed review ledger", max_bytes=MAX_LEDGER_BYTES
    )
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise ThreeDidRepairReviewError("completed ledger is not valid UTF-8") from error
    lines = _exact_lf_lines(text, label="completed ledger")
    values = [
        _load_canonical_json_line(line, label=f"completed ledger line {line_number}")
        for line_number, line in enumerate(lines, 1)
    ]
    if len(values) < 2:
        raise ThreeDidRepairReviewError("completed ledger must contain decisions and a summary")
    return values[:-1], values[-1], raw


def _validate_review_metadata(value: Any, *, dimension: str, item_id: str) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != _DECISION_FIELDS:
        raise ThreeDidRepairReviewError(f"{item_id}: decision fields differ from contract")
    action = value.get("action")
    if action not in DECISION_OPTIONS[dimension]:
        raise ThreeDidRepairReviewError(f"{item_id}: invalid or missing review action")
    reviewer = value.get("reviewer")
    if (
        not isinstance(reviewer, str)
        or reviewer != reviewer.strip()
        or not reviewer
        or len(reviewer) > 200
        or any(ord(character) < 32 for character in reviewer)
    ):
        raise ThreeDidRepairReviewError(f"{item_id}: reviewer is malformed")
    reviewed_at = value.get("reviewed_at")
    if not isinstance(reviewed_at, str) or _REVIEWED_AT.fullmatch(reviewed_at) is None:
        raise ThreeDidRepairReviewError(f"{item_id}: reviewed_at must be exact UTC seconds")
    try:
        datetime.strptime(reviewed_at, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise ThreeDidRepairReviewError(
            f"{item_id}: reviewed_at is not a real timestamp"
        ) from error
    comment = value.get("comment")
    if not isinstance(comment, str) or len(comment) > 4000 or "\x00" in comment:
        raise ThreeDidRepairReviewError(f"{item_id}: comment is malformed")
    return {
        "action": action,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "comment": comment,
    }


def validate_completed_ledger(
    supplied_rows: Sequence[Mapping[str, Any]],
    supplied_summary: Mapping[str, Any],
    *,
    expected_rows: Sequence[Mapping[str, Any]],
    expected_summary: Mapping[str, Any],
    ledger_bytes: bytes,
) -> dict[str, Any]:
    """Validate immutable bindings plus every explicit human decision."""

    if dict(supplied_summary) != dict(expected_summary):
        raise ThreeDidRepairReviewError("completed ledger template summary is stale or altered")
    if len(supplied_rows) != len(expected_rows):
        raise ThreeDidRepairReviewError("completed ledger decision-row count mismatch")
    if not ledger_bytes:
        raise ThreeDidRepairReviewError("completed ledger byte stream is empty")
    canonical_ledger_bytes = dump_review_template(supplied_rows, supplied_summary).encode("utf-8")
    if ledger_bytes != canonical_ledger_bytes:
        raise ThreeDidRepairReviewError(
            "completed ledger bytes do not match the supplied canonical decision objects"
        )

    decisions: list[dict[str, Any]] = []
    seen_items: set[str] = set()
    compatible = True
    for index, (supplied_raw, expected_raw) in enumerate(zip(supplied_rows, expected_rows), 1):
        supplied = dict(supplied_raw)
        expected = dict(expected_raw)
        if set(supplied) != _ROW_FIELDS:
            raise ThreeDidRepairReviewError(f"decision row {index}: fields differ from contract")
        item_id = supplied.get("review_item_id")
        if not isinstance(item_id, str) or item_id in seen_items:
            raise ThreeDidRepairReviewError(f"decision row {index}: duplicate/malformed item ID")
        seen_items.add(item_id)
        for field in _ROW_FIELDS - {"decision"}:
            if supplied.get(field) != expected.get(field):
                raise ThreeDidRepairReviewError(
                    f"{item_id}: immutable review binding field {field!r} changed"
                )
        binding = supplied["binding"]
        if supplied["binding_sha256"] != value_sha256(binding):
            raise ThreeDidRepairReviewError(f"{item_id}: binding hash mismatch")
        dimension = binding.get("review_dimension")
        if dimension not in DECISION_OPTIONS:
            raise ThreeDidRepairReviewError(f"{item_id}: unknown review dimension")
        metadata = _validate_review_metadata(
            supplied.get("decision"),
            dimension=dimension,
            item_id=item_id,
        )
        if metadata["action"] != COMPATIBLE_DECISIONS[dimension]:
            compatible = False
        decisions.append(
            {
                "review_item_id": item_id,
                "binding_sha256": supplied["binding_sha256"],
                "review_dimension": dimension,
                **metadata,
            }
        )

    decision_counts = Counter(row["action"] for row in decisions)
    decision_rows_hash = rows_sha256(decisions)
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": RECEIPT_KIND,
        "status": "ACCEPTED_SEMANTIC_PLAN_ONLY" if compatible else "VALID_NON_ACCEPTING",
        "proposal_compatible": compatible,
        "accepted_for_next_phase": compatible,
        "template_id": expected_summary["template_id"],
        "planner_plan_id": expected_summary["planner_plan_id"],
        "planner_rows_sha256": expected_summary["planner_rows_sha256"],
        "review_item_count": len(decisions),
        "review_dimension_counts": copy.deepcopy(expected_summary["review_dimension_counts"]),
        "decision_counts": dict(sorted(decision_counts.items())),
        "decision_rows_sha256": decision_rows_hash,
        "ledger_sha256": hashlib.sha256(ledger_bytes).hexdigest(),
        "review_scope": expected_summary["review_scope"],
        "apply_authorized": False,
        "serialization_status": "NOT_PERFORMED",
        "writes_performed": False,
        "writer_available": False,
        "grounding_gate": repair.GROUNDING_GATE,
    }
    if compatible:
        receipt["review_set_id"] = REVIEW_SET_ID_PREFIX + value_sha256(receipt)
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=repair.DEFAULT_SOURCE)
    parser.add_argument("--traits", type=Path, default=repair.DEFAULT_TRAITS)
    parser.add_argument(
        "--ledger",
        type=Path,
        help="completed copy of the emitted review template; validation remains stdout-only",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        current_rows, source_rows, planner_summary = repair.plan_from_paths(
            args.source,
            args.traits,
        )
        template_rows, template_summary = build_review_template(
            current_rows,
            source_rows,
            planner_summary,
        )
        if args.ledger is None:
            print(dump_review_template(template_rows, template_summary), end="")
            return 0
        supplied_rows, supplied_summary, raw = _read_completed_ledger(args.ledger)
        receipt = validate_completed_ledger(
            supplied_rows,
            supplied_summary,
            expected_rows=template_rows,
            expected_summary=template_summary,
            ledger_bytes=raw,
        )
    except (ThreeDidRepairReviewError, repair.ThreeDidRepairError, OSError) as error:
        print(f"refusing 3did repair review: {error}", file=sys.stderr)
        return 2
    print(canonical_json(receipt))
    return 0 if receipt["accepted_for_next_phase"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
