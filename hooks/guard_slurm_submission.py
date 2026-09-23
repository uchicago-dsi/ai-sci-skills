#!/usr/bin/env python3
"""Refuse an `sbatch` that would produce an unusable or unauthorised run.

Three AGENTS.md rules all come due at the same instant -- the moment a job is
submitted -- and all three are mechanical. Each has already been broken here,
and each costs the whole run rather than a correction.

Submitting from the shared checkout. Every array task stamps the commit it
sees when it starts, so one commit to that checkout mid-array splits a run's
provenance across two SHAs and a consumer requiring a single commit refuses
the result. A documentation-only commit is enough to do it, and three agents
share this checkout. The repair is re-running, which is why this is worth
blocking rather than warning about.

Submitting with unread peer mail. The rule is to drain queued steering
immediately before a real submission, because a hold or a correction that
arrived after the launch was approved is exactly the message that stops it.
The failure this prevents already happened: a peer killed two processes,
said so by mail, and the mail sat unread while the processes were relaunched.

A scheduler-visible name that leaks its role. `squeue` is public across the
division, and `smoke`, `probe`, `test`, `debug`, `pilot`, `placeholder` and
`holder` announce that a job is disposable to people deciding what to
preempt. The role belongs in the run root and the config, where it stays
auditable.

The worktree test is whether git's per-worktree directory differs from the
common one, which is what actually distinguishes them. Keying on the presence
of `outputs/` would not: it is tracked and exists in every worktree, and the
guard originally written to catch this passed on precisely the checkout it
existed to reject.

Nothing here touches a large filesystem. The git query is bounded to the
repository's own metadata, and the mail check is a local socketless CLI call
with a short timeout that fails open, because a broken mailbox must not be
able to block science.
"""
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hookio import allow, command_text, deny_tool, is_shell, payload  # noqa: E402

# Words that say what a job is for rather than what it computes. Matched on
# word boundaries so `probe` is caught and `microprobe_response` is not.
LEAKY_NAME = re.compile(
    r"(?<![a-z0-9])(holder|placeholder|pilot|smoke|probe|test|debug)(?![a-z0-9])",
    re.IGNORECASE)
# Only guard the checkout these rules belong to. Another repository on this
# machine has its own conventions and this hook is not entitled to them.
GUARDED_REPOSITORY = "/gpfs/data/karczmar-lab/hfdp"
AGENTCOMM = Path.home() / ".local" / "bin" / "agentcomm"


