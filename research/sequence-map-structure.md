---
date: 2026-09-19
issue: "#508 — a sequence-similarity protein map from ESM-2 650M"
---

# The sequence map: built, measured, and behind the trait map on structure

Issue #508 proposed a third protein map, laid out by protein-language-model
sequence embedding rather than by annotation text, and set the bar for it: if
it does not beat the TF-IDF protein map on CATH enrichment, it is not worth
shipping. This round built it as specified and measured it. **It does not clear
the bar**, in 2-D or in its own embedding space, and the gap is not an artefact
of CATH being among the trait map's inputs.

Every table below is printed by committed code:

```
just embed-sequences --traits-dir <export of the commit's data/traits>
just sequence-map
python3 scripts/build_protein_map.py --exclude-prefix CATH --out <control.json>
just measure-sequence-map --control-map <control.json> --breakdown
```

This revision replaces the 2026-09-16 one after an independent review of #707
(#721–#733). That version explained the result by mean pooling diluting
multidomain proteins, from an ad hoc snippet that was never committed; the
reproducible breakdown below does not support that explanation, and it is
withdrawn.

## What was built

| stage | script / recipe | output |
|---|---|---|
| ESM-2 embedding | `just embed-sequences` (`scripts/embed_sequences.py`) | `data/embeddings/esm2/` (gitignored; cache named for model, revision and dtype) |
| 2-D layout | `just sequence-map` (`scripts/build_sequence_map.py`) | `docs/data/sequence_map.json` (0.66 MB), the *Sequences* tab of `docs/map.html` |
| measurement | `just measure-sequence-map` (`scripts/measure_sequence_map.py`) | this report's tables |

Model `facebook/esm2_t33_650M_UR50D`, revision `08e4846e…`, MIT. Final-layer
residue mean excluding CLS, EOS and padding. FP32 on MPS. Sequences over 1,022
residues are cut into 1,022-residue windows with 256-residue overlap, residue
representations averaged across windows, then one equal-weight mean over
original positions — never truncated. Layout: L2 → PCA(100) → L2 → PaCMAP
(15 neighbours, PCA init, seed 42).

Input: every `canonical_examples[].sequence` in the committed `data/traits/`
(exported from the branch commit, not read from a working tree other jobs were
rewriting) — 12,705 accessions, 12,564 unique sequences, 1,026 over the ESM-2
limit, the longest titin at 34,350 aa (45 windows).

## Feasibility, measured on this machine (M1 Max, 64 GB)

#508's runtime figures were Codex estimates without a local test. Measured:

| | |
|---|--:|
| canary, 3 short proteins, MPS vs CPU FP32 | same-sequence cosine 1.00000, pairwise shift 0.00000 |
| canary, titin (34,350 aa, 45 windows) | 0.3 min on MPS; cosine vs CPU 1.00000; largest MPS driver allocation sampled after a batch 8.9 GB |
| full run, 12,560 unique sequences, 13,956 windows, 6.68 M residues | **48.8 min**, 2,279 residues/s; MPS driver allocation at the end of the run 7.7 GB |
| PCA(100) variance kept | 87.4% |
| 2-D layout | 8 s; densest 40×40 cell 1.0%, 94.7% distinct coordinates |

MPS has no peak-memory counter, so the memory figures are samples, not peaks.
The 60–90 min estimate in #508 was right. MPS reproduced CPU FP32 to five
decimals, so the `--dtype float16` question never needed opening. After the
review refactored the batching loop, both canaries were re-run into an empty
cache and their vectors were bit-identical to the first run's.

## The measurement

Neighbour purity at k = 25 as lift over the purity expected from label
proportions, on the 5,301 proteins present on every map compared; per label,
only proteins carrying it. Organism and EC come from the Swiss-Prot profiles;
CATH class is the majority class of a protein's assignments, CATH superfamily
its first sorted one.

| label | proteins | classes | chance |
|---|--:|--:|--:|
| organism | 5,301 | 10 | 0.3513 |
| CATH class | 4,966 | 5 | 0.3423 |
| CATH superfamily | 4,966 | 906 | 0.0049 |
| EC class | 2,254 | 7 | 0.2351 |
| EC sub-subclass | 2,221 | 174 | 0.0173 |

| space | organism | CATH class | CATH superfamily | EC class | EC sub-subclass |
|---|--:|--:|--:|--:|--:|
| ESM-2 embedding, raw (1,280-d) | 1.69× | 1.63× | 29.27× | 1.63× | 9.02× |
| ESM-2 embedding, centred + L2 (1,280-d) | 1.75× | 1.67× | 33.01× | 1.74× | 9.84× |
| PCA + L2 (PaCMAP's input) | 1.78× | 1.61× | 26.77× | 1.63× | 8.07× |
| sequence map 2-D | 1.64× | 1.41× | 14.84× | 1.40× | 5.22× |
| protein map 2-D (CATH among its inputs) | 1.15× | 1.59× | 52.01× | 1.92× | 12.48× |
| control protein map 2-D (CATH excluded) | 1.15× | 1.55× | 49.98× | 1.86× | 12.49× |

What these say:

1. **The bar as written: 14.8× vs 52.0× on CATH superfamily in 2-D. Failed.**
2. **CATH being an input barely matters.** Removing the CATH features moves the
   protein map from 52.0× to 50.0×: they account for 4% of its figure. The
   earlier revision called the bar unmeetable "by construction" because of
   label leakage; the control shows that was wrong. The other signatures —
   Pfam, InterPro, SUPERFAMILY, CDD — are expert homology classifications and
   carry the same information.
3. **On enzyme function, an input to neither map, the trait map also wins**:
   12.5× vs 5.2× on EC sub-subclass in 2-D, and 9.8× for the best embedding
   space.
4. **Even the best embedding space (33.0×) is below the trait map's 2-D
   layout (50.0×).** The shortfall is in the representation, not only in the
   projection.
5. **The projection loses a lot on top of that.** Centring and re-normalising
   the raw vectors *raises* the lift (29.3× → 33.0×; the raw vectors are
   strongly anisotropic, mean pairwise cosine 0.89). The builder instead
   L2-normalises uncentred vectors before PCA, and PaCMAP's input holds 26.8×
   — 81% of the centred figure. The 2-D layout then keeps 55% of its input.
6. **The sequence map is more organised by organism** (1.64× vs 1.15×). What
   drives that is not measured here.

## Where the embedding does and does not keep up

CATH superfamily, with bootstrap 95% intervals (1,000 resamples of proteins,
neighbourhoods fixed), against the control protein map. **Lifts are not
comparable across rows** — chance and the share of multi-superfamily proteins
both change with length — so the last column, the ratio within a row, is the
number to read.

| subset | n | chance | multi-superfamily | ESM-2 centred + L2 | sequence map 2-D | control protein map 2-D | embedding ÷ trait map |
|---|--:|--:|--:|--:|--:|--:|--:|
| all | 4,966 | 0.0049 | 49% | 33.0× [30.7, 35.5] | 14.8× [13.7, 15.9] | 50.0× [46.9, 53.4] | 0.66 [0.64, 0.68] |
| single-superfamily proteins | 2,548 | 0.0065 | 0% | 28.9× [26.9, 31.0] | 13.8× [12.8, 15.0] | 40.8× [38.1, 43.6] | 0.71 [0.68, 0.74] |
| multi-superfamily proteins | 2,418 | 0.0082 | 100% | 16.9× [15.0, 19.0] | 9.2× [8.2, 10.3] | 24.8× [22.1, 27.8] | 0.68 [0.65, 0.71] |
| ≤ 200 aa | 792 | 0.0084 | 10% | 17.8× [16.5, 19.2] | 11.6× [10.7, 12.7] | 15.6× [14.2, 17.1] | 1.14 [1.06, 1.23] |
| 201–500 aa | 2,182 | 0.0067 | 41% | 24.3× [22.2, 26.5] | 12.3× [11.1, 13.5] | 33.1× [30.6, 35.8] | 0.73 [0.70, 0.76] |
| 501–1,022 aa | 1,446 | 0.0082 | 71% | 14.3× [12.7, 16.2] | 8.6× [7.6, 9.8] | 20.6× [18.4, 23.2] | 0.69 [0.65, 0.74] |
| > 1,022 aa (windowed) | 546 | 0.0176 | 76% | 5.7× [4.8, 6.6] | 3.8× [3.2, 4.5] | 9.3× [8.2, 10.5] | 0.61 [0.55, 0.68] |

- **Multidomain dilution is not the explanation.** If a whole-chain mean
  blurring several folds were the cost, the embedding should close the gap on
  single-superfamily proteins. It does not: the ratio is 0.71 there and 0.68 on
  multi-superfamily proteins, intervals overlapping.
- **The embedding does beat the control trait map for proteins of 200 residues
  or fewer** (1.14, interval excluding 1) — in its embedding space, not in the
  2-D layout (11.6× vs 15.6×), and against the control rather than the shipped
  protein map.
- **The ratio falls with length** (1.14 → 0.73 → 0.69 → 0.61). The cause is not
  established. Domain count does not explain it on the evidence above; other
  candidates that were not tested are that longer proteins carry more
  signatures, giving the trait map more to match on, and the window limit.

## Verdict

**Ship the embedding pipeline; do not present the 2-D map as a structure map.**
The embeddings are correct (CPU-verified, bit-reproducible), cached, and cheap
to refresh, and they carry a 33× CATH-superfamily lift with no annotation in
the input. By the bar #508 set, and by the fairer control, the 2-D *Sequences*
tab is not a better structure map than the one already shipped. It is on the
page as a view of sequence similarity; the landing text claims no more than
that.

## What would change the answer

- **Centre before normalising.** The measured 29.3× → 33.0× says the layout
  should be centre → L2 → PCA rather than L2 → PCA, and 2-D keeps only 55% of
  its input, so neighbour count and PCA width deserve a sweep. #508's PCA(100)
  was a reasoned default, not a measured one. (#711)
- **Measure the trait map's own 50-d SVD space**, not only its 2-D layout;
  `build_protein_map.py` would need to write it out. (#711)
- **Pool per domain rather than per chain** remains worth trying for a *domain*
  map, but this round's data do not show it is where the gap comes from. (#711)
- **Domain-of-life colour** needs a taxonomy source (#712): 2,686 of the example
  proteins carry no taxon id (reproducible from `proteins.jsonl`). A one-off
  check on 2026-09-16 against UniProt `speclist.txt` release 2026_03, not
  committed as code, resolved a kingdom for 7,001 of the rest.
- ESM-C (2,048-token context) or a structure-tuned model (ProstT5) would
  address the window limit and the fold question more directly; #508 lists why
  each was passed over this round.
