# Runtime 学习路线

这套课程面向第一次接触 Runtime 的读者，主线与具体编程语言无关，最终目标是能够读懂并实现一个小型 Agent Runtime。`labs/` 中的 Python 代码只是可选实验载体。

## 总路线

```text
程序如何运行
    -> 进程、线程、内存与 I/O
    -> 协程、事件循环与异步调度
    -> 队列、Scheduler、Worker
    -> 状态机、Workflow、重试
    -> Agent 的模型决策循环
    -> Tool Registry 与 MCP
    -> Checkpoint、Durable Execution、人工审批
    -> 安全、可观测性与生产部署
```

## 每一课都回答四个问题

1. 谁决定下一步执行什么？
2. 当前状态保存在哪里？
3. 任务失败后怎么办？
4. 外部能力通过什么边界被调用？

## 统一术语

整套课程只使用下面这一组含义。代码示例可以简化实现，但不能改变对象的责任边界。

| 术语 | 唯一定义 |
| --- | --- |
| `Task` | 用户提交的逻辑任务定义，可以被多次执行 |
| `Run` | 某个 `Task` 的一次执行实例，有唯一 `run_id` |
| `State` | 一个 `Run` 在当前时刻的结构化事实 |
| `Event` | 已经发生、可以记录和审计的事实 |
| `Tool` | 经过注册、参数校验和权限检查的外部能力 |
| `Checkpoint` | 包含 State、下一步位置和版本的可恢复快照 |

### Run 生命周期

```text
created -> queued -> running
                       |
       +---------------+----------------+
       v                                v
waiting_for_tool                 waiting_for_human
       |                                |
       +-------------> running <--------+
                                      |
                         +------------+------------+
                         v                         v
                    succeeded                  failed / cancelled
```

`resumed` 只表示 `run.resumed` Event，不是生命周期状态。Workflow 可以有自己的业务子状态，但必须和 Run 生命周期分开。

### Event 命名约定

教学实验采用命名空间加动作的形式，例如 `run.created`、`run.started`、`decision.created`、`tool.call.started`、`tool.call.finished`、`approval.requested`、`approval.granted`、`checkpoint.saved`、`run.finished` 和 `run.failed`。每条 Event 至少应能关联 `run_id`、时间和结果状态。

## 课程目录

| 课次 | 主题 | 你要解决的问题 |
| --- | --- | --- |
| 00 | [Runtime 学习地图](00-runtime-map.md) | 先建立语言无关的系统模型 |
| 01 | [Runtime 的地基](01-runtime-foundation.md) | 程序如何被启动、执行、记录和结束 |
| 02 | [进程、线程与 I/O](02-process-thread-io.md) | 等待和计算分别该怎样安排 |
| 03 | [事件循环与 asyncio](03-event-loop-asyncio.md) | 一个线程如何交错推进多个等待任务 |
| 04 | [Queue、Scheduler 与 Worker](04-queue-scheduler-worker.md) | 任务多了如何排队、限流和消费 |
| 05 | [状态机与 Workflow](05-state-machine-workflow.md) | 如何限制合法状态转移和流程分支 |
| 06 | [Agent Runtime](06-agent-runtime.md) | 模型如何提出决策，Runtime 如何约束它 |
| 07 | [MCP 与 Tool Runtime](07-mcp-tool-runtime.md) | 工具如何发现、授权、调用和报错 |
| 08 | [Checkpoint 与 Durable Execution](08-durable-execution.md) | 进程崩溃后怎样从进度继续 |
| 09 | [Context、Memory 与 Human-in-the-Loop](09-context-memory-human-loop.md) | 什么该进上下文，什么该长期保存 |
| 10 | [可观测性、安全与生产化](10-observability-security-production.md) | 如何定位问题并限制风险 |
| 11 | [综合项目：研究助理 Runtime](11-capstone.md) | 把所有组件拼成一个可恢复系统 |
| 12 | [Runtime 资料索引](12-resources.md) | 按问题和阶段选择官方资料 |

附录：[Python 实验环境（可选）](00-environment-python.md)

完整课程沿用同一个“研究助理”项目逐步升级。先用 Python 标准库建立直觉，再引入框架和分布式组件。

## 学习循环

每一课固定走下面六步，不跳步：

```text
读问题场景
  -> 画出状态和数据流
  -> 跑最小代码
  -> 故意制造一次失败
  -> 用四个问题复述
  -> 再进入下一课
```

四个复述问题：

1. 谁决定下一步执行什么？
2. 当前状态保存在哪里？
3. 任务失败后怎么办？
4. 外部能力通过什么边界被调用？

## 运行入口

```powershell
python 03-Agent-Runtime/learn.py list
python 03-Agent-Runtime/learn.py run 01
python 03-Agent-Runtime/learn.py run 03
python 03-Agent-Runtime/learn.py all
```

`run 00` 只打开语言无关的学习地图；`all` 运行 01–11 的本地 Python 实验。实验不代表 Runtime 只能用 Python。
