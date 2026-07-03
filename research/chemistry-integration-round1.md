---
topic: integrating chemistry (ChEBI, formula, InChIKey, CAS) into ProteinTraitsMech
date: 2026-07-03
question: >-
  How best to represent the chemistry a protein trait touches — reaction
  substrates/products, transported substrates, cofactors — grounded in ChEBI
  with molecular formula, InChIKey, and CAS, without bloating the corpus.
status: recommendation adopted (ChemicalParticipant model + ChEBI sidecar)
---

# Chemistry integration — round 1

## 1. The gap

Chemistry currently enters the KB as scattered, semantically-loose xrefs:

- **TCDB** transport families carry ChEBI substrate ids in `xrefs` (946
  families) — but a *substrate* is not an *equivalence* of the trait.
- **Rhea** reactions know their ChEBI participants (in the raw export) but we
  deliberately did **not** write them, pending this decision.
- **EC** leaves carry cofactor/reaction chemistry only as free text (CA/CF).

There is no way to ask "which traits act on iron(2+) (CHEBI:29033)?" or to
show a molecular formula / InChIKey / structure for a participant.

## 2. The chemistry hub: ChEBI

[ChEBI](https://www.ebi.ac.uk/chebi/) (Chemical Entities of Biological
Interest, EBI) is the right and only grounding hub — it is what Rhea, TCDB
(getSubstrates), UniProt, and GO all already use.

- **Licence: CC BY 4.0** — compatible (attribution, per-record `license`).
- **Bulk flat files** (`https://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/`):
  - `chemical_data.tsv` — per CHEBI id: **FORMULA, MASS, MONOISOTOPIC MASS,
    CHARGE** (one row per datum, `TYPE` column).
  - `structures.csv.gz` — **SMILES, InChI, InChIKey** (`TYPE` column).
  - `database_accession.tsv` — external ids incl. **CAS Registry Number**,
    KEGG, MetaCyc (CAS itself is proprietary; ChEBI redistributes the mapping).
  - `names.tsv`, `compounds.tsv.gz` — labels, synonyms, stars, parents.
- Every identifier the user asked for — **formula, InChIKey, CAS** — is a
  lookup on the ChEBI id we already hold. So we do **not** need a separate
  formula/InChIKey source; we need to (a) store the ChEBI id with its *role*,
  and (b) resolve the rest from ChEBI.

## 3. Recommended model

Two-part design, following the KB's existing "lean record + derived/side-car
detail" philosophy (cf. lazy sequence sidecars, derived UniProt members link):

### (a) Schema: a `ChemicalParticipant` on the record

Add a `chemical_participants` slot (list of `ChemicalParticipant`) to
`ProteinTraitRecord`. Each entry:

| field | notes |
|---|---|
| `chebi` (required) | `CHEBI:nnnn` CURIE — the grounding |
| `role` (required)  | enum `ChemicalRoleEnum`: SUBSTRATE, PRODUCT, SUBSTRATE_OR_PRODUCT, COFACTOR, TRANSPORTED, INHIBITOR, PRODUCT_OR_SUBSTRATE |
| `name`             | human label (from the source; ChEBI canonical resolved in sidecar) |

This keeps the participant **semantically typed** (a substrate is not an
xref) and queryable. Molecular formula / InChIKey / mass / CAS are **not**
copied onto every record (167k records × many participants would bloat the
corpus and the browser payload) — they live in the sidecar:

### (b) A shared ChEBI sidecar for the browser

`docs/data/chebi.json` (built by `build_docs_index` from the ChEBI flat
files): `{ "CHEBI:29033": {name, formula, inchikey, mass, cas?} }`, restricted
to the ChEBI ids actually referenced in the corpus (a few thousand, not all of
ChEBI). The browser lazy-loads it and renders formula/InChIKey/structure-link
on demand — scalability-neutral, always current, zero per-record duplication.

## 4. Rollout

1. **Schema** — `ChemicalParticipant` class + `ChemicalRoleEnum` +
   `chemical_participants` slot. Regenerate.
2. **Rhea** — parse the ChEBI column of `rhea-reactions.tsv` →
   `chemical_participants` (role SUBSTRATE_OR_PRODUCT; direction is not in the
   master row). ~18k reactions, the highest-value chemistry set.
3. **TCDB** — migrate the ChEBI substrate `xrefs` → `chemical_participants`
   (role TRANSPORTED). Removes the semantic-abuse of `xrefs` flagged in review.
4. **EC** — cofactors (CF lines) are names, not ChEBI; defer (needs a
   name→ChEBI map) or grant a follow-up round.
5. **ChEBI sidecar** — collect referenced CHEBI ids, join against
   `chemical_data` + `structures` (+ `database_accession` for CAS), emit
   `docs/data/chebi.json`; browser renders it.

## 5. What we explicitly do NOT do

- **No formula/InChIKey/CAS on every record** — sidecar only (bloat + scale).
- **No PubChem / CAS bulk ingest** — CAS is proprietary; ChEBI's redistributed
  CAS mapping is sufficient and licence-clean.
- **No standalone "chemical trait" axis** — chemistry is an *attribute of a
  function trait* (what it acts on), not a trait of the protein itself, so it
  is a slot, not a new axis. (Reconsider only if we later seed ChEBI classes
  as first-class ligand-binding traits.)

## Sources
- [ChEBI downloads](https://www.ebi.ac.uk/chebi/downloads)
- [ChEBI flat files (FTP)](https://ftp.ebi.ac.uk/pub/databases/chebi/Flat_file_tab_delimited/)
- [ChEBI: re-engineered for a sustainable future, NAR 2026](https://academic.oup.com/nar/advance-article/doi/10.1093/nar/gkaf1271/8349173)
