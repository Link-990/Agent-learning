"""不依赖模型或网络的 Agent Runtime 决策循环。"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Task:
    question: str


@dataclass
class State:
    question: str
    observations: list[str] = field(default_factory=list)
    answer: str = ""
    steps: int = 0
    status: str = "created"


@dataclass
class Run:
    run_id: str
    task: Task
    state: State


def mock_model(state: State) -> dict:
    if not state.observations:
        return {"type": "tool_call", "name": "search.mock", "args": {"q": state.question}}
    return {"type": "final", "content": "答案来自本地 mock 观察。"}


def call_tool(name: str, args: dict) -> str:
    if name != "search.mock" or not isinstance(args.get("q"), str):
        raise ValueError("tool denied or invalid arguments")
    return f"mock observation for: {args['q']}"


def run(question: str, max_steps: int = 3) -> Run:
    task = Task(question)
    state = State(task.question)
    run = Run("run-06", task, state)
    state.status = "running"
    print("event=run.created run_id=run-06 state=created")
    print("event=run.started run_id=run-06 state=running")
    while not state.answer and state.steps < max_steps:
        state.steps += 1
        decision = mock_model(state)
        print(f"event=decision.created run_id=run-06 state=running type={decision['type']}")
        if decision["type"] == "tool_call":
            state.status = "waiting_for_tool"
            print("event=tool.call.started run_id=run-06 state=waiting_for_tool tool=search.mock")
            result = call_tool(decision["name"], decision["args"])
            state.observations.append(result)
            state.status = "running"
            print("event=tool.call.finished run_id=run-06 state=running tool=search.mock")
            print("event=checkpoint.saved run_id=run-06 state=running")
        elif decision["type"] == "final":
            state.answer = decision["content"]
            print("event=run.finished run_id=run-06 state=succeeded")
        else:
            raise ValueError("unknown decision")
    if not state.answer:
        raise TimeoutError("step budget exhausted")
    run.state = state
    return run


if __name__ == "__main__":
    result = run("什么是 Checkpoint？")
    print(f"answer={result.state.answer} steps={result.state.steps} task={result.task.question}")
