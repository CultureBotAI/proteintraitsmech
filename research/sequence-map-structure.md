---
date: 2026-09-16
issue: "#508 — a sequence-similarity protein map from ESM-2 650M"
---

# The sequence map: built, measured, and behind the trait map on structure

Issue #508 proposed a third protein map, laid out by protein-language-model
sequence embedding rather than by annotation text, and set the bar for it: if
it does not beat the TF-IDF protein map on CATH enrichment, it is not worth
shipping. This round built it exactly as specified, measured it against that
bar and against two fairer ones, and found it **behind the trait map on every
structural and functional label except for short proteins**.

## What was built

| stage | script / recipe | output |
|---|---|---|
| ESM-2 embedding | `just embed-sequences` (`scripts/embed_sequences.py`) | `data/embeddings/esm2/` (gitignored, cached by sequence SHA-256) |
| 2-D layout | `just sequence-map` (`scripts/build_sequence_map.py`) | `docs/data/sequence_map.json` (0.66 MB), the *Sequences* tab of `docs/map.html` |
| measurement | `just measure-sequence-map` (`scripts/measure_sequence_map.py`) | this report's tables |

Model `facebook/esm2_t33_650M_UR50D`, revision `08e4846e…`, MIT. Final-layer
residue mean excluding CLS, EOS and padding. FP32 on MPS. Sequences over 1,022
residues are cut into 1,022-residue windows with 256-residue overlap, residue
representations averaged across windows, then one equal-weight mean over
original positions — never truncated. Layout: L2 → PCA(100) → L2 → PaCMAP
(15 neighbours, PCA init, seed 42).

Input: every `canonical_examples[].sequence` in `data/traits/` — 12,705
accessions, 12,564 unique sequences, 1,026 over the ESM-2 limit, the longest
titin at 34,350 aa (45 windows). The corpus was read from the working tree on
2026-09-16 while a concurrent reviewed-batch installer was rewriting canonical
examples; the embedding is a snapshot of that state, and a re-run after the
batch lands only embeds sequences the cache has not seen.

## Feasibility, measured on this machine (M1 Max, 64 GB)

#508's runtime figures were Codex estimates without a local test. Measured:

| | |
|---|--:|
| canary, 3 short proteins, MPS vs CPU FP32 | same-sequence cosine 1.00000, pairwise shift 0.00000 |
| canary, titin (34,350 aa, 45 windows) | 0.3 min on MPS, peak 8.9 GB, cosine vs CPU 1.00000 |
| full run, 12,560 unique sequences, 13,956 windows, 6.68 M residues | **48.8 min**, 2,279 residues/s, peak 7.7 GB |
| PCA(100) variance kept | 87.4% |
| 2-D layout | 8 s; densest 40×40 cell 1.0%, 94.7% distinct coordinates |

The 60–90 min / 7–11 GB estimate in #508 was right. MPS reproduces CPU FP32
exactly at this precision, so the `--dtype float16` question never needed
opening.

## The measurement

Neighbour purity at k = 25 as lift over the purity expected from label
proportions, on the proteins present on every map compared (5,301; per label,
only proteins carrying it). Two protein maps: the one shipped, which takes CATH
signatures as *input features*, and a control rebuilt with
`build_protein_map.py --exclude-prefix CATH`, which does not.

| label | proteins | classes | ESM-2 embedding (1,280-d) | sequence map 2-D | protein map 2-D (CATH among inputs) | control protein map 2-D (CATH excluded) |
|---|--:|--:|--:|--:|--:|--:|
| organism | 5,301 | 13 | 1.63× | 1.57× | 1.15× | 1.15× |
| CATH class | 4,966 | 5 | 1.58× | 1.36× | 1.57× | 1.52× |
| CATH superfamily | 4,966 | 906 | 29.27× | 14.84× | 52.01× | 49.98× |
| EC class | 2,254 | 7 | 1.63× | 1.40× | 1.92× | 1.86× |
| EC sub-subclass | 2,221 | 174 | 9.02× | 5.22× | 12.48× | 12.49× |

Three readings, in order of how fair they are to the sequence map:

