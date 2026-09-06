# 第三课：事件循环与 asyncio

> 目标：理解协程如何暂停和恢复，并写出一个不会被阻塞调用拖住的异步 Runtime。

> 语言说明：`asyncio` 是本课的观察工具；核心知识是协程和事件循环，不是 Python API 记忆。

上一课用线程重叠 I/O 等待。本课换一种模型：一个线程里运行事件循环，协程在等待时主动交还控制权，让其他协程继续。核心不是“异步更快”，而是**等待期间不浪费执行路径**。

## 1. 学习目标

- 区分普通函数、协程函数、协程对象、Task 和 Future。
- 理解事件循环如何选择下一个可运行回调。
- 识别会阻塞事件循环的同步代码。
- 使用 `asyncio.gather`、超时和取消管理并发任务。

## 2. 问题场景：等待时，谁来运行下一个任务

```python
import time

def download(url):
    time.sleep(1)  # 当前线程停在这里
```

如果一个 Runtime 顺序调用三个 `download`，大约等待三秒。异步版本把等待写成 `await asyncio.sleep(1)`，协程暂停，事件循环可以运行其他协程，因此总等待时间接近一秒。

## 3. 底层机制

### 3.1 协程是可暂停的计算

`async def` 定义协程函数，调用它不会立即执行函数体，而是得到协程对象。只有把它交给事件循环，或在另一个协程中 `await`，它才会运行。

```text
协程运行 -> 遇到 await -> 保存局部状态并暂停
                         |
                         v
              事件循环运行别的任务
                         |
                         v
              等待对象完成 -> 协程恢复
```

### 3.2 Event Loop 的职责

事件循环维护就绪回调、定时器和 I/O 监听。当某个等待对象完成，它把对应任务重新放进就绪队列。事件循环本身通常在一个线程中运行，因此协程之间切换发生在明确的 `await` 边界，不会自动抢占任意 Python 指令。

### 3.3 Task 与 Future

`asyncio.create_task(coro())` 把协程包装成 Task，并立即登记到当前事件循环。Task 是 Future 的一种，表示将来会得到结果或异常。`await task` 会等待它完成并取出结果；取消 Task 会向协程注入 `CancelledError`，协程应当在 `finally` 中清理资源。

## 4. 可运行 Python 代码：一个异步 Runtime

```python
import asyncio
import time


async def fake_tool(name: str, delay: float) -> str:
    print(f"start {name} at {time.perf_counter():.2f}")
    await asyncio.sleep(delay)
    print(f"finish {name} at {time.perf_counter():.2f}")
    return f"{name}:ok"


async def run_runtime() -> None:
    started = time.perf_counter()
    tasks = [
        asyncio.create_task(fake_tool("search", 1.0)),
        asyncio.create_task(fake_tool("fetch", 0.6)),
        asyncio.create_task(fake_tool("memory", 0.2)),
    ]
    results = await asyncio.gather(*tasks)
    print("results:", results)
    print("elapsed:", round(time.perf_counter() - started, 2), "s")


asyncio.run(run_runtime())
```

对应实验脚本是 [`labs/03_asyncio_event_loop.py`](labs/03_asyncio_event_loop.py)，直接运行：

```powershell
python 03-Agent-Runtime/labs/03_asyncio_event_loop.py
```

## 5. 实验与预期现象

实验一：把 `create_task` 和 `gather` 改成：

```python
results = []
for name, delay in [("search", 1.0), ("fetch", 0.6), ("memory", 0.2)]:
    results.append(await fake_tool(name, delay))
```

总耗时会接近 1.8 秒；原版本接近最长任务的 1.0 秒。输出中三个 `start` 会很快出现，完成顺序通常是 `memory`、`fetch`、`search`。

实验二：在协程中加入 `time.sleep(1)`，例如：

```python
time.sleep(1)  # 错误示例：阻塞事件循环
```

即使其他任务写了 `await asyncio.sleep`，它们也会被拖住。改成 `await asyncio.sleep(1)`，事件循环才能切换。

实验三：验证超时和取消：

```python
async def timeout_demo() -> None:
    try:
        await asyncio.wait_for(fake_tool("slow", 2.0), timeout=0.2)
    except asyncio.TimeoutError:
        print("tool timed out")


asyncio.run(timeout_demo())
```

预期看到 `tool timed out`。生产 Runtime 还要确认底层 HTTP 连接、文件句柄和临时状态确实被清理。

## 6. 常见误区

1. 写了 `async def` 不代表并发；没有 `await` 或 `create_task`，协程不会被调度。
2. `await` 不等于开新线程。它通常仍在事件循环线程中运行。
3. 在 async 函数里调用阻塞库会卡住所有协程。可用 `await asyncio.to_thread(blocking_fn, arg)` 把少量阻塞工作移到线程。
4. `gather` 默认会把异常传播给调用者；需要逐个检查失败时可使用 `return_exceptions=True`，但不要因此吞掉错误。
5. 取消是协作式的。被取消的协程如果长时间执行纯 Python 循环且不让出控制权，无法及时响应取消。

## 7. 和 Agent Runtime 的映射

| asyncio 概念 | Agent Runtime 映射 |
| --- | --- |
| Event Loop | 在一个服务进程中驱动模型、工具和定时事件 |
| 协程 | 一次 Agent execution 的可暂停步骤 |
| `await` | 等待 LLM、MCP、数据库或人工审批结果 |
| Task | 已登记、可追踪、可取消的子任务 |
| Timeout/Cancel | 工具超时、用户取消、预算耗尽 |
| `to_thread` | 把遗留阻塞 SDK 接入异步 Runtime |

注意，事件循环只解决当前进程内的调度。进程崩溃后的恢复、跨机器排队和持久化状态仍需 Queue、StateStore 和 Scheduler。

## 8. 验收题

1. 为什么三个 `await asyncio.sleep` 的总耗时接近最长等待时间？
2. `async def` 调用后得到的是什么？何时才真正执行？
3. `time.sleep` 为什么会阻塞所有协程？
4. Task 被取消时，业务代码应该在哪里释放资源？
5. Agent 同时调用三个独立工具时，哪些工具可以 `gather`，哪些必须顺序执行？
6. 事件循环能否替代跨进程队列和持久化 checkpoint？为什么？

## 9. 官方资料

1. [asyncio - Asynchronous I/O](https://docs.python.org/3/library/asyncio.html)：模块总览。
2. [Event Loop](https://docs.python.org/3/library/asyncio-eventloop.html)：事件循环、回调和 I/O 机制。
3. [Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)：协程、Task、取消、超时和 `gather`。
4. [Running in Threads](https://docs.python.org/3/library/asyncio-task.html#running-in-threads)：`asyncio.to_thread` 的适用场景。

## 下一课

```text
事件循环能在一个进程内安排任务
-> 任务数量超过处理能力怎么办
-> Queue 保存待执行任务
-> Scheduler 决定何时取任务
-> Worker 执行、重试并报告状态
```
