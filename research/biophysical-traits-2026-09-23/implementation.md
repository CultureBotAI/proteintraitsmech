# Biophysical pilot implementation — 2026-09-23

Implemented in the isolated `feat/biophysical-observations` worktree, starting
from commit `700b6f7bced` (the local `origin/main` ref at worktree creation).
The original assessment, inventory and main-checkout audit are preserved as
historical inputs. This sparse worktree is not a replacement corpus census.

The [pilot guide](../../data/biophysical/README.md) documents the new external
LinkML descriptor/observation roots, all 12 operational descriptors, scoped
sequence calculations, missingness policy, predictor-score adapter, quality
anchors, and reproduction commands. PATO hydrophilicity/hydrophilic remain
quality classes imported with the existing audited OBO writer. Whole-chain
numerical descriptors do not inherit the importer's broad surface category.

The reproducible selection contains 23 reviewed, map-matched registry proteins
of length 30–1000: 14 from UniProt release 2026_02 and nine from 2026_03. Each
observation retains its own release, sequence version when present, and exact
sequence hash. There are 276 observations: 253 calculated results and 23 explicit
missing disorder predictions. No disorder predictor was run and no experimental
measurements were imported.

The existing sequence-map coordinates are unchanged. A hash-bound sidecar adds
continuous scalar colors, numeric bounds, missing-value filtering and CSV values
with observation IDs. It is based on verified embedding-sequence bindings, not
accession matching alone. Local/browser checks reject a stale map sidecar.

The [analysis](../../data/biophysical/pilot.analysis.json) contains 11 overall,
length, taxon and source-release strata. The FCR = basic + acidic fraction
identity holds across all 23 proteins with maximum absolute floating-point
error 2.78e-17. Overall charge/pI Spearman rho is 0.8755; those quantities use the
same titration model, so the correlation is not independent biological evidence.
The selected cohort and release strata do not establish generalization across
independent experimental sources. No descriptor-based distance metric or
mechanistic conclusion is introduced.

Validation performed:

- 361 targeted tests passed across biophysical calculations/provenance, existing
  schema/strict validation, map/page behavior, source registration, OBO emission,
  shared schema governance and category consistency.
- All 276 observations passed closed LinkML and registry/semantic validation;
  both new PATO YAMLs passed strict record validation.
- Repository-wide Ruff, source-registration and writer-safety audits passed;
  schema reachability and axis/category coherence passed. Enum-usage counts
  from the sparse checkout are not whole-corpus metrics.
- Generated Pydantic models compiled successfully.
- Headless Chrome verified loading, 23-protein coverage, numerical filtering,
  CSV export, map switching, stale-sidecar rejection and a 390-pixel-wide layout.
  No JavaScript runtime errors were observed.

The initial broader test run hit the sandbox's read-only shared uv cache;
rerunning with a writable temporary cache and the existing environment passed.
The remaining 28 inventory entries are the assessment's later/metadata/specialized
roadmap. The B22 adapter is available, but real disorder values require supplied
predictor outputs with their actual version, mode and full-sequence hash.

## Publication integration

Rebased the isolated feature branch onto current main (`183a1ad443b`). Added a
read-only publication check that replays calculations and validates the cohort,
input hashes, manifest, TSV, analysis and sequence-map sidecar together. The
existing checks workflow now runs this gate. It detects partial refreshes and
rehashed but numerically wrong observations, while allowing 1e-10 floating-point
roundoff across Python/math-library platforms. Stored hashes and all provenance
metadata remain exact checks.

Added a Pages guide and declared the new browser helper in Jekyll's publication
configuration. The CLI recipes now preserve arguments containing spaces without
shell reinterpretation.

The final regression run passed all 361 targeted tests, including 18 publication
gate and CLI argument tests. The committed pilot passed the complete bundle gate.
Partial disorder-prediction coverage now displays available scores alongside
missing entries, in either input order, while incompatible available predictor
versions still fail validation.

Follow-ups are recorded in [#753](https://github.com/CultureBotAI/proteintraitsmech/issues/753)
(real disorder outputs), [#754](https://github.com/CultureBotAI/proteintraitsmech/issues/754)
(expanded cohort and refresh workflow), and [#755](https://github.com/CultureBotAI/proteintraitsmech/issues/755)
(the other 28 inventory entries and reuse decisions). The guide links to these
issues and records the implemented scope separately from those follow-ups.
