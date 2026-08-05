#!/usr/bin/env python3
"""Seed protein-family/domain traits from InterPro member databases (#162).

UniProt's "Family & Domains" section cross-references 17 classification
databases. PTM had records for nine of them. This seeds the rest:

    PIRSF   3,285   curated full-length families        SEQUENCE
    HAMAP   2,394   curated family rules (SIB)          SEQUENCE
    PRINTS  2,106   fingerprints (ordered motif sets)   SEQUENCE
    SSF     2,019   SUPERFAMILY, SCOP-based HMMs        SEQUENCE
    SMART   1,322   domain models (EMBL)                SEQUENCE
    SFLD      303   enzyme superfamily/group/family     FUNCTION

ONE SEEDER, NOT SIX
-------------------
The six differ only in an accession pattern and a routing override. Six copies of
the InterPro streaming logic is the shape `record_io.py` and `yaml_emit.py` exist
to prevent -- 43 copies of `yaml_escape` diverged before they were consolidated.

WHERE THE DATA COMES FROM, AND WHY NOT THE MEMBER DATABASES THEMSELVES
----------------------------------------------------------------------
Two inputs, both already public-domain EBI releases:

  * `data/raw/interpro_members/<db>.jsonl` -- accession, name, type and the
    integrating InterPro entry, from the EBI API (see fetch_interpro_members.py
    for why the API and not a bulk file: SUPERFAMILY has NO name in the XML, and
    the names that are there are cryptic short forms).
  * `data/raw/interpro/interpro.xml.gz` -- the integrating entry's curated
    abstract, which becomes the definition.

Going to each database's own site was the alternative. SUPERFAMILY's hosts all
time out, and SMART's EMBLEM licence forbids redistribution and derivative works.

BUT SEEDING VIA INTERPRO DOES NOT LAUNDER A LICENCE. InterPro's licence page
dedicates to CC0 exactly four resources -- InterPro, Pfam, PRINTS and SFLD -- and
adds that "the included scanning tools and signature collections may be under
different license terms". So only PRINTS and SFLD are CC0 by that route; every
other member database keeps its own terms and needs its own answer. See LICENSES.

AXIS ROUTING FOLLOWS THE REPRESENTATION
---------------------------------------
Per entry `type`, not per database -- PRINTS alone spans domain, family and
repeat. All of these are profile HMMs / PSSMs / fingerprints, i.e. *sequence*
models, so they take SEQUENCE-axis categories even when the thing they detect is
structural. SUPERFAMILY is the sharp case: its class boundaries come from SCOP,
but the model is an HMM, so it is SEQ_HOMOLOGOUS_SUPERFAMILY. The SCOP class node
itself is separately seeded from SCOPe; these are the models that detect it.

SFLD is the deliberate exception: its classes are defined by conserved chemistry
(a shared partial reaction), which is the same "defined by conserved function"
test that routes NCBIfam equivalogs to FUNC_PROTEIN_FAMILY.

Idempotent; dry-run unless --apply. Stdlib-only.
"""
from __future__ import annotations

import argparse
import gzip
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from record_io import write_record  # noqa: E402
from yaml_emit import folded, slugify as _slugify, yaml_escape  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
MEMBERS_DIR = REPO_ROOT / "data" / "raw" / "interpro_members"
INTERPRO = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
SFLD_HIERARCHY = MEMBERS_DIR / "sfld_hierarchy_flat.txt"
PRINTS_KDAT = MEMBERS_DIR / "prints42_0.kdat"
PRINTS_HIERARCHY = MEMBERS_DIR / "FingerPRINTShierarchy21Feb2012"
TRAITS_DIR = REPO_ROOT / "data" / "traits"
DEF_CAP = 1800

