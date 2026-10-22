#!/usr/bin/env python3
"""Apply the 12 reviewed NCBI CDD source-definition errata (#1171, #1172, Stage 4 F1-F12).

Dry-run by default. Refuses curated, unexpected, or partially repaired records;
preflights the full target set before writing any file; preserves all non-target
text and writes through the atomic closed-schema gate. For qualified-example
targets (`CDD:cd00104`, `CDD:cd00959`, #1172), verifies and transactionally
re-binds the durable `qualified_record_bindings.jsonl.d/` receipts alongside the
record updates. `seed_cdd.py` consumes the same errata module so regeneration
cannot revive the upstream source errors.
"""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import os
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cdd_errata as errata  # noqa: E402
import grounding_registry_layout as layout  # noqa: E402
from record_io import (  # noqa: E402
    RecordValidationError,
    append_to_section,
    extract_block,
    is_curated,
    replace_block,
    top_level_keys,
    write_validated_record,
)
from yaml_emit import yaml_escape  # noqa: E402

TRAITS_ROOT = Path(__file__).resolve().parent.parent / "data" / "traits"
TARGETS: dict[str, Path] = {
    acc: TRAITS_ROOT / item.rel_path for acc, item in errata.ERRATA.items()
}


def should_enrich(text: str) -> bool:
    return not is_curated(text)


def _has_qualified_examples(data: dict) -> bool:
    summary = data.get("protein_example_summary")
    if isinstance(summary, dict) and summary.get("qualified_occurrence_count", 0) != 0:
        return True
    examples = data.get("canonical_examples") or []
    if not isinstance(examples, list):
        return True
    return any(
        isinstance(ex, dict) and ex.get("qualification_status") == "QUALIFIED"
        for ex in examples
    )


def _qualified_occurrence_evidence_ids(data: dict[str, Any], identifier: str) -> set[str]:
    evidence_ids: set[str] = set()
    for example in data.get("canonical_examples") or []:
        if not isinstance(example, dict):
            continue
        for occurrence in example.get("trait_occurrences") or []:
            if not isinstance(occurrence, dict):
                continue
            if occurrence.get("qualification_status") != "QUALIFIED":
                continue
            ev_id = occurrence.get("source_evidence_id")
            if not isinstance(ev_id, str) or not ev_id:
                raise ValueError(
                    f"{identifier}: qualified occurrence missing source_evidence_id"
                )
            evidence_ids.add(ev_id)
    return evidence_ids


