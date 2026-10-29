# Initial audit of eight bounded structural motif and immediate-parent records

- Review: 20261028T184459Z-structural-motif-initial-audit
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-28T18:34:27Z
- Finished UTC: 2026-10-28T18:44:59Z
- Reviewer: codex-gpt-6-astra (independent)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

Bounded scientific audit of eight original motif/parent records found five major and two minor issues despite successful deterministic validation. Correct false equivalence, unsupported provenance and hierarchy, refine definitions, and expose method/rights limits. Concrete recommendations are retained in the evidence dossier; no scientific records were edited by this review.

## Scope And Provenance

Five named local/supersecondary motifs and three directly affected existing parents; full coverage of this explicit eight-record selection only.

Selection: Named HTH, BAB, Greek key, beta hairpin and beta turn plus SUPER_SECONDARY_MOTIF, POLYPEPTIDE_STRUCTURAL_MOTIF and TURN, selected because their definitions or direct hierarchy affect the named motifs.
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
| Strict LinkML validation | passed | True | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF | Exit 0; zero error rows. |
| UniProt grounding semantic validation | passed | True | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF | Exit 0; zero semantic findings. These targets have no canonical examples, so this is not protein-example qualification. |
| Strict LinkML validation | passed | True | proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | Exit 0; zero error rows. |
| UniProt grounding semantic validation | passed | True | proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | Exit 0; zero semantic findings. These targets have no canonical examples, so this is not protein-example qualification. |
| Native content checklist and inspected-source comparison | passed | True | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | Read complete targets, captured owners, inspected primary literature or source-native authorities, compared identity, hierarchy, source support, representations, licensing, and method coverage. Completed audit found scientific defects; passed means the check was performed. |
| Ignored-inclusive alias search and cohort boundary adjudication | passed | True | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | Preserved class-versus-domain boundaries. No bare beta-beta equivalence or beta-arch record creation supported. |
| Causal-edge and protein-occurrence qualification | not_applicable | False | proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN | No causal graph or protein exemplar is present in these captured records; no promotion or occurrence claim was reviewed. |

## Scientific And Domain Assessments

### Class identity, source support, hierarchy and applicable representation

identity: concern. Targets: proteintraitsmech:HELIX_TURN_HELIX.

Keep DNA-binding examples and predictions separate from the geometrical class. No generic geometry-complete HTH classifier was verified.

Proposed definition: A recurring structural motif comprising two alpha helices linked by a short turn. Proposed direct parents: proteintraitsmech:SUPER_SECONDARY_MOTIF. Exact proposed fields and method/rights limitations are in the evidence dossier. These are proposals, not applied edits.

### Class identity, source support, hierarchy and applicable representation

identity: concern. Targets: proteintraitsmech:BETA_ALPHA_BETA.

Read .bab output. E-H-E alone omits strand pairing/orientation. Remove Rossmann parenthesis from defining criterion; it is contextual, not class identity.

Proposed definition: A supersecondary motif with two parallel, hydrogen-bonded beta strands connected in sequence through an intervening alpha helix. Proposed direct parents: proteintraitsmech:SUPER_SECONDARY_MOTIF. Exact proposed fields and method/rights limitations are in the evidence dossier. These are proposals, not applied edits.

### Class identity, source support, hierarchy and applicable representation

identity: concern. Targets: proteintraitsmech:GREEK_KEY.

Keep canonical token for compatibility; put connectivity in the STRUCTURAL definition. PROMOTIF .sht is an input for reviewed connectivity classification, not a verified automatic Greek-key call.

Proposed definition: A four-strand beta-structural motif with Greek-key connectivity, conventionally described by the topology +3,-1,-1. Proposed direct parents: proteintraitsmech:SUPER_SECONDARY_MOTIF. Exact proposed fields and method/rights limitations are in the evidence dossier. These are proposals, not applied edits.

### Class identity, source support, hierarchy and applicable representation

identity: concern. Targets: proteintraitsmech:BETA_HAIRPIN.

Read .hpin output. In the existing token, turn denotes a connector, not a necessary four-residue beta turn; keep this explicit. Do not add bare beta-beta as exact synonym.

Proposed definition: A structural motif formed by two sequence-adjacent beta strands that pair antiparallel and are joined by a connecting loop. Proposed direct parents: proteintraitsmech:SUPER_SECONDARY_MOTIF. Exact proposed fields and method/rights limitations are in the evidence dossier. These are proposals, not applied edits.

### Class identity, source support, hierarchy and applicable representation

identity: concern. Targets: proteintraitsmech:BETA_TURN.

Read .bturns output. Move from DSSP-specific TURN to existing broader motif parent. Remove unsupported commonest-turn superlative. It need not join beta strands.

Proposed definition: A local four-residue backbone motif classified by the conformation of its two central residues; an i-to-i+3 backbone hydrogen bond may be present. Proposed direct parents: proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF. Exact proposed fields and method/rights limitations are in the evidence dossier. These are proposals, not applied edits.

### Class identity, source support, hierarchy and applicable representation

identity: concern. Targets: proteintraitsmech:SUPER_SECONDARY_MOTIF.

Curator synthesis of inspected motif classes, not a quotation. Do not assert a universal fixed size or independent-folding rule. Classification requires a specified subtype rule; umbrella has no single topology matcher.

Proposed definition: A recurring arrangement of a small number of secondary-structure elements defined by their spatial relationships and connectivity. Proposed direct parents: proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF. Exact proposed fields and method/rights limitations are in the evidence dossier. These are proposals, not applied edits.

### Class identity, source support, hierarchy and applicable representation

identity: concern. Targets: proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF.

Repair does-not-form to need-not-form. Remove whole-enum and peptide-helix equivalence xrefs; retain source attribution separately.

Proposed definition: A recurring three-dimensional structural element within a polypeptide chain that need not form an independently stable globular unit. Proposed direct parents: none. Exact proposed fields and method/rights limitations are in the evidence dossier. These are proposals, not applied edits.

### Class identity, source support, hierarchy and applicable representation

identity: concern. Targets: proteintraitsmech:TURN.

Preserve the original DSSP-state identity. This class is not the universal parent of geometrically defined beta turns; source SO:0001128 has the same hydrogen-bond tension and should not be inserted as an exact equivalent.

