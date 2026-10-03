# YAML Category Review: CDD CNP020 shard-0 target-protein grounding

Durable copy of the local session report
`reports/yaml_category_review/20261003T123310Z-cdd-cnp020-shard0-target-grounding.md`.
The original remains a gitignored session artifact; this copy preserves the review-time
findings and updates relative links for publication under `research/` (PR review issue #942).

- Repository: CultureBotAI/proteintraitsmech
- Category: reviewed target-organism CDD assignments in `human-ecoli-yeast-target-cnp020-000of008`
- Selection Rule: all 46 approved alternatives, grouped into 41 exact record paths, in deterministic shard 0 of 8 of the CDD slice of `human-ecoli-yeast-repair-cnp-020`
- Started UTC: not separately timestamped; grounding adjudication preceded the PR review
- Finished UTC: 20261003T123310Z
- Verdict: pass with one minor handoff issue, addressed by the accompanying checkpoint; this is a bounded promotion review, not complete scientific recuration or organism coverage.

## Target Category

The user requested commit, push, adversarial review, issue handling, merge, and branch cleanup.
Review base is `0b7bc5bcfae788444dfab2996ca42cbaf4be8cc5`.
The full 41 target records were inspected during adjudication; this review checks their installed
qualification delta, scope, and preservation. Two selected records were already qualified and
remain byte-identical. The other 39 receive 44 existing-example upgrades and 44 localized
occurrences (31 human, nine yeast S288c, four E. coli K-12), with 22 new full-sequence references.
No new example accession is added. Exact target taxa are 9606, 559292, and 83333.

## Selection and Membership

Each row names a complete member file and the selected canonical-frame coordinates (one-based,
inclusive). CDD links identify the source models; release-pinned protein-match evidence,
sequence hashes, and binding receipts live in the durable grounding registries.

| Record | Selected protein(s) and interval(s) | Source model |
| --- | --- | --- |
| [CDD:cd23400](../data/traits/sequence/domain/cdd/arabinose-binding-domain-abd-beta-trefoil-fold-found-in-otogelin-otog--cd23400.yaml) | UniProtKB:Q6ZRI0 1245–1396 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23400) |
| [CDD:cd23523](../data/traits/sequence/domain/cdd/brca1-a-complex-subunit-abraxas-1-brca1-a-complex-subunit-abraxas-1-al-cd23523.yaml) | UniProtKB:Q6UWZ7 2–380 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23523) |
| [CDD:cd23524](../data/traits/sequence/domain/cdd/brisc-complex-subunit-abraxas-2-brisc-complex-subunit-abraxas-2-is-als-cd23524.yaml) | UniProtKB:Q15018 1–255 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23524) |
| [CDD:cd22658](../data/traits/sequence/domain/cdd/c-terminal-domain-of-stimulator-of-interferon-genes-sting-protein-in-m-cd22658.yaml) | UniProtKB:Q86WV6 154–337 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22658) |
| [CDD:cd22574](../data/traits/sequence/domain/cdd/c-terminal-histone-fold-domain-of-saccharomyces-cerevisiae-co-purified-cd22574.yaml) | UniProtKB:P43618 272–361 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22574) |
| [CDD:cd22578](../data/traits/sequence/domain/cdd/cask-lin-2-interaction-domain-cid-of-mint1-and-similar-proteins-mint1--cd22578.yaml) | UniProtKB:Q02410 343–388 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22578) |
| [CDD:cd22948](../data/traits/sequence/domain/cdd/coatomer-wd-associated-region-from-coatomer-subunit-alpha-coatomer-sub-cd22948.yaml) | UniProtKB:P53621 324–774; UniProtKB:P53622 328–777 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22948) |
| [CDD:cd23011](../data/traits/sequence/domain/cdd/colipase-colipase-also-called-clps-is-a-protein-co-enzyme-required-for-cd23011.yaml) | UniProtKB:P04118 23–106 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23011) |
| [CDD:cd22966](../data/traits/sequence/domain/cdd/dimerization-docking-d-d-domain-found-in-the-dpy30-domain-containing-p-cd22966.yaml) | UniProtKB:Q8WWB3 2–43 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22966) |
| [CDD:cd23328](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-12-fgf1-cd23328.yaml) | UniProtKB:P61328 68–206 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23328) |
| [CDD:cd23329](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-13-fgf1-cd23329.yaml) | UniProtKB:Q92913 65–212 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23329) |
| [CDD:cd23327](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-20-fgf2-cd23327.yaml) | UniProtKB:Q9NP95 56–208 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23327) |
| [CDD:cd23333](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-23-fgf2-cd23333.yaml) | UniProtKB:Q9GZV9 25–169 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23333) |
| [CDD:cd22666](../data/traits/sequence/domain/cdd/forkhead-associated-fha-domain-found-in-checkpoint-kinase-2-chk2-and-s-cd22666.yaml) | UniProtKB:O96017 93–204 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22666) |
| [CDD:cd22700](../data/traits/sequence/domain/cdd/forkhead-associated-fha-domain-found-in-forkhead-associated-domain-con-cd22700.yaml) | UniProtKB:B1AJZ9 2–97 (already installed) | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22700) |
| [CDD:cd22906](../data/traits/sequence/domain/cdd/histone-fold-domain-found-in-dr1-associated-protein-1-drap1-and-simila-cd22906.yaml) | UniProtKB:P40096 50–124; UniProtKB:Q14919 9–83 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22906) |
| [CDD:cd22623](../data/traits/sequence/domain/cdd/kunitz-domain-1-of-hepatocyte-growth-factor-activator-inhibitor-1-hai--cd22623.yaml) | UniProtKB:O43278 245–303 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22623) |
| [CDD:cd22621](../data/traits/sequence/domain/cdd/kunitz-type-domain-1-kd1-of-hepatocyte-growth-factor-activator-inhibit-cd22621.yaml) | UniProtKB:O43291 36–88 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22621) |
| [CDD:cd23293](../data/traits/sequence/domain/cdd/mir-domain-beta-trefoil-fold-found-in-family-of-metazoan-stromal-cell--cd23293.yaml) | UniProtKB:Q9HCN8 36–210 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23293) |
| [CDD:cd22884](../data/traits/sequence/domain/cdd/mitochondrial-import-receptor-subunit-tom22-and-similar-proteins-mitoc-cd22884.yaml) | UniProtKB:P49334 63–128; UniProtKB:Q9NS69 49–105 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22884) |
| [CDD:cd23953](../data/traits/sequence/domain/cdd/n-terminal-domain-of-fungal-ribosome-associated-j-protein-zuotin-and-s-cd23953.yaml) | UniProtKB:P32527 14–50; UniProtKB:Q99543 13–49 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23953) |
| [CDD:cd22560](../data/traits/sequence/domain/cdd/n-terminal-reticulon-homology-domain-of-reticulophagy-regulator-1-reti-cd22560.yaml) | UniProtKB:Q9H6L5 68–259 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22560) |
| [CDD:cd24008](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-glucokinase-glk-and-similar-proteins--cd24008.yaml) | UniProtKB:P0A6V8 5–308 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24008) |
| [CDD:cd24057](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-n-acetyl-d-glucosamine-kinase-nagk-an-cd24057.yaml) | UniProtKB:P75959 1–299 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24057) |
| [CDD:cd24126](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-the-first-repeat-of-hexokinase-domain-cd24126.yaml) | UniProtKB:Q2TB90 30–458 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24126) |
| [CDD:cd24130](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-the-second-repeat-of-hexokinase-domai-cd24130.yaml) | UniProtKB:Q2TB90 478–910 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24130) |
| [CDD:cd24091](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-the-second-repeat-of-types-i-ii-and-i-cd24091.yaml) | UniProtKB:P52790 491–916 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24091) |
| [CDD:cd22745](../data/traits/sequence/domain/cdd/otu-ovarian-tumor-domain-of-ubiquitin-thioesterase-otu1-and-similar-pr-cd22745.yaml) | UniProtKB:P43558 108–258; UniProtKB:Q5VVQ6 148–307 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22745) |
| [CDD:cd22799](../data/traits/sequence/domain/cdd/otu-ovarian-tumor-domain-of-ubiquitin-thioesterase-otulin-and-similar--cd22799.yaml) | UniProtKB:Q96BN8 80–345 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22799) |
| [CDD:cd23074](../data/traits/sequence/domain/cdd/pdz-domain-of-microtubule-associated-serine-threonine-mast-protein-kin-cd23074.yaml) | UniProtKB:Q6P0Q8 1101–1193 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23074) |
| [CDD:cd23076](../data/traits/sequence/domain/cdd/pdz-domain-of-microtubule-associated-serine-threonine-mast-protein-kin-cd23076.yaml) | UniProtKB:O15021 1138–1232 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23076) |
| [CDD:cd23117](../data/traits/sequence/domain/cdd/ring-finger-h2-subclass-found-in-saccharomyces-cerevisiae-transmembran-cd23117.yaml) | UniProtKB:P36096 693–757 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23117) |
| [CDD:cd23822](../data/traits/sequence/domain/cdd/rwd-domain-of-saccharomyces-cerevisiae-protein-yih1-and-related-protei-cd23822.yaml) | UniProtKB:P25637 8–112 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23822) |
| [CDD:cd23636](../data/traits/sequence/domain/cdd/second-extracellular-domain-ecd-found-in-cd177-antigen-and-similar-pro-cd23636.yaml) | UniProtKB:Q8N6Q3 128–204 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23636) |
| [CDD:cd23566](../data/traits/sequence/domain/cdd/second-extracellular-domain-ecd-found-in-ly6-plaur-domain-containing-p-cd23566.yaml) | UniProtKB:Q6UWN5 125–217 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23566) |
| [CDD:cd23348](../data/traits/sequence/domain/cdd/second-fascin-like-domain-beta-trefoil-fold-found-in-fascin-and-simila-cd23348.yaml) | UniProtKB:Q16658 139–258 (already installed) | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23348) |
| [CDD:cd22869](../data/traits/sequence/domain/cdd/second-rim-rtt107-interaction-motif-of-saccharomyces-cerevisiae-struct-cd22869.yaml) | UniProtKB:Q12098 535–587 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22869) |
| [CDD:cd23624](../data/traits/sequence/domain/cdd/third-extracellular-domain-ecd-found-in-cd177-antigen-and-similar-prot-cd23624.yaml) | UniProtKB:Q8N6Q3 208–299 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23624) |
| [CDD:cd24138](../data/traits/sequence/domain/cdd/trna-cytidine-32-2-sulfurtransferase-and-similar-proteins-trna-cytidin-cd24138.yaml) | UniProtKB:P76055 32–216 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24138) |
| [CDD:cd23810](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-like-domain-of-baculovi-cd23810.yaml) | UniProtKB:Q9NR09 4572–4776 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23810) |
| [CDD:cd23943](../data/traits/sequence/domain/cdd/universal-stress-protein-e-repeat-1-uspe-is-a-tandem-type-usp-that-con-cd23943.yaml) | UniProtKB:P0AAC0 4–146 | [CDD](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23943) |

