# Trait EQUIVALENCE and CONTAINMENT for the EVOLUTION axis

**Scope.** Defines the distribution cutoffs and subsumption relationships needed to make
`EVO_CONSERVATION` and `EVO_PANGENOME` equivalence *computable*. Motivated by the
merge-within-axis skill, which marks the EVOLUTION operator **"not ready — records lack
taxon-scope / threshold fields"** (`.claude/skills/merge-within-axis/reference/axis-operators.md`,
§EVOLUTION; `skill.md` §EVOLUTION). This report supplies exactly which fields and cutoffs are needed.
It does **not** change any code or record.

**Current corpus state (verified locally, 2026-07-04).** The EVOLUTION axis holds seven
*class-level* trait definitions with **no** taxon-scope or threshold slots:
`data/traits/evolution/pangenome/{core-genome,soft-core,shell,cloud,persistent-genome,singleton}-protein.yaml`
and `data/traits/evolution/conservation/conserved-protein.yaml`. E.g.
`core-genome-protein.yaml` carries only `trait_category: EVO_PANGENOME` and prose
("present in (nearly) all genomes of a species/clade pangenome") — no `%`-present cutoff,
no taxon set, no tool. `conserved-protein.yaml` says a clade scope *would* be an
`NCBITaxon` xref, but no dedicated field exists. This confirms the skill's gap statement.

The core problem this report solves: **two EVOLUTION traits are equivalent only if they
share the SAME taxon scope AND the SAME frequency-threshold definition.** "Core-genome
protein of *E. coli*" and "core-genome protein of *Salmonella*" are *not* the same trait;
"core (≥99%)" and "soft-core (≥95%)" of the *same* taxon are *not* the same trait — one
contains the other. Without scope + threshold fields on the record, neither identity nor
containment can be decided deterministically.

---

## 1. Pangenome category cutoffs

### 1.1 The classic Tettelin core/pan-genome concept

The pan-genome concept was introduced by **Tettelin et al. 2005** (PNAS) from comparative
analysis of eight *Streptococcus agalactiae* genomes. They defined the pan-genome as
composed of (i) a **core genome** = "genes present in all strains," and (ii) a
**dispensable (accessory) genome** = "genes present in two or more strains and genes unique
to single strains" [Tettelin 2005, PubMed 16185861]. In the original framing the core is a
**strict 100%-present** set, and "accessory" splits into multi-strain genes and
**singletons** (strain-specific, present in exactly one genome). The pan-genome of a species
was shown to be *open* — each newly sequenced genome adds new genes — which is precisely why
a hard 100% core shrinks as genomes are added, motivating the relaxed percentage bands below.

### 1.2 Roary defaults — the widely-used fixed-percentage bands

Roary (Page et al. 2015, *Bioinformatics*) is the most-cited bacterial pan-genome tool and
its output partitions gene families into four frequency bands. The **canonical Roary bands**
reported across the literature are:

| Category   | Band (fraction of genomes with the gene) |
|------------|-------------------------------------------|
| **Core**       | 99% ≤ strains ≤ 100% |
| **Soft core**  | 95% ≤ strains < 99%  |
| **Shell**      | 15% ≤ strains < 95%  |
| **Cloud**      | 0% ≤ strains < 15%   |

Sources: the RIBAP paper (Lataretu et al. 2024, *Genome Biology*) states the standard scheme
verbatim — "core genes are those present in at least 99% of genomes; soft-core genes occur
in 95% to 99%; shell genes are present in 15% to 95%; and cloud genes appear in less than
15% of genomes"; Roary's own tunable **`-cd` parameter** ("percentage of isolates a gene
must be in to be core") has a **default of 99%** [Roary docs, sanger-pathogens.github.io/Roary;
Sitto & Battistuzzi 2020 MBE protocol, oup.com/mbe/article/37/3/933]. The 15% and 95% shell
boundaries are Roary's `Rtab`/`accessory` conventions rather than a single tunable flag —
see the **Verification log** for the caveat on these two numbers.

### 1.3 Why the cutoff matters, and the 95% vs 99% ambiguity