Proposed definition: A backbone region assigned the hydrogen-bonded turn state T by the DSSP secondary-structure algorithm. Proposed direct parents: proteintraitsmech:SECONDARY_STRUCTURE_ELEMENT. Exact proposed fields and method/rights limitations are in the evidence dossier. These are proposals, not applied edits.

## Findings

### wrong-equivalence: Peptide-helix and whole-enumeration xrefs assert false motif equivalence

major / open / confirmed; issue key: proteintraitsmech-structural-motifs-wrong-equivalence.

SO:0001114 names peptide_helix. The whole LocalStructuralFeature enumeration is not equivalent to any individual motif. Remove these exact xrefs from the three selected records, retain source provenance separately, and preserve SO:0001079 for the broad polypeptide-motif class.

### definition-support: Named motif definitions and topology claims need class-specific evidence

major / open / confirmed; issue key: proteintraitsmech-structural-motifs-definition-support.

The generic DSSP citation does not establish the displayed HTH, BAB or Greek-key topology or the broad four-residue beta-turn class in this audit. Source-specific literature and ontology records support replacement definitions. Remove unsupported superlatives and avoid treating DNA-binding or Rossmann context as defining all instances.

### beta-turn-parent: Broad beta-turn class is placed beneath a narrower DSSP T state

major / open / confirmed; issue key: proteintraitsmech-structural-motifs-beta-turn-parent.

BETA_TURN allows absence of the i-to-i+3 hydrogen bond while TURN is explicitly the hydrogen-bonded DSSP T state. Move BETA_TURN beneath the existing broader POLYPEPTIDE_STRUCTURAL_MOTIF class and preserve TURN state identity. Blindly adopting SO:0001128 would retain an upstream hydrogen-bond inconsistency.

### motif-stability: Polypeptide structural motif incorrectly excludes independently stable units

major / open / confirmed; issue key: proteintraitsmech-structural-motifs-motif-stability.

The local does-not-form statement is stronger than SO:0001079, which makes independent stability unnecessary rather than prohibited. Repair the modal distinction; connect SUPER_SECONDARY_MOTIF below this broad existing class without imposing a universal domain-size or folding prohibition.

### topology-layer: Topology tokens omit distinguishing geometric criteria

minor / open / confirmed; issue key: proteintraitsmech-structural-motifs-topology-layer.

The generated structural definitions largely restate tokens. State BAB strand parallelism/pairing, Greek-key connectivity and hairpin antiparallel pairing in prose, and distinguish a generic hairpin connector from a four-residue beta turn. Retain canonical tokens only with explicit interpretation.

### method-coverage: Category DSSP fallback is not a complete motif classifier

minor / open / confirmed; issue key: proteintraitsmech-structural-motifs-method-coverage.

The records have no class-specific detection recipes. DSSP assigns residue states; InterPro/family matches are not geometrical proof. PROMOTIF documents BAB/hairpin/turn classification but has an unfulfilled license prerequisite. EMBOSS HTH is a sequence prediction. Greek-key and broad motif classes still require explicit reviewed topology rules; do not advertise complete executable coverage.

### rights-provenance: Source and license disposition is unresolved for selected records

major / open / confirmed; issue key: proteintraitsmech-structural-motifs-rights-provenance.

The captured records do not state source-license disposition. Reconcile source-specific attribution and the rights basis for synthesized definitions before release, distinguishing SO CC-BY-4.0 and valuesets Apache-2.0 from paper rights and conditional PROMOTIF software access. A tool license or cited PMID is not a record-wide content license.

## Recommended Actions And Acceptance Checks

### curate-owned-motifs

Apply source-grounded per-record proposals through maintained seeder/enrichment owners or a shared bounded overlay. Preserve all identities; record PROPOSED and accurate agent history only. Keep license/method gaps explicit; do not qualify examples or invent beta-beta/beta-arch identities.

- Regeneration and enrichment retain corrected fields for exactly the bounded targets.
- Every repaired definition, parent, xref and method cites its inspected evidence with source/synthesis distinctions.
- Strict schema and grounding semantic checks pass for changed targets; their success is not scientific qualification.
- Post-curation review inspects exact changed bytes and carries forward each relevant stable issue key; unresolved rights and method gaps are not marked closed.
- No REVIEWED status or human sign-off is inferred from this agent audit.

## Category Boundaries

- retain: proteintraitsmech:HELIX_TURN_HELIX, proteintraitsmech:BETA_ALPHA_BETA, proteintraitsmech:GREEK_KEY, proteintraitsmech:BETA_HAIRPIN, proteintraitsmech:BETA_TURN, proteintraitsmech:SUPER_SECONDARY_MOTIF, proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF, proteintraitsmech:TURN. The eight targets denote distinct named motifs, broad motif parents, and a residue-assignment state. Correct direct parentage without merging these identities. Bare beta-beta spans hairpin and arch usages in inspected primary literature; no exact synonym or new identity is inferred.

## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| input-records | research/structural-traits-20261028/motifs/inspection-with-parents.json; Eight target paths and SHA-256 hashes; three maintained owners; contextual schema/method catalog/parent | supports | Read each complete target and its maintained owner code. Named motifs have token-only structural layers; no target-specific detection methods, evidence blocks, source-license metadata or canonical examples are present. Inspect captured the pre-curation bytes. |
| so | https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/Ontology_Files/so.obo; SO:0001079, SO:0001081, SO:0001114, SO:0001128, SO:0001133 stanzas | supports | Class identities and exact HTH/beta-turn labels. SO:0001114 denotes peptide_helix. SO:0001128 and its beta-turn child differ about obligatory hydrogen bonding. Rights: CC-BY-4.0 |
| valuesets | https://linkml.io/valuesets/elements/LocalStructuralFeature/; BETA_HAIRPIN and POLYPEPTIDE_STRUCTURAL_MOTIF entries and schema source | supports | Hairpin entry has an ontology-gap flag, not SO:0001114; enum identifier denotes a vocabulary rather than a motif. Rights: Apache-2.0 repository license |
| promotif | https://pmc.ncbi.nlm.nih.gov/articles/PMC2143354/; Abstract; full PDF inaccessible | supports | Coordinate-based motif analyses include beta turns, hairpins, beta-alpha-beta units, and beta-sheet topology. Rights: No permissive article license inspected; no full-text redistribution |
| promotif-manual | https://www.uoxray.uoregon.edu/local/manuals/promotif/document_2.html; Availability; Running; Secondary Structure; Beta Turns; strands/sheets/BAB; Hairpins | supports | Beta turn criterion: four residues, C-alpha(i)-C-alpha(i+3) below 7 angstroms, central residues nonhelical. Hairpin requires antiparallel pairing. BAB requires parallel hydrogen-bonded strands with intervening helix. Outputs .bturns, .hpin, .bab, .sht; script invocation promotif pdbfile. Rights: Academic-use terms require signed LICENSE; industrial use requires contacting authors. Software neither installed nor licensed by this task. |
| greek-key | https://pubmed.ncbi.nlm.nih.gov/8506258/; PubMed abstract | supports | Four-strand +3,-1,-1 connectivity; three groups based on hydrogen bonding, with differing 3D shapes. Rights: Article reuse terms unresolved; no prose copied |
| hairpin-analysis | https://pmc.ncbi.nlm.nih.gov/articles/PMC7888580/; Figure 1; sections 2.1 and 4.1 | supports | Two antiparallel strands linked by a loop. This study supplements DSSP screening with contact filtering; its restricted length/contact thresholds are study selection criteria, not universal class limits. Rights: Copyright The Protein Society 2021; permissive article license not inspected |
| beta-beta-context | https://pmc.ncbi.nlm.nih.gov/articles/PMC10949314/; Section 2.1 and Figure 1 caption | supports | Uses beta-beta loops for both paired-strand hairpin and unpaired-strand arch connections. Thus bare beta-beta does not specify hairpin topology. Rights: CC-BY-NC-ND-4.0 shown on article; cited factual distinction only, no source prose/figures redistributed |
| hth-primary | https://www.nature.com/articles/298718a0; Publisher abstract, accessed through its cookies_not_supported URL | supports | Cro structural study associates a two-helix unit with DNA recognition. Does not establish universal DNA-binding activity for every geometrical H-turn-H segment. Rights: Subscription article; no permissive redistribution terms verified |
| hth-matrix | https://pubmed.ncbi.nlm.nih.gov/2402433/; PubMed abstract | supports | A sequence scoring matrix based on 91 presumed HTH sequences estimates motif likelihood; prediction does not demonstrate geometry or DNA binding. Rights: Article reuse terms unresolved; no prose copied |
| emboss | https://emboss.bioinformatics.nl/cgi-bin/emboss/help/helixturnhelix; Description and command-line qualifiers | supports | Executable uses Dodd-Egan method and reports putative motif locations and scores; -sequence, -outfile, -minsd, -auto documented. Rights: Software redistribution not evaluated; no installation or source redistribution proposed |
| dssp | https://github.com/PDB-REDO/dssp/blob/trunk/doc/mkdssp.md; Synopsis, options, details; PMID metadata independently resolved but article has no PubMed abstract | supports | Assigns per-residue secondary states from coordinates; --output-format=dssp selects legacy output. Does not itself assign the named supersecondary classes. Rights: BSD-2-Clause repository license; separate from original article rights |
| alias-search | research/structural-traits-20261028/motifs/alias-search.json | context_only | Name search returned 612 matching lines, including distinct family/domain records; this is not a duplicate count or an audit of every hit. Exact beta-arch search returned no matches in the stated surfaces. Bare beta-beta remains ambiguous, so no synonym or new record is authorized by this search. |
| source-license | https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/LICENSE; CC-BY-4.0 license; compared separately with valuesets repository Apache-2.0 license | partial | SO and valuesets source repositories expose explicit licenses. These do not automatically license unrelated articles or PROMOTIF software; existing record-level attribution and source-license disposition need explicit reconciliation. |
| six-strict | research/structural-traits-20261028/motifs/validation.json; entry 0; output TSV named in command | supports | Validating 6 files with 1 workers; schema=/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/culturebotai-claw/workspace/worktrees/ptm-structure-20261028-029cc7/worktree/src/proteintraitsmech/schema/proteintraitsmech.yaml<br><br>=== validate-strict summary ===<br>  files scanned:      6<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                research/structural-traits-20261028/motifs/strict-validation.tsv |
| six-grounding | research/structural-traits-20261028/motifs/validation.json; entry 1; output TSV named in command | supports | files scanned: 6<br>registry proteins: 13208<br>source evidence objects: 22314<br>qualified record bindings: 22314<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: research/structural-traits-20261028/motifs/grounding-validation.tsv |
| parents-strict | research/structural-traits-20261028/motifs/validation-parents.json; entry 0; output TSV named in command | supports | Validating 2 files with 1 workers; schema=/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/culturebotai-claw/workspace/worktrees/ptm-structure-20261028-029cc7/worktree/src/proteintraitsmech/schema/proteintraitsmech.yaml<br><br>=== validate-strict summary ===<br>  files scanned:      2<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                research/structural-traits-20261028/motifs/validate_strict-parents.tsv |
| parents-grounding | research/structural-traits-20261028/motifs/validation-parents.json; entry 1; output TSV named in command | supports | files scanned: 2<br>registry proteins: 13208<br>source evidence objects: 22314<br>qualified record bindings: 22314<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: research/structural-traits-20261028/motifs/validate_uniprot_grounding-parents.tsv |

## Limits And Additional Notes

- Primary PROMOTIF, Greek-key, HTH and Dodd-Egan sources were inspected as abstracts only; PROMOTIF documentation was inspected in full. No inaccessible full text is claimed read.
- No exact source quotations are copied; proposed wording is curator synthesis except where source-native term identity is explicitly stated. Article rights remain source-specific.
- PROMOTIF, EMBOSS and DSSP recipes were documented but not installed or executed during this audit. PROMOTIF access/license prerequisite remains unresolved.
- InterPro matches are treated as family/signature evidence, not structural motif proof; this audit does not evaluate every InterPro model.
- No release-pinned QUALIFIED protein occurrence or exact residue boundaries are asserted.
- Ignored-inclusive absence search is limited to its recorded corpus paths and file extensions. The 612 matched lines are neither duplicates nor individually reviewed records.
- Review does not initialize or advance workflow stages, edit scientific records or Git state, or access other live sessions.
- Original captured input hashes are preserved. This is a pre-curation observation and cannot close its own findings.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261028T184459Z-structural-motif-initial-audit
kind: category
repository: CultureBotAI/proteintraitsmech
title: Initial audit of eight bounded structural motif and immediate-parent records
started_at: '2026-10-28T18:34:27Z'
finished_at: '2026-10-28T18:44:59Z'
reviewer:
  identity: codex-gpt-6-astra
  kind: agent
  model: gpt-6-astra
  independence: independent
  independence_basis: Separate audit agent reviewed captured original records and
    sources; did not author or change the scientific records, maintained owners, schema,
    or method catalog.
