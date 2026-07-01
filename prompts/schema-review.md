# Review prompt — ProteinTraitsMech axis + category schema

Hand this to the codex rescue plugin (or any independent reviewer) as a
read-only audit of the LinkML schema and its classification system. The
reviewer must produce a written report; do **not** make code changes.

---

## Your role

You are an independent domain reviewer with expertise in protein
science (sequence analysis, structural biology, protein family
databases) and ontology/schema design (OBO, LinkML, biolink).
ProteinTraitsMech is a curated knowledge base of protein sequence and
structure traits. This repo's `ProteinTraitRecord` root class routes
every record onto one of four **axes** and one of ~40 **categories**.
Your job is to critique that classification along three dimensions:
completeness, logic, and consistency.

Report only findings you can defend from the files below or from
authoritative external references (UniProt controlled vocabulary,
InterPro/Pfam category conventions, GO namespaces, SO term
hierarchies, CATH/SCOP structural hierarchies, MEROPS). Do not invent
missing categories from intuition alone.

## Sources of truth (read fully, in order)

1. `src/proteintraitsmech/schema/proteintraitsmech.yaml` — the LinkML
   schema. In particular:
   - `TraitAxisEnum` (four axes)
   - `ProteinTraitCategoryEnum` (SEQ_*, STRUCT_*, MIXED_*, FUNC_*, UPPER, OTHER)
   - `TermKindEnum`, `MappingStatusEnum`, `SynonymTypeEnum`,
     `CausalNodeTypeEnum`, `PriorityEnum`
   - `ProteinTraitRecord.attributes` — the required/optional slots and
     the intended semantics of `sequence_pattern` vs `residue_sequence`
     vs `parent_traits` vs `xrefs`.
2. `docs/schema.md` — the human-readable summary of the same schema.
   Use it to spot places where the prose promise diverges from what the
   YAML actually enforces.
3. `README.md` — the source-to-axis/category routing tables (UniProt
   FT-line map, UniProt CC/DR map for FUNCTION, PROSITE seed table, TED
   fold seed table).
4. `scripts/seed_uniprot.py` — read `FT_TYPE_MAP`, `route_feature`,
   `function_records`, and the `_*_record` helpers. This is the *actual*
   axis + category dispatch for UniProt-seeded records.
5. `scripts/seed_prosite.py` — read `categorise_prosite`,
   `categorise_prorule`. This is the dispatch for PROSITE seeds.
6. `scripts/seed_ted.py` and `scripts/seed_localstructuralfeature.py` —
   the fold and structural-feature dispatchers.
7. A representative record per non-empty category directory under
   `data/traits/` — sample 1–2 files each from `sequence/*/`,
   `structure/*/`, `mixed/*/`, and `function/*/` and verify that the
   record's declared `trait_axis` and `trait_category` are consistent
   with what the source encoded.

The `ProteinTraitCategoryEnum` values live entirely in the schema YAML.
The four axes are `SEQUENCE`, `STRUCTURE`, `SEQUENCE_STRUCTURE`,
`FUNCTION` — `FUNCTION` is a late addition; scrutinise how it interacts
with the older three.

## What to report

Return exactly one Markdown document with these top-level sections:

### 1. Completeness

- Are there recognised protein sequence/structure trait families that
  the enum cannot express? For each gap, name the trait, cite the
  authoritative source (InterPro category, GO namespace, SO term,
  MEROPS site type, CATH class, PROSITE section), and propose the
  minimal enum extension.
- Are the seven `SEQ_*` families exhaustive for what UniProt FT lines,
  PROSITE patterns, and ELM motifs actually mark up? Check specifically
  for: cross-links, glycosylation vs. lipidation vs. phosphorylation
  granularity, non-standard residues (SEC/PYL), initiator methionine,
  transit peptides, chain/peptide products.
- Do the seventeen `STRUCT_*` families cover CATH/SCOP structural
  hierarchies, transmembrane helices vs. beta-barrels, intrinsically
  disordered regions in the structural sense, and post-translational
  structural modifications (disulfide, hydroxylation crosslinks)?
- Are the four `MIXED_*` families sufficient? What sequence-and-
  structure traits (e.g. beta-barrel transmembrane, moonlighting
  regions) fall between the cracks?
- Do the six `FUNC_*` families cover the semantics UniProt encodes in
  its CC blocks (FUNCTION, PATHWAY, ACTIVITY REGULATION, ALLERGEN,
  DISEASE, PHARMACEUTICAL, MISCELLANEOUS)? Note absent categories the
  seeder can currently reach but the schema cannot represent.
- Are the enums `TermKindEnum`, `MappingStatusEnum`,
  `CausalNodeTypeEnum`, and `PriorityEnum` complete for their intended
  use? Flag missing values (e.g. `MERGED` mapping status for
  deduplicated records, `INTERACTION` causal-node type).

### 2. Logic

