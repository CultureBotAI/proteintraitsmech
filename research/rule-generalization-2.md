# Held-out-organism replication of the cross-axis rules

trained on **Homo sapiens** (20,431 proteins), support≥30, conf≥0.95, lift≥5.0; a rule replicates at held-out confidence ≥0.9 given ≥5 carriers of the antecedent.

## seq-encodes-fold — 283 rules mined

| held-out organism | testable | replicated | contradicted | untestable | median conf |
|---|--:|--:|--:|--:|--:|
| Mus musculus (17,267) | 283 | 281 (99%) | 2 | 0 | 1.00 |
| Arabidopsis thaliana (16,419) | 155 | 152 (98%) | 3 | 128 | 1.00 |
| Saccharomyces cerevisiae (strain ATCC 204508 / S288c) (6,733) | 124 | 119 (96%) | 5 | 159 | 1.00 |
| Escherichia coli (strain K12) (4,531) | 23 | 22 (96%) | 1 | 260 | 1.00 |
| Caenorhabditis elegans (4,488) | 209 | 200 (96%) | 9 | 74 | 1.00 |
| Bacillus subtilis (strain 168) (4,191) | 23 | 21 (91%) | 2 | 260 | 1.00 |
| Drosophila melanogaster (3,899) | 197 | 190 (96%) | 7 | 86 | 1.00 |
| Methanocaldococcus jannaschii (strain ATCC 43067 / DSM 2661 / JAL-1 / JCM 10045 / NBRC 100440) (1,786) | 11 | 11 (100%) | 0 | 272 | 1.00 |
| Plasmodium falciparum (isolate 3D7) (321) | 8 | 8 (100%) | 0 | 275 | 1.00 |

## trait-implies-function — 232 rules mined

| held-out organism | testable | replicated | contradicted | untestable | median conf |
|---|--:|--:|--:|--:|--:|
| Mus musculus (17,267) | 231 | 204 (88%) | 27 | 1 | 1.00 |
| Arabidopsis thaliana (16,419) | 134 | 115 (86%) | 19 | 98 | 1.00 |
| Saccharomyces cerevisiae (strain ATCC 204508 / S288c) (6,733) | 113 | 97 (86%) | 16 | 119 | 1.00 |
| Escherichia coli (strain K12) (4,531) | 26 | 21 (81%) | 5 | 206 | 1.00 |
| Caenorhabditis elegans (4,488) | 160 | 129 (81%) | 31 | 72 | 1.00 |
| Bacillus subtilis (strain 168) (4,191) | 30 | 21 (70%) | 9 | 202 | 1.00 |
| Drosophila melanogaster (3,899) | 169 | 149 (88%) | 20 | 63 | 1.00 |
| Methanocaldococcus jannaschii (strain ATCC 43067 / DSM 2661 / JAL-1 / JCM 10045 / NBRC 100440) (1,786) | 22 | 13 (59%) | 9 | 210 | 1.00 |
| Plasmodium falciparum (isolate 3D7) (321) | 9 | 9 (100%) | 0 | 223 | 1.00 |

### seq-encodes-fold: rules that do not hold outside the training organism

_Naming the organism matters: a cellular-component rule tested in a bacterium is a category error, not a broken rule._

| rule | held-out organism | train conf | held-out conf | carriers |
|---|---|--:|--:|--:|
| PROSITE:PS50119 → CATH:3.30.160.60 | Arabidopsis thaliana | 1.00 | 0.30 | 27 |
| Pfam:PF00501 → CATH:3.40.50.12780 | Bacillus subtilis (strain 168) | 0.97 | 0.38 | 21 |
| Pfam:PF00643 → CATH:3.30.160.60 | Arabidopsis thaliana | 1.00 | 0.38 | 21 |
| Pfam:PF00038 → CATH:1.20.5.1160 | Caenorhabditis elegans | 0.97 | 0.58 | 12 |
| PROSITE:PS51842 → CATH:1.20.5.1160 | Caenorhabditis elegans | 0.97 | 0.58 | 12 |
| PROSITE:PS50119 → CATH:3.30.160.60 | Caenorhabditis elegans | 1.00 | 0.67 | 6 |

### trait-implies-function: rules that do not hold outside the training organism

_Naming the organism matters: a cellular-component rule tested in a bacterium is a category error, not a broken rule._

| rule | held-out organism | train conf | held-out conf | carriers |
|---|---|--:|--:|--:|
| PROSITE:PS00658 → GO:0000785 | Drosophila melanogaster | 0.96 | 0.00 | 10 |
| PROSITE:PS00658 → GO:0000785 | Caenorhabditis elegans | 0.96 | 0.00 | 12 |
| PROSITE:PS00657 → GO:0000785 | Caenorhabditis elegans | 0.97 | 0.00 | 6 |
| PROSITE:PS00657 → GO:0000785 | Drosophila melanogaster | 0.97 | 0.00 | 8 |
| PROSITE:PS00036 → GO:0006357 | Arabidopsis thaliana | 0.97 | 0.00 | 44 |
| CATH:1.10.565.10 → GO:0005654 | Drosophila melanogaster | 1.00 | 0.00 | 18 |

