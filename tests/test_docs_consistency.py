"""Docs claims that a test can check, checked.

`CLAUDE.md` is loaded into context at the start of every session, so stale statements
there shape work before an agent reads code. Mutable metrics live behind
`just corpus-stats`; stable catalogs and path claims are checked here.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLAUDE_MD = ROOT / "CLAUDE.md"
PROMPTS = ROOT / "prompts"
PROMPTS_README = PROMPTS / "README.md"


def _listed_in_prompt_catalog() -> set[str]:
    return set(
        re.findall(
            r"^- `([A-Za-z0-9._-]+\.md)`",
            PROMPTS_README.read_text(encoding="utf-8"),
            re.M,
        )
    )


def test_prompt_catalog_lists_every_prompt():
    """Every prompt must appear in prompts/README.md.

    A prompt nobody can find is a prompt nobody runs — which was the whole point of
    #129, the PR that added the list.
    """
    on_disk = {p.name for p in PROMPTS.glob("*.md") if p != PROMPTS_README}
    missing = on_disk - _listed_in_prompt_catalog()
    assert not missing, (
        "these prompts exist but prompts/README.md does not mention them: "
        + ", ".join(sorted(missing)))


def test_prompt_catalog_lists_no_prompt_that_is_gone():
    """The other direction: a rename or deletion must not leave a dangling reference.

    #126 renamed `prompts/goal.md` to `prompts/backlog-loop-goal.md`; nothing then
    pointed at the old name, but nothing would have caught it if something had.
    """
    on_disk = {p.name for p in PROMPTS.glob("*.md") if p != PROMPTS_README}
    dangling = _listed_in_prompt_catalog() - on_disk
    assert not dangling, (
        "prompts/README.md points at prompts that do not exist: "
        + ", ".join(sorted(dangling)))


def test_no_prompt_is_wrapped_as_a_skill():
    """#126 deleted `.claude/skills/goal/` because it SHADOWED the native `/goal`.

    Both that PR and `prompts/backlog-loop-goal.md` say in words that such a wrapper
    should be deleted rather than repointed if it reappears. This is that instruction
    as a check, since the failure mode is silent: a custom command of the same name
    simply wins, and the prompt stops being what runs.
    """
    skills = ROOT / ".claude" / "skills"
    if not skills.is_dir():
        return
    offenders = []
    for skill in skills.iterdir():
        f = skill / "SKILL.md"
        if f.is_file() and re.search(r"prompts/[A-Za-z0-9._-]+\.md", f.read_text(encoding="utf-8")):
            offenders.append(skill.name)
    assert not offenders, (
        "these skills wrap a prompt, which #126 removed on purpose — delete them rather "
        "than repointing: " + ", ".join(sorted(offenders)))


def test_every_prompt_says_how_it_is_used():
    """#117: a reader must be able to tell what kind of document they are holding.

    `prompts/` mixes three kinds — a live workflow that picks its own target, scoped
    runs that are spent once executed, and one meant for an *independent* reviewer
    rather than for the agent reading it. Confusing the last for the first is the
    expensive mistake: `schema-review.md` says explicitly not to make code changes.

    Gated rather than documented, for the same reason as the list above: the prompts
    list went stale twice while the mitigation was "remember to check".
    """
    missing = [p.name for p in PROMPTS.glob("*.md") if p != PROMPTS_README
               if not p.read_text(encoding="utf-8").split("\n\n")[1].startswith("**Use:**")]
    assert not missing, (
        "these prompts do not open with a `**Use:**` line: " + ", ".join(sorted(missing)))


def test_a_spent_prompt_names_the_issues_it_closed():
    """A spent marker must cite something DURABLE and checkable.

    It used to require `Executed as #NNN`, naming the PR. That was worse than useless:
    the check verified the *pattern*, not the number, so a wrong PR passed silently —
    and writing the marker means naming a PR that does not exist yet, so I guessed one
    and happened to be right (#137).

    The issues a prompt closed are the durable fact, are decided before the marker is
    written, and are verifiable by anyone in one click. Which PR carried them is in
    `git log`, where it cannot go stale.
    """
    import re
    bad = []
    for p in PROMPTS.glob("*.md"):
        if p == PROMPTS_README:
            continue
        use = p.read_text(encoding="utf-8").split("\n\n")[1]
        if "spent" in use and not re.search(r"closed #\d+", use):
            bad.append(p.name)
    assert not bad, f"these say 'spent' without naming the issues they closed: {bad}"


def test_no_prompt_claims_a_pull_request_number():
    """Guards the specific mistake #137 recorded, so it cannot come back.

    A `Use:` line naming a PR is unverifiable at the moment it is written — the PR does
    not exist yet — and nothing downstream can tell a wrong number from a right one.
    """
    import re
    bad = [p.name for p in PROMPTS.glob("*.md") if p != PROMPTS_README
           if re.search(r"Executed as #\d+", p.read_text(encoding="utf-8").split("\n\n")[1])]
    assert not bad, (
        "these cite a PR number in their Use line, which cannot be verified when written: "
        + ", ".join(sorted(bad)))


def test_claude_md_routes_every_tracked_skill_exactly_once():
    skill_root = ROOT / ".claude" / "skills"
    on_disk = {path.parent.name for path in skill_root.glob("*/SKILL.md")}
    listed = re.findall(r"\.claude/skills/([a-z0-9-]+)/SKILL\.md", CLAUDE_MD.read_text())
    assert set(listed) == on_disk
    assert len(listed) == len(set(listed)), "CLAUDE.md lists a skill more than once"


def test_documented_axis_paths_match_the_repository_contract():
    expected = {"sequence", "structure", "sequence_structure", "function", "evolution"}
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    claude = CLAUDE_MD.read_text(encoding="utf-8")
    for axis in expected:
        assert f"data/traits/{axis}/" in claude
        assert f"{axis}/<category>/<slug>.yaml" in readme
    assert "mixed/<category>/<slug>.yaml" not in readme
    assert "gitignored, regenerable upstream downloads" in readme

    # Sparse developer worktrees may omit data/traits. A normal checkout and CI include
    # it, where this catches a documented axis whose live path disappeared.
    traits = ROOT / "data" / "traits"
    if traits.is_dir():
        missing = {axis for axis in expected if not (traits / axis).is_dir()}
        assert not missing, f"documented axis paths missing on disk: {sorted(missing)}"


def test_startup_guidance_contains_no_point_in_time_corpus_claims():
    claude = CLAUDE_MD.read_text(encoding="utf-8")
    skill_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / ".claude" / "skills").glob("*/SKILL.md")
    )
    assert "just corpus-stats" in claude
    for stale in ("~200,600", "**0 records**", "currently unpopulated"):
        assert stale not in claude
        assert stale not in skill_text


def test_browser_guidance_matches_lazy_axis_and_detail_loading():
    claude = CLAUDE_MD.read_text(encoding="utf-8")
    builder = (ROOT / "scripts" / "build_docs_index.py").read_text(encoding="utf-8")
    browser = (ROOT / "docs" / "browse.js").read_text(encoding="utf-8")
    assert "lazily by axis" in claude
    assert "bucketed detail sidecar" in claude
    assert "fetches lean record shards lazily" in builder
    assert "function loadAxis(axis)" in browser
    assert "function loadDetail" in browser
