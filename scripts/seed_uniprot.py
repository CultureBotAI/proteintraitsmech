#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from UniProtKB flat-file `FT` lines.

NOTE (2026-07): records emitted here are **per-protein annotations**, which is
instance-level, not the trait-*class* model the rest of the corpus follows. The
original B0R5N7 / P25888 demo records were retired for this reason. The
canonical way to connect real proteins to the KB is `fetch_uniprot_examples.py`,
which attaches a UniProt entry as a `canonical_example` on the relevant
class-level trait. This seeder is kept as a demonstration of the FT-type →
trait-category demultiplexing (see the README table); if re-run, family/domain
signatures go in `xrefs` (associative), never `parent_traits`.


Each supported FT feature (DOMAIN, MOTIF, COMPBIAS, BINDING, ACT_SITE,
SITE, DISULFID, METAL, MOD_RES, LIPID, CARBOHYD, CROSSLNK, SIGNAL,
PROPEP, HELIX, STRAND, TURN, and REGION when /note="Disordered")
becomes one ProteinTraitRecord.

Membrane-span features (TRANSMEM, INTRAMEM) are deliberately NOT seeded:
a per-protein membrane span is too specific — it is covered by the more
general transmembrane trait — so demultiplexing every entry's TM helices
into standalone records just adds redundant, protein-bound noise.

