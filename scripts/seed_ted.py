#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from the TED (Encyclopedia of Domains)
novel-fold and high-symmetry-fold catalogues.

NOTE (definition-state review, research/definition-state-review.md): TED entries
are AlphaFold *novel* / de-novo folds with no reference structural classification,
so a named STRUCTURAL definition (like SCOP/CATH/ECOD carry) is not sourceable —
the record's geometric summary (residues, length, pLDDT, symmetry) is the best
available. Closing this gap would require computing geometric descriptors
(secondary-structure string, contact topology) from the AF model — a future pass,
not a text lift.

Source:
  Zenodo record 13908086 (v5, 2024-10-31, CC-BY 4.0)
  DOI:10.5281/zenodo.13908086

Files consumed (fetch via `just fetch-ted`):
  data/raw/ted_novel_folds.tsv.gz         — 7,427 novel fold representatives
  data/raw/ted_high_symmetry_folds.tsv.gz — 6,433 highly symmetric fold reps

Emits ProteinTraitRecord YAMLs to:
  data/traits/structure/fold/novel/<slug>.yaml
  data/traits/structure/fold/high_symmetry/<slug>.yaml

All records land as STRUCTURE / STRUCT_FOLD / SEEDED. Each carries a
`canonical_examples` entry linking to the source AlphaFold model +
NCBITaxon, plus an `evidence` item citing the Zenodo DOI.

Idempotent — skips existing files unless --force. Dry-run by default.
Stdlib-only.

Column layout for `*.domain_summary.tsv` (inferred from the Zenodo record
description and TED tooling; only the confident columns are consumed):

  0  ted_id            AF-<UniProt>-F1-model_v4_TED<NN>
  1  md5_domain
  2  consensus_level   high | medium | low
  3  chopping          residue ranges (single or `_`-joined multi-segment)
  4  domain_length
  5  num_segments
  6  plddt             mean pLDDT
  7..11                secondary-structure counts (not interpreted here)
  12 proteome_id       proteome-tax_id-<taxid>-<idx>_v4
  13..15               CATH class/architecture/topology (or "-" when novel)
  16..18               novelty / globularity metrics (not interpreted)
  19 taxon_name        NCBI Taxonomy scientific name
  20 taxonomy_lineage  comma-separated NCBI lineage
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
TRAITS_DIR = REPO_ROOT / "data" / "traits"

SOURCES = [
    {
        "name": "novel",
        "tsv": RAW_DIR / "ted_novel_folds.tsv.gz",
        "subdir": "structure/fold/novel",
        "label_kind": "TED novel fold",
    },
    {
        "name": "high_symmetry",
        "tsv": RAW_DIR / "ted_high_symmetry_folds.tsv.gz",
        "subdir": "structure/fold/high_symmetry",
        "label_kind": "TED highly-symmetric fold",
    },
]

RELEASE = "TED (Encyclopedia of Domains) v5, 2024-10-31 (Zenodo DOI:10.5281/zenodo.13908086)"
ZENODO_DOI = "DOI:10.5281/zenodo.13908086"

_AF_ID_RE = re.compile(r"^AF-([A-Z0-9]+)-F\d+-model_v\d+_TED(\d+)$")
_PROTEOME_RE = re.compile(r"^proteome-tax_id-(\d+)-\d+_v\d+$")
_SAFE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _SAFE.sub("-", text.lower()).strip("-")


def parse_ted_row(row: list[str]) -> dict | None:
    if len(row) < 21:
        return None
    ted_id = row[0]
    m = _AF_ID_RE.match(ted_id)
    if not m:
        return None
    uniprot, ted_index = m.group(1), m.group(2)

    entry = {
        "ted_id": ted_id,
        "uniprot": uniprot,
        "ted_index": ted_index,
        "md5": row[1],
        "consensus_level": row[2],
        "chopping": row[3],
        "length": row[4],
        "num_segments": row[5],
        "plddt": row[6],
        "proteome_id": row[12],
        "taxon_name": row[19].replace("_", " "),
        "lineage": row[20],
    }

    pm = _PROTEOME_RE.match(row[12] or "")
    entry["taxid"] = pm.group(1) if pm else None
    return entry


# ---------------------------------------------------------------------------
# YAML emission
# ---------------------------------------------------------------------------


_YAML_UNSAFE = set(':#{}[],&*!|>%@`\\"\'')
_YAML_RESERVED = {"null", "true", "false", "yes", "no", "on", "off", "~"}


