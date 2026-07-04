---
topic: Record sample review 1 — content & structure quality across all trait categories
skill: review-record-samples
date: 2026-07-04
samples: one-per-(axis,category) snapshot (48 cells, seed 20260704) + a 5-per-category deep pass (206 records)
scope: read-only; no records or seeders edited
---

# Record sample review 1

Two reproducible samples (seed `20260704`), each record read in full and scored
against Part A (per-record) / Part B (per-set):

- **Snapshot** — one random record per (axis, category) cell (48 cells).
- **Deep pass** — five per category (206 records), fanned out per axis.

Both agree; the snapshot table is below, the deep-pass detail is in
[`record-sample-review/`](record-sample-review/). **No blockers in either
sample** — every record validates, identifiers/axis/category are sound, and the
class-vs-instance split is clean (per-protein data stays in `canonical_examples`).

Snapshot verdicts: **PASS 24 · minor 20 · major 4 · blocker 0.**

## 1. One-per-(axis,category) snapshot (48 cells)

| axis | category | total | picked record | verdict | note |
|------|----------|------:|---------------|---------|------|
| EVOLUTION | EVO_CONSERVATION | 3 | EVO_VARIABLE | PASS | genuine def; `evolutionary_scope` present |
| EVOLUTION | EVO_PANGENOME | 6 | EVO_PANGENOME_CORE | PASS | def + prevalence bands + Roary method |
| FUNCTION | FUNC_ENVIRONMENTAL_RESPONSE | 49 | METPO:1000601 | minor | organism-level trait (phenotype drift) |
| FUNCTION | FUNC_ENZYMATIC_ACTIVITY | 26003 | RHEA:29471 | PASS | Rhea + ChEBI participants — model |
| FUNCTION | FUNC_INTERACTION_PARTNER | 147 | MI:0220 | **major** | interaction *type*, not a *partner*; psi_mi seeder |
| FUNCTION | FUNC_ORTHOLOG_GROUP | 9728 | COG:COG1949 | PASS | real def; member_of category |
| FUNCTION | FUNC_PATHWAY | 3969 | Reactome:R-HSA-5083635 | minor | boilerplate def; part_of parent OK |
| FUNCTION | FUNC_PROTEIN_FAMILY | 20313 | NCBIfam:NF040143 | minor | DUF template def; thin grounding |
| FUNCTION | FUNC_RESISTANCE | 7452 | ARO:3004595 | PASS | mechanistic def + PMID — model |
| FUNCTION | FUNC_TRANSPORT | 2285 | TCDB:1.D.78 | minor | boilerplate def; parent OK |
| SEQUENCE | SEQ_CLEAVAGE_SITE | 11 | ELM:ELME000103 | PASS | def + `sequence_pattern` + example |
| SEQUENCE | SEQ_CONSERVATION | 775 | InterPro:IPR019817 | PASS | full authored def — model |
| SEQUENCE | SEQ_CROSSLINK_SITE | 69 | MOD:00877 | minor | terse import def; psi-mod |
| SEQUENCE | SEQ_DISORDER | 202 | Pfam:PF03154 | minor | boilerplate template def; pfam |
| SEQUENCE | SEQ_DOMAIN | 88742 | NCBIfam:NF017413 | minor | DUF template def; no xref |
| SEQUENCE | SEQ_FAMILY | 14424 | Pfam:PF05321 | minor | "Pfam family **family**" duplication bug |
| SEQUENCE | SEQ_GLYCOSYLATION_SITE | 85 | MOD:00760 | **major** | def = "…N-linked glycosylation - **missing ref**" artifact |
| SEQUENCE | SEQ_HOMOLOGOUS_SUPERFAMILY | 5699 | InterPro:IPR016106 | PASS | full authored def — model |
| SEQUENCE | SEQ_INITIATOR_METHIONINE | 1 | UNIPROT_FT_… | PASS | singleton justified; instances in examples |
| SEQUENCE | SEQ_LEADER_PEPTIDE | 20 | RIPP_LEADER_LANTHIPEPTIDE | PASS | rich curated def |
| SEQUENCE | SEQ_LIPIDATION_SITE | 40 | MOD:01685 | PASS | genuine PSI-MOD def |
| SEQUENCE | SEQ_MATURE_CHAIN | 1 | UNIPROT_FT_… | PASS | singleton justified |
| SEQUENCE | SEQ_MODIFIED_RESIDUE | 618 | MOD:01814 | PASS | genuine def + xrefs |
| SEQUENCE | SEQ_MOTIF | 3121 | PROSITE:PS00492 | **major** | def = label restated; prosite seeder |
| SEQUENCE | SEQ_PROPEPTIDE | 1 | UNIPROT_FT_… | PASS | singleton justified |
| SEQUENCE | SEQ_PTM_SITE | 1251 | MOD:01688 | PASS | genuine def; overlaps SEQ_MODIFIED_RESIDUE |
| SEQUENCE | SEQ_REPEAT | 2073 | Pfam:PF29002 | minor | boilerplate template def; pfam |
| SEQUENCE | SEQ_SIGNAL_PEPTIDE | 1 | UNIPROT_FT_… | PASS | singleton justified |
| SEQUENCE | SEQ_TARGETING_SIGNAL | 28 | ELM:ELME000278 | PASS | def + `sequence_pattern` + examples |
| SEQUENCE | SEQ_TRANSIT_PEPTIDE | 1 | UNIPROT_FT_… | PASS | singleton justified |
| SEQUENCE_STRUCTURE | MIXED_COILED_COIL | 315 | Pfam:PF07926 | minor | boilerplate def; pfam |
| SEQUENCE_STRUCTURE | MIXED_STRUCTURAL_REPEAT | 122 | RepeatsDB:5 | PASS | real def; class-level RepeatsDB |
| STRUCTURE | STRUCT_ACTIVE_SITE | 1137 | MCSA:824 | minor | model mechanism def, but HTML `<i>` tags |
| STRUCTURE | STRUCT_ARCHITECTURE | 64 | ECOD:A.… | minor | boilerplate node def; no license |
| STRUCTURE | STRUCT_BINDING_SITE | 83 | InterPro:IPR019780 | minor | rich def but stripped-citation "( )" |
| STRUCTURE | STRUCT_CAVITY | 5 | TUNNEL | PASS | clean LSF def + xref |
| STRUCTURE | STRUCT_CLASS | 17 | SCOP:51349 | minor | boilerplate node def; no license |
| STRUCTURE | STRUCT_DISULFIDE | 1 | DISULFIDE_BOND | PASS | singleton justified |
| STRUCTURE | STRUCT_DOMAIN | 13514 | SCOP:55133 | minor | boilerplate node def; no geometry rep/license |
| STRUCTURE | STRUCT_DYNAMICS | 18 | PATO:0001171 | PASS | genuine PATO def (fair fit) |
| STRUCTURE | STRUCT_FOLD | 55735 | ECOD:F.109.4.1.2461 | minor | boilerplate def; **no `structural_geometry_representations`** |
| STRUCTURE | STRUCT_HOMOLOGOUS_SUPERFAMILY | 15177 | CATH:1.20.58.1310 | minor | boilerplate def; no geometry rep |
| STRUCTURE | STRUCT_INTERFACE | 1 | INTERFACE | PASS | singleton justified |
| STRUCTURE | STRUCT_METAL_SITE | 1 | METAL_BINDING_SITE | PASS | singleton justified |
| STRUCTURE | STRUCT_SECONDARY | 33 | HELIX_TURN_HELIX | PASS | def + `secondary_structure_representations` — model |
| STRUCTURE | STRUCT_STABILITY | 37 | STABILITY_PRESSURE_DECREASED | PASS | curated def; dual parents |
| STRUCTURE | STRUCT_SURFACE | 14 | PATO:0001986 | **major** | "dissolved"/solubility is not a surface trait |
| STRUCTURE | STRUCT_TOPOLOGY | 5427 | ECOD:T.3166.1.1 | minor | boilerplate def; no geometry rep/license |

