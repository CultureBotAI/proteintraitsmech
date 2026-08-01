---
topic: causal-graphs
round: 16
date: 2026-07-30
target: function/FUNC_ENZYMATIC_ACTIVITY — Rhea (18,558) + EC (7,375)
prior_round: causal-graphs-round15.md
---

# Causal graphs — Round 16: reaction chemistry

Round 15 closed by naming the last mechanism-rich source with no graphs: Rhea/EC
reaction chemistry, 26,003 `FUNC_ENZYMATIC_ACTIVITY` records. This round covers it.

Rounds 12–13 did catalysis (M-CSA), 14 resistance (CARD/ARO), 15 interaction
(BioLiP/MetalPDB). This is the fourth kind of mechanism the schema is for —
**transformation**: these substrates become those products.

| | round 15 | round 16 |
|---|--:|--:|
| corpus graphs | 14,201 | **39,647** |
| causal edges | 183,050 | **366,049** |
| snippet-cited | 100% | **100%** |
| grounded nodes | 338,289 / 344,134 (this round: 208,445 / 208,445) | |
| errors | 0 | **0** |
| warnings | 5,845 | **5,845** (unchanged) |

Rhea: 18,558 records / 121,909 edges. EC: 6,888 records / 61,090 edges.
Every one of the 182,999 new edges carries a verbatim snippet, an RO/SKOS
`predicate_id`, and grounded endpoints — the warning count did not move.

## Gap (from the audit, before this round)

| source | category | n | w/graph | w/ev |
|---|---|--:|--:|--:|
| rhea | FUNC_ENZYMATIC_ACTIVITY | 18,558 | 0 | 17,615 |
| ec | FUNC_ENZYMATIC_ACTIVITY | 7,375 | 0 | 0 |
| metpo | FUNC_ENZYMATIC_ACTIVITY | 70 | 0 | 0 |

## The problem this round had to solve: Rhea does not state a direction

A Rhea **master** reaction is deliberately undirected —
`pentanamide + H2O = pentanoate + NH4(+)`, an `=` and not an arrow. That is why
`seed_rhea.py` could only write `role: SUBSTRATE_OR_PRODUCT` on every participant,
and it is a real obstacle to a *causal* graph: an edge needs to know which side is
consumed. Calling the left side "substrates" would have been our claim, not Rhea's.

Rhea does make that claim, just on a different entity. Every master has a
**left-to-right directional child** whose RDF says exactly this:

```xml
<rdf:Description rdf:about="http://rdf.rhea-db.org/10001">
	<rh:substrates rdf:resource="http://rdf.rhea-db.org/10000_L"/>
	<rh:products   rdf:resource="http://rdf.rhea-db.org/10000_R"/>
</rdf:Description>
```

So every `has input` / `has output` edge in this round is cited to the directional
child (`RHEA:10001`), not to the master, and its snippet is that child's own
`rh:equation` — the one written with `=>`. The graph description says in words that
the master is undirected and that Rhea curates the reverse direction too, so nothing
here asserts that the reaction only runs one way.

This is the same discipline as rounds 12–13 and 15 — *cite the entity that actually
makes the claim* — reaching a different mechanism because the source is shaped
differently.

## Why the RDF and not the TSV

`rhea-reactions.tsv`, which the seeder used, gives one flat semicolon-joined ChEBI
list per reaction. It cannot express sides, so it could not have supported this round
at all. `rhea.rdf.gz` was already fetched and carries everything a graph needs:

| RDF | what it gives |
|---|---|
| `rh:side` → `10000_L` / `10000_R` | which participants are on which side |
| `rh:substrates` / `rh:products` | which side is consumed (on the directional child) |
| `rh:contains<N>` | stoichiometric coefficient (`contains1`, `containsN`, `contains2n`, …) |
| `rh:location` → `In` / `Out` | the membrane side of a transported participant |
| `rh:reactivePart` | for `[protein]-…` participants, the amino-acid residue that reacts |
| `rdfs:seeAlso GO_…`, `rh:ec` | the equivalent GO molecular function and the EC class |
| `rh:citation` | PubMed ids |

New reader: `scripts/rhea_rdf.py` (stdlib, streams 3.03M lines in ~5s).

## Verification without the network: the equation must round-trip

Rhea states each reaction **twice** — once as the `rh:equation` string, once as the
`rh:side` / `rh:contains<N>` / `rh:location` participant structure. That redundancy
is a free and total correctness check, the analogue of round 15's BioLiP
column-8/column-9 residue check: re-render the structure and it must reproduce the
equation *character for character*, including coefficient rendering (`1` → nothing,
`N` → `n`), participant order, and transport suffixes (`sulfate(out)`).

**All 18,558 seeded master reactions round-trip exactly.** No side assignment written
this round is a guess, and a reaction that failed would have been skipped rather than
written. The check is inside both builders, not just in this analysis.

## Graph design