skill: .claude/skills/review-yaml-category/SKILL.md
completion: completed
verdict: needs_curation
scientific_review: true
summary: Bounded scientific audit of eight original motif/parent records found five
  major and two minor issues despite successful deterministic validation. Correct
  false equivalence, unsupported provenance and hierarchy, refine definitions, and
  expose method/rights limits. Concrete recommendations are retained in the evidence
  dossier; no scientific records were edited by this review.
source:
  git_revision: c4147394c698324ae537c0c63c2c9f6647c4f4fc
  state: working_tree
  inputs:
  - path: data/methods/methods.yaml
    sha256: 1a0940b44fdf879489b664614debac0347b7780f1d9cc2d0c3c863a6fea78b54
    role: context
  - path: data/traits/structure/secondary/beta-alpha-beta.yaml
    sha256: 0a3416cb72ab91205cbce0f86a06e9136aa72dba23676df30f4e1ef984f41040
    role: target
  - path: data/traits/structure/secondary/beta-hairpin.yaml
    sha256: d2935c640d54c20d72bb4592599a38a55db4f71d553ec396df37a6a374cdf037
    role: target
  - path: data/traits/structure/secondary/beta-turn.yaml
    sha256: dea9aebe3b8802d56974040fa2ba63eeb79456d2463438a9ed547ac87a8b3b49
    role: target
  - path: data/traits/structure/secondary/greek-key.yaml
    sha256: d698b28b73843f6b5486c5eb05dabae2c5548a4e4dd98f3be6f9cae5c7019598
    role: target
  - path: data/traits/structure/secondary/helix-turn-helix.yaml
    sha256: 55f8bf78f0b7dbcbbe93734f3bc14870d440a613a918f6d236e32f097facdedb
    role: target
  - path: data/traits/structure/secondary/polypeptide-structural-motif.yaml
    sha256: fc0d3e127d690d6a85ca4ee1dc273fef91cdd2decfc2551919eeb7935ba2dc19
    role: target
  - path: data/traits/structure/secondary/secondary-structure-element.yaml
    sha256: 4a96cefafdcd3de0282b1424eab7f8faa679d55033d4f5d7ff212e126c2a7a64
    role: context
  - path: data/traits/structure/secondary/super-secondary-motif.yaml
    sha256: e49d64566c45816586040b953c75ce84ef6f96d213577b29085dcc33d49f8a18
    role: target
  - path: data/traits/structure/secondary/turn.yaml
    sha256: 964b7863277e731182507cfcf255743d8b5dcf71147ae604e012dc0725a04046
    role: target
  - path: research/cross-source-comparison-review-1.md
    sha256: 8c6acc79b03b4c970d3065e1bb67b23bac3f9baee19f2d82b23d62aa21c5e7e6
    role: context
  - path: scripts/enrich_secondary_structural_defs.py
    sha256: 1fadb6fe3541597507f592cf82e403bebf064772dba081648a001dacf542bc54
    role: context
  - path: scripts/seed_localstructuralfeature.py
    sha256: dea0ca33c86dc9cdc8597de859fe1db5ae92d3fb265e3f10b1074e5c2652415b
    role: context
  - path: scripts/seed_secondary_structure.py
    sha256: f91fbc16de8ea8ed04d6a0fd0ab37eac5243088c5f78687573abf9014eebc1da
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Five named local/supersecondary motifs and three directly affected
    existing parents; full coverage of this explicit eight-record selection only.
  selection: Named HTH, BAB, Greek key, beta hairpin and beta turn plus SUPER_SECONDARY_MOTIF,
    POLYPEPTIDE_STRUCTURAL_MOTIF and TURN, selected because their definitions or direct
    hierarchy affect the named motifs.
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
  - target: proteintraitsmech:SECONDARY_STRUCTURE_ELEMENT
    reason: Read as immediate context only; no full assessment of all its children
      or the complete 34-record structural-secondary cohort.
  - target: Other alias-search hits and beta-arch candidates
    reason: Lexical discovery is not an individual-record audit or authorization to
      create or merge classes.
  - target: Protein exemplar promotion and graph claims
    reason: No examples or graphs in captured targets; qualification handled separately.
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
- target_id: proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  path: data/traits/structure/secondary/polypeptide-structural-motif.yaml
  label: polypeptide structural motif
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
- target_id: proteintraitsmech:TURN
  path: data/traits/structure/secondary/turn.yaml
  label: turn
  kind: generated
  record_class: ProteinTraitRecord
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_secondary_structure.py
    role: maintained seeder
checks:
- check_id: six-strict
  name: Strict LinkML validation
  status: passed
  required: true
  summary: Exit 0; zero error rows.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  command: .venv/bin/python scripts/validate_strict.py --workers 1 --out research/structural-traits-20261028/motifs/strict-validation.tsv
    data/traits/structure/secondary/helix-turn-helix.yaml data/traits/structure/secondary/beta-alpha-beta.yaml
    data/traits/structure/secondary/greek-key.yaml data/traits/structure/secondary/beta-hairpin.yaml
    data/traits/structure/secondary/beta-turn.yaml data/traits/structure/secondary/super-secondary-motif.yaml
  exit_code: 0
  expected_exit_code: 0
  evidence_ids:
  - six-strict
- check_id: six-grounding
  name: UniProt grounding semantic validation
  status: passed
  required: true
  summary: Exit 0; zero semantic findings. These targets have no canonical examples,
    so this is not protein-example qualification.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  - proteintraitsmech:BETA_ALPHA_BETA
  - proteintraitsmech:GREEK_KEY
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  command: .venv/bin/python scripts/validate_uniprot_grounding.py --out research/structural-traits-20261028/motifs/grounding-validation.tsv
    data/traits/structure/secondary/helix-turn-helix.yaml data/traits/structure/secondary/beta-alpha-beta.yaml
    data/traits/structure/secondary/greek-key.yaml data/traits/structure/secondary/beta-hairpin.yaml
    data/traits/structure/secondary/beta-turn.yaml data/traits/structure/secondary/super-secondary-motif.yaml
  exit_code: 0
  expected_exit_code: 0
  evidence_ids:
  - six-grounding
