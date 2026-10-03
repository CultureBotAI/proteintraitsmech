# YAML Category Review: CDD CNP020 shard-1 target-protein grounding

Durable review handoff for [issue #943](https://github.com/CultureBotAI/proteintraitsmech/issues/943).
The original session copy is retained under the ignored category-review directory.

- Repository: CultureBotAI/proteintraitsmech
- Category: target-protein CDD assignments in `human-ecoli-yeast-target-cnp020-001of008`
- Selection Rule: all 56 approved alternatives on 52 exact record paths in deterministic shard 1 of 8 of the CDD slice of `human-ecoli-yeast-repair-cnp-020`
- Started UTC: adjudication preceded this PR review; no separate adjudication start timestamp was retained
- Finished UTC: 20261003T143347Z (initial review snapshot; final merge gates recorded below)
- Verdict: pass with two minor handoff findings (#943, #944), addressed by this report; bounded qualification-delta review, not complete scientific recuration or organism coverage

## Target Category

Review base: `828c03457158fb1b81ed9c8969d45cda994c1def`.
The 52 complete member records were read during scientific adjudication. The PR review
replays the installed delta and retained decisions, with fresh full-file checks of the
FGF2, SLURP2, FANCL DRWD-C, ST6GAL2, PanK4, and SARM1 ARM-domain records.
All 114 alternatives across 62 record groups have explicit decisions: 56 approvals,
57 non-target scope deferrals, and one already-satisfied ITPR1 assertion not replaced.

The installed delta is 56 legacy-example upgrades, 56 localized occurrences, 34 full-sequence
references, and zero new example accession IDs. It changes 52 records: 42 human, 11 yeast S288c,
and three E. coli K-12 occurrence assertions. Exact selected taxon IDs are 9606, 559292, and 83333.
This does not establish coverage of all human, E. coli, or S. cerevisiae proteins.

## Selection and Membership

Coordinates below are source-asserted, one-based inclusive, in the pinned canonical
UniProt sequence frame. Each row links the member record and the stable source model.
Exact release-bound evidence IDs, sequence checksums, and binding receipts are in the
durable records and grounding registries; CDD model links do not replace those protein-match facts.

| Record | Selected protein(s) and interval(s) | Source model |
| --- | --- | --- |
| [CDD:cd23975](../data/traits/sequence/domain/cdd/alpha-n-acetylgalactosaminide-alpha-2-6-sialyltransferase-3-st6galnac--cd23975.yaml) | UniProtKB:Q8NDV1 77–302 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23975) |
| [CDD:cd23990](../data/traits/sequence/domain/cdd/alpha-n-acetylneuraminide-alpha-2-8-sialyltransferase-5-alpha-n-acetyl-cd23990.yaml) | UniProtKB:O15466 98–370 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23990) |
| [CDD:cd23980](../data/traits/sequence/domain/cdd/beta-galactoside-alpha-2-3-sialyltransferase-1-st3gal-family-transfer--cd23980.yaml) | UniProtKB:Q11201 59–338 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23980) |
| [CDD:cd23986](../data/traits/sequence/domain/cdd/beta-galactoside-alpha-2-6-sialyltransferase-2-st6gal-family-members-a-cd23986.yaml) | UniProtKB:Q96JF0 245–514 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23986) |
| [CDD:cd23664](../data/traits/sequence/domain/cdd/brca1-a-and-brisc-complex-subunit-bre-brca1-a-and-brisc-complex-subuni-cd23664.yaml) | UniProtKB:Q9NXR7 10–378 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23664) |
| [CDD:cd23832](../data/traits/sequence/domain/cdd/c-terminal-double-rwd-domain-of-fanconi-anemia-group-l-protein-fancl-a-cd23832.yaml) | UniProtKB:Q9NW38 200–288 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23832) |
| [CDD:cd22852](../data/traits/sequence/domain/cdd/c-terminal-oligomerization-domain-of-the-survival-motor-neuron-family--cd22852.yaml) | UniProtKB:Q16637 256–284 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22852) |
| [CDD:cd22588](../data/traits/sequence/domain/cdd/central-coiled-coil-domain-of-geminin-coiled-coil-domain-containing-pr-cd22588.yaml) | UniProtKB:A6NCL1 73–133 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22588) |
| [CDD:cd23554](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-cd59-glycoprotein-and-similar-protei-cd23554.yaml) | UniProtKB:P13987 26–95 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23554) |
| [CDD:cd23561](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-secreted-ly-6-upar-related-protein-2-cd23561.yaml) | UniProtKB:P0DP57 23–97 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23561) |
| [CDD:cd23560](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-the-secreted-ly-6-upar-related-prote-cd23560.yaml) | UniProtKB:P55000 23–100 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23560) |
| [CDD:cd23320](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-10-fgf1-cd23320.yaml) | UniProtKB:O15520 72–205 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23320) |
| [CDD:cd23331](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-19-fgf1-cd23331.yaml) | UniProtKB:O95750 42–169 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23331) |
| [CDD:cd23314](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-2-fgf2--cd23314.yaml) | UniProtKB:P09038 161–285 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23314) |
| [CDD:cd23319](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-7-fgf7--cd23319.yaml) | UniProtKB:P21781 57–192 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23319) |
| [CDD:cd23322](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-8-fgf8--cd23322.yaml) | UniProtKB:P55075 52–196 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23322) |
| [CDD:cd23565](../data/traits/sequence/domain/cdd/first-extracellular-domain-ecd-found-in-ly6-plaur-domain-containing-pr-cd23565.yaml) | UniProtKB:Q6UWN5 22–116 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23565) |
| [CDD:cd22596](../data/traits/sequence/domain/cdd/first-kunitz-domain-of-bikunin-and-similar-proteins-this-subfamily-inc-cd22596.yaml) | UniProtKB:P02760 229–282 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22596) |
| [CDD:cd22734](../data/traits/sequence/domain/cdd/forkhead-associated-fha-domain-found-in-ras-interacting-protein-1-rain-cd22734.yaml) | UniProtKB:Q5U651 378–490 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22734) |
| [CDD:cd22718](../data/traits/sequence/domain/cdd/forkhead-associated-fha-domain-found-in-smad-nuclear-interacting-prote-cd22718.yaml) | UniProtKB:Q8TAD8 224–372 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22718) |
| [CDD:cd22714](../data/traits/sequence/domain/cdd/forkhead-associated-fha-domain-found-in-traf-interacting-protein-with--cd22714.yaml) | UniProtKB:Q96CG3 13–146 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22714) |
| [CDD:cd22932](../data/traits/sequence/domain/cdd/histone-fold-domain-found-in-taf6-like-rna-polymerase-ii-p300-cbp-asso-cd22932.yaml) | UniProtKB:Q9Y6J9 12–82 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22932) |
| [CDD:cd22931](../data/traits/sequence/domain/cdd/histone-fold-domain-found-in-transcription-initiation-factor-tfiid-sub-cd22931.yaml) | UniProtKB:P49848 12–77; UniProtKB:P53040 13–75 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22931) |
| [CDD:cd22900](../data/traits/sequence/domain/cdd/ligand-binding-sensor-domain-of-narx-and-related-chemoreceptors-the-pe-cd22900.yaml) | UniProtKB:P0AFA2 38–152 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22900) |
| [CDD:cd23288](../data/traits/sequence/domain/cdd/mir-domain-beta-trefoil-fold-found-in-inositol-1-4-5-trisphosphate-rec-cd23288.yaml) | UniProtKB:Q14571 218–439 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23288) |
| [CDD:cd23284](../data/traits/sequence/domain/cdd/mir-domain-beta-trefoil-fold-found-in-saccharomyces-cerevisiae-dolichy-cd23284.yaml) | UniProtKB:P31382 339–531; UniProtKB:P47190 332–525 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23284) |
| [CDD:cd23285](../data/traits/sequence/domain/cdd/mir-domain-beta-trefoil-fold-found-in-saccharomyces-cerevisiae-dolichy-cd23285.yaml) | UniProtKB:P46971 334–521 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23285) |
| [CDD:cd24153](../data/traits/sequence/domain/cdd/n-terminal-arm-repeat-domain-of-sarm1-sterile-alpha-and-tir-motif-cont-cd24153.yaml) | UniProtKB:Q6SZW1 94–399 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24153) |
| [CDD:cd23838](../data/traits/sequence/domain/cdd/n-terminal-double-rwd-domain-of-saccharomyces-cerevisiae-chromosome-tr-cd23838.yaml) | UniProtKB:Q02732 149–248 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23838) |
| [CDD:cd22809](../data/traits/sequence/domain/cdd/n-terminal-snare-complex-binding-domain-found-in-complexins-iii-and-iv-cd22809.yaml) | UniProtKB:Q8WVH0 42–85 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22809) |
| [CDD:cd23026](../data/traits/sequence/domain/cdd/n-terminus-of-dickkopf-related-protein-1-includes-the-first-cysteine-r-cd23026.yaml) | UniProtKB:O94907 16–139 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23026) |
| [CDD:cd24048](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-cell-division-protein-ftsa-and-simila-cd24048.yaml) | UniProtKB:P0ABH0 8–385 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24048) |
| [CDD:cd24111](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-ectonucleoside-triphosphate-diphospho-cd24111.yaml) | UniProtKB:Q9Y5L3 37–449 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24111) |
| [CDD:cd24114](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-ectonucleoside-triphosphate-diphospho-cd24114.yaml) | UniProtKB:O75356 47–421 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24114) |
| [CDD:cd24137](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-pantothenate-kinase-3-pank3-from-type-cd24137.yaml) | UniProtKB:Q9H999 13–365 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24137) |
| [CDD:cd24123](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-pantothenate-kinase-4-pank4-from-type-cd24123.yaml) | UniProtKB:Q04430 21–354; UniProtKB:Q9NVE7 36–366 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24123) |
| [CDD:cd24012](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-the-2-keto-3-deoxy-galactonokinase-dg-cd24012.yaml) | UniProtKB:P31459 5–289 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24012) |
| [CDD:cd24125](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-the-first-repeat-of-type-ii-hexokinas-cd24125.yaml) | UniProtKB:P52789 30–458 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24125) |
| [CDD:cd24090](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-the-first-repeat-of-type-iii-hexokina-cd24090.yaml) | UniProtKB:P52790 41–471 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24090) |
| [CDD:cd24092](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-type-iv-hexokinase-from-metazoan-hexo-cd24092.yaml) | UniProtKB:P35557 15–458 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24092) |
| [CDD:cd23072](../data/traits/sequence/domain/cdd/pdz-domain-1-of-protein-tyrosine-phosphatase-non-receptor-type-13-ptpn-cd23072.yaml) | UniProtKB:Q12923 1090–1181 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23072) |
| [CDD:cd23705](../data/traits/sequence/domain/cdd/protein-flattop-and-similar-proteins-protein-flattop-also-known-as-cil-cd23705.yaml) | UniProtKB:Q5VTH2 2–74 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23705) |
| [CDD:cd23440](../data/traits/sequence/domain/cdd/ricin-b-type-lectin-domain-beta-trefoil-fold-found-in-polypeptide-n-ac-cd23440.yaml) | UniProtKB:Q8NCW6 478–606 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23440) |
| [CDD:cd23148](../data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-saccharomyces-cerevisiae-radiation-se-cd23148.yaml) | UniProtKB:P10862 23–74 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23148) |
| [CDD:cd24164](../data/traits/sequence/domain/cdd/rwd-domain-containing-protein-3-c-terminal-domain-rwdd3-also-called-rs-cd24164.yaml) | UniProtKB:Q9Y3V2 139–247 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24164) |
| [CDD:cd23820](../data/traits/sequence/domain/cdd/rwd-domain-of-ring-finger-protein-14-rnf14-and-related-proteins-rnf14--cd23820.yaml) | UniProtKB:Q9UBS8 9–135 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23820) |
| [CDD:cd23703](../data/traits/sequence/domain/cdd/saccharomyces-cerevisiae-mitochondrial-small-ribosomal-subunit-protein-cd23703.yaml) | UniProtKB:P17558 9–224 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23703) |
| [CDD:cd22690](../data/traits/sequence/domain/cdd/second-forkhead-associated-fha-domain-found-in-saccharomyces-cerevisia-cd22690.yaml) | UniProtKB:P22216 577–695 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22690) |
| [CDD:cd23993](../data/traits/sequence/domain/cdd/seipin-and-similar-proteins-seipin-is-a-homo-oligomeric-integral-membr-cd23993.yaml) | UniProtKB:Q96G97 58–222 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23993) |
| [CDD:cd22571](../data/traits/sequence/domain/cdd/transcription-regulatory-protein-snf6-domain-family-snf6-is-a-nuclear--cd22571.yaml) | UniProtKB:P18888 70–261 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22571) |
| [CDD:cd23797](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-ubiquitin-con-cd23797.yaml) | UniProtKB:P28263 6–143 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23797) |
| [CDD:cd23803](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-ubiquitin-con-cd23803.yaml) | UniProtKB:P49427 11–180; UniProtKB:Q712K3 11–180 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23803) |

