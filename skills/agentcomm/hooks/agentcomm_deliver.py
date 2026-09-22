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
# One file per bound name, recording which session holds it. This is what makes
# the directory map safe when two agents run in one tree: the directory says
# which name a session *wants*, and the claim says whether it may have it.
CLAIM_DIR = Path.home() / ".claude" / ".agentcomm_claims"
# How long a claim survives without a heartbeat. A session that has gone away
# should not hold a name forever, and every hook event refreshes the claim, so
# a live session renews far more often than this.
CLAIM_STALE_SECONDS = 6 * 60 * 60
# Mid-turn delivery is rate limited; prompt and session start are not, because
# those are boundaries where the cost of a check is negligible and the cost of
# missing steering is a wasted turn.
MIDTURN_INTERVAL_SECONDS = 60


def configured_identity(cwd, session_id=None):
    """The name this session should bind, from the environment or the map.

    Never inferred from the directory alone when the environment disagrees:
    two Claude sessions in one repository would otherwise claim one name and
    silently consume each other's mail.

    `by_session` keys on the harness session id and is checked before
    `by_directory`, because several agents commonly run from one checkout and
    the directory then identifies none of them. The session id is the only
    discriminator that survives that arrangement without relying on each
    session having been launched with the right environment.
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
    if session_id:
        by_session = mapping.get("by_session", {}).get(session_id)
        if by_session:
            return by_session
    best = None
    for prefix, name in mapping.get("by_directory", {}).items():
        # Longest matching prefix wins, so a worktree can override its parent.
        if cwd.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
            best = (prefix, name)
    return best[1] if best else mapping.get("default")


def claim_name(name, session_id, cwd):
    """Take the name for this session, or report the session already holding it.

    Returns None when the name is ours to use. A name belongs to one session at a
    time: the first to claim it keeps it while it keeps checking in, and any other
    session is refused rather than quietly reading its mail.

    This is what makes `by_directory` safe to keep. Two agents started in the same
    checkout resolve to the same name, and without this the second consumes the
    first's inbox and hides it, which no counter afterwards can reveal. That
    happened twice here in one day. `by_session` prevents it when someone has
    configured it; this prevents it when nobody has.

    A session that cannot be identified is refused rather than allowed to share,
    because an unidentifiable session is exactly the one that cannot be shown to
    be the rightful holder.
    """
    if not session_id:
        return {"session_id": "(unidentifiable session)", "cwd": cwd}
    try:
        CLAIM_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Without somewhere to record claims this cannot enforce anything, and
        # blocking delivery on a filesystem problem would be its own failure.
        return None
    path = CLAIM_DIR / (str(name).replace("/", "_") + ".json")
    now = time.time()
    held = None
    if path.is_file():
        try:
            held = json.loads(path.read_text())
        except (ValueError, OSError):
            held = None
    if (held and held.get("session_id") and held.get("session_id") != session_id
            and now - float(held.get("last_seen", 0)) < CLAIM_STALE_SECONDS):
        return held
    try:
        path.write_text(json.dumps(
            {"session_id": session_id, "cwd": cwd, "name": name, "last_seen": now},
            indent=2) + "\n")
    except OSError:
        pass
    return None


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

    # The harness passes the event payload on stdin. It carries the session id,
    # which is what tells two agents in one checkout apart. A hook that cannot
    # read it still works; it just falls back to the directory.
    session_id = None
    try:
        if not sys.stdin.isatty():
            session_id = (json.loads(sys.stdin.read() or "{}") or {}).get("session_id")
    except (ValueError, OSError):
        session_id = None

    cwd = os.getcwd()
    name = configured_identity(cwd, session_id)
    if not name:
        if event == "session-start":
            print("AGENTCOMM: no identity for this session, so peer mail is NOT "
                  "being delivered and none has been consumed. Set "
                  "AGENTCOMM_AGENT, or add this session to "
                  "~/.claude/agentcomm_identity.json under by_session"
                  + (f' (this session is "{session_id}")' if session_id else "")
                  + ", or its directory under by_directory. Do not bind a name "
                  "another live agent is using.")
        return 0

    # One session per name. Refusing is the entire safety property: the cost of
    # sharing a name is that one agent silently reads and archives the other's
    # mail, which no counter afterwards can reveal.
    held = claim_name(name, session_id, cwd)
    if held:
        if event != "midturn":
            print("AGENTCOMM: NOT delivering. The name %r is held by another live "
                  "session (%s, in %s), so consuming it here would read that "
                  "agent's mail and hide it from them. Nothing was consumed.\n"
                  "Set AGENTCOMM_AGENT to this session's own name, which "
                  "overrides the directory map. The map keys on directory alone "
                  "and cannot tell two agents in one tree apart."
                  % (name, held.get("session_id", "?"), held.get("cwd", "?")))
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
