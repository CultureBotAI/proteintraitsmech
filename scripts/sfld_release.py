#!/usr/bin/env python3
"""Fail-closed parser and manifest contract for the archived SFLD 4 release.

SFLD 4 is not one interchangeable "family" list.  Its executable source model
is the conjunction of three files: HMMER3 profiles with gathering thresholds,
correlated catalytic-site residue tuples, and a transitive hierarchy.  This
module verifies and parses those files without consulting mutable InterPro API
metadata or changing any trait record.

The site ``FEATURE`` rows are deliberately retained as whole ordered tuples.
Flattening them into independent allowed residues at each position would admit
residue combinations that SFLD never declared.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

SFLD_4_RELEASE = "4"

SFLD_4_HMM_SOURCE_ARTIFACT = "data/raw/interpro_members/sfld.hmm"
SFLD_4_HIERARCHY_SOURCE_ARTIFACT = "data/raw/interpro_members/sfld_hierarchy_flat.txt"
SFLD_4_SITES_SOURCE_ARTIFACT = "data/raw/interpro_members/sfld_sites.annot"
SFLD_4_MANIFEST_SOURCE_ARTIFACT = "data/raw/interpro_members/sfld_release_manifest.json"

SFLD_4_HMM_URL = "https://ftp.ebi.ac.uk/pub/databases/interpro/databases/sfld/4/sfld.hmm"
SFLD_4_HIERARCHY_URL = (
    "https://ftp.ebi.ac.uk/pub/databases/interpro/databases/sfld/4/sfld_hierarchy_flat.txt"
)
SFLD_4_SITES_URL = "https://ftp.ebi.ac.uk/pub/databases/interpro/databases/sfld/4/sfld_sites.annot"

SFLD_4_HMM_SHA256 = "e011a4139e6477a526710b32e8aeaa68203329c799305b015ec35c3b6d09672f"
SFLD_4_HIERARCHY_SHA256 = "e9d379421227fb9eb3c5eb259d2a925c321a7bf1e697055d361f7397b53f86b9"
SFLD_4_SITES_SHA256 = "60ee2408e5bb2bed2eba4ee2101e219b74dcee7abb2bc03aba9e3e905dcf8c66"

SFLD_4_REPRESENTATION_TYPE = "SFLD_4_HMMER3_PROFILE_WITH_CORRELATED_SITES"
SFLD_4_PROFILE_SEARCH_MODE = "HMMSEARCH_CUT_GA"
SFLD_4_SITE_COORDINATE_SYSTEM = "HMM_MODEL_MATCH_STATE"
SFLD_4_SITE_EVIDENCE_SCOPE = "DIRECT_MODEL_MATCH_ONLY"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ACCESSION_RE = re.compile(r"^SFLD([SGF])[0-9]{5}$")
_AA_PATTERN_RE = re.compile(r"^[ACDEFGHIKLMNPQRSTVWY]+$")
_SITE_RE = re.compile(r"^SITE\s+([0-9]+)(?:\s+(.*?))?\s*$")
_HMM_ALPHABET = tuple("ACDEFGHIKLMNPQRSTVWY")
_HMM_TRANSITIONS = ("m->m", "m->i", "m->d", "i->m", "i->i", "d->m", "d->d")

_LEVELS = {
    "S": "SUPERFAMILY",
    "G": "SUBGROUP",
    "F": "FAMILY",
}

_REPO_ROOT = Path(__file__).resolve().parent.parent


class SfldReleaseError(ValueError):
    """One or more SFLD source artifacts violate the pinned release contract."""


class SfldChecksumError(SfldReleaseError):
    """An SFLD artifact does not match its caller-supplied SHA-256."""


@dataclass(frozen=True, slots=True)
class SfldHmmModel:
    """Metadata needed to replay one source-native HMMER3 model."""

    accession: str
    native_classification_level: str
    name: str
    description: str
    model_length: int
    gathering_sequence_score: float
    gathering_domain_score: float
    training_sequence_count: int
    hmm_checksum: int
    source_record_sha256: str


@dataclass(frozen=True, slots=True)
class SfldSite:
    """One SFLD catalytic/functional site in HMM match-state coordinates."""

    ordinal: int
    model_position: int
    description: str | None


@dataclass(frozen=True, slots=True)
class SfldSiteRule:
    """Correlated allowed residue tuples for one model's ordered sites."""

    accession: str
    sites: tuple[SfldSite, ...]
    feature_patterns: tuple[str, ...]
    source_record_sha256: str


