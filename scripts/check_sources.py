#!/usr/bin/env python3
"""Validate download.yaml as the enforced source and script registry.

The manifest contract, restored here because the previous docstring recorded it and
deleting it left `STATUSES` as an unexplained set literal (#543):

* every block declares a `url`;
* a block carrying `status:` also declares `source:`, so it joins a source group and
  is reachable by the per-source rules below -- without it the block is checked for
  `url` and nothing else (#543);
* `seeder`/`fetcher`/`enricher` name a script that exists, under its role's prefix;
* a source with any `seeded` block names a seeder somewhere in that group;
* a restrictive or missing-open licence declares a `license_review` disposition;
* every `seed_*.py` on disk is either source-backed or classified as a helper.

`STATUSES` is not an arbitrary set. `superseded` and `enrichment` exist because #91
needed to distinguish a block replaced by a newer release from one that only adds
fields to records another block seeded; both are legitimate terminal states that are
not `seeded`, and dropping either silently reclassifies real blocks as invalid.
"""

from __future__ import annotations

import collections
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "download.yaml"
HELPERS = REPO_ROOT / "scripts" / "source_helpers.yaml"
SCRIPTS = REPO_ROOT / "scripts"

STATUSES = {"seeded", "candidate", "deferred", "rejected", "superseded", "enrichment"}
BLOCK_ROLES = {"primary", "metadata", "documentation", "mapping", "api", "enrichment"}
HELPER_ROLES = {"helper_seeder", "local_generator"}
LICENSE_REVIEWS = {"pending", "approved", "rejected"}
RESTRICTIVE = (
    "noncommercial",
    "non-commercial",
    "-nc",
    "byncnd",
    "by-nc",
    "noderiv",
    "-nd",
    "login",
    "registration",
    "flagged",
)


@dataclass
class Result:
    blocks: int
    sources: int
    statuses: collections.Counter[str]
    errors: list[str]
    notices: list[str]


def _load_list(path: Path, label: str, errors: list[str]) -> list:
    if not path.is_file():
        errors.append(f"{label} not found: {path}")
        return []
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    except yaml.YAMLError as exc:
        errors.append(f"{label} is not valid YAML: {exc}")
        return []
    if not isinstance(value, list):
        errors.append(f"{label} must be a YAML list")
        return []
    return value


def _script_name(value: object, field: str, tag: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"[{tag}] {field} must be a non-empty command string")
        return None
    return value.split()[0]


