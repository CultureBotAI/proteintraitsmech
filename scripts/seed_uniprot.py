#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from UniProtKB flat-file `FT` lines.

Each supported FT feature (TRANSMEM, DOMAIN, MOTIF, COMPBIAS, BINDING,
ACT_SITE, SITE, DISULFID, METAL, MOD_RES, LIPID, CARBOHYD, CROSSLNK,
SIGNAL, PROPEP, INTRAMEM, HELIX, STRAND, TURN, and REGION when
/note="Disordered") becomes one ProteinTraitRecord.

Emitted layout mirrors the existing seeds:

  data/traits/sequence/composition/     COMPBIAS
  data/traits/sequence/disorder/        REGION /note=Disordered
  data/traits/sequence/motif/           MOTIF (UniProt curator-defined; PROSITE lives elsewhere)
  data/traits/sequence/ptm_site/        MOD_RES + LIPID + CARBOHYD + CROSSLNK
  data/traits/sequence/signal_peptide/  SIGNAL
  data/traits/sequence/propeptide/      PROPEP
  data/traits/structure/active_site/    ACT_SITE
  data/traits/structure/binding_site/   BINDING (non-metal ligand) + SITE
  data/traits/structure/metal_site/     BINDING (metal ligand) + METAL
  data/traits/structure/disulfide/      DISULFID
  data/traits/structure/domain/         DOMAIN
  data/traits/structure/secondary/      HELIX + STRAND + TURN
  data/traits/mixed/transmembrane/      TRANSMEM + INTRAMEM

Input options:
  --accession B0R5N7 [--accession …]    fetch each accession from UniProt REST
  --from-file <path>                    file with one accession per line
  --input <path>                        pre-downloaded flat file (single or multi-entry)

Idempotent — skips existing YAMLs unless --force. Stdlib-only; the fetch
step uses urllib.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_DIR = REPO_ROOT / "data" / "traits"

UNIPROT_TXT_URL = "https://rest.uniprot.org/uniprotkb/{acc}.txt"


# ---------------------------------------------------------------------------
# FT-type routing
# ---------------------------------------------------------------------------

FT_TYPE_MAP: dict[str, tuple[str, str, str]] = {
    # ("axis", "category", "subdir under data/traits/")
    "TRANSMEM":  ("SEQUENCE_STRUCTURE", "MIXED_TRANSMEMBRANE", "mixed/transmembrane"),
    "INTRAMEM":  ("SEQUENCE_STRUCTURE", "MIXED_TRANSMEMBRANE", "mixed/transmembrane"),
    "COMPBIAS":  ("SEQUENCE",           "SEQ_COMPOSITION",     "sequence/composition"),
    "MOTIF":     ("SEQUENCE",           "SEQ_MOTIF",           "sequence/motif"),
    "DOMAIN":    ("STRUCTURE",          "STRUCT_DOMAIN",       "structure/domain"),
    "ACT_SITE":  ("STRUCTURE",          "STRUCT_ACTIVE_SITE",  "structure/active_site"),
    "SITE":      ("STRUCTURE",          "STRUCT_BINDING_SITE", "structure/binding_site"),
    "METAL":     ("STRUCTURE",          "STRUCT_METAL_SITE",   "structure/metal_site"),
    "DISULFID":  ("STRUCTURE",          "STRUCT_DISULFIDE",    "structure/disulfide"),
    "SIGNAL":    ("SEQUENCE",           "SEQ_SIGNAL_PEPTIDE",  "sequence/signal_peptide"),
    "PROPEP":    ("SEQUENCE",           "SEQ_PROPEPTIDE",      "sequence/propeptide"),
    "MOD_RES":   ("SEQUENCE",           "SEQ_PTM_SITE",        "sequence/ptm_site"),
    "LIPID":     ("SEQUENCE",           "SEQ_PTM_SITE",        "sequence/ptm_site"),
    "CARBOHYD":  ("SEQUENCE",           "SEQ_PTM_SITE",        "sequence/ptm_site"),
    "CROSSLNK":  ("SEQUENCE",           "SEQ_PTM_SITE",        "sequence/ptm_site"),
    "HELIX":     ("STRUCTURE",          "STRUCT_SECONDARY",    "structure/secondary"),
    "STRAND":    ("STRUCTURE",          "STRUCT_SECONDARY",    "structure/secondary"),
    "TURN":      ("STRUCTURE",          "STRUCT_SECONDARY",    "structure/secondary"),
}

