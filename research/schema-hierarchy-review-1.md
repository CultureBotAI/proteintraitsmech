---
topic: Codex review — schema, protein-trait concepts & hierarchy (Biolink-typed)
date: 2026-07-03
reviewer: Codex (via codex-schema-hierarchy-review skill)
edge_typing: Biolink Model predicates (KG-Microbe biolink-model.yaml); no RO fallback needed
mode: read-only
---

# ProteinTraitsMech schema & hierarchy review 1

Predicate grounding: all Biolink predicates below are present in
`…/kg-microbe/data/raw/biolink-model.yaml` — `subclass of` (2249), `same as`
(2294), `close match` (2319), `member of` (2389), `orthologous to` (3287),
`located in` (4309), `part of` (4571), `has input` (4641), `has output` (4680),
`has participant` (4716), `participates in` (4777), `capable of` (4834),
`enables` (4857). No relationship pattern required an RO fallback.

Read-only confirmation scan: **200,629 records; 125,321 `parent_traits` edges;
16,715 dangling parent CURIE edges; 1,671 multi-parent records; 0 cross-axis
parent edges; all records `term_kind: CLASS`; no `proteintraitsmech:UNIPROTKB_*`
instance records.** Dangling parent prefixes: Pfam 13,933; PROSITE 2,745;
PATO 17; METPO 17; ARO 2; MI 1.

## 1. Concept-model assessment (summary)

The corpus is genuinely class-level (all `term_kind: CLASS`; per-protein records
retired; instance detail survives only nested in `canonical_examples`). The five
axes work as browse facets but are not equally clean upper classes:

- **SEQUENCE** — sound axis for linear residue features / sequence-defined classes.
- **STRUCTURE** — mixes three kinds: structural *classification* (CATH/SCOPe/
  ECOD/Pfam/InterPro), local structural *features* (active/binding/metal sites,
  disulfides), and structural *qualities* (PATO stability/dynamics/surface).
- **SEQUENCE_STRUCTURE** — a **bridge/intersection**, not a peer axis
  (`MIXED_*`); RepeatsDB repeats differ from sequence-only Pfam repeats.
- **FUNCTION** — too broad for one ontological kind (activity, binding,
  transport, pathway, resistance, interaction, environmental response,
  cofactor, ortholog-group); keep as one compatibility axis but sub-branch it.
- **EVOLUTION** — ontologically the most different: comparative-genomics
  *distribution* traits across taxa, not intrinsic protein features.

Category granularity is uneven (taxonomy ranks vs feature kinds vs qualities vs
activities vs membership), which is fine for a KG but means category→parent
edges do **not** all share the same semantics. `xrefs` / `mapped_xrefs` /
`parent_traits` / `chemical_participants` are conceptually distinct, but
`parent_traits` (declared `rdfs:subClassOf`) is **overloaded**: used for
subclass, membership, documentation grouping, and OBO multi-inheritance.

## 2. Relationship & hierarchy — `parent_traits` usage → correct Biolink predicate

| Source / pattern | Current edge | Correct predicate | Issue |
|---|---|---|---|
| EC hierarchy | `EC:1.1.1.2 → 1.1.1.- → …` | `biolink:subclass_of` | ✓ correct |
| CATH class/arch/topology/superfamily | `CATH:1.20 → CATH:1` | `biolink:subclass_of` | ✓ correct |
| ECOD F/T/H/X/A | `ECOD:F… → ECOD:T…` | `biolink:subclass_of` | ✓ correct |
| SCOPe cl/cf/sf/fa/dm | `SCOP:58909 → 58908` | `biolink:subclass_of` | ✓ correct |
| InterPro parent/child | `IPR034993 → IPR000504` | `biolink:subclass_of` | ✓ correct |
| **Pfam family → clan** | `PF00069 → CL0016` | **`biolink:member_of`** | ✗ subclass too strong; **13,933 dangling** (clans not materialized) |
| **COG → functional category** | `COG0753 → CATEGORY_P` | **`biolink:member_of`** | ✗ subclass too strong |
| TCDB class/subclass/family | `1.P.1 → 1.P → 1` | `biolink:subclass_of` | ✓ (systems excluded as instances) |
| RepeatsDB class→topology→fold→clan | `3.3.2.3 → 3.3.2 → …` | `biolink:subclass_of` | ✓ correct |
| **PROSITE signature → PDOC** | `PS00796 → PDOC00633` | **`biolink:member_of`** (or close_match) | ✗ PDOC is documentation/grouping; **2,745 dangling** |
| PSI-MOD / ARO / PSI-MI / PATO / METPO OBO | child → parent | `biolink:subclass_of` | ✓ (multi-parent expected; small dangling sets) |
| Reactome pathway hierarchy | child → parent | `biolink:subclass_of` **or** `biolink:part_of` | needs source-edge audit (partonomy vs taxonomy) |
| Curated stability | condition + increased/decreased | `biolink:subclass_of` | ✓ clean multiple inheritance |

