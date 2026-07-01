#!/usr/bin/env python3
"""Ground `ProteinTraitCategoryEnum` values to authoritative ontology
terms and attach them as `xrefs` on every record with that category.

Mappings are a curated dict (`CATEGORY_MAPPINGS`) shipping with this
script — you can extend it as new ontology coverage is discovered.
Each mapping is verified against two independent sources:

    OAK (Ontology Access Kit) — `sqlite:obo:<onto>` adapter, which
      downloads a local SQLite dump of the source ontology (SO, GO, MOD)
      and looks the term up locally. This is `--source oak`.
    OLS4 REST — the live EBI Ontology Lookup Service. This is
      `--source ols`.

Default: `--source oak`. Any term that fails resolution is flagged and
skipped; obsolete terms (label prefixed with "obsolete") are always
skipped. Run with `--audit` to see the full mapping table and its
resolution status without touching any files.

Usage:
  # audit only — print every mapping's canonical label
  python3 scripts/ground_categories.py --audit
  # apply — walk data/traits/, add resolved CURIEs to xrefs
  python3 scripts/ground_categories.py --apply
  # scope: same path/glob semantics as validate_linkml.py
  python3 scripts/ground_categories.py --apply data/traits/sequence/motif

Idempotent: existing xrefs are not duplicated. Records already carrying
one of the mapped CURIEs are left alone.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_DIR = REPO_ROOT / "data" / "traits"
OLS_BASE = "https://www.ebi.ac.uk/ols4/api"

# ---------------------------------------------------------------------------
# Curated category → ontology CURIE mapping
# ---------------------------------------------------------------------------
#
# Each list is applied wholesale to every record whose trait_category
# matches the key. Prefer stable, non-obsolete, sufficiently generic
# parent terms — these are broad type assertions, not per-record
# groundings. Confirm additions with:
#   python3 scripts/ground_categories.py --audit
#
# Categories with no mapping (STRUCT_CLASS, STRUCT_ARCHITECTURE,
# STRUCT_TOPOLOGY, STRUCT_HOMOLOGOUS_SUPERFAMILY, STRUCT_ALLOSTERIC_SITE,
# STRUCT_CAVITY, STRUCT_SYMMETRY, STRUCT_DYNAMICS, STRUCT_STABILITY,
# STRUCT_SURFACE, SEQ_DISORDER, SEQ_EPITOPE, SEQ_NONSTANDARD_RESIDUE,
# FUNC_COFACTOR_REQUIREMENT, UPPER, OTHER) are intentionally left blank
# because no sufficiently precise SO/GO/MOD term was identified in the
# initial pass — extend `CATEGORY_MAPPINGS` when one is found.

CATEGORY_MAPPINGS: dict[str, list[str]] = {
    # ---------- SEQUENCE ----------
    "SEQ_MOTIF":                 ["SO:0001067"],  # polypeptide_motif
    "SEQ_SIGNAL_PEPTIDE":        ["SO:0000418"],  # signal_peptide
    "SEQ_TRANSIT_PEPTIDE":       ["SO:0000725"],  # transit_peptide
    "SEQ_PROPEPTIDE":            ["SO:0001064"],  # active_peptide (closest)
    "SEQ_INITIATOR_METHIONINE":  ["SO:0000691"],  # cleaved_initiator_methionine
    "SEQ_MATURE_CHAIN":          ["SO:0001064"],  # active_peptide
    "SEQ_CLEAVAGE_SITE":         ["SO:0100011"],  # cleaved_peptide_region
    "SEQ_LOW_COMPLEXITY":        ["SO:0001066"],  # compositionally_biased_region_of_peptide
    "SEQ_COMPOSITION":           ["SO:0001066"],  # compositionally_biased_region_of_peptide
    "SEQ_REPEAT":                ["SO:0001068"],  # polypeptide_repeat
    "SEQ_CONSERVATION":          ["SO:0100021"],  # polypeptide_conserved_region
    "SEQ_PTM_SITE":              ["SO:0001089"],  # post_translationally_modified_region
    "SEQ_MODIFIED_RESIDUE":      ["SO:0001089"],  # post_translationally_modified_region
    "SEQ_GLYCOSYLATION_SITE":    ["MOD:00693"],   # glycosylated residue
    "SEQ_LIPIDATION_SITE":       ["GO:0006497"],  # protein lipidation (BP)
    "SEQ_CROSSLINK_SITE":        ["GO:0018262"],  # isopeptide cross-linking (BP)

    # ---------- STRUCTURE ----------
    "STRUCT_FOLD":               ["SO:0100021"],  # polypeptide_conserved_region
    "STRUCT_DOMAIN":             ["SO:0100021"],  # polypeptide_conserved_region
    "STRUCT_SECONDARY":          ["SO:0001114"],  # peptide_helix (exemplar; refine per-record later)
    "STRUCT_QUATERNARY":         ["GO:0032991"],  # protein-containing complex
    "STRUCT_INTERFACE":          ["SO:0001093"],  # protein_protein_contact
    "STRUCT_ACTIVE_SITE":        ["SO:0001104"],  # catalytic_residue
    "STRUCT_BINDING_SITE":       ["SO:0001091"],  # non_covalent_binding_site
    "STRUCT_DISULFIDE":          ["SO:0001088"],  # disulfide_bond
    "STRUCT_METAL_SITE":         ["GO:0046872"],  # metal ion binding

    # ---------- MIXED (SEQUENCE + STRUCTURE) ----------
    "MIXED_TRANSMEMBRANE":       ["SO:0001077"],  # transmembrane_polypeptide_region
    "MIXED_COILED_COIL":         ["SO:0001080"],  # coiled_coil
    "MIXED_STRUCTURAL_REPEAT":   ["SO:0001068"],  # polypeptide_repeat

    # ---------- FUNCTION ----------
    "FUNC_ENZYMATIC_ACTIVITY":   ["GO:0003824"],  # catalytic activity
    "FUNC_BINDING_CAPACITY":     ["GO:0005488"],  # binding
    "FUNC_LOCALIZATION":         ["GO:0005575"],  # cellular_component
    "FUNC_ENVIRONMENTAL_RESPONSE": ["GO:0050896"],  # response to stimulus
    "FUNC_INTERACTION_PARTNER":  ["GO:0005515"],  # protein binding
}


# ---------------------------------------------------------------------------
# Term lookup backends
# ---------------------------------------------------------------------------


class OAKLookup:
    """OAK-backed term label lookup. Uses `sqlite:obo:<onto>` per
    ontology — each ontology's local SQLite dump is downloaded on
    first use and then queried without further network traffic."""

    def __init__(self) -> None:
        from oaklib import get_adapter  # imported lazily so --source ols
        self._get_adapter = get_adapter
        self._adapters: dict[str, object] = {}

    def _adapter_for(self, prefix: str):
        onto = prefix.lower()
        if onto not in self._adapters:
            self._adapters[onto] = self._get_adapter(f"sqlite:obo:{onto}")
        return self._adapters[onto]

    def label(self, curie: str) -> str | None:
        if ":" not in curie:
            return None
        prefix, _, _ = curie.partition(":")
        try:
            adapter = self._adapter_for(prefix)
            return adapter.label(curie)
        except Exception as exc:  # noqa: BLE001 — surface any failure to caller
            print(f"    oak error for {curie}: {exc}", file=sys.stderr)
            return None


class OLSLookup:
    """Direct OLS4 REST lookup. One HTTP call per CURIE — cache to
    stay polite."""

    def __init__(self) -> None:
        self._cache: dict[str, str | None] = {}

    def label(self, curie: str) -> str | None:
        if curie in self._cache:
            return self._cache[curie]
        if ":" not in curie:
            self._cache[curie] = None
            return None
        prefix, _, local = curie.partition(":")
        iri = f"http://purl.obolibrary.org/obo/{prefix}_{local}"
        # OLS4 v2 needs a doubly-URL-encoded IRI in the path segment.
        encoded = urllib.parse.quote(urllib.parse.quote(iri, safe=""), safe="")
        url = f"{OLS_BASE}/v2/ontologies/{prefix.lower()}/classes/{encoded}"
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            print(f"    ols {curie}: HTTP {exc.code}", file=sys.stderr)
            self._cache[curie] = None
            return None
        except urllib.error.URLError as exc:
            print(f"    ols {curie}: {exc}", file=sys.stderr)
            self._cache[curie] = None
            return None
        label = data.get("label")
        if isinstance(label, list):
            label = label[0] if label else None
        self._cache[curie] = label
        return label


# ---------------------------------------------------------------------------
# Mapping verification
# ---------------------------------------------------------------------------


def verify_mappings(lookup) -> dict[str, list[tuple[str, str | None]]]:
    """Resolve every CURIE in CATEGORY_MAPPINGS. Return
    {category: [(curie, label|None), ...]}."""
    resolved: dict[str, list[tuple[str, str | None]]] = {}
    for cat, curies in CATEGORY_MAPPINGS.items():
        resolved[cat] = [(c, lookup.label(c)) for c in curies]
    return resolved


def is_usable(label: str | None) -> bool:
    """A term is usable as an xref if it resolves and isn't obsolete."""
    if not label:
        return False
    lower = label.lower()
    if lower.startswith("obsolete") or lower == label.replace("_", " "):
        # OLS returns the bare id (e.g. "SO_0001069") for undefined terms.
        pass
    if lower.startswith("obsolete"):
        return False
    # Filter the raw-id fallback: OLS returns "SO_0001069" as label when
    # the term has no rdfs:label.
    if label.replace("_", ":") == label.replace("_", ":").upper():
        # If label is exactly the CURIE form (SO_NNNN with no words), skip.
        if "_" in label and " " not in label and label.split("_")[0].isupper():
            return False
    return True