- Do the four axes carve the space cleanly? In particular:
  - Is `SEQUENCE_STRUCTURE` a real axis or a bag of ambiguous cases?
    Give an example where a curator would legitimately be confused
    between `SEQUENCE_STRUCTURE / MIXED_TRANSMEMBRANE` and either
    `STRUCTURE / STRUCT_TOPOLOGY` or `SEQUENCE / SEQ_MOTIF`.
  - Does `FUNCTION` overlap with `STRUCTURE / STRUCT_ACTIVE_SITE`?
    An enzyme's catalytic activity is a `FUNC_ENZYMATIC_ACTIVITY`
    trait *and* usually localises to a `STRUCT_ACTIVE_SITE`. The
    schema currently emits both records per UniProt entry. Is that
    correct as a modelling decision, and are the semantics documented?
- Are any within-axis categories redundant? Specifically check:
  - `STRUCT_ACTIVE_SITE` vs `STRUCT_BINDING_SITE` vs
    `STRUCT_METAL_SITE` vs `STRUCT_ALLOSTERIC_SITE` — is the difference
    biologically principled or an artefact of UniProt's own FT
    vocabulary?
  - `SEQ_MOTIF` vs `SEQ_PTM_SITE` vs `SEQ_CLEAVAGE_SITE` — when a
    proteolytic cleavage happens at a signal peptide (SEQ_SIGNAL_PEPTIDE
    territory), which category wins?
  - `STRUCT_INTERFACE` vs `STRUCT_QUATERNARY` — one is the interface,
    the other is the assembly state. Are they truly independent?
- Is the `TraitAxisEnum` / `ProteinTraitCategoryEnum` pairing enforced?
  The schema declares both as free enum ranges — nothing prevents a
  `SEQ_MOTIF` record from being tagged `trait_axis: STRUCTURE`. Report
  whether an axis-to-allowed-categories constraint should be added and
  what the mapping would be.
- Is `residue_sequence` semantically distinct from `sequence_pattern`
  in a way the reader will infer? Check the docstring, then check that
  no record populates both with conflicting content.
- `parent_traits` accepts any CURIE. What are the *typing* rules — must
  the parent share the same axis? Same category? The schema doesn't
  say. Flag this.

### 3. Consistency

For each of the following, either confirm the invariant holds or list
the offending records/lines:

- **Enum drift** — every category the seeders can emit must exist in
  `ProteinTraitCategoryEnum`. Grep the seeders for string literals
  matching `SEQ_*`, `STRUCT_*`, `MIXED_*`, `FUNC_*` and diff against the
  enum's permissible values. Report any orphans in either direction.
- **Axis / category pairing** — every category has a natural axis.
  Confirm that seeders never write a `SEQ_*` category with a non-
  SEQUENCE axis (and mutatis mutandis for the other three axes).
- **UniProt FT map fidelity** — the README table for FT-type routing
  must match `FT_TYPE_MAP` in `scripts/seed_uniprot.py` exactly. Report
  any silent divergence.
- **PROSITE fidelity** — the README's PROSITE row totals should match
  what `categorise_prosite` and `categorise_prorule` would produce over
  today's `data/raw/prosite.dat` and `prorule.dat`. Check by reading
  the seeder's dispatch, not by running it.
- **`residue_sequence` invariants** — for every UniProt-seeded record
  with a coordinate range, the residues stored should equal
  `entry.sequence[start-1:end]`. Spot-check the P25888 and B0R5N7
  records under `data/traits/sequence/` and `data/traits/structure/`.
  Confirm the schema's regex `^[ACDEFGHIKLMNPQRSTVWYUOBZJX*]+$`
  accepts all realistic UniProt residues (including selenocysteine `U`,
  pyrrolysine `O`, and the ambiguity codes `B`, `Z`, `J`, `X`).
- **`parent_traits` grounding** — the CURIE prefixes populated by the
  seeders (`PROSITE`, `Pfam`, `InterPro`, `SMART`, `CATH`, `MEROPS`,
  `HAMAP`) must all be declared in the schema's `prefixes:` block.
- **Docs vs schema** — every category listed in `docs/schema.md` must
  exist in the YAML enum (and vice versa). Note any doc drift.
- **`sequence_pattern` uniqueness** — should never be populated on
  STRUCTURE-axis records (schema says SEQUENCE-only). Confirm by
  grepping `data/traits/structure/**/*.yaml` for `sequence_pattern:`.

## Output constraints

- One Markdown document, ≤ 1500 words.
- Each finding tagged `[COMPLETENESS]`, `[LOGIC]`, or `[CONSISTENCY]`.
- Each finding cites at least one file path (with line number where
  applicable) and at least one authoritative external source when it
  claims something is missing.
- End with a prioritised "Top 5 actions" list, most impactful first.
  Distinguish schema edits (add / rename / constrain enum values) from
  seeder edits (widen dispatch, add validation) from documentation
  edits (README / docs/schema.md sync).
- Do not propose changes to individual data records — those follow
  from the schema fixes.
- Do not stray into the causal-graph or evidence subsystem; that's
  out of scope for this review.
