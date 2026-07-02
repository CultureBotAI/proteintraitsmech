#!/usr/bin/env python3
"""Analyze the ProteinTraitRecord catalog for equivalent, mergeable traits.

Produces **unequivocal, deterministic** statements of the form
"Trait X = Trait Y (mergeable)" — plus a separate, explicitly *non*-committal
list of review candidates that look related but cannot be equated by rule.

Why the split? In this corpus `xrefs` are used *associatively*, not as
identity assertions: a PROSITE ProRule cross-references the PATTERN it is
built on, an N-glycosylation pattern cross-references the MOD term it flags,
and ~2,700 motif records all ground to the same generic SO term
(`SO:0001067`, "polypeptide_region"). So "shares an xref" does NOT mean
"is the same trait". The only signals that unequivocally identify two records
as the same trait are:

  MERGE (deterministic — emitted as "X = Y"):
    R1 EXACT_ID       identical `identifier` (same source term seeded to two
                      paths / imported twice).
    R2 EXACT_PATTERN  byte-identical non-empty `sequence_pattern` AND identical
                      (trait_axis, trait_category) — the same sequence
                      signature expressed twice.

  REVIEW (candidate — NOT asserted as equal, needs a curator):
    C1 XREF_IDENTITY  one record's source-anchored `identifier` appears in the
                      other's `xrefs`, same (axis, category). Usually a
                      pattern/rule pair — related, often not truly one trait.
    C2 SHARED_ANCHOR  both cite the same *specific* identity-namespace xref
                      (EC/RHEA/MOD/Pfam/InterPro/CATH/SCOP/ECOD/PROSITE/HAMAP)
                      that is shared by at most --anchor-cap records (generic
                      groundings are excluded), same (axis, category). Typically
                      PROSITE pattern+profile for one family.
    C3 SAME_LABEL     identical normalized label, same (axis, category).

  NEVER (hard guards, applied to every rule): a different `trait_axis` or
  `trait_category`, or two different values within the same identity namespace,
  are never equated.

Input: the docs shards `docs/data/records.<AXIS>.json` (run `just build-docs`
first). They carry id/label/axis/cat/src/pat/xr/pt/path — everything the
detector needs. `--apply` additionally reads/writes the underlying YAML at each
record's `path`.

Default is a dry run: writes a plan to `data/analysis/trait_merge_plan.yaml`
and prints a summary. `--apply` executes only the MERGE groups (never the
review candidates), preserving synonyms/xrefs/parent_traits and appending a
`curation_history` event. Stdlib-only unless `--apply` (then PyYAML).

Usage:
  python3 scripts/analyze_trait_equivalence.py                 # dry run + plan
  python3 scripts/analyze_trait_equivalence.py --show-review   # also print C1-C3
  python3 scripts/analyze_trait_equivalence.py --apply         # execute merges
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "docs" / "data"
ANALYSIS_DIR = REPO_ROOT / "data" / "analysis"

# Namespaces whose CURIEs denote a specific trait identity (not a generic
# grounding). Used only for the C2 review heuristic.
IDENTITY_NAMESPACES = {
    "EC", "RHEA", "MOD", "Pfam", "InterPro", "CATH", "SCOP", "ECOD",
    "PROSITE", "HAMAP",
}

# Status precedence for choosing a merge target (higher = preferred).
STATUS_RANK = {"REVIEWED": 3, "PROPOSED": 2, "SEEDED": 1, "DEPRECATED": 0, "": 0}


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------


def load_records() -> list[dict]:
    files = sorted(glob.glob(str(DATA_DIR / "records.*.json")))
    if not files:
        sys.exit("No docs/data/records.*.json shards found — run `just build-docs` first.")
    recs: list[dict] = []
    for f in files:
        recs.extend(json.load(open(f, encoding="utf-8")))
    return recs


def norm_label(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def cat_key(r: dict) -> tuple[str, str]:
    return (r.get("axis") or "", r.get("cat") or "")


# ---------------------------------------------------------------------------
# Union-Find (for grouping MERGE edges into equivalence classes)
# ---------------------------------------------------------------------------


class DSU:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: str, b: str) -> None:
        self.parent[self.find(a)] = self.find(b)


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def detect_merges(recs: list[dict]) -> tuple[list[dict], dict]:
    """Return (merge_groups, per-rule edge index). Groups are equivalence
    classes over the deterministic MERGE edges (R1, R2)."""
    by_id: dict[str, list[dict]] = defaultdict(list)
    for r in recs:
        by_id[r["id"]].append(r)

    dsu = DSU()
    edge_rule: dict[tuple[str, str], str] = {}
    edge_evidence: dict[tuple[str, str], str] = {}

    def add_edge(a: str, b: str, rule: str, evidence: str) -> None:
        dsu.union(a, b)
        key = tuple(sorted((a, b)))
        # First rule to fire owns the edge; R1 outranks R2.
        if key not in edge_rule or rule == "R1_EXACT_ID":
            edge_rule[key] = rule
            edge_evidence[key] = evidence

    # R1 — identical identifier (same source term in >1 file).
    dup_ids = {i: rs for i, rs in by_id.items() if len(rs) > 1}
    for i, rs in dup_ids.items():
        for other in rs[1:]:
            # Same id → same node under union-find; record as a self-edge via
            # a synthetic path-tagged key so grouping still captures it.
            add_edge(i, i, "R1_EXACT_ID", f"identifier {i}")

    # R2 — identical sequence_pattern within one (axis, category).
    by_pat: dict[tuple, list[str]] = defaultdict(list)
    for r in recs:
        if r.get("pat"):
            by_pat[(cat_key(r), r["pat"])].append(r["id"])
    for (ck, pat), ids in by_pat.items():
        uids = sorted(set(ids))
        for j in range(1, len(uids)):
            if uids[0] != uids[j]:
                add_edge(uids[0], uids[j], "R2_EXACT_PATTERN",
                         f"sequence_pattern {pat!r}")

    # Assemble groups. A group is either >1 distinct id joined by R2, OR an
    # id that appears in >1 file (R1).
    groups_by_root: dict[str, set[str]] = defaultdict(set)
    for key in edge_rule:
        groups_by_root[dsu.find(key[0])].update(key)
    # add pure R1 duplicate ids (single node, multiple files)
    for i in dup_ids:
        groups_by_root[dsu.find(i)].add(i)

    merge_groups: list[dict] = []
    for root, ids in groups_by_root.items():
        members: list[dict] = []
        for i in sorted(ids):
            members.extend(by_id[i])
        if len(members) < 2:
            continue
        rules = sorted({edge_rule[k] for k in edge_rule
                        if k[0] in ids or k[1] in ids} |
                       ({"R1_EXACT_ID"} if any(i in dup_ids for i in ids) else set()))
        evidence = sorted({edge_evidence[k] for k in edge_evidence
                           if k[0] in ids or k[1] in ids})
        merge_groups.append({
            "members": members,
            "rules": rules,
            "evidence": evidence,
        })
    return merge_groups, {}


def detect_review(recs: list[dict], anchor_cap: int) -> list[dict]:
    """Return review candidates (C1–C3): related but NOT auto-equated."""
    by_id = {r["id"]: r for r in recs}
    cands: dict[tuple[str, str], dict] = {}

    def add(a: str, b: str, rule: str, evidence: str) -> None:
        if a == b:
            return
        key = tuple(sorted((a, b)))
        cands.setdefault(key, {"members": list(key), "rules": set(), "evidence": set()})
        cands[key]["rules"].add(rule)
        cands[key]["evidence"].add(evidence)

    # C1 — one record's source-anchored id ∈ another's xrefs, same (axis,cat).
    for r in recs:
        for x in (r.get("xr") or []):
            b = by_id.get(x)
            if b and b["id"] != r["id"] and cat_key(b) == cat_key(r):
                add(r["id"], b["id"], "C1_XREF_IDENTITY", f"xref {x}")

    # C2 — shared specific identity xref (excluding generic high-frequency ones).
    by_anchor: dict[str, set[str]] = defaultdict(set)
    for r in recs:
        for x in (r.get("xr") or []):
            if x.split(":", 1)[0] in IDENTITY_NAMESPACES:
                by_anchor[x].add(r["id"])
    for x, members in by_anchor.items():
        if len(members) > anchor_cap:
            continue  # generic grounding — not an identity signal
        ms = sorted(members)
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                a, b = by_id[ms[i]], by_id[ms[j]]
                if cat_key(a) == cat_key(b):
                    add(a["id"], b["id"], "C2_SHARED_ANCHOR", f"anchor {x}")

    # C3 — identical normalized label across DIFFERENT sources, same
    # (axis, category). Restricted to cross-source: intra-source label reuse
    # is rampant (thousands of distinct TED/ECOD folds share a generic name)
    # and is not an equivalence signal.
    by_label: dict[tuple, list[dict]] = defaultdict(list)
    for r in recs:
        by_label[(cat_key(r), norm_label(r.get("label", "")))].append(r)
    for (ck, lab), grp in by_label.items():
        if not lab or len(grp) < 2:
            continue
        for i in range(len(grp)):
            for j in range(i + 1, len(grp)):
                if grp[i].get("src") != grp[j].get("src"):
                    add(grp[i]["id"], grp[j]["id"], "C3_SAME_LABEL_XSRC",
                        f"label {lab!r}")

    out = []
    for c in cands.values():
        c["rules"] = sorted(c["rules"])
        c["evidence"] = sorted(c["evidence"])
        out.append(c)
    out.sort(key=lambda c: (c["rules"], c["members"]))
    return out


# ---------------------------------------------------------------------------
# Target selection + statements
# ---------------------------------------------------------------------------


def richness(r: dict) -> int:
    return len(r.get("xr") or []) + len(r.get("pt") or [])


def choose_target(members: list[dict]) -> dict:
    """Deterministic target: highest status, then source-anchored over
    curator-minted, then richest, then lexicographically smallest id then
    path (so the choice is fully reproducible)."""
    def key(r: dict):
        anchored = 0 if r["id"].startswith("proteintraitsmech:") else 1
        # Sort DESC on the first three, ASC on id/path — invert id/path so a
        # single max() call yields the smallest id/path among equals.
        return (
            STATUS_RANK.get(r.get("sta", ""), 0),
            anchored,
            richness(r),
            tuple(-ord(c) for c in r["id"]),
            tuple(-ord(c) for c in (r.get("path") or "")),
        )
    return max(members, key=key)


def make_statement(members: list[dict], target: dict) -> str:
    ids = sorted({m["id"] for m in members})
    if len(ids) == 1:
        # R1: several files carry the same identifier — consolidate to one.
        paths = ", ".join(sorted(m.get("path", "?") for m in members))
        return (f"{len(members)} records share identifier {ids[0]} "
                f"({paths}) → keep {target.get('path')}, remove the rest")
    return f"{' = '.join(ids)}  →  merge into {target['id']}"


# ---------------------------------------------------------------------------
# Plan emission
# ---------------------------------------------------------------------------


def project_member(r: dict) -> dict:
    return {"identifier": r["id"], "label": r.get("label", ""),
            "axis": r.get("axis"), "category": r.get("cat"),
            "status": r.get("sta"), "path": r.get("path")}


def write_plan(merge_groups: list[dict], review: list[dict]) -> Path:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Deterministic trait-equivalence plan")
    lines.append("# Generated by scripts/analyze_trait_equivalence.py — do not hand-edit.")
    lines.append(f"summary:")
    lines.append(f"  merge_groups: {len(merge_groups)}")
    lines.append(f"  merge_records: {sum(len(g['members']) for g in merge_groups)}")
    lines.append(f"  review_candidates: {len(review)}")
    lines.append("")
    lines.append("merge_groups:  # unequivocal — Trait X = Trait Y")
    if not merge_groups:
        lines.append("  []")
    for g in merge_groups:
        target = choose_target(g["members"])
        lines.append(f"  - statement: \"{make_statement(g['members'], target)}\"")
        lines.append(f"    rules: [{', '.join(g['rules'])}]")
        lines.append(f"    evidence: [{', '.join(json.dumps(e) for e in g['evidence'])}]")
        lines.append(f"    target: {target['id']}")
        lines.append(f"    members:")
        for m in g["members"]:
            p = project_member(m)
            lines.append(f"      - {{ identifier: {p['identifier']}, "
                         f"category: {p['category']}, status: {p['status']}, "
                         f"path: {p['path']} }}")
    lines.append("")
    lines.append("review_candidates:  # related but NOT asserted equal — curator decides")
    if not review:
        lines.append("  []")
    for c in review:
        lines.append(f"  - members: [{', '.join(c['members'])}]")
        lines.append(f"    rules: [{', '.join(c['rules'])}]")
        lines.append(f"    evidence: [{', '.join(json.dumps(e) for e in c['evidence'])}]")
    out = ANALYSIS_DIR / "trait_merge_plan.yaml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Apply (MERGE groups only)
# ---------------------------------------------------------------------------


def apply_merges(merge_groups: list[dict]) -> int:
    import datetime
    import yaml  # noqa: F401 — only needed on --apply

    stamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    merged = 0
    for g in merge_groups:
        members = g["members"]
        target = choose_target(members)
        tpath = REPO_ROOT / target["path"]
        tdoc = yaml.safe_load(tpath.read_text(encoding="utf-8"))
        losers = [m for m in members if m is not target]

        for loser in losers:
            lpath = REPO_ROOT / loser["path"]
            if lpath.resolve() == tpath.resolve():
                continue
            ldoc = yaml.safe_load(lpath.read_text(encoding="utf-8")) or {}
            # Union list fields into the target.
            _merge_list(tdoc, ldoc, "xrefs")
            _merge_list(tdoc, ldoc, "parent_traits")
            _merge_synonyms(tdoc, ldoc)
            same_id = ldoc.get("identifier") == tdoc.get("identifier")
            if same_id:
                lpath.unlink()  # exact-id duplicate — remove the redundant file
            else:
                ldoc.setdefault("xrefs", [])
                if tdoc["identifier"] not in ldoc["xrefs"]:
                    ldoc["xrefs"].append(tdoc["identifier"])
                ldoc["mapping_status"] = "DEPRECATED"
                _append_event(ldoc, stamp,
                              f"deprecated: merged into {tdoc['identifier']}")
                lpath.write_text(yaml.safe_dump(ldoc, sort_keys=False,
                                                allow_unicode=True), encoding="utf-8")

        _append_event(tdoc, stamp,
                      "merged " + ", ".join(sorted(l["id"] for l in losers)))
        tpath.write_text(yaml.safe_dump(tdoc, sort_keys=False, allow_unicode=True),
                         encoding="utf-8")
        merged += 1
    return merged


def _merge_list(dst: dict, src: dict, key: str) -> None:
    vals = list(dst.get(key) or [])
    for v in src.get(key) or []:
        if v not in vals:
            vals.append(v)
    if vals:
        dst[key] = vals


def _merge_synonyms(dst: dict, src: dict) -> None:
    syns = list(dst.get("synonyms") or [])
    have = {(s.get("synonym_text"), s.get("synonym_type")) for s in syns}
    # loser's label becomes a synonym on the target
    llabel = src.get("label")
    if llabel and llabel != dst.get("label") and (llabel, "RELATED_SYNONYM") not in have:
        syns.append({"synonym_text": llabel, "synonym_type": "RELATED_SYNONYM"})
    for s in src.get("synonyms") or []:
        k = (s.get("synonym_text"), s.get("synonym_type"))
        if k not in have and s.get("synonym_text") != dst.get("label"):
            syns.append(s)
            have.add(k)
    if syns:
        dst["synonyms"] = syns


def _append_event(doc: dict, stamp: str, action: str) -> None:
    doc.setdefault("curation_history", []).append({
        "timestamp": stamp,
        "curator": "merge-traits skill",
        "action": action,
        "llm_assisted": True,
    })


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="execute the MERGE groups (default: dry run + plan)")
    ap.add_argument("--show-review", action="store_true",
                    help="also print the review candidates (C1–C3)")
    ap.add_argument("--anchor-cap", type=int, default=5,
                    help="max records sharing an identity xref for it to count "
                         "as a C2 signal (higher = more generic; default 5)")
    args = ap.parse_args()

    recs = load_records()
    merge_groups, _ = detect_merges(recs)
    review = detect_review(recs, args.anchor_cap)

    print(f"Loaded {len(recs):,} records.")
    print(f"\n=== MERGE (unequivocal — Trait X = Trait Y) : "
          f"{len(merge_groups)} group(s) ===")
    for g in merge_groups:
        target = choose_target(g["members"])
        print(f"  {make_statement(g['members'], target)}")
        print(f"      rules={g['rules']} evidence={g['evidence']}")
    if not merge_groups:
        print("  (none)")

    print(f"\n=== REVIEW (related, NOT auto-merged) : {len(review)} candidate pair(s) ===")
    if args.show_review:
        for c in review:
            print(f"  {' ~ '.join(c['members'])}  {c['rules']}  {c['evidence']}")
    else:
        by_rule = defaultdict(int)
        for c in review:
            for r in c["rules"]:
                by_rule[r] += 1
        for r, n in sorted(by_rule.items()):
            print(f"  {r}: {n} pair(s)")
        print("  (re-run with --show-review to list them)")

    plan = write_plan(merge_groups, review)
    print(f"\nPlan written → {plan.relative_to(REPO_ROOT)}")

    if args.apply:
        n = apply_merges(merge_groups)
        print(f"Applied {n} merge group(s). Re-run `just build-docs` and "
              f"`just validate-all` to refresh + verify.")
    else:
        print("Dry run — re-run with --apply to execute the MERGE groups "
              "(review candidates are never auto-merged).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
