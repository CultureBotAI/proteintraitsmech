# Residue chemistry to protein-trait reasoning: implementation plan

Started: 2026-10-08. Baseline: `9c563d320b0b39548daf119812a5e25298236b63`.
Status: implementation in progress; no completion or scientific sign-off claimed.

## Objective and acceptance contract

Connect residue identity → chemical properties → local molecular interaction →
measured protein-trait consequence, with NTCP S267F and R252H as executable
acceptance cases. A retrieved chain must expose its evidence gaps; intrinsic
chemistry, static proximity, simulation, and assay outcomes are not interchangeable.
An unsupported intermediate must never become a causal edge merely to complete
the diagram. The deliverable is not just another property table or a prose report.

## Current foundation, checked against main

- `MolecularResidueBinding` addresses protein, exact sequence hash, position,
  reference residue, and optional substitution. PR #1029 retrieves complete
  curated mechanisms and their argument/context closure.
- The 20 standard residue terms MOD:00010–MOD:00029 exist as `SEEDED`
  `SEQ_PTM_SITE` records. Reuse these identifiers; do not silently reclassify
  PSI-MOD terms, duplicate them, or upgrade their whole records.
- PATO quality classes and `BiophysicalDescriptorCatalog` exist. The sequence
  calculator contains Kyte–Doolittle and Bjellqvist parameters, but the molecular
  consumer does not connect them to exact residue bindings.
- SLC10 measured transport/localization cases are curated. Their atomistic
  intermediates and historical construct reconciliation have explicit limits.
- PR #714 proposes general evidence assessments; PR #1032 proposes structured
  record reviews. Do not take over those branches or depend on unmerged changes.

## Ordered tasks

### A. Source-reviewed amino-acid property catalog

- [x] Inspect primary chemical-component, property-scale, and ionization sources;
  record stable URLs/DOIs, source versions/hashes, licenses, and short excerpts.
- [x] Add an additive, closed-schema catalog for all 20 standard residues,
  linked to existing MOD residue and PATO property identifiers. Distinguish
  peptide-residue chemistry from a free amino acid and from a modified residue.
- [x] Represent useful side-chain chemistry as structured, evidenced data:
  chemical groups/atoms, aromaticity, hydropathy, and ionization-model parameters.
  Distinguish structure-derived facts from model parameters; avoid unqualified
  hydrogen-bond counts or context-independent claims about charge.
- [x] Add catalog validation, deterministic source replay/consistency checks,
  source-transcription review records, and coverage tests. A machine-assisted
  review must identify its scope and is not independent human scientific approval.

### B. Exact residue chemistry and local-context links

- [x] Bind reference and alternate chemistry through validated sequence addresses
  and immutable catalog identity. Preserve residue-set and multi-protein scope.
- [x] Return property differences with units, methods, protonation/condition
  assumptions, provenance, and explicit limitations.
- [x] Add typed, source-backed local-context assessments attached to existing
  mechanism/binding/assay identities, including unresolved or conflicting links.
- [x] Reject stale pins, mismatched residues/variants/partners, dangling evidence,
  inappropriate evidence-type promotion, unsupported residues, and invented
  complete paths. No automatic annotations or broad-family trait promotion.

### C. SLC10 acceptance cases and user-facing retrieval

- [x] Review the primary S267F/R252H literature and relevant local-structure or
  simulation evidence. Check the Lu/Huang study (DOI 10.1016/j.bpj.2024.03.033)
  rather than inferring a microscopic effect from chemical differences alone.
- [x] S267F: show reference/alternate properties, supported local context,
  taurocholate reduction and estrone-3-sulfate increase as separate assay branches,
  expression controls, and the exact unproved chemistry-to-function links.
- [x] R252H: show reference/alternate ionization and chemistry, supported local
  context, surface-depletion and uptake evidence, mediation/construct limitations,
  and unresolved microscopic steps.
- [x] Extend the production consumer, executable pinned requests, and documentation
  so the complete chain is inspectable without manually joining separate files.
- [ ] Add positive, negative, mutation, and end-to-end tests, including native
  residues, wrong variants, equal coordinates in different proteins, partial
  compound mutants, missing local evidence, and source/citation preservation.

### D. Review, publication, and completion audit

- [ ] Run applicable schema, catalog, molecular, source, writer, focused/full-test,
  and documentation gates. Check generated outputs for stale hashes or omissions.
- [ ] Commit and push using explicit branch refspecs; open PR(s). Prefer one
  coherent integration PR unless independently useful boundaries warrant a split.
- [ ] Perform an adversarial scientific/implementation review; file concrete
  reproduced findings as GitHub issues, fix them, and test the failure modes.
  Identify self-review honestly; do not imply independent human sign-off.
- [ ] Wait for required PR and merge-queue checks, confirm actual merge and issue
  closure, sync local main, and delete only this work's local/remote branch.