def print_audit(resolved: dict[str, list[tuple[str, str | None]]]) -> None:
    ok = missing = obsolete = 0
    for cat, pairs in resolved.items():
        for curie, label in pairs:
            if label is None:
                marker = "MISSING"
                missing += 1
            elif label.lower().startswith("obsolete"):
                marker = "OBSOLETE"
                obsolete += 1
            else:
                marker = "ok"
                ok += 1
            print(f"  {marker:9s} {cat:30s} {curie:14s} {label or ''}")
    print()
    print(f"resolved: {ok}   missing: {missing}   obsolete: {obsolete}")


# ---------------------------------------------------------------------------
# Trait YAML round-trip (mirrors fetch_uniprot_examples.py)
# ---------------------------------------------------------------------------


def read_trait(path: Path) -> dict:
    import yaml
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping at top level")
    return data


def write_trait(path: Path, data: dict) -> None:
    import yaml

    class FoldedDefinition(str):
        pass

    def _folded_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")

    yaml.add_representer(FoldedDefinition, _folded_representer)

    key_order = [
        "identifier", "label", "definition", "definition_source",
        "trait_axis", "trait_category", "term_kind", "mapping_status",
        "parent_traits", "sequence_pattern", "residue_sequence",
        "xrefs", "canonical_examples", "evidence", "curation_history",
        "causal_graphs",
    ]
    ordered = {k: data[k] for k in key_order if k in data}
    for k in data:
        if k not in ordered:
            ordered[k] = data[k]

    if "definition" in ordered and isinstance(ordered["definition"], str):
        ordered["definition"] = FoldedDefinition(ordered["definition"])

    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(
            ordered,
            fh,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=100000,
        )


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------


