# Runtime 资料索引

这份索引不是“链接越多越好”。阅读顺序按问题组织：先弄清一个程序怎样运行，再学习怎样调度任务，最后进入 Agent、协议和分布式恢复。

## 一、基础地基

| 顺序 | 资料 | 适合解决的问题 |
| --- | --- | --- |
| 1 | [Python Tutorial](https://docs.python.org/3/tutorial/) | 函数、异常、模块、文件和数据结构 |
| 2 | [Python `threading`](https://docs.python.org/3/library/threading.html) | 线程、锁和共享状态 |
| 3 | [Python `multiprocessing`](https://docs.python.org/3/library/multiprocessing.html) | 进程隔离和进程间通信 |
| 4 | [Python `concurrent.futures`](https://docs.python.org/3/library/concurrent.futures.html) | 线程池、进程池和统一 Future 接口 |

先读 00、01、02 课，再查这组文档。不要从 API 名字倒推运行机制，先用实验观察，再回文档确认术语。

## 二、事件循环和异步执行

- [Python `asyncio` 总览](https://docs.python.org/3/library/asyncio.html)
- [Event Loop](https://docs.python.org/3/library/asyncio-eventloop.html)
- [Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)
- [Node.js Event Loop](https://nodejs.org/learn/asynchronous-work/event-loop-timers-and-nexttick)

Python 和 Node.js 的事件循环可以对照读。它们都能安排等待中的 I/O，但都不能自动提供跨进程 Checkpoint，也不能替代任务队列。

## 三、Workflow 和 Durable Execution

- [Temporal: Understanding the platform](https://docs.temporal.io/evaluate/understanding-temporal)
- [Temporal Workflows](https://docs.temporal.io/workflows)
- [Temporal Activities](https://docs.temporal.io/activities)
- [LangGraph Durable Execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)
- [SQLite Transactions](https://sqlite.org/lang_transaction.html)
- [AWS Builders' Library: Making retries safe](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)

阅读时抓住三个词：**持久化进度、重试语义、外部副作用**。看到“自动恢复”时，要继续追问状态存在哪里，以及重复执行是否安全。

## 四、Agent Runtime 和工具协议

- [OpenAI Agents SDK for Python](https://openai.github.io/openai-agents-python/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification)
- [MCP Architecture（固定版本示例）](https://modelcontextprotocol.io/specification/2025-06-18/architecture)
- [MCP Tools](https://modelcontextprotocol.io/docs/concepts/tools)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

MCP 文档会随规范版本更新。课程里的版本化链接用于复习当时的协议结构；做真实项目时应固定目标版本，并检查 SDK 与 Server 是否兼容。

## 五、可观测性、安全和部署

- [OpenTelemetry Observability Primer](https://opentelemetry.io/docs/concepts/observability-primer/)
- [OpenTelemetry Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OWASP Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [Kubernetes Container Runtime Interface](https://kubernetes.io/docs/concepts/containers/cri/)

OpenTelemetry 记录“发生了什么”，不是调度器；CRI 规定 Kubernetes 如何调用容器运行时，也不是 Agent Runtime。读资料时始终标出它属于哪一层。

## 六、推荐阅读方法

每篇资料只做四次记录：

1. 它管理的对象是什么？
2. 它保存了什么状态？
3. 它遇到失败时保证什么、不保证什么？
4. 它和课程中哪个组件对应？

把官方文档中的名词改写成自己的状态图，再回到代码验证。读完一页 API 但没有跑过一次失败实验，通常还没有真正理解 Runtime。
