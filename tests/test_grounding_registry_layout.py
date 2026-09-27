"""Tests for the sharded evidence/bindings registry layout (#801).

Everything here builds its registries under ``tmp_path``; nothing writes
``data/grounding``, and only the production test at the end reads it. The module never
writes a registry itself, so ``install`` below applies a ``plan_sharded_write`` plan the
way the promoter's transaction does, minus the rollback that the promoter's own tests
cover.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))
layout = importlib.import_module("grounding_registry_layout")
RegistryLayoutError = layout.RegistryLayoutError


def key(prefix: str, index: int = 0) -> str:
    """A valid evidence id that belongs in shard ``<prefix>.jsonl``."""
    return f"ug-evidence:{prefix}{index:062x}"


def row(evidence_id: str, note: str = "x") -> dict:
    return {"evidence_id": evidence_id, "note": note, "a": [1, {"z": None, "b": True}]}


def registry_text(rows: list[dict]) -> str:
    ordered = sorted(rows, key=lambda item: item["evidence_id"])
    return "".join(layout.canonical_line(item) for item in ordered)


# U+2028 is a line break to str.splitlines() but row content to JSON; the reader
# must split on LF only or this row would tear in two.
BASE_ROWS = [
    row(key("00", 1)),
    row(key("00", 2)),
    row(key("7f", 1), note="é 漢"),
    row(key("ff", 3)),
]
BASE_TEXT = registry_text(BASE_ROWS)


def install(path: Path, text: str) -> list[tuple[Path, bytes | None]]:
    plan = layout.plan_sharded_write(path, text)
    for target, payload in plan:
        if payload is None:
            target.unlink()
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    return plan


def rewrite_shard(directory: Path, name: str, data: bytes | None) -> None:
    """Replace one shard AND regenerate the manifest, isolating a row-level defect."""
    target = directory / name
    if data is None:
        target.unlink()
    else:
        target.write_bytes(data)
    shards = {
        entry.name: entry.read_bytes()
        for entry in directory.iterdir()
        if layout.SHARD_RE.fullmatch(entry.name)
    }
    (directory / layout.MANIFEST_NAME).write_text(
        layout.build_manifest_text(shards), encoding="utf-8"
    )


def codes(image) -> list[str]:
    return [issue.code for issue in image.issues]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def registry(tmp_path: Path) -> Path:
    path = tmp_path / "occurrence_evidence.jsonl.d"
    install(path, BASE_TEXT)
    return path


def random_rows(rng: random.Random, count: int) -> list[dict]:
    alphabet = 'abé漢 "\\\t\r😀 '
    rows = []
    for index in range(count):
        digest = hashlib.sha256(f"{rng.random()}:{index}".encode()).hexdigest()
        rows.append(
            {
                "evidence_id": f"ug-evidence:{digest}",
                "text": "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 16))),
                "value": rng.choice([rng.randint(-(10**15), 10**15), rng.random(), None, False]),
                "nested": {"z": [rng.randint(0, 9) for _ in range(rng.randint(0, 4))], "a": {}},
            }
        )
    return rows


# --------------------------------------------------------------------------- names


def test_names_select_the_layout() -> None:
    assert layout.is_sharded(Path("x/occurrence_evidence.jsonl.d"))
    assert not layout.is_sharded("x/occurrence_evidence.jsonl")
    assert not layout.is_sharded(".jsonl.d")
    assert layout.legacy_twin(Path("a/b.jsonl.d")) == Path("a/b.jsonl")
    assert layout.legacy_twin(Path("a/b.jsonl")) == Path("a/b.jsonl.d")
    assert layout.legacy_twin(Path("a/b.json")) is None
    assert layout.shard_name(key("ab", 7)) == "ab.jsonl"
    for bad in ("ug-evidence:AB" + "0" * 62, "ug-evidence:ab", "x" * 76, None):
        with pytest.raises(RegistryLayoutError):
            layout.shard_name(bad)


def test_canonical_line_is_the_promoters_canonical_json() -> None:
    ground = importlib.import_module("ground_uniprot_examples")
    value = {"b": 1.5, "a": "é ", "c": [None, True, {"y": 1, "x": 2}]}
    assert layout.canonical_line(value) == '{"a":"é ","b":1.5,"c":[null,true,{"x":2,"y":1}]}\n'
    assert layout.canonical_line(value) == ground._canonical_json(value) + "\n"
    registry = {item["evidence_id"]: item for item in BASE_ROWS}
    shards = layout.split_registry_text(ground._registry_text(registry))
    assert b"".join(shards[name] for name in sorted(shards)) == BASE_TEXT.encode("utf-8")


def test_registry_exists_sees_either_layout(tmp_path: Path) -> None:
    sharded = tmp_path / "r.jsonl.d"
    flat = tmp_path / "r.jsonl"
    assert not layout.registry_exists(sharded) and not layout.registry_exists(flat)
    flat.write_text("", encoding="utf-8")
    assert layout.registry_exists(sharded) and layout.registry_exists(flat)
    flat.unlink()
    flat.symlink_to(tmp_path / "dangling")
    assert layout.registry_exists(sharded)


# ---------------------------------------------------------------------- round trip


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_split_join_round_trip_on_random_canonical_rows(tmp_path: Path, seed: int) -> None:
    rng = random.Random(seed)
    text = registry_text(random_rows(rng, rng.randint(1, 400)))
    raw = text.encode("utf-8")

    shards = layout.split_registry_text(text)
    assert b"".join(shards[name] for name in sorted(shards)) == raw
    assert all(layout.SHARD_RE.fullmatch(name) and data for name, data in shards.items())
    manifest = json.loads(layout.build_manifest_text(shards))
    assert manifest["logical_sha256"] == sha(raw)
    assert (manifest["row_count"], manifest["byte_count"]) == (raw.count(b"\n"), len(raw))

    path = tmp_path / "qualified_record_bindings.jsonl.d"
    plan = install(path, text)
    assert plan[-1][0].name == layout.MANIFEST_NAME
    image = layout.read_registry(path)
    assert (image.kind, image.issues) == ("sharded", ())
    assert "".join(line for _, _, line in image.lines) == text
    assert image.logical_sha256 == layout.sharded_digest(path) == sha(raw)
    assert layout.plan_sharded_write(path, text) == []


def test_empty_registry_is_a_directory_holding_only_the_manifest(tmp_path: Path) -> None:
    assert layout.split_registry_text("") == {}
    manifest = json.loads(layout.build_manifest_text({}))
    assert manifest["shards"] == {}
    assert (manifest["row_count"], manifest["byte_count"]) == (0, 0)
    assert manifest["logical_sha256"] == sha(b"")

    path = tmp_path / "occurrence_evidence.jsonl.d"
    plan = install(path, "")
    assert plan == [(path / layout.MANIFEST_NAME, layout.build_manifest_text({}).encode())]
    assert sorted(entry.name for entry in path.iterdir()) == [layout.MANIFEST_NAME]
    image = layout.read_registry(path)
    assert (image.kind, image.lines, image.issues) == ("sharded", (), ())
    assert layout.sharded_digest(path) == sha(b"")
    assert layout.plan_sharded_write(path, "") == []


def _unsorted() -> str:
    first, second = (layout.canonical_line(item) for item in BASE_ROWS[:2])
    return second + first


@pytest.mark.parametrize(
    ("text", "code"),
    [
        pytest.param(_unsorted(), "registry_row_unsorted", id="unsorted"),
        pytest.param(layout.canonical_line(BASE_ROWS[0]) * 2, "registry_row_unsorted",
                     id="duplicate"),
        pytest.param(json.dumps(BASE_ROWS[0], sort_keys=True) + "\n",
                     "registry_row_noncanonical", id="spaced-separators"),
        pytest.param(json.dumps(BASE_ROWS[0], separators=(",", ":")) + "\n",
                     "registry_row_noncanonical", id="unsorted-object-keys"),
        pytest.param(json.dumps(BASE_ROWS[2], sort_keys=True, separators=(",", ":")) + "\n",
                     "registry_row_noncanonical", id="ascii-escaped"),
        pytest.param(layout.canonical_line(BASE_ROWS[0])[:-1] + "\r\n",
                     "registry_row_noncanonical", id="crlf"),
        pytest.param(layout.canonical_line(BASE_ROWS[0]) + "\n"
                     + layout.canonical_line(BASE_ROWS[1]),
                     "registry_row_noncanonical", id="blank-line"),
        pytest.param(layout.canonical_line(BASE_ROWS[0])[:-1],
                     "registry_row_noncanonical", id="missing-final-newline"),
        pytest.param("not json\n", "registry_row_noncanonical", id="unparseable"),
        pytest.param(layout.canonical_line({"evidence_id": "ug-evidence:" + "A" * 64}),
                     "registry_row_misplaced", id="uppercase-key"),
        pytest.param(layout.canonical_line({"evidence_id": "ug-evidence:abc"}),
                     "registry_row_misplaced", id="short-key"),
        pytest.param(layout.canonical_line({"note": "no key"}),
                     "registry_row_misplaced", id="missing-key"),
        pytest.param(layout.canonical_line([key("00")]), "registry_row_misplaced",
                     id="not-an-object"),
    ],
)
def test_split_refuses_malformed_text(text: str, code: str) -> None:
    with pytest.raises(RegistryLayoutError) as caught:
        layout.split_registry_text(text)
    assert caught.value.code == code


def test_manifest_is_a_deterministic_closed_function_of_shard_bytes(tmp_path: Path) -> None:
    shards = layout.split_registry_text(BASE_TEXT)
    text = layout.build_manifest_text(shards)
    assert layout.build_manifest_text(dict(reversed(list(shards.items())))) == text
    manifest = json.loads(text)
    assert text == json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    assert set(manifest) == {
        "byte_count", "key_field", "layout", "layout_version", "logical_sha256", "row_count",
        "shards",
    }
    assert (manifest["layout"], manifest["layout_version"], manifest["key_field"]) == (
        "evidence-id-hex2", 1, "evidence_id",
    )
    assert manifest["shards"] == {
        name: {"bytes": len(data), "rows": data.count(b"\n"), "sha256": sha(data)}
        for name, data in shards.items()
    }
    assert sorted(manifest["shards"]) == ["00.jsonl", "7f.jsonl", "ff.jsonl"]
    assert manifest["shards"]["00.jsonl"]["rows"] == 2

    # No path or registry name: the same rows give the same manifest bytes anywhere.
    first, second = tmp_path / "a.jsonl.d", tmp_path / "other" / "b.jsonl.d"
    install(first, BASE_TEXT)
    install(second, BASE_TEXT)
    assert (first / "manifest.json").read_bytes() == (second / "manifest.json").read_bytes()
    assert str(tmp_path) not in text


# -------------------------------------------------------------------------- reader


def test_clean_read_yields_shard_lines_from_checked_bytes(registry: Path) -> None:
    image = layout.read_registry(registry)
    assert (image.kind, image.issues) == ("sharded", ())
    assert [(source.name, number) for source, number, _ in image.lines] == [
        ("00.jsonl", 1), ("00.jsonl", 2), ("7f.jsonl", 1), ("ff.jsonl", 1),
    ]
    assert image.lines[2][2] == layout.canonical_line(BASE_ROWS[2])
    assert image.manifest == json.loads((registry / "manifest.json").read_text())
    assert image.logical_sha256 == sha(BASE_TEXT.encode("utf-8"))


def test_ds_store_is_the_one_tolerated_stray_entry(registry: Path) -> None:
    (registry / ".DS_Store").write_bytes(b"\0finder")
    assert layout.read_registry(registry).issues == ()
    assert layout.sharded_digest(registry) == sha(BASE_TEXT.encode("utf-8"))
    assert layout.plan_sharded_write(registry, BASE_TEXT) == []


def test_absent_registry_has_no_issue_so_callers_keep_their_not_found(tmp_path: Path) -> None:
    path = tmp_path / "missing" / "occurrence_evidence.jsonl.d"
    image = layout.read_registry(path)
    assert (image.kind, image.lines, image.issues) == ("absent", (), ())
    assert layout.sharded_digest(path) is None
    assert not path.parent.exists()


def test_unmigrated_legacy_flat_file_is_a_layout_conflict(tmp_path: Path) -> None:
    flat = tmp_path / "occurrence_evidence.jsonl"
    flat.write_text(BASE_TEXT, encoding="utf-8")
    sharded = tmp_path / "occurrence_evidence.jsonl.d"
    image = layout.read_registry(sharded)
    assert image.kind == "sharded" and codes(image) == ["registry_layout_conflict"]
    assert "unmigrated legacy flat file" in image.issues[0].message
    assert "just migrate-grounding-registries --apply" in image.issues[0].message
    assert image.lines == ()
    with pytest.raises(RegistryLayoutError) as caught:
        layout.sharded_digest(sharded)
    assert caught.value.code == "registry_layout_conflict"


def test_both_layouts_present_is_a_conflict_from_either_side(registry: Path) -> None:
    flat = registry.with_name("occurrence_evidence.jsonl")
    flat.write_text(BASE_TEXT, encoding="utf-8")
    image = layout.read_registry(registry)
    assert codes(image) == ["registry_layout_conflict"]
    assert "both layouts present" in image.issues[0].message
    image = layout.read_registry(flat)
    assert image.kind == "flat" and codes(image) == ["registry_layout_conflict"]
    assert "registry migrated to" in image.issues[0].message


def test_legacy_flat_path_after_migration_is_a_conflict(registry: Path) -> None:
    flat = registry.with_name("occurrence_evidence.jsonl")
    image = layout.read_registry(flat)
    assert (image.kind, codes(image), image.lines) == ("flat", ["registry_layout_conflict"], ())
    assert f"registry migrated to {registry}" in image.issues[0].message
    with pytest.raises(RegistryLayoutError) as caught:
        layout.sharded_digest(flat)
    assert caught.value.code == "registry_layout_conflict"


def test_sharded_path_that_is_not_a_real_directory_is_a_conflict(
    registry: Path, tmp_path: Path
) -> None:
    file_path = tmp_path / "file.jsonl.d"
    file_path.write_text(BASE_TEXT, encoding="utf-8")
    link = tmp_path / "link.jsonl.d"
    link.symlink_to(registry, target_is_directory=True)
    for path in (file_path, link):
        image = layout.read_registry(path)
        assert codes(image) == ["registry_layout_conflict"]
        assert "not a real directory" in image.issues[0].message


def test_interrupted_atomic_write_residue_is_named(registry: Path) -> None:
    residue = registry / ".00.jsonl.abcd"
    residue.write_bytes(b"partial")
    (registry / ".manifest.json.x1y2z3").write_bytes(b"{")
    image = layout.read_registry(registry)
    assert codes(image) == ["registry_shard_unexpected", "registry_shard_unexpected"]
    assert image.issues[0].file == residue
    assert image.issues[0].message == (
        f"interrupted atomic write residue: {residue}; "
        "remove after confirming no writer is running"
    )
    with pytest.raises(RegistryLayoutError) as caught:
        layout.sharded_digest(registry)
    assert caught.value.code == "registry_shard_unexpected"
    assert "interrupted atomic write residue" in str(caught.value)


UNEXPECTED_ENTRIES = [
    ("sub", lambda path: path.mkdir(), "subdirectory"),
    ("01.jsonl", lambda path: path.symlink_to(path.parent / "00.jsonl"), "symlink"),
    ("02.jsonl", lambda path: path.write_bytes(b""), "empty shard file"),
    ("notes.txt", lambda path: path.write_text("hi"), "unexpected entry"),
    ("0A.jsonl", lambda path: path.write_text("hi"), "unexpected entry"),
    (".hidden", lambda path: path.write_text("hi"), "unexpected entry"),
]


@pytest.mark.parametrize(
    ("name", "make", "fragment"),
    [pytest.param(*case, id=f"{case[0]}-{case[2]}") for case in UNEXPECTED_ENTRIES],
)
def test_unexpected_entries_are_refused(registry: Path, name, make, fragment: str) -> None:
    make(registry / name)
    image = layout.read_registry(registry)
    assert codes(image) == ["registry_shard_unexpected"]
    assert fragment in image.issues[0].message
    assert image.issues[0].file == registry / name
    with pytest.raises(RegistryLayoutError):
        layout.plan_sharded_write(registry, BASE_TEXT)


def test_missing_manifest_still_yields_lines(registry: Path) -> None:
    (registry / "manifest.json").unlink()
    image = layout.read_registry(registry)
    assert codes(image) == ["registry_manifest_missing"]
    assert len(image.lines) == len(BASE_ROWS)
    assert image.logical_sha256 is None
    with pytest.raises(RegistryLayoutError) as caught:
        layout.sharded_digest(registry)
    assert caught.value.code == "registry_manifest_missing"


def test_row_in_the_wrong_shard_is_misplaced(registry: Path) -> None:
    rewrite_shard(registry, "01.jsonl", layout.canonical_line(row(key("00", 9))).encode())
    image = layout.read_registry(registry)
    assert codes(image) == ["registry_row_misplaced"]
    issue = image.issues[0]
    assert (issue.file.name, issue.line) == ("01.jsonl", 1)
    assert "belongs in 00.jsonl" in issue.message


@pytest.mark.parametrize("duplicate", [False, True], ids=["swapped", "duplicate"])
def test_unsorted_or_duplicate_rows_are_refused(registry: Path, duplicate: bool) -> None:
    first, second = (layout.canonical_line(item) for item in BASE_ROWS[:2])
    data = (first + first) if duplicate else (second + first)
    rewrite_shard(registry, "00.jsonl", data.encode())
    image = layout.read_registry(registry)
    assert codes(image) == ["registry_row_unsorted"]
    assert (image.issues[0].file.name, image.issues[0].line) == ("00.jsonl", 2)
    assert ("duplicate" in image.issues[0].message) is duplicate


CANONICAL_00 = layout.canonical_line(BASE_ROWS[0]).encode()


@pytest.mark.parametrize(
    ("data", "line", "fragment"),
    [
        pytest.param(json.dumps(BASE_ROWS[0]).encode() + b"\n", 1, "canonical", id="spaced"),
        pytest.param(CANONICAL_00[:-1] + b"\r\n", 1, "canonical", id="crlf"),
        pytest.param(CANONICAL_00[:-1], 1, "missing final newline", id="no-final-newline"),
        pytest.param(CANONICAL_00 + b"\n", 2, "blank line", id="blank-line"),
        pytest.param(CANONICAL_00 + b"  \n", 2, "blank line", id="whitespace-line"),
        pytest.param(b'{"evidence_id":"' + key("00", 5).encode() + b'","note":"\xff"}\n', 1,
                     "not UTF-8", id="invalid-utf8"),
    ],
)
def test_noncanonical_rows_are_refused(registry: Path, data: bytes, line: int, fragment) -> None:
    rewrite_shard(registry, "00.jsonl", data)
    image = layout.read_registry(registry)
    assert codes(image) == ["registry_row_noncanonical"]
    assert (image.issues[0].file.name, image.issues[0].line) == ("00.jsonl", line)
    assert fragment in image.issues[0].message
    with pytest.raises(RegistryLayoutError) as caught:
        layout.sharded_digest(registry)
    assert caught.value.code == "registry_row_noncanonical"


def test_unparseable_row_is_left_to_the_loader_but_never_hashed(registry: Path) -> None:
    rewrite_shard(registry, "00.jsonl", CANONICAL_00 + b"{not json\n")
    image = layout.read_registry(registry)
    assert image.issues == ()
    assert image.lines[1][1:] == (2, "{not json\n")
    with pytest.raises(RegistryLayoutError) as caught:
        layout.sharded_digest(registry)
    assert caught.value.code == "registry_row_noncanonical"
    assert "00.jsonl:2" in str(caught.value)


def _edit_manifest(directory: Path, **changes) -> None:
    manifest = json.loads((directory / "manifest.json").read_text())
    manifest.update(changes)
    (directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


MANIFEST_DAMAGE = [
    (lambda path: (path / "ff.jsonl").unlink(), "missing shard ff.jsonl"),
    (lambda path: (path / "aa.jsonl").write_text(layout.canonical_line(row(key("aa")))),
     "extra shard aa.jsonl"),
    (lambda path: (path / "7f.jsonl").write_text(layout.canonical_line(row(key("7f", 1)))),
     "wrong shard 7f.jsonl"),
    (lambda path: _edit_manifest(path, layout="namespace-nt16"), "unknown layout"),
    (lambda path: _edit_manifest(path, layout_version=2), "unknown layout_version"),
    (lambda path: _edit_manifest(path, row_count=99), "wrong row_count"),
    (lambda path: _edit_manifest(path, registry="occurrence_evidence"), "wrong registry"),
    (lambda path: (path / "manifest.json").write_text(
        json.dumps(json.loads((path / "manifest.json").read_text()), sort_keys=True)),
     "not in canonical serialization"),
    (lambda path: (path / "manifest.json").write_text("{"), "not a JSON object"),
]


@pytest.mark.parametrize(
    ("damage", "fragment"),
    [pytest.param(damage, fragment, id=fragment) for damage, fragment in MANIFEST_DAMAGE],
)
def test_manifest_must_match_the_shards_exactly(registry: Path, damage, fragment: str) -> None:
    damage(registry)
    image = layout.read_registry(registry)
    assert codes(image) == ["registry_manifest_mismatch"]
    assert image.issues[0].file == registry / "manifest.json"
    assert fragment in image.issues[0].message
    with pytest.raises(RegistryLayoutError) as caught:
        layout.sharded_digest(registry)
    assert caught.value.code == "registry_manifest_mismatch"


def test_manifest_mismatch_lists_at_most_five_shards(registry: Path) -> None:
    for prefix in ("10", "20", "30", "40", "50", "60"):
        (registry / f"{prefix}.jsonl").write_text(layout.canonical_line(row(key(prefix))))
    message = layout.read_registry(registry).issues[0].message
    assert message.count("extra shard") == 5 and message.endswith("; +1 more")


def test_flat_reading_is_unchanged_and_lenient(tmp_path: Path) -> None:
    path = tmp_path / "staging.jsonl"
    lines = [layout.canonical_line(item) for item in BASE_ROWS]
    data = (lines[1] + "\n" + json.dumps(BASE_ROWS[0]) + "\r\n" + lines[2] + lines[3][:-1])
    path.write_bytes(data.encode("utf-8"))
    image = layout.read_registry(path)
    assert (image.kind, image.issues, image.manifest) == ("flat", (), None)
    with path.open(encoding="utf-8") as handle:
        assert image.lines == tuple((path, number, text) for number, text in enumerate(handle, 1))
    assert image.logical_sha256 == sha(data.encode("utf-8"))
    with pytest.raises(RegistryLayoutError) as caught:
        layout.sharded_digest(path)
    assert caught.value.code == "registry_layout_conflict"

    directory = tmp_path / "dir.jsonl"
    directory.mkdir()
    assert codes(layout.read_registry(directory)) == ["registry_layout_conflict"]


# ---------------------------------------------------------------------------- plan


def test_plan_is_empty_when_nothing_changed(registry: Path) -> None:
    assert layout.plan_sharded_write(registry, BASE_TEXT) == []


def test_plan_one_row_rewrites_one_shard_then_the_manifest(registry: Path) -> None:
    text = registry_text([*BASE_ROWS, row(key("00", 3))])
    plan = layout.plan_sharded_write(registry, text)
    assert [(target.name, payload is None) for target, payload in plan] == [
        ("00.jsonl", False), ("manifest.json", False),
    ]
    install(registry, text)
    assert layout.sharded_digest(registry) == sha(text.encode("utf-8"))


def test_plan_deletes_an_emptied_shard(registry: Path) -> None:
    kept = [item for item in BASE_ROWS if layout.shard_name(item["evidence_id"]) != "7f.jsonl"]
    text = registry_text(kept)
    plan = layout.plan_sharded_write(registry, text)
    assert [(target.name, payload) for target, payload in plan][:1] == [("7f.jsonl", None)]
    assert [target.name for target, _ in plan] == ["7f.jsonl", "manifest.json"]
    install(registry, text)
    assert not (registry / "7f.jsonl").exists()
    assert layout.read_registry(registry).issues == ()
    assert layout.sharded_digest(registry) == sha(text.encode("utf-8"))


def test_plan_orders_writes_then_deletes_then_manifest_last(registry: Path) -> None:
    rows = [row(key("01")), row(key("00", 1), note="changed"), row(key("ff", 3)), row(key("a0"))]
    plan = layout.plan_sharded_write(registry, registry_text(rows))
    assert [(target.name, payload is None) for target, payload in plan] == [
        ("00.jsonl", False), ("01.jsonl", False), ("a0.jsonl", False),
        ("7f.jsonl", True), ("manifest.json", False),
    ]


def test_plan_for_a_missing_directory_writes_everything_and_creates_nothing(
    tmp_path: Path,
) -> None:
    path = tmp_path / "new" / "qualified_record_bindings.jsonl.d"
    plan = layout.plan_sharded_write(path, BASE_TEXT)
    assert [target.name for target, _ in plan] == [
        "00.jsonl", "7f.jsonl", "ff.jsonl", "manifest.json",
    ]
    assert plan[-1][1] == layout.build_manifest_text(layout.split_registry_text(BASE_TEXT)).encode()
    assert not path.parent.exists()


def test_plan_rewrites_a_stale_manifest_even_when_shards_match(registry: Path) -> None:
    _edit_manifest(registry, row_count=99)
    plan = layout.plan_sharded_write(registry, BASE_TEXT)
    assert [target.name for target, _ in plan] == ["manifest.json"]


def test_plan_refuses_before_writing_anything(registry: Path, tmp_path: Path) -> None:
    with pytest.raises(RegistryLayoutError) as caught:
        layout.plan_sharded_write(registry, _unsorted())
    assert caught.value.code == "registry_row_unsorted"
    with pytest.raises(RegistryLayoutError) as caught:
        layout.plan_sharded_write(tmp_path / "flat.jsonl", BASE_TEXT)
    assert caught.value.code == "registry_layout_conflict"
    (registry / ".7f.jsonl.q9w8e7").write_bytes(b"partial")
    with pytest.raises(RegistryLayoutError) as caught:
        layout.plan_sharded_write(registry, BASE_TEXT)
    assert caught.value.code == "registry_shard_unexpected"
    assert "interrupted atomic write residue" in str(caught.value)
    not_a_directory = tmp_path / "file.jsonl.d"
    not_a_directory.write_text("")
    with pytest.raises(RegistryLayoutError) as caught:
        layout.plan_sharded_write(not_a_directory, BASE_TEXT)
    assert caught.value.code == "registry_layout_conflict"


# ---------------------------------------------------------------------------- lock

_HOLD = """
import sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import grounding_registry_layout as layout
with layout.registry_lock(Path(sys.argv[2])):
    print("locked", flush=True)
    time.sleep(120)