Ten record groups are excluded from the installed delta and remain byte-identical to the base.
Except for the already-satisfied ITPR1 assertion, their candidate alternatives are outside the
three selected taxa; that describes this queue, not biological absence from those taxa.

- [CDD:cd23509](../data/traits/sequence/domain/cdd/antifungal-protein-ginkbilobin-2-like-domains-found-in-plants-this-fam-cd23509.yaml)
- [CDD:cd22765](../data/traits/sequence/domain/cdd/arabidopsis-thaliana-deubiquitinating-enzyme-otu1-and-similar-plant-pr-cd22765.yaml)
- [CDD:cd22637](../data/traits/sequence/domain/cdd/drosophila-melanogaster-kunitz-domains-5-6-7-and-caenorhabditis-elegan-cd22637.yaml)
- [CDD:cd23548](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-lymphocyte-antigen-6-complex-locus-p-cd23548.yaml)
- [CDD:cd23330](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-14-fgf1-cd23330.yaml)
- [CDD:cd22909](../data/traits/sequence/domain/cdd/histone-fold-domain-mainly-found-in-archaeal-histone-fold-proteins-his-cd22909.yaml)
- [CDD:cd23287](../data/traits/sequence/domain/cdd/mir-domain-beta-trefoil-fold-found-in-inositol-1-4-5-trisphosphate-rec-cd23287.yaml) — ITPR1 Q14643, 224–445, already qualified; original evidence identity retained.
- [CDD:cd22815](../data/traits/sequence/domain/cdd/pp1c-binding-domain-found-in-protein-phosphatase-1-regulatory-subunit--cd22815.yaml)
- [CDD:cd23160](../data/traits/sequence/domain/cdd/prefoldin-alpha-subunit-archaeal-archaeal-alpha-subunit-of-prefoldin-g-cd23160.yaml)
- [CDD:cd23360](../data/traits/sequence/domain/cdd/soybean-trypsin-inhibitor-sti-like-domain-beta-trefoil-fold-found-in-c-cd23360.yaml)

