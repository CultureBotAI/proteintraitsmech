#!/usr/bin/env python3
"""Seed protein-family traits from PANTHER (CC-BY 4.0) → SEQUENCE / SEQ_FAMILY.

PANTHER classifies full-length proteins into families by profile HMM, so under
the repo's axis-follows-representation rule a PANTHER family is a **SEQUENCE**
trait (`SEQ_FAMILY`), the same call already made for Pfam/NCBIfam/CDD — not
`FUNC_PROTEIN_FAMILY`, which is reserved for families defined by conserved
*function* (NCBIfam/TIGRFAM equivalogs).

SCOPE: FAMILIES ONLY, NOT SUBFAMILIES
-------------------------------------
The release has 15,683 families and 128,012 subfamilies. Only families are
seeded, for two reasons:

  * **Scale.** The repo tracks 410,515 files. All 143,695 PANTHER entries would
    take it to ~554k, past the ~500k threshold at which git and the GitHub UI
    degrade (`research/docs-scalability-audit-1.md`, the `scalability-check`
    skill's tier D). Families alone land at ~426k.
  * **Granularity.** InterPro integrates PANTHER at the family level and only
    there — all 10,460 integrated PANTHER signatures are families, zero are
    subfamilies. The family is the unit the wider ecosystem treats as the class.

Subfamilies remain available in the same file if that decision is revisited.

WHERE DEFINITIONS COME FROM, AND WHAT IS NOT LAUNDERED
------------------------------------------------------
`PANTHER19.0_HMM_classifications` has no abstracts — only a name plus GO,
protein-class and pathway annotations. Definitions therefore come in tiers:

  1. **Curated InterPro abstract** (7,691 families). PANTHER families are
     integrated into InterPro entries, and this reads the abstract of the
     integrating entry straight out of `data/raw/interpro/interpro.xml.gz`.
     `method: SOURCED`.
  2. **Composed** from PANTHER's own name + GO + protein class otherwise, the
     same pattern `seed_ncbifam.py` uses. `method: GENERATED`.

  **InterPro now marks LLM-written abstracts** (`is-llm`, `is-llm-reviewed`).
  Of the 3,008 LLM-generated abstracts on PANTHER-integrated entries, only 262
  are curator-reviewed. An unreviewed LLM abstract is **never** used as the
  record's `definition` — that would launder machine-written text into a curated
  KB under a `definition_source: InterPro` label. It is still carried in
  `definitions[]` with `method: GENERATED` and an explicit source label, so a
  curator can promote it deliberately.

Labels are PANTHER's own, which are ALL CAPS in the source. They are kept
verbatim rather than re-cased, and InterPro's natural-case name is added as an
EXACT_SYNONYM where one exists.

Input (fetch via `just fetch-panther`, gitignored):
  data/raw/panther/PANTHER19.0_HMM_classifications
  data/raw/interpro/interpro.xml.gz          (already fetched for seed_interpro)

Idempotent; dry-run unless --apply. Stdlib-only.
"""

from __future__ import annotations

import argparse
import gzip
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from interpro_text import clean_abstract as _clean  # noqa: E402
from record_io import write_record  # noqa: E402
from yaml_emit import folded, slugify as _slugify, yaml_escape  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW = REPO_ROOT / "data" / "raw" / "panther" / "PANTHER19.0_HMM_classifications"
INTERPRO = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
OUT_DIR = REPO_ROOT / "data" / "traits" / "sequence" / "family" / "panther"
LICENSE = "CC-BY 4.0"
RELEASE = "PANTHER 19.0"
DEF_CAP = 1800
# Minimum annotated subfamilies before their consensus may speak for the family (#150).
MIN_SUBFAMILIES = 2

_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_UNNAMED = {"FAMILY NOT NAMED", "SUBFAMILY NOT NAMED", ""}
_GO_RE = re.compile(r"^(.*)#(GO:\d{7})$")
_PW_RE = re.compile(r"^(.*)#(P\d{5})$")