# Contextual routing:
#   REGION      → SEQ_DISORDER *only* if /note starts with "Disordered"
#   BINDING     → STRUCT_METAL_SITE if ligand looks metal, else STRUCT_BINDING_SITE

DISORDER_SUBDIR = "sequence/disorder"

# Metal / metal-cluster ligands. Word-boundary-checked against /ligand
# (case-insensitive). Includes complex metal cofactors like heme, cobalamin,
# molybdopterin — they're metal-coordination biologically, so route to
# STRUCT_METAL_SITE. Curators can refine.
_METAL_TOKENS = [
    "zinc", "iron", "magnesium", "calcium", "manganese", "copper",
    "nickel", "cobalt", "cadmium", "potassium", "sodium", "molybdenum",
    "tungsten", "vanadium", "mercury", "aluminum", "aluminium", "lithium",
    "chromium", "silver", "gold",
    "iron-sulfur", "fe-s", "2fe-2s", "3fe-4s", "4fe-4s", "fes cluster",
    "heme", "haem", "chlorophyll", "cobalamin", "molybdopterin",
    "siroheme", "corrin", "porphyrin",
    "zn(2+)", "fe(2+)", "fe(3+)", "mg(2+)", "ca(2+)", "mn(2+)",
    "cu(1+)", "cu(2+)", "ni(2+)", "co(2+)", "cd(2+)", "k(+)", "na(+)",
]
_METAL_RE = re.compile(
    r"(?<![A-Za-z0-9])(" + "|".join(re.escape(t) for t in _METAL_TOKENS) + r")(?![A-Za-z0-9])",
    re.IGNORECASE,
)


def is_metal_ligand(ligand_name: str) -> bool:
    if not ligand_name:
        return False
    return bool(_METAL_RE.search(ligand_name))


# ---------------------------------------------------------------------------
# Flat-file parser
# ---------------------------------------------------------------------------

# FT header lines look like `FT   TRANSMEM        27..47`
# FT continuation lines look like `FT                   /note="Helical"`
# We split each entry on `//` and iterate FT lines.

_ATTR_RE = re.compile(r'/([a-z_]+)="((?:[^"\\]|\\.)*)"', re.DOTALL)
_RANGE_RE = re.compile(r"^[<>?]?(\d+)(?:\.\.[<>?]?(\d+))?$")


class UniProtEntry:
    def __init__(self):
        self.accession = ""
        self.entry_name = ""
        self.protein_name = ""
        self.gene_name = ""
        self.organism = ""
        self.taxid = ""
        self.uniprot_version = ""
        self.features: list[dict] = []
        self.sequence_length: int | None = None


def parse_flatfile(text: str) -> list[UniProtEntry]:
    entries: list[UniProtEntry] = []
    for raw in text.split("\n//\n"):
        raw = raw.strip("\n")
        if not raw.startswith("ID "):
            continue
        entry = UniProtEntry()
        _parse_entry_body(raw, entry)
        entries.append(entry)
    return entries


def _parse_entry_body(raw: str, entry: UniProtEntry) -> None:
    lines = raw.splitlines()
    in_ft = False
    ft_buffer: list[str] = []

    def flush_ft():
        if ft_buffer:
            _consume_ft_block(ft_buffer, entry)
            ft_buffer.clear()

    for line in lines:
        if line.startswith("ID   "):
            parts = line[5:].split()
            entry.entry_name = parts[0] if parts else ""
            # sequence length is the second-to-last token (e.g. "454 AA.")
            if len(parts) >= 2 and parts[-1] == "AA.":
                try:
                    entry.sequence_length = int(parts[-2])
                except ValueError:
                    pass
        elif line.startswith("AC   ") and not entry.accession:
            acc = line[5:].split(";")[0].strip()
            entry.accession = acc
        elif line.startswith("DT   ") and "entry version" in line:
            entry.uniprot_version = line[5:].strip().rstrip(".")
        elif line.startswith("DE   RecName: Full=") and not entry.protein_name:
            body = line[len("DE   RecName: Full="):]
            entry.protein_name = _strip_evidence(body).rstrip("; ").rstrip(";")
        elif line.startswith("GN   Name=") and not entry.gene_name:
            body = line[len("GN   Name="):]
            entry.gene_name = _strip_evidence(body).split(";")[0].strip()
        elif line.startswith("OS   ") and not entry.organism:
            entry.organism = line[5:].rstrip(".").strip()
        elif line.startswith("OX   NCBI_TaxID="):
            body = line[len("OX   NCBI_TaxID="):]
            entry.taxid = _strip_evidence(body).rstrip("; ").rstrip(";")
        elif line.startswith("FT   "):
            in_ft = True
            ft_buffer.append(line)
        else:
            if in_ft:
                flush_ft()
                in_ft = False
    flush_ft()


