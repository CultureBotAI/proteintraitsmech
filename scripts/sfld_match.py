#!/usr/bin/env python3
"""Map one HMMER Stockholm alignment to the pinned SFLD 4 site model.

This module is deliberately a small, read-only bridge between ``hmmalign``
output and :mod:`sfld_release`.  It does not run HMMER, write trait records, or
claim that the aligned sequence passed an HMM gathering threshold.  A caller
must establish the profile hit separately (normally with ``hmmsearch
--cut_ga``); this script only verifies the alignment's model identity, maps HMM
match states to target residues, and evaluates the source's complete correlated
site tuple.

The CLI reads one Stockholm alignment and prints one canonical JSON object to
stdout.  There is intentionally no apply or output-file mode.  The single
target must be the domain subsequence reported by ``hmmsearch`` and must use a
canonical ``parent_identifier/start-end`` identifier.  Site coordinates are
local to that domain subsequence.  The identifier's parent bounds are reported
as unverified metadata; this diagnostic does not bind them to a parent protein.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sfld_release import (
    SFLD_4_HIERARCHY_SHA256,
    SFLD_4_HIERARCHY_SOURCE_ARTIFACT,
    SFLD_4_HMM_SHA256,
    SFLD_4_HMM_SOURCE_ARTIFACT,
    SFLD_4_PROFILE_SEARCH_MODE,
    SFLD_4_SITES_SHA256,
    SFLD_4_SITES_SOURCE_ARTIFACT,
    SfldRelease,
    SfldReleaseError,
    build_sfld_release_manifest,
    canonical_json,
    load_sfld_release,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent
_ALIGNMENT_FRAGMENT_RE = re.compile(r"^[A-Za-z.-]+$")
_DOMAIN_TARGET_IDENTIFIER_RE = re.compile(
    r"^(?P<parent_sequence_identifier>[^/\s]+)/"
    r"(?P<reported_parent_start>[1-9][0-9]*)-"
    r"(?P<reported_parent_end>[1-9][0-9]*)$"
)
_STANDARD_AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")


class SfldMatchError(ValueError):
    """The alignment cannot support an unambiguous SFLD site evaluation."""


@dataclass(frozen=True, slots=True)
class StockholmAlignment:
    """One logical target and RF annotation parsed from a Stockholm block."""

    model_accession: str
    target_identifier: str
    parent_sequence_identifier: str
    reported_parent_start: int
    reported_parent_end: int
    aligned_target: str
    reference_annotation: str
    source_sha256: str


@dataclass(frozen=True, slots=True)
class MatchStateResidue:
    """One HMM match state and its domain-local coordinate, if not deleted."""

    model_position: int
    alignment_column: int
    domain_subsequence_position: int | None
    residue: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "alignment_column": self.alignment_column,
            "domain_subsequence_position": self.domain_subsequence_position,
            "model_position": self.model_position,
            "residue": self.residue,
        }


def _stockholm_error(line_number: int | None, message: str) -> SfldMatchError:
    where = f"Stockholm line {line_number}: " if line_number is not None else "Stockholm: "
    return SfldMatchError(where + message)


def parse_hmmer_stockholm(text: str) -> StockholmAlignment:
    """Parse one wrapped/interleaved HMMER Stockholm alignment fail-closed.

    Sequence and ``#=GC RF`` fragments may recur in interleaved blocks.  Every
    non-empty logical alignment block must contain exactly one target fragment,
    followed by exactly one equal-length RF fragment.  The same canonical
    domain target identifier must be used in every block.  ``#=GF AC`` is
    mandatory because it is the source-model identity checked by the evaluator.
    """

    if not isinstance(text, str):
        raise SfldMatchError("Stockholm input must be text")
    try:
        raw = text.encode("ascii", errors="strict")
    except UnicodeEncodeError as error:
        raise SfldMatchError("Stockholm input contains non-ASCII characters") from error

    lines = text.splitlines()
    if not lines:
        raise _stockholm_error(None, "empty input")
    if lines[0] != "# STOCKHOLM 1.0":
        raise _stockholm_error(1, "expected exact '# STOCKHOLM 1.0' header")

    model_accessions: list[tuple[int, str]] = []
    target_identifier: str | None = None
    target_parts: list[str] = []
    rf_fragments: list[str] = []
    referenced_sequence_ids: list[tuple[int, str]] = []
    terminated = False
    block_target: tuple[int, str, str] | None = None
    block_rf: tuple[int, str] | None = None

    def finish_alignment_block(line_number: int | None) -> None:
        nonlocal block_target, block_rf, target_identifier
        if block_target is None and block_rf is None:
            return
        if block_target is None:
            raise _stockholm_error(
                line_number,
                "alignment block has #=GC RF fragment but no target fragment",
            )
        if block_rf is None:
            raise _stockholm_error(
                line_number,
                "alignment block has target fragment but no #=GC RF fragment",
            )
        target_line, identifier, target_fragment = block_target
        rf_line, rf_fragment = block_rf
        if len(target_fragment) != len(rf_fragment):
            raise _stockholm_error(
                rf_line,
                "target and #=GC RF fragments in one alignment block have different "
                f"lengths ({len(target_fragment)} != {len(rf_fragment)})",
            )
        if target_identifier is None:
            target_identifier = identifier
        elif identifier != target_identifier:
            raise _stockholm_error(
                target_line,
                "expected exactly one target sequence; alignment blocks name "
                f"{target_identifier!r} and {identifier!r}",
            )
        target_parts.append(target_fragment)
        rf_fragments.append(rf_fragment)
        block_target = None
        block_rf = None

    for line_number, line in enumerate(lines[1:], 2):
        if terminated:
            if line.strip():
                raise _stockholm_error(line_number, "content follows the // terminator")
            continue
        if line == "//":
            finish_alignment_block(line_number)
            terminated = True
            continue
        if not line.strip():
            finish_alignment_block(line_number)
            continue
        if line.startswith("#=GF"):
            parts = line.split(maxsplit=2)
            if len(parts) != 3:
                raise _stockholm_error(line_number, "malformed #=GF annotation")
            if parts[1] == "AC":
                value = parts[2].strip()
                if not value or any(character.isspace() for character in value):
                    raise _stockholm_error(line_number, "#=GF AC must contain one accession")
                model_accessions.append((line_number, value))
            continue
        if line.startswith("#=GC"):
            parts = line.split(maxsplit=2)
            if len(parts) != 3:
                raise _stockholm_error(line_number, "malformed #=GC annotation")
            if parts[1] == "RF":
                fragment = parts[2]
                if _ALIGNMENT_FRAGMENT_RE.fullmatch(fragment) is None:
                    raise _stockholm_error(line_number, "invalid #=GC RF fragment")
                if block_target is None:
                    raise _stockholm_error(
                        line_number,
                        "#=GC RF fragment appears before its target fragment in an alignment block",
                    )
                if block_rf is not None:
                    raise _stockholm_error(
                        line_number,
                        "alignment block contains duplicate #=GC RF fragments",
                    )
                block_rf = (line_number, fragment)
            continue
        if line.startswith("#=GR") or line.startswith("#=GS"):
            parts = line.split(maxsplit=3)
            if len(parts) < 3:
                raise _stockholm_error(line_number, "malformed per-sequence annotation")
            referenced_sequence_ids.append((line_number, parts[1]))
            continue
        if line.startswith("#"):
            continue

        parts = line.split()
        if len(parts) != 2:
            raise _stockholm_error(
                line_number, "expected target_identifier aligned_sequence_fragment"
            )
        identifier, fragment = parts
        if _ALIGNMENT_FRAGMENT_RE.fullmatch(fragment) is None:
            raise _stockholm_error(line_number, "invalid aligned target fragment")
        if block_rf is not None:
            raise _stockholm_error(
                line_number,
                "target fragment appears after #=GC RF in an alignment block",
            )
        if block_target is not None:
            raise _stockholm_error(
                line_number,
                "alignment block contains duplicate target fragments",
            )
        block_target = (line_number, identifier, fragment)

    if not terminated:
        raise _stockholm_error(None, "missing // terminator")
    if len(model_accessions) != 1:
        raise _stockholm_error(
            None,
            f"expected exactly one #=GF AC annotation; found {len(model_accessions)}",
        )
    if target_identifier is None:
        raise _stockholm_error(
            None,
            "expected exactly one target sequence; found 0",
        )
    if not rf_fragments:
        raise _stockholm_error(None, "expected exactly one logical #=GC RF annotation")

    for line_number, referenced_identifier in referenced_sequence_ids:
        if referenced_identifier != target_identifier:
            raise _stockholm_error(
                line_number,
                "per-sequence annotation names a target absent from the alignment",
            )
    aligned_target = "".join(target_parts)
    reference_annotation = "".join(rf_fragments)
    if len(aligned_target) != len(reference_annotation):
        raise _stockholm_error(
            None,
            "concatenated target and #=GC RF annotations have different lengths "
            f"({len(aligned_target)} != {len(reference_annotation)})",
        )
    if not any(character not in ".-" for character in aligned_target):
        raise _stockholm_error(None, "target contains no residues")
    if not any(character not in ".-" for character in reference_annotation):
        raise _stockholm_error(None, "#=GC RF contains no model match states")

    target_match = _DOMAIN_TARGET_IDENTIFIER_RE.fullmatch(target_identifier)
    if target_match is None:
        raise _stockholm_error(
            None,
            "target identifier must have canonical parent_identifier/start-end form "
            "with positive decimal bounds",
        )
    reported_parent_start = int(target_match.group("reported_parent_start"))
    reported_parent_end = int(target_match.group("reported_parent_end"))
    if reported_parent_start > reported_parent_end:
        raise _stockholm_error(
            None,
            "target identifier start bound must not exceed end bound",
        )
    ungapped_residue_count = sum(character not in ".-" for character in aligned_target)
    reported_span = reported_parent_end - reported_parent_start + 1
    if reported_span != ungapped_residue_count:
        raise _stockholm_error(
            None,
            "target identifier span must equal the ungapped domain subsequence length "
            f"({reported_span} != {ungapped_residue_count})",
        )

    return StockholmAlignment(
        model_accession=model_accessions[0][1],
        target_identifier=target_identifier,
        parent_sequence_identifier=target_match.group("parent_sequence_identifier"),
        reported_parent_start=reported_parent_start,
        reported_parent_end=reported_parent_end,
        aligned_target=aligned_target,
        reference_annotation=reference_annotation,
        source_sha256=hashlib.sha256(raw).hexdigest(),
    )


def map_model_match_states(
    alignment: StockholmAlignment,
    *,
    expected_model_length: int,
) -> tuple[MatchStateResidue, ...]:
    """Map RF match columns to successive model states and target residues.

    Any RF character other than Stockholm gap markers ``.`` and ``-`` denotes a
    model match state.  Domain-subsequence positions count every non-gap
    residue, including residues in insertion columns, and are 1-based.
    """

    if expected_model_length < 1:
        raise SfldMatchError("expected model length must be positive")
    if len(alignment.aligned_target) != len(alignment.reference_annotation):
        raise SfldMatchError("target/RF length mismatch in parsed alignment")

    model_position = 0
    domain_subsequence_position = 0
    mapping: list[MatchStateResidue] = []
    for alignment_column, (target_symbol, rf_symbol) in enumerate(
        zip(alignment.aligned_target, alignment.reference_annotation, strict=True),
        1,
    ):
        target_is_gap = target_symbol in ".-"
        if not target_is_gap:
            domain_subsequence_position += 1
        if rf_symbol in ".-":
            continue
        model_position += 1
        mapping.append(
            MatchStateResidue(
                model_position=model_position,
                alignment_column=alignment_column,
                domain_subsequence_position=(
                    None if target_is_gap else domain_subsequence_position
                ),
                residue=None if target_is_gap else target_symbol.upper(),
            )
        )

    if model_position != expected_model_length:
        raise SfldMatchError(
            "RF model length mismatch: alignment contains "
            f"{model_position} match states, pinned model contains {expected_model_length}"
        )
    return tuple(mapping)


def _ancestor_chain(release: SfldRelease, direct_accession: str) -> tuple[str, ...]:
    declared = set(release.ancestors.get(direct_accession, ()))
    chain: list[str] = []
    seen = {direct_accession}
    cursor = direct_accession
    while cursor in release.direct_parents:
        parent = release.direct_parents[cursor]
        if parent in seen:
            raise SfldMatchError(f"SFLD hierarchy cycle reaches {parent}")
        if parent not in release.models:
            raise SfldMatchError(f"SFLD hierarchy parent {parent} has no pinned model")
        chain.append(parent)
        seen.add(parent)
        cursor = parent
    if set(chain) != declared or len(chain) != len(declared):
        raise SfldMatchError(
            f"SFLD hierarchy closure mismatch for {direct_accession}: "
            f"chain={chain!r}, declared={sorted(declared)!r}"
        )
    return tuple(chain)


def evaluate_sfld_alignment(
    release: SfldRelease,
    model_accession: str,
    alignment: StockholmAlignment,
) -> dict[str, Any]:
    """Evaluate one direct model's complete correlated site tuple.

    Diagnostic potential ancestors are emitted only when the direct correlated
    site tuple matches (or the model has no sites).  Every projection remains
    explicitly grounding-ineligible and profile-unqualified.  Projections
    intentionally contain no alignment mapping, coordinates, residues, site
    descriptions, or site evidence: SFLD site evidence is direct-model-only.
    """

    model = release.models.get(model_accession)
    if model is None:
        raise SfldMatchError(f"requested model {model_accession!r} is absent from the release")
    if model.accession != model_accession:
        raise SfldMatchError(
            f"release model key/accession mismatch for {model_accession}: {model.accession!r}"
        )
    if alignment.model_accession != model_accession:
        raise SfldMatchError(
            "Stockholm #=GF AC source mismatch: requested "
            f"{model_accession}, alignment declares {alignment.model_accession}"
        )
    site_rule = release.site_rules.get(model_accession)
    if site_rule is None:
        raise SfldMatchError(f"requested model {model_accession} has no pinned site block")
    if site_rule.accession != model_accession:
        raise SfldMatchError(
            f"release site-rule key/accession mismatch for {model_accession}: "
            f"{site_rule.accession!r}"
        )

    mapping = map_model_match_states(alignment, expected_model_length=model.model_length)
    mapped_sites: list[dict[str, Any]] = []
    observed_residues: list[str] = []
    for site in site_rule.sites:
        if site.model_position < 1 or site.model_position > len(mapping):
            raise SfldMatchError(
                f"SFLD {model_accession} SITE {site.ordinal} position "
                f"{site.model_position} is outside the model"
            )
        match_state = mapping[site.model_position - 1]
        if match_state.domain_subsequence_position is None or match_state.residue is None:
            raise SfldMatchError(
                f"target deletion at annotated SFLD {model_accession} match state "
                f"{site.model_position}"
            )
        if match_state.residue not in _STANDARD_AMINO_ACIDS:
            raise SfldMatchError(
                f"ambiguous target residue {match_state.residue!r} at annotated SFLD "
                f"{model_accession} match state {site.model_position}"
            )
        observed_residues.append(match_state.residue)
        mapped_sites.append(
            {
                "description": site.description,
                "domain_subsequence_position": match_state.domain_subsequence_position,
                "model_position": site.model_position,
                "ordinal": site.ordinal,
                "residue": match_state.residue,
            }
        )

    observed_tuple = "".join(observed_residues) if mapped_sites else None
    if mapped_sites:
        correlated_site_tuple_matched = observed_tuple in site_rule.feature_patterns
        site_rule_status = (
            "MATCHED_CORRELATED_TUPLE"
            if correlated_site_tuple_matched
            else "MISMATCHED_CORRELATED_TUPLE"
        )
        site_evidence: dict[str, Any] | None = {
            "mapped_sites": mapped_sites,
            "matched_feature_pattern": (observed_tuple if correlated_site_tuple_matched else None),
            "observed_residue_tuple": observed_tuple,
            "source_site_record_sha256": site_rule.source_record_sha256,
        }
    else:
        if site_rule.feature_patterns:
            raise SfldMatchError(
                f"SFLD {model_accession} has FEATURE tuples but no annotated sites"
            )
        correlated_site_tuple_matched = True
        site_rule_status = "NO_SITES_DECLARED"
        site_evidence = None

    manifest = build_sfld_release_manifest(release)
    ancestors = _ancestor_chain(release, model_accession)
    diagnostic_potential_ancestor_projections: list[dict[str, Any]] = []
    if correlated_site_tuple_matched:
        for distance, accession in enumerate(ancestors, 1):
            ancestor_model = release.models[accession]
            diagnostic_potential_ancestor_projections.append(
                {
                    "accession": accession,
                    "distance_from_direct_model": distance,
                    "grounding_eligible": False,
                    "native_classification_level": ancestor_model.native_classification_level,
                    "profile_threshold_qualified": None,
                    "projection_basis": "SFLD_HIERARCHY_FROM_DIRECT_MODEL",
                    "source_model_record_sha256": ancestor_model.source_record_sha256,
                }
            )

    ungapped_length = sum(character not in ".-" for character in alignment.aligned_target)
    return {
        "artifact_kind": "SFLD_DIRECT_MODEL_ALIGNMENT_SITE_EVALUATION",
        "diagnostic_potential_ancestor_projections": (diagnostic_potential_ancestor_projections),
        "grounding_eligible": False,
        "qualification_status": "DIAGNOSTIC_ALIGNMENT_ONLY_NOT_PROFILE_QUALIFIED",
        "direct_model_evaluation": {
            "accession": model_accession,
            "alignment_mapping": [entry.as_dict() for entry in mapping],
            "gathering_domain_score": model.gathering_domain_score,
            "gathering_sequence_score": model.gathering_sequence_score,
            "model_length": model.model_length,
            "native_classification_level": model.native_classification_level,
            "profile_search_mode": SFLD_4_PROFILE_SEARCH_MODE,
            "profile_threshold_evaluation": "NOT_PROVIDED_ALIGNMENT_ONLY",
            "profile_threshold_qualified": None,
            "site_evidence": site_evidence,
            "correlated_site_tuple_matched": correlated_site_tuple_matched,
            "site_rule_status": site_rule_status,
            "source_model_record_sha256": model.source_record_sha256,
        },
        "schema_version": 1,
        "source_binding": {
            "hierarchy_artifact_sha256": release.hierarchy_sha256,
            "hmm_artifact_sha256": release.hmm_sha256,
            "manifest_sha256": manifest["manifest_sha256"],
            "sites_artifact_sha256": release.sites_sha256,
            "source_release": release.release,
        },
        "target": {
            "aligned_column_count": len(alignment.aligned_target),
            "alignment_source_sha256": alignment.source_sha256,
            "coordinate_basis": "ONE_BASED_HMMSEARCH_DOMAIN_SUBSEQUENCE",
            "identifier": alignment.target_identifier,
            "parent_sequence_binding_verified": False,
            "parent_sequence_identifier": alignment.parent_sequence_identifier,
            "reported_parent_end": alignment.reported_parent_end,
            "reported_parent_start": alignment.reported_parent_start,
            "ungapped_residue_count": ungapped_length,
        },
    }


def _read_alignment(path_text: str) -> str:
    try:
        raw = sys.stdin.buffer.read() if path_text == "-" else Path(path_text).read_bytes()
    except OSError as error:
        raise SfldMatchError(f"cannot read Stockholm alignment {path_text}: {error}") from error
    try:
        return raw.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise SfldMatchError(f"Stockholm alignment {path_text} contains non-ASCII bytes") from error


def main(argv: list[str] | None = None) -> int:
    """Load pinned SFLD sources and print one canonical alignment evaluation."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--alignment",
        required=True,
        help="HMMER Stockholm alignment path, or - for stdin.",
    )
    parser.add_argument("--model-accession", required=True, help="Exact SFLD model accession.")
    parser.add_argument(
        "--hmm",
        type=Path,
        default=_REPO_ROOT / SFLD_4_HMM_SOURCE_ARTIFACT,
        help="Pinned SFLD 4 HMM artifact.",
    )
    parser.add_argument(
        "--hierarchy",
        type=Path,
        default=_REPO_ROOT / SFLD_4_HIERARCHY_SOURCE_ARTIFACT,
        help="Pinned SFLD 4 hierarchy artifact.",
    )
    parser.add_argument(
        "--sites",
        type=Path,
        default=_REPO_ROOT / SFLD_4_SITES_SOURCE_ARTIFACT,
        help="Pinned SFLD 4 correlated-site artifact.",
    )
    args = parser.parse_args(argv)

    try:
        alignment = parse_hmmer_stockholm(_read_alignment(args.alignment))
        release = load_sfld_release(
            args.hmm,
            args.hierarchy,
            args.sites,
            expected_hmm_sha256=SFLD_4_HMM_SHA256,
            expected_hierarchy_sha256=SFLD_4_HIERARCHY_SHA256,
            expected_sites_sha256=SFLD_4_SITES_SHA256,
        )
        evaluation = evaluate_sfld_alignment(release, args.model_accession, alignment)
    except (SfldMatchError, SfldReleaseError) as error:
        print(f"SFLD match evaluation failed: {error}", file=sys.stderr)
        return 1
    print(canonical_json(evaluation))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
