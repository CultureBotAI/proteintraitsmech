#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from DisProt — the curated database
of intrinsically disordered proteins (Tosatto lab, U. Padova).

Source: https://disprot.org/api/search  (CC-BY-4.0, release 9.8+)

Each DisProt entry is one experimentally characterised IDP, carrying a
list of curator-annotated `regions` with start/end coordinates,
IDPO-ontology term IDs, and evidence references. This seeder emits one
ProteinTraitRecord per entry under `data/traits/sequence/disorder/`
with the protein as a canonical_example. The individual regions are
projected into that example's `features` list (SequenceFeatureAnnotation)
so the docs browser can colour them the same way UniProt FT features
are coloured.

Emitted record shape:
    identifier         DisProt:<disprot_id>
    label              "disorder profile — <protein name>"
    definition         Auto-composed from region terms + statement
    trait_axis         SEQUENCE
    trait_category     SEQ_DISORDER
    xrefs              UniProtKB:<acc>, unique IDPO terms across regions
    canonical_examples 1 entry (the protein), sequence + features
    evidence           PMIDs from region references
    license            CC-BY-4.0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_DIR = REPO_ROOT / "data" / "traits"
RAW_DIR = REPO_ROOT / "data" / "raw"

API_URL = ("https://disprot.org/api/search"
           "?release=current&size=20000"
           "&show_ambiguous=true&show_obsolete=false")
USER_AGENT = "proteintraitsmech-disprot-seeder/0.1"
LICENSE_TAG = "CC-BY-4.0"
CACHE_PATH = RAW_DIR / "disprot.entries.json"