def repair_record_text(text: str, *, allow_qualified: bool = False) -> str:
    keys = top_level_keys(text)
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate top-level keys")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("record is not a YAML mapping")
    identifier = data.get("identifier")
    if not isinstance(identifier, str) or not identifier.startswith("CDD:"):
        raise ValueError(f"not a CDD record: {identifier!r}")
    acc = identifier.removeprefix("CDD:")
    erratum = errata.ERRATA.get(acc)
    if erratum is None:
        raise ValueError(f"not a reviewed CDD erratum target: {identifier}")
    if (data.get("trait_axis"), data.get("trait_category")) != (
        "SEQUENCE",
        "SEQ_DOMAIN",
    ):
        raise ValueError(f"{identifier}: unexpected trait scope")
    if data.get("label") != erratum.label:
        raise ValueError(f"{identifier}: unexpected label; re-review required")
    if data.get("parent_traits") != [f"CDD:{erratum.parent}"]:
        raise ValueError(f"{identifier}: unexpected parent_traits; re-review required")
    if not allow_qualified and _has_qualified_examples(data):
        raise ValueError(
            f"{identifier}: qualified protein examples require preimage re-binding (#1172)"
        )
    corrected = errata.correct_description(
        acc, erratum.source_description, erratum.parent
    )
    blocks = errata.metadata_blocks(acc)
    # No-op must verify the provenance too; a partial repair is not success.
    if (
        data.get("definition") == corrected
        and data.get("definition_source") == erratum.definition_source
        and data.get("mapping_status") in {"PROPOSED", "REVIEWED"}
        and all(
            item in (data.get(key) or [])
            for key, block in blocks.items()
            for item in yaml.safe_load(block)[key]
        )
    ):
        return text
    if not should_enrich(text):
        raise ValueError(f"{identifier}: curated target requires explicit re-review")
    if (
        data.get("definition") != erratum.source_description
        or data.get("definition_source") != "NCBI CDD"
    ):
        raise ValueError(
            f"{identifier}: unexpected definition/source; re-review required"
        )
    block = extract_block(text, "definition")
    if block is None:
        raise ValueError(f"{identifier}: missing definition block")
    new_block = block
    for old_phrase, new_phrase in erratum.replacements:
        if new_block.count(old_phrase) != 1:
            raise ValueError(
                f"{identifier}: definition is not text-preservingly repairable"
            )
        new_block = new_block.replace(old_phrase, new_phrase)
    out = replace_block(text, "definition", new_block)
    out = replace_block(
        out,
        "definition_source",
        f"definition_source: {yaml_escape(erratum.definition_source)}\n",
    )
    out = replace_block(out, "mapping_status", "mapping_status: PROPOSED\n")
    for key, payload in blocks.items():
        updated = append_to_section(out, key, payload)
        if updated == out:
            raise ValueError(
                f"{identifier}: cannot append {key} without changing formatting"
            )
        out = updated
    expected = dict(data)
    expected.update(
        definition=corrected,
        definition_source=erratum.definition_source,
        mapping_status="PROPOSED",
    )
    for key, payload in blocks.items():
        expected[key] = (data.get(key) or []) + yaml.safe_load(payload)[key]
    if yaml.safe_load(out) != expected:
        raise ValueError(f"{identifier}: repair changed unexpected fields")
    return out


def _validate_durable_registry_paths(
    durable_protein_registry: Path,
    durable_evidence_registry: Path,
    durable_qualified_record_bindings: Path,
) -> list[Path]:
    import ground_uniprot_examples as gu

    outputs = {
        "durable protein registry": durable_protein_registry,
        "durable evidence registry": durable_evidence_registry,
        "durable qualified-record bindings": durable_qualified_record_bindings,
    }
    output_keys = {name: gu._physical_path_key(path) for name, path in outputs.items()}
    if len(set(output_keys.values())) != len(output_keys):
        raise ValueError(
            "durable protein, evidence, and qualified-record binding paths must differ"
        )
    for name, output in outputs.items():
        if gu._path_is_under(output, TRAITS_ROOT) or gu._path_is_under(
            output, gu.DEFAULT_TRAITS
        ):
            raise ValueError(
                f"durable registry output must be outside trait records: {output}"
            )
        for other_name, other in outputs.items():
            if other_name != name and gu._path_is_under(output, other):
                raise ValueError(
                    f"durable registry outputs must not nest: {output} is inside {other}"
                )
        if layout.is_sharded(output) and os.path.islink(output):
            raise ValueError(
                f"registry_layout_conflict: {name} must not be a symlink: {output}"
            )
        enclosing = layout.sharded_ancestor(output.resolve().parent)
        if enclosing is not None:
            raise ValueError(
                f"durable registry output must not be inside the sharded registry "
                f"{enclosing}: {output}"
            )
    for name in ("durable evidence registry", "durable qualified-record bindings"):
        output = outputs[name]
        if gu._path_is_under(
            output, gu.PROTECTED_GROUNDING_ROOT
        ) and not layout.is_sharded(output):
            raise ValueError(
                f"{name} under data/grounding must be a sharded {layout.SHARD_SUFFIX} "
                f"registry: {output}"
            )

    directories: dict[tuple[Any, ...], Path] = {}
    for output in outputs.values():
        directory = output.resolve().parent
        directories.setdefault(gu._physical_path_key(directory), directory)
    return sorted(directories.values())