The core/soft-core cutoff is a **modelling choice, not a biological constant**. Lowering the
core cutoff from 100% → 99% materially increases the detected core-gene count in genus-level
comparisons (large effect for *Klebsiella*/*Brucella*, small for *Chlamydia*/*Enterococcus*)
[RIBAP, Genome Biology 2024]. The pan-genome is explicitly framed as "a statistical model,
not a fixed biological property" [Bioinformatics Advances 2025, vbag069]. Consequently, a
"core" trait is only meaningful *relative to a stated cutoff*, and the community uses
several: strict **100%**, relaxed **99%** (Roary `-cd` default), and a very common **95%**
convention (often cited as popularised by Roary's soft-core option); a **90%** soft-core
threshold is also recommended as the most frequently applied [PPanGGOLiN paper, PLOS Comp
Biol 2020]. **Implication for equivalence:** the numeric cutoff must be stored on the record,
because "core@100%", "core@99%", and "core@95%" denote genuinely different (nested) sets.

### 1.4 PPanGGOLiN — statistical partitioning (persistent / shell / cloud)

PPanGGOLiN (Gautreau et al. 2020, *PLOS Comp Biol*) deliberately **does not use fixed
percentage thresholds.** It partitions gene families into **persistent**, **shell**, and
**cloud** using a two-stage statistical model:

1. a **multivariate Bernoulli Mixture Model** over gene-family presence/absence, fit by
   **Expectation-Maximization**; combined with
2. a **hidden Markov Random Field (MRF)** whose graph structure is the pangenome
   neighbourhood graph (a smoothing parameter β makes genomically adjacent families tend to
   the same partition).

[PPanGGOLiN, PMC7108747 / journals.plos.org/ploscompbiol PCBI.1007732]. Biologically:
**persistent** ≈ conserved backbone present in almost all genomes (analogous to core but
statistically defined); **shell** ≈ intermediate-frequency, lineage-specialising genes;
**cloud** ≈ low-frequency, recently acquired / rare genes. **Key contrast:** because the
partition is inferred from occurrence *patterns + graph topology*, the same partition label
("persistent") can correspond to a **different effective frequency band per dataset**. A
PPanGGOLiN "persistent" trait is therefore **not** interchangeable with a Roary "core@99%"
trait even for the same taxon — the *definition method* differs (statistical vs fixed-%),
so `tool`/`method` must be a stored field.

### 1.5 Other tools (defaults)

- **BPGA** (Chaudhari et al. 2016, *Sci Rep*): core = present in all, accessory = 2..n−1,
  unique = single strain; classification driven by a **sequence-identity clustering cutoff**
  (default 50% identity via USEARCH), *not* a frequency-band cutoff [PMC4829868]. So BPGA's
  "core" ≈ Tettelin 100% core, but its clustering identity threshold is a separate axis of
  variation — record it too when a record derives from BPGA.
- **panX** (Ding et al. 2018): core vs accessory by presence fraction; the interactive
  default core threshold is commonly **100%** (relaxable) — see Verification log (UNVERIFIED
  exact default).
- **Roary singleton/unique**: a gene in exactly one isolate is a **singleton** — a special
  case of cloud (frequency = 1/N).

---

## 2. Conservation cutoffs

### 2.1 Breadth-of-conservation (ortholog presence across a taxon set)

Conservation is scored by **ortholog presence across a defined taxon set**; the trait is a
function of *breadth* (how many/which taxa retain an ortholog), which maps onto conventional
qualitative bands:

| Conservation class      | Meaning | Typical operationalisation |
|-------------------------|---------|-----------------------------|
| **Universal / near-universal** | ortholog in (nearly) all sampled taxa across the tree of life | present in ≥ ~90–100% of a broad taxon panel (e.g. across domains). No single canonical numeric cutoff — see log. |
| **Broadly conserved / clade-core** | ortholog across a large clade | present across most members of a phylum/class-level set |
| **Clade-specific / lineage-restricted** | ortholog confined to one clade (family/genus/species) | present in the clade, **absent** outside it |
| **Lineage-specific / orphan (ORFan)** | no detectable ortholog outside the focal lineage/genome | singleton at the chosen taxon rank |

There is **no field-wide fixed numeric threshold** for "conserved" the way Roary fixes core
at 99%; conservation cutoffs are defined *per study* by (a) the **taxon panel** and (b) the
**ortholog-detection method/E-value/identity** used. Marker-gene frameworks make this
concrete with fixed panels — e.g. **BUSCO** (Simão et al. 2015) defines "near-universal
single-copy orthologs" *expected present in >90% of species* of a given lineage set; **COG**
and **OrthoDB** likewise score conservation by presence across a fixed clade tree. The
practical consequence mirrors the pangenome case: **a conservation trait is only equivalent
to another if the taxon panel (scope) and the presence-breadth definition match.**

### 2.2 dN/dS (ω) selection regimes — a *distinct* conservation signal

If conservation is scored by **selective constraint** rather than presence, the standard
metric is ω = dN/dS (nonsynonymous/synonymous substitution rate ratio):

| ω (dN/dS) | Regime | Interpretation |
|-----------|--------|----------------|
| **ω < 1** | purifying / negative selection | amino-acid changes selected against → conserved |
| **ω ≈ 1** | neutral | changes neither favoured nor disfavoured |
| **ω > 1** | positive / diversifying selection | changes advantageous |

[Yang & Nielsen; Ka/Ks ratio, en.wikipedia.org/wiki/Ka/Ks_ratio; MBE 32(4):1097]. Caveat
from the primary literature: the ω = 1 neutral threshold is **sensitive to model
assumptions** — if synonymous codons differ in fitness, ω can exceed 1 under purely purifying
selection [PLoS Genet 2008, pgen.1000304; MBE 2015]. **Modelling note:** a presence-breadth
conservation trait and a dN/dS-constraint conservation trait are **different definitions of
"conserved"** and must NOT be treated as equivalent — store which one a record uses.

---

## 3. Containment / subsumption (X contained in Y)

Two mechanisms generate containment on the EVOLUTION axis: **threshold nesting** (same
taxon, different frequency cutoff) and **taxon nesting** (same definition, nested clades).

### 3.1 Threshold nesting — stricter band ⊂ looser band

For "present-in-≥X%" bands over the **same taxon set**, a **stricter (higher) threshold set
is a SUBSET of a looser (lower) one**: every gene present in ≥99% of genomes is also present
in ≥95%. Therefore, as *sets of gene families*:

> **core(≥99%) ⊆ soft-core-inclusive(≥95%) ⊆ shell-inclusive(≥15%) ⊆ pan-genome(>0%)**

i.e. **core is the narrower / stricter subset**; the looser band is the broader superclass.
(Note the two readings of "soft-core": as an *inclusive* cumulative band ≥95% it is a
superset of core; as the Roary *exclusive* band 95–99% it is disjoint from core. State which.)
So the subsumption direction is: a **stricter-cutoff trait `narrow_match`/`subclass_of` a
looser-cutoff trait of the same taxon**; the looser one is `broad_match` of the stricter.
Same trait at two different thresholds is therefore a **broader/narrower (containment)
relationship, never equivalence.**

### 3.2 Taxon nesting — narrower clade ⊂ broader clade

Conservation/pangenome scope nests with the NCBI taxonomy: a trait defined over a **narrower
clade is a subclass of the same trait over a broader clade** that contains it — genus-level
scope ⊂ family-level scope ⊂ order-level … A "conserved within genus *Escherichia*" trait is
`subclass_of` "conserved within family *Enterobacteriaceae*". Equivalently a **clade-specific
conservation trait ⊂ a broader-taxon conservation trait.** Direction: **narrower taxon
`narrow_match`/`subclass_of` broader taxon**; broader taxon `broad_match` of narrower.

### 3.3 Predicate mapping (Biolink + RO)

Biolink mapping predicates use SKOS granularity (`exact`/`close`/`broad`/`narrow`/`related`)
[Biolink Model, biolink.github.io/biolink-model; arXiv 2203.13906]. Applied to EVOLUTION:

| Situation | Direction | Biolink predicate | Also / RO |
|-----------|-----------|-------------------|-----------|
| Same taxon scope **and** same threshold definition (incl. same tool/method) | symmetric | `biolink:same_as` (if identical) / `biolink:close_match` | — |
| Same category, same scope, **different numeric threshold** | stricter → looser | stricter `biolink:narrow_match` looser; looser `biolink:broad_match` stricter | `biolink:subclass_of`; `RO:0002131` (part-of set sense, optional) |
| Same definition, **nested taxon** (genus ⊂ family) | narrower → broader | narrower `biolink:narrow_match`/`biolink:subclass_of` broader | taxon nesting via `NCBITaxon` `rdfs:subClassOf` |
| Different definition **method** (Roary-% vs PPanGGOLiN-statistical vs dN/dS) for otherwise same intent | — | `biolink:related_to` / `biolink:close_match` only after human review | never auto-`same_as` |
| Fixed-band membership relations (a specific protein is *in* the core set) — instance level | — | `biolink:member_of` | `RO:0002350` member_of |

Per the merge-within-axis tier table: only `same_as` (and R1/R2 identity) auto-merge;
`close_match` is a **review candidate**; `narrow_match`/`broad_match`/`subclass_of`/`member_of`
are **hierarchy/relations, never a merge.** So threshold- and taxon-nesting cases are
**containment edges to keep, not merges.**

---

## Deliverable (a) — Cutoffs table

| Category | Defining threshold | Tool / source |
|----------|--------------------|---------------|
| Core (strict) | present in **100%** of genomes | Tettelin et al. 2005, PNAS (PubMed 16185861) |
| Core (relaxed) | present in **≥99%** of genomes (`-cd` default = 99) | Roary (Page 2015); docs sanger-pathogens.github.io/Roary |
| Soft-core | present in **95%–99%** (exclusive band); or ≥95% inclusive; 90% also common | Roary bands via RIBAP (Genome Biology 2024); PPanGGOLiN paper (90% note) |
| Shell | present in **15%–95%** | Roary bands via RIBAP (Genome Biology 2024) |
| Cloud | present in **<15%** | Roary bands via RIBAP (Genome Biology 2024) |
| Singleton / unique | present in **exactly 1** genome (freq = 1/N) | Tettelin 2005; Roary |
| Persistent | statistical (Bernoulli-mixture + MRF), **no fixed %** | PPanGGOLiN (Gautreau 2020, PCBI.1007732) |
| Shell (PPanGGOLiN) | statistical intermediate-frequency partition | PPanGGOLiN 2020 |
| Cloud (PPanGGOLiN) | statistical low-frequency partition | PPanGGOLiN 2020 |
| BPGA core / accessory / unique | present-in-all / 2..n−1 / single; clustering identity default **50%** | BPGA (Chaudhari 2016, PMC4829868) |
| Universal / near-universal conservation | ortholog present across (nearly) all of a broad taxon panel; **BUSCO panels: >90% of species** | BUSCO (Simão 2015); COG/OrthoDB conventions |
| Clade-specific / lineage-specific | ortholog confined to a stated clade / absent outside it | OrthoDB/EggNOG; general usage |
| Purifying selection (conserved by constraint) | **ω = dN/dS < 1** | Ka/Ks; Yang & Nielsen; MBE 32(4):1097 |
| Neutral | **ω ≈ 1** | as above |
| Positive/diversifying | **ω > 1** | as above |

## Deliverable (b) — Relationships (containment) table

| Containment case | Direction | Predicate | Source/justification |
|------------------|-----------|-----------|----------------------|
| core(≥99%) within soft-core-inclusive(≥95%), same taxon | core ⊂ soft-core | core `narrow_match`/`subclass_of` soft-core | set logic on present-in-≥X% bands; RIBAP threshold effect |
| Any stricter-% band within looser-% band, same taxon | stricter ⊂ looser | `narrow_match` (stricter) / `broad_match` (looser) | monotonic subset of ≥X% sets |
| Same category, different numeric cutoff (core@100 vs core@99) | stricter ⊂ looser | `narrow_match`; NOT `same_as` | Bioinformatics Advances 2025 (model, not constant) |
| Genus-level scope within family-level scope | narrower ⊂ broader | narrower `subclass_of`/`narrow_match` broader | NCBITaxon clade nesting |
| Clade-specific conservation within broad conservation | narrower ⊂ broader | `narrow_match`/`subclass_of` | taxon-panel nesting |
| PPanGGOLiN persistent vs Roary core, same taxon | not nested (different method) | `related_to`/`close_match` review only | PPanGGOLiN statistical ≠ fixed-% |
| dN/dS-conserved vs presence-conserved | not nested (different metric) | `related_to` only | different definition of "conserved" |
| Specific protein ∈ a pangenome partition | instance→class | `member_of` (`RO:0002350`) | class vs instance |
| Same taxon + same threshold + same method | equivalent | `same_as` / `close_match` | the only equivalence condition |

## Deliverable (c) — Verification log

| Claim | Status | Note |
|-------|--------|------|
| Roary core `-cd` default = **99%** | **VERIFIED** | Roary docs + MBE protocol both state `-cd` default 99. |
| Bands core≥99 / soft 95–99 / shell 15–95 / cloud <15 | **VERIFIED (secondary)** | Stated verbatim in RIBAP (Genome Biology 2024) and multiple reviews; the original Page 2015 Roary paper and the MBE protocol give the 99% core `-cd` default but do **not** print the 15%/95% shell/cloud boundaries. The 15% and 95% boundaries are Roary output conventions attributed via secondary literature, not a single tunable Roary flag — **flagged as secondary-sourced**. |
| "Roary default core is **95%**" (from PPanGGOLiN paper text) | **CONFLICT — UNRESOLVED** | The `-cd` default is 99%, but the PPanGGOLiN paper and some reviews attribute a popular **95%** convention to Roary (likely its soft-core usage). Treat "core@95%" and "core@99%" as *distinct* thresholds; do not assert a single "Roary default." |
| PPanGGOLiN = Bernoulli mixture + EM + hidden MRF, no fixed % | **VERIFIED** | PPanGGOLiN paper (PMC7108747 / PCBI.1007732). |
| Tettelin core = 100%, dispensable = ≥2 strains + singletons | **VERIFIED** | PubMed 16185861 abstract. |
| dN/dS regimes <1 / ≈1 / >1 = purifying / neutral / positive | **VERIFIED** | Ka/Ks (Wikipedia) + MBE 32(4):1097; ω=1 threshold model-sensitive (PLoS Genet 2008). |
| BPGA clustering identity default = **50%** | **UNVERIFIED (likely)** | From tool docs summary, not confirmed against BPGA source in this pass. |
| panX default core threshold = **100%** | **UNVERIFIED** | Not confirmed against panX source; commonly relaxable. |
| BUSCO "near-universal, present in >90% of species" | **VERIFIED (secondary)** | BUSCO methodology; exact wording from BUSCO papers, not re-fetched here. |
| "90% soft-core most frequently applied / recommended" | **VERIFIED (secondary)** | PPanGGOLiN paper text; a recommendation, not a universal default. |
| Biolink close/narrow/broad/exact SKOS mapping semantics | **VERIFIED** | Biolink Model docs + arXiv 2203.13906. |
| Subset direction stricter-% ⊂ looser-% | **VERIFIED (deductive)** | Set logic on monotone ≥X% membership — not an external citation. |

## Deliverable (d) — Fields the record must carry (to make EVOLUTION equivalence computable)

To let a deterministic operator decide EVOLUTION equivalence/containment, each
`EVO_PANGENOME` / `EVO_CONSERVATION` record needs:

1. **`taxon_scope`** — the reference taxon set the trait is computed over, as an
   `NCBITaxon:` CURIE (species or clade) **and its rank** (species/genus/family/…).
   *Required for both identity and taxon-nesting.*
2. **`distribution_threshold`** — the frequency cutoff and its comparator, e.g.
   `{ present_min_fraction: 0.99, band: "core", band_low: 0.99, band_high: 1.0 }`.
   For fixed-% pangenome traits this is the numeric band; **the number, not just the label,
   must be stored** (core@99 ≠ core@95).
3. **`definition_method` / `tool`** — how the partition/conservation was derived:
   `ROARY` (fixed-%), `PPANGGOLIN` (statistical), `BPGA`, `PANX`, `ORTHODB/BUSCO`
   (presence-breadth), `DNDS` (selective constraint). Traits from different methods are
   **not** auto-equivalent even at the same nominal band.
4. **`conservation_metric`** (EVO_CONSERVATION only) — which definition of "conserved":
   `PRESENCE_BREADTH` (ortholog panel) vs `SELECTIVE_CONSTRAINT` (dN/dS), plus the metric
   value/regime (ω-band) when applicable.
5. **`orthology_basis` / cutoff** (optional but recommended) — ortholog-detection method and
   identity/E-value used to call presence (affects clade-specific vs universal calls;
   BPGA identity cutoff).

**Equivalence rule once these exist:** two EVOLUTION records are `same_as`/`close_match`
**iff** `taxon_scope` matches **and** `distribution_threshold` matches **and**
`definition_method` matches (plus `conservation_metric` for conservation). If only one of
{scope, threshold} is nested/looser → `narrow_match`/`broad_match` (containment). If methods
differ → `related_to`/review only, never auto-merge.

---

### Primary/consulted sources
- Tettelin et al. 2005, PNAS — pan/core/dispensable genome (PubMed 16185861).
- Page et al. 2015, *Bioinformatics* — Roary; Sitto & Battistuzzi 2020, *MBE* 37(3):933 — Roary protocol / `-cd` default 99%.
- Lataretu et al. 2024, *Genome Biology* — RIBAP; states core≥99/soft 95–99/shell 15–95/cloud<15 and threshold effects.
- Gautreau et al. 2020, *PLOS Comp Biol* PCBI.1007732 / PMC7108747 — PPanGGOLiN persistent/shell/cloud statistical partition.
- Chaudhari et al. 2016, *Sci Rep* — BPGA (PMC4829868).
- Bioinformatics Advances 2025, vbag069 — "pangenome: a statistical model, not a fixed biological property."
- Ka/Ks ratio (Wikipedia); MBE 32(4):1097; PLoS Genet 2008 pgen.1000304 — dN/dS regimes and caveats.
- Biolink Model docs (biolink.github.io/biolink-model) + arXiv 2203.13906 — SKOS match predicates.
- BUSCO (Simão et al. 2015) — near-universal single-copy ortholog panels.
