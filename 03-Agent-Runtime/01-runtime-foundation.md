# 第一课：Runtime 的地基

> 目标：从“我写了一个函数”走到“我知道一个程序怎样被启动、执行、记录和结束”。

> 语言说明：本课的代码用 Python 记录执行机制；你可以把它当作伪代码阅读，不需要先学 Python。

这篇课文只解决一个问题：**Runtime 到底接管了什么**。

先不要把 Runtime 和大模型、MCP 或某个框架绑定在一起。Agent Runtime 是后面一层应用形态，地基仍然是普通程序运行的机制。

---

## 0. 先建立学习地图

Runtime 这个词之所以容易让人迷糊，是因为它同时出现在几个层次：

```text
硬件
  CPU、内存、磁盘、网卡
      |
操作系统
  进程、线程、文件、网络、权限
      |
语言 Runtime
  Python 解释器、JVM、V8、Node.js API
      |
应用代码
  函数、服务、任务
      |
Agent Runtime
  模型决策、工具、状态、工作流、恢复
```

这里不是说每一层都有一条绝对清晰的边界。实际系统常常跨层，但这个分层足够帮助我们先回答“谁负责什么”。

本课程从下往上学：先理解程序运行，再理解 Agent 运行。

---

## 1. Runtime 的一般含义

本课程统一使用以下术语：`Task` 是用户提交的逻辑任务定义；`Run` 是某个 Task 的一次执行实例；`State` 是 Run 当前状态；`Event` 是已经发生的事实；`Tool` 是受控能力；`Checkpoint` 是可恢复快照。第一课的代码是简化模型，`Run` 只用局部 `run_id` 表示。

### 1.1 源代码并不会自己执行

你写下：

```python
result = 21 * 2
print(result)
```

这只是文字。CPU 不认识 Python 语法，也不会直接理解 `print`。

程序真正运行时，大致经历下面的过程：

```text
Python 源代码
    |
    v
Python 解释器读取并执行
    |
    v
创建进程，申请内存
    |
    v
CPU 执行指令，操作系统提供文件和终端
    |
    v
屏幕出现 42
```

Python 解释器、标准库、运行时数据结构，以及它们和操作系统之间的配合，合在一起就构成了 Python 程序的运行环境。

### 1.2 编译期和运行期

| 时机 | 发生什么 | 例子 |
| --- | --- | --- |
| 编译期或加载期 | 检查语法、解析模块、准备代码 | `SyntaxError`、模块找不到 |
| 运行期 | 真正执行函数、读写资源、处理输入 | 除零、网络超时、权限错误 |

所以“运行时错误”不是一个玄学概念，它只是指：程序已经开始执行后才暴露的错误。

```text
# 语法错误：程序还没开始正常执行
if True print("hello")
```

```python
# 运行时错误：代码开始执行后才出错
number = 10 / 0
```

### 1.3 一个不容易混淆的定义

可以先记成：

> Runtime = 让代码真正运行起来，并在运行过程中管理执行、资源和错误的一组机制。

它不一定是一个独立的软件包，也不一定由一个类组成。

一个小脚本里的 Runtime 可能只是 Python 解释器；一个大型服务里的 Runtime 可能包含进程、线程池、队列、数据库、调度器和监控系统。

---

## 2. 从一个函数开始：谁在控制执行

先看最普通的程序：

```python
def double(value):
    return value * 2


result = double(21)
print(result)
```

这段程序里有几个角色：

| 角色 | 代码中的对象 | 负责什么 |
| --- | --- | --- |
| 业务逻辑 | `double` | 计算结果 |
| 调用者 | `double(21)` | 决定现在调用它 |
| 运行环境 | Python 解释器 | 读取、执行 Python 代码 |
| 资源提供者 | 操作系统 | 提供进程、内存、终端 |

这里没有一个单独的 `Runtime` 类，但 Runtime 的工作仍然存在。

最容易漏掉的事实是：**函数只描述怎么计算，不负责安排自己什么时候运行，也不负责保存运行历史。**

