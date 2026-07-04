# Equivalence cutoffs & containment relationships — reference

Synthesised from five per-axis deep-research reports (each cited to primary
sources; read them for the full citations and verification logs):
`research/equivalence-cutoffs-{sequence,structure,sequence-structure,function,evolution}.md`.

Two things this reference fixes:

1. **Cutoffs** — the numeric/logical threshold at which two traits are the *same*,
   with provenance and an honest UNVERIFIED list (thresholds a model must not
   invent).
2. **Containment is a RELATIONSHIP, not a merge.** When one trait is *contained
   in* / *narrower than* / *part of* another, that is a typed edge
   (`narrow_match` / `part_of` / `subclass_of` / `member_of`), stored in
   `trait_relations` — never a record collapse. This is the second, equally
   important output of an axis merge run.

---

## 1. Equivalence cutoffs (verified) — per axis

| Axis / operator | "Same trait" rule + cutoff | Tier | Source |
|---|---|---|---|
| **SEQ** signature family | **Same Pfam/InterPro accession** is the deterministic identity; family membership = HMMER bit score ≥ the family's curated **gathering threshold (GA)** (TC/NC bracket it). No global % — trust the accession. | MERGE (same id) | Pfam GA/TC/NC; InterPro integration |
| **SEQ** cross-source family | Signatures manually **integrated into one InterPro entry** (e.g. CUB: cd00041/PS01180/PF00431/SM00042 → IPR000859). | close_match → REVIEW | InterPro |
| **SEQ** identity zones | >40 % id = safe same-family; **20–35 % = twilight zone** (identity alone unreliable); length-dependent, not a flat number. | context | Rost 1999 |
| **SEQ** deep homology | HHsearch/HHpred **prob ≥ 95 % ≈ homology certain** (>50 %, or >30 %+top-3 = consider). | close_match | Söding HH-suite |
| **SEQ** localized feature | "Same region" only at **≥ 50 % reciprocal overlap** (⚠ borrowed from genomics — no protein-specific standard); point PTM/crosslink = **exact-residue coincidence**. Member-Jaccard alone is a trap → Tier-2 region confirmation mandatory. | close_match → REVIEW | (see UNVERIFIED) |
| **STRUCT** fold | **TM-score ≥ 0.5** = fold onset (P = 5.5×10⁻⁷; random ≈ 0.17), but same-fold *posterior* is only **13 % (SCOP)/37 % (CATH) at 0.5**, 80–90 % at 0.6 → **review, not auto-merge**. | close_match → REVIEW | Xu & Zhang 2010 |
| **STRUCT** superfamily | Repo uses TM ≥ 0.7 — **UNVERIFIED**: no source defines a superfamily TM threshold; superfamily is a *homology* claim, TM proves only geometry. Needs a second evolutionary signal; treat as heuristic. | REVIEW only | ⚠ none |
| **STRUCT** (cross-check) | DALI **Z > 2** fold floor, 8–20 probable, >20 definite; **CATH** ≥2 of {seq-id ≥35 %, SSAP ≥80 & id ≥20 %, SSAP ≥70 + function}; SCOP/ECOD manual (no numeric). | — | DALI; CATH |
| **STRUCT** secondary | DSSP **8→3** (H={H,G,I}, E={E,B}, C=rest); **topology-string identity**. Pin tool+reduction — DSSP vs STRIDE disagree 5–20 %. | close_match | DSSP; STRIDE |
| **MIXED** structural repeat | Same **RepeatsDB** branch Class→Topology→Fold→Clan (Class by period: I 1–2, II 3–7, III 5–40, IV 30–60, V >50 aa). Detectors (STRPsearch E<1e-5, HHrepID P≤1e-3) populate only. | close_match | RepeatsDB |
| **MIXED** coiled-coil | **No numeric cutoff** — categorical: heptad register a–g + oligomeric state + parallel/antiparallel (SOCKET knobs-into-holes, 7 Å). Predictor probs (NCOILS 0.5, Marcoil ≥90) gate *detection* only. | close_match (categorical) | SOCKET |
| **MIXED** transmembrane | Same class (α-helix vs β-barrel = DeepTMHMM M/B) + same topology string. | close_match | DeepTMHMM |
| **FUNC** enzymatic | **Same Rhea id** (normalise LR/RL/BI quartet to master) = **`same_as`** (strongest); **same EC leaf** (4-level) = `close_match`. GO alone ≠ identity. | MERGE (same_as) / REVIEW | Rhea; IUBMB EC |
| **FUNC** GO term | **Identical GO id** only. Semantic similarity (Resnik/Lin/JC/Wang) and Jaccard are **candidate-generation, never identity** — no canonical "same term" cutoff exists. | REVIEW | (no cutoff) |
| **FUNC** pathway | Shared **GO-BP** anchor → `close_match` (generic BP capped); enzyme-set **Jaccard** → `overlaps` (repo conv. ≥0.30; ≥0.80+label → close_match — ⚠ repo-internal, not literature). | REVIEW | (see pathway.tsv) |
| **EVOL** pangenome | `same_as`/`close_match` **iff same taxon scope AND same %-threshold AND same method**. Roary `-cd` default **99 %**; bands core ≥99 / soft-core 95–99 / shell 15–95 / cloud <15 (⚠ secondary-lit; Roary 95-vs-99 unresolved). **PPanGGOLiN** is statistical, *not* interchangeable with fixed-% Roary. | REVIEW (once fields exist) | Tettelin 2005; Roary; PPanGGOLiN |
| **EVOL** conservation | Taxon panel + ortholog method (BUSCO ">90 % of species"); dN/dS ω<1 / ≈1 / >1 = purifying/neutral/positive. Do not merge presence-breadth with dN/dS. | REVIEW | BUSCO; dN/dS |