def _strip_evidence(text: str) -> str:
    # Drop `{ECO:…}` trailer, preserving the rest.
    return re.sub(r"\s*\{ECO:[^}]+\}", "", text).strip()


def _consume_ft_block(lines: list[str], entry: UniProtEntry) -> None:
    """Group FT lines into feature dicts. A header line has a non-space at
    column 5 (0-indexed); continuation lines have a space there."""
    i = 0
    while i < len(lines):
        line = lines[i]
        if len(line) <= 5 or line[5] == " ":
            i += 1  # orphan continuation; skip
            continue
        header_body = line[5:].strip()
        header_parts = header_body.split(None, 1)
        ft_type = header_parts[0]
        location = header_parts[1].strip() if len(header_parts) > 1 else ""

        # Gather continuation lines until next header or end of block.
        cont_lines = []
        j = i + 1
        while j < len(lines) and len(lines[j]) > 5 and lines[j][5] == " ":
            cont_lines.append(lines[j][5:].strip())
            j += 1

        attrs_text = "\n".join(cont_lines)
        attrs = {k: v for k, v in _ATTR_RE.findall(attrs_text)}

        start, end = _parse_location(location)
        feature = {
            "ft_type": ft_type,
            "location": location,
            "start": start,
            "end": end,
            "note": attrs.get("note", ""),
            "evidence": attrs.get("evidence", ""),
            "ligand": attrs.get("ligand", ""),
            "ligand_id": attrs.get("ligand_id", ""),
            "ligand_note": attrs.get("ligand_note", ""),
            "attrs": attrs,
            "raw_header": line[5:].rstrip(),
        }
        entry.features.append(feature)
        i = j


def _parse_location(loc: str) -> tuple[int | None, int | None]:
    """Return (start, end) integers when we can, else (None, None) for
    complex locations like `1..29` embedded in a compound expression."""
    m = _RANGE_RE.match(loc.strip())
    if not m:
        return (None, None)
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else start
    return (start, end)


# ---------------------------------------------------------------------------
# Feature → YAML mapping
# ---------------------------------------------------------------------------


def route_feature(ft: dict) -> tuple[str, str, str] | None:
    """Return (axis, category, subdir) for a supported FT type; None to skip."""
    t = ft["ft_type"]
    if t in FT_TYPE_MAP:
        axis, category, subdir = FT_TYPE_MAP[t]
        # Re-route BINDING with a metal ligand to STRUCT_METAL_SITE.
        if t == "BINDING":  # unreachable — BINDING routed below
            pass
        return (axis, category, subdir)
    if t == "REGION":
        note_lower = ft["note"].lower()
        if note_lower.startswith("disordered"):
            return ("SEQUENCE", "SEQ_DISORDER", DISORDER_SUBDIR)
        return None  # skip generic REGION — heterogeneous curator free-text
    if t == "BINDING":
        if is_metal_ligand(ft["ligand"]) or is_metal_ligand(ft["ligand_note"]):
            return ("STRUCTURE", "STRUCT_METAL_SITE", "structure/metal_site")
        return ("STRUCTURE", "STRUCT_BINDING_SITE", "structure/binding_site")
    return None


_YAML_UNSAFE = set(':#{}[],&*!|>%@`\\"\'')
_YAML_RESERVED = {"null", "true", "false", "yes", "no", "on", "off", "~"}


def yaml_scalar(text: str) -> str:
    if text is None or text == "":
        return '""'
    if any(c in _YAML_UNSAFE for c in text) or text[0] in "-?" or text.lower() in _YAML_RESERVED:
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def yaml_folded_body(indent: str, text: str) -> list[str]:
    """Single-line >- folded scalar; blank text returns []."""
    text = " ".join((text or "").split())
    if not text:
        return []
    return [f"{indent}  {text}"]


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _range_str(ft: dict) -> str:
    if ft["start"] is not None and ft["end"] is not None:
        return f"{ft['start']}-{ft['end']}" if ft["end"] != ft["start"] else str(ft["start"])
    return _slugify(ft["location"]) or "loc"