- check_id: parents-strict
  name: Strict LinkML validation
  status: passed
  required: true
  summary: Exit 0; zero error rows.
  target_ids:
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  command: .venv/bin/python scripts/validate_strict.py --out research/structural-traits-20261028/motifs/validate_strict-parents.tsv
    --workers 1 data/traits/structure/secondary/polypeptide-structural-motif.yaml
    data/traits/structure/secondary/turn.yaml
  exit_code: 0
  expected_exit_code: 0
  evidence_ids:
  - parents-strict
- check_id: parents-grounding
  name: UniProt grounding semantic validation
  status: passed
  required: true
  summary: Exit 0; zero semantic findings. These targets have no canonical examples,
    so this is not protein-example qualification.
  target_ids:
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:TURN
  command: .venv/bin/python scripts/validate_uniprot_grounding.py --out research/structural-traits-20261028/motifs/validate_uniprot_grounding-parents.tsv
    data/traits/structure/secondary/polypeptide-structural-motif.yaml data/traits/structure/secondary/turn.yaml
  exit_code: 0
  expected_exit_code: 0
  evidence_ids:
  - parents-grounding
- check_id: scientific-source-audit
  name: Native content checklist and inspected-source comparison
  status: passed
  required: true
  summary: Read complete targets, captured owners, inspected primary literature or
    source-native authorities, compared identity, hierarchy, source support, representations,
    licensing, and method coverage. Completed audit found scientific defects; passed
    means the check was performed.
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
  - input-records
  - so
  - valuesets
  - promotif
  - promotif-manual
  - greek-key
  - hairpin-analysis
  - beta-beta-context
  - hth-primary
  - hth-matrix
  - emboss
  - dssp
- check_id: duplicate-boundary
  name: Ignored-inclusive alias search and cohort boundary adjudication
  status: passed
  required: true
  summary: Preserved class-versus-domain boundaries. No bare beta-beta equivalence
    or beta-arch record creation supported.
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
  - alias-search
  - beta-beta-context
- check_id: graph-example
  name: Causal-edge and protein-occurrence qualification
  status: not_applicable
  required: false
  summary: No causal graph or protein exemplar is present in these captured records;
    no promotion or occurrence claim was reviewed.
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
  - input-records
evidence:
- evidence_id: input-records
  kind: record_content
  reference: research/structural-traits-20261028/motifs/inspection-with-parents.json
  locator: Eight target paths and SHA-256 hashes; three maintained owners; contextual
    schema/method catalog/parent
  accessed_at: '2026-10-28T18:44:59Z'
  support: supports
  summary: Read each complete target and its maintained owner code. Named motifs have
    token-only structural layers; no target-specific detection methods, evidence blocks,
    source-license metadata or canonical examples are present. Inspect captured the
    pre-curation bytes.
- evidence_id: so
  kind: database
  reference: https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/Ontology_Files/so.obo
  locator: SO:0001079, SO:0001081, SO:0001114, SO:0001128, SO:0001133 stanzas
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'Class identities and exact HTH/beta-turn labels. SO:0001114 denotes peptide_helix.
    SO:0001128 and its beta-turn child differ about obligatory hydrogen bonding. Rights:
    CC-BY-4.0'
- evidence_id: valuesets
  kind: database
  reference: https://linkml.io/valuesets/elements/LocalStructuralFeature/
  locator: BETA_HAIRPIN and POLYPEPTIDE_STRUCTURAL_MOTIF entries and schema source
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'Hairpin entry has an ontology-gap flag, not SO:0001114; enum identifier
    denotes a vocabulary rather than a motif. Rights: Apache-2.0 repository license'
- evidence_id: promotif
  kind: primary_source
  reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC2143354/
  locator: Abstract; full PDF inaccessible
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'Coordinate-based motif analyses include beta turns, hairpins, beta-alpha-beta
    units, and beta-sheet topology. Rights: No permissive article license inspected;
    no full-text redistribution'
- evidence_id: promotif-manual
  kind: authority
  reference: https://www.uoxray.uoregon.edu/local/manuals/promotif/document_2.html
  locator: Availability; Running; Secondary Structure; Beta Turns; strands/sheets/BAB;
    Hairpins
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'Beta turn criterion: four residues, C-alpha(i)-C-alpha(i+3) below 7 angstroms,
    central residues nonhelical. Hairpin requires antiparallel pairing. BAB requires
    parallel hydrogen-bonded strands with intervening helix. Outputs .bturns, .hpin,
    .bab, .sht; script invocation promotif pdbfile. Rights: Academic-use terms require
    signed LICENSE; industrial use requires contacting authors. Software neither installed
    nor licensed by this task.'
- evidence_id: greek-key
  kind: primary_source
  reference: https://pubmed.ncbi.nlm.nih.gov/8506258/
  locator: PubMed abstract
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'Four-strand +3,-1,-1 connectivity; three groups based on hydrogen bonding,
    with differing 3D shapes. Rights: Article reuse terms unresolved; no prose copied'
- evidence_id: hairpin-analysis
  kind: primary_source
  reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC7888580/
  locator: Figure 1; sections 2.1 and 4.1
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'Two antiparallel strands linked by a loop. This study supplements DSSP
    screening with contact filtering; its restricted length/contact thresholds are
    study selection criteria, not universal class limits. Rights: Copyright The Protein
    Society 2021; permissive article license not inspected'
- evidence_id: beta-beta-context
  kind: primary_source
  reference: https://pmc.ncbi.nlm.nih.gov/articles/PMC10949314/
  locator: Section 2.1 and Figure 1 caption
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'Uses beta-beta loops for both paired-strand hairpin and unpaired-strand
    arch connections. Thus bare beta-beta does not specify hairpin topology. Rights:
    CC-BY-NC-ND-4.0 shown on article; cited factual distinction only, no source prose/figures
    redistributed'
- evidence_id: hth-primary
  kind: primary_source
  reference: https://www.nature.com/articles/298718a0
  locator: Publisher abstract, accessed through its cookies_not_supported URL
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'Cro structural study associates a two-helix unit with DNA recognition.
    Does not establish universal DNA-binding activity for every geometrical H-turn-H
    segment. Rights: Subscription article; no permissive redistribution terms verified'
