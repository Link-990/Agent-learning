# 附录 A：Python 实验环境（可选）

> 目标：如果你选择使用本目录的 Python 实验，补齐运行脚本所需的最小语法。本附录不是 Runtime 的前置课程。

这一课不是完整的 Python 教程，只补 Runtime 学习所需的最小地基。你已经有一套更完整的 Python 笔记，本课只把后面反复出现的语法串起来。

## 1. 先确认环境

在 PowerShell 中运行：

```powershell
python --version
python -c "print('python is ready')"
```

课程实验只使用 Python 标准库，不需要 API Key，也不会访问真实业务系统。建议使用 Python 3.10 或更高版本。

## 2. 变量、函数和返回值

```python
def double(value: int) -> int:
    return value * 2


number = 21
result = double(number)
print(result)
```

执行顺序是：先把函数定义加载进来，再把 `number` 绑定到整数对象，最后调用函数并把返回值绑定到 `result`。

Runtime 课程里，业务函数通常就是这种形式：接收输入，完成一小段工作，返回结果。Runtime 会在函数外面管理状态、日志、超时和错误。

## 3. 字典和 JSON

Runtime 不只传递字符串，还要传递结构化状态：

```python
state = {
    "run_id": "run-001",
    "status": "running",
    "step": 1,
}
```

Python 字典是程序内存中的对象；JSON 是一种可以写入文件或通过网络传输的文本格式：

```python
import json

encoded = json.dumps(state, ensure_ascii=False)
decoded = json.loads(encoded)
print(encoded)
print(decoded["run_id"])
```

后面保存 `Checkpoint` 时，通常就是把 State 序列化成 JSON 或数据库记录。

## 4. 异常和模块入口

```python
def divide(left: int, right: int) -> float:
    return left / right


try:
    print(divide(10, 0))
except ZeroDivisionError as exc:
    print({"status": "failed", "error": str(exc)})
```

Runtime 会把异常转换成任务可以理解的结果，例如 `failed`、`retrying` 或 `waiting_for_human`。但不能无条件吞掉异常，否则系统会把失败误报成成功。

实验文件通常使用下面的入口：

```python
def main() -> None:
    print("run lesson")


if __name__ == "__main__":
    main()
```

直接运行文件时，`__name__` 等于 `"__main__"`；被导入时，`main()` 不会自动执行。

## 5. 本课实验

```powershell
python 03-Agent-Runtime/labs/00_environment.py
```

实验会打印一份 Python 字典、它的 JSON 表示，以及一次被捕获的异常。观察同一份状态如何在“程序对象”和“可传输文本”之间转换。

## 6. 验收题

1. 函数的参数、返回值和副作用分别是什么？
2. Python 字典和 JSON 字符串有什么区别？
3. 为什么 Runtime 需要结构化 State，而不是只保存一条日志？
4. `try/except` 能处理错误，但为什么不能自动实现任务恢复？
5. `if __name__ == "__main__"` 对实验代码有什么作用？

## 推荐资料

- [Python 官方教程](https://docs.python.org/3/tutorial/)
- [Python 异常处理](https://docs.python.org/3/tutorial/errors.html)
- [Python `json` 模块](https://docs.python.org/3/library/json.html)

## 下一课

```text
有了最小 Python 语法
-> Runtime 如何启动并管理一个任务
-> Task、Run、State 和 Event 的区别
```
