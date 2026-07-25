---
date: 2026-07-24
issue: "#7 — is any of this human-specific?"
prior: swissprot-trait-profiles-5.md
---

# Swiss-Prot trait profiles — Phase 6: multi-organism matrix and held-out-organism tests

Everything through phase 5 was mined from 20,000 reviewed **human** proteins. That
made two claims untested. First, that the cross-axis rules ("this signature
encodes this fold") describe sequence→structure→function coupling rather than the
composition of one proteome. Second, that the exemplars phase 5 wrote are
archetypes rather than "the best human carrier that happened to exist".

Phase 6 rebuilds the matrix over four organisms and tests both.

## The matrix

`just build-profiles --organisms --limit 25000 --jsonl-only --apply`

| organism | proteins |
|---|--:|
| *Homo sapiens* | 20,431 |
| *Mus musculus* | 17,267 |
| *Saccharomyces cerevisiae* S288C | 6,733 |
| *Escherichia coli* K-12 | 4,531 |
| **total** | **48,962** |

Corpus trait classes observed rises **51,716 → 70,446** (+18,730). `--query` is now
repeatable and `--organisms` is shorthand for this slice; `--limit` caps per query.

## Do the rules survive a held-out organism?

`just test-rule-generalization --train 9606` — mine on human, recompute each rule's
confidence on organisms the miner never saw. Full output:
[`research/rule-generalization-1.md`](rule-generalization-1.md).

| rule family | mouse | yeast | *E. coli* |
|---|--:|--:|--:|
| **seq-encodes-fold** | **99%** (283 testable) | **96%** (124) | **96%** (23) |
| **trait-implies-function** | 88% (231) | 86% (113) | 81% (26) |

Median held-out confidence is 1.00 in every cell. **The sequence→fold rules are
biology.** A signature that encodes a fold in human encodes it in *E. coli* too,
which is what the whole SEQUENCE↔STRUCTURE overlay implicitly claimed and had never
been asked to demonstrate.

The function rules are weaker, and *how* they fail is the interesting part. The
worst offenders are not mechanism at all:

| rule | held-out organism | train conf | held-out conf |
|---|---|--:|--:|
| `CATH:3.30.50.10 → GO:0005654` (nucleoplasm) | yeast | 1.00 | 0.00 |
| `PROSITE:PS00657 → GO:0000785` (chromatin) | mouse | 0.97 | 0.03 |
| `Pfam:PF01825 → GO:0016020` (membrane) | mouse | 0.97 | 0.23 |
| `Pfam:PF00046 → GO:0000981` (homeobox → pol II TF activity) | yeast | 0.96 | 0.43 |

These are GO **cellular-component** and lineage-specific process terms. A homeobox
protein is a transcription factor in yeast as much as in human; what differs is
which GO term the curators of that organism reached for. So the
`trait-implies-function` overlay is partly measuring **annotation practice**, while
`seq-encodes-fold` measures structure. The two families deserve different trust,
and the report now names the held-out organism on every failure — without it, a
nucleoplasm rule "failing" in a bacterium reads as a broken rule rather than a
category error.

`--min-test-support` gates which rules are judged at all, and `untestable` is
reported rather than silently dropped: 159 of 283 fold rules have too few yeast
carriers to judge and 260 too few in *E. coli*. Folding those into the denominator
would have inflated replication.

## Does trait→function *prediction* transfer?

`just train-trait-tree --holdout-taxon <taxon>` — same decision trees as phase 2,
but the test set is an entire proteome instead of a random 25%.

| split | macro-F1 |
|---|--:|
| random 75/25 | 0.44 |
| held out *Mus musculus* | **0.45** |
| held out *S. cerevisiae* | 0.33 |
| held out *E. coli* | **0.20** |

Two findings. **Mouse is not a held-out test** — it scores the same as a random
split, because human and mouse proteins are near-duplicate by orthology. Any
random split of a vertebrate-heavy matrix leaks orthologs across the boundary and
reports optimistic generalisation. Real transfer decays with phylogenetic
distance: 0.45 → 0.33 → 0.20.

And within the *E. coli* holdout the collapse is selective:

| transfers | collapses |
|---|---|
| ATP binding (F1 0.67) — via P-loop NTPase | identical protein binding (0.00) |
| ATP hydrolysis (0.62) | protein homodimerisation (0.00) |
| DNA-binding TF activity (0.71) | enzyme binding (0.00) |
| GTP binding (0.31) | calcium ion binding (0.00) |
| | zinc ion binding (0.01) |

Catalytic and ligand-binding function predicted from a fold transfers across the
domain boundary. "Binds some other protein" does not — those annotations track
curation effort, and eukaryotic interaction screens have no *E. coli* counterpart.
The same split as the rule test, from an independent method.

## Corpus changes

The overlay was re-mined on the four-organism matrix and the exemplars re-ranked
against it:

| | phase 5 (human) | phase 6 (4 organisms) |
|---|--:|--:|
| `trait_cooccurrence.tsv` edges | 516 | **1,506** |
| — seq-encodes-fold | 284 | **771** (647 at conf ≥0.99) |
| trait records with `canonical_examples` | 104,699 | **120,754** (29.5%) |
| rule-backed exemplar picks | 671 | **1,704** |

`relation_source` on every edge now names the proteomes that support it rather than
the hardcoded `Swiss-Prot(human)`.

The exemplar pass wrote 142,052 examples across 60,984 records — 16,055 records
newly reachable (NCBIfam +4,111: bacterial trait classes that a human-only matrix
could never exemplify) and 44,929 phase-5 records re-ranked against the wider
matrix, of which **23,290 (52%) changed their top pick**. **9,460 records were
skipped because re-ranking would have touched a `CURATOR` or `UNIPROTKB_API`
example** — `--rerank` only ever replaces this script's own `SWISSPROT_PROFILE`
picks.

### The ranking was measuring curation effort

The first re-ranked pass produced a suspicious result: *Mus musculus* took **49%**
of top exemplars against a 35% share of the matrix, while human fell to 23.5% from
a 42% share. The cause was the `depth` term using a raw GO-term count — and mouse
averages **16.1 GO terms to human's 12.6** (median 11 vs 9), because MGI annotates
more aggressively than the human effort in Swiss-Prot. So for any human/mouse
ortholog pair the mouse entry won, not because it is a better archetype but
because its curation team was busier.

That is the same failure this phase diagnoses in the `trait-implies-function`
rules, reproduced inside our own scoring. `depth` and `focus` are now **percentiles
within the carrier's own proteome**, which asks "is this protein well
characterised *for its organism*" instead of "which community annotates hardest":

| top exemplar organism | matrix share | raw counts | within-proteome percentile |
|---|--:|--:|--:|
| *Homo sapiens* | 42% | 23.5% | **39.0%** |
| *Mus musculus* | 35% | 49.1% | **29.6%** |
| *E. coli* K-12 | 9% | 17.9% | 21.6% |
| *S. cerevisiae* | 14% | 9.5% | 9.8% |

*E. coli* stays over-represented relative to its share, and that one is intended:
bacterial proteins are compact and single-domain, so they genuinely win `focus`
for domain and fold traits — a 300-residue enzyme is a cleaner archetype for a
fold than a 2,000-residue multidomain vertebrate protein that merely contains it.
The distribution by axis reflects that (`sequence` picks are 45% human, `structure`
picks 30% *E. coli*).

## Gate

* Every rewritten file re-parsed before writing, duplicate-top-level-key guard
  active (the phase-5 review finding, #34): 0 failures across 60,984 records.
* `linkml-validate` clean on a 240-record sample stratified 30-per-namespace
  across all 8 namespaces.
* Rule-replication and decision-tree scripts are read-only.
* One provenance bug caught by spot-checking a bacterial record before commit:
  the per-example `note` named the matrix's *most common* organism, which was
  correct while the matrix was human-only and became false the moment it was not
  — an *E. coli* exemplar carried the note "48,962 reviewed Homo sapiens
  entries". The note now describes the matrix composition.

## Caveats

* Four organisms is still a narrow slice — two mammals, one fungus, one
  γ-proteobacterium. No archaea, plants, or parasites.
* `--limit 25000` did not bind on any query (largest is human at 20,431), so each
  proteome is complete; but the matrix is 76% vertebrate by protein count, which
  still biases which rules clear `--min-support`.
* The rule-replication test trains on human by design. Training on *E. coli* and
  testing on eukaryotes would probe the reverse direction and is not done here.

## Next

- Re-mine with **support weighted per organism** so a rule cannot clear threshold
  on vertebrate abundance alone.
- Split the `trait-implies-function` overlay by GO aspect — the evidence says
  molecular-function edges are trustworthy in a way cellular-component edges are
  not, and the overlay currently makes no distinction.
- Protein × trait **browser map** (UMAP/PaCMAP of `profiles.jsonl`), still open
  from phase 4.
