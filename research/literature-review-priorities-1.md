---
topic: literature-review-priorities
round: 1
date: 2026-07-29
question: where does literature review add / validate / correct the most content?
method: corpus measurement (408,978 records, 7,401 graphs, 65,093 edges) + source-cache inspection
---

# Where literature review pays off most

Measured rather than assumed. Every number below comes from the corpus or the
seeded source caches on disk, not from the backlog's own account of itself.

## Corpus state

| | |
|---|--:|
| records | 408,978 |
| `SEEDED` / `REVIEWED` | 402,796 / **6,182** |
| records with a causal graph | **7,401** (1.8%) |
| causal edges | 65,093 |
| records with ≥1 PMID | 84,217 |
| definitions ≥25 chars | 405,425 (**99.1%**) |

Two facts set the agenda. Definitions are effectively done, so
`edison-trait-definitions` has almost no volume left. And **every mechanism
graph in the corpus is antibiotic resistance** — 7,399 of 7,401, with 2 M-CSA
catalysis graphs. The KB has no catalytic mechanism content at all.

## Rank 1 — M-CSA catalytic mechanisms (the largest high-impact ADD)

**1,001 of 1,003 M-CSA records carry no causal graph**, and the material to
build them is already fetched and sitting in `data/raw/mcsa.entries.jsonl`:

| | |
|---|--:|
| entries | 1,003 (all with ≥1 mechanism) |
| curated mechanism steps | **4,881** |
| — inside `is_detailed` mechanisms | 4,575 |
| mechanisms rated 3 (highest) | 950 of 1,166 |
| literature references | **5,593** (median 4/mechanism) |
| catalytic residues | 5,248 (median 5/entry) |
| records already carrying PMIDs | 1,000 |
| records already carrying EC | 1,003 |
| records with ACT_SITE residue features | 606 |

Three things make this unusually cheap per unit of value:

1. **The step descriptions are already causal statements.** Verbatim from the
   cache: *"Asp7 deprotonates Cys70, activating it."* That is a `CausalEdge` —
   subject `Asp7`, object `Cys70`, an RO predicate, and the mechanism's own
   references as `EvidenceItem`. The literature work is verification and
   grounding, not discovery.
2. **Residues carry `domain_cath_id`.** Each catalytic residue names its CATH
   domain, so edges can be routed through the KB's existing fold and active-site
   records rather than through free-floating ontology terms — the standing
   principle that causation must run through real trait records.
3. **The seeder already discarded it once.** `seed_mcsa.py` reads
   `reaction.mechanisms` only to harvest `pubmed_id`; `steps`, `mechanism_text`
   and the residue roles are parsed and dropped. Nothing needs re-fetching.

Impact beyond volume: this is the deepest mechanistic content the schema can
hold, it is the case `edison-causal-graphs` names as its first priority, and it
would end the corpus's current state of being 100% resistance mechanism.

## Rank 2 — Two systematic defects in the existing 7,401 graphs (the cheapest CORRECT)

These are not scattered quality problems. They are uniform, which means one
decision fixes each of them across the whole corpus:

| defect | count | scope |
|---|--:|---|
| `resistance -> drug` edges with no RO `predicate_id` | **12,581** | **100%** of that edge type |
| `resistance` nodes with no grounding | **7,399** | **one in every graph** |
| edges with no verbatim snippet | 5,112 | concentrated in the 1,219 drafts |

The `drug` nodes *are* grounded (ARO:0000032, ARO:3000008, ARO:0000020 …) and the
corpus already uses `GO:0046677` in 68 places. So what is missing is two
decisions — which term grounds the resistance-phenotype node, and which RO
relation models "confers resistance to" — after which both fixes are mechanical.
The corpus's existing predicate vocabulary is narrow (RO:0002411 causally
upstream of, RO:0000056 participates in, RO:0002327 enables), so this is a real
literature/ontology question, but a small one with a very large blast radius.

## Rank 3 — Class-level evidence on gene-level claims (the VALIDATE that must precede any mass edit)

Evidence in the resistance corpus is extremely concentrated: 2,595 distinct
PMIDs, but `PMID:19136439` is cited 14,547 times and `PMID:16121396` 11,611.
Inspecting the snippets shows why — they are **class-level statements attached to
individual gene variants**:

> "AmpC β-lactamases are clinically important cephalosporinases encoded on the
> chromosomes of many of the Enterobacteriaceae…" — attached to 607 records in a
> 400-record sample

That is defensible for a `determinant -> mechanism` edge (class membership is
what the snippet supports) and **weak for a `resistance -> drug` edge**, which is
a gene-specific spectrum claim the class-level quote does not establish. Note
these are the same 12,581 edges as Rank 2.

This needs a **sampling audit to size the error rate before anything is rewritten
in bulk** — the honest sequence is measure, then correct, not correct-then-check.
It is listed third not because it matters least but because its output is a
number that determines how much of Rank 2 is a re-grounding versus a retraction.

## Rank 4 — The 1,219 un-batchable resistance drafts

Real literature work, already correctly scoped by
`causal-graphs-round11.md` as the point where automated family promotion stops:
point-mutant target genes (gyrA/rpoB/16S/23S), efflux subunits, two-component
regulators. Genuinely one-at-a-time, so it is the **highest cost per record** of
anything here. It should follow the higher-leverage items, not precede them.

## Explicitly not recommended

- **Definitions (`edison-trait-definitions`).** 99.1% covered. Of the 3,553 gaps,
  3,418 are CDD `FUNC_PROTEIN_FAMILY` — a single source's family stubs, worth a
  batch pass someday, but not "highest impact" by any reading.
- **New source discovery (`edison-deep-research`).** Three rounds done, 29
  sources seeded, 408,978 records. More sources add breadth to a corpus whose
  gap is depth: 1.8% of records carry any mechanism at all.

## Recommendation

**Rank 1 (M-CSA) as the main thread, with Rank 2's two grounding decisions taken
first** — they are a prerequisite either way, since new catalysis graphs need the
same predicate vocabulary, and settling it once avoids minting 4,881 more edges
with the same defect.

Rank 3 is the check that tells us whether the existing 6,180 promoted graphs are
sound; it should run before any of them is edited in bulk.
