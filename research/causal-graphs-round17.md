---
topic: causal-graphs
round: 17
date: 2026-07-30
target: function/FUNC_ENZYMATIC_ACTIVITY (Rhea) × structure/STRUCT_ACTIVE_SITE (M-CSA)
prior_round: causal-graphs-round16.md
---

# Causal graphs — Round 17: joining reaction chemistry to the residues that do it

Round 16 finished source coverage: every mechanism-rich source now carries graphs.
The backlog named the successor thread as **depth, not breadth** — and named it
wrongly. This round is the correction plus what could honestly be built instead.

| | round 16 | round 17 |
|---|--:|--:|
| corpus graphs | 39,647 | **40,115** |
| causal edges | 366,049 | **368,920** |
| snippet-cited | 100% | **100%** |
| errors | 0 | **0** |
| warnings | 5,845 | **5,845** (unchanged) |

427 Rhea records gained 468 `catalytic_residues` graphs / 2,871 edges.

## The gap, measured

Two mechanism subgraphs existed and never met. Counting edge shapes across the
M-CSA records:

| subject | predicate | object | n (sample of 200) |
|---|---|---|--:|
| RESIDUE | BFO:0000050 part of | MOTIF | 1,042 |
| RESIDUE | RO:0002436 interacts with | STATE (step) | 552 |
| STATE | RO:0002411 upstream of | STATE | 537 |
| MOLECULAR_FUNCTION | RO:0002233/4 input/output | CHEMICAL | 874 |

> **CORRECTION (2026-08-01, fact-check of this report).** This section originally
> read *"There is no `RESIDUE → CHEMICAL` edge anywhere in the corpus."* **That was
> false, and it was the load-bearing claim of the round.** The corpus already held
> **1,870** such edges across 230 records: 1,865 from MetalPDB (round 15 —
> residue coordinates a metal) and 5 hand-curated in two M-CSA β-lactamase records,
> including literally the edge this report says does not exist:
>
> ```
> ser70 (RESIDUE, UniProtKB:P62593) --[nucleophilic attack on / RO:0002436]--> substrate (CHEMICAL, CHEBI:35627)
> ```
>
> The error was generalising the table above — which its own header says is a
> **sample of 200 M-CSA records** — into a claim about the whole corpus, and then
> setting it in bold. A sample cannot support a universal negative. It also missed
> two records *inside* M-CSA, so even the restricted claim was wrong.

In the **seeder-generated M-CSA graphs this round joins**, residues connect to
mechanism steps and chemicals connect to the overall activity, and those halves meet
only at the top — so for 1,001 of the 1,003 M-CSA records, "which residues run this
reaction" had no answer in the graph structure. That is the gap this round closes.
It is neither a corpus-wide absence, as originally written, nor true of all 1,003:
`mcsa2` and `mcsa15` were hand-curated and already carry the edge.

## The premise I wrote into the backlog was wrong

`NEXT_TASKS.md` item 2 (written 2026-07-30, one day before this round) said the join
would let a graph answer *"which residue attacks which substrate"*. **It does not,
and M-CSA cannot support that claim.** Checked before building, not after:

- **Residue roles carry no target.** Each `residues[].roles` entry gives
  `function` (`proton acceptor`, `electrostatic stabiliser`, …), a `function_type`
  of `reactant` / `interaction` / `spectator`, and an EMO id — 55 distinct ones
  across 26,499 role annotations. **No field names a compound.**
- **`marvin_xml` is not arrow-pushing data.** The name suggests atom-mapped
  MarvinSketch XML, which would give per-atom attribution. It is a **filename**:
  maximum length **107 characters** across all 4,586 steps that have one.
- **The only place a residue and a compound co-occur is the free-text step
  description**, and there compounds appear as prose jargon — *"orientating the OSB
  C7 carboxylate group so that it can abstract the pro-2S proton"* — not by ChEBI
  name. Matching those strings would be our reading of the prose, not M-CSA's
  assertion.

So the round asserts what M-CSA does state: **this residue is causally responsible
for this reaction**, typed by M-CSA's own role classification. Every graph says so
in its description, so the limit is visible in the data and not only in this report.

## The join is verifiable, not merely inferable

All 1,003 M-CSA entries carry `reaction.compounds` with a `chebi_id` and a
`type: reactant|product`; Rhea gives every master reaction two ChEBI-typed sides.
So the join is checkable as **set equality**, in the same spirit as round 15's
BioLiP column-8/column-9 check and round 16's equation round-trip:

> an M-CSA entry matches a Rhea reaction when its reactant set **equals** one Rhea
> side and its product set **equals** the other.

EC agreement bounds the candidates but is never sufficient:

