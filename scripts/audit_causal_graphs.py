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
    • a node with no `grounding` (label-only draft node — allowed in v1);
    • an edge whose evidence carries no verbatim `snippet`;
    • an edge with no `predicate_id` (RO CURIE).

Read-only. Stdlib + PyYAML. Exit 1 on any ERROR (or WARNING under --strict), else 0.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS = REPO_ROOT / "data" / "traits"
SCHEMA = REPO_ROOT / "src" / "proteintraitsmech" / "schema" / "proteintraitsmech.yaml"
CURIE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*:[A-Za-z0-9._-]+$")


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
                 errors: list, warns: list, stats: dict) -> None:
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
            else:
                warns.append(f"{where}: node {nid!r} has no grounding (label-only)")
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
                warns.append(f"{where}: edge[{ei}] ({subj}->{obj}) has no predicate_id (RO)")
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
                    warns.append(f"{where}: edge[{ei}] ({subj}->{obj}) has no verbatim snippet")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", help="audit a single YAML file instead of data/traits/**")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings (ungrounded node, no snippet/predicate_id) as failures")
    ap.add_argument("--quiet", action="store_true", help="summary only")
    args = ap.parse_args()

    valid_types = node_type_enum()
    if not valid_types:
        print("warning: could not read CausalNodeTypeEnum from schema; "
              "node_type values will not be checked", file=sys.stderr)

    paths = ([Path(args.file)] if args.file
             else sorted(p for p in TRAITS.rglob("*.yaml")))
    errors: list = []
    warns: list = []
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
    if errors or (args.strict and warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
