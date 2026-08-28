#!/usr/bin/env python3
"""Govern the trait-category vocabulary, here and across the Mech fleet (#581).

Two questions, one audit, because both are "is a category value one this project
recognises":

MANIFEST_UNKNOWN_CATEGORY
    A ``trait_categories`` entry in ``download.yaml`` that is not a permissible
    value of ``ProteinTraitCategoryEnum``.  ``check_sources.py`` validates block
    shape, roles, statuses, script naming and licence disposition, and never
    looked at categories at all: ``trait_categories: [SEQ_NOT_A_REAL_CATEGORY]``
    passed with zero errors.  A category renamed in the schema leaves every
    manifest block silently stale.

SHARED_TOKEN_MEANING_DRIFT
    A token present in BOTH this Mech's vocabulary and TraitMech's, whose
    description differs between them.

SHARED_TOKEN_DROPPED
    A token the pinned snapshot shows in both, now absent here.

The two vocabularies are deliberately NOT converging.  TraitMech's eleven values
describe organism traits (``METABOLISM``, ``MORPHOLOGY``); this Mech's sixty-eight
describe protein traits (``SEQ_DOMAIN``, ``FUNC_ENZYMATIC_ACTIVITY``).  They meet
on two administrative tokens, ``UPPER`` and ``OTHER``, and it is only that shared
surface this audit governs: the same token must not come to mean two things in two
repositories that a reader moves between.

TraitMech is a separate repository and is not present in CI, so the comparison runs
against ``conf/traitmech_category_vocabulary.yaml`` -- a reviewed pin, refreshed on
purpose with ``--refresh``, the same shape as the vendored-sync ref.

ADVISORY BY DEFAULT: this exits 0 whatever it finds, so it can land and be watched
before it blocks anyone.  ``--fail-on any`` makes every finding an error, which is
what a CI gate would pass once the report has been quiet for a while.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml"
MANIFEST = REPO_ROOT / "download.yaml"
PINNED = REPO_ROOT / "conf" / "traitmech_category_vocabulary.yaml"
LOCAL_ENUM = "ProteinTraitCategoryEnum"


def _permissible_values(schema: dict, enum_name: str) -> dict[str, str | None]:
    """``value -> description`` for one enum, tolerating a bare value with no body."""
    spec = (schema.get("enums") or {}).get(enum_name) or {}
    out: dict[str, str | None] = {}
    for value, body in (spec.get("permissible_values") or {}).items():
        out[str(value)] = (body or {}).get("description") if isinstance(body, dict) else None
    return out


def local_vocabulary(schema_path: Path = SCHEMA) -> dict[str, str | None]:
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    values = _permissible_values(schema, LOCAL_ENUM)
    if not values:
        # A vocabulary audit that read no vocabulary must not report agreement.
        raise SystemExit(f"FAIL: {LOCAL_ENUM} has no permissible values in {schema_path}")
    return values


def pinned_vocabulary(
    pinned_path: Path = PINNED,
) -> tuple[dict[str, str | None], str, set[str]]:
    """``(values, pinned ref, governed tokens)``.

    The governed set is read, not computed as an intersection: the vocabularies are
    disjoint by design, so "in the pin but not local" cannot distinguish a token that
    was never shared from one that was dropped (#583).
    """
    document = yaml.safe_load(pinned_path.read_text(encoding="utf-8"))
    values = {
        str(name): (body or {}).get("description")
        for name, body in (document.get("permissible_values") or {}).items()
    }
    if not values:
        raise SystemExit(f"FAIL: {pinned_path} pins no values")
    governed = {str(token) for token in (document.get("governed_tokens") or [])}
    return values, str(document.get("pinned_ref", "unknown")), governed


def manifest_categories(manifest_path: Path = MANIFEST) -> dict[str, list[str]]:
    """``category -> block names declaring it``."""
    blocks = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or []
    declared: dict[str, list[str]] = {}
    for index, block in enumerate(blocks):
        if not isinstance(block, dict):
            continue
        tag = str(block.get("name") or block.get("source") or f"block[{index}]")
        for value in block.get("trait_categories") or []:
            declared.setdefault(str(value), []).append(tag)
    return declared


def findings(
    local: dict[str, str | None],
    pinned: dict[str, str | None],
    declared: dict[str, list[str]],
    governed: set[str] | None = None,
) -> list[tuple[str, str]]:
    """``(class, message)`` pairs, deterministically ordered."""
    out: list[tuple[str, str]] = []
    for category in sorted(declared):
        if category not in local:
            blocks = ", ".join(sorted(set(declared[category])))
            out.append(
                (
                    "MANIFEST_UNKNOWN_CATEGORY",
                    f"{category!r} is declared by {blocks} but is not a permissible value "
                    f"of {LOCAL_ENUM}",
                )
            )
    for token in sorted(set(local) & set(pinned)):
        if local[token] != pinned[token]:
            out.append(
                (
                    "SHARED_TOKEN_MEANING_DRIFT",
                    f"{token!r} means {local[token]!r} here and {pinned[token]!r} in "
                    f"TraitMech; a shared token must not mean two things",
                )
            )
    for token in sorted(governed or set()):
        if token not in local:
            out.append(
                (
                    "SHARED_TOKEN_DROPPED",
                    f"{token!r} is a governed cross-Mech token but is no longer a "
                    f"permissible value of {LOCAL_ENUM}",
                )
            )
    return out


def refresh(traitmech_root: Path, pinned_path: Path = PINNED) -> int:
    """Re-pin the snapshot from a local TraitMech checkout."""
    source = traitmech_root / "src" / "traitmech" / "schema" / "traitmech.yaml"
    if not source.is_file():
        print(f"ERROR: no TraitMech schema at {source}", file=sys.stderr)
        return 2
    schema = yaml.safe_load(source.read_text(encoding="utf-8"))
    values = _permissible_values(schema, "TraitCategoryEnum")
    if not values:
        print(f"ERROR: TraitCategoryEnum has no permissible values in {source}", file=sys.stderr)
        return 2
    head = subprocess.run(
        ["git", "-C", str(traitmech_root), "rev-parse", "HEAD"], capture_output=True, text=True
    )
    document = yaml.safe_load(pinned_path.read_text(encoding="utf-8"))
    existing = {
        str(name): (body or {}).get("description")
        for name, body in (document.get("permissible_values") or {}).items()
    }
    if existing == values:
        # pinned_ref means "the ref these values came from", not "the last ref seen".
        # Rewriting it for an upstream commit that did not touch the vocabulary churns
        # a reviewed file for no reason and buries the refs that did change something.
        print(
            f"unchanged: {len(values)} TraitMech values already pinned; ref left at "
            f"{str(document.get('pinned_ref', 'unknown'))[:11]}"
        )
        return 0
    document["pinned_ref"] = head.stdout.strip() or "unknown"
    document["permissible_values"] = {
        name: {"description": values[name]} for name in sorted(values)
    }
    pinned_path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=88), encoding="utf-8"
    )
    print(f"re-pinned {len(values)} TraitMech values at {document['pinned_ref'][:11]}")
    return 0


def verify_pin(traitmech_root: Path, pinned_path: Path = PINNED) -> int:
    """Fail when a local TraitMech checkout disagrees with the pin (#584).

    The fleet's other cross-repo check fetches the hub live, so hub drift is caught
    without anyone acting. This pin is static, so TraitMech drift is invisible to CI,
    which has only this repository. This is the offline half: run it anywhere both
    repositories exist.
    """
    source = traitmech_root / "src" / "traitmech" / "schema" / "traitmech.yaml"
    if not source.is_file():
        print(f"ERROR: no TraitMech schema at {source}", file=sys.stderr)
        return 2
    live = _permissible_values(
        yaml.safe_load(source.read_text(encoding="utf-8")), "TraitCategoryEnum"
    )
    pinned, pinned_ref, _governed = pinned_vocabulary(pinned_path)
    if live == pinned:
        print(f"OK: pin {pinned_ref[:11]} matches {source}")
        return 0
    for token in sorted(set(live) | set(pinned)):
        if live.get(token) != pinned.get(token):
            print(
                f"  PIN_STALE: {token!r} pinned as {pinned.get(token)!r}, "
                f"TraitMech now has {live.get(token)!r}"
            )
    print("\nThe pin is stale; re-pin with --refresh after reviewing the change.")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh",
        type=Path,
        metavar="TRAITMECH_ROOT",
        help="re-pin conf/traitmech_category_vocabulary.yaml from a local "
        "TraitMech checkout, then exit",
    )
    parser.add_argument(
        "--verify-pin",
        type=Path,
        metavar="TRAITMECH_ROOT",
        help="fail if a local TraitMech checkout disagrees with the pin. CI has only "
        "this repository, so pin staleness is otherwise invisible (#584)",
    )
    parser.add_argument(
        "--fail-on",
        choices=("never", "any"),
        default="never",
        help="'never' (default) reports and exits 0; 'any' makes every "
        "finding an error, for use once this gates CI",
    )
    args = parser.parse_args(argv)

    if args.refresh is not None:
        return refresh(args.refresh)
    if args.verify_pin is not None:
        return verify_pin(args.verify_pin)

    local = local_vocabulary()
    pinned, pinned_ref, governed = pinned_vocabulary()
    declared = manifest_categories()
    shared = sorted(governed)

    print(
        f"{LOCAL_ENUM}: {len(local)} values; TraitMech pin {pinned_ref[:11]}: "
        f"{len(pinned)} values; governed tokens: {len(shared)} ({', '.join(shared) or 'none'})"
    )
    print(f"download.yaml declares {len(declared)} distinct categories")

    results = findings(local, pinned, declared, governed)
    for kind, message in results:
        print(f"  {kind}: {message}")
    if not results:
        print("\nOK: no unknown manifest category, no shared-token drift.")
        return 0
    print(f"\n{len(results)} finding(s).")
    if args.fail_on == "any":
        return 1
    print("Advisory run (--fail-on never): reported, not failed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
