# humanize

Edits prose so it sounds like the author and reads plainly. `SKILL.md` is what
the agent reads; `registers/` holds the rules that differ between a talk, a
journal paper, a design document and the rest.

## Helper agent

`agents/humanize-auditor.md` is a read-only reviewer the skill hands a first
pass to, so the edit starts from a reading that is not anchored on the
editor's own. In Claude Code it is the `humanize-auditor` subagent, or
`humanize:humanize-auditor` when the skill is installed as a plugin.

## US-spelling commit guard

`hooks/guard_american_spelling.py` refuses a `git commit` that adds British
spellings to prose, comments, docstrings or string literals, and names the
American form. Identifiers, paths and anything in backticks are exempt; the
word list is in `hooks/british_spelling.py`. It acts in every repository, so it
is off until you turn it on; [`../../hooks/README.md`](../../hooks/README.md)
says how.