Shard 2 and the unfinished isolated target-profile InterPro crawl are excluded from this
durable delta. Ignored staging remains available locally but is not distributed with this report.

## Validation

Completed before this PR review:

- Guarded promotion: 56 approvals, 52 writes, 34 new protein references.
- Scoped `just validate-all`: 52 records, zero semantic findings, exit 0.
- Focused grounding, registry, pilot, and browser tests: 389 passed.
- Pilot replay, registry layout, writer audit, and append-only history validation: pass.

Fresh adversarial replay:

- Every old protein reference, evidence object, and binding is preserved.
- Every old example field and occurrence, and all non-example record fields, are preserved.
- Exactly 56 upgrades and new occurrences, 34 references, and zero new example IDs.
- Selected-example projections pass `require_qualified=True` for all 56 admissions.
  This is not a require-qualified pass for the remaining legacy examples in those files.
- All ten excluded groups, including the existing ITPR1 assertion, are byte-identical.
- Fresh provider replay: all 114 alternatives reproduce the frozen entry hashes,
  releases, source-asserted intervals, sequence lengths/checksums, and taxa; exit 0.
  The diagnostic's first invocation had an incorrect argument name and did not run
  verification; the corrected invocation passed. No source or record changed.

After the initial review snapshot, full `just validate-all` completed successfully:
429,293 files, zero strict errors and zero semantic findings. The full regression suite
and browser regeneration/Pages audit are still running at publication. Their final measured
outcomes must be recorded in the PR before merge; they are not inferred passes here.
No schema, validator, browser code, hierarchy, causal graph, or mapping status is changed.
Broad term recuration and experimental verification of every inherited background claim
were not performed.

