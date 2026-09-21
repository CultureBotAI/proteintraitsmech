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
The shipped 2-D map's CATH-superfamily lift rose 58% (14.8× → 23.4×; 59% on
five-seed means, 14.4× → 22.9×); the comparison with the trait map got *worse*
for the embedding once it was made like for like. An independent review of
that work (#743–#750) then showed that the argument against per-domain pooling
depended on how multi-superfamily proteins were labelled, and turned up a bug
in the shared neighbour search (#751); both are corrected below.

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
| 2-D layout (centre → no PCA → 10 neighbours) | 7 s; densest 40×40 cell 1.4%; 89.2% of coordinates distinct at 3 decimals; 322 of 1,600 cells occupied |
| superseded #508 layout (L2 → PCA(100) → 15 neighbours) | PCA kept 87.4% of variance; densest cell 1.0%; 94.7% distinct at 3 decimals; 484 cells occupied |

The new layout uses less of the canvas because a handful of far outliers set its
bounds. Rescaling to percentiles would recover about a hundred cells by pinning
some 110 proteins to false positions on the border, so it is left as it is.
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
| sequence map 2-D | 1.57× | 1.50× | 23.36× | 1.51× | 6.92× |
| protein map 2-D (CATH among its inputs) | 1.15× | 1.58× | 51.95× | 1.92× | 12.45× |
| control protein map 2-D (CATH excluded) | 1.15× | 1.55× | 49.90× | 1.86× | 12.47× |
| protein map SVD space, 50-d, as its layout consumed it | 1.14× | 1.82× | 70.01× | 2.14× | 15.78× |
| — the same, L2-normalised | 1.17× | 1.89× | 74.95× | 2.18× | 16.06× |
| control protein map SVD space, 50-d (CATH excluded) | 1.15× | 1.75× | 65.61× | 2.13× | 15.91× |
| — the same, L2-normalised | 1.15× | 1.81× | 70.46× | 2.13× | 16.83× |

These differ in the second decimal from the 2026-09-20 draft because the shared
neighbour search left a point in its own neighbour list whenever rows were
duplicated — 45% of proteins in the trait map's SVD space, 1% in the sequence
embedding (#751). Self is now excluded everywhere.

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
   measurable: 65.6× without CATH as its layout consumed it and 70.5×
   L2-normalised, against 33.0× for the best sequence space — 50% and 47%.
4. **On enzyme function, an input to neither map, the trait map also wins**:
   15.9× vs 9.8× in embedding space, 12.5× vs 6.9× in 2-D. EC is not independent
   of CATH (nearly every EC-labelled protein here has a CATH label too), so this
   is a second view of the same result, not separate confirmation.
5. **The layout was throwing signal away, and mostly no longer does.** #508's
   L2 → PCA(100) → L2 input held 26.8× of the centred embedding's 33.0×, and 15
   neighbours kept 55% of that in 2-D. Centring, no PCA and 10 neighbours keep
   71% of 33.0×. The sweep shows 5 neighbours would keep 80% — and lower the
   global triplet score in every seed, so it was not adopted. The choice was
   made on five-seed means, not on the grid's single seed.
6. **The sequence map is more organised by organism** (1.57× vs 1.15×). What
   drives that is not measured here.

## Where the embedding does and does not keep up

CATH superfamily, with bootstrap 95% intervals (1,000 resamples of proteins,
neighbourhoods fixed), against the control protein map. **Lifts are not
comparable across rows** — chance and the share of multi-superfamily proteins
both change with length — so only ratios *within* a row are read.

Half of these proteins carry more than one CATH superfamily, and there are two
defensible ways to score them. **First-label** gives each protein its
first-sorted superfamily. **Any-match** (`--any-match`) counts a neighbour that
shares any superfamily, with chance taken as the exact share rate over all
pairs. The two are identical for single-superfamily proteins by definition, and
the corrected scorer returns 0.50 for that row under both.

Centred + L2 embedding ÷ control trait map, as ratio [95% interval]:

| subset | n | multi | first-label ÷ 2-D | first-label ÷ SVD space | any-match ÷ 2-D | any-match ÷ SVD space |
|---|--:|--:|--:|--:|--:|--:|
| all | 4,966 | 49% | 0.66 [0.64, 0.68] | 0.50 [0.49, 0.52] | 0.57 [0.55, 0.58] | 0.44 [0.43, 0.45] |
| single-superfamily | 2,548 | 0% | 0.71 [0.68, 0.74] | 0.50 [0.49, 0.52] | 0.71 [0.68, 0.74] | 0.50 [0.49, 0.52] |
| multi-superfamily | 2,418 | 100% | 0.68 [0.66, 0.72] | 0.58 [0.56, 0.61] | 0.56 [0.54, 0.58] | 0.48 [0.46, 0.49] |
| ≤ 200 aa | 792 | 10% | 1.14 [1.06, 1.23] | 0.78 [0.74, 0.82] | 1.05 [0.97, 1.14] | 0.74 [0.69, 0.78] |
| 201–500 aa | 2,182 | 41% | 0.73 [0.70, 0.77] | 0.55 [0.53, 0.56] | 0.65 [0.63, 0.68] | 0.48 [0.47, 0.50] |
| 501–1,022 aa | 1,446 | 71% | 0.69 [0.65, 0.74] | 0.55 [0.52, 0.58] | 0.57 [0.55, 0.60] | 0.45 [0.43, 0.47] |
| > 1,022 aa (windowed) | 546 | 76% | 0.61 [0.55, 0.68] | 0.52 [0.48, 0.56] | 0.55 [0.51, 0.58] | 0.48 [0.44, 0.50] |

The absolute lifts behind these are printed by the script (first-label, all:
embedding 33.0× [30.7, 35.5], sequence map 2-D 23.4×, control 2-D 49.9×,
control SVD space 65.6× [61.5, 70.2]).

- **Whether multidomain dilution explains the gap is not settled, and the
  labelling decides which way it points.** Under first-label the embedding does
  relatively *better* on multi-superfamily proteins (0.58 vs 0.50 against the
  trait map's space). Under any-match it does *worse* (0.48 vs 0.50), and much
  worse against the 2-D layout (0.56 vs 0.71). First-label penalises a
  multi-domain protein's neighbours for matching its second domain, in both
  maps but not equally; any-match rewards large multi-domain proteins for
  sharing anything. The 2026-09-19 revision withdrew the dilution claim and the
  2026-09-20 draft claimed the opposite on the first-label column alone; neither
  is supported. Per-domain pooling (#711) is the experiment that would decide it.
- **The "short proteins" exception was an artefact of comparing an embedding
  with a 2-D layout.** Against the control map's 2-D layout the embedding leads
  for proteins of 200 residues or fewer under first-label (1.14, interval
  excluding 1) and ties under any-match (1.05 [0.97, 1.14]). Against that map's
  own space it trails under both (0.78, 0.74). It leads nowhere.
- **The ratio falls with length** under every column, most steeply under
  any-match against 2-D (1.05 → 0.55), which is the pattern dilution predicts —
  and also the pattern expected if longer proteins simply carry more signatures
  for the trait map to match on. Length, domain count and annotation depth move
  together here and this design cannot separate them.

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
- **Pool per domain rather than per chain** is still open (#711) and is the
  experiment the breakdown cannot replace: score each CATH-Gene3D domain's own
  residue mean against that domain's superfamily, beside the whole-chain mean of
  the same protein. It needs match coordinates, which
  `data/raw/interpro_matches/` holds for 193 proteins (`just
  fetch-interpro-frame` fetches the rest, about 5,000 API calls), and one more
  GPU pass that keeps per-region means.
- **Domain-of-life colour** is done (#712), from UniProt's lineage per
  accession rather than a taxonomy dump: it also supplies an organism for the
  2,686 examples that carry no taxon id. Those ids are *not* written back to
  the records; that belongs to the release-pinned grounding workflow.
- ESM-C (2,048-token context) or a structure-tuned model (ProstT5) would
  address the window limit and the fold question more directly; #508 lists why
  each was passed over this round.
