---
topic: Tracking sibling-Mech protein examples and including them on the correct trait record
date: 2026-10-05
status: tracking implemented; inclusion route pending (see "Inclusion")
scope: data/cross_mech, reports/cross-mech, the UniProt grounding funnel
issue: "#652"
---

# Cross-Mech protein examples

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

An exploratory exact-accession probe (UniProt `2026_03`; not durable evidence — the
funnel's fetch stage re-acquires everything under its own receipt) confirmed **361 of
the 506**: Rhea 93/96, ComplexPortal 112/112, GO localization 132/270, GO molecular
function 20/24, and all four signature pairs. Most unconfirmed localization pairs are
proteins UniProt annotates to a different or more specific GO term.

### What blocks inclusion today

1. `scripts/validate_uniprot_grounding.py` admits ComplexPortal and Rhea evidence only
   from their own `SOURCE_DATABASE` providers, with an unconditional receipt lock on
   each. A UniProt lane for them is a change to the central evidence contract, which
   the plan's priority list anticipates ("Rhea: exact Rhea-to-UniProt **or UniProt
   catalytic-activity annotation**"; "GO: direct GOA/UniProt annotation, retaining the
   evidence code"). It must keep the existing locks for the source-native lanes.
2. The UniProt membership snapshot captures only signature cross-references, and the
   registry fetch does not request GO (`go_id`), catalytic activity
   (`cc_catalytic_activity`), or `xref_complexportal`. The REST field `xref_go` does not
   exist.
3. The promoter resolves `SOURCE_MEMBERSHIP` but not `SOURCE_ANNOTATION`.

These are the next pull request. A promotion batch built from the audit's candidates
follows it, through the ordinary review and authorization steps.

## Decisions for the maintainer

- Accept a UniProt exact-accession lane for Rhea and ComplexPortal traits, or wait for
  their source-native acquisition receipts.
- GO evidence codes: admit electronic (`IEA`) annotations when a sibling independently
  asserts the same term, or require experimental/curated codes.
- GO true-path inheritance for the unconfirmed localization pairs (UniProt annotates a
  descendant term): an explicit `inheritance_path` is supported for signatures but not
  yet for GO.
- InterPro `Family` groundings used by TraitMech and CellStructureMech: map through the
  family's member signatures, or leave them `TRAIT_NOT_IN_PTM`.

## Keeping it current

- `just check-cross-mech-proteins` (CI, offline) verifies the snapshot's integrity and
  that its channel rules are the current ones.
- `--remote` (CI notice) compares every pinned commit with the live default branch and
  the pinned fleet manifest with the live one (a new Mech or changed globs is reported).
- `--local` compares sibling checkouts and separates `STALE` (record files changed)
  from `MOVED_RECORDS_UNCHANGED`.
- Refresh with `just scan-cross-mech-proteins --fetch --apply` before each cross-Mech
  grounding batch, or when the notice reports `STALE`, and commit the diff: the git
  history of `data/cross_mech/` is the history of what the siblings claimed.

## Fleet observations

- DUFMech is not in the fleet manifest and has no YAML records yet; it enters the
  scan when it is onboarded there.
- On 2026-10-05, DUFMech and PathwayMech work trees were running their own cross-Mech
  protein scans. One fleet-level extractor (claw), consumed by each Mech for its own
  inclusion question, would avoid three diverging rule sets.
