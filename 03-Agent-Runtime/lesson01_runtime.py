"""Lesson 1: a tiny synchronous runtime.

Run with:
    python 03-Agent-Runtime/lesson01_runtime.py
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional
import time
import uuid


@dataclass
class Task:
    """Logical task definition; one Task may have multiple Runs."""

    name: str
    handler: Callable[[Any], Any]
    payload: Any


@dataclass
class Run:
    """One execution instance of a Task."""

    task: Task
    run_id: str
    state: str = "created"
    result: Any = None
    error: Optional[str] = None


class Runtime:
    """Owns task lifecycle and keeps business functions unaware of it."""

    def _emit(self, run: Run, event: str) -> None:
        print(
            f"run={run.run_id} task={run.task.name} "
            f"event={event} state={run.state}"
        )

    def run(self, task: Task) -> Run:
        run_id = uuid.uuid4().hex[:8]
        started = time.perf_counter()
        run = Run(task=task, run_id=run_id)

        self._emit(run, "run.created")
        run.state = "running"
        self._emit(run, "run.started")

        try:
            run.result = task.handler(task.payload)
        except Exception as exc:  # Runtime prevents one task from killing the runner.
            run.state = "failed"
            run.error = f"{type(exc).__name__}: {exc}"
            self._emit(run, "run.failed")
        else:
            run.state = "succeeded"
            self._emit(run, "run.finished")
        finally:
            elapsed = time.perf_counter() - started
            print(f"run={run_id} elapsed={elapsed:.3f}s")

        return run


def double(value: int) -> int:
    return value * 2


def fail(_: Any) -> None:
    raise ValueError("the demo task failed on purpose")


if __name__ == "__main__":
    runtime = Runtime()

    success = runtime.run(Task("double", double, 21))
    print("success result:", success.result)
    print()

    failure = runtime.run(Task("failure-demo", fail, None))
    print("failure error:", failure.error)