## Lump and Split Review

This is a workflow cohort, not a biological equivalence class. No equivalence is inferred from
shared proteins, parent models, or folds. Distinct TAF6/TAF6L, PMT subfamilies, FGF members,
FHA repeats, HK repeats, PANK3/PANK4, and RWD-domain positions remain distinct.
No record merge, split, parent change, or exact-xref change is part of this PR.

## Identity and Grounding

All selected occurrences assert their containing model directly:
`source_trait_id == trait_id`, `LOCALIZED`, `INTERPRO_MATCH`, `UNIPROT_CANONICAL`.
Fourteen selected assertions use grouped-location identity and 42 use a single flat location.
Their InterPro release is 110.0; sequence references are pinned to UniProt 2026_03.
No hierarchy inference, local alignment, sequence scanning, or inferred isoform offset is used.

Registry totals are 12,425 protein references and 20,558 evidence/binding objects each.
The prior 12,391 references and 20,502 evidence/binding objects remain unchanged.
The pilot manifest updates only its registry checksum; observation bytes are unchanged.
All reviewed source records retain their public-domain CDD license and SEEDED mapping status.
Qualification of an occurrence is not human approval of the whole record.

## Evidence Patterns

The scientific decisions preserve the distinction between a domain assignment and proven
function, catalysis, binding, or architecture of every family member:

