---
topic: causal-graphs
round: 15
date: 2026-07-29
target: structure/STRUCT_BINDING_SITE (BioLiP) + STRUCT_METAL_SITE (MetalPDB)
prior_round: causal-graphs-round14.md
---

# Causal graphs — Round 15: binding and metal sites

Rounds 12–14 covered catalysis (M-CSA) and resistance (CARD/ARO). Both describe
*reactions*. This round covers the other kind of mechanism the schema is for —
**interaction**: which residues contact a ligand, and which coordinate a metal.

| | round 14 | round 15 |
|---|--:|--:|
| corpus graphs | 8,402 | **14,201** |
| causal edges | 82,517 | **183,050** |
| snippet-cited | 100% | **100%** |
| errors | 0 | **0** |
| warnings | 4,028 | 5,845 |

BioLiP: 5,571 records / 96,575 edges. MetalPDB: 228 records / 3,958 edges.

## The rule that shaped both: do not quote yourself

Both sources' records already contain a fluent sentence describing the site —
written by our own seeders. Quoting it as the `snippet` would have been the
easiest path and would have been **circular**: our text is not evidence for our
own claim.

So the evidence is the source's own data:

| source | snippet |
|---|---|
| BioLiP | the binding-residue field of the record line, verbatim from `BioLiP_nr.txt` |
| MetalPDB | the site entry's field values — residue, chain, donor atom, distance — from `flat_db_file.xml.gz` |

This is data rather than prose, unlike M-CSA's step descriptions, but it is the
source's own statement of exactly the claim each edge makes, and it is checkable
against a file in the repo. PMIDs stay in `notes` on the standing rule.

## Verification without the network

BioLiP reports binding residues **twice** — column 8 in PDB author numbering and
column 9 renumbered against the receptor sequence in column 21. That redundancy
is a free correctness check: a residue's letter must match that sequence at its
column-9 position or it is not written. No fetching, no SIFTS.

Neither source gives a UniProt position, and these records carry no UniProt
sequence, so **no UniProt position is asserted** — labels say the frame is PDB
author numbering. That is the same discipline as rounds 12–13, reaching the
opposite conclusion because the inputs are different.

## Source quirks that had to be handled, not passed through

- **BioLiP's EC field is `?` on 35,168 lines**, blank on 17,961, and elsewhere a
  comma-separated list mixing `?` with real numbers. `EC:?` is not a CURIE and
  failed closed-mode validation.
- **BioLiP's UniProt column names several accessions for chimeric chains**
  (`P0ABE7,P30939`). Which half a residue belongs to is not stated, so nothing is
  grounded and the note records the fusion — 1,817 residue nodes. Passing the raw
  string through produced **2,014 audit errors**, caught by `audit-graphs`, which
  checks CURIE shape on groundings where `linkml-validate` did not. Worth
  remembering: the two gates do not overlap.
- **On 197 records BioLiP's accession disagrees with the seeder's canonical
  example.** The quoted residues are BioLiP's for that chain, so its accession is
  used and the note records the disagreement.
- **MetalPDB's XML is not well-formed** — 4 lines carry a bare `&` inside
  `molecule_name`, aborting `iterparse` 6.3M lines in. Escaped while streaming.

## A bug in my own regex, and why it surfaced

The first MetalPDB pass matched `PDB (\w+)` against notes reading *"MetalPDB
mononuclear chromium site occurrence in PDB 1lm2"* — and matched the **`PDB`
inside `MetalPDB`**, extracting `mononuclear` as a PDB code. 11 codes, 0 hits.

It surfaced because the result was *loudly* wrong (zero matches against a
57,071-entry index) rather than plausibly wrong. Anchored with a lookbehind, the
real figure is 766 codes, all present, across 12,161 sites. The same shape of
error in a scoring or filtering step would not have announced itself — this one
was lucky, not caught by discipline.

## Scope choices, stated so they can be revisited

- **Only standard amino acids become residue nodes** in MetalPDB graphs. Water is
  the most common coordinating "residue" in the matched sites (12,344
  occurrences); nucleotides appear for DNA/RNA sites. Both are real chemistry,
  neither is a protein trait, and a node per water would bury the residues that
  matter. The coordination number is kept in the evidence notes so the omission
  is visible.
- **One exemplar occurrence per BioLiP record, up to three per MetalPDB record.**
  These are class records aggregating many occurrences; the graph illustrates the
  class rather than enumerating it.
- `ec2go` grounding was extended from M-CSA to BioLiP (3,086 exact + 357
  class-level), so **every `activity` node in the corpus is grounded**.

## Where the corpus stands

5,845 warnings, all ungrounded nodes and all label-only by nature: 4,023 M-CSA
STATE nodes, 1,817 BioLiP fusion-chain residues, 5 hand-curated intermediates.

## Open

- 445 BioLiP records whose PDB/chain/ligand is absent from the non-redundant
  `BioLiP_nr.txt`; the full BioLiP release would cover them.
- 63 MetalPDB records where no site matched both metal and nuclearity with a
  protein ligand.
- The remaining mechanism-rich source with no graphs is **Rhea/EC reaction
  chemistry** — 26,003 `FUNC_ENZYMATIC_ACTIVITY` records.
