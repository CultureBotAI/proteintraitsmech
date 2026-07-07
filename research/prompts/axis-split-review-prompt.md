# Codex review — are the cross-axis splits of multi-axis sources appropriate?

Read-only audit. Some data sources emit records onto **more than one trait_axis**
— most importantly split between **SEQUENCE and FUNCTION**. Assess, per source and
per record class, whether each split is **correct under this repo's governing
convention**, and flag mis-routed records.

## The governing convention (do not restate — apply it)

From `CLAUDE.md` (authoritative):

> **The axis follows the representation, not the biology.** Domain/family
> classifications defined by a *sequence signature* (profile HMM / PSSM / pattern)
> are **SEQUENCE** (`SEQ_DOMAIN`, `SEQ_FAMILY`, `SEQ_HOMOLOGOUS_SUPERFAMILY`) — a
> domain detected by a sequence model is a sequence trait. Only *structure-derived*
> classifications (CATH, SCOPe, ECOD, TED) use `STRUCT_*`. Whole-protein families
> defined by conserved *function* (NCBIfam/TIGRFAM equivalog, subfamily) are
> `FUNC_PROTEIN_FAMILY`.

The tension to adjudicate: **every** NCBIfam and CDD model is a *sequence-profile
HMM/PSSM*, so a naïve reading of "axis follows representation" puts them all on
SEQUENCE. The convention nonetheless carves out **function-defined whole-protein
families** (equivalog/subfamily; orthologous groups) to FUNCTION. Your job is to
judge whether that carve-out is (a) principled, (b) drawn at the right line, and
(c) applied consistently and correctly per record.

## The splits in scope (verify these counts yourself)

- **NCBIfam** — FUNCTION `FUNC_PROTEIN_FAMILY` (~20.3k) vs SEQUENCE `SEQ_DOMAIN`
  (~17.9k) + `SEQ_REPEAT` + `SEQ_HOMOLOGOUS_SUPERFAMILY`. Routed by TIGRFAM
  **`family_type`** in `scripts/seed_ncbifam.py` (`route()` /
  `_FUNC_FAMILY_TYPES = {equivalog, subfamily, exception, hypoth_equivalog,
  paralog}` → FUNCTION; `*_domain`, `domain`, `signature` → SEQUENCE; default
  SEQUENCE).
- **CDD** — SEQUENCE `SEQ_DOMAIN` (~32k) + `SEQ_HOMOLOGOUS_SUPERFAMILY` vs FUNCTION
  `FUNC_ORTHOLOG_GROUP` (~4.8k, the KOG/orthologous-group models). Routing in
  `scripts/seed_cdd.py`.
- **InterPro** — mostly SEQUENCE, but `Active_site`/`Binding_site` entry types →
  STRUCTURE (`scripts/seed_interpro.py`). Secondary; assess only if time permits.

## What to examine

1. **The routing tables.** Read `route()` / the family_type→axis map in
   `seed_ncbifam.py` and the equivalent in `seed_cdd.py`. Is the mapping exhaustive
   (every family_type / CDD source-DB handled)? What does the default do, and is a
   silent default to SEQ_DOMAIN safe?
2. **Sample records both sides of each split.** Pull ~10 FUNC_PROTEIN_FAMILY and
   ~10 SEQ_DOMAIN NCBIfam records (and the CDD equivalents). Read their labels,
   definitions, `family_type`/source, and groundings (EC/GO). Do the FUNCTION-side
   records genuinely describe a **whole-protein, function-conserved family**, and
   the SEQUENCE-side records a **sequence region / domain**?
3. **Mis-routing.** Look specifically for:
   - `equivalog_domain` (domain-scoped isology) that landed in FUNCTION though it
     is domain-level;
   - a `domain`/`signature` model with a strong single EC/GO function that might
     belong in FUNCTION (or vice-versa);
   - CDD KOGs that are really single-domain models, or CDD domain models that are
     really orthologous groups.
4. **Category correctness within the axis.** Is `FUNC_PROTEIN_FAMILY` the right
   category for NCBIfam equivalogs, and `FUNC_ORTHOLOG_GROUP` right for CDD KOGs
   (vs `FUNC_PROTEIN_FAMILY`, or even an EVOLUTION category — orthologous groups
   are an evolutionary construct)? Are the two sources' function-side categories
   mutually consistent (both are "conserved-function whole-protein groups")?
5. **Cross-source consistency.** NCBIfam and CDD both split "family/ortholog →
   FUNCTION, domain → SEQUENCE". Do they draw the line the same way? If not, is the
   difference justified by the sources' semantics or is it an inconsistency?
6. **Boundary cases.** `exception`, `paralog`, `hypoth_equivalog`, superfamily,
   repeat — are these on the defensible side of the line? (`paralog`/`exception`
   are arguably *not* function-conserved in the equivalog sense.)

## Deliverable

Write `research/axis-split-review-1.md` — but the Codex sandbox is read-only, so
if you cannot write it, **return the full report as your final message** for the
caller to save. Structure:

- **Verdict per split** (NCBIfam SEQ↔FUNC, CDD SEQ↔FUNC): ✅ appropriate / ⚠️
  partially / ⛔ wrong, one-line rationale.
- **The line, judged.** Is "function-conserved whole-protein family → FUNCTION;
  sequence region → SEQUENCE" the right criterion, and is it drawn correctly? State
  the principle you'd apply and where the current split departs from it.
- **Mis-routed record classes** — concrete file paths / identifiers + why, ranked
  by blast radius (a whole family_type mis-mapped ≫ a one-off).
- **Category calls** — FUNC_PROTEIN_FAMILY vs FUNC_ORTHOLOG_GROUP vs an EVOLUTION
  category for KOGs; consistency across sources.
- **Recommended fixes** — seeder routing-table changes (with the exact family_type
  / source-DB → axis edits) and any records to migrate, in priority order.

## Constraints

- **Read-only.** Do not edit code, records, or the schema.
- **Cite evidence** — quote the routing code, real record identifiers, and the
  `family_type`/source values that decided each judgement. No unsupported claims.
- Severity: **blocker** (a whole class on the wrong axis) · **major** (wrong
  category, inconsistent line between sources) · **minor** (a handful of edge
  records).
