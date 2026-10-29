# Independent post-curation scientific review of eight structural motifs

- Review: 20261028T185849Z-structural-motif-post-curation
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-28T18:54:39Z
- Finished UTC: 2026-10-28T18:58:49Z
- Reviewer: Codex cavity_binding_evidence (independent)
- Completion: completed
- Verdict: pass_with_limitations
- Scientific review: true

## Summary

All eight applied records have positive source-backed scientific assessments. Six original findings are resolved with exact predecessor lineage; the minor method-coverage finding remains deferred. Schema, graph and grounding checks pass without implying software execution, human REVIEWED status or protein qualification.

## Scope And Provenance

Exactly the eight motif/parent targets in the original scientific review; current applied working-tree bytes.

Selection: Complete original target set, not a sample; all predecessor finding target memberships retained.
Coverage: full; 8 reviewed / 8 in the declared population.
Source: working_tree at Git base c4147394c698324ae537c0c63c2c9f6647c4f4fc.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| proteintraitsmech:HELIX_TURN_HELIX | data/traits/structure/secondary/helix-turn-helix.yaml | generated | helix-turn-helix |
| proteintraitsmech:BETA_ALPHA_BETA | data/traits/structure/secondary/beta-alpha-beta.yaml | generated | beta-alpha-beta motif |
| proteintraitsmech:GREEK_KEY | data/traits/structure/secondary/greek-key.yaml | generated | Greek key motif |
| proteintraitsmech:BETA_HAIRPIN | data/traits/structure/secondary/beta-hairpin.yaml | generated | beta hairpin |
| proteintraitsmech:BETA_TURN | data/traits/structure/secondary/beta-turn.yaml | generated | beta turn |
| proteintraitsmech:SUPER_SECONDARY_MOTIF | data/traits/structure/secondary/super-secondary-motif.yaml | generated | super secondary motif |
| proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF | data/traits/structure/secondary/polypeptide-structural-motif.yaml | generated | polypeptide structural motif |
| proteintraitsmech:TURN | data/traits/structure/secondary/turn.yaml | generated | turn |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Strict LinkML validation | passed | True | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | Eight selected records pass with zero errors. |
| Causal graph structural audit | passed | True | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | No graphs present in these eight records; audit exits0 with no errors/warnings. |
| Native UniProt grounding semantic validation | passed | True | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | Eight selected records pass the legacy-compatible semantic check; this does not qualify protein occurrences. |
| Exact applied ledger and native-status consistency | passed | True | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | All eight target SHA256 values equal their maintained ledger output_sha256; records remain PROPOSED with honest agent history and no canonical example promotion. |
| Independent scientific scope and source comparison | passed | True | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | Inspected source-native terms/manuals and primary abstracts/full source sections support the bounded definitions, relations, notation and scoped representation; completed scientific judgement is not inferred from syntax checks. |
| Execution of documented structural/sequence detectors | skipped | False | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | Recipes are documentation checked only. PROMOTIF authorized-installation prerequisite, HTH screening limits and manual Greek-key classification remain explicit. |

## Scientific And Domain Assessments

### Class identity, evidence, hierarchy, representation and detection scope

identity: supported. Targets: proteintraitsmech:HELIX_TURN_HELIX.

Retained two-helix class with proper motif parent and SO mapping. Sequence-screen limitations are explicit; PDB1LMB is a supported containing structure with chain/version information and no invented motif bounds.

### Class identity, evidence, hierarchy, representation and detection scope

identity: supported. Targets: proteintraitsmech:BETA_ALPHA_BETA.

Parallel paired strands and intervening alpha helix are explicit. E-H-E is contextualized by those geometric criteria; Rossmann membership is not asserted as class identity.

### Class identity, evidence, hierarchy, representation and detection scope

identity: supported. Targets: proteintraitsmech:GREEK_KEY.

Connectivity is specified without requiring one shape. PROMOTIF supplies topology data; curator inference is explicit and appropriately labelled rather than presented as an automatic Greek-key call.

### Class identity, evidence, hierarchy, representation and detection scope

identity: supported. Targets: proteintraitsmech:BETA_HAIRPIN.

Sequence-adjacent antiparallel paired strands and a variable connector define the class. Wrong xrefs are removed; bare beta-beta is not equated with hairpin.

### Class identity, evidence, hierarchy, representation and detection scope

identity: supported. Targets: proteintraitsmech:BETA_TURN.

The compact four-residue convention is operationally specified, with nonhelical central residues and optional end-to-end hydrogen bond. It is correctly placed under the broad motif class rather than DSSP T.

### Class identity, evidence, hierarchy, representation and detection scope

identity: supported. Targets: proteintraitsmech:SUPER_SECONDARY_MOTIF.

The umbrella describes spatially connected recurring secondary elements and inherits the broader motif class. False helix equivalence and a universal matcher claim are absent.

### Class identity, evidence, hierarchy, representation and detection scope

identity: supported. Targets: proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF.

The class correctly says independent globular stability is unnecessary, retaining SO identity and attribution without treating the whole source enum as equivalent.

### Class identity, evidence, hierarchy, representation and detection scope

identity: supported. Targets: proteintraitsmech:TURN.

The class preserves the algorithm-defined DSSP T state, uses ss_string T and the appropriate elementary-state parent. It no longer acts as the universal beta-turn superclass.

### Source-specific rights disposition

provenance: supported. Targets: proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN.

All eight state an explicit reviewed rights basis; three retain SO attribution and five license only new project-authored factual synthesis. Cited sources/software remain separate, and no copied matrices, figures or code are introduced.

### Remaining class-specific detector qualification

completeness: concern. Targets: proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN.

Documented recipes have not been executed. HTH remains a sequence screen, Greek-key requires manual connectivity review, and the two umbrella classes have no universal verified classifier.

## Findings

### wrong-equivalence: Peptide-helix and whole-enumeration xrefs assert false motif equivalence

major / resolved / confirmed; issue key: proteintraitsmech-structural-motifs-wrong-equivalence.

