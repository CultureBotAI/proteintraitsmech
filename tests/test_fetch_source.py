from __future__ import annotations

import hashlib
import json
import re
import shutil
import socket
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "fetch_source.py"
MIGRATION = ROOT / "docs" / "fetch-migration.md"
PAYLOAD = b"release-data\n"


class ReleaseHandler(BaseHTTPRequestHandler):
    retry_requests = 0

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
        if self.path == "/interrupted":
            self.send_response(200)
            self.send_header("Content-Length", "100")
            self.end_headers()
            self.wfile.write(b"partial")
            self.wfile.flush()
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
            return
        self.send_response(200)
        self.send_header("Content-Length", str(len(PAYLOAD)))
        self.send_header("Content-Type", "text/plain")
        self.send_header("ETag", '"release-7"')
        self.send_header("Last-Modified", "Wed, 20 Aug 2025 12:00:00 GMT")
        self.end_headers()
        self.wfile.write(PAYLOAD)

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
    metadata = json.loads(Path(f"{destination}.fetch.json").read_text())
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
    assert not destination.exists()


def test_migration_checklist_accounts_for_every_fetch_recipe():
    recipes = set(
        re.findall(r"^(fetch-[A-Za-z0-9_-]+)(?:\s+[^:]*)?:$", (ROOT / "justfile").read_text(), re.M)
    )
    documented = set(re.findall(r"`(fetch-[A-Za-z0-9_-]+)`", MIGRATION.read_text()))
    assert documented == recipes
