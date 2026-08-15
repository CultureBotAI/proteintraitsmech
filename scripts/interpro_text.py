#!/usr/bin/env python3
"""InterPro abstract cleaning, in one place, without destroying the citations (#159).

An InterPro abstract is XML prose with two kinds of inline element:

    <cite idref="PUB00004911"/>                      bibliography pointer
    <db_xref db="PFAM" dbkey="PF07730"/>             THE ACCESSION THE SENTENCE IS ABOUT

Every seeder stripped both with `re.sub(r"<[^>]+>", " ", raw)` and then swept up
the leftover brackets. For `<cite/>` that is right -- the idref is an InterPro
-internal key, meaningless outside their database. For `<db_xref/>` it is not:
the element IS the content. InterPro writes

    This domain is usually find associated with <db_xref db="PFAM" dbkey="PF07730"/> .

and the corpus received

    This domain is usually find associated with .

The cross-reference destroyed, the sentence truncated. Measured across the
release: **16,699 inline db_xrefs inside abstracts**, of which 5,521 are EC
numbers and 2,930 are UniProt accessions -- the most specific facts in the text.
9,857 entries are affected.

The visible damage undercounts it. A truncation only looks broken when it lands
next to punctuation: `... with .` or `... (  )`. An xref in the middle of a
sentence simply vanishes and leaves grammatical prose that has quietly lost its
referent, which no gate can detect.

So `db_xref` is now SUBSTITUTED with a readable CURIE rather than deleted.

THREE COPIES BECAME ONE
-----------------------
`seed_interpro`, `seed_panther` and `seed_interpro_members` each had their own
`clean_abstract`, and they had already diverged: seed_interpro swept up both
`[ ]` and `( )` husks, the other two only `[ ]`. That is why the empty-paren tell
appears in PANTHER and PRINTS records but not InterPro's own -- same bug, two
different symptoms, because the cleanup differed. This is the sixth time in this
repo that one fix landed in one copy and not its twin.
"""

from __future__ import annotations

import html
import re

# InterPro's `db` attribute -> the corpus-canonical CURIE prefix. Same spellings
# as scripts/fetch_interpro_frame.py's DB_PREFIX, extended with the databases
# that appear only as inline citations (EC, SWISSPROT, PDBE, CAZY, GENPROP).
DB_PREFIX: dict[str, str] = {
    "INTERPRO": "InterPro",
    "EC": "EC",
    "SWISSPROT": "UniProtKB",
    "PFAM": "Pfam",
    "PDBE": "PDB",
    "PDB": "PDB",
    "CAZY": "CAZy",
    "NCBIFAM": "NCBIfam",
    "PROSITEDOC": "PROSITE",
    "PROSITE": "PROSITE",
    "PROFILE": "PROSITE",
    "GENPROP": "GenProp",
    "PIRSF": "PIRSF",
    "SSF": "SUPERFAMILY",
    "SFLD": "SFLD",
    "SMART": "SMART",
    "PRINTS": "PRINTS",
    "PANTHER": "PANTHER",
    "CDD": "CDD",
    "CATHGENE3D": "CATH",
    "HAMAP": "HAMAP",
    "METACYC": "MetaCyc",
    "REACTOME": "Reactome",
    "IUPHAR": "IUPHAR",
    "GO": "GO",
}

_DB_XREF = re.compile(r'<db_xref\s+[^>]*?db="([^"]+)"\s+dbkey="([^"]+)"[^>]*/>')
_CITE = re.compile(r"<cite\s+[^>]*/>")
_TAG = re.compile(r"<[^>]+>")
# A bracket pair left holding nothing, or nothing but commas, once <cite/> is
# gone: "[ ]", "[ , ]", "( )", "( , )".
_EMPTY_BRACKETS = re.compile(r"\s*[\[(]\s*(?:,\s*)*[\])]")
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([.,;:])")
# InterPro writes `( <db_xref/> )` with spaces around the element. Deleting the
# element left `( )`, which the bracket sweep removed; SUBSTITUTING it leaves
# `( Pfam:PF02310 )`, which is faithful but reads badly -- 4,663 records.
_PAD_OPEN = re.compile(r"([\[(])\s+")
_PAD_CLOSE = re.compile(r"\s+([\])])")