def git(cwd, *arguments):
    """One bounded git query, or None when git cannot answer."""
    try:
        done = subprocess.run(["git", "-C", str(cwd)] + list(arguments),
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if done.returncode != 0:
        return None
    return done.stdout.decode("utf-8", "replace").strip()


# Words that may sit in front of the real command without being it.
PREFIXES = ("exec", "sudo", "nohup", "time", "command", "env", "srun")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def expand(target, bound):
    """A cd target with known variables filled in, or None when one is not.

    Giving up on an unresolved variable is deliberate: the guard then judges
    the starting directory, which is the cautious answer. Guessing at a path
    it cannot see would let a submission from the shared checkout through
    because a variable happened to look like a worktree.
    """
    def replace(match):
        return bound.get(match.group(1) or match.group(2), "\x00")
    filled = re.sub(r"\$\{(\w+)\}|\$(\w+)", replace, target)
    if "\x00" in filled or "`" in filled:
        return None
    return filled


def submitting_directory(command, cwd):
    """Where the sbatch in this command actually runs, or None if there is none.

    Two things have to be right. Only the command position counts, because
    `grep -rn sbatch scripts/` names sbatch as a search pattern and submits
    nothing; refusing that would teach an agent the hook fires on mentions,
    which is how a guard stops being read and starts being routed around.

    And a leading `cd` counts. `cd "$WT" && sbatch ...` is the correct way to
    submit from a pinned worktree, and the harness reports the shell's
    starting directory, so reading that alone refuses the very command the
    rule asks for. Segments are walked in order and `cd` moves the directory
    the submission is judged against.

    A `cd` whose target this cannot resolve -- an unexpanded variable, a
    substitution -- gives up and returns the starting directory, so the guard
    can be over-cautious but never silently judges the wrong place.
    """
    here = cwd
    # Literal assignments made earlier in the same command line. `WT=/path`
    # followed by `cd "$WT"` is how a worktree submission is actually
    # written, and a guard that cannot follow it refuses the correct form.
    bound = {}
    for segment in re.split(r"(?:\|\||&&|[;&|\n])", command):
        # A heredoc body is text being written, not a command being run.
        if "<<" in segment:
            break
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        while words and (ASSIGNMENT.match(words[0]) or words[0] in PREFIXES):
            taken = words.pop(0)
            name, _, value = taken.partition("=")
            if ASSIGNMENT.match(taken) and "$" not in value and "`" not in value:
                bound[name] = value
        if not words:
            continue
        head = words[0]
        if head == "cd" and len(words) > 1:
            target = expand(words[1], bound)
            if target is None:
                continue
            here = target if os.path.isabs(target) else os.path.join(here, target)
            continue
        if head == "sbatch" or head.endswith("/sbatch"):
            return here
    return None


def job_name(command):
    """The `--job-name` this submission asks the scheduler to show, if any."""
    match = re.search(r"--job-name[= ]\s*([^\s'\"]+)", command)
    return match.group(1) if match else None


def unread_mail():
    """How many messages are waiting, or None when that cannot be determined.

    Fails open. A mailbox that is down, slow, or unconfigured must not be
    able to stop a submission; the rule this enforces is about steering that
    arrived, not about the mail system being reachable.
    """
    name = os.environ.get("AGENTCOMM_AGENT")
    if not name or not AGENTCOMM.is_file():
        return None
    try:
        done = subprocess.run([str(AGENTCOMM), "agents", "--json"],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if done.returncode != 0:
        return None
    try:
        payload = json.loads(done.stdout.decode("utf-8", "replace") or "[]")
    except ValueError:
        return None
    agents = payload if isinstance(payload, list) else payload.get("agents", [])
    for agent in agents:
        if isinstance(agent, dict) and agent.get("name") == name:
            for key in ("unread", "unread_count", "pending"):
                if isinstance(agent.get(key), int):
                    return agent[key]
    return None


def verdict(command, cwd):
    """The reason to refuse, or None to allow."""
    where = submitting_directory(command, cwd)
    if where is None:
        return None

    common = git(where, "rev-parse", "--path-format=absolute", "--git-common-dir")
    private = git(where, "rev-parse", "--path-format=absolute", "--git-dir")
    toplevel = git(where, "rev-parse", "--show-toplevel")
    if common is None or private is None:
        return None
    if os.path.realpath(str(common).rsplit("/.git", 1)[0]) != GUARDED_REPOSITORY:
        return None

    if os.path.realpath(common) == os.path.realpath(private):
        return ("this is the shared checkout at %s, not a worktree. Every array "
                "task stamps the commit it sees when it starts, so one commit "
                "here mid-run splits the run's provenance across two SHAs and a "
                "consumer requiring a single commit refuses the result.\n\n"
                "Create a pinned worktree and submit from it:\n"
                "  SHA=$(git rev-parse --short HEAD)\n"
                "  git worktree add --detach \"$HFDP_WORKTREE_ROOT/<lane>_$SHA\" HEAD\n"
                "  cd \"$HFDP_WORKTREE_ROOT/<lane>_$SHA\" && export HFDP_CLUSTER=randi\n"
                "Export HFDP_CLUSTER explicitly there: a worktree does not inherit "
                "the pin, because .hfdp_cluster is untracked."
                % (toplevel or GUARDED_REPOSITORY))

    name = job_name(command)
    if name:
        leaky = LEAKY_NAME.search(name)
        if leaky:
            return ("the scheduler-visible job name %r contains %r. squeue is "
                    "public across the division, and that word tells everyone "
                    "the job is disposable. Name it for what it computes and "
                    "keep the role in the run root, the config and the "
                    "provenance, where it stays auditable."
                    % (name, leaky.group(0)))

    waiting = unread_mail()
    if waiting:
        return ("%d unread message(s) are queued for %s. Steering that arrived "
                "after this launch was approved -- a hold, a correction, a peer "
                "who killed something -- is exactly the message that should stop "
                "a submission.\n\n"
                "Run `agentcomm inbox --json`, act on what is there, then submit."
                % (waiting, os.environ.get("AGENTCOMM_AGENT")))
    return None


def main():
    event = payload()
    if not is_shell(event):
        allow()
    command = command_text(event)
    cwd = event.get("cwd") or os.getcwd()
    reason = verdict(command, cwd)
    if not reason:
        allow()
    deny_tool("Refused this Slurm submission: %s\n\n"
              "The rule is in AGENTS.md under Compute And Slurm. Fix the cause "
              "rather than reshaping the command to get past this check; if "
              "none of it fits what you are doing, ask Anna." % reason)


if __name__ == "__main__":
    main()
