#!/usr/bin/env python3
"""Print a small maintenance inventory for a git repo.

The report is intentionally descriptive, not prescriptive. It helps an agent
start from tracked-file evidence before deciding what is safe to edit.
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
from collections import defaultdict
from pathlib import Path


def run_git(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def tracked_python_files(root: Path) -> list[Path]:
    output = run_git(root, ["ls-files", "*.py"])
    return [root / line for line in output.splitlines() if line]


def line_count(path: Path) -> int:
    with path.open("rb") as handle:
        return sum(1 for _ in handle)


def bucket_for(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    parts = rel.parts
    if not parts:
        return "."
    if len(parts) == 1:
        return "repo-root"
    return parts[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repo root; defaults to cwd")
    parser.add_argument("--top", type=int, default=30, help="number of large files to show")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = tracked_python_files(root)
    counts = [(line_count(path), path) for path in files]
    counts.sort(reverse=True)

    total = sum(count for count, _ in counts)
    by_bucket: dict[str, int] = defaultdict(int)
    files_by_bucket: dict[str, int] = defaultdict(int)
    for count, path in counts:
        bucket = bucket_for(path, root)
        by_bucket[bucket] += count
        files_by_bucket[bucket] += 1

    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    commit = run_git(root, ["rev-parse", "--short", "HEAD"]).strip()
    dirty = bool(run_git(root, ["status", "--short"]).strip())

    print("# Maintenance Inventory")
    print()
    print(f"- Timestamp: `{now}`")
    print(f"- Repo: `{root}`")
    print(f"- Git commit: `{commit}`")
    print(f"- Dirty worktree: `{dirty}`")
    print(f"- Tracked Python files: `{len(files)}`")
    print(f"- Tracked Python LOC: `{total}`")
    print()
    print("## LOC By Top-Level Area")
    print()
    print("| Area | Python files | LOC |")
    print("|---|---:|---:|")
    for bucket, loc in sorted(by_bucket.items(), key=lambda item: item[1], reverse=True):
        print(f"| `{bucket}` | {files_by_bucket[bucket]} | {loc} |")
    print()
    print(f"## Largest {min(args.top, len(counts))} Python Files")
    print()
    print("| LOC | Path |")
    print("|---:|---|")
    for count, path in counts[: args.top]:
        print(f"| {count} | `{path.relative_to(root)}` |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
