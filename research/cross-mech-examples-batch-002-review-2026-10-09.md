# Cross-Mech examples, batch 002: review and promotion record

- Date: 2026-10-09. UniProt release `2026_03`; GO `go-basic.obo` `releases/2026-06-15`.
  Reviewer: `claude` (AI review, not curator sign-off; no `mapping_status` or definition
  changed).
- Inputs: the cross-Mech snapshot in `data/cross_mech/` and the audit described in
  [cross-Mech protein examples](cross-mech-protein-examples.md). This batch takes every
  pair batch 001 left unattached on an existing record.
- Route: the UniProt exact-accession fact lane with two additions from #1031:
  - **GO true-path inheritance (#1002).** A GO record may rest on an exact,
    evidence-qualifying annotation to a descendant term, reached upward by
    `is_a`/`part_of` within one GO namespace. The strongest evidence is chosen first.
  - **A narrow Swiss-Prot rule (#1004, the maintainer's decision).** On reviewed entries
    only, it admits an `IEA:UniProtKB-EC` GO term when the EC assignment itself is
    curated: no evidence tag, or experimental/curator evidence (#1048). It also admits a
    catalytic activity curated with no evidence tag.
- A sibling claim chose each candidate; only UniProt's own facts qualified it.
- Staging batches, run in order through the ordinary recipes:
  - `cross-mech-canary-004`: shard 25 of 34, 8 candidates on 3 records. It exercised
    three paths:
    - the corrected EC rule: P00807's beta-lactamase EC rests on a sequence-model
      catalytic activity (`ECO:0000255`), so it is rejected;
    - the weak-descendant path: P18142 and P21837 have only an `IEA:UniProtKB-SubCell`
      descendant annotation, so they are rejected;
    - five inherited magnetosome rows, approved and installed first.
  - `cross-mech-examples-004`: 84 records, 217 candidates. That is the 82 records the
    canary did not cover, plus the canary's two all-rejected records, which were reopened
    by design and decided again identically. The two ledgers hold 225 decision rows for
    222 distinct pairs; every count below takes each pair once.
- Fetch receipts `uniprot-registry-fetch-receipt:4b7025ea…0509` and `…:25765fbd…2b29`.
  Both are network `UNIPROT_REST` acquisitions, verified by the promoter, with 0 blocked
  accessions. Staging files are local and ignored; the durable registries and trait
  records are the installed claims.

## Result

78 sibling-asserted (protein, trait) pairs are now `QUALIFIED` canonical examples on 19
existing trait records, each a whole-protein occurrence backed by an exact UniProt fact.
77 examples were appended, and 1 existing legacy example (P0A7S3 on `GO:0005840`) was
upgraded in place.

| Trait category | Examples | Route and evidence |
| --- | ---: | --- |
| `FUNC_LOCALIZATION` (GO cellular component) | 64 | inherited from a descendant term: IDA 63, EXP 1 |
| `FUNC_MOLECULAR_FUNCTION` (GO) | 8 | `IEA:UniProtKB-EC` on Swiss-Prot with a curated EC: 7 exact, 1 inherited (P07254) |
| `FUNC_ENZYMATIC_ACTIVITY` (Rhea) | 6 | catalytic activity curated without an evidence tag, Swiss-Prot |

- **Totals:** 65 examples are inherited and 13 exact. 14 rest on the Swiss-Prot rule: 8
  EC-derived GO and 6 Rhea. All 78 are Swiss-Prot entries and 78 distinct proteins.
- **Sources:** CellStructureMech (63), TraitMech (9), and NaturalProductMech (6).
- **Ribosome (`GO:0005840`):** 55 *E. coli* ribosomal proteins (54 appended and P0A7S3
  upgraded). Each rests on an IDA annotation to a cytosolic or a large/small ribosomal
  subunit term. P02359, P0A7S3, and P0AA10 also carry exact `GO:0005840` annotations,
  but those are IBA and do not qualify.
- **Other localization records:**
  - photosystem II (PsbA2);
  - the *M. tuberculosis* proteasome core alpha and beta subunits;
  - spore-cortex protein SafA (EXP) on `GO:0043591`;
  - five magnetosome lumen and membrane proteins.
- **Enzymes:** eight on their molecular-function terms and six on their Rhea reactions.

Durable state after promotion:

| Registry | Rows | SHA-256 |
| --- | ---: | --- |
| ProteinReferences | 12,634 | `bfca614bf9d9039e954f2148fa6acda070cb5793ee258e761f0b49ef491cec28` |
| Evidence rows (logical) | 20,976 | `7ce2d58a3a86bb34bd9dcca866c56c8b750639d1a806f6d44d339ca886cb9fc1` |
| Bindings (logical) | 20,976 | `bbca67833daac4788e263dba8f6cd23c151e5ef8f0ec1ec351a55041d84f3326` |
| `uniprot_memberships.jsonl` facts | 359 | `f47e48f0daddb79c54ac4f9c02ef84fa36d791f3c08f29bb0457b25ed61c02a4` |
| `go_true_path_edges.jsonl` edges | 12 | `e27327cc1595214a8154f7244d8d7c0c4734e47844e93528389fd4918c0423f9` |

What changed in the registries:
- **Added:** 23 ProteinReferences and 78 rows each of evidence, bindings and facts.
- **Created:** the edges file, with 12 `is_a`/`part_of` edges, all proven by GO
  `releases/2026-06-15`.
- **Stamped:** 14 facts carry `uniprot_entry_type`, and the 8 EC-derived GO facts also
  carry `uniprot_ec_evidence`.
- **Unchanged:** every previously installed ProteinReference, evidence row and fact. Three
  existing bindings on the magnetosome record were re-pinned to its new `record_sha256`,
  as the promoter must do when a bound record's text changes (#1051).

## Review decisions

Every row was decided.

**Resolver rejections.** The resolver rejects a row unless the record term itself, or a
descendant reachable upward by `is_a`/`part_of` in one GO namespace, has an exact UniProt
fact whose evidence qualifies.

**Approved rows.** For every other row, review checked that the record and the protein
agree:
- **GO localization:** the inherited term is a component or subtype of the record's
  structure. Complex and organelle terms are carried by their components, the convention
  batch 001 applied.
- **GO molecular function:** the protein itself performs the activity.
- **Rhea:** UniProt's reaction text equals the record equation. All six matched exactly.
- **Review columns:** the review TSV shows each row's `source_trait_id` and
  `inheritance_path` (#1042).

**How notes were written.**
- **Inherited rows:** generated from each row's facts: evidence code and references, and
  every edge with its relation.
- **Exact approvals:** individually written.
- **Rejected rows:** generated from a classification against the GO closure: weak exact
  fact, weak descendants only, or nothing. Rhea notes cite the reaction's own evidence.

**Per-row adjudications:**
- **P08306 (rejected on review):** cytochrome c oxidase subunit 2 on `GO:0004129`.
  Subunit II carries the CuA electron-entry site, not the heme a3-CuB catalytic site, so
  the subunit alone does not perform the activity (#983).
- **P35149 (rejected on review, #1049):** SpoIVA on `GO:0043591`. Its only qualifying
  fact is an IMP (mutant-phenotype) annotation to the endospore cortex. UniProt places the
  protein in the cytoplasm, and it sits on the mother-cell side of the outer forespore
  membrane, not in the cortex.
- **P27988 (approved):** AcsB, CODH/ACS subunit alpha, on `GO:0043884`. The alpha subunit
  carries the A-cluster, the acetyl-CoA synthase active site, and its EC and catalytic
  activity carry experimental evidence. This is an explicit AI adjudication under #983.
- **P07254 (approved):** chitinase A reaches `GO:0004568` through its EC-derived
  endochitinase annotation (`GO:0008843 is_a GO:0004568`). Its EC is curated without an
  inference tag; the Swiss-Prot EC rule and true-path inheritance combine here.
- **Mms6, Q6NE76 (approved):** two equally strong descendant annotations exist: IDA
  "magnetosome lumen" and EXP "magnetosome membrane". The lower GO ID (the lumen) was
  recorded. Both support the record.

## Not included, and why

147 sibling pairs on existing records remain unattached:

| Reason | Pairs |
| --- | ---: |
| GO: UniProt has no annotation to the record term or any term below it | 63 |
| GO: exact annotation with non-qualifying evidence: IEA (InterPro, ARBA, UniRule, SubCell) | 28 |
| GO: exact annotation with non-qualifying evidence: NAS | 10 |
| GO: exact annotation with non-qualifying evidence: IBA | 8 |
| GO: only descendant annotations, all non-qualifying | 16 |
| GO: non-qualifying exact and descendant annotations | 4 |
| GO: `IEA:UniProtKB-EC` without a curated EC on Swiss-Prot | 3 |
| Rhea: automatic evidence (`ECO:0000256`) | 5 |
| Rhea: no catalytic activity with the record's reaction | 3 |
| Rhea: untraceable (`ECO:0000303`) | 1 |
| Rhea: similarity (`ECO:0000250`) | 1 |
| Rejected on review (P08306, P35149) | 2 |
| Localized signature pairs needing an InterPro occurrence on a known frame (#1003) | 3 |

- **The three EC-rule rejections:**
  - P31896, whose EC is by similarity (`ECO:0000250`);
  - P00807, whose catalytic activity rests on a sequence model (`ECO:0000255`);
  - A0AAE7AGQ2, a TrEMBL entry.
- **Localized pairs.**
  - Two TrEMBL InterPro pairs need frames that the InterPro 109.0 sidecar lacks; topping
    it up from the current API would mix releases.
  - Lpp (P69776) sits in the general localized audit queue, whose source-stratified
    batches select at least 25 records per source.
- **Re-entry.** These pairs re-enter through the same audit if UniProt gains a qualifying
  fact or the maintainer widens the policy further.
- **Outside this repository.** Another 120 pairs name a trait this repository does not
  have, and 266 name a namespace it does not use.

## History

This batch was promoted once before merge (staging `cross-mech-canary-003` and
`cross-mech-examples-003`) and redone after review of #1047. That review found three
substantive problems:
- **#1048:** the EC rule did not look at the EC assignment's own evidence, so a
  by-similarity EC (P31896) and a sequence-model one (P00807) had qualified.
- **#1049:** SpoIVA rested on a mutant-phenotype annotation.
- **#1050:** the tie-break ignored evidence strength, installing IMP where IDA was
  available (uL4, uL22).

#1031 fixed the code, the batch was rebuilt from base, and the canary was re-run. That
review's documentation findings (#1051–#1054) are addressed in this record. The first
attempt's canary had already found #1037, also fixed in #1031.

## Notes

- **Re-serialized blocks.** For the 8 records that already had examples, the promoter
  re-serialized their `canonical_examples` blocks in its standard style, as batch 001
  did. A semantic comparison against the base confirms:
  - every existing example keeps its fields, values and order;
  - every non-example field is unchanged;
  - each record only gains its new examples, plus the one in-place upgrade.
- **Biophysical pilot.** It pins the entire protein registry (#1028), so the append
  required re-running `calculate-biophysical` for the same 23 proteins and options, then
  the analysis and map overlay. Only the manifest's `registry_sha256` changed.

## Validation

- **Promotion and checks:**
  - Promoter preflight, receipt verification, and installation succeeded for both batches.
  - The canary's resolution digests replayed byte-identically under the final code.
  - `just check-grounding-registries`, `just audit-writers`, `just check-go-true-path`
    (12 edges still hold in the local release), `just check-cross-mech-proteins`,
    `just check-biophysical-pilot`, and `git diff --check` all pass.
- **Scoped validation:** `just validate-all` on the 19 changed records gives 0 strict
  errors and 0 semantic findings. All 359 UniProt facts were replayed under the evidence
  policy, the EC rule, and the reviewed-flag cross-check (#1043).
- **Full validation:** `just validate-all` passed over 429,293 records with 0 strict
  errors and 0 semantic findings. The semantic phase loaded 12,634 proteins, 20,976
  evidence objects and bindings, and all 359 UniProt facts. It built the hierarchy from
  all 429,293 records plus the tracked GO edges.
- **Docs:** `just build-docs` passes: all 429,293 records were indexed in 66 browser
  shards and 740 detail buckets (largest 781.6 KiB). The landing-page consistency check
  passes.
- **Audit:** the cross-Mech audit after promotion reports 359 sibling pairs qualified on
  their exact record (281 before).