- evidence_id: hth-matrix
  kind: primary_source
  reference: https://pubmed.ncbi.nlm.nih.gov/2402433/
  locator: PubMed abstract
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'A sequence scoring matrix based on 91 presumed HTH sequences estimates
    motif likelihood; prediction does not demonstrate geometry or DNA binding. Rights:
    Article reuse terms unresolved; no prose copied'
- evidence_id: emboss
  kind: authority
  reference: https://emboss.bioinformatics.nl/cgi-bin/emboss/help/helixturnhelix
  locator: Description and command-line qualifiers
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'Executable uses Dodd-Egan method and reports putative motif locations
    and scores; -sequence, -outfile, -minsd, -auto documented. Rights: Software redistribution
    not evaluated; no installation or source redistribution proposed'
- evidence_id: dssp
  kind: authority
  reference: https://github.com/PDB-REDO/dssp/blob/trunk/doc/mkdssp.md
  locator: Synopsis, options, details; PMID metadata independently resolved but article
    has no PubMed abstract
  accessed_at: '2026-10-28T18:41:34Z'
  support: supports
  summary: 'Assigns per-residue secondary states from coordinates; --output-format=dssp
    selects legacy output. Does not itself assign the named supersecondary classes.
    Rights: BSD-2-Clause repository license; separate from original article rights'
- evidence_id: alias-search
  kind: search
  reference: research/structural-traits-20261028/motifs/alias-search.json
  accessed_at: '2026-10-28T18:44:59Z'
  support: context_only
  summary: Name search returned 612 matching lines, including distinct family/domain
    records; this is not a duplicate count or an audit of every hit. Exact beta-arch
    search returned no matches in the stated surfaces. Bare beta-beta remains ambiguous,
    so no synonym or new record is authorized by this search.
  search_scope: Recorded rg --no-ignore --hidden commands cover data/traits, data/equivalence
    and research, YAML/Markdown/TSV files, excluding this task dossier. Includes ignored
    and hidden files. A lexical search does not establish semantic absence across
    all resources.
- evidence_id: source-license
  kind: authority
  reference: https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/master/LICENSE
  locator: CC-BY-4.0 license; compared separately with valuesets repository Apache-2.0
    license
  accessed_at: '2026-10-28T18:44:59Z'
  support: partial
  summary: SO and valuesets source repositories expose explicit licenses. These do
    not automatically license unrelated articles or PROMOTIF software; existing record-level
    attribution and source-license disposition need explicit reconciliation.
- evidence_id: six-strict
  kind: validation
  reference: research/structural-traits-20261028/motifs/validation.json
  locator: entry 0; output TSV named in command
  accessed_at: '2026-10-28T18:44:59Z'
  support: supports
  summary: "Validating 6 files with 1 workers; schema=/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/culturebotai-claw/workspace/worktrees/ptm-structure-20261028-029cc7/worktree/src/proteintraitsmech/schema/proteintraitsmech.yaml\n\
    \n=== validate-strict summary ===\n  files scanned:      6\n  files with ERROR:\
    \   0\n  total ERROR rows:   0\n  TSV:                research/structural-traits-20261028/motifs/strict-validation.tsv"
- evidence_id: six-grounding
  kind: validation
  reference: research/structural-traits-20261028/motifs/validation.json
  locator: entry 1; output TSV named in command
  accessed_at: '2026-10-28T18:44:59Z'
  support: supports
  summary: 'files scanned: 6

    registry proteins: 13208

    source evidence objects: 22314

    qualified record bindings: 22314

    UniProt membership objects: 431

    hierarchy records: 0

    semantic findings: 0

    TSV: research/structural-traits-20261028/motifs/grounding-validation.tsv'
- evidence_id: parents-strict
  kind: validation
  reference: research/structural-traits-20261028/motifs/validation-parents.json
  locator: entry 0; output TSV named in command
  accessed_at: '2026-10-28T18:44:59Z'
  support: supports
  summary: "Validating 2 files with 1 workers; schema=/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/culturebotai-claw/workspace/worktrees/ptm-structure-20261028-029cc7/worktree/src/proteintraitsmech/schema/proteintraitsmech.yaml\n\
    \n=== validate-strict summary ===\n  files scanned:      2\n  files with ERROR:\
    \   0\n  total ERROR rows:   0\n  TSV:                research/structural-traits-20261028/motifs/validate_strict-parents.tsv"
- evidence_id: parents-grounding
  kind: validation
  reference: research/structural-traits-20261028/motifs/validation-parents.json
  locator: entry 1; output TSV named in command
  accessed_at: '2026-10-28T18:44:59Z'
  support: supports
  summary: 'files scanned: 2

    registry proteins: 13208

    source evidence objects: 22314

    qualified record bindings: 22314

    UniProt membership objects: 431

    hierarchy records: 0

    semantic findings: 0

    TSV: research/structural-traits-20261028/motifs/validate_uniprot_grounding-parents.tsv'
assessments:
- assessment_id: assess-helix-turn-helix
  area: identity
  topic: Class identity, source support, hierarchy and applicable representation
  outcome: concern
  summary: Keep DNA-binding examples and predictions separate from the geometrical
    class. No generic geometry-complete HTH classifier was verified.
  target_ids:
  - proteintraitsmech:HELIX_TURN_HELIX
  evidence_ids:
  - input-records
  - so
  - hth-primary
  - hth-matrix
  - emboss
  details: 'Proposed definition: A recurring structural motif comprising two alpha
    helices linked by a short turn. Proposed direct parents: proteintraitsmech:SUPER_SECONDARY_MOTIF.
    Exact proposed fields and method/rights limitations are in the evidence dossier.
    These are proposals, not applied edits.'
- assessment_id: assess-beta-alpha-beta
  area: identity
  topic: Class identity, source support, hierarchy and applicable representation
  outcome: concern
  summary: Read .bab output. E-H-E alone omits strand pairing/orientation. Remove
    Rossmann parenthesis from defining criterion; it is contextual, not class identity.
  target_ids:
  - proteintraitsmech:BETA_ALPHA_BETA
  evidence_ids:
  - input-records
  - promotif
  - promotif-manual
  details: 'Proposed definition: A supersecondary motif with two parallel, hydrogen-bonded
    beta strands connected in sequence through an intervening alpha helix. Proposed
    direct parents: proteintraitsmech:SUPER_SECONDARY_MOTIF. Exact proposed fields
    and method/rights limitations are in the evidence dossier. These are proposals,
    not applied edits.'
