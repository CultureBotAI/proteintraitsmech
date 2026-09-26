# Biophysical observations

This directory implements the 12 `PILOT` families in the
[2026-09-23 assessment](../../research/biophysical-traits-2026-09-23/assessment.md).
The [experimental slice](experimental/README.md) adds B25/B26/B27/B30. The remaining
inventory stays on the roadmap. These are numerical observations
on exact proteins, separate from the ontology's quality classes and from canonical
example qualification. No sixth trait axis, arbitrary high/low classes, or new
qualitative protein assignments are introduced.

`descriptors.yaml` defines the operational quantities and literature references.
`cohort.policy.json` selects **256 reviewed ProteinReferences**, retaining all 23
original anchors. Eligible references must match the map and retained embedding
snapshot by accession, full sequence hash and length, contain only standard
residues and be at most 2000 residues long. Remaining slots are filled round-robin
across release, taxon, length and embedding-axis strata, using a seeded SHA-256
ordering within each stratum. Exact duplicate sequences share one representative
unless explicitly retained as anchors. This is a stratified engineering sample,
not a representative proteome sample. No new canonical examples are qualified.

`cohort.manifest.json` records all inputs, selected/excluded IDs, duplicate groups,
stratum counts and resource estimates. There are 1,403 eligible references among
12,705 map proteins. The sample spans 10 taxa and 128,595 residues; length bins
1–100, 101–300, 301–600, 601–1000 and 1001–2000 contain 18, 78, 78, 55 and 27
proteins. It contains 169 SEQUENCE, 33 SEQUENCE+STRUCTURE and 54 STRUCTURE source-axis
bindings. These existing embedding provenance labels are not new trait evidence.
Protein sequences and labels derive from the UniProt Consortium under CC BY 4.0:
15 references use release 2026_02 and 241 use 2026_03. Exact sequences remain in
`data/grounding/protein_registry.jsonl`.

| Family | Implemented method | Default / interpretation |
|---|---|---|
| B01 charge | Independent-site Henderson–Hasselbalch; Bjellqvist tables | pH 7.0, elementary charges, explicit terminal groups |
| B02 pI | Bisection on the same charge model | pH 0–14; tolerance 1e-6; undefined without a unique crossing |
| B03, B04, B05 | KR, DE, KRDE fractions | Histidine excluded from this compositional convention; FCR = B03 + B04 |
| B06 charge patterning | Sawle–Ghosh sequence charge decoration (SCD) | KR=+1, DE=-1, others=0; no terminal charges; no kappa equivalence |
| B08 hydropathy | Mean original Kyte–Doolittle / KYTJ820101 | Higher = more hydrophobic; no solubility inference |
| B09 hydropathy profile | Uniform, stride-one complete windows | Width 19; no edge padding; full reference coordinates |
| B10 hydrophobic moment | Mean vector magnitude on KYTJ820101 | Width 11; assumed rotation 100 degrees; candidate geometry only |
| B13 composition | All 20 amino-acid fractions | One vector; no per-residue trait classes |
| B16 complexity | Shannon compositional entropy in bits | No SEG call or low-complexity/disorder cutoff |
| B22 disorder | metapredict 3.0.2, V3, CPU; full-sequence per-residue scores | Strictly greater than 0.5; fraction and contiguous segments |

The sequence bundle has **3,072 observations, all OK**, including 256 real model
predictions. Predicted disorder is not an experimental measurement. Retained
raw scores, model checkpoint, MIT license, dependency versions and the upstream
numerical example are documented in [disorder/README.md](disorder/README.md).
The separate experimental store has **14 observations across two explicitly
mapped constructs**. Region measurements are not projected onto the whole-protein map.

## Reproduce

From a dependency-installed checkout:

```bash
just refresh-biophysical                # stage and validate, no published writes
just refresh-biophysical --apply        # install the complete validated bundle
just check-biophysical-pilot
just import-biophysical-experiments --apply
just check-biophysical-experiments
```

