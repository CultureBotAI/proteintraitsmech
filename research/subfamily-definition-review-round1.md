---
topic: subfamily-definition-review
round: 1
date: 2026-08-04
target: PANTHER SEQ_FAMILY — the 228 subfamily-derived definitions from #154
prior_round: none
---

# Subfamily-derived PANTHER definitions — LLM review, round 1

## What was reviewed

#154 gave 228 annotation-free PANTHER families a definition composed from the GO /
protein-class terms **every** annotated subfamily shares. The rule is mechanical and
the provenance is explicit, but nothing had checked whether the borrowed claim is
*biologically sensible for that family*. This round asked a second model (codex,
`codex exec`) to judge exactly that, 12 records per batch, four batches in flight.

The model saw only the family name, the number of annotated subfamilies, and the
borrowed terms — not the repo, not the file. Every reply was checked to contain
exactly the ids sent, so a batch could not be answered from invention; a previous
codex run in this repo fabricated 25 plausible PANTHER records when its input went
missing, and that is the guard against a repeat.

## Verdicts

| verdict | n | of which basis n=2 |
|---|--:|--:|
| OK | 156 | 36 (23%) |
| QUESTIONABLE | 61 | 12 (20%) |
| WRONG | 11 | 5 (45%) |
| **total** | **228** | 53 (23%) |

**The two records I had flagged by hand while reviewing #151 — `PTHR10036` CD59 and
`PTHR31692` EXPANSIN-B3 — both came back WRONG, independently.** That is the main
reason to trust the rest of the list.

## The finding that changes a decision

`WRONG` is **45% n=2** against a 23% baseline. Records resting on exactly two
annotated subfamilies are roughly twice as likely to be wrong as the population.
`MIN_SUBFAMILIES = 2` was left at 2 in #154 on the argument that the definition
discloses its own basis size; this is the first evidence about what that tier
actually costs. Raising it to 3 would have prevented 5 of the 11 errors and also
removed 36 records judged OK.

## What was acted on

**The 11 WRONG are reverted to name-only stubs**, each with a `curation_history`
event carrying the model's reason. A stub is the honest outcome #115 already
describes: it says what the record is and where it came from, and does not pretend
to knowledge nobody verified.


| id | family | why it was rejected |
|---|---|---|
| `PTHR10036` | CD59 GLYCOPROTEIN | CD59 inhibits complement membrane-attack complex formation, whereas acetylcholine-receptor regulation belongs to other Ly6-family proteins such as SLURP1. |
| `PTHR12349` | ANKYRIN REPEAT AND LEM DOMAIN-CONTAINING PROTEIN 2 | ANKLE2 regulates BAF dephosphorylation and nuclear-envelope reassembly and lacks DHHC palmitoyltransferase machinery, making the lipidation terms incompatible. |
| `PTHR21444` | COILED-COIL DOMAIN-CONTAINING PROTEIN 180 | Plasma-membrane retinol transport describes STRA6 relatives, not the large coiled-coil protein CCDC180. |
| `PTHR30128` | OUTER MEMBRANE PROTEIN, OMPA-RELATED | This family actually contains photosystem I PsaA/PsaB thylakoid proteins, not bacterial outer-membrane OmpA proteins. |
| `PTHR31045` | PLAC8 FAMILY PROTEIN-RELATED | PLAC8 proteins are chiefly membrane-associated growth or metal-homeostasis proteins, not isoprenoid cyclases. |
| `PTHR31692` | EXPANSIN-B3 | Expansin-B proteins are secreted plant cell-wall-loosening proteins, not components of animal-like cell-cell or anchoring junctions. |
| `PTHR33136` | RAPID ALKALINIZATION FACTOR-LIKE | RALF-like proteins are secreted plant signaling peptides associated with the apoplast and cell wall, not anchoring or cell-cell junction components. |
| `PTHR33734` | LYSM DOMAIN-CONTAINING GPI-ANCHORED PROTEIN 2 | Plant LYM2 proteins are GPI-anchored LysM chitin-binding immune receptors, not carbon-oxygen lyases. |
| `PTHR34491` | A-TYPE INCLUSION PROTEIN, PUTATIVE-RELATED | A-type inclusion proteins form cytoplasmic viral inclusions and depend on microtubules but are not microtubule-organizing-center or cytoskeletal components. |
| `PTHR47114` | Leucine-rich repeat-containing bacterial E3 ubiquitin ligases | These are bacterial LRR effectors, whereas multicellular and nervous-system development annotations derive from unrelated eukaryotic LRR proteins. |
| `PTHR47633` | IMMUNOGLOBULIN | Immunoglobulins are antigen-binding proteins, not catalytic protein kinases. |

## What was deliberately NOT acted on

**The 61 QUESTIONABLE records keep their definitions.** Reading the reasons, the
objection is almost always "true of part of the family, misleading as a family-wide
statement" — which is precisely what the composed prose already discloses by naming
its basis (*"shared by all 3 of its annotated subfamilies"*). Reverting them would
discard defensible information to avoid a risk the reader has already been handed.
Eight of the 61 were called out as too generic to say anything; those are the
strongest candidates if a stricter pass is ever wanted.

Representative QUESTIONABLE reasons:

- `PTHR12044` **BCL2 INTERACTING MEDIATOR OF CELL DEATH** — BIM can affect reproduction, division, and organelles through apoptosis, but these secondary consequences are misleading as family-wide functions.
- `PTHR32444` **BULB-TYPE LECTIN DOMAIN-CONTAINING PROTEIN** — Bulb-type lectin proteins also include vacuolar, nucleocytoplasmic, and membrane-receptor forms, so cell-wall localization is not family-wide.
- `PTHR33404` **CELL DIVISION TOPOLOGICAL SPECIFICITY FACTOR HOMOLOG, CHLOROPLASTIC** — MinE homologs organize division-site placement, but these broad cellular-organization terms provide little meaningful family-level characterization.
- `PTHR22595` **CHITINASE-RELATED** — The family includes catalytically inactive chitinase-like GH19 proteins, so chitinase activity is not reliably family-wide.
- `PTHR31131` **CHROMOSOME 1, WHOLE GENOME SHOTGUN SEQUENCE** — Negative signaling regulation fits metazoan CASTOR subfamilies, but not the family's distant fungal and archaeal ACT-domain relatives.

## Provenance

records reviewed: 228 · reverted: 11 · unchanged: 217 · all verdicts recorded in `research/subfamily-definition-review.jsonl`

## Open questions

- Should `MIN_SUBFAMILIES` rise to 3, given WRONG is 45% n=2? That is a records
  decision, not a code one — filed rather than taken.
- The review judged the terms *as shown*, i.e. the three lowest GO IDs. #152 changes
  which three are shown, so a re-review is warranted after it lands.

