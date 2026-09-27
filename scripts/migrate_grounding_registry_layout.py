#!/usr/bin/env python3
"""One-time migration of the durable evidence and bindings registries to shards (#801).

``data/grounding/occurrence_evidence.jsonl`` and ``qualified_record_bindings.jsonl``
become the ``.jsonl.d`` shard directories described in
``scripts/grounding_registry_layout.py``. The migration is a pure re-layout: it never
parses and re-serializes its way to a different byte, so the joined shards of each
directory are the flat file it replaces and the logical sha256 is the flat sha256.

Dry-run is the default and writes nothing: it reads each flat file once, refuses any
row the layout would not accept (it never normalizes), requires the two registries to
have the same key sequence, proves the round trip, and prints the JSON plan.
``--apply`` then, under the registry lock, re-hashes both flat files, installs both
directories and deletes both flat files in one promoter transaction (rolled back on any
failure), re-checks the result on disk, and writes the JSON report.

A mixed or partial state (one registry migrated, both layouts present, a registry
missing) is refused rather than repaired; restore ``data/grounding`` from git.
``protein_registry.jsonl`` and ``uniprot_memberships.jsonl`` stay flat and are
checked to be byte-identical afterwards. Trait records are never read or written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import ground_uniprot_examples as ground
import grounding_registry_layout as layout

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GROUNDING_ROOT = REPO_ROOT / "data" / "grounding"
DEFAULT_REPORT = (
    REPO_ROOT / "reports" / "uniprot-grounding" / "registry-layout-migration-801.json"
)

# Evidence first: the bindings must carry exactly its key sequence.
REGISTRIES = ("occurrence_evidence", "qualified_record_bindings")
# Flat registries beside them that the migration must leave byte-identical. Membership
# is optional; the protein registry's sha256 is pinned by the biophysical pilot.
UNCHANGED_REGISTRIES = ("protein_registry.jsonl", "uniprot_memberships.jsonl")

_SHA256 = re.compile(r"[0-9a-f]{64}")


class MigrationError(ValueError):
    """The registries are not in a state this migration can convert safely."""


@dataclass(frozen=True)
class _FlatRegistry:
    """One flat registry, read once, with its shards and the proofs about them."""

    name: str
    flat: Path
    sharded: Path
    raw: bytes
    text: str
    sha256: str
    shards: dict[str, bytes]
    manifest_text: str
    keys: tuple[str, ...]
    proofs: dict[str, bool]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_argument(value: str) -> str:
    if _SHA256.fullmatch(value) is None:
        raise argparse.ArgumentTypeError("expected a full 64-character lowercase sha256")
    return value


def _paths(root: Path, name: str) -> tuple[Path, Path]:
    flat = root / f"{name}.jsonl"
    return flat, flat.with_name(flat.name + ".d")


def _state(root: Path) -> str:
    """``flat`` or ``sharded`` when both registries agree; refuse everything else."""

    states: dict[str, str] = {}
    for name in REGISTRIES:
        flat, sharded = _paths(root, name)
        present = (os.path.lexists(flat), os.path.lexists(sharded))
        states[name] = {
            (True, False): "flat",
            (False, True): "sharded",
            (True, True): "both layouts present",
            (False, False): "missing",
        }[present]
    if set(states.values()) in ({"flat"}, {"sharded"}):
        return next(iter(states.values()))
    detail = ", ".join(f"{name}: {state}" for name, state in states.items())
    raise MigrationError(
        f"refusing an ambiguous registry state under {root} ({detail}); the migration "
        "runs only from both flat files, so restore data/grounding from git first"
    )


def _read_flat(root: Path, name: str, expected_sha256: str | None) -> _FlatRegistry:
    """Read one flat registry once, refuse anything the layout would reject, and prove
    that its shards reproduce it exactly."""

    flat, sharded = _paths(root, name)
    if flat.is_symlink() or not flat.is_file():
        raise MigrationError(f"flat registry is not a regular file: {flat}")
    raw = flat.read_bytes()
    sha256 = _sha256(raw)
    if expected_sha256 is not None and sha256 != expected_sha256:
        raise MigrationError(
            f"{flat} has sha256 {sha256}, not the expected {expected_sha256}"
        )
    try:
        text = raw.decode("utf-8")
        shards = layout.split_registry_text(text)
    except (UnicodeDecodeError, layout.RegistryLayoutError) as exc:
        raise MigrationError(
            f"{flat} is not a canonical, sorted registry ({exc}); the migration never "
            "normalizes rows, so repair it through the promoter first"
        ) from exc
    # split_registry_text has proven every line is one canonical JSON object ending in
    # LF, so splitting on LF (never splitlines, which breaks on U+2028) yields the rows.
    rows = [json.loads(line) for line in text.split("\n")[:-1]]
    keys = tuple(row[layout.KEY_FIELD] for row in rows)
    manifest_text = layout.build_manifest_text(shards)
    manifest = json.loads(manifest_text)
    joined = b"".join(shards[shard] for shard in sorted(shards))
    # The promoter's own serializer over the parsed rows: what every later promotion
    # will write, so the first one after the migration rewrites no unchanged shard.
    replayed = ground._registry_text(dict(zip(keys, rows))).encode("utf-8")
    proofs = {
        "joined_shards_equal_flat_bytes": joined == raw,
        "manifest_logical_sha256_equals_flat_sha256": manifest["logical_sha256"] == sha256,
        "manifest_rows_and_bytes_match_flat": (
            (manifest["row_count"], manifest["byte_count"]) == (len(rows), len(raw))
        ),
        "promoter_registry_text_reproduces_flat_bytes": replayed == raw,
    }
    failed = sorted(proof for proof, passed in proofs.items() if not passed)
    if failed:
        raise MigrationError(f"{flat}: round-trip proof(s) failed: {', '.join(failed)}")
    return _FlatRegistry(
        name, flat, sharded, raw, text, sha256, shards, manifest_text, keys, proofs
    )


def _require_equal_keys(evidence: _FlatRegistry, bindings: _FlatRegistry) -> None:
    if evidence.keys == bindings.keys:
        return
    unbound = sorted(set(evidence.keys) - set(bindings.keys))
    orphaned = sorted(set(bindings.keys) - set(evidence.keys))
    raise MigrationError(
        f"evidence and bindings key sequences differ: {len(unbound)} evidence row(s) "
        f"without a binding {unbound[:3]}, {len(orphaned)} binding(s) without evidence "
        f"{orphaned[:3]}; the registries must be repaired before they are migrated"
    )


def _unchanged_digests(root: Path) -> dict[str, str | None]:
    digests: dict[str, str | None] = {}
    for name in UNCHANGED_REGISTRIES:
        path = root / name
        if not os.path.lexists(path):
            digests[name] = None
        elif path.is_symlink() or not path.is_file():
            raise MigrationError(f"flat registry is not a regular file: {path}")
        else:
            digests[name] = _sha256(path.read_bytes())
    return digests


def _registry_plan(registry: _FlatRegistry) -> dict[str, Any]:
    sizes = [len(data) for data in registry.shards.values()]
    return {
        "bytes": len(registry.raw),
        "files_to_create": len(registry.shards) + 1,
        "files_to_delete": 1,
        "flat": ground._display_path(registry.flat),
        "flat_sha256": registry.sha256,
        "key_sequence_sha256": _sha256("".join(key + "\n" for key in registry.keys).encode()),
        "logical_sha256": json.loads(registry.manifest_text)["logical_sha256"],
        "manifest_sha256": _sha256(registry.manifest_text.encode("utf-8")),
        "max_shard_bytes": max(sizes, default=0),
        "min_shard_bytes": min(sizes, default=0),
        "proofs": registry.proofs,
        "rows": len(registry.keys),
        "shards": len(registry.shards),
        "sharded": ground._display_path(registry.sharded),
    }


def _require_clean_checkout(root: Path) -> None:
    """Refuse uncommitted or untracked changes under a root inside this checkout, so the
    migration commit contains nothing but the re-layout."""

    command = [
        "git", "--no-optional-locks", "status", "--porcelain", "--untracked-files=all",
        "--", str(root.resolve()),
    ]
    try:
        result = subprocess.run(
            command, cwd=REPO_ROOT, capture_output=True, text=True, timeout=120, check=False
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise MigrationError(f"cannot confirm {root} is clean: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit {result.returncode}"
        raise MigrationError(f"cannot confirm {root} is clean: git status failed: {detail}")
    dirty = result.stdout.splitlines()
    if dirty:
        shown = "; ".join(dirty[:5]) + (f"; +{len(dirty) - 5} more" if len(dirty) > 5 else "")
        raise MigrationError(
            f"{root} has uncommitted changes ({shown}); commit or restore them first so "
            "the migration commit is a pure re-layout"
        )


def _post_apply_checks(
    registries: list[_FlatRegistry], root: Path, unchanged: dict[str, str | None]
) -> dict[str, Any]:
    """Re-read the installed image from disk and require every proof to hold again."""

    checks: dict[str, Any] = {}
    failed: list[str] = []
    for registry in registries:
        image = layout.read_registry(registry.sharded)
        try:
            digest = layout.sharded_digest(registry.sharded)
        except layout.RegistryLayoutError as exc:
            digest = None
            failed.append(f"{registry.name}: {exc}")
        names = sorted(
            entry.name
            for entry in registry.sharded.iterdir()
            if layout.SHARD_RE.fullmatch(entry.name)
        )
        # The same bytes `LC_ALL=C cat X.jsonl.d/[0-9a-f][0-9a-f].jsonl` prints.
        joined = b"".join((registry.sharded / name).read_bytes() for name in names)
        result = {
            "flat_file_removed": not os.path.lexists(registry.flat),
            "joined_shards_equal_flat_bytes": joined == registry.raw,
            "logical_sha256_equals_flat_sha256": digest == registry.sha256,
            "no_layout_issues": image.issues == (),
            "replan_is_empty": layout.plan_sharded_write(registry.sharded, registry.text) == [],
        }
        checks[registry.name] = result
        failed.extend(f"{registry.name}: {check}" for check, ok in result.items() if not ok)
    after = _unchanged_digests(root)
    checks["unchanged_registries_sha256"] = after
    if after != unchanged:
        failed.append(f"flat registries changed: {unchanged} -> {after}")
    if failed:
        raise MigrationError(
            "post-apply check(s) failed after install: " + "; ".join(failed[:5])
            + f"; restore with `git restore --source=HEAD -- {root}`"
        )
    return checks


def _apply(
    registries: list[_FlatRegistry], root: Path, unchanged: dict[str, str | None]
) -> dict[str, Any]:
    if ground._path_is_under(root, REPO_ROOT):
        _require_clean_checkout(root)
    with layout.registry_lock(root):
        # The reads above were unlocked; a writer may have finished in between.
        for registry in registries:
            if os.path.lexists(registry.sharded):
                raise MigrationError(f"{registry.sharded} appeared since the plan was made")
            current = registry.flat.read_bytes() if registry.flat.is_file() else None
            if current is None or _sha256(current) != registry.sha256:
                raise MigrationError(
                    f"{registry.flat} changed since the plan was made; re-run the migration"
                )
        # One transaction: every shard, each manifest last, then the flat deletes, then
        # the post-install verify of both directories; any failure restores both files.
        ground._install_promotion_transaction(
            [(registry.sharded, registry.text) for registry in registries]
            + [(registry.flat, None) for registry in registries],
            {},
        )
        return _post_apply_checks(registries, root, unchanged)


def _already_migrated(root: Path, expected: dict[str, str | None]) -> int:
    parts = []
    for name in REGISTRIES:
        _flat, sharded = _paths(root, name)
        digest = layout.sharded_digest(sharded)
        if expected[name] is not None and digest != expected[name]:
            raise MigrationError(
                f"{sharded} is already migrated with logical sha256 {digest}, "
                f"not the expected {expected[name]}"
            )
        parts.append(f"{sharded.name} logical_sha256={digest}")
    print(f"already migrated: {'; '.join(parts)}")
    return 0


def run(args: argparse.Namespace) -> int:
    root = args.grounding_root
    report = args.report
    if ground._path_is_under(report, REPO_ROOT / "data") or ground._path_is_under(report, root):
        raise MigrationError(f"--report must be outside data/ and the grounding root: {report}")
    expected = {
        "occurrence_evidence": args.expect_evidence_sha256,
        "qualified_record_bindings": args.expect_bindings_sha256,
    }
    if _state(root) == "sharded":
        return _already_migrated(root, expected)

    registries = [_read_flat(root, name, expected[name]) for name in REGISTRIES]
    _require_equal_keys(*registries)
    unchanged = _unchanged_digests(root)
    plan: dict[str, Any] = {
        "grounding_root": ground._display_path(root),
        "key_sequences_equal": True,
        "layout": layout.LAYOUT,
        "layout_version": layout.LAYOUT_VERSION,
        "mode": "apply" if args.apply else "dry-run",
        "registries": {registry.name: _registry_plan(registry) for registry in registries},
        "unchanged_registries_sha256": unchanged,
    }
    if not args.apply:
        print(json.dumps(plan, indent=2, sort_keys=True))
        print("DRY-RUN: nothing written; pass --apply to migrate.", file=sys.stderr)
        return 0

    plan["post_apply"] = _apply(registries, root, unchanged)
    report_text = json.dumps(plan, indent=2, sort_keys=True) + "\n"
    ground._atomic_text(report, report_text)
    print(report_text, end="")
    print(
        f"MIGRATED {len(registries)} registries under {ground._display_path(root)}; "
        f"report {ground._display_path(report)}",
        file=sys.stderr,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--grounding-root",
        type=Path,
        default=DEFAULT_GROUNDING_ROOT,
        help="directory holding the flat registries (default: data/grounding)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="install the shard directories and delete the flat files (default: dry run)",
    )
    parser.add_argument(
        "--expect-evidence-sha256",
        type=_sha256_argument,
        help="refuse unless occurrence_evidence.jsonl has exactly this sha256",
    )
    parser.add_argument(
        "--expect-bindings-sha256",
        type=_sha256_argument,
        help="refuse unless qualified_record_bindings.jsonl has exactly this sha256",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help="JSON report written after --apply; refused under data/",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except (MigrationError, ground.GroundingError, layout.RegistryLayoutError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