Removed the peptide-helix and whole-vocabulary equivalences from every original affected target; SO0001079 retained for the broad motif.

Disposition: Removed the peptide-helix and whole-vocabulary equivalences from every original affected target; SO0001079 retained for the broad motif.

### definition-support: Named motif definitions and topology claims need class-specific evidence

major / resolved / confirmed; issue key: proteintraitsmech-structural-motifs-definition-support.

Each originally affected definition now has class-specific authority or primary-source support; unsupported universal DNA-binding/Rossmann/superlative claims are removed.

Disposition: Each originally affected definition now has class-specific authority or primary-source support; unsupported universal DNA-binding/Rossmann/superlative claims are removed.

### beta-turn-parent: Broad beta-turn class is placed beneath a narrower DSSP T state

major / resolved / confirmed; issue key: proteintraitsmech-structural-motifs-beta-turn-parent.

The broad geometric beta turn now inherits POLYPEPTIDE_STRUCTURAL_MOTIF; TURN retains its DSSP-state identity and parent.

Disposition: The broad geometric beta turn now inherits POLYPEPTIDE_STRUCTURAL_MOTIF; TURN retains its DSSP-state identity and parent.

### motif-stability: Polypeptide structural motif incorrectly excludes independently stable units

major / resolved / confirmed; issue key: proteintraitsmech-structural-motifs-motif-stability.

Independent stability is now unnecessary rather than prohibited; SUPER_SECONDARY_MOTIF inherits the broader structural motif.

Disposition: Independent stability is now unnecessary rather than prohibited; SUPER_SECONDARY_MOTIF inherits the broader structural motif.

### topology-layer: Topology tokens omit distinguishing geometric criteria

minor / resolved / confirmed; issue key: proteintraitsmech-structural-motifs-topology-layer.

Geometric criteria supplement the retained tokens: BAB pairing/orientation, Greek connectivity, hairpin connector scope and beta-turn operational criteria. HTH and TURN states are explicitly sourced.

Disposition: Geometric criteria supplement the retained tokens: BAB pairing/orientation, Greek connectivity, hairpin connector scope and beta-turn operational criteria. HTH and TURN states are explicitly sourced.

### method-coverage: Category DSSP fallback is not a complete motif classifier

minor / deferred / confirmed; issue key: proteintraitsmech-structural-motifs-method-coverage.

Class-specific documented methods and limits now replace the undifferentiated fallback. Remaining qualification is deferred: PROMOTIF authorization/setup and execution were not performed, HTH is a sequence screen, Greek-key requires curator connectivity review, and broad motif umbrellas have no single verified classifier.

Disposition: The scientific scope defect is repaired, but the original method-coverage issue is not closed because executable qualification and universal coverage remain unestablished.

### rights-provenance: Source and license disposition is unresolved for selected records

major / resolved / confirmed; issue key: proteintraitsmech-structural-motifs-rights-provenance.

The maintained source-specific dispositions and record evidence now distinguish SO-derived content, project-authored synthesis, cited article rights and conditional software access.

Disposition: The maintained source-specific dispositions and record evidence now distinguish SO-derived content, project-authored synthesis, cited article rights and conditional software access.

## Recommended Actions And Acceptance Checks

### future-method-qualification

When separately authorized and supplied with software prerequisites, qualify selected detector outputs against reviewed structures and explicit subtype criteria. Keep predictions, manual classification and demonstrated geometry distinct; no universal umbrella matcher is assumed.

- Record licensed/software-versioned execution and actual outputs for the selected method.
- Document the topology/geometry decision rule and appropriate positive and negative examples.
- Do not qualify canonical UniProt occurrences without the native grounding workflow.

## Category Boundaries

- retain: proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN. Named motifs, broad structural-motif umbrellas and the DSSP assignment state have distinct identities. The beta-beta wording spans hairpin and arch contexts, so no exact synonym/merge is introduced.

## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| applied | research/structural-traits-20261028/cavities/motif-post-inspection.json; Native source hashes; complete eight applied target records | supports | All eight records were read after root signaled applied outputs. Reviewed fields include definitions, hierarchy, equivalence, representations, evidence, licenses, methods and agent history. |
| owner | data/curation/structural_trait_curations.yaml; Eight selected motif entries and shared guarded transforms | supports | Maintained ledger binds exact input/output hashes and seeder preimages. Applied target hashes match the selected ledger outputs; history remains PROPOSED and agent-attributed. |
| prior | reviews/structured/20261028T184459Z-structural-motif-initial-audit/review.yaml; Seven original finding identities and target sets | supports | This successor explicitly carries all seven issue keys and their complete affected target sets. |
| so | https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/so-edit.obo; Release2026-08-07; SO0001079,1081,1114,1128,1133 | supports | Native terms support the two-helix motif and broader structural motif. Peptide_helix is not equivalent to a hairpin or motif umbrella. The beta-turn term permits an optional end-to-end hydrogen bond. |
| so-license | https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/LICENSE; License title and scope | supports | Sequence Ontology uses CC-BY-4.0; source attribution is retained for the three SO-derived motif definitions. |
| project-license | LICENSE; Project-authored data and third-party-material scope; LICENSE-DATA | supports | Project-authored factual syntheses are licensed CC-BY-4.0. Cited articles, matrices, figures and software retain their own terms; the reviewed records do not claim relicensing those sources. |
| promotif-paper | https://pubmed.ncbi.nlm.nih.gov/8745398/; DOI10.1002/pro.5560050204 and abstract | supports | The original coordinate-analysis program covers local turns, hairpins, beta-alpha-beta units and sheet topology. Full article not required for the independently inspected manual rules. |
| promotif | https://www.uoxray.uoregon.edu/local/manuals/promotif/document_2.html; Availability, setup, run and class-specific sections | supports | The manual supports paired parallel strands for BAB, antiparallel hairpins, compact nonhelical beta turns and sheet-topology output. The program requires authorized installation and setup. Greek-key classification requires additional reviewed connectivity interpretation. |
| greek | https://pubmed.ncbi.nlm.nih.gov/8506258/; DOI10.1093/protein/6.3.233; abstract | supports | The conventional four-strand connectivity includes several three-dimensional arrangements; the record does not collapse them into one geometry. |
| hairpin | https://pubmed.ncbi.nlm.nih.gov/33389765/; DOI10.1002/pro.4020; abstract | supports | The systematic hairpin analysis examines interstrand contacts and variable turn regions. Full-text page was inaccessible; explicit pairing criteria were independently confirmed in the author manual. |
| beta-beta | https://onlinelibrary.wiley.com/doi/10.1002/pro.4936; Section2.1 and Figure1 caption | supports | The source distinguishes paired-strand hairpins and unpaired-strand arches, using beta-beta-loop terminology for both. Therefore bare beta-beta cannot be an exact hairpin synonym. |
| emboss | https://emboss.bioinformatics.nl/cgi-bin/emboss/help/helixturnhelix; Description, qualifiers and Dodd-Egan references | supports | The documented sequence-scoring program reports putative HTH motifs. Its recipe is supported, but its hit is not structural or DNA-binding proof. |
| dssp | https://raw.githubusercontent.com/PDB-REDO/dssp/trunk/doc/mkdssp.md; Synopsis, legacy output option and state table | supports | The documented coordinate-assignment command supports DSSP output and state T. This is distinct from a complete named-motif classifier. |
| 1lmb | https://www.rcsb.org/structure/1LMB; Entry1.3, primary citation abstract, chains and experimental data | supports | PMID1387915/DOI10.1016/0022-2836(92)90690-l explicitly describes the HTH region. Entry1.3 has 1.8-A Xray structure and protein chains C/D (author3/4). No local motif bounds were verified. |
| method-ontology | research/structural-traits-20261028/method-ontology-check.json; Captured native EDAM/ECO terms and source hashes | supports | EDAM codes distinguish prediction, structural analysis and secondary-state assignment. Greek-key manual adjudication uses ECO0000305; automated computational outputs use ECO0007669. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; ProteinTraitRecord; SecondaryStructureRepresentation; StructuralGeometryRepresentation; license | supports | A whole-entry geometry anchor can coexist with unspecified local bounds; it is not a canonical-example qualification. ss_string represents DSSP T state notation. |
| parent-context | data/traits/structure/secondary/secondary-structure-element.yaml; Definition and xrefs; context only | context_only | Its per-residue assignment-state definition supports TURN parentage. Its existing broad/peptide-helix xrefs remain outside the eight-target closure and are not certified by this review. |
| alias-search | research/structural-traits-20261028/cavities/motif-post-alias-context.txt; Ignored-inclusive secondary-folder context search | context_only | The bounded scan retains the beta-beta ambiguity note and reveals other pre-existing sibling equivalence issues outside this eight-target review. |
| strict | research/structural-traits-20261028/cavities/motif-post-strict.txt; Actual native command output | supports | Eight selected records pass with zero errors. |
| graph | research/structural-traits-20261028/cavities/motif-post-graph.txt; Actual native command output | supports | No graphs present in these eight records; audit exits0 with no errors/warnings. |
| grounding | research/structural-traits-20261028/cavities/motif-post-grounding.txt; Actual native command output | supports | Eight selected records pass the legacy-compatible semantic check; this does not qualify protein occurrences. |

## Limits And Additional Notes

- Method execution and PROMOTIF authorization/setup remain outside this review; documentation support is not a successful executable detector benchmark.
- Some primary literature was inspected at abstract level, with explicit algorithm rules checked in author documentation. No inaccessible full text is claimed read.
- The PDB1LMB entry is a source-supported containing structure, with no motif residue range, local contact descriptor or release-pinned qualified UniProt occurrence.
- Other existing structural-secondary records retain suspect whole-enum/peptide-helix xrefs, including the immediate SECONDARY_STRUCTURE_ELEMENT parent. This scoped review does not certify the whole hierarchy.
- All records remain PROPOSED with llm_assisted history; this review does not confer human sign-off.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261028T185849Z-structural-motif-post-curation
kind: category
repository: CultureBotAI/proteintraitsmech
title: Independent post-curation scientific review of eight structural motifs
started_at: '2026-10-28T18:54:39Z'
finished_at: '2026-10-28T18:58:49Z'
reviewer:
  identity: Codex cavity_binding_evidence
  kind: agent
  independence: independent
  independence_basis: Did not author the original motif proposals or edit the ledger/records.
    Independently inspected sources and applied outputs; supplied pre-application
    review comments that root implemented.
skill: .claude/skills/review-yaml-category/SKILL.md
completion: completed
verdict: pass_with_limitations
scientific_review: true
summary: All eight applied records have positive source-backed scientific assessments.
  Six original findings are resolved with exact predecessor lineage; the minor method-coverage
  finding remains deferred. Schema, graph and grounding checks pass without implying
  software execution, human REVIEWED status or protein qualification.
