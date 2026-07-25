#!/usr/bin/env python3
"""Suggest `canonical_examples` from the Swiss-Prot profile matrix (issue #7, phase 5).

Phases 1-2 built the protein × trait matrix (`data/profiles/profiles.jsonl`);
phases 3-4 mined and materialised the cross-axis rules ("this sequence signature
essentially always encodes this fold", "this trait implies this function") into
`data/equivalence/trait_cooccurrence.tsv`. This phase closes the loop back to
real proteins: it writes exemplar carriers onto the trait records themselves.

For each corpus trait record that is *observed* in the matrix and has no
`canonical_examples` yet, the carriers of that trait are ranked and the top few
are written as `CanonicalExample` entries with `source: SWISSPROT_PROFILE`.

Ranking — the point is to pick the carrier that best *exemplifies* the trait,
not an arbitrary one:

  score = rule_coverage + 0.2 * axis_span_frac + 0.1 * annotation_depth

  • rule_coverage  — confidence-weighted fraction of the trait's empirically
    coupled cross-axis partners (the phase-4 rule endpoints, in either
    direction) that this protein *also* carries. A protein carrying the
    signature AND the fold it encodes AND the function they imply is the
    archetypal carrier. 0.0 for traits with no mined rule; dominates the score
    where a rule exists.
  • axis_span_frac — how many of SEQUENCE / STRUCTURE / FUNCTION the protein
    demonstrates across the trait and its coupled partners.
  • annotation_depth — GO-term count (capped), so better-characterised proteins
    win ties among otherwise-equal carriers.

Ties break on accession, so the output is deterministic and the script is
idempotent: records that already carry examples are skipped unless --force.

Guards: traits carried by more than --max-prevalence of the matrix (default 25%)
are skipped — a term that generic has no archetype. Every rewritten file is
re-parsed in memory before it is written, so a malformed emission is reported
rather than committed.

Dry-run (counts + a sample) unless --apply. Requires PyYAML for the verify pass.

Usage:
  python3 scripts/suggest_canonical_examples.py --dry-run
  python3 scripts/suggest_canonical_examples.py --rule-backed-only --apply
  python3 scripts/suggest_canonical_examples.py --prefix CATH --max-examples 5 --apply
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
JSONL = REPO_ROOT / "data" / "profiles" / "profiles.jsonl"
INDEX = REPO_ROOT / "data" / "raw" / "profiles_cache" / "trait_index.json"
PATHS_CACHE = REPO_ROOT / "data" / "raw" / "profiles_cache" / "record_paths.json"
RULES = REPO_ROOT / "data" / "equivalence" / "trait_cooccurrence.tsv"

_IDENT = re.compile(r"(?m)^identifier:\s*([A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+)\s*$")
_HAS_EXAMPLES = re.compile(r"(?m)^canonical_examples:")
_LICENSE = re.compile(r"(?m)^license:")

# Namespaces that classify *what a protein is* — snapshotted onto each example
# as `family_classifications`. GO / EC are function annotations, not
# classifications, so they are excluded.
_CLASSIFICATION_PREFIXES = ("CATH", "CDD", "HAMAP", "InterPro", "NCBIfam",
                            "PANTHER", "PIRSF", "PRINTS", "PROSITE", "Pfam",
                            "SMART", "SUPERFAMILY")
_MAX_CLASSIFICATIONS = 12
_AXES = ("SEQUENCE", "STRUCTURE", "FUNCTION")


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


def load_rules(path: Path) -> dict:
    """{trait → {partner: confidence}} from the phase-4 cross-axis overlay.

    Edges are directional in the overlay (A implies B) but for *exemplar
    selection* either direction is evidence that the two travel together on a
    real protein, so partners are collected symmetrically.
    """
    partners: dict = collections.defaultdict(dict)
    if not path.exists():
        print(f"warning: no rule overlay at {path} — every pick will be "
              f"annotation-ranked only", file=sys.stderr)
        return partners
    with path.open(encoding="utf-8") as fh:
        header = next(fh, "")
        if not header.startswith("subject\t"):
            raise ValueError(f"{path}: unexpected header {header!r}")
        for line in fh:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 4:
                continue
            subj, _pred, obj, src = cols[0], cols[1], cols[2], cols[3]
            m = re.search(r"conf=([0-9.]+)", src)
            conf = float(m.group(1)) if m else 1.0
            # keep the strongest confidence seen for the pair
            partners[subj][obj] = max(partners[subj].get(obj, 0.0), conf)
            partners[obj][subj] = max(partners[obj].get(subj, 0.0), conf)
    return partners


def mine_rules(rows: list, idx: dict, min_support: int, min_conf: float,
               min_lift: float) -> dict:
    """Mine cross-axis partners straight from the matrix, same statistic as
    phase 3 (support / confidence / lift) but over *every* corpus namespace.

    The committed phase-4 overlay was mined over the signature namespaces that
    carry the SEQUENCE↔STRUCTURE encoding signal (Pfam / PROSITE / SMART /
    NCBIfam → CATH / GO / EC), so InterPro- and CDD-identified traits have no
    partners there and would rank on annotation depth alone. This widens the
    partner sets without disturbing that overlay.

    Only cross-axis ordered pairs are counted — the within-axis pairs are both
    the bulk of the pair space and useless for exemplar selection.
    """
    supp: dict = collections.Counter()
    co: dict = collections.Counter()
    n = len(rows)
    for r in rows:
        ts = [t for t in r["_traits"] if t in idx]
        axes = {t: (idx[t] or ["", ""])[0] for t in ts}
        for t in ts:
            supp[t] += 1
        for a in ts:
            for b in ts:
                if axes[a] != axes[b] and axes[a] in _AXES and axes[b] in _AXES:
                    co[(a, b)] += 1
    partners: dict = collections.defaultdict(dict)
    kept = 0
    for (a, b), c in co.items():
        if supp[a] < min_support:
            continue
        conf = c / supp[a]
        if conf < min_conf:
            continue
        lift = conf / (supp[b] / n) if supp[b] else 0.0
        if lift < min_lift:
            continue
        partners[a][b] = max(partners[a].get(b, 0.0), conf)
        partners[b][a] = max(partners[b].get(a, 0.0), conf)
        kept += 1
    print(f"mined {kept:,} cross-axis rules (support≥{min_support}, "
          f"conf≥{min_conf}, lift≥{min_lift}) over {len(partners):,} traits",
          file=sys.stderr)
    return partners


def load_profiles(path: Path) -> list:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "name" not in r:
                raise SystemExit(
                    "profiles.jsonl predates the metadata fields needed for "
                    "CanonicalExample (name / taxon / length). Rebuild it:\n"
                    "  just build-profiles --query 'reviewed:true AND "
                    "organism_id:9606' --limit 20000 --jsonl-only --apply")
            rows.append(r)
    return rows


def build_record_paths(refresh: bool = False) -> dict:
    """{trait CURIE → record path} for every ProteinTraitRecord in the corpus."""
    if PATHS_CACHE.exists() and not refresh:
        try:
            return json.loads(PATHS_CACHE.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    paths: dict = {}
    for p in TRAITS.rglob("*.yaml"):
        m = _IDENT.search(p.read_text(encoding="utf-8", errors="replace"))
        if m:
            paths[m.group(1)] = str(p.relative_to(REPO_ROOT))
    PATHS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    PATHS_CACHE.write_text(json.dumps(paths), encoding="utf-8")
    print(f"record path index: {len(paths):,} trait records", file=sys.stderr)
    return paths


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


def score_carrier(prot: dict, trait: str, trait_axis: str, partners: dict) -> tuple:
    """(score, rule_coverage, matched_partners, total_partners) for one carrier.

    `rule_coverage` dominates wherever a mined rule exists. The remaining terms
    decide the (large) rest, and are deliberately *smooth* — an earlier cut
    capped annotation depth, which saturated for any protein with 20+ GO terms
    and left 30% of traits picking their exemplar by alphabetical accession.

      depth — GO-term count, len/(len+20): well-characterised proteins win.
      focus — 1/(1+k/5) over the protein's k classification-namespace traits: a
              protein carrying this domain and little else exemplifies it more
              cleanly than a 30-domain giant that merely contains it.

    The two pull against each other, so they are weighted by what an archetype
    means on the trait's own axis: for a domain or fold, the archetypal carrier
    is the focused one; for a function, it is the well-characterised one.
    """
    tset = prot["_traits"]
    part = partners.get(trait) or {}
    matched = {b: c for b, c in part.items() if b in tset}
    total_conf = sum(part.values())
    coverage = (sum(matched.values()) / total_conf) if total_conf else 0.0

    axes = {prot["axes"].get(t) for t in ({trait} | set(matched))}
    span = len(axes & set(_AXES)) / len(_AXES)

    n_go = len(prot["go"])
    depth = n_go / (n_go + 20.0)
    n_sig = sum(1 for t in tset if t.split(":")[0] in _CLASSIFICATION_PREFIXES)
    focus = 1.0 / (1.0 + n_sig / 5.0)

    if trait_axis == "FUNCTION":
        score = coverage + 0.20 * span + 0.20 * depth + 0.05 * focus
    else:
        score = coverage + 0.20 * span + 0.15 * focus + 0.10 * depth
    return (score, coverage, len(matched), len(part))


# ---------------------------------------------------------------------------
# Emission
# ---------------------------------------------------------------------------


def _yq(text) -> str:
    """Quote a scalar for YAML only when it needs it."""
    t = str(text)
    if not t:
        return '""'
    if re.search(r'[:#\[\]{}",&*!|>%@`\']', t) or t[:1] in "-?" \
            or re.fullmatch(r"-?\d+(?:\.\d+)?", t) \
            or t.lower() in ("true", "false", "null", "yes", "no", "on", "off"):
        return '"' + t.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return t


def example_block(prot: dict, trait: str, trait_axis: str, coverage: float,
                  matched: int, total: int, n_carriers: int, matrix_note: str,
                  today: str) -> list:
    """The YAML lines for one CanonicalExample, 2-space list indent."""
    among = f"1 of {n_carriers:,} carriers"
    if total:
        note = (f"{matrix_note}: carrier of {trait} ({among}); also carries "
                f"{matched}/{total} empirically coupled cross-axis traits "
                f"(rule coverage {coverage:.2f})")
    else:
        ranked_by = ("annotation depth" if trait_axis == "FUNCTION"
                     else "carrier focus + annotation depth")
        note = (f"{matrix_note}: observed carrier of {trait} ({among}); no mined "
                f"cross-axis rule for this trait, so ranked by {ranked_by}")

    fams = sorted(t for t in prot["_traits"]
                  if t.split(":")[0] in _CLASSIFICATION_PREFIXES)[:_MAX_CLASSIFICATIONS]

    L = [f"  - protein_id: {prot['accession']}",
         f"    protein_label: {_yq(prot['name'])}"]
    if prot.get("taxon"):
        L.append(f"    taxon_id: {prot['taxon']}")
    if prot.get("taxon_label"):
        L.append(f"    taxon_label: {_yq(prot['taxon_label'])}")
    if prot.get("length"):
        L.append(f"    sequence_length: {prot['length']}")
    L.append(f"    reviewed: {'true' if prot.get('reviewed') else 'false'}")
    if fams:
        L.append("    family_classifications:")
        L += [f"      - {f}" for f in fams]
    L.append(f"    note: {_yq(note)}")
    L.append("    source: SWISSPROT_PROFILE")
    # explicitly quoted — a bare ISO date is a YAML date, not the string the
    # schema's `fetched_at` pattern expects
    L.append(f'    fetched_at: "{today}"')
    return L


def insert_block(text: str, block: list) -> str:
    """Insert a `canonical_examples:` block before the top-level `license:`
    key (keeping licence last, as the seeders emit it) or append it."""
    chunk = "canonical_examples:\n" + "\n".join(block) + "\n"
    m = _LICENSE.search(text)
    if m:
        return text[:m.start()] + chunk + text[m.start():]
    if not text.endswith("\n"):
        text += "\n"
    return text + chunk


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the records (else dry-run)")
    ap.add_argument("--max-examples", type=int, default=3,
                    help="exemplars written per record (default 3)")
    ap.add_argument("--rule-backed-only", action="store_true",
                    help="only traits that participate in a mined cross-axis rule")
    ap.add_argument("--prefix", action="append",
                    help="restrict to trait CURIE prefixes (repeatable, e.g. --prefix CATH)")
    ap.add_argument("--max-prevalence", type=float, default=0.25,
                    help="skip traits carried by more than this fraction of the "
                         "matrix — too generic to have an archetype (default 0.25)")
    ap.add_argument("--min-carriers", type=int, default=1)
    ap.add_argument("--limit", type=int, help="cap the number of records touched")
    ap.add_argument("--force", action="store_true",
                    help="also process records that already have canonical_examples "
                         "(appends; never removes a curator pick)")
    ap.add_argument("--rules", default=str(RULES))
    ap.add_argument("--mine-rules", action="store_true",
                    help="also mine cross-axis partners in-process over every "
                         "corpus namespace (the committed overlay covers only the "
                         "signature namespaces, so InterPro / CDD traits have no "
                         "partners in it)")
    ap.add_argument("--min-support", type=int, default=30)
    ap.add_argument("--min-conf", type=float, default=0.95)
    ap.add_argument("--min-lift", type=float, default=5.0)
    ap.add_argument("--refresh-paths", action="store_true")
    ap.add_argument("--out", help="write the markdown summary here")
    args = ap.parse_args()

    import yaml

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = load_profiles(JSONL)
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    paths = build_record_paths(args.refresh_paths)

    organisms = collections.Counter(r.get("taxon_label") or "?" for r in rows)
    matrix_note = (f"Swiss-Prot profile matrix ({len(rows):,} reviewed "
                   f"{organisms.most_common(1)[0][0]} entries)")

    # trait → carriers. A protein's traits are its matched corpus signatures
    # plus its GO / EC, exactly as the phase-3 mining defined them.
    carriers: dict = collections.defaultdict(list)
    for r in rows:
        r["_traits"] = set(r["traits"]) | set(r["go"]) | {f"EC:{e}" for e in r["ec"]}
        for t in r["_traits"]:
            if t in idx:
                carriers[t].append(r)

    # The committed phase-4 overlay is the authoritative rule set; --mine-rules
    # widens it to the namespaces that mining left out. Overlay confidences win
    # on collision.
    partners = load_rules(Path(args.rules))
    if args.mine_rules:
        for a, bs in mine_rules(rows, idx, args.min_support, args.min_conf,
                                args.min_lift).items():
            for b, conf in bs.items():
                partners[a].setdefault(b, conf)

    n_matrix = len(rows)
    stats = collections.Counter()
    per_prefix = collections.Counter()
    written, samples, failures = 0, [], []

    targets = sorted(carriers)
    if args.prefix:
        keep = set(args.prefix)
        targets = [t for t in targets if t.split(":")[0] in keep]

    for trait in targets:
        if args.rule_backed_only and not partners.get(trait):
            stats["skip: no mined rule"] += 1
            continue
        pool = carriers[trait]
        if len(pool) < args.min_carriers:
            stats["skip: too few carriers"] += 1
            continue
        if len(pool) / n_matrix > args.max_prevalence:
            stats["skip: too generic"] += 1
            continue
        rel = paths.get(trait)
        if not rel:
            stats["skip: no record file"] += 1
            continue
        path = REPO_ROOT / rel
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            stats["skip: unreadable"] += 1
            continue
        if _HAS_EXAMPLES.search(text) and not args.force:
            stats["skip: already has examples"] += 1
            continue

        trait_axis = (idx.get(trait) or ["", ""])[0]
        ranked = sorted(
            ((score_carrier(p, trait, trait_axis, partners), p) for p in pool),
            key=lambda sp: (-sp[0][0], sp[1]["accession"]),
        )[:args.max_examples]

        block: list = []
        for (_score, coverage, matched, total), prot in ranked:
            block += example_block(prot, trait, trait_axis, coverage, matched,
                                   total, len(pool), matrix_note, today)
        new_text = insert_block(text, block)

        # Never write YAML we cannot read back.
        try:
            parsed = yaml.safe_load(new_text)
            got = len(parsed.get("canonical_examples") or [])
            assert got >= len(ranked), f"{got} examples parsed, expected {len(ranked)}"
        except Exception as e:                            # noqa: BLE001
            failures.append(f"{rel}: {e}")
            stats["skip: verify failed"] += 1
            continue

        stats["written"] += 1
        per_prefix[trait.split(":")[0]] += 1
        if partners.get(trait):
            stats["rule-backed"] += 1
        written += len(ranked)
        if len(samples) < 8:
            samples.append((trait, rel, ranked[0][1]["accession"],
                            ranked[0][1]["name"], ranked[0][0][1]))
        if args.apply:
            path.write_text(new_text, encoding="utf-8")
        if args.limit and stats["written"] >= args.limit:
            break

    L = [f"# canonical_examples suggestions ({'APPLIED' if args.apply else 'dry-run'})",
         "",
         f"matrix: {n_matrix:,} proteins | traits observed in corpus: {len(carriers):,} | "
         f"rule overlay: {sum(len(v) for v in partners.values())//2:,} pairs",
         "",
         f"**records to update: {stats['written']:,}** "
         f"({stats['rule-backed']:,} rule-backed, "
         f"{stats['written'] - stats['rule-backed']:,} annotation-ranked); "
         f"examples emitted: {written:,}",
         "",
         "| skipped | n |", "|---|--:|"]
    for k, v in sorted(stats.items()):
        if k.startswith("skip:"):
            L.append(f"| {k[6:]} | {v:,} |")
    L += ["", "| namespace | records |", "|---|--:|"]
    for k, v in per_prefix.most_common():
        L.append(f"| {k} | {v:,} |")
    L += ["", "## Sample picks", "", "| trait | top exemplar | rule coverage |", "|---|---|--:|"]
    for trait, _rel, acc, name, cov in samples:
        L.append(f"| {trait} | {acc} — {name} | {cov:.2f} |")
    if failures:
        L += ["", f"## Verify failures ({len(failures)})", ""]
        L += [f"- {f}" for f in failures[:20]]

    report = "\n".join(L)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
    if not args.apply:
        print("\nDry-run — pass --apply to write.", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
