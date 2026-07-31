#!/usr/bin/env python3
"""Streaming reader for the Rhea RDF release (`data/raw/rhea/rhea.rdf.gz`).

Shared by `build_rhea_causal_graphs.py` and `build_ec_causal_graphs.py`.

Why the RDF and not `rhea-reactions.tsv`: the TSV gives one flat ChEBI list per
reaction, which is why the seeder could only write `role: SUBSTRATE_OR_PRODUCT`.
The RDF is the only Rhea export that states **which side each participant is on**
(`rh:side` → `<id>_L` / `<id>_R`), **which side is the substrate side**
(`rh:substrates` / `rh:products` on the directional child reaction), the
stoichiometric coefficient (`rh:contains<N>`), the membrane side of a transported
participant (`rh:location`), and — for `[protein]-…` participants — the reactive
amino-acid residue (`rh:reactivePart`). All of that is what a causal graph needs.

The file is ~3M lines of flat `rdf:Description` blocks whose subjects repeat and
whose type is only declared partway through the block, so this reads line by line,
accumulates per subject, and sorts subjects into masters / directional children at
the end.

Stdlib only.
"""

from __future__ import annotations

import gzip
import html
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RDF = REPO / "data" / "raw" / "rhea" / "rhea.rdf.gz"

_ABOUT = re.compile(r'rdf:about="http://rdf\.rhea-db\.org/([^"]+)"')
# rh:contains<coefficient> must be tested BEFORE the generic resource pattern,
# which would otherwise match it and drop the coefficient on the floor.
_CONTAINS = re.compile(r'<rh:contains([A-Za-z0-9]*) rdf:resource='
                       r'"http://rdf\.rhea-db\.org/(Participant_[^"]+)"')
_RES = re.compile(r"<(rh:[A-Za-z0-9]+|rdfs:subClassOf|rdfs:seeAlso) "
                  r'rdf:resource="([^"]+)"')
_LIT = re.compile(r"<(rh:[A-Za-z0-9]+|rdfs:label|rdfs:comment)"
                  r"(?: rdf:datatype=\"[^\"]+\")?>(.*?)</\1>")
_RP_ID = re.compile(r"^Compound_\d+_rp\d+$")

# compound class → CausalNodeTypeEnum
KIND_TO_NODE_TYPE = {
    "SmallMolecule": "CHEMICAL",
    "GenericSmallMolecule": "CHEMICAL",
    "GenericCompound": "CHEMICAL",
    "GenericHeteropolysaccharide": "CHEMICAL",
    "Polymer": "CHEMICAL",
    "GenericPolypeptide": "PROTEIN",
    "GenericPolynucleotide": "NUCLEIC_ACID",
}
_REACTION_CLASSES = {"Reaction", "DirectionalReaction", "BidirectionalReaction"}


def _text(v: str) -> str:
    """Unescape an RDF literal and flatten whitespace.

    Rhea's `rh:name` is plain text (markup lives in `rh:htmlName`), but names
    carry numeric entities for Greek letters and arrows (`&#946;`, `&#8594;`),
    so they still need unescaping before they can be used as a node label.
    """
    return " ".join(html.unescape(v).split())


class Rhea:
    """Parsed Rhea RDF. Attributes are plain dicts keyed by the RDF local name."""

    def __init__(self) -> None:
        self.compounds: dict[str, dict] = {}      # "4808" -> compound
        self.rparts: dict[str, dict] = {}         # "Compound_10594_rp1" -> part
        self.participants: dict[str, dict] = {}   # participant id -> {compound, location}
        self.sides: dict[str, dict] = {}          # "10000_L" -> {participant: coef}
        self.reactions: dict[str, dict] = {}      # "10000" -> master (undirected)
        self.directional: dict[str, dict] = {}    # "10001" -> directional / bidirectional

    def participants_of(self, side_id: str) -> list[tuple[dict, str, dict]]:
        """[(compound, coefficient, participant)] for a reaction side, in file order."""
        out = []
        for pid, coef in self.sides.get(side_id, {}).items():
            part = self.participants.get(pid) or {}
            comp = self.compounds.get(part.get("compound", ""))
            if comp:
                out.append((comp, coef, part))
        return out

    def reactive_parts(self, comp: dict) -> list[dict]:
        """The named amino-acid / nucleotide residues of a `[protein]-…` participant."""
        return [self.rparts[r] for r in comp.get("reactive_parts", []) if r in self.rparts]

    def lr_child(self, rxn: dict) -> dict | None:
        """The left-to-right directional child, i.e. the entry in which Rhea itself
        declares side `_L` to be the substrates. Direction is not a property of the
        master reaction, so every directional claim in a graph is cited to this."""
        for d in rxn.get("directional", []):
            child = self.directional.get(d)
            if child and child.get("substrates", "").endswith("_L"):
                return child
        return None


