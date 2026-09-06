"""端到端本地研究助理：Tool -> Checkpoint -> Human Event -> 完成。"""
import json
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Task:
    description: str


@dataclass
class Run:
    run_id: str
    task: Task
    state: str = "created"
    workflow_step: str = "research"
    observations: list[str] = field(default_factory=list)
    answer: str = ""


def emit(run: Run, event: str) -> None:
    print(f"event={event} state={run.state} run_id={run.run_id}")


def checkpoint(run: Run, path: Path) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(asdict(run), ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)
    emit(run, "checkpoint.saved")


def load(path: Path) -> Run:
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["task"] = Task(**raw["task"])
    return Run(**raw)


def advance(run: Run, path: Path, approval: bool = False) -> Run:
    if run.state == "created":
        emit(run, "run.created")
        run.state = "running"
        emit(run, "run.started")

    if run.state == "running" and run.workflow_step == "research":
        run.state = "waiting_for_tool"
        emit(run, "tool.call.started")
        run.observations.append(f"mock note for {run.task.description}")
        run.state = "running"
        emit(run, "tool.call.finished")
        run.state = "waiting_for_human"
        checkpoint(run, path)
        emit(run, "approval.requested")
    elif run.state == "waiting_for_human" and approval:
        run.state, run.workflow_step = "running", "writing"
        emit(run, "approval.granted")
        run.answer = "基于本地 mock 资料生成的摘要。"
        run.state = "succeeded"
        checkpoint(run, path)
        emit(run, "run.finished")
    return run


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="runtime-course-11-") as directory:
        path = Path(directory) / "run.json"
        task = Task("解释 Durable Execution")
        run = advance(Run("run-11", task), path)
        run = advance(load(path), path, approval=True)
        print(f"answer={run.answer}")


if __name__ == "__main__":
    main()
