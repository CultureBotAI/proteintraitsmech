# Cross-Mech examples, batch 001: review and promotion record

- Date: 2026-10-05. UniProt release `2026_03`. Reviewer: `claude` (AI review, not curator
  sign-off; no `mapping_status` or definition changed).
- Follow-up audit: `codex`, 2026-10-05, against base `fe2e7d947e6` and the batch-002
  data installed in `14a8a423648`. This checked the record diff, decisions, evidence,
  registries, and both acquisition receipts; it is also AI review.
- Inputs: the cross-Mech snapshot in `data/cross_mech/` (fleet manifest `ad3862e7a5b`,
  sibling commits in its `manifest.json`) and the audit described in
  [cross-Mech protein examples](cross-mech-protein-examples.md).
- Route: the UniProt exact-accession fact lane under its default-deny evidence policy and
  promote-time receipt gate (grounding plan, 2026-10-05). A sibling claim chose each
  candidate; only an exact UniProt fact with qualifying evidence qualified it.
- Staging batches, run in order through the ordinary recipes: `cross-mech-canary-002`
  (shard 0 of 40) and `cross-mech-examples-002` (everything left). Fetch receipts
  `uniprot-registry-fetch-receipt:7c9b1443…75cd` and `…:d19465ab…1dc7`, both network
  `UNIPROT_REST` acquisitions verified by the promoter. The `-001` staging batches were a
  first attempt superseded before merge (see "History"). Staging files are local and
  ignored; the durable registries and trait records are the installed claims.

## Result

281 sibling-asserted (protein, trait) pairs are now `QUALIFIED` canonical examples on
133 existing trait records, each a whole-protein occurrence backed by an exact UniProt
fact admitted by the lane's evidence policy. Of these, 253 examples were appended and
28 existing legacy examples were upgraded in place:

| Trait category | Examples | UniProt fact and evidence |
| --- | ---: | --- |
| `FUNC_INTERACTION_PARTNER` (ComplexPortal) | 112 | ComplexPortal cross-reference (curated resource) |
| `FUNC_LOCALIZATION` (GO cellular component) | 83 | GO cross-reference: IDA, IPI, EXP, or IMP |
| `FUNC_ENZYMATIC_ACTIVITY` (Rhea) | 80 | catalytic activity, all `ECO:0000269` (experimental) |
| `FUNC_MOLECULAR_FUNCTION` (GO) | 5 | GO cross-reference: IDA, IPI, EXP, or IMP |
| `FUNC_PROTEIN_FAMILY` (NCBIfam) | 1 | NCBIfam cross-reference |

GO evidence over the 88 GO examples: IDA 57, IPI 20, EXP 7, IMP 4. All 281 examples are
Swiss-Prot entries, 252 proteins in all. The claims came from CellStructureMech (195),
NaturalProductMech (79), TraitMech (6), and PathwayMech (1).

Durable state after promotion: 12,611 ProteinReferences
(`5641b424c67edb97d7d7725d14e87b85df2e446151b55272f10185c2ff473c64`), 20,898 evidence rows
and bindings (logical SHA-256 `255a493d605456bfae8967a070fe07584fe550b83295f9651ee303e6ec11617a`
and `6c0a11bd6fcb0ba08f3cb3f00388456c3cfc628bd9382268f36609a9837608ca`), and the first durable
`uniprot_memberships.jsonl`: 281 facts
(`7817f29d8cf08a5f349449b6ae50e63ea5e5fc80dd66da1b3deeffc54f3b63c3`).
The batch adds 149 ProteinReferences and 281 evidence/binding rows. Every previously
installed registry row is unchanged.

## Review decisions

Every row was decided. The resolver rejects a row without an exact UniProt fact for the
record's own identifier, and a row whose fact fails the evidence policy. For every other
row the review checked agreement between the record and the protein. That check was done
on grouped listings by record and namespace, with notes templated from the row's facts,
not individual written reasoning per row. The checks were:

- GO: the term's aspect matches the record category (no mismatches), and complex or
  organelle terms are carried by their components (for example carboxysome shell
  proteins, NarGHI subunits, MacAB-TolC, flagellar parts).
- Rhea: the enzyme catalyses the record's equation.
- No record gained two examples with the same sequence, and no TrEMBL entry was approved.