## 2. Systemic issues (ranked by blast radius)

Both samples converge on the same seeder-level defects. **The dominant issue is
templated definitions that never pull the source's own description prose** — valid
but non-defining (fails Part A4). Fix at the seeder, not the records.

| # | Issue | Seeder(s) | ~records | Severity | Fix |
|---|-------|-----------|---------:|----------|-----|
| S1 | **Boilerplate definitions** that restate the label ("`<db>` node …", "Pfam `<type>` family …") | seed_ecod/scope/cath, seed_pfam, seed_ncbifam, seed_reactome, seed_tcdb, seed_seed_subsystems | ~200k | major | pull the source description field (Pfam-A.hmm.dat `DESC`, NCBIfam `product_name`, PROSITE PDOC text, Reactome summation) into `definition`; where the source has no prose (ECOD/CATH/SCOPe nodes) keep the node def but say so |
| S2 | **CATH/SCOPe/ECOD carry no `structural_geometry_representations`** (only TED does) — A8 gap on the biggest fold/domain buckets | seed_cath/scope/ecod (or a populate step) | ~72k | major | the PDB-domain reps already exist in `data/analysis/structural_reps.tsv`; write them onto the records like the TED `--enrich` step |
| S3 | **`license` missing** on ECOD/SCOPe/CATH (and PROSITE-signature) records | seed_ecod/scope/cath, seed_prosite | ~70k | major | add the source license to the seeder output |
| S4 | **Import artifacts leak into `definition`** — PSI-MOD "…- missing ref"/"from Unimod", InterPro stripped citations "( )", M-CSA HTML `<i>`, OBO "\nab (not=) E" | seed_psimod, seed_interpro, seed_mcsa, seed_obo | ~2k | major (def) / minor | sanitize on import (drop "missing ref", strip empty "( )", strip HTML tags) |
| S5 | **CDD paragraph-as-`label`** — the full description is in `label`, the real short name only in `synonyms` | seed_cdd | ~33k | major | swap: short name → `label`, description → `definition` |
| S6 | **`prosite` signature def = the label verbatim** | seed_prosite | ~3k (PS patterns) | major | use the PDOC documentation text (already seeded as SEQ_FAMILY parents) for the definition |

