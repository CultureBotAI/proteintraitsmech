# YAML Category Review: CDD CNP020 shard-2 target-protein grounding

- Repository: CultureBotAI/proteintraitsmech
- Category: target-protein domain qualifications in `human-ecoli-yeast-target-cnp020-002of008`
- Selection Rule: all 112 queued alternatives across 68 exact CDD record groups; all 61 approved assertions reviewed, including two previously installed no-ops
- Started UTC: not separately timestamped; first retained publication-review timestamp is 20261003T154341Z, and scientific adjudication preceded this run
- Finished UTC: 2026-10-03 (source/delta review and full local validation complete; final publication-gate outcomes belong in the PR)
- Verdict: qualification-delta review passes; one major dependency finding and one minor handoff finding addressed, with CI/build gates still required before merge

## Target Category

Base: `cf9adc35d5e8af97f814448fc46e7e8ec4a7062e`.
The registered promoter installed 59 legacy-example qualifications and 59 localized
occurrences across 54 records. It added 37 full-sequence references and **zero new
example accession IDs**. The delta comprises 44 human, 11 yeast S288c, and four
E. coli K-12 assertions. The two previously installed human assertions are byte-identical.

All 68 records were read during the retained scientific adjudication. This publication
review replays every provider assertion and installed delta, reviews every retained
selected scope note, and freshly reads the complete KIF28P, VRTN, EVA1C repeat 2,
AKTIP, INO80B, yeast Sei1, T2SSL, and HK1-repeat-1 records. It is not a new
claim-by-claim literature recuration of all unchanged definitions.

## Selection and Membership

Exact target taxa: NCBITaxon:9606, NCBITaxon:559292, NCBITaxon:83333.
There are 61 approvals across 56 record groups and 51 non-target scope deferrals.
Twelve groups have no approved queued alternative; this is not a biological
absence claim. All 12 groups remain byte-identical. Four contain existing target
examples that this queue missed.

Intervals are source-asserted, one-based inclusive, in the canonical UniProt frame.
The table enumerates every selected record group, every approved assertion, and every
deferred queued alternative. Deferral preserves the existing example and is not
negative biological evidence.

