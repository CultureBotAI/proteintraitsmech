#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from M-CSA — the Mechanism and
Catalytic Site Atlas maintained by the Thornton group at EBI.

Source: https://www.ebi.ac.uk/thornton-srv/m-csa/api/entries/  (CC-BY-4.0)

Each entry (1,003 as of the 2025 release) is one enzyme mechanism —
UniProt reference, EC classification, catalytic residues, cofactors,
and one or more mechanism records with per-step chemistry and literature.
This seeder emits one ProteinTraitRecord per entry under
`data/traits/structure/active_site/mcsa/` with:

    identifier         MCSA:<mcsa_id>
    label              enzyme_name
    definition         API `description` (Thornton's curated summary)
    trait_axis         STRUCTURE
    trait_category     STRUCT_ACTIVE_SITE
    xrefs              EC:<n>, CHEBI:<compound>, PDB:<pdb_id>,
                       CATH:<cath_id>, UniProtKB:<ref>
    canonical_examples UniProtKB reference entry
    evidence           PMIDs from the mechanism references
    license            CC-BY-4.0

Uses paginated JSON at 100 entries/page (default UniProt-style page
size). Stdlib-only. Idempotent, --apply/--force, --limit N.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_DIR = REPO_ROOT / "data" / "traits"
RAW_DIR = REPO_ROOT / "data" / "raw"

API_ROOT = "https://www.ebi.ac.uk/thornton-srv/m-csa/api/entries/"
USER_AGENT = "proteintraitsmech-mcsa-seeder/0.1"
LICENSE_TAG = "CC-BY-4.0"
CACHE_PATH = RAW_DIR / "mcsa.entries.jsonl"

MIN_INTERVAL_S = 0.4
_last_req = 0.0


def _throttle() -> None:
    global _last_req
    now = time.monotonic()
    dt = now - _last_req
    if dt < MIN_INTERVAL_S:
        time.sleep(MIN_INTERVAL_S - dt)
    _last_req = time.monotonic()


def _fetch_json(url: str) -> dict:
    for attempt in range(5):
        _throttle()
        req = urllib.request.Request(url, headers={
            "User-Agent": USER_AGENT, "Accept": "application/json"
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 502, 503, 504) and attempt < 4:
                time.sleep(min(30.0, 2 ** attempt))
                continue
            raise
    raise RuntimeError(f"repeated failure fetching {url}")


def fetch_all_entries() -> list[dict]:
    """Walk the paginated `/api/entries/` and return the list of
    entry summaries — then fetch the full JSON for each entry."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    summaries: list[dict] = []
    url = f"{API_ROOT}?format=json"
    while url:
        payload = _fetch_json(url)
        summaries.extend(payload.get("results") or [])
        url = payload.get("next") or ""
        print(f"  paged {len(summaries)}/{payload.get('count', '?')}",
              file=sys.stderr)
    return summaries


def load_cached() -> list[dict] | None:
    if not CACHE_PATH.exists():
        return None
    entries: list[dict] = []
    with CACHE_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries or None


def save_cache(entries: list[dict]) -> None:
    with CACHE_PATH.open("w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False))
            fh.write("\n")


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


_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _strip_control(text: str) -> str:
    """Remove ASCII control characters — a couple of M-CSA descriptions
    have stray `\\x01` bytes that YAML refuses to load — and HTML tags
    (`<i>`, `<sub>`, `<p>`…) that M-CSA descriptions carry."""
    return re.sub(r"</?[a-zA-Z][^>]*>", "", _CTRL_RE.sub("", text or ""))


def yaml_folded(indent: str, text: str) -> list[str]:
    text = " ".join(_strip_control(text or "").split())
    if not text:
        return [">-", f"{indent}  \"\""]
    return [">-", f"{indent}  {text}"]


def extract_xrefs(entry: dict) -> list[str]:
    xrefs: list[str] = []
    for ec in entry.get("all_ecs") or []:
        xrefs.append(f"EC:{ec}")
    for comp in ((entry.get("reaction") or {}).get("compounds") or []):
        cid = comp.get("chebi_id")
        if cid:
            xrefs.append(f"CHEBI:{cid}")
    seen_pdb: set[str] = set()
    seen_cath: set[str] = set()
    for res in entry.get("residues") or []:
        for chain in res.get("residue_chains") or []:
            pdb = chain.get("pdb_id")
            if pdb and pdb not in seen_pdb:
                seen_pdb.add(pdb)
                xrefs.append(f"PDB:{pdb}")
            cath = chain.get("domain_cath_id")
            if cath and cath not in seen_cath:
                seen_cath.add(cath)
                xrefs.append(f"CATH:{cath}")
    ref_up = entry.get("reference_uniprot_id") or ""
    for acc in (a.strip() for a in ref_up.split(",")):
        if acc and re.match(r"^[A-Z0-9]+([-][0-9]+)?$", acc):
            xrefs.append(f"UniProtKB:{acc}")
    # dedupe + drop malformed
    seen: set[str] = set()
    return [x for x in xrefs
            if _CURIE_RE.match(x) and not (x in seen or seen.add(x))]


def extract_pmids(entry: dict) -> list[str]:
    pmids: set[str] = set()
    for mech in ((entry.get("reaction") or {}).get("mechanisms") or []):
        for ref in mech.get("references") or []:
            pmid = ref.get("pubmed_id")
            if pmid:
                pmids.add(str(pmid))
    return sorted(pmids)


def canonical_examples(entry: dict) -> list[dict]:
    """M-CSA sometimes returns a comma-separated list of UniProt
    accessions on hetero-oligomer enzymes. Emit one CanonicalExample
    per accession; the first is flagged in the note as the reference
    chain."""
    raw = entry.get("reference_uniprot_id") or ""
    accs = [a.strip() for a in raw.split(",") if a.strip()]
    if not accs:
        return []
    out: list[dict] = []
    for i, acc in enumerate(accs):
        if not re.match(r"^[A-Z0-9]+([-][0-9]+)?$", acc):
            continue
        role = "reference chain" if i == 0 else f"partner chain {i + 1}"
        out.append({
            "protein_id": f"UniProtKB:{acc}",
            "protein_label": entry.get("enzyme_name") or "reference enzyme",
            "note": (f"M-CSA reference entry for enzyme #{entry.get('mcsa_id')} "
                     f"({entry.get('enzyme_name', '')}) — {role}"),
            "source": "CURATOR",
        })
    return out


def build_yaml(entry: dict, release: str) -> str | None:
    mcsa_id = entry.get("mcsa_id")
    if mcsa_id is None:
        return None
    name = entry.get("enzyme_name") or f"M-CSA entry {mcsa_id}"
    description = entry.get("description") or name

    lines: list[str] = []
    lines.append(f"identifier: MCSA:{mcsa_id}")
    lines.append(f"label: {yaml_escape(name)}")
    folded = yaml_folded("", description)
    lines.append(f"definition: {folded[0]}")
    lines.extend(folded[1:])
    lines.append(f"definition_source: {yaml_escape(release)}")
    lines.append("trait_axis: STRUCTURE")
    lines.append("trait_category: STRUCT_ACTIVE_SITE")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    xrefs = extract_xrefs(entry)
    if xrefs:
        lines.append("xrefs:")
        for x in xrefs:
            lines.append(f"  - {x}")

    exs = canonical_examples(entry)
    if exs:
        lines.append("canonical_examples:")
        for ex in exs:
            lines.append(f"  - protein_id: {ex['protein_id']}")
            lines.append(f"    protein_label: {yaml_escape(ex['protein_label'])}")
            lines.append(f"    note: {yaml_escape(ex['note'])}")
            lines.append(f"    source: {ex['source']}")

    pmids = extract_pmids(entry)
    if pmids:
        lines.append("evidence:")
        for pmid in pmids:
            lines.append(f"  - reference: PMID:{pmid}")
            lines.append(f"    notes: {yaml_escape('M-CSA mechanism reference')}")

    lines.append(f"license: {LICENSE_TAG}")
    return "\n".join(lines) + "\n"


def target_path(entry: dict) -> Path:
    mcsa_id = entry.get("mcsa_id")
    slug = slugify(entry.get("enzyme_name") or f"mcsa-{mcsa_id}")
    return TRAITS_DIR / "structure" / "active_site" / "mcsa" / f"{slug}-mcsa{mcsa_id}.yaml"


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
        print("Fetching M-CSA entries from the REST API…")
        entries = fetch_all_entries()
        save_cache(entries)
        print(f"Cached {len(entries)} entries to "
              f"{CACHE_PATH.relative_to(REPO_ROOT)}.")

    release = "M-CSA (Thornton lab, EBI; fetched via REST API)"
    stats = {"written": 0, "skipped": 0, "planned": 0, "errors": 0}
    processed = 0
    for entry in entries:
        if args.limit and processed >= args.limit:
            break
        try:
            yaml_body = build_yaml(entry, release)
        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            print(f"error on mcsa_id={entry.get('mcsa_id')}: {exc}",
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