def collect_targets(paths: list[str]) -> list[Path]:
    if not paths:
        return sorted(TRAITS_DIR.rglob("*.yaml"))
    files: list[Path] = []
    for arg in paths:
        p = Path(arg)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if p.is_dir():
            files.extend(sorted(p.rglob("*.yaml")))
        elif p.is_file():
            files.append(p)
        else:
            matches = sorted(REPO_ROOT.glob(arg))
            if not matches:
                print(f"warn: no match for {arg}", file=sys.stderr)
            files.extend(matches)
    return files


def apply_mappings(
    targets: list[Path],
    usable_map: dict[str, list[str]],
    apply_: bool,
) -> tuple[int, int]:
    """Return (n_records_touched, n_xrefs_added)."""
    touched = added = 0
    for path in targets:
        try:
            record = read_trait(path)
        except Exception as exc:
            print(f"WARN {path.relative_to(REPO_ROOT)}: {exc}", file=sys.stderr)
            continue
        cat = record.get("trait_category")
        if cat not in usable_map:
            continue
        new_xrefs = usable_map[cat]
        existing = list(record.get("xrefs") or [])
        existing_set = set(existing)
        added_here = [x for x in new_xrefs if x not in existing_set]
        if not added_here:
            continue
        existing.extend(added_here)
        record["xrefs"] = existing
        touched += 1
        added += len(added_here)
        if apply_:
            write_trait(path, record)
    return touched, added


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*",
                        help="trait YAML files, dirs, or globs "
                             "(default: all data/traits)")
    parser.add_argument("--source", choices=("oak", "ols"), default="oak",
                        help="term-lookup backend (default oak = sqlite:obo)")
    parser.add_argument("--audit", action="store_true",
                        help="print the resolved mapping table and exit")
    parser.add_argument("--apply", action="store_true",
                        help="write xrefs back to disk (default: dry-run)")
    args = parser.parse_args(argv)

    lookup = OAKLookup() if args.source == "oak" else OLSLookup()

    print(f"Verifying {sum(len(v) for v in CATEGORY_MAPPINGS.values())} mappings "
          f"across {len(CATEGORY_MAPPINGS)} categories via --source {args.source}")
    print()
    resolved = verify_mappings(lookup)

    if args.audit:
        print_audit(resolved)
        return 0

    usable_map: dict[str, list[str]] = {}
    for cat, pairs in resolved.items():
        good = [c for c, label in pairs if is_usable(label)]
        skipped = [c for c, label in pairs if not is_usable(label)]
        if skipped:
            print(f"  skip (unresolved/obsolete): {cat} → {skipped}",
                  file=sys.stderr)
        if good:
            usable_map[cat] = good

    print(f"{sum(len(v) for v in usable_map.values())} usable CURIE(s) "
          f"across {len(usable_map)} categories.")

    targets = collect_targets(args.paths)
    print(f"Scanning {len(targets)} record(s).")
    touched, added = apply_mappings(targets, usable_map, args.apply)

    print()
    print(f"Records touched: {touched}")
    print(f"xrefs added:     {added}")
    if not args.apply:
        print("Dry-run — re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