| Record / source model | Approved protein and canonical interval | Deferred queued proteins |
| --- | --- | --- |
| [CDD:cd23977](../data/traits/sequence/domain/cdd/alpha-n-acetylgalactosaminide-alpha-2-6-sialyltransferase-4-st6galnac--cd23977.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23977) | [UniProtKB:Q9H4F1](https://www.uniprot.org/uniprotkb/Q9H4F1/entry) 73–300 | None |
| [CDD:cd23989](../data/traits/sequence/domain/cdd/alpha-n-acetylneuraminide-alpha-2-8-sialyltransferase-1-alpha-n-acetyl-cd23989.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23989) | [UniProtKB:Q92185](https://www.uniprot.org/uniprotkb/Q92185/entry) 73–344 | UniProtKB:Q64687 |
| [CDD:cd22651](../data/traits/sequence/domain/cdd/alpha-pore-forming-toxin-alpha-pft-hemolysin-e-hlye-clya-or-shea-in-es-cd22651.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22651) | [UniProtKB:P77335](https://www.uniprot.org/uniprotkb/P77335/entry) 14–292 | None |
| [CDD:cd23982](../data/traits/sequence/domain/cdd/beta-galactoside-alpha-2-3-sialyltransferase-4-st3gal-family-transfers-cd23982.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23982) | [UniProtKB:Q11206](https://www.uniprot.org/uniprotkb/Q11206/entry) 116–321 | UniProtKB:Q91Y74 |
| [CDD:cd23984](../data/traits/sequence/domain/cdd/beta-galactoside-alpha-2-3-sialyltransferase-6-st3gal-family-transfers-cd23984.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23984) | [UniProtKB:Q9Y274](https://www.uniprot.org/uniprotkb/Q9Y274/entry) 114–319 | None |
| [CDD:cd23296](../data/traits/sequence/domain/cdd/beta-trefoil-domain-found-in-interleukin-1-beta-il-1-beta-and-similar--cd23296.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23296) | [UniProtKB:P01584](https://www.uniprot.org/uniprotkb/P01584/entry) 118–265 | UniProtKB:P10749 |
| [CDD:cd23836](../data/traits/sequence/domain/cdd/c-terminal-double-rwd-domain-of-centromere-protein-o-cenp-o-and-relate-cd23836.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23836) | [UniProtKB:Q9BU64](https://www.uniprot.org/uniprotkb/Q9BU64/entry) 185–287 | UniProtKB:Q8K015 |
| [CDD:cd23834](../data/traits/sequence/domain/cdd/c-terminal-double-rwd-domain-of-minichromosome-maintenance-protein-21--cd23834.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23834) | [UniProtKB:Q06675](https://www.uniprot.org/uniprotkb/Q06675/entry) 276–363 | None |
| [CDD:cd23006](../data/traits/sequence/domain/cdd/dickkopf-like-protein-1-dickkopf-dkk-genes-comprise-an-evolutionarily--cd23006.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23006) | [UniProtKB:Q9UK85](https://www.uniprot.org/uniprotkb/Q9UK85/entry) 77–242 | UniProtKB:Q9QZL9 |
| [CDD:cd22568](../data/traits/sequence/domain/cdd/et-binding-motif-ebm-of-saccharomyces-cerevisiae-atp-dependent-helicas-cd22568.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22568) | [UniProtKB:P32597](https://www.uniprot.org/uniprotkb/P32597/entry) 1183–1240 | None |
| [CDD:cd23540](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-activin-receptor-like-kinase-7-alk-7-cd23540.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23540) | [UniProtKB:Q8NER5](https://www.uniprot.org/uniprotkb/Q8NER5/entry) 24–99 | UniProtKB:Q8K348 |
| [CDD:cd23631](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-activin-receptor-type-2a-actr-iia-an-cd23631.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23631) | [UniProtKB:P27037](https://www.uniprot.org/uniprotkb/P27037/entry) 25–119 | UniProtKB:P27038 |
| [CDD:cd23614](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-bone-morphogenetic-protein-receptor--cd23614.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23614) | [UniProtKB:Q13873](https://www.uniprot.org/uniprotkb/Q13873/entry) 32–131 | UniProtKB:O35607 |
| [CDD:cd23598](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-drosophila-melanogaster-baboon-and-s-cd23598.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23598) | None | UniProtKB:A1Z7L8 |
| [CDD:cd23590](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-drosophila-melanogaster-protein-boud-cd23590.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23590) | None | UniProtKB:Q9W3T7 |
| [CDD:cd23589](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-drosophila-melanogaster-protein-retr-cd23589.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23589) | None | UniProtKB:Q9VZ21 |
| [CDD:cd23575](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-glycosylphosphatidylinositol-anchore-cd23575.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23575) | [UniProtKB:Q8IV16](https://www.uniprot.org/uniprotkb/Q8IV16/entry) 63–142 | UniProtKB:Q9D1N2 |
| [CDD:cd23559](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-ly6-plaur-domain-containing-protein--cd23559.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23559) | None | UniProtKB:Q8BLC3 |
| [CDD:cd23562](../data/traits/sequence/domain/cdd/first-extracellular-domain-ecd-found-in-ly6-plaur-domain-containing-pr-cd23562.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23562) | [UniProtKB:O95274](https://www.uniprot.org/uniprotkb/O95274/entry) 31–117 | None |
| [CDD:cd22914](../data/traits/sequence/domain/cdd/first-histone-fold-domain-found-in-son-of-sevenless-homolog-1-sos-1-an-cd22914.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22914) | [UniProtKB:Q07889](https://www.uniprot.org/uniprotkb/Q07889/entry) 18–95; [UniProtKB:Q07890](https://www.uniprot.org/uniprotkb/Q07890/entry) 18–95 | UniProtKB:P26675, UniProtKB:Q02384 |
| [CDD:cd22736](../data/traits/sequence/domain/cdd/forkhead-associated-fha-domain-found-in-bifunctional-polynucleotide-ph-cd22736.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22736) | [UniProtKB:Q96T60](https://www.uniprot.org/uniprotkb/Q96T60/entry) 9–108 | UniProtKB:Q9JLV6 |
| [CDD:cd22677](../data/traits/sequence/domain/cdd/forkhead-associated-fha-domain-found-in-kanadaptin-and-similar-protein-cd22677.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22677) | [UniProtKB:Q9BWU0](https://www.uniprot.org/uniprotkb/Q9BWU0/entry) 112–222 | None |
| [CDD:cd22726](../data/traits/sequence/domain/cdd/forkhead-associated-fha-domain-found-in-kinesin-like-protein-kif1a-kif-cd22726.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22726) | [UniProtKB:Q12756](https://www.uniprot.org/uniprotkb/Q12756/entry) 491–605 | UniProtKB:P33173 |
| [CDD:cd22709](../data/traits/sequence/domain/cdd/forkhead-associated-fha-domain-found-in-kinesin-like-protein-kif28p-an-cd22709.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22709) | [UniProtKB:B7ZC32](https://www.uniprot.org/uniprotkb/B7ZC32/entry) 384–482 | None |
| [CDD:cd22667](../data/traits/sequence/domain/cdd/forkhead-associated-fha-domain-found-in-nibrin-and-similar-proteins-ni-cd22667.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22667) | [UniProtKB:O60934](https://www.uniprot.org/uniprotkb/O60934/entry) 2–110 | UniProtKB:Q9R207 |
| [CDD:cd23356](../data/traits/sequence/domain/cdd/fourth-fascin-like-domain-beta-trefoil-fold-found-in-fascin-and-simila-cd23356.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23356) | [UniProtKB:Q16658](https://www.uniprot.org/uniprotkb/Q16658/entry) 383–493 (already installed) | None |
| [CDD:cd22846](../data/traits/sequence/domain/cdd/galactose-rhamnose-binding-lectin-domain-found-in-latrophilin-3-and-si-cd22846.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22846) | [UniProtKB:Q9HAR2](https://www.uniprot.org/uniprotkb/Q9HAR2/entry) 29–127 | UniProtKB:Q80TS3 |
| [CDD:cd22842](../data/traits/sequence/domain/cdd/galactose-rhamnose-binding-lectin-domain-found-in-plant-beta-galactosi-cd22842.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22842) | None | UniProtKB:Q9SCV3, UniProtKB:Q9SCV4, UniProtKB:Q9SCV9 |
| [CDD:cd23506](../data/traits/sequence/domain/cdd/helix-located-at-the-middle-n-terminal-region-of-sfi1p-sfi1p-is-a-sing-cd23506.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23506) | [UniProtKB:Q12369](https://www.uniprot.org/uniprotkb/Q12369/entry) 218–306 | None |
| [CDD:cd22913](../data/traits/sequence/domain/cdd/histone-fold-domain-found-in-ankyrin-repeat-and-btb-poz-domain-contain-cd22913.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22913) | [UniProtKB:A6QL63](https://www.uniprot.org/uniprotkb/A6QL63/entry) 193–379 | None |
| [CDD:cd22920](../data/traits/sequence/domain/cdd/histone-fold-domain-found-in-centromere-protein-t-cenp-t-and-similar-p-cd22920.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22920) | [UniProtKB:Q96BT3](https://www.uniprot.org/uniprotkb/Q96BT3/entry) 460–549 | UniProtKB:Q3TJM4 |
| [CDD:cd22908](../data/traits/sequence/domain/cdd/histone-fold-domain-found-in-nuclear-transcription-factor-y-subunit-ga-cd22908.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22908) | None | UniProtKB:Q8L4B2, UniProtKB:Q9FMV5, UniProtKB:Q9SMP0 |
| [CDD:cd22627](../data/traits/sequence/domain/cdd/kunitz-type-domain-from-the-alpha1-chain-of-type-vii-collagen-and-simi-cd22627.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22627) | [UniProtKB:Q02388](https://www.uniprot.org/uniprotkb/Q02388/entry) 2874–2929 | None |
| [CDD:cd22539](../data/traits/sequence/domain/cdd/n-terminal-domain-of-transcription-factor-specificity-protein-sp-1-spe-cd22539.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22539) | [UniProtKB:P08047](https://www.uniprot.org/uniprotkb/P08047/entry) 54–627 | UniProtKB:O89090 |
| [CDD:cd22542](../data/traits/sequence/domain/cdd/n-terminal-domain-of-transcription-factor-specificity-protein-sp-7-spe-cd22542.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22542) | [UniProtKB:Q8TDD2](https://www.uniprot.org/uniprotkb/Q8TDD2/entry) 2–295 | None |
| [CDD:cd24017](../data/traits/sequence/domain/cdd/n-terminal-domain-of-type-ii-secretion-system-protein-l-t2ssl-and-simi-cd24017.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24017) | [UniProtKB:P45763](https://www.uniprot.org/uniprotkb/P45763/entry) 7–230 | None |
| [CDD:cd22851](../data/traits/sequence/domain/cdd/n-terminal-gemin2-binding-domain-of-the-survival-motor-neuron-family-t-cd22851.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22851) | [UniProtKB:Q16637](https://www.uniprot.org/uniprotkb/Q16637/entry) 29–59 | UniProtKB:P97801, UniProtKB:Q9VV74 |
| [CDD:cd22740](../data/traits/sequence/domain/cdd/n-terminal-snare-complex-binding-domain-of-the-complexin-family-of-sna-cd22740.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22740) | [UniProtKB:O14810](https://www.uniprot.org/uniprotkb/O14810/entry) 32–72 | UniProtKB:P63040 |
| [CDD:cd24067](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-bacillus-subtilis-fructokinase-frk-an-cd24067.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24067) | None | UniProtKB:O05510 |
| [CDD:cd24112](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-ectonucleoside-triphosphate-diphospho-cd24112.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24112) | [UniProtKB:O75355](https://www.uniprot.org/uniprotkb/O75355/entry) 57–468 | UniProtKB:Q8BFW6 |
| [CDD:cd24117](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-escherichia-coli-guanosine-pentaphosp-cd24117.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24117) | [UniProtKB:P25552](https://www.uniprot.org/uniprotkb/P25552/entry) 9–298 | None |
| [CDD:cd24047](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-ethanolamine-utilization-protein-eutj-cd24047.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24047) | [UniProtKB:P77277](https://www.uniprot.org/uniprotkb/P77277/entry) 30–266 | None |
| [CDD:cd24088](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-hexokinase-isozymes-glucokinase-1-glk-cd24088.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24088) | [UniProtKB:Q04409](https://www.uniprot.org/uniprotkb/Q04409/entry) 29–497 | None |
| [CDD:cd24087](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-hexokinase-isozymes-pi-and-pii-from-f-cd24087.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24087) | [UniProtKB:P04806](https://www.uniprot.org/uniprotkb/P04806/entry) 38–471; [UniProtKB:P04807](https://www.uniprot.org/uniprotkb/P04807/entry) 38–458 | None |
| [CDD:cd24011](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-the-butyrate-kinase-bk-domain-family--cd24011.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24011) | None | UniProtKB:P54532 |
| [CDD:cd24124](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-the-first-repeat-of-type-i-hexokinase-cd24124.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24124) | [UniProtKB:P19367](https://www.uniprot.org/uniprotkb/P19367/entry) 2–474 | None |
| [CDD:cd22772](../data/traits/sequence/domain/cdd/otu-ovarian-tumor-domain-of-otu-domain-containing-protein-7b-otu-domai-cd22772.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22772) | [UniProtKB:Q6GQQ9](https://www.uniprot.org/uniprotkb/Q6GQQ9/entry) 158–364 | UniProtKB:B2RUR8 |
| [CDD:cd22791](../data/traits/sequence/domain/cdd/otu-ovarian-tumor-domain-of-vertnin-and-similar-proteins-vertnin-vrtn--cd22791.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22791) | [UniProtKB:Q9H8Y1](https://www.uniprot.org/uniprotkb/Q9H8Y1/entry) 74–241 (already installed) | None |
| [CDD:cd23067](../data/traits/sequence/domain/cdd/pdz-domain-of-dep-domain-containing-mtor-interacting-protein-deptor-an-cd23067.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23067) | [UniProtKB:Q8TB45](https://www.uniprot.org/uniprotkb/Q8TB45/entry) 330–404 | UniProtKB:Q570Y9 |
| [CDD:cd23073](../data/traits/sequence/domain/cdd/pdz-domain-of-microtubule-associated-serine-threonine-mast-protein-kin-cd23073.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23073) | [UniProtKB:Q9Y2H9](https://www.uniprot.org/uniprotkb/Q9Y2H9/entry) 964–1058 | UniProtKB:Q9R1L5 |
| [CDD:cd22569](../data/traits/sequence/domain/cdd/periphilin-binding-domain-of-protein-tasor-and-similar-proteins-tasor--cd22569.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22569) | [UniProtKB:Q9UK61](https://www.uniprot.org/uniprotkb/Q9UK61/entry) 1014–1095 | UniProtKB:Q69ZR9 |
| [CDD:cd23156](../data/traits/sequence/domain/cdd/prefoldin-subunit-3-prefoldin-subunit-3-is-one-of-the-alpha-subunits-o-cd23156.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23156) | None | UniProtKB:P57741, UniProtKB:Q9VGP6 |
| [CDD:cd23140](../data/traits/sequence/domain/cdd/ring-finger-hc-subclass-found-in-arabidopsis-thaliana-protein-keep-on--cd23140.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23140) | None | UniProtKB:Q9FY48 |
| [CDD:cd23816](../data/traits/sequence/domain/cdd/rwd-domain-of-rwd-domain-containing-protein-1-rwdd1-and-related-protei-cd23816.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23816) | [UniProtKB:Q9H446](https://www.uniprot.org/uniprotkb/Q9H446/entry) 4–119 | UniProtKB:Q9CQK7 |
| [CDD:cd23787](../data/traits/sequence/domain/cdd/rwd-domain-of-saccharomyces-cerevisiae-chromosome-segregation-in-meios-cd23787.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23787) | [UniProtKB:P25651](https://www.uniprot.org/uniprotkb/P25651/entry) 69–179 | None |
| [CDD:cd23994](../data/traits/sequence/domain/cdd/saccharomyces-cerevisiae-seipin-and-similar-proteins-seipin-is-a-homo--cd23994.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23994) | [UniProtKB:Q06058](https://www.uniprot.org/uniprotkb/Q06058/entry) 48–232 | None |
| [CDD:cd23272](../data/traits/sequence/domain/cdd/second-cysteine-rich-cys-2-domain-of-dickkopf-related-protein-1-dickko-cd23272.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23272) | [UniProtKB:O94907](https://www.uniprot.org/uniprotkb/O94907/entry) 182–264 | UniProtKB:O54908 |
| [CDD:cd23563](../data/traits/sequence/domain/cdd/second-extracellular-domain-ecd-found-in-ly6-plaur-domain-containing-p-cd23563.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23563) | [UniProtKB:O95274](https://www.uniprot.org/uniprotkb/O95274/entry) 135–226 | None |
| [CDD:cd22829](../data/traits/sequence/domain/cdd/second-galactose-rhamnose-binding-lectin-domain-found-in-caenorhabditi-cd22829.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22829) | [UniProtKB:P58658](https://www.uniprot.org/uniprotkb/P58658/entry) 164–261 | UniProtKB:Q9XU98 |
| [CDD:cd22743](../data/traits/sequence/domain/cdd/stomagen-domain-family-stomagen-also-called-epidermal-patterning-facto-cd22743.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22743) | None | UniProtKB:Q9SV72 |
| [CDD:cd23811](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-saccharomyces-cd23811.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23811) | [UniProtKB:P14682](https://www.uniprot.org/uniprotkb/P14682/entry) 8–178 | None |
| [CDD:cd23812](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-saccharomyces-cd23812.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23812) | None | UniProtKB:Q8LGF7 |
| [CDD:cd23792](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-ubiquitin-con-cd23792.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23792) | [UniProtKB:P15731](https://www.uniprot.org/uniprotkb/P15731/entry) 4–146; [UniProtKB:P61077](https://www.uniprot.org/uniprotkb/P61077/entry) 3–145 | UniProtKB:P25867 |
| [CDD:cd23801](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-ubiquitin-con-cd23801.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23801) | [UniProtKB:O14933](https://www.uniprot.org/uniprotkb/O14933/entry) 3–148; [UniProtKB:P68036](https://www.uniprot.org/uniprotkb/P68036/entry) 3–149 | UniProtKB:P68037 |
| [CDD:cd23813](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-ubiquitin-con-cd23813.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23813) | [UniProtKB:P52490](https://www.uniprot.org/uniprotkb/P52490/entry) 4–147; [UniProtKB:P61088](https://www.uniprot.org/uniprotkb/P61088/entry) 4–147 | UniProtKB:P35128 |
| [CDD:cd23814](../data/traits/sequence/domain/cdd/ubiquitin-e2-variant-uev-domain-of-akt-interacting-protein-and-related-cd23814.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23814) | [UniProtKB:Q9H8T0](https://www.uniprot.org/uniprotkb/Q9H8T0/entry) 77–189 | UniProtKB:Q64362 |
| [CDD:cd22896](../data/traits/sequence/domain/cdd/vertebrate-periphilin-1-and-similar-proteins-this-family-contains-peri-cd22896.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22896) | [UniProtKB:Q8NEY8](https://www.uniprot.org/uniprotkb/Q8NEY8/entry) 285–341 | UniProtKB:Q8K2H1 |
| [CDD:cd23021](../data/traits/sequence/domain/cdd/zinc-finger-hit-zf-hit-found-in-ino80-complex-subunit-b-ino80b-and-sim-cd23021.yaml) · [source](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23021) | [UniProtKB:Q9C086](https://www.uniprot.org/uniprotkb/Q9C086/entry) 309–339 | UniProtKB:Q99PT3 |

## Validation

Completed:

- Guarded `promote-uniprot-review-batch human-ecoli-yeast-target-cnp020-002of008 --apply`:
  61 approvals, 54 validated record writes, two already present.
- Fresh provider replay: all 112 assertions; the 61 approvals use 21 grouped-location
  and 40 flat-location projections. Exact trait identity, canonical frame, InterPro
  110.0 intervals, UniProt 2026_03 sequence length/checksum/release, and taxon agree.
- Git-base preservation replay: all prior protein/evidence/binding objects preserved;
  all prior example fields and occurrence objects preserved; example ID order unchanged;
  raw record bytes outside `canonical_examples` unchanged.
- Selected-example semantic projections: all 61 pass `require_qualified=True`.
  This is **not** a require-qualified pass for the other legacy examples.
- Registry layout: 12,462 protein references; 20,617 evidence rows and matching bindings.
- Biophysical dependency repair: registered calculator replay changes only the registry
  checksum; observation JSONL and TSV remain byte-identical. Full pilot checker passes.
- Focused grounding, registry, pilot, documentation, landing, and Pages tests:
  389 passed in 105.18 seconds. Writer audit, append-only history validation,
  and lint pass.
- Scoped `validate-all`: all 54 changed files pass strict validation and have
  zero semantic findings, including verification of all 20,617 durable bindings.
- Browser projection replay: all 56 approved record-group projections are
  unchanged relative to the Git base; 59 of 61 selected example metadata entries
  survive the existing display cap (see the completeness caveat below).

Full `validate-all` passes all 429,293 records with zero strict errors and zero
semantic findings, including all 12,462 protein references and 20,617
evidence/binding objects.
At this review checkpoint, the full CI regression suite, browser rebuild,
and generated-size checks remain pending. Their terminal results must be recorded
on the PR before merge; this checkpoint is not a claim that unfinished jobs passed.
The first focused-test invocation named a nonexistent
`tests/test_pages_build_contract.py`, collected no tests, and exited 4; the corrected
invocation uses the verified `tests/test_pages_build.py`.

## Lump and Split Review

The shared review question is exact domain occurrence, not common biological function.
Repeat-specific records remain distinct: LYPD3 first/second LU domains, SOS first
histone-fold, FSCN1 fourth beta-trefoil, EVA1C second lectin-like repeat, and HK1 first
repeat. Paralog/source-model boundaries remain unchanged. A shared accession on two
different domain records is not a duplicate trait. No merge, split, hierarchy, label,
source-definition, or mapping-status changes are made by this batch.

## Identity and Grounding

Every approved `source_trait_id` equals its record `trait_id`; no inferred hierarchy,
local alignment, HMM scan, or invented coordinates are used. Full sequences live in
the durable protein registry and are bound by checksum and sequence version.
The installed claims are domain assignments, not independent experimental verification
of every functional sentence in a source definition.

FSCN1 Q16658/CDD:cd23356 383–493 and VRTN Q9H8Y1/CDD:cd22791 74–241 were
already installed with the exact same evidence identities. Their approvals are no-ops,
not additional occurrences or replacements.

## Evidence Patterns

- [AKTIP UEV model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23814): lacks the catalytic cysteine;
  domain qualification must not imply ubiquitin-conjugating activity.
- [HK1 repeat-1 model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24124): the source distinguishes
  the regulatory N-terminal half from the catalytic C-terminal half.
- [VRTN OTU-like model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22791): the source cautions about
  missing catalytic residues; preserve that limitation.
- [EVA1C repeat-2 model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd22829): the record's source text
  explicitly excludes a rhamnose-binding pocket for this repeat.
- [T2SSL model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd24017): ASKHA structural homology is not
  ATP-binding or ATPase evidence.
- [INO80B zf-HIT model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23021): the source states that yeast
  Ies2 lacks this domain; protein-complex homology is not a yeast occurrence.
- [Yeast Sei1 model](https://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid=cd23994): general adipocyte background
  must not be interpreted as yeast adipocyte biology.
- [KIF28P B7ZC32](https://rest.uniprot.org/uniprotkb/B7ZC32.txt):
  retained adjudication distinguishes the source FHA match from sequence/motor-function
  evidence cautions. The protein name alone is not evidence of nonexistence.

Fresh web checks resolved the AKTIP and HK1 source pages. The EVA1C and T2SSL pages
were unavailable through the web tool on this pass; their caveats were checked against
the full retained source-derived record text, not represented as a new live-page check.
Frozen provider replay, rather than mutable web text, binds the promoted coordinates.

iModulonDB is not applicable to the exact domain-coordinate admission question;
expression-module membership would not qualify any of these intervals.

## Completeness Patterns

The all-68-group inventory contains 60 target-bearing records with 61 QUALIFIED
and 11 LEGACY_UNVERIFIED existing target examples. It includes every example in
all deferred groups, not merely target-bearing candidate groups.

| Model | Existing legacy example |
| --- | --- |
| [CDD:cd23559](../data/traits/sequence/domain/cdd/extracellular-domain-ecd-found-in-ly6-plaur-domain-containing-protein--cd23559.yaml) | [UniProtKB:Q8N2G4](https://www.uniprot.org/uniprotkb/Q8N2G4/entry) — Ly6/PLAUR domain-containing protein 1 |
| [CDD:cd22913](../data/traits/sequence/domain/cdd/histone-fold-domain-found-in-ankyrin-repeat-and-btb-poz-domain-contain-cd22913.yaml) | [UniProtKB:Q8N961](https://www.uniprot.org/uniprotkb/Q8N961/entry) — Ankyrin repeat and BTB/POZ domain-containing protein 2 |
| [CDD:cd22908](../data/traits/sequence/domain/cdd/histone-fold-domain-found-in-nuclear-transcription-factor-y-subunit-ga-cd22908.yaml) | [UniProtKB:Q13952](https://www.uniprot.org/uniprotkb/Q13952/entry) — Nuclear transcription factor Y subunit gamma |
| [CDD:cd24088](../data/traits/sequence/domain/cdd/nucleotide-binding-domain-nbd-of-hexokinase-isozymes-glucokinase-1-glk-cd24088.yaml) | [UniProtKB:P17709](https://www.uniprot.org/uniprotkb/P17709/entry) — Glucokinase-1 |
| [CDD:cd23156](../data/traits/sequence/domain/cdd/prefoldin-subunit-3-prefoldin-subunit-3-is-one-of-the-alpha-subunits-o-cd23156.yaml) | [UniProtKB:P61758](https://www.uniprot.org/uniprotkb/P61758/entry) — Prefoldin subunit 3 |
| [CDD:cd23156](../data/traits/sequence/domain/cdd/prefoldin-subunit-3-prefoldin-subunit-3-is-one-of-the-alpha-subunits-o-cd23156.yaml) | [UniProtKB:P48363](https://www.uniprot.org/uniprotkb/P48363/entry) — Prefoldin subunit 3 |
| [CDD:cd23812](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-saccharomyces-cd23812.yaml) | [UniProtKB:P29340](https://www.uniprot.org/uniprotkb/P29340/entry) — Ubiquitin-conjugating enzyme E2 PEX4 |
| [CDD:cd23792](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-ubiquitin-con-cd23792.yaml) | [UniProtKB:P51668](https://www.uniprot.org/uniprotkb/P51668/entry) — Ubiquitin-conjugating enzyme E2 D1 |
| [CDD:cd23792](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-ubiquitin-con-cd23792.yaml) | [UniProtKB:P62837](https://www.uniprot.org/uniprotkb/P62837/entry) — Ubiquitin-conjugating enzyme E2 D2 |
| [CDD:cd23801](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-ubiquitin-con-cd23801.yaml) | [UniProtKB:A0A1B0GUS4](https://www.uniprot.org/uniprotkb/A0A1B0GUS4/entry) — Ubiquitin-conjugating enzyme E2 L5 |
| [CDD:cd23813](../data/traits/sequence/domain/cdd/ubiquitin-conjugating-enzyme-e2-catalytic-ubcc-domain-of-ubiquitin-con-cd23813.yaml) | [UniProtKB:Q5JXB2](https://www.uniprot.org/uniprotkb/Q5JXB2/entry) — Putative ubiquitin-conjugating enzyme E2 N-like |

A separate complete scan of the pinned profile JSONL across the 186 distinct record
groups in CNP020 shards 0–2 found 189 exact target-profile/trait pairs and three accession
IDs absent from the corresponding records:

| Model | Missing example discovery lead | Taxon |
| --- | --- | --- |
| CDD:cd23792 | [UniProtKB:Q9Y2X8](https://www.uniprot.org/uniprotkb/Q9Y2X8/entry) — E2 D4 | Human |
| CDD:cd23792 | [UniProtKB:P15732](https://www.uniprot.org/uniprotkb/P15732/entry) — E2-16 kDa | Yeast S288c |
| CDD:cd22908 | [UniProtKB:Q02516](https://www.uniprot.org/uniprotkb/Q02516/entry) — HAP5 | Yeast S288c |

The profile snapshot SHA-256 is
`57b2f433eb82bfd9f59a8da5155a4aee6f98a6dcb7391b89c5166e4ceef89fc5`.
This publication pass freshly rechecks that checksum, the three exact record example
lists, and their inclusion in the separate acquisition list. The profile is a discovery
source, not qualification evidence. None of these three examples is added by this PR.

The isolated target-profile InterPro crawl completed separately with zero reported
failed requests; its terminal hashes are retained in the execution checkpoint.
It is not a promotion input for this PR. Its end-of-crawl upstream release-consistency
check and source-backed follow-up are future coverage work. Broader strains,
unreviewed proteins, isoforms, omitted
accessions, other sources, and unsupported provider routes remain outside this
batch's completeness claim. The all-protein goal remains open.

The docs browser currently projects legacy inline sequences/features and does not
dereference these new registry-backed occurrence coordinates. A successful rebuild
does not establish that the new annotations are visible in the UI.
Its pre-existing five-example cap hides P15731 on CDD:cd23792 and P52490 on
CDD:cd23813 in this cohort. All 56 approved-group projections are unchanged
by the qualification delta. The cap limitation is already tracked in
[#806](https://github.com/CultureBotAI/proteintraitsmech/issues/806), and is not
claimed fixed here.

## Findings

1. **Major, addressed locally — [#946](https://github.com/CultureBotAI/proteintraitsmech/issues/946).**
   Promotion left the pilot manifest pinned to the old registry. The pilot checker
   reproduced the failure. Replaying the registered calculator updates the maintained
   generated manifest without changing observations; the checker now passes.
2. **Minor, addressed by this handoff — [#947](https://github.com/CultureBotAI/proteintraitsmech/issues/947).**
   Only a pre-promotion checkpoint and ignored ledgers described shard 2. This tracked
   review records all decisions and distinguishes installed, legacy, and missing-ID
   inventories. The checkpoint/history will travel with the data. Completion of the
   broader organism goal is explicitly not claimed.

No additional blocking discrepancy was found in the installed qualification delta.
These are AI review judgments, not independent human curator sign-off.

## Recommended Edits

The two PR findings are handled by the registered pilot refresh and tracked handoff.
Continue remaining protein coverage in later bounded, source-backed batches; do not
force new examples into this PR from profile membership alone. Keep source-prose and
browser enhancements separate from this qualification-only delta.

## Follow-up Checks

Before merge, record all pending terminal gate results and inspect required GitHub
checks on the exact PR head. Preserve the ignored replay inputs. If main introduces
a registry conflict, restore main's registry state and replay the guarded promotion;
never hand-merge content-addressed registry objects.

## Additional Notes

Retained ignored replay basename:
`reports/uniprot-grounding/review-batches/human-ecoli-yeast-target-cnp020-002of008`.

| Staging suffix | SHA-256 |
| --- | --- |
| `.candidates.jsonl` | `fa558c67f24ba6104da53575e362f546f9110e19d68ac1f42f4b7214b1cee9d3` |
| `.resolved.jsonl` | `7dd593a7a4e17d5fd64e2e039541dc7b2cdc0a30c09c4a13f2c5d032f99bca07` |
| `.target-review.jsonl` | `5ce606eb65e62c8ae994fc87ca2c724fb42d4d851f93b6b885dadbd27bfea48d` |
| `.review-decisions.jsonl` | `96deeab32a3b645af590645dc7e0be4112aa5d0dc58d183bdece4188ce5187f6` |
| `.approved.tsv` | `1c8b6e7118754829e0590dad66369ac71998583ee7f29bca2ef9b02443b88401` |
| `.manifest.json` | `b3ba060f0c1f5e06515f7944ad60e7f5662cfe48993670abc5f9c2e45b377120` |
| `.uniprot_fetch_receipt.json` | `fe763882d9f29dd23c25535acdaeec623738afc5aabcc20cc3f79dafe3dd490a` |

These hashes identify local staging, not downloadable artifacts in a clean checkout.
The durable records and sequence/evidence/binding registries are the installed claims.
The exact-accession acquisition requested 111 canonical proteins at UniProt 2026_03;
extra isoform responses are not admission evidence.

Installed protein-registry SHA-256:
`108ef14d1f1ad5af27999e84ce12c99968ed6c42d811c7d700b34d3241b455dd`.
Evidence logical SHA-256:
`4cb23fa6ac38ba0d531a9da399e1fb3860234044347379c34b4f3c467670b966`.
Bindings logical SHA-256:
`047f1ed403932e42907ab6225ac162c73663b7b723ccd4a657e4a2e027ad6ad7`.
Pilot observation SHA-256 remains
`1d2221a3bfe40aa1f76420276f7a100276bac54cec88321c3f8b942bb9313362`.

Absence checks include ignored/hidden review paths and exact full-record example lists.
No absence claim is made for the wider biological universe.