Emitted layout mirrors the existing seeds:

  data/traits/sequence/composition/            COMPBIAS
  data/traits/sequence/disorder/               REGION /note=Disordered
  data/traits/sequence/motif/                  MOTIF (UniProt curator-defined; PROSITE lives elsewhere)
  data/traits/sequence/modified_residue/       MOD_RES
  data/traits/sequence/glycosylation/          CARBOHYD
  data/traits/sequence/lipidation/             LIPID
  data/traits/sequence/crosslink/              CROSSLNK
  data/traits/sequence/signal_peptide/         SIGNAL
  data/traits/sequence/transit_peptide/        TRANSIT
  data/traits/sequence/propeptide/             PROPEP
  data/traits/sequence/initiator_methionine/   INIT_MET
  data/traits/sequence/mature_chain/           CHAIN + PEPTIDE
  data/traits/sequence/nonstandard_residue/    NON_STD
  data/traits/structure/active_site/           ACT_SITE
  data/traits/structure/binding_site/          BINDING (non-metal ligand) + SITE
  data/traits/structure/metal_site/            BINDING (metal ligand) + METAL
  data/traits/structure/disulfide/             DISULFID
  data/traits/structure/domain/                DOMAIN
  data/traits/structure/secondary/             HELIX + STRAND + TURN

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
    # NOTE: TRANSMEM / INTRAMEM are intentionally absent — per-protein
    # membrane spans are redundant with the general transmembrane trait,
    # so they fall through to "unsupported" and are skipped.
    "COMPBIAS":  ("SEQUENCE",           "SEQ_COMPOSITION",           "sequence/composition"),
    "MOTIF":     ("SEQUENCE",           "SEQ_MOTIF",                 "sequence/motif"),
    "DOMAIN":    ("STRUCTURE",          "STRUCT_DOMAIN",             "structure/domain"),
    "ACT_SITE":  ("STRUCTURE",          "STRUCT_ACTIVE_SITE",        "structure/active_site"),
    "SITE":      ("STRUCTURE",          "STRUCT_BINDING_SITE",       "structure/binding_site"),
    "METAL":     ("STRUCTURE",          "STRUCT_METAL_SITE",         "structure/metal_site"),
    "DISULFID":  ("STRUCTURE",          "STRUCT_DISULFIDE",          "structure/disulfide"),
    "SIGNAL":    ("SEQUENCE",           "SEQ_SIGNAL_PEPTIDE",        "sequence/signal_peptide"),
    "TRANSIT":   ("SEQUENCE",           "SEQ_TRANSIT_PEPTIDE",       "sequence/transit_peptide"),
    "PROPEP":    ("SEQUENCE",           "SEQ_PROPEPTIDE",            "sequence/propeptide"),
    "INIT_MET":  ("SEQUENCE",           "SEQ_INITIATOR_METHIONINE",  "sequence/initiator_methionine"),
    "CHAIN":     ("SEQUENCE",           "SEQ_MATURE_CHAIN",          "sequence/mature_chain"),
    "PEPTIDE":   ("SEQUENCE",           "SEQ_MATURE_CHAIN",          "sequence/mature_chain"),
    "NON_STD":   ("SEQUENCE",           "SEQ_NONSTANDARD_RESIDUE",   "sequence/nonstandard_residue"),
    # PTM subtypes — split from the legacy generic SEQ_PTM_SITE bucket.
    "MOD_RES":   ("SEQUENCE",           "SEQ_MODIFIED_RESIDUE",      "sequence/modified_residue"),
    "LIPID":     ("SEQUENCE",           "SEQ_LIPIDATION_SITE",       "sequence/lipidation"),
    "CARBOHYD":  ("SEQUENCE",           "SEQ_GLYCOSYLATION_SITE",    "sequence/glycosylation"),
    "CROSSLNK":  ("SEQUENCE",           "SEQ_CROSSLINK_SITE",        "sequence/crosslink"),
    "HELIX":     ("STRUCTURE",          "STRUCT_SECONDARY",          "structure/secondary"),
    "STRAND":    ("STRUCTURE",          "STRUCT_SECONDARY",          "structure/secondary"),
    "TURN":      ("STRUCTURE",          "STRUCT_SECONDARY",          "structure/secondary"),
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
        self.sequence: str = ""  # amino-acid residues from the SQ block
        self.cc_blocks: dict[str, list[str]] = {}
        self.go_annotations: list[dict] = []
        self.keywords: list[str] = []
        # CURIEs derived from DR lines — used to populate `parent_traits`
        # on every record emitted for this entry.
        self.family_curies: list[str] = []


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
    in_sq = False
    ft_buffer: list[str] = []
    cc_lines: list[str] = []
    kw_lines: list[str] = []
    sq_chunks: list[str] = []

    def flush_ft():
        if ft_buffer:
            _consume_ft_block(ft_buffer, entry)
            ft_buffer.clear()

    for line in lines:
        # SQ block: `SQ   SEQUENCE  ...` header followed by 5-space-indented
        # rows of residues. Runs to the end of the entry.
        if in_sq:
            if line.startswith("     ") or line.startswith("SQ   "):
                sq_chunks.append(line)
                continue
            # any non-continuation line ends the SQ block
            in_sq = False

        if line.startswith("ID   "):
            parts = line[5:].split()
            entry.entry_name = parts[0] if parts else ""
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
        elif line.startswith("CC   "):
            cc_lines.append(line[5:])
        elif line.startswith("KW   "):
            kw_lines.append(line[5:])
        elif line.startswith("DR   GO;"):
            _parse_go_dr(line, entry)
        elif line.startswith("DR   "):
            _parse_family_dr(line, entry)
        elif line.startswith("SQ   "):
            in_sq = True
            sq_chunks.append(line)
        elif line.startswith("FT   "):
            in_ft = True
            ft_buffer.append(line)
        else:
            if in_ft:
                flush_ft()
                in_ft = False
    flush_ft()
    entry.cc_blocks = _parse_cc_blocks(cc_lines)
    entry.keywords = _parse_keywords(kw_lines)
    entry.sequence = _parse_sq_block(sq_chunks)
    # De-duplicate DR-derived family CURIEs while preserving first-seen order.
    entry.family_curies = list(dict.fromkeys(entry.family_curies))


def _parse_cc_blocks(cc_lines: list[str]) -> dict[str, list[str]]:
    """Join CC lines (with the `CC   ` prefix already stripped) and split
    them into `-!- KEY: body` blocks."""
    joined = "\n".join(cc_lines)
    blocks: dict[str, list[str]] = {}
    for chunk in joined.split("-!- "):
        chunk = chunk.strip()
        if not chunk or ":" not in chunk:
            continue
        key, _, body = chunk.partition(":")
        key = key.strip()
        # Stop at the license / copyright separator UniProt inserts at end.
        body = body.split("---------")[0].strip()
        # Strip evidence tag trailers at the end of any block.
        body = body.rstrip(".").rstrip()
        if key:
            blocks.setdefault(key, []).append(body)
    return blocks


