# 基础与模型

这一阶段回答两个问题：程序怎样占用执行资源，模型怎样把输入变成输出。它是 Agent 和 Runtime 的共同底座。

## 推荐顺序

1. [Python 与程序运行](01-Python与程序运行/README.md)：对象、并发、线程、GIL 和内存。
2. [大模型运行机制](02-大模型运行机制/README.md)：Transformer、Attention、生成过程和 KV Cache。

## 学习目标

- 能区分函数、线程、进程、协程和 I/O 等待。
- 能画出 Token 从输入到输出的主要路径。
- 能解释为什么 Agent Runtime 需要调度、状态和资源边界。

下一步：进入 [Agent 核心原理](../02-Agent核心原理/README.md)。
