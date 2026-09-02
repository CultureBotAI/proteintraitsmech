from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "fetch_source.py"
MIGRATION = ROOT / "docs" / "fetch-migration.md"
PAYLOAD = b"release-data\n"


class ReleaseHandler(BaseHTTPRequestHandler):
    retry_requests = 0
    truncated_requests = 0

    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/success")
            self.end_headers()
            return
        if self.path == "/missing":
            self.send_error(404)
            return
        if self.path == "/retry":
            type(self).retry_requests += 1
            if type(self).retry_requests == 1:
                self.send_error(503)
                return
        if self.path == "/truncated-once":
            # Dies mid-body on the first attempt only, so a fetcher that retries
            # a truncated transfer succeeds and one that does not fails (#545).
            type(self).truncated_requests += 1
            if type(self).truncated_requests == 1:
                self.send_response(200)
                self.send_header("Content-Length", str(len(PAYLOAD)))
                self.end_headers()
                self.wfile.write(PAYLOAD[:3])
                self.wfile.flush()
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
                return
        if self.path == "/html-error":
            # HTTP 200 carrying an error page: passes --min-bytes, and --sha256
            # has nothing to compare against on a first fetch.
            body = b"<html><body>Service temporarily unavailable</body></html>"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/interrupted":
            self.send_response(200)
            self.send_header("Content-Length", "100")
            self.end_headers()
            self.wfile.write(b"partial")
            self.wfile.flush()
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
            return
        if self.path == "/slow":
            time.sleep(3)
        self.send_response(200)
        self.send_header("Content-Length", str(len(PAYLOAD)))
        self.send_header("Content-Type", "text/plain")
        self.send_header("ETag", '"release-7"')
        self.send_header("Last-Modified", "Wed, 20 Aug 2025 12:00:00 GMT")
        self.end_headers()
        try:
            self.wfile.write(PAYLOAD)
        except BrokenPipeError:
            pass

    def log_message(self, _format, *_args):
        pass


@pytest.fixture()
def release_server():
    ReleaseHandler.retry_requests = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), ReleaseHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def run_fetch(url: str, destination: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), url, str(destination), *args],
        capture_output=True,
        text=True,
    )


def _load_module():
    """The fetcher imported in-process, for tests that inspect its internals."""
    spec = importlib.util.spec_from_file_location("fetch_source", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pytestmark = pytest.mark.skipif(shutil.which("curl") is None, reason="curl is not installed")


def test_success_records_release_metadata(release_server, tmp_path):
    destination = tmp_path / "release.txt"
    digest = hashlib.sha256(PAYLOAD).hexdigest()
    result = run_fetch(
        f"{release_server}/redirect",
        destination,
        "--sha256",
        digest,
        "--contains",
        "release-data",
    )
    assert result.returncode == 0, result.stderr
    assert destination.read_bytes() == PAYLOAD
    assert stat.S_IMODE(destination.stat().st_mode) == 0o644
    metadata = json.loads(Path(f"{destination}.fetch.json").read_text())
    assert stat.S_IMODE(Path(f"{destination}.fetch.json").stat().st_mode) == 0o644
    assert metadata["sha256"] == digest
    assert metadata["etag"] == '"release-7"'
    assert metadata["last_modified"] == "Wed, 20 Aug 2025 12:00:00 GMT"
    assert metadata["requested_url"] == f"{release_server}/redirect"
    assert metadata["resolved_url"] == f"{release_server}/success"


def test_transient_http_failure_is_retried(release_server, tmp_path):
    destination = tmp_path / "release.txt"
    result = run_fetch(
        f"{release_server}/retry",
        destination,
        "--retries",
        "2",
        "--retry-delay",
        "0",
    )
    assert result.returncode == 0, result.stderr
    assert ReleaseHandler.retry_requests == 2
    assert destination.read_bytes() == PAYLOAD


def test_total_timeout_bounds_all_retry_attempts(release_server, tmp_path):
    destination = tmp_path / "release.txt"
    started = time.monotonic()
    result = run_fetch(
        f"{release_server}/slow",
        destination,
        "--max-time",
        "1",
        "--retries",
        "4",
        "--retry-delay",
        "0",
    )
    elapsed = time.monotonic() - started
    assert result.returncode == 1
    assert elapsed < 2.5
    assert "total download timeout" in result.stderr
    assert not destination.exists()
    assert list(tmp_path.iterdir()) == []


def test_successful_replacement_preserves_existing_mode(release_server, tmp_path):
    destination = tmp_path / "release.txt"
    destination.write_text("old", encoding="utf-8")
    destination.chmod(0o640)

    result = run_fetch(f"{release_server}/success", destination)

    assert result.returncode == 0, result.stderr
    assert destination.read_bytes() == PAYLOAD
    assert stat.S_IMODE(destination.stat().st_mode) == 0o640


@pytest.mark.parametrize(
    ("endpoint", "validation"),
    [
        ("missing", ()),
        ("interrupted", ()),
        ("success", ("--min-bytes", "1000")),
        ("success", ("--contains", "not-in-release")),
        ("success", ("--sha256", "0" * 64)),
    ],
)
def test_failure_preserves_existing_release_and_cleans_temps(
    release_server, tmp_path, endpoint, validation
):
    destination = tmp_path / "release.txt"
    metadata = Path(f"{destination}.fetch.json")
    destination.write_text("known-good\n", encoding="utf-8")
    metadata.write_text('{"known": "good"}\n', encoding="utf-8")
    result = run_fetch(
        f"{release_server}/{endpoint}",
        destination,
        "--retries",
        "0",
        *validation,
    )
    assert result.returncode == 1
    assert destination.read_text(encoding="utf-8") == "known-good\n"
    assert json.loads(metadata.read_text()) == {"known": "good"}
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "release.txt",
        "release.txt.fetch.json",
    ]