def _parse_keywords(kw_lines: list[str]) -> list[str]:
    joined = " ".join(kw_lines)
    joined = joined.replace(".", ";")
    out = []
    for kw in joined.split(";"):
        kw = kw.strip()
        if kw:
            out.append(kw)
    return out


def _parse_go_dr(line: str, entry: UniProtEntry) -> None:
    """Parse `DR   GO; GO:0009408; P:response to heat; IMP:EcoCyc.`"""
    body = line[len("DR   GO; "):].rstrip(".").strip()
    parts = [p.strip() for p in body.split(";")]
    if len(parts) < 2:
        return
    go_id = parts[0]
    aspect_label = parts[1]
    if ":" in aspect_label:
        aspect, _, label = aspect_label.partition(":")
    else:
        aspect, label = "?", aspect_label
    evidence_source = parts[2] if len(parts) >= 3 else ""
    entry.go_annotations.append({
        "go_id": go_id,
        "aspect": aspect.strip(),
        "label": label.strip(),
        "evidence_source": evidence_source.strip(),
    })


def _strip_evidence(text: str) -> str:
    # Drop `{ECO:…}` trailer, preserving the rest.
    return re.sub(r"\s*\{ECO:[^}]+\}", "", text).strip()


def _normalise_curie(curie: str) -> str:
    """UniProt occasionally writes db-prefixed CURIEs whose accession
    itself carries the DB prefix (`ChEBI:CHEBI:30616`). The schema's
    xref pattern only accepts a single `prefix:local` colon, so collapse
    the redundant prefix. Currently only ChEBI is known to be affected."""
    if curie.startswith("ChEBI:CHEBI:"):
        return "CHEBI:" + curie[len("ChEBI:CHEBI:"):]
    return curie


# DR databases that map cleanly to a CURIE prefix declared in the schema.
# Each entry: UniProt DR key → CURIE prefix. The first `;`-delimited field
# after the key is treated as the accession.
_FAMILY_DR_PREFIXES: dict[str, str] = {
    "PROSITE":  "PROSITE",
    "Pfam":     "Pfam",
    "InterPro": "InterPro",
    "SMART":    "SMART",
    "CATH":     "CATH",
    "MEROPS":   "MEROPS",
    "HAMAP":    "HAMAP",
}


def _parse_family_dr(line: str, entry: UniProtEntry) -> None:
    """Parse a `DR   <DB>; <acc>; …` line into a CURIE and stash on the
    entry. Only whitelisted family/domain databases (see
    _FAMILY_DR_PREFIXES) contribute — DR lines to sequence databases
    (EMBL, RefSeq, PDB, …) are ignored here."""
    body = line[len("DR   "):].rstrip().rstrip(".")
    if ";" not in body:
        return
    db, _, rest = body.partition(";")
    db = db.strip()
    prefix = _FAMILY_DR_PREFIXES.get(db)
    if prefix is None:
        return
    acc = rest.strip().split(";")[0].strip()
    if not acc or acc == "-":
        return
    entry.family_curies.append(f"{prefix}:{acc}")


def _parse_sq_block(sq_lines: list[str]) -> str:
    """Concatenate the residue rows of an `SQ ...` block into a single
    uppercase amino-acid string. The header line (`SQ   SEQUENCE ...`)
    is discarded; every subsequent 5-space-indented row contributes its
    non-whitespace characters."""
    residues: list[str] = []
    for line in sq_lines:
        if line.startswith("SQ   "):
            continue
        residues.append("".join(line.split()))
    seq = "".join(residues).upper()
    # Strip any non-letter residue codes defensively; UniProt uses IUPAC
    # single letters + `*` for stop codons in translated CDS entries.
    return re.sub(r"[^A-Z*]", "", seq)


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


