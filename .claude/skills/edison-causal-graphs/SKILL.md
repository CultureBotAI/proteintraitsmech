---
name: edison-causal-graphs
description: Use this skill to research and write evidence-backed causal / mechanism graphs (`causal_graphs`) onto ProteinTraitRecords — one record (or one tight mechanism) at a time — prioritizing mechanism-rich sources (M-CSA catalytic mechanisms first, then ARO resistance mechanisms, active/binding/metal sites). It applies the Edison method (many small literature-verified experiments, a `research/` report every round) to CAUSAL MECHANISM rather than to source discovery (`edison-deep-research`) or definitions (`edison-trait-definitions`). Every `CausalEdge` gets a grounded node pair, an RO predicate, and at least one `EvidenceItem` with a PMID/DOI + verbatim snippet. Trigger when asked to add/curate causal graphs, write mechanism graphs, populate `causal_graphs`, or "deep research the mechanism for record/source X".
---

# Edison Causal Graphs

Third sibling of [[edison-deep-research]] (finds *sources*) and
[[edison-trait-definitions]] (writes *definitions*). This one attaches the
**evidence-backed causal mechanism** — a directed `causal_graphs` block — to
records that carry mechanism structure. "Edison" = many small literature-verified
experiments, keep only what a citation supports, and **write a report every round**.

The corpus is **greenfield for mechanism**: as of 2026-07 **0 records** carry
`causal_graphs`. So this skill establishes the pattern, not patches it. Adding a
graph is the curation act that flips a record `SEEDED → REVIEWED` (README step 3).

## The one rule that is never skipped

> **Every round produces a markdown file under `research/`.** Name it
> `research/causal-graphs-round<N>.md` (increment per round, never overwrite). The
> ranked target table + the per-graph node/edge design + the literature that backs
> each edge are the deliverable — the YAML is downstream of the report.

## The hard schema contract (verify against the schema, don't guess)

`causal_graphs:` is a list of `CausalGraph`:
- **CausalGraph** — `graph_id` (req, stable local id), `title`, `description`,
  `nodes` (req, ≥1), `edges` (req, ≥1).
- **CausalNode** — `node_id` (req, local id used by edges), `label` (req),
  `node_type` (req; `CausalNodeTypeEnum`: PROTEIN, DOMAIN, MOTIF, RESIDUE, PTM,
  LIGAND, NUCLEIC_ACID, CHEMICAL, PATHWAY, MOLECULAR_FUNCTION, BIOLOGICAL_PROCESS,
  CELLULAR_LOCALIZATION, PHENOTYPE, DISEASE, TRAIT, STATE, QUALITY,
  ENVIRONMENTAL_FACTOR, EXPERIMENTAL_FACTOR, OTHER), `grounding` (preferred CURIE),
  `xrefs`, `description`.
- **CausalEdge** — `subject` (req, a local `node_id`), `predicate` (req, label or
  CURIE), `predicate_id` (RO CURIE, e.g. RO:0002211), `object` (req, a local
  `node_id`), `description`, **`evidence` (REQUIRED, ≥1 `EvidenceItem`)**.
- **EvidenceItem** — `reference` (req; `PMID:…`, `DOI:…`, a database CURIE, or a
  URL), `snippet` (the **verbatim** supporting quote), `notes`.

**The non-negotiable:** every mechanism edge must carry ≥1 `EvidenceItem` — closed-
mode `just validate` fails an evidence-less edge. `subject`/`object` are **local
`node_id`s**, not CURIEs (grounding lives on the node). Ground the node, cite the
edge.

## What a good causal edge is (score every edge)

1. **Cited, with a verbatim snippet.** `reference` is a real PMID/DOI (or the M-CSA
   / Rhea / ARO entry), and `snippet` is a quote from *that* source that states the
   claim. No snippet you can't paste from the source → the edge is not ready.
2. **Grounded nodes.** Prefer real CURIEs: PR (proteins), GO (MF/BP/CC), CHEBI
   (ligands/substrates/products), MOD/PSI-MOD (PTMs), SO (residues/motifs), HP /
   MONDO (phenotype/disease). Label-only draft nodes are allowed in v1 but flag them.
3. **RO predicate.** Put the relation ontology CURIE in `predicate_id` (e.g.
   RO:0002211 regulates, RO:0002212/RO:0002213 negatively/positively regulates,
   RO:0002233 has input, RO:0002234 has output, RO:0002327 enables, RO:0002436
   molecularly interacts with, RO:0002411 causally upstream of); a readable label
   in `predicate`.
