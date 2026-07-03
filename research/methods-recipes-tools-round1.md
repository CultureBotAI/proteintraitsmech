---
topic: where methods / recipes / tools belong in ProteinTraitsMech
date: 2026-07-03
question: >-
  A trait catalogue says WHAT traits exist. To be useful for annotation it must
  also say HOW each trait is detected / predicted / computed on a real protein —
  the method, the tool, and a runnable recipe. Where in this repo should that
  live, and how should it be grounded?
status: recommendation (per-category methods catalogue + detection_methods slot)
---

# Methods, recipes & tools — placement round 1

## 1. Why this matters

Every ProteinTraitRecord is a **class** ("iron ion binding", "beta-solenoid",
"Pkinase domain"). What turns a class into an annotation on a real protein is a
**method**: a PROSITE regex, a Pfam HMM run with `hmmsearch`, a disorder
predictor, DSSP for secondary structure, an EC classifier, Foldseek for folds.
Today the KB encodes methods only implicitly and inconsistently:

- `sequence_pattern` on a SEQ record *is* a runnable method (a regex), but only
  ~2.8k records have one.
- A `Pfam:`/`InterPro:`/`HAMAP:` identifier *implies* "run this HMM/pattern",
  but nothing says so, and nothing gives the command.
- Predicted traits (disorder, transmembrane, secondary structure, signal
  peptide, EC/GO prediction, localisation) have **no** method representation at
  all — the definitions even say "predicted or experimentally validated"
  without naming a predictor.

So a user who finds "SEQ_DISORDER" cannot learn from the KB *how* to detect it.
That is the gap.

## 2. How peer resources do it

- **InterPro** — each entry is backed by **member-database signatures**, and
  each signature carries its method type (HMM / pattern / profile / ML) and the
  tool that scans it (`hmmscan`, `ps_scan`, etc.). Method ≈ a property of the
  signature, reused across all proteins.
- **MobiDB / DisProt** — each disorder annotation cites the **predictor** (MobiDB-lite,
  IUPred, flDPnn, AlphaFold-pLDDT…) plus an **ECO** evidence code (predicted vs
  experimental). Method + evidence are first-class.
- **UniProt** — every feature/annotation carries an evidence tag (ECO) naming
  the method class (sequence analysis, similarity, experimental).
