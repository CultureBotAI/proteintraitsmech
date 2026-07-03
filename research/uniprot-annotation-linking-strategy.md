---
topic: linking traits to UniProt-annotated proteins (marked-up examples + member queries)
date: 2026-07-02
question: >-
  For every family/domain/site trait, attach (a) a marked-up sequence example
  from a real UniProt protein already annotated with that trait's source id,
  and (b) a UniProtKB query link that returns ALL family members via the family
  id (Pfam, CATH, SCOP, TED, KO, …).
---

# Strategy: UniProt-anchored examples + family-member queries

Two deliverables per trait record: a **marked-up example** (one representative
Swiss-Prot protein with the trait's region highlighted) and a **members link**
(the UniProt query returning every protein carrying that family id). Most of the
machinery already exists — this is reuse + extension, not new infrastructure.

## What already exists

`scripts/fetch_uniprot_examples.py` (`just fetch-examples`) already:
- builds a UniProt REST query from a record's identifier / parent_traits / xrefs
  (`Pfam:PF… → xref:pfam-PF…`, `InterPro:IPR… → xref:interpro-IPR…`,
  `PROSITE:PS…`, `SMART:SM…`, `HAMAP:MF_…`, `CATH:… → xref:cath-…`);
- filters to `reviewed:true` (Swiss-Prot), picks top hits by annotation score;
- writes `canonical_examples` with `sequence`, `features` (start/end/type/axis),
  `sequence_length`, `family_classifications`, etc.;
- the browser renders these as a **per-residue marked-up sequence viewer** with
  the feature tracks coloured by axis.

So "a marked-up sequence example from each trait" is **already supported** — the
work is (1) run it across the new sources, (2) fix the per-source query mapping,
(3) add the members link.

## Per-source UniProt query (verified member counts)

The member query is `xref:<db>-<id>` (web:
`https://www.uniprot.org/uniprotkb?query=<q>`; REST:
`https://rest.uniprot.org/uniprotkb/search?query=<q>&format=list`).

| Trait source | UniProt query | Direct? | Notes |
|---|---|---|---|
| **Pfam** `PF00069` | `xref:pfam-PF00069` | ✅ (1.3M) | as-is |
| **InterPro** `IPR…` | `xref:interpro-IPR…` | ✅ | as-is |
| **PROSITE/SMART/HAMAP/PIRSF/PRINTS/PANTHER/NCBIfam** | `xref:<db>-<id>` | ✅ | PANTHER `PTHR24356` → 27,873 |
| **CATH** `3.40.50.300` | `xref:gene3d-3.40.50.300` | ✅ via **Gene3D** | UniProt exposes CATH as Gene3D (`cath-…` returns 0; use `gene3d-`) |
| **SCOP / SCOPe** superfamily | `xref:supfam-SSF52540` | ✅ via **SUPERFAMILY** | SUPERFAMILY is SCOP-built (7M members). Need `sccs → SSF` map (SUPERFAMILY release) |
| **SUPERFAMILY** `SSF…` | `xref:supfam-SSF…` | ✅ | as-is |
| **TED** `AF-P12345-F1-TED01` | — | ⚠️ bridge | no UniProt xref; the accession is embedded (`AF-<acc>`) → the example IS UniProt `<acc>`; "members" = other TED domains of the same fold (TED-side, not a UniProt query) |
| **KEGG KO** `K00099` | — | ⚠️ bridge | no `xref:ko-` query; use KEGG `link/uniprot/ko:K…`, or the KO xrefs already on our EC records |

## The members link — implement in the browser (no schema/data change)

Because the query is a pure function of the identifier, add it as a **derived
link in `browse.js`** rather than storing a URL on every record:

- a `MEMBER_QUERY` map: identifier prefix → `(id → uniprot query)`
  (`Pfam → xref:pfam-<id>`, `CATH → xref:gene3d-<id>`, `SCOP → xref:supfam-<ssf>`
  after the sccs→SSF map, InterPro/SMART/HAMAP/PANTHER/SUPERFAMILY direct);
- on the detail view, render **"All UniProt members ↗"** →
  `https://www.uniprot.org/uniprotkb?query=<q>`, optionally fetching
  `x-total-results` to show the count;
- zero schema change, zero per-record data, always current.

For the SCOP→SUPERFAMILY and (optional) KO→KEGG cases, ship the small `sccs→SSF`
lookup as a `docs/data/` map the browser loads, or bake it into the seeder as an
xref (`SUPERFAMILY:SSF…`) so the link is derivable.

## Marked-up examples — rollout

1. **Extend the query dispatch** in `fetch_uniprot_examples.py`: add `Gene3D`
   for CATH (map `CATH:x` → `xref:gene3d-x`), `SUPERFAMILY` for SCOP (via the
   sccs→SSF map), and the TED-accession shortcut (fetch `<acc>` directly).
2. **One reviewed exemplar per record** (top annotation score), with the
   trait's feature range as a `feature` so the viewer highlights exactly the
   domain/site region. Cap sequence length shown; store the full sequence in the
   lazy per-record sidecar (already the pattern).
3. **Batch + cache + rate-limit** (~4 req/s, backoff) — the fetcher already
   does this; run per category (`just fetch-examples data/traits/structure/domain/pfam --limit N --apply`).
4. **Prioritise** the high-value, queryable categories first: Pfam & InterPro
   domains, CATH/SCOP superfamilies (huge member sets, clean marked-up
   examples), then PROSITE motifs and the site categories.

## Scale note

Examples live in `canonical_examples` and their heavy sequences in the lazy
`docs/data/seq/` buckets (already bucketed for Pages). Adding one example per
record does not grow the browser's initial load (sequences are fetched on
detail view), and the members link is derived — so this enrichment is
**scalability-neutral**, which matters now that the corpus is ~158k records.

## Recommended first step

Ship the **browser members-link** (derived, immediate, no data change) for the
directly-queryable sources (Pfam, InterPro, CATH→Gene3D, SUPERFAMILY, PANTHER,
SMART, HAMAP), then extend `fetch_uniprot_examples.py` to CATH/SCOP and run it
per category for the marked-up exemplars.