def _residue_substring(entry: UniProtEntry, ft: dict) -> str:
    """Return the amino-acid substring covered by a feature, or empty
    string if unavailable (missing sequence, unparsable range, or
    bond-encoding FT types like DISULFID and CROSSLNK, whose two
    coordinates identify the linked residues rather than a span)."""
    if not entry.sequence:
        return ""
    if ft["ft_type"] in {"DISULFID", "CROSSLNK"}:
        # These FT types encode a bond between two residues; the two
        # coordinates are the endpoints, not the range of a contiguous
        # region. Extracting the intervening residues would misrepresent
        # the trait.
        return ""
    start, end = ft.get("start"), ft.get("end")
    if start is None or end is None:
        return ""
    if start < 1 or end > len(entry.sequence) or start > end:
        return ""
    return entry.sequence[start - 1 : end]


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
        # UniProt FT `/ligand_id` uses `ChEBI:CHEBI:NNNN` form; normalise
        # to the schema's declared `CHEBI:NNNN` CURIE.
        xrefs.append(_normalise_curie(ft["ligand_id"]))
    # The entry's family/domain signatures (Pfam/InterPro/HAMAP/…) are the
    # PROTEIN's memberships — associative cross-references, NOT broader classes
    # of this specific feature-trait, so they go in xrefs, never parent_traits
    # (see review-source-categories FAMILY_AS_PARENT).
    xrefs.extend(entry.family_curies)
    lines.append("xrefs:")
    for x in xrefs:
        lines.append(f"  - {x}")

    residues = _residue_substring(entry, ft)
    if residues:
        lines.append(f"residue_sequence: {residues}")

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
# FUNCTION-axis parsing + emission
# ---------------------------------------------------------------------------

FUNC_SUBDIRS = {
    "FUNC_ENZYMATIC_ACTIVITY":     "function/enzymatic",
    "FUNC_BINDING_CAPACITY":       "function/binding",
    "FUNC_COFACTOR_REQUIREMENT":   "function/cofactor",
    "FUNC_LOCALIZATION":           "function/localization",
    "FUNC_ENVIRONMENTAL_RESPONSE": "function/environmental",
    "FUNC_INTERACTION_PARTNER":    "function/interaction",
}

# Environmental cue keywords surfaced in CC INDUCTION and GO BP `response to *`
# terms. Values are kebab slugs used in identifiers/paths.
ENV_KEYWORDS: list[tuple[str, str]] = [
    ("cold shock",        "cold-shock"),
    ("cold",              "cold"),
    ("heat shock",        "heat-shock"),
    ("response to heat",  "heat"),
    ("heat",              "heat"),
    ("oxidative stress",  "oxidative-stress"),
    ("hypoxia",           "hypoxia"),
    ("anaerobic",         "anaerobic"),
    ("aerobic",           "aerobic"),
    ("acid stress",       "acid-stress"),
    ("alkaline",          "alkaline"),
    ("osmotic",           "osmotic-stress"),
    ("salt stress",       "salt-stress"),
    ("starvation",        "starvation"),
    ("uv",                "uv"),
    ("dna damage",        "dna-damage"),
    ("cold",              "cold"),
]

# GO F: term suffixes → category
_GO_MF_ACTIVITY_SUFFIX = re.compile(r"\bactivity\b", re.IGNORECASE)
_GO_MF_BINDING_SUFFIX = re.compile(r"\bbinding\b", re.IGNORECASE)

_INTERACTS_RE = re.compile(
    r"[Ii]nteracts?\s+(?:in\s+vitro\s+)?with\s+([A-Za-z0-9][A-Za-z0-9/\- ]{0,30})",
)
_PUBMED_RE = re.compile(r"PubMed:(\d+)")
_CHEBI_RE = re.compile(r"ChEBI:CHEBI:(\d+)")
_RHEA_RE = re.compile(r"Rhea:RHEA:(\d+)")
_EC_RE = re.compile(r"EC=([\d.]+)")


def _pmids_in(text: str) -> list[str]:
    return list(dict.fromkeys(_PUBMED_RE.findall(text)))


def _slugify_partner(name: str) -> str:
    name = name.strip().rstrip(".").rstrip(",")
    # Trim trailing noise like "in the presence of" — cheap heuristic
    for stop in (" and ", " through ", " during ", " via ", " to form "):
        if stop in name:
            name = name.split(stop)[0]
    return re.sub(r"[^A-Za-z0-9]+", "-", name.strip().lower()).strip("-")[:40] or "partner"