source:
  git_revision: c4147394c698324ae537c0c63c2c9f6647c4f4fc
  state: working_tree
  inputs:
  - path: .claude/skills/curate-yaml-record/references/review-checklist.md
    sha256: 59f39fad3e6447e7be30da72667befd3d2e383b68bea5f497952f2ab080da90d
    role: context
  - path: LICENSE
    sha256: d920683ada4ab4646467cbe49944e08172d8f10c92ce3e631d6f3460b4b40a52
    role: context
  - path: LICENSE-DATA
    sha256: 9e5f1b3c610b9c2da5c313bf81d577a7d1acec686bdb0384edefa6df0f90cd94
    role: context
  - path: data/curation/structural_trait_curations.yaml
    sha256: 31716fb836efcf8971e19179970f0adafd7925bc6353cd44e4d5f763bd361fd4
    role: context
  - path: data/traits/structure/secondary/beta-alpha-beta.yaml
    sha256: a52a695dcb80e0dc019362ec15e57f136a4ba508162e4cb97d248e24b31a339f
    role: target
  - path: data/traits/structure/secondary/beta-hairpin.yaml
    sha256: 9d6c5788befde58602fe7675cc1206e05a79a6399b6be8669e4c8b593226f20a
    role: target
  - path: data/traits/structure/secondary/beta-turn.yaml
    sha256: 920094fe23b009d0b804fb6bd9e2a12f51b1b5b60c66dfd363b5beee7be81784
    role: target
  - path: data/traits/structure/secondary/greek-key.yaml
    sha256: 47526b5b5be1a72ebc3969df2f49131e7e564d19ab1396b2a1cbc811da031dd5
    role: target
  - path: data/traits/structure/secondary/helix-turn-helix.yaml
    sha256: ed98dc3aec98bbc020a1f913358719163a8c40590e6d87fd85414a0bf8941297
    role: target
  - path: data/traits/structure/secondary/polypeptide-structural-motif.yaml
    sha256: 4f2e3c1f9464fbd703efd2ab7a7e3f6f3de2021eb72d5550c1bcc836d003cd19
    role: target
  - path: data/traits/structure/secondary/secondary-structure-element.yaml
    sha256: 4a96cefafdcd3de0282b1424eab7f8faa679d55033d4f5d7ff212e126c2a7a64
    role: context
  - path: data/traits/structure/secondary/super-secondary-motif.yaml
    sha256: 6cd335a8aff68fa61c254d1b0f948b05aca163cedda30b6019df0af1f48a0cac
    role: target
  - path: data/traits/structure/secondary/turn.yaml
    sha256: 890629d4940b0c61a729525276ee6a0b38c12bf05e82d9ff0c12e0c62d93d648
    role: target
  - path: docs/record-review-profile.md
    sha256: 06cec6693ded193231a378bba04e7c1ad3e295f88903ee8b7c30b3238daab9df
    role: context
  - path: docs/record-reviews.md
    sha256: 452a19ab688276747b7c4308523a14d4d99c1c39ef6909ae8a90b85b7a9b3e9b
    role: context
  - path: research/structural-traits-20261028/cavities/motif-independent-review.json
    sha256: 7b64016dd41e56ce7523cce3fac19c965d347ea503c6b21d85a29575186f5028
    role: context
  - path: research/structural-traits-20261028/cavities/motif-post-ledger-reassessment.json
    sha256: 83221dacd8c3b182d1cdda700d7ddd4d5256dbd8f6656ad0a2da9e74a05e59dd
    role: context
  - path: research/structural-traits-20261028/method-ontology-check.json
    sha256: 4161354a17456dd2168314f12bc04be87a3a3688972dd0888271682d893ca608
    role: context
  - path: research/structural-traits-20261028/motifs/evidence-dossier.json
    sha256: 2365b337930122508817dd59747ca2149d1627660c66809f39899a48bd3f2fdb
    role: context
  - path: reviews/structured/20261028T184459Z-structural-motif-initial-audit/review.yaml
    sha256: c4d902739aefe65feaf543012b104a541882677974419496b22e85042fc9ee11
    role: context
  - path: scripts/curate_structural_traits.py
    sha256: 60fe9bf32d9d4f3801fba1342dc3bb5aa7e0e85c05f496dac710d75524204ddc
    role: context
  - path: scripts/enrich_secondary_structural_defs.py
    sha256: 1fadb6fe3541597507f592cf82e403bebf064772dba081648a001dacf542bc54
    role: context
  - path: scripts/seed_localstructuralfeature.py
    sha256: 50969e6bdafaaf2eb57ada680868a8ef5417951654c2157f28122c60bfda9036
    role: context
  - path: scripts/seed_secondary_structure.py
    sha256: 21f0ad5a35c97ce6f448887a166e5afb31dc0f22bce777b0f318456875ea5064
    role: context
  - path: scripts/structural_trait_curations.py
    sha256: 72226af447168758724b895c89d38d901ca7a20c4afe80229ee21b4d555989fc
    role: context
  - path: src/proteintraitsmech/schema/mech_shared.yaml
    sha256: c2e7054fd32635e380c698282bd886a9105861009b9f0474f02bb1b80865e895
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Exactly the eight motif/parent targets in the original scientific review;
    current applied working-tree bytes.
  selection: Complete original target set, not a sample; all predecessor finding target
    memberships retained.
  coverage: full
  population_size: 8
  reviewed_target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  exclusions:
  - target: Other structural-secondary siblings including SECONDARY_STRUCTURE_ELEMENT
    reason: Immediate parent definition and alias context read only; its remaining
      xref issues and other sibling records are outside this eight-target disposition.
  - target: Canonical protein occurrence qualification and structural method execution
    reason: No occurrence promotion or execution evidence was produced; representation
      anchors and documented recipes are assessed at their declared scope.
targets:
- target_id: proteintraitsmech:HELIX_TURN_HELIX
  path: data/traits/structure/secondary/helix-turn-helix.yaml
  label: helix-turn-helix
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
- target_id: proteintraitsmech:BETA_ALPHA_BETA
  path: data/traits/structure/secondary/beta-alpha-beta.yaml
  label: beta-alpha-beta motif
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
- target_id: proteintraitsmech:GREEK_KEY
  path: data/traits/structure/secondary/greek-key.yaml
  label: Greek key motif
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
- target_id: proteintraitsmech:BETA_HAIRPIN
  path: data/traits/structure/secondary/beta-hairpin.yaml
  label: beta hairpin
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
- target_id: proteintraitsmech:BETA_TURN
  path: data/traits/structure/secondary/beta-turn.yaml
  label: beta turn
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
- target_id: proteintraitsmech:SUPER_SECONDARY_MOTIF
  path: data/traits/structure/secondary/super-secondary-motif.yaml
  label: super secondary motif
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
- target_id: proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  path: data/traits/structure/secondary/polypeptide-structural-motif.yaml
  label: polypeptide structural motif
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
- target_id: proteintraitsmech:TURN
  path: data/traits/structure/secondary/turn.yaml
  label: turn
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
checks:
- check_id: strict
  name: Strict LinkML validation
  status: passed
  required: true
  summary: Eight selected records pass with zero errors.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  command: .venv/bin/python scripts/validate_strict.py --workers 1 --out research/structural-traits-20261028/cavities/motif-post-strict-errors.tsv
    data/traits/structure/secondary/helix-turn-helix.yaml data/traits/structure/secondary/beta-alpha-beta.yaml
    data/traits/structure/secondary/greek-key.yaml data/traits/structure/secondary/beta-hairpin.yaml
    data/traits/structure/secondary/beta-turn.yaml data/traits/structure/secondary/super-secondary-motif.yaml
    data/traits/structure/secondary/polypeptide-structural-motif.yaml data/traits/structure/secondary/turn.yaml
  exit_code: 0
  evidence_ids:
  - strict
