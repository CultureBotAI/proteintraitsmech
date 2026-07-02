# Rules & evidence — trait equivalence

This file explains why the analyzer draws the MERGE / REVIEW line exactly where
it does. The short version: in a naive pass, "shares an xref" and "same label"
look like strong equivalence signals. In *this* corpus they are dominated by
false positives, so they are demoted to REVIEW. Only exact identity qualifies
for MERGE.

## The NEVER guards

Applied to **R2 and every review rule** (C1–C3), a candidate pair is discarded
outright if:

- the two records have a **different `trait_axis`**, or
- a **different `trait_category`**, or
- they carry **different values in the same identity namespace** (e.g. two
  distinct `EC:` numbers, two distinct `MOD:` ids) — a positive identity
  mismatch, not just "not equal".

**R1 (EXACT_ID) is deliberately exempt from the axis/category guard.** An
identical `identifier` is definitional identity: a source-anchored CURIE names
exactly one entity, so two records carrying it are the same entity regardless of
which directory/category the seeder placed them in. A cross-category R1 hit is a
*mis-categorization to be fixed*, not two distinct traits — and the merge fixes
it by keeping the more specific categorization. (The identity-namespace mismatch
guard still holds trivially: two records with the same identifier cannot carry
different values of that same identifier.)

These guards are what make the surviving MERGE statements safe.

## MERGE rules (unequivocal)

### R1 — EXACT_ID
Two records with the identical `identifier` string. In a path-idempotent seeder
world this only happens when one source term is deliberately or accidentally
written to two directories. Examples found in the catalog:

- `PROSITE:PRU00498` in both `sequence/glycosylation/` and `sequence/prorule/`
- `PROSITE:PRU00672`, `PROSITE:PRU00673` in both `sequence/modified_residue/`
  and `sequence/prorule/`
- `PROSITE:PS00654` in both `sequence/modified_residue/` and `sequence/pattern/`

These are the same PROSITE entity by definition — merging is not a judgment call.

### R2 — EXACT_PATTERN
Byte-identical, non-empty `sequence_pattern` **and** identical `(axis,
category)`. A PROSITE pattern / regex is a highly specific string; two records
carrying the same one describe the same sequence signature. The `(axis,
category)` guard prevents equating, say, a motif and a PTM record that happen to
reuse a fragment. In the current catalog R2 only ever coincides with R1, but it
generalizes to future cross-source imports (e.g. a PROSITE PATTERN and a UniProt
`MOTIF` that share an identical regex).

## REVIEW rules (candidates — never auto-merged)

### C1 — XREF_IDENTITY
One record's source-anchored `identifier` appears in the other's `xrefs`, same
`(axis, category)`. This *looks* like "A declares it is B", but in practice it is
associative:

- `PROSITE:PRU00293` (ProRule) xrefs `PROSITE:PS00016` (the PATTERN it is built
  on). Same category (`SEQ_MOTIF`), but a rule and a pattern are distinct
  PROSITE entries — a rule can span several patterns.
- `MOD:00693` (a PSI-MOD glycosylation term) and `PROSITE:PS00001`
  (N-glyco pattern) cross-reference each other; one is the modification, the
  other is the sequence pattern that flags it.

So C1 is a strong "these are about the same thing" signal, but not "these are the
same trait record". A curator decides whether the corpus should keep both.

### C2 — SHARED_ANCHOR
Both records cite the same **specific** identity-namespace xref, and that xref is
shared by at most `--anchor-cap` records (default 5). The cap is the crucial
part: without it, the top "shared xref" is `SO:0001067` ("polypeptide_region"),
cited by ~2,700 motif records — a generic grounding, not an identity. With the
cap, C2 surfaces things like PROSITE pattern+profile pairs for one family
(`PS00171`+`PS51440`, both linked to `PRU10127`). Same underlying signature, two
detection methods — the repo keeps both intentionally, so this is REVIEW, not
MERGE.

**Identity namespaces** (used only for C2): `EC`, `RHEA`, `MOD`, `Pfam`,
`InterPro`, `CATH`, `SCOP`, `ECOD`, `PROSITE`, `HAMAP`. Namespaces like `GO`,
`SO`, `PATO`, `PMID`, `DOI` are deliberately excluded — in this corpus they
ground records rather than identify them.

### C3 — SAME_LABEL_XSRC
Identical normalized label (lowercased, punctuation collapsed) across **different
sources**, same `(axis, category)`. Restricted to cross-source on purpose:
intra-source label reuse is rampant and meaningless — 25,685 same-label pairs
exist, and **all** are intra-source, dominated by TED/ECOD folds
(`STRUCT_FOLD` alone contributes ~22k) that share a generic name while being
distinct domains. Cross-source label collisions (0 today) are a plausible future
duplicate worth a human look.

## Why not more aggressive?

The temptation is to auto-merge C1/C2 ("same anchor, same category — surely the
same trait?"). Resist it. The corpus intentionally holds distinct records for a
family's PROSITE *pattern* vs *profile* vs *ProRule*, and for a modification vs
the motif that flags it. Collapsing those loses real distinctions. If two records
truly are one trait, the correct fix is to make the deterministic signal fire —
give them the same `identifier` or `sequence_pattern`, or fix the seeder — not to
lower the merge bar.