- **[EDAM](https://edamontology.org/)** — the community ontology of
  bioinformatics **operations** (e.g. *protein feature detection*, *protein
  binding site prediction*), **data**, **formats**, **topics**. This is the
  grounding vocabulary for "what a method does".
- **[bio.tools](https://bio.tools/)** — the registry of the tools themselves,
  each annotated with EDAM operations/inputs/outputs — the grounding for "which
  software".
- **[ECO](https://www.evidenceontology.org/)** — evidence & conclusion codes,
  including the computational-method branch — the grounding for "how strong /
  what kind of evidence".

Consensus pattern: **method = (EDAM operation) + (bio.tools tool) + (ECO
evidence) + a runnable command**, attached at the level where it is *reused* —
which here is the **trait_category**, not the individual record.

## 3. Where it belongs in THIS repo — recommendation

Detection method is overwhelmingly a function of **trait_category** (every
`SEQ_DISORDER` is found by the same predictor family; every `STRUCT_SECONDARY`
by DSSP/STRIDE; every EC leaf by the same EC classifiers). So the natural home
is a **methods catalogue keyed by category**, mirroring the KB's existing
"registry + lean per-record reference" philosophy (cf. the ChEBI sidecar, the
download.yaml source catalogue):

### (a) `data/methods/` — a per-category methods catalogue *(primary)*
One YAML per trait_category (or a `methods.yaml`), each listing the methods
that assign it:

```yaml
category: SEQ_DISORDER
methods:
  - name: MobiDB-lite
    method_type: ML_PREDICTOR          # → ECO:0000203 sequence-analysis evidence
    edam_operation: EDAM:operation_0472 # Protein feature detection
    tool: biotools:mobidb-lite
    reference: PMID:28453701
    recipe: "mobidb_lite.py {input.fasta} -o {output.json}"
    inputs: [EDAM:format_1929]          # FASTA
    outputs: [EDAM:format_3464]         # JSON
  - name: IUPred3
    ...
```

### (b) Schema: an optional `detection_methods` slot on ProteinTraitRecord
For **record-specific** methods that aren't category-generic — the PROSITE
regex a pattern record already carries, a specific Pfam HMM accession, an M-CSA
template. A `DetectionMethod` class: `method_type` (enum, ECO-groundable),
`tool` / `tool_id` (bio.tools), `edam_operation`, `reference`, `recipe`,
`evidence` (ECO). Records mostly *inherit* their category's methods; the slot is
for overrides / specifics.

### (c) Recipes = the `recipe` field + thin `just` wrappers
A "recipe" is a runnable command template in the catalogue entry (`hmmsearch
Pfam-A.hmm {input}`, `mkdssp {pdb}`, `iupred3 {fasta} long`). The handful of
in-house ones can get `just detect-<x>` wrappers; most just document the
invocation. No new execution engine — this KB describes, it doesn't run.

### (d) Docs + browser surface
A "Methods & Tools" docs page (category → method/tool/recipe), and a **"How
this trait is detected"** row on the browser detail view, resolved from the
category catalogue (derived, zero per-record bloat — same trick as the members
link and ChEBI sidecar).

## 4. The method landscape (what the catalogue will hold)

| Axis / category | Detection method(s) | Tool(s) |
|---|---|---|
| SEQ_MOTIF / _PATTERN | regex / profile scan | ps_scan, ScanProsite, ELM |
| SEQ family (Pfam/InterPro) | HMM search | hmmsearch/hmmscan, InterProScan |
| SEQ_DISORDER | disorder prediction | MobiDB-lite, IUPred3, flDPnn, AlphaFold pLDDT |
| SEQ transmembrane | TM topology prediction | DeepTMHMM, TMHMM, Phobius |
| SEQ signal/targeting | signal-peptide prediction | SignalP 6, TargetP |
| SEQ_PTM/_MODIFIED_RESIDUE | PTM-site prediction / MS | NetPhos, MusiteDeep, dbPTM |
| SEQ_COMPOSITION | compositional bias | SEG, fLPS, biopython |
| STRUCT_SECONDARY | secondary-structure assignment | DSSP, STRIDE |
| STRUCT_FOLD / domain | fold / domain assignment | Foldseek, TED, Gene3D, InterProScan |
| STRUCT_ACTIVE_SITE | catalytic-site prediction | M-CSA transfer, CSA-3D |
| STRUCT_BINDING_SITE / CAVITY | pocket / site prediction | fpocket, P2Rank |
| STRUCT_METAL_SITE | metal-site prediction | MetalPDB, AlphaFill |
| STRUCT_DISULFIDE | disulfide prediction | DiANNA, DISULFIND |
| FUNC_ENZYMATIC_ACTIVITY (EC) | EC prediction | DeepEC, CLEAN, ECpred |
| FUNC_BINDING_CAPACITY / GO | GO/function prediction | DeepGO, NetGO3, InterPro2GO |
| FUNC_TRANSPORT (TCDB) | transporter classification | TCDB-BLAST, TransportTP |
| FUNC_PATHWAY / _ORTHOLOG_GROUP | KO / OG assignment | KofamScan, eggNOG-mapper |
| FUNC_RESISTANCE | AMR gene calling | RGI (CARD), AMRFinderPlus |
| EVO_CONSERVATION | conservation / orthology | ConSurf, OrthoFinder, eggNOG |
| EVO_PANGENOME | pangenome partitioning | Roary, PPanGGOLiN, panaroo |

Most of these are **CC-compatible, open tools with a PMID and a bio.tools
entry** — clean to ground.

## 5. Rollout

1. **Schema** — `DetectionMethod` class + `MethodTypeEnum` (ECO-aligned) +
   `detection_methods` slot. Regenerate.
2. **Catalogue** — seed `data/methods/` from the table above, one entry per
   category, grounded (EDAM operation + bio.tools + PMID + recipe). A
   `seed_methods.py` / hand-curated YAMLs; `just methods-check` to validate
   coverage (every populated category has ≥1 method).
3. **Backfill record-specifics** — the PROSITE regex and Pfam/HAMAP HMM
   accessions already on records become `detection_methods` entries (they are
   literally the method).
4. **Surface** — docs Methods page + browser "How detected" row (derived from
   the category catalogue).

## 6. What we do NOT do

- **No execution engine** — recipes are documented commands, not a workflow
  runner. (If runnable workflows are later wanted, emit CWL/Nextflow from the
  EDAM annotations rather than inventing a format.)
- **No per-record method duplication** — methods live once per category;
  records reference/override. Scalability-neutral, like the other sidecars.
- **No re-inventing vocabularies** — ground in EDAM (operation/data/format),
  bio.tools (tool identity), ECO (evidence). Don't mint local method types
  beyond a small enum that maps to ECO.

## Sources
- [EDAM ontology](https://edamontology.org/) · [paper (Bioinformatics 2013)](https://academic.oup.com/bioinformatics/article-abstract/29/10/1325/255660)
- [bio.tools registry](https://bio.tools/)
- [Evidence & Conclusion Ontology (ECO)](https://www.evidenceontology.org/)
- InterPro member-database signature model · MobiDB predictor+ECO annotation model
