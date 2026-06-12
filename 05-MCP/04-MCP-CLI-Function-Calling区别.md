# MCP、CLI 和 Function Calling 的区别

## 🎭 面试官这样问
> 面试官：你在项目里用了 MCP、CLI 和 Function Calling，那你说说这三者有什么区别？
> 你：它们都是用来让模型调用外部工具的。MCP 是协议，Function Calling 是模型能力，CLI 是命令行。
> 面试官：这个回答太标签化了。我问你——能不能只用 Function Calling 不用 MCP？能不能只用 CLI 不用 Function Calling？如果我让你设计一个"查询 Git 状态"的功能，这三者分别出现在哪里？
> 你：Function Calling 用来让模型选择工具……MCP 用来连接工具……CLI 用来执行命令……但它们的边界我不太确定。
> 面试官：核心是你把三者当成了"同一层的三种选择"，但它们根本不在同一层。Function Calling 是模型的"嘴巴"——决定说什么；MCP 是"电话线"——决定怎么连到对方；CLI 是对方"手上的工具"——决定怎么干活。嘴巴、电话线、工具，能混在一起比吗？
> 这个类比就是今天我们要彻底讲清楚的事——三层分工，一层都不能乱。

## 💡 简要回答（面试话术）

MCP、CLI 和 Function Calling 经常被混在一起讨论，但它们处于三个完全不同的工程层次。一句话分清楚：**Function Calling 是模型接口层，MCP 是连接协议层，CLI 是系统执行层。** 这三者不是"选 A 还是选 B"的关系，而是可以串在一起协同工作的。

你可以这样记：Function Calling 回答"模型怎么表达'我要调哪个工具'"——它把自然语言变成结构化的函数名和参数。MCP 回答"Host 怎么找到并连上这个工具"——它定义了发现、连接、调用的标准协议。CLI 回答"这个工具在操作系统里怎么真正执行"——它是具体的命令行程序，有 stdin/stdout/stderr 和退出码。

它们协同工作时是一条链：模型通过 Function Calling 选择了一个来自 MCP Server 的 tool，MCP Server 内部可能调用了一个受限的 CLI 命令来完成任务。比如你问"当前 Git 分支改了什么"，模型用 Function Calling 选 `get_git_status`，这个 tool 在 Git MCP Server 里，Server 内部执行了 `git diff --name-only`，然后把结果结构化返回。模型、MCP、CLI 各司其职，没有谁替代谁。

面试中能把这"三层"讲清楚，并且举出一个串联的例子，面试官就知道你不是在背概念，是真的理解了架构。

