#!/usr/bin/env python3
"""Replay source-backed record-content gates before UniProt example approval.

The UniProt grounding resolver proves that a protein and occurrence exist.  That is
not enough when the *trait record* being instantiated is truncated, definition-only
boilerplate, or contradicts the source that supplied its route or positional identity.
This module implements the small set of deterministic checks discovered during
full-file review of the ``ready-local-review`` batches.

All source reads are checksum-pinned.  A check that needs a missing, changed, or
incomplete source raises :class:`ContentGateError`; it never degrades to "no finding".
The CLI is read-only and is also used for production replays of review ledgers.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

from interpro_text import clean_abstract_element

# ``yaml.safe_load`` selects PyYAML's pure-Python SafeLoader.  A full candidate
# replay currently reads tens of thousands of already-validated trait records, so
# parser dispatch dominates the gate even though each document is small.  LibYAML's
# CSafeLoader implements the same safe schema in C; retain SafeLoader as the portable
# fallback for environments whose PyYAML wheel was built without LibYAML.
_YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INTERPRO_XML = REPO_ROOT / "data" / "raw" / "interpro" / "interpro.xml.gz"
DEFAULT_PFAM_CLANS = REPO_ROOT / "data" / "raw" / "pfam" / "Pfam-A.clans.tsv.gz"
DEFAULT_PFAM_TYPES = REPO_ROOT / "data" / "raw" / "pfam" / "pfam_types.tsv"
DEFAULT_PANTHER_CLASSIFICATIONS = (
    REPO_ROOT / "data" / "raw" / "panther" / "PANTHER19.0_HMM_classifications"
)

# These are the exact local source images used to seed the records under review.  The
# upstream URLs say ``current_release`` and are therefore not reproducibility pins.
INTERPRO_109_XML_SHA256 = "c77fe193c1a0de8df903deff9325f734bfca3c9fbf59fd4ce697489c33ef0d87"
PFAM_A_CLANS_SHA256 = "86062b7ef1a0e0caee0c28cef479ac0d294c80789c51cbf75e513b368ce3a6f6"
PFAM_TYPES_SHA256 = "5cce3b49fb64afd2c43157600d7a43bee572765b1bc6e918b3e4210bd12313b9"
PANTHER_19_CLASSIFICATIONS_SHA256 = (
    "94b0c70dc84b9888bf2a784a3ba52f775412546b07bc1bad19302a04353cc07c"
)

HARD = "HARD"
REVIEW = "REVIEW"
HARD_CODES = frozenset(
    {
        "SOURCE_DEFINITION_MALFORMED",
        "SOURCE_DEFINITION_TRUNCATED",
        "DEFINITION_TEMPLATE_ONLY",
        "UNRESOLVED_SOURCE_PLACEHOLDER",
        "SOURCE_POSITIONAL_IDENTITY_CONFLICT",
        "SOURCE_FAMILY_IDENTITY_CONFLICT",
        "SOURCE_SCOPE_CONFLICT",
    }
)
REASON_PREFIX = "unqualifiable:record_content:"

_IPR = re.compile(r"^InterPro:(IPR\d+) abstract\b")
_HAMAP = re.compile(r"^HAMAP:(MF_\d+(?:_[A-Z])?)$")
_PFAM = re.compile(r"^Pfam:(PF\d+)$")
_PANTHER = re.compile(r"^PANTHER:(PTHR\d+)$")
_ANGLE_PLACEHOLDER = re.compile(r"<[A-Za-z][A-Za-z0-9_.-]*>")
_EXPLICIT_TERMINAL = re.compile(r"\b([NC])[- ]terminal\b|\b([NC])\s+terminus\b", re.IGNORECASE)
_DEICTIC_TERMINAL_REGION = re.compile(r"\bThis\s+([NC])-terminal\s+region\b", re.IGNORECASE)
_LOW_INFORMATION = re.compile(
    r"^This entry represents (?:a )?(?:small )?"
    r"(?:(N|C)-terminal )?(domain|region|repeat|motif) found in (.+?) proteins\.$",
    re.IGNORECASE,
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ORDINAL_WORDS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
    "fourteenth": 14,
    "fifteenth": 15,
    "sixteenth": 16,
    "seventeenth": 17,
    "eighteenth": 18,
    "nineteenth": 19,
    "twentieth": 20,
}


def _malformed_interpro_artifact(value: str) -> str | None:
    """Return a narrow, substantively incomplete pinned-InterPro artifact.

    Readable typography debt (duplicated words or stray spaces around a hyphen) is
    deliberately non-hard.  The grounding policy blocks only corruption that removes
    substantive prose, such as a stripped citation leaving an impossible fragment or
    a missing trait noun.
    """

    if "[,." in value:
        return "[,."
    if value.endswith("(."):
        return "(."
    if re.search(r"\brepresents\s+a\s+of\b", value, flags=re.IGNORECASE):
        return "represents a of"
    return None


class ContentGateError(ValueError):
    """A source image cannot support an exact, fail-closed content replay."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _value_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _collapse(value: Any) -> str:
    return " ".join(str(value or "").split())


def _lexical_tokens(value: str) -> frozenset[str]:
    """Return literal alphanumeric tokens for conservative redundancy checks."""

    return frozenset(re.findall(r"[a-z0-9]+", value.lower()))


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _read_pinned(path: Path, expected_sha256: str, label: str) -> tuple[bytes, str]:
    if _SHA256.fullmatch(expected_sha256) is None:
        raise ContentGateError(f"{label}: invalid expected SHA-256 {expected_sha256!r}")
    if not path.is_file():
        raise ContentGateError(f"{label}: pinned source does not exist: {path}")
    raw = path.read_bytes()
    observed = hashlib.sha256(raw).hexdigest()
    if observed != expected_sha256:
        raise ContentGateError(
            f"{label}: source SHA-256 mismatch for {path}; expected "
            f"{expected_sha256}, got {observed}"
        )
    return raw, observed


@dataclass(frozen=True)
class SourceConfig:
    interpro_xml: Path = DEFAULT_INTERPRO_XML
    interpro_xml_sha256: str = INTERPRO_109_XML_SHA256
    pfam_clans: Path = DEFAULT_PFAM_CLANS
    pfam_clans_sha256: str = PFAM_A_CLANS_SHA256
    pfam_types: Path = DEFAULT_PFAM_TYPES
    pfam_types_sha256: str = PFAM_TYPES_SHA256
    panther_classifications: Path = DEFAULT_PANTHER_CLASSIFICATIONS
    panther_classifications_sha256: str = PANTHER_19_CLASSIFICATIONS_SHA256


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    detail: str
    source_bindings: tuple[dict[str, Any], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "detail": self.detail,
            "source_bindings": [dict(binding) for binding in self.source_bindings],
        }


