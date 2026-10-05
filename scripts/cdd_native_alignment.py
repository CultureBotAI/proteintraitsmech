"""Read CDD viewer hierarchy and source-numbered hypertext alignment snapshots.

Pure parsing helpers: no fetch, file writes, qualification, or inferred coordinates.
Inputs are immutable bytes; their hashes identify captures, NOT acquisition receipts
or CDD releases. A production provider contract is still required before grounding.

Supported formats are cddsrv.cgi?uid=cdNNNNN&json=svg and the full Hypertext
alignment in the viewer's #seqalign div. Compact displays (omitted residues),
all-gap chunks, consensus/feature rows, and unfamiliar markup fail closed. This
does not parse mFASTA, run a sequence search, or infer positions from a child model.

CDD documents lowercase as unaligned residues and dashes as alignment gaps:
https://www.ncbi.nlm.nih.gov/Structure/cdd/cdd_help.shtml (alignment formats).
Multiple rows can represent different domains of the same protein. Preserve row
order across blocks, never join by accession. Counts describe the displayed
alignment only: even an all-row seed alignment is not a census of all carriers.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit

from validate_uniprot_grounding import UNIPROT_RE, validate_protein_reference


class CDDParseError(ValueError):
    """Unsupported, incomplete, inconsistent, or ambiguous source display."""


CD = re.compile(r"cd[0-9]{5}")
RESIDUES = re.compile(r"[ACDEFGHIKLMNPQRSTVWYUOBZJXacdefghiklmnpqrstvwyuobzjx-]+")
DISPLAY = re.compile(r"(\S+)\s+([0-9]+)\s+(\S+)\s+([0-9]+)\s+(.+)")


def _capture(raw: bytes) -> tuple[str, str]:
    if not isinstance(raw, bytes) or not raw:
        raise CDDParseError("nonempty immutable source bytes required")
    try:
        return raw.decode("utf-8"), hashlib.sha256(raw).hexdigest()
    except UnicodeDecodeError as exc:
        raise CDDParseError("source is not UTF-8") from exc


def _json(text: str) -> dict:
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise CDDParseError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise CDDParseError(f"invalid JSON constant: {value}")

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, RecursionError) as exc:
        raise CDDParseError(f"invalid source JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CDDParseError("source JSON must be an object")
    return value


def _accession(value: object) -> str:
    if not isinstance(value, str) or not CD.fullmatch(value):
        raise CDDParseError("expected an exact curated CDD accession")
    return value


def _positive(value: object, name: str) -> int:
    if type(value) is not int or value < 1:
        raise CDDParseError(f"{name} must be a positive integer")
    return value


@dataclass(frozen=True)
class CDDNode:
    accession: str
    pssmid: int
    name: str
    parent: str | None
    path: tuple[str, ...]


@dataclass(frozen=True)
class CDDHierarchy:
    source_sha256: str
    requested_accession: str
    root_accession: str
    nodes: tuple[CDDNode, ...]


def parse_hierarchy(raw: bytes, *, requested_accession: str) -> CDDHierarchy:
    """Use nested children for direct parent edges, never the root as a shortcut."""
    requested_accession = _accession(requested_accession)
    text, digest = _capture(raw)
    value = _json(text)
    if value.get("hasError") is not False:
        raise CDDParseError("CDD publisher error or missing error status")
    root = _accession(value.get("rootAccession"))
    pending = [(value.get("hierarchy"), ())]
    seen, pssmids, selected, result = set(), set(), [], []
    while pending:
        node, ancestors = pending.pop()
        if not isinstance(node, dict):
            raise CDDParseError("hierarchy node must be an object")
        acc = _accession(node.get("accession"))
        if acc in seen:
            raise CDDParseError("duplicate accession or cyclic hierarchy")
        seen.add(acc)
        pssmid = _positive(node.get("pssmid"), "pssmid")
        if pssmid in pssmids:
            raise CDDParseError("duplicate PSSM identifier")
        pssmids.add(pssmid)
        if not ancestors and acc != root:
            raise CDDParseError("hierarchy root mismatch")
        name = node.get("name")
        if not isinstance(name, str) or not name.strip():
            raise CDDParseError("missing node name")
        if type(node.get("isc")) is not bool:
            raise CDDParseError("missing or invalid selected-model flag")
        if node["isc"]:
            selected.append(acc)
        if node.get("collapsed", False) is not False:
            raise CDDParseError("collapsed or invalid hierarchy node")
        path = (*ancestors, acc)
        result.append(CDDNode(acc, pssmid, name, ancestors[-1] if ancestors else None, path))
        children = node.get("children", [])
        if not isinstance(children, list):
            raise CDDParseError("children must be a list")
        pending.extend((child, path) for child in reversed(children))
    if selected != [requested_accession]:
        raise CDDParseError("selected model does not match the requested accession")
    return CDDHierarchy(digest, requested_accession, root, tuple(result))


@dataclass(frozen=True)
class AlignmentChunk:
    start: int
    end: int
    display_sequence: str

    @property
    def sequence(self) -> str:
        return self.display_sequence.replace("-", "").upper()


@dataclass(frozen=True)
class AlignmentRow:
    row_index: int  # zero-based position in the source display, not a protein key
    native_accession: str
    protein_link: str
    taxon_id: str
    chunks: tuple[AlignmentChunk, ...]

    @property
    def start(self) -> int:
        return self.chunks[0].start

    @property
    def end(self) -> int:
        return self.chunks[-1].end

    @property
    def sequence(self) -> str:
        return "".join(chunk.sequence for chunk in self.chunks)


@dataclass(frozen=True)
class CDDAlignment:
    source_sha256: str
    accession: str
    pssmid: int
    total_seq_rows: int
    total_sequences: int
    max_aln_seq: int
    rows: tuple[AlignmentRow, ...]


def _attributes(attrs: list[tuple[str, str | None]]) -> dict:
    result = dict(attrs)
    if len(result) != len(attrs):
        raise CDDParseError("duplicate HTML attribute")
    return result


class _Viewer(HTMLParser):
    """Extract only script text and complete pre blocks inside #seqalign."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts, self.blocks = [], []
        self.script = None
        self.block = None
        self.depth = self.alignments = 0

    def handle_starttag(self, tag, attrs):
        # The publisher's surrounding form/layout can contain duplicate cosmetic
        # attributes. Only alignment markup and the selector that enters it are
        # evidence inputs; reject duplicates there, not in unrelated page chrome.
        attrs = (_attributes(attrs) if self.depth or ("id", "seqalign") in attrs
                 else dict(attrs))
        if tag == "script":
            if self.script is not None or self.depth:
                raise CDDParseError("unexpected script in alignment")
            self.script = []
        if attrs.get("id") == "seqalign":
            if tag != "div" or self.alignments:
                raise CDDParseError("duplicate or invalid alignment container")
            self.alignments += 1
            self.depth = 1
        elif tag == "div" and self.depth:
            self.depth += 1
        if tag == "pre" and self.depth:
            if self.block is not None:
                raise CDDParseError("nested alignment block")
            self.block = []
        elif self.block is not None:
            self.block.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if self.depth:
            raise CDDParseError("unsupported self-closing alignment markup")

    def handle_endtag(self, tag):
        if tag == "script" and self.script is not None:
            self.scripts.append("".join(self.script))
            self.script = None
        if tag == "pre" and self.depth:
            if self.block is None:
                raise CDDParseError("unexpected alignment block close")
            self.blocks.append("".join(self.block))
            self.block = None
        elif self.block is not None:
            self.block.append(f"</{tag}>")
        if tag == "div" and self.depth:
            if self.block is not None:
                raise CDDParseError("unclosed alignment block")
            self.depth -= 1

    def handle_data(self, data):
        if self.script is not None:
            self.script.append(data)
        if self.block is not None:
            self.block.append(data)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")

    def handle_comment(self, data):
        if self.depth:
            raise CDDParseError("unsupported alignment comment")


