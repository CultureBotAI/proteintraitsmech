#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from PSI-MOD, the HUPO-PSI protein
modification controlled vocabulary.

Source: https://github.com/HUPO-PSI/psi-mod-CV (CC-BY-4.0)

Requires the OBO release fetched into `data/raw/PSI-MOD.obo` — either
via `just fetch-psimod` or a manual curl of
    https://raw.githubusercontent.com/HUPO-PSI/psi-mod-CV/master/PSI-MOD.obo

Each non-obsolete `[Term]` becomes one ProteinTraitRecord under
`data/traits/sequence/{modified_residue,glycosylation,lipidation,
crosslink,ptm_ontology}/`. Routing follows the same PTM-keyword table
used by `seed_prosite.py` — glycosyl/carbohydrate terms → glycosylation;
myristoyl/palmitoyl/prenyl/farnesyl/geranyl → lipidation;
ubiquitin/SUMO/cross-link → crosslink; phosphoryl/methyl/acetyl/
hydroxyl/sulf/adp-ribos → modified_residue. Terms that don't match any
subtype keyword land in `sequence/ptm_ontology/` as a generic
SEQ_PTM_SITE bucket (this is where the ontology-level "protein
modification" root and its abstract mid-level categories live).

Every emitted record carries:
  - identifier: MOD:NNNNN
  - definition: OBO `def` text (source citations stripped)
  - parent_traits: is_a targets (MOD CURIEs)
  - xrefs: OBO xref lines (Unimod / RESID / etc.)
  - synonyms: OBO synonym lines
  - license: CC-BY-4.0
  - mapping_status: SEEDED

Idempotent by default; --force overwrites. Dry-run unless --apply.
Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
TRAITS_DIR = REPO_ROOT / "data" / "traits"

PSI_MOD_OBO = RAW_DIR / "PSI-MOD.obo"
LICENSE_TAG = "CC-BY-4.0"

# Ordered PTM keyword → (schema category, subdir). Same taxonomy as
# `seed_prosite.py`'s PTM_KEYWORD_ROUTES so PSI-MOD terms and PROSITE
# PTM patterns land in matching category directories. Keys are matched
# as case-insensitive substrings of the OBO `name:` field.
PTM_KEYWORD_ROUTES: tuple[tuple[str, tuple[str, str]], ...] = (
    # SEQ_GLYCOSYLATION_SITE
    ("glycosyl",               ("SEQ_GLYCOSYLATION_SITE", "sequence/glycosylation")),
    ("carbohydr",              ("SEQ_GLYCOSYLATION_SITE", "sequence/glycosylation")),
    ("mannosyl",               ("SEQ_GLYCOSYLATION_SITE", "sequence/glycosylation")),
    ("fucosyl",                ("SEQ_GLYCOSYLATION_SITE", "sequence/glycosylation")),
    # SEQ_LIPIDATION_SITE
    ("myristoyl",              ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    ("palmitoyl",              ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    ("prenyl",                 ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    ("farnesyl",               ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    ("geranylgeranyl",         ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    ("gpi anchor",             ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    # SEQ_CROSSLINK_SITE
    ("ubiquitin",              ("SEQ_CROSSLINK_SITE",     "sequence/crosslink")),
    ("sumoyl",                 ("SEQ_CROSSLINK_SITE",     "sequence/crosslink")),
    ("cross-link",             ("SEQ_CROSSLINK_SITE",     "sequence/crosslink")),
    ("crosslink",              ("SEQ_CROSSLINK_SITE",     "sequence/crosslink")),
    ("isopeptide",             ("SEQ_CROSSLINK_SITE",     "sequence/crosslink")),
    # SEQ_MODIFIED_RESIDUE
    ("phospho",                ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("methyl",                 ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("acetyl",                 ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("hydroxyl",               ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("sulfat",                 ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("sulfon",                 ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("amidat",                 ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("carboxyl",               ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("nitrat",                 ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("adp-ribo",               ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("adp ribo",               ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("selenocystein",          ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("pyrrolysin",             ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("alkylat",                ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("iodinat",                ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("halogen",                ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("modified l-",            ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("oxidiz",                 ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("nitrosyl",               ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("formyl",                 ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("succinyl",               ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("malonyl",                ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("propionyl",              ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("butyryl",                ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("dehydr",                 ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
)


def classify(name: str) -> tuple[str, str]:
    """Return (schema category, subdir) for a PSI-MOD term based on its
    name. Falls back to the generic SEQ_PTM_SITE umbrella when no
    specific subtype keyword matches."""
    n = name.lower()
    for kw, route in PTM_KEYWORD_ROUTES:
        if kw in n:
            return route
    return ("SEQ_PTM_SITE", "sequence/ptm_ontology")


# ---------------------------------------------------------------------------
# OBO parser (deliberately minimal — matches PSI-MOD's actual usage)
# ---------------------------------------------------------------------------


_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(text: str) -> str:
    s = _SLUG_RE.sub("-", text.lower()).strip("-")
    return s[:80] or "term"


def parse_obo(text: str) -> list[dict]:
    """Return one dict per `[Term]` stanza. Repeated keys (synonym,
    xref, is_a, alt_id) become lists; single-valued keys are strings."""
    entries: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        line = line.rstrip()
        if line.startswith("[Term]"):
            if current is not None:
                entries.append(current)
            current = {}
            continue
        if line.startswith("[") and current is not None:
            # A non-[Term] stanza (e.g. [Typedef]) ends the current term.
            entries.append(current)
            current = None
            continue
        if current is None or not line or line.startswith("!"):
            continue
        key, _, value = line.partition(": ")
        if not value:
            continue
        if key in ("synonym", "xref", "is_a", "alt_id", "consider", "relationship"):
            current.setdefault(key, []).append(value)
        else:
            current[key] = value
    if current is not None:
        entries.append(current)
    return entries


# ---------------------------------------------------------------------------
# Field extraction
# ---------------------------------------------------------------------------


_DEF_RE = re.compile(r'^"((?:[^"\\]|\\.)*)"(?:\s*\[(.*)\])?\s*$')
_IS_A_RE = re.compile(r"^(MOD:\d+)(?:\s*!\s*(.*))?$")
_SYNONYM_RE = re.compile(r'^"((?:[^"\\]|\\.)*)"\s+(EXACT|BROAD|NARROW|RELATED)(?:\s+([^\s\[]+))?\s*\[.*\]?\s*$')
_XREF_RE = re.compile(r"^([A-Za-z][A-Za-z0-9._-]*):\s*(.*?)(?:\s*(?:!.*)?)$")
_XREF_TRAILING_QUOTE_RE = re.compile(r'^"(.*)"$')


def parse_def(raw: str) -> tuple[str, list[str]]:
    """Return (definition_text, list_of_source_citations) from a raw OBO
    `def:` value. Sources are the comma-separated tokens between the
    outermost square brackets."""
    m = _DEF_RE.match(raw or "")
    if not m:
        return (raw or "", [])
    text = m.group(1).replace('\\"', '"')
    sources_raw = m.group(2) or ""
    sources = [s.strip() for s in sources_raw.split(",") if s.strip()]
    return (text, sources)


def normalise_source(token: str) -> str | None:
    """Map an OBO def-source token to a CURIE our schema accepts, or
    None if it's an internal PSI-MOD reference we can drop."""
    if not token:
        return None
    token = token.strip()
    if ":" not in token:
        return None
    prefix, _, local = token.partition(":")
    prefix = prefix.strip()
    local = local.strip()
    if not local:
        return None
    if prefix.lower() in {"pubmed", "pmid"}:
        return f"PMID:{local}"
    if prefix.lower() == "doi":
        return f"DOI:{local}"
    if prefix.lower() == "psi-mod":
        return None
    # Return other prefixes as-is (RESID:, Unimod:, etc.). Some will not
    # match the schema xref pattern; the caller filters those.
    return f"{prefix}:{local}"


def parse_synonym(raw: str) -> tuple[str, str] | None:
    m = _SYNONYM_RE.match(raw)
    if not m:
        return None
    text = m.group(1).replace('\\"', '"').strip()
    scope = m.group(2)
    scope_map = {
        "EXACT":   "EXACT_SYNONYM",
        "BROAD":   "BROAD_SYNONYM",
        "NARROW":  "NARROW_SYNONYM",
        "RELATED": "RELATED_SYNONYM",
    }
    return (text, scope_map.get(scope, "RELATED_SYNONYM"))


def parse_xref(raw: str) -> str | None:
    """Return a CURIE for an OBO xref, or None to skip. PSI-MOD embeds a
    number of non-CURIE keys (Origin, Source, TermSpec, Formula, DiffMono,
    …) that we can't project into `xrefs`."""
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1]
    # Strip trailing `! comment` if present.
    body = raw.split("!", 1)[0].strip()
    m = _XREF_RE.match(body)
    if not m:
        return None
    prefix = m.group(1).strip()
    local = m.group(2).strip()
    # Some xrefs use `Origin: "S"` style — reject non-accession locals.
    if not local or local.startswith('"'):
        return None
    # Filter internal PSI-MOD annotation keys.
    if prefix in {"Origin", "Source", "TermSpec", "Formula", "DiffFormula",
                  "DiffAvg", "DiffMono", "MassAvg", "MassMono",
                  "Remap", "Comment"}:
        return None
    # Prefer canonical prefix casing for the sources we already use.
    prefix_map = {
        "Unimod":  "Unimod",
        "unimod":  "Unimod",
        "RESID":   "RESID",
        "resid":   "RESID",
        "UniMod":  "Unimod",
    }
    prefix = prefix_map.get(prefix, prefix)
    curie = f"{prefix}:{local}"
    # Final schema-pattern check: must match ^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$
    if not re.match(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$", curie):
        return None
    return curie


def parse_is_a(raw: str) -> str | None:
    m = _IS_A_RE.match(raw.strip())
    if not m:
        return None
    return m.group(1)


# ---------------------------------------------------------------------------
# YAML emission (hand-formatted; no PyYAML dep in this seeder)
# ---------------------------------------------------------------------------


def yaml_escape(text: str) -> str:
    if text is None:
        return '""'
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def yaml_folded(indent: str, text: str) -> list[str]:
    """Return a `>-` folded-scalar block, each line prefixed with two
    extra spaces beyond `indent`."""
    text = " ".join((text or "").split())
    if not text:
        return [">-", f"{indent}  \"\""]
    return [">-", f"{indent}  {text}"]


def build_yaml(entry: dict, release: str) -> str | None:
    if entry.get("is_obsolete") == "true":
        return None
    term_id = entry.get("id", "").strip()
    if not term_id.startswith("MOD:"):
        return None
    name = entry.get("name", "").strip()
    if not name:
        return None
    category, _ = classify(name)

    def_text, def_sources = parse_def(entry.get("def", ""))
    definition = def_text or name

    parents = [
        pid for pid in (parse_is_a(x) for x in (entry.get("is_a") or []))
        if pid
    ]
    seen_parents: set[str] = set()
    parents = [p for p in parents if not (p in seen_parents or seen_parents.add(p))]

    xrefs: list[str] = []
    for raw in entry.get("xref") or []:
        curie = parse_xref(raw)
        if curie:
            xrefs.append(curie)
    for src in def_sources:
        curie = normalise_source(src)
        if curie and re.match(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$", curie):
            xrefs.append(curie)
    # dedupe, preserve order
    seen_x: set[str] = set()
    xrefs = [x for x in xrefs if not (x in seen_x or seen_x.add(x))]

    synonyms: list[tuple[str, str]] = []
    for raw in entry.get("synonym") or []:
        pair = parse_synonym(raw)
        if pair:
            synonyms.append(pair)
    seen_syn: set[str] = set()
    synonyms = [
        (t, s) for (t, s) in synonyms
        if t != name and not ((t, s) in seen_syn or seen_syn.add((t, s)))
    ]

    lines: list[str] = []
    lines.append(f"identifier: {term_id}")
    lines.append(f"label: {yaml_escape(name)}")
    folded = yaml_folded("", definition)
    lines.append(f"definition: {folded[0]}")
    lines.extend(folded[1:])
    lines.append(f"definition_source: {yaml_escape(release)}")
    lines.append("trait_axis: SEQUENCE")
    lines.append(f"trait_category: {category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    if parents:
        lines.append("parent_traits:")
        for p in parents:
            lines.append(f"  - {p}")

    if synonyms:
        lines.append("synonyms:")
        for text, scope in synonyms:
            lines.append(f"  - synonym_text: {yaml_escape(text)}")
            lines.append(f"    synonym_type: {scope}")

    if xrefs:
        lines.append("xrefs:")
        for x in xrefs:
            lines.append(f"  - {x}")

    lines.append(f"license: {LICENSE_TAG}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def target_path(entry: dict) -> Path:
    _, subdir = classify(entry.get("name", ""))
    slug = slugify(entry.get("name", "") or entry.get("id", "").replace(":", "-"))
    # Suffix the MOD id so slug collisions (many "modified L-serine"
    # variants) don't clobber files.
    term_local = entry.get("id", "").split(":", 1)[-1]
    return TRAITS_DIR / subdir / f"{slug}-mod{term_local}.yaml"


def read_release_stamp() -> str:
    header = PSI_MOD_OBO.read_text(encoding="utf-8", errors="replace").splitlines()[:20]
    version = ""
    date = ""
    for line in header:
        if line.startswith("data-version:"):
            version = line.split(":", 1)[1].strip()
        elif line.startswith("date:"):
            date = line.split(":", 1)[1].strip()
    stamp = f"PSI-MOD v{version}" if version else "PSI-MOD"
    if date:
        stamp += f" ({date})"
    return stamp


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="write YAMLs (default: dry-run)")
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing files")
    parser.add_argument("--limit", type=int, default=0,
                        help="cap number of records processed (0 = all)")
    args = parser.parse_args()

    if not PSI_MOD_OBO.exists():
        print(f"missing {PSI_MOD_OBO}; run `just fetch-psimod` first",
              file=sys.stderr)
        return 2

    release = read_release_stamp()
    text = PSI_MOD_OBO.read_text(encoding="utf-8", errors="replace")
    entries = parse_obo(text)
    print(f"Parsed {len(entries)} [Term] stanzas from PSI-MOD ({release}).")

    stats = {"written": 0, "skipped": 0, "obsolete": 0, "planned": 0,
             "by_dir": {}, "errors": 0}
    processed = 0
    for entry in entries:
        if args.limit and processed >= args.limit:
            break
        if entry.get("is_obsolete") == "true":
            stats["obsolete"] += 1
            continue
        try:
            yaml_body = build_yaml(entry, release)
        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            print(f"error on {entry.get('id')}: {exc}", file=sys.stderr)
            continue
        if yaml_body is None:
            continue
        path = target_path(entry)
        key = str(path.parent.relative_to(TRAITS_DIR))
        stats["by_dir"][key] = stats["by_dir"].get(key, 0) + 1
        processed += 1
        if path.exists() and not args.force:
            stats["skipped"] += 1
            continue
        stats["planned"] += 1
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml_body, encoding="utf-8")
            stats["written"] += 1

    print()
    print("Per-directory totals (all supported, not just new):")
    for d, n in sorted(stats["by_dir"].items()):
        print(f"  data/traits/{d:34s} {n}")
    print()
    print(f"Obsolete terms skipped: {stats['obsolete']}")
    if stats["errors"]:
        print(f"Errors: {stats['errors']}")
    if args.apply:
        print(f"Wrote {stats['written']} file(s); skipped {stats['skipped']} existing.")
    else:
        print(f"Dry-run — would write {stats['planned']} file(s); "
              f"{stats['skipped']} already exist.")
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
