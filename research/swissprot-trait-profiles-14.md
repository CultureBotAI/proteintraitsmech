---
date: 2026-07-27
issue: "#7 — lifting the constraint phase 13 identified"
prior: swissprot-trait-profiles-13.md
---

# Swiss-Prot trait profiles — Phase 14: raising the exemplar cap

Phase 13 established that the residue frame had saturated: adding 14,670 proteins
produced zero new edges, because 83,604 of them host records of only one trait
category. What binds is protein *sharing* — only 8,689 proteins hosted ≥2
comparable records — and sharing was capped by our own
`suggest_canonical_examples --max-examples 3`, with **57% of records sitting
exactly at it**.

This lifts that cap.

## Choosing the cap with evidence

The ceiling is large: **75,980** of the matrix's 78,296 trait-carrying proteins
carry traits of ≥2 distinct categories, against 8,689 hosting ≥2 comparable
records today — 8.7× headroom. But exemplars are meant to be exemplars, not
exhaustive carrier lists (the median capped trait has 9 carriers; the 90th
percentile has 53).

So rather than guess, the real ranking was simulated across candidate caps:

| cap | examples emitted | proteins hosting ≥2 categories |
|--:|--:|--:|
| 3 (before) | 196,160 | 25,703 |
| **8** | **356,799** (+82%) | **42,199** (+64%) |
| 12 | 435,566 (+122%) | 48,355 (+88%) |
| 16 | 494,946 (+152%) | 52,182 (+103%) |

Returns fall off after 8: going 8→12 buys +15% shareable proteins for +22%
payload, and 12→16 buys +8% for +14%. **Cap 8.**

## What changed in the corpus

`just suggest-examples --rerank --mine-rules --max-examples 8 --apply`

| | before | after |
|---|--:|--:|
| `canonical_examples` (SWISSPROT_PROFILE) | 169,177 | **309,535** |
| records touched | — | 72,003 |
| records skipped to protect curated picks | — | 11,579 |
| records sitting at the cap | 57% | **30%** |

The cap still binds for 30% of records, so the constraint is loosened rather than
removed. The distribution below it is unchanged by construction: 16,100 records
have one exemplar and 14,632 have two because those traits simply have few
carriers — the cap never touched them.

## The dependency worth naming

Raising the cap **cannot** produce edges on its own. New exemplars are proteins
the coordinate sidecars have never seen, and an unlocalized record contributes
nothing. The chain is:

1. re-rank at the new cap → new exemplar proteins appear
2. top up the residue frame → *not needed*: the new exemplars come from the
   ten-proteome matrix the frame already covers (its only 10,238 "missing"
   accessions are the known-dead ones from phase 13)
3. top up the InterPro frame → **needed**: edge-capable targets grew
   27,498 → 41,585, a 14,087-protein crawl
4. rebuild and verify

Step 2 being unnecessary is worth recording: it means the residue frame's
phase-13 completeness, which bought no edges then, is what makes this step free
now.

## What it bought

Unlike phase 13, this moved the artefacts:

| | before | after |
|---|--:|--:|
| proteins hosting ≥2 comparable records | 8,689 | **15,554** (+79%) |
| records localized | 61,017 | **64,063** |
| `seq_struct_alignment.tsv` | 12,424 | **16,350** edges |
| `seq_struct_func_sites.tsv` | 6,982 | **9,798** edges (+40%) |
| identical-residue `related_to` | 1,747 | **1,871** |
| adjudicated `close_match` (`residue_identity.tsv`) | 1,640 | **1,697** |

A clean superset on both overlays: **0 edges lost**, +3,087 base-alignment and
+2,816 func-site pairs.

The measured gain is well below the simulation's projection, and that was
expected — the simulation counted proteins carrying ≥2 trait *categories*
(42,199 at cap 8), whereas an edge additionally needs both records to be
**localizable** and **comparable**. 15,554 of those 42,199 cleared both bars.
Quoting the projection as the result would have overstated it 2.7×.

The 68 refuted identity pairs (was 40) keep the phase-12 pattern: every one is an
InterPro entry that integrates no Gene3D signature at all, so `related_to` stays
correct for them.

## Gate

* Superset verified before writing: 0 lost on both overlays.
* InterPro crawl: 14,087 proteins, **0 failures**; sidecar 27,498 → 41,585
  proteins, 583,627 signature matches.
* Coordinate provenance stamped on every edge and the two sidecars' build dates
  cross-checked (#60, merged this session).

## Caveats

* The corpus's exemplar payload nearly doubled (169,177 → 309,535). That is real
  cost in YAML size and in the docs detail sidecars, taken deliberately for a
  ~40% edge gain.
* 30% of records still sit at the cap. The constraint is loosened, not removed,
  and the next increment is worth less: the simulation says 8→12 buys +15%
  sharing for +22% payload.
* The ~10,238 permanently-absent accessions are still re-requested on every
  residue-frame top-up; nothing records that they are dead.