# Per-source licence, because "seed it from InterPro" does NOT make it CC0.
# InterPro's licence page enumerates exactly four resources:
#   "All of the InterPro, Pfam, PRINTS and SFLD downloadable data provided on the
#    InterPro website is freely available under CC0 1.0 Universal ... The included
#    scanning tools and signature collections may be under different license terms."
# So PRINTS and SFLD inherit CC0; PIRSF, SUPERFAMILY, SMART and HAMAP do not, and
# each needs its own answer. HAMAP's is CC BY 4.0, stated verbatim in the ExPASy
# README: "HAMAP is copyrighted by the SIB Swiss Institute of Bioinformatics and
# distributed under the Creative Commons Attribution (CC BY 4.0) License".
LICENSES: dict[str, str] = {
    "prints": "CC0-1.0 (InterPro CC0 dedication covers PRINTS)",
    "sfld":   "CC0-1.0 (InterPro CC0 dedication covers SFLD)",
    "hamap":  "CC-BY 4.0 (SIB HAMAP)",
}

# A database absent from LICENSES cannot be seeded. This is a hard refusal rather
# than a default, because the failure mode of guessing is publishing records the
# repo has no right to publish -- and that is not something a later run can undo.
UNSETTLED = {
    "smart": "the EMBLEM SMART licence forbids redistribution and derivative "
             "works, and InterPro's CC0 dedication does not name SMART",
    "pirsf": "PIR's terms are unverified, and InterPro's CC0 dedication names "
             "only InterPro, Pfam, PRINTS and SFLD",
    "ssf":   "SUPERFAMILY's terms are unverified and its own hosts are "
             "unreachable; InterPro's CC0 dedication does not name it",
}

# InterPro `source_database` -> (CURIE prefix, slug fallback, accession pattern).
# The prefixes are NOT invented here: they are the corpus-canonical spellings
# already used by scripts/fetch_interpro_frame.py's DB_PREFIX map.
MEMBER_DBS: dict[str, tuple[str, str, re.Pattern]] = {
    "pirsf":  ("PIRSF",       "pirsf",       re.compile(r"^PIRSF\d+$")),
    "prints": ("PRINTS",      "prints",      re.compile(r"^PR\d+$")),
    "ssf":    ("SUPERFAMILY", "superfamily", re.compile(r"^SSF\d+$")),
    "sfld":   ("SFLD",        "sfld",        re.compile(r"^SFLD[SGF]\d+$")),
    "smart":  ("SMART",       "smart",       re.compile(r"^SM\d+$")),
    "hamap":  ("HAMAP",       "hamap",       re.compile(r"^MF_\d+(_[A-Z])?$")),
}

# InterPro signature `type` -> (axis, category, directory under data/traits/).
# Mirrors seed_interpro.TYPE_MAP, which routes the corresponding ENTRY types.
TYPE_MAP: dict[str, tuple[str, str, str]] = {
    "family":                 ("SEQUENCE", "SEQ_FAMILY",                 "sequence/family"),
    "domain":                 ("SEQUENCE", "SEQ_DOMAIN",                 "sequence/domain"),
    "homologous_superfamily": ("SEQUENCE", "SEQ_HOMOLOGOUS_SUPERFAMILY",
                               "sequence/homologous_superfamily"),
    "repeat":                 ("SEQUENCE", "SEQ_REPEAT",                 "sequence/repeat"),
    "conserved_site":         ("SEQUENCE", "SEQ_CONSERVATION",           "sequence/conservation"),
    "active_site":            ("SEQUENCE", "SEQ_ACTIVE_SITE",            "sequence/active_site"),
    "binding_site":           ("SEQUENCE", "SEQ_BINDING_SITE",           "sequence/binding_site"),
    "ptm":                    ("SEQUENCE", "SEQ_PTM_SITE",               "sequence/ptm_ontology"),
}

# A whole database whose routing does not follow the signature type. SFLD's
# classes are defined by conserved chemistry, not by the signature's shape.
DB_OVERRIDE: dict[str, tuple[str, str, str]] = {
    "sfld": ("FUNCTION", "FUNC_PROTEIN_FAMILY", "function/protein_family"),
}


def slugify(text: str, fallback: str = "entry") -> str:
    """Shared implementation, with this source's length and fallback (#93)."""
    return _slugify(text, 70, fallback)


