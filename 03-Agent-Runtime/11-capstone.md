# 第十一课：Capstone：实现一个可恢复的研究助理 Runtime

> 目标：把前面课程的对象串起来，完成一个不依赖真实模型和外部 API 的小型 Agent Runtime。

> 语言说明：综合项目先按语言无关的组件接口设计，再用 Python mock 验证；换成 Go/TypeScript 不改变架构。

## 前置依赖

完成 [05 状态机与 Workflow](05-state-machine-workflow.md) 到 [10 可观测性、安全与生产化](10-observability-security-production.md)，能够解释 `Task`、`Run`、`State`、`Event`、`Tool` 和 `Checkpoint` 的边界。

## 1. 问题场景与验收目标

输入一个研究问题，Runtime 应完成：创建 Task 和 Run、调用本地 mock `Tool`、把观察写入 State、请求人工批准、从临时 Checkpoint 恢复后生成答案，并输出可关联的 Event。骨架通过后再把这些步骤拆成 StateMachine、ToolRegistry、CheckpointStore、EventSink 和 Policy 接口；本课不声称已经实现完整组件。禁止真实网络、真实密钥或任意命令执行。

```text
Task
  -> Run(created)
  -> State(researching)
  -> Tool(mock_search)
  -> Checkpoint
  -> State(waiting_for_human)
  -> Event(approval.granted)
  -> State(writing)
  -> succeeded
```

## 2. 推荐的最小架构

```text
Runtime
  +-- StateMachine.transition(State, Event)
  +-- ToolRegistry.call(name, args)
  +-- CheckpointStore.save/load(Run)
  +-- EventSink.emit(Event)
  +-- Policy (budget, auth, timeout)
```

当前骨架用函数分别承担状态转移、Tool 调用、Checkpoint 保存/加载和 Event 输出，Policy 只体现在人工批准与本地 mock 边界；接口稳定后再替换为数据库、队列或 MCP Client。`Run` 是执行实例，`Task` 可以有多次 Run；每个 Event 都携带 `run_id`，每个 Checkpoint 都带版本号。

## 3. 可运行伪代码骨架

```python
from dataclasses import dataclass, field
from pathlib import Path
import json
import tempfile

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
    answer: str | None = None

def emit(run: Run, event: str, **data):
    print({"run_id": run.run_id, "event": event, **data})

def mock_search(question: str) -> str:
    return f"local note: {question} relates to state and recovery"

def save(run: Run, file: Path):
    file.write_text(json.dumps(run.__dict__, ensure_ascii=False), encoding="utf-8")

def load(file: Path) -> Run:
    raw = json.loads(file.read_text(encoding="utf-8"))
    raw["task"] = Task(**raw["task"])
    return Run(**raw)

def execute(run: Run, file: Path, approval: bool = False):
    if run.state == "created":
        emit(run, "run.created")
        run.state = "running"
        emit(run, "run.started")
    if run.state == "running" and run.workflow_step == "research":
        run.observations.append(mock_search(run.task.description))
        run.state = "waiting_for_tool"
        emit(run, "tool.call.started", tool_name="mock_search")
        emit(run, "tool.call.finished", tool_name="mock_search")
        run.state = "running"
        run.state = "waiting_for_human"
        save(run, file)
        emit(run, "approval.requested")
        return run
    if run.state == "waiting_for_human" and approval:
        emit(run, "approval.granted")
        run.state, run.workflow_step = "running", "writing"
        run.answer = "基于本地资料生成的摘要。"
        run.state = "succeeded"
        save(run, file)
        emit(run, "run.finished", status=run.state)
    return run

with tempfile.TemporaryDirectory(prefix="runtime-course-11-") as directory:
    path = Path(directory) / "run.json"
    task = Task("解释 Durable Execution")
    run = execute(Run("run-capstone", task), path)
    run = execute(load(path), path, approval=True)
    print(run.state, run.answer)
```

这是教学骨架，不是生产实现：`tmp.replace()` 只是教学级同文件系统原子替换，不保证电源故障持久性；生产版本要使用数据库事务、版本检查、租约、超时、幂等 Tool 和结构化错误类型。

## 4. 故障实验

- 在第一次 `save` 后退出进程，重新 `load` 并批准，确认不会重复 mock 搜索。
- 传入两次批准，确认已 `succeeded` 的 Run 不会再次写答案。
- 删除 Checkpoint 文件，明确返回“无法恢复”而不是默默从头运行。
- 将 Tool 名称改成未知值，确认 Registry 拒绝调用并产生 `tool.denied` Event。

## 5. Capstone 验收清单

1. 能画出 Task、Run、State、Event、Tool、Checkpoint 的数据流。
2. 能运行骨架并看到 `tool.finished`、`approval.requested`、`approval.granted`、`checkpoint.saved` 和 `run.finished`。
3. 能证明从临时 Checkpoint 的 `waiting_for_human` 恢复，而不是重新检索。
4. 能指出骨架尚未覆盖未知 Tool、非法 Event、超步数和 Checkpoint 冲突，并说明下一步应在哪个边界加入测试。
5. 能解释日志脱敏、最小权限、超时和幂等分别防御什么风险。

## 6. 延伸边界

当单进程骨架通过后，再引入 SQLite 事务、异步 Worker、MCP transport、OpenTelemetry 和真实模型适配层。每次只替换一个边界，并保留 mock 测试；否则很难判断失败来自模型、网络还是 Runtime。

## 官方资料

- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [Temporal Python SDK](https://docs.temporal.io/develop/python)
- [Model Context Protocol specification](https://modelcontextprotocol.io/specification)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