These commands use retained inputs and need no predictor installation or network.
When registry/map inputs or the cohort policy change, explicitly refresh the
selection with `just select-biophysical-cohort --apply`, rerun the optional
[predictor](disorder/README.md#reproduce-inference), then run the complete refresh.
An ineligible retained anchor fails selection until its policy is explicitly
reviewed. A changed input, missing prediction, stale source hash or mixed run fails
the publication gate. Refresh validates a temporary stage before replacing outputs;
an interruption during installation leaves `.refresh-incomplete` and blocks the gate
until a complete refresh succeeds. Individual calculator commands remain available
for exploratory outputs but are not a complete publication refresh.

Calculation writes a
JSONL store, a manifest with input hashes/options, and a TSV whose `value` column
is populated only for scalar results. Profiles and composition vectors remain
in JSONL; blank scalar cells are not zeros. Repeating the same inputs and code
in the same Python/math-library environment produces identical bytes and
observation IDs. The calculator's source hash is
recorded on every observation, so code changes deliberately change the IDs.

The `cohort.embedding-*` snapshot retains the full existing embedding metadata
(5.24 MB) so the selection itself can be replayed offline. `pilot.embedding-*`
contains the selected subset. The numerical publication bundle is about 24 MB;
the recorded pre-run estimate was 43.7 MB. The selected SCD workload is 2,884,991
charged pairs; its planning estimate covers only the inner loop, not validation,
I/O or predictor setup. No new ESM-2 embeddings are computed.
For other proteins, pass the full `--embedding-proteins` and `--embedding-meta`
artifacts to `just biophysical-map`. Hash/length mismatches, duplicate results,
and incompatible methods/conditions fail. Rebuilding the underlying map requires
rebuilding the overlay; the browser verifies the exact map-file hash before use.

Open `docs/map.html#sequences` through a local HTTP server or Pages. Choose a
continuous descriptor in **Color by**, then use minimum/maximum values and the
availability checkbox. Coverage is shown explicitly; missing values are gray and
initially filtered out. Existing domain, CATH and length filters still apply.
CSV exports include the selected descriptor's values and observation IDs.
Coordinates and embeddings are unchanged. The browser exports every plotted
protein, including currently filtered points, consistent with the existing CSV.

`pilot.analysis.json` reports pairwise Spearman correlations overall and within
length, taxon, and source-release strata, with descriptor status counts in each
stratum. Exact duplicate sequences count once per paired analysis. This does not
control homology or phylogeny. It verifies the FCR identity explicitly.
There are no significance tests, distance weights, or causal claims. Sparse or
constant pairs return null; release strata from one database cannot establish
robustness across independent experimental sources.

## Scope, residues, and methods

Whole-protein calculations use the exact pinned precursor/isoform sequence;
processing or PTMs are not inferred. To calculate a contiguous region, select
one protein and pass `--start N --end M` (1-based inclusive). Default
`--region-termini native` includes a terminal group only if the region contains
that original chain end. `--region-termini cleaved` models a separate free
peptide. The full and analyzed sequence hashes are both stored. Region
observations cannot silently become whole-protein map overlays.

Any nonstandard/ambiguous residue makes the local sequence calculations
`UNDEFINED`; residues are not masked, imputed or removed from denominators.
A profile shorter than its window is `UNDEFINED`. SCD has a quadratic reference
implementation and a default maximum length of 5000; above that limit it is
`NOT_AVAILABLE`, not zero. SCD is defined as zero when there are no charged
pairs. Its conformational interpretation is intended for disordered chains,
not a universal fold classification.

Charge/pI include histidine, cysteine, tyrosine and explicit termini in addition
to KRDE. They do not model ligands, cofactors, PTMs, disulfide state or
structure-dependent pKa shifts. pH 7 is a reference setting, not a claim of a
universal physiological condition. B10 stores the geometry assumption and a
windowed profile instead of treating an entire folded protein as one helix.

To supply disorder predictions, pass `--disorder predictions.jsonl`. Each line
must contain exactly these fields (the short example is synthetic):

```json
{"protein_id":"UniProtKB:P12345","sequence_sha256":"<SHA-256 of the full registry sequence>","predictor":"IUPred3","version":"<actual version>","mode":"long","reference":"<source or run reference>","scores":[0.1,0.6,0.7]}
```

Require one score in [0,1] for every residue of the full reference sequence and
supply the predictor/version/mode actually used. The adapter never contacts a
prediction server. For a region, scores are sliced after validating the full
sequence context. The source object is content-hashed; the input file hash is
also retained in the run manifest. Exactly 0.5 does not exceed the default
threshold. Imported scores remain `MODEL_PREDICTION`, not observed disorder.
Partial predictor coverage is supported: proteins without supplied scores stay
unavailable. Available scores in one map overlay must share their predictor,
version, mode and threshold.
The adapter preserves every reference residue and does not claim a predictor's
alphabet or nonstandard-residue policy. The predictor's documented input
limitations must be checked when acquiring its scores.

## Schema and vocabulary

`BiophysicalDescriptorCatalog` and `BiophysicalObservation` are new external
LinkML document roots. Nested method, conditions, uncertainty, comparator,
profile, and vector objects are closed. The validator checks registry identity,
hashes, scope, profile windows, composition sums, missingness, thresholded
disorder summaries and content IDs. Unknown fields, nonfinite values, stale
sequence versions, unresolved descriptor IDs and duplicate observations fail.
The twelve pilot IDs also have fixed inventory IDs, result shapes and units;
catalog edits cannot bypass their scientific checks. These operational
descriptors require `SEQUENCE_CALCULATION`, except B22, which requires
`MODEL_PREDICTION`. Experimental B25/B26/B27/B30 have a separate catalog with fixed
units, EXPERIMENT evidence, source/construct identity, assay-specific conditions,
sign conventions and reporting gaps. Populated B22 results must retain predictor mode and
the full-reference-sequence prediction context.
`just validate-biophysical` validates an individual observation store. CI runs
`just check-biophysical-pilot` to validate the entire published sequence bundle: cohort policy,
input hashes, all 12 results per protein, numerical replay, manifest, TSV,
analysis and the map sidecar. Numerical replay tolerates 1e-10 rounding differences
across Python/math-library platforms; stored content hashes and metadata must
still agree exactly. CI also verifies retained raw disorder scores, the pinned
upstream example and the experimental source-table replay without installing
metapredict. This prevents a partial refresh from passing publication
checks. Every selected pilot protein must appear exactly once in the source map.
Calculation and verification share the same cohort-file parser, including blank
lines and indented `#` comments. The production check requires cohort and prediction
provenance; its lower-level API still supports minimal legacy test fixtures.

PATO:0001886 (hydrophilicity) and PATO:0001887 (hydrophilic) are imported from the
same 2025-05-14 release as the existing PATO qualities through `seed_obo.py` and
its audited writer. Routing remains `STRUCT_SURFACE` alongside the hydrophobicity
sibling for vocabulary compatibility. That legacy route is broad: the numerical
whole-protein descriptors here have no trait axis and assert no surface area.
No existing charge/solubility/stability/dynamics class is recast as a measurement.
PATO:0002420 is deliberately not mapped to the hydrophobic-moment descriptor.

Primary method references are in the descriptor catalog. Numeric regression
checks use Biopython's documented INGAR/PETER examples and independent geometry,
composition, entropy and SCD examples. The original assessment/audit remain
historical evidence from the user's main checkout; do not regenerate its corpus
counts from a sparse worktree.

## Follow-up work

- [#753: real disorder predictions](https://github.com/CultureBotAI/proteintraitsmech/issues/753)
  is implemented by the retained metapredict run and offline replay gate.
- [#754: cohort expansion and refresh](https://github.com/CultureBotAI/proteintraitsmech/issues/754)
  is implemented by the bounded policy, coverage report and staged refresh.
- [#755: remaining descriptor roadmap](https://github.com/CultureBotAI/proteintraitsmech/issues/755)
  remains the roadmap; B25/B26/B27/B30 now have a bounded experimental implementation.