@dataclass(frozen=True)
class InterProEntry:
    accession: str
    entry_type: str
    short_name: str
    name: str
    abstract: str
    hamap_members: Mapping[str, str]
    pfam_members: Mapping[str, str]
    panther_members: Mapping[str, str]

    def projection(self) -> dict[str, Any]:
        return {
            "accession": self.accession,
            "type": self.entry_type,
            "short_name": self.short_name,
            "name": self.name,
            "abstract": self.abstract,
            "pfam_members": dict(sorted(self.pfam_members.items())),
        }

    def panther_projection(self) -> dict[str, Any]:
        """Stable projection used only by the PANTHER/InterPro identity rule."""

        return {
            "accession": self.accession,
            "type": self.entry_type,
            "short_name": self.short_name,
            "name": self.name,
            "abstract": self.abstract,
            "panther_members": dict(sorted(self.panther_members.items())),
        }

    def hamap_projection(self) -> dict[str, Any]:
        """Stable projection used only by the HAMAP/InterPro identity rule."""

        return {
            "accession": self.accession,
            "type": self.entry_type,
            "short_name": self.short_name,
            "name": self.name,
            "abstract": self.abstract,
            "hamap_members": dict(sorted(self.hamap_members.items())),
        }


@dataclass(frozen=True)
class PfamEntry:
    accession: str
    clan: str
    clan_name: str
    short_name: str
    description: str
    entry_type: str

    def projection(self) -> dict[str, Any]:
        return {
            "accession": self.accession,
            "clan": self.clan,
            "clan_name": self.clan_name,
            "short_name": self.short_name,
            "description": self.description,
            "type": self.entry_type,
        }


@dataclass(frozen=True)
class PantherEntry:
    accession: str
    name: str
    children: Mapping[str, str]

    def projection(self) -> dict[str, Any]:
        return {
            "accession": self.accession,
            "name": self.name,
            "children": dict(sorted(self.children.items())),
        }


def _mapped_interpro(record: Mapping[str, Any]) -> str | None:
    found = {
        str(item.get("object"))
        for item in record.get("mapped_xrefs") or []
        if isinstance(item, dict)
        and str(item.get("object") or "").startswith("InterPro:IPR")
        and item.get("mapping_source") in {"pfam2interpro", "interpro-member-list"}
    }
    if len(found) > 1:
        raise ContentGateError(
            f"{record.get('identifier')}: multiple integrating InterPro mappings: "
            + ", ".join(sorted(found))
        )
    return next(iter(found)).split(":", 1)[1] if found else None


def _definition_interpro(record: Mapping[str, Any]) -> str | None:
    source = str(record.get("definition_source") or "")
    match = _IPR.match(source)
    if match:
        return match.group(1)
    identifier = str(record.get("identifier") or "")
    if identifier.startswith("InterPro:IPR") and source == "InterPro":
        return identifier.split(":", 1)[1]
    return None


def _needs_pfam(record: Mapping[str, Any]) -> bool:
    return bool(
        _PFAM.fullmatch(str(record.get("identifier") or ""))
        and (record.get("definition_source") == "Pfam" or _mapped_interpro(record) is not None)
    )


def _needs_panther(record: Mapping[str, Any]) -> bool:
    return bool(
        _PANTHER.fullmatch(str(record.get("identifier") or ""))
        and (
            str(record.get("definition_source") or "").startswith("PANTHER 19.0")
            or _mapped_interpro(record) is not None
        )
    )


def _load_interpro(
    path: Path,
    expected_sha256: str,
    wanted_iprs: set[str],
    wanted_hamap: set[str],
    wanted_pfam: set[str],
    wanted_panther: set[str],
) -> tuple[dict[str, InterProEntry], dict[str, str], dict[str, Any]]:
    _, observed_sha = _read_pinned(path, expected_sha256, "InterPro XML")
    entries: dict[str, InterProEntry] = {}
    integrations: dict[str, str] = {}
    try:
        with gzip.open(path, "rb") as handle:
            for _event, element in ET.iterparse(handle, events=("end",)):
                if element.tag != "interpro":
                    continue
                accession = element.get("id") or ""
                members_element = element.find("member_list")
                hamap_members: dict[str, str] = {}
                pfam_members: dict[str, str] = {}
                panther_members: dict[str, str] = {}
                if members_element is not None:
                    for xref in members_element.findall("db_xref"):
                        database = (xref.get("db") or "").upper()
                        pfam_accession = xref.get("dbkey") or ""
                        if database == "HAMAP" and pfam_accession in wanted_hamap:
                            hamap_members[pfam_accession] = xref.get("name") or ""
                        if database == "PFAM" and pfam_accession in wanted_pfam:
                            previous = integrations.get(pfam_accession)
                            if previous and previous != accession:
                                raise ContentGateError(
                                    f"Pfam {pfam_accession} occurs in multiple InterPro "
                                    f"member lists: {previous}, {accession}"
                                )
                            integrations[pfam_accession] = accession
                            pfam_members[pfam_accession] = xref.get("name") or ""
                        if database == "PANTHER":
                            panther_members[pfam_accession] = xref.get("name") or ""
                if (
                    accession in wanted_iprs
                    or hamap_members
                    or pfam_members
                    or bool(wanted_panther.intersection(panther_members))
                ):
                    entries[accession] = InterProEntry(
                        accession=accession,
                        entry_type=element.get("type") or "",
                        short_name=element.get("short_name") or "",
                        name=element.findtext("name") or "",
                        abstract=clean_abstract_element(element.find("abstract")),
                        hamap_members=hamap_members,
                        pfam_members=pfam_members,
                        panther_members=panther_members,
                    )
                element.clear()
    except (OSError, EOFError, ET.ParseError) as exc:
        raise ContentGateError(f"cannot parse pinned InterPro XML {path}: {exc}") from exc

    absent_iprs = sorted(wanted_iprs - set(entries))
    if absent_iprs:
        raise ContentGateError(
            "pinned InterPro XML lacks required entry/entries: " + ", ".join(absent_iprs[:10])
        )
    binding = {
        "kind": "INTERPRO_XML",
        "path": _display_path(path),
        "sha256": observed_sha,
    }
    return entries, integrations, binding


