# Held-out-organism replication of the cross-axis rules

trained on **Homo sapiens** (20,431 proteins), support≥30, conf≥0.95, lift≥5.0; a rule replicates at held-out confidence ≥0.9 given ≥5 carriers of the antecedent.

## seq-encodes-fold — 283 rules mined

| held-out organism | testable | replicated | contradicted | untestable | median conf |
|---|--:|--:|--:|--:|--:|
| Mus musculus (17,267) | 283 | 281 (99%) | 2 | 0 | 1.00 |
| Saccharomyces cerevisiae (strain ATCC 204508 / S288c) (6,733) | 124 | 119 (96%) | 5 | 159 | 1.00 |
| Escherichia coli (strain K12) (4,531) | 23 | 22 (96%) | 1 | 260 | 1.00 |

## trait-implies-function — 232 rules mined

| held-out organism | testable | replicated | contradicted | untestable | median conf |
|---|--:|--:|--:|--:|--:|
| Mus musculus (17,267) | 231 | 204 (88%) | 27 | 1 | 1.00 |
| Saccharomyces cerevisiae (strain ATCC 204508 / S288c) (6,733) | 113 | 97 (86%) | 16 | 119 | 1.00 |
| Escherichia coli (strain K12) (4,531) | 26 | 21 (81%) | 5 | 206 | 1.00 |

### seq-encodes-fold: rules that do not hold outside the training organism

_Naming the organism matters: a cellular-component rule tested in a bacterium is a category error, not a broken rule._

| rule | held-out organism | train conf | held-out conf | carriers |
|---|---|--:|--:|--:|
| PROSITE:PS51450 → CATH:3.80.10.10 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 1.00 | 0.73 | 11 |
| PROSITE:PS50076 → CATH:1.10.287.110 | Escherichia coli (strain K12) | 1.00 | 0.80 | 5 |
| Pfam:PF00022 → CATH:3.90.640.10 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 1.00 | 0.82 | 11 |
| PROSITE:PS00028 → CATH:3.30.160.60 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 0.95 | 0.85 | 46 |
| PROSITE:PS50118 → CATH:1.10.30.10 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 0.98 | 0.88 | 8 |
| PROSITE:PS50888 → CATH:4.10.280.10 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 0.98 | 0.88 | 8 |
| Pfam:PF01454 → CATH:1.10.10.1200 | Mus musculus | 0.97 | 0.89 | 9 |
| PROSITE:PS50838 → CATH:1.10.10.1200 | Mus musculus | 0.97 | 0.89 | 9 |

### trait-implies-function: rules that do not hold outside the training organism

_Naming the organism matters: a cellular-component rule tested in a bacterium is a category error, not a broken rule._

| rule | held-out organism | train conf | held-out conf | carriers |
|---|---|--:|--:|--:|
| CATH:3.30.50.10 → GO:0005654 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 1.00 | 0.00 | 10 |
| Pfam:PF15974 → GO:0007399 | Mus musculus | 1.00 | 0.00 | 5 |
| PROSITE:PS00657 → GO:0000785 | Mus musculus | 0.97 | 0.03 | 29 |
| PROSITE:PS00658 → GO:0000785 | Mus musculus | 0.96 | 0.05 | 41 |
| Pfam:PF01825 → GO:0016020 | Mus musculus | 0.97 | 0.23 | 30 |
| CATH:2.60.220.50 → GO:0016020 | Mus musculus | 0.97 | 0.26 | 31 |
| PROSITE:PS50221 → GO:0016020 | Mus musculus | 0.97 | 0.30 | 33 |
| PROSITE:PS50071 → GO:0000981 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 0.97 | 0.33 | 9 |
| Pfam:PF00046 → GO:0000981 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 0.96 | 0.43 | 7 |
| PROSITE:PS00036 → GO:0000981 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 0.97 | 0.50 | 12 |
| PROSITE:PS00036 → GO:0006357 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 0.97 | 0.50 | 12 |
| PROSITE:PS00027 → GO:0000981 | Saccharomyces cerevisiae (strain ATCC 204508 / S288c) | 1.00 | 0.50 | 6 |

