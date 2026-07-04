#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from SCOPe, the extended Structural
Classification of Proteins (Berkeley / SCOP).

Source: https://scop.berkeley.edu/downloads/

The seeder consumes three tab-delimited parseable files:

    data/raw/scope/dir.des.scope.<release>.txt
        one row per node with sunid, sccs, node-level, sid, description
    data/raw/scope/dir.hie.scope.<release>.txt
        parent/child edges (child_sunid, parent_sunid, [siblings])
    data/raw/scope/dir.cla.scope.<release>.txt
        leaf-node classification strings (PDB IDs, ranges, sccs, sunids)

Because scop.berkeley.edu currently sits behind an anti-bot challenge
that rejects plain HTTP clients, this seeder assumes the files have
been manually placed under `data/raw/scope/`. `just fetch-scope`
attempts an automated download but is expected to fail — treat it as
an announcement of the required filenames rather than a live fetch.

Level mapping (SCOPe standard 7-level hierarchy):

    'cl' Class           → STRUCT_CLASS
    'cf' Fold            → STRUCT_FOLD
    'sf' Superfamily     → STRUCT_HOMOLOGOUS_SUPERFAMILY
    'fa' Family          → STRUCT_FOLD    (family within a fold)
    'dm' Protein domain  → STRUCT_DOMAIN
    'sp' Species         (skipped — instance-level; not a trait)
    'px' Domain          (skipped — instance-level; not a trait)

Each emitted record carries:
    identifier: SCOP:<sunid>
    label: description
    parent_traits: [SCOP:<parent_sunid>] via dir.hie
    xrefs: [SCOP:<sccs>]  (the dotted classification string)
    license: CC-BY 4.0  (SCOPe terms; tighter than the CC0 corpus default)
    mapping_status: SEEDED

Dry-run by default; --apply to write. Stream-parses each file.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw" / "scope"
TRAITS_DIR = REPO_ROOT / "data" / "traits"

DES_PATTERN = "dir.des.scope.*.txt"
HIE_PATTERN = "dir.hie.scope.*.txt"

LEVEL_TO_CATEGORY = {
    "cl": ("STRUCT_CLASS",                 "structure/class/scope"),
    "cf": ("STRUCT_FOLD",                  "structure/fold/scope"),
    "sf": ("STRUCT_HOMOLOGOUS_SUPERFAMILY","structure/homologous_superfamily"),
    "fa": ("STRUCT_FOLD",                  "structure/fold/scope"),
    "dm": ("STRUCT_DOMAIN",                "structure/domain/scope"),
    # 'sp' species and 'px' domain-instance skipped — those are examples
    # of a trait, not the trait itself.
}


_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(text: str) -> str:
    s = _SLUG_RE.sub("-", (text or "").lower()).strip("-")
    return s[:80] or "node"


def yaml_escape(text: str) -> str:
    if text is None or text == "":
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def yaml_folded(indent: str, text: str) -> list[str]:
    text = " ".join((text or "").split())
    if not text:
        return [">-", f"{indent}  \"\""]
    return [">-", f"{indent}  {text}"]


def latest(pattern: str) -> Path | None:
    matches = sorted(RAW_DIR.glob(pattern))
    if not matches:
        return None
    return matches[-1]


def parse_des(path: Path) -> dict[str, dict]:
    """dir.des.scope columns (tab-delimited):
        sunid  level  sccs  sid  description
    Returns {sunid: {'level': ..., 'sccs': ..., 'sid': ..., 'desc': ...}}."""
    out: dict[str, dict] = {}
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            sunid, level, sccs, sid, desc = parts[0], parts[1], parts[2], parts[3], parts[4]
            out[sunid] = {
                "level": level,
                "sccs": sccs,
                "sid": sid,
                "desc": desc,
            }
    return out


def parse_hie(path: Path) -> dict[str, str]:
    """dir.hie.scope columns (tab-delimited):
        child_sunid  parent_sunid  child_sibling_sunids (comma-separated)
    Returns {child_sunid: parent_sunid}."""
    out: dict[str, str] = {}
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            child, parent = parts[0], parts[1]
            if parent and parent != "0":
                out[child] = parent
    return out