- check_id: graph
  name: Causal graph structural audit
  status: passed
  required: true
  summary: No graphs present in these eight records; audit exits0 with no errors/warnings.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  command: .venv/bin/python scripts/audit_causal_graphs.py data/traits/structure/secondary/helix-turn-helix.yaml
    data/traits/structure/secondary/beta-alpha-beta.yaml data/traits/structure/secondary/greek-key.yaml
    data/traits/structure/secondary/beta-hairpin.yaml data/traits/structure/secondary/beta-turn.yaml
    data/traits/structure/secondary/super-secondary-motif.yaml data/traits/structure/secondary/polypeptide-structural-motif.yaml
    data/traits/structure/secondary/turn.yaml
  exit_code: 0
  evidence_ids:
  - graph
- check_id: grounding
  name: Native UniProt grounding semantic validation
  status: passed
  required: true
  summary: Eight selected records pass the legacy-compatible semantic check; this
    does not qualify protein occurrences.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  command: .venv/bin/python scripts/validate_uniprot_grounding.py --out research/structural-traits-20261028/cavities/motif-post-grounding-errors.tsv
    data/traits/structure/secondary/helix-turn-helix.yaml data/traits/structure/secondary/beta-alpha-beta.yaml
    data/traits/structure/secondary/greek-key.yaml data/traits/structure/secondary/beta-hairpin.yaml
    data/traits/structure/secondary/beta-turn.yaml data/traits/structure/secondary/super-secondary-motif.yaml
    data/traits/structure/secondary/polypeptide-structural-motif.yaml data/traits/structure/secondary/turn.yaml
  exit_code: 0
  evidence_ids:
  - grounding
- check_id: applied-ledger
  name: Exact applied ledger and native-status consistency
  status: passed
  required: true
  summary: All eight target SHA256 values equal their maintained ledger output_sha256;
    records remain PROPOSED with honest agent history and no canonical example promotion.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  evidence_ids:
  - applied
  - owner
- check_id: science
  name: Independent scientific scope and source comparison
  status: passed
  required: true
  summary: Inspected source-native terms/manuals and primary abstracts/full source
    sections support the bounded definitions, relations, notation and scoped representation;
    completed scientific judgement is not inferred from syntax checks.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  evidence_ids:
  - so
  - promotif
  - greek
  - hairpin
  - beta-beta
  - emboss
  - dssp
  - 1lmb
- check_id: software-execution
  name: Execution of documented structural/sequence detectors
  status: skipped
  required: false
  summary: Recipes are documentation checked only. PROMOTIF authorized-installation
    prerequisite, HTH screening limits and manual Greek-key classification remain
    explicit.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  evidence_ids:
  - promotif
  - emboss
  - dssp
evidence:
- evidence_id: applied
  kind: record_content
  reference: research/structural-traits-20261028/cavities/motif-post-inspection.json
  locator: Native source hashes; complete eight applied target records
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: All eight records were read after root signaled applied outputs. Reviewed
    fields include definitions, hierarchy, equivalence, representations, evidence,
    licenses, methods and agent history.
- evidence_id: owner
  kind: record_content
  reference: data/curation/structural_trait_curations.yaml
  locator: Eight selected motif entries and shared guarded transforms
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: Maintained ledger binds exact input/output hashes and seeder preimages.
    Applied target hashes match the selected ledger outputs; history remains PROPOSED
    and agent-attributed.
- evidence_id: prior
  kind: prior_review
  reference: reviews/structured/20261028T184459Z-structural-motif-initial-audit/review.yaml
  locator: Seven original finding identities and target sets
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: This successor explicitly carries all seven issue keys and their complete
    affected target sets.
- evidence_id: so
  kind: authority
  reference: https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/so-edit.obo
  locator: Release2026-08-07; SO0001079,1081,1114,1128,1133
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: Native terms support the two-helix motif and broader structural motif.
    Peptide_helix is not equivalent to a hairpin or motif umbrella. The beta-turn
    term permits an optional end-to-end hydrogen bond.
- evidence_id: so-license
  kind: authority
  reference: https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/LICENSE
  locator: License title and scope
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: Sequence Ontology uses CC-BY-4.0; source attribution is retained for the
    three SO-derived motif definitions.
- evidence_id: project-license
  kind: authority
  reference: LICENSE
  locator: Project-authored data and third-party-material scope; LICENSE-DATA
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: Project-authored factual syntheses are licensed CC-BY-4.0. Cited articles,
    matrices, figures and software retain their own terms; the reviewed records do
    not claim relicensing those sources.
- evidence_id: promotif-paper
  kind: primary_source
  reference: https://pubmed.ncbi.nlm.nih.gov/8745398/
  locator: DOI10.1002/pro.5560050204 and abstract
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: The original coordinate-analysis program covers local turns, hairpins,
    beta-alpha-beta units and sheet topology. Full article not required for the independently
    inspected manual rules.
- evidence_id: promotif
  kind: authority
  reference: https://www.uoxray.uoregon.edu/local/manuals/promotif/document_2.html
  locator: Availability, setup, run and class-specific sections
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: The manual supports paired parallel strands for BAB, antiparallel hairpins,
    compact nonhelical beta turns and sheet-topology output. The program requires
    authorized installation and setup. Greek-key classification requires additional
    reviewed connectivity interpretation.