The 50 non-target alternatives in the 96-row ledger are explicit scope deferrals, not biological
rejections. They remain unmodified. Fifteen non-target-only record groups were retained by the
selector but excluded from target promotion:

- [CDD:cd22786](../data/traits/sequence/domain/cdd/double-psi-beta-barrel-fold-of-yuic-subfamily-proteins-the-yuic-subfam-cd22786.yaml)
- [CDD:cd23615](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-the-activin-receptor-type-2-actr-ii--cd23615.yaml)
- [CDD:cd23592](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-ly6-upar-superfamily-three-finger-domain-tfd--cd23592.yaml)
- [CDD:cd23321](../data/traits/sequence/domain/cdd/fgf-domain-beta-trefoil-fold-found-in-fibroblast-growth-factor-22-fgf2-cd23321.yaml)
- [CDD:cd23345](../data/traits/sequence/domain/cdd/first-fascin-like-domain-beta-trefoil-fold-found-in-fascin-2-and-simil-cd23345.yaml)
- [CDD:cd22532](../data/traits/sequence/domain/cdd/first-type-ii-k-homology-kh-rna-binding-domain-found-in-archaeal-cleav-cd22532.yaml)
- [CDD:cd24100](../data/traits/sequence/domain/cdd/n-terminal-nucleotide-binding-domain-nbd-of-methanocaldococcus-jannasc-cd24100.yaml)
- [CDD:cd24131](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-trna-n6-adenosine-threonylcarbamoyltr-cd24131.yaml)
- [CDD:cd23077](../data/traits/sequence/domain/cdd/pdz-domain-of-pdz-domain-containing-protein-gipc1-pdz-psd-95-postsynap-cd23077.yaml)
- [CDD:cd22585](../data/traits/sequence/domain/cdd/rcat-domain-of-atp-dependent-rna-helicase-deah12-and-similar-proteins--cd22585.yaml)
- [CDD:cd23275](../data/traits/sequence/domain/cdd/second-cysteine-rich-cys-2-domain-of-dickkopf-related-protein-4-dickko-cd23275.yaml)
- [CDD:cd23635](../data/traits/sequence/domain/cdd/second-extracellular-domain-ecd-found-in-ly6-plaur-domain-containing-p-cd23635.yaml)
- [CDD:cd23369](../data/traits/sequence/domain/cdd/soybean-trypsin-inhibitor-sti-like-domain-beta-trefoil-fold-found-in-a-cd23369.yaml)
- [CDD:cd23355](../data/traits/sequence/domain/cdd/third-fascin-like-domain-beta-trefoil-fold-found-in-drosophila-melanog-cd23355.yaml)
- [CDD:cd22533](../data/traits/sequence/domain/cdd/type-ii-k-homology-kh-rna-binding-domain-found-in-bacillus-subtilis-up-cd22533.yaml)

