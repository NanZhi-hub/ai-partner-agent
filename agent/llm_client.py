"""
LLM 客户端模块
封装对大语言模型的调用，支持流式和非流式两种模式
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Windows 终端 UTF-8 兼容
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 加载环境变量
load_dotenv()


class HelloAgentsLLM:
    """
    大语言模型客户端
    兼容 OpenAI 接口的服务（DeepSeek、OpenAI 等）
    """

    def __init__(self, model: str = None, api_key: str = None, base_url: str = None, timeout: int = 60):
        self.model = model or os.getenv("LLM_MODEL_ID") or "deepseek-chat"
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("LLM_API_KEY")
        base_url = base_url or os.getenv("DEEPSEEK_BASE_URL") or os.getenv("LLM_BASE_URL") or "https://api.deepseek.com"
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", "60"))

        if not all([self.model, api_key, base_url]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> str:
        """
        调用大语言模型思考（流式），返回完整回复文本
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            print("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()
            return "".join(collected_content)

        except Exception as e:
            error_msg = f"调用大模型时发生错误: {e}"
            print(error_msg)
            return f"【错误】{error_msg}"

    def think_nonstream(self, messages: List[Dict[str, str]], temperature: float = 0) -> str:
        """
        调用大语言模型思考（非流式），直接返回完整回复文本
        适用于需要解析结构化输出的场景（如 ReAct 的 Action 解析）
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=False,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            error_msg = f"调用大模型时发生错误: {e}"
            print(error_msg)
            return f"【错误】{error_msg}"
