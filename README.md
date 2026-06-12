# AI Agent 与大模型应用开发面试笔记

这是一套面向 **AI Agent、大模型应用开发、RAG、MCP、微调与强化学习** 方向的系统化面试学习笔记。

我整理这套内容的目的不是简单堆概念，也不是把零散八股题拼在一起，而是希望用更接近真实面试和工程实践的方式，把每个知识点讲清楚：它解决什么问题、为什么会出现、底层机制是什么、工程上容易在哪里翻车、面试官会怎么追问，以及最后应该怎样组织成一段能复述的答案。

每个考点都尽量按照下面的逻辑展开：

```text
真实问题 / 失败场景
  → 核心矛盾
  → 底层机制
  → 工程例子
  → 适用边界和失败模式
  → 高频面试追问
  → 可复述答案
  → 排查和实践建议
```

如果你正在准备 AI 应用开发、Agent 工程、大模型后端、RAG 工程、LLMOps 或相关岗位，希望这份笔记能帮你从“知道这个词”走到“能讲清楚、能抗追问、能联系工程落地”。

## 这份笔记适合谁

这份笔记更适合下面几类读者：

- 准备 **AI Agent / 大模型应用开发** 方向面试的同学。
- 已经听过 RAG、Agent、MCP、Function Calling、LoRA、RLHF 等概念，但回答不成体系的人。
- 有后端、算法或 Python 基础，想转向大模型应用工程的人。
- 想系统复习 AI 应用开发八股，但不想只背定义的人。
- 想把“面试答案”和“真实工程问题”联系起来的人。

如果你完全没有编程基础，建议先补 Python、HTTP API、数据库、基础机器学习和深度学习常识，再阅读后面的 RAG、Agent 和微调部分。

## 应该如何学习

不要把这套笔记当成普通题库从头背到尾。更推荐用下面的方法学习。

### 第一步：先建立主线

先快速浏览每个模块的 README 或目录，搞清楚这套知识在大模型应用开发里的位置：

```text
Python 是基础工程能力
Transformer 是模型底层机制
RAG 解决外部知识接入
Agent 解决多步任务执行
MCP / Skills 解决工具和能力组织
微调解决稳定行为适配
强化学习解决偏好对齐
Agent 框架解决工程编排和运行时问题
```

先有这条主线，后面看单篇文章就不容易迷路。

### 第二步：每篇文章按“三遍法”阅读

第一遍只看标题、开头场景和图，回答一个问题：

```text
这个知识点到底在解决什么问题？
```

第二遍认真看机制拆解和工程例子，尝试自己画出流程：

```text
输入是什么？
中间经过哪些步骤？
输出是什么？
哪里可能失败？
```

第三遍只看“高频追问”和“可复述答案”，关掉文章后自己复述一遍。如果复述时只能说概念，讲不出例子，说明还没真正掌握。

### 第三步：用面试官视角追问自己

每个知识点至少追问三层：

```text
是什么？
为什么需要它？
不用它会怎样？
它和相邻方案有什么区别？
工程上怎么落地？
线上出问题怎么排查？
```

比如学习 RAG 时，不要只背“检索增强生成”，还要能回答：

- 为什么 RAG 不能完全消除幻觉？
- chunk 太大和太小分别有什么问题？
- 为什么生产系统常用混合检索？
- 召回到了正确文档但答案还是错，可能是哪一层出问题？

学习 Agent 时，不要只背“规划、工具、记忆”，还要能回答：

- 工具调用成功是否代表任务成功？
- Agent 和 Workflow 到底怎么选？
- 什么时候不应该上 Agent？
- 如何防止 Agent 无限循环或越权调用工具？

### 第四步：把答案压缩成自己的版本

文章里的“可复述答案”不是让你逐字背，而是给你一个组织结构。你应该把它压缩成自己的表达。

一个比较好的面试回答通常是：

```text
先给一句定义
再说解决的问题
然后讲核心机制
接着讲工程边界
最后补一个排查或实践经验
```

例如回答 “SFT 和 RAG 的区别” 时，不要只说一个改参数、一个不改参数，还要继续说：

```text
SFT 更适合稳定行为和输出格式，RAG 更适合可更新、可追溯的外部知识。
如果业务政策经常变化，我不会用 SFT 把政策写进模型参数，而会用 RAG 接知识库，用 SFT 规范回答风格和拒答边界。
```

