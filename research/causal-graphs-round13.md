---
topic: causal-graphs
round: 13
date: 2026-07-29
target: close M-CSA (#78, #79) + re-base the resistance drug edges (priorities item 2/3)
prior_round: causal-graphs-round12.md
priorities: literature-review-priorities-1.md
---

# Causal graphs — Round 13: finish M-CSA, fix what round 1–11 mis-cited

Four pieces of work, three of which began by falsifying something I had written
down myself. That is the useful content of this round.

| | before round 13 | after |
|---|--:|--:|
| M-CSA records with a graph | 738 / 1,003 | **1,003 / 1,003** |
| corpus graphs | 8,137 | **8,402** |
| causal edges | 79,087 | **82,517** |
| edges with no `predicate_id` | 12,581 | **0** |
| ungrounded nodes | 11,896 | 5,029 |
| audit warnings | 29,589 | **9,146** |
| `audit-graphs` errors | 0 | **0** |
| residue positions claimed / verified | 3,184 / 3,184 | **4,772 / 4,772** |

## 1. The evidence audit that changed the plan (priorities item 3 → item 2)

The plan was to add an RO predicate to the 12,581 `resistance -> drug` edges —
100% of that edge type had none. Sampling their evidence first stopped that:

| `resistance -> drug` snippets, 300-record sample | share |
|---|--:|
| names the exact gene variant | ~0% |
| names the family, not the variant | 34.2% |
| names neither | 64.6% |

`GES-61` cited *"In the first acylation step, the β-lactam antibiotic forms an
acyl-enzyme intermediate…"* — generic class chemistry offered as support for a
drug-**spectrum** claim, which it cannot establish. Adding a predicate would have
tidied a badly-cited claim.

**Then I got the follow-up wrong.** I measured how many of those edges CARD
actually asserts, got **6.4%**, and was ready to conclude the rest were
fabricated by family-template promotion. That measurement ignored `is_a`
inheritance. With the ancestor closure the number is **100%** — 808 asserted on
the record's own ARO term, 11,773 on the family term the variant inherits from.

The inheritance is also the *explanation* for the class-level snippets: the
assertion itself is class-level. So the fix was to cite the assertion and say it
is inherited, not to delete anything:

```
determinant -[ARO:2000001]-> drug1  (confers resistance to (drug class))
  ref:     ARO:3000059
  snippet: relationship: confers_resistance_to_drug_class ARO:0000020 ! carbapenem
  notes:   Asserted on ARO:3000059 (KPC beta-lactamase), an is_a ancestor of this
           record's ARO:3002312; inherited by this variant.
```

The subject moved `resistance` → `determinant`, because ARO's subject is the gene
product and the old direction did not match the relation being asserted. The
7,399 label-only `resistance` nodes are grounded to GO:0046677 — the nearest real
superclass, since ARO models determinants and mechanisms but has no term for the
resistance phenotype itself, which the node description states.

## 2. #78 — the last 265 M-CSA entries, where both my hypotheses failed

Round 12 skipped them for empty per-step `description` fields. I filed #78
proposing to scrape the entry pages for residue-role prose the API omits.

**Wrong about the pages.** The page-only prose is real — the hand-curated MCSA:2
snippet is on the page, absent from the API, and `main_annotation` is empty for
all 5,248 cached residues. But *these* entries do not have it: their pages are
29–40 KB against 176 KB for entry 2, with zero residue-annotation blocks.

**Wrong about the API.** All 264 carry a populated `mechanism_text` the generator
never read, because it keyed on *step* descriptions. Same prose, unstepped,
median 520 chars: *"First, Asp 222 B deprotonates the 2-hydroxy oxygen, followed
by the formation of a double bond forcing hydride transfer from C2 to NAD(P)."*
They were being dropped for a **formatting** reason, and no fetching was needed.

They now build a single unstepped mechanism node labelled *"not resolved into
steps by M-CSA"* rather than implying a step structure that is not there.

## 3. #79 — SIFTS, and why the earlier refusal was right

200 records said "UniProt position not established" because no single integer
offset fits. SIFTS shows the cause: multi-chain enzymes whose chains map at
different offsets. MCSA:5 (carboxypeptidase D) —

    chain A  auth  -4..248  ->  UniProt   6..260   (+10)
    chain B  auth 264..423  ->  UniProt 287..439   (+23)

No global offset can fit that, so declining was correct rather than lazy.

Two frames, in order of directness: author numbering (M-CSA's `auth_resid`), then
`residue_number` — 365 residues sit in segments whose `author_residue_number` is
null and are invisible to the first frame, while M-CSA's own `resid` is in that
same frame. The fallback recovered 274 of them, more than doubling the yield.

**602 residues resolved across 173 of 200 records. 87 SIFTS-derived positions
failed the sequence check and were dropped**, not written with a caveat. 226 have
no usable segment and keep PDB numbering.

## The invariant that held throughout

Every residue position asserted anywhere in the M-CSA corpus is checked against
the reference sequence stored on its own record: **4,772 claimed, 4,772 verified,
0 mismatches**, with 325 nodes correctly asserting no position. That property was
re-measured after each of the three changes, not just at the end.

## Open

- 226 residues with no SIFTS segment (different organism/isoform in the PDB entry).
- `activity` nodes carry EC xrefs but no `grounding`; an EC → GO molecular-function
  mapping would ground ~1,000 more.
- STATE nodes are label-only by nature and account for most remaining warnings.
- 4,117 edges still lack a verbatim snippet, nearly all in the resistance drafts
  rather than in M-CSA.
