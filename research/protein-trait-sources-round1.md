---
topic: protein sequence & structure trait sources
round: 1
date: 2026-07-01
question: >-
  Which established, downloadable resources supply protein sequence/structure
  traits (ideally as classifications/hierarchies, minimally with a definition in
  terms of sequence or structure elements) that can be seeded into
  ProteinTraitsMech?
method: reconstructed from the seeding work done in round 1 (see README seeds table + git history)
next_round: protein-trait-sources-round2.md
---

# Protein trait sources — Round 1

> Reconstructed after the fact. Round 1 was executed as seeding work, not
> written up at the time — this file captures what was evaluated and adopted so
> Round 2 can build on it. (Going forward every round is saved to markdown via
> the `edison-deep-research` skill.)

## Selection criteria (unchanged across rounds)

1. **Established** — a recognised, maintained community resource.
2. **Downloadable** — bulk data available (FTP/HTTP/API/flat files), licence
   compatible with a CC0 knowledge base (note any that are not).
3. **Classification / hierarchy preferred** — parent/child structure we can map
   to `parent_traits`.
4. **Minimum bar** — each trait must have a definition grounded in **sequence**
   or **structure** elements.

## Adopted in Round 1 (now seeded)

| Source | Trait kind → category | Hierarchy | Licence | Notes |
|---|---|---|---|---|
| LinkML `LocalStructuralFeature` | STRUCT_* (secondary, sites, cavity, …) | flat enum | CC0 | schema-native seed |
| PROSITE (patterns / profiles / ProRules) | SEQ_MOTIF, SEQ_PTM_*, STRUCT_DOMAIN | patterns→rules | CC-BY-ND (patterns), free | signatures = sequence definitions |
| TED (Encyclopedia of Domains) | STRUCT_FOLD (novel, high-symmetry) | CATH-derived | CC-BY 4.0 | Zenodo download |
| UniProtKB FT + CC + GO | SEQ/STRUCT/FUNC (demo seed) | — | CC-BY 4.0 | per-accession FT demux |
| PSI-MOD | SEQ_MODIFIED_RESIDUE etc. | OBO is_a | CC-BY 4.0 | modification CV |
| ECOD | STRUCT_{architecture,homologous_superfamily,topology,fold} | A/X/H/T/F | free | 45k nodes |
| M-CSA | STRUCT_ACTIVE_SITE | — | CC-BY 4.0 | catalytic sites/mechanisms |
| DisProt | SEQ_DISORDER | — | CC-BY 4.0 | IDRs with IDPO terms |
| PSI-MI (interaction type) | FUNC_INTERACTION_PARTNER | OBO is_a | CC-BY 4.0 | branch-scoped (round 1.5) |
| PATO (quality whitelist) | STRUCT_{stability,dynamics,surface} | OBO is_a | CC-BY 4.0 | branch-scoped (round 1.5) |
| METPO | FUNC_{environmental_response,enzymatic_activity} | OBO is_a | CC-BY 4.0 | ecophysiological, branch-scoped |
| Curated stability taxonomy | STRUCT_STABILITY | PATO-parented | CC0 | condition × direction matrix |

## Deferred / carried to Round 2

| Candidate | Why deferred |
|---|---|
| **NCBIfam** (ex-TIGRFAMs, ~17k prokaryotic HMMs, US-gov PD) | mechanically like PROSITE/Pfam HMM path; not yet done |
| **CDD** (NCBI, ~68k models w/ hierarchy, ~PD) | direct NCBI FTP; not yet done |
| **IDEAL** (~950 IDPs, CC-BY 4.0) | small, complements DisProt; not yet done |
| **PRO** (Protein Ontology) | **poor fit** — entity ontology (families/complexes), not traits; >1 GB reasoned; endpoints flaky. Rejected as a trait source. |

## Open gaps identified (targets for Round 2)

- **Structural tandem repeats** (`MIXED_STRUCTURAL_REPEAT`) — no source yet.
- **Metal sites** (`STRUCT_METAL_SITE`) — only 1 record.
- **Ligand/binding sites** (`STRUCT_BINDING_SITE`) — only ~2 records.
- **Enzyme mechanism / superfamily** grounding for `FUNC_ENZYMATIC_ACTIVITY`.
- **Linear motifs** beyond PROSITE (SLiMs).
- An **integrative** family/domain resource to unify PROSITE/Pfam/etc.
