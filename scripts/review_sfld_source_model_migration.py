#!/usr/bin/env python3
"""Prepare or validate semantic review for the pinned SFLD migration plan.

The command freshly replays :mod:`plan_sfld_source_model_migration`; it never
accepts a saved plan as authority.  Without ``--ledger`` it emits a canonical
JSONL template with independent decisions for routing and label/definition on
every current SFLD record, source-profile representation on every executable
model, and disposition on each of the four model-less signatures.  With ``--ledger``
it validates a completed copy and prints one content-addressed receipt.

An accepted route selection must remain consistent across every source parent
edge.  Mixed routes would make the retained ``parent_traits`` edges cross
incompatible categories; those ledgers are valid but non-accepting and require
a separate hierarchy-replan proposal.

Even a compatible receipt is semantic-plan state only.  This module has no
serializer, output-file, trait writer, apply, grounding, or promotion path, and
it cannot replace the independent content-addressed hmmsearch receipt gate.
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
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import plan_sfld_source_model_migration as migration

SCHEMA_VERSION = 1
DECISION_ROW_KIND = "SFLD_SOURCE_MODEL_MIGRATION_REVIEW_DECISION"
TEMPLATE_SUMMARY_KIND = "SFLD_SOURCE_MODEL_MIGRATION_REVIEW_TEMPLATE_SUMMARY"
RECEIPT_KIND = "SFLD_SOURCE_MODEL_MIGRATION_REVIEW_RECEIPT"
TEMPLATE_ID_PREFIX = "sfld-source-model-migration-review-template:"
REVIEW_ITEM_ID_PREFIX = "sfld-source-model-migration-review-item:"
REVIEW_SET_ID_PREFIX = "sfld-source-model-migration-review-set:"
MAX_LEDGER_BYTES = 64 * 1024 * 1024
_READ_CHUNK_BYTES = 1024 * 1024

ROUTING_DIMENSION = "SEMANTIC_ROUTING"
DEFINITION_DIMENSION = "LABEL_AND_DEFINITION"
PROFILE_DIMENSION = "SOURCE_PROFILE_REPRESENTATION"
MODELLESS_DIMENSION = "MODELLESS_DISPOSITION"

ROUTE_TARGETS: dict[str, dict[str, str]] = {
    "KEEP_FUNCTION_PROTEIN_FAMILY_ROUTE": {
        "trait_axis": "FUNCTION",
        "trait_category": "FUNC_PROTEIN_FAMILY",
        "directory": "data/traits/function/protein_family/sfld",
    },
    "ROUTE_TO_FUNCTION_ENZYMATIC_ACTIVITY": {
        "trait_axis": "FUNCTION",
        "trait_category": "FUNC_ENZYMATIC_ACTIVITY",
        "directory": "data/traits/function/enzymatic_activity/sfld",
    },
    "ROUTE_TO_SEQUENCE_DOMAIN": {
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_DOMAIN",
        "directory": "data/traits/sequence/domain/sfld",
    },
    "ROUTE_TO_SEQUENCE_FAMILY": {
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_FAMILY",
        "directory": "data/traits/sequence/family/sfld",
    },
    "ROUTE_TO_SEQUENCE_HOMOLOGOUS_SUPERFAMILY": {
        "trait_axis": "SEQUENCE",
        "trait_category": "SEQ_HOMOLOGOUS_SUPERFAMILY",
        "directory": "data/traits/sequence/homologous_superfamily/sfld",
    },
}

DECISION_OPTIONS: dict[str, tuple[str, ...]] = {
    ROUTING_DIMENSION: (
        *ROUTE_TARGETS,
        "BLOCK_RECORD_ROUTING",
        "REQUEST_ROUTING_REPLAN",
    ),
    DEFINITION_DIMENSION: (
        "KEEP_CURRENT_LABEL_AND_DEFINITION",
        "BLOCK_CURRENT_LABEL_OR_DEFINITION",
        "REQUEST_LABEL_OR_DEFINITION_REPLAN",
    ),
    PROFILE_DIMENSION: (
        "APPROVE_SOURCE_PROFILE_PROJECTION",
        "BLOCK_SOURCE_PROFILE_PROJECTION",
        "REQUEST_SOURCE_MODEL_REPLAN",
    ),
    MODELLESS_DIMENSION: (
        "RETAIN_MODELLESS_REFERENCE_ONLY",
        "BLOCK_MODELLESS_RECORD",
        "REQUEST_SOURCE_MODEL_REPLAN",
    ),
}

_COMPATIBLE_FIXED_DECISIONS = {
    DEFINITION_DIMENSION: "KEEP_CURRENT_LABEL_AND_DEFINITION",
    PROFILE_DIMENSION: "APPROVE_SOURCE_PROFILE_PROJECTION",
    MODELLESS_DIMENSION: "RETAIN_MODELLESS_REFERENCE_ONLY",
}

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_PLAN_ID_RE = re.compile(r"^sfld-source-model-migration-plan:[0-9a-f]{64}$")
_REVIEWED_AT_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
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
_SUPPORTED_PLANNER_REVIEW_REQUIREMENTS = frozenset(
    {
        "SEMANTIC_ROUTING_REVIEW",
        "DEFINITION_REVIEW",
        "NO_EXECUTABLE_MODEL_DISPOSITION_REVIEW",
        "PROFILE_SERIALIZATION_CONFLICT_REVIEW",
        "PROFILE_REPRESENTATION_REVIEW",
        "LABEL_NORMALIZATION_REVIEW",
        "LABEL_REVIEW",
        "INTERPRO_DOMAIN_GRANULARITY_REVIEW",
        "DEFINITION_PROVENANCE_REVIEW",
        "PATH_REVIEW",
        "CURRENT_ROUTE_DRIFT_REVIEW",
    }
)


class SfldMigrationReviewError(ValueError):
    """The review template or completed ledger is not exactly replayable."""


def canonical_json(value: Any) -> str:
    return migration.canonical_json(value)


def value_sha256(value: Any) -> str:
    return migration.value_sha256(value)


def rows_sha256(rows: Iterable[Mapping[str, Any]]) -> str:
    return migration.rows_sha256(rows)


def _require_sha256(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise SfldMigrationReviewError(f"{label} is not a lower-case SHA-256")
    return value


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise SfldMigrationReviewError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _load_canonical_json_line(line: str, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(line, object_pairs_hook=_unique_json_object)
    except (ValueError, RecursionError, SfldMigrationReviewError) as error:
        raise SfldMigrationReviewError(f"{label}: invalid JSON: {error}") from error
    if type(value) is not dict:
        raise SfldMigrationReviewError(f"{label}: expected a JSON object")
    try:
        canonical = canonical_json(value)
    except (TypeError, ValueError, RecursionError) as error:
        raise SfldMigrationReviewError(f"{label}: value is not canonical JSON data") from error
    if canonical != line:
        raise SfldMigrationReviewError(f"{label}: JSON is not canonical")
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
            raise SfldMigrationReviewError(f"{label}: forbidden {name} line separator")
    if not text or not text.endswith("\n"):
        raise SfldMigrationReviewError(f"{label}: must be non-empty and LF-terminated")
    lines = text[:-1].split("\n")
    if any(not line for line in lines):
        raise SfldMigrationReviewError(f"{label}: blank lines are forbidden")
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
    """Capture one bounded regular file through stable component-no-follow descriptors."""

    if max_bytes < 1:
        raise SfldMigrationReviewError(f"{label}: invalid capture byte limit")
    no_follow = getattr(os, "O_NOFOLLOW", None)
    directory_only = getattr(os, "O_DIRECTORY", None)
    supports_dir_fd = getattr(os, "supports_dir_fd", set())
    supports_follow_symlinks = getattr(os, "supports_follow_symlinks", set())
    if (
        not isinstance(no_follow, int)
        or no_follow == 0
        or not isinstance(directory_only, int)
        or directory_only == 0
        or os.open not in supports_dir_fd
        or os.stat not in supports_follow_symlinks
    ):
        raise SfldMigrationReviewError(
            f"{label}: platform lacks descriptor-relative no-follow support"
        )
    lexical = Path(os.path.abspath(path)) if path.is_absolute() else path
    components = lexical.parts[1:] if lexical.is_absolute() else lexical.parts
    start = lexical.anchor if lexical.is_absolute() else "."
    if not components or any(component in {"", ".", ".."} for component in components):
        raise SfldMigrationReviewError(f"{label}: path must have ordinary components: {path}")

    close_on_exec = getattr(os, "O_CLOEXEC", 0)
    directory_flags = os.O_RDONLY | directory_only | no_follow | close_on_exec
    file_flags = os.O_RDONLY | no_follow | close_on_exec | getattr(os, "O_NONBLOCK", 0)
    descriptors: list[int] = []
    bindings: list[tuple[int, str, tuple[int, int, int]]] = []
    try:
        try:
            current = os.open(start, directory_flags)
        except OSError as error:
            raise SfldMigrationReviewError(
                f"{label}: cannot safely open path root for {path}: {error}"
            ) from error
        descriptors.append(current)
        for component in components[:-1]:
            try:
                child = os.open(component, directory_flags, dir_fd=current)
                child_metadata = os.fstat(child)
            except OSError as error:
                raise SfldMigrationReviewError(
                    f"{label}: cannot safely open directory component {component!r}: {error}"
                ) from error
            bindings.append((current, component, _entry_identity(child_metadata)))
            descriptors.append(child)
            current = child

        final_name = components[-1]
        try:
            descriptor = os.open(final_name, file_flags, dir_fd=current)
            before = os.fstat(descriptor)
        except OSError as error:
            raise SfldMigrationReviewError(
                f"{label}: cannot safely open regular file {path}: {error}"
            ) from error
        descriptors.append(descriptor)
        bindings.append((current, final_name, _entry_identity(before)))
        if not stat.S_ISREG(before.st_mode):
            raise SfldMigrationReviewError(f"{label}: input is not a regular file: {path}")
        if before.st_size < 1 or before.st_size > max_bytes:
            raise SfldMigrationReviewError(
                f"{label}: input size {before.st_size} is outside 1..{max_bytes} bytes"
            )

        chunks: list[bytes] = []
        captured = 0
        while True:
            try:
                chunk = os.read(
                    descriptor,
                    min(_READ_CHUNK_BYTES, max_bytes - captured + 1),
                )
            except OSError as error:
                raise SfldMigrationReviewError(f"{label}: read failed: {error}") from error
            if not chunk:
                break
            chunks.append(chunk)
            captured += len(chunk)
            if captured > max_bytes:
                raise SfldMigrationReviewError(f"{label}: input exceeds {max_bytes} bytes")
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        if len(raw) != before.st_size or _content_identity(after) != _content_identity(before):
            raise SfldMigrationReviewError(f"{label}: input changed during capture")
        for parent_descriptor, component, expected_identity in bindings:
            try:
                live = os.stat(component, dir_fd=parent_descriptor, follow_symlinks=False)
            except OSError as error:
                raise SfldMigrationReviewError(
                    f"{label}: path component changed during capture: {component!r}: {error}"
                ) from error
            if _entry_identity(live) != expected_identity:
                raise SfldMigrationReviewError(
                    f"{label}: path component changed during capture: {component!r}"
                )
        return raw
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _require_hashed_planner_row(
    row: Mapping[str, Any],
    *,
    index: int,
) -> dict[str, Any]:
    value = copy.deepcopy(dict(row))
    if (
        value.get("schema_version") != migration.SCHEMA_VERSION
        or value.get("kind") != migration.ROW_KIND
    ):
        raise SfldMigrationReviewError(f"planner row {index}: version/kind mismatch")
    observed = _require_sha256(
        value.pop("row_sha256", None),
        label=f"planner row {index}.row_sha256",
    )
    expected = value_sha256(value)
    if observed != expected:
        raise SfldMigrationReviewError(
            f"planner row {index}: row hash mismatch; expected {expected}, found {observed}"
        )
    value["row_sha256"] = observed
    return value


def _validate_planner_partition(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
) -> list[dict[str, Any]]:
    if summary.get("schema_version") != migration.SCHEMA_VERSION:
        raise SfldMigrationReviewError("planner summary schema version mismatch")
    if (
        summary.get("kind") != migration.SUMMARY_KIND
        or summary.get("plan_kind") != migration.PLAN_KIND
    ):
        raise SfldMigrationReviewError("planner summary kind mismatch")
    plan_id = summary.get("plan_id")
    if not isinstance(plan_id, str) or _PLAN_ID_RE.fullmatch(plan_id) is None:
        raise SfldMigrationReviewError("planner plan_id is malformed")
    summary_without_id = copy.deepcopy(dict(summary))
    summary_without_id.pop("plan_id")
    expected_plan_id = migration.PLAN_ID_PREFIX + value_sha256(summary_without_id)
    if plan_id != expected_plan_id:
        raise SfldMigrationReviewError(
            f"planner plan_id content address mismatch; expected {expected_plan_id}"
        )
    if summary.get("current_record_count") != len(rows):
        raise SfldMigrationReviewError("planner current-record count mismatch")
    checked = [_require_hashed_planner_row(row, index=index) for index, row in enumerate(rows, 1)]
    if rows_sha256(checked) != summary.get("rows_sha256"):
        raise SfldMigrationReviewError("planner row-stream digest mismatch")

    identifiers: set[str] = set()
    classification_counts: Counter[str] = Counter()
    profile_count = 0
    model_less: list[str] = []
    for row in checked:
        identifier = row.get("identifier")
        if not isinstance(identifier, str) or identifier in identifiers:
            raise SfldMigrationReviewError("planner identifiers are malformed or duplicate")
        identifiers.add(identifier)
        if row.get("apply_authorized") is not False:
            raise SfldMigrationReviewError(f"{identifier}: planner unexpectedly authorizes apply")
        if row.get("grounding_eligible") is not False:
            raise SfldMigrationReviewError(f"{identifier}: planner unexpectedly allows grounding")
        if row.get("record_serialization_status") != "NOT_MATERIALIZED_REVIEW_ONLY":
            raise SfldMigrationReviewError(f"{identifier}: planner serialization status changed")
        if row.get("routing_decision_status") != "NOT_MADE_REVIEW_REQUIRED":
            raise SfldMigrationReviewError(f"{identifier}: planner routing is already decided")
        if row.get("definition_decision_status") != "NOT_MADE_REVIEW_REQUIRED":
            raise SfldMigrationReviewError(f"{identifier}: planner definition is already decided")
        review_requirements = row.get("review_requirements")
        if (
            type(review_requirements) is not list
            or any(type(requirement) is not str for requirement in review_requirements)
            or len(review_requirements) != len(set(review_requirements))
        ):
            raise SfldMigrationReviewError(f"{identifier}: review requirements are malformed")
        requirement_set = set(review_requirements)
        unsupported_requirements = sorted(requirement_set - _SUPPORTED_PLANNER_REVIEW_REQUIREMENTS)
        if unsupported_requirements:
            raise SfldMigrationReviewError(
                f"{identifier}: review compiler does not cover planner requirements "
                f"{unsupported_requirements!r}"
            )
        if not {"SEMANTIC_ROUTING_REVIEW", "DEFINITION_REVIEW"}.issubset(requirement_set):
            raise SfldMigrationReviewError(
                f"{identifier}: planner omitted mandatory routing/definition review"
            )
        definition_projection = row.get("definition_review_projection")
        if not isinstance(definition_projection, dict) or value_sha256(
            definition_projection
        ) != row.get("definition_review_projection_sha256"):
            raise SfldMigrationReviewError(f"{identifier}: definition projection hash mismatch")

        classification = row.get("classification")
        classification_counts[str(classification)] += 1
        if classification == "EXECUTABLE_MODEL_SEMANTIC_REVIEW_REQUIRED":
            if "PROFILE_REPRESENTATION_REVIEW" not in requirement_set:
                raise SfldMigrationReviewError(
                    f"{identifier}: executable row omits profile review requirement"
                )
            profile = row.get("source_profile_projection")
            if not isinstance(profile, dict) or value_sha256(profile) != row.get(
                "source_profile_projection_sha256"
            ):
                raise SfldMigrationReviewError(f"{identifier}: source profile hash mismatch")
            if not isinstance(row.get("source_model"), dict):
                raise SfldMigrationReviewError(f"{identifier}: executable model binding missing")
            profile_count += 1
        elif classification == "NO_EXECUTABLE_MODEL_DISPOSITION_REVIEW_REQUIRED":
            if "NO_EXECUTABLE_MODEL_DISPOSITION_REVIEW" not in requirement_set:
                raise SfldMigrationReviewError(
                    f"{identifier}: model-less row omits disposition review requirement"
                )
            if (
                row.get("source_profile_projection") is not None
                or row.get("source_model") is not None
            ):
                raise SfldMigrationReviewError(
                    f"{identifier}: model-less row carries an executable source projection"
                )
            model_less.append(identifier)
        else:
            raise SfldMigrationReviewError(
                f"{identifier}: unsupported planner classification {classification!r}"
            )

    expected_classifications = dict(sorted(classification_counts.items()))
    if summary.get("classification_counts") != expected_classifications:
        raise SfldMigrationReviewError("planner classification counts mismatch")
    if summary.get("review_required_count") != len(checked):
        raise SfldMigrationReviewError("planner review-required count mismatch")
    if summary.get("content_ready_count") != 0:
        raise SfldMigrationReviewError("planner unexpectedly reports content-ready rows")
    if summary.get("routing_policy_status") != "NOT_DECIDED_FULL_FILE_REVIEW_REQUIRED":
        raise SfldMigrationReviewError("planner routing policy status changed")
    if summary.get("definition_policy_status") != "NOT_DECIDED_FULL_FILE_REVIEW_REQUIRED":
        raise SfldMigrationReviewError("planner definition policy status changed")
    if summary.get("legacy_sfld_api_snapshot_status") != "ABSENT_NOT_REPLAYED":
        raise SfldMigrationReviewError(
            "planner legacy API snapshot status changed; review contract needs re-audit"
        )
    if summary.get("source_model_count") != profile_count:
        raise SfldMigrationReviewError("planner source-model count mismatch")
    if summary.get("source_profile_projection_count") != profile_count:
        raise SfldMigrationReviewError("planner source-profile count mismatch")
    if summary.get("model_less_current_count") != len(model_less):
        raise SfldMigrationReviewError("planner model-less count mismatch")
    if summary.get("model_less_current_identifiers") != sorted(model_less):
        raise SfldMigrationReviewError("planner model-less identifier set mismatch")
    if summary.get("serialization_status") != "NOT_PERFORMED":
        raise SfldMigrationReviewError("planner summary serialization status changed")
    if summary.get("writer_available") is not False or summary.get("apply_authorized") is not False:
        raise SfldMigrationReviewError("planner summary unexpectedly exposes a writer/apply path")
    if summary.get("grounding_eligible") is not False:
        raise SfldMigrationReviewError("planner summary unexpectedly permits grounding")
    if summary.get("grounding_gate") != migration.GROUNDING_GATE:
        raise SfldMigrationReviewError("planner grounding gate mismatch")
    checked_by_id = {row["identifier"]: row for row in checked}
    for row in checked:
        identifier = row["identifier"]
        if row["classification"] == "EXECUTABLE_MODEL_SEMANTIC_REVIEW_REQUIRED":
            parents = row.get("source_parent_traits")
            if (
                type(parents) is not list
                or len(parents) > 1
                or any(type(parent) is not str for parent in parents)
            ):
                raise SfldMigrationReviewError(
                    f"{identifier}: source parent projection is malformed"
                )
            if row.get("parent_status") != "MATCHES_SOURCE_HIERARCHY":
                raise SfldMigrationReviewError(
                    f"{identifier}: hierarchy drift needs a dedicated review dimension"
                )
            if parents and parents[0] not in checked_by_id:
                raise SfldMigrationReviewError(
                    f"{identifier}: source parent {parents[0]} has no planner row"
                )
        else:
            if row.get("source_parent_traits") is not None:
                raise SfldMigrationReviewError(
                    f"{identifier}: model-less row unexpectedly has a source parent"
                )
            if row.get("current_parent_traits") != []:
                raise SfldMigrationReviewError(
                    f"{identifier}: model-less current parent needs a dedicated review dimension"
                )
    return sorted(checked, key=lambda row: row["identifier"])


def _plan_context(summary: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "plan_id",
        "rows_sha256",
        "source_model_manifest_sha256",
        "source_hmm_sha256",
        "source_hierarchy_sha256",
        "source_sites_sha256",
        "interpro_xml_sha256",
        "current_trait_binding_sha256",
        "source_model_projection_sha256",
        "source_release",
        "grounding_gate",
    )
    context = {field: copy.deepcopy(summary.get(field)) for field in fields}
    for field in fields[1:9]:
        _require_sha256(context[field], label=f"planner summary {field}")
    if context["grounding_gate"] != migration.GROUNDING_GATE:
        raise SfldMigrationReviewError("planner context grounding gate mismatch")
    return context


def replay_migration_plan(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Freshly replay all source and trait inputs; never trust a saved plan."""

    snapshot = migration.load_verified_source_snapshot(
        hmm_path=args.hmm,
        hierarchy_path=args.hierarchy,
        sites_path=args.sites,
        manifest_path=args.manifest,
        interpro_path=args.interpro,
    )
    records = migration.index_sfld_records(args.traits)
    return migration.build_plan(records=records, snapshot=snapshot)