def is_curated_abstract(entry: dict | None) -> bool:
    """Whether an InterPro abstract may be used as a `definition`.

    An LLM-written abstract that no curator has reviewed must never become the
    record's definition under a `definition_source: InterPro` label -- that
    launders machine text into a curated KB in a way nobody could later detect.
    It is still carried in `definitions[]` so a curator can promote it
    deliberately (#92). Factored out here rather than copied a seventh time;
    seed_panther.py has the same predicate inline twice.
    """
    return bool(entry and entry.get("abstract")
                and (not entry.get("llm") or entry.get("reviewed")))


def clean_abstract(raw: str) -> str:
    """Strip InterPro markup, leaving the prose.

    NOTE: this drops inline `<db_xref/>` citations along with the tags, which
    truncates sentences that were about the referenced accession -- tracked in
    #159. Kept identical to seed_panther.clean_abstract so a fix lands in one
    place rather than diverging here.
    """
    txt = re.sub(r"<[^>]+>", " ", raw)
    txt = html.unescape(txt)
    txt = re.sub(r"\[\s*(,\s*)*\]", "", txt)
    txt = re.sub(r"\s+([.,;:])", r"\1", txt)
    return " ".join(txt.split())


def interpro_entries() -> dict[str, dict]:
    """InterPro accession -> its name, abstract and LLM flags.

    Keyed by ENTRY, not by member signature: the API already tells us which entry
    integrates each signature, so there is no need to reconstruct the association
    from `<member_list>` document order the way seed_panther does.

    That also sidesteps a trap in the XML. A `<db_xref>` inside `<member_list>`
    carries `protein_count=`; a `<db_xref>` inside abstract PROSE is an inline
    citation and carries nothing. Matching on `db=`/`dbkey=` alone conflates the
    two -- 19 PIRSF and 7 SSF "signatures" in this release are citations in
    someone's abstract.
    """
    if not INTERPRO.exists():
        print(f"missing {INTERPRO} — run `just fetch-interpro` first; refusing to "
              f"seed with every definition composed", file=sys.stderr)
        raise SystemExit(1)

    ent = re.compile(r'<interpro id="(IPR\d+)"')
    abst = re.compile(r"<abstract([^>]*)>")
    name_re = re.compile(r"<name>(.*?)</name>")

    out: dict[str, dict] = {}
    cur = name = None
    inabs = False
    buf: list[str] = []
    llm = reviewed = False

    def flush():
        if cur:
            out[cur] = {"name": name, "abstract": clean_abstract(" ".join(buf)),
                        "llm": llm, "reviewed": reviewed}

    with gzip.open(INTERPRO, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = ent.search(line)
            if m:
                flush()
                cur, name, inabs, buf = m.group(1), None, False, []
                llm = reviewed = False
                continue
            if cur is None:
                continue
            if name is None:
                n = name_re.search(line)
                if n:
                    name = html.unescape(n.group(1))
            a = abst.search(line)
            if a:
                llm = 'is-llm="true"' in a.group(1)
                reviewed = 'is-llm-reviewed="true"' in a.group(1)
                # 8 entries put the open tag, the body and </abstract> on one
                # line. Skipping the line whenever it closed threw that text away
                # and substituted a composed stub, so the guard meant to stop LLM
                # text being promoted was discarding curator text instead.
                inabs = "</abstract>" not in line
                buf = [] if inabs else [line[a.end():].split("</abstract>", 1)[0]]
                continue
            if inabs:
                if "</abstract>" in line:
                    inabs = False
                else:
                    buf.append(line)
    flush()
    return out


def sfld_parents() -> dict[str, str]:
    """SFLD accession -> its IMMEDIATE parent, from EBI's hierarchy file.

    The InterPro API reports `hierarchy: null` for every SFLD accession at all
    three levels, so this is the only route to the superfamily/group/family
    structure. Without it, a subgroup literally named "I" (SFLDG01162) says
    nothing at all -- subgroup I *of what*?

    The file gives ANCESTORS, not a parent, one line per entry:

        SFLDF00425: SFLDS00029 SFLDG01116
        SFLDG01162: SFLDS00036

    and the ancestors are unordered, so "the last one" is not the parent. The
    immediate parent is the DEEPEST ancestor, and depth is derivable from the
    file itself: an ancestor's own ancestor count. Emitting the full ancestor
    list instead would be redundant -- `parent_traits` is subClassOf, which is
    transitive.
    """
    if not SFLD_HIERARCHY.exists():
        return {}
    ancestors: dict[str, list[str]] = {}
    for line in SFLD_HIERARCHY.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        acc, rest = line.split(":", 1)
        ancestors[acc.strip()] = rest.split()
    depth = {a: len(ancestors.get(a, ())) for a in
             {x for v in ancestors.values() for x in v} | set(ancestors)}
    return {acc: max(anc, key=lambda a: depth.get(a, 0))
            for acc, anc in ancestors.items() if anc}


def prints_titles() -> dict[str, dict]:
    """PRINTS accession -> its real title and motif count, from the .kdat.

    The API cannot supply this. A fingerprint's `name` in the API is its CODE:
    PR00001 comes back as "GLABLOOD", and the detail endpoint shows why --
    `{"name": null, "short": "GLABLOOD"}`. There is no full name there at all,
    so seeding from the API alone would label 2,106 records with strings like
    RETINOIDXR and MTVERTEBRATE.

    The .kdat is a tagged flat file; the two tags that matter are

        gx; PR00439                 accession
        gt; 11-S seed storage protein family signature

    and `gn; COMPOUND(6)` gives the number of motifs, which is worth stating
    because a fingerprint IS an ordered set of motifs -- that is what
    distinguishes it from a single-motif signature.
    """
    if not PRINTS_KDAT.exists():
        return {}
    out: dict[str, dict] = {}
    acc = title = motifs = None
    for line in PRINTS_KDAT.open(encoding="utf-8", errors="replace"):
        if line.startswith("gc;"):
            acc = title = motifs = None
        elif line.startswith("gx;"):
            acc = line[3:].strip()
        elif line.startswith("gt;"):
            title = line[3:].strip()
        elif line.startswith("gn;"):
            m = re.search(r"\((\d+)\)", line)
            motifs = int(m.group(1)) if m else None
        if acc and title is not None:
            out[acc] = {"title": title, "motifs": motifs}
    return out


def prints_parents() -> dict[str, str]:
    """PRINTS accession -> its immediate parent, from the FingerPRINTS hierarchy.

    Format is `CODE|ACCESSION|evalue|level|descendant,codes` with `*` for a leaf.
    Note field 5 lists DESCENDANTS by code, not the parent, and lists the whole
    subtree rather than direct children -- GPCRRHODOPSN names hundreds. So the
    immediate parent of X is the entry with the SMALLEST descendant set that
    still contains X, which is the same "nearest enclosing set" rule
    `sfld_parents` uses, inverted.
    """
    if not PRINTS_HIERARCHY.exists():
        return {}
    code_to_acc: dict[str, str] = {}
    subtree: dict[str, set[str]] = {}
    for line in PRINTS_HIERARCHY.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) < 5:
            continue
        code, acc, kids = parts[0].strip(), parts[1].strip(), parts[4].strip()
        code_to_acc[code] = acc
        if kids and kids != "*":
            subtree[code] = {k.strip() for k in kids.split(",") if k.strip()}
    parents: dict[str, str] = {}
    for child_code, child_acc in code_to_acc.items():
        holders = [c for c, kids in subtree.items()
                   if child_code in kids and c != child_code]
        if holders:
            nearest = min(holders, key=lambda c: len(subtree[c]))
            parents[child_acc] = code_to_acc[nearest]
    return parents


