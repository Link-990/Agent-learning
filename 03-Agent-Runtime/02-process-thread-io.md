# 第二课：进程、线程与 I/O

> 目标：理解操作系统怎样承载一次运行，以及为什么等待 I/O 时需要并发设计。

> 语言说明：本课的 Python 示例只是实验载体，进程、线程和 I/O 的模型适用于 Java、Go、Node.js 等 Runtime。

第一课把任务放在一个 Python 进程里同步执行。本课向下走一层，观察进程、线程、内存和 I/O 的边界。先记住：**并发是安排多个任务交错推进，并行是多个 CPU 核心同时执行。**

## 1. 学习目标

- 区分进程、线程和函数调用。
- 判断任务受 CPU 还是 I/O 影响。
- 理解线程共享地址空间、进程隔离地址空间的代价。
- 能解释为什么 I/O 型 Runtime 常用线程池，CPU 型任务常用进程池。

## 2. 问题场景：一个任务为什么会拖住其他任务

假设 Agent Runtime 同时收到三个请求：读取网页、查询数据库、生成报告。读取网页时，CPU 可能几乎没事做，但程序在等待网卡和远端服务器。如果 Runtime 只有一个执行路径，其他两个请求也只能排队。

```text
单线程：读取网络 ---- 等待 ---- 返回
        查询数据库            （只能等）

多线程：读取网络 ---- 等待 ---- 返回
        查询数据库 -- 等待 -- 返回
        生成报告        执行
```

线程解决的是同一进程内的并发安排；它不会让单个 CPU 核心突然变成两个核心。

## 3. 底层机制

### 3.1 进程：资源隔离的运行容器

进程通常拥有独立的虚拟地址空间、文件描述符表和环境。操作系统可以暂停一个进程、恢复另一个进程，也可以在进程异常退出后回收它的资源。

对 Runtime 来说，进程适合承载隔离性要求高的工作：不可信代码、容易崩溃的插件、需要利用多核 CPU 的计算任务。代价是创建和通信成本更高，数据不能直接共享，需要管道、队列或文件等 IPC 机制。

### 3.2 线程：共享进程资源的执行路径

同一进程中的线程共享堆、模块和打开的文件，但每个线程有自己的栈和指令位置。共享让线程传递数据很方便，也带来竞态条件：两个线程可能同时修改同一个变量。

默认 CPython 构建包含 GIL，纯 Python CPU 计算通常不能靠多个线程获得真正的多核并行；等待 socket、文件等 I/O 时，线程可以释放执行机会，因此仍然适合 I/O 型任务。Python 也提供 free-threaded 构建作为例外选项，但它不是所有发行版的默认构建，不能把该行为泛化到所有 Python 环境。

### 3.3 I/O：程序把时间交给外部设备

一次 I/O 大致经历：发起请求、等待设备或远端响应、收到数据、继续执行。阻塞 I/O 会让当前线程停在系统调用上；非阻塞 I/O 会立即返回，再由事件循环或其他机制通知“可以继续读写”。

```text
业务代码 -> Python 标准库 -> 系统调用 -> 网卡/磁盘
                                  |
                                  +-- 等待期间，线程可能被挂起
```

## 4. 可运行实验：线程并发 I/O，进程并行 CPU

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import os
import threading
import time


def io_task(number: int) -> str:
    time.sleep(0.5)  # 模拟等待网络或磁盘
    return f"io-{number} thread={threading.current_thread().name}"


def cpu_task(number: int) -> tuple[int, int, int]:
    total = sum(i * i for i in range(350_000))
    return number, total, os.getpid()


if __name__ == "__main__":
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(io_task, range(3)))
    print("thread results:", results)
    print("thread elapsed:", round(time.perf_counter() - started, 2), "s")

    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(cpu_task, range(2)))
    print("parent pid:", os.getpid(), "process results (includes worker pid):", results)
    print("process elapsed:", round(time.perf_counter() - started, 2), "s")
```

对应实验脚本是 [`labs/02_process_thread_io.py`](labs/02_process_thread_io.py)，直接运行：

```powershell
python 03-Agent-Runtime/labs/02_process_thread_io.py
```

## 5. 实验与预期现象

实验一：把 `max_workers=3` 改成 `1`。三个 `sleep(0.5)` 会接近 1.5 秒；三个线程并发时通常接近 0.5 秒。这个差异来自等待时间重叠，不代表 CPU 计算速度提高了三倍。

实验二：把 `io_task` 改成短循环，观察线程收益下降。再增加 `cpu_task` 的循环次数，比较线程池和进程池，并查看结果中的 worker PID。进程 PID 与父进程不同，说明 CPU 工作确实交给了子进程；机器核心数、任务大小和进程启动开销都会影响结果，所以只观察趋势，不把示例耗时当作固定基准。

实验三：给线程任务共享一个普通整数并循环递增。结果可能小于预期，说明“读、改、写”不是一个不可分割的操作。使用 `threading.Lock` 包住临界区，再比较结果。

## 6. 常见误区

1. 线程不等于并行。默认 CPython 的 I/O 型线程能交错等待，纯 Python CPU 代码受 GIL 影响；free-threaded 构建是需要单独确认的例外。
2. 进程不是“更快的线程”。它需要序列化参数、启动子进程和传回结果。
3. 共享变量不等于安全变量。共享内存减少通信，却要求锁、队列或其他同步协议。
4. `sleep` 只是模拟等待。真实网络调用还要设置超时、取消和连接关闭。
5. 不要把线程池无限扩大。线程太多会消耗内存、连接数和上下文切换时间。

## 7. 和 Agent Runtime 的映射

| 基础概念 | Agent Runtime 映射 |
| --- | --- |
| 进程 | 隔离某个 Worker、插件或不可信工具 |
| 线程 | 并发处理多个阻塞式工具调用 |
| I/O 等待 | LLM、MCP、数据库、文件和 HTTP 请求等待 |
| 锁/队列 | 保护共享会话状态，避免并发写坏 checkpoint |
| 进程退出 | Worker 崩溃，需要由上层检测并重试或恢复 |

Runtime 需要先决定任务性质，再选择执行模型：短 CPU 计算可以进程化；大量等待可以线程化或异步化；不可信工具还要增加权限和资源隔离。

## 8. 验收题

1. 为什么三个 `sleep` 在线程池中可以重叠？
2. 线程共享哪些资源，进程之间为什么不能直接共享普通 Python 对象？
3. GIL 对 I/O 型任务和 CPU 型任务的影响分别是什么？
4. Agent 调用 MCP 工具时，哪些部分是 I/O，哪些部分可能是 CPU？
5. 两个 Worker 同时更新同一个任务状态，怎样避免后写覆盖先写？
6. 什么时候应该选择进程隔离而不是线程池？

## 9. 官方资料

1. [Python `threading`](https://docs.python.org/3/library/threading.html)：线程、锁和条件变量。
2. [Python `concurrent.futures`](https://docs.python.org/3/library/concurrent.futures.html)：线程池和进程池接口。
3. [Python multiprocessing](https://docs.python.org/3/library/multiprocessing.html)：进程、队列与进程间通信。
4. [Python glossary: global interpreter lock](https://docs.python.org/3/glossary.html#term-global-interpreter-lock)：CPython GIL 的术语说明。

## 下一课

```text
线程可以并发等待，但每个线程仍有成本
-> 协程把等待交给事件循环
-> asyncio.Task 与 Future
-> 不阻塞事件循环
-> 用异步 Runtime 管理大量 I/O
```