- assessment_id: assess-greek-key
  area: identity
  topic: Class identity, source support, hierarchy and applicable representation
  outcome: concern
  summary: Keep canonical token for compatibility; put connectivity in the STRUCTURAL
    definition. PROMOTIF .sht is an input for reviewed connectivity classification,
    not a verified automatic Greek-key call.
  target_ids:
  - proteintraitsmech:GREEK_KEY
  evidence_ids:
  - input-records
  - greek-key
  details: 'Proposed definition: A four-strand beta-structural motif with Greek-key
    connectivity, conventionally described by the topology +3,-1,-1. Proposed direct
    parents: proteintraitsmech:SUPER_SECONDARY_MOTIF. Exact proposed fields and method/rights
    limitations are in the evidence dossier. These are proposals, not applied edits.'
- assessment_id: assess-beta-hairpin
  area: identity
  topic: Class identity, source support, hierarchy and applicable representation
  outcome: concern
  summary: Read .hpin output. In the existing token, turn denotes a connector, not
    a necessary four-residue beta turn; keep this explicit. Do not add bare beta-beta
    as exact synonym.
  target_ids:
  - proteintraitsmech:BETA_HAIRPIN
  evidence_ids:
  - input-records
  - hairpin-analysis
  - promotif-manual
  - beta-beta-context
  details: 'Proposed definition: A structural motif formed by two sequence-adjacent
    beta strands that pair antiparallel and are joined by a connecting loop. Proposed
    direct parents: proteintraitsmech:SUPER_SECONDARY_MOTIF. Exact proposed fields
    and method/rights limitations are in the evidence dossier. These are proposals,
    not applied edits.'
- assessment_id: assess-beta-turn
  area: identity
  topic: Class identity, source support, hierarchy and applicable representation
  outcome: concern
  summary: Read .bturns output. Move from DSSP-specific TURN to existing broader motif
    parent. Remove unsupported commonest-turn superlative. It need not join beta strands.
  target_ids:
  - proteintraitsmech:BETA_TURN
  evidence_ids:
  - input-records
  - so
  - promotif-manual
  details: 'Proposed definition: A local four-residue backbone motif classified by
    the conformation of its two central residues; an i-to-i+3 backbone hydrogen bond
    may be present. Proposed direct parents: proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF.
    Exact proposed fields and method/rights limitations are in the evidence dossier.
    These are proposals, not applied edits.'
- assessment_id: assess-super-secondary-motif
  area: identity
  topic: Class identity, source support, hierarchy and applicable representation
  outcome: concern
  summary: Curator synthesis of inspected motif classes, not a quotation. Do not assert
    a universal fixed size or independent-folding rule. Classification requires a
    specified subtype rule; umbrella has no single topology matcher.
  target_ids:
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  evidence_ids:
  - input-records
  - promotif
  - greek-key
  - beta-beta-context
  details: 'Proposed definition: A recurring arrangement of a small number of secondary-structure
    elements defined by their spatial relationships and connectivity. Proposed direct
    parents: proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF. Exact proposed fields
    and method/rights limitations are in the evidence dossier. These are proposals,
    not applied edits.'
- assessment_id: assess-polypeptide-structural-motif
  area: identity
  topic: Class identity, source support, hierarchy and applicable representation
  outcome: concern
  summary: Repair does-not-form to need-not-form. Remove whole-enum and peptide-helix
    equivalence xrefs; retain source attribution separately.
  target_ids:
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  evidence_ids:
  - input-records
  - so
  - valuesets
  details: 'Proposed definition: A recurring three-dimensional structural element
    within a polypeptide chain that need not form an independently stable globular
    unit. Proposed direct parents: none. Exact proposed fields and method/rights limitations
    are in the evidence dossier. These are proposals, not applied edits.'
- assessment_id: assess-turn
  area: identity
  topic: Class identity, source support, hierarchy and applicable representation
  outcome: concern
  summary: Preserve the original DSSP-state identity. This class is not the universal
    parent of geometrically defined beta turns; source SO:0001128 has the same hydrogen-bond
    tension and should not be inserted as an exact equivalent.
  target_ids:
  - proteintraitsmech:TURN
  evidence_ids:
  - input-records
  - dssp
  details: 'Proposed definition: A backbone region assigned the hydrogen-bonded turn
    state T by the DSSP secondary-structure algorithm. Proposed direct parents: proteintraitsmech:SECONDARY_STRUCTURE_ELEMENT.
    Exact proposed fields and method/rights limitations are in the evidence dossier.
    These are proposals, not applied edits.'
