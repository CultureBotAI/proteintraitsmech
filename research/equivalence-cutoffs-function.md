---
topic: equivalence and containment cutoffs for the FUNCTION trait axis
date: 2026-07-04
question: >-
  For the FUNCTION-axis operators (FUNC_ENZYMATIC_ACTIVITY, FUNC_PATHWAY,
  FUNC_TRANSPORT, FUNC_RESISTANCE, FUNC_INTERACTION_PARTNER,
  FUNC_ORTHOLOG_GROUP, FUNC_PROTEIN_FAMILY), when are two function traits the
  SAME (equivalence + cutoffs) and when is one CONTAINED IN the other
  (subsumption)? Map each to the correct Biolink predicate.
status: cited deep-research report (adversarially verified)
scope: research only — no code or records changed
---

# Equivalence and containment cutoffs — FUNCTION axis

## Purpose and scope

This report backs the FUNCTION rows of the merge-within-axis operator matrix
(`.claude/skills/merge-within-axis/reference/axis-operators.md`, §FUNCTION) with
primary-source citations and, crucially, works out the **containment /
subsumption** relationships that the equivalence operator alone does not
capture. Equivalence answers "are these the same trait?" (→ merge or
`close_match`); containment answers "is X a special case or a part of Y?" (→
`narrow_match`/`broad_match`, `subclass_of`, `part_of`/`has_part`, `member_of`)
— a relation that is **never a merge**.

The FUNCTION operators and their ontology anchors (from `skill.md` /
`axis-operators.md`):

| Category | Anchor | Repo builder |
|----------|--------|--------------|
| `FUNC_ENZYMATIC_ACTIVITY` | EC leaf + Rhea (ChEBI participants) | `build_function_anchor_equivalence.py` |
| `FUNC_PATHWAY` | GO biological-process + constituent EC-set | `build_pathway_overlap_equivalence.py` |
| `FUNC_TRANSPORT` | TCDB TC number | `build_function_anchor_equivalence.py` |
| `FUNC_RESISTANCE` | CARD/ARO id | `build_function_anchor_equivalence.py` |
| `FUNC_INTERACTION_PARTNER` | PSI-MI interaction type | `build_function_anchor_equivalence.py` |
| `FUNC_ORTHOLOG_GROUP` | COG / OrthoDB / eggNOG group | — (relation only) |
| `FUNC_PROTEIN_FAMILY` | family signature | — |

**Repo-internal cutoffs already in force** (from
`research/cross-source-comparison-review-1.md` and `axis-operators.md`), reused
below where an external "same" threshold does not exist:
- Member/Jaccard: `J ≥ 0.90` → merge candidate; `0.50 ≤ J < 0.90` →
  `close_match`; containment `C ≥ 0.90` → `narrow_match`.
- Pathway EC-set: Jaccard `overlaps`; `close_match` only at `≥ 0.80` Jaccard **and**
  an agreeing label.
- The function anchor builder deliberately **excludes GO and ChEBI** as identity
  anchors (generic-anchor trap); GO/ChEBI are `has_participant`/relation, never
  identity.

---

## 1. Equivalence — when two FUNCTION traits are the SAME

### 1.1 EC / Rhea (`FUNC_ENZYMATIC_ACTIVITY`)

**EC leaf identity.** An Enzyme Commission number is a four-level hierarchy
`EC A.B.C.D`: A = main class (1–7, e.g. oxidoreductase/transferase/…), B =
subclass (functional group or substrate acted on), C = sub-subclass (specific
substrate or co-substrate/coenzyme), D = serial number of the specific enzyme
[IUBMB *A Brief Guide to Enzyme Nomenclature and Classification*; ScienceDirect
"Enzyme Commission Number" overview]. Two records with the **same 4-level leaf**
denote the same catalysed reaction class → identity-grade equivalence. IUBMB
never reuses a number: deleted/transferred numbers are retained with notes and
never reassigned, so a leaf is a stable identity key
[ScienceDirect overview; Grokipedia "Enzyme Commission number"].