def render_xref(db: str, key: str) -> str:
    """`db="PFAM" dbkey="PF07730"` -> `Pfam:PF07730`.

    An unknown database keeps its own name rather than being dropped: losing the
    accession is the bug being fixed, and a slightly odd prefix is a much smaller
    problem than a missing referent.
    """
    prefix = DB_PREFIX.get(db.upper(), db)
    return f"{prefix}:{key}"


def clean_abstract(raw: str) -> str:
    """InterPro abstract XML -> prose, with cross-references preserved as CURIEs.

    Order matters. `db_xref` must be substituted BEFORE the generic tag strip, or
    the element is gone before anything can read its attributes -- which is
    exactly how the original lost them. `cite` is removed before the bracket
    sweep so the brackets it leaves behind are empty by then.
    """
    txt = _DB_XREF.sub(lambda m: render_xref(m.group(1), m.group(2)), raw)
    txt = _CITE.sub("", txt)
    txt = _TAG.sub(" ", txt)
    txt = html.unescape(txt)
    txt = _EMPTY_BRACKETS.sub("", txt)
    txt = _PAD_OPEN.sub(r"\1", txt)
    txt = _PAD_CLOSE.sub(r"\1", txt)
    txt = _SPACE_BEFORE_PUNCT.sub(r"\1", txt)
    return " ".join(txt.split())


def clean_abstract_element(el) -> str:
    """Same, for an ElementTree element (`seed_interpro` parses that way).

    `itertext()` cannot see attributes, so the element is re-serialised first and
    then run through the string path. Doing it this way keeps ONE implementation
    of the substitution rather than a second one that drifts.
    """
    if el is None:
        return ""
    import xml.etree.ElementTree as ET
    return clean_abstract(ET.tostring(el, encoding="unicode"))


# ---------------------------------------------------------------------------------------
# WHICH InterPro entry integrates a member signature (#344)
# ---------------------------------------------------------------------------------------

def iter_member_signatures(xml_gz):
    """Yield `(db, dbkey, interpro_id)` for every signature in every `member_list`.

    THE SINGLE PARSER. Five places in this repo had independently written this walk --
    `seed_pfam`, `enrich_pfam_definitions`, `migrate_mapped_xrefs`, `build_equivalence`
    and the `pfam2interpro.tsv` generator -- and the last of those got it wrong, taking
    every `db_xref db="PFAM"` in the release including the ones inside OTHER entries'
    abstract prose. That is #344: 407 records received a neighbouring domain's abstract as
    their own definition. This module's top docstring counts six earlier instances of one
    fix landing in one copy and not its twin.

    `member_list` is the only place the release states integration. An abstract's
    `db_xref` is CONTENT -- the accession a sentence is about -- which is exactly what the
    rest of this module exists to preserve, one level down.
    """
    import gzip
    import xml.etree.ElementTree as ET

    with gzip.open(xml_gz, "rb") as fh:
        for _ev, el in ET.iterparse(fh, events=("end",)):
            if el.tag != "interpro":
                continue
            ipr = el.get("id") or ""
            members = el.find("member_list")
            if ipr and members is not None:
                for xref in members.findall("db_xref"):
                    db, key = xref.get("db", ""), xref.get("dbkey", "")
                    if db and key:
                        yield db, key, ipr
            el.clear()


def load_member_integration(xml_gz, db: str = "PFAM") -> dict[str, str]:
    """member accession -> the InterPro entry whose `member_list` contains it.

    THE SAME TRAP THIS MODULE ALREADY DOCUMENTS, ONE LEVEL UP. `db_xref` appears in two
    completely different places in `interpro.xml`, and they mean opposite things:

        <member_list>
          <db_xref protein_count="112789" db="PFAM" dbkey="PF00575" name="S1"/>
        </member_list>              <- IPR003029 IS the integration of PF00575

        <abstract>
          ... associated with <db_xref db="PFAM" dbkey="PF00575"/> ...
        </abstract>                 <- IPR059328 merely MENTIONS PF00575 in prose

    `data/raw/mappings/pfam2interpro.tsv` was derived by taking both, so 465 Pfam
    accessions map to more than one entry there and nothing says which is real. Three
    scripts read that file, two of them last-wins -- and last-wins picked the prose mention
    for 407 records, which then received a definition describing a DIFFERENT domain.
    `Pfam:PF00246` ("Zinc carboxypeptidase") got an abstract about a Big domain "found
    C-terminal to the M14 carboxypeptidase catalytic domain (Pfam:PF00246)" -- the very
    sentence that created the false mapping.

    So this is the only mapping any caller should use for "which entry's abstract describes
    this signature". Nothing here reads the TSV; it cannot, because the TSV is the defect.
    """
    out: dict[str, str] = {}
    clashes: list[tuple[str, str, str]] = []
    for xdb, key, ipr in iter_member_signatures(xml_gz):
        if xdb.upper() != db.upper():
            continue
        if key in out and out[key] != ipr:
            clashes.append((key, out[key], ipr))
        out[key] = ipr
    # ONE ENTRY PER SIGNATURE is the invariant every caller relies on -- the repair
    # rewrites a record's definition to whatever this returns, so a signature in two
    # member lists would be rewritten to a coin flip. Measured true across the release
    # (0 of 29,105), which is exactly why it must be checked rather than assumed: an
    # invariant that holds today and is enforced nowhere is a silent failure tomorrow,
    # and the last-wins dict above would hide it perfectly.
    if clashes:
        raise ValueError(
            f"{len(clashes)} {db} signature(s) appear in more than one member_list, so "
            f"'the entry that integrates it' is not well defined: "
            + ", ".join(f"{k} in {a} and {b}" for k, a, b in clashes[:5]))
    return out