- [ ] Audit every checkbox against current files, runtime output, tests, source
  evidence and GitHub state. Remaining biological unknowns may be explicit
  evidence gaps, but missing catalog/integration functionality is not completion.

## Scientific and compatibility boundaries

The catalog must be connected to the consumer, not merely available in a separate
directory. The consumer must return complete source-backed case evidence, not
just generic amino-acid properties. Experimental uptake does not establish a
particular bond, salt bridge, gating step, or necessity/sufficiency claim.
Published simulations can support an explicitly labeled computational hypothesis;
they cannot be described as an experimentally observed contact change or as a
simulation independently reproduced here. Whole-protein trait classes, exact
residue occurrences, and chemical entities remain distinct. Existing assertion
requests, bundle validation, no-match behavior, and annotation refusal must remain
compatible. No unrelated worktrees or unmerged feature branches are modified.

## Verification evidence to record before completion

For each requirement, record the implementing paths and tests; for the catalog,
the 20 identities and reviewed evidence coverage; for each acceptance case, the
production CLI result with exact pins, property contrasts, context, measured
branches and unresolved links; for publication, the reviewed head, issue/PR URLs,
required check results, merge SHA and verified source-branch deletion.

## Implementation log (not completion)

- Added a bounded, new-snapshot-only 22-source fetch route, closed catalog schema,
  deterministic CCD/parameter projection, validation, and property comparison code.
- Downloaded all 20 CCD components and the two Biopython 1.85 parameter sources
  through the shared fetcher. Raw files are ignored and will not be committed.
- The initial source replay exposed a chemical-group classification defect:
  protonated lysine was missed, while amide/guanidino nitrogens were called amines.
  Regression tests were observed failing before correcting the rule. This is a
  finding to retain in the adversarial-review record, not a scientific claim.
- Initial gates: nine fetch-boundary tests, twenty schema-audit tests, and lint
  passed. Catalog review, consumer integration, case curation and publication are
  still pending.

### Integrated implementation and review (2026-10-08)

- Published the 20-entry reference catalog with 22 hashed sources, explicit BSD
  attribution, exact-content self-review and no MOD trait-record promotions.
  Catalog content digest: `f65397d77b660b7f3f3bc564707a75aaa2dcec19e367c698a448f4bd2369939b`;
  complete catalog digest including review:
  `98bc2f0d2a75537a89ac631a30df27ce94113f76507bbee648b0a50fd35a7c94`.
- Added closed-schema residue environments, published simulations and evidence
  ledgers. S267F/R252H reference neighborhoods are replayed from 7ZYI/SIFTS;
  their 4.5-Angstrom shells have respectively 83 and 127 atom pairs. They are
  reference geometry, including sequence neighbors, not mutant contact changes.
- The published Lu/Huang text supplies S267F/TCA simulation context, with one
  short source excerpt. R252H is not among its ten simulated variants. The
  accessible 2023 preprint does not supply this variant result; no preprint claim
  was substituted for the published analysis. Trajectories were not replayed.
- Both production residue requests now expose chemistry, exact context and two
  independent assay branches each, with unresolved molecular mediation. Queries
  without a matching graph still return reference chemistry and scoped context,
  not borrowed variant effects. Original causal graphs remain unchanged.
- Adversarial AI self-review findings (not independent human review):
  [#1033](https://github.com/CultureBotAI/proteintraitsmech/issues/1033), cross-substrate
  simulation transfer, reproduced with a failing test and fixed by explicit
  simulation-partner/assay-substrate matching;
  [#1034](https://github.com/CultureBotAI/proteintraitsmech/issues/1034), amino-group
  classifier defect, fixed with four observed-failing-then-passing regressions;
  [#1035](https://github.com/CultureBotAI/proteintraitsmech/issues/1035), new CHO prose
  mislabeling, corrected against RCSB to glycochenodeoxycholic acid.
- Observed gates so far: 45 catalog/fetch tests; 28 initial integration tests;
  eight targeted case/substrate/compound-mutant regressions; lint, source registry,
  writer audit, schema generation, exact catalog replay and initial bundle replay.
  The first broader focused run had 295 passes and three failures because synthetic
  compound-mutant fixtures retained the real single-mutant ledger. Removed that
  inapplicable ledger from those fixtures while preserving their retrieval assertions;
  separate rejection tests cover stale single-mutant ledgers on compound nodes.
- Offline JavaScript DOM-contract test passes for both case cards, property tables,
  unresolved links and provenance/detail actions. No browser is available through
  CUA, so real-browser visual verification is not claimed. The docs build must run
  in the project environment (`uv run --extra molecular just build-docs`); system
  Python lacks PyYAML.
- Full tests, full corpus validation, full schema audit and docs generation are
  still running. Publication/merge remains pending. Main advanced to `195e24f5e1f`
  (structured record-review adoption #1032); integration must preserve it. That
  review profile concerns native trait-record routes; this catalog self-review
  neither promotes nor certifies the existing 20 SEEDED records.
