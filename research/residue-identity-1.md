# Identical-residue links: adjudicated against InterPro membership

1,680 CATH↔InterPro pairs cover the identical residue set on every shared exemplar protein, and **none appear in `cross_source.tsv`** — the residue frame found them independently of the corpus's identifier mappings.

| verdict | pairs | meaning |
|---|--:|---|
| **confirmed** | **1,640** | InterPro lists this CATH superfamily among the entry's Gene3D members — the same superfamily under two identifiers |
| refuted | 40 | InterPro integrates no Gene3D signature, or a different one: the residues coincide for another reason |
| unresolved | 0 | membership could not be fetched |

Confirmed pairs by supporting-protein count (3 is the ceiling — `suggest_canonical_examples --max-examples 3` gives each record at most three exemplars, so n=3 means *all* available evidence agrees):

| proteins | pairs |
|---|--:|
| 1 | 339 |
| 2 | 249 |
| 3 | 1,052 |