## 3. Modelling / scoping decisions (need a human call)

- **`FUNC_INTERACTION_PARTNER` (MI:0220 etc.)** — the psi_mi seeder routes interaction
  *type/method* MI terms here, but the category is meant for interaction *partners*.
  Run `review-source-categories --source PSI-MI` and re-scope (a `FUNC_*` interaction-type
  bucket, or restrict to the partner branch).
- **`FUNC_ENVIRONMENTAL_RESPONSE` (METPO)** — holds *organism* phenotypes (mesophilic,
  halotolerant, oxygen-preference), not protein functions. Decide whether organism-level
  ecophysiology is in scope for a **protein**-trait KB, or reframe as the protein's
  environmental-response *capacity*.
- **`STRUCT_SURFACE` PATO whitelist** — "dissolved" / solubility is a solution state, not a
  surface-geometry trait; tighten the PATO whitelist in seed_obo/seed_stability.
- **M-CSA `STRUCT_ACTIVE_SITE` (1,137)** — content is excellent (mechanism + evidence) but the
  records are enzyme/mechanism-centric (label = enzyme, def = reaction); confirm whether they
  belong as active-site traits or should link to a `FUNC_ENZYMATIC_ACTIVITY` counterpart.
- **PSI-MOD granularity** — modification terms fragment across SEQ_MODIFIED_RESIDUE /
  SEQ_PTM_SITE / SEQ_CROSSLINK_SITE / SEQ_GLYCOSYLATION_SITE / SEQ_LIPIDATION_SITE; watch for
  near-duplicate classes (feed to `merge-within-axis`, SEQUENCE localized operator).

## 4. What's already model-quality (keep as the template)

The hand-curated / well-sourced tier is clean and should be the bar: **EVOLUTION**
(every record now carries `evolutionary_scope`), **InterPro** SEQ_CONSERVATION /
SEQ_HOMOLOGOUS_SUPERFAMILY (full authored definitions), **Rhea**
FUNC_ENZYMATIC_ACTIVITY, **ARO** FUNC_RESISTANCE, **STRUCT_SECONDARY** (definitions
+ `secondary_structure_representations`), curated STABILITY, and the eight
justified singletons (UniProt-FT feature classes + LSF cavity/interface/metal/
disulfide) — correct class-not-instance modelling with per-protein hits in
`canonical_examples`.

## 5. Method

`review-record-samples` skill, seed `20260704`. Snapshot = one random record per
(axis, category) cell; deep pass = five per category, one reviewer per axis. Each
record read in full; Part A (A1–A9) + Part B. Detail per axis:
[`record-sample-review/`](record-sample-review/).