**Rhea reaction identity (stronger than EC).** Rhea is an expert-curated,
non-redundant set of biochemical reactions balanced for mass and charge; it is
the enzyme-annotation vocabulary in UniProtKB [Bansal et al., *Bioinformatics*
2020, "Enzyme annotation in UniProtKB using Rhea"; Rhea NAR 2022]. A **shared
Rhea reaction id is the strongest same-reaction signal** → `biolink:same_as`
(this is why the operator table gives Rhea `same_as` but EC-leaf only
`close_match`). Rhea is finer-grained than EC: **Rhea contains thousands of
reactions with no EC number**, so many distinct Rhea reactions map to the same
(or no) EC — EC-leaf identity is therefore weaker than Rhea identity
[Rhea NAR 2022, D693].

**EC ↔ Rhea mapping.** Rhea publishes `rhea2ec.tsv` (Rhea id ↔ EC number) on its
download page/FTP [Rhea download help; Rhea NAR 2022]. Because the mapping is
many-Rhea-to-one-EC (and Rhea ⊋ EC), EC→Rhea expansion is one-to-many and must
not be treated as identity in that direction.

**Rhea directionality (LR / RL / BI / master).** Rhea organises each reaction as
a **quartet** of identifiers that share identical reaction sides but differ in
net-flux direction: an undirected **master** reaction plus three directional
forms — **left-to-right (LR)**, **right-to-left (RL)** and **bidirectional (BI)**
[Rhea NAR 2022, "quartet of Rhea reaction identifiers"; Rhea help "Reaction sides
and directions"; `rhea-directions.tsv`]. Rhea help renders these as `=` (LR),
`<=>`… — see verification log for the exact glyph/offset caveat. For
equivalence: **collapse a quartet to its master** before comparing; two records
whose masters agree are the same reaction regardless of the annotated direction.
`rhea-directions.tsv` maps undirected → LR/RL/BI so this normalisation is
deterministic [Rhea download help].

- **same_as**: identical Rhea reaction id (or identical Rhea master after
  direction-normalisation).
- **close_match**: identical EC 4-level leaf, with an agreeing Rhea id /
  participant set as the second signal.
- **has_participant** (RO:0000057): ChEBI substrate/product — a *relation*, not
  identity (generic-anchor trap).

### 1.2 GO (used for `FUNC_PATHWAY` GO-BP anchor; also FUNC entry-level terms)

**Identity = same term ID only.** GO is a DAG with `is_a`, `part_of`, `has_part`,
`regulates` edges; a child is always more specialised than its parent, and a term
may have multiple parents [GeneOntology.org "Relations in the GO"; GO overview].
Two GO annotations are equivalent **only when the term CURIE is identical** —
GO exposes no "equivalent term" relation, and subsumption is emphatically not
identity (§2.2).

**Why broad GO ≠ identity — information content (IC).** IC-based semantic
similarity (introduced to GO by Lord et al. 2003) weights a term by
`IC(t) = −log p(t)`, where `p(t)` is the annotation frequency of `t` (and its
descendants) in a corpus such as UniProtKB. A **generic/shallow** term (near the
root, high `p`) has low IC and carries little functional meaning; a **specific**
term (deep, low `p`) has high IC [Mazandu & Mulder, *BioMed Res Int* 2013,
"Information Content-Based GO Semantic Similarity… Unified Framework"; GOSemSim,
Yu et al. *Bioinformatics* 2010]. The named measures:
- **Resnik**: similarity = IC of the Most Informative Common Ancestor (MICA)
  [Resnik 1995; GOSemSim].
- **Lin**: `2·IC(MICA) / (IC(t1)+IC(t2))` — normalises Resnik by the two terms'
  own IC (range 0–1) [Lin 1998; GOSemSim].
- **Jiang–Conrath**: a distance `IC(t1)+IC(t2) − 2·IC(MICA)` (shortest-path +
  MICA IC) [Jiang & Conrath 1997; GOSemSim].
- **Wang**: graph-based ("S-value"), aggregates weighted `is_a`/`part_of`
  contributions of common ancestors, corpus-independent [Wang et al. 2007;
  GOSemSim].

**Threshold for "same": there is no canonical cutoff (see verification log).**
No primary source defines a universal semantic-similarity value at which two GO
terms become "the same" — similarity is used for *clustering/reduction* and
*candidate generation*, not identity. E.g. `rrvgo` reduces GO lists by cutting a
similarity dendrogram at a user threshold (docs use 0.7/0.9) and keeping the
highest-IC representative — a *summarisation* threshold, not an equivalence proof
[Sayols, *rrvgo*, F1000/Bioconductor 2023]. **Consequence for the repo: GO-BP is
used as a *shared anchor* for pathway `close_match`, with generic BP terms capped
by `--max-group` (the IC cutoff, operationalised as a frequency cap), never as an
autonomous identity signal** [`axis-operators.md` §FUNC_PATHWAY / open gaps]. The
generic-anchor trap is precisely the low-IC failure mode.

### 1.3 Pathway (`FUNC_PATHWAY`)

**No universal "same pathway" metric; overlap is measured, not equated.** Same-
pathway calls rest on gene/enzyme-set overlap:
- **Jaccard** `|A∩B| / |A∪B|` — 1 for identical sets, 0 for disjoint
  [Wadi et al.; metabolomics ORA recommendations, *PLOS Comp Biol* 2021].
- **Overlap (Szymkiewicz–Simpson) coefficient** `|A∩B| / min(|A|,|B|)` —
  normalises by the *smaller* set, so it is robust to the large size differences
  between pathway definitions and, by construction, **= 1 when one set is a
  subset of the other** (the containment signal, §2.3) [metabolomics ORA
  recommendations, *PLOS Comp Biol* 2021].

**Cross-database caution — shared enzymes ≠ same pathway.** Reactome- and
KEGG-derived gene sets show **most Jaccard scores below 0.1**, i.e. the databases
are largely complementary, not redundant; the same enzyme appears in many
pathways [Reactome/KEGG gene-set comparison; Altman et al. MetaCyc vs KEGG
systematic comparison, *BMC Bioinformatics* 2013]. Therefore:
- **`close_match`** (pathway ≈ pathway) only on a **shared GO biological-process
  anchor** (generic BP capped), OR constituent **EC-set Jaccard ≥ 0.80 with an
  agreeing label** [`axis-operators.md`, open gaps].
- **`overlaps`** for any lower EC-set Jaccard — two pathways sharing enzymes are
  related, never identical (pathway ≠ enzyme trap).
- A `FUNC_PATHWAY` sharing one EC with a `FUNC_ENZYMATIC_ACTIVITY` is **not**
  equivalent — different granularity (§2.3).

### 1.4 TCDB (`FUNC_TRANSPORT`)

TC numbers are a 5-tier code `V.W.X.Y.Z`: V = class, W = subclass (letter),
X = family (sometimes superfamily), Y = subfamily, Z = specific transport
system/substrate; the system is explicitly "analogous to the EC system…except
that it incorporates both functional and phylogenetic information" [Saier et al.,
TCDB, *NAR* 2006/2014/2021]. **Equivalence = same TC family id** at the
X (family) level for family-grade traits, or the full `V.W.X.Y.Z` for a specific
system. → `close_match` (single-source today, so no cross-source second signal
yet).

