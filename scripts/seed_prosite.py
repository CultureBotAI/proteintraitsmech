#!/usr/bin/env python3
"""Seed ProteinTraitRecord YAMLs from PROSITE patterns / profiles and ProRules.

Source: ftp://ftp.expasy.org/databases/prosite/

Requires prior download via `just fetch-prosite` (or manual curl of
prosite.dat and prorule.dat into data/raw/).

Emits YAMLs to:
  data/traits/sequence/pattern/<slug>.yaml   — PROSITE PATTERN entries (non-PTM)
  data/traits/sequence/ptm_site/<slug>.yaml  — PROSITE PATTERN entries flagged as a PTM
  data/traits/sequence/profile/<slug>.yaml   — PROSITE MATRIX (profile) entries
  data/traits/sequence/domain/prosite/<slug>.yaml — ProRule entries with DC=Domain (SEQ_DOMAIN)
  data/traits/sequence/prorule/<slug>.yaml   — ProRule entries with DC=Site (non-Domain)

Idempotent: skips existing YAMLs by default; pass --force to overwrite.
Dry-run by default; pass --apply to write. Stdlib-only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
TRAITS_DIR = REPO_ROOT / "data" / "traits"

PROSITE_DAT = RAW_DIR / "prosite.dat"
PRORULE_DAT = RAW_DIR / "prorule.dat"
RELEASE_TXT = RAW_DIR / "ps_reldt.txt"

# PTM keyword → (schema category, subdir). Used by both the PROSITE
# PATTERN classifier (matches on `/SITE=N,label`) and the ProRule
# classifier (matches on the Names: field). Everything not matched here
# stays as SEQ_MOTIF (disulfide is captured by the STRUCT_DISULFIDE
# pipeline separately; active-site / metal / heme / substrate_binding /
# pyridoxal_phosphate / thiolester / retinal / primer_binding stay as
# motifs unless a curator promotes them).
PTM_KEYWORD_ROUTES: tuple[tuple[str, tuple[str, str]], ...] = (
    # SEQ_GLYCOSYLATION_SITE
    ("glycosylation",         ("SEQ_GLYCOSYLATION_SITE", "sequence/glycosylation")),
    ("carbohydrate",          ("SEQ_GLYCOSYLATION_SITE", "sequence/glycosylation")),
    # SEQ_LIPIDATION_SITE
    ("myristylation",         ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    ("myristoylation",        ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    ("palmitoylation",        ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    ("prenylation",           ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    ("farnesylation",         ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    ("geranyl-geranylation",  ("SEQ_LIPIDATION_SITE",    "sequence/lipidation")),
    # SEQ_CROSSLINK_SITE  (isopeptide-linked / covalent branches, not disulfides)
    ("ubiquitination",        ("SEQ_CROSSLINK_SITE",     "sequence/crosslink")),
    ("sumoylation",           ("SEQ_CROSSLINK_SITE",     "sequence/crosslink")),
    ("cross-linking",         ("SEQ_CROSSLINK_SITE",     "sequence/crosslink")),
    # SEQ_MODIFIED_RESIDUE (fallback bucket for MOD_RES-style modifications)
    ("phosphorylation",       ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("amidation",             ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("methylation",           ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("acetylation",           ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("hydroxylation",         ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("sulfation",             ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("sulfonation",           ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("uridylation",           ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("adp_ribosylation",      ("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
    ("gamma_carboxyglutamate",("SEQ_MODIFIED_RESIDUE",   "sequence/modified_residue")),
)


def classify_ptm(text: str) -> tuple[str, str] | None:
    """Return (category, subdir) if `text` matches a known PTM keyword,
    else None. Case-insensitive, substring match — cheap and stable
    because the keyword vocabulary is a small closed set."""
    lower = text.lower()
    for kw, route in PTM_KEYWORD_ROUTES:
        if kw in lower:
            return route
    return None

_SAFE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    return _SAFE.sub("-", text.lower()).strip("-")


def read_release() -> str:
    if RELEASE_TXT.exists():
        return RELEASE_TXT.read_text().strip()
    return "PROSITE (release unknown)"


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_prosite_dat(text: str) -> list[dict]:
    """Split prosite.dat on `//` and pull the fields we care about per entry."""
    entries: list[dict] = []
    for raw in text.split("\n//\n"):
        # First block is the copyright/preamble (all CC lines, no ID).
        if "\nID   " not in ("\n" + raw):
            continue
        entry: dict = {
            "pattern_parts": [],
            "site_labels": [],
            "prorule_refs": [],
            "doc_refs": [],
        }
        for line in raw.splitlines():
            if line.startswith("ID   "):
                body = line[5:].rstrip(".").strip()
                parts = [p.strip() for p in body.split(";", 1)]
                entry["id"] = parts[0]
                entry["type"] = parts[1] if len(parts) > 1 else ""
            elif line.startswith("AC   "):
                entry["ac"] = line[5:].rstrip(";").strip()
            elif line.startswith("DE   "):
                entry["de"] = line[5:].rstrip(".").strip()
            elif line.startswith("PA   "):
                entry["pattern_parts"].append(line[5:].strip())
            elif line.startswith("CC   "):
                cc = line[5:].strip()
                if "/SITE=" in cc:
                    site = cc.split("/SITE=", 1)[1].split(";", 1)[0]
                    if "," in site:
                        entry["site_labels"].append(site.split(",", 1)[1].strip())
            elif line.startswith("PR   "):
                # A single PR line can list several ProRule accessions
                # separated by `;`, e.g. `PR   PRU00434; PRU01700;`.
                for pr in line[5:].split(";"):
                    pr = pr.strip()
                    if pr:
                        entry["prorule_refs"].append(pr)
            elif line.startswith("DO   "):
                # Same story for DO — one line, possibly several PDOCs.
                for do in line[5:].split(";"):
                    do = do.strip()
                    if do:
                        entry["doc_refs"].append(do)
        if entry.get("ac") and entry.get("id"):
            entry["pattern"] = "".join(entry.pop("pattern_parts"))
            entries.append(entry)
    return entries


def parse_prorule_dat(text: str) -> list[dict]:
    """Split prorule.dat on `//` and pull AC / DC / TR / Names / Function."""
    entries: list[dict] = []
    for raw in text.split("\n//\n"):
        if "\nAC   " not in ("\n" + raw):
            continue
        entry: dict = {"trigger_ps": []}
        lines = raw.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("AC   "):
                entry["ac"] = line[5:].rstrip(";").strip()
            elif line.startswith("DC   "):
                entry["dc"] = line[5:].rstrip(";").strip()
            elif line.startswith("TR   "):
                parts = [p.strip() for p in line[5:].split(";")]
                # TR   PROSITE; PS50844; AFP_LIKE; 1; level=0
                if len(parts) >= 2 and parts[0] == "PROSITE":
                    entry["trigger_ps"].append(parts[1])
            elif line.startswith("Names:"):
                entry["names"] = line[len("Names:"):].strip()
            elif line.startswith("Function:"):
                fn = [line[len("Function:"):].strip()]
                for nxt in lines[i + 1:]:
                    if nxt.startswith(" "):
                        fn.append(nxt.strip())
                    else:
                        break
                entry["function"] = " ".join(f for f in fn if f)
        if entry.get("ac"):
            entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# Categorisation
# ---------------------------------------------------------------------------


def categorise_prosite(entry: dict) -> tuple[str, str, str]:
    """Return (trait_axis, trait_category, subdir_relative_to_TRAITS_DIR)."""
    if entry["type"] == "PATTERN":
        # `/SITE=N,label` labels can carry a PTM keyword — route to the
        # specific PTM subtype. Multiple labels: first PTM match wins;
        # if none match, treat as a generic motif.
        for lbl in entry.get("site_labels", []):
            ptm = classify_ptm(lbl)
            if ptm is not None:
                cat, subdir = ptm
                return ("SEQUENCE", cat, subdir)
        return ("SEQUENCE", "SEQ_MOTIF", "sequence/pattern")
    if entry["type"] == "MATRIX":
        return ("SEQUENCE", "SEQ_MOTIF", "sequence/profile")
    # Fallback — shouldn't happen given the PROSITE distribution.
    return ("SEQUENCE", "SEQ_MOTIF", "sequence/pattern")


def categorise_prorule(entry: dict) -> tuple[str, str, str]:
    if entry.get("dc") == "Domain":
        # ProRule domain profiles are sequence signatures — the trait axis
        # follows the representation (sequence space), so SEQ_DOMAIN, not
        # STRUCT_DOMAIN (which is reserved for structure-derived domains).
        return ("SEQUENCE", "SEQ_DOMAIN", "sequence/domain/prosite")
    # DC=Site (or other) — check the Names: field for a PTM keyword. If
    # matched, the rule targets that specific modification; otherwise it
    # is a generic motif rule.
    ptm = classify_ptm(entry.get("names", ""))
    if ptm is not None:
        cat, subdir = ptm
        return ("SEQUENCE", cat, subdir)
    return ("SEQUENCE", "SEQ_MOTIF", "sequence/prorule")


# ---------------------------------------------------------------------------
# YAML emission (hand-formatted; no PyYAML dependency)
# ---------------------------------------------------------------------------


def yaml_escape(text: str) -> str:
    """Emit a value safe for a single-line YAML scalar. Fallback to double-quoted."""
    if text is None:
        return '""'
    # Multi-line? Use folded scalar handled by caller. Single line here.
    if not text:
        return '""'
    # Characters that force quoting under YAML 1.1.
    unsafe = set(': #{}[],&*!|>%@`\\"\'')
    if any(c in unsafe for c in text) or text[0] in "-?" or text.lower() in {"null", "true", "false", "yes", "no", "on", "off"}:
        # Double-quote and escape.
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def yaml_folded(indent: str, text: str) -> list[str]:
    """Emit a folded scalar (>-) with a single continuation line."""
    lines = [">-"]
    # Collapse whitespace so long PROSITE definitions stay tidy.
    for chunk in text.strip().split("\n"):
        chunk = " ".join(chunk.split())
        if chunk:
            lines.append(f"{indent}  {chunk}")
    return lines


def build_prosite_yaml(entry: dict, release: str) -> str:
    axis, category, _ = categorise_prosite(entry)
    identifier = f"PROSITE:{entry['ac']}"
    de = entry.get("de") or entry["id"]
    label = de
    definition = de

    lines: list[str] = []
    lines.append(f"identifier: {identifier}")
    lines.append(f"label: {yaml_escape(label)}")
    lines.append("definition: " + yaml_folded("", definition)[0])
    for cont in yaml_folded("", definition)[1:]:
        lines.append(cont)
    lines.append(f"definition_source: {yaml_escape(release)}")
    lines.append(f"trait_axis: {axis}")
    lines.append(f"trait_category: {category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    # PDOC documentation entries are the family-level parents for one or
    # more PROSITE signatures (multiple ACs can share a single PDOC —
    # e.g. PS00796 + PS01180 both point at PDOC00633 "14-3-3 proteins").
    # They are the closest thing to a parent class in PROSITE, so we
    # promote them from `xrefs` to `parent_traits`.
    parent_traits = [f"PROSITE:{do}" for do in entry.get("doc_refs", [])]
    if parent_traits:
        lines.append("parent_traits:")
        for p in parent_traits:
            lines.append(f"  - {p}")
        # A signature is a MEMBER of its PDOC documentation group, not a subclass.
        lines.append("trait_relations:")
        for p in parent_traits:
            lines += ["  - predicate: biolink:member_of",
                      f"    object: {p}",
                      "    relation_source: PROSITE documentation"]

    if entry.get("pattern") and entry["type"] == "PATTERN":
        lines.append(f"sequence_pattern: {yaml_escape(entry['pattern'])}")

    xrefs: list[str] = [f"PROSITE:{entry['id']}"]  # ID as a searchable alias
    xrefs.extend(f"PROSITE:{pr}" for pr in entry.get("prorule_refs", []))
    # dedupe, preserve order, drop the self-referential AC form (already in identifier)
    seen: set[str] = set()
    out_xrefs: list[str] = []
    for x in xrefs:
        if x in seen or x == identifier:
            continue
        seen.add(x)
        out_xrefs.append(x)
    if out_xrefs:
        lines.append("xrefs:")
        for x in out_xrefs:
            lines.append(f"  - {x}")

    return "\n".join(lines) + "\n"


def build_prorule_yaml(entry: dict, release: str) -> str:
    axis, category, _ = categorise_prorule(entry)
    identifier = f"PROSITE:{entry['ac']}"
    label = entry.get("names") or entry["ac"]
    function = entry.get("function") or ""
    if function.lower() in {"", "undefined", "undefined."}:
        definition = label
    else:
        definition = function

    lines: list[str] = []
    lines.append(f"identifier: {identifier}")
    lines.append(f"label: {yaml_escape(label)}")
    lines.append("definition: " + yaml_folded("", definition)[0])
    for cont in yaml_folded("", definition)[1:]:
        lines.append(cont)
    lines.append(f"definition_source: {yaml_escape(release + ' (ProRule)')}")
    lines.append(f"trait_axis: {axis}")
    lines.append(f"trait_category: {category}")
    lines.append("term_kind: CLASS")
    lines.append("mapping_status: SEEDED")

    xrefs: list[str] = [f"PROSITE:{ps}" for ps in entry.get("trigger_ps", [])]
    if xrefs:
        lines.append("xrefs:")
        for x in xrefs:
            lines.append(f"  - {x}")

    lines.append("license: CC BY-NC-ND 4.0 (SIB)")   # PROSITE terms (tighter than CC0)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Filename resolution
# ---------------------------------------------------------------------------


def prosite_target(entry: dict) -> Path:
    _, _, subdir = categorise_prosite(entry)
    slug = slugify(entry["id"]) or entry["ac"].lower()
    return TRAITS_DIR / subdir / f"{slug}.yaml"


def prorule_target(entry: dict) -> Path:
    _, _, subdir = categorise_prorule(entry)
    base = entry.get("names") or entry["ac"]
    slug = slugify(base) or entry["ac"].lower()
    # Every ProRule slug gets its AC as a suffix — Names can collide (many
    # ProRules use short generic labels like "Zinc finger"), and prefixing
    # keeps the file discoverable by AC too.
    return TRAITS_DIR / subdir / f"{slug}-{entry['ac'].lower()}.yaml"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def process(entries, target_fn, build_fn, release, apply_, force, stats):
    for entry in entries:
        try:
            path = target_fn(entry)
        except Exception as exc:
            stats["errors"] += 1
            print(f"  [ERROR         ] {entry.get('ac', '?')}: {exc}", file=sys.stderr)
            continue

        cat_key = str(path.parent.relative_to(TRAITS_DIR))
        stats["by_dir"][cat_key] = stats["by_dir"].get(cat_key, 0) + 1

        if path.exists() and not force:
            stats["skipped"] += 1
            continue

        stats["planned"] += 1
        if apply_:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(build_fn(entry, release))
            stats["written"] += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write YAMLs (default: dry-run)")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="cap entries per source (per source, in file order) — useful for smoke tests",
    )
    parser.add_argument(
        "--only",
        choices=("prosite", "prorule"),
        default=None,
        help="process only one source",
    )
    args = parser.parse_args()

    for src in (PROSITE_DAT, PRORULE_DAT):
        if not src.exists():
            print(
                f"ERROR: {src.relative_to(REPO_ROOT)} not found. Run `just fetch-prosite` first.",
                file=sys.stderr,
            )
            return 2

    release = read_release()
    stats: dict = {"by_dir": {}, "written": 0, "skipped": 0, "planned": 0, "errors": 0}

    if args.only in (None, "prosite"):
        text = PROSITE_DAT.read_text()
        entries = parse_prosite_dat(text)
        if args.limit:
            entries = entries[: args.limit]
        print(f"PROSITE .dat: {len(entries)} entries parsed.")
        process(entries, prosite_target, build_prosite_yaml, release, args.apply, args.force, stats)

    if args.only in (None, "prorule"):
        text = PRORULE_DAT.read_text()
        entries = parse_prorule_dat(text)
        if args.limit:
            entries = entries[: args.limit]
        print(f"ProRule .dat: {len(entries)} entries parsed.")
        process(entries, prorule_target, build_prorule_yaml, release, args.apply, args.force, stats)

    print()
    print("Per-directory totals:")
    for d, n in sorted(stats["by_dir"].items()):
        print(f"  data/traits/{d:32s} {n}")
    print()
    if args.apply:
        print(
            f"Wrote {stats['written']} file(s); skipped {stats['skipped']} existing; "
            f"{stats['errors']} error(s)."
        )
    else:
        print(
            f"Dry-run — would write {stats['planned']} file(s); "
            f"{stats['skipped']} already exist; {stats['errors']} error(s)."
        )
        print("Re-run with --apply to write.")
    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
