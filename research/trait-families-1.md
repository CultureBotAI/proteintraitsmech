# Multi-trait families (DiviK-style divisive clustering)

matrix: 68,657 proteins × 19,894 signature traits (GO/EC excluded — they cluster by annotation depth, not architecture)

**1,837 families** with a shared core, covering 29,313 proteins (43%); largest 449, median 9

39,344 proteins (57%) are **unassigned** — they end up in core-less leaves. Binary divisive k-means peels coherent groups off a large remainder one at a time, so that remainder shrinks with `--max-depth` (44,582 at 24, 34,412 at 60) without dissolving. They are reported as unassigned rather than labelled a family.

| size | core traits (carried by ≥80% of members) | label |
|--:|---|---|
| 449 | CATH:1.20.1070.10, InterPro:IPR017452, PROSITE:PS00237, PROSITE:PS50262 | Rhodopsin 7-helix transmembrane proteins |
| 348 | CATH:3.30.160.60, InterPro:IPR013087, PROSITE:PS00028, PROSITE:PS50157 | Classic Zinc Finger |
| 340 | CATH:3.30.420.40, InterPro:IPR043129 | ATPase, nucleotide binding domain |
| 280 | CATH:3.30.70.330, InterPro:IPR000504, InterPro:IPR012677, InterPro:IPR035979 | RRM (RNA recognition motif) domain |
| 280 | CATH:1.10.510.10, CATH:3.30.200.20, InterPro:IPR000719, InterPro:IPR008271 | Transferase(Phosphotransferase) domain 1 |
| 261 | CATH:3.30.160.60, InterPro:IPR001909, InterPro:IPR013087, InterPro:IPR036051 | Classic Zinc Finger |
| 247 | CATH:3.40.50.300, InterPro:IPR027417 | P-loop containing nucleotide triphosphate hydrolases |
| 208 | InterPro:IPR035892, InterPro:IPR000008, PROSITE:PS50004, CATH:2.60.40.150 | C2 domain superfamily |
| 205 | InterPro:IPR011598, InterPro:IPR036638, PROSITE:PS50888, Pfam:PF00010 | Myc-type, basic helix-loop-helix (bHLH) domain |
| 183 | CATH:1.50.40.10, InterPro:IPR023395, InterPro:IPR018108, PROSITE:PS50920 | Mitochondrial carrier domain |
| 182 | CATH:2.60.40.10, InterPro:IPR007110, InterPro:IPR013106, InterPro:IPR013783 | Immunoglobulins |
| 154 | CATH:2.60.40.10, InterPro:IPR003599, InterPro:IPR007110, InterPro:IPR013106 | Immunoglobulins |
| 153 | CATH:3.30.50.10, InterPro:IPR013088, InterPro:IPR001628, PROSITE:PS51030 | Erythroid Transcription Factor GATA-1, subunit A |
| 150 | CATH:1.25.10.10, InterPro:IPR011989, InterPro:IPR016024 | Leucine-rich Repeat Variant |
| 149 | CATH:1.20.1070.10, InterPro:IPR017452, PROSITE:PS00237, PROSITE:PS50262 | Rhodopsin 7-helix transmembrane proteins |
| 142 | InterPro:IPR001471, CATH:3.30.730.10, InterPro:IPR016177, InterPro:IPR036955 | AP2/ERF domain |
| 137 | CATH:1.10.238.10, CDD:cd00051, InterPro:IPR002048, InterPro:IPR011992 | EF-hand |
| 134 | CATH:1.25.40.20, InterPro:IPR002110, InterPro:IPR036770, PROSITE:PS50088 | Ankyrin repeat-containing domain |
| 131 | CATH:3.40.630.30, InterPro:IPR000182, InterPro:IPR016181, Pfam:PF00583 | Gcn5-related N-acetyltransferase (GNAT) |
| 125 | CATH:1.20.1250.20, InterPro:IPR020846, InterPro:IPR036259, PROSITE:PS50850 | MFS general substrate transporter like domains |
| 122 | CATH:1.10.630.10, InterPro:IPR017972, InterPro:IPR036396, PROSITE:PS00086 | Cytochrome P450 |
| 119 | CATH:1.20.1070.10, InterPro:IPR017452, PROSITE:PS50262, Pfam:PF00001 | Rhodopsin 7-helix transmembrane proteins |
| 117 | CATH:1.10.10.60, CDD:cd00086, InterPro:IPR001356, InterPro:IPR009057 | Homeodomain-like |
| 115 | CATH:3.40.50.2000, CDD:cd03784, InterPro:IPR035595, PROSITE:PS00375 | Glycogen Phosphorylase B; |
| 108 | CATH:1.10.510.10, InterPro:IPR000719, InterPro:IPR008271, InterPro:IPR011009 | Transferase(Phosphotransferase) domain 1 |