| outcome | n |
|---|--:|
| joined — exact ChEBI set equality | **472** |
| EC matched but ChEBI sets disagree — **dropped** | 289 |
| EC matches no Rhea reaction | 242 |
| **total M-CSA entries** | 1,003 |

The 289 dropped pairs are the point: an EC-only join would have written them, and
289/761 ≈ **38% of EC-agreeing pairs do not actually share chemistry**. Rhea and
M-CSA disagree about protonation states, cofactor inclusion and reaction granularity
often enough that EC alone is not a join key.

## Two disagreements recorded rather than reconciled

**47 matches are reverse-oriented** — M-CSA's reactants equal Rhea's `_R` side (42
records; some records carry more than one). Both sources are right: a Rhea master
reaction is deliberately undirected (round 16), and M-CSA curates the physiological
direction. Each such graph states the orientation in its evidence notes. Silently
flipping one to agree with the other would have destroyed the only signal that says
which direction an enzyme actually runs.

**35 reactions are curated by more than one M-CSA entry** (up to 4) — that is 35 of
the 430 reactions the join *matched*; the table below counts 34, because it covers
the 427 reactions actually *written* (4 M-CSA entries were dropped for having no
residue nodes to reuse). Both figures are right; they count different populations.
The first implementation wrote one graph per *reaction* and skipped ~43 entries as "already
wired" — a silent cap, and the wrong call: these are different enzymes, often
different folds, converging on the same chemistry. `graph_id` is now
`catalytic_residues_mcsa<id>`, one graph per entry.

| mechanisms on one reaction | records |
|---|--:|
| 1 | 393 |
| 2 | 28 |
| 3 | 5 |
| 4 | 1 |

`RHEA:15017` (`a phosphate monoester + H2O = an alcohol + phosphate`) now carries
four independently curated catalytic solutions — MCSA:43, 44, 454, 558.

## Graph design

Nodes: `activity` (MOLECULAR_FUNCTION, grounded to the Rhea record) · `mcsa`
(MOTIF, grounded to the `MCSA:` KB record) · one RESIDUE per catalytic residue,
grounded `UniProtKB:`.

Edges:

| edge | predicate | evidence |
|---|---|---|
| `activity` → `mcsa` | skos:closeMatch | `MCSA:<id>` + the verbatim `reaction.compounds` name/type list, with the set-equality proof in notes |
| `residue` → `activity` | RO:0002500 causal agent in process | `MCSA:<id>` + the residue's verbatim M-CSA role list, with the entry's `function_type` census and the join proof in notes |

**Residue nodes are reused verbatim, not re-derived.** Rounds 12–13 already resolved
every M-CSA residue's UniProt position through SIFTS. Copying those nodes means this
round introduces no new residue-numbering claim and cannot drift from the M-CSA
record it came from — the cheapest possible way to be right about the hardest part.

## Gates

`just validate-all data/traits/function/enzymatic_activity/rhea` → **18,558/18,558**.
`just audit-graphs` → 40,115 graphs · 347,473 nodes · 368,920 edges · **0 errors** ·
368,920/368,920 snippet-cited · **5,845 warnings, unchanged** (this round added no
ungrounded node).

## Open

- **The residue→substrate edge cannot be derived *from M-CSA at scale*, but it is
  not absent from the corpus** — see the correction above: 5 such edges exist,
  hand-curated, in two β-lactamase M-CSA records, and 1,865 residue→metal edges
  exist from MetalPDB. The open work is **generalising** what those five demonstrate
  to the other 1,001 M-CSA records, which needs a source that states the target
  compound per residue. Candidates: UniProt `ACT_SITE` comments naming the attacked
  bond, or MACiE/EzCatDB. Rhea's `rh:reactivePart` is *not* one — it describes
  generic `[protein]-…` participants, not catalytic residues.
  **Start by reading the two hand-curated records**, since they are an existing
  worked example of the target shape.
- **289 EC-agreeing pairs remain unjoined** because their ChEBI sets differ. Some are
  genuine granularity differences that a ChEBI-hierarchy-aware comparison (parent /
  conjugate-acid-base relations) could close; that needs the ChEBI ontology, which is
  already in `data/raw/chebi/`.
- **242 M-CSA entries have an EC that maps to no Rhea reaction** — a Rhea coverage
  gap, not fixable locally.
- **4 M-CSA entries had no residue nodes to reuse**, so their join is measured but
  not written.
- The 5,845 corpus warnings are unchanged and all inherited: 4,023 M-CSA STATE nodes,
  1,817 BioLiP fusion-chain residues, and 5 hand-curated label-only nodes (4 reaction
  intermediates in two β-lactamase M-CSA records, plus one `rrna` node in
  `function/resistance/aro/ermb-aro3000375.yaml`, which is not an intermediate —
  the group is often described as "5 intermediates", which is not quite right).