- evidence_id: greek
  kind: primary_source
  reference: https://pubmed.ncbi.nlm.nih.gov/8506258/
  locator: DOI10.1093/protein/6.3.233; abstract
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: The conventional four-strand connectivity includes several three-dimensional
    arrangements; the record does not collapse them into one geometry.
- evidence_id: hairpin
  kind: primary_source
  reference: https://pubmed.ncbi.nlm.nih.gov/33389765/
  locator: DOI10.1002/pro.4020; abstract
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: The systematic hairpin analysis examines interstrand contacts and variable
    turn regions. Full-text page was inaccessible; explicit pairing criteria were
    independently confirmed in the author manual.
- evidence_id: beta-beta
  kind: primary_source
  reference: https://onlinelibrary.wiley.com/doi/10.1002/pro.4936
  locator: Section2.1 and Figure1 caption
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: The source distinguishes paired-strand hairpins and unpaired-strand arches,
    using beta-beta-loop terminology for both. Therefore bare beta-beta cannot be
    an exact hairpin synonym.
- evidence_id: emboss
  kind: authority
  reference: https://emboss.bioinformatics.nl/cgi-bin/emboss/help/helixturnhelix
  locator: Description, qualifiers and Dodd-Egan references
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: The documented sequence-scoring program reports putative HTH motifs. Its
    recipe is supported, but its hit is not structural or DNA-binding proof.
- evidence_id: dssp
  kind: authority
  reference: https://raw.githubusercontent.com/PDB-REDO/dssp/trunk/doc/mkdssp.md
  locator: Synopsis, legacy output option and state table
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: The documented coordinate-assignment command supports DSSP output and state
    T. This is distinct from a complete named-motif classifier.
- evidence_id: 1lmb
  kind: database
  reference: https://www.rcsb.org/structure/1LMB
  locator: Entry1.3, primary citation abstract, chains and experimental data
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: PMID1387915/DOI10.1016/0022-2836(92)90690-l explicitly describes the HTH
    region. Entry1.3 has 1.8-A Xray structure and protein chains C/D (author3/4).
    No local motif bounds were verified.
- evidence_id: method-ontology
  kind: authority
  reference: research/structural-traits-20261028/method-ontology-check.json
  locator: Captured native EDAM/ECO terms and source hashes
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: EDAM codes distinguish prediction, structural analysis and secondary-state
    assignment. Greek-key manual adjudication uses ECO0000305; automated computational
    outputs use ECO0007669.
- evidence_id: schema
  kind: authority
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  locator: ProteinTraitRecord; SecondaryStructureRepresentation; StructuralGeometryRepresentation;
    license
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: A whole-entry geometry anchor can coexist with unspecified local bounds;
    it is not a canonical-example qualification. ss_string represents DSSP T state
    notation.
- evidence_id: parent-context
  kind: record_content
  reference: data/traits/structure/secondary/secondary-structure-element.yaml
  locator: Definition and xrefs; context only
  accessed_at: '2026-10-28T18:58:49Z'
  support: context_only
  summary: Its per-residue assignment-state definition supports TURN parentage. Its
    existing broad/peptide-helix xrefs remain outside the eight-target closure and
    are not certified by this review.
- evidence_id: alias-search
  kind: search
  reference: research/structural-traits-20261028/cavities/motif-post-alias-context.txt
  locator: Ignored-inclusive secondary-folder context search
  accessed_at: '2026-10-28T18:58:49Z'
  support: context_only
  summary: The bounded scan retains the beta-beta ambiguity note and reveals other
    pre-existing sibling equivalence issues outside this eight-target review.
  search_scope: rg --no-ignore --hidden --glob *.yaml over data/traits/structure/secondary
    for beta-beta/beta-arch aliases and the two suspect xrefs. No corpus-wide absence
    claim.
- evidence_id: strict
  kind: validation
  reference: research/structural-traits-20261028/cavities/motif-post-strict.txt
  locator: Actual native command output
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: Eight selected records pass with zero errors.
- evidence_id: graph
  kind: validation
  reference: research/structural-traits-20261028/cavities/motif-post-graph.txt
  locator: Actual native command output
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: No graphs present in these eight records; audit exits0 with no errors/warnings.
- evidence_id: grounding
  kind: validation
  reference: research/structural-traits-20261028/cavities/motif-post-grounding.txt
  locator: Actual native command output
  accessed_at: '2026-10-28T18:58:49Z'
  support: supports
  summary: Eight selected records pass the legacy-compatible semantic check; this
    does not qualify protein occurrences.
assessments:
- assessment_id: target-0
  area: identity
  topic: Class identity, evidence, hierarchy, representation and detection scope
  outcome: supported
  summary: Retained two-helix class with proper motif parent and SO mapping. Sequence-screen
    limitations are explicit; PDB1LMB is a supported containing structure with chain/version
    information and no invented motif bounds.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  evidence_ids:
  - applied
  - so
  - emboss
  - 1lmb
- assessment_id: target-1
  area: identity
  topic: Class identity, evidence, hierarchy, representation and detection scope
  outcome: supported
  summary: Parallel paired strands and intervening alpha helix are explicit. E-H-E
    is contextualized by those geometric criteria; Rossmann membership is not asserted
    as class identity.
  target_ids:
  - proteintraitsmech:BETA_ALPHA_BETA
  evidence_ids:
  - applied
  - promotif
  - promotif-paper
  - schema
- assessment_id: target-2
  area: identity
  topic: Class identity, evidence, hierarchy, representation and detection scope
  outcome: supported
  summary: Connectivity is specified without requiring one shape. PROMOTIF supplies
    topology data; curator inference is explicit and appropriately labelled rather
    than presented as an automatic Greek-key call.
  target_ids:
  - proteintraitsmech:GREEK_KEY
  evidence_ids:
  - applied
  - greek
  - promotif
  - method-ontology
- assessment_id: target-3
  area: identity
  topic: Class identity, evidence, hierarchy, representation and detection scope
  outcome: supported
  summary: Sequence-adjacent antiparallel paired strands and a variable connector
    define the class. Wrong xrefs are removed; bare beta-beta is not equated with
    hairpin.
  target_ids:
  - proteintraitsmech:BETA_HAIRPIN
  evidence_ids:
  - applied
  - hairpin
  - promotif
  - beta-beta
