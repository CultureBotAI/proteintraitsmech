#!/usr/bin/env python3
"""Add assembled-enzyme caveat notes to Q8GBW6 and Q04507 (#1026).

GO:0047154 is the full transcarboxylase reaction, while the 12S subunit
Q8GBW6 performs only the carboxyl-transfer half (PMID:8366018). AmoA Q04507's
experimental annotation (PMID:19453274) comes from an active multi-subunit AMO
preparation rather than isolated AmoA.

Both examples were originally added as bare QUALIFIED blocks without an inline
note, so the record presented an unqualified activity claim. This repair
records the assembled-enzyme caveat directly on the canonical example in both
trait records.

Dry-run by default; --apply writes in place.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_ROOT = REPO_ROOT / "data" / "traits"

CAVEAT_NOTES = {
    "GO:0047154": {
        "rel_path": "function/molecular_function/go/methylmalonyl-coa-carboxytransferase-activity-go0047154.yaml",
        "protein_id": "UniProtKB:Q8GBW6",
        "note": (
            "Assembled-enzyme context: recombinant 12S subunit catalyses the carboxyl-transfer "
            "partial reaction (PMID:8366018), not the complete transcarboxylase reaction independently."
        ),
        "note_yaml": (
            "  note: >-\n"
            "    Assembled-enzyme context: recombinant 12S subunit catalyses the carboxyl-transfer\n"
            "    partial reaction (PMID:8366018), not the complete transcarboxylase reaction independently.\n"
        ),
    },
    "GO:0018597": {
        "rel_path": "function/molecular_function/go/ammonia-monooxygenase-activity-go0018597.yaml",
        "protein_id": "UniProtKB:Q04507",
        "note": (
            "Assembled-enzyme context: experimental evidence (PMID:19453274) measures an active "
            "multi-subunit AMO preparation rather than isolated AmoA; preserves experimental "
            "annotation in the assembled-enzyme context."
        ),
        "note_yaml": (
            "  note: >-\n"
            "    Assembled-enzyme context: experimental evidence (PMID:19453274) measures an active\n"
            "    multi-subunit AMO preparation rather than isolated AmoA; preserves experimental\n"
            "    annotation in the assembled-enzyme context.\n"
        ),
    },
}


def repair_record_text(text: str, trait_id: str) -> tuple[str | None, str]:
    """Return (repaired_text, status_message).

    If already correct, returns (text, 'already correct').
    If not applicable or unexpected structure, returns (None, reason).
    """
    config = CAVEAT_NOTES.get(trait_id)
    if not config:
        return None, f"no config for trait {trait_id}"

    try:
        data = yaml.safe_load(text)
    except Exception as exc:
        return None, f"YAML parse error: {exc}"

    if not isinstance(data, dict):
        return None, "record root is not a mapping"

    examples = data.get("canonical_examples") or []
    target_example = None
    for ex in examples:
        if ex.get("protein_id") == config["protein_id"]:
            target_example = ex
            break

    if target_example is None:
        return None, f"example {config['protein_id']} not found in record"

    current_note = target_example.get("note")
    if current_note:
        collapsed_cur = " ".join(current_note.split())
        collapsed_want = " ".join(config["note"].split())
        if collapsed_cur == collapsed_want:
            return text, "already correct"
        return None, f"note already present but differs: {current_note!r}"

    # Target location: right under `qualification_status: QUALIFIED`
    target_needle = "  qualification_status: QUALIFIED\n"
    if target_needle not in text:
        return None, "could not locate '  qualification_status: QUALIFIED\\n'"

    # Insert note
    new_text = text.replace(
        target_needle,
        target_needle + config["note_yaml"],
        1,
    )

    # Verification: parse back and check semantics
    try:
        reparsed = yaml.safe_load(new_text)
    except Exception as exc:
        return None, f"re-parsed YAML error: {exc}"

    rep_ex = None
    for ex in reparsed.get("canonical_examples", []):
        if ex.get("protein_id") == config["protein_id"]:
            rep_ex = ex
            break

    if rep_ex is None:
        return None, "example disappeared in re-parsed data"

    collapsed_new = " ".join((rep_ex.get("note") or "").split())
    collapsed_want = " ".join(config["note"].split())
    if collapsed_new != collapsed_want:
        return None, f"note mismatch in re-parsed data: {collapsed_new!r} vs {collapsed_want!r}"

    return new_text, "repaired"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write repairs in place (default is dry-run)",
    )
    args = parser.parse_args(argv)

    paths = sorted(TRAITS_ROOT.glob("function/molecular_function/go/*.yaml"))
    target_rel_paths = {cfg["rel_path"]: tid for tid, cfg in CAVEAT_NOTES.items()}

    repaired = 0
    already = 0
    errors = 0

    for path in paths:
        rel = str(path.relative_to(TRAITS_ROOT))
        if rel not in target_rel_paths:
            continue

        trait_id = target_rel_paths[rel]
        text = path.read_text(encoding="utf-8")
        new_text, status = repair_record_text(text, trait_id)

        if status == "already correct":
            print(f"  {path.name}: already correct")
            already += 1
        elif status == "repaired":
            verb = "wrote" if args.apply else "would write"
            print(f"  {verb} {path.name}: added assembled-enzyme caveat note")
            if args.apply:
                path.write_text(new_text, encoding="utf-8")
            repaired += 1
        else:
            print(f"ERROR {path.name}: {status}", file=sys.stderr)
            errors += 1

    print(f"\nSummary: {repaired} to write, {already} already correct, {errors} errors")
    if not args.apply and repaired > 0:
        print("Dry run complete; run with --apply to write changes.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