"""

_TRY = """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import grounding_registry_layout as layout
try:
    with layout.registry_lock(Path(sys.argv[2])):
        print("acquired")
except layout.RegistryLayoutError as error:
    print(error)
    raise SystemExit(3)
"""


def test_registry_lock_second_holder_in_a_subprocess_fails_fast(tmp_path: Path) -> None:
    with layout.registry_lock(tmp_path) as lock_path:
        assert lock_path == tmp_path / layout.LOCK_NAME
        assert lock_path.read_text() == f"{os.getpid()}\n"
        # LOCK_NB: a blocking lock would hang here until the timeout fails the test.
        result = subprocess.run(
            [sys.executable, "-c", _TRY, str(SCRIPTS), str(tmp_path)],
            capture_output=True, text=True, timeout=120,
        )
    assert result.returncode == 3, result.stderr
    assert result.stdout.startswith("registry_locked: ")
    assert f"pid {os.getpid()}" in result.stdout
    with layout.registry_lock(tmp_path) as lock_path:
        assert lock_path is not None


def test_registry_lock_is_released_when_the_holder_is_killed(tmp_path: Path) -> None:
    holder = subprocess.Popen(
        [sys.executable, "-c", _HOLD, str(SCRIPTS), str(tmp_path)],
        stdout=subprocess.PIPE, text=True,
    )
    try:
        assert holder.stdout.readline().strip() == "locked"
        with pytest.raises(RegistryLayoutError) as caught:
            with layout.registry_lock(tmp_path):
                pass
        assert caught.value.code == "registry_locked"
        assert f"pid {holder.pid}" in str(caught.value)
        holder.kill()
        holder.wait(timeout=60)
    finally:
        holder.kill()
        holder.wait(timeout=60)
        holder.stdout.close()
    with layout.registry_lock(tmp_path) as lock_path:
        assert lock_path.read_text() == f"{os.getpid()}\n"


def test_registry_lock_on_a_missing_directory_yields_none_and_creates_nothing(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing" / "grounding"
    with layout.registry_lock(missing) as lock_path:
        assert lock_path is None
    assert not missing.parent.exists()


@pytest.mark.parametrize("spelling", ["exact", "case-alias", "subdirectory"])
def test_registry_lock_never_lands_inside_a_sharded_registry(
    registry: Path, spelling: str
) -> None:
    # On case-insensitive APFS the upper-case alias *is* the registry directory.
    directory = {
        "exact": registry,
        "case-alias": registry.with_name(registry.name[: -len("d")] + "D"),
        "subdirectory": registry / "nested",
    }[spelling]
    before = sorted(entry.name for entry in registry.iterdir())
    with pytest.raises(RegistryLayoutError) as caught:
        with layout.registry_lock(directory):
            pass
    assert caught.value.code == "registry_layout_conflict"
    assert sorted(entry.name for entry in registry.iterdir()) == before
    assert list(registry.parent.rglob(layout.LOCK_NAME)) == []


def test_sharded_ancestor_ignores_letter_case() -> None:
    assert layout.sharded_ancestor(Path("/r/x.jsonl.d/sub/f")) == Path("/r/x.jsonl.d")
    assert layout.sharded_ancestor(Path("/r/X.JSONL.D")) == Path("/r/X.JSONL.D")
    assert layout.sharded_ancestor(Path("/r/.jsonl.d/x.jsonl")) is None
    assert layout.sharded_ancestor(Path("/r/grounding")) is None


# --------------------------------------------------------------------------- check


@pytest.fixture
def grounding_root(tmp_path: Path) -> Path:
    root = tmp_path / "grounding"
    for name in layout.CHECKED_REGISTRIES:
        install(root / name, BASE_TEXT)
    return root


def test_check_passes_a_clean_matched_pair(grounding_root: Path, capsys) -> None:
    assert layout.main(["check", "--root", str(grounding_root)]) == 0
    out = capsys.readouterr().out
    digest = sha(BASE_TEXT.encode("utf-8"))
    for name in layout.CHECKED_REGISTRIES:
        assert f"{name}: kind=sharded rows=4 shards=3 " in out
    assert f"logical_sha256={digest}" in out
    assert out.rstrip().endswith("grounding registries: OK")


def test_check_script_entry_point(grounding_root: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "grounding_registry_layout.py"), "check",
         "--root", str(grounding_root)],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert "grounding registries: OK" in result.stdout


def test_check_fails_when_key_sets_differ(grounding_root: Path, capsys) -> None:
    install(grounding_root / layout.CHECKED_REGISTRIES[1], registry_text(BASE_ROWS[:3]))
    assert layout.main(["check", "--root", str(grounding_root)]) == 1
    captured = capsys.readouterr()
    assert "key sets differ: 1 evidence row(s) without a binding" in captured.err
    assert captured.out.rstrip().endswith("grounding registries: FAILED")


def test_check_fails_on_any_issue(grounding_root: Path, capsys) -> None:
    (grounding_root / layout.CHECKED_REGISTRIES[0] / "manifest.json").unlink()
    assert layout.main(["check", "--root", str(grounding_root)]) == 1
    assert "registry_manifest_missing" in capsys.readouterr().err


def test_check_fails_on_an_oversized_shard(grounding_root: Path, capsys, monkeypatch) -> None:
    monkeypatch.setattr(layout, "MAX_SHARD_BYTES", 100)
    assert layout.main(["check", "--root", str(grounding_root)]) == 1
    assert "exceeds MAX_SHARD_BYTES 100" in capsys.readouterr().err


def test_check_fails_when_a_registry_is_absent(grounding_root: Path, capsys) -> None:
    for entry in (grounding_root / layout.CHECKED_REGISTRIES[1]).iterdir():
        entry.unlink()
    (grounding_root / layout.CHECKED_REGISTRIES[1]).rmdir()
    assert layout.main(["check", "--root", str(grounding_root)]) == 1
    assert f"{layout.CHECKED_REGISTRIES[1]}: absent" in capsys.readouterr().err


# ---------------------------------------------------------------------- production


def test_committed_registries_are_sharded_clean_and_paired() -> None:
    """Read-only check of the committed ``data/grounding`` registries.

    It fails rather than skips: a missing directory, a leftover flat twin, any layout
    issue, unequal evidence and bindings key sets, or a shard over the tripwire means
    the promoter and validator are about to refuse production data.
    """
    ground = importlib.import_module("ground_uniprot_examples")
    validator = importlib.import_module("validate_uniprot_grounding")
    evidence_path, bindings_path = (
        layout.DEFAULT_ROOT / name for name in layout.CHECKED_REGISTRIES
    )
    assert (ground.DEFAULT_DURABLE_EVIDENCE_REGISTRY, validator.DEFAULT_EVIDENCE_REGISTRY) == (
        evidence_path, evidence_path,
    )
    assert (
        ground.DEFAULT_DURABLE_QUALIFIED_RECORD_BINDINGS,
        validator.DEFAULT_QUALIFIED_RECORD_BINDINGS,
    ) == (bindings_path, bindings_path)

    key_sets = []
    for path in (evidence_path, bindings_path):
        assert not os.path.lexists(layout.legacy_twin(path)), f"legacy flat twin of {path}"
        image = layout.read_registry(path)
        assert image.kind == "sharded", f"{path} is {image.kind}"
        assert image.issues == (), image.issues[:5]
        # Also refuses a row that does not parse, which read_registry leaves to loaders.
        assert layout.sharded_digest(path) == image.logical_sha256
        shards = image.manifest["shards"]
        assert shards, f"{path} has no rows"
        assert max(entry["bytes"] for entry in shards.values()) <= layout.MAX_SHARD_BYTES
        key_sets.append({json.loads(line)[layout.KEY_FIELD] for _, _, line in image.lines})
    evidence_keys, binding_keys = key_sets
    assert evidence_keys == binding_keys, (
        f"{len(evidence_keys - binding_keys)} evidence row(s) without a binding, "
        f"{len(binding_keys - evidence_keys)} binding(s) without evidence"
    )