一旦需求变成下面这样，问题就出现了：

- 同时跑 100 个任务；
- 某个任务失败后重试；
- 用户关闭页面后任务继续运行；
- 程序重启后从上次进度继续；
- 某个任务执行前需要人工批准。

这些需求都不是 `double()` 这个函数本身应该解决的，而是 Runtime 层的问题。

---

## 3. Runtime 最先管理的是“任务生命周期”

把函数调用包装成任务后，我们就能明确描述它的状态：

```text
created
   |
   v
queued -> running
  /   \
 v     v
succeeded  failed
```

以后再加入暂停和等待：

```text
created -> queued -> running -> waiting_for_tool -> succeeded
                         |              |
                         |              +----> failed
                         +--> waiting_for_human --run.resumed Event--> running
                         +--> cancelled
```

生命周期不是装饰信息。它会影响用户界面、重试策略、资源回收和恢复逻辑。

例如：

- `created`/`queued` 的任务还没有占用 Worker；
- `running` 的任务可能正在消耗 CPU 或调用 API；
- `waiting_for_tool`/`waiting_for_human` 的任务可能正在等待外部结果；
- `failed` 的任务可以进入重试队列；
- `cancelled` 的任务需要释放连接和临时文件。

如果系统只返回一个字符串“处理中”，后续几乎无法可靠地调度它。

---

## 4. 第一个可运行实验：最小同步 Runtime

完整代码见：[lesson01_runtime.py](lesson01_runtime.py)。

它故意只做五件事：

1. 创建任务；
2. 记录任务状态；
3. 执行业务函数；
4. 捕获任务异常；
5. 输出运行 ID 和耗时。

核心代码：

```python
from dataclasses import dataclass
from typing import Any, Callable, Optional
import time
import uuid


@dataclass
class Task:
    name: str
    handler: Callable[[Any], Any]
    payload: Any
    # Task 是定义；一次执行由 Run 单独标识。


@dataclass
class Run:
    task: Task
    run_id: str
    state: str = "created"
    result: Any = None
    error: Optional[str] = None


class Runtime:
    def run(self, task: Task) -> Run:
        run_id = uuid.uuid4().hex[:8]
        started = time.perf_counter()

        run = Run(task=task, run_id=run_id, state="running")
        print(f"run={run_id} event=run.created state=created")
        print(f"run={run_id} event=run.started state={run.state}")

        try:
            run.result = task.handler(task.payload)
        except Exception as exc:
            run.state = "failed"
            run.error = f"{type(exc).__name__}: {exc}"
            print(f"run={run_id} event=run.failed state={run.state}")
        else:
            run.state = "succeeded"
            print(f"run={run_id} event=run.finished state={run.state}")
        finally:
            elapsed = time.perf_counter() - started
            print(f"run={run_id} elapsed={elapsed:.3f}s")

        return run
```

### 4.1 `Task` 是什么

```python
Task("double", double, 21)
```

这不是函数调用，而是一份“待执行任务的描述”：

```text
任务名称：double
执行函数：double
输入数据：21
当前状态：created
```

把任务变成数据以后，Runtime 才能把它放入队列、写入数据库、重新加载，或者交给另一个 Worker。

### 4.2 `handler` 为什么要和 Runtime 分开

`handler` 只关心业务：输入 21，得到 42。

它不需要知道：

- 任务 ID 怎么生成；
- 状态什么时候改成 `running`；
- 失败后是否记录日志；
- 结果是否要写入数据库。

这种分离很重要。以后换成异步 Worker、远程服务或 Agent 工具时，业务函数可以少改很多。

### 4.3 `try/except` 在这里解决什么

它不是为了“让错误消失”，而是把错误变成 Runtime 能理解的状态：

```text
Python 异常
    |
    v
任务状态 = failed
任务错误 = ValueError: ...
    |
    v
上层决定：重试、暂停、告警或结束
```

生产系统通常还要区分可重试错误和不可重试错误。比如网络暂时断开可能值得重试，参数非法则应该直接失败并提示调用方。

