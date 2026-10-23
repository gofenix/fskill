#!/usr/bin/env python3
"""Read-only validation and ready-frontier calculation for an execution ledger.

This checks recorded evidence, not Git ancestry or whether a test really ran.
The coordinator must read those facts back before recording `verified`.
Only the Python standard library is required; run from any target directory.
"""

from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path
import re
import sys


STATUSES = {"pending", "running", "done", "merged", "verified", "failed", "blocked"}
COMMIT_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


class GraphError(ValueError):
    """An invalid graph or unsupported completion claim."""


def nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GraphError(f"{label} must be a non-empty string")
    if value != value.strip():
        raise GraphError(f"{label} must not have surrounding whitespace")
    return value


def verified_evidence(task: dict) -> None:
    task_id = task["id"]
    commit = task.get("integration_commit")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        raise GraphError(f"verified task {task_id}: integration_commit must be a full Git commit ID")
    verification = task.get("verification")
    if not isinstance(verification, dict):
        raise GraphError(f"verified task {task_id}: missing verification evidence")
    if verification.get("result") != "passed":
        raise GraphError(f"verified task {task_id}: verification result must be passed")
    if verification.get("commit") != commit:
        raise GraphError(f"verified task {task_id}: verification commit must match integration_commit")
    nonempty_string(verification.get("evidence"), f"verified task {task_id}: evidence")


def inspect_graph(data: object) -> dict:
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise GraphError("ledger must be an object with a tasks array")
    if not data["tasks"]:
        raise GraphError("tasks must not be empty")

    tasks: dict[str, dict] = {}
    for task in data["tasks"]:
        if not isinstance(task, dict):
            raise GraphError("each task must be an object")
        task_id = nonempty_string(task.get("id"), "task id")
        if task_id in tasks:
            raise GraphError(f"duplicate task id: {task_id}")
        status = task.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            raise GraphError(f"task {task_id}: unsupported status {status!r}")
        dependencies = task.get("blocked_by")
        if not isinstance(dependencies, list):
            raise GraphError(f"task {task_id}: blocked_by must be an array")
        seen: set[str] = set()
        for dependency in dependencies:
            dependency = nonempty_string(dependency, f"task {task_id}: blocker")
            if dependency in seen:
                raise GraphError(f"task {task_id}: duplicate blocker {dependency}")
            seen.add(dependency)
        if status == "verified":
            verified_evidence(task)
        tasks[task_id] = task

    dependents: dict[str, list[str]] = {task_id: [] for task_id in tasks}
    remaining: dict[str, int] = {}
    for task_id, task in tasks.items():
        remaining[task_id] = len(task["blocked_by"])
        for dependency in task["blocked_by"]:
            if dependency not in tasks:
                raise GraphError(f"task {task_id}: missing blocker {dependency}")
            dependents[dependency].append(task_id)

    frontier = deque(task_id for task_id, count in remaining.items() if count == 0)
    visited = 0
    while frontier:
        task_id = frontier.popleft()
        visited += 1
        for dependent in dependents[task_id]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                frontier.append(dependent)
    if visited != len(tasks):
        unresolved = [task_id for task_id, count in remaining.items() if count]
        raise GraphError(f"dependency cycle; unresolved tasks: {', '.join(unresolved)}")

    verified = {task_id for task_id, task in tasks.items() if task["status"] == "verified"}
    blocked = {}
    invalidated = {}
    ready = []
    for task_id, task in tasks.items():
        unmet = [dependency for dependency in task["blocked_by"] if dependency not in verified]
        if task["status"] == "verified" and unmet:
            raise GraphError(f"verified task {task_id}: unverified blockers: {', '.join(unmet)}")
        if task["status"] == "pending":
            if unmet:
                blocked[task_id] = unmet
            else:
                ready.append(task_id)
        elif task["status"] in {"running", "done", "merged"} and unmet:
            invalidated[task_id] = unmet

    return {
        "verification_scope": "ledger_only",
        "ready": ready,
        "blocked": blocked,
        "invalidated": invalidated,
        "in_progress": [
            task_id for task_id, task in tasks.items()
            if task["status"] == "running" and task_id not in invalidated
        ],
        "awaiting_integration": [
            task_id for task_id, task in tasks.items()
            if task["status"] in {"done", "merged"} and task_id not in invalidated
        ],
        "needs_recovery": [
            task_id for task_id, task in tasks.items()
            if task["status"] in {"failed", "blocked"} or task_id in invalidated
        ],
        "verified": [task_id for task_id in tasks if task_id in verified],
        "complete": len(verified) == len(tasks),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, help="JSON execution ledger; never modified")
    args = parser.parse_args()
    try:
        data = json.loads(args.ledger.read_text(encoding="utf-8"))
        result = inspect_graph(data)
    except (OSError, UnicodeError, json.JSONDecodeError, GraphError) as error:
        parser.exit(2, f"task_graph: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