def yaml_scalar(text: str) -> str:
    if not text:
        return '""'
    if any(c in _YAML_UNSAFE for c in text) or text[0] in "-?" or text.lower() in _YAML_RESERVED:
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def build_yaml(entry: dict, source: dict) -> str:
    identifier = f"TED:{entry['ted_id']}"
    label = f"{source['label_kind']} {entry['ted_id']}"

    definition_bits = [
        f"{source['label_kind']} observed in {entry['taxon_name']} "
        f"(AlphaFold model AF-{entry['uniprot']}-F1)",
        f"residues {entry['chopping'].replace('_', ', ')}",
        f"length {entry['length']}",
        f"mean pLDDT {entry['plddt']}",
        f"consensus {entry['consensus_level']}",
    ]
    definition = "; ".join(definition_bits) + "."

    lines: list[str] = []
    lines.append(f"identifier: {identifier}")
    lines.append(f"label: {yaml_scalar(label)}")
    lines.append("definition: >-")
    lines.append(f"  {definition}")
    lines.append(f"definition_source: {yaml_scalar(RELEASE)}")
    lines.append("trait_axis: STRUCTURE")
    lines.append("trait_category: STRUCT_FOLD")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    xrefs = [
        f"AlphaFoldDB:{entry['uniprot']}",
        f"UniProtKB:{entry['uniprot']}",
    ]
    lines.append("xrefs:")
    for x in xrefs:
        lines.append(f"  - {x}")

    lines.append("canonical_examples:")
    lines.append(f"  - protein_id: UniProtKB:{entry['uniprot']}")
    lines.append(f"    protein_label: {yaml_scalar('AlphaFold model AF-' + entry['uniprot'] + '-F1')}")
    if entry["taxid"]:
        lines.append(f"    taxon_id: NCBITaxon:{entry['taxid']}")
    lines.append(f"    taxon_label: {yaml_scalar(entry['taxon_name'])}")
    lines.append(
        f"    note: {yaml_scalar('TED domain ' + entry['ted_id'] + ', chopping ' + entry['chopping'] + ', pLDDT ' + entry['plddt'])}"
    )

    lines.append("evidence:")
    lines.append(f"  - reference: {ZENODO_DOI}")
    lines.append(f"    notes: {yaml_scalar(RELEASE + ' — ' + source['label_kind'] + ' set')}")

    return "\n".join(lines) + "\n"


def target_path(entry: dict, source: dict) -> Path:
    slug = f"af-{entry['uniprot'].lower()}-ted{entry['ted_index']}"
    return TRAITS_DIR / source["subdir"] / f"{slug}.yaml"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="cap entries per source in row order — smoke tests only",
    )
    parser.add_argument(
        "--only",
        choices=("novel", "high_symmetry"),
        default=None,
        help="process only one catalogue",
    )
    args = parser.parse_args()

    for src in SOURCES:
        if not src["tsv"].exists():
            print(
                f"ERROR: {src['tsv'].relative_to(REPO_ROOT)} not found. "
                f"Run `just fetch-ted` first.",
                file=sys.stderr,
            )
            return 2

    stats = {"written": 0, "skipped": 0, "planned": 0, "malformed": 0, "by_dir": {}}

    for src in SOURCES:
        if args.only and args.only != src["name"]:
            continue
        with gzip.open(src["tsv"], "rt", encoding="utf-8", errors="replace") as fh:
            entries: list[dict] = []
            for line in fh:
                row = line.rstrip("\n").split("\t")
                entry = parse_ted_row(row)
                if entry is None:
                    stats["malformed"] += 1
                    continue
                entries.append(entry)
                if args.limit and len(entries) >= args.limit:
                    break

        print(f"{src['name']}: {len(entries)} entries parsed from {src['tsv'].name}.")

        for entry in entries:
            path = target_path(entry, src)
            key = str(path.parent.relative_to(TRAITS_DIR))
            stats["by_dir"][key] = stats["by_dir"].get(key, 0) + 1

            if path.exists() and not args.force:
                stats["skipped"] += 1
                continue
            stats["planned"] += 1
            if args.apply:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(build_yaml(entry, src))
                stats["written"] += 1

    print()
    print("Per-directory totals:")
    for d, n in sorted(stats["by_dir"].items()):
        print(f"  data/traits/{d:34s} {n}")
    print()
    if args.apply:
        print(
            f"Wrote {stats['written']} file(s); skipped {stats['skipped']} existing; "
            f"malformed rows: {stats['malformed']}."
        )
    else:
        print(
            f"Dry-run — would write {stats['planned']} file(s); "
            f"{stats['skipped']} already exist; malformed rows: {stats['malformed']}."
        )
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
