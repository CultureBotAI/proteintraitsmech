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
import hashlib
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_ROOT = REPO_ROOT / "data" / "traits"
BINDINGS_ROOT = REPO_ROOT / "data" / "grounding" / "qualified_record_bindings.jsonl.d"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import grounding_registry_layout as layout

CAVEAT_NOTES = {
    "GO:0047154": {
        "rel_path": "function/molecular_function/go/methylmalonyl-coa-carboxytransferase-activity-go0047154.yaml",
        "protein_id": "UniProtKB:Q8GBW6",
        "shard": "c9.jsonl",
        "evidence_id": "ug-evidence:c96c63450c96bb20093b9a8e9909226f40504e3075aece9539241d6e68eb841f",
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
        "shard": "62.jsonl",
        "evidence_id": "ug-evidence:6276754b86bfaeace8689767ddb0502d528c4da7aa2baf713957b3ae41e85726",
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


def repair_bindings(apply: bool) -> tuple[int, int, int]:
    """Sync record_sha256 in qualified_record_bindings.jsonl.d shards and rebuild manifest.json.

    Returns (repaired, already_correct, errors).
    """
    if not BINDINGS_ROOT.is_dir():
        return 0, 0, 0

    repaired = 0
    already = 0
    errors = 0
    dirty_shards = False

    for trait_id, cfg in sorted(CAVEAT_NOTES.items()):
        yaml_path = TRAITS_ROOT / cfg["rel_path"]
        if not yaml_path.is_file():
            print(f"ERROR: trait file missing: {yaml_path}", file=sys.stderr)
            errors += 1
            continue

        target_sha256 = hashlib.sha256(yaml_path.read_bytes()).hexdigest()
        shard_path = BINDINGS_ROOT / cfg["shard"]
        if not shard_path.is_file():
            print(f"ERROR: shard file missing: {shard_path}", file=sys.stderr)
            errors += 1
            continue

        lines = shard_path.read_text(encoding="utf-8").splitlines(keepends=True)
        evidence_id = cfg["evidence_id"]
        found = False
        new_lines = []

        for line in lines:
            if evidence_id in line:
                found = True
                row = json.loads(line)
                if row.get("evidence_id") == evidence_id:
                    if row.get("record_sha256") == target_sha256:
                        already += 1
                        new_lines.append(line)
                        print(f"  binding {cfg['shard']} ({trait_id}): already correct")
                    else:
                        row["record_sha256"] = target_sha256
                        dumped = json.dumps(row, separators=(",", ":"), ensure_ascii=False) + "\n"
                        new_lines.append(dumped)
                        repaired += 1
                        verb = "wrote" if apply else "would write"
                        print(f"  {verb} binding {cfg['shard']} ({trait_id}): updated record_sha256 to {target_sha256}")
                        dirty_shards = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        if not found:
            print(f"ERROR: evidence_id {evidence_id} not found in {shard_path}", file=sys.stderr)
            errors += 1
        elif dirty_shards and apply:
            shard_path.write_text("".join(new_lines), encoding="utf-8")

    if dirty_shards:
        if apply:
            shards = {p.name: p.read_bytes() for p in BINDINGS_ROOT.glob("*.jsonl")}
            manifest_text = layout.build_manifest_text(shards)
            (BINDINGS_ROOT / "manifest.json").write_text(manifest_text, encoding="utf-8")
            print("  wrote updated manifest.json for qualified_record_bindings.jsonl.d")
        else:
            print("  would rebuild manifest.json for qualified_record_bindings.jsonl.d")

    return repaired, already, errors


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

    print("Checking trait YAML files:")
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

    print("\nChecking qualified-record bindings:")
    b_repaired, b_already, b_errors = repair_bindings(args.apply)
    repaired += b_repaired
    already += b_already
    errors += b_errors

    print(f"\nSummary: {repaired} to write, {already} already correct, {errors} errors")
    if not args.apply and repaired > 0:
        print("Dry run complete; run with --apply to write changes.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