@dataclass(frozen=True, slots=True)
class SfldRelease:
    """The verified three-artifact SFLD 4 source model."""

    release: str
    hmm_path: Path
    hierarchy_path: Path
    sites_path: Path
    hmm_sha256: str
    hierarchy_sha256: str
    sites_sha256: str
    models: Mapping[str, SfldHmmModel]
    site_rules: Mapping[str, SfldSiteRule]
    ancestors: Mapping[str, tuple[str, ...]]
    direct_parents: Mapping[str, str]


def _read_pinned(path: str | Path, expected_sha256: str, label: str) -> tuple[Path, bytes, str]:
    source_path = Path(path)
    if _SHA256_RE.fullmatch(expected_sha256) is None:
        raise SfldReleaseError(
            f"expected {label} SHA-256 must be 64 lower-case hexadecimal characters: "
            f"{expected_sha256!r}"
        )
    if not source_path.is_file():
        raise SfldReleaseError(f"missing pinned SFLD {label} artifact: {source_path}")
    try:
        raw = source_path.read_bytes()
    except OSError as error:
        raise SfldReleaseError(
            f"cannot read SFLD {label} artifact {source_path}: {error}"
        ) from error
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise SfldChecksumError(
            f"SFLD {label} checksum mismatch for {source_path}: expected "
            f"{expected_sha256}, got {actual}"
        )
    return source_path, raw, actual


def _ascii(raw: bytes, path: Path, context: str) -> str:
    try:
        return raw.decode("ascii", errors="strict")
    except UnicodeDecodeError as error:
        raise SfldReleaseError(f"{path}: non-ASCII bytes in {context}") from error


def _accession_level(accession: str, path: Path, context: str) -> str:
    match = _ACCESSION_RE.fullmatch(accession)
    if match is None:
        raise SfldReleaseError(f"{path}: invalid SFLD accession {accession!r} in {context}")
    return _LEVELS[match.group(1)]


def _required_header(headers: Mapping[str, str], key: str, path: Path, accession: str) -> str:
    value = headers.get(key)
    if value is None or not value.strip():
        raise SfldReleaseError(f"{path}: model {accession} has no {key} header")
    return value.strip()


