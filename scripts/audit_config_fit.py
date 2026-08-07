"""Which already-curated records would NO config accept today? (#267)

Five records were found one at a time this session sitting under a mechanism their own
definition contradicts -- MecI (#251), pilQ (#254), ahpC (#260), five class D records
(#265), tet(34) (#267). Each was found because some unrelated family happened to get
curated. This asks the question directly.

The question has to be CROSS-family. A first attempt asked it per-family and reported
1,561 "problems", nearly all of them records legitimately curated under their own more
specific family, or one config of a list-form family refusing another's records by design.
Asking "does ANY config of ANY family this record belongs to accept it?" gives 1.

It earned its place immediately: it found 7 PBP records stranded by round 53's own
"fix" (`\bpbp\s?\d` -> `\bpbp\b`, which stopped matching "PBP1"). Promotion is
idempotent and never re-checks what it already wrote, so nothing else would have surfaced
them.

Exit code is always 0 -- a stranded record is a question, not a failure.
"""
import pathlib
import re
import sys
import collections
sys.path.insert(0, 'scripts')
import promote_family_drafts as P
import enrich_aro_resistance as E

terms = E.parse_obo(E.OBO)
fams = list(P.FAMILY_SNIPPETS)
orphan = collections.Counter()
examples = []
scanned = 0
for p in pathlib.Path('data/traits/function/resistance/aro').rglob('*.yaml'):
    text = p.read_text(encoding='utf-8')
    if 'graph_id: resistance\n' not in text:
        continue
    m = re.search(r'^identifier:\s*(ARO:\S+)', text, re.M)
    if not m:
        continue
    ident = m.group(1)
    label = terms.get(ident, {}).get('name', '')
    anc = E.ancestry(terms, ident)
    # families this record could belong to
    cands = [f for f in fams if f in anc or f == ident]
    if not cands:
        continue                     # curated by a config no longer keyed here
    scanned += 1
    if any(P.config_for(f, ident, label, text) is not None for f in cands):
        continue
    orphan[cands[0]] += 1
    if len(examples) < 6:
        examples.append((ident, label[:44], cands[0]))
print(f"curated records under a known family: {scanned:,}")
print(f"accepted by NO config of any of their families: {sum(orphan.values()):,}")
for f, n in orphan.most_common(6):
    print(f"   {n:>5}  under {f} ({terms.get(f,{}).get('name','?')[:44]})")
for e in examples:
    print("   eg", e)
