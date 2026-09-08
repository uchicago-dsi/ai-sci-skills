#!/usr/bin/env python3
"""Launch one Claude worker with AgentCom assignment and synchronous return."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any


def _run(
    command: list[str], *, cwd: Path, input_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def _failure(stage: str, completed: subprocess.CompletedProcess[str]) -> int:
    print(
        json.dumps(
            {
                "status": "error",
                "stage": stage,
                "exit_code": completed.returncode,
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
            }
        )
    )
    return completed.returncode or 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Send one task through AgentCom, launch Claude once, and return the "
            "bridge result synchronously."
        )
    )
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--task-file", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--supervisor", required=True)
    parser.add_argument("--worker", required=True)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--task-class", default="bounded_worker")
    parser.add_argument("--timeout-seconds", type=int)
    parser.add_argument("--max-budget-usd", type=float)
    parser.add_argument("--agentcomm")
    return parser


def _json_stdout(completed: subprocess.CompletedProcess[str]) -> Any:
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"raw_stdout": completed.stdout.strip()}


def _diff_receipt(workdir: Path) -> dict[str, Any]:
    status = _run(["git", "status", "--short"], cwd=workdir)
    numstat = _run(["git", "diff", "--numstat", "HEAD", "--"], cwd=workdir)
    if status.returncode or numstat.returncode:
        return {"status_available": False}
    additions = 0
    deletions = 0
    tracked_files = 0
    for line in numstat.stdout.splitlines():
        added, deleted, _path = line.split("\t", 2)
        tracked_files += 1
        if added.isdigit():
            additions += int(added)
        if deleted.isdigit():
            deletions += int(deleted)
    changed_paths = [line[3:] for line in status.stdout.splitlines() if len(line) > 3]
    return {
        "status_available": True,
        "changed_file_count": len(changed_paths),
        "changed_paths": changed_paths,
        "tracked_changed_file_count": tracked_files,
        "tracked_additions": additions,
        "tracked_deletions": deletions,
        "tracked_net_loc": additions - deletions,
    }


def _write_json(path: Path, payload: Any) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.chmod(0o600)
    os.replace(temporary, path)


def main() -> int:
    args = _parser().parse_args()
    repo = args.repo.resolve()
    workdir = args.workdir.resolve()
    task_file = args.task_file.resolve()
    state_dir = args.state_dir.resolve()

    if args.timeout_seconds is not None and args.timeout_seconds <= 0:
        raise SystemExit("--timeout-seconds must be positive")
    if args.max_budget_usd is not None and args.max_budget_usd <= 0:
        raise SystemExit("--max-budget-usd must be positive")

    for label, path in (("repo", repo), ("workdir", workdir)):
        if not path.is_dir():
            raise SystemExit(f"{label} is not a directory: {path}")
    if not task_file.is_file():
        raise SystemExit(f"task file does not exist: {task_file}")

    agentcomm_text = args.agentcomm or shutil.which("agentcomm")
    if not agentcomm_text:
        raise SystemExit(
            "agentcomm is not on PATH; pass --agentcomm with its exact path"
        )
    agentcomm = Path(agentcomm_text).resolve()
    if not agentcomm.is_file() or not os.access(agentcomm, os.X_OK):
        raise SystemExit(f"agentcomm is not executable: {agentcomm}")

    bridge = Path(__file__).resolve().with_name("run_claude_worker.py")
    if not bridge.is_file():
        raise SystemExit(f"Claude bridge is missing beside helper: {bridge}")

    state_dir.mkdir(parents=True, exist_ok=True)
    state_dir.chmod(0o700)
    bootstrap = state_dir / "agentcomm_bootstrap.md"
    bootstrap.write_text(
        f"""You are `{args.worker}`. AgentCom is exactly `{agentcomm}`; do not search
for another installation. Use `--repo {repo}` and `--as {args.worker}` on every
AgentCom command. Register, consume the single assignment from `{args.supervisor}`,
and send that supervisor a short acknowledgement and completion notice. Execute the
assignment exactly. Do not wait for a live reply: if a decision is required, send one
concise question and return BLOCKED with the question in your final bridge response.
Return a compact structured result directly as your final bridge response, with outcome,
changed paths, checks, remaining risks, and blocker, so the supervisor does not need to
poll AgentCom. Keep detailed evidence in the worktree or state directory and cite its
path. If AgentCom fails, return a compact transport error and do not broaden the search.\n""",
        encoding="utf-8",
    )
    bootstrap.chmod(0o600)

    register = _run(
        [
            str(agentcomm),
            "register",
            "--repo",
            str(repo),
            "--as",
            args.supervisor,
            "--status",
            f"supervising {args.worker}",
        ],
        cwd=repo,
    )
    if register.returncode:
        return _failure("agentcomm_register", register)

    send = _run(
        [
            str(agentcomm),
            "send",
            args.worker,
            "--repo",
            str(repo),
            "--as",
            args.supervisor,
            "--subject",
            "task",
        ],
        cwd=repo,
        input_text=task_file.read_text(encoding="utf-8"),
    )
    if send.returncode:
        return _failure("agentcomm_send", send)

    bridge_started = time.monotonic()
    bridge_command = [
        sys.executable,
        str(bridge),
        "start",
        "--workdir",
        str(workdir),
        "--prompt-file",
        str(bootstrap),
        "--state-dir",
        str(state_dir),
        "--model",
        args.model,
        "--effort",
        args.effort,
    ]
    if args.timeout_seconds is not None:
        bridge_command.extend(["--timeout-seconds", str(args.timeout_seconds)])
    if args.max_budget_usd is not None:
        bridge_command.extend(["--max-budget-usd", str(args.max_budget_usd)])
    bridge_result = _run(
        bridge_command,
        cwd=repo,
    )
    bridge_duration_seconds = time.monotonic() - bridge_started
    if bridge_result.returncode:
        payload = _json_stdout(bridge_result)
        print(
            json.dumps(
                {
                    "status": payload.get("status", "error")
                    if isinstance(payload, dict)
                    else "error",
                    "stage": "claude_bridge",
                    "bridge": payload,
                    "bridge_duration_seconds": bridge_duration_seconds,
                    "bridge_stderr": bridge_result.stderr.strip(),
                }
            )
        )
        return bridge_result.returncode

    bridge_payload = _json_stdout(bridge_result)
    usage = bridge_payload.get("usage", {}) if isinstance(bridge_payload, dict) else {}
    receipt = {
        "schema_version": "claude_agentcomm_delegation_receipt_v1",
        "task_class": args.task_class,
        "model": args.model,
        "effort": args.effort,
        "duration_seconds": bridge_duration_seconds,
        "claude_turns": bridge_payload.get("num_turns")
        if isinstance(bridge_payload, dict)
        else None,
        "claude_usage": usage,
        "claude_cost_usd": bridge_payload.get("total_cost_usd")
        if isinstance(bridge_payload, dict)
        else None,
        "supervisor_wakeups_expected": 1,
        "followup_count": 0,
        "parent_correction_count": 0,
        "scope": _diff_receipt(workdir),
    }
    receipt_path = state_dir / "delegation_receipt.json"
    _write_json(receipt_path, receipt)
    print(
        json.dumps(
            {
                "status": "success",
                "result": bridge_payload.get("result")
                if isinstance(bridge_payload, dict)
                else bridge_payload,
                "session_id": bridge_payload.get("session_id")
                if isinstance(bridge_payload, dict)
                else None,
                "state_path": bridge_payload.get("state_path")
                if isinstance(bridge_payload, dict)
                else None,
                "receipt_path": str(receipt_path),
                "bridge_duration_seconds": bridge_duration_seconds,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
