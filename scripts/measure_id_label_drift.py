#!/usr/bin/env python3
r"""How far do our node labels drift from the ontology's own? (#493, for #484 item 5)

MEASUREMENT, NOT A GATE. `validate_id_label_correspondence.py` is vendored, governed by
`just check-vendored-sync`, and passing its 69 tests -- but it needs a config saying where
this repo keeps `(id, label)` pairs, and #493's whole point is that writing that config
before measuring produces a gate whose failures nobody can act on. This produces the
number the gate would be pinned to.

WHERE THE PAIRS ARE, measured rather than assumed
--------------------------------------------------
Only ONE surface in this corpus carries an id AND a label:

    causal_graphs[].nodes[]   grounding: CHEBI:15377   label: water

`parent_traits` is a bare CURIE list, and `trait_relations` / `mapped_xrefs` carry `object:`
with no label at all. An id with no label has no correspondence to check, so those three
are out of scope -- not deferred, not exempted: there is nothing there to validate. That
finding is why this script exists at all rather than a four-surface adapter.

WHICH PREFIXES ARE CHECKABLE
-----------------------------
Grounded+labelled nodes, by prefix (6,000-file sample): CHEBI 40.2%, UniProtKB 23.6%,
ARO 8.2%, GO 7.3%, RHEA 6.2%, EC 4.5%, RHEA-COMP 3.2%, CATH 1.8%, then a tail.

Only the ontologies among those have canonical labels to compare against. UniProtKB, RHEA,
EC, CATH, PROSITE, MCSA and pdb.ligand are DATABASES: their "label" is a protein or
reaction name that no ontology owns, so they belong in the vendored validator's
`ignored_prefixes`, where a typo'd prefix still fails as UNKNOWN_PREFIX.

Everything here reads `data/raw/` releases that are already fetched -- aro.obo, go.obo and
CHEBI's compounds.tsv.gz -- so the measurement needs no OAK download and no network. Like
the other release-reading audits it is therefore LOCAL ONLY (data/raw is gitignored).
"""

from __future__ import annotations

import argparse
import collections
import csv
import gzip
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "data" / "traits"
ARO_OBO = ROOT / "data" / "raw" / "aro" / "aro.obo"
GO_OBO = ROOT / "data" / "raw" / "go.obo"
CHEBI_TSV = ROOT / "data" / "raw" / "chebi" / "compounds.tsv.gz"
CHEBI_NAMES = ROOT / "data" / "raw" / "chebi" / "names.tsv.gz"

# Databases, not ontologies: their label is a protein/reaction/domain name no ontology
# owns. Listed so a typo'd ontology prefix is not quietly swept in with them.
NOT_ONTOLOGIES = {"UniProtKB", "RHEA", "RHEA-COMP", "EC", "CATH", "PROSITE", "MCSA",
                  "pdb.ligand", "proteintraitsmech", "Pfam", "InterPro", "PDB", "SCOP"}


def _norm(text: str) -> str:
    """Case- and space-insensitive, because a label differing only in those is not drift
    anyone needs to act on -- and counting it would bury the real mismatches."""
    return " ".join(str(text or "").split()).casefold()


def load_obo(path: Path) -> tuple[dict[str, str], dict[str, set[str]]]:
    """(id -> canonical name, id -> synonyms). Streamed; go.obo is 35 MB."""
    names: dict[str, str] = {}
    syns: dict[str, set[str]] = collections.defaultdict(set)
    cur = None
    syn_re = re.compile(r'^synonym:\s+"(.*?)"')
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("[Term]"):
            cur = None
        elif line.startswith("id: "):
            cur = line[4:].strip()
        elif cur and line.startswith("name: "):
            names[cur] = line[6:].strip()
        elif cur:
            m = syn_re.match(line)
            if m:
                syns[cur].add(m.group(1))
    return names, syns