def _load_panther(
    config: SourceConfig, wanted: set[str]
) -> tuple[dict[str, PantherEntry], dict[str, Any]]:
    raw, observed_sha = _read_pinned(
        config.panther_classifications,
        config.panther_classifications_sha256,
        "PANTHER classifications",
    )
    names: dict[str, str] = {}
    children: dict[str, dict[str, str]] = defaultdict(dict)
    try:
        for line_number, raw_line in enumerate(io.BytesIO(raw), 1):
            line = raw_line.decode("utf-8", errors="strict").rstrip("\r\n")
            if not line:
                continue
            columns = line.split("\t")
            if len(columns) < 2:
                raise ContentGateError(
                    f"PANTHER classifications:{line_number}: expected at least two columns"
                )
            source_id, name = columns[:2]
            root, separator, _subfamily = source_id.partition(":")
            if root not in wanted:
                continue
            if separator:
                previous = children[root].get(source_id)
                if previous is not None and previous != name:
                    raise ContentGateError(
                        f"PANTHER classifications:{line_number}: conflicting {source_id} name"
                    )
                children[root][source_id] = name
            else:
                previous = names.get(root)
                if previous is not None and previous != name:
                    raise ContentGateError(
                        f"PANTHER classifications:{line_number}: conflicting {root} name"
                    )
                names[root] = name
    except UnicodeDecodeError as exc:
        raise ContentGateError(
            f"cannot parse pinned PANTHER classifications {config.panther_classifications}: {exc}"
        ) from exc
    absent = sorted(wanted - set(names))
    if absent:
        raise ContentGateError(
            "pinned PANTHER classifications lack required family/families: "
            + ", ".join(absent[:10])
        )
    entries = {
        accession: PantherEntry(
            accession=accession,
            name=names[accession],
            children=children.get(accession, {}),
        )
        for accession in sorted(wanted)
    }
    binding = {
        "kind": "PANTHER_HMM_CLASSIFICATIONS",
        "path": _display_path(config.panther_classifications),
        "sha256": observed_sha,
    }
    return entries, binding


def _load_pfam(
    config: SourceConfig, wanted: set[str]
) -> tuple[dict[str, PfamEntry], tuple[dict[str, Any], dict[str, Any]]]:
    _, clans_sha = _read_pinned(config.pfam_clans, config.pfam_clans_sha256, "Pfam clans")
    types_raw, types_sha = _read_pinned(config.pfam_types, config.pfam_types_sha256, "Pfam types")
    types: dict[str, str] = {}
    for line in types_raw.decode("utf-8", errors="strict").splitlines():
        if "\t" in line:
            accession, entry_type = line.split("\t", 1)
            if accession in wanted:
                types[accession] = entry_type.strip()

    rows: dict[str, PfamEntry] = {}
    try:
        with gzip.open(config.pfam_clans, "rt", encoding="utf-8", errors="strict") as handle:
            for line in handle:
                columns = line.rstrip("\n").split("\t")
                if len(columns) < 5 or columns[0] not in wanted:
                    continue
                accession, clan, clan_name, short_name, description = columns[:5]
                rows[accession] = PfamEntry(
                    accession=accession,
                    clan=clan,
                    clan_name=clan_name,
                    short_name=short_name,
                    description=description,
                    entry_type=types.get(accession, ""),
                )
    except (OSError, EOFError, UnicodeDecodeError) as exc:
        raise ContentGateError(
            f"cannot parse pinned Pfam clans {config.pfam_clans}: {exc}"
        ) from exc
    absent = sorted(wanted - set(rows))
    missing_types = sorted(accession for accession in wanted if not types.get(accession))
    if absent:
        raise ContentGateError("pinned Pfam clans lack: " + ", ".join(absent[:10]))
    if missing_types:
        raise ContentGateError("pinned Pfam types lack: " + ", ".join(missing_types[:10]))
    return rows, (
        {"kind": "PFAM_CLANS", "path": _display_path(config.pfam_clans), "sha256": clans_sha},
        {"kind": "PFAM_TYPES", "path": _display_path(config.pfam_types), "sha256": types_sha},
    )


def _directions(value: str) -> frozenset[str]:
    normalized = re.sub(r"[_-]+", " ", value.upper())
    found: set[str] = set()
    if re.search(r"(?:^|\W)N(?:\W|$)|\bN TERMINAL\b|\bAMINO TERMINAL\b", normalized):
        found.add("N")
    if re.search(r"(?:^|\W)C(?:\W|$)|\bC TERMINAL\b|\bCARBOXY TERMINAL\b", normalized):
        found.add("C")
    return frozenset(found)


def _explicit_terminal_directions(value: str) -> frozenset[str]:
    """Extract only spelled-out termini, excluding ambiguous bare N/C name tokens."""

    return frozenset(
        direction.upper()
        for match in _EXPLICIT_TERMINAL.finditer(value)
        for direction in match.groups()
        if direction
    )


def _deictic_terminal_directions(value: str) -> frozenset[str]:
    """Extract exact ``This N/C-terminal region`` references from sourced prose."""

    return frozenset(match.group(1).upper() for match in _DEICTIC_TERMINAL_REGION.finditer(value))


def _ordinals(value: str) -> frozenset[int]:
    """Extract explicit ordinal identities without treating bare numbers as positions."""

    normalized = value.lower().replace("_", " ")
    found = {
        int(match.group(1))
        for match in re.finditer(r"\b([1-9][0-9]*)(?:st|nd|rd|th)\b", normalized)
    }
    tokens = set(re.findall(r"[a-z]+", normalized))
    found.update(position for word, position in _ORDINAL_WORDS.items() if word in tokens)
    return frozenset(found)


def _source_scope(value: str, *, source: str) -> str:
    normalized = value.strip().lower().replace("_", " ")
    if source == "Pfam":
        return "WHOLE_PROTEIN" if normalized == "family" else "LOCALIZED"
    return "WHOLE_PROTEIN" if normalized in {"family", "homologous superfamily"} else "LOCALIZED"


