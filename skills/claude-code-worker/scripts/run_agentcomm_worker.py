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


def _run(command: list[str], *, cwd: Path, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
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
    parser.add_argument("--agentcomm")
    return parser


def main() -> int:
    args = _parser().parse_args()
    repo = args.repo.resolve()
    workdir = args.workdir.resolve()
    task_file = args.task_file.resolve()
    state_dir = args.state_dir.resolve()

    for label, path in (("repo", repo), ("workdir", workdir)):
        if not path.is_dir():
            raise SystemExit(f"{label} is not a directory: {path}")
    if not task_file.is_file():
        raise SystemExit(f"task file does not exist: {task_file}")

    agentcomm_text = args.agentcomm or shutil.which("agentcomm")
    if not agentcomm_text:
        raise SystemExit("agentcomm is not on PATH; pass --agentcomm with its exact path")
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
assignment exactly. Return its requested compact result directly as your final bridge
response too, so the supervisor does not need to poll AgentCom. If AgentCom fails,
return a compact transport error and do not broaden the search.\n""",
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
    bridge_result = _run(
        [
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
        ],
        cwd=repo,
    )
    bridge_duration_seconds = time.monotonic() - bridge_started
    if bridge_result.returncode:
        return _failure("claude_bridge", bridge_result)

    try:
        bridge_payload: Any = json.loads(bridge_result.stdout)
    except json.JSONDecodeError:
        bridge_payload = {"raw_stdout": bridge_result.stdout.strip()}
    print(
        json.dumps(
            {
                "status": "success",
                "assignment_message": send.stdout.strip(),
                "bridge": bridge_payload,
                "bridge_duration_seconds": bridge_duration_seconds,
                "bridge_stderr": bridge_result.stderr.strip(),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