- assessment_id: target-4
  area: identity
  topic: Class identity, evidence, hierarchy, representation and detection scope
  outcome: supported
  summary: The compact four-residue convention is operationally specified, with nonhelical
    central residues and optional end-to-end hydrogen bond. It is correctly placed
    under the broad motif class rather than DSSP T.
  target_ids:
  - proteintraitsmech:BETA_TURN
  evidence_ids:
  - applied
  - so
  - promotif
  - dssp
- assessment_id: target-5
  area: identity
  topic: Class identity, evidence, hierarchy, representation and detection scope
  outcome: supported
  summary: The umbrella describes spatially connected recurring secondary elements
    and inherits the broader motif class. False helix equivalence and a universal
    matcher claim are absent.
  target_ids:
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  evidence_ids:
  - applied
  - promotif-paper
  - promotif
  - so
- assessment_id: target-6
  area: identity
  topic: Class identity, evidence, hierarchy, representation and detection scope
  outcome: supported
  summary: The class correctly says independent globular stability is unnecessary,
    retaining SO identity and attribution without treating the whole source enum as
    equivalent.
  target_ids:
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  evidence_ids:
  - applied
  - so
  - so-license
  - project-license
- assessment_id: target-7
  area: identity
  topic: Class identity, evidence, hierarchy, representation and detection scope
  outcome: supported
  summary: The class preserves the algorithm-defined DSSP T state, uses ss_string
    T and the appropriate elementary-state parent. It no longer acts as the universal
    beta-turn superclass.
  target_ids:
  - proteintraitsmech:TURN
  evidence_ids:
  - applied
  - dssp
  - schema
  - parent-context
- assessment_id: rights
  area: provenance
  topic: Source-specific rights disposition
  outcome: supported
  summary: All eight state an explicit reviewed rights basis; three retain SO attribution
    and five license only new project-authored factual synthesis. Cited sources/software
    remain separate, and no copied matrices, figures or code are introduced.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  evidence_ids:
  - applied
  - owner
  - project-license
  - so-license
- assessment_id: method-limits
  area: completeness
  topic: Remaining class-specific detector qualification
  outcome: concern
  summary: Documented recipes have not been executed. HTH remains a sequence screen,
    Greek-key requires manual connectivity review, and the two umbrella classes have
    no universal verified classifier.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  evidence_ids:
  - applied
  - promotif
  - emboss
  - dssp
findings:
- finding_id: wrong-equivalence
  issue_key: proteintraitsmech-structural-motifs-wrong-equivalence
  category: grounding
  severity: major
  status: resolved
  certainty: confirmed
  title: Peptide-helix and whole-enumeration xrefs assert false motif equivalence
  description: Removed the peptide-helix and whole-vocabulary equivalences from every
    original affected target; SO0001079 retained for the broad motif.
  target_ids:
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  field_paths:
  - xrefs
  evidence_ids:
  - applied
  - so
  - prior
  rule_id: .claude/skills/curate-yaml-record/references/review-checklist.md#Hierarchy-equivalence
  native_severity: major
  normalization_reason: Material scientific grounding, scope or source-support defect
    within the selected records.
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261028T184459Z-structural-motif-initial-audit
    finding_id: wrong-equivalence
  disposition_reason: Removed the peptide-helix and whole-vocabulary equivalences
    from every original affected target; SO0001079 retained for the broad motif.
- finding_id: definition-support
  issue_key: proteintraitsmech-structural-motifs-definition-support
  category: evidence
  severity: major
  status: resolved
  certainty: confirmed
  title: Named motif definitions and topology claims need class-specific evidence
  description: Each originally affected definition now has class-specific authority
    or primary-source support; unsupported universal DNA-binding/Rossmann/superlative
    claims are removed.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_TURN
  field_paths:
  - definition
  - definition_source
  - secondary_structure_representations.evidence_source
  evidence_ids:
  - applied
  - so
  - promotif
  - greek
  - emboss
  - prior
  rule_id: .claude/skills/curate-yaml-record/references/review-checklist.md#Definition
  native_severity: major
  normalization_reason: Material scientific grounding, scope or source-support defect
    within the selected records.
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261028T184459Z-structural-motif-initial-audit
    finding_id: definition-support
  disposition_reason: Each originally affected definition now has class-specific authority
    or primary-source support; unsupported universal DNA-binding/Rossmann/superlative
    claims are removed.
- finding_id: beta-turn-parent
  issue_key: proteintraitsmech-structural-motifs-beta-turn-parent
  category: consistency
  severity: major
  status: resolved
  certainty: confirmed
  title: Broad beta-turn class is placed beneath a narrower DSSP T state
  description: The broad geometric beta turn now inherits POLYPEPTIDE_STRUCTURAL_MOTIF;
    TURN retains its DSSP-state identity and parent.
  target_ids:
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:TURN
  field_paths:
  - parent_traits
  - definition
  - secondary_structure_representations
  evidence_ids:
  - applied
  - so
  - promotif
  - dssp
  - prior
  rule_id: .claude/skills/curate-yaml-record/references/review-checklist.md#Hierarchy-equivalence
  native_severity: major
  normalization_reason: Material scientific grounding, scope or source-support defect
    within the selected records.
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261028T184459Z-structural-motif-initial-audit
    finding_id: beta-turn-parent
  disposition_reason: The broad geometric beta turn now inherits POLYPEPTIDE_STRUCTURAL_MOTIF;
    TURN retains its DSSP-state identity and parent.
