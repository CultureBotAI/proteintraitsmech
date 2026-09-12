# eLife 109154: metallophore protein-trait ingestion

This ingestion adds **20 protein sequence traits and 33 qualified UniProt protein
examples across 16 families**. Four domain traits retain source associations without
canonical examples because their coordinates could not be established from the deposited
annotations. All definitions have `mapping_status: PROPOSED`; qualification of an example
means supported sequence classification, not experimentally demonstrated enzyme activity.
The complete [504-row association ledger](../data/curation/elife109154_protein_associations.tsv)
also preserves proteins outside the bounded canonical-example panel.

The starting reference was the supplied `elife-109154-figures-v2.pdf`. The full
[article, Reitz, Pourmohsenin et al.](https://elifesciences.org/articles/109154),
Version of Record published 9 March 2026, is identified here as
`DOI:10.7554/eLife.109154.3`. The `v2` suffix on downloadable PDF/XLSX assets is a
publisher file revision, not the DOI version. The article's Methods still name
Zenodo `17806971`, while its Data availability section links the later
[Zenodo 18866949 deposit](https://zenodo.org/records/18866949), published 4 March 2026.
This ingestion pins the latter release. Retrieval occurred on 12 September 2026 UTC
(11 September in the workspace's local timezone).

The study detects nonribosomal peptide metallophore biosynthetic clusters by combining
chelator-biosynthesis protein profiles with NRPS context. Figure 1 organizes eight
chelator types. Here those chemical groups provide context for sequence families and
domains: a compound or an entire gene cluster is not itself a protein trait. The
definitions and category choices are agent-curated interpretations of the article and
deposited models. No metal preference, generic transport capability, or experimental
activity is inferred solely from a profile association. See the
[curation catalog](../data/curation/elife109154_traits.yaml) for the exact definitions.

The following inventory uses the identifiers `proteintraitsmech:ELIFE109154_<model>`.
Thresholds are the source's bitscore cutoffs. The four domain records are under
[`sequence/domain/elife_metallophores`](../data/traits/sequence/domain/elife_metallophores/);
the others are under
[`sequence/family/elife_metallophores`](../data/traits/sequence/family/elife_metallophores/).

| Chelator or assembly context | Model | Scope | Cutoff | Canonical examples |
| --- | --- | --- | ---: | ---: |
| Catechol / 2,3-dihydroxybenzoate | EntA | Family | 205 | 2 |
| Catechol / 2,3-dihydroxybenzoate | EntC | Family | 300 | 2 |
| Salicylate | IPL | Family | 110 | 1 |
| Salicylate | SalSyn | Family | 350 | 2 |
| Hydroxamate | Orn_monoox | Family | 415 | 2 |
| Hydroxamate | Lys_monoox | Family | 300 | 3 |
| Hydroxamate / vicibactin | VbsL | Family | 570 | 1 |
| β-Hydroxyaspartate | TBH_Asp | Family | 420 | 3 |
| β-Hydroxyaspartate | IBH_Asp | Domain | 440 | 0 |
| β-Hydroxyhistidine | IBH_His | Family | 470 | 2 |
| Putative cyanobacterial β-hydroxyaspartate | CyanoBH_Asp1 | Domain | 400 | 0 |
| Putative cyanobacterial β-hydroxyaspartate | CyanoBH_Asp2 | Domain | 450 | 0 |
| Graminine | GrbD | Family | 400 | 2 |
| Graminine | GrbE | Family | 250 | 2 |
| Dmaq | FbnL | Family | 40 | 2 |
| Dmaq | FbnM | Family | 180 | 3 |
| Pyoverdine chromophore | PvdP | Family | 600 | 3 |
| Pyoverdine chromophore | PvdO | Family | 250 | 2 |
| Catecholic/phenolic assembly | VibH_like | Family | 400 | 1 |
| Catecholic/phenolic assembly | Cy_tandem | Domain | 350 | 0 |

The source rule requires joint EntA/EntC, GrbD/GrbE, and FbnL/FbnM matches; it accepts
PvdP or PvdO independently. Most alternatives also require a CDS bearing condensation
and AMP-binding domains. VibH_like and Cy_tandem are independent alternatives.
KtzT, MetRS-like, and SBH_Asp are negative constraints, so they were not ingested as
positive metallophore traits. The exploratory FbnE model is excluded from the final
rule. These distinctions come from `1_rule_development/rule.txt` in the
[supplemental archive](https://zenodo.org/api/records/18866949/files/nrp-metallophore-SI.zip/content).
The per-trait HMM recipes classify proteins; running one recipe does not reproduce
the cluster-level rule, its 30-kb cutoff, or its 20-kb neighbourhood.

All four files listed in Zenodo 18866949 were downloaded and their publisher MD5
checksums verified. The main 272,356,490-byte ZIP contains 291 entries: rule development,
alignments and HMMs, manual benchmarking, RefSeq and GTDB analyses, reference BGCs,
phylogenies, and reconciliation resources. The inspection focused on model definitions,
seed identities, explicit reference-BGC annotations, tabulated results, and the three
study validation clusters; genome mining and evolutionary reconciliations were not
rerun. The actual development directory is `1_rule_development/`, rather than the
`1_development/` path printed in the Methods.

The deposit has two material gaps. `Lys_monoox.hmm` is named in the model table but
absent from the complete ZIP inventory; its seed alignment is present. Its trait
therefore has no executable HMM recipe. VbsL has a deposited HMM but no seed alignment;
its qualified example comes from an explicit profile annotation in the reference
vicibactin BGC. Archive inventories, including all nested path names, were searched
independently of filesystem ignore rules. Identical duplicate alignment/FASTA rows were
collapsed; conflicting duplicates are rejected.

The source table calls CyanoBH_Asp2 standalone, but its deposited identifiers include
larger fusion proteins. Both cyanobacterial subtypes and IBH_Asp are represented as
domains to accommodate their observed protein context. Cy_tandem is also a domain
signature; one hit does not establish a tandem pair. Cropped alignment sequences and
inconsistent header intervals were not converted into fabricated full-protein
coordinates. Their association-ledger status is `DOMAIN_COORDINATES_UNRESOLVED`.

The 504 associations comprise 376 seed-alignment memberships and 128 explicit
reference-BGC profile annotations. Supplementary file 1a lists 78 reference clusters,
including three marked false positives: himastatin (`BGC0001117`), kutzneride
(`BGC0000378`), and viscosin (`BGC0001312`). Protein annotations from those three
clusters were excluded. These are association counts, not unique-protein counts.

A bounded panel of 46 source candidates was checked against exact UniProt accessions
or exact RefSeq/EMBL cross-references. Thirty-three passed the sequence and identity
checks; 13 were unresolved or rejected. Each accepted full sequence matches its
deposited source sequence exactly and is pinned to the acquired UniProt release
`2026_03`. For beta-hydroxylase families, full sequences were recovered from the
deposit's `hydroxylase_tree/genes.faa` where the source identifier matched exactly.
The [review decisions](../data/curation/elife109154_example_decisions.jsonl) bind each
accepted protein, organism, source assertion, and trait snapshot. They document agent
review under the user's ingestion request, not human expert review.
The deposited seed alignments include both known-pathway and putative-cluster proteins.
These examples therefore document source-defined classifications and are not an
independent experimental test set for the profiles that were trained on them.

Examples include EntA [P15047](https://www.uniprot.org/uniprotkb/P15047/entry), EntC
[P0AEJ2](https://www.uniprot.org/uniprotkb/P0AEJ2/entry), Lys_monoox
[P9WKF7](https://www.uniprot.org/uniprotkb/P9WKF7/entry), PvdP
[Q9I188](https://www.uniprot.org/uniprotkb/Q9I188/entry), and PvdO
[Q9I185](https://www.uniprot.org/uniprotkb/Q9I185/entry). UniProt names and organisms
were preserved even where the annotation is generic or differs from the paper's
classification. In particular, VbsL example Q2JYI5 is labelled cystathionine
gamma-synthase by UniProt: its evidence is the deposited vicibactin profile annotation
and matching full sequence, not proof of its proposed epimerase activity. Source seed
membership and BGC annotation use different evidence methods in the durable registry.

Recalculation from the cached cell values in
[Supplementary file 1](https://cdn.elifesciences.org/articles/109154/elife-109154-supp1-v2.xlsx)
reproduces the paper's rounded benchmark metrics. The validation sheet has 758 regions,
176 initial positives and 180 positives after manual correction. Using that corrected
column gives:

| Detector | TP | FP | FN | TN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| antiSMASH metallophore rule | 140 | 5 | 40 | 573 | 0.9655 | 0.7778 | 0.8615 |
| Transporter signatures | 100 | 8 | 80 | 570 | 0.9259 | 0.5556 | 0.6944 |
| Either/or ensemble | 159 | 13 | 21 | 565 | 0.9244 | 0.8833 | 0.9034 |

These are cluster-classification benchmarks, not validation rates for the 33 protein
examples. The RefSeq representative sheet contains 30,973 rows, 20,107 NRPS regions,
3,264 predicted NRP-metallophore regions, and 2,523 complete NRP-metallophore regions
(2,485 of them also flagged NRPS). Figure 2 instead describes 2,489 regions plus 38
additional assembly-marker regions, implying 2,527. The four-region difference is
recorded rather than silently reconciled. The machine-readable
[source summary](../data/curation/elife109154_source_summary.json) retains the spreadsheet
counts; `scripts/analyze_elife_metallophores.py` reproduces them without evaluating
spreadsheet formulas.

The GTDB export `7_gtdb_reps_statistics/All_genomes_AS7_parsed_products_with_taxonomy.csv`
contains 65,703 distinct genome accessions, of which 59,851 carry bacterial taxonomy.
Of those bacterial genomes, 4,098 (6.85%) have an NRP-metallophore product annotation,
reproducing the deposit's phylum summary and the article's corresponding result.
Pseudomonadota accounts for 2,042 positive genomes and Actinomycetota for 1,561.
These taxonomic counts describe the sampled genomes and computational detections;
they do not establish a species-wide absence of metallophore production when a marker
is undetected. The export's denominator and detection-based prevalence should be
retained when using these resources for organism comparisons.

The three small Zenodo archives contain antiSMASH v8 annotations for the strains used
in the paper's product-validation experiments. Their associated MIBiG identifiers and
reported positive signatures are:

| Product | Organism | MIBiG submission | Positive profile annotations |
| --- | --- | --- | --- |
| Enterobactin | Buttiauxella brennerae DSM 9396 | BGC0003172 | EntA, EntC |
| Marinobactin | Terasakiispira papahanaumokuakeensis DSM 29361 | BGC0003173 | Orn_monoox, TBH_Asp |
| Ornicorrugatin | Pseudomonas brassicacearum DSM 13227 | BGC0003174 | IBH_Asp, IBH_His, TBH_Asp |

Their inspection connects source protein predictions to the experimental study; product
identification does not demonstrate the activity of every annotated protein. The paper
also reports pyoverdine A214 from the P. brassicacearum strain. These study archives
were analyzed separately from the reference-BGC example panel.

The main archive is pinned by SHA-256
`638f968c12034b197ddf2b66c7450b3c76bb993faf7cf118d5972ee38228c8cc`
and publisher MD5 `301af6363922095f6a70dd9408378d0a`. The supplement's SHA-256 is
`5242bdba1a752bd914c3f9deebf908b5b79fbcea0153a52e077e71466631c522`.
Per-download receipts retain URLs, retrieval times, sizes, and hashes in ignored
`data/raw/elife_metallophores/`. Canonical assertions and API-response hashes are
preserved in the durable
[source assertions](../data/grounding/elife109154_source_assertions.jsonl) and
[acquisition receipt](../data/grounding/elife109154_acquisition_receipt.json).
The source and derived records preserve CC BY 4.0 attribution; the repository's CC0
dedication does not replace upstream terms.

The source-specific pipeline is reproducible through these recipes. Fetch/acquire
require network access; all other stages replay local bytes. The resolver refuses
release or sequence disagreement. A future live UniProt release cannot substitute for
the pinned responses without renewed acquisition and review.

```bash
just fetch-elife-metallophores
just seed-elife-metallophores --apply
just acquire-elife-metallophore-examples --apply
just resolve-elife-metallophore-examples --apply
# Inspect the resolution ledger and bind decisions to its resolution digests.
just promote-elife-metallophore-examples \
  --decisions data/curation/elife109154_example_decisions.jsonl --apply
just analyze-elife-metallophores --apply
just validate-all
just build-docs
just analyze-merges
```

The seeder and promotion commands default to dry-run. Promotion uses the existing
registered validated writer, preflights both closed-schema and semantic validation,
and installs records with their registries transactionally. Reapplying the reviewed
panel changes no trait records. Regression checks cover duplicate source rows,
identity/release/sequence mismatches, altered trait meaning, false-positive profile
filtering, missing receipts, and cached spreadsheet values.

Validation of the completed ingestion scanned 429,291 corpus records with zero
closed-schema errors and zero grounding findings. All 16 new family records also
passed `--require-qualified`. The full test suite passed with 2,867 tests passed and
51 skipped; the focused integration run passed 630 tests with five skipped. Lint,
writer-route auditing, source-registry checks, and curation-history validation passed.
The original 126 protein references and 127 evidence rows are preserved byte-for-byte.
SFLD's single-release execution contract remains enforced; a release-specific staging
registry is required when using it with the now multi-release durable registry.
The rebuilt documentation displays all 20 new records and all 33 examples. The merge
analyzer found no deterministic merge groups in the rebuilt corpus, and none of its
review pairs involve an `ELIFE109154_` identifier. The documentation scan uses
`Path.rglob`, which includes ignored trait YAML files; the generated merge plan was
also searched with `rg --no-ignore --hidden`.
