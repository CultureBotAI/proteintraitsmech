#!/usr/bin/env python3
"""Seed protein metal-site trait CLASSES from MetalPDB → STRUCTURE /
STRUCT_METAL_SITE.

Source: MetalPDB (CERM, University of Florence) — bulk `flat_db_file.xml.gz`
        https://metalpdb.cerm.unifi.it/download?t=flatdb&id=flat_db_file.xml.gz
        (fetch via `just fetch-metalpdb`; gitignored under data/raw/metalpdb/).

MODELLING — instances → classes
-------------------------------
Each MetalPDB `<site>` element is a *per-PDB metal site* — a concrete
INSTANCE (e.g. site `101m_1`, the heme iron of sperm-whale myoglobin in
PDB 101m). This knowledge base catalogues reusable trait CLASSES, not
instances, so this seeder AGGREGATES the ~160 k sites into one
ProteinTraitRecord per **(metal element, nuclearity)** pair — the two
axes MetalPDB itself organises sites by. That yields classes such as
"mononuclear zinc site", "dinuclear iron site" or "tetranuclear iron
site" (~240 populated combinations over 56 metals × 11 nuclearity
levels).

The class key is intentionally (metal, nuclearity) — the level the flat
file gives cleanly and unambiguously. Finer coordinating-residue
signatures (MetalPDB's `ligands_pattern`, e.g. `H`, `CCCC`,
`HX(1)HX(22)H`) are *summarised inside each class* (top signatures +
counts folded into the definition) rather than exploded into a separate
class per pattern, which would produce thousands of thinly-populated
records. A future finer tier keyed on (metal, nuclearity, dominant
ligands_pattern) is possible but deliberately deferred.

Per class the seeder records, from the aggregated instances:
  * counts (distinct sites / PDB structures / UniProt proteins) — in the
    definition text (the schema has no dedicated count slot);
  * the top endogenous coordination signatures + typical geometry — in
    the definition;
  * the metal ion as a `chemical_participants` entry (role COFACTOR),
    grounded to its oxidation-state-agnostic ChEBI *atom* term
    (e.g. zinc → CHEBI:27363), verified against ChEBI/OLS4;
  * a capped handful of exemplar proteins in `canonical_examples`
    (distinct UniProtKB accessions drawn from the member sites, with the
    representative PDB noted).
Every class is parented to the generic `proteintraitsmech:METAL_BINDING_SITE`.

LICENSE
-------
MetalPDB (CERM, Univ. Florence) publishes NO explicit reuse licence. Every
record is stamped with the flag string below (mirroring how CAZy is flagged
in this repo) rather than the corpus CC0 default. CONFIRM reuse terms with
CERM before any redistribution of MetalPDB-derived content.

Inputs (fetch via `just fetch-metalpdb`, gitignored):
  data/raw/metalpdb/flat_db_file.xml.gz

Output:
  data/traits/structure/metal_site/metalpdb/<slug>.yaml

Idempotent (skips existing files unless --force); dry-run unless --apply.
Stdlib-only: the flat file contains unescaped `&` in some molecule names,
so a streaming sanitiser escapes stray ampersands before feeding the bytes
to xml.etree's pull parser (no lxml dependency).
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "metalpdb" / "flat_db_file.xml.gz"
OUT_DIR = REPO_ROOT / "data" / "traits" / "structure" / "metal_site" / "metalpdb"
PARENT = "proteintraitsmech:METAL_BINDING_SITE"
LICENSE = ("MetalPDB (CERM, Univ. Florence) — no explicit license published; "
           "reuse terms unconfirmed (confirm with CERM before redistribution)")
DEFINITION_SOURCE = "MetalPDB (CERM, University of Florence)"

MAX_EXAMPLES = 5

# nuclearity term -> (adjective, ion-count text)
NUCLEARITY = {
    "Mononuclear": ("mononuclear", "1 metal ion"),
    "Dinuclear": ("dinuclear", "2 metal ions"),
    "Trinuclear": ("trinuclear", "3 metal ions"),
    "Tetranuclear": ("tetranuclear", "4 metal ions"),
    "Pentanuclear": ("pentanuclear", "5 metal ions"),
    "Hexanuclear": ("hexanuclear", "6 metal ions"),
    "Heptanuclear": ("heptanuclear", "7 metal ions"),
    "Octanuclear": ("octanuclear", "8 metal ions"),
    "Nonanuclear": ("nonanuclear", "9 metal ions"),
    "Decanuclear": ("decanuclear", "10 metal ions"),
    "Multinuclear": ("multinuclear", "multiple metal ions"),
}

# periodic symbol -> (element name, ChEBI atom CURIE). ChEBI ids are the
# oxidation-state-agnostic *atom* terms, verified against ChEBI/OLS4.
METAL = {
    "Ag": ("silver", "CHEBI:30512"), "Al": ("aluminium", "CHEBI:28984"),
    "Am": ("americium", "CHEBI:33389"), "As": ("arsenic", "CHEBI:27563"),
    "Au": ("gold", "CHEBI:29287"), "Ba": ("barium", "CHEBI:32594"),
    "Be": ("beryllium", "CHEBI:30501"), "Bi": ("bismuth", "CHEBI:33301"),
    "Ca": ("calcium", "CHEBI:22984"), "Cd": ("cadmium", "CHEBI:22977"),
    "Ce": ("cerium", "CHEBI:33369"), "Cf": ("californium", "CHEBI:33392"),
    "Cm": ("curium", "CHEBI:33390"), "Co": ("cobalt", "CHEBI:27638"),
    "Cr": ("chromium", "CHEBI:28073"), "Cs": ("caesium", "CHEBI:30514"),
    "Cu": ("copper", "CHEBI:28694"), "Dy": ("dysprosium", "CHEBI:33377"),
    "Er": ("erbium", "CHEBI:33379"),
    "Eu": ("europium", "CHEBI:32999"), "Fe": ("iron", "CHEBI:18248"),
    "Ga": ("gallium", "CHEBI:49631"), "Gd": ("gadolinium", "CHEBI:33375"),
    "Hf": ("hafnium", "CHEBI:33343"), "Hg": ("mercury", "CHEBI:25195"),
    "Ho": ("holmium", "CHEBI:49648"), "In": ("indium", "CHEBI:30430"),
    "Ir": ("iridium", "CHEBI:49666"), "K": ("potassium", "CHEBI:26216"),
    "La": ("lanthanum", "CHEBI:33336"), "Li": ("lithium", "CHEBI:30145"),
    "Lu": ("lutetium", "CHEBI:33382"), "Mg": ("magnesium", "CHEBI:25107"),
    "Mn": ("manganese", "CHEBI:18291"), "Mo": ("molybdenum", "CHEBI:28685"),
    "Na": ("sodium", "CHEBI:26708"), "Ni": ("nickel", "CHEBI:28112"),
    "Os": ("osmium", "CHEBI:30687"), "Pa": ("protactinium", "CHEBI:33386"),
    "Pb": ("lead", "CHEBI:25016"), "Pd": ("palladium", "CHEBI:33363"),
    "Pr": ("praseodymium", "CHEBI:49828"), "Pt": ("platinum", "CHEBI:33364"),
    "Pu": ("plutonium", "CHEBI:33388"),
    "Rb": ("rubidium", "CHEBI:33322"), "Re": ("rhenium", "CHEBI:49882"),
    "Rh": ("rhodium", "CHEBI:33359"), "Ru": ("ruthenium", "CHEBI:30682"),
    "Sb": ("antimony", "CHEBI:30513"), "Sc": ("scandium", "CHEBI:33330"),
    "Sm": ("samarium", "CHEBI:33374"),
    "Sn": ("tin", "CHEBI:27007"), "Sr": ("strontium", "CHEBI:33324"),
    "Ta": ("tantalum", "CHEBI:33348"), "Tb": ("terbium", "CHEBI:33376"),
    "Tc": ("technetium", "CHEBI:33353"), "Th": ("thorium", "CHEBI:33385"),
    "Ti": ("titanium", "CHEBI:33341"), "Tl": ("thallium", "CHEBI:30440"),
    "U": ("uranium", "CHEBI:27214"), "V": ("vanadium", "CHEBI:27698"),
    "W": ("tungsten", "CHEBI:27998"), "Y": ("yttrium", "CHEBI:33331"),
    "Yb": ("ytterbium", "CHEBI:33381"), "Zn": ("zinc", "CHEBI:27363"),
    "Zr": ("zirconium", "CHEBI:33342"),
}

# One-letter -> residue name, for spelling out simple coordination signatures.
AA = {
    "A": "Ala", "R": "Arg", "N": "Asn", "D": "Asp", "C": "Cys", "E": "Glu",
    "Q": "Gln", "G": "Gly", "H": "His", "I": "Ile", "L": "Leu", "K": "Lys",
    "M": "Met", "F": "Phe", "P": "Pro", "S": "Ser", "T": "Thr", "W": "Trp",
    "Y": "Tyr", "V": "Val",
}

_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
# stray `&` not opening a valid XML entity
_AMP_RE = re.compile(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)")
_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def slugify(text: str) -> str:
    return (_SLUG_RE.sub("-", text.lower()).strip("-")[:70]) or "metal-site"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text: str) -> list[str]:
    return [">-", f"  {' '.join((text or '').split())}"]


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


class ClassAgg:
    __slots__ = ("sites", "pdbs", "patterns", "geometries", "cofactors",
                 "examples")

    def __init__(self) -> None:
        self.sites = 0
        self.pdbs: set[str] = set()
        self.patterns: Counter = Counter()
        self.geometries: Counter = Counter()
        self.cofactors: Counter = Counter()
        # uniprot acc -> (protein_label, taxon_label, pdb_code)
        self.examples: dict[str, tuple[str, str, str]] = {}


def iter_sites(path: Path):
    """Stream <site> elements from the gzipped flat file, escaping stray
    `&` so stdlib xml.etree can parse it (no lxml)."""
    parser = ET.XMLPullParser(events=("end",))
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parser.feed(_AMP_RE.sub("&amp;", _CTRL_RE.sub("", line)))
            for _event, elem in parser.read_events():
                if elem.tag == "site":
                    yield elem
                    elem.clear()
    parser.close()
    for _event, elem in parser.read_events():
        if elem.tag == "site":
            yield elem


def aggregate(path: Path) -> dict[tuple[str, str], ClassAgg]:
    classes: dict[tuple[str, str], ClassAgg] = defaultdict(ClassAgg)
    n = 0
    for site in iter_sites(path):
        n += 1
        if n % 40000 == 0:
            print(f"  parsed {n} sites…", file=sys.stderr)
        nucl = (site.findtext("site_nuclearity") or "").strip()
        pdb = (site.findtext("pdb_code") or "").strip()
        # first UniProt-bearing protein chain → exemplar candidate
        acc = label = taxon = ""
        for chain in site.findall("site_chain"):
            up = (chain.findtext("uniprot") or "").strip()
            if up and re.match(r"^[A-Z0-9]+$", up):
                acc = up
                label = (chain.findtext("molecule_name") or "").strip()
                taxon = (chain.findtext("taxonomy_name") or "").strip()
                break
        metals = site.findall("metal")
        syms = {(m.findtext("periodic_symbol") or "").strip() for m in metals}
        for sym in syms:
            if not sym or not nucl:
                continue
            agg = classes[(sym, nucl)]
            agg.sites += 1
            if pdb:
                agg.pdbs.add(pdb)
            if acc and acc not in agg.examples and len(agg.examples) < 200:
                agg.examples[acc] = (label, taxon, pdb)
        for m in metals:
            sym = (m.findtext("periodic_symbol") or "").strip()
            if not sym or not nucl:
                continue
            agg = classes[(sym, nucl)]
            lp = (m.findtext("ligands_pattern") or "").strip()
            if lp:
                agg.patterns[lp] += 1
            g = (m.findtext("geometry") or "").strip()
            if g and g != "n/a":
                agg.geometries[g.split(" (")[0]] += 1
            cof = (m.findtext("cofactor") or "").strip()
            if cof:
                agg.cofactors[cof] += 1
    print(f"  parsed {n} sites total.", file=sys.stderr)
    return classes


# ---------------------------------------------------------------------------
# YAML emission
# ---------------------------------------------------------------------------


def describe_pattern(pat: str) -> str:
    """Render a MetalPDB ligands_pattern legibly where it is a simple
    homo-residue string (e.g. `H`→'His', `CCCC`→'Cys4'); otherwise keep the
    raw signature."""
    if pat and set(pat) <= set(AA):
        c = Counter(pat)
        return "".join(f"{AA[a]}{n if n > 1 else ''}" for a, n in
                       sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))
    return pat


def build_definition(sym: str, nucl: str, agg: ClassAgg) -> str:
    name, _chebi = METAL[sym]
    adj, ion_txt = NUCLEARITY.get(nucl, (nucl.lower(), "metal ions"))
    n_prot = len(agg.examples)
    parts = [
        f"A structural metal-binding site in which {name} is coordinated by "
        f"protein side-chain, backbone and/or exogenous ligands, classified by "
        f"MetalPDB as a {adj} {name} site ({ion_txt} per site).",
        f"Across the MetalPDB release this class aggregates {agg.sites} "
        f"metal-site occurrences in {len(agg.pdbs)} PDB structures "
        f"({n_prot}+ distinct UniProt proteins).",
    ]
    top_pat = [p for p, _ in agg.patterns.most_common(3)]
    if top_pat:
        rendered = "; ".join(f"{describe_pattern(p)} ({agg.patterns[p]})"
                             for p in top_pat)
        parts.append("The most frequent endogenous coordination signatures "
                     f"(MetalPDB ligands_pattern) are {rendered}.")
    top_geom = [g for g, _ in agg.geometries.most_common(2)]
    if top_geom:
        parts.append("Typical coordination geometry: "
                     + ", ".join(top_geom) + ".")
    top_cof = [c for c, _ in agg.cofactors.most_common(2)
               if c not in ("Metallic", "Metal Ion")]
    if top_cof:
        parts.append("Recurring cofactor context: " + ", ".join(top_cof) + ".")
    return " ".join(parts)


def build_yaml(sym: str, nucl: str, agg: ClassAgg) -> str:
    name, chebi = METAL[sym]
    adj, _ = NUCLEARITY.get(nucl, (nucl.lower(), ""))
    label = f"{adj} {name} site"
    ident = f"proteintraitsmech:METALPDB_{sym.upper()}_{nucl.upper()}"

    lines = [f"identifier: {ident}", f"label: {yaml_escape(label)}"]
    d = folded(build_definition(sym, nucl, agg))
    lines += [f"definition: {d[0]}", *d[1:]]
    lines += [f"definition_source: {yaml_escape(DEFINITION_SOURCE)}",
              "trait_axis: STRUCTURE",
              "trait_category: STRUCT_METAL_SITE",
              "term_kind: CLASS",
              "mapping_status: SEEDED",
              "parent_traits:", f"  - {PARENT}"]

    # metal ion as cofactor-role chemical participant, ChEBI-grounded
    lines += ["chemical_participants:",
              f"  - chebi: {chebi}", "    role: COFACTOR",
              f"    name: {yaml_escape(name)}"]

    # a capped handful of exemplar proteins
    exs = sorted(agg.examples.items())[:MAX_EXAMPLES]
    if exs:
        lines.append("canonical_examples:")
        for acc, (plabel, taxon, pdb) in exs:
            lines.append(f"  - protein_id: UniProtKB:{acc}")
            lines.append(f"    protein_label: {yaml_escape(plabel or acc)}")
            if taxon:
                lines.append(f"    taxon_label: {yaml_escape(taxon)}")
            note = f"MetalPDB {adj} {name} site occurrence"
            if pdb:
                note += f" in PDB {pdb}"
            lines.append(f"    note: {yaml_escape(note)}")
    lines.append(f"license: {yaml_escape(LICENSE)}")
    return "\n".join(lines) + "\n"


def target_path(sym: str, nucl: str) -> Path:
    adj, _ = NUCLEARITY.get(nucl, (nucl.lower(), ""))
    name, _ = METAL[sym]
    return OUT_DIR / f"{slugify(adj + '-' + name + '-site')}.yaml"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="write YAMLs (default: dry-run)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing files")
    ap.add_argument("--min-sites", type=int, default=1,
                    help="skip (metal, nuclearity) classes with fewer than N "
                         "aggregated site occurrences (default 1 = all)")
    ap.add_argument("--sample", type=int, default=0,
                    help="print the built YAML for N classes (dry-run review)")
    args = ap.parse_args()

    if not RAW.exists():
        print("missing data/raw/metalpdb/flat_db_file.xml.gz; run "
              "`just fetch-metalpdb`", file=sys.stderr)
        return 2

    print("Aggregating MetalPDB sites into (metal, nuclearity) classes…",
          file=sys.stderr)
    classes = aggregate(RAW)

    unknown = sorted({s for s, _ in classes if s not in METAL})
    if unknown:
        print(f"WARNING: {len(unknown)} metal symbol(s) lack a ChEBI/name "
              f"mapping and are skipped: {unknown}", file=sys.stderr)

    kept = {k: v for k, v in classes.items()
            if k[0] in METAL and k[1] in NUCLEARITY and v.sites >= args.min_sites}

    # per-metal distribution (classes + sites)
    per_metal_sites: Counter = Counter()
    per_metal_classes: Counter = Counter()
    for (sym, _nucl), agg in kept.items():
        per_metal_sites[sym] += agg.sites
        per_metal_classes[sym] += 1

    written = skipped = planned = 0
    sampled = 0
    for (sym, nucl), agg in sorted(kept.items(),
                                   key=lambda kv: (-kv[1].sites, kv[0])):
        body = build_yaml(sym, nucl, agg)
        if args.sample and sampled < args.sample:
            print("\n" + "=" * 70)
            print(f"# {target_path(sym, nucl).relative_to(REPO_ROOT)}")
            print("=" * 70)
            print(body, end="")
            sampled += 1
        path = target_path(sym, nucl)
        if path.exists() and not args.force:
            skipped += 1
            continue
        planned += 1
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
            written += 1

    print()
    print(f"MetalPDB → STRUCT_METAL_SITE: {len(kept)} classes "
          f"over {len(per_metal_classes)} metals "
          f"(min-sites={args.min_sites}).")
    print("Per-metal distribution (metal: classes / total site occurrences):")
    for sym, nsites in per_metal_sites.most_common():
        name = METAL[sym][0]
        print(f"  {sym:3} {name:14} {per_metal_classes[sym]:2} classes / "
              f"{nsites} sites")
    print()
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing → "
              f"{OUT_DIR.relative_to(REPO_ROOT)}/")
    else:
        print(f"Dry-run — would write {planned}; {skipped} already exist. "
              f"Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
