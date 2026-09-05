"""结构化 Event、脱敏和最小策略检查实验。"""
import json
import time


def redact(value: object) -> str:
    text = str(value)
    if "token=" in text or "sk-" in text:
        return "[REDACTED]"
    return text[:160]


def emit(run_id: str, event: str, **fields: object) -> None:
    record = {"ts": round(time.time(), 3), "run_id": run_id, "event": event}
    record.update({key: redact(value) for key, value in fields.items()})
    print(json.dumps(record, ensure_ascii=False))


def authorize(tool: str, allowed: set[str], budget: int) -> bool:
    permitted = tool in allowed and budget > 0
    emit("run-10", "policy.checked", tool=tool, allowed=permitted, budget=budget)
    return permitted


def main() -> None:
    emit("run-10", "run.created", state="created")
    emit("run-10", "run.started", state="running")
    if authorize("search.mock", {"search.mock"}, 2):
        emit("run-10", "tool.call.started", tool="search.mock", state="waiting_for_tool")
        emit("run-10", "tool.call.finished", tool="search.mock", result="mock notes")
    emit("run-10", "error", message="token=sk-demo-secret")
    emit("run-10", "run.finished", state="succeeded")


if __name__ == "__main__":
    main()