The next shard `human-ecoli-yeast-target-cnp020-001of008` and the isolated
`target-profile-interpro-completion-2026-10-03` acquisition are excluded from this durable delta.

## Validation

Completed at report time:

- Guarded promotion preflight and apply: 46 approvals, 39 record writes, two already present.
- Strict validation and migration-safe grounding validation of all 41 target records: exit 0.
- `validate_record(..., require_qualified=True)` on the 46 selected-example projections:
  zero findings. This is not a require-qualified pass for every legacy example in those files.
- Independent semantic comparison to the Git base: preserved every old protein reference,
  evidence row, binding, example field, occurrence, and non-example record field;
  exactly 44 upgrades, 44 new occurrences, 22 new references, and zero new example IDs.
- `just check-grounding-registries`: 20,502 evidence and 20,502 binding rows, all structural
  checks pass. Protein registry: 12,391 references.
- `just check-biophysical-pilot`, `just audit-writers`, and `just validate-history`: pass.
  Only the pilot manifest's protein-registry checksum changed; observation bytes did not.
- Docs consistency, landing, Pages, registry layout, and biophysical pilot tests: 155 passed.
- `tests/test_validate_uniprot_grounding.py`: 234 passed.
- `git diff --check`: pass.

Full `uv run --no-sync just validate-all` and
`uv run --no-sync just build-docs && uv run --no-sync just audit-pages --site docs`
were still running at this report's finish; they are merge gates, not claimed passes here.
The direct system-Python docs attempt failed for missing PyYAML before generating artifacts;
the running replacement uses the project environment. Final gate results belong in the PR.
No schema, validator, browser code, causal graph, or hierarchy edge is changed. Broad ontology
term recuration and experimental verification of all inherited background prose were not performed.