# ---------------------------------------------------------------------------------------
# The API's description format, which is NOT the release's abstract format (#445)
# ---------------------------------------------------------------------------------------

# A citation GROUP: `[[cite:PUB00012956], [cite:PUB00079463], [cite:PUB00079464]]`. The
# first version matched each `[cite:X]` on its own and left the separators behind, which
# turned one ferrochelatase sentence into "...at the C terminus,,,,,,,,,,,." -- #448's
# damage class, written by the fix for it.
#
# TWO defences, and either alone handles the observed shape (verified by removing each):
# this one takes the group structurally, `_API_ORPHAN_PUNCT` below sweeps a separator left
# by any citation form this does not anticipate. The test pins the OUTCOME rather than
# either mechanism, so replacing one with something better does not fail it.
_API_CITE_GROUP = re.compile(r"\[\[cite:[^\]]*\](?:\s*,\s*\[cite:[^\]]*\])*\]")
_API_CITE = re.compile(r"\[?\[cite:[^\]]*\]\]?")
# `[interpro:IPR000001]`, `[ec:1.2.4.1]`, `[cazy:GH25]`. THE MARKER IS THE CONTENT, exactly
# as this module's top docstring says of `db_xref`: 64 accessions and EC numbers across
# these entries, which a bracket sweep would delete.
_API_XREF = re.compile(r"\[(\w+):([^\]\s]+)\]")
# Paragraph boundaries. BOTH the opening and closing tag: InterPro opens a second `<p>`
# without closing the first in 5 of the 209, so a closing-tag-only split fuses two
# sentences with no punctuation between them.
_API_PARA = re.compile(r"</?(?:p|ul|ol|reaction)>", re.I)
_API_LI_END = re.compile(r"</li>", re.I)
_API_LI_OPEN = re.compile(r"<li>", re.I)
# `Synonym(s): Penicillinase, Cephalosporinase` is metadata InterPro renders above the
# prose. Concatenated into a definition it reads as one -- 9 entries opened with it, and
# `imp-dehydrogenase` opened with two stacked. Dropped, not merged.
_API_SYNONYMS = re.compile(r"^\s*Synonym\(s\):", re.I)
# `<sup>`/`<sub>` carry chemistry, so they normally close up: `H<sub>2</sub>O` -> `H2O`,
# and 22 of the 61 occurrences are followed by a capital that continues a formula. But 18
# are followed by a LOWERCASE letter that starts an English word -- `H<sub>2</sub>O<sub>2
# </sub>to give`, `Mn<sup>2+</sup>serves`, `NADP<sup>+</sup>reductases` -- where closing up
# welds the formula to the next word. Split on the case of what follows.
# The case-insensitive flag is SCOPED to the tag. `re.I` on the whole pattern makes the
# `[a-z]` in the lookahead match capitals too, so `H<sub>2</sub>O` -- the commonest case --
# took the spaced branch and became "H2 O".
_API_TIGHT_TAG = re.compile(r"(?i:</?(?:sup|sub)>)(?![a-z])")
_API_SPACED_TAG = re.compile(r"</?(?:sup|sub)>", re.I)
# Punctuation left stranded once a citation group is gone: " ,", ",,", " ." and so on.
_API_ORPHAN_PUNCT = re.compile(r"\s*,(?=\s*[,.;:])")


