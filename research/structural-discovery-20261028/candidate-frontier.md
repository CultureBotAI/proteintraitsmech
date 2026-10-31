# First bounded structural discovery frontier

Prepared 2026-10-29 UTC for the accepted 2026-10-28 standalone goal. Ranking favors
distinct class identity, missing catalog coverage, compatible inspected primary
evidence, an explicit detection criterion, and a defensible structure example.
All are established literature concepts; no novel-to-science claim is proposed.

| Rank | Candidate | Initial disposition and discriminator |
| --- | --- | --- |
| 1 | Protein tunnel bottleneck | Canary: minimum-radius region of a specified tunnel; part_of TUNNEL, not a whole-tunnel subclass. CAVER primary article and documented executable; source-computed 1CQW representative. |
| 2 | Beta-arch | Strong supersecondary candidate: strand connection without hydrogen-bond pairing of the flanking strands; distinguish hairpin and full Ig fold. Compatible 2022 primary source; confirm exact absence and structure identity. |
| 3 | Membrane-facing lateral fenestration | Conditional: central pore/cavity to membrane-side passage; distinguish axial pore and enclosed void. Compatible primary evidence and executable geometry discrimination under review. |
| 4 | Asx turn | Conditional: three-residue side-chain/backbone turn; distinct from existing five-residue Asx motif. SO:0000912 is a possible exact external identifier; requires collision and example review. |
| 5 | Serine/threonine turn | Conditional: analogous three-residue geometry defined by Ser/Thr side chain. SO:0001141 is a possible exact identifier; accepted only with adequate example support. |
| 6 | Schellman motif/loop | Defer pending precise topology and umbrella/subtype overlap review against helix-cap and pi-turn. |
| 7 | Beta-bulge loop | Defer for separate topology/example audit; generic beta bulge already exists. |
| 8 | Psi-loop | Defer pending full topology and runnable detection evidence. |
| 9 | Pocket subcompartment/subpocket | Defer: algorithm-dependent partition and identity require a justified class contract. |
| 10 | Intersubunit/interdomain cavity | Defer: needs assembly/domain partition and explicit cavity-connectivity criteria. |
| 11 | Generic cryptic pocket | Defer: distinguish existing allosteric cryptic pocket, comparator-state requirements and functional implications. |

Rejected as existing generic classes after direct current-corpus inspection:
beta bulge, alpha turn, pi turn, alpha-alpha corner, beta meander. Their YAMLs are
in `data/traits/structure/secondary/`; their enrichment is not a discovery addition.
The earlier 24 enriched records are also excluded from the new-record count.

## Canary coordination decision

The isolated discovery writer owns proposed ID
`proteintraitsmech:TUNNEL_BOTTLENECK`, destination
`data/traits/structure/cavity/tunnel-bottleneck.yaml`, and its maintained manifest
and seeder. Native assignment authority and coordination limits are documented
in `preflight/coordination-contract-audit-20261029T064651Z.json`.
The ignored-inclusive cavity inventory reports no matching record identity or
indexed label; the nine contextual mentions denote whole tunnels or unrelated
biology, not this geometric part. No exact external ontology identifier was
identified in the bounded search; inaccessible OLS results are not negative proof.
The native writer independently checks the proposed ID against all corpus YAML,
including ignored/hidden paths, immediately before writing.

`open-work-prewrite.json` pins current main and 32 open PRs; the retained preflight
review identifies shared owners. This task uses inline record methods and current
schema, leaving grounding registries untouched. Shared changes will be limited to
the corpus-count baseline, an added native seeding recipe, the source-helper
classification of that local generator, and generated browser artifacts.
Concurrent PR706 owns browser builder changes, PR714 owns proposed
schema additions, and PR797–800 own grounding. Generated artifacts must be
reconciled from maintained inputs if those PRs land first. No shared checkout is
edited, no durable ID reservation is claimed, and no long-held repository lease
is created.

## Canary completion and batch decision

The canary was emitted by the native writer with SHA-256
`d4793579cd2dd1f5240deb43476c7f56bc0da359731094049a39c36d34f46ae2` after
parsing all 429394 existing corpus YAMLs. Strict/grounding validation passed and
the graph audit found no graphs or errors. Independent scientific review was
saved as `reviews/structured/20261029T071028Z-independent-tunnel-bottleneck-canary/`.
The independent writer review is
`reviews/structured/20261029T070848Z-independent-structural-discovery-writer/`;
issue #1204 records the three reproduced and fixed guard defects.

The bounded batch selects ranks 1–3. The additional assigned IDs and owned paths are:

- `proteintraitsmech:BETA_ARCH`: `data/traits/structure/secondary/beta-arch.yaml`.
- `proteintraitsmech:MEMBRANE_FACING_CHANNEL_FENESTRATION`:
  `data/traits/structure/cavity/membrane-facing-channel-fenestration.yaml`.

Motif and cavity inventories include ignored/hidden evidence, corpus, aliases
and indexed labels. The candidate-specific matching contexts were adjudicated;
an anatomical glomerular fenestra is not a protein passage, and full folds are
not beta-arch motif classes. Existing broad parents and issue plans do not
constitute equivalent implemented records. Current main remained `7276814b…`
and all 32 PR heads matched the initial snapshot immediately before this batch
(`prebatch-main.txt`, `prebatch-pr-heads.json`). The writer repeats parsed ID/xref
collision checks before creation. This is coordinated assignment, not reservation.

Asx and ST turns are deferred from this first batch despite clear class identity:
the compatible-example assertion and class-specific executable detection route
need additional work. Their exact SO identifiers are retained in the cards;
internal replacement IDs are not minted. The other ranked deferrals remain as
listed above. Emitted validation, independent review and byte-identical replay
accepted three new PROPOSED records: one supersecondary motif and two tertiary
geometric features. No qualified protein or residue occurrence was added.