![三者所在的工程层次](https://gitee.com/linkio666/image/raw/main/05-MCP/04-mcp-vs-cli-fc/01-概念总览.png)

## 📝 详细解析

### 核心矛盾：都和"工具调用"有关，但解决的是完全不同的问题

很多人在第一次接触 MCP 时会问："这不就是 Function Calling 加了个协议吗？"或者"CLI 不就能执行命令吗，为什么还要 MCP？"这些问题的根源是没有区分开三个工程问题：

- **表达问题**：模型怎么告诉系统"我要调用哪个工具，参数是什么"？→ Function Calling 解决的。
- **连接问题**：系统怎么发现有哪些工具可用、怎么连上这些工具、怎么复用？→ MCP 解决的。
- **执行问题**：工具在操作系统里怎么真正运行、怎么管理权限和副作用？→ CLI 解决的（或者是 Server 内部的其他执行方式）。

三者混淆会带来真实的工程灾难。如果你让模型直接拼 shell 命令——"模型你自己生成一条命令去查日志吧"——你就绕过了 Function Calling 的参数校验、绕过了 MCP 的权限治理、绕过了能力描述和审计。模型可能生成 `cat /etc/passwd` 或者 `rm -rf /tmp/*`，而没有任何一层在拦截。反之，如果你不用 MCP，把每个 CLI 工具都手写进 Host 代码里，那换一个 Host 就要重新写一遍，完全无法复用。

所以说，这三者的区分不是学术讨论，而是直接影响系统安全性和可维护性的工程决策。

### 底层机制：三个层次，三种角色

**第一层——模型接口层：Function Calling。**

Function Calling 是模型厂商提供的接口能力。它的核心工作是把用户的自然语言意图翻译成结构化的函数调用请求。比如用户说"帮我查一下订单 12345 的状态"，模型通过 Function Calling 输出：

```json
{
  "name": "get_order_status",
  "parameters": {
    "order_id": "12345"
  }
}
```

Function Calling 的关键贡献是**结构化**。模型不是输出一段自由文本让你去解析，而是输出一个严格符合 schema 的函数名和参数。这让下游系统可以安全、可靠地消费模型的意图。但 Function Calling 不关心这个函数是谁实现的、部署在哪里、需要什么权限——它只是"把话说清楚"。

**第二层——连接协议层：MCP。**

MCP 回答的是"这些函数从哪来、怎么发现、怎么连"。它不生成函数调用，而是提供了一套标准协议让 Host 能发现 Server 暴露的 tools、resources 和 prompts。MCP 的核心贡献是**标准化连接**。一个 MCP Server 写好后，可以被任何实现了 MCP Client 的 Host 使用——不管这个 Host 是 VS Code、JetBrains IDE、Web 助手还是命令行 Agent。MCP Server 内部可以是一个数据库、一个文件系统、一个 HTTP API，甚至是——一个封装好的 CLI 调用。MCP 不管你能力是怎么实现的，它只负责"把能力登记好，把请求传到位，把结果带回来"。

**第三层——系统执行层：CLI。**

CLI 是最底层——它是操作系统里的真实程序。`git status`、`kubectl get pods`、`python script.py`，这些都是 CLI。CLI 强大但危险：参数拼接可能被注入、环境变量可能被泄露、工作目录可能越界、退出码可能被忽略。直接让模型接触 CLI 是大忌。正确的做法是把 CLI 封装在一个 MCP Server 内部：只暴露有限的命令、限制参数范围、固定工作目录、设置超时、解析输出成结构化格式、把退出码映射成 MCP 错误码。这样模型通过 Function Calling 看到的是一组安全的 tool，而不是"随便你想跑什么命令都行"的万能接口。

一个精妙的类比：把这三层想象成"打电话点外卖"。Function Calling 是你的嘴巴——把"我要一份黄焖鸡米饭"说出来。MCP 是电话系统——把你的声音编码、传输、找到正确的餐馆、接通。CLI 是餐馆后厨——真正在炒菜。嘴巴不会自己炒菜，电话线不会替你点菜，厨师不会接电话——三层各干各的，但缺一层你都吃不上饭。

![Function Calling、MCP 和 CLI 的协同调用](https://gitee.com/linkio666/image/raw/main/05-MCP/04-mcp-vs-cli-fc/02-运行机制.png)

### 工程例子：查询 Git 状态的完整三层串联

假设你在 IDE 里问 AI 助手："当前分支有哪些文件被修改了？"

**第一层**，模型通过 Function Calling 输出：
```json
{
  "name": "get_git_status",
  "parameters": {
    "repo_path": "/home/user/project",
    "include_untracked": false
  }
}
```

**第二层**，这个 `get_git_status` 是一个 MCP tool，来自 Git MCP Server。Host 的 Git Client 把请求发给了 Git Server。Server 收到后做校验：`repo_path` 是否在允许范围内？`include_untracked` 是否允许为 false？校验通过。

**第三层**，Git MCP Server 内部执行了受限制的 CLI 命令：
```
cd /home/user/project && git status --short
```
注意：这不是用户或者模型拼的命令，而是 Server 代码里写死的固定命令模板。Server 只拼接了 `repo_path` 这一个参数，而且做了严格的路径校验。CLI 执行完毕后，Server 解析 `git status --short` 的文本输出，转成结构化 JSON：
```json
{
  "modified": ["src/auth.go", "src/main.go"],
  "added": ["src/utils_test.go"],
  "deleted": []
}
```

结果通过 MCP Client 返回给 Host，Host 回填给模型，模型生成回答："当前分支有 2 个文件被修改：auth.go 和 main.go，还有 1 个新文件 utils_test.go。"

整个链路里，模型没有直接执行 CLI，CLI 没有被直接暴露给用户，Function Calling 没有替代 MCP——三层紧密协作，但各守边界。

### 边界和风险：不要把任意命令暴露给模型

**直接暴露 CLI 是自杀级风险。** 如果你在 Host 里写了一个万能 tool——`execute_shell(command: string)`——那模型有可能生成任何命令。命令注入（`; rm -rf /`）、路径越界（`../../../etc/shadow`）、环境变量泄露（`echo $AWS_SECRET`）全都有可能发生。

**只用 Function Calling 不用 MCP 是扩展性灾难。** 每个工具你都得在 Host 代码里手写适配——参数怎么定义、怎么调用、怎么处理返回。当你有 20 个 Host 和 50 个工具时，维护成本是乘法级别的。

**只用 MCP 不用 Function Calling？** 技术上不通。MCP 负责连接能力，但模型仍然需要一种机制来选择工具和生成参数——这个机制就是 Function Calling（或者类似的 tool-use 接口）。两者不是"二选一"，是"上下游"。

还有一个常见误区：把 MCP 等同于"高级 CLI"。MCP Server 内部不一定要调用 CLI——它可以直接调数据库驱动、HTTP API、gRPC 服务。CLI 只是 Server 内部的一种可选实现方式。

## 🎯 面试总结

- **必答 3 点**：
  1. Function Calling 是模型接口层（解决"模型如何表达工具调用"），MCP 是连接协议层（解决"Host 如何发现和连接工具"），CLI 是系统执行层（解决"工具在 OS 中如何执行"）
  2. 三者可以串联：模型用 Function Calling 选择 MCP tool → MCP Client 发请求给 Server → Server 内部调用受限 CLI 完成任务
  3. 不能直接让模型拼 CLI 命令——必须通过 Function Calling 做参数校验、MCP Server 做权限控制、CLI 在沙箱内执行

- **加分项**：能类比"嘴巴-电话线-厨师"讲清楚三层分工；能指出 MCP 和 Function Calling 是上下游协同关系而非替代关系；能说明 MCP Server 内部不一定要用 CLI（还可以调 API、数据库驱动等）

- **一句话总结**：Function Calling 让模型"说得清"，MCP 让能力"接得上"，CLI 让命令"跑得动"——三层各管各的，串起来才是一条安全可控的工具链。

## 🔍 排查和实践建议

排查时按层定位故障：模型没选工具 → 检查 Function Calling 的 tool 描述和 schema 是否清晰；工具不存在 → 检查 MCP 能力发现是否成功、Host 是否过滤了该工具；工具调用失败 → 检查 MCP Client-Server 连接；工具执行报错 → 检查 Server 内部逻辑或 CLI 命令；结果异常 → 检查 Server 输出解析和 Host 回填。

设计原则：永远把高风险 CLI 封装在 MCP Server 内作为窄工具，永远让模型通过 Function Calling 使用这些工具，永远不要给模型一个"执行任意命令"的万能 tool。安全是从每一层收口开始的，而不是某一道防火墙能解决的。

---
[返回 05-MCP 模块目录](README.md)