### 1.5 CARD / ARO (`FUNC_RESISTANCE`)

The Antibiotic Resistance Ontology (ARO) organises AMR genes, mutations,
mechanisms, drugs and targets; CARD's four primary classification tags are
**AMR Gene Family, Drug Class, Resistance Mechanism, Antibiotic** [CARD 2020,
*NAR*; CARD 2023, *NAR*; arpcard/aro]. **Equivalence = same ARO id** →
`close_match` (single-source today). ARO's relational edges (`is_a`,
`confers_resistance_to_antibiotic`, `confers_resistance_to_drug_class`,
`part_of`, `regulates`) are hierarchy/relation signals, not identity
[arpcard/aro; CARD 2020].

### 1.6 PSI-MI interaction type (`FUNC_INTERACTION_PARTNER`)

PSI-MI is the HUPO-PSI controlled vocabulary for molecular interactions; the
interaction-type branch is a hierarchy of increasing specificity:
`association` (MI:0914) ⊃ `physical association` (MI:0915) ⊃
`direct interaction` (MI:0407), alongside `colocalization` (MI:0403) and
`genetic interaction` [Sivade Dumousseau et al. PSI-MI XML3.0; OLS MI:0407;
PSICQUIC]. **Equivalence = same, equally-specific MI interaction-type id** →
`close_match`; the interacting entities themselves relate by `interacts_with`.
Two records at *different* levels of the MI branch are subsumption, not identity
(§2.5).