def slug_for(entry: UniProtEntry, ft: dict) -> str:
    return f"{entry.accession.lower()}_{ft['ft_type'].lower()}_{_range_str(ft)}"


def identifier_for(entry: UniProtEntry, ft: dict) -> str:
    rng = f"{ft['start']}_{ft['end']}" if ft["start"] is not None else _slugify(ft["location"])
    return f"proteintraitsmech:UNIPROTKB_{entry.accession}_{ft['ft_type']}_{rng}"


def label_for(entry: UniProtEntry, ft: dict) -> str:
    friendly = _FT_TYPE_LABEL.get(ft["ft_type"], ft["ft_type"].lower().replace("_", " "))
    rng = _range_str(ft)
    if ft.get("ligand"):
        friendly = f"{ft['ligand']} {friendly}"
    elif ft.get("note"):
        friendly = f"{friendly} — {ft['note']}"
    protein = entry.protein_name or entry.entry_name
    return f"{friendly} {rng} in {protein} ({entry.accession})"


_FT_TYPE_LABEL = {
    "TRANSMEM":  "transmembrane span",
    "INTRAMEM":  "intramembrane region",
    "COMPBIAS":  "compositional bias",
    "MOTIF":     "motif",
    "DOMAIN":    "domain",
    "ACT_SITE":  "active site",
    "SITE":      "site",
    "METAL":     "metal binding site",
    "DISULFID":  "disulfide bond",
    "SIGNAL":    "signal peptide",
    "PROPEP":    "propeptide",
    "MOD_RES":   "modified residue",
    "LIPID":     "lipid attachment",
    "CARBOHYD":  "glycosylation site",
    "CROSSLNK":  "cross-link",
    "REGION":    "region",
    "BINDING":   "binding site",
    "HELIX":     "alpha helix",
    "STRAND":    "beta strand",
    "TURN":      "turn",
}


def definition_for(entry: UniProtEntry, ft: dict) -> str:
    friendly = _FT_TYPE_LABEL.get(ft["ft_type"], ft["ft_type"])
    parts = [f"{friendly.capitalize()} at residues {_range_str(ft)}"]
    parts.append(f"of UniProtKB:{entry.accession} ({entry.protein_name or entry.entry_name})")
    if entry.organism:
        parts.append(f"from {entry.organism}")
    if ft["note"]:
        parts.append(f"— {ft['note']}")
    if ft["ligand"]:
        lig = ft["ligand"]
        if ft["ligand_id"]:
            lig = f"{lig} ({ft['ligand_id']})"
        parts.append(f"[ligand: {lig}]")
    return " ".join(parts) + "."


def evidence_items(entry: UniProtEntry, ft: dict) -> list[tuple[str, str]]:
    """Return [(reference, notes), …] for the FT line's /evidence tag(s)."""
    items: list[tuple[str, str]] = []
    ev = ft.get("evidence", "")
    if ev:
        for token in ev.split(","):
            token = token.strip()
            # ECO:0000269|PubMed:15196029  →  PMID:15196029
            m = re.search(r"PubMed:(\d+)", token)
            if m:
                items.append((f"PMID:{m.group(1)}", f"UniProt FT evidence: {token}"))
                continue
            m = re.search(r"HAMAP-Rule:(MF_\d+)", token)
            if m:
                items.append((f"HAMAP:{m.group(1)}", f"UniProt FT evidence: {token}"))
                continue
            m = re.search(r"SAM:([A-Za-z0-9_-]+)", token)
            if m:
                items.append((f"UniProtKB:{entry.accession}",
                              f"UniProt FT evidence: {token}"))
                continue
            # ECO:0000305, ECO:0000305|PubMed:xxx already handled above; fallthrough:
            items.append((f"UniProtKB:{entry.accession}",
                          f"UniProt FT evidence: {token}"))
    if not items:
        items.append((f"UniProtKB:{entry.accession}",
                      f"UniProt FT {ft['ft_type']} {ft['location']}"))
    return items