def parse_catalytic_activity(block: str) -> list[dict]:
    out: list[dict] = []
    # Each Reaction=... clause is a separate activity.
    chunks = re.split(r"(?=Reaction=)", block)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk.startswith("Reaction="):
            continue
        reaction = chunk[len("Reaction="):].split(";", 1)[0].strip()
        out.append({
            "reaction": reaction,
            "rhea": (_RHEA_RE.search(chunk).group(1) if _RHEA_RE.search(chunk) else None),
            "ec": (_EC_RE.search(chunk).group(1) if _EC_RE.search(chunk) else None),
            "chebis": list(dict.fromkeys(_CHEBI_RE.findall(chunk))),
            "pmids": _pmids_in(chunk),
        })
    return out


def parse_cofactor(block: str) -> list[dict]:
    out: list[dict] = []
    for chunk in re.split(r"(?=Name=)", block):
        chunk = chunk.strip()
        if not chunk.startswith("Name="):
            continue
        name_m = re.match(r"Name=([^;]+)", chunk)
        chebi_m = _CHEBI_RE.search(chunk)
        out.append({
            "name": (_strip_evidence(name_m.group(1)) if name_m else "").strip(),
            "chebi": chebi_m.group(1) if chebi_m else None,
            "pmids": _pmids_in(chunk),
        })
    return out


def parse_subcellular_location(block: str) -> list[dict]:
    """Return locations from a CC SUBCELLULAR LOCATION block.

    UniProt syntax: primary compartments separated by `.`; `; qualifier`
    tacks a topology descriptor onto the previous location; `Note=` is
    a free-text tail we surface as a note.
    """
    if "Note=" in block:
        main, _, note_body = block.partition("Note=")
    else:
        main, note_body = block, ""
    note = _strip_evidence(note_body).strip().rstrip(".")

    main = _strip_evidence(main)
    out: list[dict] = []
    for seg in main.split("."):
        seg = seg.strip()
        if not seg:
            continue
        parts = [p.strip() for p in seg.split(";") if p.strip()]
        if not parts:
            continue
        location = parts[0]
        qualifiers = "; ".join(parts[1:]) if len(parts) > 1 else ""
        out.append({
            "location": location,
            "qualifiers": qualifiers,
            "note": note if not out else "",
            "pmids": _pmids_in(block),
        })
    return out


def parse_induction(block: str) -> list[dict]:
    """Keyword-scan an INDUCTION block for environmental cues.

    Longest keyword wins on overlap — matching "cold shock" suppresses a
    later match on plain "cold" over the same character range.
    """
    lower = block.lower()
    hits: list[dict] = []
    seen_slugs: set[str] = set()
    covered: list[tuple[int, int]] = []
    kw_sorted = sorted(ENV_KEYWORDS, key=lambda kv: -len(kv[0]))
    for kw, slug in kw_sorted:
        idx = lower.find(kw)
        while idx != -1:
            hi = idx + len(kw)
            if any(idx < c_hi and hi > c_lo for (c_lo, c_hi) in covered):
                idx = lower.find(kw, hi)
                continue
            if slug not in seen_slugs:
                seen_slugs.add(slug)
                hits.append({
                    "cue": kw,
                    "slug": slug,
                    "pmids": _pmids_in(block),
                    "context": _strip_evidence(block).strip(),
                })
            covered.append((idx, hi))
            idx = lower.find(kw, hi)
    return hits


def parse_subunit(block: str) -> list[dict]:
    """Extract 'Interacts with X' clauses from a SUBUNIT block."""
    out: list[dict] = []
    seen: set[str] = set()
    for m in _INTERACTS_RE.finditer(block):
        partner_raw = m.group(1).strip().rstrip(".").rstrip(",")
        # Trim at conjunctions the regex was greedy enough to swallow.
        for stop in (" and ", " via ", " through ", " during "):
            if stop in partner_raw:
                partner_raw = partner_raw.split(stop)[0]
        partner = partner_raw.strip()
        if not partner or partner.lower() in seen:
            continue
        seen.add(partner.lower())
        # Grab the containing sentence for context + PMIDs
        start = max(0, m.start() - 40)
        end = min(len(block), m.end() + 120)
        context = _strip_evidence(block[start:end]).strip()
        out.append({
            "partner": partner,
            "context": context,
            "pmids": _pmids_in(context) or _pmids_in(block),
        })
    return out