findings:
- finding_id: wrong-equivalence
  issue_key: proteintraitsmech-structural-motifs-wrong-equivalence
  category: grounding
  severity: major
  status: open
  certainty: confirmed
  title: Peptide-helix and whole-enumeration xrefs assert false motif equivalence
  description: SO:0001114 names peptide_helix. The whole LocalStructuralFeature enumeration
    is not equivalent to any individual motif. Remove these exact xrefs from the three
    selected records, retain source provenance separately, and preserve SO:0001079
    for the broad polypeptide-motif class.
  target_ids:
  - proteintraitsmech:BETA_HAIRPIN
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  field_paths:
  - xrefs
  evidence_ids:
  - input-records
  - so
  - valuesets
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
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
- finding_id: definition-support
  issue_key: proteintraitsmech-structural-motifs-definition-support
  category: evidence
  severity: major
  status: open
  certainty: confirmed
  title: Named motif definitions and topology claims need class-specific evidence
  description: The generic DSSP citation does not establish the displayed HTH, BAB
    or Greek-key topology or the broad four-residue beta-turn class in this audit.
    Source-specific literature and ontology records support replacement definitions.
    Remove unsupported superlatives and avoid treating DNA-binding or Rossmann context
    as defining all instances.
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
  - input-records
  - so
  - promotif
  - promotif-manual
  - greek-key
  - hth-primary
  - dssp
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
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
- finding_id: beta-turn-parent
  issue_key: proteintraitsmech-structural-motifs-beta-turn-parent
  category: consistency
  severity: major
  status: open
  certainty: confirmed
  title: Broad beta-turn class is placed beneath a narrower DSSP T state
  description: BETA_TURN allows absence of the i-to-i+3 hydrogen bond while TURN is
    explicitly the hydrogen-bonded DSSP T state. Move BETA_TURN beneath the existing
    broader POLYPEPTIDE_STRUCTURAL_MOTIF class and preserve TURN state identity. Blindly
    adopting SO:0001128 would retain an upstream hydrogen-bond inconsistency.
  target_ids:
  - proteintraitsmech:BETA_TURN
  - proteintraitsmech:TURN
  field_paths:
  - parent_traits
  - definition
  - secondary_structure_representations
  evidence_ids:
  - input-records
  - so
  - promotif-manual
  - dssp
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
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
- finding_id: motif-stability
  issue_key: proteintraitsmech-structural-motifs-motif-stability
  category: identity
  severity: major
  status: open
  certainty: confirmed
  title: Polypeptide structural motif incorrectly excludes independently stable units
  description: The local does-not-form statement is stronger than SO:0001079, which
    makes independent stability unnecessary rather than prohibited. Repair the modal
    distinction; connect SUPER_SECONDARY_MOTIF below this broad existing class without
    imposing a universal domain-size or folding prohibition.
  target_ids:
  - proteintraitsmech:POLYPEPTIDE_STRUCTURAL_MOTIF
  - proteintraitsmech:SUPER_SECONDARY_MOTIF
  field_paths:
  - definition
  - definition_source
  - parent_traits
  evidence_ids:
  - input-records
  - so
  - valuesets
  - promotif
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
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
- finding_id: topology-layer
  issue_key: proteintraitsmech-structural-motifs-topology-layer
  category: representation
  severity: minor
  status: open
  certainty: confirmed
  title: Topology tokens omit distinguishing geometric criteria
  description: The generated structural definitions largely restate tokens. State
    BAB strand parallelism/pairing, Greek-key connectivity and hairpin antiparallel
    pairing in prose, and distinguish a generic hairpin connector from a four-residue
    beta turn. Retain canonical tokens only with explicit interpretation.
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
  - input-records
  - so
  - promotif-manual
  - greek-key
  - hairpin-analysis
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
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
- finding_id: method-coverage
  issue_key: proteintraitsmech-structural-motifs-method-coverage
  category: completeness
  severity: minor
  status: open
  certainty: confirmed
  title: Category DSSP fallback is not a complete motif classifier
  description: The records have no class-specific detection recipes. DSSP assigns
    residue states; InterPro/family matches are not geometrical proof. PROMOTIF documents
    BAB/hairpin/turn classification but has an unfulfilled license prerequisite. EMBOSS
    HTH is a sequence prediction. Greek-key and broad motif classes still require
    explicit reviewed topology rules; do not advertise complete executable coverage.
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
  - input-records
  - dssp
  - promotif-manual
  - emboss
  - hth-matrix
  - greek-key
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
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
- finding_id: rights-provenance
  issue_key: proteintraitsmech-structural-motifs-rights-provenance
  category: provenance
  severity: major
  status: open
  certainty: confirmed
  title: Source and license disposition is unresolved for selected records
  description: The captured records do not state source-license disposition. Reconcile
    source-specific attribution and the rights basis for synthesized definitions before
    release, distinguishing SO CC-BY-4.0 and valuesets Apache-2.0 from paper rights
    and conditional PROMOTIF software access. A tool license or cited PMID is not
    a record-wide content license.
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
  - input-records
  - so
  - valuesets
  - source-license
  - promotif-manual
  - beta-beta-context
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
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
actions:
- action_id: curate-owned-motifs
  description: Apply source-grounded per-record proposals through maintained seeder/enrichment
    owners or a shared bounded overlay. Preserve all identities; record PROPOSED and
    accurate agent history only. Keep license/method gaps explicit; do not qualify
    examples or invent beta-beta/beta-arch identities.
  finding_ids:
  - wrong-equivalence
  - definition-support
  - beta-turn-parent
  - motif-stability
  - topology-layer
  - method-coverage
  - rights-provenance
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
    role: maintained motif seeder
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_secondary_structural_defs.py
    role: structural definition editor
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_localstructuralfeature.py
    role: maintained seeder
  acceptance_checks:
  - Regeneration and enrichment retain corrected fields for exactly the bounded targets.
  - Every repaired definition, parent, xref and method cites its inspected evidence
    with source/synthesis distinctions.
  - Strict schema and grounding semantic checks pass for changed targets; their success
    is not scientific qualification.
  - Post-curation review inspects exact changed bytes and carries forward each relevant
    stable issue key; unresolved rights and method gaps are not marked closed.
  - No REVIEWED status or human sign-off is inferred from this agent audit.
  generator: scripts/seed_secondary_structure.py; scripts/seed_localstructuralfeature.py;
    scripts/enrich_secondary_structural_defs.py
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
  rationale: The eight targets denote distinct named motifs, broad motif parents,
    and a residue-assignment state. Correct direct parentage without merging these
    identities. Bare beta-beta spans hairpin and arch usages in inspected primary
    literature; no exact synonym or new identity is inferred.
  evidence_ids:
  - so
  - promotif-manual
  - greek-key
  - hairpin-analysis
  - beta-beta-context
  - alias-search
limitations:
- Primary PROMOTIF, Greek-key, HTH and Dodd-Egan sources were inspected as abstracts
  only; PROMOTIF documentation was inspected in full. No inaccessible full text is
  claimed read.
- No exact source quotations are copied; proposed wording is curator synthesis except
  where source-native term identity is explicitly stated. Article rights remain source-specific.
- PROMOTIF, EMBOSS and DSSP recipes were documented but not installed or executed
  during this audit. PROMOTIF access/license prerequisite remains unresolved.
- InterPro matches are treated as family/signature evidence, not structural motif
  proof; this audit does not evaluate every InterPro model.
- No release-pinned QUALIFIED protein occurrence or exact residue boundaries are asserted.
- Ignored-inclusive absence search is limited to its recorded corpus paths and file
  extensions. The 612 matched lines are neither duplicates nor individually reviewed
  records.
- Review does not initialize or advance workflow stages, edit scientific records or
  Git state, or access other live sessions.
- Original captured input hashes are preserved. This is a pre-curation observation
  and cannot close its own findings.
links:
- research/structural-traits-20261028/motifs/evidence-dossier.json
tags:
- structure
- motif
- bounded
- initial-audit
```
