# Identical-residue links: adjudicated against InterPro membership

1,765 CATH↔InterPro pairs cover the identical residue set on every shared exemplar protein, and **none appear in `cross_source.tsv`** — the residue frame found them independently of the corpus's identifier mappings.

| verdict | pairs | meaning |
|---|--:|---|
| **confirmed** | **1,697** | InterPro lists this CATH superfamily among the entry's Gene3D members — the same superfamily under two identifiers |
| refuted | 68 | InterPro integrates no Gene3D signature, or a different one: the residues coincide for another reason |
| unresolved | 0 | membership unfetchable, or the InterPro entry no longer exists |

Confirmed pairs by supporting-protein count (3 is the ceiling — `suggest_canonical_examples --max-examples 3` gives each record at most three exemplars, so n=3 means *all* available evidence agrees):

| proteins | pairs |
|---|--:|
| 1 | 322 |
| 2 | 227 |
| 3 | 93 |
| 4 | 129 |
| 5 | 106 |
| 6 | 119 |
| 7 | 108 |
| 8 | 593 |