4. **Mechanistically specific + directional.** "Ser68 nucleophilically attacks the
   β-lactam carbonyl → acyl-enzyme intermediate," not "enzyme acts on substrate."
   Subject upstream, object downstream; the arrow means *because of*.
5. **In scope for the record.** The graph explains *this trait's* mechanism
   (a catalytic-site record's chemistry; a resistance record's resistance route) —
   not the protein's whole biography. One record, one focused mechanism.

## Where the mechanism content comes from (prioritized)

| Source | What it gives | Route to a graph |
|--------|---------------|------------------|
| **M-CSA** (`data/traits/structure/active_site/mcsa/`, 1,003 records) | **explicit stepwise catalytic mechanisms** with residue roles, arrow-pushing, and per-step literature references | the flagship seed — each step = a RESIDUE/LIGAND edge; M-CSA's own reference is the citation |
| **CARD / ARO** (`…/resistance/aro/`, ~7.4k) | resistance *mechanism* + drug class + determinant | determinant → mechanism → resistant phenotype edges (RO regulates / causally upstream of) |
| **UniProt / BioLiP / MetalPDB active/binding/metal sites** | which residues bind ligand/metal | RESIDUE —molecularly interacts with→ LIGAND, backed by the site's PDB + UniProt evidence |
| **Rhea / EC / Reactome** | reaction chemistry (substrate → product) | CHEMICAL(substrate) —has input/has output→ MOLECULAR_FUNCTION → CHEMICAL(product) |

Start with **M-CSA** — it is the one source that already encodes the causal steps
and their citations, so the graph is a *transcription-with-grounding* task, not an
invention. Verify each step's residue numbering and reference on the M-CSA entry
page (and the cited paper) before writing the edge.

## Protocol

1. **Read prior rounds** (`research/causal-graphs-round*.md`). Carry forward the
   open targets; don't redo a finished record.
2. **Enumerate the gap** (audit below): rank mechanism-rich records that have **no**
   `causal_graphs` yet, preferring those that already carry `evidence` / a cited
   mechanism (M-CSA first).
3. **Pick ONE record** (or one tight mechanism within it). Pull its definition,
   `xrefs`, `canonical_examples`, and the source's mechanism page.
4. **Research the mechanism.** Read the M-CSA entry / the cited PMIDs
   (`WebFetch`/`WebSearch`); for each causal step capture the claim **and a verbatim
   snippet** you can quote. Ground every participant (residue, ligand, product,
   function) to a CURIE.
5. **Design the graph** — list nodes (id, label, type, grounding) then edges
   (subject→object, RO predicate, ≥1 evidence with snippet). Draw it in the report
   first; only then write YAML.
6. **Write the YAML** onto the record's `causal_graphs:` (skeleton below). Flip
   `mapping_status: SEEDED → REVIEWED` and add a `curation_history` event.
7. **Validate + gate.** `just validate <file>` (closed-mode — enforces the required
   evidence + CURIE patterns). Run `just audit-graphs` if the audit script exists;
   if `scripts/audit_causal_graphs.py` is still absent (it is referenced by the
   recipe but not yet written), say so and lean on `just validate` — do **not**
   claim a structural audit that didn't run.
8. **Write the round report** (template below). No report → the round didn't happen.

## Enumerate the gap (reproducible audit)

```bash
python3 - <<'PY'
import os, re, collections
agg = collections.defaultdict(lambda: {"n": 0, "graph": 0, "ev": 0})
for root, _, fs in os.walk('data/traits'):
    for fn in fs:
        if not fn.endswith('.yaml'): continue
        t = open(os.path.join(root, fn), encoding='utf-8').read()
        s = (re.search(r'^identifier:\s*([A-Za-z0-9_]+):', t, re.M) or [0, '?'])[1].lower()
        c = (re.search(r'^trait_category:\s*(\S+)', t, re.M) or [0, '?'])[1]
        v = agg[(s, c)]; v["n"] += 1
        v["graph"] += ('causal_graphs:' in t)
        v["ev"] += re.search(r'(?m)^evidence:', t) is not None
# mechanism-rich sources worth a graph, ranked by how many still lack one
RICH = {'mcsa', 'aro', 'card'}
rows = [(v["n"] - v["graph"], s, c, v["n"], v["graph"], v["ev"])
        for (s, c), v in agg.items()
        if (s in RICH or 'ACTIVE_SITE' in c or 'BINDING' in c or 'METAL' in c
            or 'RESISTANCE' in c) and v["n"] - v["graph"] > 0]
rows.sort(reverse=True)
print(f"{'source':<12}{'category':<24}{'n':>7}{'w/graph':>8}{'w/ev':>6}  (no-graph)")
for miss, s, c, n, g, ev in rows[:25]:
    print(f"{s:<12}{c:<24}{n:>7,}{g:>8}{ev:>6}{miss:>10,}")
PY
```