def function_records(entry: UniProtEntry) -> list[dict]:
    """Return a list of function-record dicts ready to emit as YAMLs."""
    records: list[dict] = []

    for block in entry.cc_blocks.get("CATALYTIC ACTIVITY", []):
        for rx in parse_catalytic_activity(block):
            records.append(_enzymatic_from_reaction(entry, rx))
    for block in entry.cc_blocks.get("COFACTOR", []):
        for cf in parse_cofactor(block):
            records.append(_cofactor_record(entry, cf))
    for block in entry.cc_blocks.get("SUBCELLULAR LOCATION", []):
        for loc in parse_subcellular_location(block):
            records.append(_localization_record(entry, loc))
    for block in entry.cc_blocks.get("INDUCTION", []):
        for env in parse_induction(block):
            records.append(_environmental_record(entry, env, source="INDUCTION"))
    for block in entry.cc_blocks.get("SUBUNIT", []):
        for partner in parse_subunit(block):
            records.append(_interaction_record(entry, partner))

    # GO cross-refs — one record per relevant GO term.
    for go in entry.go_annotations:
        rec = _record_from_go(entry, go)
        if rec is not None:
            records.append(rec)

    return records


def _base_metadata(entry: UniProtEntry, category: str, key: str, label: str, definition: str,
                   xrefs: list[str], pmids: list[str], sources: list[str]) -> dict:
    """Bundle every field the YAML emitter needs."""
    axis = "FUNCTION"
    subdir = FUNC_SUBDIRS[category]
    identifier = f"proteintraitsmech:UNIPROTKB_{entry.accession}_{key}"
    slug = f"{entry.accession.lower()}_{re.sub(r'[^a-z0-9]+', '_', key.lower()).strip('_')}"
    return {
        "axis": axis,
        "category": category,
        "subdir": subdir,
        "identifier": identifier,
        "slug": slug,
        "label": label,
        "definition": definition,
        "xrefs": xrefs,
        "pmids": pmids,
        "sources": sources,
    }


def _enzymatic_from_reaction(entry: UniProtEntry, rx: dict) -> dict:
    key_bits = []
    if rx["rhea"]:
        key_bits.append(f"RHEA_{rx['rhea']}")
    elif rx["ec"]:
        key_bits.append("EC_" + rx["ec"].replace(".", "_"))
    else:
        key_bits.append("REACTION_" + re.sub(r"[^A-Za-z0-9]+", "_", rx["reaction"])[:30].strip("_"))
    key = f"ACTIVITY_{key_bits[0]}"
    label = f"Enzymatic activity — {rx['reaction']}"
    if rx["ec"]:
        label += f" (EC {rx['ec']})"
    label += f" [{entry.accession}]"
    definition = (
        f"Catalytic activity of UniProtKB:{entry.accession} "
        f"({entry.protein_name or entry.entry_name}): {rx['reaction']}."
    )
    if rx["ec"]:
        definition += f" EC {rx['ec']}."
    if rx["rhea"]:
        definition += f" Rhea:{rx['rhea']}."
    xrefs = [f"UniProtKB:{entry.accession}"]
    if rx["rhea"]:
        xrefs.append(f"RHEA:{rx['rhea']}")
    if rx["ec"]:
        xrefs.append(f"EC:{rx['ec']}")
    for chebi in rx["chebis"]:
        xrefs.append(f"CHEBI:{chebi}")
    return _base_metadata(entry, "FUNC_ENZYMATIC_ACTIVITY", key, label, definition,
                          xrefs, rx["pmids"], ["CC CATALYTIC ACTIVITY"])


