---
date: 2026-07-27
issue: "#7 / #57 — closing the residue frame's gaps"
prior: swissprot-trait-profiles-12.md
---

# Swiss-Prot trait profiles — Phase 13: the last exemplars, and provenance for the caches

Two items left explicitly undone by phase 12: the exemplar accessions the residue
frame was still missing, and #57 — the sidecars recording nothing about where
they came from.

## 1. Release stamps, and refusing to resume across them (#57)

Three caches feed the residue-frame alignment:

| cache | holds |
|---|---|
| `residue_frame.json` | UniProt sequences + FT intervals |
| `interpro_frame.json` | InterPro member-DB matches with coordinates |
| `interpro_members.json` | which Gene3D signatures each InterPro entry integrates |

All three were plain `{key: value}` maps with no record of when they were built or
which release they came from. That matters more than it first looks, because **the
fetchers resume** — they skip keys already present. So a stale entry is never
refreshed, and the resumability that makes a 27,000-protein crawl affordable also
makes staleness permanent. Signature boundaries move between InterPro releases,
and a moved boundary flips `part_of` / `overlaps` / `related_to` in the emitted
overlay. The residue-set identity call is *exact*: a one-residue shift changes the
answer, and phase 12 promoted 1,640 of those calls to `close_match`.

Both releases turn out to be discoverable, so nothing needs to be configured:

* UniProt returns `x-uniprot-release: 2026_02` as a response header.
* InterPro publishes `utils/release/`; the current release is **109.0**.

`scripts/sidecar.py` wraps each cache:

```json
{"_meta": {"schema": 1, "built": "2026-07-27", "source": "UniProt",
           "release": "2026_02", "count": 98922},
 "proteins": { … }}
```

and the fetchers now refuse to resume across a release change:

| cached | current | behaviour |
|---|---|---|
| 109.0 | 109.0 | resume |
| 108.0 | 109.0 | **refuse** — "resuming would mix coordinates from two releases" (`--allow-stale` overrides) |
| headerless (legacy) | 109.0 | **refuse**, with a rebuild hint — data still loads for consumers |
| 109.0 | unavailable | resume, with a warning |

The last row is deliberate: a network hiccup while checking the release should not
block a crawl. The third is the one that will actually fire — every existing
sidecar predates stamping — and it distinguishes "I know these disagree" from "I
cannot tell", which is the distinction that was missing.

Consumers accept both shapes, so `build_sequence_structure_alignment.py` keeps
working against an unstamped cache and simply cannot report its provenance. It
now prints the source and release when they are available, which puts the
coordinate provenance next to the overlay it produced.

## 2. The last 24,908 exemplars

Phase 12's dry-run fix — making `--dry-run` mean "no network" — immediately
surfaced that the residue frame was missing **24,908** exemplar accessions, well
beyond the 19,711 phase 11 topped up. The cause was phase 11's own regex
correction: it made 27,325 previously-invisible records visible, and their
exemplars had never been fetched.

This is the tail of a chain worth naming, because each step only became visible
after the previous one was fixed:

1. Phase 10 built the frame for ten proteomes → exemplars outside them invisible.
2. Phase 11 topped up 19,711 → but a regex skipped 27,325 records entirely.
3. Phase 11 fixed the regex → 24,908 more exemplars became visible.
4. Phase 12 made dry runs offline → which is how anyone could see that.

### It bought no edges, and that is the finding

The frame grew **98,922 → 113,592 proteins** (+14,670; the ~10k shortfall are
accessions UniProt no longer serves). The overlays did not move at all:

| | before | after |
|---|--:|--:|
| records localized | 61,015 | 61,017 |
| `seq_struct_func_sites.tsv` | 6,982 | 6,982 |
| `seq_struct_alignment.tsv` | 12,424 | 12,424 |

Zero new edges. The reason is structural:

> **83,604 of the 113,592 proteins in the frame host records of only one trait
> category.** A residue-frame edge needs two *comparable* records on one protein,
> so those proteins can never contribute one.

The residue frame is now complete with respect to the corpus's exemplars, and
completeness was not the binding constraint. That is worth stating plainly:
phase 12 queued this item as if the missing exemplars were leaving edges on the
table, and they were not.

### What the binding constraint actually is

Only **8,689 proteins host ≥2 comparable records**. More proteins do not help;
more *sharing* would. And sharing is capped by our own hand:

| SWISSPROT_PROFILE exemplars per record | records |
|---|--:|
| 1 | 16,100 |
| 2 | 14,632 |
| **3 (the `--max-examples` cap)** | **41,271** |

**57% of records sit exactly at the cap.** `suggest_canonical_examples
--max-examples 3` is therefore the live limit on how often two records can share
a protein — the same cap that makes `n=3` the ceiling on phase 12's support
counts. Raising it is the concrete lever for more residue-frame edges, and it
costs nothing to fetch: the exemplars are ranked from a matrix we already hold.

## Gate

* Release guard unit-tested across all four cases (match / mismatch / legacy /
  release-undeterminable) before being wired in.
* Consumers verified against both the stamped and legacy shapes.
* Overlays rebuilt and checked as a superset before writing (0 lost, 0 added —
  byte-identical, which is itself the result).

## Caveats

* The top-up re-requests the ~10,238 accessions UniProt no longer serves on every
  run. They return no result inside an otherwise-successful batch, so nothing
  records that they are permanently dead — unlike the 9 malformed ones, which
  fail loudly. A "known-absent" list would stop the retry.
* The release guard cannot help the caches built before it: they load, warn, and
  need `--allow-stale` once. From the next rebuild they are stamped.

## Next

- Raise `--max-examples` above 3 and re-rank: 57% of records are at the cap, and
  protein sharing — not protein count — is what limits the residue frame.
- The 14 SUPERFAMILY-based refutations from phase 12 could be checked against
  SUPERFAMILY↔CATH mappings.
