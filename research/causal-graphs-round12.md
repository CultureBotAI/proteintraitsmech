---
topic: causal-graphs
round: 12
date: 2026-07-29
target: mcsa/STRUCT_ACTIVE_SITE — all 1,003 M-CSA entries (736 written)
prior_round: causal-graphs-round11.md
priorities: literature-review-priorities-1.md
---

# Causal graphs — Round 12: M-CSA catalysis, the whole source

Rounds 1–11 built out antibiotic resistance. That left the corpus in a lopsided
state that `literature-review-priorities-1.md` measured: **every mechanism graph
was resistance** — 7,399 of 7,401 — and the one source that already encodes
stepwise *catalytic* chemistry had 2 graphs out of 1,003 records.

This round transcribes M-CSA in bulk. It is not a departure from "one mechanism
per round" so much as an admission of what M-CSA is: the steps, the residue
roles, and the citations are already curated by the Thornton group, so writing a
graph is transcription-with-grounding, not research. The research effort went
into the two things transcription can still get wrong — **what is cited** and
**which residue is meant**.

## Gap (before)

| source | category | n | w/graph | w/ev |
|---|---|--:|--:|--:|
| mcsa | STRUCT_ACTIVE_SITE | 1,003 | **2** | 1,000 |
| aro | FUNC_RESISTANCE | 7,452 | 7,399 | 7,452 |

## What was written

| | before | after |
|---|--:|--:|
| M-CSA records with a graph | 2 | **738** |
| corpus records with a graph | 7,401 | **8,137** |
| causal edges | 65,093 | **79,087** |
| snippet-cited edges | 59,981 | **73,975** |
| `audit-graphs` errors | 0 | **0** |

736 records written, 13,994 edges, 12,979 nodes. Every new edge carries a
verbatim snippet — the +13,994 edges and +13,994 snippet-cited edges are the same
set.

## Decision 1 — cite M-CSA, not the PMID

The obvious move is to cite the mechanism's primary literature: M-CSA gives 5,593
references, median 4 per mechanism. **That would have been a misattribution.**
The prose being quoted — *"Glu165 acts as the catalytic base, abstracting a
proton from the alpha-carbonyl carbon."* — was written by M-CSA's curators, not
by the paper. Pairing it with a PMID would put a quotation in a source's mouth
that never contained it.

So every edge cites the **M-CSA entry URL**, whose text the snippet genuinely is,
and M-CSA's primary references travel in the edge `notes`:

```
reference: https://www.ebi.ac.uk/thornton-srv/m-csa/entry/324/
snippet:   "Glu165 acts as the catalytic base, abstracting a proton from the
            alpha-carbonyl carbon."
notes:     M-CSA entry 324, mechanism 1; M-CSA cites PMID:1... ; step 1
```

Promoting a PMID to `reference` stays a per-edge curation act that requires
reading the paper. This is deliberately a weaker claim than the round-1–11
resistance graphs make, and it is the honest one.

## Decision 2 — verify the residue frame, never assume it

M-CSA numbers residues in the **PDB author frame** (`auth_resid` — the
field-standard numbering, e.g. Ambler for β-lactamases). The KB is in the
**UniProt frame**. For MCSA:2 those differ by 2. Asserting one as the other
silently puts every residue edge on the wrong amino acid.

Rather than trust an offset, the generator *derives* it and *checks* it: it finds
the unique integer offset for which **every** catalytic residue's one-letter code
matches the reference sequence already stored on the record.

- **796** entries → a unique verified offset (560 of them offset 0).
- **205** entries → no unique offset. These keep M-CSA/PDB numbering and their
  labels say *"UniProt position not established"* rather than inventing one.

Validated against the hand-curated MCSA:2, where the method independently
recovers the curator's SIFTS result: offset −2, Ambler Ser70/Lys73/Ser130/Glu166
= UniProt 68/71/128/164.

Then checked against what was actually written, not what was intended:

| residue nodes claiming a UniProt position | 3,184 |
|---|--:|
| **verified against the record's own sequence** | **3,184** |
| mismatches | **0** |
| nodes correctly asserting no position | 652 |

## Graph design

Nodes — catalytic RESIDUEs (grounded `UniProtKB:`, roles from M-CSA), reactant
and product CHEMICALs (grounded CHEBI — all 1,003 entries have them), one STATE
per mechanism step, and the trait partonomy: the active site (`MCSA:<id>`, the
record itself), the fold (`CATH:<id>`, written **only** where that CATH record
exists in the corpus — 483 of 489 do), and the activity (EC xrefs).

Edges —
- `residue —RO:0002436→ step` for each residue *named in that step's own text*
- `step —RO:0002411→ step` for the ordering
- `residue —BFO:0000050→ active_site —BFO:0000050→ fold`
- `active_site —RO:0002327→ activity —RO:0002233/RO:0002234→ reactant/product`

The partonomy is the requirement that causation run through the KB's own trait
records rather than through free-floating ontology classes, and it is what links
this STRUCTURE record to its SEQUENCE and FUNCTION neighbours.

**Two edge types were designed and then dropped.** Linking the first reactant to
step 1, and the last step to the first product, both required picking one of
several compounds M-CSA lists *without ordering them* — an invented claim in a
transcription. Substrate and product are carried instead by
`activity has-input / has-output`, which is what M-CSA actually states.

## What was not written, and why

- **265 entries have mechanisms with no prose.** Their steps carry arrow-pushing
  `marvin_xml` but empty `description` fields. There is nothing to quote, so no
  edge was written. Extracting chemistry from the Marvin XML is a real option for
  a later round; fabricating prose for it is not.
- **2 entries** already had hand-curated graphs (MCSA:2, MCSA:15) and were
  skipped, not overwritten.

## Provenance

records touched: 736 · edges written: 13,994 · all edges cited with a verbatim
snippet: **yes** · status → REVIEWED · `just validate` clean on sampled records ·
`just audit-graphs` 0 errors.

Generator: `scripts/build_mcsa_causal_graphs.py` (idempotent — skips records that
already carry `causal_graphs:`; dry-run by default).

## Open questions

- The 205 unresolved-offset entries are worth a SIFTS-backed pass; most are
  hetero-oligomers where the reference UniProt is not the catalytic chain.
- `activity` nodes carry EC xrefs but no `grounding` — M-CSA gives no GO term.
  Mapping EC → GO molecular function would ground ~736 more nodes.
- STATE (step) nodes are label-only by nature; they are chemical intermediates,
  not ontology classes. They account for most of the new audit warnings.
- The 265 Marvin-XML-only entries are the largest remaining M-CSA gap.