def _family_identity(value: str) -> str | None:
    """Resolve only strong, mutually exclusive identities used by source-conflict gates."""

    normalized = re.sub(r"[^A-Z0-9]+", " ", value.upper()).strip()
    identities: set[str] = set()
    if re.search(r"\bDNA LIGASE\b", normalized):
        identities.add("DNA_LIGASE")
    if (
        re.search(r"\bADP RIBOSYLTRANSFERASE\b", normalized)
        or re.search(r"\bADP RIBOSE POLYMERASE\b", normalized)
        or re.search(r"\bPARP(?:[0-9]+)?\b", normalized)
        or re.search(r"\bARTD\b", normalized)
        or re.search(r"\bTANKYRASE\b", normalized)
    ):
        identities.add("ADP_RIBOSYLTRANSFERASE")
    if re.search(r"\bGLYCOSYL\s*TRANSFERASE\b", normalized):
        identities.add("GLYCOSYL_TRANSFERASE")
    if re.search(r"\bDEACETYLASE\b", normalized) or (
        re.search(r"\bDEFORMYLASE\b", normalized) and re.search(r"\bARND\b", normalized)
    ):
        # The PTHR10587 source hierarchy contains polysaccharide/chitin/peptidoglycan
        # deacetylases plus the homologous ArnD deformylase.  Treat those exact enzyme
        # names as one carbohydrate-deacylase identity; do not infer from "hydrolase"
        # or from generic protein-class annotations.
        identities.add("CARBOHYDRATE_DEACYLASE")
    return next(iter(identities)) if len(identities) == 1 else None


def _generic_panther_child_name(value: str) -> bool:
    """Recognize only the exact low-information child confirmed for PTHR10587."""

    normalized = re.sub(r"[^A-Z0-9]+", " ", value.upper()).strip()
    return normalized == "SECRETED PROTEIN"


def _panther_full_length_claim(record: Mapping[str, Any], accession: str) -> bool:
    """Recognize the seeder's explicit generated full-length-family assertion."""

    label = _collapse(record.get("label"))
    definition = _collapse(record.get("definition"))
    prefix = (
        f"{label} — a full-length protein family modelled by "
        f"the PANTHER 19.0 profile HMM {accession}."
    )
    generated = any(
        isinstance(item, dict)
        and item.get("method") == "GENERATED"
        and _collapse(item.get("text")) == definition
        for item in record.get("definitions") or []
    )
    return bool(
        generated
        and str(record.get("definition_source") or "").startswith("PANTHER 19.0")
        and (definition == prefix or definition.startswith(prefix + " "))
    )


