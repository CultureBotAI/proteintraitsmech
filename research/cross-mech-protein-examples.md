---
topic: Tracking sibling-Mech protein examples and including them on the correct trait record
date: 2026-10-05
status: tracking and the UniProt fact lane implemented; inclusion runs as reviewed batches
scope: data/cross_mech, reports/cross-mech, the UniProt grounding funnel
issue: "#652"
---

# Cross-Mech protein examples

## Protein-first continuation — 2026-10-10

The coverage-priority queue was restaged without replacing the original
discovery queue or sibling snapshot. Before this batch it contained 702 proteins
on 485 records: 113 ComplexPortal, 400 Rhea and 189 GO candidates. The native selector chose
25 of the 76 ComplexPortal records, retaining all 37 alternatives in those
selected groups (`cross-mech-complex-20261010`). An ignored-inclusive search of
the grounding decision JSONL and approval TSV history found no prior decisions
for these complex-record paths. The newer live main commit
`8d03f7179457729a0d907412b16afff077b6d506` only changes the vendored CLAW pin;
this continuation preserves the dirty worktree and its existing source pins.

Independent acquisition returned all 37 exact proteins and 1,382 membership
facts at UniProt `2026_03`, with zero blocked accessions. The receipt is
`uniprot-registry-fetch-receipt:bff7517ddf7032545a89a44ac306f29b23fa8ee0d56ed944fefbde0014661429`.
All 37 passed mechanical resolution. Reading all 25 target records and checking
each membership against exact source facts yielded **36 approvals on 24 records
and one rejection**, documented in the
[structured review](../reviews/structured/20261010T203945Z-cross-mech-complex-membership/review.md)
and [authoritative YAML](../reviews/structured/20261010T203945Z-cross-mech-complex-membership/review.yaml).

