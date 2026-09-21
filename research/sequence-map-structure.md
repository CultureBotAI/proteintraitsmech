---
date: 2026-09-20
issue: "#508 — a sequence-similarity protein map from ESM-2 650M; #711, #712 follow-ups"
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
just fetch-uniprot-lineage --apply
just sweep-sequence-map --out research/sequence-map-sweep.md
just sequence-map
python3 scripts/build_protein_map.py --out <scratch.json> --dump-space <space>
python3 scripts/build_protein_map.py --exclude-prefix CATH --out <control.json> \
    --dump-space <control-space>
just measure-sequence-map --control-map <control.json> --protein-space <space> \
    --control-space <control-space> --breakdown
```

Revision history. 2026-09-19 replaced the first version after an independent
review of #707 (#721–#733): that version explained the result by mean pooling
diluting multidomain proteins, from an ad hoc snippet that was never committed;
the reproducible breakdown does not support it, and it is withdrawn. 2026-09-20
(#711, #712): the layout settings were swept and changed, the trait map's own
SVD space was exported and measured, and the map is coloured by domain of life.
The 2-D map improved by 59%; the comparison with the trait map got *worse* for
the embedding once it was made like for like.

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
original positions — never truncated. Layout: centre → L2 → PaCMAP (10
neighbours, PCA init, seed 42), chosen by `research/sequence-map-sweep.md`
over #508's L2 → PCA(100) → L2 → 15 neighbours. Colour: domain of life from
UniProt's lineage for each accession (`just fetch-uniprot-lineage`, release
2026_03: 12,699 of 12,705 accessions returned, every one with a taxon id;
8,105 Eukaryota, 4,204 Bacteria, 190 Archaea, 200 viruses).

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
| ESM-2 embedding, centred + L2 (1,280-d) = the layout's input | 1.75× | 1.67× | 33.01× | 1.74× | 9.84× |
| sequence map 2-D | 1.57× | 1.50× | 23.37× | 1.51× | 6.92× |
| protein map 2-D (CATH among its inputs) | 1.15× | 1.59× | 52.01× | 1.92× | 12.48× |
| control protein map 2-D (CATH excluded) | 1.15× | 1.55× | 49.98× | 1.86× | 12.49× |
| protein map SVD space, 50-d (CATH among its inputs) | 1.17× | 1.82× | 70.06× | 2.14× | 15.83× |
| control protein map SVD space, 50-d (CATH excluded) | 1.18× | 1.75× | 65.72× | 2.13× | 15.96× |

What these say:

1. **The bar as written: 23.4× vs 52.0× on CATH superfamily in 2-D. Failed**,
   though less badly than the first build's 14.8×.
2. **CATH being an input barely matters.** Removing the CATH features moves the
   protein map from 52.0× to 50.0× in 2-D (4%) and from 70.1× to 65.7× in its
   SVD space (6%). The first revision called the bar unmeetable "by
   construction" because of label leakage; the control shows that was wrong.
   Pfam, InterPro, SUPERFAMILY and CDD are expert homology classifications and
   carry the same information.
3. **Like for like, the gap is a factor of two.** The first two revisions could
   only set the sequence embedding against the trait map's *2-D layout*. With
   `build_protein_map.py --dump-space` the trait map's own 50-d space is
   measurable: 65.7× without CATH, against 33.0× for the best sequence space.
4. **On enzyme function, an input to neither map, the trait map also wins**:
   16.0× vs 9.8× in embedding space, 12.5× vs 6.9× in 2-D.
5. **The layout was throwing signal away, and mostly no longer does.** #508's
   L2 → PCA(100) → L2 input held 26.8× of the centred embedding's 33.0×, and 15
   neighbours kept 55% of that in 2-D. Centring, no PCA and 10 neighbours keep
   71% of 33.0×. The sweep shows 5 neighbours would keep 80% — and lower the
   global triplet score in every seed, so it was not adopted.
6. **The sequence map is more organised by organism** (1.57× vs 1.15×). What
   drives that is not measured here.

## Where the embedding does and does not keep up

CATH superfamily, with bootstrap 95% intervals (1,000 resamples of proteins,
neighbourhoods fixed), against the control protein map. **Lifts are not
comparable across rows** — chance and the share of multi-superfamily proteins
both change with length — so the last column, the ratio within a row, is the
number to read.

| subset | n | chance | multi-superfamily | ESM-2 centred + L2 | sequence map 2-D | control protein map 2-D | control protein map SVD space | embedding ÷ trait 2-D | embedding ÷ trait SVD space |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| all | 4,966 | 0.0049 | 49% | 33.0× [30.7, 35.5] | 23.4× [21.7, 25.1] | 50.0× [46.9, 53.4] | 65.7× [61.6, 70.3] | 0.66 [0.64, 0.68] | 0.50 [0.49, 0.51] |
| single-superfamily proteins | 2,548 | 0.0065 | 0% | 28.9× [26.9, 31.0] | 20.6× [19.2, 22.3] | 40.8× [38.1, 43.6] | 57.3× [53.7, 61.2] | 0.71 [0.68, 0.74] | 0.50 [0.49, 0.52] |
| multi-superfamily proteins | 2,418 | 0.0082 | 100% | 16.9× [15.0, 19.0] | 13.6× [12.1, 15.2] | 24.8× [22.1, 27.8] | 29.0× [26.0, 32.4] | 0.68 [0.65, 0.71] | 0.58 [0.56, 0.61] |
| ≤ 200 aa | 792 | 0.0084 | 10% | 17.8× [16.5, 19.2] | 15.6× [14.5, 16.9] | 15.6× [14.2, 17.1] | 22.8× [21.2, 24.6] | 1.14 [1.06, 1.23] | 0.78 [0.74, 0.82] |
| 201–500 aa | 2,182 | 0.0067 | 41% | 24.3× [22.2, 26.5] | 18.2× [16.5, 20.0] | 33.1× [30.6, 35.8] | 44.6× [41.3, 48.0] | 0.73 [0.70, 0.76] | 0.54 [0.53, 0.56] |
| 501–1,022 aa | 1,446 | 0.0082 | 71% | 14.3× [12.7, 16.2] | 11.1× [9.8, 12.7] | 20.6× [18.4, 23.2] | 26.2× [23.4, 29.3] | 0.69 [0.65, 0.74] | 0.54 [0.51, 0.58] |
| > 1,022 aa (windowed) | 546 | 0.0176 | 76% | 5.7× [4.8, 6.6] | 4.8× [4.0, 5.7] | 9.3× [8.2, 10.5] | 10.9× [9.6, 12.3] | 0.61 [0.55, 0.68] | 0.52 [0.48, 0.56] |

- **Multidomain dilution is not the explanation.** If a whole-chain mean
  blurring several folds were the cost, the embedding should close the gap on
  single-superfamily proteins. Against the trait map's SVD space the ratio is
  0.50 there and 0.58 on *multi*-superfamily proteins — the opposite direction.
- **The "short proteins" exception was an artefact of comparing an embedding
  with a 2-D layout.** The embedding beats the control trait map's 2-D layout
  for proteins of 200 residues or fewer (1.14, interval excluding 1), which the
  previous revision reported. Against that map's own space it does not (0.78
  [0.74, 0.82]). Short proteins are where it comes closest; it leads nowhere.
- **In 2-D the two maps now tie for short proteins** (15.6× each), where the
  first build trailed 11.6× to 15.6×.
- **The ratio still falls with length** against the 2-D layout (1.14 → 0.61);
  against the SVD space it is flat from 201 residues up (0.54, 0.54, 0.52). The
  cause of the short-protein advantage is not established.

## Verdict

**Keep the embedding pipeline and the tab; do not present the tab as a structure
map.** The embeddings are correct (CPU-verified, bit-reproducible), cached, and
cheap to refresh, and they carry a 33× CATH-superfamily lift with no annotation
in the input. By the bar #508 set, by the fairer control, and by the
like-for-like comparison of spaces, a whole-chain ESM-2 mean recovers about half
the fold structure that curated signatures do. The maintainer's decision
(2026-09-20, #508) is that the *Sequences* tab stays, as a view of sequence
similarity; the landing text claims no more than that.

## What would change the answer

- **Done in this revision:** centre before normalising, sweep PCA width and
  neighbours (`research/sequence-map-sweep.md`), and measure the trait map's
  own SVD space. The first two improved the map; the third widened the gap.
- **Pool per domain rather than per chain** is still open (#711), but this
  round's data argue against it as the explanation: the embedding does
  *relatively better* on multi-superfamily proteins. It would need
  CATH-Gene3D match coordinates, which `data/raw/interpro_matches/` holds for
  193 proteins; `just fetch-interpro-frame` can fetch the rest.
- **Domain-of-life colour** is done (#712), from UniProt's lineage per
  accession rather than a taxonomy dump: it also supplies an organism for the
  2,686 examples that carry no taxon id. Those ids are *not* written back to
  the records; that belongs to the release-pinned grounding workflow.
- ESM-C (2,048-token context) or a structure-tuned model (ProstT5) would
  address the window limit and the fold question more directly; #508 lists why
  each was passed over this round.