def slugify(text: str) -> str:
    """Shared implementation, with this source's length and fallback (#93)."""
    return _slugify(text, 70, 'panther')


def interpro_index() -> dict[str, dict]:
    """PANTHER family id -> the integrating InterPro entry, its name and abstract.

    Streams the InterPro XML rather than loading it: the entry's abstract is
    emitted before its `member_list`, so the abstract seen most recently belongs
    to the entry whose members follow.
    """
    ent = re.compile(r'<interpro id="(IPR\d+)"[^>]*type="([A-Za-z_]+)"')
    abst = re.compile(r"<abstract([^>]*)>")
    pan = re.compile(r'db="PANTHER" dbkey="(PTHR[0-9]+)"')
    name_re = re.compile(r"<name>(.*?)</name>")

    out: dict[str, dict] = {}
    cur = name = None
    inabs = False
    buf: list[str] = []
    llm = reviewed = False
    if not INTERPRO.exists():
        # Hard failure, not a warning. Without it half the corpus silently loses its
        # curated definition, and because the skip predicate is per-record a later
        # run with InterPro present would not repair any of it.
        print(f"missing {INTERPRO} — run `just fetch-interpro` first; refusing to "
              f"seed with every definition composed", file=sys.stderr)
        raise SystemExit(1)
    with gzip.open(INTERPRO, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = ent.search(line)
            if m:
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
                # 8 InterPro entries put the open tag, the text and </abstract> on a
                # single line. Skipping the line whenever it closed threw that text
                # away and substituted a composed stub — so the guard meant to stop
                # LLM text being promoted was discarding curator-written text instead.
                # Capture the inline body before deciding whether the block continues.
                inabs = "</abstract>" not in line
                buf = [] if inabs else [line[a.end():].split("</abstract>", 1)[0]]
                continue
            if inabs:
                if "</abstract>" in line:
                    inabs = False
                else:
                    buf.append(line)
            m = pan.search(line)
            if m:
                out[m.group(1)] = {"ipr": cur, "name": name,
                                   "abstract": clean_abstract(" ".join(buf)),
                                   "llm": llm, "reviewed": reviewed}
    return out


def clean_abstract(raw: str) -> str:
    """Delegates to the shared cleaner (#159).

    This stripped every tag with one regex, which deleted inline `<db_xref/>`
    citations along with the markup -- the accession the sentence was about.
    """
    return _clean(raw)


def parse_annotations(parts: list[str]) -> dict:
    def col(i: int) -> str:
        return parts[i].strip() if len(parts) > i else ""

    def gos(i: int) -> list[tuple[str, str]]:
        out = []
        for tok in col(i).split(";"):
            m = _GO_RE.match(tok.strip())
            if m:
                out.append((m.group(1).strip(), m.group(2)))
        return out

    classes = [t.split("#")[0].strip() for t in col(5).split(";") if t.strip()]
    pathways = []
    for tok in col(6).split(";"):
        m = _PW_RE.match(tok.strip())
        if m:
            pathways.append((m.group(1).strip(), m.group(2)))
    return {"mf": gos(2), "bp": gos(3), "cc": gos(4),
            "classes": [c for c in classes if c], "pathways": pathways}


def has_annotations(ann: dict) -> bool:
    return any(ann[k] for k in ("mf", "bp", "cc", "classes"))


def subfamily_consensus(lines=None) -> dict[str, tuple[dict, int]]:
    """Per family, the annotations EVERY one of its annotated subfamilies carries.

    PANTHER annotates the subfamily (`PTHR12652:SF23`) far more often than the family.
    3,596 families are annotation-free at source, but 339 of them have at least one
    annotated subfamily -- so the release does say something about the family, just not
    on the family's own row (#150).

    Two deliberate restrictions, because a family-level definition composed from
    subfamily rows asserts something the source does not state directly:

      * at least MIN_SUBFAMILIES annotated subfamilies must exist, so a single outlier
        subfamily cannot speak for the whole family;
      * a term must appear in EVERY annotated subfamily, not merely in a majority. A GO
        term carried by 2 of 10 subfamilies describes those two, not the family.

    Intersection rather than majority is what makes the claim safe to state, and it is
    what costs the most coverage: 339 families have an annotated subfamily, 243 have two
    or more, and 228 of those share a term. The callers phrase the result as
    subfamily-derived so it can never be read as a family-level source annotation.

    Returns {family_pid: (annotations, number_of_annotated_subfamilies)}.

    `lines` defaults to the raw release; tests pass their own rows so the rule can be
    exercised without the 88 MB file.
    """
    groups: dict[str, list[dict]] = {}
    for line in (RAW.open(encoding="utf-8") if lines is None else lines):
        parts = line.rstrip("\n").split("\t")
        pid = parts[0].strip()
        if ":SF" not in pid:
            continue
        ann = parse_annotations(parts)
        if has_annotations(ann):
            groups.setdefault(pid.split(":")[0], []).append(ann)

    out: dict[str, tuple[dict, int]] = {}
    for family, anns in groups.items():
        if len(anns) < MIN_SUBFAMILIES:
            continue
        agreed: dict = {"pathways": []}
        for key in ("mf", "bp", "cc"):
            shared = set.intersection(*({go for _, go in a[key]} for a in anns))
            names = {go: n for a in anns for n, go in a[key]}
            # Sorted by CURIE so the composed text is stable across runs.
            agreed[key] = [(names[go], go) for go in sorted(shared)]
        agreed["classes"] = sorted(set.intersection(*(set(a["classes"]) for a in anns)))
        if has_annotations(agreed):
            out[family] = (agreed, len(anns))
    return out


def compose_from_subfamilies(pid: str, label: str, agreed: dict, n_sub: int,
                            ranker=None) -> str:
    """A definition for a family PANTHER annotates only through its subfamilies.

    Says so in the prose. "Subfamilies are annotated with ..." is a different claim from
    "Members are annotated with ...", and the difference is the whole reason this is
    allowed to exist -- see subfamily_consensus.
    """
    bits = [f"{label} — a full-length protein family modelled by the "
            f"{RELEASE} profile HMM {pid}.",
            f"{RELEASE} records no annotations on the family itself; the following are "
            f"shared by all {n_sub} of its annotated subfamilies."]
    if agreed["classes"]:
        bits.append("PANTHER protein class: "
                    + ", ".join(agreed["classes"][:3]) + ".")
    for key, lead in (("mf", "Subfamilies are annotated with the molecular function"),
                      ("bp", "Subfamilies participate in"),
                      ("cc", "Subfamilies localise to")):
        terms = ranker.rank(agreed[key]) if ranker is not None else agreed[key]
        names = [n for n, _ in terms][:3]
        if names:
            bits.append(f"{lead} {', '.join(names)}.")
    return " ".join(bits)


SUBFAMILY_SOURCE = (f"{RELEASE} (composed from the family name and the GO / "
                    f"protein-class annotations shared by all of its annotated "
                    f"subfamilies)")


def compose_definition(pid: str, label: str, ann: dict, ranker=None) -> str:
    """`ranker` is a `go_hierarchy.GoRanker`, or None to keep the source's order.

    With one, redundant ancestors are dropped and the rest ordered most-specific-first
    before the three-term cap applies, so the cap keeps the terms that say the most
    rather than the ones with the lowest GO ids (#152). None reproduces the pre-#152
    text exactly, which is what the recompose script needs to identify untouched
    records and what the tests use to avoid depending on a 38k-term ontology file.
    """
    bits = [f"{label} — a full-length protein family modelled by the "
            f"{RELEASE} profile HMM {pid}."]
    if ann["classes"]:
        bits.append("PANTHER protein class: " + ", ".join(ann["classes"][:3]) + ".")
    # Each clause is a standalone sentence. The leads used to read "and
    # participate in" / "and localise to", which only parsed when the molecular
    # function clause preceded them -- any family annotated with BP or CC but no
    # MF got a sentence starting "and". Since bits are joined after each already
    # ends in ".", the "and" forms never worked at all: 1,707 records read
    # "... profile HMM PTHR46022. and localise to cell periphery." Standalone
    # sentences are correct for all eight present/absent combinations without
    # any conditional grammar. See scripts/repair_panther_definitions.py.
    for key, lead in (("mf", "Members are annotated with the molecular function"),
                      ("bp", "Members participate in"),
                      ("cc", "Members localise to")):
        terms = ranker.rank(ann[key]) if ranker is not None else ann[key]
        names = [n for n, _ in terms][:3]
        if names:
            bits.append(f"{lead} {', '.join(names)}.")
    return " ".join(bits)


def build_yaml(pid: str, label: str, ann: dict, ipr: dict | None,
               ranker=None) -> str:
    curated = bool(ipr and ipr["abstract"] and (not ipr["llm"] or ipr["reviewed"]))
    if curated:
        definition = ipr["abstract"][:DEF_CAP]
        source = f"InterPro:{ipr['ipr']} abstract (PANTHER {pid} is a member signature)"
    else:
        definition = compose_definition(pid, label, ann, ranker)
        source = (f"{RELEASE} (composed from the family name and its GO / "
                  f"protein-class annotations)")

    lines = [f"identifier: PANTHER:{pid}", f"label: {yaml_escape(label)}"]
    f = folded(definition)
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += [f"definition_source: {yaml_escape(source)}",
              "trait_axis: SEQUENCE",
              "trait_category: SEQ_FAMILY",
              "term_kind: CLASS",
              "mapping_status: SEEDED"]

    if ipr and ipr["name"] and ipr["name"].strip().lower() != label.strip().lower():
        lines += ["synonyms:",
                  f"  - synonym_text: {yaml_escape(ipr['name'])}",
                  "    synonym_type: EXACT_SYNONYM",
                  f"    source: InterPro:{ipr['ipr']}"]

    xrefs = []
    if ipr:
        xrefs.append((f"InterPro:{ipr['ipr']}", "interpro-member-list"))
    for key in ("mf", "bp", "cc"):
        for _, go in ann[key]:
            xrefs.append((go, "panther-hmm-classifications"))
    for _, pw in ann["pathways"]:
        xrefs.append((f"panther.pathway:{pw}", "panther-hmm-classifications"))
    seen = set()
    rows = [(o, s) for o, s in xrefs if not (o in seen or seen.add(o))]
    if rows:
        lines.append("mapped_xrefs:")
        for obj, src in rows:
            lines += [f"  - object: {obj}", f"    mapping_source: {src}"]

    defs = [("GENERAL", definition, source, "SOURCED" if curated else "GENERATED")]
    # An unreviewed LLM abstract is kept but never promoted to `definition`.
    if ipr and ipr["abstract"] and not curated:
        defs.append(("GENERAL", ipr["abstract"][:DEF_CAP],
                     f"InterPro:{ipr['ipr']} abstract (LLM-generated, not "
                     f"curator-reviewed)", "GENERATED"))
    lines.append("definitions:")
    for kind, text, src, method in defs:
        d = folded(text)
        lines += [f"  - kind: {kind}", f"    text: {d[0]}", f"    {d[1]}",
                  f"    source: {yaml_escape(src)}", f"    method: {method}"]

    lines.append(f"license: {LICENSE}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write files")
    ap.add_argument("--force", action="store_true", help="overwrite existing")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--subfamilies", action="store_true",
                    help="also emit the 128,012 subfamilies (see the scale note "
                         "in this module's docstring before using)")
    args = ap.parse_args()

    if not RAW.exists():
        print(f"missing {RAW} — run `just fetch-panther`", file=sys.stderr)
        return 1

    # Load the GO hierarchy up front so a missing ontology fails before any record is
    # written, the same way a missing InterPro release does. Without it the composer
    # would silently fall back to source order and emit definitions that differ from
    # every other record's (#152).
    from go_hierarchy import GO_OBO, GoRanker  # noqa: PLC0415
    if not GO_OBO.exists():
        print(f"missing {GO_OBO} — run `just fetch-obo` first; refusing to seed with "
              f"unranked GO terms", file=sys.stderr)
        return 1
    ranker = GoRanker()
    print(f"  {len(ranker.parents):,} GO terms indexed for term ranking",
          file=sys.stderr)

    print("indexing InterPro abstracts…", file=sys.stderr)
    ipr_idx = interpro_index()
    print(f"  {len(ipr_idx):,} PANTHER families integrated into InterPro",
          file=sys.stderr)

    # identifier -> current path, so idempotency survives a family being renamed
    # upstream (the filename embeds the label, the identifier does not).
    by_identifier: dict[str, Path] = {}
    if OUT_DIR.exists():
        for f in OUT_DIR.glob("*.yaml"):
            with f.open(encoding="utf-8") as fh:
                for ln in fh:
                    if ln.startswith("identifier:"):
                        by_identifier[ln.split(":", 1)[1].strip()] = f
                        break
    print(f"  {len(by_identifier):,} PANTHER records already in the corpus",
          file=sys.stderr)

    stat: dict[str, int] = {}

    def bump(k, n=1):
        stat[k] = stat.get(k, 0) + n

    written = 0
    for line in RAW.open(encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        pid = parts[0].strip()
        if not pid:
            continue
        if ":SF" in pid and not args.subfamilies:
            bump("skipped: subfamily (out of scope)")
            continue
        raw_label = (parts[1] if len(parts) > 1 else "").strip()
        ipr = ipr_idx.get(pid)
        label = raw_label
        if raw_label.upper() in _UNNAMED:
            # PANTHER declines to name it; borrow InterPro's name if the family is
            # integrated, otherwise there is no trait to state and it is skipped.
            if ipr and ipr.get("name"):
                label = ipr["name"]
                bump("unnamed in PANTHER: named from InterPro")
            else:
                bump("skipped: unnamed and not in InterPro")
                continue

        ann = parse_annotations(parts)
        path = OUT_DIR / f"{slugify(label)}-{pid.lower()}.yaml"
        # Skip on the IDENTIFIER, not the filename. The filename embeds the slugified
        # label, so if a release renames a family the old path no longer exists and a
        # second file would be written carrying the same `identifier: PANTHER:…`.
        # The 229 families whose label comes from InterPro are the most exposed,
        # since they track a second, independently-versioned source.
        existing = by_identifier.get(f"PANTHER:{pid}")
        if existing is not None and not args.force:
            bump("skipped: already present")
            continue

        text = build_yaml(pid, label, ann, ipr, ranker)
        curated = bool(ipr and ipr["abstract"] and (not ipr["llm"] or ipr["reviewed"]))
        bump("definition: curated InterPro abstract" if curated
             else "definition: composed from PANTHER annotations")
        if ipr and ipr["abstract"] and not curated:
            bump("  ...LLM abstract kept in definitions[] but not promoted")
        bump("written")
        if args.apply:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            write_record(path, text)
            # A rename leaves the record at a stale path; remove it so the
            # identifier stays unique in the corpus.
            if existing is not None and existing != path:
                existing.unlink()
                bump("renamed: removed the stale file at the old label's path")
        elif written == 0:
            print(text)
        written += 1
        if args.limit and written >= args.limit:
            break

    for k in sorted(stat, key=lambda k: -stat[k]):
        print(f"  {k:<52}{stat[k]:>8,}", file=sys.stderr)
    if not args.apply:
        print("\nDry run — pass --apply to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
