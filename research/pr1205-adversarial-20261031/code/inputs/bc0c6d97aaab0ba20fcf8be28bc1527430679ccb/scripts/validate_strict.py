#!/usr/bin/env python3
"""Strict LinkML validation harness for ProteinTraitsMech instance records.

Wraps the in-process linkml.validator with JsonschemaValidationPlugin(closed=True)
so unknown fields are flagged. The previous `just validate-all` batched ordinary
`linkml-validate` CLI calls (open mode), which silently accepts unknown top-level
and nested slots. Emits a structured TSV of every ERROR result and exits non-zero
if any are found.

Usage:
    python scripts/validate_strict.py [PATH ...]
    python scripts/validate_strict.py --sample 5
    python scripts/validate_strict.py --out reports/instance_validation_failures.tsv

Paths may be files or directories; directories are walked for *.yaml.

Default scope when no paths given:
    data/traits/

ProteinTraitsMech has a single root class (ProteinTraitRecord); no class routing
required.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

import yaml
from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin
from linkml.validator.report import Severity

from prints_kdat import (
    PRINTS_42_0_RELEASE,
    PRINTS_42_0_SHA256,
    PRINTS_42_0_SOURCE_ARTIFACT,
)
from sfld_release import (
    SFLD_4_HIERARCHY_SHA256,
    SFLD_4_HIERARCHY_SOURCE_ARTIFACT,
    SFLD_4_HMM_SHA256,
    SFLD_4_HMM_SOURCE_ARTIFACT,
    SFLD_4_PROFILE_SEARCH_MODE,
    SFLD_4_RELEASE,
    SFLD_4_REPRESENTATION_TYPE,
    SFLD_4_SITE_COORDINATE_SYSTEM,
    SFLD_4_SITE_EVIDENCE_SCOPE,
    SFLD_4_SITES_SHA256,
    SFLD_4_SITES_SOURCE_ARTIFACT,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = _REPO_ROOT / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml"
DEFAULT_ROOTS = [_REPO_ROOT / "data" / "traits"]
TARGET_CLASS = "ProteinTraitRecord"

# Per-worker singleton — built lazily after fork so the schema parses once per
# worker process, not once per file.
_VALIDATOR: Validator | None = None


def _get_validator() -> Validator:
    global _VALIDATOR
    if _VALIDATOR is None:
        _VALIDATOR = Validator(
            schema=str(SCHEMA_PATH),
            validation_plugins=[JsonschemaValidationPlugin(closed=True)],
        )
    return _VALIDATOR


# Classifier regexes — keep narrow so each category is meaningful and the rest
# fall into "other" for manual review rather than getting silently bucketed.
_CATEGORY_RULES: list[tuple[str, re.Pattern[str]]] = [
    # jsonschema says "'a' was unexpected" for one key and "'a', 'b' were
    # unexpected" for several.  Matching only the singular bucketed every
    # multi-key record as "other" -- under-reporting the one category closed
    # mode exists to produce, and exactly the shape a generator emitting
    # undeclared slots produces, since it emits several at once (#541).
    (
        "unexpected_field",
        re.compile(
            r"Additional properties are not allowed \((?P<key>'[^']+'(?:, '[^']+')*)"
            r" (?:was|were) unexpected\) in (?P<path>\S+)"
        ),
    ),
    ("missing_required", re.compile(r"'(?P<key>[^']+)' is a required property in (?P<path>\S+)")),
    ("enum_mismatch", re.compile(r"'(?P<value>[^']+)' is not one of \[(?P<choices>[^\]]+)\]")),
    ("type_mismatch", re.compile(r"(?P<value>'[^']+'|\S+) is not of type '(?P<type>[^']+)'")),
    ("pattern_mismatch", re.compile(r"(?P<value>'[^']+'|\S+) does not match (?P<pattern>'[^']+')")),
    ("format_mismatch", re.compile(r"(?P<value>'[^']+'|\S+) is not a '(?P<format>[^']+)'")),
    ("range_violation", re.compile(r"(?P<value>\S+) is (less than|greater than) (?P<bound>\S+)")),
]


def classify(message: str) -> tuple[str, str]:
    """Return (category, detail) for a validator message."""
    for name, rule in _CATEGORY_RULES:
        m = rule.search(message)
        if m:
            parts = m.groupdict()
            detail = "|".join(f"{k}={v}" for k, v in parts.items())
            return name, detail
    return "other", ""


def _semantic_row(path: Path, instance_path: str, message: str) -> dict:
    return {
        "file": str(path),
        "category": "semantic_invariant",
        "detail": "",
        "path": instance_path,
        "message": message[:300],
    }


def _fingerprint_invariant_errors(path: Path, instance: object) -> list[dict]:
    """Enforce ordered-fingerprint facts that JSON Schema cannot express."""

    if not isinstance(instance, dict):
        return []
    representations = instance.get("sequence_fingerprint_representations")
    if not isinstance(representations, list):
        return []
    rows: list[dict] = []
    identifier = instance.get("identifier")
    for representation_index, representation in enumerate(representations):
        if not isinstance(representation, dict):
            continue
        base = f"/sequence_fingerprint_representations/{representation_index}"
        motifs = representation.get("motifs")
        motif_count = representation.get("motif_count")
        if isinstance(motifs, list) and isinstance(motif_count, int):
            if motif_count != len(motifs):
                rows.append(
                    _semantic_row(
                        path,
                        base,
                        f"motif_count {motif_count} does not equal {len(motifs)} motif rows",
                    )
                )
            ordinals = [motif.get("ordinal") for motif in motifs if isinstance(motif, dict)]
            expected = list(range(1, len(motifs) + 1))
            if len(ordinals) == len(motifs) and ordinals != expected:
                rows.append(
                    _semantic_row(
                        path,
                        f"{base}/motifs",
                        f"motif ordinals must be contiguous source order {expected!r}; "
                        f"found {ordinals!r}",
                    )
                )
            for motif_index, motif in enumerate(motifs):
                if not isinstance(motif, dict):
                    continue
                minimum = motif.get("training_distance_from_previous_min")
                maximum = motif.get("training_distance_from_previous_max")
                if isinstance(minimum, int) and isinstance(maximum, int) and minimum > maximum:
                    rows.append(
                        _semantic_row(
                            path,
                            f"{base}/motifs/{motif_index}",
                            "training_distance_from_previous_min exceeds "
                            "training_distance_from_previous_max",
                        )
                    )
                constraint = motif.get("inter_motif_distance_constraint")
                if not isinstance(constraint, dict):
                    continue
                constraint_minimum = constraint.get("minimum")
                constraint_maximum = constraint.get("maximum")
                constraint_base = f"{base}/motifs/{motif_index}/inter_motif_distance_constraint"
                if (
                    isinstance(constraint_minimum, int)
                    and isinstance(constraint_maximum, int)
                    and constraint_minimum > constraint_maximum
                ):
                    rows.append(
                        _semantic_row(
                            path,
                            constraint_base,
                            "inter-motif constraint minimum exceeds maximum",
                        )
                    )
                ordinal = motif.get("ordinal")
                region_start = constraint.get("region_start_ordinal")
                region_end = constraint.get("region_end_ordinal")
                if (
                    isinstance(ordinal, int)
                    and isinstance(region_start, int)
                    and isinstance(region_end, int)
                    and (region_start, region_end) != (ordinal - 1, ordinal)
                ):
                    rows.append(
                        _semantic_row(
                            path,
                            constraint_base,
                            f"inter-motif constraint REGION must be {ordinal - 1}-{ordinal} "
                            f"for motif ordinal {ordinal}; found {region_start}-{region_end}",
                        )
                    )

        if representation.get("representation_type") != "PRINTS_FINAL_ORDERED_MOTIF_SETS":
            continue
        expected_fields = {
            "source_accession": identifier,
            "source_release": PRINTS_42_0_RELEASE,
            "source_artifact": PRINTS_42_0_SOURCE_ARTIFACT,
            "source_artifact_sha256": PRINTS_42_0_SHA256,
            "compatible_derivation_tool_hint": "EMBOSS_PRINTSEXTRACT",
        }
        for field_name, expected_value in expected_fields.items():
            actual_value = representation.get(field_name)
            if actual_value != expected_value:
                rows.append(
                    _semantic_row(
                        path,
                        f"{base}/{field_name}",
                        f"PRINTS 42.0 {field_name} must be {expected_value!r}; "
                        f"found {actual_value!r}",
                    )
                )
        if instance.get("sequence_pattern") is not None:
            rows.append(
                _semantic_row(
                    path,
                    "/sequence_pattern",
                    "a PRINTS ordered fingerprint must not be serialized as one sequence_pattern",
                )
            )
    return rows


def _profile_invariant_errors(path: Path, instance: object) -> list[dict]:
    """Enforce cross-field SFLD profile facts JSON Schema cannot express."""

    if not isinstance(instance, dict):
        return []
    representations = instance.get("sequence_profile_representations")
    if not isinstance(representations, list):
        return []
    rows: list[dict] = []
    identifier = instance.get("identifier")
    for representation_index, representation in enumerate(representations):
        if not isinstance(representation, dict):
            continue
        base = f"/sequence_profile_representations/{representation_index}"
        sites = representation.get("sites", [])
        patterns = representation.get("site_feature_patterns", [])
        site_count = representation.get("site_count")
        pattern_count = representation.get("site_feature_pattern_count")
        if isinstance(sites, list) and isinstance(site_count, int):
            if site_count != len(sites):
                rows.append(
                    _semantic_row(
                        path,
                        base,
                        f"site_count {site_count} does not equal {len(sites)} SITE rows",
                    )
                )
            ordinals = [site.get("ordinal") for site in sites if isinstance(site, dict)]
            expected_ordinals = list(range(1, len(sites) + 1))
            if len(ordinals) == len(sites) and ordinals != expected_ordinals:
                rows.append(
                    _semantic_row(
                        path,
                        f"{base}/sites",
                        "site ordinals must be contiguous source order "
                        f"{expected_ordinals!r}; found {ordinals!r}",
                    )
                )
            positions = [site.get("model_position") for site in sites if isinstance(site, dict)]
            if len(positions) == len(sites) and all(
                isinstance(position, int) for position in positions
            ):
                if positions != sorted(set(positions)):
                    rows.append(
                        _semantic_row(
                            path,
                            f"{base}/sites",
                            "site model_position values must be strictly increasing",
                        )
                    )
                model_length = representation.get("model_length")
                if isinstance(model_length, int) and any(
                    position > model_length for position in positions
                ):
                    rows.append(
                        _semantic_row(
                            path,
                            f"{base}/sites",
                            f"site model_position exceeds model_length {model_length}",
                        )
                    )
        if isinstance(patterns, list) and isinstance(pattern_count, int):
            if pattern_count != len(patterns):
                rows.append(
                    _semantic_row(
                        path,
                        base,
                        f"site_feature_pattern_count {pattern_count} does not equal "
                        f"{len(patterns)} FEATURE rows",
                    )
                )
            if isinstance(site_count, int) and any(
                isinstance(pattern, str) and len(pattern) != site_count for pattern in patterns
            ):
                rows.append(
                    _semantic_row(
                        path,
                        f"{base}/site_feature_patterns",
                        "every correlated FEATURE tuple length must equal site_count",
                    )
                )
            if len(patterns) != len({pattern for pattern in patterns if isinstance(pattern, str)}):
                rows.append(
                    _semantic_row(
                        path,
                        f"{base}/site_feature_patterns",
                        "correlated FEATURE tuples must be unique",
                    )
                )
        if (
            isinstance(site_count, int)
            and isinstance(pattern_count, int)
            and (site_count == 0) != (pattern_count == 0)
        ):
            rows.append(
                _semantic_row(
                    path,
                    base,
                    "SFLD sites and correlated FEATURE tuples must both be empty or both present",
                )
            )

        if representation.get("representation_type") != SFLD_4_REPRESENTATION_TYPE:
            continue
        expected_fields = {
            "source_accession": identifier,
            "source_release": SFLD_4_RELEASE,
            "source_model_artifact": SFLD_4_HMM_SOURCE_ARTIFACT,
            "source_model_artifact_sha256": SFLD_4_HMM_SHA256,
            "source_sites_artifact": SFLD_4_SITES_SOURCE_ARTIFACT,
            "source_sites_artifact_sha256": SFLD_4_SITES_SHA256,
            "source_hierarchy_artifact": SFLD_4_HIERARCHY_SOURCE_ARTIFACT,
            "source_hierarchy_artifact_sha256": SFLD_4_HIERARCHY_SHA256,
            "profile_search_mode": SFLD_4_PROFILE_SEARCH_MODE,
            "site_coordinate_system": SFLD_4_SITE_COORDINATE_SYSTEM,
            "site_evidence_scope": SFLD_4_SITE_EVIDENCE_SCOPE,
        }
        for field_name, expected_value in expected_fields.items():
            actual_value = representation.get(field_name)
            if actual_value != expected_value:
                rows.append(
                    _semantic_row(
                        path,
                        f"{base}/{field_name}",
                        f"SFLD 4 {field_name} must be {expected_value!r}; found {actual_value!r}",
                    )
                )
        source_accession = representation.get("source_accession")
        accession = (
            source_accession.split(":", 1)[1]
            if isinstance(source_accession, str) and ":" in source_accession
            else ""
        )
        level_by_prefix = {
            "SFLDS": "SUPERFAMILY",
            "SFLDG": "SUBGROUP",
            "SFLDF": "FAMILY",
        }
        expected_level = next(
            (level for prefix, level in level_by_prefix.items() if accession.startswith(prefix)),
            None,
        )
        if (
            expected_level is not None
            and representation.get("native_classification_level") != expected_level
        ):
            rows.append(
                _semantic_row(
                    path,
                    f"{base}/native_classification_level",
                    f"SFLD accession {accession} requires native level {expected_level}",
                )
            )
        if instance.get("sequence_pattern") is not None:
            rows.append(
                _semantic_row(
                    path,
                    "/sequence_pattern",
                    "an SFLD HMM plus correlated sites must not be serialized as one "
                    "sequence_pattern",
                )
            )
    return rows


def validate_one(path: Path) -> list[dict]:
    """Validate a single YAML file. Returns one dict per ERROR result."""
    validator = _get_validator()
    try:
        with path.open() as f:
            instance = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [
            {
                "file": str(path),
                "category": "yaml_parse_error",
                "detail": "",
                "path": "",
                "message": str(e).splitlines()[0][:300],
            }
        ]
    if instance is None:
        return [
            {
                "file": str(path),
                "category": "empty_file",
                "detail": "",
                "path": "",
                "message": "file parsed as None",
            }
        ]

    try:
        report = validator.validate(instance, target_class=TARGET_CLASS)
    except Exception as e:  # noqa: BLE001 — surface anything weird as a row
        return [
            {
                "file": str(path),
                "category": "validator_crash",
                "detail": type(e).__name__,
                "path": "",
                "message": str(e)[:300],
            }
        ]

    rows = []
    for result in report.results:
        if result.severity != Severity.ERROR:
            continue
        category, detail = classify(result.message)
        rows.append(
            {
                "file": str(path),
                "category": category,
                "detail": detail,
                "path": result.instance_index or "",
                "message": result.message[:300],
            }
        )
    rows.extend(_fingerprint_invariant_errors(path, instance))
    rows.extend(_profile_invariant_errors(path, instance))
    return rows


_YAML_SUFFIXES = {".yaml", ".yml"}


def iter_yaml_files(paths: Iterable[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_file():
            if p.suffix.lower() not in _YAML_SUFFIXES:
                print(f"Skipping non-YAML file: {p}", file=sys.stderr)
                continue
            out.append(p)
        elif p.is_dir():
            out.extend(sorted(p.rglob("*.yaml")))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths", nargs="*", type=Path, help="Files or directories. Defaults to data/traits/."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("reports/instance_validation_failures.tsv"),
        help="TSV output path.",
    )
    parser.add_argument(
        "--sample",
        type=int,
        metavar="N",
        help="Validate only the first N files (after sorting). Useful for smoke tests.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, (os.cpu_count() or 4) - 1),
        help="Process pool size. Default: ncpu - 1.",
    )
    parser.add_argument(
        "--fail-on",
        choices=("error", "never"),
        default="error",
        help="Exit non-zero policy. 'error' (default) exits 1 if any ERROR row was emitted.",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="exit 0 when every supplied path is missing; for the CI diff "
        "caller, whose file list can be deletion-only (#540)",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress per-file progress dots.")
    args = parser.parse_args(argv)
    if args.workers < 1:
        parser.error("--workers must be at least 1")

    roots = args.paths or DEFAULT_ROOTS
    files = iter_yaml_files(roots)
    if args.sample:
        files = files[: args.sample]
    if not files:
        if args.paths:
            # Explicit paths were given but none exist on disk. For the CI diff
            # caller that is a deletion-only change and fine; for a human typing
            # `just validate <path>` it is a typo, and returning 0 reported
            # "validated" for a file that was never read -- weaker than the open
            # mode CLI this replaced, which exits 2 (#540). Opt in, do not assume.
            if args.allow_missing:
                print(
                    "All supplied paths were missing (e.g. deleted files) — nothing to validate.",
                    file=sys.stderr,
                )
                return 0
            listed = ", ".join(str(path) for path in args.paths[:5])
            more = "" if len(args.paths) <= 5 else f" (+{len(args.paths) - 5} more)"
            print(
                f"None of the supplied paths exist: {listed}{more}. Nothing was validated; "
                f"pass --allow-missing if a deletion-only file list is expected.",
                file=sys.stderr,
            )
            return 2
        print("No YAML files found.", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)

    print(
        f"Validating {len(files)} files with {args.workers} workers; schema={SCHEMA_PATH}",
        file=sys.stderr,
    )

    all_rows: list[dict] = []
    if args.workers == 1:
        # A one-worker run is also the portable path for constrained macOS
        # environments where ProcessPoolExecutor cannot query POSIX named-
        # semaphore limits.  Do not construct a process pool when the caller
        # explicitly requested serial validation.
        for done, path in enumerate(files, 1):
            all_rows.extend(validate_one(path))
            if not args.quiet and done % 2000 == 0:
                print(
                    f"  {done}/{len(files)} files processed, {len(all_rows)} ERROR rows so far",
                    file=sys.stderr,
                )
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(validate_one, p): p for p in files}
            done = 0
            for fut in as_completed(futures):
                done += 1
                rows = fut.result()
                all_rows.extend(rows)
                if not args.quiet and done % 2000 == 0:
                    print(
                        f"  {done}/{len(files)} files processed, {len(all_rows)} ERROR rows so far",
                        file=sys.stderr,
                    )

    # Sort for deterministic TSV output (avoids noisy diffs from worker scheduling).
    all_rows.sort(key=lambda r: (r["file"], r["path"], r["category"], r["message"]))
    with args.out.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["file", "category", "detail", "path", "message"],
            delimiter="\t",
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(all_rows)

    by_cat: dict[str, int] = {}
    files_with_errors: set[str] = set()
    for row in all_rows:
        by_cat[row["category"]] = by_cat.get(row["category"], 0) + 1
        files_with_errors.add(row["file"])

    print("", file=sys.stderr)
    print("=== validate-strict summary ===", file=sys.stderr)
    print(f"  files scanned:      {len(files)}", file=sys.stderr)
    print(f"  files with ERROR:   {len(files_with_errors)}", file=sys.stderr)
    print(f"  total ERROR rows:   {len(all_rows)}", file=sys.stderr)
    print(f"  TSV:                {args.out}", file=sys.stderr)
    if by_cat:
        print("  by category:", file=sys.stderr)
        for cat, count in sorted(by_cat.items(), key=lambda kv: -kv[1]):
            print(f"    {cat:24s} {count:>8d}", file=sys.stderr)

    if args.fail_on == "error" and all_rows:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