### 1.7 COG / OrthoDB / eggNOG (`FUNC_ORTHOLOG_GROUP`) and `FUNC_PROTEIN_FAMILY`

An orthologous group is "a cluster of three or more homologous sequences that
diverge from the same speciation event"; each COG "assembles the descendants
from the same gene in the ancestral genome"; OrthoDB clusters best-reciprocal-
hits; eggNOG adds hierarchical (taxon-level) resolution of groups [NCBI COG
project; OrthoDB *NAR* 2013; eggNOG v7 2025]. Because different resources cluster
by different procedures at different taxonomic scopes, **two ortholog groups are
treated as membership, not identity**: a protein/record is `member_of` a group;
groups themselves are only asserted equal on an **identical group id**. The
operator table gives `FUNC_ORTHOLOG_GROUP` `member_of` (a relation), **never a
merge**.

---

## 2. Containment / subsumption — "X contained in Y"

This is the part the equivalence operator misses. Each case maps to a Biolink
predicate (directional: **subject → object**).

### 2.1 EC partial ⊃ EC leaf

A **partial EC number** uses a hyphen for an unspecified sub-subclass/serial:
`EC 1.1.1.-` fixes class/subclass/sub-subclass but leaves the serial number
unspecified [IUBMB nomenclature; ExplorEnz; used in EMBL/KEGG/UniProt]. Thus
`EC:1.1.1.1` (alcohol dehydrogenase) is **subsumed by** `EC:1.1.1.-`, which is
subsumed by `EC:1.1.-.-`, etc. This is a class hierarchy:
- specific leaf → partial parent: `biolink:subclass_of` (rdfs:subClassOf) or,
  cross-schema, `biolink:narrow_match` (leaf is narrower than the partial).
- partial parent → leaf: `biolink:broad_match`.

(The letter-`n` convention, e.g. `EC 2.3.4.n`, marks a characterised enzyme
awaiting an official number — a different case from the hyphen placeholder
[IUBMB].)

### 2.2 GO `is_a` and `part_of` (specific GO-BP ⊂ broad GO-BP)

- **`is_a`** — "A is a subtype of B" [GeneOntology.org]. A specific biological
  process is subsumed by its ancestors up the `is_a` chain (true-path rule: the
  path from a child to its top-level parent must always hold) [GO overview;
  Primer on the GO]. → subject (specific) `biolink:subclass_of` object (broad);
  cross-schema `narrow_match`/`broad_match`.
- **`part_of`** — B `part_of` A means "wherever B exists, it is as part of A, and
  the presence of B implies the presence of A; but given A we cannot say B
  exists" (necessary-part, not necessary-whole) [GeneOntology.org
  "Relations in the GO"]. This decomposes a process into sub-steps. → subject
  (the part) `biolink:part_of` (BFO:0000050) object (the whole); inverse
  `has_part` (BFO:0000051).
