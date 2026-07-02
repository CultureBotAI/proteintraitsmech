#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from ECOD, the Evolutionary
Classification Of protein Domains from UT Southwestern (Grishin lab).

Source: http://prodata.swmed.edu/ecod/complete/distribution
Bulk file: ecod.latest.domains.txt (tab-delimited, ~689 MB, 1.8M rows)

Each domain row carries the full A / X / H / T / F hierarchy label
chain. Rather than emit ~1.8M ProteinTraitRecords (one per domain),
this seeder emits one record per *distinct hierarchy node* — the
canonical structural taxonomy — with:

  A (Architecture)              → STRUCT_ARCHITECTURE
  X (Possible Homology)         → STRUCT_HOMOLOGOUS_SUPERFAMILY
  H (Homology group)            → STRUCT_HOMOLOGOUS_SUPERFAMILY
  T (Topology group)            → STRUCT_TOPOLOGY
  F (Family)                    → STRUCT_FOLD

Each node's `parent_traits` list contains its immediate ancestor node's
CURIE (e.g. an F-group points to its parent T-group). The 1.8M actual
domains are surfaced as `canonical_examples` on the F-group records
(up to N per group; default 5, override with --max-examples).

The ECOD flat file encodes the hierarchy as one text column
(`architecture_name`, the A level, e.g. "beta barrels") plus a 4-part
dotted `f_id` field whose components are X.H.T.F.

    A id = slug(architecture_name)            (e.g. `beta-barrels`)
    X id = 1st component of f_id              (e.g. `1`)
    H id = 1st + 2nd                          (e.g. `1.1`)
    T id = 1st + 2nd + 3rd                    (e.g. `1.1.1`)
    F id = the full f_id                      (e.g. `1.1.1.3`)

Identifier scheme in xrefs: `ECOD:<level>.<id>` where <level> ∈
{A, X, H, T, F}. Labels come from the matching `*_name` column.

Requires the flat file at data/raw/ecod.latest.domains.txt (fetched by
`just fetch-ecod`). Idempotent, --apply/--force. Stream-parses the
file in one pass — memory is bounded by the number of distinct nodes
(~19K), not the file size.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
TRAITS_DIR = REPO_ROOT / "data" / "traits"

ECOD_TXT = RAW_DIR / "ecod.latest.domains.txt"

# ECOD is redistributed under a permissive academic license
# (http://prodata.swmed.edu/ecod/). No SPDX identifier — leave the
# license slot unset on individual records and note the source in
# definition_source.

LEVEL_TO_CATEGORY = {
    "A": ("STRUCT_ARCHITECTURE",         "structure/architecture"),
    "X": ("STRUCT_HOMOLOGOUS_SUPERFAMILY","structure/homologous_superfamily"),
    "H": ("STRUCT_HOMOLOGOUS_SUPERFAMILY","structure/homologous_superfamily"),
    "T": ("STRUCT_TOPOLOGY",             "structure/topology"),
    "F": ("STRUCT_FOLD",                 "structure/fold/ecod"),
}

