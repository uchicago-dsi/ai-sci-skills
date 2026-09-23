#!/usr/bin/env python3
"""Block a reply that contains the padding CLAUDE.md bans, and say which.

Instructions alone have not worked. The style rules in CLAUDE.md are clear
and were violated repeatedly in a single session -- "in a way that matters",
"worth flagging", "measured rather than assumed" -- by an agent that had the
file in context the whole time. A rule with no feedback loop competes with
every other rule for attention and loses.

This is the loop. It reads the reply about to be sent, matches the banned
patterns, and refuses the stop so the reply is rewritten before Anna sees it.
The agent is told exactly which phrases matched, so the fix is mechanical.

Code blocks are exempt. Quoting a banned phrase to say it is banned is the
one place the phrase belongs, and a linter that cannot tell use from mention
fires on its own documentation -- which is how this exemption was found.

Two deliberate limits.

It only catches patterns that are almost always padding. Judgement calls --
whether a contrast is genuinely load-bearing, whether a caveat is a caveat or
narration -- are left to the agent, because a linter that fires on legitimate
prose teaches people to route around it.

It never blocks twice on the same reply. The harness sets stop_hook_active
when it is already re-running after a block; honouring that is what keeps a
disagreement between linter and model from becoming an infinite loop.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hookio import allow, block_stop, payload  # noqa: E402

# Each entry: a compiled pattern and what to do instead. Patterns are chosen
# to be near-zero false positive; anything arguable belongs in CLAUDE.md as
# guidance, not here as a block.
RULES = [
    (r"\bin a way that matters\b", "cut it"),
    (r"\bworth (?:noting|flagging|knowing|mentioning|naming|stating|your attention)\b",
     "cut the flag and state the thing"),
    (r"\b(?:it'?s|that'?s|this is) worth\b", "cut the flag and state the thing"),
    (r"\b(?:Notably|Crucially|Importantly|Significantly)\b", "cut the adverb"),
    (r"\b(?:stands?|stood) out\b", "just say it"),
    (r"\bto be honest\b", "cut it"),
    (r"\blet me be (?:direct|clear|honest)\b", "cut it"),
    (r"\bI (?:should|want to|need to) (?:say|flag|note|admit|correct)\b",
     "say the thing, or make the correction"),
    (r"\bI need to correct something\b", "make the correction and continue"),
    (r"\bno errors,? no warnings\b", "say what passed, or say nothing"),
    (r"\b(?:carefully|thoroughly|properly) (?:checked|verified|tested|reviewed)\b",
     "drop the adverb"),
    # Contrastive padding. Restricted to the forms that are almost never
    # load-bearing: the inferior alternative is named right after the verb.
    (r"\b(?:measured|verified|checked|tested|computed|derived|fixed)\s+"
     r"rather than\s+(?:assum\w+|guess\w+|estimat\w+|inferr\w+|speculat\w+)",
     "drop the 'rather than' clause"),
    (r"\brather than (?:silently )?(?:omitt\w+|ignor\w+|assum\w+|guess\w+)\b",
     "drop the 'rather than' clause"),
    (r"\bnot (?:a guess|an assumption|speculation)\b", "drop it"),
    (r"\ba (?:measurement|finding|result) rather than\b", "drop the contrast"),
]
COMPILED = [(re.compile(p, re.IGNORECASE), fix) for p, fix in RULES]


def prose_only(text):
    """The reply with code stripped, so a quoted example is not a violation.

    Fenced blocks and inline spans are where a phrase gets named rather than
    used: a table of banned wording, a diff, a log line. Replacing them with
    blank lines rather than deleting them keeps the rest of the text intact.
    """
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else re.sub(r"`[^`]*`", " ", line))
    return "\n".join(out)


def last_assistant_text(transcript_path):
    """The text of the reply about to be sent, from the transcript tail."""
    try:
        with open(transcript_path, encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError:
        return ""
    for line in reversed(lines):
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get("type") != "assistant":
            continue
        content = (record.get("message") or {}).get("content") or []
        if isinstance(content, str):
            return content
        return "\n".join(part.get("text", "") for part in content
                         if isinstance(part, dict) and part.get("type") == "text")
    return ""


def main():
    event = payload()
    # Already re-running after a block. Letting it through beats looping.
    if event.get("stop_hook_active"):
        allow()

    text = prose_only(last_assistant_text(event.get("transcript_path", "")))
    if not text.strip():
        allow()

    hits = []
    for pattern, fix in COMPILED:
        for match in pattern.finditer(text):
            hits.append((match.group(0).strip(), fix))
            break  # one report per rule is enough to prompt a pass
    if not hits:
        allow()

    report = ["CLAUDE.md prose rules: %d banned pattern(s) in this reply. "
              "Rewrite it and send again." % len(hits)]
    for phrase, fix in hits:
        report.append("  %-42s -> %s" % ('"%s"' % phrase, fix))
    report.append("These are the ones with near-zero false positives. While "
                  "rewriting, also check the judgement calls the linter "
                  "cannot: contrasts naming an alternative nobody proposed, "
                  "and sentences whose subject is your own candour or "
                  "thoroughness.")
    block_stop("\n".join(report))


if __name__ == "__main__":
    main()
