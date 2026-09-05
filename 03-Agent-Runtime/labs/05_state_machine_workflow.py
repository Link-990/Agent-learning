"""最小 State/Event 状态机实验。"""
from dataclasses import dataclass, replace
from enum import Enum


class Status(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    WAITING_HUMAN = "waiting_for_human"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class State:
    run_id: str = "run-05"
    status: Status = Status.CREATED
    workflow_step: str = "research"
    events: tuple[str, ...] = ()
    answer: str = ""


RULES = {
    (Status.CREATED, "run.started"): (Status.RUNNING, "research"),
    (Status.RUNNING, "research.done"): (Status.WAITING_HUMAN, "research"),
    (Status.WAITING_HUMAN, "approval.granted"): (Status.RUNNING, "writing"),
    (Status.RUNNING, "write.done"): (Status.SUCCEEDED, "writing"),
}


def transition(state: State, event: str) -> State:
    key = (state.status, event)
    if key not in RULES:
        raise ValueError(f"illegal transition {state.status.value} + {event}")
    next_status, workflow_step = RULES[key]
    next_state = replace(state, status=next_status, workflow_step=workflow_step,
                         events=state.events + (event,))
    print(f"event={event} run_id={next_state.run_id} state={next_state.status.value}")
    return next_state


def main() -> None:
    state = State()
    print(f"event=run.created run_id={state.run_id} state=created")
    for event in ("run.started", "research.done", "approval.granted", "write.done"):
        state = transition(state, event)
    print(f"final_state={state.status.value} event_count={len(state.events)}")


if __name__ == "__main__":
    main()
