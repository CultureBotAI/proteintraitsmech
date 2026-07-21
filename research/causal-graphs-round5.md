---
topic: causal-graphs
round: 5
date: 2026-07-21
target: aro/FUNC_RESISTANCE — ErmB (ARO:3000375, target alteration) + tet(M) (ARO:3000186, target protection) + auto-draft capability
prior_round: causal-graphs-round4.md
method: enriched ARO trait_relations (round 4) transcribed; verbatim from PMID:31601908 (Erm) + PMID:8655505 (tet(M)); ChEBI checks via OLS
---

# Causal graphs — Round 5: two more resistance mechanisms + auto-draft at scale

Round 4 built the ARO enrichment (drug-class + mechanism → `trait_relations`) so
graphs become *transcribable*. This round cashes that in three ways: two more
hand-curated mechanism graphs (a **third** and **fourth** distinct edge shape), and
an **auto-draft** tool that scaffolds a graph on every enriched ARO gene.

## (A) ErmB — target alteration (ARO:3000375, 7 edges)

The **third** mechanism type: the drug's *target* is chemically modified. ErmB is a
23S rRNA methyltransferase that dimethylates adenine A2058 (SAM as methyl donor);
the methylated ribosome no longer binds macrolide/lincosamide/streptogramin-B drugs
→ MLSB phenotype.

- Nodes (grounded 5/7): ermb (`ARO:3000375`), erm_family (`ARO:3000560`),
  methylation (MOLECULAR_FUNCTION `ARO:0001001`, xref `ARO:3000211`), sam
  (`CHEBI:15414`), rrna A2058 (NUCLEIC_ACID, label-only), mls (`CHEBI:25105`),
  resistance (PHENOTYPE).
- Edges (7/7 cited): ermb→erm_family (member of); ermb→methylation (enables);
  sam→methylation (methyl donor); methylation→rrna (has output — dimethylates
  A2058); rrna→mls (reduces binding, RO:0002212); methylation→resistance;
  ermb→resistance. Verbatim from PMID:31601908 ("dimethylates A2058 in 23S rRNA",
  "protecting the ribosomes from macrolide binding") + the ARO record ("ErmB
  confers the MLSb phenotype.").

## (B) tet(M) — target protection (ARO:3000186, 6 edges)

The **fourth** mechanism type: neither drug nor target is modified — the drug is
physically displaced. Tet(M) is a ribosome-binding GTPase (EF-G paralogue) that,
via GTP hydrolysis, dislodges tetracycline from its (unmodified) ribosomal site,
letting translation resume.

- Nodes (grounded 5/6): tetm (`ARO:3000186`), rpp_family (`ARO:3000185`), protection
  (MOLECULAR_FUNCTION `ARO:0001003`), gtp (`CHEBI:15996`), tetracycline
  (`CHEBI:27902`), resistance (PHENOTYPE).
- Edges (6/6 cited): tetm→rpp_family; tetm→protection (enables); gtp→protection
  (energises); protection→tetracycline (has input — releases); protection→resistance;
  tetm→resistance. Verbatim from PMID:8655505 ("Tet(M)-promoted release of
  tetracycline from ribosomes is GTP dependent") + the ARO record ("Tet(M) is a
  ribosomal protection protein that confers tetracycline resistance.").

Groundings verified via OLS: SAM `CHEBI:15414`, GTP `CHEBI:15996`, tetracycline
`CHEBI:27902`, macrolide `CHEBI:25105`.

## (C) Auto-draft — `scripts/draft_aro_causal_graphs.py`

Turns the round-4 enrichment into scaffolds: for each ARO determinant with enriched
mechanism/drug-class relations, it writes a `causal_graphs` block
(determinant → mechanism → resistance → drug-class) from the relations alone.

- **Explicitly DRAFTS:** `mapping_status` stays **SEEDED**; graph_id `resistance-draft`;
  each edge cites the record but carries **no verbatim snippet** (`notes` say "snippet
  pending curation"). `just audit-graphs --strict` flags every missing snippet — the
  "still needs a curator" signal. Records with a hand-curated graph are skipped.
- **Scale:** dry-run reports **7,395** draftable records (the 4 hand-curated ARO
  graphs skipped; 53 have no enriched mechanism). Validated + audited on a sample
  (0 errors). Recipe `just draft-aro-causal-graphs --apply`.
- **Not applied at scale in this commit** — writing 7,395 unreviewed graphs to the
  corpus (and deploying them to the browser) is a large, hard-to-reverse change, so
  it is left as a curator-invoked option rather than done by default.

## The resistance-mechanism set is now complete (4 shapes)
| round | determinant | mechanism | what happens to the drug/target |
|---|---|---|---|
| 3 | GOB-10 | antibiotic **inactivation** | drug chemically destroyed (β-lactam ring hydrolysed) |
| 4 | MdfA | antibiotic **efflux** | intact drug pumped out of the cell |
| 5 | ErmB | **target alteration** | target (23S rRNA A2058) methylated so drug can't bind |
| 5 | tet(M) | **target protection** | drug physically dislodged from an unmodified target |

Together with the two M-CSA reaction-mechanism graphs (rounds 1–2), the causal-graph
layer now demonstrates every major CARD resistance-mechanism class **and** the
atomic chemistry beneath one of them (MCSA:15 ↔ GOB-10).

## Provenance
records touched: **2** hand-curated (ErmB, tet(M)) → **REVIEWED**; new scripts:
`draft_aro_causal_graphs.py` (+ recipe). Gates: `just validate` clean on both;
`just audit-graphs` → **6 graphs, 48/48 edges snippet-cited, 0 errors**.

## Open questions / next
- **Apply the auto-drafts?** 7,395 scaffolds are one `--apply` away; a curator pass
  could then promote families to REVIEWED by adding verbatim snippets. Recommend
  applying per-family on demand rather than all at once.
- **Predicate gaps:** the drug-resistance and "reduces binding" edges still lack a
  precise biolink/RO predicate; a curated resistance predicate would sharpen them.
- **Node grounding:** rRNA-nucleotide and phenotype nodes remain label-only; SO /
  MONDO / ARO-phenotype groundings could be added.
