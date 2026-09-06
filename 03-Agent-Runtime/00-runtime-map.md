# 第 0 课：Runtime 学习地图（语言无关）

> 这门课的主线不依赖 Python、Java、Go 或 TypeScript。代码只是观察机制的工具，Runtime 本身是执行模型和可靠性问题。

## 1. Runtime 不是某门语言

同一个问题可以用不同语言实现：

```text
业务代码 / Agent 决策
          |
          v
Runtime：调度、状态、工具、失败、恢复
          |
          v
操作系统 / 容器：进程、内存、网络、权限
```

JVM、Node.js、容器运行时和 Agent Runtime 的共同点，不是语法相同，而是它们都把某种“可执行对象”放进一个受管理的环境里。

## 2. Agent Runtime 的学习主线

```text
一次函数调用
  -> 一次有状态的 Run
  -> 多 Run 排队与调度
  -> Workflow 状态机
  -> 模型提出动态 Decision
  -> Tool Gateway / MCP
  -> Checkpoint 与恢复
  -> Context、Memory、人工审批
  -> Trace、Policy、Sandbox、生产部署
```

每一步都回答四个问题：

1. 谁决定下一步？
2. 当前状态在哪里？
3. 失败后怎么处理？
4. 外部能力经过什么边界？

## 3. 统一对象

| 对象 | 含义 |
| --- | --- |
| `Task` | 用户提交的逻辑任务定义 |
| `Run` | 一个 Task 的具体执行实例 |
| `State` | Run 当前的结构化事实 |
| `Event` | 已经发生、可审计的事实 |
| `Tool` | 经过授权和参数校验的外部能力 |
| `Checkpoint` | 用于恢复的 State 快照 |

## 4. 你不需要先学什么

不需要先学某个 Agent 框架，也不需要先掌握 Python。你只需要能读懂少量伪代码：

```text
Run.state = running
decision = model(Run.state)
if decision requests a tool:
    Runtime checks policy
    result = Tool.call(decision.args)
    Run.state = update(Run.state, result)
    Checkpoint.save(Run.state)
```

之后的 Python、TypeScript 或 Go 实验只是把这些动作写成可运行程序。换语言时，核心因果链不变。

## 5. 学习顺序

| 阶段 | 主题 | 主要产物 |
| --- | --- | --- |
| 1 | 程序执行与资源 | 理解进程、线程、I/O、事件循环 |
| 2 | 任务编排 | Queue、Scheduler、Worker、State Machine |
| 3 | Agent 执行 | Decision、Tool Gateway、停止条件 |
| 4 | 外部能力 | MCP Host、Client、Server 和错误边界 |
| 5 | 可靠性 | Checkpoint、幂等、租约、重试、Outbox |
| 6 | 生产化 | Memory、审批、Trace、Sandbox、SLO |

## 6. 如何使用本目录

先读本课和 [第一课：Runtime 的地基](01-runtime-foundation.md)，再按 01–11 课顺序学习。`labs/` 目录中的 Python 脚本是可选实验，不是概念前置；如果你更熟悉其他语言，可以用伪代码、TypeScript 或 Go 重写同一个实验。

Python 补充内容见[附录 A：Python 实验环境](00-environment-python.md)。

下一课进入“程序为什么需要运行环境”：从代码、进程、状态和任务生命周期开始。