## Lump and Split Review

This is a workflow cohort, not a proposed biological equivalence class.
Distinct CDD models remain separate, including HKDC1 repeat 1/repeat 2, CD177 extracellular
repeat 2/repeat 3, FGF12/13/20/23, MAST2/MAST4 PDZ domains, and Abraxas 1/2.
Two proteins sharing a domain or parent does not imply interchangeable function or identity.
No merge, split, synonym, parent, or cross-reference mutation is proposed by this promotion.

## Identity and Grounding

All admitted occurrences assert their containing exact CDD ID directly:
`source_trait_id == trait_id`, `LOCALIZED`, `INTERPRO_MATCH`,
`UNIPROT_CANONICAL`. Frozen InterPro 110.0 coordinates and normalized provider digests were
checked against the selected alternatives; 19 use grouped-location identity and 27 a single
flat location. Full sequences are pinned to UniProt 2026_03, with lengths and SHA-256 checksums.
The official UniProt fetch receipt accounts for all 91 requested canonical accessions; 62 extra
isoform responses were not promoted without exact isoform-coordinate evidence.
Source licenses and `mapping_status: SEEDED` remain unchanged. Qualification is not human
approval of the complete record.

## Evidence Patterns

No local alignment, motif inference, generic feature track, or family co-membership was used to
invent coordinates. Existing source-selection notes are retained rather than rewritten as
experimental proof. The content-addressed facts here are checksummed data objects, not
cryptographic signatures by the source provider.

