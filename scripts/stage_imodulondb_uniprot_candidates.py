#!/usr/bin/env python3
"""Join iModulonDB component genes to local ProteinTraitsMech records.

This command consumes normalized iModulonDB gene rows: the row shape emitted by
``kg_microbe_sources.imodulondb.ImodulonGene`` plus the dataset-local
``imodulon`` component number that identified the source endpoint. It never
writes trait YAML. Matching rows become review candidates only when they name an
explicit UniProt accession that is present in the local ProteinReference
registry and already appears as a canonical example on one or more trait
records.

iModulon membership is computational transcriptomics context. A candidate says
"this reviewed UniProt accession appears in component K" and still needs a
curator to decide which exact trait claim, if any, the expression module
supports.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAITS = REPO_ROOT / "data" / "traits"
DEFAULT_PROTEIN_REGISTRY = REPO_ROOT / "data" / "grounding" / "protein_registry.jsonl"
DEFAULT_OUT = REPO_ROOT / "reports" / "imodulondb"

UNIPROT_ID = re.compile(
    r"^UniProtKB:(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|"
    r"[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})$"
)

CANDIDATE_COLUMNS = (
    "candidate_id",
    "organism",
    "dataset",
    "imodulon",
    "gene_id",
    "gene_name",
    "gene_product",
    "weight",
    "all_regulators",
    "cog",
    "protein_id",
    "protein_label",
    "taxon_id",
    "taxon_label",
    "record_path",
    "trait_id",
    "trait_label",
)

BLOCKED_COLUMNS = (
    "reason",
    "detail",
    "organism",
    "dataset",
    "imodulon",
    "gene_id",
    "gene_name",
    "gene_product",
    "uniprot_id",
)

EVIDENCE_GUARDRAIL = (
    "iModulonDB membership is computational transcriptomics context; review the "
    "source component before using it as ProteinExample evidence."
)


class ImodulonStageError(RuntimeError):
    """iModulonDB candidates cannot be staged safely."""


@dataclass(frozen=True)
class ImodulonGeneRow:
    organism: str
    dataset: str
    imodulon: int
    gene_id: str
    gene_locus: str | None
    gene_name: str | None
    gene_product: str | None
    weight: float
    in_imodulon: bool
    cog: str | None
    all_regulators: str | None
    uniprot_id: str | None
    source_path: str
    source_line: int

    @property
    def imodulon_key(self) -> str:
        return f"{self.organism}/{self.dataset}/{self.imodulon}"

    @property
    def gene_key(self) -> str:
        return f"{self.organism}/{self.dataset}/{self.gene_id}"


@dataclass(frozen=True)
class ProteinReference:
    protein_id: str
    protein_label: str
    taxon_id: str
    taxon_label: str


@dataclass(frozen=True)
class RecordHit:
    trait_id: str
    trait_label: str
    record_path: str


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    gene: ImodulonGeneRow
    protein: ProteinReference
    record: RecordHit

    @property
    def sort_key(self) -> tuple[str, str, int, float, str, str, str]:
        return (
            self.gene.organism,
            self.gene.dataset,
            self.gene.imodulon,
            -abs(self.gene.weight),
            self.gene.gene_id,
            self.protein.protein_id,
            self.record.record_path,
        )


@dataclass(frozen=True)
class Blocked:
    gene: ImodulonGeneRow
    reason: str
    detail: str

    @property
    def sort_key(self) -> tuple[str, str, int, str, str]:
        return (
            self.gene.organism,
            self.gene.dataset,
            self.gene.imodulon,
            self.gene.gene_id,
            self.reason,
        )


@dataclass(frozen=True)
class StageResult:
    input_rows: int
    candidates: tuple[Candidate, ...]
    blocked: tuple[Blocked, ...]
    matched_proteins: int
    matched_records: int


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _text(value: Any, *, field: str, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ImodulonStageError(f"{context}: {field} must be a non-empty string")
    return value.strip()


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return str(value)
    value = value.strip()
    return value or None


def _int(value: Any, *, field: str, context: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ImodulonStageError(f"{context}: {field} must be an integer")
    return value


def _number(value: Any, *, field: str, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ImodulonStageError(f"{context}: {field} must be a number")
    return float(value)


def _bool(value: Any, *, field: str, context: str) -> bool:
    if not isinstance(value, bool):
        raise ImodulonStageError(f"{context}: {field} must be a boolean")
    return value


def _imodulon_value(row: Mapping[str, Any], *, context: str) -> int:
    for key in ("imodulon", "imodulon_id", "k"):
        if key in row:
            return _int(row[key], field=key, context=context)
    raise ImodulonStageError(f"{context}: missing dataset-local imodulon integer")


def _protein_id(value: str | None) -> tuple[str | None, str | None]:
    if value is None:
        return None, "missing UniProt accession"
    protein_id = value if value.startswith("UniProtKB:") else f"UniProtKB:{value}"
    if UNIPROT_ID.fullmatch(protein_id) is None:
        return None, f"invalid UniProt accession {value!r}"
    return protein_id, None


def _read_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    if not path.is_file():
        raise ImodulonStageError(f"JSONL input does not exist: {path}")
    try:
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ImodulonStageError(
                        f"{path}:{line_number}: invalid JSON: {exc}"
                    ) from exc
                if not isinstance(row, dict):
                    raise ImodulonStageError(
                        f"{path}:{line_number}: expected a JSON object"
                    )
                yield line_number, row
    except UnicodeDecodeError as exc:
        raise ImodulonStageError(f"{path}: not valid UTF-8: {exc}") from exc


def load_imodulondb_genes(paths: Sequence[Path]) -> tuple[ImodulonGeneRow, ...]:
    rows: list[ImodulonGeneRow] = []
    for path in paths:
        for line_number, row in _read_jsonl(path):
            context = f"{path}:{line_number}"
            rows.append(
                ImodulonGeneRow(
                    organism=_text(row.get("organism"), field="organism", context=context),
                    dataset=_text(row.get("dataset"), field="dataset", context=context),
                    imodulon=_imodulon_value(row, context=context),
                    gene_id=_text(row.get("gene_id"), field="gene_id", context=context),
                    gene_locus=_optional_text(row.get("gene_locus")),
                    gene_name=_optional_text(row.get("gene_name")),
                    gene_product=_optional_text(row.get("gene_product")),
                    weight=_number(row.get("weight"), field="weight", context=context),
                    in_imodulon=_bool(
                        row.get("in_imodulon"), field="in_imodulon", context=context
                    ),
                    cog=_optional_text(row.get("cog")),
                    all_regulators=_optional_text(row.get("all_regulators")),
                    uniprot_id=_optional_text(row.get("uniprot_id")),
                    source_path=path.as_posix(),
                    source_line=line_number,
                )
            )
    return tuple(rows)


def load_protein_registry(path: Path) -> dict[str, ProteinReference]:
    references: dict[str, ProteinReference] = {}
    for line_number, row in _read_jsonl(path):
        context = f"{path}:{line_number}"
        protein_id = _text(row.get("protein_id"), field="protein_id", context=context)
        if UNIPROT_ID.fullmatch(protein_id) is None:
            raise ImodulonStageError(f"{context}: invalid protein_id {protein_id!r}")
        if protein_id in references:
            raise ImodulonStageError(f"{context}: duplicate ProteinReference {protein_id}")
        references[protein_id] = ProteinReference(
            protein_id=protein_id,
            protein_label=_text(
                row.get("protein_label"), field="protein_label", context=context
            ),
            taxon_id=_text(row.get("taxon_id"), field="taxon_id", context=context),
            taxon_label=_text(row.get("taxon_label"), field="taxon_label", context=context),
        )
    return references


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().relative_to(root.resolve()).as_posix()


def load_record_examples(traits: Path) -> dict[str, tuple[RecordHit, ...]]:
    by_protein: dict[str, list[RecordHit]] = defaultdict(list)
    for path in sorted(traits.rglob("*.yaml")):
        try:
            parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ImodulonStageError(f"{path}: invalid YAML: {exc}") from exc
        if not isinstance(parsed, dict):
            continue
        trait_id = parsed.get("identifier")
        label = parsed.get("label")
        if not isinstance(trait_id, str) or not isinstance(label, str):
            continue
        hit = RecordHit(
            trait_id=trait_id,
            trait_label=label,
            record_path=_display_path(path, traits),
        )
        examples = parsed.get("canonical_examples") or []
        if not isinstance(examples, list):
            continue
        for example in examples:
            if not isinstance(example, dict):
                continue
            protein_id = example.get("protein_id")
            if isinstance(protein_id, str):
                by_protein[protein_id].append(hit)
    return {
        protein_id: tuple(sorted(hits, key=lambda hit: hit.record_path))
        for protein_id, hits in sorted(by_protein.items())
    }


def _candidate_id(gene: ImodulonGeneRow, protein_id: str, record: RecordHit) -> str:
    digest = hashlib.sha256(
        _canonical_json(
            {
                "dataset": gene.dataset,
                "gene_id": gene.gene_id,
                "imodulon": gene.imodulon,
                "organism": gene.organism,
                "protein_id": protein_id,
                "record_path": record.record_path,
                "trait_id": record.trait_id,
            }
        ).encode("utf-8")
    ).hexdigest()
    return f"imodulondb-{digest}"


def stage(
    *,
    genes: Sequence[ImodulonGeneRow],
    references: Mapping[str, ProteinReference],
    record_examples: Mapping[str, Sequence[RecordHit]],
) -> StageResult:
    candidates: dict[str, Candidate] = {}
    blocked: list[Blocked] = []

    for gene in genes:
        protein_id, protein_error = _protein_id(gene.uniprot_id)
        if not gene.in_imodulon:
            blocked.append(Blocked(gene, "OUTSIDE_IMODULON", "row is below threshold"))
            continue
        if protein_id is None:
            blocked.append(Blocked(gene, "NO_UNIPROT", protein_error or ""))
            continue
        protein = references.get(protein_id)
        if protein is None:
            blocked.append(Blocked(gene, "NO_PROTEIN_REFERENCE", protein_id))
            continue
        records = record_examples.get(protein_id, ())
        if not records:
            blocked.append(Blocked(gene, "NO_TRAIT_RECORD", protein_id))
            continue
        for record in records:
            candidate = Candidate(
                candidate_id=_candidate_id(gene, protein_id, record),
                gene=gene,
                protein=protein,
                record=record,
            )
            if candidate.candidate_id in candidates:
                raise ImodulonStageError(
                    "duplicate iModulonDB candidate key for "
                    f"{gene.imodulon_key}/{gene.gene_id} on {record.record_path}"
                )
            candidates[candidate.candidate_id] = candidate

    ordered_candidates = tuple(sorted(candidates.values(), key=lambda row: row.sort_key))
    ordered_blocked = tuple(sorted(blocked, key=lambda row: row.sort_key))
    return StageResult(
        input_rows=len(genes),
        candidates=ordered_candidates,
        blocked=ordered_blocked,
        matched_proteins=len({candidate.protein.protein_id for candidate in candidates.values()}),
        matched_records=len({candidate.record.record_path for candidate in candidates.values()}),
    )


def _candidate_row(candidate: Candidate) -> dict[str, Any]:
    return {
        "all_regulators": candidate.gene.all_regulators,
        "candidate_id": candidate.candidate_id,
        "cog": candidate.gene.cog,
        "dataset": candidate.gene.dataset,
        "evidence_guardrail": EVIDENCE_GUARDRAIL,
        "gene_id": candidate.gene.gene_id,
        "gene_key": candidate.gene.gene_key,
        "gene_locus": candidate.gene.gene_locus,
        "gene_name": candidate.gene.gene_name,
        "gene_product": candidate.gene.gene_product,
        "imodulon": candidate.gene.imodulon,
        "imodulon_key": candidate.gene.imodulon_key,
        "in_imodulon": candidate.gene.in_imodulon,
        "organism": candidate.gene.organism,
        "protein_id": candidate.protein.protein_id,
        "protein_label": candidate.protein.protein_label,
        "record_path": candidate.record.record_path,
        "review_status": "NEEDS_REVIEW",
        "source_line": candidate.gene.source_line,
        "source_path": candidate.gene.source_path,
        "source_repository": "iModulonDB",
        "taxon_id": candidate.protein.taxon_id,
        "taxon_label": candidate.protein.taxon_label,
        "trait_id": candidate.record.trait_id,
        "trait_label": candidate.record.trait_label,
        "weight": candidate.gene.weight,
    }


def _write_outputs(result: StageResult, out: Path) -> None:
    _atomic_text(
        out / "candidates.jsonl",
        "".join(
            f"{_canonical_json(_candidate_row(candidate))}\n"
            for candidate in result.candidates
        ),
    )
    _atomic_text(out / "candidates.tsv", _candidates_tsv(result.candidates))
    _atomic_text(out / "blocked.tsv", _blocked_tsv(result.blocked))
    _atomic_text(out / "summary.md", _summary_markdown(result))


def _blocked_tsv(blocked: Sequence[Blocked]) -> str:
    rows = []
    for row in blocked:
        rows.append(
            {
                "reason": row.reason,
                "detail": row.detail,
                "organism": row.gene.organism,
                "dataset": row.gene.dataset,
                "imodulon": row.gene.imodulon,
                "gene_id": row.gene.gene_id,
                "gene_name": row.gene.gene_name or "",
                "gene_product": row.gene.gene_product or "",
                "uniprot_id": row.gene.uniprot_id or "",
            }
        )
    return _tsv(BLOCKED_COLUMNS, rows)


def _candidates_tsv(candidates: Sequence[Candidate]) -> str:
    rows = []
    for candidate in candidates:
        row = _candidate_row(candidate)
        rows.append(
            {
                column: row[column] if row[column] is not None else ""
                for column in CANDIDATE_COLUMNS
            }
        )
    return _tsv(CANDIDATE_COLUMNS, rows)


def _tsv(columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> str:
    class _Echo:
        def write(self, value: str) -> str:
            return value

    writer = csv.DictWriter(
        _Echo(), fieldnames=columns, delimiter="\t", lineterminator="\n"
    )
    return writer.writeheader() + "".join(writer.writerow(row) for row in rows)


def _summary_markdown(result: StageResult) -> str:
    blocked = Counter(row.reason for row in result.blocked)
    lines = [
        "# iModulonDB ProteinTraits candidates",
        "",
        f"- Source rows: {result.input_rows}",
        f"- Review candidates: {len(result.candidates)}",
        f"- Blocked rows: {len(result.blocked)}",
        f"- Matched UniProt accessions: {result.matched_proteins}",
        f"- Matched trait records: {result.matched_records}",
        f"- Guardrail: {EVIDENCE_GUARDRAIL}",
        "",
        "## Blocked Rows",
        "",
        "| reason | rows |",
        "|---|---:|",
    ]
    if blocked:
        lines.extend(f"| {reason} | {count} |" for reason, count in sorted(blocked.items()))
    else:
        lines.append("| None | 0 |")

    lines.extend(
        [
            "",
            "## Review Candidates",
            "",
            "| iModulon | gene | UniProt | record | weight |",
            "|---|---|---|---|---:|",
        ]
    )
    if result.candidates:
        for candidate in result.candidates[:25]:
            lines.append(
                "| "
                f"{_md(candidate.gene.imodulon_key)} | "
                f"{_md(candidate.gene.gene_name or candidate.gene.gene_id)} | "
                f"{_md(candidate.protein.protein_id)} | "
                f"{_md(candidate.record.record_path)} | "
                f"{candidate.gene.weight:.6g} |"
            )
    else:
        lines.append("| None | | | | |")
    lines.append("")
    return "\n".join(lines)


def _md(value: object) -> str:
    return str(value).replace("\n", " ").replace("|", r"\|")


def _validate_output(out: Path) -> None:
    resolved = out.resolve()
    data_traits = (REPO_ROOT / "data" / "traits").resolve()
    try:
        resolved.relative_to(data_traits)
    except ValueError:
        return
    raise ImodulonStageError("--out must not write under data/traits")


def _atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _run(args: argparse.Namespace) -> int:
    result = stage(
        genes=load_imodulondb_genes(args.genes),
        references=load_protein_registry(args.protein_registry),
        record_examples=load_record_examples(args.traits),
    )
    print(
        "staged "
        f"{len(result.candidates):,} iModulonDB candidate row(s); "
        f"{len(result.blocked):,} row(s) blocked"
    )
    if not args.apply:
        print("dry run: no output written; pass --apply to write review artifacts")
        return 0
    _validate_output(args.out)
    _write_outputs(result, args.out)
    print(f"wrote {args.out}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--genes",
        type=Path,
        nargs="+",
        required=True,
        help=(
            "normalized iModulonDB component-gene JSONL. Each row must include "
            "organism, dataset, imodulon, gene_id, weight, in_imodulon, and "
            "optionally uniprot_id."
        ),
    )
    parser.add_argument(
        "--protein-registry",
        type=Path,
        default=DEFAULT_PROTEIN_REGISTRY,
        help=f"ProteinReference JSONL registry (default: {DEFAULT_PROTEIN_REGISTRY})",
    )
    parser.add_argument(
        "--traits",
        type=Path,
        default=DEFAULT_TRAITS,
        help=f"trait YAML root (default: {DEFAULT_TRAITS})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"artifact directory (default: {DEFAULT_OUT})",
    )
    parser.add_argument("--apply", action="store_true", help="write output artifacts")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        return _run(_parser().parse_args(argv))
    except (ImodulonStageError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