- Because a broad GO term subsumes many specifics, a **broad GO anchor is never
  identity** — it is exactly the low-IC generic-anchor trap of §1.2.

### 2.3 Pathway partonomy (reaction/step ⊂ pathway ⊂ superpathway)

Reactome models everything as **Events**; a pathway `hasEvent` its sub-pathways
and reactions, recursively, from top-level pathways down to individual reactions;
"arc edges represent the `part_of` relationships between pathways and
subpathways" [Reactome *NAR* 2020; Reactome pathway-browser/hierarchy docs;
reactome2py ContentService]. Mapping:
- a reaction/step → its pathway: `biolink:part_of`.
- a sub-pathway → its (super)pathway / module → superpathway: `biolink:part_of`
  (inverse `has_part`, mirroring Reactome `hasEvent`).
- an enzyme/EC that catalyses a step of a pathway → the pathway:
  **not `part_of`** — the enzyme *participates*; use `biolink:has_participant`
  (pathway → enzyme) / participates-in (RO:0000056, enzyme → pathway). This
  keeps `FUNC_ENZYMATIC_ACTIVITY` distinct from `FUNC_PATHWAY`.
- Overlap-coefficient = 1 (one enzyme-set ⊆ the other, §1.3) is a **containment**
  signal → `narrow_match`, not `close_match`.

### 2.4 TC family ⊃ subfamily; ARO hierarchy

- **TCDB**: family (X) subsumes subfamily (Y) subsumes the specific system (Z):
  `V.W.X.Y.Z` narrows at each step [TCDB *NAR*]. subfamily → family:
  `biolink:subclass_of` / `narrow_match`.
- **ARO**: the ontology's own `is_a` edges give the hierarchy (a specific gene
  `is_a` an AMR Gene Family) → `biolink:subclass_of`/`narrow_match`; the
  functional edge `confers_resistance_to_antibiotic` /
  `confers_resistance_to_drug_class` is a *relation* (RO/ARO relation, not
  Biolink `same_as`), best carried as `related_to` or an RO fallback, never a
  merge [arpcard/aro; CARD 2020].

### 2.5 Ortholog-group membership; PSI-MI type specificity

- **Ortholog group**: a protein/record → its COG/OrthoDB/eggNOG group is
  `biolink:member_of` (RO:0002350); eggNOG's nested (taxon-level) groups relate
  child group → parent group by `part_of`/`subclass_of` [eggNOG v7; NCBI COG].
  **Membership is never a record merge.**
- **PSI-MI**: `direct interaction` (MI:0407) → `physical association` (MI:0915)
  → `association` (MI:0914) is an `is_a` chain of increasing specificity
  [OLS MI:0407; PSICQUIC]. A more specific interaction-type record →
  less-specific: `biolink:subclass_of` / `narrow_match`.

---

## Deliverable (a): Cutoffs table — equivalence rules