def resolve_label(sig: dict, titles: dict[str, dict] | None) -> str:
    """The record's label, and the string its filename is slugified from.

    Computed in one place because the two must agree: the first PRINTS canary
    produced `label: "Coagulation factor GLA domain signature"` in a file named
    `glablood-pr00001.yaml`, because the path was slugified from the API's code
    while the label came from the source release's title.
    """
    extra = (titles or {}).get(sig["accession"]) or {}
    return extra.get("title") or sig["name"] or sig["accession"]


def compose_definition(prefix: str, acc: str, label: str, kind: str,
                       motifs: int | None = None) -> str:
    """Fallback when the signature has no usable InterPro abstract."""
    what = (f"a {motifs}-element fingerprint" if motifs
            else f"a protein {kind} signature")
    return (f"{label} — {what} modelled by {prefix} {acc}. "
            f"No curated InterPro abstract is available for this signature.")


def build_yaml(db: str, sig: dict, entry: dict | None,
               parents: dict[str, str] | None = None,
               titles: dict[str, dict] | None = None) -> tuple[str, str, str]:
    """Return (yaml_text, subdir, identifier) for one member signature."""
    prefix, fallback, _ = MEMBER_DBS[db]
    acc = sig["accession"]
    extra = (titles or {}).get(acc) or {}
    label = resolve_label(sig, titles)
    axis, category, subdir = DB_OVERRIDE.get(db) or TYPE_MAP[sig["type"]]
    ipr = sig.get("integrated")
    kind = sig["type"].replace("_", " ")

    if is_curated_abstract(entry):
        definition = entry["abstract"][:DEF_CAP]
        source = f"InterPro:{ipr} abstract ({prefix} {acc} is a member signature)"
        method = "SOURCED"
    else:
        definition = compose_definition(prefix, acc, label, kind,
                                        extra.get("motifs"))
        source = f"{prefix} signature name (composed; no curated InterPro abstract)"
        method = "GENERATED"

    lines = [f"identifier: {prefix}:{acc}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += [f"definition_source: {yaml_escape(source)}",
              f"trait_axis: {axis}",
              f"trait_category: {category}",
              "term_kind: CLASS",
              "mapping_status: SEEDED"]

    parent = (parents or {}).get(acc)
    if parent:
        lines += ["parent_traits:", f"  - {prefix}:{parent}"]

    if entry and entry.get("name") and entry["name"].strip().lower() != label.strip().lower():
        lines += ["synonyms:",
                  f"  - synonym_text: {yaml_escape(entry['name'])}",
                  "    synonym_type: RELATED_SYNONYM",
                  f"    source: InterPro:{ipr}"]

    if ipr:
        # `mapped_xrefs`, not `xrefs`: the association is asserted by InterPro's
        # integration, not by the member database's own record.
        lines += ["mapped_xrefs:",
                  f"  - object: InterPro:{ipr}",
                  "    mapping_source: interpro-member-list"]

    defs = [("GENERAL", definition, source, method)]
    # An unreviewed LLM abstract is kept but never promoted to `definition`.
    if entry and entry.get("abstract") and not is_curated_abstract(entry):
        defs.append(("GENERAL", entry["abstract"][:DEF_CAP],
                     f"InterPro:{ipr} abstract (LLM-generated, not curator-reviewed)",
                     "GENERATED"))
    lines.append("definitions:")
    for kind_, text, src, meth in defs:
        # `folded` indents by two, which is right for a top-level key. A
        # definitions[] entry is nested one list level deeper, so the value needs
        # six. Emitting four produced YAML whose text sat at the same depth as
        # its own `text:` key.
        d = folded(text)
        lines += [f"  - kind: {kind_}", f"    text: {d[0]}",
                  f"      {d[1].strip()}",
                  f"    source: {yaml_escape(src)}", f"    method: {meth}"]

    lines.append(f"license: {LICENSES[db]}")
    return "\n".join(lines) + "\n", f"{subdir}/{fallback}", f"{prefix}:{acc}"


