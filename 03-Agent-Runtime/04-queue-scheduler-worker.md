# 第四课：Queue、Scheduler 与 Worker

> 目标：把“调用一个函数”升级为可排队、可限流、可重试的任务执行系统。

> 语言说明：示例使用 Python 标准库模拟队列和 Worker，生产系统也可以使用 Redis、Kafka、RabbitMQ 或云队列。

前两课解决了执行路径和 I/O 等待，本课开始组装 Runtime 的最小骨架。一个可靠系统不会让 API 进程直接执行所有工作，而是把任务交给队列，由 Scheduler 和 Worker 协作完成。

## 1. 学习目标

- 说清 Queue、Scheduler、Worker 的职责边界。
- 理解生产者、消费者、背压和幂等。
- 用标准库实现带优先级、重试和优雅退出的最小 Runtime。
- 能指出内存队列与持久化队列的可靠性差异。

## 2. 问题场景：请求来了，但现在不能执行

API 收到用户请求时，可能暂时没有空闲 Worker；工具服务也可能限流。若 API 进程同步执行，连接会长时间占用，超时后任务状态还可能不明确。

```text
Producer/API -> Queue -> Scheduler -> Worker -> StateStore
                  ^          |
                  |          +-- 失败：重试或死信
                  +-- 背压：队列已满，拒绝或延迟提交
```

Queue 保存“还没执行的任务”，Scheduler 决定取哪个，Worker 负责真正运行。三者分开后，接收速度和执行速度可以独立扩展。

## 3. 底层机制

### 3.1 Queue：时间和速度的缓冲层

生产者把任务放入队列，消费者从队列取出任务。队列长度是系统压力的一个直接信号：持续增长说明提交速度超过处理能力。

有界队列比无限队列更诚实。队列满时，系统必须选择拒绝、阻塞提交、丢弃低优先级任务或扩容；无限堆积只会把故障推迟到内存耗尽。

### 3.2 Scheduler：选择顺序和时机

Scheduler 可以按 FIFO、优先级、截止时间、租户配额或重试时间选择任务。它还可以做限流、去重和超时检查，但不应把业务逻辑塞进调度器，否则难以测试和替换。

### 3.3 Worker：执行与确认

Worker 取到任务后执行 handler，成功则确认完成，失败则根据错误类型重试或标记失败。确认必须和状态更新一起设计：进程在“执行成功但尚未确认”时崩溃，任务可能再次执行，因此业务通常要做到幂等。

## 4. 核心 Python 代码：优先级队列加重试

下面保留 Runtime 的主要接口，完整的可运行脚本 [`labs/04_queue_scheduler_worker.py`](labs/04_queue_scheduler_worker.py) 使用同一套 `Job`、`PriorityQueue`、`max_retries` 和重试语义，并额外处理未知异常和带超时的优雅关闭。

```python
"""Priority queue, temporary retry, unknown errors, and safe shutdown."""

from dataclasses import dataclass, field
import queue
import threading
import time
import uuid


@dataclass(order=True)
class Job:
    priority: int
    created_at: float = field(compare=True)
    job_id: str = field(compare=False)
    attempts: int = field(default=0, compare=False)
    stop: bool = field(default=False, compare=False)


class Runtime:
    def __init__(self, worker_count: int = 2, max_retries: int = 2) -> None:
        self.jobs: queue.PriorityQueue[Job] = queue.PriorityQueue(maxsize=3)
        self.worker_count = worker_count
        self.max_retries = max_retries
        self.stop = threading.Event()
        self.threads: list[threading.Thread] = []

    def submit(self, job: Job) -> None:
        self.jobs.put(job)  # 队列满时阻塞，形成背压
        print(f"submit job={job.job_id} priority={job.priority}")

    def worker(self, number: int) -> None:
        while True:
            try:
                job = self.jobs.get(timeout=0.1)
            except queue.Empty:
                if self.stop.is_set():
                    return
                continue
            try:
                if job.stop:
                    return
                job.attempts += 1
                print(
                    f"worker={number} start job={job.job_id} "
                    f"priority={job.priority} attempt={job.attempts}"
                )
                time.sleep(0.05)
                if job.attempts == 1:
                    raise TimeoutError("temporary tool timeout")
                print(f"worker={number} success job={job.job_id}")
            except TimeoutError as exc:
                if job.attempts <= self.max_retries:
                    print(f"retry job={job.job_id} reason={exc}")
                    self.jobs.put(job)
                else:
                    print(f"failed job={job.job_id} attempts={job.attempts}")
            except Exception as exc:
                print(f"failed job={job.job_id} unexpected={type(exc).__name__}: {exc}")
            finally:
                self.jobs.task_done()

    def start(self) -> None:
        for number in range(self.worker_count):
            thread = threading.Thread(target=self.worker, args=(number,), daemon=True)
            thread.start()
            self.threads.append(thread)

    def shutdown(self, timeout: float = 5.0) -> None:
        joiner = threading.Thread(target=self.jobs.join, daemon=True)
        joiner.start()
        joiner.join(timeout)
        if joiner.is_alive():
            print("shutdown timeout: abandoning queued jobs")
            while True:
                try:
                    self.jobs.get_nowait()
                except queue.Empty:
                    break
                else:
                    self.jobs.task_done()
        self.stop.set()
        for _ in self.threads:
            self.jobs.put(Job(10**9, time.time(), "STOP", stop=True))
        for thread in self.threads:
            thread.join(timeout=timeout)
        print("all jobs completed and workers stopped")


if __name__ == "__main__":
    runtime = Runtime()
    runtime.start()
    for priority in (5, 1, 3):
        runtime.submit(Job(priority, time.time(), uuid.uuid4().hex[:6]))
    runtime.shutdown()
```

