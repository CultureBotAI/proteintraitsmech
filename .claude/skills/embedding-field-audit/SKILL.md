---
name: embedding-field-audit
description: Use this skill to decide which ProteinTraitRecord fields to include vs exclude when assembling the text that gets embedded (scripts/embed_records.py → load_corpus), so the vectors capture what defines and distinguishes each trait CLASS rather than per-instance noise, opaque identifiers, or boilerplate. It profiles each field empirically (coverage, cardinality, length, opaque-id-ness) and applies a fixed decision rubric — e.g. EXCLUDE canonical_examples protein sequences (per-protein, long, non-class-level) but INCLUDE sequence_pattern regexes (PROSITE patterns are class-defining). Trigger when asked which fields to embed, to tune/curate the embedding document, to improve the corpus map / related-traits quality, or before re-running embed_records.
---

# Embedding Field Audit

## What this is

`embed_records.py` serializes each record to one short document, then embeds it
(bge-large, ~512-token window). The **quality of every downstream semantic
feature** — related-traits, Tier-5 candidates, the corpus map, the
definition-only map — is bounded by *what text goes into that document*. This
skill decides, field by field, what to include.

The goal is a document that captures the trait **class's semantic identity** plus
the **shared identifiers/groundings that tie it to its source/classification
neighbours** — and nothing else. Every token spent on **per-instance** data
(example sequences, one protein's accession) or boilerplate is a token stolen
from the 512-token window. Note the distinction: an *opaque but shared* token (a
hierarchical id, a common xref) is signal — related traits co-occur on it; an
*opaque and unique* token (an example's accession) is noise.

## The four tests (apply to every field)

A field's text earns a place in the embedding only if it passes **all four**:

1. **Class-level, not instance-level.** Does it describe the *trait class*, or a
   particular protein that happens to carry it? Example proteins, their
   sequences, accessions, and taxa describe instances → **out**.
2. **Discriminative.** Does the value differ between classes? A field that is
   near-constant across the corpus (license, term_kind, mapping_status) adds no
   separating signal → **out**.
3. **Meaningful OR shared.** A token earns its place if it is natural language,
   OR a coded token whose *form carries meaning* (a PROSITE regex, an EC number's
   dotted class), OR **an identifier/grounding shared between related class-level
   entries**. This last case matters: a record's own hierarchical id
   (`ECOD:F.1.1.1.3` / `…1.4` share the `F.1.1.1` prefix), its parent id (siblings
   share it exactly), and its xrefs/mappings (related traits are grounded to the
   same `GO:…`/`InterPro:…`) all cluster same-source / same-classification-subtree
   traits **by co-occurrence**, even though each token is individually opaque —
   that is genuine within-source structural similarity, not noise. What fails this
   test is a token **unique to one instance** and therefore never shared (a
   canonical_example's protein sequence or accession) — pure noise.
4. **Fits the window.** Would it crowd out the definition? Long repeated blocks
   (full example lists, evidence snippets) → **out** or heavily capped.

## Field-by-field rubric

| Field | Embed? | Rationale |
|---|---|---|
| `label` | **INCLUDE** | The trait name — highest signal per token. |
| `definition` | **INCLUDE** | Primary semantic content. The anchor. |
| `definitions[].text` (GENERAL/STRUCTURAL/MECHANISTIC) | **INCLUDE** | Rich, distinguishing prose — the structural "multihelical; 2 layers…" and mechanistic layers are exactly what separates near-neighbours. Prefix each with its `kind`. |
| `synonyms[].synonym_text` | **INCLUDE** | Alternate names broaden lexical coverage; cheap, high-value. |
| `trait_axis`, `trait_category` | **INCLUDE (spelled out)** | Coarse semantic bucket ("ptm site (sequence trait)"), already done via `human_cat`. |
| `sequence_pattern` (regex / motif) | **INCLUDE** | A PROSITE pattern like `C-x(2)-C-x(4)-H` **defines** the class; its token structure is discriminative. Include the regex/consensus text. |
| `secondary_structure_representations` (descriptive parts) | **INCLUDE (text only)** | Fold/topology words are semantic; drop any bare ids. |
| `chemical_participants` (ChEBI **names** / roles) | **INCLUDE names** | "ATP", "substrate", "cofactor" are semantic. Exclude the bare `CHEBI:` ids. |
| `evolutionary_scope` (taxon_scope, method words) | **INCLUDE text** | Short descriptive tokens; skip numeric prevalence. |
| `identifier` (the record's own CURIE) | **INCLUDE** | Opaque alone, but siblings share its hierarchical prefix (`ECOD:F.1.1.1.3`/`…1.4` → `F.1.1.1`), so it clusters same-source / same-subtree traits by co-occurrence. Still the row key in `ids.json` too. |
| `parent_traits` | **INCLUDE (the CURIEs)** | All children of a group share the **exact** parent id — the strongest within-source clustering token. (The parent's label is a bonus if cheap to resolve, but the shared CURIE alone already works.) |
| `xrefs` / `mapped_xrefs` | **INCLUDE, capped** | Related traits are grounded to the **same** `GO:…`/`EC:…`/`InterPro:…`/`PDB:…`; the shared token pulls them together regardless of whether the CURIE is "semantic". Do **not** prefix-filter — an audit showed 85% are structural accessions, and those are exactly the source/category-similarity signal. Cap (~16 total with the id + parents) for the window. |
| `trait_relations` | **CONDITIONAL** | The `predicate` (member_of/part_of) is signal; the object CURIE overlaps parent_traits. |
| `structural_geometry_representations` | **CONDITIONAL** | `structure_ref: PDB:4ION` is mostly per-record → low sharing; include only if members are shared across the group. Descriptive fold text → in. |
| `canonical_examples[].sequence` and the whole example block | **EXCLUDE** | **Per-protein instances**: sequences (long, dominate the window) and `protein_id`/`taxon_*`/`sequence_length`/`fetched_at` are **unique to one protein — never shared between class-level traits**, so they add noise, not clustering. This is the canonical thing to strip. |
| `evidence` (DOI/PMID + snippet) | **EXCLUDE** | Provenance, not identity. A verbatim snippet risks leaking example-specific wording that pulls unrelated records together. |
| `definition_source`, `license`, `term_kind`, `mapping_status` | **EXCLUDE** | Metadata / near-constant → zero discriminative value. |

## Empirical audit (data-drive the borderline calls)

Rules of thumb are a start; measure before committing a field. For each candidate
field compute **coverage** (too rare → not worth wiring), **cardinality /
uniqueness** (near-constant → boilerplate; near-unique → discriminative),
**mean token length** (window cost), and an **opaque-id ratio** (share of values
that are bare CURIEs/accessions → model-noise).

```bash
python3 - <<'PY'
import os, re, json, collections
FIELDS = ["definition", "sequence_pattern", "license", "term_kind"]  # extend
OPAQUE = re.compile(r'^[A-Za-z][\w.]*:[\w.:-]+$|^cd\d+$|^[A-Za-z]{2}\d{5,}$')
stat = {f: {"n": 0, "vals": collections.Counter(), "len": 0, "opaque": 0} for f in FIELDS}
tot = 0
for root, _, files in os.walk("data/traits"):
    for fn in files:
        if not fn.endswith(".yaml"): continue
        tot += 1
        t = open(os.path.join(root, fn), encoding="utf-8").read()
        for f in FIELDS:
            # folded/literal block (>- , |-) first, else an inline scalar that
            # is NOT just a block marker
            m = (re.search(rf'(?m)^{f}:[ \t]*[>|]-?\s*\n((?:[ \t]+.*\n)+)', t)
                 or re.search(rf'(?m)^{f}:[ \t]+(?![>|]\s*$)(.+)$', t))
            if not m: continue
            v = " ".join(m.group(1).split())
            s = stat[f]; s["n"] += 1; s["vals"][v[:40]] += 1
            s["len"] += len(v.split())
            if OPAQUE.match(v): s["opaque"] += 1
for f, s in stat.items():
    n = s["n"] or 1
    print(f"{f:28} cov {100*s['n']//tot:>3}%  uniq {len(s['vals'])/n:.2f}  "
          f"avg_tok {s['len']//n:>4}  opaque {100*s['opaque']//n:>3}%")
PY
```

Read it as: **high coverage + high uniqueness + low opaque% + modest length =
INCLUDE**; **near-constant (uniq→0) or high opaque% = EXCLUDE**; long + rare =
skip.

## Applying it

The decisions live in `load_corpus()` in `scripts/embed_records.py` (the `parts`
list it joins per record). To change what is embedded:

1. Ensure the field is **projected into the docs shards / detail sidecars** by
   `build_docs_index.py` (embed_records reads the projection, not the YAML) — e.g.
   `sequence_pattern` and `definitions` need a projection key before they can be
   embedded.
2. Add/remove the corresponding `parts.append(...)` in `load_corpus`, following
   the rubric (spell out coded values; cap and prefix-filter groundings; never
   append example sequences).
3. **Re-embed and re-index:** `embed_records` → `embed_neighbors` → `embed_map`
   → `just build-docs`. Embedding is the dominant compute (see
   `research/tool-value-analysis.md`), so batch field changes and re-run once.

## Best practices

1. **The definition (+ layered definitions) should dominate the vector.** Order
   `parts` so label + definition come first; keep everything else short so the
   512-token window is spent on meaning.
2. **Spell out coded *category* fields, but keep *identifiers*.** `human_cat`
   turns `SEQ_PTM_SITE` into "ptm site" — do that for enum-like fields. But keep
   the record's own id, its parents, and its xref CURIEs: their **shared** tokens
   cluster same-source / same-subtree traits (a bare `ECOD:F.1.1.1.x` is signal
   *because* siblings share the prefix).
3. **Keep groundings; cap, don't prefix-filter.** Related traits share the same
   `GO:…`/`InterPro:…`/`PDB:…` — that co-occurrence is the within-source
   similarity signal (the 85%-"opaque" xrefs are the point, not noise). Cap the
   id+parents+xrefs bundle (~16) so it doesn't crowd the definition.
4. **Never embed `canonical_examples`.** Especially sequences — they are long and
   **unique to one protein** (never shared between class-level traits), so they
   add noise, not clustering.
5. **Measure, then commit.** Run the audit snippet on any field you're unsure
   about; let coverage/uniqueness/opaque% decide the borderline cases.
6. **Re-embedding is expensive — change fields in a batch**, then re-run the
   whole embed → neighbors → map → build-docs chain once.