def _cofactor_record(entry: UniProtEntry, cf: dict) -> dict:
    key_slug = cf["chebi"] or re.sub(r"[^A-Za-z0-9]+", "_", cf["name"])[:20]
    key = f"COFACTOR_{key_slug}"
    label = f"Cofactor requirement — {cf['name']} [{entry.accession}]"
    definition = (
        f"UniProtKB:{entry.accession} requires {cf['name']} as a cofactor."
    )
    xrefs = [f"UniProtKB:{entry.accession}"]
    if cf["chebi"]:
        xrefs.append(f"CHEBI:{cf['chebi']}")
    return _base_metadata(entry, "FUNC_COFACTOR_REQUIREMENT", key, label, definition,
                          xrefs, cf["pmids"], ["CC COFACTOR"])


def _localization_record(entry: UniProtEntry, loc: dict) -> dict:
    loc_slug = re.sub(r"[^A-Za-z0-9]+", "_", loc["location"]).strip("_").upper()
    key = f"LOCALIZATION_{loc_slug}"
    label = f"Localised to {loc['location']} [{entry.accession}]"
    definition = (
        f"UniProtKB:{entry.accession} ({entry.protein_name or entry.entry_name}) "
        f"is localised to {loc['location']}"
    )
    if loc["qualifiers"]:
        definition += f" ({loc['qualifiers']})"
    definition += "."
    if loc["note"]:
        definition += f" Note: {loc['note']}."
    xrefs = [f"UniProtKB:{entry.accession}"]
    return _base_metadata(entry, "FUNC_LOCALIZATION", key, label, definition,
                          xrefs, loc["pmids"], ["CC SUBCELLULAR LOCATION"])


def _environmental_record(entry: UniProtEntry, env: dict, source: str) -> dict:
    key = f"ENV_{env['slug'].replace('-', '_').upper()}"
    label = f"Response to {env['cue']} [{entry.accession}]"
    definition = (
        f"UniProtKB:{entry.accession} shows a response to {env['cue']}. "
        f"Source: {source}. Context: \"{env['context'][:200]}\"."
    )
    xrefs = [f"UniProtKB:{entry.accession}"]
    return _base_metadata(entry, "FUNC_ENVIRONMENTAL_RESPONSE", key, label, definition,
                          xrefs, env["pmids"], [f"CC {source}"])


def _interaction_record(entry: UniProtEntry, partner: dict) -> dict:
    key = f"INTERACTS_{_slugify_partner(partner['partner']).upper()}"
    label = f"Interacts with {partner['partner']} [{entry.accession}]"
    definition = (
        f"UniProtKB:{entry.accession} ({entry.protein_name or entry.entry_name}) "
        f"interacts with {partner['partner']}. Context: \"{partner['context'][:200]}\"."
    )
    xrefs = [f"UniProtKB:{entry.accession}"]
    return _base_metadata(entry, "FUNC_INTERACTION_PARTNER", key, label, definition,
                          xrefs, partner["pmids"], ["CC SUBUNIT"])


