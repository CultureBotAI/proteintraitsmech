# Corpus-map projection parameters — rationale

Rationale for the parameters used by `scripts/embed_map.py` to project the
record text embeddings (bge-large-en-v1.5, 1024-d, L2-normalized) to the 2-D
corpus map (`docs/data/corpus_map.json`, rendered by `docs/map.html`).

## Method: PaCMAP (primary; UMAP / PCA secondary)

PaCMAP (Pairwise Controlled Manifold Approximation, Wang et al., *JMLR* 2021) is
the primary projection because, for a corpus this size (≈317k points spanning
five very unevenly-sized axes), it preserves **both local neighbourhoods and
global structure** better than t-SNE (local-only) or UMAP (local-biased), and it
is far less sensitive to its hyper-parameters — the authors show the same
settings work across datasets, so we are not tuning per-release. PCA and UMAP are
kept as `--method` options for cross-checking, not for the published map.

## Parameters

| Parameter | Value | Why |
|-----------|-------|-----|
| `n_components` | **2** | The map is a 2-D scatter. |
| `n_neighbors` | **15** | Near-pair count. 15 (vs PaCMAP's own default of 10) matches the `n_neighbors=15` used for the record→record semantic-neighbour index (`embed_neighbors`) and UMAP, so "near" means the same thing across the site. PaCMAP additionally auto-scales the neighbour count with N, so 15 is the floor, not a hard cap. |
| `MN_ratio` | **0.5** (default) | Mid-near pairs ÷ near pairs. Left at PaCMAP's default — this is the knob that gives PaCMAP its global-structure preservation; the paper's ablations show 0.5 is robust and we have no reason to depart from it. |
| `FP_ratio` | **2.0** (default) | Further pairs ÷ near pairs. Default; controls repulsion / cluster separation. Also shown robust in the paper. |
| `init` | **"pca"** | PCA initialization (not random). Three reasons: (1) **reproducibility** — deterministic starting layout; (2) **global-structure anchoring** — the macro arrangement of axes/categories is stable and meaningful rather than an artefact of a random seed; (3) **stability across embedding updates** — when the embedding model or corpus changes, the map's gross layout stays comparable instead of rotating/reflecting arbitrarily. This is why re-embedding (bge-base→bge-large) did not scramble the map. |
| `random_state` | **42** | Determinism. With `init="pca"` the result is effectively fixed; the seed only pins the stochastic pair-sampling so re-runs are byte-identical. |
| distance | Euclidean on the L2-normalized vectors | The vectors are unit-normalized, so Euclidean distance is monotonic in cosine distance (‖a−b‖² = 2−2·cos) — i.e. Euclidean here *is* cosine similarity, matching how the semantic-neighbour index ranks. (UMAP is passed `metric="cosine"` explicitly for the same reason.) |

## Coverage: full corpus, not a sample

The published map runs with `--sample 0` (**all** points), so every record is
plotted — the map is a census, not an estimate. `embed_map.py` defaults to a
**60,000** stratified-by-axis sample only for quick previews (`default_sample`);
the deployed `corpus_map.json` is regenerated over the whole corpus. The sample,
when used, is drawn proportionally per axis (`round(len(members)/N * sample)`)
with the same `--seed`, so even a preview keeps the axis mix representative and is
reproducible.

## What is *not* tuned, and why

We deliberately do **not** grid-search `MN_ratio` / `FP_ratio` / `n_neighbors`
per release. PaCMAP's design goal — and its main empirical result — is that one
setting generalizes, so tuning would (a) cost compute for marginal gain and (b)
make maps across releases incomparable. Stability and reproducibility outrank
squeezing the last bit of cluster separation for an exploratory browse tool.

## Reproducing

```bash
just embed-map                 # PaCMAP, full corpus → docs/data/corpus_map.json
python3 scripts/embed_map.py --method umap --sample 20000   # secondary cross-check
python3 scripts/embed_map.py --method pca                    # secondary (variance-explained)
```
