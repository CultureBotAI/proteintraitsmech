# Does `corpus_map_definitions.json` show trait axis, or source database?

40,000 records sampled of 344,797 joined to the embedding (344,797 on the map, all matched); 5 axes, 28 source namespaces; k=25 neighbours.

| space | label | purity | chance | lift |
|---|---|--:|--:|--:|
| embedding (pre-projection) | trait axis | 0.932 | 0.342 | **2.72×** |
| embedding (pre-projection) | source database | 0.799 | 0.083 | **9.63×** |
| 2-d map (what is rendered) | trait axis | 0.934 | 0.342 | **2.73×** |
| 2-d map (what is rendered) | source database | 0.787 | 0.083 | **9.49×** |

**Source database organises the embedding 3.53× as strongly as trait axis does.**

## Confound check: are source and axis just the same variable?

3 of 28 source namespaces emit more than one axis. Where a source maps to exactly one axis the two labelings are indistinguishable by construction, so the comparison above is only meaningful to the extent this number is large.

| source | records | axes emitted |
|---|--:|---|
| ECOD | 5,194 | STRUCTURE 100% |
| NCBIfam | 4,460 | FUNCTION 58%, SEQUENCE 42% |
| GO | 4,440 | FUNCTION 100% |
| CDD | 4,428 | SEQUENCE 62%, FUNCTION 38% |
| Pfam | 3,615 | SEQUENCE 100% |
| InterPro | 3,058 | SEQUENCE 100% |
| SCOP | 2,663 | STRUCTURE 100% |
| ComplexPortal | 2,384 | FUNCTION 100% |
| RHEA | 2,116 | FUNCTION 100% |
| TED | 1,585 | STRUCTURE 100% |
| CATH | 950 | STRUCTURE 100% |
| proteintraitsmech | 912 | STRUCTURE 80%, FUNCTION 19%, SEQUENCE 0% |

## The conditional test: source structure *within* one axis

Restricted to one axis at a time, so axis cannot explain the result. A high lift here means the map is separating provenance, not biology.

| axis | records | sources | source purity | chance | lift |
|---|--:|--:|--:|--:|--:|
| EVOLUTION | 2 | 1 | — | — | too few to judge |
| FUNCTION | 16,330 | 13 | 0.925 | 0.156 | **5.95×** |
| SEQUENCE | 12,393 | 11 | 0.544 | 0.221 | **2.46×** |
| SEQUENCE_STRUCTURE | 10 | 1 | — | — | too few to judge |
| STRUCTURE | 11,265 | 7 | 0.993 | 0.300 | **3.31×** |

## Counter-test: can the embedding retrieve cross-source equivalents?

1,500 pairs from `cross_source.tsv` whose two ends come from different databases, queried against all 344,797 embedded records.

| | |
|---|--:|
| partner ranked #1 | **70.5%** |
| partner within top-25 | **93.4%** |
| share of those top-25 that are same-source | 42.2% |

Read this against the purity tables above before concluding anything. Source-dominated neighbourhoods do **not** mean the embedding is blind across sources — where a genuine cross-source equivalent exists it is usually the nearest neighbour of all. Most records simply have no counterpart in another database, and their neighbourhoods fill with same-source records by default.