- **CDD:cd22571:** Yeast SNF6 conserved source domain, not intrinsic ATPase activity inferred from its SWI/SNF complex.
- **CDD:cd22588:** GEMC1 central coiled-coil domain, distinguished from related geminin-family members.
- **CDD:cd22596:** First bikunin Kunitz domain in the full AMBP precursor, not the second repeat or alpha-1-microglobulin region.
- **CDD:cd22690:** Yeast Rad53 second FHA domain, distinguished from FHA1 and the kinase domain.
- **CDD:cd22714:** TIFA FHA domain, not a newly inferred Thr9 phosphorylation-site annotation.
- **CDD:cd22718:** SNIP1 FHA domain, exact named-protein identity.
- **CDD:cd22734:** RASIP1/RAIN FHA domain; the source explicitly allows missing phosphothreonine-binding residues, so binding activity is not inferred.
- **CDD:cd22809:** Complexin-3 SNARE-complex-binding domain. Human complexin-4 Q7Z7G2 remains an unqueued legacy example.
- **CDD:cd22852:** SMN C-terminal YG-box oligomerization domain, not its Tudor domain; the accession represents the named canonical protein.
- **CDD:cd22900:** E. coli NarX periplasmic sensor domain, not its downstream histidine-kinase domain.
- **CDD:cd22931:** TAF6 N-terminal histone-fold domain; both human and yeast exact carriers retained.
- **CDD:cd22932:** TAF6L histone-fold domain, distinguished from TAF6.
- **CDD:cd23026:** DKK1 N-terminal region including Cys-1, matching the model span rather than its Cys-2 domain.
- **CDD:cd23072:** PTPN13 first PDZ domain, distinguished from its other four PDZ domains and phosphatase domain.
- **CDD:cd23148:** Yeast Rad18 N-terminal RING-HC domain, exact named-protein identity.
- **CDD:cd23284:** Yeast PMT2/PMT3 MIR domains. PMT6 is separately named in the definition and remains unqueued/unqualified.
- **CDD:cd23285:** Yeast PMT4 MIR domain; correct PMT subfamily.
- **CDD:cd23288:** ITPR2 MIR domain, distinguished from the ITPR1 model.
- **CDD:cd23314:** FGF2 beta-trefoil domain on the pinned 288-residue canonical sequence; no shorter-isoform coordinate offset inferred.
- **CDD:cd23319:** FGF7 beta-trefoil domain, exact named-protein identity.
- **CDD:cd23320:** FGF10 beta-trefoil domain, exact growth-factor identity.
- **CDD:cd23322:** FGF8 beta-trefoil domain, exact named-protein identity.
- **CDD:cd23331:** FGF19 beta-trefoil domain, exact human identity without transfer of all narrative signaling claims.
- **CDD:cd23440:** GALNT11 C-terminal ricin-type lectin domain, not the upstream glycosyltransferase region.
- **CDD:cd23554:** CD59 extracellular LU domain in the precursor coordinate frame.
- **CDD:cd23560:** SLURP1 extracellular LU domain. Definition also mentions LYPD2, requiring separate source/inheritance evidence.
- **CDD:cd23561:** SLURP2 extracellular LU domain; no inferred processing or receptor activity annotation.
- **CDD:cd23565:** LYPD5 first extracellular LU domain, not the second repeat.
- **CDD:cd23664:** BRE conserved source region spans its broader architecture; not an individual UEV repeat or inferred DUB activity.
- **CDD:cd23703:** Yeast mitochondrial mS26/PET12 source signature, exact named-protein identity.
- **CDD:cd23705:** Flattop conserved source segment; localized classification does not assert whole-protein coverage.
- **CDD:cd23797:** Yeast Ubc8 is explicitly included in the UBE2H subfamily. Human UBE2H P62256 remains unqueued.
- **CDD:cd23803:** Both human UBE2R1 and UBE2R2 catalytic-domain classifications are explicitly covered by the source subfamily.
- **CDD:cd23820:** RNF14 N-terminal RWD domain, not its RBR ligase domains.
- **CDD:cd23832:** FANCL C-terminal member of its double-RWD domain, distinct from DRWD-N and the RING domain.
- **CDD:cd23838:** Ctf19 first member of the tandem RWD pair; N-terminal is relative to the pair, not residue 1.
- **CDD:cd23975:** ST6GALNAC3 GT29 domain, not a generic sialyltransferase assignment.
- **CDD:cd23980:** ST3GAL1 GT29 domain with exact named-protein identity.
- **CDD:cd23986:** ST6GAL2 GT29 domain. Existing definition contains a contradictory alpha-2,3 phrase despite naming ST6GAL2 and specifying alpha-2,6 linkage; that source-prose correction remains pending and is not validated by this domain match.
- **CDD:cd23990:** ST8SIA5 GT29 domain; the protein synonym alpha-2,8-sialyltransferase 8E matches this model.
- **CDD:cd23993:** Human seipin source domain. Yeast Sei1 has a different source model and needs supported direct or inherited evidence.
- **CDD:cd24012:** E. coli DgoK ASKHA signature; broad source span retained without inferring narrower nucleotide-binding coordinates.
- **CDD:cd24048:** E. coli FtsA source ASKHA model; retain the exact broad model span.
- **CDD:cd24090:** HK3 first two-domain repeat, distinguished from its second repeat.
- **CDD:cd24092:** HK4/GCK source two-domain unit, not an inferred duplicated repeat.
- **CDD:cd24111:** ENTPD2/NTPDase2 conserved source domain, exact named-protein identity.
- **CDD:cd24114:** ENTPD5/NTPDase5 conserved source domain, exact named-protein identity.
- **CDD:cd24123:** PanK4-like sequence domain includes yeast CAB1 and human PANK4. CAB1 classification does not assert an animal kinase-phosphatase fusion; human localization is the N-terminal pseudoPanK domain, not C-terminal phosphatase activity.
- **CDD:cd24125:** HK2 first two-domain repeat, distinguished from its second repeat.
- **CDD:cd24137:** PANK3 type-II PanK source model, distinguished from the PANK4 pseudoenzyme.
- **CDD:cd24153:** SARM1 N-terminal ARM domain, distinct from its SAM and catalytic TIR domains.
- **CDD:cd24164:** RWDD3 C-terminal domain, not its N-terminal RWD domain; the source's AlphaFold fold prediction is not experimental structure evidence.