| Operator (category) | Equivalence rule + cutoff | Predicate | Source |
|---|---|---|---|
| `FUNC_ENZYMATIC_ACTIVITY` (Rhea) | identical Rhea reaction id, after normalising the LR/RL/BI quartet to its **master** | `biolink:same_as` (owl:sameAs / skos:exactMatch) | Rhea NAR 2022 D693; `rhea-directions.tsv`; Biolink same_as doc |
| `FUNC_ENZYMATIC_ACTIVITY` (EC) | identical **4-level EC leaf** `A.B.C.D` + agreeing Rhea/participant set (2nd signal) | `biolink:close_match` (skos:closeMatch) | IUBMB Brief Guide; ScienceDirect EC overview; Biolink close_match doc |
| EC↔Rhea bridge | `rhea2ec.tsv`; many-Rhea→one-EC, so EC→Rhea is not identity | `close_match` (Rhea→EC dir. only) | Rhea download help; Rhea NAR 2022 |
| ChEBI substrate/product | shared participant is a **relation, not identity** | `biolink:has_participant` (RO:0000057) | `axis-operators.md` trap 3 |
| `FUNC_PATHWAY` (GO-BP) | shared **GO biological-process** anchor, generic BP capped (`--max-group`; low-IC terms excluded) | `biolink:close_match` | `axis-operators.md`; Mazandu 2013 (IC) |
| `FUNC_PATHWAY` (EC-set) | constituent **EC-set Jaccard ≥ 0.80 + agreeing label** = close; lower = overlaps | `close_match` (≥0.80) / `biolink:overlaps` | `axis-operators.md`; PLOS Comp Biol 2021 |
| `FUNC_TRANSPORT` (TCDB) | same TC family id (X level) / full `V.W.X.Y.Z` for a system | `biolink:close_match` | TCDB NAR 2006/2021 |
| `FUNC_RESISTANCE` (ARO) | same ARO id | `biolink:close_match` | CARD 2020/2023 NAR; arpcard/aro |
| `FUNC_INTERACTION_PARTNER` (PSI-MI) | same, equally-specific MI interaction-type id | `biolink:close_match`; `interacts_with` for entities | OLS MI:0407; PSICQUIC |
| `FUNC_ORTHOLOG_GROUP` (COG/OrthoDB/eggNOG) | identical group id only; otherwise **membership, not identity** | `biolink:member_of` (relation) | NCBI COG; OrthoDB NAR 2013; eggNOG v7 |
| GO term (generic) | semantic similarity (Resnik/Lin/JC/Wang) — **no canonical "same" cutoff**; identity = same term ID | (candidate only, not identity) | GOSemSim 2010; rrvgo 2023; Mazandu 2013 |

## Deliverable (b): Relationships table — containment / subsumption

| Containment case | Direction (subject → object) | Predicate (CURIE) | Source |
|---|---|---|---|
| EC leaf ⊂ partial EC (`1.1.1.1` ⊂ `1.1.1.-`) | leaf → partial | `biolink:subclass_of` (rdfs:subClassOf); x-schema `narrow_match` | IUBMB; ExplorEnz |
| partial EC ⊃ leaf | partial → leaf | `biolink:broad_match` (skos:broadMatch) | IUBMB |
| specific GO-BP ⊂ broad GO-BP (`is_a`) | specific → broad | `biolink:subclass_of` | GeneOntology relations; GO overview |
| GO process step ⊂ process (`part_of`) | part → whole | `biolink:part_of` (BFO:0000050); inv. `has_part` | GeneOntology relations |
| reaction/step ⊂ Reactome pathway (`hasEvent`) | step → pathway | `biolink:part_of` | Reactome NAR 2020 |
| sub-pathway ⊂ pathway ⊂ superpathway | sub → super | `biolink:part_of`; inv. `has_part` | Reactome hierarchy docs |
| enzyme/EC catalyses a pathway step | pathway → enzyme | `biolink:has_participant` (RO:0000057) / participates-in RO:0000056 | pathway≠enzyme trap; RO |
| pathway enzyme-set ⊆ other (overlap-coef = 1) | subset → superset | `biolink:narrow_match` | PLOS Comp Biol 2021 |
| TC subfamily ⊂ TC family (`…Y` ⊂ `…X`) | subfamily → family | `biolink:subclass_of` / `narrow_match` | TCDB NAR |
| ARO gene ⊂ AMR Gene Family (`is_a`) | gene → family | `biolink:subclass_of` / `narrow_match` | arpcard/aro; CARD 2020 |
| ARO confers-resistance (functional edge) | gene → drug/class | `biolink:related_to` (RO fallback; ARO `confers_resistance_to_*`) | arpcard/aro |
| protein/record ∈ ortholog group | record → group | `biolink:member_of` (RO:0002350) | NCBI COG; eggNOG v7 |
| eggNOG child group ⊂ parent group | child → parent | `biolink:part_of` / `subclass_of` | eggNOG v7 |
| PSI-MI `direct interaction` ⊂ `physical association` ⊂ `association` | specific → general | `biolink:subclass_of` / `narrow_match` | OLS MI:0407; PSICQUIC |