def _clean_api_paragraph(raw: str) -> str:
    """One paragraph of API HTML -> prose."""
    txt = _API_CITE_GROUP.sub("", raw)
    txt = _API_CITE.sub("", txt)
    txt = _API_XREF.sub(
        lambda m: (render_xref(m.group(1), m.group(2))
                   if m.group(1).upper() in DB_PREFIX else m.group(0)), txt)
    txt = _API_TIGHT_TAG.sub("", txt)       # chemistry closes up...
    txt = _API_SPACED_TAG.sub(" ", txt)     # ...unless a word follows
    txt = _TAG.sub(" ", txt)                # every other tag needs the space
    txt = html.unescape(txt)
    txt = _EMPTY_BRACKETS.sub("", txt)
    txt = _API_ORPHAN_PUNCT.sub("", txt)
    txt = _SPACE_BEFORE_PUNCT.sub(r"\1", txt)
    return " ".join(txt.split())


def clean_api_paragraphs(blocks) -> list[str]:
    """The API description as cleaned paragraphs, in order, metadata dropped.

    Paragraph-level because the CAP has to be: InterPro puts the general subject matter
    first and the sentence that is actually about THIS entry last -- "This entry represents
    an active site found in a number of peroxidases." A head-truncation at 1,800 characters
    therefore deletes the only part that distinguishes the entry, and it did: IPR019794
    (active site) and IPR019793 (haem-binding site) came out byte-identical, as did two
    other pairs, none of them mentioning its own trait.
    """
    out = []
    for block in blocks:
        raw = block.get("text", "") if isinstance(block, dict) else str(block)
        if not raw:
            continue
        # `<li>` items are paragraphs for splitting, but rejoin with "; " below, so a list
        # reads as one sentence rather than as N fragments.
        for para in _API_PARA.split(raw):
            if not para.strip():
                continue
            items = [_clean_api_paragraph(x) for x in _API_LI_END.split(para)]
            items = [_API_LI_OPEN.sub("", x).strip() for x in items if x.strip()]
            if not items:
                continue
            # "; " ONLY where the item does not already end in punctuation. InterPro's list
            # items mostly end in a full stop, and appending unconditionally wrote 125
            # `".;"` sequences into 32 records -- against 9 in the entire 429k-record corpus
            # before this.
            joined = items[0]
            for item in items[1:]:
                joined += ("" if joined.endswith((".", ";", ":", ",")) else ";") + " " + item
            cleaned = _clean_api_paragraph(joined)
            if cleaned and not _API_SYNONYMS.match(cleaned):
                out.append(cleaned)
    return out


def clean_api_description(blocks, cap: int | None = None) -> str:
    """InterPro API `description` blocks -> prose, cross-references preserved as CURIEs.

    A SECOND cleaner, deliberately, rather than a branch inside `clean_abstract`. The two
    formats share nothing but intent: the release ships XML elements
    (`<db_xref db=... dbkey=.../>`, `<cite idref=.../>`), the API ships HTML with square
    -bracket markers. Running either text through the other's cleaner leaves markup in the
    corpus, which is how the `({swissprot:D4GXU1])` in #448 got there.

    What the corpus would lose to a naive strip, measured over the 209 entries this exists
    for: 64 `[interpro:]`/`[ec:]`/`[cazy:]` accessions deleted, and every `[2Fe-2S]`,
    `[Fe<sup>4+</sup>=O]` and `[(L-alanin-3-ylcarbamoyl)methyl]` mangled -- those are
    chemistry, not markup, and they are left exactly as they are.

    `cap` KEEPS THE LAST PARAGRAPH WHOLE and elides from the middle, because that is where
    InterPro puts the entry-specific sentence. Truncating the tail instead produced three
    pairs of byte-identical definitions for genuinely different entries.
    """
    paras = clean_api_paragraphs(blocks)
    full = " ".join(paras)
    if cap is None or len(full) <= cap or not paras:
        return full
    tail = paras[-1]
    if len(tail) >= cap:                       # one enormous paragraph: nothing to preserve
        return tail[:cap - 1].rstrip() + "\u2026"
    head = " ".join(paras[:-1])
    budget = cap - len(tail) - 3               # " … "
    return head[:budget].rstrip() + " \u2026 " + tail