这样的答案才更像真实做过项目的人。

## 推荐学习路线

如果你是从零开始准备 AI 应用开发方向面试，建议按下面顺序学习：

```text
01 Python 基础
  → 02 大模型基本框架
  → 03 RAG
  → 04 Agent
  → 05 MCP
  → 06 Skills
  → 07 微调
  → 08 强化学习
  → 09 主流 Agent 框架
```

这条路线适合从基础能力逐步走到应用工程。

如果你已经有后端或算法基础，想快速准备大模型应用岗位，可以优先看：

```text
03 RAG
  → 04 Agent
  → 05 MCP
  → 06 Skills
  → 07 微调
  → 08 强化学习
  → 09 主流 Agent 框架
```

如果你主要准备 RAG 工程岗位，可以重点看：

```text
02 大模型输入到输出运行机制
03 RAG 全流程
03 向量模型选型及区别
03 分块策略选型
03 向量检索和关键词检索区别
03 检索优化策略
07 监督微调
```

如果你主要准备 Agent 工程岗位，可以重点看：

```text
04 Agent 核心组件
04 Agent 推理范式
04 Agent 和 Workflow 区别
04 Function Calling 工具调用
05 MCP 核心组件
05 MCP 调用流程
06 Skills 实现方式
09 Harness 机制
09 Claude Code 中的 Harness 实现
09 LangChain、LangGraph 与简单 Agent 搭建
```

## 内容特点

- **模块化组织**：覆盖 Python 基础、大模型框架、RAG、Agent、MCP、Skills、微调、强化学习、主流 Agent 框架。
- **每个考点独立成文**：方便单篇阅读、复习、收藏和发布到博客平台。
- **问题驱动写法**：从真实失败现象和面试追问切入，而不是直接堆定义。
- **配套图解**：每个考点配有概念总览、运行机制、面试答题框架等图。
- **面试导向**：重点关注如何组织答案、如何应对追问、如何联系工程场景。
- **工程边界意识**：不仅讲“怎么做”，也讲“不适合什么场景”和“线上怎么排查”。

## 目录

### 01. Python 基础

Python 基础部分主要用于补齐 AI 应用开发中常见的工程语言能力。面试里很多大模型应用问题最终还是会落到数据结构、对象引用、并发模型、内存管理和 Python 运行机制上。

- [基础数据类型](01-python-basics/01-basic-types.md)
- [可变与不可变数据类型](01-python-basics/02-mutable-immutable.md)
- [装饰器与生成器](01-python-basics/03-decorators-generators.md)
- [深拷贝与浅拷贝](01-python-basics/04-deep-shallow-copy.md)
- [并发与并行](01-python-basics/05-concurrency-parallelism.md)
- [多线程实现与 GIL](01-python-basics/06-threading-gil.md)
- [Python 内存管理方式](01-python-basics/07-memory-management.md)

### 02. 大模型基本框架

这一部分帮助你理解大模型为什么能处理上下文、为什么推理是逐 token 生成、为什么长上下文会变慢，以及 KV Cache 为什么会影响推理成本。

- [Transformer 架构和核心组件](02-llm-framework/01-transformer.md)
- [自注意力机制](02-llm-framework/02-self-attention.md)
- [Encoder-Only 和 Decoder-Only 模型区别](02-llm-framework/03-encoder-decoder.md)
- [大模型输入到输出运行机制](02-llm-framework/04-llm-io.md)
- [KV 缓存](02-llm-framework/05-kv-cache.md)

### 03. RAG

RAG 是大模型应用开发面试中的高频核心模块。学习时重点关注知识从哪里来、如何被切分和召回、为什么召回到了也可能答错，以及如何建立评测和排查链路。

- [RAG 全流程](03-RAG/01-rag-overview.md)
- [向量模型选型及区别](03-RAG/02-embedding-models.md)
- [分块策略选型](03-RAG/03-chunking.md)
- [向量检索和关键词检索区别](03-RAG/04-vector-vs-keyword.md)
- [检索优化策略](03-RAG/05-retrieval-optimization.md)

### 04. Agent

Agent 部分重点不是“模型会规划”，而是模型如何在受控系统里使用工具、读取反馈、管理状态和完成多步任务。学习时要特别注意 Agent 与 Workflow 的边界。