SLX4 illustrates the scope distinction: the admitted Q12098 RIM2 span is 535–587.
[Wan et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC6745058/)
(DOI:10.1016/j.molcel.2019.05.035) supports the Rtt107 interaction, not intrinsic nuclease
catalysis by that motif. [The SMX DNA Repair Tri-nuclease](https://pmc.ncbi.nlm.nih.gov/articles/PMC5344696/)
distinguishes catalytic nuclease subunits from the SLX4 scaffold. The unchanged source-derived
definition's subunit/complex conflation remains a separate scientific curation caveat.

iModulonDB is not applicable to this exact CDD coordinate/sequence classification question;
expression-module membership would not establish these domain locations.

## Completeness Patterns

DYDC2 Q96IM9 on CDD:cd22966 and SDF2 Q99470 on CDD:cd23293 remain legacy-unverified.
Their accessions occur in the separate acquisition list, verified at lines 21274 and 21938.
They were not silently dropped from records. This batch therefore does not even complete all
existing target examples in its own reviewed cohort, let alone all proteomes/strains/isoforms.

A non-target mouse CD177 location (Q8R2S8, CDD:cd23636, 506–580) seen during adjudication is
not represented in this historical queue. No mouse assertion was promoted in this pass; this
reinforces that queue exhaustion is not exhaustive source-location coverage.

## Findings

- **Minor, #940:** durable promotion handoff was missing from tracked documentation.
  The ignored decision artifacts alone did not expose actual delta, replay hashes, or known
  gaps to a fresh checkout. Owner: `research/uniprot-organism-protein-grounding-plan.md`.
  Addressed by its CNP020 shard-0 checkpoint, this report, and an append-only batch history record.
- **Blocker/major introduced by this qualification delta:** none found.
  The unchanged SLX4 prose and unresolved example/source coverage above are explicitly retained
  limitations, not certified by this review or silently reported as fixed.

## Recommended Edits

Merge only the guarded shard-0 records/registries, refreshed pilot pin, and durable handoff after
all gates pass. Do not promote shard 1, mark the overall coverage goal complete, or rewrite
source-derived biological prose as a side effect of this PR. Follow up on DYDC2/SDF2 through the
reviewed grounding pipeline and on SLX4 wording through a source-aware registered editor.

## Follow-up Checks

Confirm full-corpus validation, browser regeneration, Pages size limits, and the four required
GitHub checks on the final PR head before merge. Verify #940 is closed by the merged fix.
Re-fetch main and verify local/remote feature-branch cleanup while preserving ignored acquisition
and adjudication artifacts for continuation.

## Additional Notes

The missing-checkpoint search covered Markdown under research/, reports/, .claude/, and
README.md with `rg --hidden --no-ignore`; ignored files were included.
All selected records have public-domain CDD provenance; no license disposition was broadened.
Report limits are intentional: no blanket claim of functional proof, new examples, complete
target coverage, or independent human approval is made.