**EVOLUTION is blocked** until records carry: `taxon_scope` (+rank),
numeric `distribution_threshold`, `definition_method`/tool, `conservation_metric`,
`orthology_basis`.

---

## 2. Containment → predicate matrix

"One trait contained in another" is the second output of a merge run. Direction
is **subject is the narrower/part; object is the broader/whole.**

| Containment case (axis) | Predicate | Grounding |
|---|---|---|
| InterPro child → parent entry (SEQ) | `biolink:subclass_of` / `narrow_match` | InterPro hierarchy |
| CATH/SCOP/ECOD family ⊂ superfamily ⊂ fold ⊂ class (STRUCT) | `biolink:subclass_of` | classification levels |
| EC leaf `1.1.1.1` ⊂ partial `1.1.1.-` ⊂ `1.1.-.-` (FUNC) | `biolink:subclass_of` / `narrow_match` | IUBMB EC (hyphen = placeholder) |
| Specific GO ⊂ broad GO via `is_a` (FUNC) | `biolink:subclass_of` / `narrow_match` | GO `is_a` |
| TCDB subfamily ⊂ family; ARO gene `is_a` AMR-family (FUNC) | `biolink:subclass_of` | TCDB; CARD |
| PSI-MI `direct interaction` ⊂ `physical association` ⊂ `association` | `biolink:subclass_of` | PSI-MI |
| Stricter %-band ⊂ looser band (core ⊂ soft-core); narrower taxon ⊂ broader (EVOL) | `biolink:narrow_match` / `subclass_of` | pangenome bands |
| RepeatsDB clan ⊂ fold ⊂ topology; specific-oligomer CC / β-barrel (MIXED) | `biolink:narrow_match` | RepeatsDB; category |
| Cross-source geometric subsumption (STRUCT, one fold inside another's set) | `biolink:narrow_match` | TM/DALI |
| Motif/site ⊂ domain; domain ⊂ multi-domain chain (SEQ/STRUCT) | `biolink:part_of` / `has_part` | BFO:0000050 |
| β-hairpin ⊂ β-sheet; helix ⊂ coiled-coil; SSE ⊂ super-secondary motif (STRUCT) | `biolink:part_of` | BFO:0000050 |
| Repeat unit ⊂ region ⊂ domain; TM span ⊂ topology; CC segment ⊂ protein (MIXED) | `biolink:part_of` | BFO:0000050 |
| Reaction/step ⊂ pathway; sub-pathway ⊂ super-pathway (FUNC) | `biolink:part_of` | Reactome `hasEvent` |
| Enzyme catalyses a step of a pathway (FUNC) | `biolink:has_participant` | RO:0000057 |
| Protein/instance → Pfam family / COG / OrthoDB / eggNOG group | `biolink:member_of` | membership |
| Enzyme-set overlap-coef = 1 (one pathway's enzymes ⊆ another's) (FUNC) | `biolink:narrow_match` | set containment |
| Partial enzyme-set / gene-set overlap (FUNC pathway) | `biolink:overlaps` | shared parts |
| Same-clan Pfam families; SEQ_REPEAT ↔ MIXED_STRUCTURAL_REPEAT bridge | `biolink:related_to` | related, **not** merge |

Rule: **anything in this table is a `trait_relations` edge, never a merge.** Only
`same_as` and merge-traits' R1/R2 collapse records.

---

## 3. Do NOT hard-code these (UNVERIFIED / no standard)

- **STRUCT superfamily TM ≥ 0.7** — no published basis; heuristic only.
- **SEQ localized "≥ 50 % reciprocal overlap"** — borrowed from genomics; no
  protein-specific primary standard.
- **GO / pathway semantic-similarity thresholds** — Resnik/Lin/Wang/Jaccard are
  candidate-generation; there is **no** canonical "same term / same pathway" cutoff.
- **Pathway EC-Jaccard 0.30 / 0.80** — repo-internal conventions, not literature.
- **Roary 95 % vs 99 %** core — conflicting conventions; record the exact tool+flag.
- **TMHMM ">18 expected TM-aa"**, **Rhea quartet ID-offset glyphs** — unverified
  to a fetched primary source (see per-axis logs).
- **InterPro's internal Jaccard/containment-index numbers** — method named, values
  unpublished; rely on the accession mapping, not a recomputed number.

---

## 4. Implied code follow-ups

- `build_structural_equivalence.py`: relabel the 0.7 tier `-superfamily-heuristic`
  and treat all TM edges as REVIEW (not merge); consider raising the fold review
  floor toward 0.6 where a second signal is absent.
- Overlays should emit **containment edges** (`narrow_match`/`part_of`/`member_of`)
  from the source hierarchies (EC partial→leaf, GO is_a/part_of, CATH/SCOP levels,
  Reactome hasEvent, pangenome band nesting), routed to `trait_relations` — the
  existing `migrate_trait_relations.py` is the natural home to extend.
- EVOLUTION: add the 5 fields above before any EVO equivalence is attempted.
