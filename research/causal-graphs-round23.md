---
topic: causal-graphs
round: 23
date: 2026-08-06
target: aro/FUNC_RESISTANCE — the D-Ala-D-Ser route: ligase (ARO:3002979), vanT (ARO:3000372), vanXY (ARO:3000496), 19 records
prior_round: causal-graphs-round22.md
---

# Causal graphs — Round 23: the other terminus, and the first round the guard ran *before* the fan-out

Rounds 20–21 covered the D-Ala-D-**Lac** route (vanX removes the target, vanH supplies the
replacement). This is the D-Ala-D-**Ser** route of the vanC/E/G/L/N clusters: three enzymes
that between them build a precursor ending in D-Ala-D-Ser.

## One sentence carries the whole division of labour

**Arias, Courvalin & Reynolds, AAC 2000 — PMID:10817725**:

> *"Three genes are sufficient for resistance: vanC-1 encodes a ligase that synthesizes the
> dipeptide D-Ala-D-Ser for addition to UDP-MurNAc-tripeptide, vanXY(C) encodes a
> D,D-dipeptidase-carboxypeptidase that hydrolyzes D-Ala-D-Ala and removes D-Ala from
> UDP-MurNAc-pentapeptide[D-Ala], and vanT encodes a membrane-bound serine racemase that
> provides D-Ser for the synthetic pathway."*

and the causal core, both halves in one sentence:

> *"Glycopeptide-resistant enterococci of the VanC type synthesize
> UDP-muramyl-pentapeptide[D-Ser] for cell wall assembly and prevent synthesis of
> peptidoglycan precursors ending in D-Ala."*

Each family then adds its own primary characterisation:

| family | records | its own paper |
|---|--:|---|
| D-Ala-D-Ser ligase (vanC/E/G/L/N) | 6 | PMID:10817725 |
| vanT — membrane serine racemase | 7 | **PMID:10209740** — *"serine racemase activity was detected in the membrane but not in the cytoplasmic fraction… whereas alanine racemase activity was located almost exclusively in the cytoplasm"* |
| vanXY — bifunctional | 6 | **PMID:10564477** — *"a soluble protein designated VanXYC (Mr 22 318), which had both of these activities"* |

## The specificity edge is a negative result, again

vanXY's `dipeptidase has input D-Ala-D-Ala` cites:

> *"It had very low dipeptidase activity against D-Ala-D-Ser, unlike VanX, and no activity
> against UDP-MurNAc-pentapeptide[D-Ser], unlike VanY."*

That is what makes the pathway coherent: the enzyme clears the D-Ala route **without**
destroying the D-Ser precursor it is helping to leave in place. Round 20 used the same
device for vanX. A mechanism graph that only records what an enzyme *does* cannot explain
why the cell survives its own clean-up.

## Cross-round citation, now in both directions

vanT's graph ends at `ARO:3002979`, the ligase record curated in **this same round** —
`d_serine --causally upstream of--> ligase_gene` — rather than restating the ligase's
chemistry. Round 22 established the pattern pointing backwards at rounds 20–21; this is the
first time it happens within a round.

## The guard ran first this time

Round 22 shipped 12 records asserting an operon composition false for their cluster, and
#201 was built afterwards. Here the three configs carried `_requires_ser_cluster` **before**
the first `--apply`, and `just verify-family-drafts` was run before promoting:

```
verify ARO:3002979: 1 KB CURIEs checked, 6 candidates, 0 precondition skips, 0 problems
verify ARO:3000372: 3 KB CURIEs checked, 7 candidates, 0 precondition skips, 0 problems
verify ARO:3000496: 3 KB CURIEs checked, 6 candidates, 0 precondition skips, 0 problems
```

**And the guard immediately found a gap in itself.** The ligase family reported *"0 KB
CURIEs checked"* — `EC:` was missing from `KB_PREFIXES`, so `EC:6.3.2.35` was being written
unchecked. Added, along with `SFLD:`, `PANTHER:` and `HAMAP:`, which are all record
identifier prefixes in this corpus.

## Provenance

* records touched: **19** (6 ligase + 7 vanT + 6 vanXY) · SEEDED → REVIEWED
* corpus after: **39,647 records · 40,115 graphs · 348,004 nodes · 369,618 edges ·
  0 errors · 369,618/369,618 edges snippet-cited**
* warnings 5,976 → **6,020**: +44, the ungrounded precursor and dipeptide nodes
* `just validate` on all 19 individually: **0 failures**
* drafts remaining: **1,133 → 1,114**

## Open questions

* **The 12 vanR/vanS records in these clusters are still blocked, and now for a code
  reason** — filed as **#208**. `vanR`/`vanS` span *both* routes, but the promoter is keyed
  by family ARO id and one family gets one config. Round 22's config names vanH/vanX and its
  precondition correctly refuses them; there is nowhere to put the config that would serve
  them. The cheapest fix is a list of configs per family, selected by their preconditions —
  which the guard already computes.
* **Three ungrounded nodes per record** (`precursor_ser`, `precursor_dala`, `dala_dser`),
  the same ChEBI gap as rounds 20–21: the amino acids and dipeptides are there, the
  UDP-MurNAc pentapeptides are not. Across rounds 20–23 that is ~70 such nodes, which is
  now enough to price a term request rather than keep noting it.
* **vanY (7) remains**, and is the last enzyme family in the van set.