ARG82/P07250 on CPX-1152 remains discovery-only for this pair. Its association
with ARG80/MCM1 and stabilizing role do not unambiguously establish membership
in the mature DNA-bound complex: the target definition preserves this caveat,
and the [primary abstract](https://doi.org/10.1046/j.1365-2958.2000.01665.x)
distinguishes those states. Broader component language in later literature was
not ignored; assembly-state ambiguity is the reason to hold promotion, not a
claim that ARG82 never interacts with the complex. The review preserves a major
deferred finding and a concrete re-review condition; no GitHub issue was opened.
The protein itself remains `LEGACY_EXAMPLES_ONLY`: its 11 older GO examples are
preserved, not requalified by this complex review.
The unabridged queue also retains five ARG82 reaction candidates: RHEA:11020,
RHEA:11856, RHEA:17717, RHEA:21292 and RHEA:32359. Their fetched exact-entry
facts carry ECO:0000269, but none was selected or scientifically approved in
this complex-only batch. Review one through the Rhea lane rather than repeatedly
reselecting the unchanged CPX-1152 choice; these evidence codes alone are not
permission to install it.

The approved scope is **complex membership**, never automatic assignment of all
complex activities to every chain. In particular, RNR4 is an assembly-supporting
component, CSG2 is regulatory, and the OTCase component is inhibited in its
epiarginase complex. Two less-obvious cases received additional primary checks:
Hsp104 in the GET4/GET5-associated assembly
([Results/Figure 2](https://doi.org/10.1016/j.molcel.2010.08.038)), and Ssc1 in
Cox1 pre-assembly, not mature complex IV
([abstract](https://doi.org/10.1128/MCB.00983-09)). Neither check establishes fixed
stoichiometry or residue interfaces. Most other supporting papers were not
reread; this is an AI database-level self-review, not human sign-off.

Native preflight passed, followed by explicitly authorized promotion of all
**36 approved examples on 24 records**, covering 36 distinct proteins (32 yeast,
four human). These records previously had no canonical examples. No rejected
candidate, legacy upgrade, definition edit or mapping-status change was installed.
The durable registries contain 12,699 ProteinReferences, 21,047 evidence objects
and matching record bindings, and 430 UniProt membership facts. Sharded integrity
checks pass. All 36 proteins have full sequences and generic annotations in the
normalized store; the [calcineurin B1 example](../data/cross_mech/README.md#annotated-sequence-example-human-calcineurin-b1)
illustrates the separation between whole-protein complex membership and generic
residue features. Both README FASTA sequences match the store and their checksums.

The regenerated inventory reports **714 qualified / 537 legacy-only / 796
discovery-only proteins**, retaining both batches' 71 approvals and 180 rejections.
It retains 11,473 not-installed discovery pairs, including reviewed rejections;
these are not all unreviewed or approvable. Sequence coverage remains 1,932 full
sequences, 1,876 with generic annotations. The sibling-named pair counts are
unchanged: this batch adds independently discovered traits for sibling proteins,
not new qualifications of the specific trait named in a sibling record.
All 71 installed pairs from the two batches have exact matching sequence frames
in the inventory. **666 proteins in the coverage-priority cohort still lack a
qualified example**: 77 ComplexPortal, 400 Rhea and 189 GO candidates, including
the held ARG82 choice. This is a priority cohort, not the entire remaining debt.

A full-store check verifies all 1,932 lengths/checksums and the bounds, release
and generic-only evidence role of 68,772 stored feature items (not deduplicated
biological features). The store deliberately preserves five existing `2026_02`
ProteinReferences; the other 1,927 sequences use `2026_03`. Those five older
references have no attached current-release generic features and retain both
release/sequence mismatch flags. A fresh discovery response does not silently
upgrade an existing reference. All 36 examples added in this batch use `2026_03`.

The focused cross-Mech/documentation/SLC10 regression run passes all 140 tests;
the writer audit, Ruff, local documentation links and all three structured review
bundles also pass. All 24 changed records pass closed-schema validation and the
full changed-record `--require-qualified` semantic gate, which loads 21,047
durable bindings and the 430-fact membership registry, with zero findings.
Exactly 36 examples were added; all other record fields and the rejected record
are unchanged. The inventory passes byte-for-byte `--check` with both review
input lanes retained, and the regenerated 23-protein biophysical pilot passes its
full bundle check. The full browser rebuild succeeds for all 429,293 records;
landing-page and SLC10 export checks pass. All 36 new examples are present in the
generated detail files with exact reference sequences and checksums, with no
display-cap omissions. The earlier batch retains its 33 visible examples and two
expected cap omissions; all 71 installed pairs are present in the uncapped
inventory. The post-build documentation/SLC10 regression run passes all 75 tests.
This is bounded validation, not a full-suite or full-corpus scientific review.

The localized backlog is now explicit. In the inspected InterPro `110.0` caches
(built 2026-09-27), A0A099LXT1/IPR040942 and A0A099LW44/IPR041208 are absent
from both flat and grouped protein maps. P69776/PF04728 has a flat 26–78 match,
but P69776 is absent from the grouped map. These observations are cache scope,
not biological absence or approved occurrences. Preserve the Lpp legacy example
and acquire/review source-asserted occurrences through the guarded workflow;
do not construct a new qualified occurrence from the flat interval alone.

## Current protein-first checkpoint — 2026-10-10

This section preserves the **first promotion checkpoint**. The continuation above
supersedes its coverage and registry totals; its review decisions remain in force.

The inventory now joins **every explicitly detected UniProt accession** to all
existing PTM examples, not only the trait named by the sibling. It includes
compound targets, graph objects and accessions embedded in prose/UniProt URLs.
Text mentions are references, never implied family members or trait evidence.
See [linked coverage](../data/cross_mech/coverage.md) and
[machine-readable inventory](../data/cross_mech/protein_inventory.jsonl).

Scope is pinned by fleet commit `249e6757595d04b5df67deafa43ea922b49fe55d`
and each sibling commit in [the manifest](../data/cross_mech/manifest.json):

| Sibling | Declared records | Records with detected proteins | Mentions |
| --- | ---: | ---: | ---: |
| AntibioticMech | 2,939 | 48 | 281 |
| CellStructureMech | 909 | 140 | 1,162 |
| DUFMech | 8,295 | 27 | 40 |
| NaturalProductMech | 3,115 | 289 | 4,216 |
| PathwayMech | 157 | 142 | 6,312 |
| TraitMech | 1,084 | 188 | 409 |
| Other six fleet siblings | 638,911 | 0 | 0 |

Total: **655,410 records, 12,420 mentions, 2,047 distinct proteins**, including
1,026 proteins in explicit example roles. No unclassified protein-bearing paths
remain under extraction version 3 / snapshot schema 2. CMMMech is included
(10 records), with no explicit recognizable accessions at this pin. These are
git-object record scans, not absence claims about ignored/uncommitted sibling
files or gene names. PTM example and identifier joins include hidden/ignored YAML.

One sibling moved during execution: CellStructureMech from `f346ba56ced970ce94afed30ec349a61b3982c17`
to `ab85e79339bef69350636de06a070cde22e0f8b9`. All four changed record blobs were
re-extracted and have identical protein mentions. The snapshot retains its original
pin; this is a bounded drift comparison, not a promise that live branches stop moving.
Subsequently HabitatMech moved to `2b6f1be181928935a95fd71146928dcce2bd89ef`;
the six changed habitat records also re-extract to identical protein mentions.
PathwayMech moved without changes to its declared record paths. Neither changes
the measured accession cohort at these checked heads.

Sequence acquisition queried all 2,047 exact accessions at UniProt `2026_03`:
1,932 active responses, 114 deleted entries and one split entry. No replacements
were substituted. The normalized store has 1,932 sequences and 1,876 with usable
generic annotations from exact-entry discovery and the matching local residue
frame. Features on uncertain/alternative frames or mismatching releases are not
grafted onto the sequence. Generic features and source-asserted qualified trait
occurrences remain separate. This work does not create residue-level causal claims.

The independent protein-first annotation pass identified 11,363 potential new
functional pairs in GO/Rhea/ComplexPortal (before merging sibling candidates).
These facts choose candidates, not approvals. One accession, `UniProtKB:A7EQI8`,
was blocked by ambiguous Rhea facts (`RHEA:17989`). The combined pre-promotion queue
has 11,544 candidates for 1,416 proteins on 4,825 records. A deterministic
coverage-first queue chooses one candidate for each of 730 proteins that lacked a
qualified example at that checkpoint: 115 ComplexPortal, 408 Rhea, 207 GO,
covering 494 records. This larger cohort remains **unadjudicated discovery**;
do not count it as scientifically reviewed or promoted.

The sibling-linked functional batch `cross-mech-refresh-20261010` independently
fetched 195 exact entries (receipt `9b0445868c861417c98505e4cf1c4d007867e6b01a99ed84600dc15e0db8592e`),
then resolved 214 alternatives on 84 records: 36 mechanically eligible, 178
ineligible. Scientific review approved 35 on 14 records and retained the prior
P08306/GO:0004129 subunit-versus-complex rejection. The 35 approvals comprise
21 localization examples and 14 enzymatic examples, all whole-protein; no
coordinate inference, mapping-status upgrade or human sign-off is implied.
The mixed candidate verdict and limits are preserved in the
[structured review](../reviews/structured/20261010T080519Z-cross-mech-refresh-examples/review.md)
and its [authoritative YAML](../reviews/structured/20261010T080519Z-cross-mech-refresh-examples/review.yaml).
The [source-stratified addendum](../reviews/structured/20261010T081233Z-cross-mech-refresh-source-strata/review.md)
records 41 full target-record reads (25 GO, all 16 Rhea) and 103 candidate-scope
assessments; it changes no decisions. All 214 finalized dispositions are also
projected into the inventory with resolution digests and explicit review-versus-
installation semantics.
Mechanical rejections in this batch used exact facts, not a new GO true-path pass.

With explicit user authorization, native promotion installed all **35 approved
examples on 14 records** (30 distinct proteins; 35 appended, no legacy upgrades).
Durable registries now contain 12,663 ProteinReferences, 21,011 evidence objects
and matching record bindings, and 394 UniProt membership facts. The sharded
registry integrity check passed. Promotion did not change source qualification
rules, infer coordinates, or install rejected candidates.

After promotion, protein-first coverage is **678 qualified / 571 legacy-only /
798 discovery-only proteins**. There are 387 qualified sibling-named pairs,
180 absent pairs and two legacy pairs on existing traits; 175 sibling trait IDs
are absent from PTM and 566 pairs use non-PTM namespaces. The combined discovery
snapshot retains 11,509 not-installed pairs, including alternatives with explicit
rejection history; this is not a count of unreviewed or approvable pairs. Of the
730-protein priority cohort, **702 still lack a qualified example**. The three
localized sibling pairs remain unresolved.

The normalized store and [Lpp sequence example](../data/cross_mech/README.md#annotated-sequence-example-e-coli-lpp)
keep source feature evidence separate from PTM qualification. The regenerated
23-protein biophysical pilot passes its complete bundle check; hydrophobic-moment
profiles have platform-level rounding changes of at most `4.44e-16`, with derived
content IDs regenerated consistently. No cohort, method, coordinates or biological
interpretation changed.

Post-install verification confirms exactly 35 additions and preservation of every
pre-existing example and non-example field. All 14 changed records pass closed
schema validation. Native semantic validation checks all 21,011 durable bindings
and replays the changed records' claims against the 394-fact membership registry,
with no new-claim or other semantic findings. The whole-record
`--require-qualified` gate reports exactly 16 pre-existing legacy examples on
GO:0031021 and GO:0034515; they were not upgraded or hidden. The bounded projection
of all 35 new examples passes `require_qualified=True` with zero findings.

The final inventory rebuild passes byte-for-byte `--check` with all input lanes
and review history retained. 140 focused inventory/extraction/documentation/SLC10 tests pass,
both saved structured reviews validate, Ruff and `git diff --check` pass, and the
writer audit accepts all 610 scripts. The broad suite was interrupted after
3,390 passes, 28 skips and one failure: the new skill was initially absent from
the `CLAUDE.md` router. That registration was fixed and its test passes in the
focused rerun. This is **not a full-suite pass**. Browser artifacts were rebuilt
for all 429,293 records using the project virtual environment (the system Python
lacked PyYAML); landing-page and SLC10 export checks pass.
The first post-build documentation/SLC10 regression run passed 72 tests; the
140-test run also includes the subsequent display-ranking regressions below.

A final generated-output spot check found that the browser's source-only rank
placed `UNIPROT_GROUNDING` after legacy profile suggestions, hiding the five new
examples on GO:0031021 and GO:0034515. The maintained browser builder now ranks
qualified examples first, retaining the existing source order within each
qualification stratum and the five-example display cap. The uncapped inventory
still contains every installed example; no qualification status is changed by
display ranking. Regression tests cover the mixed legacy/qualified case,
unchanged legacy ordering and the stable five-example cap.
The corrected full browser rebuild succeeds. Its generated detail contains 33
of this batch's new examples with exact reference sequences/checksums; the two
expected cap omissions are Q9Y8G3/GO:0140602 and B0R753/RHEA:32239. All 35 are
verified present in the uncapped inventory. Landing-page and SLC10 checks pass.
The final post-rebuild documentation/SLC10 test run passes all 75 tests.

Remaining work is visible, not silently qualified: review the larger independent
cohort through the ordinary selector/fetch/resolve pipeline, retain prior
rejection dispositions, resolve the three localized sibling pairs through
source-asserted coordinates, and resolve non-UniProt gene/protein identifiers
separately. "All" here is all recognized accessions in the declared pinned scope.
The reusable [cross-Mech protein skill](../.claude/skills/proteintraitsmech-cross-mech-proteins/SKILL.md)
owns refresh, provenance, sequences, coverage priorities and guarded promotion.

## Question

Sibling Mechs curate proteins too. Which of those proteins are tied, by the sibling,
to a trait that ProteinTraitsMech defines, and how do they get onto *that* trait
record without weakening the fail-closed grounding contract?

Issue #652 measured the gap once (2026-09-06, 127 sibling proteins absent here) and
proposed a candidate source for the funnel. It did not say which trait each protein
belongs to, and its count went stale as the fleet changed: two Mechs it never saw
(NaturalProductMech, PathwayMech) now carry most of the protein-to-trait links.

## Strategy in one paragraph

Keep a **tracked, commit-pinned snapshot** of every UniProt protein mention in the
sibling Mechs' records (`data/cross_mech/`), classified by declared extraction rules
that also capture the sibling CURIE naming the protein's trait. **Audit** it against
`data/traits` to give each (protein, trait) pair exactly one status. Treat every
sibling assertion as **discovery only**: a pair is included only when a release-pinned
UniProt exact-accession fact independently asserts the same exact trait, and only
through the existing select → fetch → resolve → review → promote funnel. Refresh the
snapshot on purpose. CI reports drift against the live siblings as a notice, so a
stale snapshot or a new protein-bearing sibling field is visible, not silent.

## Layer 1 — snapshot (what the siblings say)

`just scan-cross-mech-proteins [--fetch] --apply` writes
`data/cross_mech/protein_mentions.jsonl` (one canonical-JSON row per mention, sorted)
and `data/cross_mech/manifest.json`.

- **Fleet membership** comes from claw's canonical manifest
  (`CultureBotAI/culturebotai-claw:src/kg_microbe_fleet/fleet.yaml`), pinned by commit
  and SHA-256; each Mech's `record_globs` decide which files are records. This
  repository never re-declares the fleet.
- **Sibling bytes** are read from git objects at `origin/main`, never from a working
  tree (CultureMech's checkout sat on a feature branch when this was written). Each
  checkout's `origin` must be the manifest's repository or the scan refuses it. Every
  Mech's resolved commit is pinned in the manifest.
- **Detection**: a value is a protein when it is `UniProtKB:`/`UniProt:`-prefixed, or
  a bare accession under a key that says so (`uniprot_id`, `protein_accession`, ...).
  A byte prefilter skips records that cannot contain one (TaxonMech alone has 625,960
  records and no proteins).
- **Channels**: one declared rule per protein-bearing path assigns a role (EXAMPLE,
  GRAPH_NODE, TARGET, SUBSTRATE, REFERENCE, CROSSWALK), a relation, and where the
  trait CURIE is read. A path no rule knows is kept as **UNCLASSIFIED** and reported
  by `check`, so sibling schema growth surfaces as drift. Today there are none.
- **Qualifiers**: a channel can copy declared keys that hedge a claim onto each
  annotation. NaturalProductMech's `proposed` ("inferred rather than demonstrated") is
  one; the audit carries qualifiers to every pair and counts the pairs whose every
  supporting claim is only a proposal, so a reviewer never mistakes a restated
  prediction for independent support.

The channels that carry a trait:

| Sibling | Path | Trait CURIE read from | Relation |
| --- | --- | --- | --- |
| NaturalProductMech | `/biosynthetic_pathway/[]/enzyme_id` | same step's `reaction_id` (Rhea) | catalyzes |
| PathwayMech | `/mechanistic_edges/[]/subject` | edge `object` when `predicate: catalyzes` | catalyzes |
| PathwayMech | `/participants/[]/id` | record `id` (pathway) | participates_in_pathway |
| TraitMech | `/causal_graphs/[]/nodes/[]/protein_examples/[]/uniprot_id` | node `grounding` | exemplifies_node_grounding |
| CellStructureMech | `/components/[]/protein_examples/[]/uniprot_id` | component `grounding`; record `identifier` (GO CC) | exemplifies_component_grounding; component_of_structure |
| CellStructureMech | `/complex_compositions/[]/participants/[]/participant_id` | composition `source_accession` (ComplexPortal); record `identifier` | component_of_complex; component_of_structure |
| CellStructure/AntibioticMech | `/causal_graphs/[]/nodes/[]/xrefs/[]` | the node's other xrefs / `grounding` | node_xref |
| AntibioticMech | `/resistance_mechanisms/[]/protein_accession` | `aro_id`, `phenotype_id` | resistance_* |

Compound targets (`target_enzyme`, `molecular_targets`), substrates, evidence citations,
and identifier crosswalks are tracked but declare no trait: a compound's target says
nothing about the protein's own traits.

## Layer 2 — audit (how this repository reads it)

`just audit-cross-mech-proteins` writes `reports/cross-mech/{pairs.tsv,pairs.jsonl,summary.md}`.

- Every declared (protein, trait CURIE) pair is resolved to an **exact record
  identifier**. A Rhea directional ID is mapped to its master reaction only through
  `data/raw/rhea/rhea-directions.tsv`, pinned to the same release-141 SHA-256 the
  Rhea grounding stage pins (a test keeps the two pins equal); if that file is absent,
  master IDs still resolve and directional ones are reported as unchecked. There is
  no hierarchy or equivalence inference at this layer.
- Statuses: `QUALIFIED_ON_TRAIT`, `LEGACY_ON_TRAIT` (present but unproven),
  `ABSENT_FROM_TRAIT` (record exists, protein missing), `TRAIT_NOT_IN_PTM` (namespace
  used here, identifier not), `NOT_A_PTM_NAMESPACE`.
- The identifier index is the committed tree plus every working-tree difference, so a
  promotion in progress is seen without scanning 2 GB of YAML.

### Measurement, 2026-10-05

Snapshot fleet manifest `ad3862e7a5b`; sibling commits are in
`data/cross_mech/manifest.json`. Re-run the audit rather than quoting these numbers
later.

| Mech | Records scanned | With proteins | Mentions |
| --- | ---: | ---: | ---: |
| AntibioticMech | 2,939 | 47 | 278 |
| CellStructureMech | 892 | 116 | 723 |
| NaturalProductMech | 3,115 | 250 | 1,096 |
| PathwayMech | 152 | 5 | 123 |
| TraitMech | 1,011 | 128 | 143 |
| CommunityMech, CultureMech, HabitatMech, MediaIngredientMech, TaxonMech | 638,899 | 0 | 0 |

2,363 mentions name 1,027 distinct proteins. 892 (protein, trait) pairs are declared:

| Status | Pairs |
| --- | ---: |
| ABSENT_FROM_TRAIT | 475 |
| LEGACY_ON_TRAIT | 31 |
| QUALIFIED_ON_TRAIT | 0 |
| TRAIT_NOT_IN_PTM | 120 |
| NOT_A_PTM_NAMESPACE | 266 |

The 506 absent-or-legacy pairs cover 406 proteins on 216 records: 270
`FUNC_LOCALIZATION` (GO cellular component), 112 `FUNC_INTERACTION_PARTNER`
(ComplexPortal), 96 `FUNC_ENZYMATIC_ACTIVITY` (Rhea), 24 `FUNC_MOLECULAR_FUNCTION`
(GO), 3 `SEQ_DOMAIN` and 1 `FUNC_PROTEIN_FAMILY`.

`TRAIT_NOT_IN_PTM` is mostly by design: all 84 distinct InterPro IDs among them are
InterPro `Family` entries, which `seed_interpro.py` excludes by default. The other 17
are 15 *M. tuberculosis* (`R-MTU`) Reactome pathway and reaction IDs (this repository
carries only `R-HSA` pathways) and two GO identifiers absent here (`GO:0004085` and the
provisional-range `GO:7770085`). `NOT_A_PTM_NAMESPACE` is
PHI-base phenotypes, WikiPathways steps, MetaCyc, and CellStructureMech's own minted
structure IDs.

## Layer 3 — inclusion (not by this snapshot)

**A sibling assertion is never qualification evidence.** CellStructureMech states it in
its own records: a component's protein example is "the single reviewed UniProtKB entry
for gene X in a taxon this record names ... it is not itself evidence that the protein
is part of this structure." The plan's completion rule also requires that an included
example be exact, release-pinned, and replayable. So each absent or legacy pair is a
**candidate**, and qualifies only when UniProt itself asserts the same exact trait in a
release-pinned exact-accession response:

| Namespace | Route | UniProt fact |
| --- | --- | --- |
| GO | `SOURCE_ANNOTATION`, provider `UNIPROT` | `uniProtKBCrossReferences` GO entry with the exact ID; evidence code retained |
| RHEA | `SOURCE_MEMBERSHIP`, provider `UNIPROT` | catalytic-activity `reactionCrossReferences` with the exact master Rhea ID |
| ComplexPortal | `SOURCE_MEMBERSHIP`, provider `UNIPROT` | `ComplexPortal` cross-reference with the exact `CPX-n` |
| Pfam, InterPro, NCBIfam, ... | `INTERPRO_MATCH` (localized) or existing `SOURCE_MEMBERSHIP` (whole-protein records) | existing routes |

An exploratory exact-accession probe during design (UniProt `2026_03`; not retained and
not evidence) suggested that most Rhea, ComplexPortal, and GO molecular-function pairs
are confirmed and that about half of the GO localization pairs are not, mostly because
UniProt annotates a different or more specific term. The reproducible result is the
inclusion batch's own record, which supersedes it.

### The UniProt fact lane

The validator used to admit ComplexPortal and Rhea evidence only from their own
`SOURCE_DATABASE` providers, each behind an unconditional receipt lock. The UniProt
membership snapshot captured only signature cross-references, and the promoter could
not resolve `SOURCE_ANNOTATION`. The lane now exists (grounding plan, 2026-10-05):

- the snapshot captures `ComplexPortal` and `GO` cross-references and catalytic-activity
  Rhea reactions, and the registry fetch requests `go_id`, `xref_complexportal`, and
  `cc_catalytic_activity` (the REST field `xref_go` does not exist);
- GO facts support only `SOURCE_ANNOTATION`, every other fact only `SOURCE_MEMBERSHIP`;
- ComplexPortal and Rhea gain a UniProt lane beside their source-native lanes, which keep
  their receipt locks. The promoter installs a ComplexPortal, Rhea, or GO fact only after
  verifying the batch's network UniProt fetch receipt binds the exact membership bytes it
  installs from. Accepting this is a change to the central evidence contract and is the
  maintainer's call at merge.
- Capturing a fact is not qualifying it. The resolver and the validator share one
  default-deny evidence policy, because the plan keeps "EC-only, textual, homology-only,
  or generic pathway inference" as candidate evidence. A GO fact qualifies only with an
  experimental code (EXP, IDA, IPI, IMP, IGI, IEP, and the HT variants) or a curator code
  (IC, TAS). IEA, IBA, the ISS family, NAS, and RCA stay candidates. A catalytic activity
  qualifies only with experimental (`ECO:0000269`), curator-inference (`ECO:0000305`), or
  traceable author-statement (`ECO:0000304`) evidence. The stored Rhea fact keeps the
  reaction's evidence list so this stays auditable. A catalytic activity scoped to an
  isoform or chain is never a whole-protein fact.
- One narrow widening, the maintainer's decision on #1004: on a reviewed Swiss-Prot entry,
  a GO term inferred from the entry's curated EC number (`IEA:UniProtKB-EC`) and a
  catalytic activity curated with no evidence tag also qualify. Neither qualifies on
  TrEMBL. Every other IEA source (InterPro2GO, ARBA, UniRule, SubCell), IBA, NAS, curated
  similarity (`ECO:0000250`), automatic (`ECO:0000256`), and untraceable author statements
  (`ECO:0000303`) stay candidates. The EC number must itself be curated (#1048): every
  evidence code on the entry's EC assignments, in its protein names and catalytic
  activities, must be absent or experimental/curator (`ECO:0000269`, `0000304`,
  `0000305`), so a GO term derived from a by-similarity or sequence-model EC stays a
  candidate. The fact row records `uniprot_entry_type`, and for an EC-derived GO term
  `uniprot_ec_evidence`, only where this rule decides it, so every earlier fact keeps its
  content address.
- GO true-path inheritance (#1002). When a GO record's own term has no exact qualifying
  fact, the resolver looks for one of the protein's qualifying GO facts whose term reaches
  the record's term by `is_a` or `part_of` within one GO namespace in the local
  `go-basic.obo`. The strongest evidence wins (direct experimental, then mutant
  phenotype or expression, then curator, then the EC rule; #1050), then the shortest
  path, then the lowest GO ID. The occurrence records
  the descendant as `source_trait_id` with an explicit `inheritance_path`; the review
  TSV shows both, and review samples every such row (`ANCESTOR_INHERITANCE`). The
  promoter proves each edge in that release and installs it, with the release that proved
  it, in `data/grounding/go_true_path_edges.jsonl`, which the validator replays without
  the OBO file. The GO release itself is not pinned (#1039): a tracked edge stays valid
  while a later release keeps it, and `just check-go-true-path` reports any tracked edge
  the local release no longer has. An annotation to a less specific term never supports
  a more specific record.

The sequence, in order:

```bash
just audit-cross-mech-proteins                      # statuses -> reports/cross-mech/
just discover-cross-mech-sequences --apply          # exact sequence identity, pinned release
just stage-cross-mech-candidates --apply            # the funnel queue
just select-cross-mech-review-batch <id> --apply    # a bounded batch
```

The ordinary fetch, resolve, review, and promote recipes do the rest.

## Decisions for the maintainer

- Keep the UniProt exact-accession lane for Rhea and ComplexPortal traits, or wait for
  their source-native acquisition receipts.
- Any further widening of the evidence policy beyond the narrow Swiss-Prot rule above
  (decided on #1004), for example curated "by similarity" (`ECO:0000250`) catalytic
  activities. A sibling claim never counts toward qualification, so any widening has to
  stand on UniProt's evidence alone.
- InterPro `Family` groundings used by TraitMech and CellStructureMech: map through the
  family's member signatures, or leave them `TRAIT_NOT_IN_PTM`.

## Keeping it current

- CI runs `just check-cross-mech-proteins --remote`. Snapshot integrity (bytes, sort
  order, per-row classification under the current rules, per-Mech counts) and rule
  currency fail the job.
- `--remote` adds notices only: every pinned commit against the live default branch, and
  the pinned fleet manifest against the live one (a new Mech or changed globs). An
  unreachable network, a timeout, or an HTTP error is reported as `UNAVAILABLE`.
- `--local` compares sibling checkouts and separates `STALE` (record files changed)
  from `MOVED_RECORDS_UNCHANGED`.
- Refresh with `just scan-cross-mech-proteins --fetch --apply` before each cross-Mech
  grounding batch, or when the notice reports `STALE`, and commit the diff: the git
  history of `data/cross_mech/` is the history of what the siblings claimed.
- After a rules change, `just scan-cross-mech-proteins --at-manifest
  data/cross_mech/manifest.json --apply` re-derives the snapshot at the same pinned
  sibling and fleet commits, so the diff shows only what the rules changed.

## Fleet observations

- On 2026-10-05, DUFMech was not yet in the fleet manifest. It is included in the
  2026-10-10 checkpoint above; this historical exclusion no longer applies.
- On 2026-10-05, DUFMech and PathwayMech work trees were running their own cross-Mech
  protein scans. One fleet-level extractor (claw), consumed by each Mech for its own
  inclusion question, would avoid three diverging rule sets.