# Column order in the v295 header (verified 2026-06):
#   uid ecod_domain_id manual_rep f_id pdb chain pdb_range seqid_range
#   architecture_name x_name h_name t_name f_name assembly_id
#   domain_id_short range_count arch_manual x_manual h_manual t_manual
#   f_manual valid_structure ligand_binding ligand_comp_ids ligand_pdbnum
COL_INDEX = {
    "uid": 0, "ecod_domain_id": 1, "manual_rep": 2, "f_id": 3,
    "pdb": 4, "chain": 5, "pdb_range": 6, "seqid_range": 7,
    "architecture_name": 8, "x_name": 9, "h_name": 10, "t_name": 11,
    "f_name": 12,
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


# ---------------------------------------------------------------------------
# Node model
# ---------------------------------------------------------------------------
#
# X.H.T.F is the 4-part dotted `f_id` in the flat file. The A level is
# a separate text column, so its ids are architecture_name slugs.


def truncate_id(f_id: str, level: str) -> str:
    depth = {"X": 1, "H": 2, "T": 3, "F": 4}.get(level)
    if depth is None:
        return ""
    parts = f_id.split(".")
    if len(parts) < depth:
        return ""
    return ".".join(parts[:depth])


def parent_level(level: str) -> str | None:
    return {"F": "T", "T": "H", "H": "X", "X": "A", "A": None}[level]


class Node:
    __slots__ = ("level", "node_id", "label", "example_count", "examples")

    def __init__(self, level: str, node_id: str, label: str) -> None:
        self.level = level
        self.node_id = node_id
        self.label = label
        self.example_count = 0
        self.examples: list[dict] = []


def stream_parse(path: Path, max_examples: int) -> tuple[
    dict[tuple[str, str], Node],
    dict[str, str],
]:
    """Return ({(level, node_id): Node}, {X-node-id: A-node-id})."""
    nodes: dict[tuple[str, str], Node] = {}
    x_to_a: dict[str, str] = {}

    def touch(level: str, node_id: str, label: str) -> Node:
        if not node_id:
            return None  # type: ignore[return-value]
        key = (level, node_id)
        node = nodes.get(key)
        if node is None:
            node = Node(level, node_id, label or "")
            nodes[key] = node
        elif not node.label and label:
            node.label = label
        return node

    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for raw_line in fh:
            if not raw_line or raw_line.startswith("#"):
                continue
            if raw_line.startswith("uid\t"):
                continue
            parts = raw_line.rstrip("\n").split("\t")
            if len(parts) < 13:
                continue
            f_id = parts[COL_INDEX["f_id"]]
            if not f_id or f_id.count(".") != 3:  # expect X.H.T.F (4 parts)
                continue
            pdb = parts[COL_INDEX["pdb"]]
            chain = parts[COL_INDEX["chain"]]
            pdb_range = parts[COL_INDEX["pdb_range"]]
            arch = parts[COL_INDEX["architecture_name"]]
            xname = parts[COL_INDEX["x_name"]]
            hname = parts[COL_INDEX["h_name"]]
            tname = parts[COL_INDEX["t_name"]]
            fname = parts[COL_INDEX["f_name"]]

            a_id = slugify(arch) or "unnamed"
            touch("A", a_id, arch)
            x_id = truncate_id(f_id, "X")
            x_to_a.setdefault(x_id, a_id)
            touch("X", x_id, xname)
            touch("H", truncate_id(f_id, "H"), hname)
            touch("T", truncate_id(f_id, "T"), tname)
            f_node = touch("F", truncate_id(f_id, "F"), fname)
            if f_node is None:
                continue
            f_node.example_count += 1
            if len(f_node.examples) < max_examples and pdb:
                f_node.examples.append({
                    "pdb": pdb,
                    "chain": chain,
                    "range": pdb_range,
                    "domain_id": parts[COL_INDEX["ecod_domain_id"]],
                })
    return nodes, x_to_a


# ---------------------------------------------------------------------------
# YAML emission
# ---------------------------------------------------------------------------


def label_for(level: str, node: Node) -> str:
    if node.label:
        return node.label
    return f"ECOD {level}-group {node.node_id}"


def build_yaml(node: Node, release: str, nodes: dict, x_to_a: dict[str, str]) -> str:
    category, _ = LEVEL_TO_CATEGORY[node.level]
    ident = f"ECOD:{node.level}.{node.node_id}"
    label = label_for(node.level, node)
    definition = f"ECOD {node.level}-group '{label}' ({node.node_id})."
    if node.level == "F" and node.example_count:
        definition += f" Comprises {node.example_count} classified domain(s)."

    lines: list[str] = []
    lines.append(f"identifier: {ident}")
    lines.append(f"label: {yaml_escape(label)}")
    folded = yaml_folded("", definition)
    lines.append(f"definition: {folded[0]}")
    lines.extend(folded[1:])
    lines.append(f"definition_source: {yaml_escape(release)}")
    lines.append("trait_axis: STRUCTURE")
    lines.append(f"trait_category: {category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    p_level = parent_level(node.level)
    if p_level:
        if node.level == "X":
            p_id = x_to_a.get(node.node_id, "")
        else:
            p_id = node.node_id.rsplit(".", 1)[0] if "." in node.node_id else ""
        if p_id and (p_level, p_id) in nodes:
            lines.append("parent_traits:")
            lines.append(f"  - ECOD:{p_level}.{p_id}")

    # ECOD is PDB-indexed; UniProt mapping requires a SIFTS follow-up.
    # For now the PDB representatives land as xrefs, one per example.
    if node.level == "F" and node.examples:
        xref_items: list[str] = []
        seen: set[str] = set()
        for ex in node.examples:
            for x in (f"PDB:{ex['pdb']}", f"ECOD:{ex['domain_id']}"):
                if x not in seen:
                    seen.add(x)
                    xref_items.append(x)
        if xref_items:
            lines.append("xrefs:")
            for x in xref_items:
                lines.append(f"  - {x}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def target_path(node: Node) -> Path:
    _, subdir = LEVEL_TO_CATEGORY[node.level]
    slug = slugify(node.label or node.node_id)
    return TRAITS_DIR / subdir / f"{slug}-{node.node_id.replace('.', '_')}.yaml"


def read_release_stamp() -> str:
    with ECOD_TXT.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("# Version:"):
                v = line.split(":", 1)[1].strip()
                return f"ECOD {v}"
            if not line.startswith("#"):
                break
    return "ECOD latest"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="write YAMLs (default: dry-run)")
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing files")
    parser.add_argument("--max-examples", type=int, default=5,
                        help="max canonical_examples per F-group (default 5)")
    parser.add_argument("--levels", default="A,X,H,T,F",
                        help="comma-separated levels to emit (default all)")
    args = parser.parse_args()

    if not ECOD_TXT.exists():
        print(f"missing {ECOD_TXT}; run `just fetch-ecod` first", file=sys.stderr)
        return 2

    levels = {lv.strip().upper() for lv in args.levels.split(",")}
    unknown = levels - set(LEVEL_TO_CATEGORY)
    if unknown:
        print(f"unknown level(s): {unknown}", file=sys.stderr)
        return 2

    release = read_release_stamp()
    print(f"Streaming {ECOD_TXT.name} ({release})…")
    nodes, x_to_a = stream_parse(ECOD_TXT, args.max_examples)
    print(f"Distinct nodes: "
          f"A={sum(1 for k in nodes if k[0] == 'A')}, "
          f"X={sum(1 for k in nodes if k[0] == 'X')}, "
          f"H={sum(1 for k in nodes if k[0] == 'H')}, "
          f"T={sum(1 for k in nodes if k[0] == 'T')}, "
          f"F={sum(1 for k in nodes if k[0] == 'F')}")

    stats = {"written": 0, "skipped": 0, "planned": 0, "by_dir": {}}
    for key, node in nodes.items():
        if node.level not in levels:
            continue
        path = target_path(node)
        dkey = str(path.parent.relative_to(TRAITS_DIR))
        stats["by_dir"][dkey] = stats["by_dir"].get(dkey, 0) + 1
        if path.exists() and not args.force:
            stats["skipped"] += 1
            continue
        stats["planned"] += 1
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_yaml(node, release, nodes, x_to_a),
                            encoding="utf-8")
            stats["written"] += 1

    print()
    print("Per-directory totals:")
    for d, n in sorted(stats["by_dir"].items()):
        print(f"  data/traits/{d:34s} {n}")
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
