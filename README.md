# Agent-learning：从大模型基础到 Agent Runtime

这是一个面向 AI Agent、RAG、MCP 和大模型应用工程的中文学习仓库。内容按“先理解运行机制，再动手搭建系统，最后准备面试”的顺序整理，文章配有流程图、代码片段和工程边界说明。

## 先从这里开始

| 目标 | 推荐入口 |
| --- | --- |
| 第一次系统学习 | [学习导航](00-学习导航/README.md) |
| 理解 Agent Runtime | [Agent Runtime 课程](03-Agent-Runtime/README.md) |
| 准备 Agent / 应用工程岗位 | [Agent 核心原理](02-Agent核心原理/README.md) → [Runtime](03-Agent-Runtime/README.md) → [企业级工程化](07-企业级工程化/README.md) |
| 准备 RAG 岗位 | [RAG 与知识库](04-RAG与知识库/README.md) |
| 学习工具调用和 MCP | [工具、协议与能力封装](05-工具、协议与能力封装/README.md) |
| 学习 LangGraph、LangChain 等框架 | [Agent 框架](06-Agent框架/README.md) |
| 准备系统设计和项目面试 | [系统设计](09-系统设计/README.md) → [项目深挖与模拟面试](10-项目深挖与模拟面试/README.md) |
| 学习 SFT、LoRA、RLHF、DPO、GRPO | [模型训练与对齐](90-模型训练与对齐/README.md) |

## 主学习路径

```text
学习导航
  -> 基础与模型
  -> Agent 核心原理
  -> Agent Runtime
  -> RAG 与知识库
  -> 工具、协议与能力封装
  -> Agent 框架
  -> 企业级工程化
  -> 场景实战
  -> 系统设计
  -> 项目深挖与模拟面试
```

模型训练与对齐是独立分支，不是 Agent 应用开发的前置条件：

```text
基础与模型 -> 模型训练与对齐
```

## 课程目录

| 阶段 | 目录 | 学完之后能够回答 |
| --- | --- | --- |
| 00 | [学习导航](00-学习导航/README.md) | 我应该先学什么，怎样做实验和复习？ |
| 01 | [基础与模型](01-基础与模型/README.md) | 程序、线程、内存和模型是怎样运行的？ |
| 02 | [Agent 核心原理](02-Agent核心原理/README.md) | LLM、Agent、Workflow 和 Memory 的边界是什么？ |
| 03 | [Agent Runtime](03-Agent-Runtime/README.md) | 一次 Run 如何被调度、约束、恢复和审计？ |
| 04 | [RAG 与知识库](04-RAG与知识库/README.md) | 外部知识如何接入、检索、授权和评测？ |
| 05 | [工具、协议与能力封装](05-工具、协议与能力封装/README.md) | 模型意图如何变成安全的工具调用？ |
| 06 | [Agent 框架](06-Agent框架/README.md) | 各框架怎样映射 State、Tool、Workflow 和 Runtime？ |
| 07 | [企业级工程化](07-企业级工程化/README.md) | 系统怎样做到安全、可观测、可限流和可上线？ |
| 08 | [场景实战](08-场景实战/README.md) | 企业协作中的 Agent 应该怎样拆解？ |
| 09 | [系统设计](09-系统设计/README.md) | 如何从需求推导出可上线的 Agent 架构？ |
| 10 | [项目深挖与模拟面试](10-项目深挖与模拟面试/README.md) | 如何用目标、边界、证据和复盘讲清项目？ |
| 90 | [模型训练与对齐](90-模型训练与对齐/README.md) | SFT、PEFT、RLHF、PPO、DPO、GRPO 怎么选？ |
| 99 | [附录](99-附录/README.md) | 术语、接口、流程图和资料在哪里查？ |

## Runtime 主线

Runtime 是本仓库新增的系统实现主线。它不依赖真实模型或外部 API，用 Python 标准库和固定 mock 实验，把抽象概念变成可观察的执行过程：

```text
程序执行
  -> 进程、线程与 I/O
  -> 事件循环与异步
  -> Queue、Scheduler、Worker
  -> State Machine 与 Workflow
  -> Agent 决策循环
  -> Tool Runtime 与 MCP
  -> Checkpoint 与 Durable Execution
  -> Context、Memory 与人工审批
  -> Observability、安全与生产化
  -> 可恢复的研究助理 Runtime
```

进入 [03-Agent-Runtime](03-Agent-Runtime/README.md) 后，每一课都沿用 `Task`、`Run`、`State`、`Event`、`Tool`、`Checkpoint` 六个术语，并要求做一次失败实验和一次复述。

## 如何阅读

每篇文章建议按下面的顺序使用：

1. 先看问题场景和总览图，明确系统要解决什么矛盾。
2. 再读机制和代码，记录输入、状态、输出和失败分支。
3. 跑对应实验或用自己的语言重写最小示例。
4. 合上文章，用“定义、问题、机制、边界、案例”复述。
5. 最后回答本仓库统一的四个 Runtime 问题：谁决定下一步，状态保存在哪里，失败后怎么办，外部能力经过什么边界。

## 旧路径说明

仓库早期的 `01-python基础`、`02-大模型基本框架`、`03-RAG`、`04-Agent`、`05-MCP`、`06-Skills`、`07-微调`、`08-强化学习` 和 `09-主流Agent框架` 目录已经按新学习路径归档。新的学习请从上面的 canonical 目录开始；旧路径的迁移说明会保留原有文章的去向。

## 贡献方式

新增课程时，请同时补充：课程 README、前置关系、一个可运行或可复现的最小实验、失败边界，以及文章中的内部链接。Runtime 实验不使用真实密钥、任意 shell 或未授权的外部网络。
