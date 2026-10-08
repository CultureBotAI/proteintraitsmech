# SLC10 molecular evidence pilot

This is a **PROPOSED research bundle**, not a set of GO annotations, qualified
trait occurrences, or reviewed canonical examples. It tests whether PTM can
provide reusable, source-backed structure/function explanations while preserving
the distinction between observation, computation, and interpretation.

## Scope

The bounded comparison panel contains human NTCP/SLC10A1 (Q14973), ASBT/SLC10A2
(Q12908), SLC10A4 (Q96EP9), SOAT/SLC10A6 (Q3KNW5), SLC10A7 (Q0GE19), rat Ntcp
(P26435), and mouse Ntcp (O08705). This is **not a single source-family panel**:
the pinned UniProt files assign Q0GE19 to Pfam:PF13593 / PANTHER:PTHR18640;
the other six have Pfam:PF01758 / PANTHER:PTHR10361 cross-references. The bundle's
`scope_note` is generated from those source files. Neither source cross-references
nor gene names qualify an occurrence in PTM's grounding registry.

The related trait records are `Pfam:PF01758` and `Pfam:PF13593`. Their definitions,
status, legacy examples, and grounding registry entries are not changed by this
pilot. NTCP-specific mechanism edges must not be generalized to their entire
families, including the broader SBF/BASS/ACR3 membership.

## Files and evidence boundaries

| Artifact | Meaning |
| --- | --- |
| `curation.yaml` | Authored assay observations, interpretations, and local mechanism graphs; DOI/URL evidence and limitations remain attached. |
| `pilot.json` | Generated, closed-schema `MolecularEvidenceBundle`; exact sequences, source hashes, contacts, correspondence, model comparisons, observations and explanations. |
| `gene-review-fixture.json` | Explicitly labelled consumer test, **not Chris's repository**; pins the complete bundle bytes and target sequence. |
| `gene-review-integration.json` | Read-only integration pin for the actual `ai4curation/ai-gene-review` SLC10A4 review; exact upstream commit, file hash, annotation locator and expected claim count. Not upstream adoption. |
| `residue-query-s267f.json`, `residue-query-r252h.json` | Executable consumer requests for exact NTCP substitutions; return curated mechanisms and evidence, not predicted effects or upstream annotations. |
| `docs/slc10.html` | Comparison page, loaded separately from the main corpus browser. |
| `docs/data/slc10-pilot-v1.json` | Generated, ignored, byte-identical export built for Pages. Its sibling manifest records SHA-256 and byte count. |

The schema is `src/proteintraitsmech/schema/proteintraitsmech.yaml`, not the
curation input format. Molecular data have an external bundle root so they do not
masquerade as one trait record per protein. Molecular mechanisms reuse the existing
`CausalGraph` structure with explicit protein scope and sequence-checked residue
bindings. Every graph edge has a DOI/stable URL and a short supporting excerpt.
Local residue sets and cavities are explicitly local, not new ontology classes.

### What the computational objects mean

- **Experimental contact shells:** 7ZYI (substrate-bound), 9QZQ
  (nanobody-inhibited), and 8RQF (bulevirtide-bound) stay distinct. Each selected
  ligand instance is enumerated from coordinates. SIFTS maps deposited residues
  to the exact pinned NTCP sequence. Alternate atoms retain their occupancy and
  identity; pairwise proximity does not assert that every conformer coexists.
- **Cutoff sensitivity:** the same source/ligand is recomputed at 4.0, 4.5, and
  5.0 angstrom. N/O/S side-chain proximity is distinguished from carbon proximity,
  but neither alone proves chemical coordination, necessity, or sufficiency.
- **Sequence correspondence:** global BLOSUM62 at two affine-gap settings;
  an optimal-path DAG considers every tied optimal alignment without an
  enumeration cap. Its optimal score is cross-checked with Biopython. A column
  with any gap or disagreement remains unresolved. Consensus is still a
  computational hypothesis, not independent proof of evolutionary correspondence.
- **Predicted geometry:** AlphaFold DB v6 apo models for NTCP, A4 and A7 are
  compared with 7ZYI. Sequence pairing precedes fitting. All observed consensus
  CA pairs with target pLDDT >=70 enter an untrimmed least-squares fit. The transform,
  fit count, per-residue confidence, coordinates and residuals are retained.
  No experimental ion is transferred to a model. Large residuals cannot be read
  as measured movements, and low residuals do not establish activity.