def load(path: Path | None = None) -> Rhea:
    r = Rhea()
    ents: dict[str, dict] = {}   # every numeric subject, sorted into masters later
    path = path or RDF
    opener = gzip.open if str(path).endswith(".gz") else open
    cur = ""
    with opener(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = _ABOUT.search(line)
            if m:
                cur = m.group(1)
                continue
            if cur:
                _absorb(r, ents, cur, line)

    for rid, e in ents.items():
        (r.reactions if e.get("class") == "Reaction" else r.directional)[rid] = e
    return r


def _ent(ents: dict, rid: str) -> dict:
    return ents.setdefault(rid, {
        "id": rid, "class": "", "accession": f"RHEA:{rid}", "equation": "",
        "transport": False, "balanced": None, "go": [], "ec": [], "pmids": [],
        "sides": [], "directional": [], "comment": "",
    })


def _comp(r: Rhea, cid: str) -> dict:
    return r.compounds.setdefault(cid, {
        "id": cid, "name": "", "accession": "", "kind": "", "reactive_parts": [],
    })


def _absorb(r: Rhea, ents: dict, cur: str, line: str) -> None:
    is_rxn = cur.isdigit()
    is_comp = cur.startswith("Compound_") and not _RP_ID.match(cur)
    is_rp = bool(_RP_ID.match(cur))
    cid = cur.split("_", 1)[1] if is_comp else ""

    m = _CONTAINS.search(line)
    if m:
        # Every participant is stated twice: once as bare `rh:contains` and once as
        # `rh:contains<coefficient>` (`contains1`, `containsN`, `contains2n`, …).
        # Only the suffixed form carries the stoichiometry, so it wins; the bare
        # form is kept as a fallback for the handful of participants that have no
        # suffixed statement, and never overwrites a real coefficient with "1".
        side, coef, pid = r.sides.setdefault(cur, {}), m.group(1), m.group(2)
        if coef:
            side[pid] = coef
        else:
            side.setdefault(pid, "1")
        return

    m = _RES.search(line)
    if m:
        prop, local = m.group(1), m.group(2).rsplit("/", 1)[-1]
        if prop == "rdfs:subClassOf":
            if is_rxn and local in _REACTION_CLASSES:
                _ent(ents, cur)["class"] = local
            elif is_comp and local in KIND_TO_NODE_TYPE:
                _comp(r, cid)["kind"] = local
        elif prop == "rdfs:seeAlso" and local.startswith("GO_") and is_rxn:
            _ent(ents, cur)["go"].append(local.replace("_", ":"))
        elif prop == "rh:ec" and is_rxn:
            _ent(ents, cur)["ec"].append(local)
        elif prop == "rh:citation" and is_rxn and local.isdigit():
            _ent(ents, cur)["pmids"].append(local)
        elif prop == "rh:side" and is_rxn:
            _ent(ents, cur)["sides"].append(local)
        elif prop == "rh:directionalReaction" and is_rxn:
            _ent(ents, cur)["directional"].append(local)
        elif prop in ("rh:substrates", "rh:products") and is_rxn:
            _ent(ents, cur)[prop.split(":")[1]] = local
        elif prop == "rh:compound":
            r.participants.setdefault(cur, {})["compound"] = local.split("_", 1)[1]
        elif prop == "rh:location":
            r.participants.setdefault(cur, {})["location"] = local
        elif prop in ("rh:chebi", "rh:underlyingChebi"):
            curie = local.replace("_", ":")
            if is_rp:
                r.rparts.setdefault(cur, {"id": cur})["chebi"] = curie
            elif is_comp:
                _comp(r, cid).setdefault("chebi", curie)
        elif prop == "rh:reactivePart" and is_comp:
            _comp(r, cid)["reactive_parts"].append(local)
        return

    m = _LIT.search(line)
    if not m:
        return
    prop, val = m.group(1), _text(m.group(2))
    if prop == "rh:accession" and is_comp:
        _comp(r, cid)["accession"] = val
    elif prop == "rh:name":
        if is_rp:
            r.rparts.setdefault(cur, {"id": cur})["name"] = val
        elif is_comp:
            _comp(r, cid)["name"] = val
    elif prop == "rh:position" and is_rp:
        r.rparts.setdefault(cur, {"id": cur})["position"] = val
    elif prop == "rh:formula":
        if is_rp:
            r.rparts.setdefault(cur, {"id": cur})["formula"] = val
        elif is_comp:
            _comp(r, cid)["formula"] = val
    elif prop == "rh:polymerizationIndex" and is_comp:
        _comp(r, cid)["polymer_index"] = val
    elif is_rxn:
        e = _ent(ents, cur)
        if prop == "rh:equation":
            e["equation"] = val
        elif prop == "rh:isTransport":
            e["transport"] = (val == "true")
        elif prop == "rh:isChemicallyBalanced":
            e["balanced"] = (val == "true")
        elif prop == "rdfs:comment":
            e["comment"] = val


if __name__ == "__main__":  # smoke test
    import sys
    rh = load()
    print(f"masters={len(rh.reactions):,} directional={len(rh.directional):,} "
          f"compounds={len(rh.compounds):,} sides={len(rh.sides):,} "
          f"participants={len(rh.participants):,} reactive_parts={len(rh.rparts):,}",
          file=sys.stderr)
    for rid in ("10000", "10192", "10008", "10068"):
        rxn = rh.reactions.get(rid)
        if not rxn:
            print(f"\nRHEA:{rid} MISSING")
            continue
        print(f"\nRHEA:{rid}  {rxn['equation']}")
        print(f"  transport={rxn['transport']} balanced={rxn['balanced']} "
              f"go={rxn['go']} ec={rxn['ec']} pmids={rxn['pmids'][:3]}")
        for side in rxn["sides"]:
            for comp, coef, part in rh.participants_of(side):
                rp = "; ".join(f"{p.get('position', '-')}:{p.get('name')}"
                               f"({p.get('chebi')})" for p in rh.reactive_parts(comp))
                print(f"    {side} {coef} x {comp['accession']:<16} {comp['name'][:44]!r}"
                      f" chebi={comp.get('chebi')} loc={part.get('location')}"
                      + (f" rp[{rp}]" if rp else ""))
        lr = rh.lr_child(rxn)
        print(f"    LR child: {lr and lr['accession']} substrates={lr and lr.get('substrates')}"
              f" eq={lr and lr.get('equation')!r}")
