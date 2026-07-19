# AI Agent 与大模型应用开发面试笔记

![GitHub last commit](https://img.shields.io/github/last-commit/Link-990/Agent-learning?style=flat-square)
![GitHub repo size](https://img.shields.io/github/repo-size/Link-990/Agent-learning?style=flat-square)
![License](https://img.shields.io/badge/用途-学习交流-blue?style=flat-square)

面向 AI Agent、大语言模型（LLM）、RAG、MCP、Skills、微调、强化学习与 Agent 框架岗位的中文面试与工程实践笔记。

> 一份可检索、可复述、贴近工程落地的 AI 面试知识库。

这不是只背定义的题库：每篇内容都围绕“问题场景 → 核心机制 → 工程边界 → 高频追问 → 可复述答案”展开，帮助你把概念讲清楚、把方案落下来、把线上问题排查出来。

## 快速开始

| 你的目标 | 从这里开始 |
| --- | --- |
| 零基础建立主线 | [Python 基础](01-python基础/README.md) → [大模型基本框架](02-大模型基本框架/README.md) |
| 准备 RAG 面试 | [RAG 全流程](03-RAG/01-RAG全流程.md) |
| 准备 Agent 面试 | [Agent 核心组件](04-Agent/01-Agent核心组件.md) |
| 理解工具生态 | [MCP](05-MCP/README.md) → [Skills](06-Skills/README.md) |
| 复习训练与对齐 | [微调](07-微调/README.md) → [强化学习](08-强化学习/README.md) |

## 适合搜索的问题

- AI Agent 面试题、LLM 应用开发面试题
- RAG 全流程、分块、Embedding、混合检索、Rerank 与评测
- Agent 与 Workflow、Function Calling、Memory、Multi-Agent
- MCP 核心组件、调用流程、通信机制与安全边界
- Skills 渐进式披露、MCP/CLI/Function Calling 对比
- SFT、LoRA、QLoRA、RLHF、PPO、DPO、GRPO
- OpenAI Agents、LangChain、LangGraph、Harness 机制

## 推荐学习路径

```text
Python 基础 → 大模型基本框架 → RAG → Agent → MCP → Skills → 微调 → 强化学习 → Agent 框架
```

已有后端或算法基础，可直接从 RAG、Agent、MCP 开始；准备 RAG 岗位，优先阅读 RAG 全流程、向量模型、分块策略和检索优化；准备 Agent 岗位，优先阅读 Agent 核心组件、推理范式、工具调用、MCP 与 Harness。

## 专题目录

| 专题 | 重点内容 |
| --- | --- |
| [Python 基础](01-python基础/README.md) | 数据类型、对象模型、并发、GIL、内存管理 |
| [大模型基本框架](02-大模型基本框架/README.md) | Transformer、注意力、Decoder、生成机制、KV Cache |
| [RAG](03-RAG/README.md) | 数据处理、Embedding、分块、检索、重排、评测 |
| [Agent](04-Agent/README.md) | 规划、工具、记忆、反馈、多 Agent 与 A2A |
| [MCP](05-MCP/README.md) | Server/Client/Host、协议流程、通信与安全 |
| [Skills](06-Skills/README.md) | 能力封装、渐进式披露、与工具调用协同 |
| [微调](07-微调/README.md) | SFT、LoRA、QLoRA 等参数高效微调 |
| [强化学习](08-强化学习/README.md) | RLHF、PPO、DPO、GRPO 与对齐训练 |
| [主流 Agent 框架](09-主流Agent框架/README.md) | Agents、LangChain、LangGraph、Harness |

## 如何高效使用

1. 先看专题 README 和配图，建立知识地图。
2. 再读正文，记录输入、处理链路、输出和失败模式。
3. 合上文章，用“定义—问题—机制—边界—案例”复述。
4. 用相邻方案对比和线上排查问题检验是否真正掌握。

## FAQ

**这套笔记适合什么岗位？**
AI 应用开发、Agent 工程、RAG 工程、LLMOps、大模型后端及相关算法岗位。

**RAG 和微调怎么选？**
知识经常变化、需要引用来源时优先 RAG；需要稳定改变行为、格式或风格时考虑微调，实际项目通常组合使用。

**Agent 和 Workflow 怎么选？**
流程固定、可预测时优先 Workflow；步骤需要根据环境反馈动态变化时再引入 Agent，并设置工具权限、超时和停止条件。

## 说明

本项目用于学习、复习和面试准备。欢迎通过 Issue 或 Pull Request 修正文档、补充面试追问、工程案例和配图。
