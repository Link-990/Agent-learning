"""用本地 JSON-RPC 形状模拟 MCP Tool 发现与调用。"""
import json


TOOLS = {
    "weather.mock": {
        "description": "返回固定天气",
        "inputSchema": {"type": "object", "required": ["city"]},
    }
}

TOOL_LIST = [{"name": name, **descriptor} for name, descriptor in TOOLS.items()]


def list_tools() -> dict:
    return {"jsonrpc": "2.0", "id": 1, "result": {"tools": TOOL_LIST}}


def call_tool(name: str, arguments: dict, allowed: set[str]) -> dict:
    if name not in allowed or name not in TOOLS:
        return {"jsonrpc": "2.0", "id": 2, "error": {"code": -32001, "message": "tool_not_allowed"}}
    city = arguments.get("city")
    if not isinstance(city, str) or not city:
        return {"jsonrpc": "2.0", "id": 2, "error": {"code": -32602, "message": "invalid_arguments"}}
    return {"jsonrpc": "2.0", "id": 2, "result": {"content": [{"type": "text", "text": f"{city}: 25C (mock)"}], "isError": False}}


def main() -> None:
    discovered = list_tools()
    print(f"event=tool.discovered run_id=run-07 state=running names={[item['name'] for item in discovered['result']['tools']]}")
    request = {"name": "weather.mock", "arguments": {"city": "Shanghai"}}
    print("event=tool.call.started run_id=run-07 state=waiting_for_tool tool=weather.mock")
    result = call_tool(request["name"], request["arguments"], {"weather.mock"})
    print("event=tool.call.finished run_id=run-07 state=running")
    print(json.dumps(result, ensure_ascii=False))
    denied = call_tool("shell", {}, {"weather.mock"})
    print(f"event=tool.denied run_id=run-07 state=failed reason={denied['error']['message']}")


if __name__ == "__main__":
    main()
