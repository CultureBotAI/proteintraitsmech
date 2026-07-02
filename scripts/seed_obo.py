#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from OBO-format ontologies.

A generic, reusable importer for CC-BY OBO ontologies whose terms carry
protein-trait analogies. Unlike `seed_psi_mod.py` (where every MOD term
is a PTM → a sequence trait, so the whole ontology maps 1:1), the
ontologies handled here are *broad* — they describe interactions,
qualities, or organismal phenotypes, only a subset of which are protein
traits. Each source therefore declares **branch-scoped routes**: a term
is imported only if it is an `is_a` descendant (transitive, inclusive)
of a configured root, and it inherits that root's `(trait_axis,
trait_category, subdir)`. Everything outside the configured roots is
deliberately skipped.

Sources (`just fetch-obo` mirrors each into `data/raw/<FILE>.obo`):

  psimi  PSI-MI (HUPO-PSI molecular-interaction CV, CC-BY-4.0)
         → only the `interaction type` branch (MI:0190), mapped to
           FUNCTION / FUNC_INTERACTION_PARTNER. The bulk of PSI-MI is
           experimental *methods* (detection, participant identification)
           which are not protein traits and are skipped.

  pato   PATO (Phenotype And Trait Ontology, CC-BY-4.0)
         → a curated whitelist of protein-relevant physicochemical
           quality roots (stability, flexibility, elasticity → dynamics;
           solubility, hydrophobicity, electric charge → surface). PATO
           qualities are generic modifiers for *any* entity, so a
           whitelist — not a dump — is the right scope.

  metpo  METPO (Microbial Ecophysiological Trait & Phenotype Ontology,
           CC-BY-4.0) → the growth-preference / tolerance branches
           (temperature, pH, salinity, oxygen, pressure, radiation,
           osmotic, metal) map to FUNC_ENVIRONMENTAL_RESPONSE; the
           metabolism / biological-process branch and the enzyme-activity
           biochemical tests (catalase, oxidase, urease, coagulase,
           indole, methyl-red, Voges-Proskauer) map to
           FUNC_ENZYMATIC_ACTIVITY. Purely organismal phenotypes (cell
           shape, gram stain, motility, sporulation, pigmentation,
           colony morphology, pathogenicity, GC content, biosafety) have
           no protein analogue and are skipped.

Every emitted record carries: identifier (source CURIE), label, OBO
`def` text, definition_source (release stamp), trait_axis, trait_category,
term_kind: CLASS, mapping_status: SEEDED, parent_traits (same-ontology
is_a targets), synonyms, xrefs (OBO xref lines + grounding CURIEs from
the def source list), and license.

Idempotent by default; --force overwrites. Dry-run unless --apply.
Stdlib-only.

Usage:
  python3 scripts/seed_obo.py psimi                # dry-run
  python3 scripts/seed_obo.py metpo --apply
  python3 scripts/seed_obo.py all --apply          # every configured source
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
TRAITS_DIR = REPO_ROOT / "data" / "traits"


# ---------------------------------------------------------------------------
# Per-source configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Route:
    """A branch of an ontology to import. `root` is a term CURIE; its
    transitive `is_a` descendants (inclusive) are routed to
    `(axis, category, subdir)`. Routes are applied in declaration order;
    a term takes the first route whose subtree contains it."""
    root: str
    axis: str
    category: str
    subdir: str


@dataclass(frozen=True)
class Source:
    key: str
    obo_file: str
    id_prefix: str            # e.g. "MI:", "PATO:", "METPO:"
    release_prefix: str       # human stamp, e.g. "PSI-MI"
    license: str
    routes: tuple[Route, ...] = field(default_factory=tuple)


SOURCES: dict[str, Source] = {
    "psimi": Source(
        key="psimi",
        obo_file="PSI-MI.obo",
        id_prefix="MI:",
        release_prefix="PSI-MI",
        license="CC-BY-4.0",
        routes=(
            Route("MI:0190", "FUNCTION", "FUNC_INTERACTION_PARTNER",
                  "function/interaction_partner/psi_mi"),
        ),
    ),
    "pato": Source(
        key="pato",
        obo_file="PATO.obo",
        id_prefix="PATO:",
        release_prefix="PATO",
        license="CC-BY-4.0",
        routes=(
            # dynamics-like mechanical qualities
            Route("PATO:0015026", "STRUCTURE", "STRUCT_STABILITY",
                  "structure/stability/pato"),          # stability
            Route("PATO:0001543", "STRUCTURE", "STRUCT_DYNAMICS",
                  "structure/dynamics/pato"),           # flexibility
            Route("PATO:0001031", "STRUCTURE", "STRUCT_DYNAMICS",
                  "structure/dynamics/pato"),           # elasticity
            # surface / physicochemical qualities
            Route("PATO:0001536", "STRUCTURE", "STRUCT_SURFACE",
                  "structure/surface/pato"),            # solubility
            Route("PATO:0001884", "STRUCTURE", "STRUCT_SURFACE",
                  "structure/surface/pato"),            # hydrophobicity
            Route("PATO:0002193", "STRUCTURE", "STRUCT_SURFACE",
                  "structure/surface/pato"),            # electric charge
        ),
    ),
    "metpo": Source(
        key="metpo",
        obo_file="METPO.obo",
        id_prefix="METPO:",
        release_prefix="METPO",
        license="CC-BY-4.0",
        routes=(
            # --- environmental response (qualitative growth preferences /
            #     tolerances). The "phenotype with numerical limits"
            #     branches (METPO:1000531-536) are deliberately excluded:
            #     they hold machine-binned measurement values (e.g. "NaCl
            #     delta mid1") with no protein analogue. ---
            Route("METPO:1000601", "FUNCTION", "FUNC_ENVIRONMENTAL_RESPONSE",
                  "function/environmental_response/metpo"),  # oxygen preference
            Route("METPO:1000613", "FUNCTION", "FUNC_ENVIRONMENTAL_RESPONSE",
                  "function/environmental_response/metpo"),  # temperature preference
            Route("METPO:1000629", "FUNCTION", "FUNC_ENVIRONMENTAL_RESPONSE",
                  "function/environmental_response/metpo"),  # halophily preference
            Route("METPO:1003000", "FUNCTION", "FUNC_ENVIRONMENTAL_RESPONSE",
                  "function/environmental_response/metpo"),  # pH growth preference
            Route("METPO:1007070", "FUNCTION", "FUNC_ENVIRONMENTAL_RESPONSE",
                  "function/environmental_response/metpo"),  # pressure tolerance
            Route("METPO:1007072", "FUNCTION", "FUNC_ENVIRONMENTAL_RESPONSE",
                  "function/environmental_response/metpo"),  # radiation tolerance
            Route("METPO:1007073", "FUNCTION", "FUNC_ENVIRONMENTAL_RESPONSE",
                  "function/environmental_response/metpo"),  # osmotic tolerance
            Route("METPO:1007074", "FUNCTION", "FUNC_ENVIRONMENTAL_RESPONSE",
                  "function/environmental_response/metpo"),  # metal tolerance
            Route("METPO:1007092", "FUNCTION", "FUNC_ENVIRONMENTAL_RESPONSE",
                  "function/environmental_response/metpo"),  # xerophilic phenotype
            # --- enzymatic activity (metabolism + enzyme biochemical tests) ---
            Route("METPO:1000630", "FUNCTION", "FUNC_ENZYMATIC_ACTIVITY",
                  "function/enzymatic_activity/metpo"),  # biological process (metabolism, N-cycle)
            Route("METPO:1000631", "FUNCTION", "FUNC_ENZYMATIC_ACTIVITY",
                  "function/enzymatic_activity/metpo"),  # trophic type
            Route("METPO:1005010", "FUNCTION", "FUNC_ENZYMATIC_ACTIVITY",
                  "function/enzymatic_activity/metpo"),  # indole test
            Route("METPO:1005013", "FUNCTION", "FUNC_ENZYMATIC_ACTIVITY",
                  "function/enzymatic_activity/metpo"),  # methyl red test
            Route("METPO:1005016", "FUNCTION", "FUNC_ENZYMATIC_ACTIVITY",
                  "function/enzymatic_activity/metpo"),  # Voges-Proskauer test
            Route("METPO:1007080", "FUNCTION", "FUNC_ENZYMATIC_ACTIVITY",
                  "function/enzymatic_activity/metpo"),  # catalase test
            Route("METPO:1007081", "FUNCTION", "FUNC_ENZYMATIC_ACTIVITY",
                  "function/enzymatic_activity/metpo"),  # oxidase test
            Route("METPO:1007082", "FUNCTION", "FUNC_ENZYMATIC_ACTIVITY",
                  "function/enzymatic_activity/metpo"),  # urease test
            Route("METPO:1007089", "FUNCTION", "FUNC_ENZYMATIC_ACTIVITY",
                  "function/enzymatic_activity/metpo"),  # coagulase activity
        ),
    ),
}


# ---------------------------------------------------------------------------
# OBO parser (shared shape with seed_psi_mod.py)
# ---------------------------------------------------------------------------


_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slugify(text: str) -> str:
    s = _SLUG_RE.sub("-", text.lower()).strip("-")
    return s[:80] or "term"


def parse_obo(text: str) -> list[dict]:
    """Return one dict per `[Term]` stanza. Repeated keys (synonym,
    xref, is_a, alt_id, relationship) become lists; single-valued keys
    are strings."""
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


# Text in the leading quotes; optional first [source] bracket; trailing
# OBO 1.4 qualifier blocks ({...}) or comments are ignored.
_DEF_RE = re.compile(r'^"((?:[^"\\]|\\.)*)"\s*(?:\[([^\]]*)\])?.*$')
_SYNONYM_RE = re.compile(
    r'^"((?:[^"\\]|\\.)*)"\s+(EXACT|BROAD|NARROW|RELATED)(?:\s+[^\s\[]+)?\s*\[.*\]?\s*$')
_XREF_RE = re.compile(r"^([A-Za-z][A-Za-z0-9._-]*):\s*(.*?)(?:\s*(?:!.*)?)$")
_CURIE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$")


def parse_def(raw: str) -> tuple[str, list[str]]:
    m = _DEF_RE.match(raw or "")
    if not m:
        return (raw or "", [])
    text = m.group(1).replace('\\"', '"')
    sources_raw = m.group(2) or ""
    sources = [s.strip() for s in sources_raw.split(",") if s.strip()]
    return (text, sources)


def normalise_source(token: str) -> str | None:
    """Map an OBO def-source token to a CURIE our schema accepts, or None
    to drop it. PubMed/DOI are canonicalised; other CURIE-shaped tokens
    (GO, PATO, OMP, ECOCORE, MicrO, …) pass through for grounding."""
    if not token or ":" not in token:
        return None
    prefix, _, local = token.partition(":")
    prefix, local = prefix.strip(), local.strip()
    if not local:
        return None
    low = prefix.lower()
    if low in {"pubmed", "pmid"}:
        return f"PMID:{local}"
    if low == "doi":
        return f"DOI:{local}"
    # Drop free-text / URL / internal-note sources.
    if low in {"url", "http", "https", "omo"}:
        return None
    curie = f"{prefix}:{local}"
    return curie if _CURIE_RE.match(curie) else None


def parse_synonym(raw: str) -> tuple[str, str] | None:
    m = _SYNONYM_RE.match(raw)
    if not m:
        return None
    text = m.group(1).replace('\\"', '"').strip()
    scope_map = {
        "EXACT": "EXACT_SYNONYM", "BROAD": "BROAD_SYNONYM",
        "NARROW": "NARROW_SYNONYM", "RELATED": "RELATED_SYNONYM",
    }
    return (text, scope_map.get(m.group(2), "RELATED_SYNONYM"))


def parse_xref(raw: str) -> str | None:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1]
    body = raw.split("!", 1)[0].strip()
    m = _XREF_RE.match(body)
    if not m:
        return None
    prefix, local = m.group(1).strip(), m.group(2).strip()
    if not local or local.startswith('"'):
        return None
    # Non-grounding lexical sources some OBO files attach as xrefs.
    if prefix in {"WordNet", "url", "URL"}:
        return None
    curie = f"{prefix}:{local}"
    return curie if _CURIE_RE.match(curie) else None


def parse_is_a(raw: str) -> str | None:
    head = raw.split("!", 1)[0].strip()
    return head if _CURIE_RE.match(head) else None


# ---------------------------------------------------------------------------
# Routing — transitive is_a descendants per configured root
# ---------------------------------------------------------------------------


def build_routing(entries: list[dict], src: Source) -> dict[str, Route]:
    """Return {term_id: Route} for every in-scope term. A term is in
    scope iff it is the root of, or an is_a descendant of, some route's
    root. When subtrees overlap, the earlier-declared route wins."""
    # child adjacency over same-ontology is_a edges
    children: dict[str, list[str]] = {}
    ids: set[str] = set()
    for e in entries:
        tid = (e.get("id") or "").strip()
        if not tid.startswith(src.id_prefix) or e.get("is_obsolete") == "true":
            continue
        ids.add(tid)
    for e in entries:
        tid = (e.get("id") or "").strip()
        if tid not in ids:
            continue
        for raw in e.get("is_a") or []:
            pid = parse_is_a(raw)
            if pid in ids:
                children.setdefault(pid, []).append(tid)

    assigned: dict[str, Route] = {}
    for route in src.routes:
        if route.root not in ids:
            print(f"  WARN: route root {route.root} not found in {src.obo_file}",
                  file=sys.stderr)
            continue
        # inclusive BFS
        stack = [route.root]
        seen = {route.root}
        while stack:
            node = stack.pop()
            assigned.setdefault(node, route)
            for c in children.get(node, ()):
                if c not in seen:
                    seen.add(c)
                    stack.append(c)
    return assigned


# ---------------------------------------------------------------------------
# YAML emission (hand-formatted; no PyYAML dep)
# ---------------------------------------------------------------------------


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def yaml_folded(text: str) -> list[str]:
    text = " ".join((text or "").split())
    if not text:
        return [">-", '  ""']
    return [">-", f"  {text}"]


def build_yaml(entry: dict, route: Route, src: Source, release: str) -> str | None:
    if entry.get("is_obsolete") == "true":
        return None
    term_id = (entry.get("id") or "").strip()
    if not term_id.startswith(src.id_prefix):
        return None
    name = (entry.get("name") or "").strip()
    if not name:
        return None

    def_text, def_sources = parse_def(entry.get("def", ""))
    definition = def_text or name

    parents, seen_p = [], set()
    for raw in entry.get("is_a") or []:
        pid = parse_is_a(raw)
        if pid and pid.startswith(src.id_prefix) and pid not in seen_p:
            seen_p.add(pid)
            parents.append(pid)

    xrefs, seen_x = [], set()
    for raw in entry.get("xref") or []:
        curie = parse_xref(raw)
        if curie and curie not in seen_x:
            seen_x.add(curie)
            xrefs.append(curie)
    for tok in def_sources:
        curie = normalise_source(tok)
        if curie and curie not in seen_x:
            seen_x.add(curie)
            xrefs.append(curie)

    synonyms, seen_s = [], set()
    for raw in entry.get("synonym") or []:
        pair = parse_synonym(raw)
        if pair and pair[0] != name and pair not in seen_s:
            seen_s.add(pair)
            synonyms.append(pair)

    lines: list[str] = []
    lines.append(f"identifier: {term_id}")
    lines.append(f"label: {yaml_escape(name)}")
    folded = yaml_folded(definition)
    lines.append(f"definition: {folded[0]}")
    lines.extend(folded[1:])
    lines.append(f"definition_source: {yaml_escape(release)}")
    lines.append(f"trait_axis: {route.axis}")
    lines.append(f"trait_category: {route.category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    if parents:
        lines.append("parent_traits:")
        lines.extend(f"  - {p}" for p in parents)
    if synonyms:
        lines.append("synonyms:")
        for text, scope in synonyms:
            lines.append(f"  - synonym_text: {yaml_escape(text)}")
            lines.append(f"    synonym_type: {scope}")
    if xrefs:
        lines.append("xrefs:")
        lines.extend(f"  - {x}" for x in xrefs)

    lines.append(f"license: {src.license}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def target_path(entry: dict, route: Route, src: Source) -> Path:
    local = entry.get("id", "").split(":", 1)[-1]
    slug = slugify(entry.get("name", "") or local)
    tag = src.id_prefix.rstrip(":").lower()
    return TRAITS_DIR / route.subdir / f"{slug}-{tag}{local}.yaml"


def read_release_stamp(path: Path, prefix: str) -> str:
    header = path.read_text(encoding="utf-8", errors="replace").splitlines()[:30]
    version = date = ""
    for line in header:
        if line.startswith("data-version:"):
            version = line.split(":", 1)[1].strip()
        elif line.startswith("date:"):
            date = line.split(":", 1)[1].strip()
    # Prefer an explicit YYYY-MM-DD found anywhere in the header block.
    m = re.search(r"\d{4}-\d{2}-\d{2}", "\n".join(header))
    iso = m.group(0) if m else ""
    stamp = prefix
    if iso:
        stamp += f" ({iso})"
    elif version:
        stamp += f" v{version}"
    return stamp


def seed_source(src: Source, args) -> dict:
    obo_path = RAW_DIR / src.obo_file
    if not obo_path.exists():
        print(f"[{src.key}] missing {obo_path}; run `just fetch-obo` first",
              file=sys.stderr)
        return {"missing": True}

    release = read_release_stamp(obo_path, src.release_prefix)
    entries = parse_obo(obo_path.read_text(encoding="utf-8", errors="replace"))
    routing = build_routing(entries, src)
    in_scope = sum(1 for e in entries
                   if (e.get("id") or "").strip() in routing
                   and e.get("is_obsolete") != "true")
    print(f"[{src.key}] {release}: {len(entries)} terms, {in_scope} in scope "
          f"across {len(src.routes)} route(s).")

    stats = {"written": 0, "skipped": 0, "planned": 0, "errors": 0, "by_dir": {}}
    processed = 0
    for entry in entries:
        tid = (entry.get("id") or "").strip()
        route = routing.get(tid)
        if route is None or entry.get("is_obsolete") == "true":
            continue
        if args.limit and processed >= args.limit:
            break
        try:
            yaml_body = build_yaml(entry, route, src, release)
        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            print(f"  error on {tid}: {exc}", file=sys.stderr)
            continue
        if yaml_body is None:
            continue
        path = target_path(entry, route, src)
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

    for d, n in sorted(stats["by_dir"].items()):
        print(f"    data/traits/{d:38s} {n}")
    if stats["errors"]:
        print(f"    errors: {stats['errors']}")
    if args.apply:
        print(f"    wrote {stats['written']}; skipped {stats['skipped']} existing.")
    else:
        print(f"    dry-run — would write {stats['planned']}; "
              f"{stats['skipped']} already exist.")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", choices=[*SOURCES, "all"],
                        help="which configured ontology to seed")
    parser.add_argument("--apply", action="store_true",
                        help="write YAMLs (default: dry-run)")
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing files")
    parser.add_argument("--limit", type=int, default=0,
                        help="cap records processed per source (0 = all)")
    args = parser.parse_args()

    keys = list(SOURCES) if args.source == "all" else [args.source]
    any_missing = False
    for k in keys:
        result = seed_source(SOURCES[k], args)
        any_missing = any_missing or result.get("missing", False)
    if not args.apply:
        print("\nRe-run with --apply to write.")
    return 2 if any_missing else 0


if __name__ == "__main__":
    sys.exit(main())
