#!/usr/bin/env python3
r"""Who is allowed to write a trait record, and by what route? (#492, for #484 item 4)

THE INVARIANT THIS REPO ACTUALLY NEEDS, which is not the siblings'
-------------------------------------------------------------------
`record_io.write_record` is the choke point that makes `merge_on_reseed` reachable, and
#455 measured what it protects: a `--force` re-seed shortened 27,784 definitions when one
rule inside it failed to fire. So the question here is not "does a writer validate before
replacing" (the sibling Mechs' framing) but **"does every writer of a trait record go
through that choke point, or is it a deliberate, declared exception?"**

AND A BLANKET RULE WOULD BE WRONG. An in-place editor MUST bypass `write_record`:
`merge_on_reseed` reads its input as "what the seeder would emit today", so handing it an
edited copy of the file reconciles the record against itself and REVERTS the edit. That is
measured too -- #148, 566 of 1,707 records silently keeping text a repair had removed. The
six definition editors bypass it on purpose and `tests/test_inplace_editor_guards.py`
keeps them honest. (This sentence said "six" while the tool printed 4 for an entire PR,
because the detector could not see the `files += sorted(d.glob(...))` accumulator. A
docstring disagreeing with its own tool is a finding, not a typo -- it was the visible
symptom of two blind spots.)

So there are four legitimate routes and one finding:

  * SEEDER          calls `write_record` -- merge on, curation preserved.
  * EDITOR          in `tests/test_inplace_editor_guards.py::EDITORS` -- an in-place
                    definition editor, must bypass the merge through
                    `write_validated_record`, and that test proves it carries
                    `should_enrich`.
  * VALIDATED       an explicitly registered transactional promoter that writes only
                    through `write_validated_record` after its own review/semantic gates.
  * DECLARED        a repair, migration or builder listed in `BYPASS` below WITH A REASON.
  * anything else   FINDING. A script writing trait records by a route nobody has thought
                    about is exactly how #455 and #148 happened.

WHY THE REGISTRY IS READ, NOT DUPLICATED
-----------------------------------------
`EDITORS` lives in the guard test. This reads it from there rather than keeping a second
copy, because two lists of the same thing is how `slugify` reached 31 copies and 28
distinct implementations (#110). A script added to one and not the other would otherwise
pass both checks.

WHAT "WRITES A TRAIT RECORD" MEANS HERE
-----------------------------------------
Not "mentions data/traits" -- `audit_reproducible.py` names `ARO_DIR` and writes only a
baseline JSON. The test is structural: does the script iterate a traits directory and then
write back to a path derived from that iteration? That is the shape every in-place editor
in this repo has, and it is what a grep cannot see.
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
GUARD_TEST = ROOT / "tests" / "test_inplace_editor_guards.py"

# Traits roots are DERIVED FROM THE MODULE, not hand-listed. The hand-list missed
# `OUT_DIR` in revert_rejected_subfamily_definitions -- a genuine in-place writer -- and
# there is no reason to think it was the only name nobody guessed. A module-level constant
# whose value mentions "traits" is a traits root, whatever it is called.
FALLBACK_ROOTS = {"ARO_DIR", "TRAITS", "TRAITS_ROOT", "TRAIT_ROOT", "traits_root"}

# Scripts that write trait records WITHOUT `write_record`, deliberately. Each needs a
# reason, because "it has always been in the list" is how an allow-list stops being a
# decision. A repair or migration edits text in place; routing it through the merge would
# revert its own edit (#148).
BYPASS = {
    "promote_family_drafts": "writes causal_graphs in place; the merge would revert the "
                             "graph it just built (#204 guards the same path)",
    "repair_self_referential_notes": "in-place note rewrite (#364)",
    "repair_misattributed_snippets": "in-place snippet rewrite (#422/#425)",
    "repair_beta_lactam_notes": "in-place note rewrite (#466)",
    "repair_interpro_abstracts": "in-place definition restore (#159); its docstring "
                                 "explains why a re-seed cannot do it",
    "repair_pfam_interpro_xrefs": "in-place mapped_xrefs rewrite (#344); a re-seed cannot "
                                  "REMOVE a stale xref, by design (#120)",
    "repair_panther_definitions": "in-place definition repair",
    "migrate_axis_split_fixes": "one-off migration",
    "migrate_coiled_coils_to_sequence": "one-off migration",
    "migrate_domain_families_to_sequence": "one-off migration",
    "migrate_trait_relations": "one-off migration",
    "fix_noncurie_xrefs": "in-place xref repair",
    "backfill_source_citations": "in-place citation backfill",
    "enrich_aro_resistance": "in-place trait_relations enrichment",
    "enrich_cath_structural_defs": "in-place definition enrichment",
    "enrich_cazy_groundings": "in-place grounding enrichment",
    "enrich_ecod_structural_defs": "in-place definition enrichment",
    "enrich_family_mechanistic_inherited_defs": "in-place definition enrichment",
    "enrich_go_mf_mechanistic_defs": "in-place definition enrichment",
    "enrich_interaction_mechanistic_defs": "in-place definition enrichment",
    "enrich_mechanistic_defs": "in-place definition enrichment",
    "enrich_panther_from_subfamilies": "in-place; its comment records that write_record "
                                       "would restore the stub it is replacing",
    "enrich_prosite_citations": "in-place citation enrichment",
    "enrich_scop_inherited_structural": "in-place definition enrichment",
    "enrich_secondary_structural_defs": "in-place definition enrichment",
    "enrich_seq_structural_inherited_defs": "in-place definition enrichment",
    "enrich_structural_provenance": "in-place provenance enrichment",
    "build_biolip_causal_graphs": "appends a causal graph to an existing record",
    "build_rhea_causal_graphs": "appends a causal graph to an existing record",
    "draft_aro_causal_graphs": "writes draft graphs in place",
    # Found only after the detector learned `p.open("w")`, accumulators and
    # helper-returned paths. Every one was invisible to the first version, and
    # build_mcsa_causal_graphs is the tell: its four sibling graph builders were already
    # in this list, and it was absent purely because the detector could not see it.
    "build_mcsa_causal_graphs": "writes M-CSA catalytic graphs onto existing records",
    "enrich_repeatsdb_inherited_reps": "in-place repeat enrichment via a helper-returned path",
    "enrich_repeatsdb_member_reps": "in-place repeat enrichment via a helper-returned path",
    "migrate_mapped_xrefs": "one-off migration; writes with path.open(\"w\") + yaml.dump",
    "ground_categories": "in-place category grounding; writes with path.open(\"w\")",
    "migrate_ncbifam_filenames": "renames records in place; a rename is a write",
    "ground_activity_nodes_ec2go": "grounds M-CSA activity nodes to GO MF via ec2go",
    "recompose_panther_definitions": "in-place PANTHER definition recomposition",
    "revert_rejected_subfamily_definitions": "in-place revert; the merge would restore the "
                                             "very text being reverted",
    # Added from the audit's own findings, with each script's own description as the
    # reason -- not invented. Every one is a builder, enricher or repair that edits an
    # existing record, so routing it through `write_record` would revert its edit (#148).
    "build_ec_causal_graphs": "writes reaction-chemistry graphs onto EC records",
    "build_metalpdb_causal_graphs": "writes metal-coordination graphs onto MetalPDB records",
    "build_rhea_mcsa_residue_graphs": "gives Rhea records their catalytic residues from M-CSA",
    "build_structural_equivalence": "phase-3 structural equivalence (entry-merge round 1)",
    "build_swissprot_profiles": "builds per-protein trait profiles from Swiss-Prot (#7)",
    "cite_resistance_draft_edges": "gives resistance draft edges a verbatim ARO snippet",
    "enrich_ec_general_defs": "adds a general definition layer to EC records",
    "enrich_scop_structural_defs": "adds structural definitions to SCOP fold records",
    "fix_resistance_drug_edges": "re-bases resistance -> drug edges on CARD/ARO's assertion",
    "resolve_mcsa_residue_frames": "resolves M-CSA residue frames a global offset cannot (#79)",
    "review_llm_abstracts": "promotes reviewed LLM abstracts into `definition` in place",
}


# Transactional record promoters that intentionally do not use seed/merge semantics and
# are not definition editors.  These must be named separately from BYPASS: their contract
# is precisely that the final replacement goes through write_validated_record after an
# explicit review gate.  The audit verifies the call structurally and rejects stale or
# overlapping entries.
VALIDATED_WRITERS = {
    "ground_uniprot_examples": "review-bound UniProt grounding promotion; every applied "
                               "record uses write_validated_record after closed LinkML and "
                               "sequence-dependent semantic validation",
}


# Scripts this detector flags that do NOT write trait records. Declared rather than
# chased, because each fix to the detector so far has traded one false clearance for a new
# false positive, and an audit that is quietly wrong in the safe direction is still wrong.
#
# Both are the one-hop root propagation being loose: a name assigned FROM a traits root
# (`base = TRAITS_DIR / ...` in build_docs_index) is treated as a traits path even when the
# assignment walks OUT of the corpus. Narrowing that rule is #TBD; until then the two are
# named here with what they actually write, so the list is falsifiable by reading it.
NOT_RECORD_WRITERS = {
    "build_docs_index": "writes docs/data/*.json shards; `base` is tainted from TRAITS_DIR "
                        "by the one-hop rule but resolves under docs/",
    "build_sequence_structure_alignment": "writes data/equivalence/*.tsv",
    "validate_uniprot_grounding": "reads trait records and writes only its validation TSV "
                                  "under reports/; the detector taints that report path",
}


def registered_editors() -> set[str]:
    """`EDITORS` from the guard test -- read, never copied (see the module docstring)."""
    text = GUARD_TEST.read_text(encoding="utf-8")
    block = re.search(r"^EDITORS = \[(.*?)^\]", text, re.M | re.S)
    if not block:
        raise SystemExit("FAIL: could not find EDITORS in tests/test_inplace_editor_guards.py"
                         " -- this audit reads that list rather than keeping its own")
    return set(re.findall(r'"([^"]+)"', block.group(1)))


# Method names that put bytes on disk or move a file there. `unlink` counts: deleting a
# record is a write to the corpus by any reading a curator cares about.
# `replace` and `unlink` are NOT here, deliberately. `str.replace` is one of the most
# common calls in Python -- `p.replace("-", "")` in build_sequence_structure_alignment is
# string surgery on a pattern, not `Path.replace` -- and `unlink` flagged build_docs_index
# for deleting stale docs shards. An attribute name alone cannot distinguish them, and a
# detector that errs toward flagging still may not flag string methods as file writes.
# `os.replace(a, b)` is a function call and would need its own rule if it ever appears.
WRITE_METHODS = {"write_text", "write_bytes", "rename", "touch"}

# `.open(...)` is a write ONLY with a write mode. Counting it unconditionally made
# `p.open(encoding="utf-8")` -- a READ, in review_source_categories -- a record write, and
# flagged three scripts that write docs/data and data/equivalence. A detector that errs
# toward flagging still may not call reading writing.
WRITE_MODES = {"w", "a", "x", "wb", "ab", "xb", "w+", "r+", "a+", "wt", "at"}


def _is_write_open(node: ast.Call) -> bool:
    if node.args and isinstance(node.args[0], ast.Constant):
        return str(node.args[0].value) in WRITE_MODES
    for kw in node.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            return str(kw.value.value) in WRITE_MODES
    return False


def traits_roots(tree: ast.AST) -> tuple[set[str], bool]:
    """(names bound to a path under `data/traits`, whether any was DERIVED from the code).

    The second value matters: `ARO_DIR` is in the fallback set, so a module whose only
    traits root IS `ARO_DIR` produced `roots - FALLBACK_ROOTS == set()` and was read as
    "defines no traits root at all". That cleared `repair_beta_lactam_notes`, whose whole
    purpose is writing trait records in place -- the third time this detector cleared a
    known writer, each time for a different reason.
    """
    derived = False
    roots = set(FALLBACK_ROOTS)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            dumped = ast.dump(node.value)
            # A PATH, not any expression mentioning the word. `{"traits": traits}` in
            # build_swissprot_profiles registered a local dict as a "traits root", tainted
            # 22 names, and put a script that writes data/profiles into BYPASS -- the same
            # error as build_chebi_sidecar, which the commit message claimed to have caught.
            # A LIST or TUPLE of paths counts too. `DIRS = [TRAITS / "a", TRAITS / "b"]`
            # in ground_activity_nodes_ec2go is a genuine root, and requiring a bare BinOp
            # excluded it -- trading the dict-key false positive for a false clearance of a
            # script that writes records with f.write_text.
            path_like = (isinstance(node.value, (ast.BinOp, ast.List, ast.Tuple))
                         or "Call(" in dumped)
            if path_like and ("'traits'" in dumped or "data/traits" in dumped):
                for tgt in node.targets:
                    for name in ast.walk(tgt):
                        if isinstance(name, ast.Name):
                            roots.add(name.id)
                            derived = True
    # one hop: `ARO_DIR = D.ARO_DIR`, `OUT_DIR = TRAITS / "function"`
    for _ in range(3):
        before = len(roots)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                dumped = ast.dump(node.value)
                if any(f"id='{r}'" in dumped or f"attr='{r}'" in dumped for r in roots):
                    for tgt in node.targets:
                        for name in ast.walk(tgt):
                            if isinstance(name, ast.Name):
                                roots.add(name.id)
        if len(roots) == before:
            break
    return roots, derived


def imported_roots(tree: ast.AST) -> set[str]:
    """Traits roots this module IMPORTS from a sibling script.

    `revert_rejected_subfamily_definitions` does `from seed_panther import OUT_DIR` and
    globs it -- and `OUT_DIR` is `data/traits/sequence/family/panther`. Resolving only
    module-local assignments cleared it, so a genuine in-place writer was removed from the
    registry on this audit's own say-so. Fourth distinct reason this detector has cleared a
    known writer; each was a different blind spot, which is the argument for the audit
    erring toward flagging rather than clearing.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            sibling = SCRIPTS / f"{node.module.split('.')[-1]}.py"
            if not sibling.is_file():
                continue
            try:
                other = ast.parse(sibling.read_text(encoding="utf-8"))
            except SyntaxError:                     # pragma: no cover
                continue
            their_roots, their_derived = traits_roots(other)
            if not their_derived:
                continue
            for alias in node.names:
                if alias.name in their_roots:
                    names.add(alias.asname or alias.name)
    return names


