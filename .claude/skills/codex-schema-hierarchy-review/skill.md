---
name: codex-schema-hierarchy-review
description: Run a Codex review of the ProteinTraitsMech schema, protein-trait concepts/representations, and existing trait relationships — and have it propose a single hierarchy/taxonomy for the trait space with Biolink-Model-typed edges (RO for gaps). Trigger when asked to review the schema / trait concepts / trait hierarchy, or to propose a trait taxonomy, or "run the codex schema review".
---

# Codex schema & trait-hierarchy review

Hands the review below to **Codex** (via the `codex:codex-rescue` agent, or a
codex plugin) as a read-only analysis, and saves the report under `research/`.

## How to run

1. Launch the `codex:codex-rescue` agent with the **prompt** below verbatim.
2. Tell it to write its report to
   `research/schema-hierarchy-review-<N>.md` (increment N per run; never
   overwrite a prior review).
3. It is read-only: Codex must not edit the schema, run seeders, or modify data
   — it proposes and reports.

## Edge-typing policy (important)

Trait↔trait and trait↔entity relationships are typed with the **Biolink Model
first**, exactly as [KG-Microbe](file:///Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/kg-microbe)
does. The Biolink Model is downloaded there:

```
/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/kg-microbe/data/raw/biolink-model.yaml
```

KG-Microbe's predicate usage (the precedent to mirror): `biolink:subclass_of`
(dominant), `biolink:member_of`, `biolink:part_of` / `has_part`,
`biolink:participates_in`, `biolink:has_participant` / `has_input` /
`has_output`, `biolink:capable_of`, `biolink:enables` / `enabled_by`,
`biolink:located_in`, `biolink:consumes` / `produces`, `biolink:orthologous_to`,
`biolink:interacts_with`, `biolink:related_to`. **Use a `RO:` predicate only
where the Biolink Model has no suitable slot**, and say so explicitly when you
do.

---

## Prompt

You are reviewing **ProteinTraitsMech**, a LinkML-governed knowledge base of
**protein sequence / structure / function traits** — a corpus of ~200,600 YAML
files (one `ProteinTraitRecord` each) under `data/traits/`. It is a catalogue of
trait **classes**, not per-protein annotations.

### Your task
Critically review (1) the schema and how protein-trait **concepts** are
represented, (2) how **relationships / hierarchy** among traits are modelled and
whether they are consistent, then (3) **propose a single hierarchy / taxonomy**
covering the whole trait space, with every edge typed by a **Biolink Model
predicate** (RO only for gaps). The proposed hierarchy need not be perfect —
**explicitly report oddities, tensions, and uncertainties.**

Read-only: do not edit files, run seeders, or modify the schema. Cite concrete
paths / record identifiers for every claim. Ground **node** alignments in
standard ontologies (SO, GO, PATO, EDAM, ChEBI); type **edges** with Biolink
(RO fallback) — see the edge-typing policy above.

### Read first
- `src/proteintraitsmech/schema/proteintraitsmech.yaml` — the authoritative
  LinkML schema. Focus on `ProteinTraitRecord` (~L104) and its slots
  `trait_axis`, `trait_category`, `term_kind`, `parent_traits` (~L149, typed
  `rdfs:subClassOf`), `xrefs` vs `mapped_xrefs` (`MappedXref`),
  `chemical_participants` (`ChemicalParticipant`), `canonical_examples`,
  `causal_graphs`; `TraitAxisEnum` (~L706, the 5 axes SEQUENCE / STRUCTURE /
  SEQUENCE_STRUCTURE / FUNCTION / EVOLUTION); `ProteinTraitCategoryEnum` (~L739,
  prefix-coded `SEQ_ / STRUCT_ / MIXED_ / FUNC_ / EVO_`); `TermKindEnum`,
  `CausalEdge` (its `predicate` / `predicate_id`).
- The **Biolink Model** at
  `/Users/marcin/Documents/VIMSS/ontology/KG-Hub/KG-Microbe/kg-microbe/data/raw/biolink-model.yaml`
  — the predicate hierarchy under `related to` (`subclass of`, `member of`,
  `part of`, `has participant`, `capable of`, `located in`, …). Skim
  KG-Microbe's `kg_microbe/` for how predicates are applied.
- `CLAUDE.md`, `README.md` (FT-type → category map + seeds table),
  `download.yaml` (per-source declared `trait_categories`),
  `scripts/build_docs_index.py` `infer_source()`.
- A **representative sample of records per source** (not all 200k):
  EC leaf + its parent chain (`data/traits/function/enzymatic_activity/ec/*ec1-1-1-2*`),
  CATH class/architecture/topology/homologous_superfamily, TED/ECOD/SCOPe folds
  (`data/traits/structure/fold/{novel,ecod,scope}/`), a Pfam family + its clan
  parent (`…/structure/domain/pfam/*pf00069*`), TCDB class→subclass→family,
  COG + functional category, a Rhea reaction with `chemical_participants`,
  RepeatsDB class→topology→fold→clan, InterPro entries, and the 9 EVO records.
- Run `just review-categories` (`scripts/review_source_categories.py`) — a
  per-source category audit; use it as a starting point, not the last word.

### Questions
**A. Concept model.** Are the 5 axes the right top-level partition? Is
`SEQUENCE_STRUCTURE` an axis or a bridge category? Is `EVOLUTION` (a property of
a protein across taxa) the same *kind* of thing as SEQUENCE/STRUCTURE/FUNCTION?
Is `FUNCTION` one axis or several (enzymatic activity, binding, transport,
pathway, ortholog-group, resistance, localisation, interaction, environmental
response, cofactor)? Is axis→category granularity consistent (`STRUCT_FOLD` =
whole folds vs `STRUCT_DOMAIN` = Pfam families / CATH-domains)? Are categories
MECE per axis? Is `term_kind` used consistently and the class-vs-instance
boundary clean (per-protein records were retired — confirm none remain)? Are
`xrefs` / `mapped_xrefs` / `parent_traits` / `chemical_participants`
semantically non-overlapping?

**B. Relationships & existing hierarchy.** `parent_traits` (typed
`rdfs:subClassOf`) is currently the **only** trait↔trait relation. For each way
it is used, is `subclass_of` correct, or is it really `biolink:member_of`
(Pfam family → clan), `biolink:part_of` (a binding *site* within a *domain*; a
domain within a protein), or `biolink:has_participant` (reaction → ChEBI)? Which
Biolink predicates are missing from the model entirely (needing RO)? Audit the
per-source hierarchies (EC, CATH, ECOD, SCOPe, TCDB, COG, RepeatsDB, Pfam→clan,
InterPro) for correct typing, **dangling parents** (CURIEs to non-existent
records), **cross-axis parents**, and **multi-parent** inconsistencies. Where do
different sources classify the same biological thing (Pfam vs CATH vs SCOP vs
ECOD domain over one region; EC vs Rhea for one reaction) — relate them with
which Biolink predicate (`same_as` / `close_match` / leave parallel)?

**C. Propose a hierarchy / taxonomy.** Propose a single upper hierarchy rooted
at "protein trait" covering the whole space: root → axis branches → category
classes → source-native sub-hierarchies. Present it as a tree, and label **every
edge with its Biolink predicate CURIE** (`biolink:subclass_of`,
`biolink:part_of`, `biolink:member_of`, `biolink:has_participant`, …), using
`RO:` only where Biolink lacks a slot (flag each such case). Give a **node
grounding table** mapping each axis/category to the community ontology it should
align to (SO / GO CC-MF-BP / PATO / EDAM / ChEBI), flagging where no clean
grounding exists. Show how the parallel source hierarchies reconcile (or why
they must stay parallel).

**D. Oddities (required).** Enumerate, ranked, everything that doesn't fit —
one-record / empty categories; mixed-granularity categories; the `MIXED_` /
SEQUENCE_STRUCTURE naming; `SEQ_REPEAT` vs `MIXED_STRUCTURAL_REPEAT`; whether
FUNCTION should split into several axes; the EVOLUTION axis's small size and
different ontological character; PROSITE pattern→PDOC parents; any residual
instance-level modelling; `term_kind` usage; whether "trait" (a class of protein
feature) is the right unit vs "annotation". Tag each {cosmetic | real problem |
open question}.

### Deliverable
One markdown report at `research/schema-hierarchy-review-<N>.md`:
1. **Concept-model assessment.**
2. **Relationship & hierarchy assessment** — a table of every `parent_traits`
   usage pattern with its correct Biolink predicate (or RO, flagged).
3. **Proposed taxonomy** — the tree with Biolink-typed edges + the node
   grounding table.
4. **Oddities** — ranked, each tagged {cosmetic | real problem | open question}.
5. **Minimal path to adopt** — the smallest schema/data changes toward the
   proposed hierarchy without a mass re-seed, and what to defer.

Be concrete and cite paths/identifiers. It is expected that the proposed
hierarchy is imperfect — surface the tensions rather than hiding them.