def build_yaml(sunid: str, node: dict, parents: dict[str, str], release: str) -> str | None:
    level = node.get("level", "")
    routed = LEVEL_TO_CATEGORY.get(level)
    if not routed:
        return None
    category, _ = routed

    label = node.get("desc") or node.get("sccs") or f"SCOPe {level} {sunid}"
    definition = f"SCOPe {level}-level node '{label}' (sccs {node.get('sccs') or '—'})."

    lines: list[str] = []
    lines.append(f"identifier: SCOP:{sunid}")
    lines.append(f"label: {yaml_escape(label)}")
    folded = yaml_folded("", definition)
    lines.append(f"definition: {folded[0]}")
    lines.extend(folded[1:])
    lines.append(f"definition_source: {yaml_escape(release)}")
    lines.append("trait_axis: STRUCTURE")
    lines.append(f"trait_category: {category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    parent_sunid = parents.get(sunid)
    if parent_sunid:
        lines.append("parent_traits:")
        lines.append(f"  - SCOP:{parent_sunid}")

    xrefs = []
    if node.get("sccs"):
        xrefs.append(f"SCOP:{node['sccs']}")
    if node.get("sid") and node["sid"] != "-":
        xrefs.append(f"SCOP:{node['sid']}")
    if xrefs:
        lines.append("xrefs:")
        for x in xrefs:
            lines.append(f"  - {x}")

    lines.append("license: CC-BY 4.0")   # SCOPe is CC-BY (tighter than the CC0 corpus default)
    return "\n".join(lines) + "\n"


def target_path(sunid: str, node: dict) -> Path:
    level = node.get("level", "")
    _, subdir = LEVEL_TO_CATEGORY[level]
    slug = slugify(node.get("desc") or node.get("sccs") or sunid)
    return TRAITS_DIR / subdir / f"{slug}-sunid{sunid}.yaml"


def release_from_path(path: Path) -> str:
    m = re.search(r"scope\.(\d+\.\d+(?:-stable)?)\.txt$", path.name)
    return f"SCOPe {m.group(1)}" if m else f"SCOPe ({path.name})"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="write YAMLs (default: dry-run)")
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing files")
    parser.add_argument("--des", help="explicit path to dir.des.scope.*.txt")
    parser.add_argument("--hie", help="explicit path to dir.hie.scope.*.txt")
    args = parser.parse_args()

    des_path = Path(args.des) if args.des else latest(DES_PATTERN)
    hie_path = Path(args.hie) if args.hie else latest(HIE_PATTERN)
    if des_path is None or hie_path is None:
        print(f"missing {RAW_DIR}/{DES_PATTERN} or {HIE_PATTERN}. "
              "Download manually from https://scop.berkeley.edu/downloads/ "
              "and drop the files into data/raw/scope/.", file=sys.stderr)
        return 2

    release = release_from_path(des_path)
    print(f"Reading {des_path.name} + {hie_path.name} ({release})…")
    nodes = parse_des(des_path)
    parents = parse_hie(hie_path)
    print(f"Parsed {len(nodes)} nodes, {len(parents)} parent edges.")

    stats = {"written": 0, "skipped": 0, "planned": 0, "by_dir": {},
             "unsupported": {}}
    for sunid, node in nodes.items():
        level = node.get("level", "")
        if level not in LEVEL_TO_CATEGORY:
            stats["unsupported"][level] = stats["unsupported"].get(level, 0) + 1
            continue
        yaml_body = build_yaml(sunid, node, parents, release)
        if yaml_body is None:
            continue
        path = target_path(sunid, node)
        dkey = str(path.parent.relative_to(TRAITS_DIR))
        stats["by_dir"][dkey] = stats["by_dir"].get(dkey, 0) + 1
        if path.exists() and not args.force:
            stats["skipped"] += 1
            continue
        stats["planned"] += 1
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml_body, encoding="utf-8")
            stats["written"] += 1

    print()
    print("Per-directory totals:")
    for d, n in sorted(stats["by_dir"].items()):
        print(f"  data/traits/{d:34s} {n}")
    if stats["unsupported"]:
        print()
        print("Skipped SCOPe levels (not modeled):")
        for lv, n in sorted(stats["unsupported"].items()):
            print(f"  {lv:4s} {n}")
    print()
    if args.apply:
        print(f"Wrote {stats['written']} file(s); skipped {stats['skipped']} existing.")
    else:
        print(f"Dry-run — would write {stats['planned']} file(s); "
              f"{stats['skipped']} already exist.")
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
