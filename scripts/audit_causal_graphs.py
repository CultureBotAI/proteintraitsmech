#!/usr/bin/env python3
"""Structural-integrity audit of the inline `causal_graphs` on ProteinTraitRecords.

`just validate` proves a record matches the LinkML schema (required slots, CURIE
patterns, ≥1 EvidenceItem per edge). It does NOT check the graph's *internal*
consistency — that an edge's `subject`/`object` name real nodes, that node_ids are
unique, that node_types are in the enum, or how well the mechanism is grounded and
snippet-cited. This audit closes that gap: it is the modelling-quality gate for the
mechanism layer, the analogue of `review-source-categories` for causal graphs.

Checks per CausalGraph (see the schema's CausalGraph/CausalNode/CausalEdge):
  ERRORS (fail the gate)
    • graph_id present + unique within the record;
    • ≥1 node and ≥1 edge;
    • node_id present + unique within the graph;
    • node label + node_type present; node_type ∈ CausalNodeTypeEnum (read live
      from the schema);
    • edge subject/object each resolve to a node_id in the SAME graph (no dangling);
    • edge predicate present; ≥1 evidence; each EvidenceItem has a `reference`;
    • any `grounding` / `xrefs` / `predicate_id` present matches the CURIE pattern.
  WARNINGS (surfaced; fail only under --strict)
    • a groundable non-local node with no `grounding` (label-only draft node — allowed in v1);
    • an edge whose evidence carries no verbatim `snippet`;
    • an edge with no `predicate_id` (RO CURIE).

`--warning-baseline` pins known warning identities so NEW warnings fail even if another
warning was fixed and the total count did not change.

Read-only. Stdlib + PyYAML. Exit 1 on any ERROR (or WARNING under --strict), else 0.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
SCHEMA = REPO_ROOT / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml"
CURIE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$")


@dataclass(frozen=True)
class AuditWarning:
    """A warning message plus its stable identity for warning baselines."""

    key: str
    message: str

    def __str__(self) -> str:
        return self.message


def warning_key(rel_path: str, graph_id, kind: str, target: str) -> str:
    """Return the identity key for a warning.

    The key intentionally omits the human-readable warning text so the baseline
    follows the graph element, not the exact phrasing of a diagnostic.
    """
    return f"{rel_path}|{graph_id}|{kind}|{target}"


def count_warnings(warnings: list[AuditWarning]) -> dict[str, int]:
    """Return sorted key -> count warning identities.

    Counts, rather than a set, keep duplicate edge-level warnings visible if a
    graph ever grows parallel edges with the same subject and object.
    """
    return dict(sorted(Counter(warning.key for warning in warnings).items()))


def diff_baseline(current: dict[str, int], known: dict[str, int]) -> tuple[list[str], list[str]]:
    """Return (fixed, new) warning keys by count."""
    fixed: list[str] = []
    new: list[str] = []
    for key in sorted(set(current) | set(known)):
        current_count = current.get(key, 0)
        known_count = known.get(key, 0)
        if known_count > current_count:
            fixed.extend([key] * (known_count - current_count))
        elif current_count > known_count:
            new.extend([key] * (current_count - known_count))
    return fixed, new


def needs_grounding(node: dict) -> bool:
    """Return True when an ungrounded node is probably still a draft.

    Several complete, curated graph families need source-local nodes that do not
    have stable ontology or database CURIEs:

    * explicitly described local mechanism nodes with no stable external term;
    * hand-curated reaction intermediates represented as described STATE nodes;
    * BioLiP and MetalPDB RESIDUE nodes in PDB author numbering when SIFTS or
      UniProt residue coordinates are not asserted;
    * Rhea reactive-group RESIDUE nodes inside generic protein participants.

    The audit should still warn on under-modeled local nodes, so every STATE or
    RESIDUE that lacks both a grounding and one of those locality signals keeps
    getting reported.
    """
    if node.get("local") is True and node.get("description"):
        return False

    node_type = node.get("node_type")
    if node_type == "STATE" and node.get("description"):
        return False
    if node_type == "RESIDUE":
        label = str(node.get("label") or "")
        if node.get("description"):
            return False
        if "no UniProt position asserted" in label:
            return False
        if "UniProt position not established" in label:
            return False
    return True


def node_type_enum() -> set[str]:
    """The permissible CausalNodeTypeEnum values, read live from the schema so this
    audit never drifts from the source of truth."""
    try:
        schema = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
        pv = schema["enums"]["CausalNodeTypeEnum"]["permissible_values"]
        return set(pv)
    except (OSError, KeyError, yaml.YAMLError):
        return set()


def audit_record(rec: dict, rel: str, valid_types: set[str],
                 errors: list, warns: list[AuditWarning], stats: dict) -> None:
    graphs = rec.get("causal_graphs") or []
    if not isinstance(graphs, list):
        errors.append(f"{rel}: causal_graphs is not a list")
        return
    seen_graphs: set = set()
    for gi, g in enumerate(graphs):
        stats["graphs"] += 1
        where = f"{rel} graph[{gi}]"
        if not isinstance(g, dict):
            errors.append(f"{where}: not a mapping")
            continue
        gid = g.get("graph_id")
        if not gid:
            errors.append(f"{where}: missing graph_id")
        elif gid in seen_graphs:
            errors.append(f"{where}: duplicate graph_id {gid!r} in record")
        else:
            seen_graphs.add(gid)
        where = f"{rel} graph {gid or gi}"

        nodes = g.get("nodes") or []
        edges = g.get("edges") or []
        if not nodes:
            errors.append(f"{where}: no nodes")
        if not edges:
            errors.append(f"{where}: no edges")

        node_ids: set = set()
        for n in nodes:
            stats["nodes"] += 1
            if not isinstance(n, dict):
                errors.append(f"{where}: a node is not a mapping")
                continue
            nid = n.get("node_id")
            if not nid:
                errors.append(f"{where}: node missing node_id")
            elif nid in node_ids:
                errors.append(f"{where}: duplicate node_id {nid!r}")
            else:
                node_ids.add(nid)
            if not n.get("label"):
                errors.append(f"{where}: node {nid!r} missing label")
            nt = n.get("node_type")
            if not nt:
                errors.append(f"{where}: node {nid!r} missing node_type")
            elif valid_types and nt not in valid_types:
                errors.append(f"{where}: node {nid!r} bad node_type {nt!r}")
            gr = n.get("grounding")
            if gr and not CURIE.match(str(gr)):
                errors.append(f"{where}: node {nid!r} grounding {gr!r} not a CURIE")
            elif gr:
                stats["grounded"] += 1
            elif needs_grounding(n):
                warns.append(AuditWarning(
                    warning_key(rel, gid or gi, "ungrounded-node", str(nid)),
                    f"{where}: node {nid!r} has no grounding (label-only)",
                ))
            for x in (n.get("xrefs") or []):
                if not CURIE.match(str(x)):
                    errors.append(f"{where}: node {nid!r} xref {x!r} not a CURIE")

        for ei, e in enumerate(edges):
            stats["edges"] += 1
            if not isinstance(e, dict):
                errors.append(f"{where}: edge[{ei}] is not a mapping")
                continue
            subj, obj = e.get("subject"), e.get("object")
            for role, ref in (("subject", subj), ("object", obj)):
                if not ref:
                    errors.append(f"{where}: edge[{ei}] missing {role}")
                elif ref not in node_ids:
                    errors.append(f"{where}: edge[{ei}] {role} {ref!r} is not a "
                                  f"node_id in this graph (dangling)")
            if not e.get("predicate"):
                errors.append(f"{where}: edge[{ei}] missing predicate")
            pid = e.get("predicate_id")
            if pid and not CURIE.match(str(pid)):
                errors.append(f"{where}: edge[{ei}] predicate_id {pid!r} not a CURIE")
            elif not pid:
                warns.append(AuditWarning(
                    warning_key(rel, gid or gi, "missing-predicate-id", f"{subj}->{obj}"),
                    f"{where}: edge[{ei}] ({subj}->{obj}) has no predicate_id (RO)",
                ))
            ev = e.get("evidence") or []
            if not ev:
                errors.append(f"{where}: edge[{ei}] ({subj}->{obj}) has NO evidence")
            for evi in ev:
                if not isinstance(evi, dict) or not evi.get("reference"):
                    errors.append(f"{where}: edge[{ei}] evidence missing reference")
                elif evi.get("snippet"):
                    stats["snippet_edges"] += 1
                    break
            else:
                if ev:
                    warns.append(AuditWarning(
                        warning_key(rel, gid or gi, "missing-snippet", f"{subj}->{obj}"),
                        f"{where}: edge[{ei}] ({subj}->{obj}) has no verbatim snippet",
                    ))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*",
                    help="files or directories to audit (default: data/traits/**)")
    ap.add_argument("--file", help="[deprecated, use positional args] audit a single YAML file")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings (ungrounded node, no snippet/predicate_id) as failures")
    ap.add_argument("--warning-baseline", default="",
                    help="JSON pinning known warning identities, so a warning swap fails "
                         "even when the total count is unchanged")
    ap.add_argument("--update-warning-baseline", action="store_true",
                    help="rewrite --warning-baseline from the current warnings")
    ap.add_argument("--quiet", action="store_true", help="summary only")
    args = ap.parse_args()

    valid_types = node_type_enum()
    if not valid_types:
        print("warning: could not read CausalNodeTypeEnum from schema; "
              "node_type values will not be checked", file=sys.stderr)

    if args.file:
        paths = [Path(args.file)]
    elif args.paths:
        collected: list[Path] = []
        for raw in args.paths:
            p = Path(raw)
            if p.is_dir():
                collected.extend(sorted(p.rglob("*.yaml")))
            elif p.is_file():
                collected.append(p)
            else:
                print(f"Skipping missing path: {p}", file=sys.stderr)
        paths = sorted(collected)
    else:
        paths = sorted(p for p in TRAITS.rglob("*.yaml"))
    errors: list = []
    warns: list[AuditWarning] = []
    stats = {"records": 0, "graphs": 0, "nodes": 0, "edges": 0,
             "grounded": 0, "snippet_edges": 0}
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        if "causal_graphs:" not in text:
            continue
        try:
            rel = str(p.resolve().relative_to(REPO_ROOT))
        except ValueError:
            rel = str(p)                       # a --file outside the repo tree
        try:
            rec = yaml.safe_load(text)
        except yaml.YAMLError as e:
            errors.append(f"{rel}: YAML parse error ({e})")
            continue
        if not isinstance(rec, dict) or not rec.get("causal_graphs"):
            continue
        stats["records"] += 1
        audit_record(rec, rel, valid_types, errors, warns, stats)

    if not args.quiet:
        for w in warns:
            print(f"WARN  {w}")
        for e in errors:
            print(f"ERROR {e}")
    n = f"{stats['nodes']} nodes"
    print(f"causal-graph audit: {stats['records']} records, {stats['graphs']} graphs, "
          f"{n}, {stats['edges']} edges | "
          f"grounded nodes {stats['grounded']}/{stats['nodes']}, "
          f"snippet-cited edges {stats['snippet_edges']}/{stats['edges']} | "
          f"{len(errors)} errors, {len(warns)} warnings")
    rc = 1 if errors else 0
    if args.update_warning_baseline and not args.warning_baseline:
        print("\nFAIL: --update-warning-baseline needs --warning-baseline; on its own "
              "it writes nothing and would exit 0 as though it had.")
        return 1

    if args.warning_baseline:
        bpath = Path(args.warning_baseline)
        current = count_warnings(warns)
        if args.update_warning_baseline:
            known = json.loads(bpath.read_text(encoding="utf-8")) if bpath.exists() else {}
            fixed, new = diff_baseline(current, known)
            print(f"\nwarning baseline: {sum(known.values()):,} -> "
                  f"{sum(current.values()):,}  "
                  f"({len(fixed):,} FIXED, {len(new):,} NEW)")
            for key in new[:12]:
                print(f"  NEW    {key}")
            bpath.parent.mkdir(parents=True, exist_ok=True)
            bpath.write_text(json.dumps(current, indent=1, sort_keys=True) + "\n",
                             encoding="utf-8")
            print(f"warning baseline written -> {bpath}")
            if new:
                print("NOTE: newly-blessed warnings above. `git diff` the baseline before "
                      "committing -- this command can launder a regression.")
            return rc
        if not bpath.exists():
            print(f"\nFAIL: --warning-baseline {bpath} does not exist; run "
                  "--update-warning-baseline")
            return 1
        known = json.loads(bpath.read_text(encoding="utf-8"))
        fixed, new = diff_baseline(current, known)
        print(f"\nwarning baseline: {sum(known.values()):,} known · "
              f"{len(fixed):,} FIXED · {len(new):,} NEW")
        for key in new[:12]:
            print(f"  NEW    {key}")
        if new:
            print(f"\nFAIL: {len(new)} new causal-graph warning(s). Fix them, or bless "
                  "them with --update-warning-baseline and say why in the commit.")
            rc = 1
    elif args.strict and warns:
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