- finding_id: motif-stability
  issue_key: proteintraitsmech-structural-motifs-motif-stability
  category: identity
  severity: major
  status: resolved
  certainty: confirmed
  title: Polypeptide structural motif incorrectly excludes independently stable units
  description: Independent stability is now unnecessary rather than prohibited; SUPER_SECONDARY_MOTIF
    inherits the broader structural motif.
  target_ids:
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  field_paths:
  - definition
  - definition_source
  - parent_traits
  evidence_ids:
  - applied
  - so
  - prior
  rule_id: .claude/skills/curate-yaml-record/references/review-checklist.md#Identity
  native_severity: major
  normalization_reason: Material scientific grounding, scope or source-support defect
    within the selected records.
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261028T184459Z-structural-motif-initial-audit
    finding_id: motif-stability
  disposition_reason: Independent stability is now unnecessary rather than prohibited;
    SUPER_SECONDARY_MOTIF inherits the broader structural motif.
- finding_id: topology-layer
  issue_key: proteintraitsmech-structural-motifs-topology-layer
  category: representation
  severity: minor
  status: resolved
  certainty: confirmed
  title: Topology tokens omit distinguishing geometric criteria
  description: 'Geometric criteria supplement the retained tokens: BAB pairing/orientation,
    Greek connectivity, hairpin connector scope and beta-turn operational criteria.
    HTH and TURN states are explicitly sourced.'
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  field_paths:
  - definitions
  - secondary_structure_representations
  evidence_ids:
  - applied
  - promotif
  - greek
  - so
  - dssp
  - prior
  rule_id: .claude/skills/curate-yaml-record/references/review-checklist.md#Representations
  native_severity: minor
  normalization_reason: Bounded completeness or provenance defect; optional fields
    are not made universally mandatory.
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261028T184459Z-structural-motif-initial-audit
    finding_id: topology-layer
  disposition_reason: 'Geometric criteria supplement the retained tokens: BAB pairing/orientation,
    Greek connectivity, hairpin connector scope and beta-turn operational criteria.
    HTH and TURN states are explicitly sourced.'
- finding_id: method-coverage
  issue_key: proteintraitsmech-structural-motifs-method-coverage
  category: completeness
  severity: minor
  status: deferred
  certainty: confirmed
  title: Category DSSP fallback is not a complete motif classifier
  description: 'Class-specific documented methods and limits now replace the undifferentiated
    fallback. Remaining qualification is deferred: PROMOTIF authorization/setup and
    execution were not performed, HTH is a sequence screen, Greek-key requires curator
    connectivity review, and broad motif umbrellas have no single verified classifier.'
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  field_paths:
  - detection_methods
  evidence_ids:
  - applied
  - promotif
  - emboss
  - dssp
  - method-ontology
  rule_id: .claude/skills/curate-yaml-record/references/review-checklist.md#Representations
  native_severity: minor
  normalization_reason: Bounded completeness or provenance defect; optional fields
    are not made universally mandatory.
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261028T184459Z-structural-motif-initial-audit
    finding_id: method-coverage
  disposition_reason: The scientific scope defect is repaired, but the original method-coverage
    issue is not closed because executable qualification and universal coverage remain
    unestablished.
- finding_id: rights-provenance
  issue_key: proteintraitsmech-structural-motifs-rights-provenance
  category: provenance
  severity: major
  status: resolved
  certainty: confirmed
  title: Source and license disposition is unresolved for selected records
  description: The maintained source-specific dispositions and record evidence now
    distinguish SO-derived content, project-authored synthesis, cited article rights
    and conditional software access.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  field_paths:
  - definition_source
  - definitions
  - license
  - evidence
  evidence_ids:
  - applied
  - owner
  - project-license
  - so-license
  - prior
  rule_id: .claude/skills/curate-yaml-record/references/review-checklist.md#Identity
  native_severity: major
  normalization_reason: Material scientific grounding, scope or source-support defect
    within the selected records.
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  previous_occurrences:
  - repository: CultureBotAI/proteintraitsmech
    review_id: 20261028T184459Z-structural-motif-initial-audit
    finding_id: rights-provenance
  disposition_reason: The maintained source-specific dispositions and record evidence
    now distinguish SO-derived content, project-authored synthesis, cited article
    rights and conditional software access.
actions:
- action_id: future-method-qualification
  description: When separately authorized and supplied with software prerequisites,
    qualify selected detector outputs against reviewed structures and explicit subtype
    criteria. Keep predictions, manual classification and demonstrated geometry distinct;
    no universal umbrella matcher is assumed.
  finding_ids:
  - method-coverage
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: data/curation/structural_trait_curations.yaml
    role: maintained bounded curation ledger
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/structural_trait_curations.py
    role: shared ledger transform
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/curate_structural_traits.py
    role: guarded curation writer
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  acceptance_checks:
  - Record licensed/software-versioned execution and actual outputs for the selected
    method.
  - Document the topology/geometry decision rule and appropriate positive and negative
    examples.
  - Do not qualify canonical UniProt occurrences without the native grounding workflow.
boundary_decisions:
- action: retain
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  rationale: Named motifs, broad structural-motif umbrellas and the DSSP assignment
    state have distinct identities. The beta-beta wording spans hairpin and arch contexts,
    so no exact synonym/merge is introduced.
  evidence_ids:
  - so
  - promotif
  - greek
  - beta-beta
limitations:
- Method execution and PROMOTIF authorization/setup remain outside this review; documentation
  support is not a successful executable detector benchmark.
- Some primary literature was inspected at abstract level, with explicit algorithm
  rules checked in author documentation. No inaccessible full text is claimed read.
- The PDB1LMB entry is a source-supported containing structure, with no motif residue
  range, local contact descriptor or release-pinned qualified UniProt occurrence.
- Other existing structural-secondary records retain suspect whole-enum/peptide-helix
  xrefs, including the immediate SECONDARY_STRUCTURE_ELEMENT parent. This scoped review
  does not certify the whole hierarchy.
- All records remain PROPOSED with llm_assisted history; this review does not confer
  human sign-off.
related_reviews:
- repository: CultureBotAI/proteintraitsmech
  review_id: 20261028T184459Z-structural-motif-initial-audit
  relationship: supersedes findings through explicit previous_occurrences and exact
    affected-target retention
links:
- research/structural-traits-20261028/cavities/motif-independent-review.json
- https://github.com/CultureBotAI/proteintraitsmech/issues/1200
tags:
- structure
- motif
- post-curation
- independent
```