- **Assays:** detected, not detected, and not assessed are separate outcomes.
  A7's exact human assay assignment remains unverified in this extraction; that
  is an evidence gap, not a claim that no experiments exist. Historical assay
  constructs are not silently equated to present-day reference sequences.
- **Perturbations:** E257A is a typed substitution relative to the human NTCP
  reference, with a linked uptake-reduction observation and graph. The checksum
  pins reference coordinates, not a complete mutant or tagged assay construct.
  The 2014 study reports comparable expression controls and a 95-99% uptake
  reduction across a group including E257A; the pilot does not invent an exact
  E257A-specific estimate or turn reduced uptake into complete absence. This
  tests a functional consequence without assigning a unique microscopic cause.
- **Explanations:** the A4 residue-loss explanation and the sufficiency of mouse
  preS1 binding for infection are assessed independently of the assay outcomes.
  A7's site-divergence explanation is explicitly UNRESOLVED. `context_assertions`
  connect assay and computational context without counting as arguments for an
  explanation; the consumer returns these separately from its supporting/challenging
  `basis`. Interpretation dependencies cannot justify themselves through cycles.
  Nested explanations retain their complete argument closure and per-edge
  SUPPORTS/CHALLENGES polarity; context is collected separately at every level.
  Disputed A4 uptake studies retain their different cell systems and attribution
  limits. Partial contacts do not become an invented complete transport cycle.

The 8RQF BJU component is a myristoylated glycine representation, not the whole
bulevirtide drug. Its bound substituent and complete BLV have different chemical
identities. Author-described M133 contact is retained in the graph with an
explicit note that it is outside the pilot's 4.5 angstrom shell. Similarly, a
9QZQ E257 side-chain carbon contact is not treated as a carboxylate ligand.

## Residue-to-function development cases

The second development pass adds two **SUPPORTED / PROPOSED** explanations.
`SUPPORTED` assesses the bounded claim; it does not mean expert review or a
complete atomistic mechanism. Sequence-bound substitutions, assay context,
source excerpts and unresolved questions remain attached.

