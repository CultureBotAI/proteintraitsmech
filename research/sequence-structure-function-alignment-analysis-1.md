---
topic: sequence-structure-function coordinate alignment
round: 1
date: 2026-07-20
prompt: research/prompts/sequence-structure-function-alignment-prompt.md
builds_on: research/sequence-structure-alignment-analysis-1.md
method: >-
  Repository-side analysis (Codex, read-only) + live UniProtKB REST + PDBe SIFTS/CATH
  API grounding (Claude, 2026-07-20). Codex's own live grounding was blocked by a
  read-only sandbox with intermittent DNS; the exemplar residue/PDB/EC facts below
  were re-fetched and verified live against rest.uniprot.org and ebi.ac.uk/pdbe.
---

# Aligning the SEQUENCE, STRUCTURE, and FUNCTION coordinate systems

Extends the sequence↔structure alignment
([`sequence-structure-alignment-analysis-1.md`](sequence-structure-alignment-analysis-1.md),
built as `scripts/build_sequence_structure_alignment.py`) to a **third axis,
FUNCTION**. The core finding: the three axes do **not** share one coordinate
system. They share *two* — a **residue frame** (where they are directly
commensurable) and an **entity/ontology anchor frame** (where they only co-occur
on the same protein) — plus a **chemistry frame** that bridges them. Which frame
applies is decided by the *representation*, exactly as the axis rule predicts.

## 1. Coordinate-system taxonomy

A "coordinate" is *what pins a trait to a place*. There are four kinds; each
category uses exactly one as its primary locator (counts = live corpus,
2026-07-20).

| Axis | Category (n) | Coordinate type | Frame | Residue-localizable? |
|------|-------------|-----------------|-------|----------------------|
| **SEQ** | `SEQ_DOMAIN` 75,853 · `SEQ_FAMILY` 16,184 · `SEQ_HOMOLOGOUS_SUPERFAMILY` 5,699 · `SEQ_CONSERVATION` 775 | **signature identity** (Pfam/PROSITE/InterPro model) | model → matches on UniProt frame | via match, not intrinsic |
| **SEQ** | `SEQ_MOTIF` 3,121 · `SEQ_REPEAT` 2,073 · `SEQ_EPITOPE` 20,000 · `SEQ_PTM_SITE` 1,251 · `SEQ_MODIFIED_RESIDUE` 618 · `SEQ_CLEAVAGE_SITE` 841 · `SEQ_ACTIVE_SITE` 133 · `SEQ_BINDING_SITE` 82 · `SEQ_GLYCOSYLATION/CROSSLINK/LIPIDATION` 194 | **1-indexed residue span** (+ regex) | **UniProt residue** | **yes** |
| **STRUCT** | `STRUCT_FOLD` 55,735 · `STRUCT_HOMOLOGOUS_SUPERFAMILY` 15,177 · `STRUCT_DOMAIN` 13,514 · `STRUCT_TOPOLOGY` 5,427 · `STRUCT_CLASS/ARCHITECTURE/SECONDARY` 397 | **fold classification** (CATH/SCOP/ECOD/TED) + 3-D geometry | classification tree + PDB/AF coords | via SIFTS |
| **STRUCT** | `STRUCT_INTERFACE` 20,639 · `STRUCT_BINDING_SITE` 6,020 · `STRUCT_ACTIVE_SITE` 1,004 · `STRUCT_METAL_SITE` 292 · `STRUCT_SURFACE/CAVITY/DISULFIDE` 20 | **residue set via SIFTS** (+ 3-D contact geometry) | **UniProt residue** (PDB author → UniProt) | **yes** |
| **FUNC** | `FUNC_PROTEIN_FAMILY` 32,313 · `FUNC_ORTHOLOG_GROUP` 31,819 · `FUNC_PATHWAY` 28,098 · `FUNC_INTERACTION_PARTNER` 20,579 · `FUNC_MOLECULAR_FUNCTION` 10,041 · `FUNC_RESISTANCE` 7,452 · `FUNC_LOCALIZATION` 4,075 · `FUNC_TRANSPORT` 2,285 · `FUNC_COFACTOR_REQUIREMENT` 287 · `FUNC_BINDING_CAPACITY` 69 | **ontology / identity anchor** (EC · GO · OrthoDB/OMA/COG · Pfam · Reactome · TCDB · ARO) + whole-protein membership | **no residue** — protein-entity | **no** (whole-protein) |
| **FUNC** | `FUNC_ENZYMATIC_ACTIVITY` 26,003 (+ its `chemical_participants`) | **reaction / chemical-entity** anchor (EC leaf · RHEA · CHEBI) | chemical + protein-entity | no (but *implies* residues via its site records) |