def _decision_row(binding: dict[str, Any]) -> dict[str, Any]:
    binding_sha256 = value_sha256(binding)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": DECISION_ROW_KIND,
        "review_item_id": REVIEW_ITEM_ID_PREFIX + binding_sha256,
        "binding": binding,
        "binding_sha256": binding_sha256,
        "decision": {
            "action": None,
            "reviewer": None,
            "reviewed_at": None,
            "comment": None,
        },
    }


def _common_binding(row: Mapping[str, Any], context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "target_identifier": row["identifier"],
        "planner_row_sha256": row["row_sha256"],
        "record_path": row["record_path"],
        "current_record_yaml_sha256": row["current_record_yaml_sha256"],
        "planner_context": copy.deepcopy(context),
    }


def build_review_template(
    planner_rows: Sequence[Mapping[str, Any]],
    planner_summary: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build the exhaustive blank template from one authenticated planner replay."""

    checked = _validate_planner_partition(planner_rows, planner_summary)
    context = _plan_context(planner_summary)
    rows: list[dict[str, Any]] = []
    for planner_row in checked:
        common = _common_binding(planner_row, context)
        routing = {
            **copy.deepcopy(common),
            "review_dimension": ROUTING_DIMENSION,
            "current_native_level_from_accession": planner_row[
                "current_native_level_from_accession"
            ],
            "current_route": copy.deepcopy(planner_row["current_route"]),
            "current_record_path_status": planner_row["path_status"],
            "current_parent_traits": copy.deepcopy(planner_row["current_parent_traits"]),
            "source_parent_traits": copy.deepcopy(planner_row["source_parent_traits"]),
            "parent_status": planner_row["parent_status"],
            "source_model_native_level": (
                planner_row["source_model"]["native_classification_level"]
                if planner_row["source_model"] is not None
                else None
            ),
            "integrating_interpro_types": copy.deepcopy(planner_row["integrating_interpro_types"]),
            "route_targets": copy.deepcopy(ROUTE_TARGETS),
            "decision_options": list(DECISION_OPTIONS[ROUTING_DIMENSION]),
        }
        rows.append(_decision_row(routing))

        definition = {
            **copy.deepcopy(common),
            "review_dimension": DEFINITION_DIMENSION,
            "source_label_status": planner_row["source_label_status"],
            "definition_status": planner_row["definition_status"],
            "definition_review_projection": copy.deepcopy(
                planner_row["definition_review_projection"]
            ),
            "definition_review_projection_sha256": planner_row[
                "definition_review_projection_sha256"
            ],
            "source_model_name": (
                planner_row["source_model"]["name"]
                if planner_row["source_model"] is not None
                else None
            ),
            "source_model_description": (
                planner_row["source_model"]["description"]
                if planner_row["source_model"] is not None
                else None
            ),
            "decision_options": list(DECISION_OPTIONS[DEFINITION_DIMENSION]),
        }
        rows.append(_decision_row(definition))

        if planner_row["source_profile_projection"] is not None:
            profile = {
                **copy.deepcopy(common),
                "review_dimension": PROFILE_DIMENSION,
                "profile_status": planner_row["profile_status"],
                "source_profile_projection": copy.deepcopy(
                    planner_row["source_profile_projection"]
                ),
                "source_profile_projection_sha256": planner_row["source_profile_projection_sha256"],
                "source_profile_projection_status": planner_row["source_profile_projection_status"],
                "decision_options": list(DECISION_OPTIONS[PROFILE_DIMENSION]),
            }
            rows.append(_decision_row(profile))
        else:
            model_less = {
                **copy.deepcopy(common),
                "review_dimension": MODELLESS_DIMENSION,
                "classification": planner_row["classification"],
                "profile_status": planner_row["profile_status"],
                "legacy_sfld_api_snapshot_status": planner_summary[
                    "legacy_sfld_api_snapshot_status"
                ],
                "retention_semantics": (
                    "REFERENCE_CLASS_ONLY_NO_EXECUTABLE_PROFILE_OR_GROUNDING_ELIGIBILITY"
                ),
                "decision_options": list(DECISION_OPTIONS[MODELLESS_DIMENSION]),
            }
            rows.append(_decision_row(model_less))

    rows.sort(
        key=lambda row: (
            row["binding"]["review_dimension"],
            row["binding"]["target_identifier"],
            row["review_item_id"],
        )
    )
    dimension_counts = Counter(row["binding"]["review_dimension"] for row in rows)
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
        "planner_schema_version": migration.SCHEMA_VERSION,
        "planner_plan_id": planner_summary["plan_id"],
        "planner_rows_sha256": planner_summary["rows_sha256"],
        "review_item_count": len(rows),
        "review_dimension_counts": dict(sorted(dimension_counts.items())),
        "decision_options": {
            dimension: list(options) for dimension, options in sorted(DECISION_OPTIONS.items())
        },
        "route_targets": copy.deepcopy(ROUTE_TARGETS),
        "route_consistency_policy": (
            "EVERY_RETAINED_SOURCE_PARENT_EDGE_REQUIRES_IDENTICAL_CHILD_AND_PARENT_ROUTE"
        ),
        "bindings_sha256": rows_sha256(bindings),
        "template_rows_sha256": rows_sha256(rows),
        "review_scope": (
            "SEMANTIC_ROUTING_LABEL_DEFINITION_PROFILE_AND_MODELLESS_DISPOSITION_ONLY_"
            "NO_SERIALIZATION_OR_GROUNDING_AUTHORIZATION"
        ),
        "writes_performed": False,
        "writer_available": False,
        "apply_authorized": False,
        "serialization_status": "NOT_PERFORMED",
        "grounding_eligible": False,
        "grounding_gate": migration.GROUNDING_GATE,
    }
    summary["template_id"] = TEMPLATE_ID_PREFIX + value_sha256(summary)
    return rows, summary


def dump_review_template(rows: Iterable[Mapping[str, Any]], summary: Mapping[str, Any]) -> str:
    return "".join(canonical_json(row) + "\n" for row in [*rows, summary])


def _read_completed_ledger(
    path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any], bytes]:
    raw = _capture_regular_file(
        path,
        label="SFLD completed review ledger",
        max_bytes=MAX_LEDGER_BYTES,
    )
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise SfldMigrationReviewError("completed ledger is not valid UTF-8") from error
    lines = _exact_lf_lines(text, label="completed ledger")
    values = [
        _load_canonical_json_line(line, label=f"completed ledger line {line_number}")
        for line_number, line in enumerate(lines, 1)
    ]
    if len(values) < 2:
        raise SfldMigrationReviewError("completed ledger must contain decisions and a summary")
    return values[:-1], values[-1], raw


def _validate_review_metadata(value: Any, *, dimension: str, item_id: str) -> dict[str, str]:
    if type(value) is not dict or set(value) != _DECISION_FIELDS:
        raise SfldMigrationReviewError(f"{item_id}: decision fields differ from contract")
    action = value.get("action")
    if action not in DECISION_OPTIONS[dimension]:
        raise SfldMigrationReviewError(f"{item_id}: invalid or missing review action")
    reviewer = value.get("reviewer")
    if (
        not isinstance(reviewer, str)
        or reviewer != reviewer.strip()
        or not reviewer
        or len(reviewer) > 200
        or any(ord(character) < 32 for character in reviewer)
    ):
        raise SfldMigrationReviewError(f"{item_id}: reviewer is malformed")
    reviewed_at = value.get("reviewed_at")
    if not isinstance(reviewed_at, str) or _REVIEWED_AT_RE.fullmatch(reviewed_at) is None:
        raise SfldMigrationReviewError(f"{item_id}: reviewed_at must be exact UTC seconds")
    try:
        datetime.strptime(reviewed_at, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise SfldMigrationReviewError(f"{item_id}: reviewed_at is not a real timestamp") from error
    comment = value.get("comment")
    if not isinstance(comment, str) or len(comment) > 4000 or "\x00" in comment:
        raise SfldMigrationReviewError(f"{item_id}: comment is malformed")
    return {
        "action": action,
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "comment": comment,
    }


def _decision_is_compatible(dimension: str, action: str) -> bool:
    if dimension == ROUTING_DIMENSION:
        return action in ROUTE_TARGETS
    return action == _COMPATIBLE_FIXED_DECISIONS.get(dimension)


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
        raise SfldMigrationReviewError("completed ledger template summary is stale or altered")
    if len(supplied_rows) != len(expected_rows):
        raise SfldMigrationReviewError("completed ledger decision-row count mismatch")
    if not ledger_bytes:
        raise SfldMigrationReviewError("completed ledger byte stream is empty")
    canonical_ledger = dump_review_template(supplied_rows, supplied_summary).encode("utf-8")
    if ledger_bytes != canonical_ledger:
        raise SfldMigrationReviewError(
            "completed ledger bytes do not match supplied canonical decision objects"
        )

    decisions: list[dict[str, Any]] = []
    seen_items: set[str] = set()
    compatible = True
    routing_by_identifier: dict[str, dict[str, Any]] = {}
    for index, (supplied_raw, expected_raw) in enumerate(zip(supplied_rows, expected_rows), 1):
        supplied = dict(supplied_raw)
        expected = dict(expected_raw)
        if set(supplied) != _ROW_FIELDS:
            raise SfldMigrationReviewError(f"decision row {index}: fields differ from contract")
        item_id = supplied.get("review_item_id")
        if not isinstance(item_id, str) or item_id in seen_items:
            raise SfldMigrationReviewError(f"decision row {index}: duplicate/malformed item ID")
        seen_items.add(item_id)
        for field in _ROW_FIELDS - {"decision"}:
            if supplied.get(field) != expected.get(field):
                raise SfldMigrationReviewError(
                    f"{item_id}: immutable review binding field {field!r} changed"
                )
        binding = supplied["binding"]
        if supplied["binding_sha256"] != value_sha256(binding):
            raise SfldMigrationReviewError(f"{item_id}: binding hash mismatch")
        dimension = binding.get("review_dimension")
        if dimension not in DECISION_OPTIONS:
            raise SfldMigrationReviewError(f"{item_id}: unknown review dimension")
        metadata = _validate_review_metadata(
            supplied.get("decision"),
            dimension=dimension,
            item_id=item_id,
        )
        if not _decision_is_compatible(dimension, metadata["action"]):
            compatible = False
        decision: dict[str, Any] = {
            "review_item_id": item_id,
            "binding_sha256": supplied["binding_sha256"],
            "target_identifier": binding["target_identifier"],
            "review_dimension": dimension,
            **metadata,
        }
        if dimension == ROUTING_DIMENSION and metadata["action"] in ROUTE_TARGETS:
            decision["selected_route"] = copy.deepcopy(ROUTE_TARGETS[metadata["action"]])
            routing_by_identifier[binding["target_identifier"]] = {
                "action": metadata["action"],
                "selected_route": copy.deepcopy(ROUTE_TARGETS[metadata["action"]]),
                "source_parent_traits": copy.deepcopy(binding["source_parent_traits"]),
            }
        decisions.append(decision)

    cross_route_edges: list[dict[str, str]] = []
    for child, routing in sorted(routing_by_identifier.items()):
        parents = routing["source_parent_traits"]
        if not parents:
            continue
        parent = parents[0]
        parent_routing = routing_by_identifier.get(parent)
        if parent_routing is None:
            compatible = False
            cross_route_edges.append(
                {
                    "child": child,
                    "parent": parent,
                    "status": "PARENT_HAS_NO_COMPATIBLE_ROUTE_SELECTION",
                }
            )
        elif routing["selected_route"] != parent_routing["selected_route"]:
            compatible = False
            cross_route_edges.append(
                {
                    "child": child,
                    "parent": parent,
                    "status": "CROSS_ROUTE_SOURCE_PARENT_EDGE_REQUIRES_REPLAN",
                }
            )

    decision_counts = Counter(row["action"] for row in decisions)
    route_counts = Counter(
        row["action"] for row in decisions if row["review_dimension"] == ROUTING_DIMENSION
    )
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
        "routing_decision_counts": dict(sorted(route_counts.items())),
        "cross_route_source_parent_edge_count": len(cross_route_edges),
        "cross_route_source_parent_edges": cross_route_edges,
        "decision_rows_sha256": rows_sha256(decisions),
        "ledger_sha256": hashlib.sha256(ledger_bytes).hexdigest(),
        "review_scope": expected_summary["review_scope"],
        "apply_authorized": False,
        "serialization_status": "NOT_PERFORMED",
        "writes_performed": False,
        "writer_available": False,
        "grounding_eligible": False,
        "grounding_gate": migration.GROUNDING_GATE,
    }
    if compatible:
        receipt["review_set_id"] = REVIEW_SET_ID_PREFIX + value_sha256(receipt)
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hmm", type=Path, default=migration.DEFAULT_HMM)
    parser.add_argument("--hierarchy", type=Path, default=migration.DEFAULT_HIERARCHY)
    parser.add_argument("--sites", type=Path, default=migration.DEFAULT_SITES)
    parser.add_argument("--manifest", type=Path, default=migration.DEFAULT_MANIFEST)
    parser.add_argument("--interpro", type=Path, default=migration.DEFAULT_INTERPRO)
    parser.add_argument("--traits", type=Path, default=migration.DEFAULT_TRAITS)
    parser.add_argument(
        "--ledger",
        type=Path,
        help="completed copy of the emitted template; validation remains stdout-only",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        planner_rows, planner_summary = replay_migration_plan(args)
        template_rows, template_summary = build_review_template(
            planner_rows,
            planner_summary,
        )
        if args.ledger is None:
            sys.stdout.write(dump_review_template(template_rows, template_summary))
            return 0
        supplied_rows, supplied_summary, raw = _read_completed_ledger(args.ledger)
        receipt = validate_completed_ledger(
            supplied_rows,
            supplied_summary,
            expected_rows=template_rows,
            expected_summary=template_summary,
            ledger_bytes=raw,
        )
    except (SfldMigrationReviewError, migration.SfldMigrationPlanError, OSError) as error:
        print(f"refusing SFLD migration review: {error}", file=sys.stderr)
        return 2
    print(canonical_json(receipt))
    return 0 if receipt["accepted_for_next_phase"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