### 4.4 `run_id` 为什么重要

假设同一秒内有 10 个任务都失败了，只看一句“请求失败”无法判断它们是否属于同一次运行。

`run_id` 是一条关联线索，后面会贯穿：

```text
用户请求
 -> Runtime
 -> LLM 调用
 -> 工具调用
 -> 数据库查询
 -> 最终回答
```

在生产环境里，它通常会升级成 trace ID 或 execution ID。

---

## 5. 运行实验时要观察什么

执行：

```powershell
python 03-Agent-Runtime/lesson01_runtime.py
```

成功任务的输出类似：

```text
event=run.created state=created
event=run.started state=running
event=run.finished state=succeeded
elapsed=0.000s
success result: 42
```

失败任务的输出类似：

```text
event=run.created state=created
event=run.started state=running
event=run.failed state=failed
elapsed=0.000s
failure error: ValueError: the demo task failed on purpose
```

重点观察两件事：

第一，失败任务没有让整个 Python 进程立刻崩溃，错误被转成了任务状态。

第二，当前状态只存在 `Task` 对象里。程序一旦退出，状态也就没了。

这正是后续要引入 `StateStore` 的原因。

---

## 6. 三个实验：让缺失的能力暴露出来

### 实验 A：同步等待

把业务函数改成：

```python
def slow_double(value):
    time.sleep(2)
    return value * 2
```

再运行两个任务：

```python
runtime.run(Task("first", slow_double, 1))
runtime.run(Task("second", slow_double, 2))
```

总耗时大约是 4 秒。

原因很简单：当前 Runtime 只有一个执行路径，第二个任务要等第一个任务完全返回。

此时我们自然会问：任务在等待网络或磁盘时，能不能先去做另一个任务？

这个问题会把我们带到下一课的事件循环和异步 Runtime。

### 实验 B：进程中途退出

在 `handler` 里加入较长的 `sleep`，任务运行时手动终止程序。

重新启动后，你会发现 Runtime 不知道刚才执行到哪里了，因为：

```text
Run 状态只在内存里
进程退出 -> 内存释放 -> 状态消失
```

这和“重试”不是一回事。重试只是再次调用；恢复需要知道上次执行到了哪一步。

### 实验 C：异常分类

分别制造两类错误：

```python
def temporary_error(_):
    raise TimeoutError("network timeout")


def permanent_error(_):
    raise ValueError("invalid parameter")
```

现在两个错误都会变成 `failed`，但生产 Runtime 不能因此采用同一种处理方式：

| 错误 | 可能策略 |
| --- | --- |
| 网络超时 | 延迟后重试，设置最大次数 |
| 参数非法 | 直接失败，返回明确原因 |
| 权限不足 | 请求授权或转人工 |
| 进程崩溃 | 从 Checkpoint 恢复 |

到这里你已经能看到：Runtime 不是“包一层函数”，而是在建立一套执行语义。

---

## 7. 从普通 Runtime 走到 Agent Runtime

普通任务的下一步通常由代码决定：

```python
article = fetch_article(url)
summary = summarize(article)
save(summary)
```

Agent 的下一步可能由模型根据环境结果决定：

```text
用户目标
   |
   v
模型读取当前状态
   |
   +--> 直接回答
   |
   +--> 选择工具
   |
   +--> 请求人工批准
   |
   +--> 重新规划
```

因此 Agent Runtime 比普通 Runtime 多了几类对象：

| 普通 Runtime | Agent Runtime 中的对应物 |
| --- | --- |
| `handler` | LLM 决策加工具执行 |
| `payload` | 用户目标、上下文、当前状态 |
| `result` | 模型回复、工具观察、任务产物 |
| `failed` | 工具错误、模型无法继续、策略拒绝 |
| 顺序调用 | 动态推理循环 |

Agent Runtime 的基本循环可以先写成伪代码：

```python
while not state.finished:
    decision = model(state)

    if decision.type == "tool_call":
        result = execute_tool(decision)
        state = update_state(state, result)
    elif decision.type == "final":
        state.finished = True
        state.answer = decision.content

    save_state(state)
```

