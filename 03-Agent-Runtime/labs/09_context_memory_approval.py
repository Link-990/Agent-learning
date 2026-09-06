"""Context 截断、Memory 隔离和人工审批 Event 实验。"""
from dataclasses import dataclass


@dataclass
class State:
    run_id: str
    tenant_id: str
    goal: str
    memory: list[str]
    observations: list[str]
    errors: list[str]
    status: str = "running"


def build_context(state: State, limit: int = 100) -> str:
    goal = f"goal={state.goal}"
    recent = [f"error={item}" for item in state.errors[-1:]]
    recent += [f"observation={item}" for item in state.observations[-2:]]
    prefix = goal + "\n"
    return prefix + "\n".join(recent)[:max(0, limit - len(prefix))]


def request_approval(state: State, action: str) -> None:
    state.status = "waiting_for_human"
    print(f"event=approval.requested run_id={state.run_id} state={state.status} action={action}")
    print(f"context_preview={build_context(state)}")


def main() -> None:
    state = State("run-09", "tenant-a", "整理本地资料", ["偏好中文"], ["mock search complete"], ["mock timeout recovered"])
    request_approval(state, "发布摘要")
    print(f"event=approval.granted run_id={state.run_id} state=running")
    state.status = "running"
    print(f"event=context.built run_id={state.run_id} state={state.status} chars={len(build_context(state))}")


if __name__ == "__main__":
    main()
