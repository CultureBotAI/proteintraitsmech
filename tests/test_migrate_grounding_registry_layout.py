"""Tests for the one-time flat-to-sharded grounding registry migration (#801).

Every test migrates a small registry pair under ``tmp_path``; nothing reads or writes
``data/grounding``. The one git test builds its own throwaway repository.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
import shlex
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))
migrate = importlib.import_module("migrate_grounding_registry_layout")
ground = importlib.import_module("ground_uniprot_examples")
layout = importlib.import_module("grounding_registry_layout")

EVIDENCE = "occurrence_evidence"
BINDINGS = "qualified_record_bindings"


def key(prefix: str, index: int) -> str:
    return f"ug-evidence:{prefix}{index:062x}"


KEYS = [key("00", 1), key("00", 2), key("7f", 1), key("ff", 3)]
# 3 shards + manifest per registry, then the two flat deletes.
INSTALL_STEPS = 10


def registry_text(rows: list[dict]) -> str:
    ordered = sorted(rows, key=lambda row: row["evidence_id"])
    return "".join(layout.canonical_line(row) for row in ordered)


EVIDENCE_TEXT = registry_text(
    [{"evidence_id": item, "provider_kind": "INTERPRO", "note": "é 漢 "} for item in KEYS]
)
BINDINGS_TEXT = registry_text(
    [{"evidence_id": item, "record_path": f"data/traits/{index}.yaml"}
     for index, item in enumerate(KEYS)]
)
PROTEIN_BYTES = b'{"protein_id":"UniProtKB:P00001"}\n'
MEMBERSHIP_BYTES = b'{"membership_id":"m"}\n'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree(root: Path) -> dict[str, bytes | None]:
    """Every file (bytes) and directory (None) under ``root``, minus the lock file."""
    return {
        entry.relative_to(root).as_posix(): None if entry.is_dir() else entry.read_bytes()
        for entry in sorted(root.rglob("*"))
        if entry.name != layout.LOCK_NAME
    }


@pytest.fixture
def root(tmp_path: Path) -> Path:
    grounding = tmp_path / "grounding"
    grounding.mkdir()
    (grounding / f"{EVIDENCE}.jsonl").write_text(EVIDENCE_TEXT, encoding="utf-8")
    (grounding / f"{BINDINGS}.jsonl").write_text(BINDINGS_TEXT, encoding="utf-8")
    (grounding / "protein_registry.jsonl").write_bytes(PROTEIN_BYTES)
    (grounding / "uniprot_memberships.jsonl").write_bytes(MEMBERSHIP_BYTES)
    return grounding


@pytest.fixture
def report(tmp_path: Path) -> Path:
    return tmp_path / "reports" / "migration.json"


def run(root: Path, report: Path, *extra: str) -> int:
    return migrate.main(["--grounding-root", str(root), "--report", str(report), *extra])


def joined_shards(directory: Path) -> bytes:
    """What ``LC_ALL=C cat X.jsonl.d/[0-9a-f][0-9a-f].jsonl`` prints."""
    return b"".join(path.read_bytes() for path in sorted(directory.glob("[0-9a-f][0-9a-f].jsonl")))


# ------------------------------------------------------------------------- dry run


def test_dry_run_prints_the_plan_and_writes_nothing(root: Path, report: Path, capsys) -> None:
    before = tree(root.parent)

    assert run(root, report) == 0

    assert tree(root.parent) == before
    assert not (root / layout.LOCK_NAME).exists()
    captured = capsys.readouterr()
    assert "DRY-RUN: nothing written" in captured.err
    plan = json.loads(captured.out)
    assert (plan["mode"], plan["layout"], plan["layout_version"]) == (
        "dry-run", "evidence-id-hex2", 1,
    )
    assert plan["key_sequences_equal"] is True
    assert plan["unchanged_registries_sha256"] == {
        "protein_registry.jsonl": sha(PROTEIN_BYTES),
        "uniprot_memberships.jsonl": sha(MEMBERSHIP_BYTES),
    }
    for name, text in ((EVIDENCE, EVIDENCE_TEXT), (BINDINGS, BINDINGS_TEXT)):
        entry = plan["registries"][name]
        raw = text.encode("utf-8")
        assert entry["flat_sha256"] == entry["logical_sha256"] == sha(raw)
        assert (entry["rows"], entry["bytes"], entry["shards"]) == (4, len(raw), 3)
        assert (entry["files_to_create"], entry["files_to_delete"]) == (4, 1)
        assert entry["max_shard_bytes"] >= entry["min_shard_bytes"] > 0
        assert set(entry["proofs"].values()) == {True} and len(entry["proofs"]) == 4
    evidence, bindings = (plan["registries"][name] for name in (EVIDENCE, BINDINGS))
    assert evidence["key_sequence_sha256"] == bindings["key_sequence_sha256"]
    assert evidence["key_sequence_sha256"] == sha("".join(item + "\n" for item in KEYS).encode())


def test_expected_input_hashes_are_accepted_when_they_match(
    root: Path, report: Path, capsys
) -> None:
    arguments = [
        "--expect-evidence-sha256", sha(EVIDENCE_TEXT.encode("utf-8")),
        "--expect-bindings-sha256", sha(BINDINGS_TEXT.encode("utf-8")),
    ]
    assert run(root, report, *arguments) == 0
    assert json.loads(capsys.readouterr().out)["mode"] == "dry-run"


@pytest.mark.parametrize("value", ["caa9834e838a", "A" * 64, "g" * 64])
def test_expected_hash_must_be_a_full_lowercase_sha256(root: Path, report: Path, value) -> None:
    with pytest.raises(SystemExit) as caught:
        run(root, report, "--expect-evidence-sha256", value)
    assert caught.value.code == 2


# --------------------------------------------------------------------------- apply


def test_apply_migrates_byte_identically(root: Path, report: Path, capsys) -> None:
    arguments = [
        "--apply",
        "--expect-evidence-sha256", sha(EVIDENCE_TEXT.encode("utf-8")),
        "--expect-bindings-sha256", sha(BINDINGS_TEXT.encode("utf-8")),
    ]
    assert run(root, report, *arguments) == 0

    captured = capsys.readouterr()
    assert "MIGRATED 2 registries" in captured.err
    for name, text in ((EVIDENCE, EVIDENCE_TEXT), (BINDINGS, BINDINGS_TEXT)):
        raw = text.encode("utf-8")
        directory = root / f"{name}.jsonl.d"
        assert not os.path.lexists(root / f"{name}.jsonl")
        assert sorted(entry.name for entry in directory.iterdir()) == [
            "00.jsonl", "7f.jsonl", "ff.jsonl", layout.MANIFEST_NAME,
        ]
        assert joined_shards(directory) == raw
        manifest = json.loads((directory / layout.MANIFEST_NAME).read_text(encoding="utf-8"))
        assert manifest["logical_sha256"] == sha(raw)
        assert layout.read_registry(directory).issues == ()
        assert layout.plan_sharded_write(directory, text) == []
        # The promoter sees the digest it saw before the migration.
        assert ground._artifact_digest(directory) == sha(raw)
    assert (root / "protein_registry.jsonl").read_bytes() == PROTEIN_BYTES
    assert (root / "uniprot_memberships.jsonl").read_bytes() == MEMBERSHIP_BYTES
    assert layout.main(["check", "--root", str(root)]) == 0

    written = json.loads(report.read_text(encoding="utf-8"))
    assert json.loads(captured.out) == written
    assert written["mode"] == "apply"
    for name in (EVIDENCE, BINDINGS):
        assert set(written["post_apply"][name].values()) == {True}
    assert written["post_apply"]["unchanged_registries_sha256"] == (
        written["unchanged_registries_sha256"]
    )


def test_rerun_after_apply_is_a_no_op(root: Path, report: Path, capsys) -> None:
    assert run(root, report, "--apply") == 0
    report.unlink()
    capsys.readouterr()
    after = tree(root)

    for extra in ((), ("--apply",)):
        assert run(root, report, *extra) == 0
        out = capsys.readouterr().out
        assert out.startswith("already migrated: ")
        assert f"logical_sha256={sha(EVIDENCE_TEXT.encode('utf-8'))}" in out
        assert tree(root) == after
        assert not report.exists()

    # The pins stay meaningful after migration: the logical sha is the flat sha.
    assert run(root, report, "--expect-bindings-sha256", sha(BINDINGS_TEXT.encode())) == 0
    assert run(root, report, "--apply", "--expect-bindings-sha256", "0" * 64) == 2
    assert "already migrated with logical sha256" in capsys.readouterr().err


def test_rerun_refuses_a_damaged_sharded_registry(root: Path, report: Path, capsys) -> None:
    assert run(root, report, "--apply") == 0
    (root / f"{BINDINGS}.jsonl.d" / "7f.jsonl").unlink()
    capsys.readouterr()
    assert run(root, report) == 2
    assert "registry_manifest_mismatch" in capsys.readouterr().err


# ------------------------------------------------------------------------ refusals


def _make_sharded(root: Path, name: str, text: str, *, keep_flat: bool) -> None:
    directory = root / f"{name}.jsonl.d"
    directory.mkdir()
    shards = layout.split_registry_text(text)
    for shard, data in shards.items():
        (directory / shard).write_bytes(data)
    (directory / layout.MANIFEST_NAME).write_text(
        layout.build_manifest_text(shards), encoding="utf-8"
    )
    if not keep_flat:
        (root / f"{name}.jsonl").unlink()


def _lines(text: str) -> list[str]:
    # LF only: EVIDENCE_TEXT carries a raw U+2028, which splitlines() would break on.
    return [line + "\n" for line in text.split("\n")[:-1]]


def _swap_lines(text: str) -> str:
    lines = _lines(text)
    return "".join([lines[1], lines[0], *lines[2:]])


REFUSALS = {
    "mixed": (
        lambda root: _make_sharded(root, EVIDENCE, EVIDENCE_TEXT, keep_flat=False),
        "occurrence_evidence: sharded, qualified_record_bindings: flat",
    ),
    "both-layouts": (
        lambda root: _make_sharded(root, BINDINGS, BINDINGS_TEXT, keep_flat=True),
        "qualified_record_bindings: both layouts present",
    ),
    "missing": (
        lambda root: (root / f"{BINDINGS}.jsonl").unlink(),
        "qualified_record_bindings: missing",
    ),
    "noncanonical": (
        lambda root: (root / f"{EVIDENCE}.jsonl").write_text(
            "".join(
                json.dumps(json.loads(line), sort_keys=True) + "\n"
                for line in _lines(EVIDENCE_TEXT)
            ),
            encoding="utf-8",
        ),
        "registry_row_noncanonical",
    ),
    "unsorted": (
        lambda root: (root / f"{BINDINGS}.jsonl").write_text(
            _swap_lines(BINDINGS_TEXT), encoding="utf-8"
        ),
        "registry_row_unsorted",
    ),
    "crlf": (
        lambda root: (root / f"{EVIDENCE}.jsonl").write_bytes(
            EVIDENCE_TEXT.replace("\n", "\r\n").encode("utf-8")
        ),
        "never normalizes rows",
    ),
    "key-sequence-mismatch": (
        lambda root: (root / f"{BINDINGS}.jsonl").write_text(
            "".join(_lines(BINDINGS_TEXT)[:3]), encoding="utf-8"
        ),
        "1 evidence row(s) without a binding",
    ),
    "not-utf8": (
        lambda root: (root / f"{EVIDENCE}.jsonl").write_bytes(b"\xff\n"),
        "is not a canonical, sorted registry",
    ),
    "flat-symlink": (
        lambda root: (
            (root / f"{EVIDENCE}.jsonl").rename(root / "elsewhere.jsonl"),
            (root / f"{EVIDENCE}.jsonl").symlink_to(root / "elsewhere.jsonl"),
        ),
        "not a regular file",
    ),
}


@pytest.mark.parametrize("apply", [False, True], ids=["dry-run", "apply"])
@pytest.mark.parametrize("case", sorted(REFUSALS))
def test_refusals_leave_everything_untouched(
    root: Path, report: Path, capsys, case: str, apply: bool
) -> None:
    damage, fragment = REFUSALS[case]
    damage(root)
    before = tree(root.parent)

    assert run(root, report, *(["--apply"] if apply else [])) == 2

    assert fragment in capsys.readouterr().err
    assert tree(root.parent) == before
    assert not (root / layout.LOCK_NAME).exists()


@pytest.mark.parametrize("registry", [EVIDENCE, BINDINGS])
def test_expected_hash_mismatch_is_refused(root: Path, report: Path, capsys, registry) -> None:
    before = tree(root.parent)
    flag = "--expect-evidence-sha256" if registry == EVIDENCE else "--expect-bindings-sha256"

    assert run(root, report, "--apply", flag, "0" * 64) == 2

    assert f"not the expected {'0' * 64}" in capsys.readouterr().err
    assert tree(root.parent) == before


def test_report_inside_data_or_the_grounding_root_is_refused(
    root: Path, tmp_path: Path, capsys, monkeypatch
) -> None:
    monkeypatch.setattr(migrate, "REPO_ROOT", tmp_path)
    before = tree(tmp_path)
    for target in (tmp_path / "data" / "report.json", root / "report.json"):
        assert run(root, target, "--apply") == 2
        assert "--report must be outside data/" in capsys.readouterr().err
    assert tree(tmp_path) == before


def test_flat_change_between_plan_and_apply_is_refused(
    root: Path, report: Path, capsys, monkeypatch
) -> None:
    flat = root / f"{EVIDENCE}.jsonl"
    real_lock = layout.registry_lock

    @contextmanager
    def lock_after_a_concurrent_write(directory):
        # Another writer finished between the unlocked read and taking the lock.
        flat.write_text(
            EVIDENCE_TEXT + layout.canonical_line({"evidence_id": key("ff", 9)}),
            encoding="utf-8",
        )
        with real_lock(directory) as held:
            yield held

    monkeypatch.setattr(migrate.layout, "registry_lock", lock_after_a_concurrent_write)
    assert run(root, report, "--apply") == 2
    assert "changed since the plan was made" in capsys.readouterr().err
    assert not (root / f"{EVIDENCE}.jsonl.d").exists()
    assert not (root / f"{BINDINGS}.jsonl.d").exists()
    assert (root / f"{BINDINGS}.jsonl").read_text(encoding="utf-8") == BINDINGS_TEXT
    assert not report.exists()


def test_apply_refuses_while_another_writer_holds_the_lock(
    root: Path, report: Path, capsys
) -> None:
    before = tree(root.parent)
    with layout.registry_lock(root) as held:
        assert held == root / layout.LOCK_NAME
        assert run(root, report, "--apply") == 2
        assert "registry_locked" in capsys.readouterr().err
        # A dry run never takes the lock.
        assert run(root, report) == 0
    assert tree(root.parent) == before


# ------------------------------------------------------------------------ rollback


@pytest.mark.parametrize("step_index", range(INSTALL_STEPS))
def test_injected_failure_restores_both_flat_files_and_removes_both_directories(
    root: Path, report: Path, capsys, monkeypatch, step_index: int
) -> None:
    before = tree(root.parent)
    calls = 0
    apply_operation = ground._apply_artifact_operation

    def fail_after(path, payload):
        nonlocal calls
        calls += 1
        apply_operation(path, payload)
        if calls - 1 == step_index:
            raise OSError("injected migration fault")

    monkeypatch.setattr(ground, "_apply_artifact_operation", fail_after)
    assert run(root, report, "--apply") == 2

    assert calls == step_index + 1
    assert "failed and was rolled back: injected migration fault" in capsys.readouterr().err
    assert tree(root.parent) == before


def test_interrupt_during_the_flat_deletes_rolls_back_and_reraises(
    root: Path, report: Path, monkeypatch
) -> None:
    before = tree(root.parent)
    apply_operation = ground._apply_artifact_operation

    def interrupt_on_delete(path, payload):
        apply_operation(path, payload)
        if payload is None:
            raise KeyboardInterrupt

    monkeypatch.setattr(ground, "_apply_artifact_operation", interrupt_on_delete)
    with pytest.raises(KeyboardInterrupt):
        run(root, report, "--apply")
    assert tree(root.parent) == before


def test_post_install_verify_mismatch_rolls_back(
    root: Path, report: Path, capsys, monkeypatch
) -> None:
    before = tree(root.parent)
    monkeypatch.setattr(ground.layout, "sharded_digest", lambda path: "0" * 64)
    assert run(root, report, "--apply") == 2
    assert "does not verify as the intended image" in capsys.readouterr().err
    assert tree(root.parent) == before


# ----------------------------------------------------------------------------- git


def _git(repo: Path, *arguments: str) -> str:
    environment = {
        **os.environ,
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test",
    }
    result = subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *arguments],
        cwd=repo, env=environment, capture_output=True, text=True, timeout=120, check=True,
    )
    return result.stdout


def test_apply_inside_a_checkout_requires_a_clean_grounding_root(
    tmp_path: Path, report: Path, capsys, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    grounding = repo / "data" / "grounding"
    grounding.mkdir(parents=True)
    (grounding / f"{EVIDENCE}.jsonl").write_text(EVIDENCE_TEXT, encoding="utf-8")
    (grounding / f"{BINDINGS}.jsonl").write_text(BINDINGS_TEXT, encoding="utf-8")
    (grounding / "protein_registry.jsonl").write_bytes(PROTEIN_BYTES)
    (repo / ".gitignore").write_text(f"data/grounding/{layout.LOCK_NAME}\n", encoding="utf-8")
    _git(repo, "init", "-q", ".")
    monkeypatch.setattr(migrate, "REPO_ROOT", repo)

    # Untracked: the dry run still plans, but --apply refuses.
    assert run(grounding, report) == 0
    capsys.readouterr()
    assert run(grounding, report, "--apply") == 2
    assert "has uncommitted changes" in capsys.readouterr().err
    assert (grounding / f"{EVIDENCE}.jsonl").exists()

    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "flat registries")
    (grounding / "protein_registry.jsonl").write_bytes(PROTEIN_BYTES + b"\n")
    assert run(grounding, report, "--apply") == 2
    assert "M data/grounding/protein_registry.jsonl" in capsys.readouterr().err

    _git(repo, "checkout", "--", ".")
    assert run(grounding, report, "--apply") == 0
    status = _git(repo, "status", "--porcelain", "--untracked-files=all").splitlines()
    assert sorted(line for line in status if line.startswith(" D")) == [
        f" D data/grounding/{EVIDENCE}.jsonl",
        f" D data/grounding/{BINDINGS}.jsonl",
    ]
    added = [line for line in status if line.startswith("??")]
    assert len(added) == len(status) - 2 == 2 * 4


def _committed_flat_checkout(tmp_path: Path) -> tuple[Path, Path]:
    """A throwaway repository whose HEAD holds the flat registries, as before #801."""

    repo = tmp_path / "repo"
    grounding = repo / "data" / "grounding"
    grounding.mkdir(parents=True)
    (grounding / f"{EVIDENCE}.jsonl").write_text(EVIDENCE_TEXT, encoding="utf-8")
    (grounding / f"{BINDINGS}.jsonl").write_text(BINDINGS_TEXT, encoding="utf-8")
    (grounding / "protein_registry.jsonl").write_bytes(PROTEIN_BYTES)
    (repo / ".gitignore").write_text(f"data/grounding/{layout.LOCK_NAME}\n", encoding="utf-8")
    _git(repo, "init", "-q", ".")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "flat registries")
    return repo, grounding


