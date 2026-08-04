"""Docs claims that a test can check, checked.

`CLAUDE.md` is loaded into context at the start of every session, so a stale statement
there is read by every agent working in this repo before it reads anything else. That
makes it the worst place in the tree for a list to drift.

The prompts list has gone stale **twice in one day**: #130 added
`prompts/has-graph-hardening.md` without listing it, and #133 added two more the moment
after. Both times the fix was to notice by hand and patch it, and the second time the
mitigation proposed was to tell the next runner to re-verify — which is not a gate, it
is the ambient-red problem #107 existed to remove.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLAUDE_MD = ROOT / "CLAUDE.md"
PROMPTS = ROOT / "prompts"


def _listed_in_claude_md() -> set[str]:
    return set(re.findall(r"prompts/([A-Za-z0-9._-]+\.md)", CLAUDE_MD.read_text(encoding="utf-8")))


def test_claude_md_lists_every_prompt():
    """Every file in prompts/ must appear in CLAUDE.md.

    A prompt nobody can find is a prompt nobody runs — which was the whole point of
    #129, the PR that added the list.
    """
    on_disk = {p.name for p in PROMPTS.glob("*.md")}
    missing = on_disk - _listed_in_claude_md()
    assert not missing, (
        "these prompts exist but CLAUDE.md does not mention them: " + ", ".join(sorted(missing)))


def test_claude_md_lists_no_prompt_that_is_gone():
    """The other direction: a rename or deletion must not leave a dangling reference.

    #126 renamed `prompts/goal.md` to `prompts/backlog-loop-goal.md`; nothing then
    pointed at the old name, but nothing would have caught it if something had.
    """
    on_disk = {p.name for p in PROMPTS.glob("*.md")}
    dangling = _listed_in_claude_md() - on_disk
    assert not dangling, (
        "CLAUDE.md points at prompts that do not exist: " + ", ".join(sorted(dangling)))


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
