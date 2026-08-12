# Agent 面试文档 v1

## 这套文档解决什么问题

这是一套面向 AI 应用开发、Agent 工程、RAG 工程和大模型应用后端岗位的面试笔记。

它不追求把所有概念都写成百科，而是训练你回答面试官最常见的五层问题：

```text
它是什么 -> 解决什么问题 -> 底层怎么工作 -> 项目里怎么落地 -> 代价和边界是什么
```

文档中的“飞书场景”只是企业协作类项目的示例，用来把 Agent 放进真实业务里理解。它不是飞书 API 使用手册，也不是只面向飞书岗位的题库。

## 适用岗位

- AI 应用开发工程师
- Agent 工程师
- RAG 工程师
- LLM 应用后端工程师
- AI 产品经理技术面试

## 推荐学习路径

1. 先看 Agent、LLM 和 Workflow 的边界。
2. 再看 Agent 的组件和运行循环，搞清楚系统到底如何执行。
3. 然后学习 ReAct、Plan-and-Execute、Reflection 等设计范式。
4. 接着补任务拆分、规划、记忆和上下文工程。
5. 最后学习 Single-Agent 与 Multi-Agent 的架构取舍。

## 每篇文章的固定结构

```text
面试官追问
-> 常见错误回答
-> 30 秒简答
-> 原理拆解
-> 企业协作场景
-> 工程方案与取舍
-> 继续追问
-> 面试总结
```

阅读时不要只背“30 秒简答”。建议合上文章，自己按下面五句话重新回答：

```text
定义是什么？
它解决了什么问题？
它是怎么工作的？
什么场景适合用？
它的成本、风险和边界是什么？
```

## 目录

| 文件 | 主题 | 重点 |
| --- | --- | --- |
| `01-agent-vs-llm-workflow.md` | Agent、LLM、Workflow 的区别 | 解释决策权和流程控制权属于谁 |
| `02-agent-components-and-loop.md` | Agent 核心组件与 Agent Loop | 解释从用户请求到最终答案的完整链路 |
| `03-agent-patterns.md` | ReAct、Plan-and-Execute、Reflection | 根据任务特征做范式选型 |
| `04-task-planning-memory-context.md` | 任务拆分、规划、记忆、上下文 | 解释复杂任务为什么失败以及怎么稳定它 |
| `05-single-vs-multi-agent.md` | Single-Agent 与 Multi-Agent | 判断多 Agent 是否真的值得引入 |

## 后续扩展

第一版先把 Agent 主线写清楚。后续可以继续增加 Function Calling、MCP、Skills、RAG、评测、安全、LangGraph、Harness 和项目系统设计。
