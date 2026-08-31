#!/usr/bin/env python3
"""Prepare and validate a review ledger for the PRINTS migration plan.

This command is deliberately stdout-only.  It replays
``migrate_prints_source_model.py`` against the pinned local source snapshot and
either emits an exhaustive review template or validates a completed copy of
that template.  It never serializes or writes a trait, grounding object, or
review artifact.

The template summary remains unchanged when reviewers fill its decision rows.
Validation replays the migration plan again and requires every immutable row
binding and the trailing template summary to match that fresh replay exactly.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import io
import json
import os
import re
import stat
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

import migrate_prints_source_model as migration

SCHEMA_VERSION = 2
DECISION_ROW_KIND = "PRINTS_MIGRATION_REVIEW_DECISION"
TEMPLATE_SUMMARY_KIND = "PRINTS_MIGRATION_REVIEW_TEMPLATE_SUMMARY"
RECEIPT_KIND = "PRINTS_MIGRATION_REVIEW_RECEIPT"
TEMPLATE_ID_PREFIX = "prints-migration-review-template:"
REVIEW_SET_ID_PREFIX = "prints-migration-review-set:"
MAX_LEDGER_BYTES = 64 * 1024 * 1024
_READ_CHUNK_BYTES = 1024 * 1024

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REVIEWED_AT = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")

DECISION_OPTIONS: dict[str, tuple[str, ...]] = {
    "RECORD_REVIEW": (
        "APPROVE_SOURCE_NATIVE_CONTENT",
        "BLOCK_CONTENT_MIGRATION",
        "REQUEST_CONTENT_REPLAN",
    ),
    "ROUTING_REVIEW": (
        "KEEP_PRINTS_MEMBER_ROUTE",
        "BLOCK_ROUTING_MIGRATION",
        "REQUEST_ROUTING_REPLAN",
    ),
    "HIERARCHY_REPAIR": (
        "REMOVE_CONFIRMED_LEGACY_GENERATED_PARENT",
        "BLOCK_HIERARCHY_REPAIR",
        "REQUEST_HIERARCHY_REPLAN",
    ),
}

COMPATIBLE_DECISIONS = {
    "RECORD_REVIEW": "APPROVE_SOURCE_NATIVE_CONTENT",
    "ROUTING_REVIEW": "KEEP_PRINTS_MEMBER_ROUTE",
    "HIERARCHY_REPAIR": "REMOVE_CONFIRMED_LEGACY_GENERATED_PARENT",
}

_DECISION_FIELDS = frozenset({"decision", "reviewer", "reviewed_at", "comment"})
_ROW_FIELDS = frozenset({"schema_version", "kind", "binding", "binding_sha256", "decisions"})

_PLANNER_REVIEW_CONTEXT_FIELDS = frozenset(
    {
        "normalized_hierarchy_row",
        "normalized_hierarchy_row_sha256",
        "normalized_hierarchy_domain_flag",
        "member_type_is_domain",
        "member_hierarchy_domain_alignment",
        "record_review_value_projections",
        "record_review_value_projections_sha256",
    }
)
_PLANNER_REVIEW_SUMMARY_FIELDS = frozenset(
    {
        "normalized_hierarchy_row_count",
        "normalized_hierarchy_projection_sha256",
        "normalized_hierarchy_domain_count",
        "member_hierarchy_domain_alignment_counts",
        "routing_review_member_hierarchy_domain_alignment_counts",
    }
)


class PrintsMigrationReviewError(ValueError):
    """The review template or completed ledger is not exactly replayable."""


def canonical_json(value: Any) -> str:
    return migration.canonical_json(value)


def value_sha256(value: Any) -> str:
    return migration.value_sha256(value)


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise PrintsMigrationReviewError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _load_canonical_json_line(line: str, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(line, object_pairs_hook=_unique_json_object)
    except (json.JSONDecodeError, PrintsMigrationReviewError) as error:
        raise PrintsMigrationReviewError(f"{label}: invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise PrintsMigrationReviewError(f"{label}: expected a JSON object")
    if canonical_json(value) != line:
        raise PrintsMigrationReviewError(f"{label}: JSON is not canonical")
    return value


def _exact_lf_lines(text: str, *, label: str) -> list[str]:
    """Split an exact LF-framed stream without accepting Unicode line aliases."""

    forbidden = {
        "\r": "CR/CRLF",
        "\u0085": "U+0085",
        "\u2028": "U+2028",
        "\u2029": "U+2029",
    }
    for character, name in forbidden.items():
        if character in text:
            raise PrintsMigrationReviewError(f"{label}: forbidden {name} line separator")
    if not text or not text.endswith("\n"):
        raise PrintsMigrationReviewError(f"{label}: must be non-empty and LF-terminated")
    lines = text[:-1].split("\n")
    if any(not line for line in lines):
        raise PrintsMigrationReviewError(f"{label}: blank lines are forbidden")
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
        raise PrintsMigrationReviewError(f"{label}: invalid capture byte limit")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise PrintsMigrationReviewError(
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
        raise PrintsMigrationReviewError(f"{label}: path must have ordinary components: {path}")

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
            raise PrintsMigrationReviewError(
                f"{label}: cannot open path root for {path}: {error}"
            ) from error
        descriptors.append(current)
        for component in component_names[:-1]:
            try:
                child = os.open(component, directory_flags, dir_fd=current)
                descriptors.append(child)
                child_metadata = os.fstat(child)
            except OSError as error:
                raise PrintsMigrationReviewError(
                    f"{label}: cannot safely open directory component {component!r}: {error}"
                ) from error
            bindings.append((current, component, _entry_identity(child_metadata)))
            current = child

        final_name = component_names[-1]
        try:
            file_descriptor = os.open(final_name, file_flags, dir_fd=current)
            descriptors.append(file_descriptor)
            before = os.fstat(file_descriptor)
        except OSError as error:
            raise PrintsMigrationReviewError(
                f"{label}: cannot safely open regular file {path}: {error}"
            ) from error
        bindings.append((current, final_name, _entry_identity(before)))
        if not stat.S_ISREG(before.st_mode):
            raise PrintsMigrationReviewError(f"{label}: input is not a regular file: {path}")
        if before.st_size < 1 or before.st_size > max_bytes:
            raise PrintsMigrationReviewError(
                f"{label}: input size {before.st_size} is outside 1..{max_bytes} bytes"
            )

        chunks: list[bytes] = []
        captured_bytes = 0
        while True:
            try:
                chunk = os.read(
                    file_descriptor,
                    min(_READ_CHUNK_BYTES, max_bytes - captured_bytes + 1),
                )
            except OSError as error:
                raise PrintsMigrationReviewError(f"{label}: read failed: {error}") from error
            if not chunk:
                break
            chunks.append(chunk)
            captured_bytes += len(chunk)
            if captured_bytes > max_bytes:
                raise PrintsMigrationReviewError(
                    f"{label}: input exceeds the {max_bytes}-byte limit"
                )
        raw = b"".join(chunks)
        after = os.fstat(file_descriptor)
        if len(raw) != before.st_size or _content_identity(after) != _content_identity(before):
            raise PrintsMigrationReviewError(f"{label}: input changed during capture")

        for parent_descriptor, component, expected_identity in bindings:
            try:
                live = os.stat(component, dir_fd=parent_descriptor, follow_symlinks=False)
            except OSError as error:
                raise PrintsMigrationReviewError(
                    f"{label}: path component changed during capture: {component!r}: {error}"
                ) from error
            if _entry_identity(live) != expected_identity:
                raise PrintsMigrationReviewError(
                    f"{label}: path component changed during capture: {component!r}"
                )
        return raw
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _parse_plan_stdout(text: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    lines = _exact_lf_lines(text, label="migration planner stdout")
    payloads = [
        _load_canonical_json_line(line, label=f"migration plan line {number}")
        for number, line in enumerate(lines, 1)
    ]
    rows, summary = payloads[:-1], payloads[-1]
    if summary.get("kind") != migration.SUMMARY_KIND:
        raise PrintsMigrationReviewError("migration planner lacks one trailing summary")
    if summary.get("schema_version") != migration.SCHEMA_VERSION:
        raise PrintsMigrationReviewError("migration planner summary schema mismatch")
    if summary.get("record_count") != len(rows):
        raise PrintsMigrationReviewError("migration planner row count mismatch")

    identifiers: list[str] = []
    for number, row in enumerate(rows, 1):
        if row.get("kind") != migration.ROW_KIND:
            raise PrintsMigrationReviewError(f"migration plan row {number}: wrong kind")
        if row.get("schema_version") != migration.SCHEMA_VERSION:
            raise PrintsMigrationReviewError(f"migration plan row {number}: schema mismatch")
        identifier = row.get("identifier")
        if not isinstance(identifier, str):
            raise PrintsMigrationReviewError(
                f"migration plan row {number}: missing string identifier"
            )
        identifiers.append(identifier)
        row_copy = copy.deepcopy(row)
        row_sha256 = row_copy.pop("row_sha256", None)
        if not isinstance(row_sha256, str) or not _SHA256.fullmatch(row_sha256):
            raise PrintsMigrationReviewError(f"migration plan row {identifier}: invalid row_sha256")
        if row_sha256 != value_sha256(row_copy):
            raise PrintsMigrationReviewError(
                f"migration plan row {identifier}: row_sha256 does not replay"
            )
    if identifiers != sorted(identifiers) or len(set(identifiers)) != len(identifiers):
        raise PrintsMigrationReviewError(
            "migration planner rows must have unique sorted identifiers"
        )

    rows_bytes = "".join(canonical_json(row) + "\n" for row in rows).encode("utf-8")
    if hashlib.sha256(rows_bytes).hexdigest() != summary.get("rows_sha256"):
        raise PrintsMigrationReviewError("migration planner rows_sha256 does not replay")
    summary_copy = copy.deepcopy(summary)
    plan_id = summary_copy.pop("plan_id", None)
    if plan_id != migration.PLAN_ID_PREFIX + value_sha256(summary_copy):
        raise PrintsMigrationReviewError("migration planner plan_id does not replay")
    return rows, summary


def _planner_argv(args: argparse.Namespace) -> list[str]:
    values = (
        ("--api", args.api),
        ("--kdat", args.kdat),
        ("--hierarchy", args.hierarchy),
        ("--legacy-hierarchy-source", args.legacy_hierarchy_source),
        ("--manifest", args.manifest),
        ("--interpro", args.interpro),
        ("--traits", args.traits),
    )
    return [item for option, path in values for item in (option, str(path))]


def replay_migration_plan(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay the existing planner and authenticate its canonical stdout."""

    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        status = migration.main(_planner_argv(args))
    if status != 0:
        detail = stderr.getvalue().strip() or stdout.getvalue().strip() or "unknown error"
        raise PrintsMigrationReviewError(f"migration plan replay failed: {detail}")
    return _parse_plan_stdout(stdout.getvalue())