class _DisplayLine(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text, self.anchors, self.stack = [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = _attributes(attrs)
        if tag not in {"a", "span"} or self.stack:
            raise CDDParseError("unsupported or nested display markup")
        self.stack.append((tag, attrs, len(self.text)))

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1][0] != tag:
            raise CDDParseError("unbalanced display markup")
        _, attrs, start = self.stack.pop()
        if tag == "a":
            self.anchors.append((attrs.get("href"), "".join(self.text[start:])))

    def handle_data(self, data):
        self.text.append(data)

    def handle_comment(self, data):
        raise CDDParseError("unsupported display comment")

    def handle_startendtag(self, tag, attrs):
        raise CDDParseError("unsupported self-closing display markup")


def _display_line(raw: str) -> tuple[str, str, str, AlignmentChunk]:
    parser = _DisplayLine()
    parser.feed(raw)
    parser.close()
    match = DISPLAY.fullmatch("".join(parser.text).strip())
    if parser.stack or not match or len(parser.anchors) != 2:
        raise CDDParseError("incomplete or unsupported source display row")
    acc, start, seq, end, label = match.groups()
    (protein_link, linked_acc), (taxon_link, linked_label) = parser.anchors
    if linked_acc != acc or linked_label != label or not protein_link or not taxon_link:
        raise CDDParseError("source identity/link mismatch")
    protein = urlsplit(protein_link)
    taxon = urlsplit(taxon_link)
    if (protein.scheme or protein.netloc or protein.fragment
            or not re.fullmatch(r"/protein/[A-Za-z0-9_.-]+", protein.path)
            or parse_qs(protein.query, keep_blank_values=True) != {"report": ["GenPept"]}):
        raise CDDParseError("unsupported source protein link")
    taxon_query = parse_qs(taxon.query, keep_blank_values=True)
    if (taxon.scheme or taxon.netloc or taxon.fragment
            or taxon.path != "/Taxonomy/Browser/wwwtax.cgi"
            or set(taxon_query) != {"id"} or len(taxon_query["id"]) != 1
            or not re.fullmatch(r"[1-9][0-9]*", taxon_query["id"][0])):
        raise CDDParseError("unsupported source taxonomy link")
    chunk = AlignmentChunk(int(start), int(end), seq)
    if (not RESIDUES.fullmatch(seq) or chunk.start < 1 or chunk.end < chunk.start
            or len(chunk.sequence) != chunk.end - chunk.start + 1):
        raise CDDParseError("source bounds/sequence mismatch or compact display")
    return acc, protein_link, "NCBITaxon:" + taxon_query["id"][0], chunk


def parse_alignment(raw: bytes, *, requested_accession: str) -> CDDAlignment:
    """Keep native numbering and repeated rows; never imply exhaustive coverage."""
    requested_accession = _accession(requested_accession)
    text, digest = _capture(raw)
    viewer = _Viewer()
    viewer.feed(text)
    viewer.close()
    if (viewer.depth or viewer.block is not None or viewer.script is not None
            or viewer.alignments != 1 or not viewer.blocks):
        raise CDDParseError("missing or unclosed alignment display")
    declarations = re.findall(r"\bvar\s+CDD\s*=\s*(\{[^;]*\})\s*;", "\n".join(viewer.scripts))
    if len(declarations) != 1:
        raise CDDParseError("missing or duplicate CDD viewer metadata")
    meta = _json(declarations[0])
    if meta.get("accession") != requested_accession:
        raise CDDParseError("alignment model mismatch")
    if (meta.get("isCuratedCD") is not True or meta.get("isCluster") is not False
            or meta.get("hasQuery") is not False):
        raise CDDParseError("only curated, non-query model alignments are supported")
    pssmid = _positive(meta.get("pssmId"), "pssmId")
    total_rows = _positive(meta.get("totalSeqRows"), "totalSeqRows")
    total_sequences = _positive(meta.get("totalSequences"), "totalSequences")
    max_aln = _positive(meta.get("maxAlnSeq"), "maxAlnSeq")
    blocks = []
    for block in viewer.blocks:
        rows = [_display_line(line) for line in block.splitlines() if line.strip()]
        if not rows or len({len(row[3].display_sequence) for row in rows}) != 1:
            raise CDDParseError("empty block or inconsistent alignment column widths")
        if blocks and len(rows) != len(blocks[0]):
            raise CDDParseError("missing rows between alignment blocks")
        if len(rows) > total_rows or len(rows) > max_aln:
            raise CDDParseError("display rows exceed viewer metadata")
        blocks.append(rows)
    result = []
    for ordinal, first in enumerate(blocks[0]):
        chunks = []
        for block in blocks:
            *identity, chunk = block[ordinal]
            if tuple(identity) != first[:3]:
                raise CDDParseError("row identity/order changed between blocks")
            if chunks and chunk.start != chunks[-1].end + 1:
                raise CDDParseError("noncontiguous or reordered source chunks")
            chunks.append(chunk)
        result.append(AlignmentRow(ordinal, *first[:3], tuple(chunks)))
    return CDDAlignment(digest, requested_accession, pssmid, total_rows,
                        total_sequences, max_aln, tuple(result))


def verify_uniprot_slice(row: AlignmentRow, reference: dict) -> None:
    """Check a source-printed UniProt row against one exact local reference.

    This proves only identity/taxon/slice agreement, not receipt provenance or
    eligibility for promotion. PDB, RefSeq, and GI-only rows require a separate
    mapping route; sequence agreement alone must not relabel those frames.
    """
    pid = "UniProtKB:" + row.native_accession
    if not UNIPROT_RE.fullmatch(pid):
        raise CDDParseError("native row is not explicitly a UniProt accession; mapping required")
    findings = validate_protein_reference(reference, path=Path("<memory>"), line=1)
    if findings:
        raise CDDParseError("invalid ProteinReference: " + ", ".join(f.code for f in findings))
    if reference["protein_id"] != pid or reference["taxon_id"] != row.taxon_id:
        raise CDDParseError("exact accession/isoform or taxon mismatch")
    if row.end > reference["sequence_length"]:
        raise CDDParseError("source coordinates exceed reference sequence")
    if reference["sequence"][row.start - 1:row.end] != row.sequence:
        raise CDDParseError("source slice mismatch; no alignment or coordinate shift allowed")