The [ST6GAL2 source model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=467714)
was inspected again during PR review: its alpha-2,3 wording conflicts with its alpha-2,6
identity/linkage description, while its human Q96JF0 alignment spans 245–514.
The domain qualification does not repair or certify that inherited prose.

The [PanK4 source model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24123)
explicitly describes the human N-terminal domain as inactive pseudoPanK.
The admitted Q9NVE7 36–366 interval is not the C-terminal phosphatase.
Yeast CAB1 Q04430 21–354 membership does not prove the animal fusion architecture.

iModulonDB is not applicable to this exact domain-coordinate/sequence question;
expression-module membership cannot establish these locations.
Content-addressed evidence hashes are integrity checks, not provider cryptographic signatures.

## Completeness Patterns

Five existing target examples remain legacy-unverified and outside this shard's queue:
CPLX4 Q7Z7G2 on CDD:cd22809, PMT6 P42934 on CDD:cd23284, UBE2H P62256 on CDD:cd23797,
FGF14 Q92915 on CDD:cd23330, and PPP1R3C Q9UQK1 on CDD:cd22815.
The final comparison covers all examples in all 62 selected record groups and the full
ignored candidate/resolved ledgers: 55 records contain target examples, totaling 57 qualified
and five legacy-unverified examples. The initial 53-group target-candidate projection missed
the two human examples in excluded FGF14 and PPP1R3C groups; issue #944 records the correction.
Non-target-only candidate alternatives do not imply non-target-only records.
No biological absence is inferred. All five accessions remain in the separate acquisition list;
Q92915 and Q9UQK1 were verified at lines 20703 and 25020, respectively. Future qualification
requires source-asserted coordinates and the reviewed promoter, not this reporting correction.