| Case | Graph | Evidence boundary |
| --- | --- | --- |
| NTCP R252H | Substitution → surface-depleted state → reduced taurocholate uptake | Localization and uptake were measured; the second edge is the authors' mediation interpretation, not an independently isolated effect. [Vaz et al., Figure 2](https://doi.org/10.1002/hep.27240). |
| NTCP S267F | Substitution → decreased taurocholate uptake; substitution → increased estrone-3-sulfate uptake | Substrate-specific assay branches, with surface-expression controls; no invented binding/gating intermediate. [Ruggiero et al., Figures 1–4 and Table 1](https://doi.org/10.1074/jbc.RA120.014889). |

The R252H surface assay's negative result is not zero residual transport. Its
FLAG-tagged localization construct is not assumed identical to the Figure 2A
uptake construct, whose tag is not specified in that panel. S267F's
twofold estrone-sulfate result belongs to the initial uptake assay, not the
surface-normalized comparison or kinetic efficiency. Neither mechanism explains
SLC10A4 or SLC10A7 by analogy. Their previous challenged/unresolved explanations
remain unchanged. These cases advance the explanatory goal but do not finish it.

The molecular-causal-graphs skill informed the node/edge inventory and required
unsupported intermediates to remain questions. The existing external bundle
retains protein-instance scope; no broad-family trait graph or GO annotation was
promoted. New edges distinguish experimental results from author interpretation
in their descriptions. Evidence type at edge level is currently descriptive,
not a separate schema enum.

Next research target: assess the [Lu and Huang simulation study](https://doi.org/10.1016/j.bpj.2024.03.033)
for candidate S267F molecular steps. Its simulations have not been curated or
replayed here; they must remain distinct from the measured uptake evidence.

## Reproduce

Install the project's development and molecular extras:

```bash
uv sync --extra dev --extra molecular
```

Acquisition is dry-run unless `--apply` is supplied. These commands require a
**new** snapshot directory; do not overwrite a completed snapshot. Verify the
upstream UniProt release before choosing `--expect-release`. A changed release
must not be relabelled as the old one.

```bash
just fetch-slc10-pilot --snapshot pilot-2026-10-05 --expect-release 2026_03
just fetch-slc10-models --snapshot af-v6-2026-10-05
```

Add `--apply` to acquire the reviewed plan. Public raw files stay ignored under
`data/raw/slc10/`. Fixed downloads use the shared fetcher. Completion manifests
are written last; builders reject partial snapshots, changed hashes and mixed
identity/version frames. UniProt is CC-BY-4.0, PDB/SIFTS inputs are CC0-1.0,
and AlphaFold predictions are CC-BY-4.0; source-specific licence URLs are retained.
Each source artifact declares its role and protein or structure identity. Sites
and model comparisons must reference the matching structure, residue-mapping and
prediction roles; an arbitrary existing source ID is not sufficient. Resolved
sequence correspondences must have unique, strictly increasing target positions.
Optional fields are omitted when unavailable: explicit JSON nulls are rejected
with their object paths rather than accepted as missing values.

With the original snapshots available:

```bash
just build-slc10-pilot \
  --snapshot data/raw/slc10/pilot-2026-10-05 \
  --model-snapshot data/raw/slc10/af-v6-2026-10-05
```

This is a dry run. Use `--apply` to regenerate the fixed bundle destination, or
`--check` to require byte-identical reproduction. Upstream mutable URLs may no
longer serve old bytes in the future: a hash mismatch is a refusal, not permission
to silently update an old snapshot. Preserve the original raw snapshot for replay.

```bash
just validate-molecular-evidence data/molecular/slc10/pilot.json
just build-slc10-docs
just build-slc10-docs --check
just consume-molecular-evidence \
  --bundle data/molecular/slc10/pilot.json \
  --request data/molecular/slc10/gene-review-fixture.json
```

The consumer is read-only. It verifies the complete export checksum, bundle
identity/version, exact protein and sequence, and claim ID. It returns evidence,
supporting/challenging assertions, open questions, limitations and
`annotation_action: NONE`. Any changed bundle bytes require an explicit new
consumer pin, even while v1 remains a draft.
The `basis` includes intermediate explanations and terminal arguments once each;
`argument_edges` preserves which explanation each assertion supports or
challenges. `context_edges` similarly preserves attribution without using context
to justify upstream residue claims. No flattened net polarity is inferred.

### Residue-level mechanism retrieval

The same consumer can start from an exact residue/variant rather than requiring
the caller to know an explanation ID:

```bash
just consume-molecular-evidence \
  --bundle data/molecular/slc10/pilot.json \
  --request data/molecular/slc10/residue-query-s267f.json

just consume-molecular-evidence \
  --bundle data/molecular/slc10/pilot.json \
  --request data/molecular/slc10/residue-query-r252h.json
```

A residue request replaces `assertion_id` with `residue_query`, retaining all
other bundle, protein, sequence, usage and fixture fields. For example:

```json
"residue_query": {"position": 267, "residue": "S", "substituted_residue": "F"}
```

Positions are one-based in the pinned **reference** sequence. `residue` must
match that sequence; a supplied `substituted_residue` must differ. Omitting
`substituted_residue` selects only unsubstituted graph bindings, **not all
variants at that position** and not a verified wild-type assay construct.
For example, E257 retrieves the curated sodium-coordination residue set, while
E257A retrieves the tested uptake-reduction mechanism. A single-substitution
query does not match one component of a multi-substitution residue node.
Residue requests cannot also select an assertion or an upstream review.

The response includes:

- `retrieval_status`: `MATCHED_CURATED_MECHANISMS` or `NO_CURATED_MECHANISM`.
  The latter means no matching curated graph binding in this pinned bundle,
  **not** no biological effect, no literature, or no other evidence in the bundle.
- `mechanisms`: complete, unchanged graph fields, including all residue bindings,
  protein/trait scope, per-edge DOI/URL references and excerpts, review status and
  limitations. `matched_residue_bindings` identifies the exact query matches
  without reducing a residue-set claim to an individual-residue claim.
- Each mechanism's `assertions`: its explicitly referenced assertions plus the
  complete supporting/challenging and context closure. Assay conditions,
  constructs, localization controls, evidence origin, claim assessment and open
  questions remain attached. `argument_edges` and `context_edges` preserve their
  attribution; context is not silently counted as support.
- `retrieval_limitations`, the original request, bundle scope and source metadata,
  with `annotation_action: NONE` unchanged.

Existing assertion requests now also return `mechanisms`, but only where the
graph explicitly lists the requested assertion in `assertion_refs`. Shared
citations, supporting assertions, family membership or sequence correspondence
do not select or transfer a graph. The additional consumer response fields are
not new fields in the stored `MolecularEvidenceBundle`.

This is evidence-preserving retrieval, not automatic causal-path composition or
variant-effect prediction. S267F's two substrate branches stay separate; R252H's
author-interpreted mediation edge does not become an isolated experimental result.
Existing assertion-level evidence types are preserved; machine-readable
edge-level evidence assessments remain follow-up work, coordinated with
[PR #714](https://github.com/CultureBotAI/proteintraitsmech/pull/714).
No bundle bytes, scientific claims or review statuses change for this consumer
extension, and no new simulation result is incorporated.

### Read-only check against the actual gene review

The public SLC10A4 review at commit
`1d36e6d20901b617d02a69388f13dbe3c26ade96` contains the seven retained sodium-site
residue claims shown in the report, under
`existing_annotations[9].review.propagation_review.residue_claims`. The integration
request pins the complete 75,151-byte source file and that annotation's identity
and action. The consumer checks each anchor/target against PTM's exact sequences
and the two sodium-site comparisons cited by the explanation. All seven matched
in the live read-only check; E257 maps to E335, for example.

To reproduce without retaining or modifying upstream files, stream the pinned
GitHub API response to the consumer (requires `gh`):

```bash
set -o pipefail
gh api -H 'Accept: application/vnd.github.raw+json' \
  'repos/ai4curation/ai-gene-review/contents/genes/human/SLC10A4/SLC10A4-ai-review.yaml?ref=1d36e6d20901b617d02a69388f13dbe3c26ade96' \
  | uv run --extra molecular python scripts/consume_molecular_evidence.py \
      --bundle data/molecular/slc10/pilot.json \
      --request data/molecular/slc10/gene-review-integration.json \
      --upstream-review -
```

Alternatively, pass an existing checkout file as `--upstream-review PATH`; the
same checksum requirement applies. This is a bounded, read-only consumer check,
not a raw-data fetch or an upstream editor. The source file is not vendored.
Its [upstream licence](https://github.com/ai4curation/ai-gene-review/blob/1d36e6d20901b617d02a69388f13dbe3c26ade96/LICENSE)
remains applicable. The result does **not** adopt the upstream `STRUCTURE` method
label as experimental evidence, certify site necessity, or endorse its GO action.
No upstream review has been modified to cite PTM; that adoption is a separate step.

Serve `docs/` over HTTP to inspect the page; opening it directly as `file://` does
not provide the required fetch/secure-context behavior. The optional real-browser
check uses a fresh temporary Chrome profile, never the user's existing profile:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory docs
# In another terminal, with a locally installed Chrome executable:
node scripts/check_slc10_page.mjs /path/to/chrome http://127.0.0.1:8765/slc10.html
```

## Review and release gates

### Scientific claim audit (author self-review, not independent sign-off)

The supplied report motivates questions; it does not replace primary evidence.
The following boundaries were checked against the bundle and original sources:

| Claim or shortcut | Pilot disposition |
| --- | --- |
| A4 negative transport implies loss of the NTCP sodium-site identities | CHALLENGED by sequence-derived comparisons; the [2015 assay](https://doi.org/10.1186/s12868-015-0174-2), Figure 4, remains a separate, condition-specific observation. The 2013 cellular-accumulation report is retained with disputed attribution, not erased. |
| A contact shell establishes residues required for function | Not accepted. [7ZYI](https://doi.org/10.2210/pdb7ZYI/pdb) supplies coordinates; proximity is not an intervention or a universal necessity test. |
| Main-chain contact makes a substitution harmless | Not accepted. Atom role is recorded; no functional-neutrality verdict is derived from it. |
| A7 sequence/model differences explain a human negative assay | UNRESOLVED. The [2007 study](https://doi.org/10.1016/j.ejcb.2007.06.001) needs full-text species/construct reconciliation; correspondence candidates and model residuals cannot supply that missing experiment. |
| SOAT is a generic bile-acid transport control | Not accepted. The [original study](https://doi.org/10.1074/jbc.M702663200) distinguishes sulfated substrates, including taurolithocholic acid-3-sulfate, from the tested nonsulfated bile acids. |
| E257A proves complete loss or one unique microscopic mechanism | Not accepted. The [2014 study](https://doi.org/10.1128/JVI.03478-13), Figure 6A/B, supports reduced uptake with expression controls, not a unique explanation of the reduction. |

Separate scientific-agent review of commit `05730841aaf46f4578095c3ddb1fcfa20435e0f4`
checked source-to-claim fidelity, assay boundaries and the original coordinate
snapshots. It found an incorrect sodium-coordination figure locator, corrected
to Figure 1i and Supplementary Figure S7
([#1011](https://github.com/CultureBotAI/proteintraitsmech/issues/1011)), and no
substantive scientific blocker within that review's scope. This is separate agent
review, not human expert sign-off or experimental verification. Full historical
construct reconciliation and A7's exact human assay assignment remain unresolved;
neither author nor separate-agent review upgrades PROPOSED assertions.

### Software and publication gates

Focused offline tests cover coordinate identity, ambiguous alignment, exhaustive
small-alignment equivalence, self-mapping, missing ligands, contact chemistry,
model transforms/confidence/least-squares optimality, contact atom identity,
reference/substitution consistency and matching mutant-assay graph bindings,
graph residue scope, consumer pin drift, upstream residue claims, export
checksums, explanation dependency cycles, context/argument separation and unsafe
rendering. Consumer tests also cover exact residue/variant retrieval, full graph
and evidence preservation, grouped residue scope, partial multi-mutant refusal,
no-match abstention, A4/A7 non-transfer, and the executable query examples.
Raw downloads are not required for those tests.
The `--check` replay is a separate integration test requiring the original inputs.

```bash
uv run --extra molecular pytest \
  tests/test_molecular_evidence.py tests/test_fetch_slc10_pilot.py \
  tests/test_fetch_slc10_models.py tests/test_slc10_docs.py \
  tests/test_consume_molecular_evidence.py
just lint
just test
just audit-schema
just gen-schema
just validate-all
just sources-check
just audit-writers
uv run just build-docs
just validate-history
just check-vendored-sync
```

Also inspect the rendered page, run the Pages size audit on the built site, and
review the scientific interpretation independently. A green schema or test is not
evidence that a biological mechanism is true.

Browser checks have passed for desktop and mobile rendering, site switching,
evidence dialogs, accessible graph titles, and stable assertion deep links;
the corresponding screenshots were visually inspected. Local adversarial review
found and fixed contact-residue/fit-optimality gaps
([#1005](https://github.com/CultureBotAI/proteintraitsmech/issues/1005)) and unnamed
graph dialogs ([#1006](https://github.com/CultureBotAI/proteintraitsmech/issues/1006)).
An additional reproduced gap allowed indirect explanation self-justification
([#1008](https://github.com/CultureBotAI/proteintraitsmech/issues/1008)); the validator
now rejects evidence-dependency cycles without banning biological feedback loops.

Separate technical-agent review also reproduced and prompted fixes for
many-to-one or reversed correspondences
([#1012](https://github.com/CultureBotAI/proteintraitsmech/issues/1012)), mismatched
source roles/identities ([#1013](https://github.com/CultureBotAI/proteintraitsmech/issues/1013)),
foreign-protein evidence hidden in explanation dependencies
([#1014](https://github.com/CultureBotAI/proteintraitsmech/issues/1014)), dropped
nested consumer arguments ([#1016](https://github.com/CultureBotAI/proteintraitsmech/issues/1016)),
and null-triggered validator crashes
([#1018](https://github.com/CultureBotAI/proteintraitsmech/issues/1018)). Each has
targeted regression coverage; these findings concern enforcement, not observed
corruption of the pilot's source coordinates.

Release requires resolution of review issues, final full-tree gates, Pages size
audit and PR integration. Exact assay-construct reconciliation and A7's human assay
assignment remain explicit scientific gaps; neither can be filled by an alignment
or a model. Generalizing beyond this panel should follow review of this example,
not automatic propagation across protein families.