**ComplexPortal adjudication (#983).** These 19 records are classified as
`FUNC_INTERACTION_PARTNER`. Their definitions describe the complexes, including their
collective functions. Each of the 112 approved proteins has an exact UniProt
ComplexPortal cross-reference and appears in the record's `biolink:has_part` component
list. Its `SOURCE_MEMBERSHIP` occurrence asserts membership in that complex; it does not
assert that the individual subunit performs all of the complex's activities. Acceptance
of this UniProt membership route alongside the source-native route remains a maintainer
decision on #971. The rejected P08306/GO:0004129 activity claim is separate from this
membership adjudication.

**GO molecular-function adjudication (#983).** The five retained activity examples are:

| Protein | Trait | Pinned UniProt evidence | Adjudication |
| --- | --- | --- | --- |
| P06278, alpha-amylase | GO:0004556 | IDA:CACAO, PMID:2540150 | Retain the exact experimental alpha-amylase annotation. |
| P09373, formate acetyltransferase 1 | GO:0008861 | IDA:EcoCyc, PMID:4615902 | Retain the exact experimental formate C-acetyltransferase annotation. |
| Q04507, ammonia monooxygenase alpha subunit | GO:0018597 | EXP:UniProtKB, PMID:19453274 | Retain as the annotated AmoA subunit in the active assembled enzyme, with the limitation below. |
| Q9S1E5, NrfA/cytochrome c-552 | GO:0042279 | EXP:UniProtKB, PMID:18201106 | Retain the catalytic nitrite-reductase protein; its cytochrome label does not make it merely an electron-transfer partner. |
| Q8GBW6, methylmalonyl-CoA carboxyltransferase 12S subunit | GO:0047154 | EXP:UniProtKB, PMID:8366018 | Retain the experimentally active 12S catalytic component, with the limitation below. |

The Q04507 reference measures an active multi-subunit AMO preparation, rather than
isolated AmoA ([Gilch et al., 2009](https://pubmed.ncbi.nlm.nih.gov/19453274/)). The Q8GBW6
reference shows that recombinant 12S catalyses one partial reaction of the complete
transcarboxylase reaction ([Thornton et al., 1993](https://pubmed.ncbi.nlm.nih.gov/8366018/)).
The Q9S1E5 functional assignment also agrees with the source's description of NrfA as
the nitrite-reducing protein ([UniProt Q9S1E5](https://www.uniprot.org/uniprotkb/Q9S1E5/entry)).
Thus the two subunit rows preserve exact experimental UniProt annotations in their
assembled-enzyme context; they do not establish that an isolated subunit catalyses the
record's entire equation. This is an explicit AI adjudication under the plan's
multi-protein exception, requiring maintainer acceptance at merge. The durable schema
does not encode a separate subunit-contribution qualifier. These contextual readings
must remain visible in review; if single-protein sufficiency is required, those two
rows need a fresh reviewed promotion without them.

222 pairs were rejected:

| Reason | GO localization | GO molecular function | Rhea |
| --- | ---: | ---: | ---: |
| No exact UniProt fact for the record identifier | 138 | 4 | 3 |
| Electronic `IEA` | 24 | 15 | — |
| Phylogenetic `IBA` | 15 | — | — |
| Untraceable `NAS` | 10 | — | — |
| No evidence on the catalytic activity | — | — | 6 |
| Automatic `ECO:0000256` (ARBA/UniRule) | — | — | 5 |
| Curated similarity `ECO:0000250` | — | — | 1 |
| Untraceable author statement `ECO:0000303` | — | — | 1 |

All of the earlier concerns fall under the evidence policy:

- The automatic-only Rhea facts are rejected: A6N339 (#980) and the agrobactin enzymes
  and Q2UA48, whose sibling steps are `proposed`.
- The EC-only, InterPro2GO, and phylogenetic GO annotations are rejected (#981).
- The duplicate cytoophidium pair (#982) and the cytochrome c oxidase subunit II example
  (#983) are rejected.
- The four proposed-step examples with stronger UniProt evidence went two ways. GsfA and
  GsfD (`ECO:0000269`) qualify. PhlD (`ECO:0000250`) and EctC (no evidence tag) do not.

## Not included, and why

- 3 localized signature pairs (two InterPro, one Pfam) need an InterPro occurrence on a
  known sequence frame; they wait in the `cross-mech-needs-occurrence` batch label. Lpp
  (P69776, `Pfam:PF04728`) is in the existing audit queue with an InterPro frame match;
  the two TraitMech InterPro pairs need a frame top-up for their proteins.
- 120 pairs name a trait this repository does not have: 93 pairs over 84 distinct InterPro
  `Family` IDs, 24 pairs over 15 *M. tuberculosis* Reactome IDs, and 3 pairs over 2 GO
  IDs. Another 266 pairs name a namespace it does not use.
- The 222 rejected pairs above re-enter through the same audit if UniProt gains an exact
  fact with qualifying evidence, if GO true-path inheritance is added, or if the
  maintainer widens the policy.
- Accounting: 281 approved + 222 rejected + 3 localized = the 506 candidate pairs.
  The two staging review ledgers contain 507 rows: 281 approved and 226 rejected. Four
  rejected pairs occur in both batches; all pair counts above deduplicate those repeats.
- Follow-ups already filed: GO inheritance (#1002), the two InterPro frame top-ups
  (#1003), and possible evidence-policy changes (#1004). P19787/RHEA:23196 is a separate
  follow-up candidate identified in #980; it is not installed by this batch.

## History

A first attempt (`cross-mech-canary-001`, `cross-mech-examples-001`) qualified 354
examples. It admitted IEA, IBA, and NAS GO annotations and automatic catalytic
activities. Its canary also found four lane defects, all fixed before any durable write.
Reviews #973-#984 showed those admissions contradicted the plan, which keeps "EC-only,
textual, homology-only, or generic pathway inference" as candidate evidence. That attempt
was rolled back unmerged. The lane gained the evidence policy and the receipt gate, and
the batch was redone from a fresh canary.

## Notes

- For the 20 records that already had examples, the promoter re-serialized their
  `canonical_examples` blocks in its standard style (indentation, quoting, line folding),
  as earlier promotions did. All 87 existing examples retain their original fields and
  order. Of these, 28 gain qualification and occurrence fields, while 59 remain unchanged
  legacy examples. The other 253 qualified examples are appended. This is more than a
  formatting change for the 28 upgrades.
- The biophysical pilot pins the entire protein registry, so this append requires a
  refresh through `calculate-biophysical` and the dependent overlay/analysis generators.
  The 23 selected proteins and calculator options are unchanged. Replaying on this
  machine changes only floating-point roundoff in 23 B10 profiles and their content
  hashes; all 276 observations agree within the publication gate's `1e-10` tolerance.

## Validation

- Promoter preflight, receipt verification, and installation for both batches.
  `just check-grounding-registries` OK; `just audit-writers` OK.
- Scoped `validate-strict` and `validate-uniprot-grounding` on the 133 records: 0 errors and
  0 findings, all 281 UniProt facts replayed under the evidence policy.
- Full `just validate-all` completed successfully on the batch-002 data: 429,293 records,
  0 strict errors, and 0 semantic findings. The semantic phase loaded 12,611 proteins,
  20,898 evidence objects/bindings, and all 281 UniProt facts. The local run log is
  `validate_all_C2.log` in the session scratchpad; subsequent changes touch only this
  record, the plan, and the derived biophysical publication bundle.
- The follow-up audit verified both fetch receipts against their request plans and
  checked every installed fact against the receipt-bound staging output and approved
  decision. It also confirmed unchanged definitions/statuses, preservation of existing
  example fields/order, no duplicate sequence hashes per changed record, and exact GO
  aspect/category agreement. All 80 Rhea facts carry `ECO:0000269`; all 88 GO facts use
  IDA, IPI, EXP, or IMP.
- Focused receipt, membership-policy, documentation-consistency, and biophysical-pilot
  tests: 172 passed.
- Fresh semantic replay of the 133 changed records: 0 findings. With
  `--require-qualified`, it reports 59 `legacy_unverified_example` findings, all
  individually compared with the base and confirmed unchanged. Every batch-002 example
  is qualified; the migration-completion check is not globally clean on those records.
- `just check-biophysical-pilot` passes after regenerating the publication bundle.
  `just check-grounding-registries`, `just audit-writers`,
  `just check-cross-mech-proteins`, and `git diff --check` pass. The snapshot check is
  offline integrity validation; it does not check current sibling-branch drift.
- `just build-docs` passes: all 429,293 records were indexed in 66 browser shards and
  733 detail buckets (largest 826.1 KiB). The landing-page consistency check passes.
