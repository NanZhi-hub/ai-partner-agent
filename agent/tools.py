"""
工具集模块
为 Agent 提供各种可调用的工具：搜索、计算器、时间等
"""

import os
import sys
import datetime
import requests

# Windows 终端 UTF-8 兼容
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def web_search(query: str) -> str:
    """
    基于 Tavily 的 AI 搜索引擎工具。
    专为 AI Agent 设计，返回结构化结果和总结性答案。
    """
    print(f"🔍 正在执行 [Tavily] 网页搜索: {query}")
    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "错误：TAVILY_API_KEY 未在 .env 文件中配置。"

        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        results = client.search(
            query=query,
            search_depth="advanced",
            include_answer=True,
            max_results=5,
        )

        if results.get("answer"):
            output = [f"📝 总结：{results['answer']}\n"]
        else:
            output = []

        if results.get("results"):
            for i, res in enumerate(results["results"][:5]):
                output.append(
                    f"[{i+1}] {res.get('title', '')}\n"
                    f"    {res.get('content', '')[:200]}\n"
                    f"    🔗 {res.get('url', '')}"
                )

        if output:
            return "\n\n".join(output)

        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"


def calculator(expression: str) -> str:
    """
    计算数学表达式
    支持 + - * / 和括号运算
    """
    print(f"🧮 正在计算: {expression}")
    try:
        # 安全过滤：只允许数字和运算符
        safe_chars = set("0123456789+-*/().,% ")
        cleaned = "".join(c for c in expression if c in safe_chars)
        result = eval(cleaned, {"__builtins__": {}}, {})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"


def get_current_time(format_str: str = "") -> str:
    """
    获取当前日期时间
    format_str 可选: 'date' / 'time' / 留空则返回完整时间
    """
    now = datetime.datetime.now()
    if format_str == "date":
        return f"当前日期: {now.strftime('%Y年%m月%d日')}"
    elif format_str == "time":
        return f"当前时间: {now.strftime('%H:%M:%S')}"
    else:
        return f"当前日期时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"


def get_weather(city: str) -> str:
    """
    查询指定城市的实时天气
    使用 wttr.in（免费，无需 API Key）
    """
    print(f"🌤️ 正在查询天气: {city}")
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=%C+%t+%h+%w",
            timeout=10
        )
        if response.status_code == 200:
            weather_info = response.text.strip()
            return f"{city} 天气: {weather_info}"
        else:
            return f"无法获取 {city} 的天气信息"
    except Exception as e:
        return f"查询天气失败: {e}"


# 工具注册表：名称 -> (描述, 函数)
TOOL_REGISTRY = {
    "web_search": {
        "description": "网页搜索引擎。当你需要回答关于时事、实时信息或你知识库中找不到的信息时使用。输入：搜索关键词。",
        "func": web_search,
    },
    "calculator": {
        "description": "数学计算器。用于计算数学表达式，如 '2 + 3 * 4'。输入：数学表达式。",
        "func": calculator,
    },
    "get_time": {
        "description": "获取当前日期时间。输入：'date' 获取日期，'time' 获取时间，留空获取完整日期时间。",
        "func": get_current_time,
    },
    "get_weather": {
        "description": "查询指定城市的天气。输入：城市名称，如 '北京'。",
        "func": get_weather,
    },
}


def get_tool_descriptions() -> str:
    """返回所有工具的格式化描述"""
    lines = []
    for name, info in TOOL_REGISTRY.items():
        lines.append(f"- {name}: {info['description']}")
    return "\n".join(lines)


def execute_tool(name: str, arg: str) -> str:
    """执行指定名称的工具，传入参数"""
    tool = TOOL_REGISTRY.get(name)
    if not tool:
        return f"错误：没有名为 '{name}' 的工具。可用工具：{', '.join(TOOL_REGISTRY.keys())}"
    try:
        return tool["func"](arg)
    except Exception as e:
        return f"执行工具 '{name}' 时出错: {e}"
