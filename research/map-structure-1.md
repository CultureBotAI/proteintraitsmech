# Does `corpus_map.json` show trait axis, or source database?

40,000 records sampled of 344,797 mapped (5 axes, 28 source namespaces); k=25 neighbours.

| space | label | purity | chance | lift |
|---|---|--:|--:|--:|
| embedding (pre-projection) | trait axis | 0.943 | 0.342 | **2.76×** |
| embedding (pre-projection) | source database | 0.803 | 0.083 | **9.68×** |
| 2-d map (what is rendered) | trait axis | 0.962 | 0.342 | **2.81×** |
| 2-d map (what is rendered) | source database | 0.761 | 0.083 | **9.17×** |

**Source database organises the embedding 3.51× as strongly as trait axis does.**

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
| FUNCTION | 16,330 | 13 | 0.894 | 0.156 | **5.75×** |
| SEQUENCE | 12,393 | 11 | 0.596 | 0.221 | **2.69×** |
| SEQUENCE_STRUCTURE | 10 | 1 | — | — | too few to judge |
| STRUCTURE | 11,265 | 7 | 0.991 | 0.300 | **3.31×** |

## Counter-test: can the embedding retrieve cross-source equivalents?

1,500 pairs from `cross_source.tsv` whose two ends come from different databases, queried against all 344,797 embedded records.

| | |
|---|--:|
| partner ranked #1 | **68.1%** |
| partner within top-25 | **94.7%** |
| share of those top-25 that are same-source | 49.7% |

Read this against the purity tables above before concluding anything. Source-dominated neighbourhoods do **not** mean the embedding is blind across sources — where a genuine cross-source equivalent exists it is usually the nearest neighbour of all. Most records simply have no counterpart in another database, and their neighbourhoods fill with same-source records by default.