def writes_trait_records(tree: ast.AST) -> bool:
    """True if the script iterates a traits directory and writes back into it.

    Structural rather than textual. A script that merely NAMES a traits root -- every
    audit does -- is not a writer; one that binds a loop variable from `<root>.glob()` or
    `.rglob()` and then calls `.write_text` on something derived from it is.
    """
    def bound_names(node) -> set[str]:
        return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}

    # Functions whose body globs a traits root and returns something: a caller doing
    # `path = find_file(rid)` then `path.write_text(...)` is writing a record, and the
    # first version could not see it because the glob was one frame away. Three scripts
    # in this repo do exactly that.
    globbing_helpers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = ast.dump(node)
            if ("glob" in body or "iterdir" in body) and "Return(" in body:
                globbing_helpers.add(node.name)

    roots, derived = traits_roots(tree)
    borrowed = imported_roots(tree)
    roots |= borrowed
    derived = derived or bool(borrowed)
    if not derived:
        # No module-level path under data/traits at all -- it cannot be writing records.
        return False
    # A glob over a CLI argument counts. `repair_beta_lactam_notes` does
    # `paths = sorted(Path(args.path).rglob("*.yaml"))` with the traits default declared
    # inside `add_argument`, which no amount of AST-walking over module constants can see.
    # So once a module is known to define a traits root, ANY glob it writes back into is
    # treated as a record write. That errs toward FLAGGING, which is the safe direction
    # for an audit whose failure mode is clearing a real writer -- as this one did twice.
    iterated: set[str] = set()
    # FIXED POINT, not a single pass. The chain is routinely three hops --
    #   paths = sorted(Path(args.path).rglob("*.yaml"))
    #   for i, path in enumerate(paths):
    #       path.write_text(...)
    # -- and a single pass binds only `paths`, so `path.write_text` matches nothing and
    # the script reads as "does not write trait records". The first version of this audit
    # did exactly that and cleared `repair_beta_lactam_notes`, a script whose entire
    # purpose is writing trait records in place. An audit that clears a known writer is
    # worse than none.
    for _ in range(6):
        before = len(iterated)
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.comprehension)):
                src = ast.dump(node.iter)
                rooted = "glob" in src or "rglob" in src
                chained = any(f"id='{v}'" in src for v in iterated)
                if rooted or chained:
                    iterated |= bound_names(node.target)
            elif isinstance(node, ast.AugAssign):
                # `files += sorted(d.glob("*.yaml"))`. Not an ast.Assign, so the first
                # version never bound `files` -- which is why the tool reported 4 of the
                # SIX registered editors while this file's own docstring said six.
                src = ast.dump(node.value)
                if ("glob" in src or "iterdir" in src
                        or any(f"id='{v}'" in src for v in iterated)):
                    iterated |= bound_names(node.target)
            elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                  and node.func.attr in ("append", "extend")):
                src = ast.dump(ast.Tuple(elts=list(node.args), ctx=ast.Load()))
                if ("glob" in src or "iterdir" in src
                        or any(f"id='{v}'" in src for v in iterated)):
                    iterated |= bound_names(node.func.value)
            elif isinstance(node, ast.Assign):
                src = ast.dump(node.value)
                rooted = "glob" in src or "rglob" in src
                chained = any(f"id='{v}'" in src for v in iterated)
                helper = any(f"id='{h}'" in src for h in globbing_helpers)
                if rooted or chained or helper:
                    for tgt in node.targets:
                        iterated |= bound_names(tgt)
        if len(iterated) == before:
            break
    if not iterated:
        return False
    for node in ast.walk(tree):
        # EVERY WAY A SCRIPT CAN WRITE A FILE, not just `write_text`. The first version
        # recognised one method, so `path.open("w")` + `yaml.dump` -- which three scripts
        # in this repo use -- was invisible, and `p.rename(dst)` was not a write at all.
        # A survey of realistic idioms found 21 of 31 missed.
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and (node.func.attr in WRITE_METHODS
                     or (node.func.attr == "open" and _is_write_open(node)))):
            recv = ast.dump(node.func.value)
            # `(TRAITS / dst / p.name).write_text(...)` -- the receiver is an expression
            # DERIVED from the loop variable, not the variable. migrate_axis_split_fixes
            # writes every record that way, and the first version of this audit cleared it.
            if any(f"id='{v}'" in recv for v in iterated):
                return True
            if any(f"id='{r}'" in recv or f"attr='{r}'" in recv for r in roots):
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", type=int, default=20)
    args = ap.parse_args()

    editors = registered_editors()
    seeders: list[str] = []
    declared: list[str] = []
    registered: list[str] = []
    validated: list[str] = []
    findings: list[tuple[str, str]] = []
    examined = 0

    for path in sorted(SCRIPTS.glob("*.py")):
        stem = path.stem
        if stem in ("record_io", "audit_writers"):
            continue                        # the choke point itself, and this audit
        if stem in NOT_RECORD_WRITERS:
            continue                        # declared detector false positive, see above
        src = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(src)
        except SyntaxError as exc:          # pragma: no cover
            findings.append((stem, f"does not parse: {exc}"))
            continue
        examined += 1
        uses_choke_point = "write_record(" in src
        uses_validated_write = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "write_validated_record"
            for node in ast.walk(tree)
        )
        in_place = writes_trait_records(tree)
        if stem in VALIDATED_WRITERS:
            if uses_validated_write and not uses_choke_point and not in_place:
                validated.append(stem)
            else:
                findings.append(
                    (stem, "registered validated writer must use write_validated_record "
                           "exclusively and must not contain a raw in-place record write")
                )
            continue
        if stem in editors:
            if uses_validated_write and not in_place:
                registered.append(stem)
            else:
                findings.append(
                    (stem, "registered editor does not use write_validated_record "
                     "exclusively")
                )
            continue
        if not in_place:
            if uses_choke_point:
                seeders.append(stem)
            continue
        if stem in BYPASS:
            declared.append(stem)
        elif uses_choke_point:
            seeders.append(stem)
        else:
            findings.append((stem, "writes trait records in place and is in neither "
                                   "EDITORS nor BYPASS"))

    print(f"scripts examined: {examined:,}")
    print(f"  seeders (route through record_io.write_record) : {len(seeders):,}")
    print(f"  registered in-place definition editors (EDITORS): {len(registered):,}")
    print(f"  registered transactional promoters (VALIDATED): {len(validated):,}")
    print(f"  declared bypasses (repairs/migrations/builders) : {len(declared):,}")
    if not examined:
        # #418/#432/#469: an audit that examined nothing must not report a clean tree.
        print("FAIL: no scripts examined; this cannot certify anything.")
        return 1

    # NOT minus `seeders`. BYPASS is documented as "writes trait records WITHOUT
    # write_record", so naming a plain seeder in it asserts a falsehood -- and subtracting
    # seeders meant `BYPASS["seed_prosite"] = "..."` kept the audit green.
    stale = sorted(set(BYPASS) - set(declared) - set(registered))
    if stale:
        # An allow-list that outlives what it allows stops being a decision and becomes
        # decoration -- and it would silently cover a future script that reuses the name.
        print(f"\nFAIL: {len(stale)} BYPASS entr(ies) name a script that no longer writes "
              f"trait records in place. Remove them:")
        for name in stale:
            print(f"  {name}")
    overlap = sorted(set(BYPASS) & editors)
    if overlap:
        print(f"\nFAIL: {len(overlap)} script(s) are in BOTH EDITORS and BYPASS. One "
              f"route each, or the registry says nothing:")
        for name in overlap:
            print(f"  {name}")
    registry_overlap = sorted(
        (set(VALIDATED_WRITERS) & set(BYPASS))
        | (set(VALIDATED_WRITERS) & editors)
    )
    if registry_overlap:
        print(f"\nFAIL: {len(registry_overlap)} script(s) are in VALIDATED_WRITERS and "
              "another writer registry. One route each:")
        for name in registry_overlap:
            print(f"  {name}")
    missing_validated = sorted(set(VALIDATED_WRITERS) - set(validated))
    if missing_validated:
        print(f"\nFAIL: {len(missing_validated)} registered validated writer(s) do not "
              "use the exclusive validated-write route:")
        for name in missing_validated:
            print(f"  {name}")
    missing_editors = sorted(editors - set(registered))
    if missing_editors:
        print(
            f"\nFAIL: {len(missing_editors)} registered editor(s) do not use the "
            "validated-write route:"
        )
        for name in missing_editors:
            print(f"  {name}")
    if findings:
        print(f"\nFAIL: {len(findings)} script(s) write trait records by an undeclared "
              f"route. Each is a place a re-seed's protections do not reach:")
        for name, why in findings[:args.show]:
            print(f"  {name}: {why}")
    if findings or stale or overlap or registry_overlap or missing_editors or missing_validated:
        return 1
    print("\nOK: every writer of a trait record is a seeder, a registered editor, a "
          "registered validated promoter, or a declared bypass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