def test_dry_run_does_not_create_or_contact_destination(tmp_path):
    destination = tmp_path / "release.txt"
    result = run_fetch("http://127.0.0.1:1/unreachable", destination, "--dry-run")
    assert result.returncode == 0
    assert json.loads(result.stdout)["destination"] == str(destination)
    assert json.loads(result.stdout)["transport"]["max_time"] == 300
    assert not destination.exists()


def test_migration_checklist_accounts_for_every_fetch_recipe():
    recipes = set(
        re.findall(r"^(fetch-[A-Za-z0-9_-]+)(?:\s+[^:]*)?:$", (ROOT / "justfile").read_text(), re.M)
    )
    documented = set(re.findall(r"`(fetch-[A-Za-z0-9_-]+)`", MIGRATION.read_text()))
    assert documented == recipes


def test_a_truncated_transfer_is_retried_and_succeeds(release_server, tmp_path):
    """curl does not retry a transfer that dies mid-body (#545).

    A server closing early gives exit 18 (CURLE_PARTIAL_FILE) and a reset gives
    56; neither is in curl's transient set, so `--retry` never fires for the
    failure mode that bites hardest on the largest files. Measured before the
    fix: one attempt, immediate failure.

    Asserts the fetch *succeeds*, not merely that it retried -- the destination
    must hold the whole payload rather than the first attempt's three bytes,
    which is also what proves curl truncates its output on retry, not appends.
    """
    ReleaseHandler.truncated_requests = 0
    destination = tmp_path / "release.txt"

    result = run_fetch(f"{release_server}/truncated-once", destination, "--retries", "2")

    assert result.returncode == 0, result.stderr
    assert destination.read_bytes() == PAYLOAD
    assert ReleaseHandler.truncated_requests >= 2, "the truncated attempt was not retried"


def test_a_200_carrying_an_html_error_page_is_refused(release_server, tmp_path):
    """The #455 shape: a cached null that looked like an absent mapping (#545).

    Distinct from --min-bytes and --sha256, which do fire: an error page is
    comfortably over one byte, and a first fetch has no digest to compare
    against. Eight migrated call sites have no other content check at all.
    """
    destination = tmp_path / "release.txt"
    destination.write_bytes(b"previous release\n")

    result = run_fetch(f"{release_server}/html-error", destination, "--retries", "0")

    assert result.returncode != 0
    assert "error page rather than a release" in result.stderr
    assert destination.read_bytes() == b"previous release\n", "the error page was installed"
    assert not list(destination.parent.glob(".*.part")), "a temp file leaked"


def test_html_is_accepted_when_the_caller_says_the_source_serves_it(release_server, tmp_path):
    """The guard is a default, not a prohibition.

    No migrated call site fetches HTML today, which is what makes rejecting it a
    safe default -- but a source that genuinely serves HTML must stay fetchable
    without disabling every other check.
    """
    destination = tmp_path / "page.html"

    result = run_fetch(
        f"{release_server}/html-error", destination, "--retries", "0", "--allow-html"
    )

    assert result.returncode == 0, result.stderr
    assert destination.read_bytes().startswith(b"<html>")
    sidecar = json.loads(Path(f"{destination}.fetch.json").read_text(encoding="utf-8"))
    assert sidecar["content_type"].startswith("text/html")


@pytest.mark.parametrize(
    "value,rejected",
    [
        ("text/html", True),
        ("text/html; charset=utf-8", True),
        ("TEXT/HTML", True),
        ("application/xhtml+xml", True),
        ("text/plain", False),
        ("application/gzip", False),
        ("", False),
    ],
)
def test_content_type_matching_ignores_parameters_and_case(value, rejected):
    """A bare `== "text/html"` would miss the form servers actually send."""
    assert _load_module()._is_rejected_content_type(value) is rejected


def test_truncation_retries_share_one_deadline_rather_than_multiplying_it(monkeypatch, tmp_path):
    """Retrying must not multiply the ceiling SKILL.md promises (#545).

    That document states "a wall-clock deadline for the complete curl process,
    including retries and delays". Giving each truncation attempt its own
    --max-time would make it (retries + 1) x the stated number -- the defect
    #545 raises against curl's own --retry-max-time, no better for being
    reintroduced in Python.

    Asserted on the timeout actually handed to each attempt, not on elapsed wall
    clock. Two earlier wall-clock versions of this test passed against the
    mutation: `/interrupted` fails instantly so it bounded only the backoff, and
    a slow endpoint makes curl hit its OWN --max-time and exit 28, which is not
    a truncation code, so the retry never fired at all.
    """
    module = _load_module()
    timeouts: list[float] = []

    def fake_run(_command, **kwargs):
        timeouts.append(kwargs["timeout"])
        return subprocess.CompletedProcess(args=_command, returncode=18, stdout="", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    with pytest.raises(module.FetchError, match="truncated attempts"):
        module.fetch(
            "http://example.invalid/release", tmp_path / "release.txt", max_time=30, retries=3
        )

    assert len(timeouts) == 4, "a truncated transfer was not retried to exhaustion"
    assert timeouts[0] <= 30
    assert all(later <= earlier for earlier, later in zip(timeouts, timeouts[1:])), timeouts
    assert timeouts[-1] < 30, "each attempt got a fresh budget instead of sharing one"