class _Killed(Exception):
    """Stands in for SIGKILL: the install stops dead and nothing rolls it back."""


@pytest.mark.parametrize("failure", ["post-apply-check", "killed-before-last-delete"])
def test_the_printed_recovery_returns_a_failed_migration_to_a_state_it_accepts(
    tmp_path: Path, report: Path, capsys, monkeypatch, failure: str
) -> None:
    repo, grounding = _committed_flat_checkout(tmp_path)
    monkeypatch.setattr(migrate, "REPO_ROOT", repo)
    if failure == "post-apply-check":
        # Another writer, one that ignores the lock, touches the protein registry after
        # the transaction committed; the checks fail with the install left in place.
        real_digests = migrate._unchanged_digests
        calls: list[Path] = []

        def drifted(root: Path) -> dict[str, str | None]:
            calls.append(root)
            digests = real_digests(root)
            if len(calls) > 1:
                digests["protein_registry.jsonl"] = "0" * 64
            return digests

        monkeypatch.setattr(migrate, "_unchanged_digests", drifted)
        assert run(grounding, report, "--apply") == 2
        monkeypatch.setattr(migrate, "_unchanged_digests", real_digests)
        message = capsys.readouterr().err
        assert "post-apply check(s) failed after install" in message
    else:
        def killed_before_last_delete(artifact_updates, trait_updates):
            planned, _verify = ground._plan_artifact_updates(artifact_updates)
            for path, payload in planned[:-1]:
                ground._apply_artifact_operation(path, payload)
            raise _Killed

        real_install = ground._install_promotion_transaction
        monkeypatch.setattr(ground, "_install_promotion_transaction", killed_before_last_delete)
        with pytest.raises(_Killed):
            run(grounding, report, "--apply")
        monkeypatch.setattr(ground, "_install_promotion_transaction", real_install)
        capsys.readouterr()
        assert run(grounding, report) == 2
        message = capsys.readouterr().err
        assert "refusing an ambiguous registry state" in message
    # The torn state holds untracked shard directories that `git restore` cannot remove.
    assert (grounding / f"{EVIDENCE}.jsonl.d").is_dir()
    assert (grounding / f"{BINDINGS}.jsonl.d").is_dir()

    commands = [
        shlex.split(command)
        for command in re.findall(r"`([^`]+)`", message)
        if command.startswith("git ")
    ]
    assert commands, message
    for command in commands:
        _git(repo, *command[1:])

    assert _git(repo, "status", "--porcelain", "--untracked-files=all") == ""
    assert (grounding / layout.LOCK_NAME).exists()  # gitignored, so git clean keeps it
    assert run(grounding, report) == 0
    assert run(grounding, report, "--apply") == 0
    for name, text in ((EVIDENCE, EVIDENCE_TEXT), (BINDINGS, BINDINGS_TEXT)):
        assert joined_shards(grounding / f"{name}.jsonl.d") == text.encode("utf-8")
        assert not (grounding / f"{name}.jsonl").exists()


# ---------------------------------------------------------------------- entry point


def test_script_entry_point_dry_run(root: Path, report: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "migrate_grounding_registry_layout.py"),
         "--grounding-root", str(root), "--report", str(report)],
        capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["registries"][EVIDENCE]["rows"] == 4
