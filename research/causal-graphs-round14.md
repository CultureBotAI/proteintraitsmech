---
topic: causal-graphs
round: 14
date: 2026-07-29
target: the three defects left after round 13 — snippets, EC→GO grounding, SIFTS tail
prior_round: causal-graphs-round13.md
---

# Causal graphs — Round 14: every edge is now cited

| | round 13 | round 14 |
|---|--:|--:|
| **snippet-cited edges** | 78,400 / 82,517 | **82,517 / 82,517 (100%)** |
| grounded nodes | 64,501 | **65,502** |
| audit warnings | 9,146 | **4,028** |
| errors | 0 | **0** |
| residue positions claimed / verified | 4,772 / 4,772 | **4,785 / 4,785** |

## 1. The 4,117 snippet-less edges — a mis-scoped "un-batchable"

All of them sat in the 1,219 `resistance-draft` graphs. Round 11 called that tail
un-batchable and stopped. That judgement was correct about **promotion** — the
mechanisms genuinely differ and no family config fits — and it was silently
carried over to **citation**, which is a different problem with a different
answer.

ARO already states in prose what each of the three edge shapes claims:

| edge | what backs it |
|---|---|
| `mech -> resistance` | the mechanism class definition, which states the causal link outright: *"Enzymatic inactivation of antibiotic to confer drug resistance."* (ARO:0001004) |
| `determinant -> resistance` | the `confers_resistance_to_*` relationship line |
| `determinant -> mech` | the determinant's own ARO definition |

Each edge gained a second `EvidenceItem`; the CARD DOI/PMID was **kept**, because
it remains the thing a curator reads when promoting the draft.

The third row is the one that needed care. No mech node is in its determinant's
`is_a` ancestor closure — checked — so the mechanism class is CARD's
categorisation, not an ontology axiom. The note says exactly that rather than
letting the citation imply more than ARO asserts.

## 2. A false provenance claim that was already in the corpus

1,449 draft notes read *"Auto-drafted from ARO participates_in ARO:x"*. Checked
against `aro.obo`: **only 40 of those relationships exist**. The remaining
**1,409** cited an axiom that is not there.

This was not introduced by this round; it was found because writing an honest
note for the same edge meant checking whether the existing one was true. Notes
are claims about the source and have to hold up like any other. They now record
what actually assigned the mechanism.

## 3. EC → GO for the activity nodes

GO publishes `external2go/ec2go`, so grounding 1,001 M-CSA `activity` nodes was a
lookup against an authoritative table rather than an inference. 905 resolve on
the exact EC; 96 only match a parent EC class and are grounded to that broader
term **with a description saying so** — the difference between "triose-phosphate
isomerase activity" and "glycosyltransferase activity" has to be visible without
opening the source. Verified: TIM, EC:5.3.1.1 → GO:0004807.

## 4. The SIFTS tail — the smallest result, stated as such

The 226 residues with no SIFTS segment failed for two diagnosable reasons: the
record's accession is not the one SIFTS names (Q05489 → P0DUB8; UniProt renames
and demerges), and M-CSA's `chain_name` sometimes matches `struct_asym_id` rather
than `chain_id`. Both are now tried, after the record's own accession, with the
sequence check still deciding.

**Yield: 9 records.** 288 relaxed candidates were rejected by the sequence check —
the guard working, not a loss. A wrong protein cannot survive that check; a
renamed one can, which is the entire reason the relaxation is safe.

## Where the corpus now stands

Every causal edge in all 8,402 graphs has a predicate, evidence, and a verbatim
snippet. Every residue position asserted anywhere is verified against its own
record's sequence.

All 4,028 remaining warnings are ungrounded nodes, and **4,023 are `step` STATE
nodes** — chemical intermediates with no CURIE by nature. This axis is at its
floor; further work on it would be manufacturing groundings rather than finding
them.

## Open

- The 1,219 drafts are now *cited* but still drafts: promoting them to
  family-wired graphs remains per-gene curation work.
- 312 residue nodes assert no UniProt position.
- The real remaining frontier is not these graphs but the corpus's other
  mechanism-rich sources — Rhea/EC reaction chemistry (26,003
  `FUNC_ENZYMATIC_ACTIVITY` records) and the UniProt/BioLiP binding and metal
  sites, neither of which carries a causal graph yet.
