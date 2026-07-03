# NEXT TASK — peptide / signal / leader / targeting trait sources

Deep research into data sources for traits about **signal peptides, leader
peptides, propeptides / preproteins, targeting & localization signals, and
related peptide signatures**. Goal: identify seedable, class-level, licensed
sources to populate the (largely empty) peptide/targeting categories.

status: research complete — ready to seed; ELM is the top pick
date: 2026-07-03

## 1. The trait sub-space

| Sub-space | Examples | Schema category (existing unless noted) |
|---|---|---|
| **Secretory signal peptide** | Sec/SRP N-terminal signal, signal-anchor | `SEQ_SIGNAL_PEPTIDE` |
| **Twin-arginine (Tat) signal** | `S/T-R-R-x-F-L-K` twin-Arg motif | `SEQ_SIGNAL_PEPTIDE` |
| **Lipoprotein signal (lipobox)** | `L-[AS]-[GA]-C` (signal peptidase II) | `SEQ_SIGNAL_PEPTIDE` |
| **Transit peptide** | chloroplast / mitochondrial N-terminal targeting | `SEQ_TRANSIT_PEPTIDE` |
| **Propeptide / proprotein** | furin/PC cleavage, zymogen pro-region | `SEQ_PROPEPTIDE` + `SEQ_CLEAVAGE_SITE` |
| **Mature chain** | the processed product | `SEQ_MATURE_CHAIN` |
| **Nuclear localization / export** | NLS (mono/bipartite), NES (Leu-rich) | `SEQ_MOTIF` → **propose `SEQ_TARGETING_SIGNAL`** |
| **Peroxisomal targeting** | PTS1 (`-SKL`), PTS2 | as above |
| **ER retention / retrieval** | KDEL, KKXX | as above |
| **GPI-anchor signal** | C-terminal ω-site + hydrophobic tail | as above / `SEQ_LIPIDATION_SITE` |
| **Cell-wall sorting (sortase)** | LPXTG motif | as above |
| **RiPP / bacteriocin leader** | lanthipeptide, lasso, sactipeptide, bacteriocin leaders | **propose `SEQ_LEADER_PEPTIDE`** (or a FUNC RiPP class) |
| **Cleavage sites** | signal peptidase I/II, PC, caspase, MEROPS | `SEQ_CLEAVAGE_SITE` |

Most categories already exist; the two gaps are **targeting/localization
signals** (NLS/NES/PTS/KDEL — currently would fall to `SEQ_MOTIF`) and **RiPP
leader peptides**.

## 2. Candidate sources (ranked)