**Merge-safety reminder** (from `skill.md` tier table): only `same_as`/R1/R2
auto-merge; `close_match` is a **review** candidate needing a second signal;
`narrow_match`/`broad_match`/`subclass_of`/`part_of`/`has_part`/`member_of`/
`overlaps`/`has_participant` are **relations kept as `trait_relations`, never a
merge**.

## Deliverable (c): Verification log

**Directly fetched / quoted (high confidence):**
- Biolink `same_as` def + `owl:sameAs`/`skos:exactMatch` mappings — fetched
  biolink-model doc. VERIFIED.
- Biolink `close_match` (skos:closeMatch; parent `related_to_at_concept_level`,
  child `exact_match`) and `narrow_match` (skos:narrowMatch; inverse
  `broad_match`) — fetched biolink-model docs. VERIFIED.
- GO `is_a` / `part_of` / `has_part` / `regulates` definitions — fetched
  GeneOntology.org relations page (exact necessary-part wording). VERIFIED.
- Overlap (Szymkiewicz–Simpson) coefficient normalises by the smaller set /
  preferred over Jaccard for differently-sized pathways — fetched PLOS Comp Biol
  2021 (exact quote). VERIFIED. **The "= 1 when one set is a subset" property is
  definitional math (|A∩B|/min(|A|,|B|) with A⊆B), NOT a direct quote** — the
  fetched paper did not state it verbatim. VERIFIED-BY-DEFINITION.

**From search snippets (medium confidence — corroborated across ≥2 results):**
- EC 4-level structure and hyphen-placeholder semantics; IUBMB never reuses
  numbers. VERIFIED (multiple sources).
- Rhea quartet = master + LR/RL/BI; rhea2ec.tsv / rhea-directions.tsv exist;
  Rhea ⊋ EC (reactions without EC). VERIFIED (Rhea NAR 2022 + Rhea help snippets).
- TCDB 5-tier `V.W.X.Y.Z` and "analogous to EC + phylogenetic". VERIFIED (TCDB NAR).
- CARD/ARO tags and `is_a`/`confers_resistance_to_*` edges. VERIFIED (CARD NAR + arpcard/aro).
- PSI-MI association(MI:0914) ⊃ physical association(MI:0915) ⊃ direct
  interaction(MI:0407). VERIFIED (OLS + PSICQUIC snippets).
- COG/OrthoDB/eggNOG group definitions. VERIFIED (NCBI/OrthoDB/eggNOG snippets).
- GO IC = −log(annotation frequency); Resnik/Lin/JC/Wang definitions. VERIFIED
  (GOSemSim + Mazandu 2013).

**⚠ UNVERIFIED / flagged numbers and specifics:**
1. **Rhea quartet ID offset convention** (master, master+1=LR, +2=RL, +3=BI, and
   the exact direction glyphs `=`/`<=>`): the quartet *structure* is verified but
   the precise numeric offsets and glyph-to-direction mapping were **NOT pinned to
   a primary quote** (Rhea download help returned HTTP 403; NAR paper only says
   "quartet"). Treat the offset rule as UNVERIFIED — confirm against
   `rhea-directions.tsv` columns before encoding. Normalisation-to-master is
   still valid regardless of the offset detail.
2. **GO semantic-similarity "same term" threshold**: **no canonical numeric
   cutoff exists.** Any value (e.g. rrvgo 0.7/0.9) is a *reduction/summarisation*
   threshold, not an equivalence proof. Do NOT hard-code a GO-similarity number
   as identity. UNVERIFIED-BY-DESIGN (the literature offers none).
3. **"Same pathway" Jaccard threshold**: no universal standard. The Reactome-vs-
   KEGG "most Jaccard < 0.1" figure is a *complementarity* observation, not a
   same-pathway cutoff. The repo's `EC-set Jaccard ≥ 0.80` is a **repo-internal**
   choice (`axis-operators.md`), not an externally-standard number. FLAGGED as
   repo-convention, not literature-canonical.