def load_signatures(db: str) -> list[dict]:
    path = MEMBERS_DIR / f"{db}.jsonl"
    if not path.exists():
        print(f"missing {path} — run `just fetch-interpro-members --db {db}` first",
              file=sys.stderr)
        raise SystemExit(1)
    return [json.loads(ln) for ln in path.open(encoding="utf-8") if ln.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", required=True, choices=sorted(MEMBER_DBS),
                    help="which member database to seed")
    ap.add_argument("--apply", action="store_true", help="write files")
    ap.add_argument("--force", action="store_true", help="overwrite existing")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    db = args.db
    if db not in LICENSES:
        why = UNSETTLED.get(db, "no licence has been recorded for this database")
        print(f"refusing to seed {db}: {why}.\n"
              f"Settle the licence and add an entry to LICENSES first — a record "
              f"published without redistribution rights cannot be un-published.",
              file=sys.stderr)
        return 2
    prefix, fallback, pattern = MEMBER_DBS[db]
    signatures = load_signatures(db)
    print(f"{db}: {len(signatures):,} signatures", file=sys.stderr)

    print("indexing InterPro abstracts…", file=sys.stderr)
    entries = interpro_entries()
    print(f"  {len(entries):,} InterPro entries", file=sys.stderr)
    parents = {"sfld": sfld_parents, "prints": prints_parents}.get(
        db, dict)()
    titles = prints_titles() if db == "prints" else {}
    if parents:
        print(f"  {len(parents):,} parent links", file=sys.stderr)
    if titles:
        print(f"  {len(titles):,} titles from the source release", file=sys.stderr)

    # identifier -> current path, so idempotency survives a signature being
    # renamed upstream (the filename embeds the label, the identifier does not).
    by_identifier: dict[str, Path] = {}
    for sub in {(DB_OVERRIDE.get(db) or v)[2] for v in TYPE_MAP.values()} | \
               {(DB_OVERRIDE[db][2] if db in DB_OVERRIDE else "")}:
        d = TRAITS_DIR / sub / fallback if sub else None
        if d and d.exists():
            for f in d.glob("*.yaml"):
                with f.open(encoding="utf-8") as fh:
                    for ln in fh:
                        if ln.startswith("identifier:"):
                            by_identifier[ln.split(":", 1)[1].strip()] = f
                            break
    print(f"  {len(by_identifier):,} {prefix} records already in the corpus",
          file=sys.stderr)

    stat: dict[str, int] = {}

    def bump(k, n=1):
        stat[k] = stat.get(k, 0) + n

    written = 0
    for sig in signatures:
        acc = sig["accession"]
        if not pattern.match(acc):
            bump(f"skipped: accession does not match {pattern.pattern}")
            continue
        if db not in DB_OVERRIDE and sig["type"] not in TYPE_MAP:
            bump(f"skipped: unroutable signature type {sig['type']!r}")
            continue

        entry = entries.get(sig["integrated"]) if sig.get("integrated") else None
        if sig.get("integrated") and entry is None:
            bump("integrated into an InterPro entry absent from this release")
        if is_curated_abstract(entry):
            bump("definition: curated InterPro abstract")
        elif entry and entry.get("abstract"):
            bump("definition: composed (LLM abstract kept but not promoted)")
        elif sig.get("integrated"):
            bump("definition: composed (integrating entry has no abstract)")
        else:
            bump("definition: composed (not integrated into InterPro)")
        bump("parent_traits: linked" if parents.get(acc)
             else "parent_traits: none (top level or absent from the hierarchy)")

        text, subdir, ident = build_yaml(db, sig, entry, parents, titles)
        out_dir = TRAITS_DIR / subdir
        path = out_dir / f"{slugify(resolve_label(sig, titles), fallback)}-{acc.lower()}.yaml"

        existing = by_identifier.get(ident)
        if existing is not None and not args.force:
            bump("skipped: already present")
            continue

        if args.apply:
            out_dir.mkdir(parents=True, exist_ok=True)
            write_record(path, text)
            if existing is not None and existing != path:
                existing.unlink()
                bump("renamed: removed the stale file at the old label's path")
        elif written == 0:
            print(text)
        written += 1
        bump(f"written: {subdir}")
        if args.limit and written >= args.limit:
            break

    print(f"\n{'wrote' if args.apply else 'would write'}: {written:,}", file=sys.stderr)
    for k in sorted(stat, key=lambda k: -stat[k]):
        print(f"  {k:<58}{stat[k]:>8,}", file=sys.stderr)
    if args.limit and written >= args.limit:
        print(f"  PARTIAL: stopped at --limit {args.limit}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