def _parse_positive_int(value: str, path: Path, accession: str, field: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise SfldReleaseError(
            f"{path}: model {accession} has non-integer {field} {value!r}"
        ) from error
    if number < 1:
        raise SfldReleaseError(f"{path}: model {accession} has non-positive {field}")
    return number


def _require_hmm_scores(
    values: list[str],
    expected_count: int,
    path: Path,
    accession: str,
    context: str,
) -> None:
    if len(values) != expected_count:
        raise SfldReleaseError(
            f"{path}: model {accession} {context} contains {len(values)} scores; "
            f"expected {expected_count}"
        )
    for value in values:
        if value == "*":
            continue
        try:
            score = float(value)
        except ValueError as error:
            raise SfldReleaseError(
                f"{path}: model {accession} {context} has invalid score {value!r}"
            ) from error
        if not math.isfinite(score):
            raise SfldReleaseError(f"{path}: model {accession} {context} has non-finite score")


def _validate_hmm_matrix(
    lines: list[str], matrix_start: int, model_length: int, path: Path, accession: str
) -> None:
    alphabet = lines[matrix_start].split()[1:]
    if alphabet != list(_HMM_ALPHABET):
        raise SfldReleaseError(f"{path}: model {accession} has unexpected HMM alphabet order")
    cursor = matrix_start + 1
    if cursor >= len(lines) - 1 or tuple(lines[cursor].split()) != _HMM_TRANSITIONS:
        raise SfldReleaseError(f"{path}: model {accession} has invalid transition header")
    cursor += 1

    if cursor >= len(lines) - 1:
        raise SfldReleaseError(f"{path}: model {accession} has no COMPO row")
    composition = lines[cursor].split()
    if not composition or composition[0] != "COMPO":
        raise SfldReleaseError(f"{path}: model {accession} has no COMPO row")
    _require_hmm_scores(composition[1:], 20, path, accession, "COMPO row")
    cursor += 1
    if cursor + 1 >= len(lines) - 1:
        raise SfldReleaseError(f"{path}: model {accession} has truncated COMPO rows")
    _require_hmm_scores(lines[cursor].split(), 20, path, accession, "COMPO insertion row")
    cursor += 1
    _require_hmm_scores(lines[cursor].split(), 7, path, accession, "COMPO transition row")
    cursor += 1

    for expected_position in range(1, model_length + 1):
        if cursor + 2 >= len(lines) - 1:
            raise SfldReleaseError(
                f"{path}: model {accession} matrix is truncated before match state "
                f"{expected_position}"
            )
        match_tokens = lines[cursor].split()
        if len(match_tokens) != 26:
            raise SfldReleaseError(
                f"{path}: model {accession} match state {expected_position} has "
                f"{len(match_tokens)} fields; expected 26"
            )
        try:
            observed_position = int(match_tokens[0])
        except ValueError as error:
            raise SfldReleaseError(
                f"{path}: model {accession} has non-integer match-state position"
            ) from error
        if observed_position != expected_position:
            raise SfldReleaseError(
                f"{path}: model {accession} matrix positions are not contiguous 1..{model_length}"
            )
        _require_hmm_scores(
            match_tokens[1:21], 20, path, accession, f"match state {expected_position}"
        )
        map_token, consensus, reference, mask, structure = match_tokens[21:]
        if map_token != "-":
            try:
                if int(map_token) < 1:
                    raise ValueError
            except ValueError as error:
                raise SfldReleaseError(
                    f"{path}: model {accession} match state {expected_position} has invalid MAP"
                ) from error
        if len(consensus) != 1 or len(reference) != 1 or mask != "-" or structure != "-":
            raise SfldReleaseError(
                f"{path}: model {accession} match state {expected_position} has invalid "
                "annotation fields"
            )
        cursor += 1
        _require_hmm_scores(
            lines[cursor].split(),
            20,
            path,
            accession,
            f"match state {expected_position} insertion row",
        )
        cursor += 1
        _require_hmm_scores(
            lines[cursor].split(),
            7,
            path,
            accession,
            f"match state {expected_position} transition row",
        )
        cursor += 1
    if cursor != len(lines) - 1 or lines[-1] != "//":
        raise SfldReleaseError(
            f"{path}: model {accession} has trailing or unterminated matrix data"
        )


def _split_hmm_records(raw: bytes, path: Path) -> list[bytes]:
    lines = raw.splitlines(keepends=True)
    if not lines:
        raise SfldReleaseError(f"{path}: empty HMM artifact")
    records: list[bytes] = []
    current: list[bytes] = []
    for line_number, line in enumerate(lines, 1):
        stripped = line.rstrip(b"\r\n")
        if not current:
            if not stripped.startswith(b"HMMER3/f "):
                raise SfldReleaseError(f"{path}:{line_number}: expected HMMER3/f record opener")
            current.append(line)
            continue
        if stripped.startswith(b"HMMER3/f "):
            raise SfldReleaseError(f"{path}:{line_number}: prior HMM record lacks // terminator")
        current.append(line)
        if stripped == b"//":
            records.append(b"".join(current))
            current = []
    if current:
        raise SfldReleaseError(f"{path}: final HMM record lacks // terminator")
    if not records:
        raise SfldReleaseError(f"{path}: no HMM records found")
    return records


def parse_sfld_hmm(
    path: str | Path,
    expected_sha256: str,
) -> tuple[Path, str, dict[str, SfldHmmModel]]:
    """Parse checksum-pinned HMMER3/f records and source GA thresholds."""

    source_path, raw, actual_sha256 = _read_pinned(path, expected_sha256, "HMM")
    models: dict[str, SfldHmmModel] = {}
    for record_number, record_raw in enumerate(_split_hmm_records(raw, source_path), 1):
        lines = [
            _ascii(line.rstrip(b"\r\n"), source_path, f"HMM record {record_number}")
            for line in record_raw.splitlines(keepends=True)
        ]
        try:
            matrix_start = next(
                index for index, line in enumerate(lines) if line.startswith("HMM ")
            )
        except StopIteration as error:
            raise SfldReleaseError(
                f"{source_path}: HMM record {record_number} has no HMM matrix header"
            ) from error

        headers: dict[str, str] = {}
        for line in lines[1:matrix_start]:
            if not line.strip():
                raise SfldReleaseError(
                    f"{source_path}: blank line in HMM record {record_number} header"
                )
            key, _, value = line.partition(" ")
            if key == "STATS":
                continue
            if key in headers:
                raise SfldReleaseError(
                    f"{source_path}: duplicate {key} header in HMM record {record_number}"
                )
            headers[key] = value.strip()

        accession = _required_header(headers, "ACC", source_path, f"record {record_number}")
        level = _accession_level(accession, source_path, "HMM header")
        if accession in models:
            raise SfldReleaseError(f"{source_path}: duplicate HMM accession {accession}")
        name = _required_header(headers, "NAME", source_path, accession)
        description = _required_header(headers, "DESC", source_path, accession)
        model_length = _parse_positive_int(
            _required_header(headers, "LENG", source_path, accession),
            source_path,
            accession,
            "LENG",
        )
        nseq = _parse_positive_int(
            _required_header(headers, "NSEQ", source_path, accession),
            source_path,
            accession,
            "NSEQ",
        )
        checksum = _parse_positive_int(
            _required_header(headers, "CKSUM", source_path, accession),
            source_path,
            accession,
            "CKSUM",
        )
        if checksum > 0xFFFFFFFF:
            raise SfldReleaseError(f"{source_path}: model {accession} CKSUM exceeds uint32")
        if _required_header(headers, "ALPH", source_path, accession) != "amino":
            raise SfldReleaseError(f"{source_path}: model {accession} is not an amino-acid HMM")
        for field, expected in {"MM": "no", "CONS": "yes", "MAP": "yes"}.items():
            if _required_header(headers, field, source_path, accession) != expected:
                raise SfldReleaseError(
                    f"{source_path}: model {accession} {field} is not exactly {expected!r}"
                )

        ga_parts = _required_header(headers, "GA", source_path, accession).split()
        if len(ga_parts) != 2:
            raise SfldReleaseError(
                f"{source_path}: model {accession} GA must contain sequence and domain scores"
            )
        try:
            ga_sequence, ga_domain = (float(part) for part in ga_parts)
        except ValueError as error:
            raise SfldReleaseError(
                f"{source_path}: model {accession} has non-numeric GA threshold"
            ) from error
        if not math.isfinite(ga_sequence) or not math.isfinite(ga_domain):
            raise SfldReleaseError(f"{source_path}: model {accession} has non-finite GA threshold")

        _validate_hmm_matrix(lines, matrix_start, model_length, source_path, accession)

        models[accession] = SfldHmmModel(
            accession=accession,
            native_classification_level=level,
            name=name,
            description=description,
            model_length=model_length,
            gathering_sequence_score=ga_sequence,
            gathering_domain_score=ga_domain,
            training_sequence_count=nseq,
            hmm_checksum=checksum,
            source_record_sha256=hashlib.sha256(record_raw).hexdigest(),
        )
    return source_path, actual_sha256, models


def parse_sfld_sites(
    path: str | Path,
    expected_sha256: str,
) -> tuple[Path, str, dict[str, SfldSiteRule]]:
    """Parse SFLD 1.1 site annotations, retaining correlated FEATURE tuples."""

    source_path, raw, actual_sha256 = _read_pinned(path, expected_sha256, "sites")
    lines = raw.splitlines(keepends=True)
    required_header = (
        b"## MSA feature annotation file",
        b"# Format version: 1.1",
        b"# MSA file: sfld.msa",
    )
    if len(lines) < 5:
        raise SfldReleaseError(f"{source_path}: truncated site annotation artifact")
    for index, expected in enumerate(required_header):
        if lines[index].rstrip(b"\r\n") != expected:
            raise SfldReleaseError(f"{source_path}:{index + 1}: unexpected site annotation header")
    if not lines[3].rstrip(b"\r\n").startswith(b"# Date "):
        raise SfldReleaseError(f"{source_path}:4: missing site annotation date")

    rules: dict[str, SfldSiteRule] = {}
    index = 4
    while index < len(lines):
        raw_line = lines[index]
        line_number = index + 1
        line = _ascii(raw_line.rstrip(b"\r\n"), source_path, "site annotation")
        parts = line.split()
        if len(parts) != 4 or parts[0] != "ACC":
            raise SfldReleaseError(
                f"{source_path}:{line_number}: expected ACC accession site_count feature_count"
            )
        accession = parts[1]
        _accession_level(accession, source_path, "site annotation")
        if accession in rules:
            raise SfldReleaseError(f"{source_path}:{line_number}: duplicate ACC {accession}")
        try:
            site_count, feature_count = int(parts[2]), int(parts[3])
        except ValueError as error:
            raise SfldReleaseError(
                f"{source_path}:{line_number}: non-integer site/feature count"
            ) from error
        if site_count < 0 or feature_count < 0:
            raise SfldReleaseError(f"{source_path}:{line_number}: negative site/feature count")

        block_lines = [raw_line]
        sites: list[SfldSite] = []
        patterns: list[str] = []
        index += 1
        saw_feature = False
        while index < len(lines) and not lines[index].startswith(b"ACC "):
            block_raw = lines[index]
            block_lines.append(block_raw)
            block_line_number = index + 1
            block = _ascii(block_raw.rstrip(b"\r\n"), source_path, "site annotation block")
            if block.startswith("SITE"):
                if saw_feature:
                    raise SfldReleaseError(
                        f"{source_path}:{block_line_number}: SITE follows FEATURE in {accession}"
                    )
                match = _SITE_RE.fullmatch(block)
                if match is None:
                    raise SfldReleaseError(f"{source_path}:{block_line_number}: malformed SITE row")
                position = int(match.group(1))
                if position < 1:
                    raise SfldReleaseError(
                        f"{source_path}:{block_line_number}: non-positive SITE position"
                    )
                description = match.group(2)
                description = description.strip() if description else None
                sites.append(
                    SfldSite(
                        ordinal=len(sites) + 1,
                        model_position=position,
                        description=description or None,
                    )
                )
            elif block.startswith("FEATURE "):
                saw_feature = True
                pattern = block.removeprefix("FEATURE ").strip()
                if _AA_PATTERN_RE.fullmatch(pattern) is None:
                    raise SfldReleaseError(
                        f"{source_path}:{block_line_number}: invalid FEATURE residue tuple"
                    )
                patterns.append(pattern)
            else:
                raise SfldReleaseError(
                    f"{source_path}:{block_line_number}: unexpected site annotation row"
                )
            index += 1

        if len(sites) != site_count or len(patterns) != feature_count:
            raise SfldReleaseError(
                f"{source_path}:{line_number}: {accession} declares {site_count} sites/"
                f"{feature_count} features but contains {len(sites)}/{len(patterns)}"
            )
        positions = [site.model_position for site in sites]
        if positions != sorted(set(positions)):
            raise SfldReleaseError(
                f"{source_path}:{line_number}: {accession} SITE positions are not strictly ordered"
            )
        if len(set(patterns)) != len(patterns):
            raise SfldReleaseError(
                f"{source_path}:{line_number}: {accession} has duplicate FEATURE tuples"
            )
        if any(len(pattern) != site_count for pattern in patterns):
            raise SfldReleaseError(
                f"{source_path}:{line_number}: {accession} FEATURE tuple length does not equal "
                "site_count"
            )
        if (site_count == 0) != (feature_count == 0):
            raise SfldReleaseError(
                f"{source_path}:{line_number}: {accession} sites and FEATURE tuples must both "
                "be empty or both be present"
            )
        rules[accession] = SfldSiteRule(
            accession=accession,
            sites=tuple(sites),
            feature_patterns=tuple(patterns),
            source_record_sha256=hashlib.sha256(b"".join(block_lines)).hexdigest(),
        )
    if not rules:
        raise SfldReleaseError(f"{source_path}: no site annotation blocks found")
    return source_path, actual_sha256, rules


def parse_sfld_hierarchy(
    path: str | Path,
    expected_sha256: str,
    model_accessions: set[str],
) -> tuple[Path, str, dict[str, tuple[str, ...]], dict[str, str]]:
    """Parse complete ancestor closures and derive one verified direct parent."""

    source_path, raw, actual_sha256 = _read_pinned(path, expected_sha256, "hierarchy")
    ancestors: dict[str, tuple[str, ...]] = {}
    for line_number, raw_line in enumerate(raw.splitlines(), 1):
        line = _ascii(raw_line, source_path, "hierarchy")
        if not line.strip() or line.count(":") != 1:
            raise SfldReleaseError(
                f"{source_path}:{line_number}: expected child: complete ancestor closure"
            )
        child, ancestor_text = (part.strip() for part in line.split(":", 1))
        _accession_level(child, source_path, "hierarchy child")
        if child in ancestors:
            raise SfldReleaseError(f"{source_path}:{line_number}: duplicate child {child}")
        declared = ancestor_text.split()
        if not declared:
            raise SfldReleaseError(f"{source_path}:{line_number}: {child} has no ancestors")
        for ancestor in declared:
            _accession_level(ancestor, source_path, "hierarchy ancestor")
        if len(set(declared)) != len(declared):
            raise SfldReleaseError(f"{source_path}:{line_number}: {child} has duplicate ancestors")
        if child in declared:
            raise SfldReleaseError(f"{source_path}:{line_number}: {child} is its own ancestor")
        ancestors[child] = tuple(sorted(declared))
    if not ancestors:
        raise SfldReleaseError(f"{source_path}: no hierarchy rows found")

    referenced = set(ancestors)
    referenced.update(ancestor for values in ancestors.values() for ancestor in values)
    unknown = sorted(referenced - model_accessions)
    if unknown:
        raise SfldReleaseError(
            f"{source_path}: hierarchy references accessions absent from sfld.hmm: {unknown[:5]!r}"
        )

    direct_parents: dict[str, str] = {}
    for child, declared_tuple in ancestors.items():
        declared = set(declared_tuple)
        depths = {candidate: len(ancestors.get(candidate, ())) for candidate in declared}
        maximum_depth = max(depths.values())
        candidates = sorted(
            candidate for candidate, depth in depths.items() if depth == maximum_depth
        )
        if len(candidates) != 1:
            raise SfldReleaseError(
                f"{source_path}: cannot derive one direct parent for {child}; "
                f"max-depth candidates are {candidates!r}"
            )
        parent = candidates[0]
        expected_closure = {parent, *ancestors.get(parent, ())}
        if declared != expected_closure:
            raise SfldReleaseError(
                f"{source_path}: {child} row is not the exact transitive closure of direct "
                f"parent {parent}"
            )
        direct_parents[child] = parent

    for child in direct_parents:
        seen: set[str] = set()
        cursor = child
        while cursor in direct_parents:
            if cursor in seen:
                raise SfldReleaseError(f"{source_path}: hierarchy cycle reaches {cursor}")
            seen.add(cursor)
            cursor = direct_parents[cursor]
    return source_path, actual_sha256, ancestors, direct_parents


def load_sfld_release(
    hmm_path: str | Path,
    hierarchy_path: str | Path,
    sites_path: str | Path,
    *,
    expected_hmm_sha256: str = SFLD_4_HMM_SHA256,
    expected_hierarchy_sha256: str = SFLD_4_HIERARCHY_SHA256,
    expected_sites_sha256: str = SFLD_4_SITES_SHA256,
    enforce_release_contract: bool = True,
) -> SfldRelease:
    """Load the three SFLD 4 artifacts as one inseparable source model."""

    hmm_source, hmm_sha256, models = parse_sfld_hmm(hmm_path, expected_hmm_sha256)
    sites_source, sites_sha256, site_rules = parse_sfld_sites(sites_path, expected_sites_sha256)
    model_set = set(models)
    site_set = set(site_rules)
    if site_set != model_set:
        missing = sorted(model_set - site_set)
        extra = sorted(site_set - model_set)
        raise SfldReleaseError(
            "SFLD site-block accessions must equal HMM accessions; "
            f"missing={missing[:5]!r}, extra={extra[:5]!r}"
        )
    for accession, rule in site_rules.items():
        model_length = models[accession].model_length
        if any(site.model_position > model_length for site in rule.sites):
            raise SfldReleaseError(
                f"SFLD {accession} site position exceeds HMM model length {model_length}"
            )

    hierarchy_source, hierarchy_sha256, ancestors, direct_parents = parse_sfld_hierarchy(
        hierarchy_path,
        expected_hierarchy_sha256,
        model_set,
    )
    release = SfldRelease(
        release=SFLD_4_RELEASE,
        hmm_path=hmm_source,
        hierarchy_path=hierarchy_source,
        sites_path=sites_source,
        hmm_sha256=hmm_sha256,
        hierarchy_sha256=hierarchy_sha256,
        sites_sha256=sites_sha256,
        models=models,
        site_rules=site_rules,
        ancestors=ancestors,
        direct_parents=direct_parents,
    )
    if enforce_release_contract:
        _enforce_sfld_4_counts(release)
    return release


def _release_counts(release: SfldRelease) -> dict[str, Any]:
    level_counts = {level: 0 for level in _LEVELS.values()}
    for model in release.models.values():
        level_counts[model.native_classification_level] += 1
    edge_type_counts: dict[str, int] = {}
    for child, parent in release.direct_parents.items():
        edge_type = f"{child[4]}_TO_{parent[4]}"
        edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1
    participating = set(release.ancestors)
    participating.update(ancestor for values in release.ancestors.values() for ancestor in values)
    return {
        "model_count": len(release.models),
        "model_count_by_native_level": level_counts,
        "model_length_min": min(model.model_length for model in release.models.values()),
        "model_length_max": max(model.model_length for model in release.models.values()),
        "site_block_count": len(release.site_rules),
        "site_bearing_model_count": sum(bool(rule.sites) for rule in release.site_rules.values()),
        "site_position_count": sum(len(rule.sites) for rule in release.site_rules.values()),
        "site_feature_pattern_count": sum(
            len(rule.feature_patterns) for rule in release.site_rules.values()
        ),
        "hierarchy_child_count": len(release.ancestors),
        "hierarchy_ancestor_relation_count": sum(
            len(values) for values in release.ancestors.values()
        ),
        "direct_edge_type_counts": dict(sorted(edge_type_counts.items())),
        "isolated_model_count": len(set(release.models) - participating),
    }


_SFLD_4_EXPECTED_COUNTS: dict[str, Any] = {
    "model_count": 299,
    "model_count_by_native_level": {
        "SUPERFAMILY": 15,
        "SUBGROUP": 132,
        "FAMILY": 152,
    },
    "model_length_min": 119,
    "model_length_max": 3378,
    "site_block_count": 299,
    "site_bearing_model_count": 274,
    "site_position_count": 1368,
    "site_feature_pattern_count": 372,
    "hierarchy_child_count": 266,
    "hierarchy_ancestor_relation_count": 580,
    "direct_edge_type_counts": {
        "F_TO_G": 142,
        "F_TO_S": 3,
        "G_TO_G": 48,
        "G_TO_S": 73,
    },
    "isolated_model_count": 25,
}


def _enforce_sfld_4_counts(release: SfldRelease) -> None:
    observed = _release_counts(release)
    if observed != _SFLD_4_EXPECTED_COUNTS:
        raise SfldReleaseError(
            "parsed artifacts do not have the pinned SFLD 4 release shape: "
            f"expected {_SFLD_4_EXPECTED_COUNTS!r}, found {observed!r}"
        )


def canonical_json(value: Any) -> str:
    """Canonical encoding used to content-address the generated manifest."""

    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def build_sfld_release_manifest(release: SfldRelease) -> dict[str, Any]:
    """Return a deterministic manifest for a successfully parsed release."""

    payload: dict[str, Any] = {
        "schema_version": 1,
        "manifest_kind": "SFLD_SOURCE_MODEL",
        "source_release": release.release,
        "artifacts": {
            "hmm": {
                "path": SFLD_4_HMM_SOURCE_ARTIFACT,
                "sha256": release.hmm_sha256,
                "url": SFLD_4_HMM_URL,
            },
            "hierarchy": {
                "path": SFLD_4_HIERARCHY_SOURCE_ARTIFACT,
                "sha256": release.hierarchy_sha256,
                "url": SFLD_4_HIERARCHY_URL,
            },
            "sites": {
                "path": SFLD_4_SITES_SOURCE_ARTIFACT,
                "sha256": release.sites_sha256,
                "url": SFLD_4_SITES_URL,
            },
        },
        "matching_contract": {
            "profile_search_mode": SFLD_4_PROFILE_SEARCH_MODE,
            "site_coordinate_system": SFLD_4_SITE_COORDINATE_SYSTEM,
            "site_evidence_scope": SFLD_4_SITE_EVIDENCE_SCOPE,
            "feature_patterns_are_correlated_tuples": True,
            "ancestor_propagation_clears_sites": True,
        },
        "counts": _release_counts(release),
    }
    manifest_sha256 = hashlib.sha256(canonical_json(payload).encode("ascii")).hexdigest()
    return {"manifest_sha256": manifest_sha256, **payload}


def build_sfld_profile_representation(
    release: SfldRelease,
    accession: str,
) -> dict[str, Any]:
    """Project one parsed model into the schema's source-native representation.

    This is a source fact, not evidence that any protein matches the model.  In
    particular it carries neither a protein accession nor an alignment and does
    not relax the separate SFLD execution-receipt and grounding gates.
    """

    model = release.models.get(accession)
    if model is None:
        raise SfldReleaseError(f"SFLD release has no executable model {accession}")
    site_rule = release.site_rules.get(accession)
    if site_rule is None:
        raise SfldReleaseError(f"SFLD release has no site block {accession}")

    sites: list[dict[str, Any]] = []
    for site in site_rule.sites:
        projected_site: dict[str, Any] = {
            "ordinal": site.ordinal,
            "model_position": site.model_position,
        }
        if site.description is not None:
            projected_site["description"] = site.description
        sites.append(projected_site)

    return {
        "source_accession": f"SFLD:{accession}",
        "source_release": release.release,
        "representation_type": SFLD_4_REPRESENTATION_TYPE,
        "source_model_artifact": SFLD_4_HMM_SOURCE_ARTIFACT,
        "source_model_artifact_sha256": release.hmm_sha256,
        "source_model_record_sha256": model.source_record_sha256,
        "source_sites_artifact": SFLD_4_SITES_SOURCE_ARTIFACT,
        "source_sites_artifact_sha256": release.sites_sha256,
        "source_site_record_sha256": site_rule.source_record_sha256,
        "source_hierarchy_artifact": SFLD_4_HIERARCHY_SOURCE_ARTIFACT,
        "source_hierarchy_artifact_sha256": release.hierarchy_sha256,
        "native_classification_level": model.native_classification_level,
        "model_length": model.model_length,
        "gathering_sequence_score": model.gathering_sequence_score,
        "gathering_domain_score": model.gathering_domain_score,
        "training_sequence_count": model.training_sequence_count,
        "hmm_checksum": model.hmm_checksum,
        "profile_search_mode": SFLD_4_PROFILE_SEARCH_MODE,
        "site_coordinate_system": SFLD_4_SITE_COORDINATE_SYSTEM,
        "site_evidence_scope": SFLD_4_SITE_EVIDENCE_SCOPE,
        "site_count": len(sites),
        "sites": sites,
        "site_feature_pattern_count": len(site_rule.feature_patterns),
        "site_feature_patterns": list(site_rule.feature_patterns),
    }


def _atomic_write_manifest(path: Path, manifest: Mapping[str, Any]) -> bool:
    """Atomically install canonical manifest bytes; return false if unchanged."""

    content = (canonical_json(manifest) + "\n").encode("ascii")
    if path.is_file() and path.read_bytes() == content:
        return False
    if not path.parent.is_dir():
        raise SfldReleaseError(f"manifest parent directory does not exist: {path.parent}")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.chmod(0o644)
        os.replace(temporary_path, path)
    except OSError as error:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise SfldReleaseError(f"cannot atomically write SFLD manifest {path}: {error}") from error
    return True


def main(argv: list[str] | None = None) -> int:
    """Verify the local pinned release and print its complete manifest."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--hmm",
        type=Path,
        default=_REPO_ROOT / SFLD_4_HMM_SOURCE_ARTIFACT,
        help="Local sfld.hmm path (still checked against the pinned SFLD 4 digest).",
    )
    parser.add_argument(
        "--hierarchy",
        type=Path,
        default=_REPO_ROOT / SFLD_4_HIERARCHY_SOURCE_ARTIFACT,
        help="Local sfld_hierarchy_flat.txt path (pinned digest required).",
    )
    parser.add_argument(
        "--sites",
        type=Path,
        default=_REPO_ROOT / SFLD_4_SITES_SOURCE_ARTIFACT,
        help="Local sfld_sites.annot path (pinned digest required).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Atomically write the canonical ignored raw manifest after verification.",
    )
    args = parser.parse_args(argv)

    try:
        release = load_sfld_release(
            args.hmm,
            args.hierarchy,
            args.sites,
            expected_hmm_sha256=SFLD_4_HMM_SHA256,
            expected_hierarchy_sha256=SFLD_4_HIERARCHY_SHA256,
            expected_sites_sha256=SFLD_4_SITES_SHA256,
        )
        manifest = build_sfld_release_manifest(release)
        print(json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True))
        if args.apply:
            manifest_path = _REPO_ROOT / SFLD_4_MANIFEST_SOURCE_ARTIFACT
            changed = _atomic_write_manifest(manifest_path, manifest)
            state = "wrote" if changed else "unchanged"
            print(f"{state}: {manifest_path}", file=sys.stderr)
    except SfldReleaseError as error:
        print(f"SFLD verification failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