- [Agent 核心组件](04-Agent/01-agent-core.md)
- [Agent 推理范式](04-Agent/02-agent-reasoning.md)
- [Agent 和 Workflow 区别](04-Agent/03-agent-vs-workflow.md)
- [记忆管理](04-Agent/04-memory.md)
- [Function Calling 工具调用](04-Agent/05-function-calling.md)
- [Multi-Agent 架构通信机制与 A2A](04-Agent/06-multi-agent-a2a.md)

### 05. MCP

MCP 部分关注模型与外部工具、资源、提示词能力之间的标准化连接方式。学习时要把 MCP 和 Function Calling、CLI、普通 HTTP API 区分开。

- [MCP 核心组件](05-MCP/01-mcp-core.md)
- [MCP 调用流程](05-MCP/02-mcp-flow.md)
- [MCP 通信机制](05-MCP/03-mcp-comm.md)
- [MCP、CLI、Function Calling 区别](05-MCP/04-mcp-vs-cli-fc.md)
- [MCP 优缺点](05-MCP/05-mcp-pros-cons.md)

### 06. Skills

Skills 可以理解为面向任务的能力包。学习时重点看它如何通过渐进式披露降低上下文成本，以及它和 MCP、CLI、Function Calling 如何协同。

- [Skills 实现方式](06-Skills/01-skills-impl.md)
- [Skills 渐进式披露特点](06-Skills/02-skills-disclosure.md)
- [MCP、CLI、Skills、Function Calling 区别与协同](06-Skills/03-mcp-cli-skills-fc.md)
- [Skills 优缺点](06-Skills/04-skills-pros-cons.md)

### 07. 微调

微调部分重点是理解“行为适配”和“知识更新”的区别。SFT、LoRA、QLoRA、Prefix Tuning、Prompt Tuning 解决的问题不同，更新的参数范围也不同。

- [监督微调](07-finetuning/01-sft.md)
- [参数高效微调方法](07-finetuning/02-peft.md)

### 08. 强化学习

强化学习部分主要用于理解大模型对齐。学习时重点区分 RLHF、PPO、DPO、GRPO 的训练信号、优化目标和工程代价，而不是只背缩写。

- [RLHF：基于人类反馈的强化学习](08-rl/01-rlhf.md)
- [PPO](08-rl/02-PPO.md)
- [DPO](08-rl/03-DPO.md)
- [GRPO](08-rl/04-GRPO.md)

### 09. 主流 Agent 框架

框架部分重点是理解框架为什么存在：它们解决的是工具编排、状态管理、运行时边界、可观测性和工程协作问题，而不是单纯的名词对比。

- [OpenAI Agents 和 Hermes 区别](09-agent-frameworks/01-openai-vs-hermes.md)
- [Harness 机制](09-agent-frameworks/02-harness.md)
- [Claude Code 中的 Harness 实现](09-agent-frameworks/03-claude-harness.md)
- [LangChain、LangGraph 与简单 Agent 搭建](09-agent-frameworks/04-langchain-langgraph.md)

## 如何使用配图

每篇文章通常包含三类图：

- **概念总览图**：适合第一遍建立整体框架。
- **运行机制图**：适合理解流程、链路和中间状态。
- **面试答题框架图**：适合复习前快速回忆答案结构。

建议学习时先看图，再读正文，最后根据图自己复述。面试前可以只扫每篇文章的第三张图，用来快速恢复记忆。

## 如何贡献

欢迎提交 Issue 和 Pull Request，一起完善这套笔记。

你可以贡献的方向包括：

- 修正文章中的技术错误或表述不准确之处。
- 补充真实面试追问和更好的回答方式。
- 增加工程案例、线上排查经验和踩坑记录。
- 优化文章结构，让内容更适合初学者阅读。
- 补充或优化配图。
- 新增更多 AI 应用开发相关主题。

提交 PR 时建议说明：

```text
修改了哪篇文章
为什么要改
改动解决了什么问题
是否影响图片或目录链接
```

如果你发现某篇文章讲得不够深入，也欢迎直接开 Issue 指出具体位置。越具体越容易改，例如“RAG 检索优化里缺少 rerank 评估指标”会比“这篇不够好”更容易处理。

## 说明

本项目内容主要用于学习、复习和面试准备。文章中的图解位于 [images](images/) 目录，Markdown 中使用相对路径引用，适合在 GitHub 中直接阅读。

如果你觉得这份笔记对你有帮助，欢迎 Star、Fork，也欢迎提交合并请求一起完善。