Non-`parent_traits` relations to type explicitly: Rhea→ChEBI participants =
`biolink:has_participant` (→ `has_input`/`has_output` when direction parsed);
site/domain within domain/protein = `biolink:part_of`; activity = `enables` /
`capable_of`; pathway = `participates_in`; localization = `located_in`;
orthology = `orthologous_to`; cross-source near-equivalent classifications =
`biolink:close_match` (not `same_as`).

## 3. Proposed taxonomy (top level)

```
protein trait
  ├─ sequence trait                     (SEQ_*)
  ├─ structure trait                    (STRUCT_* → classification / local feature / quality sub-branches)
  ├─ sequence-structure bridge trait    (MIXED_*)
  ├─ function trait                     (FUNC_* → molecular activity / biological participation / cellular context / interaction / resistance / orthology-grouping)
  └─ evolutionary distribution trait    (EVO_*)
```
All axis/category edges `biolink:subclass_of`, EXCEPT Pfam→clan and
COG→category (`biolink:member_of`) and Rhea→ChEBI (`biolink:has_participant`).
The taxonomy is an **overlay** — source-native hierarchies stay parallel
(`biolink:close_match` between Pfam/InterPro/CATH/SCOPe/ECOD, never auto-merge).
Full per-node tree + node-grounding table (SO/GO/PATO/EDAM/ChEBI) in the Codex
transcript; grounding highlights: SEQ_MOTIF→SO:0001067, PTM→PSI-MOD/MOD,
stability/dynamics/surface→PATO, enzymatic→EC/Rhea/GO-MF, localization→GO-CC.

## 4. Oddities (ranked)

1. **{real}** `parent_traits` overloaded (subclass + membership + grouping + multi-inheritance).
2. **{real}** 16,715 dangling parents — 13,933 Pfam clans + 2,745 PROSITE PDOC not materialized.
3. **{real}** Pfam family→clan should be `member_of`, not subclass.
4. **{real}** COG→functional-category should be `member_of`.
5. **{real}** PROSITE→PDOC is documentation grouping, not subclass.
6. **{real}** `mapped_xrefs` often lack a `predicate` (pfam2go/pfam2interpro/ec2go/rhea2ec conflated).
7. **{real}** Rhea `chemical_participants` are `SUBSTRATE_OR_PRODUCT` — only `has_participant` is safe until direction parsed.
8. **{open}** FUNCTION spans several ontological kinds — sub-branch it.
9. **{open}** EVOLUTION is a distribution trait, different kind; small (9 records).
10. **{open}** SEQUENCE_STRUCTURE is a bridge; `MIXED_` vs `SEQUENCE_STRUCTURE` naming mismatch.
11. **{open}** SEQ_REPEAT vs MIXED_STRUCTURAL_REPEAT — defensible but don't merge without evidence.
12. **{open}** Parallel Pfam/InterPro/CATH/SCOPe/ECOD classify overlapping biology → `close_match` default.
13. **{real}** Reactome hierarchy may be partonomy (`part_of`) — audit source edges.
14. **{real}** Schema has SEQ_/STRUCT_/MIXED_/FUNC_ axis rules but **no `EVO_* → EVOLUTION` rule**.
15. **{open}** `xrefs` vs `mapped_xrefs` both need relation typing for KG export.
16. **{cosmetic}** `TermKindEnum` has property kinds but every record is CLASS.
17–22. STRUCT_DOMAIN/FOLD/TOPOLOGY granularity, sparse categories, "trait" doing broad work — mostly {open}.

## 5. Minimal path to adopt (no mass re-seed)

1. Add a typed `trait_relations` slot (`{predicate, object, relation_source}`); keep `parent_traits` as the backward-compatible subclass path.
2. Populate typed relations by **deterministic overlay** from source/prefix/category (subclass for EC/CATH/ECOD/SCOPe/InterPro/OBO; `member_of` for Pfam→clan and COG→category).
3. **Materialize the missing grouping nodes** (Pfam clans, PROSITE PDOC, sparse PATO/METPO/ARO/MI parents) — fixes most of the 16,715 dangling parents.
4. Add `predicate` to mapping-derived `mapped_xrefs` (`close_match` for pfam2interpro; function assoc for pfam2go/ec2go).
5. Export `chemical_participants` as `has_participant` (→ has_input/has_output after direction parsing).
6. Add the missing `EVO_* → EVOLUTION` schema validation rule.
7. Add read-only hierarchy QA (parent-exists, predicate-compatible, no cross-axis, dangling-by-prefix).

**Defer:** redesigning axes, mass re-seed, auto-merging cross-source
classifications, `same_as` assertions, forcing Reactome to `part_of`, promoting
nested `canonical_examples.features` to top-level records.
