# Biophysical follow-up implementation and review, 2026-09-26

Implements #753 and #754, and the first experimental slice of #755, tracked as
[#793](https://github.com/CultureBotAI/proteintraitsmech/issues/793). Base:
`5bf6e9fcb8aea9db21250133a39b7d1a760692db`. Work was isolated from the user's
existing checkout in a separate worktree.

## Results and bounds

The deterministic cohort contains 256 proteins / 128,595 residues across 10 taxa,
retaining all 23 original anchors. The 12,705-point map has 1,452 exact registry
matches; 46 exceed the 2,000-residue budget and three contain unsupported residues.
The remaining 1,403 eligible references have unique full-sequence hashes. The
cohort manifest retains every exclusion and unsampled eligible ID, source-release,
taxon, length and existing embedding-axis count, and the selection seed/policy.

All 3,072 sequence observations are OK. The 256 B22 profiles are actual local
metapredict 3.0.2 / V3 CPU predictions, not synthetic or composition-based scores.
The retained upstream reference example has maximum absolute error zero under
the declared 0.001 tolerance. Full raw sequences/scores, normalized adapter rows,
checkpoint, MIT notice, package versions, hashes and run metadata are committed.
CI verifies the retained artifacts and summary calculations without executing
the neural network. The predictor's training targets prevent treating this as
independent validation of an ESM embedding.

The original sequence map is byte-identical, SHA-256
`eaaf62489d43b55032f274cf62e3e4c4fe458723e948cba74f0165ebb459a749`.
The global protein registry is unchanged. The sequence output bundle is
23,901,938 bytes, below the recorded 43,662,800-byte planning bound. The retained
full embedding binding snapshot adds 5,241,863 bytes without model recomputation.
The SCD estimate covers 2,884,991 charged pairs and explicitly excludes validation,
I/O and predictor setup. These bounds support this run, not an unbounded corpus run.

Exploratory analysis reports overall and length/taxon/release-stratified Spearman
associations, retaining missingness and counting identical sequences once per
pair. It verifies FCR = fraction(KR) + fraction(DE), maximum error
2.78e-17. For example, mean hydropathy versus predicted disorder has overall rho
−0.503 in this selected cohort; this is descriptive and method-related, with no
causal, homology-controlled or population-level interpretation.

The separate experimental store contains eight B25 thermal midpoints, one B26
free energy, two B27 chemical midpoints and three B30 solubilities. It explicitly
maps study-named human ubiquitin to P0CG47 1–76 and mature hen egg-white lysozyme
to P00698 19–147. These are curated reference-frame assignments with stated
sample/sequence uncertainty, not lot-specific sequencing or canonical qualification.
The [experimental guide](../../data/biophysical/experimental/README.md) documents
the source tables, sign convention, reporting gaps and redistribution terms.

## Adversarial review

| Concern | Resolution / evidence |
|---|---|
| Cohort could depend on input order or silently lose an original anchor | Selection is sorted and seeded; shuffled-input test; ineligible anchors fail with an explicit policy-review requirement. |
| Boolean policy version could compare equal to integer 1 | Require an actual integer; regression test rejects `true`. |
| Embedding snapshot hash could disagree with its metadata | Check the full retained snapshot against `source_proteins_sha256`; changed-snapshot test. |
| Predictor outputs could be partial, misaligned, nonfinite or unsupported | Reject sequence mismatch, truncation, missing/duplicate/unknown IDs, booleans, out-of-range scores and masked residues. |
| Retained prediction run could silently change methods or lose provenance | Version/mode, checkpoint, dependency, raw-output and fixture hashes are checked; tampering tests. |
| Mixed publication after interrupted file replacement | Validate a complete temporary stage, reject inputs changed during staging, mark replacement in progress, and fail the gate until replacement completes. Simulated interruption and recovery test. |
| Experimental measurements could be generalized to the wrong molecule | REGION scope, explicit reference-frame and proteoform assumptions, full/analyzed hashes; whole-protein promotion fails validation. |
| Source's negative free energy could be assigned the opposite meaning | Preserve −26.16 kJ/mol and the source formula; explicitly normalize to +26.16 kJ/mol for G(unfolded)−G(native). |
| A reactor concentration could be mislabeled as solubility | Select only Forsythe's equilibrium rows in the retained 2015 table; retain both original-study and compilation citations. |
| TSV could detach numbers from conditions | Export pH, temperature, buffer, uncertainty, reporting gaps, proteoform, normalization, complete conditions and method parameters, including salt composition. |
| Rehashed but wrong measurements could pass generic schema checks | Exact source replay compares all artifacts; mutation test changes and rehashes a measured value and still fails. Reviewed XML hashes are fixed. |

## Verification

- 220 affected tests passed, including sequence-map and map-page regressions.
- Final experimental export/provenance tests: 54 passed after adding complete
  condition/method fields to the TSV.
- Locked Ruff 0.15.20: all repository script/test checks passed.
- Source registry: passed, zero warnings; existing licensing notices remain.
- Complete 256-protein publication gate: passed, including numerical replay,
  cohort policy, retained prediction provenance, TSV, analysis and map bindings.
- Experimental source replay: passed for all 14 measurements.

## Remaining work

#755 stays open: these four experimental families are a bounded first source
slice, not the entire inventory or broad measurement coverage. Existing B17
sequence-length metadata is reused. Other structure, kinetics, interaction,
metadata and specialized branches need their own source and observable choices.
Homology-aware associations, representative proteome sampling and bulk experimental
database licensing are not established by this engineering sample. Source-rights
decisions remain tracked in #517; external-store schema-audit coverage in #512.