Definition-named relatives, other strains, unreviewed proteins, isoforms, and source locations
absent from the historical queue remain broader discovery/review work. No new accession ID is
added by this delta; a queue of existing examples cannot prove all-protein inclusion.

## Findings

- **Minor, #943:** the scientific review handoff was available only in ignored staging.
  This tracked report publishes the complete member roster, coordinates, source links,
  per-record scope notes, exclusions, and remaining gaps. The execution checkpoint retains
  the local replay hashes and separates shard-2 staging.
- **New blocker/major in the installed qualification delta:** none found in this review.
  Existing source-prose conflicts and incomplete coverage are retained limitations, not
  silently fixed or certified by the new qualification status.
- **Minor, #944:** the initial completeness handoff omitted FGF14 and PPP1R3C because
  it counted only target-candidate groups. An all-62-group scan corrects the denominator
  and enumerates all five legacy target examples. The excluded records remain unchanged.

## Recommended Edits

Merge only this reviewed shard-1 delta and its handoff after all merge gates pass.
Do not promote shard 2 or complete the overall organism-coverage goal as a side effect.
Future source-prose correction belongs to a source-aware registered record editor;
future examples/coordinates belong to the reviewed grounding promoter.

## Follow-up Checks

Verify full-corpus validation, full regressions, browser rebuild, Pages budgets, tracked report
links/counts, and required GitHub checks on the final head. Close #943 and #944 only with the merged fix.
After merging, verify main and exact local/remote feature-branch deletion while preserving
ignored source acquisition and future-shard staging.

## Additional Notes

The handoff search included ignored and hidden Markdown under research/, reports/, .claude/,
and README.md; GitHub duplicate-issue searches were also checked.
The protein-grounding skill kept all coordinates source-asserted and the record-review skill
kept functional caveats, unchanged assertions, and coverage limitations visible.