**The load-bearing observation:** the FUNCTION axis carries **no residue-localized
categories of its own.** Residue-level function biology — active sites, ligand-
binding sites, metal sites, cleavage sites, PTMs — is deliberately filed on the
SEQ_ and STRUCT_ axes (axis-follows-representation: a residue is located by a
*sequence position* or a *structure*, not by "function"). So the FUNCTION axis as
represented here is almost entirely **whole-protein / ontology-anchored + reaction
chemistry**. This is what makes the three-way alignment two problems, not one:

- **residue-frame problem** — connect the function-bearing SEQ/STRUCT *site*
  records to each other on the UniProt residue frame (a direct extension of the
  existing overlay); and
- **entity-frame problem** — connect whole-protein FUNC_* records to the SEQ
  *signatures* and STRUCT *folds* that co-occur on the same proteins (a new,
  weaker, relate-only overlay).

The three systems are **commensurable only on the residue frame**; everywhere else
they are related by shared *identity*, not shared *coordinates*.

## 2. Alignment-path map

| # | Path | Anchor | Level | Predicate | Data present vs. fetch | Limit |
|---|------|--------|-------|-----------|------------------------|-------|
| **1** | **Residue-frame** — residue-localized FUNCTION sites (active/binding/metal/cleavage/PTM, on SEQ_/STRUCT_ axes) ↔ each other ↔ SEQ features ↔ STRUCT sites | overlapping **UniProt residue** intervals | residue | `biolink:overlaps` / `part_of` | Present: the exact mechanism of `build_sequence_structure_alignment.py` (stored/interpro/**sifts** providers). Extension = add the site categories as providers. | needs a UniProt anchor per record; PDB numbering must go through SIFTS (offsets are real — see §3) |
| **2** | **Whole-protein co-membership** — FUNC_* (EC/GO/family/ortholog/pathway) ↔ SEQ signatures (Pfam/InterPro) ↔ STRUCT folds (CATH/ECOD) | **same UniProt protein** carrying all three annotations (+ shared xrefs) | entity | `biolink:related_to` (relate-only; never merge — cross-axis) | Partly present (records already carry Pfam/EC/GO xrefs); the *co-membership graph* must be built from a UniProt-entry pivot | anchor must be **specific** — a broad GO/EC term co-occurs with everything (generic-anchor trap) |
| **3** | **Cross-scale partonomy** — a residue site ⊂ a whole-protein activity, *hosted by* a domain (SEQ) and a fold (STRUCT) | scale ladder: residue → domain/region → whole-protein → fold | mixed | `biolink:part_of` / `has_part` | Derivable by composing paths 1+2 on one protein | not a single overlap edge — a multi-hop relation; needs the two frames joined per protein |
| **4** | **Chemistry bridge** — FUNC reaction chemistry (RHEA/CHEBI substrate·cofactor) ↔ the binding/metal-site **residues** that contact that ligand | the **ligand** (CHEBI) shared by a `FUNC_ENZYMATIC_ACTIVITY` reaction and a `STRUCT_BINDING_SITE`/`STRUCT_METAL_SITE` | chemical → residue | `biolink:related_to` | RHEA/CHEBI present on activity records; BioLiP/MetalPDB ligand identity present on site records | ligand-identity matching is noisy (ion vs. complex vs. analogue); confirm per case |

**Ranking (Codex + this analysis agree):** **Path 1 is the strongest and the
smallest first step** — it reuses machinery that already exists and produces
residue-precise, defensible edges. Path 2 has the most *reach* (it is the only way
to connect the 100k+ whole-protein FUNC_* records to sequence/structure) but is
inherently relate-only and trap-prone. Paths 3–4 are compositions best built after
1 and 2 exist.

## 3. UniProt/PDB-grounded exemplars (live-verified 2026-07-20)

Four enzymes, each carrying SEQUENCE + STRUCTURE + FUNCTION annotations, traced on
the shared UniProt residue frame. Residue numbers, PDB ids, Pfam/CATH/EC/RHEA are
from live `rest.uniprot.org` + `ebi.ac.uk/pdbe` calls.

### 3.1 `P62593` — TEM-1 β-lactamase *(flagship; fully traced, and the numbering lesson)*
- **SEQUENCE** — Pfam `PF13354` (Beta-lactamase family) span **UniProt 32–286**;
  PROSITE `PS00146` (class-A β-lactamase active-site signature).
- **STRUCTURE** — PDB `1BTL` chain A; SIFTS: **PDB author 26–290 = UniProt 24–286**;
  CATH `3.40.710.10` (β-lactamase fold).
- **FUNCTION** — EC `3.5.2.6`, `RHEA:20401`; active sites **UniProt 68** (Ser,
  nucleophile / acyl-ester intermediate), **71** (Lys), **128** (Ser), **164**
  (Glu); binding 232–234.
- **Alignment on the frame** — the Pfam domain (32–286), the CATH fold (SIFTS
  24–286), and the four catalytic residues (68/71/128/164) all project onto one
  UniProt interval; the nucleophile at UniProt-68 sits inside the Pfam span and
  inside the SIFTS-mapped structural domain → path-1 residue edge, path-3
  partonomy (site ⊂ activity ⊂ domain/fold).
- **Why the shared frame is not optional:** SIFTS offset here is **author =
  UniProt + 2**, so UniProt-**68** is PDB/literature **Ser70** — the canonical
  "Ser70" Ambler nucleophile every β-lactamase paper (and M-CSA) cites. Aligning on
  raw numbers would fail; aligning through SIFTS on the UniProt frame reconciles
  UniProt-68 = author-70.

### 3.2 `P00918` — human carbonic anhydrase II *(metalloenzyme; chemistry bridge)*
- **SEQUENCE** — Pfam `PF00194`; PROSITE `PS00162`, `PS51144`.
- **STRUCTURE** — PDB `1CA2` chain A = **UniProt 2–260**; CATH `3.10.200.10`.
- **FUNCTION** — EC `4.2.1.1` (`RHEA:10748`) + `4.2.1.69`; active site **64**
  (proton shuttle, His64); **Zn²⁺-binding His 94 / 96 / 119**.
- **Path-4 demonstrated:** the CHEBI zinc cofactor of the reaction ↔ the three
  His residues (94/96/119) of the `STRUCT_METAL_SITE` are the same chemistry seen
  from the reaction side and the residue side.

### 3.3 `P00760` — bovine cationic trypsin *(serine protease; 3 numbering systems)*
- **SEQUENCE** — Pfam `PF00089` (Trypsin); PROSITE `PS50240`, `PS00134` (His
  active-site), `PS00135` (Ser active-site); MEROPS clan PA / family S1.
- **STRUCTURE** — PDB `1S0R` chain A **author 1–223 = UniProt 24–246** (≈23-residue
  activation-peptide offset); CATH `2.40.10.10` (trypsin-like β-barrel).
- **FUNCTION** — EC `3.4.21.4`; catalytic triad **UniProt 63 (His) / 107 (Asp) /
  200 (Ser)** — the charge-relay system; substrate specificity links to
  `SEQ_CLEAVAGE_SITE` (cleaves after Arg/Lys).
- **Lesson:** *three* coexisting coordinate systems — UniProt (63/107/200), PDB
  author (1-based mature), and the chymotrypsinogen convention (His57/Asp102/
  Ser195). Only SIFTS pins them to one frame; this is the general case, not the
  exception.

### 3.4 `P17612` — PKA catalytic α *(kinase; two-domain fold, partonomy)*
- **SEQUENCE** — Pfam `PF00069` (Protein kinase); PROSITE `PS00107` (ATP-binding),
  `PS00108` (Ser/Thr active site), `PS50011`.
- **STRUCTURE** — PDB `2GU8` chain A **author 14–350 = UniProt 15–351** (offset +1);
  CATH `1.10.510.10` **+** `3.30.200.20` — the **bilobal kinase fold, two CATH
  domains over one chain**.
- **FUNCTION** — EC `2.7.11.11` (`RHEA:17989`); active site **167** (catalytic
  Asp); ATP-binding 50–58, 122–128, 169–172.
- **Path-3 demonstrated:** one active site (167) and the ATP-binding residues span
  the cleft **between two structural domains** — a single whole-protein activity is
  hosted by a fold that decomposes into two CATH units, so the partonomy is
  genuinely multi-scale (site ⊂ activity ⊂ {domain₁, domain₂} ⊂ fold).

## 4. Recommended builder extension

Grow `scripts/build_sequence_structure_alignment.py` into a three-way overlay in
two increments, smallest-useful-first:

1. **Path 1 first (residue provider).** Add the residue-localized *function* site
   categories (`SEQ_ACTIVE_SITE`, `SEQ_BINDING_SITE`, `SEQ_CLEAVAGE_SITE`,
   `SEQ_PTM_SITE`/`SEQ_MODIFIED_RESIDUE`, `STRUCT_ACTIVE_SITE`,
   `STRUCT_BINDING_SITE`, `STRUCT_METAL_SITE`) as feature providers on the existing
   UniProt residue frame; emit `data/equivalence/seq_struct_func_sites.tsv` with
   `biolink:overlaps`/`part_of`. This reuses the SIFTS + stored-feature path
   verbatim — the only new code is enumerating those categories and reading their
   residue spans. **This is the first step to ship.**
2. **Path 2 second (co-membership overlay).** A separate builder that pivots on the
   **UniProt entry**: for each Swiss-Prot exemplar, collect its Pfam (SEQ), CATH
   (STRUCT), and EC/GO/ortholog (FUNC) annotations and emit relate-only
   `biolink:related_to` edges between the corresponding trait classes, with a
   **specificity guard** (drop anchors shared by more than `--anchor-cap` records —
   the generic-GO/EC trap). Output `data/equivalence/func_signature_comembership.tsv`.

Both are **cross-axis → relate, never merge** (per [[merge-within-axis]]); they
feed the browser's `eq` projection exactly like the existing overlays, and are
loaded bidirectionally by `build_docs_index.py`.

## 5. Open questions / risks

- **UniProt anchor coverage** — path 1 only fires for site records that carry a
  UniProt residue anchor; class-level site records (e.g. a MEROPS cleavage
  *consensus*) have a *pattern*, not a protein position, so they align by regex
  (path 1's `stored` provider), not by SIFTS. Keep the two sub-mechanisms distinct.
- **PDB author numbering is never trustworthy raw** — every exemplar above has a
  non-zero offset (β-lactamase +2/Ambler, trypsin −23/activation peptide, PKA +1).
  SIFTS is mandatory, not optional; hard-coding literature residue numbers (Ser70,
  Ser195, Asp166) would silently mis-align.
- **Generic-anchor trap on path 2** — a broad GO ("catalytic activity") or a
  1-level EC co-occurs with tens of thousands of proteins; without the specificity
  cap, path 2 degenerates into a near-complete bipartite graph. Cap and prefer leaf
  terms.
- **Whole-protein vs residue granularity** — path 2 relates a *fold* to an
  *activity* at the protein level; it must never be read as "this fold = this
  activity" (many folds are catalytically promiscuous; many activities span folds).
  The predicate stays `related_to`.
- **Multi-domain / multi-chain proteins** — PKA (two CATH domains) shows one
  activity spanning two structural units; the partonomy builder must handle
  one-to-many domain hosting rather than assuming one fold per activity.
- **Curator judgement remains** for path-4 ligand identity (ion vs. complex vs.
  substrate analogue in a crystal) and for promoting any co-membership edge beyond
  `related_to`.

---
*Provenance: repository-side path ranking and the β-lactamase candidate are from
the Codex read-only pass (its live grounding was blocked by a read-only sandbox +
intermittent DNS). All exemplar residue numbers, PDB ids, SIFTS offsets, CATH ids,
EC/RHEA anchors, and Pfam spans in §3 were fetched and verified live against the
UniProtKB REST API and PDBe SIFTS/CATH APIs on 2026-07-20.*
