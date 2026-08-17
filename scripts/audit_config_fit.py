r"""Which already-curated records would NO config accept today? (#267)

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

A stranded record is a QUESTION, not a failure: any number of them exits 0. What does not
exit 0 is a run that could not ask the question -- no release, or no records found. Those
are the two ways this printed "accepted by NO config: 0" while having examined nothing,
which reads as a clean corpus and is the norm #418 and #432 exist to enforce.

EVERYTHING BELOW LIVES IN `main()`, and that is the point rather than tidiness. This file
used to run the whole cross-family sweep AT IMPORT TIME, so `parse_obo` fired the moment
anything touched it -- which `test_every_seeder_is_importable` does, by design, for every
script in this directory. `data/raw/` is gitignored, so that test raised FileNotFoundError
on EVERY CI run (#469), and on a machine that did have the release it silently ran a 7,211
file sweep inside the test suite instead of importing a module.

EVERY PATH IS RESOLVED FROM THE MODULE, not from the process's cwd. The corpus glob was
the literal string 'data/traits/function/resistance/aro', so running this from anywhere
but the repo root globbed nothing and printed

    curated records under a known family: 0
    accepted by NO config of any of their families: 0

and exited 0 -- indistinguishable from a clean sweep, and the failure this file's own
sibling `audit-reproducible` is gated against one recipe away. It uses `E.ARO_DIR` now,
which is the same path, absolute, and already the source of truth.

(The `sys.path.insert(0, 'scripts')` it also carried was NOT a real bug -- Python already
puts a script's own directory on `sys.path[0]`, so the sibling imports resolved from any
cwd. It is resolved from `__file__` for consistency, not to fix anything.)
"""
import pathlib
import re
import sys
import collections

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import promote_family_drafts as P
import enrich_aro_resistance as E


def main() -> int:
    if not E.OBO.exists():
        print(f"FAIL: {E.OBO} is absent (data/raw is gitignored); run `just fetch-aro`.")
        return 1
    terms = E.parse_obo(E.OBO)
    fams = list(P.FAMILY_SNIPPETS)
    orphan = collections.Counter()
    examples = []
    scanned = 0
    for p in E.ARO_DIR.rglob('*.yaml'):
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
    if not scanned:
        # A sweep that examined nothing must not print a zero that reads as "all clean".
        print(f"FAIL: no curated records with a known family under {E.ARO_DIR}. "
              f"Nothing was examined, so the 0 below would be meaningless.")
        return 1
    print(f"curated records under a known family: {scanned:,}")
    print(f"accepted by NO config of any of their families: {sum(orphan.values()):,}")
    for f, n in orphan.most_common(6):
        print(f"   {n:>5}  under {f} ({terms.get(f,{}).get('name','?')[:44]})")
    for e in examples:
        print("   eg", e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