def _prepare_qualified_rebindings(
    planned: list[tuple[str, Path, str, str, bool]],
    *,
    durable_protein_registry: Path,
    durable_evidence_registry: Path,
    durable_qualified_record_bindings: Path,
) -> tuple[
    int,
    dict[str, dict[str, Any]] | None,
    tuple[Path, str | None],
    tuple[Path, str | None],
    tuple[Path, str | None],
]:
    import ground_uniprot_examples as gu

    all_planned_paths = {target.resolve(): acc for acc, target, _, _, _ in planned}
    has_yaml_qualified = any(
        _has_qualified_examples(yaml.safe_load(before_text))
        for _, _, before_text, _, _ in planned
    )
    any_under_traits_root = any(
        gu._path_is_under(path, TRAITS_ROOT.resolve()) for path in all_planned_paths
    )
    bindings_present = (
        any_under_traits_root
        and gu._artifact_digest(durable_qualified_record_bindings) is not None
    )
    if not has_yaml_qualified and not bindings_present:
        return (
            0,
            None,
            (durable_protein_registry, None),
            (durable_evidence_registry, None),
            (durable_qualified_record_bindings, None),
        )

    existing_registry, reg_digest = gu._load_durable_registry(durable_protein_registry)
    existing_evidence, ev_digest = gu._load_durable_evidence_registry(
        durable_evidence_registry
    )
    existing_bindings, bind_digest = gu._load_durable_qualified_record_bindings(
        durable_qualified_record_bindings,
        existing_evidence,
    )
    bound_planned_paths = {
        gu._safe_record_path(binding["record_path"], TRAITS_ROOT).resolve()
        for binding in existing_bindings.values()
        if gu._safe_record_path(binding["record_path"], TRAITS_ROOT).resolve()
        in all_planned_paths
    }
    qualified_planned = [
        (acc, target, before_text, out, changed)
        for acc, target, before_text, out, changed in planned
        if _has_qualified_examples(yaml.safe_load(before_text))
        or target.resolve() in bound_planned_paths
    ]
    if not qualified_planned:
        return (
            0,
            None,
            (durable_protein_registry, reg_digest),
            (durable_evidence_registry, ev_digest),
            (durable_qualified_record_bindings, bind_digest),
        )
    if not existing_bindings:
        raise ValueError(
            "qualified CDD erratum target requires durable qualified_record_bindings, "
            f"none loaded from {durable_qualified_record_bindings}"
        )

    target_paths_by_acc = {
        acc: target.resolve() for acc, target, _, _, _ in qualified_planned
    }
    changed_paths = {
        target.resolve()
        for _, target, _, _, changed in qualified_planned
        if changed
    }
    unchanged_digests = {
        target.resolve(): gu._text_digest(before_text)
        for _, target, before_text, _, changed in qualified_planned
        if not changed
    }

    required_ev_ids_by_path: dict[Path, set[str]] = {}
    for acc, target, before_text, _, _ in qualified_planned:
        data = yaml.safe_load(before_text)
        ev_ids = _qualified_occurrence_evidence_ids(data, f"CDD:{acc}")
        if not ev_ids:
            raise ValueError(
                f"CDD:{acc}: qualified record has no qualified trait_occurrences"
            )
        missing = sorted(ev_ids - set(existing_bindings))
        if missing:
            raise ValueError(
                f"CDD:{acc}: qualified occurrence(s) missing durable binding receipt: "
                f"{missing[:5]}"
            )
        required_ev_ids_by_path[target.resolve()] = ev_ids

    changed_bindings: dict[str, dict[str, Any]] = {}
    for ev_id, binding in existing_bindings.items():
        bound_path = gu._safe_record_path(binding["record_path"], TRAITS_ROOT).resolve()
        if bound_path in changed_paths:
            changed_bindings[ev_id] = binding
        elif bound_path in unchanged_digests:
            if binding.get("record_sha256") != unchanged_digests[bound_path]:
                raise ValueError(
                    f"{ev_id}: stale qualified-record binding record_sha256 for "
                    f"{binding['record_path']}"
                )

    for acc, path in target_paths_by_acc.items():
        bound_for_path = {
            ev_id
            for ev_id, binding in existing_bindings.items()
            if gu._safe_record_path(binding["record_path"], TRAITS_ROOT).resolve() == path
        }
        if bound_for_path != required_ev_ids_by_path[path]:
            raise ValueError(
                f"CDD:{acc}: durable binding receipts {sorted(bound_for_path)} do not "
                f"match qualified occurrence evidence IDs {sorted(required_ev_ids_by_path[path])}"
            )

    if not changed_bindings:
        return (
            0,
            None,
            (durable_protein_registry, reg_digest),
            (durable_evidence_registry, ev_digest),
            (durable_qualified_record_bindings, bind_digest),
        )

    bound_records, _, replay_rows = gu._load_bound_durable_records(
        changed_bindings,
        existing_evidence,
        existing_registry,
        TRAITS_ROOT,
    )
    prospective_records: dict[Path, dict[str, Any]] = {}
    prospective_sha256: dict[Path, str] = {}
    for acc, target, _, out, changed in qualified_planned:
        if not changed:
            continue
        resolved = target.resolve()
        parsed_out = yaml.safe_load(out)
        sem_errors = gu._semantic_errors_for_record(
            parsed_out,
            existing_registry,
            resolved,
            evidence_registry=existing_evidence,
        )
        if sem_errors:
            detail = "; ".join(f"{e.code}: {e.message}" for e in sem_errors[:5])
            raise ValueError(
                f"CDD:{acc}: post-repair semantic grounding validation failed: {detail}"
            )
        prospective_records[resolved] = parsed_out
        prospective_sha256[resolved] = gu._text_digest(out)

    gate_args = argparse.Namespace(
        interpro_xml=gu.DEFAULT_INTERPRO_XML,
        pfam_clans=gu.DEFAULT_CONTENT_GATE_PFAM_CLANS,
        pfam_types=gu.DEFAULT_CONTENT_GATE_PFAM_TYPES,
        panther_classifications=gu.DEFAULT_CONTENT_GATE_PANTHER_CLASSIFICATIONS,
        interpro_xml_sha256=gu.INTERPRO_109_XML_SHA256,
        pfam_clans_sha256=gu.PFAM_A_CLANS_SHA256,
        pfam_types_sha256=gu.PFAM_TYPES_SHA256,
        panther_classifications_sha256=gu.PANTHER_19_CLASSIFICATIONS_SHA256,
    )
    rebound_subset = gu._promotion_qualified_record_preflight(
        selected=[],
        selected_evidence={},
        durable_bindings=changed_bindings,
        durable_records=bound_records,
        durable_replay_rows=replay_rows,
        prospective_records=prospective_records,
        prospective_sha256=prospective_sha256,
        args=gate_args,
        traits_root=TRAITS_ROOT,
    )
    merged_bindings = dict(existing_bindings)
    merged_bindings.update(rebound_subset)
    if set(merged_bindings) != set(existing_evidence):
        missing = sorted(set(existing_evidence) - set(merged_bindings))
        extra = sorted(set(merged_bindings) - set(existing_evidence))
        raise ValueError(
            "prospective qualified-record bindings do not exactly cover durable "
            f"evidence; missing={missing[:5]}, extra={extra[:5]}"
        )
    return (
        len(rebound_subset),
        merged_bindings,
        (durable_protein_registry, reg_digest),
        (durable_evidence_registry, ev_digest),
        (durable_qualified_record_bindings, bind_digest),
    )


