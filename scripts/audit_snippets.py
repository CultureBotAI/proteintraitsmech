#!/usr/bin/env python3
r"""Does every cited snippet actually appear in the source it names? (#365)

Every `EvidenceItem` claims a `snippet` is verbatim from its `reference`. Nothing checked
that. This checks the part that CAN be checked offline.

SCOPE, stated plainly because the first version of this docstring overclaimed it: this
catches **#400's class** -- a snippet under the wrong ARO/KB CURIE. It does NOT catch #348
(a sentence attributed to the wrong PMID) or #382 (evidence that survived a removal),
because both are PMID-attributed and PMIDs cannot be verified offline. 40,270 of 69,749
ARO evidence items -- 58% -- are PMIDs or DOIs this tool never checks, and 7,119 of 7,211
promoted ARO records carry one. **The dominant citation vector in this corpus sits outside
this gate.**

What no gate did before this, and still does not for PMIDs:

  * `--verify` (#201) checks that a cited CURIE RESOLVES to a record;
  * `audit-graphs` checks that a snippet is PRESENT on the edge;
  * `validate` treats snippets as opaque strings.

None of them compares a snippet to its source. This does, for on-disk sources.

Only references that are resolvable ON DISK are checked -- ARO ids against
`data/raw/aro/aro.obo`, KB CURIEs against their own record's definition. PMIDs and DOIs are
skipped and counted: they are valid citations we cannot verify offline, and treating them
as failures would drown the real signal (7,119 of 7,211 promoted ARO records carry one).

An ARO snippet may legitimately come from the term's `def:` OR from one of its
`relationship:` lines -- `_drug_assertion` quotes the latter -- so both are searched.

Exit code is 0 unless --strict, or a gate is breached.

TWO gates, because a scalar count is not enough. `--max N` pins a ceiling, and a ceiling
masks a SWAP: #411 demonstrated fixing one pre-existing mismatch while reintroducing #400
in the same tree, leaving the total unchanged and the gate green. In a repo whose recorded
pathology is four rounds of "a fix produced the defect it was fixing", that is the wrong
shape.

`--baseline FILE` pins the IDENTITY of every known mismatch -- (record, graph, edge,
reference, snippet), one key per item -- so a new one fails even when an old one is fixed
in the same change. Write it
with --update-baseline, and read the diff it prints: FIXED lines are progress, NEW lines
are the thing this exists to catch.

`--archetypes` (#425) asks a DIFFERENT question, and it is the one everything above is
blind to by construction. Those gates ask "is this quote real?". This one asks "is it
about this record?" -- because a snippet can be verbatim in the term it cites and still be
wrong, when that term is one gene in one organism and the record is neither. carO's
definition sat on 42 permeability records, 2 of them carO, and passed every gate here: it
was a truncation that made it read as generic, and repairing the truncation (#423) is what
exposed it. Reported against a baseline rather than zeroed, because some of these are
legitimate -- an efflux repressor citing the pump it represses is citing the edge's own
object, not misattributing anything.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

try:                                    # 5-10x on this workload; the audit parses 7.4k files
    _Loader = yaml.CSafeLoader
except AttributeError:                  # pure-python fallback
    _Loader = yaml.SafeLoader

ROOT = Path(__file__).resolve().parent.parent
TRAITS = ROOT / "data" / "traits"
OBO = ROOT / "data" / "raw" / "aro" / "aro.obo"

# References we can resolve without network access. Anything else (PMID, DOI, URL) is
# counted as unverifiable rather than failed.
# Prefixes whose text we actually hold: ARO via aro.obo, the rest as KB trait records.
# `UniProtKB`, `CHEBI`, `RHEA`, `EC` and `MCSA` are deliberately ABSENT -- they are cited as
# external identifiers, not as records whose prose we can quote-check. Including them made
# the first run report 127,286 "unresolvable" references as failures, which was the audit's
# bug and not the corpus's.
ON_DISK_PREFIXES = ("ARO", "Pfam", "GO", "CATH", "PROSITE", "NCBIfam", "InterPro",
                    "PANTHER", "HAMAP", "SFLD", "TED", "ECOD")


def _norm(text: str) -> str:
    """Whitespace-insensitive, so a YAML fold does not read as a mismatch."""
    return " ".join(text.split())


def load_obo_stanzas() -> dict[str, str]:
    """ARO id -> the whole stanza body, normalised.

    The stanza is everything until the next `[Term]`/`[Typedef]` header. Searching the
    WHOLE body, not just `def:`, is deliberate: `_drug_assertion` quotes `relationship:`
    lines verbatim and those are legitimate sources.
    """
    if not OBO.exists():
        return {}
    out: dict[str, str] = {}
    current: str | None = None
    body: list[str] = []
    for line in OBO.read_text(encoding="utf-8").splitlines():
        if line.startswith("["):
            if current:
                out[current] = _norm(" ".join(body))
            current, body = None, []
        elif line.startswith("id: ARO:"):
            current = line[4:].strip()
        elif current:
            body.append(line)
    if current:
        out[current] = _norm(" ".join(body))
    return out


_SHORT_NAME = re.compile(r'synonym: "[^"]*" EXACT CARD_Short_Name')
_IS_A = re.compile(r"is_a: (ARO:\d+)")


def load_obo_facts(obo: dict[str, str]) -> tuple[set[str], dict[str, set[str]]]:
    """(gene-level term ids, id -> direct is_a parents), from the stanzas already loaded.

    "Gene-level" means the term carries a `CARD_Short_Name` synonym. That is CARD's own
    marker for "this term is a named gene or a named organism-specific variant" as opposed
    to a mechanism, family or drug class -- exactly the line #425 is drawn on. Deriving it
    from the release beats a hand-list: the list would go stale on the next `fetch-aro`
    and nothing would say so.
    """
    gene_level = {tid for tid, body in obo.items() if _SHORT_NAME.search(body)}
    parents = {tid: set(_IS_A.findall(body)) for tid, body in obo.items()}
    return gene_level, parents


def ancestors(tid: str, parents: dict[str, set[str]]) -> set[str]:
    """Transitive is_a closure. Iterative and `seen`-guarded: ARO is a DAG, several terms
    have two parents, and a recursive walk over it revisits the shared upper levels once
    per path."""
    out: set[str] = set()
    stack = list(parents.get(tid, ()))
    while stack:
        p = stack.pop()
        if p in out:
            continue
        out.add(p)
        stack.extend(parents.get(p, ()))
    return out


KB_HEAD_BYTES = 8000


def load_kb_definitions(wanted: set[str]) -> dict[str, str]:
    """KB CURIE -> the first KB_HEAD_BYTES of that record's RAW YAML, normalised.

    NOT just its `definition:` -- `label:`, `description:` and `notes:` are in range too,
    so the KB side of this check is laxer than the ARO side. Measured: 5,901 of 12,544
    KB-side passes match outside the definition block, mostly the `label:` line. Stated
    because the first version's docstring said "definition" and did not do that.

    Collect-then-resolve: indexing all 429k records' heads to answer a few hundred
    lookups reads ~1.7 GB. This walks once and keeps only what was asked for.
    """
    if not wanted:
        return {}
    out: dict[str, str] = {}
    ident = re.compile(r'^identifier:\s*"?(\S+?)"?\s*$', re.M)
    # Most KB CURIEs encode their own filename (Pfam:PF00297 -> ...-pf00297.yaml), so try
    # a targeted glob before falling back to the 429k-record walk. The walk was ~60s per
    # invocation and made the #424 boundary test 8.7 minutes.
    # ONE filename index, not one rglob per reference. The per-ref glob resolved only
    # 34 of 50 -- all 14 CATH and 2 PROSITE refs miss, because their filenames do not end
    # in the CURIE local part -- so `remaining` never emptied and the 429k-file fallback
    # ran anyway. The glob phase cost 21s to shorten a 56s walk; the index costs ~1s
    # (#428).
    remaining = set(wanted)
    index: dict[str, list[Path]] = defaultdict(list)
    for path in TRAITS.rglob("*.yaml"):
        index[path.stem.lower()].append(path)
    for ref in sorted(wanted):
        local = ref.split(":", 1)[-1].lower()
        for stem, paths in index.items():
            if not stem.endswith(local):
                continue
            for cand in paths:
                head = cand.read_text(encoding="utf-8")[:KB_HEAD_BYTES]
                m = ident.search(head)
                if m and m.group(1) == ref:
                    raw = cand.read_text(encoding="utf-8")
                    out[ref] = _norm(raw if len(raw) > KB_HEAD_BYTES else head)
                    remaining.discard(ref)
                    break
            if ref in out:
                break
    if not remaining:
        return out
    for path in TRAITS.rglob("*.yaml"):
        raw = path.read_text(encoding="utf-8")
        head = raw[:KB_HEAD_BYTES]
        m = ident.search(head)
        if m and m.group(1) in remaining and m.group(1) not in out:
            # A record longer than the cut would silently turn real quotes into
            # "mismatches". Read the whole file for those rather than guess.
            out[m.group(1)] = _norm(raw if len(raw) > KB_HEAD_BYTES else head)
            if len(out) == len(wanted):
                break
    return out


def iter_evidence(paths):
    """(path, graph_id, subject, object, reference, snippet, record identifier) per item.

    The identifier is there for the archetype check (#425), the only question that needs
    to know whose record a snippet is sitting on.

    #436: this said the identifier was placed LAST "so the six-field unpacking every
    existing caller does keeps working". It does not -- appending a seventh element raises
    `too many values to unpack`, and every caller in this module was in fact changed. Note
    also that `bad` in `main()` is a seven-tuple too, whose last field is `why` rather than
    an identifier; the two shapes are not interchangeable.
    """
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if "causal_graphs:" not in text:
            continue
        try:
            doc = yaml.load(text, Loader=_Loader)
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        ident = doc.get("identifier")
        for graph in doc.get("causal_graphs") or []:
            for edge in graph.get("edges") or []:
                for ev in edge.get("evidence") or []:
                    ref, snip = ev.get("reference"), ev.get("snippet")
                    if ref and snip:
                        yield (path, graph.get("graph_id"), edge.get("subject"),
                               edge.get("object"), ref, snip, ident)


def _rel(path: Path) -> str:
    """Repo-relative where possible, absolute otherwise.

    `relative_to(ROOT)` raised for any corpus outside the repo, which made the audit
    uncrashable-in-practice but untestable -- the first fixture test hit it immediately
    (#418).
    """
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def baseline_key(rel_path: str, graph_id, subject, obj, reference: str, snippet: str) -> str:
    """One key per EVIDENCE ITEM. Keyed on the edge, not on (record, reference, snippet):
    that collapsed 174 items into 71 and let a record gain a duplicate bad edge unseen."""
    return f"{rel_path}|{graph_id}|{subject}->{obj}|{reference}|{_norm(snippet)}"


def diff_baseline(current: dict[str, int], known: dict[str, int]) -> tuple[list, list]:
    """(fixed, new) by COUNT, so a duplicated bad edge is new even at the same key.

    Extracted so the swap proof is a fixture test rather than a second full-corpus walk --
    the two corpus tests cost 127s and both skip in CI, where data/raw is gitignored (#416).
    """
    new = sorted(k for k in current if current[k] > known.get(k, 0))
    fixed = sorted(k for k in known if current.get(k, 0) < known[k])
    return fixed, new


def _load_baseline(path: Path) -> dict[str, int]:
    """Baseline as {key: count}, tolerating the earlier list-of-keys form."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: 1 for k in data} if isinstance(data, list) else data


def iter_config_snippets():
    """(family, field, reference, snippet) for every literal in FAMILY_SNIPPETS.

    The data-side check above reads RECORDS. Nothing read the CONFIGS, which is how #423
    shipped two corrupt literals -- a spliced class-D snippet and a `mas` one duplicated by
    Python's implicit string concatenation -- past lint, 768 tests, audit-graphs,
    --verify-all and this audit's own data side. Both were latent only because the promoter
    skips existing records; the next new record would have written them as evidence (#424).
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import promote_family_drafts as promote

    def _items(value, fallback):
        """A field is a bare string, a list of evidence dicts, or a dict of them."""
        if isinstance(value, str):
            yield promote._true_source(value, fallback), value
        elif isinstance(value, dict):
            for v in value.values():
                yield from _items(v, fallback)
        elif isinstance(value, (list, tuple)):
            for v in value:
                if isinstance(v, dict) and "snippet" in v:
                    yield v.get("reference", fallback), v["snippet"]
                else:
                    yield from _items(v, fallback)

    for family, entry in promote.FAMILY_SNIPPETS.items():
        for cfg in (entry if isinstance(entry, list) else [entry]):
            fallback = cfg.get("reference", "")
            for field in ("mech", "mech_res", "det_res", "res_drug"):
                for ref, snip in _items(cfg.get(field), fallback):
                    if ref and snip:
                        yield family, field, ref, snip
            for edge in cfg.get("extra_edges", ()):
                for ev in edge.get("evidence", ()):
                    if ev.get("reference") and ev.get("snippet"):
                        yield family, "extra_edges", ev["reference"], ev["snippet"]
            pt = cfg.get("protein_traits") or {}
            for key, val in pt.items():
                if isinstance(val, tuple) and len(val) == 4:
                    yield family, f"protein_traits[{key}]", val[0], val[3]


def config_key(family: str, field: str, reference: str, snippet: str) -> str:
    """One key per config literal, so the config gate gets #411's identity pin too.

    It shipped ceiling-only, which is the argument #411 makes against a bare count -- and
    verified: fixing Pfam:PF04563 while introducing a new corrupt literal leaves 13 and a
    ceiling passes it (#428).
    """
    return f"{family}|{field}|{reference}|{_norm(snippet)}"


def audit_configs(show: int, obo=None, kb=None) -> tuple[int, dict[str, int]]:
    """Every config literal must be verbatim in the source it names.

    Returns (failures, {key: count}). `obo`/`kb` are passed in by main() so the two sides
    share one resolution pass: the config `wanted` set is 50 refs and the data side's is
    53, overlapping 50, and re-resolving cost 26s of the 60s recipe (#428).
    """
    items = list(iter_config_snippets())
    if obo is None or kb is None:
        wanted = {r for _f, _k, r, _s in items if r.split(":")[0] in ON_DISK_PREFIXES
                  and not r.startswith("ARO:")}
        obo, kb = load_obo_stanzas(), load_kb_definitions(wanted)
    checked = unresolved = skipped = 0
    bad, counts = [], defaultdict(int)
    for family, field, ref, snip in items:
        if ref.split(":")[0] not in ON_DISK_PREFIXES:
            skipped += 1
            continue
        body = obo.get(ref) if ref.startswith("ARO:") else kb.get(ref)
        if body is None:
            unresolved += 1
            continue
        checked += 1
        if _norm(snip) not in body:
            bad.append((family, field, ref, snip))
            counts[config_key(family, field, ref, snip)] += 1
    print(f"\nconfig literals:           {len(items):,}")
    print(f"  checked against disk:    {checked:,}")
    print(f"  skipped (PMID/DOI/URL):  {skipped:,}  -- valid, not verifiable offline")
    print(f"  not on disk (not a fail): {unresolved:,}")
    print(f"  NOT VERBATIM:            {len(bad):,}")
    for family, field, ref, snip in bad[:show]:
        print(f"  {family}  {field}  cites {ref}")
        print(f"    {_norm(snip)[:110]}")
    return len(bad), dict(sorted(counts.items()))


def archetype_key(rel_path: str, graph_id, subject, obj, reference: str,
                  snippet: str) -> str:
    """One key per evidence item, snippet included -- like the other two baselines.

    #434: it shipped WITHOUT the snippet, on the reasoning that the quote here is already
    verbatim so including it would make every rewording read as a new finding. That
    reasoning applies just as well to the other two baselines, which include it anyway,
    and it left a hole of exactly the shape this module exists to close (#411):

      an edge in the baseline cites gene-level ARO:3003808 quoting a sentence that is
      legitimately about it; swap that for a DIFFERENT sentence from the same term, about
      Acinetobacter and Moraxella, and the count at the key is unchanged, so the identity
      gate reports 0 NEW -- while the data-side gate stays green, because the new sentence
      is also verbatim in ARO:3003808.

    The cost is the one anticipated: rewording a blessed snippet shows as 1 FIXED + 1 NEW.
    That is diff noise a human reads, which is the trade the other two already make.
    """
    return f"{rel_path}|{graph_id}|{subject}->{obj}|{reference}|{_norm(snippet)}"


def audit_archetypes(items, obo: dict[str, str], show: int) -> tuple[int, dict[str, int]]:
    """Evidence citing a GENE-LEVEL ARO term that is neither this record's own term nor
    one of its ancestors (#425).

    Not a quote check -- every one of these snippets IS verbatim in the term it names,
    which is why `--max 0` on the data side says nothing about them. The question is
    relevance: carO's definition names *Acinetobacter baumannii* and the carO gene, and
    sat on 42 permeability records of which 2 are carO. #423 did not cause that; it
    *revealed* it, by restoring the clause the truncation had removed.

    ANCESTORS ARE NOT FLAGGED, deliberately. Quoting a parent term on a child is the
    normal, correct shape for this corpus -- a variant record inheriting its family's
    mechanism claim -- and flagging it would bury the real signal under thousands of items.

    Returns (failures, {key: count}). Reports rather than judges: some of these are fine
    (an efflux repressor citing the pump it represses is citing the edge's own object),
    which is why this gets a BASELINE and not a hard zero.
    """
    gene_level, parents = load_obo_facts(obo)
    bad, counts = [], defaultdict(int)
    anc_cache: dict[str, set[str]] = {}
    for path, gid, subj, obj, ref, snip, ident in items:
        if not ref.startswith("ARO:") or ref == ident or ref not in gene_level:
            continue
        if not isinstance(ident, str) or not ident.startswith("ARO:"):
            continue
        if ident not in anc_cache:
            anc_cache[ident] = ancestors(ident, parents)
        if ref in anc_cache[ident]:
            continue
        bad.append((path, gid, subj, obj, ref, snip, ident))
        counts[archetype_key(_rel(path), gid, subj, obj, ref, snip)] += 1

    by_ref: dict[str, int] = defaultdict(int)
    recs: dict[str, set] = defaultdict(set)
    for path, _g, _s, _o, ref, _sn, _i in bad:
        by_ref[ref] += 1
        recs[ref].add(path)
    print(f"\narchetype reuse (#425):    {len(bad):,} evidence item(s) across "
          f"{len({b[0] for b in bad}):,} records, {len(by_ref):,} cited gene-level terms")
    for ref, n in sorted(by_ref.items(), key=lambda kv: -kv[1])[:show]:
        print(f"  {n:>5}  {ref}  on {len(recs[ref]):,} record(s)")
    return len(bad), dict(sorted(counts.items()))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", default="", help="restrict to a subtree of data/traits")
    ap.add_argument("--traits-root", default="",
                    help="override data/traits (for testing against a fixture corpus, #418)")
    ap.add_argument("--obo", default="", help="override data/raw/aro/aro.obo (#418)")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any snippet mismatches")
    ap.add_argument("--max", type=int, default=None,
                    help="exit 1 if mismatches exceed N (pins a known backlog)")
    ap.add_argument("--show", type=int, default=12, help="how many examples to print")
    ap.add_argument("--configs-only", action="store_true",
                    help="skip the record walk entirely; check only config literals. The "
                         "config tests do not assert on the data side and paid ~50s a call "
                         "for it (#428).")
    ap.add_argument("--configs", action="store_true",
                    help="also check FAMILY_SNIPPETS literals against their cited source (#424)")
    ap.add_argument("--max-configs", type=int, default=None,
                    help="exit 1 if config-literal failures exceed N (a CEILING)")
    ap.add_argument("--config-baseline", default="",
                    help="pin the IDENTITY of each known config-literal failure, so a swap "
                         "fails even at an unchanged count (#411's argument, #428)")
    ap.add_argument("--archetypes", action="store_true",
                    help="also report evidence citing a GENE-LEVEL ARO term that is not "
                         "this record's own term or an ancestor of it (#425). A different "
                         "question from the rest of this script: those snippets ARE "
                         "verbatim in the term they name.")
    ap.add_argument("--max-archetypes", type=int, default=None,
                    help="exit 1 if archetype-reuse items exceed N (a CEILING)")
    ap.add_argument("--archetype-baseline", default="",
                    help="pin the IDENTITY of each known archetype reuse, so a swap fails "
                         "at an unchanged count (#411's argument again)")
    ap.add_argument("--baseline", default="",
                    help="JSON of known mismatches; fails on any NEW one even if the total "
                         "is unchanged (#411). A ceiling cannot see a swap.")
    ap.add_argument("--update-baseline", action="store_true",
                    help="rewrite --baseline from the current state")
    ap.add_argument("--require-aro", action="store_true",
                    help="exit 1 if aro.obo is absent, instead of reporting a meaningless "
                         "small number (#365)")
    args = ap.parse_args()

    # #418: the identity gate's EXIT CODE had no test -- changing `return 1` to `return 0`
    # passed the whole suite. It could not be tested because the corpus paths were module
    # constants; overriding them makes a fixture-corpus CLI test possible.
    global TRAITS, OBO
    if args.traits_root:
        TRAITS = Path(args.traits_root).resolve()
        if not TRAITS.is_dir():
            print(f"FAIL: --traits-root {TRAITS} is not a directory. A typo here reports "
                  f"'0 evidence items, MISMATCHED: 0' and exits 0 -- a silent bypass of a "
                  f"merge gate, since the recipe forwards {{args}}.")
            return 1
        # Refuse only when the target is a baseline INSIDE the repo -- that is the one an
        # override would corrupt with absolute keys. A scratch baseline beside a fixture
        # corpus is exactly what testing needs, and the first version of this guard banned
        # it, breaking the test written one commit earlier.
        if args.update_baseline and args.baseline:
            target = Path(args.baseline).resolve()
            if target.is_relative_to(ROOT):
                print(f"FAIL: refusing --update-baseline on {_rel(target)} while "
                      f"--traits-root is set. It would replace a committed baseline with "
                      f"keys from the override corpus, including absolute paths.")
                return 1
    if args.obo:
        OBO = Path(args.obo).resolve()
    if args.require_aro and not OBO.exists():
        print(f"FAIL: --require-aro and {_rel(OBO)} is absent; run `just fetch-aro`")
        return 1
    rc = 0
    if args.configs_only:
        args.configs = True
        # B1: with the record walk skipped, `bad` is empty -- so the data-side identity
        # gate reported "41 FIXED" and printed "re-run with --update-baseline to lock it
        # in", which zeroed the committed baseline and exited 0. The tool recommended its
        # own self-destruct. The data-side gates are off when their input is (#429 review).
        # The archetype gate reads RECORDS and nothing else, so --configs-only starves it
        # exactly as it starves the data side. Left on, it would report "0 items" against
        # a 100-entry baseline, print "100 FIXED", and -- with --update-baseline, which
        # the recipe forwards -- overwrite the baseline with `{}`. Same self-destruct B1
        # found for --baseline; same fix.
        if (args.baseline or args.update_baseline or args.max is not None or args.strict
                or args.archetypes or args.max_archetypes is not None
                or args.archetype_baseline):
            print("NOTE: --configs-only skips the record walk, so --baseline/--max/--strict "
                  "and the --archetypes gates have no data to judge and are ignored. Run "
                  "without it to gate the data side.")
        args.baseline, args.max, args.strict = "", None, False
        args.archetypes, args.max_archetypes, args.archetype_baseline = False, None, ""
    root = TRAITS / args.path if args.path else TRAITS
    paths = [] if args.configs_only else sorted(root.rglob("*.yaml"))
    items = list(iter_evidence(paths))

    wanted = {it[4] for it in items
              if it[4].split(":")[0] in ON_DISK_PREFIXES and not it[4].startswith("ARO:")}
    if args.configs:
        # ONE resolution pass for both sides: the config `wanted` is 50 refs, the data
        # side's 53, overlapping 50 -- resolving twice cost 26s of the 60s recipe (#428).
        wanted |= {r for _f, _k, r, _s in iter_config_snippets()
                   if r.split(":")[0] in ON_DISK_PREFIXES and not r.startswith("ARO:")}
    obo = load_obo_stanzas()
    if not obo:
        print(f"NOTE: {_rel(OBO)} is absent (data/raw is gitignored), so every "
              f"ARO reference is unverifiable here. Run `just fetch-aro` first -- otherwise "
              f"this reports a small number and means nothing (#365).")
        # #432: the archetype gate reads NOTHING BUT the obo -- "is this term gene-level"
        # and "is it an ancestor" both come from it -- so without it the check reports 0
        # items, the identity gate prints "323 FIXED", and `--update-baseline`, which the
        # recipe documents as the normal follow-up and forwards {{args}} to, writes `{}`
        # over the committed baseline and exits 0. The entire review queue would be
        # blessed away by a command that reads as progress.
        #
        # This is the same starvation B1 found for --configs-only, reached by a different
        # route: there the RECORDS are missing, here the OBO is. The data-side and config
        # gates survive it -- unresolvable is not a failure for them, and both baselines
        # are empty -- but the archetype gate cannot tell "no findings" from "no input".
        if args.archetypes:
            print("NOTE: --archetypes needs the obo for both of its questions, so it is "
                  "OFF here rather than reporting 0 of everything. Its gates and its "
                  "baseline are untouched.")
            args.archetypes = False
            args.max_archetypes, args.archetype_baseline = None, ""
    kb = load_kb_definitions(wanted)

    checked = unresolved = skipped = 0
    bad: list[tuple] = []
    by_ref: dict[str, int] = defaultdict(int)
    by_ref_unresolved: dict[str, int] = defaultdict(int)
    for path, gid, subj, obj, ref, snip, _ident in items:
        prefix = ref.split(":")[0]
        if prefix not in ON_DISK_PREFIXES:
            skipped += 1                      # PMID / DOI / URL -- valid, not verifiable here
            continue
        body = obo.get(ref) if ref.startswith("ARO:") else kb.get(ref)
        if body is None:
            # Not a failure: a prefix we hold text for, but this particular id is not a
            # record here. Reported so it cannot hide, never counted as a mismatch --
            # an unverifiable citation and a false one are different things (#365).
            unresolved += 1
            by_ref_unresolved[ref] += 1
            continue
        checked += 1
        if _norm(snip) not in body:
            bad.append((path, gid, subj, obj, ref, snip, "snippet not in that source"))
            by_ref[ref] += 1

    records = {b[0] for b in bad}
    if args.configs_only:
        print("record walk skipped (--configs-only)")
    else:
        print(f"evidence items:            {len(items):,}")
    if not args.configs_only:
        print(f"  checked against disk:    {checked:,}")
        print(f"  skipped (PMID/DOI/URL):  {skipped:,}  -- valid, not verifiable offline")
        print(f"  not on disk (not a fail): {unresolved:,}"
              f"{'  e.g. ' + ', '.join(sorted(by_ref_unresolved)[:3]) if by_ref_unresolved else ''}")
        print(f"MISMATCHED:                {len(bad):,}  across {len(records):,} records, "
              f"{len(by_ref):,} distinct references")

    # Classify: is the snippet verbatim in some OTHER term? Then the text is real CARD
    # prose under the wrong attribution -- a mechanical repoint. If it is nowhere on disk,
    # it was truncated or reworded when quoted, and a human has to read the source.
    if bad:
        misattributed, unfindable = [], []
        for entry in bad:
            snip = _norm(entry[5])
            owners = [tid for tid, body in obo.items() if snip in body]
            if len(owners) == 1:
                misattributed.append((entry, owners[0]))
            elif owners:
                unfindable.append((entry, f"ambiguous: {len(owners)} terms contain it"))
            else:
                unfindable.append((entry, "verbatim in no term on disk"))
        print(f"\n  misattributed (snippet IS verbatim in exactly one other term -- "
              f"a repoint): {len(misattributed):,}")
        print(f"  needs reading (truncated, reworded, or ambiguous): "
              f"{len(unfindable):,}")
        if misattributed:
            print("\n  repoint suggestions:")
            seen = set()
            for (path, gid, subj, obj, ref, snip, why), owner in misattributed:
                key = (ref, owner)
                if key in seen:
                    continue
                seen.add(key)
                n = sum(1 for e, ow in misattributed if e[4] == ref and ow == owner)
                print(f"    {n:>5}x  {ref}  ->  {owner}")
        if unfindable:
            print("\n  needs reading, by reference:")
            counts: dict[str, int] = defaultdict(int)
            for entry, _ in unfindable:
                counts[entry[4]] += 1
            for ref, n in sorted(counts.items(), key=lambda kv: -kv[1])[:args.show]:
                print(f"    {n:>5}  {ref}")

        print("\nworst references:")
        for ref, n in sorted(by_ref.items(), key=lambda kv: -kv[1])[:args.show]:
            print(f"  {n:>5}  {ref}")
        print("\nexamples:")
        for path, gid, subj, obj, ref, snip, why in bad[:args.show]:
            rel = _rel(path)
            print(f"  {rel}")
            print(f"    {gid}: {subj} -> {obj}  cites {ref} ({why})")
            print(f"    snippet: {_norm(snip)[:110]}")

    # The config gate runs BEFORE every early return. It sat after them, so
    # `--update-baseline` -- which the justfile documents as the normal follow-up
    # workflow and which forwards {{args}} -- skipped it entirely: --max-configs 0
    # against 13 real failures exited 0. That is the SAME defect this commit claims to
    # have fixed twice, a third time, in the branch it was fixed in (#424 review).
    if args.configs:
        n_cfg, cfg_counts = audit_configs(args.show, obo, kb)
        if args.max_configs is not None and n_cfg > args.max_configs:
            print(f"FAIL: {n_cfg} config literals are not verbatim in the source they name, "
                  f"exceeding --max-configs {args.max_configs}")
            rc = 1
        elif args.strict and n_cfg:
            rc = 1
        # A ceiling masks a swap here exactly as it does on the data side: fixing
        # Pfam:PF04563 while introducing a new corrupt literal leaves 13 (#428).
        if args.config_baseline:
            cb = Path(args.config_baseline)
            if args.update_baseline:
                # B2: `cb` was not resolved, and `Path("audit/...").is_relative_to(ROOT)`
                # is False -- the relative form the justfile passes. The guard was dead.
                if cb.resolve().is_relative_to(ROOT) and args.traits_root:
                    print("FAIL: refusing --update-baseline on an in-repo config baseline "
                          "while --traits-root is set.")
                    return 1
                was = _load_baseline(cb)
                gone, added = diff_baseline(cfg_counts, was)
                print(f"\nconfig baseline: {sum(was.values()):,} -> {sum(cfg_counts.values()):,}"
                      f"  ({len(gone):,} FIXED, {len(added):,} NEW)")
                for k in added[:args.show]:
                    fam, field, ref, snip = k.split("|", 3)
                    print(f"  NEW    {fam}  {field}  cites {ref}\n         {snip[:100]}")
                cb.parent.mkdir(parents=True, exist_ok=True)
                cb.write_text(json.dumps(cfg_counts, indent=1) + "\n", encoding="utf-8")
                print(f"config baseline written -> {cb}")
                if added:
                    print("NOTE: newly-blessed config literals above. `git diff` the baseline "
                          "before committing -- this command can launder a regression.")
            elif not cb.exists():
                print(f"\nFAIL: --config-baseline {cb} does not exist; run --update-baseline")
                rc = 1
            else:
                known = _load_baseline(cb)
                fixed, new = diff_baseline(cfg_counts, known)
                print(f"\nconfig baseline: {sum(known.values()):,} known · "
                      f"{len(fixed):,} FIXED · {len(new):,} NEW")
                for k in new[:args.show]:
                    fam, field, ref, snip = k.split("|", 3)
                    print(f"  NEW    {fam}  {field}  cites {ref}\n         {snip[:100]}")
                if new:
                    print(f"FAIL: {len(new)} config literal(s) newly cite a source that does "
                          f"not contain them.")
                    rc = 1

    # --- archetype gate (#425) ------------------------------------------------------
    # BEFORE the data-side identity gate, for the reason the config gate is: that block
    # returns, and `--update-baseline` is the documented follow-up workflow. A gate placed
    # after a `return` is a gate that is off exactly when someone is changing things.
    if args.archetypes:
        n_arch, arch_counts = audit_archetypes(items, obo, args.show)
        if args.max_archetypes is not None and n_arch > args.max_archetypes:
            print(f"FAIL: {n_arch} archetype-reuse item(s), exceeding --max-archetypes "
                  f"{args.max_archetypes}")
            rc = 1
        if args.archetype_baseline:
            abp = Path(args.archetype_baseline)
            if args.update_baseline:
                if abp.resolve().is_relative_to(ROOT) and args.traits_root:
                    print("FAIL: refusing --update-baseline on an in-repo archetype "
                          "baseline while --traits-root is set.")
                    return 1
                was = _load_baseline(abp)
                gone, added = diff_baseline(arch_counts, was)
                print(f"\narchetype baseline: {sum(was.values()):,} -> "
                      f"{sum(arch_counts.values()):,}  ({len(gone):,} FIXED, "
                      f"{len(added):,} NEW)")
                for k in added[:args.show]:
                    rec, _g, edge, ref, snip = k.split("|", 4)
                    print(f"  NEW    {rec.rsplit('/', 1)[-1]}  {edge}  {ref}\n"
                          f"         {snip[:100]}")
                abp.parent.mkdir(parents=True, exist_ok=True)
                abp.write_text(json.dumps(arch_counts, indent=1) + "\n", encoding="utf-8")
                print(f"archetype baseline written -> {abp}")
                if added:
                    print("NOTE: newly-blessed archetype reuse above. `git diff` the "
                          "baseline before committing -- this command can launder one.")
            elif not abp.exists():
                print(f"\nFAIL: --archetype-baseline {abp} does not exist; run "
                      f"--update-baseline")
                rc = 1
            else:
                known = _load_baseline(abp)
                fixed, new = diff_baseline(arch_counts, known)
                print(f"\narchetype baseline: {sum(known.values()):,} known · "
                      f"{len(fixed):,} FIXED · {len(new):,} NEW")
                for k in new[:args.show]:
                    rec, _g, edge, ref, snip = k.split("|", 4)
                    print(f"  NEW    {rec.rsplit('/', 1)[-1]}  {edge}  {ref}\n"
                          f"         {snip[:100]}")
                if new:
                    print(f"FAIL: {len(new)} evidence item(s) newly cite a gene-level term "
                          f"that is neither the record's own nor an ancestor of it.")
                    rc = 1

    # --- identity gate (#411) -------------------------------------------------------
    if args.baseline:
        bpath = Path(args.baseline)
        # Keyed on the EDGE, not just (record, reference, snippet). The first version
        # collapsed 174 items into 71 triples, leaving 103 (59%) unpinned -- and a record
        # that already carries a known-bad triple could gain ANOTHER edge with the same
        # one and both gates stayed green. Demonstrated on basr-aro3003582, which already
        # has five such edges, so a sixth is a routine promoter change (#411 review).
        counts: dict[str, int] = defaultdict(int)
        for p_, g, su, o, r, s, _w in bad:
            counts[baseline_key(_rel(p_), g, su, o, r, s)] += 1
        current = dict(sorted(counts.items()))
        if args.update_baseline:
            # Report BEFORE writing. The first version wrote and returned 0 immediately,
            # so `--update-baseline` rewrote the record of what is known AND short-circuited
            # --max in one command, printing nothing about what changed (#411 review).
            was = _load_baseline(bpath)
            gone, added = diff_baseline(current, was)
            print(f"\nbaseline update: {len(was):,} -> {len(current):,}  "
                  f"({len(gone):,} FIXED, {len(added):,} NEW)")
            for k in added[:args.show]:
                print(f"  NEW    {k.split('|')[0].rsplit('/', 1)[-1]}  {k.split('|')[3]}")
            bpath.parent.mkdir(parents=True, exist_ok=True)
            bpath.write_text(json.dumps(current, indent=1) + "\n", encoding="utf-8")
            print(f"baseline written -> {bpath}")
            if added:
                print("NOTE: newly-blessed mismatches above. `git diff` the baseline before "
                      "committing -- this command can launder a regression.")
            # --max/--strict still decide the exit code; updating is not a bypass.
            if args.strict and bad:
                return 1
            if args.max is not None and len(bad) > args.max:
                print(f"FAIL: {len(bad)} mismatches exceeds --max {args.max}")
                return 1
            return rc
        if not bpath.exists():
            print(f"\nFAIL: --baseline {bpath} does not exist; run --update-baseline")
            return 1
        known = _load_baseline(bpath)
        # COUNTS, not a set. A record already carrying a known-bad edge could gain another
        # identical one and a set-keyed baseline would not see it -- demonstrated by cloning
        # an edge on basr-aro3003582 (#411 review).
        fixed, new = diff_baseline(current, known)
        print(f"\nbaseline: {sum(known.values()):,} known · {len(fixed):,} FIXED · "
              f"{len(new):,} NEW")
        for k in fixed[:args.show]:
            rec, _g, edge, ref, _s = k.split("|", 4)
            print(f"  FIXED  {rec.rsplit('/', 1)[-1]}  {edge}  {ref}")
        for k in new[:args.show]:
            rec, _g, edge, ref, snip = k.split("|", 4)
            print(f"  NEW    {rec.rsplit('/', 1)[-1]}  {edge}  {ref}\n         {snip[:100]}")
        if new:
            print(f"\nFAIL: {len(new)} snippet(s) cite a source that does not contain them. "
                  f"If they are intentional, re-run with --update-baseline.")
            return 1
        if fixed:
            print("Progress: re-run with --update-baseline to lock it in.")


    if args.strict and bad:
        return 1
    if args.max is not None and len(bad) > args.max:
        print(f"\nFAIL: {len(bad)} mismatches exceeds --max {args.max}")
        return 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