def _require_plan_sha(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise PrintsMigrationReviewError(f"invalid {label} in migration plan")
    return value


def _planner_review_context(row: Mapping[str, Any]) -> dict[str, Any]:
    """Authenticate the planner's mandatory explicit reviewer context."""

    present = _PLANNER_REVIEW_CONTEXT_FIELDS.intersection(row)
    if present != _PLANNER_REVIEW_CONTEXT_FIELDS:
        missing = sorted(_PLANNER_REVIEW_CONTEXT_FIELDS - present)
        raise PrintsMigrationReviewError(
            f"{row.get('identifier')}: incomplete planner review context; missing={missing}"
        )

    hierarchy_row = row.get("normalized_hierarchy_row")
    hierarchy_fields = {
        "accession",
        "code",
        "domain_flag",
        "evalue_cutoff",
        "hierarchical_relations",
        "minimum_motif_count",
    }
    if not isinstance(hierarchy_row, dict) or set(hierarchy_row) != hierarchy_fields:
        raise PrintsMigrationReviewError(
            f"{row.get('identifier')}: normalized hierarchy row fields are not exact"
        )
    hierarchy_sha256 = _require_plan_sha(
        row.get("normalized_hierarchy_row_sha256"),
        label="normalized_hierarchy_row_sha256",
    )
    if hierarchy_sha256 != value_sha256(hierarchy_row):
        raise PrintsMigrationReviewError(
            f"{row.get('identifier')}: normalized hierarchy row hash does not replay"
        )
    identifier = row.get("identifier")
    expected_accession = identifier.split(":", 1)[1] if isinstance(identifier, str) else None
    if hierarchy_row.get("accession") != expected_accession:
        raise PrintsMigrationReviewError(
            f"{identifier}: normalized hierarchy accession does not match identifier"
        )
    hierarchy_domain = row.get("normalized_hierarchy_domain_flag")
    member_is_domain = row.get("member_type_is_domain")
    if type(hierarchy_domain) is not bool or hierarchy_domain != hierarchy_row.get("domain_flag"):
        raise PrintsMigrationReviewError(
            f"{identifier}: normalized hierarchy domain flag does not replay"
        )
    if type(member_is_domain) is not bool or member_is_domain != (
        row.get("member_type") == "domain"
    ):
        raise PrintsMigrationReviewError(f"{identifier}: member domain flag does not replay")
    alignment = row.get("member_hierarchy_domain_alignment")
    expected_alignment = "AGREES" if member_is_domain == hierarchy_domain else "DISAGREES"
    if alignment != expected_alignment:
        raise PrintsMigrationReviewError(
            f"{identifier}: member/hierarchy domain alignment does not replay"
        )

    projections = row.get("record_review_value_projections")
    if not isinstance(projections, dict) or set(projections) != set(
        row.get("legacy_mismatch_fields") or []
    ):
        raise PrintsMigrationReviewError(
            f"{identifier}: record review projections do not exactly cover mismatch fields"
        )
    projection_sha256 = _require_plan_sha(
        row.get("record_review_value_projections_sha256"),
        label="record_review_value_projections_sha256",
    )
    if projection_sha256 != value_sha256(projections):
        raise PrintsMigrationReviewError(
            f"{identifier}: record review projection hash does not replay"
        )
    for field_name, projection in projections.items():
        if not isinstance(projection, dict) or set(projection) != {
            "current",
            "legacy_expected",
            "proposed",
        }:
            raise PrintsMigrationReviewError(
                f"{identifier}/{field_name}: record review projection fields are not exact"
            )
        for state_name, state in projection.items():
            if not isinstance(state, dict) or set(state) != {"present", "value"}:
                raise PrintsMigrationReviewError(
                    f"{identifier}/{field_name}/{state_name}: value projection is not exact"
                )
            if type(state.get("present")) is not bool:
                raise PrintsMigrationReviewError(
                    f"{identifier}/{field_name}/{state_name}: present must be boolean"
                )
            if not state["present"] and state.get("value") is not None:
                raise PrintsMigrationReviewError(
                    f"{identifier}/{field_name}/{state_name}: absent value must be null"
                )

    return {
        "normalized_hierarchy_row": copy.deepcopy(hierarchy_row),
        "normalized_hierarchy_row_sha256": hierarchy_sha256,
        "normalized_hierarchy_domain_flag": hierarchy_domain,
        "member_type_is_domain": member_is_domain,
        "member_hierarchy_domain_alignment": alignment,
        "record_review_value_projections": copy.deepcopy(projections),
        "record_review_value_projections_sha256": projection_sha256,
    }


def _planner_review_summary_context(
    summary: Mapping[str, Any],
    *,
    rows: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Replay the mandatory hierarchy aggregates against every planner row."""

    missing = sorted(_PLANNER_REVIEW_SUMMARY_FIELDS - set(summary))
    if missing:
        raise PrintsMigrationReviewError(
            f"migration summary lacks mandatory review context; missing={missing}"
        )
    row_count = summary.get("record_count")
    hierarchy_count = summary.get("normalized_hierarchy_row_count")
    domain_count = summary.get("normalized_hierarchy_domain_count")
    plan_rows = list(rows)
    identifiers = [row.get("identifier") for row in plan_rows]
    if (
        any(not isinstance(identifier, str) for identifier in identifiers)
        or identifiers != sorted(identifiers)
        or len(set(identifiers)) != len(identifiers)
    ):
        raise PrintsMigrationReviewError(
            "migration rows must have unique sorted identifiers for review summary replay"
        )
    row_contexts = [_planner_review_context(row) for row in plan_rows]
    if (
        type(row_count) is not int
        or row_count != len(row_contexts)
        or type(hierarchy_count) is not int
        or hierarchy_count != row_count
        or type(domain_count) is not int
        or domain_count < 0
        or domain_count > hierarchy_count
    ):
        raise PrintsMigrationReviewError("migration hierarchy summary counts do not replay")
    hierarchy_projection_sha256 = _require_plan_sha(
        summary.get("normalized_hierarchy_projection_sha256"),
        label="normalized_hierarchy_projection_sha256",
    )
    expected_hierarchy_projection_sha256 = value_sha256(
        [context["normalized_hierarchy_row"] for context in row_contexts]
    )
    if hierarchy_projection_sha256 != expected_hierarchy_projection_sha256:
        raise PrintsMigrationReviewError(
            "migration normalized hierarchy projection hash does not replay"
        )
    if domain_count != sum(context["normalized_hierarchy_domain_flag"] for context in row_contexts):
        raise PrintsMigrationReviewError(
            "migration normalized hierarchy domain count does not replay"
        )

    alignment_counts = summary.get("member_hierarchy_domain_alignment_counts")
    routing_alignment_counts = summary.get(
        "routing_review_member_hierarchy_domain_alignment_counts"
    )
    for label, counts in (
        ("member hierarchy alignment counts", alignment_counts),
        ("routing review hierarchy alignment counts", routing_alignment_counts),
    ):
        if (
            not isinstance(counts, dict)
            or not set(counts).issubset({"AGREES", "DISAGREES"})
            or any(type(value) is not int or value < 0 for value in counts.values())
        ):
            raise PrintsMigrationReviewError(f"migration {label} are invalid")
    expected_alignment_counts = dict(
        sorted(
            Counter(
                context["member_hierarchy_domain_alignment"] for context in row_contexts
            ).items()
        )
    )
    if alignment_counts != expected_alignment_counts:
        raise PrintsMigrationReviewError(
            "migration member hierarchy alignment counts do not replay"
        )
    route_status_counts = summary.get("route_status_counts")
    routing_review_count = (
        route_status_counts.get("ROUTING_REVIEW") if isinstance(route_status_counts, dict) else None
    )
    expected_routing_alignment_counts = dict(
        sorted(
            Counter(
                context["member_hierarchy_domain_alignment"]
                for row, context in zip(plan_rows, row_contexts)
                if row.get("route_status") == "ROUTING_REVIEW"
            ).items()
        )
    )
    if (
        type(routing_review_count) is not int
        or routing_review_count != sum(expected_routing_alignment_counts.values())
        or routing_alignment_counts != expected_routing_alignment_counts
    ):
        raise PrintsMigrationReviewError(
            "migration routing review hierarchy alignment counts do not replay"
        )
    return {
        "normalized_hierarchy_row_count": hierarchy_count,
        "normalized_hierarchy_projection_sha256": hierarchy_projection_sha256,
        "normalized_hierarchy_domain_count": domain_count,
        "member_hierarchy_domain_alignment_counts": copy.deepcopy(alignment_counts),
        "routing_review_member_hierarchy_domain_alignment_counts": copy.deepcopy(
            routing_alignment_counts
        ),
    }


def _binding(
    row: Mapping[str, Any],
    summary: Mapping[str, Any],
    *,
    planner_context: Mapping[str, Any],
    planner_summary_context: Mapping[str, Any],
) -> dict[str, Any]:
    requirements = row.get("review_requirements")
    if not isinstance(requirements, list) or not requirements:
        raise PrintsMigrationReviewError(
            f"{row.get('identifier')}: review row lacks review_requirements"
        )
    if any(requirement not in DECISION_OPTIONS for requirement in requirements):
        unknown = sorted(
            str(requirement) for requirement in requirements if requirement not in DECISION_OPTIONS
        )
        raise PrintsMigrationReviewError(
            f"{row.get('identifier')}: unsupported review requirements {unknown}"
        )
    if len(set(requirements)) != len(requirements):
        raise PrintsMigrationReviewError(f"{row.get('identifier')}: duplicate review requirement")
    record_facts = {
        "record_state": row.get("record_state"),
        "legacy_mismatch_fields": copy.deepcopy(row.get("legacy_mismatch_fields")),
        "changed_fields": copy.deepcopy(row.get("changed_fields")),
        "content_proposal_semantic_sha256": row.get("content_proposal_semantic_sha256"),
    }
    routing_facts = {
        "route_status": row.get("route_status"),
        "current_route": copy.deepcopy(row.get("current_route")),
        "member_type": row.get("member_type"),
        "member_route": copy.deepcopy(row.get("member_route")),
        "integrating_interpro": row.get("integrating_interpro"),
        "integrating_interpro_type": row.get("integrating_interpro_type"),
        "integrating_interpro_route": copy.deepcopy(row.get("integrating_interpro_route")),
    }
    hierarchy_facts = {
        "hierarchy_status": row.get("hierarchy_status"),
        "confirmed_legacy_generated_parent": row.get("confirmed_legacy_generated_parent"),
        "remove_fields": copy.deepcopy(row.get("remove_fields")),
        "source_semantics": row.get("hierarchy_source_semantics"),
    }
    record_facts.update(
        {
            "record_review_value_projections": planner_context["record_review_value_projections"],
            "record_review_value_projections_sha256": planner_context[
                "record_review_value_projections_sha256"
            ],
        }
    )
    routing_facts.update(
        {
            "member_type_is_domain": planner_context["member_type_is_domain"],
            "member_hierarchy_domain_alignment": planner_context[
                "member_hierarchy_domain_alignment"
            ],
        }
    )
    hierarchy_facts.update(
        {
            "normalized_hierarchy_row": planner_context["normalized_hierarchy_row"],
            "normalized_hierarchy_row_sha256": planner_context["normalized_hierarchy_row_sha256"],
            "normalized_hierarchy_domain_flag": planner_context["normalized_hierarchy_domain_flag"],
        }
    )

    return {
        "snapshot_manifest_id": summary.get("snapshot_manifest_id"),
        "migration_plan_id": summary.get("plan_id"),
        "migration_rows_sha256": _require_plan_sha(summary.get("rows_sha256"), label="rows_sha256"),
        "source_release": summary.get("source_release"),
        "source_artifact_sha256": _require_plan_sha(
            summary.get("source_artifact_sha256"), label="source_artifact_sha256"
        ),
        "legacy_parent_replay_source_sha256": _require_plan_sha(
            summary.get("legacy_parent_replay_source_sha256"),
            label="legacy_parent_replay_source_sha256",
        ),
        "planner_review_summary": planner_summary_context,
        "plan_row_sha256": _require_plan_sha(row.get("row_sha256"), label="row_sha256"),
        "source_record_sha256": _require_plan_sha(
            row.get("source_record_sha256"), label="source_record_sha256"
        ),
        "motif_count": row.get("motif_count"),
        "identifier": row.get("identifier"),
        "record_path": row.get("record_path"),
        "current_record_yaml_sha256": _require_plan_sha(
            row.get("current_record_yaml_sha256"), label="current_record_yaml_sha256"
        ),
        "review_requirements": list(requirements),
        "record_facts": record_facts,
        "routing_facts": routing_facts,
        "hierarchy_facts": hierarchy_facts,
        "path_facts": {
            "path_status": row.get("path_status"),
            "expected_record_directory": row.get("expected_record_directory"),
        },
    }


def build_review_template(
    rows: Iterable[Mapping[str, Any]], summary: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Project every blocked plan row into one deterministic review template."""

    plan_rows = list(rows)
    planner_summary_context = _planner_review_summary_context(summary, rows=plan_rows)
    planner_contexts = {row["identifier"]: _planner_review_context(row) for row in plan_rows}
    template_rows: list[dict[str, Any]] = []
    requirement_counts: Counter[str] = Counter()
    for plan_row in plan_rows:
        requirements = plan_row.get("review_requirements")
        if not requirements:
            continue
        binding = _binding(
            plan_row,
            summary,
            planner_context=planner_contexts[plan_row.get("identifier")],
            planner_summary_context=planner_summary_context,
        )
        requirement_counts.update(binding["review_requirements"])
        template_rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "kind": DECISION_ROW_KIND,
                "binding": binding,
                "binding_sha256": value_sha256(binding),
                "decisions": {
                    requirement: {
                        "decision": "PENDING",
                        "reviewer": "",
                        "reviewed_at": "",
                        "comment": "",
                    }
                    for requirement in binding["review_requirements"]
                },
            }
        )
    template_rows.sort(key=lambda row: row["binding"]["identifier"])

    expected_count = summary.get("review_required_count")
    if expected_count != len(template_rows):
        raise PrintsMigrationReviewError(
            "migration summary review_required_count does not match review rows"
        )
    template_rows_bytes = "".join(canonical_json(row) + "\n" for row in template_rows).encode(
        "utf-8"
    )
    template_summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": TEMPLATE_SUMMARY_KIND,
        "status": "PENDING_REVIEW",
        "snapshot_manifest_id": summary.get("snapshot_manifest_id"),
        "migration_plan_id": summary.get("plan_id"),
        "migration_rows_sha256": summary.get("rows_sha256"),
        "source_release": summary.get("source_release"),
        "source_artifact_sha256": summary.get("source_artifact_sha256"),
        "legacy_parent_replay_source_sha256": summary.get("legacy_parent_replay_source_sha256"),
        "planner_review_summary": planner_summary_context,
        "review_row_count": len(template_rows),
        "review_dimension_count": sum(requirement_counts.values()),
        "requirement_counts": dict(sorted(requirement_counts.items())),
        "decision_options": {
            requirement: list(DECISION_OPTIONS[requirement])
            for requirement in sorted(requirement_counts)
        },
        "template_rows_sha256": hashlib.sha256(template_rows_bytes).hexdigest(),
    }
    template_summary["template_id"] = TEMPLATE_ID_PREFIX + value_sha256(template_summary)
    return template_rows, template_summary