def validate_registry(
    manifest: Path = MANIFEST,
    helpers: Path = HELPERS,
    scripts: Path = SCRIPTS,
) -> Result:
    errors: list[str] = []
    notices: list[str] = []
    blocks = _load_list(manifest, manifest.name, errors)
    helper_entries = _load_list(helpers, helpers.name, errors)

    referenced_seeders: set[str] = set()
    source_blocks: dict[str, list[dict]] = collections.defaultdict(list)
    status_counts: collections.Counter[str] = collections.Counter()

    for index, block in enumerate(blocks):
        if not isinstance(block, dict):
            errors.append(f"block[{index}] must be a mapping")
            continue
        tag = str(block.get("name") or block.get("source") or f"block[{index}]")
        if not block.get("url"):
            errors.append(f"[{tag}] missing required field: url")

        status = block.get("status")
        if status is not None:
            if status not in STATUSES:
                errors.append(f"[{tag}] invalid status {status!r}")
            else:
                status_counts[status] += 1
        role = block.get("role", "primary")
        if role not in BLOCK_ROLES:
            errors.append(f"[{tag}] invalid role {role!r}")
        if role == "api" and status == "seeded":
            # Nothing linked role to status, so a per-accession API block could call
            # itself seeded while a sibling in the same source group supplied the
            # seeder -- the shape #458 was filed about, closed at one site but never
            # as a rule (#543).
            errors.append(
                f"[{tag}] role: api may not be status: seeded; an API endpoint "
                "is a lookup route, not a seeded source"
            )

        source = block.get("source")
        if source:
            source_blocks[str(source)].append(block)
        elif status is not None:
            # Grouping is by `source:`, and every per-source rule below iterates those
            # groups. A block with a status but no source was therefore checked for
            # `url` and nothing else -- including the seeded-needs-a-seeder rule (#543).
            errors.append(
                f"[{tag}] declares status {status!r} but no source: it joins no "
                "source group, so no per-source rule can see it"
            )

        for field in ("seeder", "fetcher", "enricher"):
            if field not in block:
                continue
            script = _script_name(block[field], field, tag, errors)
            if not script:
                continue
            if not (scripts / script).is_file():
                errors.append(f"[{tag}] {field} script not found: scripts/{script}")
            if field == "seeder":
                if not script.startswith("seed_"):
                    errors.append(f"[{tag}] seeder must name a seed_*.py script, not {script!r}")
                else:
                    referenced_seeders.add(script)
            elif field == "fetcher" and not script.startswith("fetch_"):
                errors.append(f"[{tag}] fetcher must name a fetch_*.py script, not {script!r}")
            elif field == "enricher" and script.startswith(("seed_", "fetch_")):
                # `enricher` had no naming rule at all, so `enricher: fetch_thing.py`
                # passed and read as a fetch route to anyone scanning the manifest (#543).
                errors.append(
                    f"[{tag}] enricher must not be named like a seeder or fetcher, not {script!r}"
                )

        license_review = block.get("license_review")
        if license_review is not None and license_review not in LICENSE_REVIEWS:
            errors.append(f"[{tag}] invalid license_review {license_review!r}")
        license_text = str(block.get("license", "")).lower()
        if any(token in license_text for token in RESTRICTIVE):
            if license_review is None:
                errors.append(
                    f"[{tag}] restrictive/missing-open licence must declare "
                    "license_review: pending|approved|rejected"
                )
            elif license_review == "pending":
                notices.append(f"[{tag}] licence disposition pending under #517")
            elif license_review == "approved":
                # `approved` on a FLAGGED block produced zero errors AND zero notices,
                # so a restrictive licence could be waved through leaving no approver,
                # date or issue behind (#543). It must name who decided, and it stays
                # visible in the report rather than vanishing.
                reference = str(block.get("license_review_ref") or "").strip()
                if not reference:
                    errors.append(
                        f"[{tag}] license_review: approved must carry "
                        "license_review_ref naming an approver or issue"
                    )
                else:
                    notices.append(f"[{tag}] restrictive licence approved: {reference}")
        elif not str(block.get("license", "")).strip():
            # The error text says "restrictive/missing-open", but a block with no
            # licence at all was never asked for a review state (#543). Reported as a
            # notice: 11 blocks in the manifest are in this state today, and deciding
            # them is #517's licensing question, not this checker's.
            notices.append(f"[{tag}] no licence recorded; disposition unresolved under #517")

    for source, grouped in sorted(source_blocks.items()):
        if any(block.get("status") == "seeded" for block in grouped):
            seeders = [block.get("seeder") for block in grouped if block.get("seeder")]
            if not seeders:
                errors.append(f"source {source!r} has a seeded block but no block names a seeder")

    helper_scripts: set[str] = set()
    for index, entry in enumerate(helper_entries):
        if not isinstance(entry, dict):
            errors.append(f"source_helpers[{index}] must be a mapping")
            continue
        tag = str(entry.get("script") or f"source_helpers[{index}]")
        script = _script_name(entry.get("script"), "script", tag, errors)
        role = entry.get("role")
        if role not in HELPER_ROLES:
            errors.append(f"[{tag}] invalid helper role {role!r}")
        if not str(entry.get("reason") or "").strip():
            errors.append(f"[{tag}] helper entry requires a reason")
        if not script:
            continue
        if not script.startswith("seed_"):
            errors.append(f"[{tag}] helper registry may only classify seed_*.py scripts")
        if not (scripts / script).is_file():
            errors.append(f"[{tag}] helper script not found: scripts/{script}")
        if script in helper_scripts:
            errors.append(f"[{tag}] helper script is classified more than once")
        if script in referenced_seeders:
            errors.append(f"[{tag}] seeder is both source-backed and helper-classified")
        helper_scripts.add(script)

    referenced_fetchers = {
        _script_name(block["fetcher"], "fetcher", "", [])
        for block in blocks
        if isinstance(block, dict) and block.get("fetcher")
    }
    for script in sorted(scripts.glob("fetch_*.py")):
        if script.name not in referenced_fetchers:
            # Orphan detection globbed seed_*.py only, so an unregistered fetch route was
            # invisible (#543). A notice, not an error: six are unregistered today, and
            # registering them is a manifest decision rather than this PR's to make.
            notices.append(f"fetcher scripts/{script.name} is not referenced by any block")

    classified = referenced_seeders | helper_scripts
    for script in sorted(scripts.glob("seed_*.py")):
        if script.name not in classified:
            errors.append(
                f"seeder scripts/{script.name} is unclassified; reference it from "
                "download.yaml or scripts/source_helpers.yaml"
            )

    return Result(
        blocks=len(blocks),
        sources=len(source_blocks),
        statuses=status_counts,
        errors=errors,
        notices=notices,
    )


def main() -> int:
    result = validate_registry()
    summary = ", ".join(f"{count} {status}" for status, count in sorted(result.statuses.items()))
    print(
        f"download.yaml: {result.blocks} blocks, {result.sources} sources "
        f"(block statuses: {summary})"
    )
    for notice in result.notices:
        print(f"  NOTICE: {notice}")
    for error in result.errors:
        print(f"  ERROR: {error}")
    if result.errors:
        print(f"\n{len(result.errors)} error(s).")
        return 1
    print(f"\nOK ({len(result.notices)} reviewed notice(s), 0 warnings).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