直接运行完整实验脚本：

```powershell
python 03-Agent-Runtime/labs/04_queue_scheduler_worker.py
```

## 5. 实验与预期现象

实验一：提交优先级 `5、1、3` 的任务。由于 Worker 可能已经取走第一个任务，输出不保证严格按全局优先级排序；但尚未取出的任务通常会优先选择数字更小的任务。这正是并发系统中“调度策略”和“已开始执行”之间的边界。

实验二：把 `worker_count=2` 改为 `1`。任务会串行执行，重试也会占用同一个 Worker。把它改回 `2`，可以看到不同任务交错开始。

实验三：把 `maxsize=3` 改成 `1`，快速提交很多任务。提交线程会在 `put` 处等待，队列满造成背压；这比无限创建线程更容易保护系统。

实验四：将 `worker` 中的临时失败条件改为始终抛出 `TimeoutError`。任务会执行到最大重试次数后输出 `failed`。真实系统还应记录重试时间、错误类型和最终失败原因。

## 6. 常见误区

1. Queue 不是数据库。示例使用内存队列，进程崩溃后未完成任务会丢失。
2. 重试不是免费的。没有退避、最大次数和幂等设计，重试会放大故障或重复扣款。
3. `task_done()` 必须和每次 `get()` 配对，否则 `join()` 会永久等待。
4. 优先级队列不能抢回已经被 Worker 取走的任务。
5. 守护线程方便示例退出，但生产 Worker 需要优雅关闭、超时和未完成任务转移。
6. 调度成功不等于业务成功。状态应区分 queued、running、succeeded、retrying、failed、cancelled。

## 7. 和 Agent Runtime 的映射

| 组件 | Agent Runtime 中的职责 |
| --- | --- |
| Queue | 暂存用户请求、工具调用、重试任务和人工审批后的继续执行 |
| Scheduler | 按优先级、租户配额、预算和截止时间选择 execution |
| Worker | 执行模型调用、工具调用或 Workflow 节点 |
| StateStore | 持久化 queued/running/retrying 等状态和 checkpoint |
| Dead-letter queue | 保存多次失败、等待人工处理的任务 |
| Idempotency key | 防止重试导致重复写入、重复扣费或重复发送消息 |

一次 Agent execution 可以这样流动：

```text
用户请求
  -> API 创建 execution_id
  -> Queue 排队
  -> Scheduler 选中
  -> Worker 调用模型或工具
  -> StateStore 保存观察结果
  -> 继续入队 / 请求审批 / 输出最终答案
```

这套结构解释了为什么 Agent Runtime 不能只是一段 `while` 循环：它需要在进程、网络和服务重启后仍能知道任务处于哪个阶段。

## 8. 验收题

1. Queue、Scheduler、Worker 各自负责什么，为什么不合并成一个类？
2. 有界队列如何产生背压？API 应该怎样向用户表达队列已满？
3. Worker 在业务成功后、确认前崩溃，会发生什么？如何用幂等键降低风险？
4. 哪些 Agent 错误适合重试，哪些应该直接失败或请求人工介入？
5. 为什么优先级队列不能保证所有输出严格按优先级出现？
6. 内存队列升级到 Redis、数据库或消息系统时，需要补上哪些可靠性语义？

## 9. 官方资料

1. [Python `queue`](https://docs.python.org/3/library/queue.html)：线程安全队列和 `task_done`/`join`。
2. [Python `threading`](https://docs.python.org/3/library/threading.html)：线程生命周期与同步原语。
3. [Python `concurrent.futures`](https://docs.python.org/3/library/concurrent.futures.html)：Executor/Worker 风格的标准库接口。
4. [Python `heapq`](https://docs.python.org/3/library/heapq.html)：优先级队列的底层堆结构。

## 下一课

```text
任务能排队和重试
-> 状态怎样持久化
-> Workflow 节点怎样推进
-> Checkpoint 怎样支持暂停、恢复和人工审批
```