def load_chebi() -> tuple[dict[str, str], dict[str, set[str]]]:
    names: dict[str, str] = {}
    syns: dict[str, set[str]] = collections.defaultdict(set)
    if CHEBI_TSV.exists():
        with gzip.open(CHEBI_TSV, "rt", encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                # lowercase columns, checked against the release header rather than
                # guessed: compounds.tsv.gz is id/name/.../chebi_accession
                cid, nm = row.get("chebi_accession") or row.get("id"), row.get("name")
                if cid and nm and nm != "null":
                    names[cid if ":" in str(cid) else f"CHEBI:{cid}"] = nm
    if CHEBI_NAMES.exists():
        with gzip.open(CHEBI_NAMES, "rt", encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                cid, nm = row.get("compound_id"), row.get("name")
                if cid and nm:
                    syns[f"CHEBI:{cid}"].add(nm)
    return names, syns


def classify(curie: str, label: str, names: dict, syns: dict) -> str:
    if curie not in names:
        return "ID_NOT_FOUND"
    if _norm(label) == _norm(names[curie]):
        return "OK_CANONICAL"
    if _norm(label) in {_norm(s) for s in syns.get(curie, ())}:
        return "OK_SYNONYM"
    return "MISMATCH"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", default=str(TRAITS))
    ap.add_argument("--show", type=int, default=8)
    args = ap.parse_args()

    sources: dict[str, tuple[dict, dict]] = {}
    if ARO_OBO.exists():
        sources["ARO"] = load_obo(ARO_OBO)
    if GO_OBO.exists():
        sources["GO"] = load_obo(GO_OBO)
    chebi = load_chebi()
    if chebi[0]:
        sources["CHEBI"] = chebi
    if not sources:
        # #418/#432/#469: a sweep with no label source would report 0 mismatches and exit
        # 0, which reads as a clean corpus.
        print("FAIL: no local label source found (aro.obo / go.obo / chebi). "
              "Run the matching `just fetch-*` first; this cannot certify anything.")
        return 1
    print("label sources: " + ", ".join(f"{k} ({len(v[0]):,} terms)"
                                        for k, v in sorted(sources.items())))

    verdicts: collections.Counter = collections.Counter()
    by_prefix: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    examples: dict[str, list] = collections.defaultdict(list)
    pairs = skipped_db = unknown = 0

    for path in Path(args.path).rglob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        if "grounding:" not in text:
            continue
        try:
            doc = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            continue
        for graph in doc.get("causal_graphs") or []:
            for node in graph.get("nodes") or []:
                curie, label = node.get("grounding"), node.get("label")
                if not curie or not label or ":" not in str(curie):
                    continue
                pairs += 1
                prefix = str(curie).split(":")[0]
                if prefix in NOT_ONTOLOGIES:
                    skipped_db += 1
                    continue
                if prefix not in sources:
                    unknown += 1
                    by_prefix[prefix]["NO_SOURCE"] += 1
                    continue
                names, syns = sources[prefix]
                verdict = classify(str(curie), str(label), names, syns)
                verdicts[verdict] += 1
                by_prefix[prefix][verdict] += 1
                if verdict in ("MISMATCH", "ID_NOT_FOUND") and len(examples[prefix]) < args.show:
                    examples[prefix].append((path.name, curie, label,
                                             names.get(str(curie), "—")))

    checked = sum(verdicts.values())
    print(f"\ngrounded+labelled causal nodes : {pairs:,}")
    print(f"  database prefixes, no ontology: {skipped_db:,}  (UniProtKB, RHEA, EC, …)")
    print(f"  ontology prefix, no local source: {unknown:,}")
    print(f"  CHECKED                       : {checked:,}")
    if not checked:
        print("FAIL: nothing was checked, so the 0 above means nothing.")
        return 1
    for verdict, n in verdicts.most_common():
        print(f"    {n:>7,}  ({100 * n / checked:5.1f}%)  {verdict}")

    print("\nby prefix:")
    for prefix in sorted(by_prefix, key=lambda p: -sum(by_prefix[p].values())):
        counts = by_prefix[prefix]
        tot = sum(counts.values())
        detail = "  ".join(f"{k} {v:,}" for k, v in counts.most_common())
        print(f"  {prefix:<12} {tot:>7,}   {detail}")

    for prefix, rows in sorted(examples.items()):
        print(f"\n{prefix} examples (label on disk vs the ontology's):")
        for name, curie, label, canonical in rows:
            print(f"  {curie}  ours={label!r}")
            print(f"      ontology={canonical!r}   ({name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