def main(argv: list[str] | None = None) -> int:
    import ground_uniprot_examples as gu

    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument(
        "--durable-protein-registry",
        type=Path,
        default=gu.DEFAULT_DURABLE_PROTEIN_REGISTRY,
    )
    parser.add_argument(
        "--durable-evidence-registry",
        type=Path,
        default=gu.DEFAULT_DURABLE_EVIDENCE_REGISTRY,
    )
    parser.add_argument(
        "--durable-qualified-record-bindings",
        type=Path,
        default=gu.DEFAULT_DURABLE_QUALIFIED_RECORD_BINDINGS,
    )
    args = parser.parse_args(argv)
    try:
        from validate_strict import validate_one

        lock_directories = _validate_durable_registry_paths(
            args.durable_protein_registry,
            args.durable_evidence_registry,
            args.durable_qualified_record_bindings,
        )
        with ExitStack() as locks:
            if args.apply:
                for directory in lock_directories:
                    locks.enter_context(layout.registry_lock(directory))

            planned: list[tuple[str, Path, str, str, bool]] = []
            for acc, target in TARGETS.items():
                text = target.read_text(encoding="utf-8")
                # The writer validates changed output, but preview and no-op paths
                # never reach it. Reject invalid inputs before claiming success.
                errors = validate_one(target)
                if errors:
                    raise RecordValidationError(target, errors)
                out = repair_record_text(text, allow_qualified=True)
                if out == text:
                    planned.append((acc, target, text, out, False))
                    continue
                if not should_enrich(text):
                    raise ValueError(f"CDD:{acc}: refusing curated target")
                planned.append((acc, target, text, out, True))

            (
                rebound_count,
                merged_bindings,
                reg_expect,
                ev_expect,
                bind_expect,
            ) = _prepare_qualified_rebindings(
                planned,
                durable_protein_registry=args.durable_protein_registry,
                durable_evidence_registry=args.durable_evidence_registry,
                durable_qualified_record_bindings=args.durable_qualified_record_bindings,
            )

            if args.apply:
                changed_traits = {
                    target: out
                    for _, target, _, out, changed in planned
                    if changed
                }
                if merged_bindings is not None:
                    for label_name, (path, expected_digest) in (
                        ("durable protein registry", reg_expect),
                        ("durable evidence registry", ev_expect),
                        ("durable qualified-record bindings", bind_expect),
                    ):
                        if gu._artifact_digest(path) != expected_digest:
                            raise ValueError(
                                f"{label_name} changed during preflight: {path}"
                            )
                for _acc, target, before_text, _out, _changed in planned:
                    if target.read_text(encoding="utf-8") != before_text:
                        raise ValueError(
                            f"record changed during preflight: {target}"
                        )
                if merged_bindings is not None:
                    gu._install_promotion_transaction(
                        [
                            (
                                args.durable_qualified_record_bindings,
                                gu._registry_text(merged_bindings),
                            )
                        ],
                        changed_traits,
                    )
                elif changed_traits:
                    snapshots = {
                        target.resolve(): (
                            target.read_bytes() if target.is_file() else None
                        )
                        for target in sorted(changed_traits)
                    }
                    attempted: list[Path] = []
                    try:
                        for target, out in sorted(changed_traits.items()):
                            resolved = target.resolve()
                            attempted.append(resolved)
                            write_validated_record(resolved, out, encoding="utf-8")
                    except BaseException:
                        with gu._interrupts_held():
                            for path in reversed(attempted):
                                snapshot = snapshots[path]
                                if snapshot is None:
                                    path.unlink(missing_ok=True)
                                else:
                                    gu._atomic_bytes(path, snapshot)
                        raise

        for acc, _target, _before, _out, changed in planned:
            if not changed:
                print(f"CDD:{acc}: already corrected; no history appended")
                continue
            print(
                f"CDD:{acc}: {'wrote' if args.apply else 'would write'} "
                f"source-definition erratum ({errata.ERRATA[acc].finding_id})"
            )
        if rebound_count:
            print(
                f"qualified_record_bindings: {'re-bound' if args.apply else 'would re-bind'} "
                f"{rebound_count} durable receipt(s) (#1172)"
            )
        return 0
    except (
        OSError,
        ValueError,
        yaml.YAMLError,
        gu.GroundingError,
        layout.RegistryLayoutError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