def _merged_candidate_coverage(
    candidate: Mapping[str, Any], *, identifier: str
) -> tuple[int, int, list[tuple[int, int]]]:
    length = candidate.get("sequence_length")
    if isinstance(length, bool) or not isinstance(length, int) or length < 1:
        raise ContentGateError(
            f"{identifier}: full-length PANTHER candidate lacks a valid sequence_length"
        )
    raw_intervals = candidate.get("intervals")
    if not isinstance(raw_intervals, list) or not raw_intervals:
        raise ContentGateError(
            f"{identifier}: interval-backed full-length PANTHER candidate lacks intervals"
        )
    intervals: list[tuple[int, int]] = []
    for index, interval in enumerate(raw_intervals):
        if not isinstance(interval, Mapping):
            raise ContentGateError(f"{identifier}: candidate interval {index} is not a mapping")
        start = interval.get("start")
        end = interval.get("end")
        if (
            isinstance(start, bool)
            or isinstance(end, bool)
            or not isinstance(start, int)
            or not isinstance(end, int)
            or start < 1
            or end < start
            or end > length
        ):
            raise ContentGateError(
                f"{identifier}: invalid candidate interval {index}: {interval!r} "
                f"for sequence length {length}"
            )
        intervals.append((start, end))
    merged: list[tuple[int, int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    covered = sum(end - start + 1 for start, end in merged)
    return covered, length, merged


def _low_information_flag(record: Mapping[str, Any]) -> Finding | None:
    definition = _collapse(record.get("definition"))
    match = _LOW_INFORMATION.fullmatch(definition)
    if match is None:
        return None
    terminal, feature, carrier = match.groups()
    expected_tokens = set(re.findall(r"[A-Za-z0-9]+", carrier.lower()))
    expected_tokens.add(feature.lower())
    if terminal:
        expected_tokens.update({terminal.lower(), "terminal"})
    label_tokens = set(re.findall(r"[A-Za-z0-9]+", str(record.get("label") or "").lower()))
    if label_tokens != expected_tokens:
        return None
    return Finding(
        code="LOW_INFORMATION_SOURCE_DEFINITION",
        severity=REVIEW,
        detail="the sourced definition only restates the label's carrier, position, and feature",
    )


class RecordContentGate:
    """Evaluate a fixed record set against exact pinned source images."""

    def __init__(self, records: Sequence[Mapping[str, Any]], config: SourceConfig = SourceConfig()):
        self.config = config
        wanted_iprs: set[str] = set()
        wanted_hamap: set[str] = set()
        wanted_pfam: set[str] = set()
        wanted_panther: set[str] = set()
        for record in records:
            definition_ipr = _definition_interpro(record)
            if definition_ipr:
                wanted_iprs.add(definition_ipr)
            mapped_ipr = _mapped_interpro(record)
            identifier = str(record.get("identifier") or "")
            hamap_match = _HAMAP.fullmatch(identifier)
            if hamap_match and mapped_ipr and definition_ipr == mapped_ipr:
                wanted_hamap.add(hamap_match.group(1))
            if mapped_ipr and (_PFAM.fullmatch(identifier) or _PANTHER.fullmatch(identifier)):
                wanted_iprs.add(mapped_ipr)
            if _needs_pfam(record):
                wanted_pfam.add(str(record["identifier"]).split(":", 1)[1])
            if _needs_panther(record):
                wanted_panther.add(str(record["identifier"]).split(":", 1)[1])

        self.interpro_entries: dict[str, InterProEntry] = {}
        self.pfam_integrations: dict[str, str] = {}
        self.interpro_binding: dict[str, Any] | None = None
        if wanted_iprs:
            (
                self.interpro_entries,
                self.pfam_integrations,
                self.interpro_binding,
            ) = _load_interpro(
                config.interpro_xml,
                config.interpro_xml_sha256,
                wanted_iprs,
                wanted_hamap,
                wanted_pfam,
                wanted_panther,
            )

        self.pfam_entries: dict[str, PfamEntry] = {}
        self.pfam_bindings: tuple[dict[str, Any], ...] = ()
        if wanted_pfam:
            self.pfam_entries, self.pfam_bindings = _load_pfam(config, wanted_pfam)

        self.panther_entries: dict[str, PantherEntry] = {}
        self.panther_binding: dict[str, Any] | None = None
        if wanted_panther:
            self.panther_entries, self.panther_binding = _load_panther(config, wanted_panther)

    def _interpro_bindings(self, entry: InterProEntry) -> tuple[dict[str, Any], ...]:
        assert self.interpro_binding is not None
        return (
            {
                **self.interpro_binding,
                "entry_id": f"InterPro:{entry.accession}",
                "entry_sha256": _value_sha256(entry.projection()),
            },
        )

    def _pfam_source_bindings(self, entry: PfamEntry) -> tuple[dict[str, Any], ...]:
        return tuple(
            {
                **binding,
                "entry_id": f"Pfam:{entry.accession}",
                "entry_sha256": _value_sha256(entry.projection()),
            }
            for binding in self.pfam_bindings
        )

    def _interpro_panther_bindings(self, entry: InterProEntry) -> tuple[dict[str, Any], ...]:
        assert self.interpro_binding is not None
        return (
            {
                **self.interpro_binding,
                "entry_id": f"InterPro:{entry.accession}",
                "entry_sha256": _value_sha256(entry.panther_projection()),
            },
        )

    def _interpro_hamap_bindings(self, entry: InterProEntry) -> tuple[dict[str, Any], ...]:
        assert self.interpro_binding is not None
        return (
            {
                **self.interpro_binding,
                "entry_id": f"InterPro:{entry.accession}",
                "entry_sha256": _value_sha256(entry.hamap_projection()),
            },
        )

    def _panther_source_bindings(self, entry: PantherEntry) -> tuple[dict[str, Any], ...]:
        assert self.panther_binding is not None
        return (
            {
                **self.panther_binding,
                "entry_id": f"PANTHER:{entry.accession}",
                "entry_sha256": _value_sha256(entry.projection()),
            },
        )

    def evaluate(self, record: Mapping[str, Any]) -> list[Finding]:
        identifier = str(record.get("identifier") or "")
        label = _collapse(record.get("label"))
        definition = _collapse(record.get("definition"))
        findings: list[Finding] = []

        placeholder = _ANGLE_PLACEHOLDER.search(label)
        if placeholder is not None:
            findings.append(
                Finding(
                    code="UNRESOLVED_SOURCE_PLACEHOLDER",
                    severity=HARD,
                    detail=(
                        f"primary label contains literal unresolved placeholder "
                        f"{placeholder.group(0)!r}"
                    ),
                )
            )

        definition_ipr = _definition_interpro(record)
        if definition_ipr:
            entry = self.interpro_entries.get(definition_ipr)
            if entry is None or not entry.abstract:
                raise ContentGateError(
                    f"{identifier}: declared InterPro definition cannot be replayed from "
                    f"InterPro:{definition_ipr}"
                )
            full = _collapse(entry.abstract)
            malformed_artifact = _malformed_interpro_artifact(full)
            if definition == full and malformed_artifact is not None:
                findings.append(
                    Finding(
                        code="SOURCE_DEFINITION_MALFORMED",
                        severity=HARD,
                        detail=(
                            f"definition exactly replays InterPro:{definition_ipr} but contains "
                            f"confirmed malformed-source artifact {malformed_artifact!r}"
                        ),
                        source_bindings=self._interpro_bindings(entry),
                    )
                )
            old_head = _collapse(full[:1800])
            old_ellipsis = full[:1799].rstrip() + "…"
            if definition != full and definition in {old_head, old_ellipsis}:
                findings.append(
                    Finding(
                        code="SOURCE_DEFINITION_TRUNCATED",
                        severity=HARD,
                        detail=(
                            f"definition is an exact historical truncation of "
                            f"InterPro:{definition_ipr} ({len(definition)}/{len(full)} characters)"
                        ),
                        source_bindings=self._interpro_bindings(entry),
                    )
                )

            title_directions = _explicit_terminal_directions(f"{entry.short_name} {entry.name}")
            opening_directions = _explicit_terminal_directions(full.split(".", 1)[0])
            deictic_directions = _deictic_terminal_directions(full)
            if (
                definition == full
                and len(title_directions) == 1
                and title_directions == opening_directions
                and len(deictic_directions) == 1
                and title_directions.isdisjoint(deictic_directions)
            ):
                title_direction = next(iter(title_directions))
                deictic_direction = next(iter(deictic_directions))
                findings.append(
                    Finding(
                        code="SOURCE_POSITIONAL_IDENTITY_CONFLICT",
                        severity=HARD,
                        detail=(
                            f"InterPro:{definition_ipr} title and opening sentence identify "
                            f"a {title_direction}-terminal trait, but the same exact copied "
                            f"abstract later deictically says 'This {deictic_direction}-terminal "
                            "region'"
                        ),
                        source_bindings=self._interpro_bindings(entry),
                    )
                )

            # InterPro 109.0 integrates HAMAP MF_00100_A into an archaeal aIF-2
            # entry whose own abstract explicitly distinguishes aIF-2 from aIF-5B
            # and calls aIF-2 a heterotrimer.  The HAMAP record instead asserts the
            # monomeric IF-2/infB identity.  Keep this rule deliberately exact: the
            # sibling MF_00100_B and any locally corrected definition remain clean.
            hamap_match = _HAMAP.fullmatch(identifier)
            mapped_ipr = _mapped_interpro(record)
            if (
                hamap_match
                and hamap_match.group(1) == "MF_00100_A"
                and label == "Translation initiation factor IF-2 [infB]"
                and definition_ipr == "IPR004544"
                and mapped_ipr == definition_ipr
                and definition == full
                and entry.entry_type == "Family"
                and entry.short_name == "TF_aIF-2_arc"
                and entry.name == "Translation initiation factor aIF-2, archaea"
                and entry.hamap_members.get("MF_00100_A") == "IF_2_A"
                and "aIF-2, and aIF-5B" in full
                and "aIF-2 promotes the GTP-dependent binding" in full
                and "heterotrimer formed by three subunits" in full
            ):
                findings.append(
                    Finding(
                        code="SOURCE_FAMILY_IDENTITY_CONFLICT",
                        severity=HARD,
                        detail=(
                            "record label asserts monomeric translation initiation factor "
                            "IF-2/infB, but exact HAMAP member MF_00100_A is integrated into "
                            "InterPro:IPR004544, whose copied abstract distinguishes aIF-2 "
                            "from aIF-5B and identifies aIF-2 as a heterotrimer"
                        ),
                        source_bindings=self._interpro_hamap_bindings(entry),
                    )
                )

            # PTHR10593 is an exact source-level identity split: the PANTHER root
            # name says RIO kinase, while the exact InterPro member, copied
            # definition, and informative PANTHER children all identify the plant
            # IDD/C2H2 transcription-factor family.  Keep this deliberately bound
            # to the observed accession, labels, mapping, and pinned source images;
            # a corrected local identity or source mapping remains clean.
            panther_match = _PANTHER.fullmatch(identifier)
            mapped_ipr = _mapped_interpro(record)
            if (
                panther_match
                and panther_match.group(1) == "PTHR10593"
                and label == "SERINE/THREONINE-PROTEIN KINASE RIO"
                and definition_ipr == "IPR031140"
                and mapped_ipr == definition_ipr
                and definition == full
                and entry.entry_type == "Family"
                and entry.short_name == "IDD1-16"
                and entry.name == "Protein indeterminate-domain 1-16"
                and entry.panther_members.get("PTHR10593") == ""
                and "plant-specific transcription factors" in full
                and "INDETERMINATE DOMAIN (IDD)" in full
                and "four zinc finger motifs" in full
            ):
                panther = self.panther_entries.get("PTHR10593")
                if panther is None:
                    raise ContentGateError(
                        f"{identifier}: pinned PANTHER classifications cannot be replayed"
                    )
                required_children = {
                    "PROTEIN SHOOT GRAVITROPISM 5",
                    "ZINC FINGER PROTEIN MAGPIE",
                    "PROTEIN INDETERMINATE-DOMAIN 14",
                }
                child_names = set(panther.children.values())
                if (
                    panther.name == "SERINE/THREONINE-PROTEIN KINASE RIO"
                    and required_children <= child_names
                    and not any(re.search(r"\bRIO\b", name) for name in child_names)
                ):
                    findings.append(
                        Finding(
                            code="SOURCE_FAMILY_IDENTITY_CONFLICT",
                            severity=HARD,
                            detail=(
                                "record and PANTHER root assert a RIO kinase, but exact "
                                "PANTHER member PTHR10593 in InterPro:IPR031140, the copied "
                                "abstract, and informative PANTHER children identify the "
                                "plant IDD/C2H2 transcription-factor family"
                            ),
                            source_bindings=(
                                *self._panther_source_bindings(panther),
                                *self._interpro_panther_bindings(entry),
                            ),
                        )
                    )

        panther_match = _PANTHER.fullmatch(identifier)
        if panther_match and str(record.get("definition_source") or "").startswith("PANTHER "):
            panther_accession = panther_match.group(1)
            expected = (
                f"{label} — a full-length protein family modelled by "
                f"the PANTHER 19.0 profile HMM {panther_accession}."
            )
            generated = any(
                isinstance(item, dict)
                and item.get("method") == "GENERATED"
                and _collapse(item.get("text")) == definition
                for item in record.get("definitions") or []
            )
            template_detail: str | None = None
            if definition == expected:
                template_detail = (
                    "generated PANTHER definition contains only the label and model identifier"
                )
            class_prefix = expected + " PANTHER protein class: "
            if generated and definition.startswith(class_prefix) and definition.endswith("."):
                protein_class = definition[len(class_prefix) : -1].strip()
                class_tokens = _lexical_tokens(protein_class)
                label_tokens = _lexical_tokens(label)
                if (
                    protein_class
                    and "." not in protein_class
                    and class_tokens
                    and class_tokens <= label_tokens
                ):
                    template_detail = (
                        "generated PANTHER definition contains only the label/model "
                        f"template plus lexically redundant protein class {protein_class!r}"
                    )
            if generated and template_detail is not None:
                findings.append(
                    Finding(
                        code="DEFINITION_TEMPLATE_ONLY",
                        severity=HARD,
                        detail=template_detail,
                    )
                )

            panther = self.panther_entries.get(panther_accession)
            if panther is None:
                raise ContentGateError(
                    f"{identifier}: pinned PANTHER classifications cannot be replayed"
                )
            mapped_ipr = _mapped_interpro(record)
            record_identity = _family_identity(label)
            if mapped_ipr and record_identity is not None:
                if not panther.children:
                    raise ContentGateError(
                        f"{identifier}: pinned PANTHER family has no child classifications"
                    )
                classified_children = [
                    (child_name, identity)
                    for child_name in panther.children.values()
                    if (identity := _family_identity(child_name)) is not None
                ]
                generic_children = [
                    child_name
                    for child_name in panther.children.values()
                    if _family_identity(child_name) is None
                    and _generic_panther_child_name(child_name)
                ]
                unclassified_children = [
                    child_name
                    for child_name in panther.children.values()
                    if _family_identity(child_name) is None
                    and not _generic_panther_child_name(child_name)
                ]
                child_identities = {identity for _name, identity in classified_children}
                # Two independently named informative children are the minimum.  This
                # preserves the prior conservative negative control where one PARP
                # child plus one uncharacterized child was insufficient evidence.
                informative_children_agree = (
                    len(classified_children) >= 2
                    and len(child_identities) == 1
                    and not unclassified_children
                )
                interpro = self.interpro_entries.get(mapped_ipr)
                if interpro is None:
                    raise ContentGateError(
                        f"{identifier}: mapped InterPro:{mapped_ipr} cannot be replayed"
                    )
                if panther_accession not in interpro.panther_members:
                    raise ContentGateError(
                        f"{identifier}: InterPro:{mapped_ipr} does not contain exact "
                        f"PANTHER member {panther_accession} in the pinned XML"
                    )
                interpro_identity = _family_identity(f"{interpro.short_name} {interpro.name}")
                member_identity = _family_identity(interpro.panther_members[panther_accession])
                panther_root_identity = _family_identity(panther.name)
                if informative_children_agree and panther_root_identity == record_identity:
                    child_identity = next(iter(child_identities))
                    if (
                        child_identity != record_identity
                        and interpro_identity == child_identity
                        and member_identity == child_identity
                    ):
                        findings.append(
                            Finding(
                                code="SOURCE_FAMILY_IDENTITY_CONFLICT",
                                severity=HARD,
                                detail=(
                                    f"record label and PANTHER root {label!r} imply "
                                    f"{record_identity}, but all {len(classified_children)} "
                                    f"informative PANTHER 19.0 child names (of "
                                    f"{len(panther.children)}; {len(generic_children)} exact "
                                    f"generic ignored) imply {child_identity}, corroborated by "
                                    f"the exact PANTHER member in InterPro:{mapped_ipr} "
                                    f"{interpro.short_name!r}/{interpro.name!r}"
                                ),
                                source_bindings=(
                                    *self._panther_source_bindings(panther),
                                    *self._interpro_panther_bindings(interpro),
                                ),
                            )
                        )

        pfam_match = _PFAM.fullmatch(identifier)
        if pfam_match and _needs_pfam(record):
            pfam_accession = pfam_match.group(1)
            pfam = self.pfam_entries.get(pfam_accession)
            if pfam is None:
                raise ContentGateError(f"{identifier}: pinned Pfam record cannot be replayed")
            if record.get("definition_source") == "Pfam":
                expected = _collapse(
                    f"{pfam.description or pfam.short_name}. Pfam {pfam.entry_type.lower()} "
                    f"family {pfam.short_name} (Pfam:{pfam_accession})."
                )
                if definition == expected:
                    findings.append(
                        Finding(
                            code="DEFINITION_TEMPLATE_ONLY",
                            severity=HARD,
                            detail="definition is the exact source-name/identifier Pfam seeder template",
                            source_bindings=self._pfam_source_bindings(pfam),
                        )
                    )

            mapped_ipr = _mapped_interpro(record)
            if mapped_ipr:
                integrated_ipr = self.pfam_integrations.get(pfam_accession)
                if integrated_ipr is None:
                    raise ContentGateError(
                        f"{identifier}: no exact PFAM member-list integration in pinned InterPro XML"
                    )
                if integrated_ipr != mapped_ipr:
                    raise ContentGateError(
                        f"{identifier}: mapped InterPro:{mapped_ipr} disagrees with pinned "
                        f"member-list InterPro:{integrated_ipr}"
                    )
                interpro = self.interpro_entries[integrated_ipr]
                member_name = interpro.pfam_members.get(pfam_accession, "")
                member_direction = _directions(member_name)
                entry_direction = _directions(f"{interpro.short_name} {interpro.name}")
                positional_conflict: str | None = None
                if (
                    len(member_direction) == 1
                    and len(entry_direction) == 1
                    and member_direction.isdisjoint(entry_direction)
                ):
                    positional_conflict = (
                        f"Pfam member name {member_name!r} says "
                        f"{next(iter(member_direction))}-terminal while InterPro "
                        f"{integrated_ipr} {interpro.short_name!r}/{interpro.name!r} says "
                        f"{next(iter(entry_direction))}-terminal"
                    )
                pfam_ordinals = _ordinals(f"{pfam.short_name} {pfam.description} {member_name}")
                interpro_ordinals = _ordinals(f"{interpro.short_name} {interpro.name}")
                if (
                    positional_conflict is None
                    and len(pfam_ordinals) == 1
                    and len(interpro_ordinals) == 1
                    and pfam_ordinals.isdisjoint(interpro_ordinals)
                ):
                    positional_conflict = (
                        f"Pfam {pfam_accession} source/member identity says ordinal "
                        f"{next(iter(pfam_ordinals))}, while InterPro:{integrated_ipr} "
                        f"{interpro.short_name!r}/{interpro.name!r} says ordinal "
                        f"{next(iter(interpro_ordinals))}"
                    )
                if positional_conflict is not None:
                    findings.append(
                        Finding(
                            code="SOURCE_POSITIONAL_IDENTITY_CONFLICT",
                            severity=HARD,
                            detail=positional_conflict,
                            source_bindings=(
                                *self._pfam_source_bindings(pfam),
                                *self._interpro_bindings(interpro),
                            ),
                        )
                    )
                pfam_scope = _source_scope(pfam.entry_type, source="Pfam")
                interpro_scope = _source_scope(interpro.entry_type, source="InterPro")
                if pfam_scope != interpro_scope:
                    findings.append(
                        Finding(
                            code="SOURCE_SCOPE_CONFLICT",
                            severity=HARD,
                            detail=(
                                f"Pfam type {pfam.entry_type!r} implies {pfam_scope}, but "
                                f"InterPro:{integrated_ipr} type {interpro.entry_type!r} "
                                f"implies {interpro_scope}"
                            ),
                            source_bindings=(
                                *self._pfam_source_bindings(pfam),
                                *self._interpro_bindings(interpro),
                            ),
                        )
                    )

        low_information = _low_information_flag(record)
        if low_information is not None:
            findings.append(low_information)
        return sorted(
            findings, key=lambda finding: (finding.severity, finding.code, finding.detail)
        )

    def evaluate_candidate(
        self, record: Mapping[str, Any], candidate: Mapping[str, Any]
    ) -> list[Finding]:
        """Evaluate late, candidate-specific review signals after evidence normalization."""

        identifier = str(record.get("identifier") or "")
        panther_match = _PANTHER.fullmatch(identifier)
        if panther_match is None:
            return []
        panther_accession = panther_match.group(1)
        if not (
            _panther_full_length_claim(record, panther_accession)
            and candidate.get("trait_id") == identifier
            and candidate.get("source_trait_id") == identifier
            and candidate.get("mapping_method") == "INTERPRO_MATCH"
            and candidate.get("scope") == "WHOLE_PROTEIN"
        ):
            return []
        panther = self.panther_entries.get(panther_accession)
        if panther is None:
            raise ContentGateError(
                f"{identifier}: pinned PANTHER classifications cannot be replayed"
            )
        covered, length, merged = _merged_candidate_coverage(candidate, identifier=identifier)
        # Strictly below 25%; exactly one quarter is the conservative
        # negative-control boundary and does not trigger this review signal.
        if covered * 4 >= length:
            return []
        return [
            Finding(
                code="LOW_WHOLE_PROTEIN_FAMILY_COVERAGE",
                severity=REVIEW,
                detail=(
                    f"explicit full-length family claim conflicts with InterPro match "
                    f"coverage {covered}/{length} residues ({covered / length:.1%}); "
                    f"merged intervals={merged}"
                ),
                source_bindings=self._panther_source_bindings(panther),
            )
        ]


def hard_reasons(findings: Iterable[Finding]) -> list[str]:
    return sorted(
        {REASON_PREFIX + finding.code.lower() for finding in findings if finding.severity == HARD}
    )


def _load_ledger(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ContentGateError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ContentGateError(f"{path}:{line_number}: ledger row is not an object")
            rows.append(row)
    if not rows:
        raise ContentGateError(f"ledger has no rows: {path}")
    return rows


def _record_path(value: Any, traits: Path) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ContentGateError("ledger row lacks record_path")
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path if value.startswith("data/traits/") else traits / value
    path = path.resolve()
    try:
        path.relative_to(traits.resolve())
    except ValueError as exc:
        raise ContentGateError(f"record path is outside --traits: {value}") from exc
    if not path.is_file():
        raise ContentGateError(f"record does not exist: {path}")
    return path


def _load_record(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        record = yaml.load(handle, Loader=_YAML_LOADER)
    if not isinstance(record, dict):
        raise ContentGateError(f"record is not a YAML mapping: {path}")
    return record


def _decision_map(path: Path | None, jsonl_paths: Sequence[Path]) -> dict[str, str]:
    decisions: dict[str, str] = {}

    def add(candidate_id: str, decision: str, source: str) -> None:
        candidate_id = candidate_id.strip()
        decision = decision.strip().upper()
        if not candidate_id:
            raise ContentGateError(f"{source}: missing candidate_id")
        if decision not in {"", "APPROVED", "REJECTED"}:
            raise ContentGateError(f"{source}: invalid decision {decision!r}")
        if candidate_id in decisions:
            raise ContentGateError(f"{source}: duplicate candidate_id {candidate_id}")
        decisions[candidate_id] = decision

    if path is not None:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if not reader.fieldnames or not {"candidate_id", "decision"} <= set(reader.fieldnames):
                raise ContentGateError("decision TSV requires candidate_id and decision columns")
            for line_number, row in enumerate(reader, 2):
                add(
                    row.get("candidate_id") or "",
                    row.get("decision") or "",
                    f"{path}:{line_number}",
                )

    for jsonl_path in jsonl_paths:
        for line_number, row in enumerate(_load_ledger(jsonl_path), 1):
            add(
                str(row.get("candidate_id") or ""),
                str(row.get("decision") or ""),
                f"{jsonl_path}:{line_number}",
            )
    return decisions


def replay_ledger(
    ledger: Path,
    *,
    traits: Path,
    config: SourceConfig,
    decisions_tsv: Path | None = None,
    decisions_jsonl: Sequence[Path] = (),
) -> dict[str, Any]:
    rows = _load_ledger(ledger)
    paths: dict[Path, list[dict[str, Any]]] = defaultdict(list)
    records: dict[Path, dict[str, Any]] = {}
    resolved_paths: dict[str, Path] = {}
    for row in rows:
        raw_path = row.get("record_path")
        if isinstance(raw_path, str) and raw_path in resolved_paths:
            path = resolved_paths[raw_path]
        else:
            path = _record_path(raw_path, traits)
            if isinstance(raw_path, str):
                resolved_paths[raw_path] = path
        paths[path].append(row)
        if path not in records:
            records[path] = _load_record(path)
    gate = RecordContentGate(list(records.values()), config)
    decisions = _decision_map(decisions_tsv, decisions_jsonl)
    findings_by_path: dict[Path, list[Finding]] = {}
    findings_by_row: list[tuple[Path, dict[str, Any], list[Finding]]] = []
    for path, path_rows in paths.items():
        unique: dict[str, Finding] = {}
        for row in path_rows:
            findings = [
                *gate.evaluate(records[path]),
                *gate.evaluate_candidate(records[path], row),
            ]
            findings_by_row.append((path, row, findings))
            for finding in findings:
                unique[_canonical_json(finding.as_dict())] = finding
        findings_by_path[path] = sorted(
            unique.values(),
            key=lambda finding: (finding.severity, finding.code, finding.detail),
        )
    hard_paths = {
        path
        for path, findings in findings_by_path.items()
        if any(finding.severity == HARD for finding in findings)
    }
    hard_rows = [
        row
        for _path, row, findings in findings_by_row
        if any(finding.severity == HARD for finding in findings)
    ]
    approved_ids = {
        candidate_id for candidate_id, decision in decisions.items() if decision == "APPROVED"
    }
    hard_approved = [row for row in hard_rows if str(row.get("candidate_id") or "") in approved_ids]
    finding_counts = Counter(
        finding.code for findings in findings_by_path.values() for finding in findings
    )
    return {
        "schema_version": 1,
        "ledger": _display_path(ledger),
        "ledger_sha256": hashlib.sha256(ledger.read_bytes()).hexdigest(),
        "record_count": len(records),
        "candidate_row_count": len(rows),
        "hard_record_count": len(hard_paths),
        "hard_candidate_row_count": len(hard_rows),
        "approved_candidate_count": len(approved_ids),
        "hard_approved_candidate_count": len(hard_approved),
        "findings_by_code": dict(sorted(finding_counts.items())),
        "hard_record_ids": sorted(
            str(records[path].get("identifier") or "") for path in hard_paths
        ),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--traits", type=Path, default=REPO_ROOT / "data" / "traits")
    parser.add_argument("--decisions-tsv", type=Path)
    parser.add_argument(
        "--decisions-jsonl",
        type=Path,
        action="append",
        default=[],
        help="review-decision JSONL partition; repeat for disjoint partitions",
    )
    parser.add_argument("--interpro-xml", type=Path, default=DEFAULT_INTERPRO_XML)
    parser.add_argument("--interpro-xml-sha256", default=INTERPRO_109_XML_SHA256)
    parser.add_argument("--pfam-clans", type=Path, default=DEFAULT_PFAM_CLANS)
    parser.add_argument("--pfam-clans-sha256", default=PFAM_A_CLANS_SHA256)
    parser.add_argument("--pfam-types", type=Path, default=DEFAULT_PFAM_TYPES)
    parser.add_argument("--pfam-types-sha256", default=PFAM_TYPES_SHA256)
    parser.add_argument(
        "--panther-classifications", type=Path, default=DEFAULT_PANTHER_CLASSIFICATIONS
    )
    parser.add_argument(
        "--panther-classifications-sha256", default=PANTHER_19_CLASSIFICATIONS_SHA256
    )
    parser.add_argument("--fail-on-hard-approved", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        summary = replay_ledger(
            args.ledger,
            traits=args.traits,
            decisions_tsv=args.decisions_tsv,
            decisions_jsonl=args.decisions_jsonl,
            config=SourceConfig(
                interpro_xml=args.interpro_xml,
                interpro_xml_sha256=args.interpro_xml_sha256,
                pfam_clans=args.pfam_clans,
                pfam_clans_sha256=args.pfam_clans_sha256,
                pfam_types=args.pfam_types,
                pfam_types_sha256=args.pfam_types_sha256,
                panther_classifications=args.panther_classifications,
                panther_classifications_sha256=args.panther_classifications_sha256,
            ),
        )
    except (ContentGateError, OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, sort_keys=True))
    return int(args.fail_on_hard_approved and summary["hard_approved_candidate_count"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())
