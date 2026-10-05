#!/usr/bin/env python3
r"""Track the protein examples sibling Mechs carry and route each to its trait record (#652).

WHY THIS EXISTS
---------------
The UniProt grounding funnel discovers candidates only from this repository's own
trait records and local provider frames, so a protein that only a sibling Mech
curates never reaches review (#652). Yet the siblings often say *which trait* a
protein exemplifies: a NaturalProductMech biosynthetic step names the enzyme and the
Rhea reaction it catalyses, a TraitMech causal-graph node pairs a GO or InterPro
grounding with protein examples, and a CellStructureMech complex composition lists
the ComplexPortal components of a cellular structure. When that annotation is an
exact ProteinTraitsMech trait identifier, the protein belongs on that trait record.

THREE LAYERS, THREE TRUST LEVELS
--------------------------------
1. SNAPSHOT (tracked, ``data/cross_mech/``) -- what the siblings say. One row per
   UniProtKB protein mention in a structured field of a sibling record, read from
   git objects at a pinned commit (never a working tree: a sibling checkout may sit
   on a feature branch). Each mention is classified by a declared CHANNEL rule into a
   role (EXAMPLE, TARGET, GRAPH_NODE, SUBSTRATE, REFERENCE, CROSSWALK), a relation,
   and the sibling CURIEs that name its trait. A mention no rule recognises is
   UNCLASSIFIED, never dropped, so a sibling that starts storing proteins somewhere
   new surfaces as drift instead of disappearing.
2. AUDIT (read-only, ``reports/cross-mech/``) -- how this repository reads it. Every
   (protein, annotation) pair a channel declares is resolved to an exact trait
   record (a Rhea directional ID to its master reaction through the pinned
   ``rhea-directions.tsv``), joined with that record's canonical examples, and given
   exactly one status: QUALIFIED_ON_TRAIT, LEGACY_ON_TRAIT, ABSENT_FROM_TRAIT,
   TRAIT_NOT_IN_PTM, or NOT_A_PTM_NAMESPACE.
3. CANDIDATES (``candidates``, ignored ``reports/uniprot-grounding/cross-mech/``) -- one
   grounding-funnel candidate per ABSENT or LEGACY pair that has a route, carrying the
   sibling provenance. The ordinary selector, fetch, resolver, review, and promoter
   take it from there.
4. INCLUSION -- not here. A sibling assertion is discovery provenance, never
   qualification evidence: CellStructureMech says in its own records that a protein
   example "is not itself evidence that the protein is part of this structure". An
   ABSENT or LEGACY pair becomes a grounding-funnel candidate, and qualifies only
   through the same release-pinned select -> fetch -> resolve -> review -> promote
   route as every other example. This module writes no trait record.

Fleet membership comes from claw's canonical manifest
(``CultureBotAI/culturebotai-claw:src/kg_microbe_fleet/fleet.yaml``), pinned by
commit and SHA-256 in the snapshot manifest, never from a list re-declared here.

COMMANDS
--------
``scan``   read every fleet Mech at ``origin/main`` and print the snapshot summary;
           ``--apply`` replaces ``data/cross_mech/`` atomically.
``audit``  resolve the snapshot against ``data/traits`` and write the status report.
``check``  verify snapshot integrity offline; ``--local`` / ``--remote`` add a drift
           report against sibling checkouts / live default branches (NOTICE only
           unless ``--fail-on-drift``).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from http.client import HTTPException
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TRAITS_ROOT = REPO_ROOT / "data" / "traits"
SNAPSHOT_DIR = REPO_ROOT / "data" / "cross_mech"
MENTIONS_NAME = "protein_mentions.jsonl"
MANIFEST_NAME = "manifest.json"
REPORT_DIR = REPO_ROOT / "reports" / "cross-mech"
CANDIDATE_QUEUE = REPO_ROOT / "reports" / "uniprot-grounding" / "cross-mech" / "candidates.jsonl"
CANDIDATE_BATCH = "cross-mech"
# Discovery-state reasons every UniProt-fact producer attaches; the resolver discharges
# them only through the exact release/checksum/fact replay (ground_uniprot_examples).
CANDIDATE_RESOLUTION_REASONS = (
    "exact membership must be replayed from a same-response UniProt xref snapshot",
    "full release-pinned sequence and checksum require resolution",
)
RHEA_DIRECTIONS = REPO_ROOT / "data" / "raw" / "rhea" / "rhea-directions.tsv"
# The release-141-compatible bytes stage_rhea_uniprot_grounding.py already pins;
# tests/test_cross_mech_proteins.py asserts the two pins stay equal.
RHEA_DIRECTIONS_SHA256 = "0b62f0cd92991b89e7b6e05707e671e80787527c30192b3d44cf7fc05a5c748f"

SNAPSHOT_KIND = "proteintraitsmech-cross-mech-protein-snapshot"
SNAPSHOT_SCHEMA_VERSION = 1
SELF_KEY = "proteintraitsmech"
DEFAULT_REF = "origin/main"
FLEET_REPOSITORY = "CultureBotAI/culturebotai-claw"
FLEET_PATH = "src/kg_microbe_fleet/fleet.yaml"
GITHUB_HOST = "github.com"
RAW_HOST = "raw.githubusercontent.com"
_FETCH_TIMEOUT_SECONDS = 30
_FETCH_MAX_BYTES = 2_000_000

_ACCESSION = r"(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})"
# Prefixed forms are recognised under any key; a bare accession only under a key whose
# name already says it holds one, so a coincidental six-character token stays text.
PREFIXED_PROTEIN = re.compile(rf"^(?:UniProtKB|UniProt|uniprot|uniprotkb):({_ACCESSION}(?:-\d+)?)$")
BARE_PROTEIN = re.compile(rf"^({_ACCESSION}(?:-\d+)?)$")
BARE_PROTEIN_KEYS = frozenset(
    {"uniprot_id", "uniprot_accession", "protein_accession", "uniprot", "uniprotkb"}
)
# Byte prefilter for the scan: every prefixed form contains "niprot" (any case) and the
# only bare-accession key without it is protein_accession, so a blob matching neither
# cannot hold a mention and is not parsed (TaxonMech alone has ~626k records).
PROTEIN_PREFILTER = re.compile(rb"(?i)niprot|protein_accession")
# Bump whenever iter_mentions/annotations_for/mention_rows change what a row says, so the
# rule digest (and `check`) notices code that hashing the declared tables cannot (#967).
EXTRACTION_VERSION = 2
CURIE = re.compile(r"^([A-Za-z][A-Za-z0-9_.-]*):(\S+)$")
_NON_CURIE_SCHEMES = frozenset({"http", "https", "ftp", "file", "mailto", "urn"})
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
COMMIT_HEX = re.compile(r"^[0-9a-f]{40}$")

ROLES = (
    "EXAMPLE",  # the sibling says the protein carries or exemplifies something
    "TARGET",  # a compound's measured target; says nothing about the protein's own traits
    "GRAPH_NODE",  # a causal-graph node that IS the protein
    "SUBSTRATE",  # the protein is a substrate (e.g. a precursor peptide)
    "REFERENCE",  # the UniProt entry is cited as evidence or a reference sequence
    "CROSSWALK",  # an identifier mapping row
    "UNCLASSIFIED",  # no channel rule recognises this path: drift to triage
)

# A route is how a namespace could QUALIFY once the funnel admits it; the audit only
# reports it. Signature namespaces use the exact InterPro/member match (or whole-protein
# UniProt membership where the record allows it); the functional namespaces need the
# UniProt exact-accession annotation lane.
SIGNATURE_NAMESPACES = frozenset(
    {
        "CDD",
        "CATH",
        "HAMAP",
        "InterPro",
        "NCBIfam",
        "PANTHER",
        "Pfam",
        "PRINTS",
        "PROSITE",
        "SFLD",
        "SMART",
        "SUPERFAMILY",
    }
)
UNIPROT_ANNOTATION_NAMESPACES = frozenset({"GO", "RHEA", "ComplexPortal"})


class CrossMechError(RuntimeError):
    """A sibling, the fleet manifest, or the snapshot cannot be read as declared."""


# --------------------------------------------------------------------------- rules


@dataclass(frozen=True)
class AnnotationSource:
    """Where a channel finds the CURIE that names the protein's trait.

    ``scope`` is the object the key is read from, relative to the mention:
    ``self`` is the mapping holding the protein value, ``parent`` the next mapping up,
    ``record`` the record root, and ``list`` the other entries of the list the protein
    value sits in (a node's ``xrefs``). ``when`` restricts the source to objects whose
    named keys hold one of the listed values on the same scope (an edge predicate).
    """

    scope: str
    key: str
    relation: str
    when: tuple[tuple[str, tuple[str, ...]], ...] = ()

    def projection(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "key": self.key,
            "relation": self.relation,
            "when": [[key, list(values)] for key, values in self.when],
        }


@dataclass(frozen=True)
class Channel:
    """One declared place a sibling Mech stores a protein, and what it means there."""

    key: str
    mech: str
    pattern: str
    role: str
    relation: str
    annotations: tuple[AnnotationSource, ...] = ()
    label_key: str | None = None
    # Keys on an annotation's scope object that qualify the claim (NaturalProductMech's
    # `proposed`: "inferred rather than demonstrated"). Copied onto each annotation so a
    # sibling's own hedge is never lost (#965).
    qualifier_keys: tuple[str, ...] = ()
    note: str = ""

    def projection(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "mech": self.mech,
            "pattern": self.pattern,
            "role": self.role,
            "relation": self.relation,
            "annotations": [source.projection() for source in self.annotations],
            "label_key": self.label_key,
            "qualifier_keys": list(self.qualifier_keys),
        }


def _src(scope: str, key: str, relation: str, **when: Sequence[str]) -> AnnotationSource:
    return AnnotationSource(
        scope, key, relation, tuple((name, tuple(values)) for name, values in sorted(when.items()))
    )


# Every protein-bearing path observed at the 2026-10-05 fleet heads, one rule each.
# Adding a sibling field means adding a rule here (and a test); until then its
# mentions are UNCLASSIFIED and `check` reports them.
CHANNELS: tuple[Channel, ...] = (
    Channel(
        "antibioticmech.resistance_protein",
        "antibioticmech",
        "/resistance_mechanisms/[]/protein_accession",
        "EXAMPLE",
        "associated_with_resistance_phenotype",
        (
            _src("self", "aro_id", "resistance_gene_family"),
            _src("self", "phenotype_id", "resistance_phenotype"),
        ),
        note="PHI-base gene alteration associated with resistance; not a biochemical mechanism.",
    ),
    Channel(
        "antibioticmech.target_protein_example",
        "antibioticmech",
        "/molecular_targets/[]/protein_examples/[]/uniprot_id",
        "TARGET",
        "measured_target_of_compound",
        label_key="protein_label",
    ),
    Channel(
        "antibioticmech.causal_node_xref",
        "antibioticmech",
        "/causal_graphs/[]/nodes/[]/xrefs/[]",
        "GRAPH_NODE",
        "node_xref",
        (_src("list", "xrefs", "node_xref"), _src("self", "grounding", "node_grounding")),
    ),
    Channel(
        "cellstructuremech.component_protein_example",
        "cellstructuremech",
        "/components/[]/protein_examples/[]/uniprot_id",
        "EXAMPLE",
        "exemplifies_component",
        (
            _src("parent", "grounding", "exemplifies_component_grounding"),
            _src("record", "identifier", "component_of_structure"),
        ),
        label_key="protein_label",
        note="CellStructureMech: the accession identifies the component gene; it is not "
        "evidence of structure membership.",
    ),
    Channel(
        "cellstructuremech.complex_participant",
        "cellstructuremech",
        "/complex_compositions/[]/participants/[]/participant_id",
        "EXAMPLE",
        "component_of_complex",
        (
            _src("parent", "source_accession", "component_of_complex"),
            _src("record", "identifier", "component_of_structure"),
        ),
        label_key="label",
    ),
    Channel(
        "cellstructuremech.causal_node_xref",
        "cellstructuremech",
        "/causal_graphs/[]/nodes/[]/xrefs/[]",
        "GRAPH_NODE",
        "node_xref",
        (_src("list", "xrefs", "node_xref"), _src("self", "grounding", "node_grounding")),
    ),
    Channel(
        "cellstructuremech.canonical_example_reference",
        "cellstructuremech",
        "/canonical_examples/[]/reference",
        "REFERENCE",
        "reference_sequence",
    ),
    Channel(
        "naturalproductmech.biosynthetic_enzyme",
        "naturalproductmech",
        "/biosynthetic_pathway/[]/enzyme_id",
        "EXAMPLE",
        "catalyzes",
        (_src("self", "reaction_id", "catalyzes"),),
        label_key="enzyme_label",
        qualifier_keys=("proposed",),
    ),
    Channel(
        "naturalproductmech.biosynthetic_substrate",
        "naturalproductmech",
        "/biosynthetic_pathway/[]/substrate",
        "SUBSTRATE",
        "substrate_of_biosynthetic_step",
    ),
    Channel(
        "naturalproductmech.causal_node",
        "naturalproductmech",
        "/causal_graphs/[]/nodes/[]/identifier",
        "GRAPH_NODE",
        "node_identifier",
    ),
    Channel(
        "naturalproductmech.bioactivity_target",
        "naturalproductmech",
        "/bioactivities/[]/target_enzyme",
        "TARGET",
        "bioactivity_target",
    ),
    Channel(
        "naturalproductmech.target_protein_example",
        "naturalproductmech",
        "/molecular_targets/[]/protein_examples/[]",
        "TARGET",
        "measured_target_of_compound",
    ),
    Channel(
        "pathwaymech.catalyzing_edge_subject",
        "pathwaymech",
        "/mechanistic_edges/[]/subject",
        "EXAMPLE",
        "edge_subject",
        (_src("self", "object", "catalyzes", predicate=("catalyzes",)),),
    ),
    Channel(
        "pathwaymech.pathway_participant",
        "pathwaymech",
        "/participants/[]/id",
        "EXAMPLE",
        "participates_in_pathway",
        (_src("record", "id", "participates_in_pathway"),),
        label_key="label",
    ),
    Channel(
        "pathwaymech.source_mapping_subject",
        "pathwaymech",
        "/source_mappings/[]/subject_id",
        "CROSSWALK",
        "source_mapping",
    ),
    Channel(
        "pathwaymech.source_mapping_object",
        "pathwaymech",
        "/source_mappings/[]/object_id",
        "CROSSWALK",
        "source_mapping",
    ),
    Channel(
        "pathwaymech.reference",
        "pathwaymech",
        "/references/[]/id",
        "REFERENCE",
        "reference",
    ),
    Channel(
        "traitmech.node_protein_example",
        "traitmech",
        "/causal_graphs/[]/nodes/[]/protein_examples/[]/uniprot_id",
        "EXAMPLE",
        "exemplifies_node",
        (_src("parent", "grounding", "exemplifies_node_grounding"),),
        label_key="protein_label",
    ),
)

# Any Mech: a UniProt entry cited as evidence is a reference, not an example.
GENERIC_SUFFIX_CHANNELS: tuple[tuple[str, str, str], ...] = (
    ("/evidence/[]/reference", "REFERENCE", "evidence_reference"),
    ("/evidence/[]/reference_id", "REFERENCE", "evidence_reference"),
)

_CHANNEL_INDEX = {(channel.mech, channel.pattern): channel for channel in CHANNELS}
if len(_CHANNEL_INDEX) != len(CHANNELS):
    raise CrossMechError("duplicate (mech, pattern) channel rule")


def rules_projection() -> dict[str, Any]:
    """Everything that decides a snapshot row besides sibling bytes."""

    return {
        "channels": [channel.projection() for channel in CHANNELS],
        "generic_suffix_channels": [list(rule) for rule in GENERIC_SUFFIX_CHANNELS],
        "prefixed_protein": PREFIXED_PROTEIN.pattern,
        "bare_protein": BARE_PROTEIN.pattern,
        "bare_protein_keys": sorted(BARE_PROTEIN_KEYS),
        "curie": CURIE.pattern,
        "non_curie_schemes": sorted(_NON_CURIE_SCHEMES),
        "protein_prefilter": PROTEIN_PREFILTER.pattern.decode("ascii"),
        "generalize": _GENERALIZE.pattern,
        "extraction_version": EXTRACTION_VERSION,
    }


def rules_sha256() -> str:
    return sha256_text(canonical_json(rules_projection()))


def classify(mech: str, pattern: str) -> tuple[Channel | None, str, str]:
    """Return (channel, role, relation) for one generalized mention path."""

    channel = _CHANNEL_INDEX.get((mech, pattern))
    if channel is not None:
        return channel, channel.role, channel.relation
    for suffix, role, relation in GENERIC_SUFFIX_CHANNELS:
        if pattern.endswith(suffix):
            return None, role, relation
    return None, "UNCLASSIFIED", ""


# --------------------------------------------------------------------- utilities


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a fleet ``record_globs`` entry; ``**/`` matches zero or more directories."""

    out: list[str] = []
    index = 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            out.append("(?:[^/]+/)*")
            index += 3
        elif pattern.startswith("**", index):
            out.append(".*")
            index += 2
        elif pattern[index] == "*":
            out.append("[^/]*")
            index += 1
        elif pattern[index] == "?":
            out.append("[^/]")
            index += 1
        elif pattern[index] == "[" and "]" in pattern[index + 2 :]:
            # fnmatch-style class, as pathlib and claw's validator accept: [abc], [!abc].
            close = pattern.index("]", index + 2)
            body = pattern[index + 1 : close]
            negate = body.startswith("!")
            body = body[1:] if negate else body
            escaped = body.replace("\\", "\\\\").replace("^", "\\^").replace("]", "\\]")
            out.append(("[^/" if negate else "[") + escaped + "]")
            index = close + 1
        else:
            out.append(re.escape(pattern[index]))
            index += 1
    return re.compile("^" + "".join(out) + "$")


def _pointer_token(key: Any) -> str:
    return str(key).replace("~", "~0").replace("/", "~1")


_GENERALIZE = re.compile(r"/\d+(?=/|$)")


def generalize(pointer: str) -> str:
    """Replace list indices with ``[]`` so one rule covers every element."""

    return _GENERALIZE.sub("/[]", pointer)


def _is_curie(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    match = CURIE.match(value.strip())
    return bool(match) and match.group(1).lower() not in _NON_CURIE_SCHEMES


def _curies(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if _is_curie(value) else []
    if isinstance(value, list):
        return [item.strip() for item in value if _is_curie(item)]
    return []


def _protein_value(key: str, value: str) -> str | None:
    text = value.strip()
    match = PREFIXED_PROTEIN.match(text)
    if match is None and key in BARE_PROTEIN_KEYS:
        match = BARE_PROTEIN.match(text)
    return match.group(1) if match else None


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


# ------------------------------------------------------------------ fleet manifest


@dataclass(frozen=True)
class MechTarget:
    key: str
    github: str
    record_globs: tuple[str, ...]
    environment_variable: str = ""

    @property
    def repo_name(self) -> str:
        return self.github.split("/", 1)[1]


@dataclass(frozen=True)
class FleetManifest:
    commit: str
    sha256: str
    targets: tuple[MechTarget, ...]
    self_github: str


def parse_fleet_manifest(text: str, *, commit: str) -> FleetManifest:
    """Read the sibling Mechs and their record globs from claw's manifest bytes."""

    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise CrossMechError(f"fleet manifest is not YAML: {error}") from error
    if not isinstance(document, Mapping) or document.get("version") != 1:
        raise CrossMechError("fleet manifest must be a version-1 mapping")
    mechs = document.get("mechs")
    if not isinstance(mechs, Mapping) or not mechs:
        raise CrossMechError("fleet manifest declares no mechs")
    targets: list[MechTarget] = []
    self_github = ""
    for key, entry in mechs.items():
        if not isinstance(key, str) or not isinstance(entry, Mapping):
            raise CrossMechError(f"fleet manifest mech {key!r} is malformed")
        github = entry.get("github")
        globs = entry.get("record_globs")
        if not isinstance(github, str) or github.count("/") != 1:
            raise CrossMechError(f"fleet manifest mech {key!r} lacks an owner/repo github slug")
        if not isinstance(globs, list) or not all(isinstance(g, str) and g for g in globs):
            raise CrossMechError(f"fleet manifest mech {key!r} lacks record_globs")
        if key == SELF_KEY:
            self_github = github
            continue
        variable = entry.get("environment_variable")
        targets.append(
            MechTarget(
                key=key,
                github=github,
                record_globs=tuple(globs),
                environment_variable=variable if isinstance(variable, str) else "",
            )
        )
    if not self_github:
        raise CrossMechError(f"fleet manifest does not list {SELF_KEY}; refusing a foreign fleet")
    return FleetManifest(
        commit=commit,
        sha256=sha256_text(text),
        targets=tuple(sorted(targets, key=lambda target: target.key)),
        self_github=self_github,
    )


def _guarded_fetch(url: str, *, opener: Callable[..., Any], host: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "ProteinTraitsMech-cross-mech/1"})
    try:
        with opener(request, timeout=_FETCH_TIMEOUT_SECONDS) as response:
            final = urllib.parse.urlparse(response.geturl())
            if final.scheme != "https" or final.hostname != host:
                raise CrossMechError(f"fetch redirected off {host}: {final.geturl()}")
            if response.status != 200:
                raise CrossMechError(f"{url} returned HTTP {response.status}")
            raw = response.read(_FETCH_MAX_BYTES + 1)
    except (urllib.error.URLError, HTTPException, OSError) as error:
        # HTTPError (an error status urlopen raises), URLError, timeouts and resets all
        # mean "the network said no": a notice for the caller, never a crash (#962).
        raise CrossMechError(f"{url} could not be fetched: {error}") from error
    if len(raw) > _FETCH_MAX_BYTES:
        raise CrossMechError(f"{url} exceeds {_FETCH_MAX_BYTES} bytes")
    return raw


def remote_head(github: str, *, runner: Callable[..., Any] = subprocess.run) -> str:
    """The live default-branch commit of one GitHub repository, anonymously."""

    try:
        completed = runner(
            ["git", "ls-remote", f"https://{GITHUB_HOST}/{github}.git", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except (subprocess.TimeoutExpired, OSError) as error:
        raise CrossMechError(f"git ls-remote {github} did not complete: {error}") from error
    if completed.returncode:
        raise CrossMechError(f"git ls-remote {github} failed: {completed.stderr.strip()}")
    head = completed.stdout.split()[0] if completed.stdout.split() else ""
    if not COMMIT_HEX.fullmatch(head):
        raise CrossMechError(f"git ls-remote {github} returned no commit")
    return head


def fetch_fleet_manifest(
    commit: str | None = None,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
    runner: Callable[..., Any] = subprocess.run,
) -> FleetManifest:
    """claw's fleet manifest at an exact commit (the live default branch if omitted)."""

    resolved = commit or remote_head(FLEET_REPOSITORY, runner=runner)
    if not COMMIT_HEX.fullmatch(resolved):
        raise CrossMechError(f"fleet manifest commit must be a full SHA-1, got {resolved!r}")
    url = f"https://{RAW_HOST}/{FLEET_REPOSITORY}/{resolved}/{FLEET_PATH}"
    raw = _guarded_fetch(url, opener=opener, host=RAW_HOST)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CrossMechError(f"fleet manifest at {resolved} is not UTF-8") from error
    return parse_fleet_manifest(text, commit=resolved)


# ---------------------------------------------------------------- sibling checkouts


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )
    if completed.returncode:
        raise CrossMechError(f"git {' '.join(args)} failed in {repo}: {completed.stderr.strip()}")
    return completed.stdout


def normalize_remote(url: str) -> str:
    """``owner/repo`` (lower case) from an https, ssh, or scp-style GitHub remote URL."""

    text = url.strip()
    for prefix in (
        f"https://{GITHUB_HOST}/",
        f"http://{GITHUB_HOST}/",
        f"ssh://git@{GITHUB_HOST}/",
        f"git@{GITHUB_HOST}:",
    ):
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    else:
        return ""
    text = text.removesuffix("/").removesuffix(".git")
    return text.lower() if text.count("/") == 1 else ""


def resolve_checkout(target: MechTarget, mechs_root: Path, environ: Mapping[str, str]) -> Path:
    """Locate a sibling checkout and prove its origin is the manifest's repository."""

    configured = environ.get(target.environment_variable) if target.environment_variable else None
    repo = Path(configured) if configured else mechs_root / target.repo_name
    if not (repo / ".git").exists():
        raise CrossMechError(f"{target.key}: no git checkout at {repo}")
    origin = normalize_remote(_git(repo, "remote", "get-url", "origin"))
    if origin != target.github.lower():
        raise CrossMechError(
            f"{target.key}: {repo} has origin {origin or 'unknown'!r}, not {target.github!r}"
        )
    return repo


def list_records(repo: Path, commit: str, globs: Sequence[str]) -> list[tuple[str, str]]:
    """(blob sha, path) of every tracked file at ``commit`` that a record glob matches."""

    compiled = [glob_to_regex(glob) for glob in globs]
    listing = _git(repo, "ls-tree", "-r", "-z", "--full-tree", commit)
    blobs: list[tuple[str, str]] = []
    for entry in listing.split("\0"):
        if not entry:
            continue
        meta, path = entry.split("\t", 1)
        _, kind, sha = meta.split()
        if kind == "blob" and any(regex.match(path) for regex in compiled):
            blobs.append((sha, path))
    return sorted(blobs, key=lambda item: item[1])


def read_blobs(repo: Path, blobs: Sequence[tuple[str, str]]) -> Iterator[tuple[str, bytes]]:
    if not blobs:
        return
    process = subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert process.stdin is not None and process.stdout is not None
    try:
        for sha, path in blobs:
            process.stdin.write(f"{sha}\n".encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) != 3 or header[1] != b"blob":
                raise CrossMechError(f"{repo}: cannot read blob for {path}")
            data = process.stdout.read(int(header[2]))
            process.stdout.read(1)
            yield path, data
    finally:
        process.stdin.close()
        process.wait()


# ------------------------------------------------------------------- extraction


@dataclass
class Mention:
    pointer: str
    key: str
    raw_value: str
    protein_id: str
    chain: list[tuple[str, Mapping[str, Any]]]
    container: list[Any] | None = None


def iter_mentions(document: Any) -> list[Mention]:
    """Every UniProtKB protein value in a parsed record, with its enclosing objects.

    Strings are found at any list depth, including a root-level list (#968); a value in
    a list carries that list as ``container`` for ``list``-scope annotations.
    """

    found: list[Mention] = []

    def walk_list(
        values: list[Any], pointer: str, key: str, chain: list[tuple[str, Mapping[str, Any]]]
    ) -> None:
        for index, item in enumerate(values):
            item_pointer = f"{pointer}/{index}"
            if isinstance(item, str):
                accession = _protein_value(key, item)
                if accession:
                    found.append(
                        Mention(item_pointer, key, item, f"UniProtKB:{accession}", chain, values)
                    )
            elif isinstance(item, list):
                walk_list(item, item_pointer, key, chain)
            else:
                walk(item, item_pointer, chain)

    def walk(node: Any, pointer: str, chain: list[tuple[str, Mapping[str, Any]]]) -> None:
        if isinstance(node, Mapping):
            here = chain + [(pointer, node)]
            for key, value in node.items():
                child = f"{pointer}/{_pointer_token(key)}"
                if isinstance(value, str):
                    accession = _protein_value(str(key), value)
                    if accession:
                        found.append(
                            Mention(child, str(key), value, f"UniProtKB:{accession}", here)
                        )
                elif isinstance(value, list):
                    walk_list(value, child, str(key), here)
                elif isinstance(value, Mapping):
                    walk(value, child, here)
        elif isinstance(node, list):
            walk_list(node, pointer, "", chain)

    walk(document, "", [])
    return found


def _scope_object(mention: Mention, scope: str) -> Mapping[str, Any] | None:
    if not mention.chain:
        return None
    if scope == "self":
        return mention.chain[-1][1]
    if scope == "parent":
        return mention.chain[-2][1] if len(mention.chain) >= 2 else None
    if scope == "record":
        return mention.chain[0][1]
    raise CrossMechError(f"unknown annotation scope {scope!r}")


def annotations_for(mention: Mention, channel: Channel | None) -> list[dict[str, Any]]:
    if channel is None:
        return []
    out: list[dict[str, Any]] = []
    for source in channel.annotations:
        if source.scope == "list":
            values = [
                item.strip()
                for item in (mention.container or [])
                if _is_curie(item) and not PREFIXED_PROTEIN.match(item.strip())
            ]
            obj = _scope_object(mention, "self")
        else:
            obj = _scope_object(mention, source.scope)
            values = _curies(obj.get(source.key)) if obj is not None else []
        if obj is None or any(obj.get(key) not in allowed for key, allowed in source.when):
            continue
        qualifiers = {
            key: obj[key]
            for key in channel.qualifier_keys
            if isinstance(obj.get(key), (str, bool, int, float))
        }
        for value in values:
            if PREFIXED_PROTEIN.match(value):
                continue  # the protein itself, or another protein: not a trait
            annotation: dict[str, Any] = {
                "curie": value,
                "relation": source.relation,
                "source": f"{source.scope}.{source.key}",
            }
            if qualifiers:
                annotation["qualifiers"] = qualifiers
            out.append(annotation)
    unique = {canonical_json(item): item for item in out}
    return [unique[key] for key in sorted(unique)]


def _record_identity(document: Any) -> str | None:
    if isinstance(document, Mapping):
        for key in ("identifier", "id"):
            value = document.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def mention_rows(mech: str, record_path: str, document: Any) -> list[dict[str, Any]]:
    """Snapshot rows for one sibling record."""

    rows: list[dict[str, Any]] = []
    record_id = _record_identity(document)
    for mention in iter_mentions(document):
        pattern = generalize(mention.pointer)
        channel, role, relation = classify(mech, pattern)
        holder = mention.chain[-1][1] if mention.chain else {}
        label_value = holder.get(channel.label_key) if channel and channel.label_key else None
        label = (
            label_value.strip() if isinstance(label_value, str) and label_value.strip() else None
        )
        taxon = holder.get("taxon_id")
        rows.append(
            {
                "mech": mech,
                "record_path": record_path,
                "record_id": record_id,
                "pointer": mention.pointer,
                "pattern": pattern,
                "protein_id": mention.protein_id,
                "raw_value": mention.raw_value,
                "channel": channel.key if channel else None,
                "role": role,
                "relation": relation,
                "annotations": annotations_for(mention, channel),
                "sibling_label": label,
                "sibling_taxon_id": taxon.strip() if _is_curie(taxon) else None,
            }
        )
    return rows


# -------------------------------------------------------------------------- scan


@dataclass
class ScanResult:
    rows: list[dict[str, Any]] = field(default_factory=list)
    mechs: list[dict[str, Any]] = field(default_factory=list)


Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def scan_mech(target: MechTarget, repo: Path, ref: str) -> tuple[list[dict[str, Any]], dict]:
    commit = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()
    blobs = list_records(repo, commit, target.record_globs)
    rows: list[dict[str, Any]] = []
    with_proteins = 0
    for path, data in read_blobs(repo, blobs):
        if PROTEIN_PREFILTER.search(data) is None:
            continue  # sound: every recognised protein value matches the prefilter
        try:
            document = yaml.load(data.decode("utf-8"), Loader=Loader)  # noqa: S506 - safe loader
        except (UnicodeDecodeError, yaml.YAMLError) as error:
            raise CrossMechError(f"{target.key}:{path} is not readable YAML: {error}") from error
        record_rows = mention_rows(target.key, path, document)
        if record_rows:
            with_proteins += 1
            rows.extend(record_rows)
    summary = {
        "key": target.key,
        "github": target.github,
        "environment_variable": target.environment_variable,
        "ref": ref,
        "commit": commit,
        "record_globs": list(target.record_globs),
        "records_scanned": len(blobs),
        "records_with_proteins": with_proteins,
        "mentions": len(rows),
    }
    return rows, summary


def scan(
    fleet: FleetManifest,
    mechs_root: Path,
    *,
    ref: str = DEFAULT_REF,
    refs: Mapping[str, str] | None = None,
    environ: Mapping[str, str] | None = None,
    fetch: bool = False,
) -> ScanResult:
    """Scan every fleet Mech at ``ref``, or at its own commit in ``refs`` when given."""

    result = ScanResult()
    env = os.environ if environ is None else environ
    for target in fleet.targets:
        repo = resolve_checkout(target, mechs_root, env)
        if fetch:
            _git(repo, "fetch", "--quiet", "origin")
        if refs is not None and target.key not in refs:
            raise CrossMechError(f"{target.key} has no pinned commit to rescan at")
        rows, summary = scan_mech(target, repo, refs[target.key] if refs else ref)
        result.rows.extend(rows)
        result.mechs.append(summary)
    result.rows.sort(key=lambda row: (row["mech"], row["record_path"], row["pointer"]))
    keys = [(row["mech"], row["record_path"], row["pointer"]) for row in result.rows]
    if len(set(keys)) != len(keys):
        raise CrossMechError("internal error: duplicate mention keys")
    return result


def render_mentions(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(row) + "\n" for row in rows)


def snapshot_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_role = Counter(row["role"] for row in rows)
    proteins = {row["protein_id"] for row in rows}
    example_proteins = {row["protein_id"] for row in rows if row["role"] == "EXAMPLE"}
    annotated = {
        (row["protein_id"], annotation["curie"])
        for row in rows
        for annotation in row["annotations"]
    }
    return {
        "mentions": len(rows),
        "distinct_proteins": len(proteins),
        "distinct_example_proteins": len(example_proteins),
        "distinct_annotated_protein_pairs": len(annotated),
        "mentions_by_role": dict(sorted(by_role.items())),
        "unclassified_patterns": sorted(
            {f"{row['mech']}:{row['pattern']}" for row in rows if row["role"] == "UNCLASSIFIED"}
        ),
    }


def build_manifest(result: ScanResult, fleet: FleetManifest, mentions_text: str) -> dict:
    return {
        "kind": SNAPSHOT_KIND,
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "fleet_manifest": {
            "repository": FLEET_REPOSITORY,
            "path": FLEET_PATH,
            "commit": fleet.commit,
            "sha256": fleet.sha256,
        },
        "rules_sha256": rules_sha256(),
        "mechs": result.mechs,
        "mentions_file": MENTIONS_NAME,
        "mentions_sha256": sha256_text(mentions_text),
        "counts": snapshot_counts(result.rows),
    }


def write_snapshot(result: ScanResult, fleet: FleetManifest, out_dir: Path) -> dict:
    mentions_text = render_mentions(result.rows)
    manifest = build_manifest(result, fleet, mentions_text)
    # Mentions first, manifest last: a manifest that verifies names the bytes beside it.
    _atomic_write(out_dir / MENTIONS_NAME, mentions_text)
    _atomic_write(out_dir / MANIFEST_NAME, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


# ---------------------------------------------------------------------- snapshot io


ROW_FIELDS = frozenset(
    {
        "mech",
        "record_path",
        "record_id",
        "pointer",
        "pattern",
        "protein_id",
        "raw_value",
        "channel",
        "role",
        "relation",
        "annotations",
        "sibling_label",
        "sibling_taxon_id",
    }
)


def load_snapshot(directory: Path = SNAPSHOT_DIR) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load the tracked snapshot and refuse it unless its manifest names its bytes."""

    manifest_path = directory / MANIFEST_NAME
    mentions_path = directory / MENTIONS_NAME
    if not manifest_path.is_file() or not mentions_path.is_file():
        raise CrossMechError(f"no cross-Mech snapshot under {directory}; run the scan first")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw = mentions_path.read_bytes()
    errors = verify_snapshot(raw, manifest)
    if errors:
        raise CrossMechError("cross-Mech snapshot fails integrity: " + "; ".join(errors))
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    return rows, manifest


def verify_snapshot(raw: bytes, manifest: Mapping[str, Any]) -> list[str]:
    """Integrity of the tracked snapshot, independent of any sibling checkout."""

    errors: list[str] = []
    if manifest.get("kind") != SNAPSHOT_KIND:
        errors.append(f"manifest kind is not {SNAPSHOT_KIND}")
    if manifest.get("schema_version") != SNAPSHOT_SCHEMA_VERSION:
        errors.append(f"manifest schema_version is not {SNAPSHOT_SCHEMA_VERSION}")
    if manifest.get("mentions_sha256") != sha256_bytes(raw):
        errors.append("mentions bytes do not match manifest mentions_sha256")
    fleet = manifest.get("fleet_manifest") or {}
    if not COMMIT_HEX.fullmatch(str(fleet.get("commit", ""))) or not SHA256_HEX.fullmatch(
        str(fleet.get("sha256", ""))
    ):
        errors.append("fleet manifest pin must carry a full commit and sha256")
    pinned_mechs = set()
    for mech in manifest.get("mechs") or []:
        if not COMMIT_HEX.fullmatch(str(mech.get("commit", ""))):
            errors.append(f"mech {mech.get('key')!r} lacks a full pinned commit")
        pinned_mechs.add(mech.get("key"))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return errors + ["mentions file is not UTF-8"]
    if text and not text.endswith("\n"):
        errors.append("mentions file must end with a newline")
    previous: tuple[str, str, str] | None = None
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), 1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"line {number}: invalid JSON: {error.msg}")
            continue
        if not isinstance(row, dict) or set(row) != ROW_FIELDS:
            errors.append(f"line {number}: row fields differ from the snapshot schema")
            continue
        if canonical_json(row) != line:
            errors.append(f"line {number}: row is not canonical JSON")
        if row["role"] not in ROLES:
            errors.append(f"line {number}: unknown role {row['role']!r}")
        if row["mech"] not in pinned_mechs:
            errors.append(f"line {number}: mech {row['mech']!r} is not pinned in the manifest")
        key = (row["mech"], row["record_path"], row["pointer"])
        if previous is not None and key <= previous:
            errors.append(f"line {number}: rows are not strictly sorted and unique")
        previous = key
        rows.append(row)
    if manifest.get("counts") != snapshot_counts(rows):
        errors.append("manifest counts do not match the mentions")
    by_mech = Counter(row["mech"] for row in rows)
    records_by_mech = Counter(
        mech for mech, _ in {(row["mech"], row["record_path"]) for row in rows}
    )
    for mech in manifest.get("mechs") or []:
        if mech.get("mentions") != by_mech.get(mech.get("key"), 0) or mech.get(
            "records_with_proteins"
        ) != records_by_mech.get(mech.get("key"), 0):
            errors.append(f"mech {mech.get('key')!r} counts do not match its rows")
    if manifest.get("rules_sha256") != rules_sha256():
        errors.append("channel rules changed since the snapshot: rescan with `scan --apply`")
        return errors
    # Under the current rules every row's classification is a function of its own
    # pointer, so a relabelled role, channel or relation cannot verify (#967).
    for number, row in enumerate(rows, 1):
        if generalize(row["pointer"]) != row["pattern"]:
            errors.append(f"row {number}: pattern is not the generalized pointer")
            continue
        channel, role, relation = classify(row["mech"], row["pattern"])
        if (channel.key if channel else None, role, relation) != (
            row["channel"],
            row["role"],
            row["relation"],
        ):
            errors.append(f"row {number}: channel/role/relation disagree with the rules")
    return errors


# ------------------------------------------------------------------------- audit


STATUSES = (
    "QUALIFIED_ON_TRAIT",
    "LEGACY_ON_TRAIT",
    "ABSENT_FROM_TRAIT",
    "TRAIT_NOT_IN_PTM",
    "NOT_A_PTM_NAMESPACE",
)


def load_rhea_directions(
    path: Path = RHEA_DIRECTIONS, *, expected_sha256: str = RHEA_DIRECTIONS_SHA256
) -> tuple[dict[str, str], str | None]:
    """Directional Rhea ID -> master ID, only from the pinned release-141 bytes."""

    if not path.is_file():
        return {}, None
    raw = path.read_bytes()
    digest = sha256_bytes(raw)
    if digest != expected_sha256:
        raise CrossMechError(
            f"{path} sha256 {digest} is not the pinned release-141 {expected_sha256}"
        )
    lines = raw.decode("utf-8").splitlines()
    if not lines or lines[0].split("\t") != [
        "RHEA_ID_MASTER",
        "RHEA_ID_LR",
        "RHEA_ID_RL",
        "RHEA_ID_BI",
    ]:
        raise CrossMechError(f"{path} header is not the Rhea directions header")
    mapping: dict[str, str] = {}
    for line in lines[1:]:
        fields = line.split("\t")
        if len(fields) != 4:
            raise CrossMechError(f"{path}: malformed directions row {line!r}")
        master = f"RHEA:{fields[0]}"
        for value in fields:
            mapping[f"RHEA:{value}"] = master
    return mapping, digest


def normalize_annotation(curie: str, rhea_masters: Mapping[str, str]) -> str:
    """The exact trait identifier this repository would key the annotation under."""

    prefix, _, local = curie.partition(":")
    if prefix.upper() == "RHEA":
        return rhea_masters.get(f"RHEA:{local}", f"RHEA:{local}")
    if prefix == "ComplexPortal" or prefix.lower() == "complexportal":
        return f"ComplexPortal:{local}"
    return curie


IDENTIFIER_LINE = re.compile(r"^identifier:[ \t]*(['\"]?)([^'\"\s]+)\1[ \t]*$")


# User configuration must not change what is parsed: colour codes or full names would
# silently empty the index or double its paths (#963).
_GIT_OUTPUT_CONFIG = ("-c", "color.ui=never", "-c", "grep.fullName=false")


def _git_lines(traits_root: Path, args: Sequence[str], runner: Callable[..., Any]) -> str:
    completed = runner(
        ["git", *_GIT_OUTPUT_CONFIG, "-C", str(traits_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    # git grep exits 1 for "no match"; anything else non-zero is a real failure.
    if completed.returncode not in (0, 1) or (completed.returncode == 1 and completed.stderr):
        raise CrossMechError(f"git {args[0]} in {traits_root} failed: {completed.stderr.strip()}")
    return completed.stdout


def _working_identifiers(path: Path) -> list[str]:
    identifiers: list[str] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = IDENTIFIER_LINE.match(line.rstrip("\n"))
            if match:
                identifiers.append(match.group(2))
    return identifiers


def build_identifier_index(
    traits_root: Path = TRAITS_ROOT, *, runner: Callable[..., Any] = subprocess.run
) -> dict[str, list[str]]:
    """Every record ``identifier`` -> record paths relative to ``traits_root``.

    The committed tree is read with one ``git grep`` (object reads, no 2 GB working-tree
    scan), then patched with every working-tree difference: a modified or deleted
    tracked record and an untracked, non-ignored one are re-read from disk. A promotion
    rewrites ``canonical_examples``, never ``identifier``, so the patch is usually empty.
    """

    by_path: dict[str, list[str]] = defaultdict(list)
    committed = _git_lines(
        traits_root, ["grep", "-z", "-I", "-E", "^identifier:", "HEAD", "--", "."], runner
    )
    for line in committed.split("\n"):
        head, separator, text = line.partition("\0")
        if not separator:
            continue
        match = IDENTIFIER_LINE.match(text)
        if match:
            by_path[head.removeprefix("HEAD:")].append(match.group(2))
    changed = _git_lines(
        traits_root, ["diff", "--no-renames", "--name-only", "-z", "HEAD", "--", "."], runner
    )
    untracked = _git_lines(
        traits_root, ["ls-files", "-z", "--others", "--exclude-standard", "--", "."], runner
    )
    prefix = _git_lines(traits_root, ["rev-parse", "--show-prefix"], runner).strip()
    for entry in (changed + untracked).split("\0"):
        if not entry:
            continue
        # `git diff` names paths from the repository root; ls-files from the cwd.
        relative = entry.removeprefix(prefix) if prefix and entry.startswith(prefix) else entry
        by_path.pop(relative, None)
        path = traits_root / relative
        if path.is_file() and path.suffix in {".yaml", ".yml"}:
            identifiers = _working_identifiers(path)
            if identifiers:
                by_path[relative] = identifiers
    index: dict[str, list[str]] = defaultdict(list)
    for path, identifiers in by_path.items():
        for identifier in identifiers:
            index[identifier].append(path)
    return {identifier: sorted(paths) for identifier, paths in index.items()}


def load_record_examples(path: Path) -> dict[str, Any]:
    document = yaml.load(path.read_text(encoding="utf-8"), Loader=Loader)  # noqa: S506
    if not isinstance(document, Mapping):
        raise CrossMechError(f"{path} is not a YAML mapping")
    examples: dict[str, str] = {}
    for example in document.get("canonical_examples") or []:
        if not isinstance(example, Mapping):
            continue
        protein = example.get("protein_id")
        if isinstance(protein, str) and protein.strip():
            status = example.get("qualification_status") or "LEGACY_UNVERIFIED"
            examples[protein.strip()] = str(status)
    return {
        "identifier": document.get("identifier"),
        "trait_axis": document.get("trait_axis"),
        "trait_category": document.get("trait_category"),
        "examples": examples,
    }


def route_for(namespace: str, axis: str | None, category: str | None) -> str:
    if namespace in UNIPROT_ANNOTATION_NAMESPACES:
        method = "SOURCE_ANNOTATION" if namespace == "GO" else "SOURCE_MEMBERSHIP"
        return f"{method}:UniProtKB"
    if namespace in SIGNATURE_NAMESPACES:
        whole = axis in {"FUNCTION", "EVOLUTION"} or category in {
            "SEQ_FAMILY",
            "SEQ_HOMOLOGOUS_SUPERFAMILY",
        }
        return "SOURCE_MEMBERSHIP:UniProtKB" if whole else "INTERPRO_MATCH:InterPro"
    return "NONE"


def _example_status(protein_id: str, examples: Mapping[str, str]) -> str:
    accession = protein_id.removeprefix("UniProtKB:")
    status = examples.get(protein_id) or examples.get(accession)
    if status is None:
        return "ABSENT_FROM_TRAIT"
    return "QUALIFIED_ON_TRAIT" if status == "QUALIFIED" else "LEGACY_ON_TRAIT"


def audit(
    rows: Sequence[Mapping[str, Any]],
    *,
    traits_root: Path = TRAITS_ROOT,
    rhea_directions: Path = RHEA_DIRECTIONS,
    rhea_directions_sha256: str = RHEA_DIRECTIONS_SHA256,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    """One status per (protein, normalized annotation) pair a channel declares."""

    rhea_masters, rhea_digest = load_rhea_directions(
        rhea_directions, expected_sha256=rhea_directions_sha256
    )
    pairs: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        # Any channel that declares a trait annotation counts, whatever the role: a
        # causal-graph node whose xrefs name the protein and its Pfam family ties the
        # two exactly as an example list does. TARGET/SUBSTRATE/REFERENCE/CROSSWALK
        # channels declare none, so they never reach this loop.
        for annotation in row["annotations"]:
            trait_id = normalize_annotation(annotation["curie"], rhea_masters)
            pair = pairs.setdefault(
                (row["protein_id"], trait_id),
                {
                    "protein_id": row["protein_id"],
                    "trait_id": trait_id,
                    "sibling_curies": set(),
                    "mechs": set(),
                    "channels": set(),
                    "relations": set(),
                    "sibling_records": set(),
                    "qualifiers": set(),
                    "mentions": 0,
                },
            )
            pair["sibling_curies"].add(annotation["curie"])
            pair["mechs"].add(row["mech"])
            pair["channels"].add(row["channel"])
            pair["relations"].add(annotation["relation"])
            pair["sibling_records"].add(f"{row['mech']}:{row['record_path']}")
            pair["qualifiers"].add(canonical_json(annotation.get("qualifiers") or {}))
            pair["mentions"] += 1
    index = build_identifier_index(traits_root, runner=runner)
    namespaces = {identifier.split(":", 1)[0] for identifier in index if ":" in identifier}
    locations = {trait: index[trait] for _, trait in pairs if trait in index}
    duplicate_ids = sorted(trait for trait, paths in locations.items() if len(paths) > 1)
    if duplicate_ids:
        raise CrossMechError(f"trait identifiers resolve to several records: {duplicate_ids[:5]}")
    records = {
        trait: load_record_examples(traits_root / paths[0]) for trait, paths in locations.items()
    }
    out: list[dict[str, Any]] = []
    for (protein_id, trait_id), pair in sorted(pairs.items()):
        namespace = trait_id.split(":", 1)[0]
        record = records.get(trait_id)
        if record is not None:
            status = _example_status(protein_id, record["examples"])
            record_path = f"data/traits/{locations[trait_id][0]}"
            axis, category = record["trait_axis"], record["trait_category"]
        else:
            status = "TRAIT_NOT_IN_PTM" if namespace in namespaces else "NOT_A_PTM_NAMESPACE"
            record_path, axis, category = None, None, None
        out.append(
            {
                "protein_id": protein_id,
                "trait_id": trait_id,
                "status": status,
                "record_path": record_path,
                "trait_axis": axis,
                "trait_category": category,
                "route": route_for(namespace, axis, category) if record is not None else "NONE",
                "sibling_curies": sorted(pair["sibling_curies"]),
                "mechs": sorted(pair["mechs"]),
                "channels": sorted(pair["channels"]),
                "relations": sorted(pair["relations"]),
                "sibling_records": sorted(pair["sibling_records"]),
                # Every distinct qualifier set the supporting claims carry ({} = none).
                "qualifiers": [json.loads(item) for item in sorted(pair["qualifiers"])],
                "mentions": pair["mentions"],
            }
        )
    unresolved_directional = sorted(
        {
            pair["trait_id"]
            for pair in out
            if pair["trait_id"].startswith("RHEA:")
            and pair["status"] == "TRAIT_NOT_IN_PTM"
            and rhea_digest is None
        }
    )
    return {
        "pairs": out,
        "rhea_directions_sha256": rhea_digest,
        "rhea_ids_unchecked_for_direction": unresolved_directional,
        "summary": audit_summary(rows, out),
    }


def audit_summary(rows: Sequence[Mapping[str, Any]], pairs: Sequence[Mapping[str, Any]]) -> dict:
    by_status = Counter(pair["status"] for pair in pairs)
    by_category = Counter(
        (pair["trait_category"] or "-", pair["status"]) for pair in pairs if pair["record_path"]
    )
    by_mech_status: Counter[tuple[str, str]] = Counter()
    for pair in pairs:
        for mech in pair["mechs"]:
            by_mech_status[(mech, pair["status"])] += 1
    example_proteins = {row["protein_id"] for row in rows if row["role"] == "EXAMPLE"}
    annotated_proteins = {pair["protein_id"] for pair in pairs}
    on_trait = {pair["protein_id"] for pair in pairs if pair["record_path"]}
    return {
        "pairs": len(pairs),
        "pairs_by_status": dict(sorted(by_status.items())),
        "pairs_on_existing_records_by_category": {
            f"{category}|{status}": count
            for (category, status), count in sorted(by_category.items())
        },
        "pairs_by_mech_and_status": {
            f"{mech}|{status}": count for (mech, status), count in sorted(by_mech_status.items())
        },
        "example_proteins": len(example_proteins),
        "example_proteins_without_trait_annotation": len(example_proteins - annotated_proteins),
        "proteins_with_annotation_on_existing_record": len(on_trait),
        "records_targeted": len({pair["record_path"] for pair in pairs if pair["record_path"]}),
        "candidate_pairs": sum(
            1
            for pair in pairs
            if pair["status"] in {"ABSENT_FROM_TRAIT", "LEGACY_ON_TRAIT"}
            and pair["route"] != "NONE"
        ),
        # Pairs whose every supporting sibling claim calls itself a proposal (#965).
        "pairs_resting_only_on_proposed_claims": sum(
            1
            for pair in pairs
            if pair["qualifiers"]
            and all(item.get("proposed") is True for item in pair["qualifiers"])
        ),
    }


PAIR_COLUMNS = (
    "protein_id",
    "trait_id",
    "status",
    "route",
    "trait_category",
    "record_path",
    "sibling_curies",
    "mechs",
    "channels",
    "relations",
    "mentions",
    "sibling_records",
    "qualifiers",
)


def render_pairs_tsv(pairs: Iterable[Mapping[str, Any]]) -> str:
    out = io.StringIO()
    writer = csv.writer(out, delimiter="\t", lineterminator="\n")
    writer.writerow(PAIR_COLUMNS)
    for pair in pairs:
        writer.writerow(
            [
                canonical_json(pair[column])
                if column == "qualifiers"
                else ";".join(pair[column])
                if isinstance(pair[column], list)
                else ("" if pair[column] is None else pair[column])
                for column in PAIR_COLUMNS
            ]
        )
    return out.getvalue()


def render_summary_markdown(report: Mapping[str, Any], manifest: Mapping[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Cross-Mech protein examples: audit",
        "",
        f"Snapshot fleet manifest: `{manifest['fleet_manifest']['commit']}`; "
        f"rules `{manifest['rules_sha256'][:12]}`; "
        f"Rhea directions `{report['rhea_directions_sha256'] or 'ABSENT'}`.",
        "",
        "| Mech | Pinned commit | Records scanned | Records with proteins | Mentions |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for mech in manifest["mechs"]:
        lines.append(
            f"| {mech['key']} | `{mech['commit'][:11]}` | {mech['records_scanned']:,} | "
            f"{mech['records_with_proteins']:,} | {mech['mentions']:,} |"
        )
    lines += ["", "| Status | Pairs |", "| --- | ---: |"]
    for status in STATUSES:
        lines.append(f"| {status} | {summary['pairs_by_status'].get(status, 0):,} |")
    lines += [
        "",
        f"Candidate pairs (absent or legacy, with a route): {summary['candidate_pairs']:,}.",
        f"Example proteins with no trait annotation: "
        f"{summary['example_proteins_without_trait_annotation']:,} "
        f"of {summary['example_proteins']:,}.",
        "",
    ]
    if report["rhea_ids_unchecked_for_direction"]:
        lines.append(
            "Rhea IDs not normalized (directions table absent): "
            + ", ".join(report["rhea_ids_unchecked_for_direction"])
        )
    return "\n".join(lines) + "\n"


# -------------------------------------------------------------------- candidates


def candidate_rows(
    pairs: Sequence[Mapping[str, Any]],
    *,
    uniprot_release: str,
    mentions_sha256: str,
) -> list[dict[str, Any]]:
    """Funnel candidates for every absent or legacy pair that has a qualification route.

    A row says only "the sibling claims this protein carries this exact trait". It names
    the route that could prove it (an exact UniProt fact, or an exact InterPro match),
    and nothing else: sequence, organism, and the fact itself come from the release-
    pinned fetch, never from the sibling record.
    """

    if re.fullmatch(r"[0-9]{4}_[0-9]{2}", uniprot_release) is None:
        raise CrossMechError(f"--uniprot-release must look like 2026_03, got {uniprot_release!r}")
    scripts = str(Path(__file__).resolve().parent)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from ground_uniprot_examples import derive_candidate_id  # noqa: PLC0415

    rows: list[dict[str, Any]] = []
    for pair in pairs:
        if (
            pair["status"] not in {"ABSENT_FROM_TRAIT", "LEGACY_ON_TRAIT"}
            or pair["route"] == "NONE"
        ):
            continue
        method, _, evidence_source = pair["route"].partition(":")
        trait_id = pair["trait_id"]
        row: dict[str, Any] = {
            "schema_version": 1,
            "batch": CANDIDATE_BATCH,
            "candidate_status": "CANDIDATE_PROTEIN",
            "qualification_status": "CANDIDATE_PROTEIN",
            "trait_id": trait_id,
            "record_path": pair["record_path"],
            "trait_axis": pair["trait_axis"],
            "trait_category": pair["trait_category"],
            "source_namespace": trait_id.split(":", 1)[0],
            "protein_id": pair["protein_id"],
            "scope": "LOCALIZED" if method == "INTERPRO_MATCH" else "WHOLE_PROTEIN",
            "source_trait_id": trait_id,
            "mapping_method": method,
            "evidence_source": evidence_source,
            "evidence_tier": "A",
            "cross_mech_provenance": {
                "status": pair["status"],
                "sibling_curies": pair["sibling_curies"],
                "relations": pair["relations"],
                "mechs": pair["mechs"],
                "sibling_records": pair["sibling_records"],
                "snapshot_mentions_sha256": mentions_sha256,
            },
        }
        if method != "INTERPRO_MATCH":
            # The exact-accession snapshot replaces this with its own release.
            row["source_release"] = uniprot_release
            row["reasons"] = list(CANDIDATE_RESOLUTION_REASONS)
        row["candidate_id"] = derive_candidate_id(row)
        rows.append(row)
    rows.sort(key=lambda row: (row["trait_id"], row["protein_id"], row["candidate_id"]))
    if len({row["candidate_id"] for row in rows}) != len(rows):
        raise CrossMechError("internal error: duplicate candidate IDs")
    return rows


# ------------------------------------------------------------------------- check


def local_drift(
    manifest: Mapping[str, Any],
    mechs_root: Path,
    *,
    ref: str = DEFAULT_REF,
    environ: Mapping[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Which pinned Mechs have record files that changed since the snapshot."""

    env = os.environ if environ is None else environ
    report: list[dict[str, Any]] = []
    for mech in manifest["mechs"]:
        target = MechTarget(
            mech["key"],
            mech["github"],
            tuple(mech["record_globs"]),
            str(mech.get("environment_variable") or ""),
        )
        compiled = [glob_to_regex(glob) for glob in target.record_globs]
        try:
            repo = resolve_checkout(target, mechs_root, env)
            head = _git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()
            if head == mech["commit"]:
                report.append({"key": mech["key"], "state": "CURRENT", "head": head, "changed": 0})
                continue
            # --no-renames: a record moved out of the globs is a change (#964).
            diff = _git(repo, "diff", "--no-renames", "--name-only", "-z", mech["commit"], head)
        except CrossMechError as error:
            report.append({"key": mech["key"], "state": "UNAVAILABLE", "detail": str(error)})
            continue
        changed = [
            path
            for path in diff.split("\0")
            if path and any(regex.match(path) for regex in compiled)
        ]
        report.append(
            {
                "key": mech["key"],
                "state": "STALE" if changed else "MOVED_RECORDS_UNCHANGED",
                "head": head,
                "changed": len(changed),
                "examples": changed[:5],
            }
        )
    return report


def remote_drift(
    manifest: Mapping[str, Any],
    *,
    runner: Callable[..., Any] = subprocess.run,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> list[dict[str, Any]]:
    """Live default-branch heads against the pins, plus fleet membership drift."""

    report: list[dict[str, Any]] = []
    for mech in manifest["mechs"]:
        try:
            head = remote_head(mech["github"], runner=runner)
        except CrossMechError as error:
            report.append({"key": mech["key"], "state": "UNAVAILABLE", "detail": str(error)})
            continue
        state = "CURRENT" if head == mech["commit"] else "MOVED"
        report.append({"key": mech["key"], "state": state, "head": head})
    try:
        live = fetch_fleet_manifest(opener=opener, runner=runner)
    except CrossMechError as error:
        report.append({"key": "fleet-manifest", "state": "UNAVAILABLE", "detail": str(error)})
        return report
    pinned = {
        (mech["key"], mech["github"], tuple(mech["record_globs"])) for mech in manifest["mechs"]
    }
    current = {(target.key, target.github, target.record_globs) for target in live.targets}
    if live.sha256 == manifest["fleet_manifest"]["sha256"]:
        report.append({"key": "fleet-manifest", "state": "CURRENT", "head": live.commit})
    elif pinned == current:
        report.append(
            {"key": "fleet-manifest", "state": "MOVED_MEMBERSHIP_UNCHANGED", "head": live.commit}
        )
    else:
        report.append(
            {
                "key": "fleet-manifest",
                "state": "STALE",
                "head": live.commit,
                "added": sorted(f"{key} {github}" for key, github, _ in current - pinned),
                "removed": sorted(f"{key} {github}" for key, github, _ in pinned - current),
            }
        )
    return report


# --------------------------------------------------------------------------- CLI


def _print_scan_summary(manifest: Mapping[str, Any]) -> None:
    counts = manifest["counts"]
    print(
        f"fleet manifest {manifest['fleet_manifest']['commit'][:11]}; rules {manifest['rules_sha256'][:12]}"
    )
    for mech in manifest["mechs"]:
        print(
            f"  {mech['key']:20s} {mech['commit'][:11]}  records={mech['records_scanned']:>7,}  "
            f"with_proteins={mech['records_with_proteins']:>5,}  mentions={mech['mentions']:>6,}"
        )
    print(
        f"mentions={counts['mentions']:,} proteins={counts['distinct_proteins']:,} "
        f"example_proteins={counts['distinct_example_proteins']:,} "
        f"annotated_pairs={counts['distinct_annotated_protein_pairs']:,}"
    )
    print(
        "by role: " + ", ".join(f"{role}={n:,}" for role, n in counts["mentions_by_role"].items())
    )
    if counts["unclassified_patterns"]:
        print("UNCLASSIFIED patterns (add a channel rule):")
        for pattern in counts["unclassified_patterns"]:
            print(f"  {pattern}")


def cmd_scan(args: argparse.Namespace) -> int:
    refs: dict[str, str] | None = None
    if args.at_manifest:
        # Re-derive under the current rules at exactly the pinned sibling and fleet commits,
        # so a rules change shows in the diff without unrelated sibling drift.
        pinned = json.loads(Path(args.at_manifest).read_text(encoding="utf-8"))
        refs = {mech["key"]: mech["commit"] for mech in pinned["mechs"]}
        args.fleet_commit = args.fleet_commit or pinned["fleet_manifest"]["commit"]
    if args.fleet_manifest:
        text = Path(args.fleet_manifest).read_text(encoding="utf-8")
        if not args.fleet_commit:
            raise CrossMechError(
                "--fleet-manifest requires --fleet-commit (the claw commit it came from)"
            )
        fleet = parse_fleet_manifest(text, commit=args.fleet_commit)
    else:
        fleet = fetch_fleet_manifest(args.fleet_commit)
    result = scan(fleet, Path(args.mechs_root), ref=args.ref, refs=refs, fetch=args.fetch)
    mentions_text = render_mentions(result.rows)
    manifest = build_manifest(result, fleet, mentions_text)
    _print_scan_summary(manifest)
    if not args.apply:
        print("dry run: pass --apply to replace data/cross_mech/")
        return 0
    write_snapshot(result, fleet, Path(args.out))
    print(f"WROTE {Path(args.out) / MENTIONS_NAME} and {MANIFEST_NAME}")
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    rows, manifest = load_snapshot(Path(args.snapshot))
    report = audit(rows, traits_root=Path(args.traits), rhea_directions=Path(args.rhea_directions))
    out = Path(args.out)
    _atomic_write(out / "pairs.tsv", render_pairs_tsv(report["pairs"]))
    _atomic_write(
        out / "pairs.jsonl", "".join(canonical_json(pair) + "\n" for pair in report["pairs"])
    )
    _atomic_write(out / "summary.md", render_summary_markdown(report, manifest))
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"WROTE {out}/pairs.tsv, pairs.jsonl, summary.md")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    directory = Path(args.snapshot)
    if not (directory / MANIFEST_NAME).is_file() or not (directory / MENTIONS_NAME).is_file():
        raise CrossMechError(f"no cross-Mech snapshot under {directory}; run the scan first")
    try:
        manifest = json.loads((directory / MANIFEST_NAME).read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CrossMechError(f"{directory / MANIFEST_NAME} is not JSON: {error}") from error
    errors = verify_snapshot((directory / MENTIONS_NAME).read_bytes(), manifest)
    for error in errors:
        print(f"ERROR: {error}")
    unclassified = manifest.get("counts", {}).get("unclassified_patterns") or []
    for pattern in unclassified:
        print(f"NOTICE: unclassified sibling protein path {pattern} (add a channel rule)")
    drift: list[dict[str, Any]] = []
    if args.local:
        drift.extend(local_drift(manifest, Path(args.mechs_root), ref=args.ref))
    if args.remote:
        drift.extend(remote_drift(manifest))
    stale = False
    for item in drift:
        state = item["state"]
        detail = {key: value for key, value in item.items() if key not in {"key", "state"}}
        print(f"NOTICE: {item['key']}: {state} {json.dumps(detail, sort_keys=True)}")
        stale = stale or state in {"STALE", "MOVED"}
    if errors:
        return 1
    if stale and args.fail_on_drift:
        return 1
    print(
        "OK: snapshot integrity verified"
        + ("" if drift else " (drift not checked; pass --local or --remote)")
    )
    return 0


def cmd_candidates(args: argparse.Namespace) -> int:
    rows, manifest = load_snapshot(Path(args.snapshot))
    if args.pairs:
        pairs = [
            json.loads(line) for line in Path(args.pairs).read_text(encoding="utf-8").splitlines()
        ]
    else:
        pairs = audit(
            rows, traits_root=Path(args.traits), rhea_directions=Path(args.rhea_directions)
        )["pairs"]
    candidates = candidate_rows(
        pairs, uniprot_release=args.uniprot_release, mentions_sha256=manifest["mentions_sha256"]
    )
    by_route = Counter(f"{row['mapping_method']}:{row['source_namespace']}" for row in candidates)
    print(
        f"{len(candidates):,} candidates over {len({row['record_path'] for row in candidates}):,} "
        f"records and {len({row['protein_id'] for row in candidates}):,} proteins"
    )
    for route, count in sorted(by_route.items()):
        print(f"  {route}: {count:,}")
    if not args.apply:
        print(f"dry run: pass --apply to write {args.out}")
        return 0
    _atomic_write(Path(args.out), "".join(canonical_json(row) + "\n" for row in candidates))
    print(f"WROTE {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan_parser = sub.add_parser("scan", help="read sibling Mechs into the snapshot")
    scan_parser.add_argument("--mechs-root", default=str(REPO_ROOT.parent))
    scan_parser.add_argument("--ref", default=DEFAULT_REF)
    scan_parser.add_argument("--fetch", action="store_true", help="git fetch each sibling first")
    scan_parser.add_argument(
        "--fleet-commit", help="claw commit of the fleet manifest (default: live)"
    )
    scan_parser.add_argument("--fleet-manifest", help="local fleet.yaml bytes for --fleet-commit")
    scan_parser.add_argument(
        "--at-manifest", help="rescan at the sibling and fleet commits pinned in this manifest"
    )
    scan_parser.add_argument("--out", default=str(SNAPSHOT_DIR))
    scan_parser.add_argument("--apply", action="store_true")
    scan_parser.set_defaults(func=cmd_scan)

    audit_parser = sub.add_parser("audit", help="resolve the snapshot against data/traits")
    audit_parser.add_argument("--snapshot", default=str(SNAPSHOT_DIR))
    audit_parser.add_argument("--traits", default=str(TRAITS_ROOT))
    audit_parser.add_argument("--rhea-directions", default=str(RHEA_DIRECTIONS))
    audit_parser.add_argument("--out", default=str(REPORT_DIR))
    audit_parser.set_defaults(func=cmd_audit)

    candidates_parser = sub.add_parser("candidates", help="emit grounding-funnel candidates")
    candidates_parser.add_argument("--snapshot", default=str(SNAPSHOT_DIR))
    candidates_parser.add_argument("--traits", default=str(TRAITS_ROOT))
    candidates_parser.add_argument("--rhea-directions", default=str(RHEA_DIRECTIONS))
    candidates_parser.add_argument(
        "--pairs", help="reuse an audit pairs.jsonl instead of re-auditing"
    )
    candidates_parser.add_argument("--uniprot-release", required=True)
    candidates_parser.add_argument("--out", default=str(CANDIDATE_QUEUE))
    candidates_parser.add_argument("--apply", action="store_true")
    candidates_parser.set_defaults(func=cmd_candidates)

    check_parser = sub.add_parser("check", help="verify the snapshot; optionally report drift")
    check_parser.add_argument("--snapshot", default=str(SNAPSHOT_DIR))
    check_parser.add_argument("--local", action="store_true", help="compare sibling checkouts")
    check_parser.add_argument("--remote", action="store_true", help="compare live default branches")
    check_parser.add_argument("--mechs-root", default=str(REPO_ROOT.parent))
    check_parser.add_argument("--ref", default=DEFAULT_REF)
    check_parser.add_argument("--fail-on-drift", action="store_true")
    check_parser.set_defaults(func=cmd_check)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except CrossMechError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
