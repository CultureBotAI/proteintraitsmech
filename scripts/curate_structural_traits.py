"""Apply the bounded, reviewed structural-trait ledger without reformatting records.

Dry-run by default. All targets and candidate outputs are validated before the
first corpus write. Input/output hashes make partial repairs and drift explicit;
the exact completed output is an idempotent no-op. No new records are created.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import yaml

from record_io import RecordValidationError, is_curated, write_validated_record
from structural_trait_curations import ROOT, apply_blocks, digest, load_curations, parse_record
from validate_strict import validate_one

TRAITS_ROOT = ROOT / "data/traits"


def should_enrich(text: str) -> bool:
    return not is_curated(text)


def reviewed_seeded_history(text: str, entry: dict) -> bool:
    """A documented exception covers only this exact reviewed SEEDED preimage."""
    return (entry.get("allow_seeded_history") is True
            and digest(text) == entry["input_sha256"]
            and parse_record(text).get("mapping_status") == "SEEDED")


def reviewed_proposed_followup(text: str, entry: dict) -> bool:
    """An independent-review correction to this agent's exact prior output only."""
    data = parse_record(text)
    history = data.get("curation_history") or []
    return (entry.get("allow_proposed_followup") is True
            and digest(text) == entry.get("prior_output_sha256") == entry["input_sha256"]
            and data.get("mapping_status") == "PROPOSED"
            and bool(history) and history[-1].get("curator") == "codex-gpt-6-astra"
            and history[-1].get("llm_assisted") is True)


def reviewed_input(text: str, entry: dict) -> bool:
    return (should_enrich(text) or reviewed_seeded_history(text, entry)
            or reviewed_proposed_followup(text, entry))


def curate_record_text(text: str, entry: dict) -> str:
    data = parse_record(text)
    if (data.get("identifier") != entry["identifier"]
            or data.get("trait_axis") != "STRUCTURE"
            or data.get("trait_category") != entry["trait_category"]
            or data.get("term_kind") != "CLASS"):
        raise ValueError("unexpected structural trait identity/scope; re-review required")
    if digest(text) == entry["output_sha256"]:
        return text
    if not reviewed_input(text, entry):
        raise ValueError(f"{entry['identifier']}: curated input requires re-review")
    if digest(text) != entry["input_sha256"]:
        raise ValueError(f"{entry['identifier']}: input drift; re-review required")
    out = apply_blocks(text, entry)
    if len(parse_record(out).get("curation_history", [])) != len(data.get("curation_history", [])) + 1:
        raise ValueError("curation must append exactly one history event")
    if digest(out) != entry["output_sha256"]:
        raise ValueError(f"{entry['identifier']}: output does not match reviewed ledger")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only", nargs="+", help="exact existing trait identifiers")
    args = parser.parse_args(argv)
    try:
        entries = load_curations()
        requested = set(args.only or entries)
        missing = requested - entries.keys()
        if missing:
            raise ValueError(f"unknown curation targets: {sorted(missing)}")
        plans: list[tuple[Path, str, str]] = []
        with tempfile.TemporaryDirectory(prefix="ptm-structural-curation-") as preview:
            for identifier in sorted(requested):
                entry = entries[identifier]
                path = ROOT / entry["path"]
                if (path.is_symlink() or not path.is_file()
                        or path.resolve() != path.absolute()
                        or not path.is_relative_to(TRAITS_ROOT)):
                    raise ValueError(f"unsafe or missing existing target: {path}")
                errors = validate_one(path)
                if errors:
                    raise RecordValidationError(path, errors)
                text = path.read_text(encoding="utf-8")
                out = curate_record_text(text, entry)
                if out == text:
                    print(f"UNCHANGED {identifier}")
                    continue
                if (not should_enrich(text) and not reviewed_seeded_history(text, entry)
                        and not reviewed_proposed_followup(text, entry)):
                    raise ValueError(f"refusing curated target: {identifier}")
                write_validated_record(Path(preview) / path.name, out)
                plans.append((path, text, out))
            for path, before, after in plans:
                if path.read_text(encoding="utf-8") != before:
                    raise ValueError(f"target changed during preflight: {path}")
                if args.apply:
                    write_validated_record(path, after)
                print(f"{'WROTE' if args.apply else 'WOULD WRITE'} {path.relative_to(ROOT)}")
        print(f"{len(plans)} changed; {len(requested) - len(plans)} unchanged; "
              f"{'applied' if args.apply else 'dry-run'}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