注意最后一行：每一步都要保存状态。否则模型刚调用完三个工具，进程一重启，系统仍然不知道发生过什么。

---

## 8. 重新看你的生产级架构图

截图里的结构可以先按“当前已经有”和“未来需要补上”来理解：

| 截图组件 | 它解决的问题 | 当前小实验的状态 |
| --- | --- | --- |
| Client / API | 接收用户请求 | 还没有 |
| Runtime | 统一控制一次运行 | `Runtime.run()` |
| Queue | 暂存待执行任务 | 还没有 |
| Scheduler | 决定何时、以什么顺序执行 | 还没有 |
| Workers | 真正执行任务 | 当前进程里的函数调用 |
| StateStore | 保存任务状态和执行进度 | 只有内存对象 |
| MemoryStore | 保存长期记忆和检索资料 | 还没有 |
| ToolRegistry | 管理可用工具和参数 | 还没有 |
| LLM | 做语言理解和下一步决策 | 还没有 |
| MCP | 跨进程或跨服务连接工具 | 还没有 |
| Observability | 追踪一次运行发生了什么 | 只有 `print()` |
| Postgres / VectorDB | 持久化结构化数据和向量记忆 | 还没有 |

所以你现在不需要死记这张图。它其实是一张“能力缺口地图”：每个方框都是为了回答一个具体问题而出现的。

---

## 9. 四个必须分清的概念

### Runtime 和操作系统

操作系统管理机器资源和进程；Runtime 使用这些资源，把某种语言或应用模型运行起来。

### Runtime 和框架

框架通常提供开发抽象和默认实现；Runtime 关注代码或任务在真实环境中的执行过程。一个框架可以内置 Runtime 能力，但两个词不是同义词。

### Runtime 和 Workflow

Workflow 重点是“流程节点怎么连接”；Runtime 还要负责状态、资源、错误、暂停、恢复和调度。

### Runtime 和 MCP

MCP 是能力连接协议；Runtime 是 Agent 的执行控制层。MCP 不会自动提供任务恢复、重试或完整权限系统。

---

## 10. 本课的验收标准

不要只看懂代码，合上页面后尝试回答：

1. 为什么一个 Python 函数不能自己解决重试和恢复？
2. `Task` 对象相比直接调用函数，多保存了什么信息？
3. 当前实验中，状态究竟保存在哪里？进程退出后会怎样？
4. `run_id` 解决了什么排查问题？
5. 为什么“重试”不等于“从断点恢复”？
6. 你的截图中，Queue、Scheduler、StateStore 分别解决什么问题？
7. Agent Runtime 与普通 Runtime 相比，哪一步变成了动态决策？

如果你能用自己的话讲清这七个问题，第一课就过关了。

---

## 11. 官方资料：现在只读两篇

不要一次读完所有框架文档。当前阶段先看：

1. [Python Tutorial](https://docs.python.org/3/tutorial/)：补齐解释器、函数、异常和模块基础。
2. [Python Event Loop](https://docs.python.org/3/library/asyncio-eventloop.html)：先看目录和术语，不要求现在就读懂全部 API。

下一课会用 `asyncio` 把本课的同步 Runtime 改成异步 Runtime。Python 官方文档把事件循环定义为运行异步任务、回调和网络 I/O 的机制；它解决的是等待期间的调度，不会自动提供持久化恢复。

本课程使用的 Event 命名空间是教学简化：`run.created`、`run.started`、`tool.call.started`、`tool.call.finished`、`approval.requested`、`approval.granted`、`checkpoint.saved`、`run.finished`/`run.failed`。生产系统通常还需要时间戳、事件 ID、版本和幂等键。

---

## 下一课

```text
为什么 sleep 会卡住程序？
→ 阻塞与非阻塞
→ 协程、Task、Future
→ Event Loop 怎样切换任务
→ 并发和并行的区别
→ 把 Runtime 改造成异步版本
```
