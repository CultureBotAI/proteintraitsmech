#!/usr/bin/env python3
"""Seed hierarchical-orthologous-group traits from OMA → FUNCTION /
FUNC_ORTHOLOG_GROUP.

An OMA HOG (hierarchical orthologous group) is a set of orthologues at a
taxonomic level — a reusable, class-level conserved-function trait, like a COG or
an OrthoDB OG. This complements the OrthoDB seed (both populate
FUNC_ORTHOLOG_GROUP; cross-source dedup is a downstream merge-within-axis concern,
never a merge here). OMA has ~1.1M root HOGs, so we **scope by level** (`--level`,
default `root` = the universal, most-conserved groups) and **cap** (`--limit`).

Source is the OMA REST API (`/api/hog/?level=<level>`), which returns HOGs with a
functional `description` — paginated. First run fetches + caches each page to
data/raw/oma/ (gitignored); re-runs replay the cache. No bulk download needed.

Licence: CC-BY 4.0 (OMA). Idempotent; dry-run unless --apply. Stdlib-only
(urllib). Requires network on the first run for uncached pages.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE = REPO_ROOT / "data" / "raw" / "oma"
OUT_DIR = REPO_ROOT / "data" / "traits" / "function" / "ortholog_group" / "oma"
LICENSE = "CC-BY 4.0 (OMA)"
API = "https://omabrowser.org/api/hog/"
_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")


def slug(t): return (_SLUG_RE.sub("-", (t or "").lower()).strip("-")[:70]) or "hog"


def yaml_escape(text: str) -> str:
    if not text:
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[:1] in ("-", "?")
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}
            or re.fullmatch(r"-?\d+(?:\.\d+)?", text)):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def folded(text):
    text = " ".join((text or "").split())
    return [">-", f"  {text}"] if text else [">-", '  ""']


def fetch_page(level, page, per_page, sleep):
    """Cached GET of one HOG page; returns the parsed list (or [])."""
    cf = CACHE / f"hog_{slug(level)}_{page}.json"
    if cf.exists():
        try:
            return json.loads(cf.read_text())
        except ValueError:
            pass
    url = f"{API}?level={level}&per_page={per_page}&page={page}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (ProteinTraitsMech seeder; +https://github.com/CultureBotAI/proteintraitsmech)"})
    data = None
    for attempt in range(5):                 # retry with backoff on 429 / errors
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                back = 5 * (attempt + 1)
                print(f"  429 page {page}; backoff {back}s", file=sys.stderr)
                time.sleep(back)
                continue
            print(f"  http {e.code} page {page}", file=sys.stderr)
            return []
        except Exception as e:  # noqa: BLE001
            print(f"  fetch err page {page}: {e}", file=sys.stderr)
            time.sleep(3)
    if data is None:
        return []
    CACHE.mkdir(parents=True, exist_ok=True)
    cf.write_text(json.dumps(data))
    if sleep:
        time.sleep(sleep)
    return data


def level_rid(level): return f"proteintraitsmech:OMA_LEVEL_{slug(level)}"


def build_level(level):
    lines = [f"identifier: {level_rid(level)}",
             f"label: {yaml_escape(f'{level} hierarchical orthologous groups (OMA)')}"]
    f = folded(f"OMA hierarchical orthologous groups defined at the {level} "
               f"taxonomic level.")
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: OMA", "trait_axis: FUNCTION",
              "trait_category: FUNC_ORTHOLOG_GROUP", "term_kind: CLASS",
              "mapping_status: SEEDED", f"license: {yaml_escape(LICENSE)}"]
    return "\n".join(lines) + "\n"


# OMA descriptions may append a source-protein provenance tag, e.g.
# "Uncharacterized protein MJ1511 {UniProtKB/Swiss-Prot Q58906}". Extract the
# UniProt accession as an xref and strip the {…} tag from the label.
_UNP = re.compile(r"[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2}")
_TAG = re.compile(r"\s*\{[^}]*\}")
# Non-functional / boilerplate descriptions to skip (quality over quantity —
# OrthoDB covers the exhaustive orthology; OMA contributes its well-named HOGs).
_NOFUNC = re.compile(
    r"hypothetical|uncharacteri[sz]ed|unknown function|domain of unknown|"
    r"gene prediction|automated computational|genemarks|putative protein|"
    r"predicted protein", re.I)


def clean_desc(desc: str):
    """(clean_label, uniprot_acc|None) from a raw OMA description."""
    desc = (desc or "").strip()
    acc = None
    tm = re.search(r"\{UniProtKB[^}]*\}", desc)
    if tm:
        am = _UNP.search(tm.group(0))
        if am:
            acc = am.group(0)
    return _TAG.sub("", desc).strip(), acc


def is_uncharacterized(label: str) -> bool:
    """True if the label carries no function (empty or hypothetical/boilerplate)."""
    return not (label or "").strip() or bool(_NOFUNC.search(label))


def build_hog(hog):
    hid = hog["hog_id"]                       # e.g. HOG:F0000001
    ident = "OMA:" + hid.split(":", 1)[-1]    # OMA:F0000001 (canonical F-id)
    label, acc = clean_desc(hog.get("description"))
    label = label or hid
    level = hog.get("level", "root")
    lines = [f"identifier: {ident}", f"label: {yaml_escape(label)}"]
    f = folded(f"{label} — an OMA hierarchical orthologous group at the "
               f"{level} level.")
    lines += [f"definition: {f[0]}", *f[1:]]
    lines += ["definition_source: OMA", "trait_axis: FUNCTION",
              "trait_category: FUNC_ORTHOLOG_GROUP", "term_kind: CLASS",
              "mapping_status: SEEDED",
              "parent_traits:", f"  - {level_rid(level)}",
              "trait_relations:", "  - predicate: biolink:member_of",
              f"    object: {level_rid(level)}", "    relation_source: OMA level"]
    if acc:
        lines += ["xrefs:", f"  - UniProtKB:{acc}"]
    lines.append(f"license: {yaml_escape(LICENSE)}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--level", default="root", help="OMA taxonomic level (default root)")
    ap.add_argument("--limit", type=int, default=10000, help="cap HOG records")
    ap.add_argument("--per-page", type=int, default=500)
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    written = skipped = hogs = 0

    def emit(fname, text):
        nonlocal written, skipped
        path = OUT_DIR / fname
        if path.exists() and not args.force:
            skipped += 1
            return
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1

    emit(f"oma-level-{slug(args.level)}.yaml", build_level(args.level))

    page = 1
    while hogs < args.limit:
        batch = fetch_page(args.level, page, args.per_page, args.sleep)
        if not batch:
            break
        for hog in batch:
            if hogs >= args.limit:
                break
            label, _ = clean_desc(hog.get("description"))
            if is_uncharacterized(label):     # prefer functionally-named HOGs
                continue
            hogs += 1
            emit(f"{slug(label)}-{slug(hog['hog_id'])}.yaml", build_hog(hog))
        page += 1

    print(f"OMA: {hogs} named HOGs at level '{args.level}' (capped at {args.limit}) "
          f"+ 1 level node → FUNC_ORTHOLOG_GROUP.")
    if args.apply:
        print(f"Wrote {written}; skipped {skipped} existing.")
    else:
        print(f"Dry-run — cached pages; would write {hogs + 1 - skipped}; {skipped} exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
