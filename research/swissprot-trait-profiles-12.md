---
date: 2026-07-27
issue: "#7 — adjudicating what the residue frame found"
prior: swissprot-trait-profiles-11.md
---

# Swiss-Prot trait profiles — Phase 12: 1,640 equivalences the mappings never had

Phase 11 populated the base signature↔fold overlay for the first time, including
1,747 edges whose two records cover the **identical residue set** on every shared
exemplar protein. Those were left as `biolink:related_to` pending curation. This
phase adjudicates them, and clears two smaller items.

## 1. The identical-residue links are almost all real — and all new

1,680 of the 1,747 pair a CATH superfamily with an InterPro entry. The first
thing worth knowing about them:

> **None of the 1,747 appear in `cross_source.tsv`.**

That overlay holds 24,299 cross-source pairs derived from identifier mappings
(interpro2cdd, interpro2go, …). The residue frame found these independently, from
coordinates, with no mapping involved.

Identical residues on a protein prove co-extension *there*, not that two records
denote the same thing — so each pair was checked against the authority. InterPro
publishes the member signatures each entry integrates; if `InterPro:IPRxxxxxx`
lists `G3DSA:<cath>` among its Gene3D members, the two are the same superfamily
under two identifiers.

`just verify-residue-identity` (`scripts/verify_residue_identity.py`):

| verdict | pairs | |
|---|--:|---|
| **confirmed** | **1,640** (97.6%) | InterPro integrates that exact Gene3D signature |
| refuted | 40 | InterPro integrates **no** Gene3D signature at all |
| unresolved | 0 | |

The refutations are clean: not one of the 40 pointed at a *different* Gene3D
signature. Those entries are built on SUPERFAMILY rather than Gene3D, so their
residues genuinely coincide with a CATH superfamily without the two being the
same object. They stay `related_to`.

Confirmed pairs are emitted as `data/equivalence/residue_identity.tsv` with
`biolink:close_match` — a stronger claim than the alignment overlay's
`related_to`, carried by two independent lines of evidence (residue co-extension
plus InterPro's own membership).

**Not a merge, deliberately.** Cross-axis pairs are relate-only per the
merge-within-axis skill, and that is right here: a sequence signature and a
structural superfamily are two representations of one biological entity, which is
what `close_match` says and `exact_match` would overstate.

### What the support counts mean

| supporting proteins | confirmed pairs |
|---|--:|
| 3 | 1,052 |
| 2 | 249 |
| 1 | 339 |

Three is the **ceiling**, not a coincidence: `suggest_canonical_examples
--max-examples 3` gives each record at most three exemplars, so two records can
share at most three proteins. `n=3` therefore means *all available evidence
agrees*, and the distribution says roughly two-thirds of confirmed pairs are at
maximum support. Reading `n` as a raw count would badly understate it.

## 2. The nine bad exemplars are rRNA chains (#54)

Phase 11 found nine `protein_id` values that are `UNS…` placeholders, and guessed
they were "PDB chains with no UniProt mapping". Removing them showed something
more specific:

```yaml
-  - protein_id: UniProtKB:UNS1553536315
-    protein_label: "16S ribosomal RNA"
-  - protein_id: UniProtKB:UNS282796703
-    protein_label: "23S ribosomal RNA"
```

They are **nucleic acid chains**. MetalPDB metal sites occur on rRNA as readily as
on protein, and the seeder emitted those occurrences as `canonical_examples` —
a field whose whole contract is *exemplar proteins* — with fabricated accessions.
The right fix is removal, not repair: there is no UniProt accession to find.

34 such exemplars across 22 records are gone. Every affected record still has
genuine protein exemplars or none.

The schema pattern is now UniProt's actual accession syntax:

```
^UniProtKB:([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})([-][0-9]+)?$
```

Checked against all **93,150** distinct `protein_id` values in the corpus: it
rejects exactly the nine known-bad ones and nothing else. The previous pattern,
`[A-Z0-9]+`, accepted any alphanumeric string — which is why these validated
cleanly for as long as they existed.

## 3. Dry runs no longer hit the network

`fetch_residue_frame.py` streamed every proteome during `--dry-run` and gated only
the *write*, so a dry run cost a full crawl (and ~200 more requests with
`--top-up`). It now reports the planned queries, how many accessions the top-up
would fetch, and the frame's current size, without a single request.

That immediately surfaced something: **24,908 exemplar accessions are still
missing from the residue frame** — far more than the 19,711 phase 11 topped up,
because phase 11's corrected regex made 27,325 previously-invisible records
visible. Recorded as the next phase's first item rather than expanding this one.

## Gate

* Tightened pattern verified against all 93,150 corpus `protein_id` values before
  changing the schema; the 22 rewritten records validate clean.
* Adjudication caches verdicts, so re-runs are free and deterministic.
* `residue_identity.tsv` is additive — it does not touch the alignment overlay,
  so nothing from phase 11 is at risk.

## Caveats

* The InterPro membership check is a point-in-time snapshot with no release
  stamp — the same gap #57 records for the coordinate sidecars, now applying to a
  third cache.
* 339 confirmed pairs rest on a single shared protein. They are confirmed by
  InterPro membership independently of that, so the evidence is not weak — but the
  residue-coincidence half of it is.

## Next

- Top up the residue frame with the 24,908 newly-visible exemplars and rebuild
  the overlays.
- #57: give the sidecars a release stamp and refuse to resume across releases.
- The 40 refuted pairs are SUPERFAMILY-based InterPro entries; checking them
  against SUPERFAMILY membership would either confirm or finally close them.