The top rows (M-CSA `STRUCT_ACTIVE_SITE`, ARO `FUNC_RESISTANCE`) are the targets:
mechanism-rich, high `evidence` coverage, zero graphs.

## CausalGraph YAML skeleton (the exact shape to write)

```yaml
causal_graphs:
  - graph_id: catalysis
    title: Catalytic mechanism of <trait>
    description: >-
      Stepwise mechanism from M-CSA entry <MCSA:id>; residue numbering on
      <UniProtKB:acc>.
    nodes:
      - node_id: ser68
        label: catalytic serine (Ser68)
        node_type: RESIDUE
        grounding: UniProtKB:P62593     # + xrefs: [SO:0001104] for "catalytic residue"
      - node_id: substrate
        label: β-lactam substrate
        node_type: CHEMICAL
        grounding: CHEBI:35627
      - node_id: acyl_enzyme
        label: acyl-enzyme intermediate
        node_type: STATE
    edges:
      - subject: ser68
        predicate: nucleophilic attack on
        predicate_id: RO:0002436          # molecularly interacts with
        object: substrate
        description: Ser68 Oγ attacks the β-lactam carbonyl, opening the ring.
        evidence:
          - reference: PMID:xxxxxxx
            snippet: "Ser70 (Ambler) acts as the catalytic nucleophile, attacking
              the carbonyl carbon of the β-lactam ring to form an acyl-enzyme."
            notes: M-CSA MCSA:xx step 1; Ambler Ser70 = UniProt Ser68 via SIFTS.
      - subject: substrate
        predicate: is converted to
        predicate_id: RO:0002234          # has output
        object: acyl_enzyme
        evidence:
          - reference: DOI:10.xxxx/xxxx
            snippet: "…covalent acyl-enzyme intermediate…"
```

(Numbering note: cite the residue in the frame the record uses — reconcile
literature/PDB numbering to the UniProt frame via SIFTS, per
`research/sequence-structure-function-alignment-analysis-1.md`.)

## Report template

```markdown
---
topic: causal-graphs
round: <N>
date: <YYYY-MM-DD>
target: <source>/<trait_category> — <record identifier>
prior_round: causal-graphs-round<N-1>.md
---

# Causal graphs — Round <N>: <record>

## Gap (from the audit)
| source | category | n | w/graph | w/ev |
...

## Mechanism (researched)
<the stepwise mechanism in prose, each step with its citation + verbatim snippet>

## Graph design
- nodes: id · label · type · grounding  (×K)
- edges: subject → [RO predicate] → object · evidence(ref + snippet)  (×M)

## Provenance
records touched: N · edges written: M · all edges cited: yes/no · status → REVIEWED

## Open questions
<ambiguous steps, ungrounded nodes, numbering caveats>
```

## Best practices

1. **One mechanism per round.** A focused, fully-cited 4–8-edge graph beats a
   sprawling half-evidenced one. Finish and validate before the next.
2. **Cite the edge, ground the node.** Never write an edge you can't attach a
   verbatim snippet to; never leave a participant as a bare label if a CURIE exists.
3. **Transcribe M-CSA first, invent nothing.** M-CSA already gives the steps,
   roles, and references — the task is grounding + RO predicates, not novel biology.
4. **RO predicates, directional edges.** Upstream `subject` → downstream `object`;
   put the RO CURIE in `predicate_id`.
5. **Flip status + audit-trail.** Adding a graph makes the record REVIEWED; append a
   `curation_history` CurationEvent (`llm_assisted: true`).
6. **Validate closed-mode; don't over-claim the audit.** `just validate` is the gate
   that runs today; `just audit-graphs` needs `scripts/audit_causal_graphs.py`,
   which is currently missing — flag it rather than imply it ran.
7. **Write the report even for one graph.** The Edison rule: no `research/` file →
   the round didn't happen.
