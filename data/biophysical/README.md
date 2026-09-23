# Biophysical observations: sequence pilot

This directory implements the 12 `PILOT` families in the
[2026-09-23 assessment](../../research/biophysical-traits-2026-09-23/assessment.md).
The other 28 inventory entries remain a roadmap. These are numerical observations
on exact proteins, separate from the ontology's quality classes and from canonical
example qualification. No sixth trait axis, arbitrary high/low classes, or new
qualitative protein assignments are introduced.

`descriptors.yaml` defines the operational quantities and literature references.
`pilot.proteins.txt` selects the 23 reviewed ProteinReferences in the committed
registry that occur in the committed sequence map and have lengths 30–1000.
This is a convenience sample for an engineering pilot, not a representative
protein population. Protein sequences and labels derive from the UniProt
Consortium under CC BY 4.0: 14 references are pinned to release 2026_02 and nine
to 2026_03. Exact sequences remain in
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
| B22 disorder | Import named, versioned per-residue predictor scores | Strictly greater than 0.5; fraction and contiguous segments |

The shipped pilot has **276 observations: 253 OK and 23 NOT_AVAILABLE**. The latter
are disorder entries: no external predictor was run or supplied. The adapter is
implemented and tested using explicitly synthetic inputs; those tests are not
biological evidence. This pilot does not implement the 19 later, five metadata,
or four specialized descriptors, or import experimental measurements.

## Reproduce

From a dependency-installed checkout:

```bash
just calculate-biophysical --proteins data/biophysical/pilot.proteins.txt \
  --output data/biophysical/pilot.observations.jsonl --apply
just validate-biophysical
just biophysical-map --apply
just analyze-biophysical
just check-biophysical-pilot
```

The calculator and overlay builder are dry-run by default. Calculation writes a
JSONL store, a manifest with input hashes/options, and a TSV whose `value` column
is populated only for scalar results. Profiles and composition vectors remain
in JSONL; blank scalar cells are not zeros. Repeating the same inputs and code
in the same Python/math-library environment produces identical bytes and
observation IDs. The calculator's source hash is
recorded on every observation, so code changes deliberately change the IDs.

The embedding snapshot contains only the selected proteins' existing embedding
sequence hashes and metadata, plus the SHA-256 of the parent embedding artifacts.
It makes this pilot reproducible without downloading a model or rerunning ESM-2.
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
length, taxon, and source-release strata. It verifies the FCR identity explicitly.
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

## Schema and vocabulary

`BiophysicalDescriptorCatalog` and `BiophysicalObservation` are new external
LinkML document roots. Nested method, conditions, uncertainty, comparator,
profile, and vector objects are closed. The validator checks registry identity,
hashes, scope, profile windows, composition sums, missingness, thresholded
disorder summaries and content IDs. Unknown fields, nonfinite values, stale
sequence versions, unresolved descriptor IDs and duplicate observations fail.
`just validate-biophysical` validates an individual observation store. CI runs
`just check-biophysical-pilot` to validate the entire published pilot: cohort,
input hashes, all 12 results per protein, numerical replay, manifest, TSV,
analysis and the map sidecar. Numerical replay tolerates 1e-10 rounding differences
across Python/math-library platforms; stored content hashes and metadata must
still agree exactly. This prevents a partial refresh from passing publication
checks. Supply `--disorder path/to/scores.jsonl` to the bundle check when real
predictor inputs are recorded in the manifest.

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
  tracks a versioned, licensed source and durable predictor outputs for B22.
- [#754: cohort expansion and refresh](https://github.com/CultureBotAI/proteintraitsmech/issues/754)
  tracks representative sampling, coverage, runtime/storage and refresh behavior.
- [#755: remaining descriptor roadmap](https://github.com/CultureBotAI/proteintraitsmech/issues/755)
  tracks the 28 later/metadata/specialized entries and their measurement contracts.