1. **The bar as written (#508): 14.8× vs 52.0× on CATH superfamily in 2-D.**
   Failed — but that bar cannot be met by construction, because CATH
   superfamily identifiers are literally input features of the protein map.
   Its 52× is label leakage, not recovery.
2. **Against the CATH-free control: 14.8× vs 50.0×.** Still failed, and the
   control lost almost nothing when CATH was removed (52.0× → 50.0×). The
   remaining signatures — Pfam, InterPro, SUPERFAMILY, CDD — are expert
   homology classifications that encode superfamily membership nearly as
   directly as CATH does. A map of curated family assignments *should* recover
   a curated family label; the fair question is what the sequence adds beyond
   them, and the answer here is: less, not more.
3. **On enzyme function, an input to neither map: 5.2× vs 12.5×** (EC
   sub-subclass, 2-D). The trait map wins here too, for the same reason —
   family membership predicts EC well, and the trait map has it as input.

The sequence map is also **more organism-organised** (1.57× vs 1.15×). That is
phylogeny — orthologues across the ten profile proteomes have near-identical
sequences — rather than the curation-practice confound
`protein-map-feature-space.md` removed from the trait map, but it is still
organism, and it competes with fold for the same neighbourhoods.

The 2-D projection keeps only 51% of the embedding's superfamily lift (29.3×
→ 14.8×). Even at full dimensionality the embedding does not reach the control
map's 2-D figure.

## Why: mean pooling dilutes multidomain proteins

#508 named this limitation in advance. Splitting the superfamily lift by
sequence length, on the same shared proteins:

| length bin | n | superfamilies | ESM-2 embedding | sequence map 2-D | control protein map 2-D |
|---|--:|--:|--:|--:|--:|
| ≤ 200 aa | 792 | 223 | **16.6×** | 11.6× | 15.6× |
| 201–500 aa | 2,182 | 513 | 21.9× | 12.3× | **33.1×** |
| 501–1,022 aa | 1,446 | 408 | 13.1× | 8.6× | **20.6×** |
| > 1,022 aa (windowed) | 546 | 172 | 5.2× | 3.8× | **9.3×** |

The embedding beats the trait map only for proteins under 200 residues, which
are mostly single-domain, and falls behind progressively with length. Half of
the shared proteins (2,418 of 4,966) carry two or more CATH superfamilies; on
the single-superfamily half the embedding scores 26.2× against the control's
40.8×. A whole-chain mean makes a kinase-plus-SH2-plus-SH3 protein a blend of
three folds, while its trait vector lists all three as separate features that
neighbours can match one at a time.

## Verdict

**Ship the embedding pipeline; do not present the 2-D map as a structure map.**
The embeddings are correct (CPU-verified), cached, cheap to refresh, and useful
as a sequence-similarity signal — the per-protein nearest neighbours in the
1,280-d space carry a 29× superfamily lift with no annotation in the input,
which the trait map cannot claim. The 2-D *Sequences* tab is on the branch so
the picture can be looked at, but by the bar #508 set and by both fairer
bars, it is not a better structure map than the one already shipped, and the
landing-page text should not say it is. Whether the tab stays is a merge-time
call.

## What would change the answer

- **Pool per domain, not per chain.** Embed each Pfam/CATH-bounded region
  (`family_classifications` and the InterPro match coordinates already in
  `data/raw/interpro_matches/`) and map *domains* rather than proteins. The
  length table predicts this is where the gap comes from.
- **Measure the trait map's own embedding space** (its 50-d SVD) rather than
  only its 2-D layout; `build_protein_map.py` would need a `--dump-space`.
- **Try the projection on the raw 1,280-d vectors** or a larger PCA; the 2-D
  step halves the signal, and #508's PCA(100) was a reasoned default, not a
  measured one.
- **Domain-of-life colour** needs a taxonomy source: 2,686 of the example
  proteins carry no taxon id and UniProt's species list resolves only 7,001 of
  the rest, so the map colours by exemplified trait axis instead.
- ESM-C (2,048-token context) or a structure-tuned model (ProstT5) would
  address the window limit and the fold question more directly; #508 lists why
  each was passed over this round.
