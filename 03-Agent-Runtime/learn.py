"""List lessons and run local labs with temporary, documented side effects."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LABS = {
    "01": ROOT / "lesson01_runtime.py",
    "02": ROOT / "labs" / "02_process_thread_io.py",
    "03": ROOT / "labs" / "03_asyncio_event_loop.py",
    "04": ROOT / "labs" / "04_queue_scheduler_worker.py",
    "05": ROOT / "labs" / "05_state_machine_workflow.py",
    "06": ROOT / "labs" / "06_agent_runtime_mock.py",
    "07": ROOT / "labs" / "07_mcp_like_tool_runtime.py",
    "08": ROOT / "labs" / "08_durable_checkpoint.py",
    "09": ROOT / "labs" / "09_context_memory_approval.py",
    "10": ROOT / "labs" / "10_observability_policy.py",
    "11": ROOT / "labs" / "11_capstone.py",
}


def list_lessons() -> None:
    print("00: 00-runtime-map.md [language-neutral; read the lesson]", flush=True)
    for number, path in LABS.items():
        status = "ready" if path.exists() else "missing lab"
        print(f"{number}: {path.relative_to(ROOT)} [{status}]", flush=True)


def run_lesson(number: str) -> int:
    if number == "00":
        print("lesson 00 is language-neutral; read 03-Agent-Runtime/00-runtime-map.md", flush=True)
        return 0
    path = LABS.get(number)
    if path is None:
        print(f"unknown lesson: {number}", file=sys.stderr)
        return 2
    if not path.exists():
        print(f"lab is not available yet: {path}", file=sys.stderr)
        return 2
    print(f"\n=== lesson {number}: {path.name} ===", flush=True)
    try:
        completed = subprocess.run(
            [sys.executable, "-X", "utf8", str(path)],
            cwd=ROOT,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print(f"lab timed out after 30s: {path.name}", file=sys.stderr, flush=True)
        return 124
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Runtime course runner")
    parser.add_argument("command", choices=("list", "run", "all"))
    parser.add_argument("lesson", nargs="?")
    args = parser.parse_args()

    if args.command == "list":
        list_lessons()
        return 0
    if args.command == "run":
        if args.lesson is None:
            parser.error("run requires a lesson number, for example 03")
        return run_lesson(args.lesson.zfill(2))

    for number in LABS:
        exit_code = run_lesson(number)
        if exit_code != 0:
            return exit_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
