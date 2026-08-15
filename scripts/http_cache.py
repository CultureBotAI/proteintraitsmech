#!/usr/bin/env python3
r"""One cached GET-JSON client, for every script that talks to a public API.

WHY THIS EXISTS AS A MODULE
---------------------------
`build_sequence_structure_alignment` had the only implementation, embedded. #445 needed
the same thing for the InterPro entry API and the obvious move was to write a second one
-- which is the mistake this repo documents more than any other. `interpro_text`'s header
counts three copies of one cleaner that had already diverged; `yaml_emit`'s counts ten of
`yaml_escape` and twenty-eight of `slugify`; `record_io` exists because five builders
reimplemented two operations and four of the six defects in one PR were instances of
getting one of them wrong.

WHAT A CACHE IS FOR HERE, AND WHAT IT IS NOT
---------------------------------------------
`data/raw/` is gitignored, so nothing fetched is committed -- the corpus is rebuilt from
sources, not from checked-in copies of them. That applies to a 300 MB release tarball and
to 209 REST calls alike; neither belongs in git. The cache is what makes the second kind
as cheap to re-materialise as the first: a re-run costs nothing for what it already has.

It is NOT a provenance record. A cached response is a copy of what a service said once,
and the service can change its mind. Anything that needs the text to be reproducible for
audit has to say where it came from IN THE RECORD -- which is what `definition_source`
does -- not rely on a cache still being there.

TRANSIENT FAILURES ARE NOT CACHED, and that distinction is the whole design
---------------------------------------------------------------------------
The original cached every miss as `null`, including timeouts, with the comment
"misses/404s are cached as null so absent mappings aren't re-fetched". For a 404 that is
right: the resource does not exist and asking again is waste. For a timeout it is
poisoning -- one flaky minute becomes a permanent hole that looks exactly like an absent
mapping, and no later run can tell them apart.

So `get()` distinguishes them:

  * 404              -> cached as None. Asked once, absent for good.
  * timeout / 5xx    -> NOT cached, and reported. The next run retries it.

`cache_missing_as_none=True` restores the old behaviour byte for byte, because
`build_sequence_structure_alignment` has a 34k-entry cache on disk built under it and
changing what a null means would silently re-query or silently skip.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


class TransientHttpError(RuntimeError):
    """A failure worth retrying: timeout, connection reset, 5xx.

    Distinguished from "absent" so a caller can refuse to write a partial artefact rather
    than treat a flaky network as an empty result.
    """


class Http:
    """Cached GET-JSON client. Caches per URL to a JSON file so re-runs and partial runs
    do not re-query.

    Flush often: the cache is only useful across runs if it survives one being killed.
    """

    def __init__(self, cache_path: Path, sleep: float = 0.2,
                 user_agent: str = "ProteinTraitsMech/1.0",
                 cache_missing_as_none: bool = True):
        self.cache_path = Path(cache_path)
        self.sleep = sleep
        self.user_agent = user_agent
        self.cache_missing_as_none = cache_missing_as_none
        self.cache: dict = {}
        self.dirty = self.hits = self.misses = self.errors = 0
        if self.cache_path.exists():
            try:
                self.cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                # A truncated cache is a performance problem, not a correctness one:
                # every entry is re-fetchable by construction.
                self.cache = {}

    def get(self, url: str, timeout: int = 30, strict: bool = False):
        """The parsed JSON, or None when the resource is absent (404).

        `strict=True` raises `TransientHttpError` instead of returning None for a failure
        that is not a 404, so a caller assembling a complete artefact can stop rather than
        write a hole. Default False keeps the original best-effort behaviour.
        """
        if url in self.cache:
            self.hits += 1
            return self.cache[url]
        self.misses += 1
        val = None
        transient = None
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/json",
                              "User-Agent": self.user_agent})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                val = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                pass                                   # absent: cache it below
            else:
                transient = f"http {exc.code}"
        except (urllib.error.URLError, ValueError, TimeoutError, OSError) as exc:
            transient = f"{type(exc).__name__}: {exc}"

        if transient:
            self.errors += 1
            if self.sleep:
                time.sleep(self.sleep)
            if strict:
                raise TransientHttpError(f"{transient}: {url}")
            print(f"  http err: {url} ({transient})", file=sys.stderr)
            # NOT cached. A timeout must not become a permanent "absent".
            return None

        if val is not None or self.cache_missing_as_none:
            self.cache[url] = val
            self.dirty += 1
        if self.sleep:
            time.sleep(self.sleep)
        return val

    def flush(self) -> None:
        if self.dirty:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self.cache), encoding="utf-8")
            self.dirty = 0