def fetch_all() -> list[dict]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(API_URL, headers={
        "User-Agent": USER_AGENT, "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return list(payload.get("data") or [])


def load_cached() -> list[dict] | None:
    if not CACHE_PATH.exists():
        return None
    with CACHE_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_cache(entries: list[dict]) -> None:
    with CACHE_PATH.open("w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False)


# ---------------------------------------------------------------------------
# YAML emission
# ---------------------------------------------------------------------------


_SLUG_RE = re.compile(r"[^A-Za-z0-9]+")
_CURIE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$")


def slugify(text: str) -> str:
    s = _SLUG_RE.sub("-", (text or "").lower()).strip("-")
    return s[:80] or "entry"


def yaml_escape(text: str) -> str:
    if text is None or text == "":
        return '""'
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if (any(c in unsafe for c in text) or text[0] in "-?"
            or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def yaml_folded(indent: str, text: str) -> list[str]:
    text = " ".join((text or "").split())
    if not text:
        return [">-", f"{indent}  \"\""]
    return [">-", f"{indent}  {text}"]


def regions_to_features(regions: list[dict], seq_len: int) -> list[dict]:
    """Convert DisProt regions into SequenceFeatureAnnotation shape."""
    feats: list[dict] = []
    for r in regions or []:
        start = r.get("start")
        end = r.get("end")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        if start < 1 or end < start or start > seq_len:
            continue
        end = min(end, seq_len)
        term_id = r.get("term_id") or ""
        term_name = r.get("term_name") or ""
        namespace = r.get("term_namespace") or ""
        feat = {
            "start": start,
            "end": end,
            "feature_type": "DISORDER",
            "trait_axis": "SEQUENCE",
            "trait_category": "SEQ_DISORDER",
        }
        note_parts = [term_name] if term_name else []
        if namespace:
            note_parts.append(f"[{namespace}]")
        if term_id:
            note_parts.append(f"({term_id})")
        note = " ".join(note_parts).strip()
        if note:
            feat["note"] = note
        feats.append(feat)
    return feats


def extract_pmids(regions: list[dict]) -> list[str]:
    pmids: set[str] = set()
    for r in regions or []:
        ref = r.get("reference_id") or ""
        source = (r.get("reference_source") or "").lower()
        if not ref:
            continue
        if source == "pubmed" or (ref.isdigit() and len(ref) >= 5):
            pmids.add(ref.strip())
    return sorted(pmids)


def extract_ontology_terms(regions: list[dict]) -> list[str]:
    curies: set[str] = set()
    for r in regions or []:
        term = r.get("term_id") or ""
        if term and _CURIE_RE.match(term):
            curies.add(term)
    return sorted(curies)


def build_yaml(entry: dict, release: str) -> str | None:
    disprot_id = entry.get("disprot_id")
    if not disprot_id:
        return None
    acc = entry.get("acc") or ""
    name = entry.get("name") or f"DisProt entry {disprot_id}"
    seq = entry.get("sequence") or ""
    seq_len = int(entry.get("length") or len(seq))
    organism = entry.get("organism") or ""
    taxon_id = entry.get("ncbi_taxon_id")
    regions = entry.get("regions") or []
    disorder_content = entry.get("disorder_content")

    ident = f"DisProt:{disprot_id}"
    label = f"intrinsic disorder profile — {name}"
    definition_bits = [
        f"DisProt-curated intrinsically disordered profile for "
        f"UniProtKB:{acc} ({name})."
    ]
    if organism:
        definition_bits.append(f"Organism: {organism}.")
    if isinstance(disorder_content, (int, float)):
        definition_bits.append(f"Disorder content: {disorder_content:.2f}.")
    if regions:
        definition_bits.append(f"{len(regions)} curator-annotated region(s).")
    definition = " ".join(definition_bits)

    xrefs: list[str] = []
    if acc:
        xrefs.append(f"UniProtKB:{acc}")
    xrefs.extend(extract_ontology_terms(regions))
    # dedupe
    seen: set[str] = set()
    xrefs = [x for x in xrefs
             if _CURIE_RE.match(x) and not (x in seen or seen.add(x))]

    lines: list[str] = []
    lines.append(f"identifier: {ident}")
    lines.append(f"label: {yaml_escape(label)}")
    folded = yaml_folded("", definition)
    lines.append(f"definition: {folded[0]}")
    lines.extend(folded[1:])
    lines.append(f"definition_source: {yaml_escape(release)}")
    lines.append("trait_axis: SEQUENCE")
    lines.append("trait_category: SEQ_DISORDER")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    if xrefs:
        lines.append("xrefs:")
        for x in xrefs:
            lines.append(f"  - {x}")

    if acc:
        lines.append("canonical_examples:")
        lines.append(f"  - protein_id: UniProtKB:{acc}")
        lines.append(f"    protein_label: {yaml_escape(name)}")
        if taxon_id:
            lines.append(f"    taxon_id: NCBITaxon:{taxon_id}")
        if organism:
            lines.append(f"    taxon_label: {yaml_escape(organism)}")
        if seq_len:
            lines.append(f"    sequence_length: {seq_len}")
        lines.append(f"    note: {yaml_escape('DisProt entry ' + disprot_id)}")
        lines.append("    source: CURATOR")
        if seq and re.match(r"^[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+$", seq):
            lines.append(f"    sequence: {seq}")
        feats = regions_to_features(regions, len(seq) if seq else seq_len)
        if feats:
            lines.append("    features:")
            for f in feats:
                lines.append(f"      - start: {f['start']}")
                lines.append(f"        end: {f['end']}")
                lines.append(f"        feature_type: {f['feature_type']}")
                lines.append(f"        trait_axis: {f['trait_axis']}")
                lines.append(f"        trait_category: {f['trait_category']}")
                if f.get("note"):
                    lines.append(f"        note: {yaml_escape(f['note'])}")

    pmids = extract_pmids(regions)
    if pmids:
        lines.append("evidence:")
        for pmid in pmids[:20]:
            lines.append(f"  - reference: PMID:{pmid}")
            lines.append(f"    notes: {yaml_escape('DisProt region evidence')}")

    lines.append(f"license: {LICENSE_TAG}")
    return "\n".join(lines) + "\n"


def target_path(entry: dict) -> Path:
    disprot_id = entry.get("disprot_id") or "unknown"
    name = entry.get("name") or disprot_id
    slug = slugify(name)
    return TRAITS_DIR / "sequence" / "disorder" / f"{slug}-{disprot_id.lower()}.yaml"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="write YAMLs (default: dry-run)")
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing files")
    parser.add_argument("--refetch", action="store_true",
                        help="ignore the local cache and re-hit the API")
    parser.add_argument("--limit", type=int, default=0,
                        help="cap number of records processed (0 = all)")
    args = parser.parse_args()

    entries = None if args.refetch else load_cached()
    if entries:
        print(f"Loaded {len(entries)} entries from cache "
              f"({CACHE_PATH.relative_to(REPO_ROOT)}).")
    else:
        print("Fetching DisProt search page…")
        entries = fetch_all()
        save_cache(entries)
        print(f"Cached {len(entries)} entries to "
              f"{CACHE_PATH.relative_to(REPO_ROOT)}.")

    release = "DisProt (Tosatto lab, U. Padova; fetched via REST API)"
    stats = {"written": 0, "skipped": 0, "planned": 0, "errors": 0}
    processed = 0
    for entry in entries:
        if args.limit and processed >= args.limit:
            break
        try:
            yaml_body = build_yaml(entry, release)
        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            print(f"error on disprot_id={entry.get('disprot_id')}: {exc}",
                  file=sys.stderr)
            continue
        if yaml_body is None:
            continue
        path = target_path(entry)
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
    if args.apply:
        print(f"Wrote {stats['written']} file(s); skipped {stats['skipped']} "
              f"existing; {stats['errors']} error(s).")
    else:
        print(f"Dry-run — would write {stats['planned']} file(s); "
              f"{stats['skipped']} already exist.")
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
