#!/usr/bin/env python3
"""Run or resume a write-capable Claude Code worker in an isolated worktree."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import fcntl
import json
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SYSTEM_APPEND = """You are a coding worker delegated by a supervising Codex agent.
Work only inside the current Git worktree. You may inspect, edit, and run relevant checks.
Do not access credentials, protected clinical data, or external services unless the task
prompt explicitly authorizes that exact access. Do not commit unless the prompt explicitly
asks you to. Keep changes scoped. At the end report the outcome, changed files, checks run,
remaining risks, and any blocker. The supervising Codex agent will inspect and integrate
your work."""
DEFAULT_TOOLS = "Read,Glob,Grep,Edit,Write,Bash"


class QuotaCooldown(Exception):
    def __init__(self, state: dict[str, Any]):
        self.state = state
        super().__init__("Claude quota cooldown")


@contextmanager
def _lock(path: Path):
    _private_directory(path.parent)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        os.fchmod(descriptor, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("another worker/probe owns this state; do not duplicate it") from error
        yield
    finally:
        os.close(descriptor)


def _availability(path: Path, now: datetime | None = None) -> dict[str, Any]:
    if path.is_symlink():
        raise RuntimeError("quota state must not be a symlink")
    if not path.exists():
        return {"status": "unknown", "quota_path": str(path)}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state["status"] == "rate_limited":
        now = now or datetime.now(timezone.utc)
        seconds = (datetime.fromisoformat(state["retry_at"]) - now).total_seconds()
        state.update(status="waiting" if seconds > 0 else "probe_due",
                     wait_seconds=max(0, int(seconds) + 1))
    return {**state, "quota_path": str(path)}


def _cooldown(path: Path) -> None:
    state = _availability(path)
    if state["status"] == "waiting":
        raise QuotaCooldown(state)


def _limit_state(message: str, now: datetime) -> dict[str, Any]:
    # Unknown or date-bearing reset formats use a bounded backoff, never an
    # invented date. The CLI's observed time-only form includes an IANA zone.
    retry = now + timedelta(minutes=15)
    basis = "15_minute_backoff"
    match = re.search(r"resets?\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\s*\(([^)]+)\)",
                      message, re.IGNORECASE)
    if match:
        hour, minute = int(match[1]), int(match[2] or 0)
        try:
            zone = ZoneInfo(match[4])
            if not 1 <= hour <= 12 or not 0 <= minute <= 59:
                raise ValueError("invalid reset clock")
            local = now.astimezone(zone)
            hour = hour % 12 + (12 if match[3].lower() == "pm" else 0)
            reset = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if reset + timedelta(minutes=1) <= local:
                reset += timedelta(days=1)
            retry = reset.astimezone(timezone.utc) + timedelta(minutes=1)
            basis = "provider_reset_plus_60_seconds"
        except (ValueError, ZoneInfoNotFoundError):
            pass
    return {"status": "rate_limited", "observed_at": now.isoformat(),
            "retry_at": retry.isoformat(), "retry_basis": basis}


def _interpret(completed: subprocess.CompletedProcess, quota_path: Path) -> dict[str, Any]:
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        result = None
    failed = completed.returncode != 0 or isinstance(result, dict) and result.get("is_error")
    message = str(result.get("result", "")) if isinstance(result, dict) else completed.stdout
    message += "\n" + (completed.stderr or "")
    limited = re.search(r"(?:hit|reached|exceeded).*?(?:session|usage|rate).*?limit|"
                        r"rate_limit_error|rate limit exceeded|usage limit reached",
                        message, re.IGNORECASE)
    if failed and limited:
        state = _limit_state(message, datetime.now(timezone.utc))
        _atomic_json(quota_path, state)
        raise QuotaCooldown({**state, "quota_path": str(quota_path)})
    if failed:
        raise RuntimeError(f"Claude failed (exit {completed.returncode}); not a recognized quota limit")
    if not isinstance(result, dict):
        raise RuntimeError("Claude returned invalid JSON or a non-object result")
    return result


def _available(path: Path, started_at: datetime) -> dict[str, Any]:
    previous = _availability(path)
    if previous["status"] in {"waiting", "probe_due"}:
        if datetime.fromisoformat(previous["observed_at"]) > started_at:
            return previous
    state = {"status": "available", "checked_at": datetime.now(timezone.utc).isoformat()}
    _atomic_json(path, state)
    return {**state, "quota_path": str(path)}


def _probe(args: argparse.Namespace) -> dict[str, Any]:
    # One shared lock prevents simultaneous supervisors from probing the same
    # account. A probe has no tools, customizations, persisted session or task.
    with _lock(args.quota_file.with_suffix(".probe.lock")):
        _cooldown(args.quota_file)
        started_at = datetime.now(timezone.utc)
        previous = _availability(args.quota_file)
        if previous["status"] == "available":
            age = (started_at - datetime.fromisoformat(previous["checked_at"])).total_seconds()
            if age < 60:
                return previous
        completed = subprocess.run(
            [str(_claude_binary(args.claude_binary)), "--safe-mode", "--restricted",
             "--strict-mcp-config", "--no-chrome", "--disable-slash-commands",
             "--print", "--output-format", "json", "--tools", "",
             "--no-session-persistence", "--model", args.model, "--effort", "low",
             "--system-prompt", "Reply exactly AVAILABLE. Do not perform any task.",
             "Reply exactly AVAILABLE."],
            cwd=args.quota_file.parent, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False, timeout=45,
        )
        result = _interpret(completed, args.quota_file)
        if str(result.get("result", "")).strip() != "AVAILABLE":
            raise RuntimeError("availability probe did not return its expected marker")
        return _available(args.quota_file, started_at)


def _next_turn(state_dir: Path, state: dict[str, Any]) -> int:
    recorded = [int(p.stem.removeprefix("turn_")) for p in state_dir.glob("turn_*.json")
                if p.stem.removeprefix("turn_").isdigit()]
    return max([int(state["turn_count"]), *recorded]) + 1


def _private_directory(path: Path) -> Path:
    if path.is_symlink():
        raise RuntimeError(f"state directory must not be a symlink: {path}")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path, 0o700)
    return path


def _atomic_json(path: Path, value: Any) -> None:
    _private_directory(path.parent)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise RuntimeError(f"temporary state already exists: {temporary}")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.chmod(temporary, 0o600)
    if path.exists() and os.path.samefile(temporary, path):
        raise RuntimeError("temporary and final state paths name the same file")
    os.replace(temporary, path)


def _atomic_text(path: Path, value: str) -> None:
    if path.exists():
        raise RuntimeError(f"worker turn artifact already exists: {path}")
    _private_directory(path.parent)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists():
        raise RuntimeError(f"temporary turn artifact already exists: {temporary}")
    temporary.write_text(value, encoding="utf-8")
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def _regular_prompt(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"prompt must be a regular non-symlink file: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise RuntimeError("worker prompt must not be empty")
    return text


def _git_output(workdir: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=workdir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Git validation failed: {' '.join(arguments)}")
    return completed.stdout.strip()


def _validate_worktree(workdir: Path, *, require_clean: bool) -> Path:
    workdir = workdir.resolve()
    if not workdir.is_dir():
        raise RuntimeError(f"worker directory does not exist: {workdir}")
    top = Path(_git_output(workdir, "rev-parse", "--show-toplevel")).resolve()
    if top != workdir:
        raise RuntimeError("--workdir must name the root of the worker Git worktree")
    git_dir = Path(_git_output(workdir, "rev-parse", "--git-dir"))
    common_dir = Path(_git_output(workdir, "rev-parse", "--git-common-dir"))
    if not git_dir.is_absolute():
        git_dir = (workdir / git_dir).resolve()
    if not common_dir.is_absolute():
        common_dir = (workdir / common_dir).resolve()
    if git_dir == common_dir:
        raise RuntimeError("Claude write workers require a linked Git worktree")
    if require_clean and _git_output(workdir, "status", "--porcelain"):
        raise RuntimeError("Claude worker must start from a clean worktree")
    return workdir


def _claude_binary(value: str | None) -> Path:
    candidate = value or os.environ.get("CLAUDE_CODE_BIN") or shutil.which("claude")
    if not candidate:
        fallback = Path.home() / ".local/bin/claude"
        candidate = str(fallback) if fallback.is_file() else ""
    path = Path(candidate).expanduser().resolve() if candidate else Path()
    if not path.is_file() or not os.access(path, os.X_OK):
        raise RuntimeError("Claude Code executable was not found")
    return path


def _invoke(
    *,
    binary: Path,
    workdir: Path,
    prompt: str,
    state_dir: Path,
    turn: int,
    model: str,
    effort: str,
    session_id: str,
    resume: bool,
    max_budget_usd: float | None,
    quota_path: Path,
) -> dict[str, Any]:
    command = [
        str(binary),
        "--safe-mode",
        "--restricted",
        "--strict-mcp-config",
        "--no-chrome",
        "--disable-slash-commands",
        "--print",
        "--output-format",
        "json",
        "--model",
        model,
        "--effort",
        effort,
        "--autocompact",
        "auto",
        "--permission-mode",
        "acceptEdits",
        "--tools",
        DEFAULT_TOOLS,
        "--allowed-tools",
        DEFAULT_TOOLS,
        "--append-system-prompt",
        SYSTEM_APPEND,
    ]
    if max_budget_usd is not None:
        command.extend(["--max-budget-usd", str(max_budget_usd)])
    if resume:
        command.extend(["--resume", session_id])
    else:
        command.extend(["--session-id", session_id])
    command.append(prompt)
    started_at = datetime.now(timezone.utc)
    completed = subprocess.run(
        command,
        cwd=workdir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    raw_path = state_dir / f"turn_{turn:03d}.json"
    error_path = state_dir / f"turn_{turn:03d}.stderr"
    _atomic_text(raw_path, completed.stdout or "")
    _atomic_text(error_path, completed.stderr or "")
    result = _interpret(completed, quota_path)
    observed_session = str(result.get("session_id", session_id))
    if observed_session != session_id:
        raise RuntimeError("Claude returned a different session ID")
    _available(quota_path, started_at)
    return result


def _start(args: argparse.Namespace) -> dict[str, Any]:
    workdir = _validate_worktree(args.workdir, require_clean=True)
    state_dir = _private_directory(args.state_dir.resolve())
    if state_dir == workdir or state_dir.is_relative_to(workdir):
        raise RuntimeError("worker state directory must be outside the worktree")
    state_path = state_dir / "session.json"
    if state_path.exists():
        raise RuntimeError("worker state already exists; use followup")
    _cooldown(args.quota_file)
    session_id = str(uuid.uuid4())
    state = {
        "schema_version": "codex_claude_code_worker_v1",
        "session_id": session_id,
        "workdir": str(workdir),
        "model": args.model,
        "effort": args.effort,
        "max_budget_usd": args.max_budget_usd,
        "turn_count": 1,
    }
    prompt = _regular_prompt(args.prompt_file)
    binary = _claude_binary(args.claude_binary)
    _atomic_json(state_path, state)
    result = _invoke(
        binary=binary,
        workdir=workdir,
        prompt=prompt,
        state_dir=state_dir,
        turn=1,
        model=args.model,
        effort=args.effort,
        session_id=session_id,
        resume=False,
        max_budget_usd=args.max_budget_usd,
        quota_path=args.quota_file,
    )
    return {"state_path": str(state_path), "turn": 1, **result}


def _followup(args: argparse.Namespace) -> dict[str, Any]:
    state_dir = args.state_dir.resolve()
    state_path = state_dir / "session.json"
    if state_path.is_symlink() or not state_path.is_file():
        raise RuntimeError("Claude worker session state is missing")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    _cooldown(args.quota_file)
    workdir = _validate_worktree(Path(state["workdir"]), require_clean=False)
    turn = _next_turn(state_dir, state)
    prompt = _regular_prompt(args.prompt_file)
    binary = _claude_binary(args.claude_binary)
    state["turn_count"] = turn
    _atomic_json(state_path, state)
    result = _invoke(
        binary=binary,
        workdir=workdir,
        prompt=prompt,
        state_dir=state_dir,
        turn=turn,
        model=str(state["model"]),
        effort=str(state["effort"]),
        session_id=str(state["session_id"]),
        resume=True,
        max_budget_usd=state.get("max_budget_usd"),
        quota_path=args.quota_file,
    )
    return {"state_path": str(state_path), "turn": turn, **result}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    start = subparsers.add_parser("start")
    start.add_argument("--workdir", type=Path, required=True)
    start.add_argument("--prompt-file", type=Path, required=True)
    start.add_argument("--state-dir", type=Path, required=True)
    start.add_argument("--model", default="sonnet")
    start.add_argument("--effort", choices=("low", "medium", "high"), default="medium")
    start.add_argument("--max-budget-usd", type=float)
    start.add_argument("--claude-binary")
    followup = subparsers.add_parser("followup")
    followup.add_argument("--state-dir", type=Path, required=True)
    followup.add_argument("--prompt-file", type=Path, required=True)
    followup.add_argument("--claude-binary")
    availability = subparsers.add_parser("availability")
    availability.add_argument("--probe", action="store_true")
    availability.add_argument("--model", default="sonnet")
    availability.add_argument("--claude-binary")
    for command in (start, followup, availability):
        command.add_argument("--quota-file", type=Path,
                             default=Path.home() / ".cache/claude-code-worker/quota.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    os.umask(0o077)
    args = build_parser().parse_args(argv)
    if getattr(args, "max_budget_usd", None) is not None and args.max_budget_usd <= 0:
        raise ValueError("--max-budget-usd must be positive")
    args.quota_file = args.quota_file.expanduser().absolute()
    try:
        if args.action == "availability":
            result = _probe(args) if args.probe else _availability(args.quota_file)
        else:
            with _lock(args.state_dir / ".worker.lock"):
                result = _start(args) if args.action == "start" else _followup(args)
    except QuotaCooldown as error:
        print(json.dumps(error.state, indent=2, sort_keys=True))
        return 75
    compact = {
        key: result.get(key)
        for key in (
            "turn",
            "session_id",
            "result",
            "is_error",
            "num_turns",
            "total_cost_usd",
            "usage",
            "state_path",
            "status",
            "checked_at",
            "retry_at",
            "wait_seconds",
            "quota_path",
        )
        if key in result
    }
    print(json.dumps(compact, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
