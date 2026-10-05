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
  Disputed A4 uptake studies retain their different cell systems and attribution
  limits. Partial contacts do not become an invented complete transport cycle.

The 8RQF BJU component is a myristoylated glycine representation, not the whole
bulevirtide drug. Its bound substituent and complete BLV have different chemical
identities. Author-described M133 contact is retained in the graph with an
explicit note that it is outside the pilot's 4.5 angstrom shell. Similarly, a
9QZQ E257 side-chain carbon contact is not treated as a carboxylate ligand.

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

The next reviewer should check source-to-claim fidelity, full assay constructs,
ambiguous A7 correspondence, and whether the displayed evidence boundaries are
clear to a gene curator. None of this self-review upgrades PROPOSED assertions.

### Software and publication gates

Focused offline tests cover coordinate identity, ambiguous alignment, exhaustive
small-alignment equivalence, self-mapping, missing ligands, contact chemistry,
model transforms/confidence/least-squares optimality, contact atom identity,
reference/substitution consistency and matching mutant-assay graph bindings,
graph residue scope, consumer pin drift, upstream residue claims, export
checksums, explanation dependency cycles, context/argument separation and unsafe
rendering. Raw downloads are not required for those tests.
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
These findings remain open until their fixes are integrated.

Still required before calling the pilot complete: independent scientific review,
resolution of remaining review issues, final full-tree gates, Pages size audit,
and PR integration. Exact assay-construct reconciliation and A7's human assay
assignment remain explicit scientific gaps; neither can be filled by an alignment
or a model. Generalizing beyond this panel should follow review of this example,
not automatic propagation across protein families.
