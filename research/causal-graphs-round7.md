---
topic: causal-graphs
round: 7
date: 2026-07-21
target: modeling correction — route causal graphs through the KB's specific protein-trait records (MCSA:2 retrofit + KPC family re-promotion)
prior_round: causal-graphs-round6.md
---

# Causal graphs — Round 7: incorporate the protein traits directly

**Modeling correction.** The graphs so far ran the causation through *generic*
ontology entities (ARO mechanism classes, whole-protein `UniProtKB:` groundings,
bare GO/CHEBI). But this is a KB *of protein traits* — the causation must run
through the corpus's **specific protein-trait records** (the domain, fold,
active-site, motif traits), and residues must sit on the **full protein sequence**.
A graph of only ARO/GO/CHEBI classes does not connect to what the KB is about.

Enshrined as a hard skill criterion (#6) + a "wire the mechanism through
protein-trait nodes" section in `edison-causal-graphs`, and as a persistent memory
([[causal-graphs-must-incorporate-protein-traits]]).

## The pattern
Ground DOMAIN/MOTIF/FOLD/RESIDUE/site nodes to the **actual KB trait CURIEs that
exist as records** (`grep -rl "^identifier: <CURIE>$" data/traits`) and route the
mechanism through them with partonomy/host edges:

    residue --part_of--> active-site/motif --part_of--> domain --member_of--> fold
    active-site --enables--> molecular-function --(...)--> product / phenotype

This is the same cross-axis link the sequence↔structure↔function alignment overlays
capture: a FUNCTION resistance determinant's mechanism runs through its SEQUENCE
signature/domain and STRUCTURE fold/active-site traits.

## (A) MCSA:2 retrofit — the canonical exemplar
The class A β-lactamase reaction mechanism now runs through four **real KB trait
records** (all verified present):
- `PROSITE:PS00146` (SEQ_MOTIF, "Beta-lactamase class-A active site")
- `Pfam:PF13354` (SEQ_DOMAIN, "Beta-lactamase enzyme family", UniProt 32–286)
- `CATH:3.40.710.10` (STRUCT_HOMOLOGOUS_SUPERFAMILY)
- `GO:0008800` (β-lactamase activity)

Added 4 nodes + 5 edges: `ser70 part_of active_site part_of domain member_of fold`;
`active_site enables activity has_output product`. The atomic chemistry (11 edges)
is unchanged; it is now *located within* the protein's traits. Graph: **15 nodes /
16 edges, 16/16 snippet-cited, 0 errors.**

## (B) KPC family re-promotion — at scale
`promote_family_drafts.py` gained a per-family `protein_traits` config. Because all
class A serine β-lactamases share the class-A active-site signature and the
β-lactamase fold, **all 232 KPC records** now wire their resistance mechanism through:
- `active_site` → `PROSITE:PS00146`, `part_of` the determinant;
- `determinant` → `member_of` `CATH:3.40.710.10` (fold);
- `active_site` → `enables` the serine-hydrolysis mechanism (ARO:3000187).

Each KPC graph went 8→10 nodes, 9→12 edges, **12/12 snippet-cited, 0 errors**,
validates. The promoter now re-promotes its own prior output (guarded by its
curation-history signature) so it never clobbers hand-curated graphs.

## Result
| | before | after |
|---|---|---|
| MCSA:2 | residues on whole UniProt only | + PROSITE/Pfam/CATH/GO trait nodes, partonomy |
| KPC ×232 | ARO mechanism + drug classes only | + active-site (PROSITE) + fold (CATH) traits |

The FUNCTION-axis resistance graphs now reach into the SEQUENCE (`PROSITE:PS00146`)
and STRUCTURE (`CATH:3.40.710.10`) trait records — the causal-graph layer is wired
into the KB's own content, not floating on external ontologies.

## Open questions / next
- **Backfill the other curated graphs:** MCSA:15 (class B → Pfam/CATH metallo-β-lac
  traits), GOB-10, MdfA (MFS transporter domain), ErmB (methyltransferase domain +
  23S rRNA target), tet(M) (EF-G-like domain) — each needs its own protein-trait
  records wired in.
- **Drafts:** the 7,163 remaining auto-drafts still use generic ARO nodes; the
  per-family `protein_traits` config extends the wiring to each family as it is
  promoted (TEM/SHV/CTX-M/OXA next — all class A/D β-lactamases sharing the same
  fold trait).
- **Pfam for KPC:** used the class-A active-site signature + fold (certain for KPC);
  a per-variant Pfam domain trait could be added if confirmed.