4. **Member/Jaccard 0.90 / 0.50 / containment 0.90 cutoffs**: these are
   **repo-internal** (`cross-source-comparison-review-1.md`), reused here for
   FUNCTION member-set cases; not external standards. FLAGGED.
5. **Biolink CURIE mappings for `subclass_of` (rdfs:subClassOf), `part_of`
   (BFO:0000050), `has_part` (BFO:0000051), `member_of` (RO:0002350),
   `has_participant` (RO:0000057), `overlaps` (RO:0002131)**: standard
   biolink-model mappings from prior knowledge; **only `same_as`, `close_match`,
   `narrow_match` were fetched this session.** The rest are STANDARD-BUT-
   UNFETCHED — confirm against the current biolink-model.yaml before encoding.

---

## References

- IUBMB, *A Brief Guide to Enzyme Nomenclature and Classification*
  (iubmb.org). — EC 4-level hierarchy, partial-EC hyphen, `n` convention.
- ScienceDirect Topics, "Enzyme Commission Number" overview. — EC levels;
  numbers never reused.
- Bansal et al. (2020) "Enzyme annotation in UniProtKB using Rhea",
  *Bioinformatics* 36(6):1896. — Rhea as UniProt enzyme vocabulary.
- Bansal/Morgat et al. (2022) "Rhea, the reaction knowledgebase in 2022",
  *NAR* 50:D693. — quartet identifiers; Rhea ⊋ EC; rhea2ec.
- Rhea help — Download; Reaction sides and directions (rhea-db.org).
- GeneOntology.org — "Relations in the Gene Ontology"; Ontology overview;
  Primer on the GO (PMC6377150). — is_a/part_of/has_part/regulates; true-path.
- Yu et al. (2010) "GOSemSim", *Bioinformatics* 26(7):976. — Resnik/Lin/JC/Wang.
- Mazandu & Mulder (2013) "Information Content-Based GO Semantic Similarity…",
  *BioMed Res Int* 2013:292063. — IC = −log p(t); shallow-annotation problem.
- Sayols (2023) "rrvgo", F1000/Bioconductor. — similarity as reduction threshold.
- Wieder et al. (2021) "Pathway analysis in metabolomics… over-representation
  analysis", *PLOS Comp Biol* 17:e1009105 (PMC8448349). — overlap coefficient
  vs Jaccard.
- Altman et al. (2013) "A systematic comparison of MetaCyc and KEGG",
  *BMC Bioinformatics* (PMC3665663). — pathway DB complementarity.
- Reactome/KEGG gene-set overlap (Jaccard < 0.1) — reactome.org research spotlight.
- Reactome (2020) *NAR* 48:D498 (PMC5753187); Reactome pathway-browser /
  hierarchy docs; reactome2py ContentService. — hasEvent / part_of partonomy.
- Saier et al. — TCDB, *NAR* 34:D181 (2006); 44:D372 (2016); 49:D461 (2021). —
  TC 5-tier V.W.X.Y.Z; analogy to EC.
- Alcock et al. — CARD 2020, *NAR* 48:D517; CARD 2023, *NAR* 51:D690;
  github.com/arpcard/aro. — ARO tags; is_a; confers_resistance_to_*.
- HUPO-PSI MI — OLS MI:0407 "direct interaction"; PSICQUIC MITAB;
  Sivade Dumousseau et al. PSI-MI XML3.0. — association/physical/direct hierarchy.
- NCBI COG project; Galperin et al. COG update *NAR* 49:D274 (2021);
  Kriventseva et al. OrthoDB *NAR* 41:D358 (2013); eggNOG v7 (2025,
  PMC12807745). — orthologous-group definitions.
- Unni et al. (2022) "Biolink Model", *Clin Transl Sci* 15:1848; biolink-model
  docs for same_as / close_match / narrow_match (fetched). — mapping predicates.