**Rhea record** (`graph_id: reaction_chemistry`) — e.g. `RHEA:10192`,
`sulfate(out) + ATP + H2O = sulfate(in) + ADP + phosphate + H(+)`:

| node | type | grounding |
|---|---|---|
| `activity` | MOLECULAR_FUNCTION | `RHEA:10192` (the record itself) |
| `sub1…` / `prd1…` | CHEMICAL / PROTEIN / NUCLEIC_ACID | `CHEBI:…`, else `RHEA-COMP:…` |
| `sub2_rp1…` | RESIDUE | the reactive part's `CHEBI:…` |
| `go` | MOLECULAR_FUNCTION | `GO:0015419` (a KB record) |
| `ec1` | MOLECULAR_FUNCTION | `EC:7.3.2.3` (a KB record) |
| `prot_*` | PROTEIN | `UniProtKB:…` |

| edge | predicate | evidence |
|---|---|---|
| `activity` → `subN` | has input · RO:0002233 | `RHEA:<LR>` + the LR `rh:equation` |
| `activity` → `prdN` | has output · RO:0002234 | `RHEA:<LR>` + the LR `rh:equation` |
| `subN_rpK` → `subN` | part of · BFO:0000050 | `RHEA:<master>` + the reactive part's `rh:name` |
| `activity` → `go` | skos:closeMatch | the verbatim `rdfs:seeAlso` triple |
| `activity` → `ec1` | skos:broadMatch | the verbatim `rh:ec` triple |
| `prot_*` → `activity` | enables · RO:0002327 | the ExPASy `DR` line **and** the `rh:ec` triple |

**EC record** — same shape, anchored on `EC:x.x.x.x`, GO from the `ec2go` line,
exemplar enzymes from the `DR` lines, chemistry borrowed from Rhea (below).

## What is cited, and the rule that keeps it non-circular

Round 15's rule — **do not quote yourself** — applies unchanged. Every one of these
records already contains a fluent sentence describing the reaction, written by our
own seeder; quoting it as the snippet would have been evidence for our own claim.

| edge kind | snippet |
|---|---|
| has input / has output | the directional child's `rh:equation`, verbatim |
| residue `part of` protein | the reactive part's `rh:name` (`L-cysteine residue`) |
| GO cross-reference | the verbatim `<rdfs:seeAlso …GO_0050168"/>` triple |
| EC cross-reference | the verbatim `<rh:ec …enzyme/3.5.1.50"/>` triple |
| protein `enables` | the verbatim ExPASy `DR` line |
| EC → GO | the verbatim `ec2go` mapping line |

Two of these are RDF triples rather than prose. They are the source's own statement
of exactly the claim the edge makes, and they are checkable against a file in
`data/raw/`, which is the standard round 15 set for data-shaped evidence — but they
are **reconstructed** from the parsed value rather than captured as raw text, so they
are byte-identical to the release by construction and not by capture. Worth stating
plainly rather than implying a stronger provenance than exists.

Rhea's `rh:citation` PMIDs travel in the edge `notes`, never as `reference`, on the
standing rule from round 12: a PMID becomes a reference when someone has read the
paper. 17,615 Rhea records carry at least one.

## Where the chemistry runs through protein traits

A reaction record is the hardest case yet for the requirement that a graph route
through the KB's own protein traits — its participants are metabolites, not proteins.
Three routes were available and all three are used:

1. **`[protein]-…` participants are protein traits.** Rhea models
   `[protein]-dithiol` as a *generic polypeptide* and names the residue that actually
   reacts: `rh:reactivePart` at position C1 = `L-cysteine residue` (`CHEBI:29950`),
   becoming `[protein]-disulfide` with an `L-cystine residue` (`CHEBI:50058`). Those
   become RESIDUE nodes with a `part of` edge into the protein participant —
   3,364 Rhea and 1,158 EC records. The label says no position on any specific
   protein sequence is asserted, because Rhea asserts none.
2. **The GO molecular function and EC class are KB records.** 6,949 Rhea graphs carry
   a `GO:` node and 7,635 an `EC:` node that resolve to real trait records, so the
   reaction is wired to the FUNCTION-axis traits that describe the same catalysis.
3. **Exemplar enzymes.** 4,194 Rhea and 5,784 EC graphs carry `UniProtKB:` PROTEIN
   nodes with an `enables` edge, from ExPASy ENZYME's `DR` cross-references.

## Two places where the honest answer was to write less

**Exemplar proteins on Rhea records.** ExPASy names proteins per *EC class*, and Rhea
assigns reactions to EC classes, so a protein can be attached to a reaction in two
hops. But an EC class that maps to several Rhea reactions does not say which one a
given protein runs. So `enables` edges are written **only for the 5,136 EC classes
that map to exactly one Rhea master reaction**; for the rest, no exemplar protein is
written and the graph says so.

**Chemistry on EC records.** Same asymmetry, mirrored:

| EC record | n | what the graph does |
|---|--:|---|
| maps to exactly 1 Rhea reaction | 5,136 | inputs/outputs hang directly off the EC activity node |
| maps to several (up to 3 shown) | 1,063 | one node per reaction, grounded to its `RHEA:` KB record, `skos:narrowMatch` from the class; the class node never claims a substrate only one of its reactions consumes |
| maps to none | 689 | exemplar enzymes and GO equivalence only; no substrate asserted |

ExPASy's own `CA` line (`RH + Br(-) + H2O2 = RBr + 2 H2O`) is free text with no ChEBI
behind it, so parsing it into participants would have been our reading, not the
source's. It is quoted in the graph *description* so the two can be compared, and it
never underpins an edge.

## Two parser bugs, and which one would have been dangerous

**Every participant was counted twice.** Rhea states each one as both a bare
`rh:contains` and a suffixed `rh:contains1` / `containsN`. My first regex,
`contains([A-Za-z0-9]*)`, matched both and appended both, so `RHEA:10000` came out
with four participants instead of two — *and* the bare form's defaulted coefficient
of `1` overwrote the real `N` on polymerisation reactions.

**Directional reactions leaked into the master dict.** The RDF declares a subject's
class partway through its block, and I created a master-reaction record on first
sight of any reaction-ish property. Masters came out as 74,528 instead of 18,854.

Both were loud: 74,528 against an expected ~19k, and duplicated participants visible
in the first smoke test. The coefficient corruption underneath the first bug was
**not** loud — `1` instead of `n` on a polymer reaction is a plausible-looking wrong
number, and it is exactly the kind of error the round-15 report worried about. What
caught it was not the smoke test but the equation round-trip check, which fails on a
wrong coefficient because Rhea renders the coefficient into the equation string. That
argues for building the redundancy check *before* trusting any of the parse, not
after.

## One decision reversed mid-round

The first Rhea pass left 6,985 nodes ungrounded — Rhea's generic participants
(`[protein]-dithiol`, polymers) have no ChEBI of their own. I had put Rhea's internal
accession in `xrefs` and left `grounding` empty.

Round 15 had already settled this: BioLiP's ligand node falls back to
`pdb.ligand:<CCD>` when no ChEBI is found, on the grounds that a real source
identifier beats a label-only node. Following that precedent, the fallback is
`RHEA-COMP:10594` — the identifier UniProt and bioregistry use for Rhea compounds,
rather than Rhea's internal `GENERIC:10594` spelling, which is kept in the node
description. The 18,558 records were reverted with `git checkout` and rebuilt.

Result: **0 ungrounded nodes** from this round, and the corpus warning count is
unchanged at 5,845.

## Where the corpus stands

| source | records w/ graph | round |
|---|--:|--:|
| Rhea | 18,558 | 16 |
| ARO / CARD | 7,399 | 14 |
| EC | 6,888 | 16 |
| BioLiP | 5,571 | 15 |
| M-CSA | 1,003 | 12–13 |
| MetalPDB | 228 | 15 |
| **total** | **39,647** | |

344,134 nodes, 366,049 edges, 0 errors, 5,845 warnings — all warnings inherited from
earlier rounds (4,023 M-CSA STATE nodes, 1,817 BioLiP fusion-chain residues, 5
hand-curated label-only nodes — 4 reaction intermediates plus one `rrna` node that
is not an intermediate). `just validate-all data/traits/function/enzymatic_activity`
passes 26,003/26,003.

## Open

- **`chemical_participants` still says `SUBSTRATE_OR_PRODUCT` on all 18,558 Rhea
  records.** That is correct for an undirected master, but the graph now carries side
  information the record's own field cannot express, so the two disagree in
  informativeness. Either the seeder should gain a directional variant or the field
  should defer to the graph — a schema question, not a curation one.
- **70 METPO records** in `FUNC_ENZYMATIC_ACTIVITY` (acetogenesis, aerobic
  respiration) got no graph and should not have: they are metabolic strategies, not
  enzymatic activities. That looks like a mis-categorisation for
  `review-source-categories` rather than a gap for this skill.
- **689 EC records have no Rhea reaction**, so they assert no chemistry. Rhea covers
  the EC hierarchy incompletely; nothing local fixes this.
- **487 EC records got no graph at all** — 410 class-level nodes (`EC:1.1.1.-`), 77
  leaf entries with no reaction, no `DR` protein and no GO mapping.
- **1,063 multi-reaction EC classes show at most 3 of their reactions.** The cap is
  stated in each graph's description; it is a display choice, not a data limit.
- The mechanism-rich sources are now all covered. The next frontier is not a new
  source but **depth**: M-CSA's stepwise arrow-pushing is transcribed only for the
  1,003 M-CSA records, and nothing yet links a Rhea reaction's chemistry to the
  catalytic residues that perform it — the Rhea↔M-CSA join is the obvious round 17.