def _record_from_go(entry: UniProtEntry, go: dict) -> dict | None:
    """Map a DR GO annotation to a FUNC_* record, or None to skip."""
    go_id = go["go_id"]
    label_text = go["label"]
    aspect = go["aspect"]

    if aspect == "F":
        if _GO_MF_BINDING_SUFFIX.search(label_text):
            key = f"BINDING_GO_{go_id.split(':', 1)[1]}"
            label = f"{label_text} ({go_id}) [{entry.accession}]"
            definition = (
                f"UniProtKB:{entry.accession} exhibits {label_text} "
                f"({go_id}, aspect F)."
            )
            xrefs = [f"UniProtKB:{entry.accession}", go_id]
            return _base_metadata(entry, "FUNC_BINDING_CAPACITY", key, label,
                                  definition, xrefs, [], [f"DR GO {go['evidence_source']}"])
        if _GO_MF_ACTIVITY_SUFFIX.search(label_text):
            key = f"ACTIVITY_GO_{go_id.split(':', 1)[1]}"
            label = f"{label_text} ({go_id}) [{entry.accession}]"
            definition = (
                f"UniProtKB:{entry.accession} exhibits {label_text} "
                f"({go_id}, aspect F)."
            )
            xrefs = [f"UniProtKB:{entry.accession}", go_id]
            return _base_metadata(entry, "FUNC_ENZYMATIC_ACTIVITY", key, label,
                                  definition, xrefs, [], [f"DR GO {go['evidence_source']}"])
    elif aspect == "C":
        key = f"LOCALIZATION_GO_{go_id.split(':', 1)[1]}"
        label = f"Localised to {label_text} ({go_id}) [{entry.accession}]"
        definition = (
            f"UniProtKB:{entry.accession} is localised to {label_text} "
            f"({go_id}, aspect C)."
        )
        xrefs = [f"UniProtKB:{entry.accession}", go_id]
        return _base_metadata(entry, "FUNC_LOCALIZATION", key, label,
                              definition, xrefs, [], [f"DR GO {go['evidence_source']}"])
    elif aspect == "P":
        # BP records — only surface as ENVIRONMENTAL_RESPONSE when the GO term
        # is a `response to *` term (matches the user's environmental-trait scope).
        if label_text.lower().startswith("response to "):
            cue = label_text[len("response to "):].strip().rstrip(".")
            slug = re.sub(r"[^A-Za-z0-9]+", "-", cue.lower()).strip("-") or "unknown"
            key = f"ENV_{slug.replace('-', '_').upper()}_GO_{go_id.split(':', 1)[1]}"
            label = f"Response to {cue} ({go_id}) [{entry.accession}]"
            definition = (
                f"UniProtKB:{entry.accession} shows a response to {cue} "
                f"({go_id}, aspect P)."
            )
            xrefs = [f"UniProtKB:{entry.accession}", go_id]
            return _base_metadata(entry, "FUNC_ENVIRONMENTAL_RESPONSE", key, label,
                                  definition, xrefs, [], [f"DR GO {go['evidence_source']}"])
    return None


def build_function_yaml(entry: UniProtEntry, rec: dict, release: str) -> str:
    lines: list[str] = []
    lines.append(f"identifier: {rec['identifier']}")
    lines.append(f"label: {yaml_scalar(rec['label'])}")
    lines.append("definition: >-")
    lines.extend(yaml_folded_body("", rec["definition"]))
    lines.append(f"definition_source: {yaml_scalar(release)}")
    lines.append(f"trait_axis: {rec['axis']}")
    lines.append(f"trait_category: {rec['category']}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    # The entry's family/domain signatures (Pfam/InterPro/HAMAP/…) are the
    # PROTEIN's memberships — associative cross-references, NOT broader classes
    # of this specific feature-trait, so they join xrefs, never parent_traits
    # (see review-source-categories FAMILY_AS_PARENT).
    lines.append("xrefs:")
    for x in dict.fromkeys(list(rec["xrefs"]) + entry.family_curies):
        lines.append(f"  - {x}")

    lines.append("canonical_examples:")
    lines.append(f"  - protein_id: UniProtKB:{entry.accession}")
    lines.append(f"    protein_label: {yaml_scalar(entry.protein_name or entry.entry_name)}")
    if entry.taxid:
        lines.append(f"    taxon_id: NCBITaxon:{entry.taxid}")
    if entry.organism:
        lines.append(f"    taxon_label: {yaml_scalar(entry.organism)}")
    lines.append(f"    note: {yaml_scalar('Source: ' + ', '.join(rec['sources']))}")

    lines.append("evidence:")
    if rec["pmids"]:
        for pmid in dict.fromkeys(rec["pmids"]):
            lines.append(f"  - reference: PMID:{pmid}")
            lines.append(f"    notes: {yaml_scalar('Cited in: ' + ', '.join(rec['sources']))}")
    else:
        lines.append(f"  - reference: UniProtKB:{entry.accession}")
        lines.append(f"    notes: {yaml_scalar('Source: ' + ', '.join(rec['sources']))}")

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
        # 1. Per-region FT records
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

        # 2. Function-axis records from CC / DR GO
        for rec in function_records(entry):
            path = TRAITS_DIR / rec["subdir"] / f"{rec['slug']}.yaml"
            key = str(path.parent.relative_to(TRAITS_DIR))
            stats["by_dir"][key] = stats["by_dir"].get(key, 0) + 1
            if path.exists() and not args.force:
                stats["skipped"] += 1
                continue
            stats["planned"] += 1
            if args.apply:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(build_function_yaml(entry, rec, release))
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