| # | Source | What it gives (class-level) | Download | Licence | Class vs instance | Verdict |
|---|---|---|---|---|---|---|
| **1** | **[ELM](http://elm.eu.org/)** (Eukaryotic Linear Motif) | ~350 linear-motif **classes** in 6 categories — **TRG** (targeting: NLS, NES, PTS1/PTS2, KDEL, mito, endosome), **CLV** (cleavage: signal peptidase, proprotein convertase, caspase), plus MOD/LIG/DOC/DEG. Each class = regex + description + instances. | `elm_classes.tsv` / `elm_instances.tsv` (API + bulk) | ⚠️ **non-commercial** (ELM Software License) — like PROSITE (already in as CC-BY-NC-ND); stamp per-record | **class** (motif classes) + instances (→ examples) | **SEED FIRST.** The single best class-level source for targeting + cleavage. TRG→`SEQ_TARGETING_SIGNAL`, CLV→`SEQ_CLEAVAGE_SITE`, others map to existing SEQ_* |
| **2** | **UniProt feature-type + keyword classes** | The peptide feature *types* as trait classes: SIGNAL, TRANSIT, PROPEP, PEPTIDE, plus KW-0732 Signal, KW-0809 Transit peptide, KW-0865 Zymogen, KW-0325 Glycoprotein… | UniProt keyword list + FT type table (already used by `seed_uniprot.py`) | CC-BY 4.0 | **class** (feature types) + per-protein FT (→ examples, **pivot**) | **SEED** the ~12 peptide feature-type / keyword classes; attach proteins as `canonical_examples` (pivot model, as done for DisProt) |
| **3** | **PROSITE** (already seeded) | Patterns for lipobox (PS51257), microbody/PTS1 (PS00342), ER-retention, prokaryotic membrane-lipoprotein attachment (PS00013), N-myristoylation | already in `data/raw` | CC-BY-NC-ND (already flagged) | class | **already covered** — verify these patterns are routed to signal/targeting, not generic `SEQ_MOTIF` |
| **4** | **MEROPS** (schema prefix exists) | Peptidase clans/families + **propeptide** and cleavage specificity; the processing enzymes behind signal/propeptide cleavage | FTP / API | academic (verify) | class | **SEED** peptidase families → `STRUCT_DOMAIN` / cleavage; complements SEQ_CLEAVAGE_SITE |
| **5** | **RiPP: [BAGEL4](http://bagel4.molgenrug.nl/) + MIBiG + antiSMASH** | RiPP/bacteriocin **classes** (lanthipeptide, lasso, sactipeptide, thiopeptide, microcin…) and their leader-peptide HMMs | BAGEL4 standalone DBs; MIBiG JSON (CC-BY 4.0); antiSMASH rule set | mixed — MIBiG CC-BY 4.0; BAGEL check | class | **SEED** the RiPP leader classes → propose `SEQ_LEADER_PEPTIDE` (+ FUNC link); MIBiG is the clean-licence entry point |
| 6 | **[SPdb](http://proline.bic.nus.edu.sg/spdb) / [signalpeptide.de](http://www.signalpeptide.de/)** | Curated signal-peptide records | web / flat | academic / unclear | **instance** (per-protein) | pivot to a `SEQ_SIGNAL_PEPTIDE` trait + proteins as examples; lower priority (UniProt SIGNAL already gives this) |
| 7 | Predictors — SignalP 6, TargetP 2, DeepLoc, TatP, LipoP, PredGPI, ChloroP, cNLS Mapper | define the trait **vocabulary**, not seedable data | — | — | — | use to *name/scope* categories + as `detection_methods` (see methods research) — do not seed as records |
| 8 | **SO / GO** | grounding terms: `SO:0000418` signal_peptide, `SO:0000725` transit_peptide, `SO:0001062` propeptide, `SO:0000419` mature_protein_region; GO CC for localization | OBO | CC-BY | class | use for **node grounding** of the categories, not as a standalone seed |

## 3. Recommended plan

1. **ELM** (`seed_elm.py`) — parse `elm_classes.tsv`: one record per motif class,
   `sequence_pattern` = the regex, route by ELM category
   (TRG→`SEQ_TARGETING_SIGNAL` [new], CLV→`SEQ_CLEAVAGE_SITE`, MOD→`SEQ_PTM_SITE`,
   LIG/DOC→`SEQ_MOTIF`, DEG→`SEQ_MOTIF`). Attach ELM instances as
   `canonical_examples`. Stamp `license: ELM non-commercial` per-record (as
   PROSITE). ~350 high-value class-level records.
2. **Schema** — add `SEQ_TARGETING_SIGNAL` (NLS/NES/PTS/KDEL/GPI/sortase) and
   `SEQ_LEADER_PEPTIDE` (RiPP/bacteriocin leaders) to `ProteinTraitCategoryEnum`
   + the `SEQ_* → SEQUENCE` rule (already covers new SEQ_ values). Ground both to
   SO/GO.
3. **UniProt peptide feature-type / keyword classes** — ~12 class records
   (SIGNAL/TRANSIT/PROPEP/PEPTIDE/lipobox/Tat…), proteins as examples (pivot).
4. **RiPP leaders** — MIBiG (CC-BY) RiPP classes → `SEQ_LEADER_PEPTIDE`, linked
   to the biosynthetic function.
5. **MEROPS** — peptidase families (processing enzymes) as a later structural add.

## 4. Notes / cautions

- **Licence**: ELM is **non-commercial** — acceptable only because the repo
  already carries PROSITE (CC-BY-NC-ND) under per-record licensing; keep the
  `license:` field accurate and never relabel as CC0.
- **Class vs instance** (the pivot rule): SPdb, signalpeptide.de and UniProt FT
  are per-protein — seed the *signal/targeting class* as the trait and the
  proteins as `canonical_examples`, never one record per protein.
- **Overlap**: many signal/leader families are already in Pfam / InterPro /
  NCBIfam / PROSITE — dedupe with `merge-traits` after seeding ELM.
- **Detection methods**: SignalP/TargetP/TatP/LipoP/PredGPI map cleanly to the
  `detection_methods` model in `research/methods-recipes-tools-round1.md`.

## Sources
- [ELM 2024 update (NAR)](https://academic.oup.com/nar/article/52/D1/D442/7420098) · [elm.eu.org](http://elm.eu.org/) · [ELM academic licence](http://elm.eu.org/media/Elm_academic_license.pdf)
- [SPdb — signal peptide database](https://pmc.ncbi.nlm.nih.gov/articles/PMC1276010/) · [signalpeptide.de](http://www.signalpeptide.de/)
- [BAGEL4 (RiPP/bacteriocin miner)](https://academic.oup.com/nar/article/46/W1/W278/5000017) · [bagel4.molgenrug.nl](http://bagel4.molgenrug.nl/)
- SO/GO for grounding; SignalP 6 / TargetP 2 / LipoP / TatP / PredGPI as detection methods