def dump_review_template(rows: Iterable[Mapping[str, Any]], summary: Mapping[str, Any]) -> str:
    template_rows, template_summary = build_review_template(rows, summary)
    return "".join(canonical_json(value) + "\n" for value in [*template_rows, template_summary])


def _read_completed_ledger(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any], bytes]:
    try:
        raw = _capture_regular_file(
            path,
            label="PRINTS migration review ledger",
            max_bytes=MAX_LEDGER_BYTES,
        )
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise PrintsMigrationReviewError(f"cannot read review ledger {path}: {error}") from error
    lines = _exact_lf_lines(text, label="review ledger")
    values = [
        _load_canonical_json_line(line, label=f"review ledger line {number}")
        for number, line in enumerate(lines, 1)
    ]
    return values[:-1], values[-1], raw


def _validate_review_metadata(
    value: Mapping[str, Any], *, identifier: str, requirement: str
) -> None:
    if set(value) != _DECISION_FIELDS:
        raise PrintsMigrationReviewError(
            f"{identifier}/{requirement}: decision fields must be exact"
        )
    decision = value.get("decision")
    if decision not in DECISION_OPTIONS[requirement]:
        raise PrintsMigrationReviewError(
            f"{identifier}/{requirement}: invalid or pending decision {decision!r}"
        )
    reviewer = value.get("reviewer")
    if (
        not isinstance(reviewer, str)
        or not reviewer
        or reviewer != reviewer.strip()
        or len(reviewer) > 200
    ):
        raise PrintsMigrationReviewError(
            f"{identifier}/{requirement}: reviewer must be a non-empty trimmed string"
        )
    reviewed_at = value.get("reviewed_at")
    if not isinstance(reviewed_at, str) or _REVIEWED_AT.fullmatch(reviewed_at) is None:
        raise PrintsMigrationReviewError(
            f"{identifier}/{requirement}: reviewed_at must be UTC YYYY-MM-DDTHH:MM:SSZ"
        )
    try:
        datetime.strptime(reviewed_at, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise PrintsMigrationReviewError(
            f"{identifier}/{requirement}: reviewed_at is not a real UTC timestamp"
        ) from error
    comment = value.get("comment")
    if not isinstance(comment, str) or comment != comment.strip() or len(comment) > 4000:
        raise PrintsMigrationReviewError(
            f"{identifier}/{requirement}: comment must be a trimmed string"
        )
    if (
        requirement != "HIERARCHY_REPAIR" or decision != COMPATIBLE_DECISIONS["HIERARCHY_REPAIR"]
    ) and not comment:
        raise PrintsMigrationReviewError(f"{identifier}/{requirement}: comment must be non-empty")


def _decision_is_proposal_compatible(
    *, binding: Mapping[str, Any], requirement: str, decision: str
) -> bool:
    if decision != COMPATIBLE_DECISIONS[requirement]:
        return False
    if requirement == "ROUTING_REVIEW":
        routing_facts = binding.get("routing_facts")
        if not isinstance(routing_facts, dict):
            return False
        if routing_facts.get("member_hierarchy_domain_alignment") != "AGREES":
            return False
    return True


def validate_completed_ledger(
    *,
    ledger_path: Path,
    plan_rows: Iterable[Mapping[str, Any]],
    plan_summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate an exact completed template and return a content-addressed receipt."""

    expected_rows, expected_summary = build_review_template(plan_rows, plan_summary)
    rows, supplied_summary, raw = _read_completed_ledger(ledger_path)
    if supplied_summary != expected_summary:
        raise PrintsMigrationReviewError(
            "review ledger template summary is stale or does not replay"
        )
    if len(rows) != len(expected_rows):
        raise PrintsMigrationReviewError("review ledger row set is incomplete or has extras")

    expected_identifiers = [row["binding"]["identifier"] for row in expected_rows]
    supplied_identifiers = [
        binding.get("identifier") if isinstance(binding := row.get("binding"), dict) else None
        for row in rows
    ]
    if (
        any(not isinstance(identifier, str) for identifier in supplied_identifiers)
        or len(set(supplied_identifiers)) != len(supplied_identifiers)
        or supplied_identifiers != expected_identifiers
    ):
        raise PrintsMigrationReviewError(
            "review ledger identifiers must be the exact unique sorted template set"
        )

    identifiers: list[str] = []
    decision_counts: dict[str, Counter[str]] = {
        requirement: Counter() for requirement in expected_summary["requirement_counts"]
    }
    reviewer_dimension_counts: Counter[str] = Counter()
    reviewed_at_values: list[str] = []
    incompatible_identifiers: set[str] = set()
    for supplied, expected in zip(rows, expected_rows):
        binding = supplied.get("binding")
        identifier = binding.get("identifier") if isinstance(binding, dict) else None
        if not isinstance(identifier, str):
            raise PrintsMigrationReviewError("review ledger row lacks a bound identifier")
        identifiers.append(identifier)
        if set(supplied) != _ROW_FIELDS:
            raise PrintsMigrationReviewError(f"{identifier}: review row fields must be exact")
        if supplied.get("schema_version") != SCHEMA_VERSION:
            raise PrintsMigrationReviewError(f"{identifier}: review row schema mismatch")
        if supplied.get("kind") != DECISION_ROW_KIND:
            raise PrintsMigrationReviewError(f"{identifier}: review row kind mismatch")
        if binding != expected["binding"]:
            raise PrintsMigrationReviewError(
                f"{identifier}: immutable review binding is stale or changed"
            )
        if supplied.get("binding_sha256") != expected["binding_sha256"]:
            raise PrintsMigrationReviewError(f"{identifier}: binding_sha256 does not replay")
        decisions = supplied.get("decisions")
        expected_requirements = expected["binding"]["review_requirements"]
        if not isinstance(decisions, dict) or set(decisions) != set(expected_requirements):
            raise PrintsMigrationReviewError(
                f"{identifier}: decisions must exactly cover review requirements"
            )
        for requirement in expected_requirements:
            decision_value = decisions[requirement]
            if not isinstance(decision_value, dict):
                raise PrintsMigrationReviewError(
                    f"{identifier}/{requirement}: decision must be an object"
                )
            _validate_review_metadata(
                decision_value,
                identifier=identifier,
                requirement=requirement,
            )
            decision = decision_value["decision"]
            decision_counts[requirement][decision] += 1
            reviewer_dimension_counts[decision_value["reviewer"]] += 1
            reviewed_at_values.append(decision_value["reviewed_at"])
            if not _decision_is_proposal_compatible(
                binding=binding,
                requirement=requirement,
                decision=decision,
            ):
                incompatible_identifiers.add(identifier)

    if identifiers != expected_identifiers:
        raise PrintsMigrationReviewError("review ledger identifier replay changed unexpectedly")

    decision_projection_sha256 = value_sha256(rows)
    incompatible_projection_sha256 = value_sha256(sorted(incompatible_identifiers))
    proposal_compatible = not incompatible_identifiers
    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": RECEIPT_KIND,
        "status": ("ACCEPTED_SEMANTIC_PLAN_ONLY" if proposal_compatible else "VALID_NON_ACCEPTING"),
        "proposal_compatible": proposal_compatible,
        "accepted_for_next_phase": proposal_compatible,
        "apply_authorized": False,
        "serialization_status": "NOT_PERFORMED",
        "trait_write_count": 0,
        "grounding_write_count": 0,
        "migration_review_outcome": (
            "ALL_REVIEW_DIMENSIONS_PROPOSAL_COMPATIBLE"
            if proposal_compatible
            else "BLOCKED_OR_REPLAN_REQUIRED"
        ),
        "snapshot_manifest_id": expected_summary["snapshot_manifest_id"],
        "migration_plan_id": expected_summary["migration_plan_id"],
        "migration_rows_sha256": expected_summary["migration_rows_sha256"],
        "source_release": expected_summary["source_release"],
        "source_artifact_sha256": expected_summary["source_artifact_sha256"],
        "legacy_parent_replay_source_sha256": expected_summary[
            "legacy_parent_replay_source_sha256"
        ],
        "template_id": expected_summary["template_id"],
        "template_rows_sha256": expected_summary["template_rows_sha256"],
        "review_row_count": len(rows),
        "review_dimension_count": sum(sum(counts.values()) for counts in decision_counts.values()),
        "requirement_counts": expected_summary["requirement_counts"],
        "decision_counts": {
            requirement: dict(sorted(counts.items()))
            for requirement, counts in sorted(decision_counts.items())
        },
        "reviewer_dimension_counts": dict(sorted(reviewer_dimension_counts.items())),
        "reviewed_at_min": min(reviewed_at_values),
        "reviewed_at_max": max(reviewed_at_values),
        "incompatible_record_count": len(incompatible_identifiers),
        "incompatible_identifier_projection_sha256": incompatible_projection_sha256,
        "decision_projection_sha256": decision_projection_sha256,
        "ledger_sha256": hashlib.sha256(raw).hexdigest(),
    }
    receipt["diagnostic_content_sha256"] = value_sha256(receipt)
    if proposal_compatible:
        receipt["review_set_id"] = REVIEW_SET_ID_PREFIX + value_sha256(receipt)
    return receipt


def _add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api", type=Path, default=migration.DEFAULT_API)
    parser.add_argument("--kdat", type=Path, default=migration.DEFAULT_KDAT)
    parser.add_argument("--hierarchy", type=Path, default=migration.DEFAULT_HIERARCHY)
    parser.add_argument(
        "--legacy-hierarchy-source",
        type=Path,
        default=migration.DEFAULT_HIERARCHY_SOURCE,
    )
    parser.add_argument("--manifest", type=Path, default=migration.DEFAULT_MANIFEST)
    parser.add_argument("--interpro", type=Path, default=migration.DEFAULT_INTERPRO)
    parser.add_argument("--traits", type=Path, default=migration.DEFAULT_TRAITS)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    template = subparsers.add_parser("template", help="emit the exhaustive pending template")
    _add_source_arguments(template)
    validate = subparsers.add_parser(
        "validate", help="validate a completed canonical template and emit one receipt"
    )
    validate.add_argument("--ledger", type=Path, required=True)
    _add_source_arguments(validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        rows, summary = replay_migration_plan(args)
        if args.command == "template":
            print(dump_review_template(rows, summary), end="")
            return 0
        receipt = validate_completed_ledger(
            ledger_path=args.ledger,
            plan_rows=rows,
            plan_summary=summary,
        )
    except (PrintsMigrationReviewError, OSError, ValueError) as error:
        failure = {
            "schema_version": SCHEMA_VERSION,
            "kind": RECEIPT_KIND,
            "status": "INVALID",
            "proposal_compatible": False,
            "accepted_for_next_phase": False,
            "apply_authorized": False,
            "serialization_status": "NOT_PERFORMED",
            "trait_write_count": 0,
            "grounding_write_count": 0,
            "error": str(error),
        }
        print(canonical_json(failure))
        return 2
    print(canonical_json(receipt))
    return 0 if receipt["accepted_for_next_phase"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
