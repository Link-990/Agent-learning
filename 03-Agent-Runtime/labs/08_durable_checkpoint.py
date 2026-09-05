"""本地 JSON Checkpoint、原子替换和恢复实验。"""
import json
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Checkpoint:
    run_id: str
    next_step: str
    state: str
    data: dict
    version: int = 1


def save(cp: Checkpoint, path: Path) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(asdict(cp), ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)
    print(f"event=checkpoint.saved run_id={cp.run_id} run_state={cp.state} version={cp.version}")


def load(path: Path) -> Checkpoint:
    cp = Checkpoint(**json.loads(path.read_text(encoding="utf-8")))
    print(f"event=checkpoint.loaded run_id={cp.run_id} run_state={cp.state} next_step={cp.next_step}")
    return cp


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="runtime-course-08-") as directory:
        path = Path(directory) / "checkpoint.json"
        save(Checkpoint("run-08", "approval", "waiting_for_human", {"notes": ["mock result"]}), path)
        restored = load(path)
        restored.next_step = "writing"
        restored.state = "running"
        restored.version += 1
        save(restored, path)
        final = load(path)
        print(f"event=run.resumed run_id={final.run_id} run_state={final.state} next_step={final.next_step}")


if __name__ == "__main__":
    main()