def build_yaml(entry: UniProtEntry, ft: dict, axis: str, category: str, release: str) -> str:
    lines: list[str] = []
    lines.append(f"identifier: {identifier_for(entry, ft)}")
    lines.append(f"label: {yaml_scalar(label_for(entry, ft))}")
    lines.append("definition: >-")
    lines.extend(yaml_folded_body("", definition_for(entry, ft)))
    lines.append(f"definition_source: {yaml_scalar(release)}")
    lines.append(f"trait_axis: {axis}")
    lines.append(f"trait_category: {category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    xrefs = [f"UniProtKB:{entry.accession}"]
    if ft.get("ligand_id"):
        xrefs.append(ft["ligand_id"])
    lines.append("xrefs:")
    for x in xrefs:
        lines.append(f"  - {x}")

    lines.append("canonical_examples:")
    lines.append(f"  - protein_id: UniProtKB:{entry.accession}")
    lines.append(f"    protein_label: {yaml_scalar(entry.protein_name or entry.entry_name)}")
    if entry.taxid:
        lines.append(f"    taxon_id: NCBITaxon:{entry.taxid}")
    if entry.organism:
        lines.append(f"    taxon_label: {yaml_scalar(entry.organism)}")
    ex_note = f"UniProt FT {ft['ft_type']} at {ft['location']}"
    if ft["note"]:
        ex_note += f"; note: {ft['note']}"
    lines.append(f"    note: {yaml_scalar(ex_note)}")

    lines.append("evidence:")
    for ref, note in evidence_items(entry, ft):
        lines.append(f"  - reference: {ref}")
        lines.append(f"    notes: {yaml_scalar(note)}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def fetch_flatfile(accession: str) -> str:
    url = UNIPROT_TXT_URL.format(acc=accession)
    req = urllib.request.Request(url, headers={"User-Agent": "proteintraitsmech-seeder/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def load_input(args) -> str:
    accessions: list[str] = list(args.accession or [])
    if args.from_file:
        for line in Path(args.from_file).read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                accessions.append(line)

    chunks: list[str] = []
    if args.input:
        chunks.append(Path(args.input).read_text())
    for acc in accessions:
        print(f"  fetching {acc} …", file=sys.stderr)
        try:
            chunks.append(fetch_flatfile(acc))
        except urllib.error.HTTPError as exc:
            print(f"  WARN: {acc}: HTTP {exc.code}", file=sys.stderr)
    return "\n".join(chunks)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--accession", action="append", help="UniProt accession (repeat)")
    parser.add_argument("--from-file", help="file with one accession per line")
    parser.add_argument("--input", help="pre-downloaded UniProt flat file (may hold many entries)")
    parser.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args()

    if not (args.accession or args.from_file or args.input):
        parser.error("provide --accession, --from-file, or --input")

    text = load_input(args)
    entries = parse_flatfile(text)
    print(f"Parsed {len(entries)} UniProt entries.")

    stats = {"written": 0, "skipped": 0, "planned": 0, "unsupported": {}, "by_dir": {}}

    for entry in entries:
        if not entry.accession:
            continue
        release = f"UniProtKB entry {entry.accession} ({entry.uniprot_version or 'unversioned'})"
        for ft in entry.features:
            routed = route_feature(ft)
            if routed is None:
                stats["unsupported"][ft["ft_type"]] = (
                    stats["unsupported"].get(ft["ft_type"], 0) + 1
                )
                continue
            axis, category, subdir = routed
            if ft["start"] is None:
                stats["unsupported"][f"{ft['ft_type']} (unparsable location)"] = (
                    stats["unsupported"].get(f"{ft['ft_type']} (unparsable location)", 0) + 1
                )
                continue
            path = TRAITS_DIR / subdir / f"{slug_for(entry, ft)}.yaml"
            key = str(path.parent.relative_to(TRAITS_DIR))
            stats["by_dir"][key] = stats["by_dir"].get(key, 0) + 1
            if path.exists() and not args.force:
                stats["skipped"] += 1
                continue
            stats["planned"] += 1
            if args.apply:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(build_yaml(entry, ft, axis, category, release))
                stats["written"] += 1

    print()
    print("Per-directory totals (all supported, not just new):")
    for d, n in sorted(stats["by_dir"].items()):
        print(f"  data/traits/{d:34s} {n}")
    if stats["unsupported"]:
        print()
        print("Skipped FT types (not in current mapping):")
        for t, n in sorted(stats["unsupported"].items(), key=lambda kv: -kv[1]):
            print(f"  {t:36s} {n}")
    print()
    if args.apply:
        print(f"Wrote {stats['written']} file(s); skipped {stats['skipped']} existing.")
    else:
        print(
            f"Dry-run — would write {stats['planned']} file(s); "
            f"{stats['skipped']} already exist."
        )
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
