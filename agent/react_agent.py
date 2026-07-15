"""
ReAct Agent 核心引擎
实现 Reasoning + Acting 循环：思考→行动→观察→再思考→...→最终回答
"""

import re
import sys
from typing import Optional, List, Dict

from .llm_client import HelloAgentsLLM
from .tools import get_tool_descriptions, execute_tool

# Windows 终端 UTF-8 兼容
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


# ReAct 系统提示词模板
REACT_SYSTEM_TEMPLATE = """
你叫{name}，是用户的智能伴侣助手，性格特点：{personality}。
请在对话中充分体现你的性格特点，像伴侣一样自然亲切。

你可以使用以下工具来帮助回答用户的问题：

{tools}

请严格按照以下格式回应：

Thought: 你的思考过程（分析用户想问什么，需要用什么工具）
Action: 你采取的行动，必须是以下之一：
- 工具名[参数]：调用工具
- Finish[最终答案]：你已经得出答案时的最终回复

注意：
1. 每次只输出一个 Thought + Action
2. 工具调用后你会看到 Observation（观察结果）
3. 根据 Observation 继续思考，直到可以给出最终答案
4. 最终答案要亲切自然，体现你的性格特点
5. 日常聊天（问候、闲聊等）不需要调用工具，直接用 Finish 回复
6. 如果工具多次调用仍无法解决问题，也要用 Finish 回复用户说明情况
"""


class ReActAgent:
    """ReAct 智能体"""

    def __init__(self, llm: HelloAgentsLLM, name: str = "小甜甜", personality: str = "活泼开朗的南方姑娘",
                 max_steps: int = 8):
        self.llm = llm
        self.name = name
        self.personality = personality
        self.max_steps = max_steps

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        tools_desc = get_tool_descriptions()
        return REACT_SYSTEM_TEMPLATE.format(
            name=self.name,
            personality=self.personality,
            tools=tools_desc,
        )

    def _parse_action(self, response: str) -> tuple:
        """
        解析 LLM 返回中的 Thought 和 Action
        返回: (thought_text, action_name, action_arg)
        """
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", response, re.DOTALL)
        action_match = re.search(r"Action:\s*(.*?)$", response, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else ""

        if not action_match:
            return thought, None, None

        action_text = action_match.group(1).strip()

        # 检查是否是 Finish
        finish_match = re.match(r"Finish\[(.*)\]", action_text, re.DOTALL)
        if finish_match:
            return thought, "Finish", finish_match.group(1)

        # 解析工具调用: 工具名[参数]
        tool_match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if tool_match:
            return thought, tool_match.group(1), tool_match.group(2)

        return thought, None, action_text

    def run(self, user_input: str, chat_history: List[Dict] = None) -> str:
        """
        运行 ReAct 循环处理用户输入

        Args:
            user_input: 用户输入的消息
            chat_history: 本轮对话之前的历史消息列表

        Returns:
            Agent 的最终回复
        """
        # 构建对话历史上下文
        history_str = ""
        if chat_history:
            # 取最近 6 条历史消息作为上下文（避免太长）
            recent_history = chat_history[-6:]
            for msg in recent_history:
                role = "用户" if msg["role"] == "user" else "你"
                history_str += f"{role}: {msg['content']}\n"

        system_prompt = self._build_system_prompt()

        # ReAct 循环
        react_history = []
        current_input = user_input

        for step in range(1, self.max_steps + 1):
            # 构建当前轮的 prompt
            history_context = f"{history_str}\n历史工具调用:\n" + "\n".join(react_history[-6:]) if react_history else history_str

            user_prompt = f"""当前对话历史：
{history_context}

用户最新消息：{current_input}

请分析并决定下一步行动。"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # 调用 LLM（非流式，方便解析结构化输出）
            response = self.llm.think_nonstream(messages)
            if not response:
                return "抱歉，我暂时无法思考了，请稍后再试。😅"

            # 解析返回
            thought, action_name, action_arg = self._parse_action(response)

            # 如果是 Finish，直接返回最终答案
            if action_name == "Finish":
                return action_arg

            # 如果没解析出 action，把整个回复作为答案
            if action_name is None:
                return response

            # 执行工具
            print(f"  🎬 第{step}步: {action_name}[{action_arg}]")
            observation = execute_tool(action_name, action_arg)
            print(f"  👀 观察: {observation[:100]}...")

            # 记录到 react 历史
            react_history.append(f"Thought: {thought}")
            react_history.append(f"Action: {action_name}[{action_arg}]")
            react_history.append(f"Observation: {observation}")

            # 下一轮将 observation 作为输入继续
            current_input = f"工具 '{action_name}' 返回: {observation}\n\n请根据这个结果继续，如果信息足够请用 Finish 给出最终答案。"

        return "我思考了太久，怕你等急了。要不我们换个话题？😅"
