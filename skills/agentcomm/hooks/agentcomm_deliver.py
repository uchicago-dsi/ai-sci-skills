#!/usr/bin/env python3
"""Deliver peer mail into the agent's context, and consume it in the same step.

Written for the oldest interpreter a hook may be handed. A hook runs in
whatever shell the harness gives it, which here is a system python3 that
predates variable annotations, so this file uses none; depending on a newer
interpreter would make the hook fail silently and put us back where we
started.

The problem this solves is not that agents forget to read mail. It is that
reading and being told there is mail were two different actions, and only the
second was automated. A hook that previews leaves the unread count and the
last-read stamp untouched, so peers watching those two numbers see an agent
that has never read anything, and reasonably conclude their message did not
land. That cost two round trips in one day, and once cost real work: a peer
killed two processes, said so by mail, and the mail sat in a mailbox this
session was not attached to while the processes were relaunched.

So this consumes. The `agentcomm` skill forbids a hook from consuming, and
the reason it gives is sound: a hook that archived mail would destroy
messages the agent never saw. That reasoning holds only for a hook that
discards what it read. This one prints every body to stdout, and the harness
puts stdout into the conversation, so consuming here means the message has
been delivered to the only place that counts. Nothing is lost that a preview
would have preserved.

Two safeguards, because the failure mode of getting this wrong is silent
message loss:

Bodies are printed before anything else happens, and printing is the last
thing that can fail. `agentcomm inbox` itself prints before archiving, so an
interrupted read costs a duplicate rather than a message.

An identity is never guessed. If no name is configured this prints how to set
one and consumes nothing, because binding the wrong name would read another
agent's mail and hide it from them.

This is Claude-specific wiring. Codex resolves hooks through its own
`/hooks` trust flow and a different configuration file, and its digest
events are not these events, so a Codex session needs the equivalent set up
on its own terms rather than this file.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

AGENTCOMM = Path.home() / ".local" / "bin" / "agentcomm"
IDENTITY_MAP = Path.home() / ".claude" / "agentcomm_identity.json"
STAMP_DIR = Path.home() / ".claude" / ".agentcomm_stamps"
# Mid-turn delivery is rate limited; prompt and session start are not, because
# those are boundaries where the cost of a check is negligible and the cost of
# missing steering is a wasted turn.
MIDTURN_INTERVAL_SECONDS = 60


def configured_identity(cwd):
    """The name this session should bind, from the environment or the map.

    Never inferred from the directory alone when the environment disagrees:
    two Claude sessions in one repository would otherwise claim one name and
    silently consume each other's mail.
    """
    from_env = os.environ.get("AGENTCOMM_AGENT")
    if from_env:
        return from_env
    if not IDENTITY_MAP.is_file():
        return None
    try:
        mapping = json.loads(IDENTITY_MAP.read_text())
    except (ValueError, OSError):
        return None
    best = None
    for prefix, name in mapping.get("by_directory", {}).items():
        # Longest matching prefix wins, so a worktree can override its parent.
        if cwd.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
            best = (prefix, name)
    return best[1] if best else mapping.get("default")


def run(args, name):
    """Call agentcomm, capturing output without newer subprocess keywords.

    capture_output and text arrive in 3.7, and the interpreter a hook is
    handed here is older than that. Spelling it out with PIPE keeps the hook
    working on the oldest python on PATH instead of failing in a way only a
    hook log would show.
    """
    environment = dict(os.environ, AGENTCOMM_AGENT=name)
    command = [str(AGENTCOMM)] + list(args)
    try:
        done = subprocess.run(command, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=25,
                              env=environment)
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    return done.returncode, done.stdout.decode("utf-8", "replace")


def deliver(name):
    """Consume the inbox and render it for the conversation."""
    code, raw = run(["inbox", "--json"], name)
    if code != 0 or not raw.strip():
        return ""
    try:
        payload = json.loads(raw)
    except ValueError:
        # Unparseable output is still delivered verbatim rather than dropped:
        # the mail is already archived by this point.
        return raw.strip()
    messages = payload if isinstance(payload, list) else payload.get("messages", [])
    if not messages:
        return ""
    lines = ["AGENTCOMM: %d message(s) delivered to %s and now marked read."
             % (len(messages), name)]
    for message in messages:
        lines.append("")
        lines.append("--- from %s | %s | %s"
                     % (message.get("from", "?"), message.get("subject", "(no subject)"),
                        message.get("ts", "")))
        lines.append((message.get("body") or "").strip())
    return "\n".join(lines)


def rate_limited(event):
    """True when this event fired too recently to be worth repeating."""
    if event != "midturn":
        return False
    STAMP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = STAMP_DIR / "midturn"
    now = time.time()
    try:
        if stamp.is_file() and now - stamp.stat().st_mtime < MIDTURN_INTERVAL_SECONDS:
            return True
    except OSError:
        return False
    try:
        stamp.touch()
    except OSError:
        pass
    return False


def main():
    event = sys.argv[1] if len(sys.argv) > 1 else "prompt"
    if not AGENTCOMM.is_file():
        return 0
    if rate_limited(event):
        return 0

    cwd = os.getcwd()
    name = configured_identity(cwd)
    if not name:
        if event == "session-start":
            print("AGENTCOMM: no identity for this session, so peer mail is NOT "
                  "being delivered and none has been consumed. Set "
                  "AGENTCOMM_AGENT, or add this directory to "
                  "~/.claude/agentcomm_identity.json under by_directory. Do not "
                  "bind a name another live agent is using.")
        return 0

    # Registering every time is a heartbeat as well as a bind: `agents` reports
    # how long ago each name last consumed, and peers steer on that number.
    run(["register", "--as", name], name)
    rendered = deliver(name)
    if rendered:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
