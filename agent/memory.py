"""
长期记忆模块 (ChromaDB)
存储和检索用户的重要信息，实现跨会话记忆
"""

import os
import sys
import datetime
import json
from typing import List, Dict, Optional

import chromadb
from chromadb.config import Settings

# Windows 终端 UTF-8 兼容
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 记忆提取系统提示词
MEMORY_EXTRACT_PROMPT = """
你是一个记忆提取助手。请分析以下对话，提取出关于用户的**重要个人信息**需要记住的内容。

你需要关注的信息类型：
1. 用户的个人偏好（喜欢/不喜欢什么食物、颜色、风格、话题等）
2. 用户的重要情况（工作、学习、家庭、生活状况等）
3. 用户的习惯或特征
4. 用户提到的重要事件或计划
5. 用户说过的任何可以用于个性化服务的细节

规则：
- 只提取事实性、可长期保留的信息
- 忽略日常寒暄（如"你好"、"今天天气不错"、"再见"等）
- 每一条记忆应该是一句简洁完整的话
- 如果没有值得记住的信息，请返回空列表 []
- 用中文输出

请严格以JSON数组格式返回，例如：
["用户喜欢吃辣", "用户养了一只叫小白的猫", "用户在北京工作"]
"""


class MemoryManager:
    """长期记忆管理器，基于 ChromaDB 向量数据库"""

    def __init__(self, collection_name: str = "partner_memories",
                 persist_dir: str = None):
        """
        初始化记忆管理器

        Args:
            collection_name: ChromaDB 集合名称
            persist_dir: 持久化存储目录，默认项目下的 memory_store/
        """
        if persist_dir is None:
            persist_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "memory_store"
            )

        os.makedirs(persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        self.memory_count = self.collection.count()
        print(f"🧠 长期记忆已加载，已有 {self.memory_count} 条记忆")

    # ------------------------------------------------------------
    # 核心读写操作
    # ------------------------------------------------------------

    def store_memory(self, text: str, user_id: str = "default") -> bool:
        """存储一条记忆（含简单去重）"""
        if not text or len(text.strip()) < 4:
            return False

        try:
            ts = int(datetime.datetime.now().timestamp() * 1000)
            unique_id = f"mem_{ts}_{abs(hash(text)) % 100000}"

            # 简单去重：检查最近 50 条中是否有相似内容
            existing = self.collection.get(
                where={"user_id": user_id},
                limit=50,
            )
            if existing and existing["documents"]:
                for doc in existing["documents"]:
                    a, b = text[:20], doc[:20]
                    if a in b or b in a:
                        return False

            self.collection.add(
                documents=[text],
                metadatas=[{
                    "user_id": user_id,
                    "timestamp": datetime.datetime.now().isoformat(),
                }],
                ids=[unique_id],
            )
            self.memory_count = self.collection.count()
            print(f"💾 新增记忆 ({self.memory_count}): {text[:50]}...")
            return True
        except Exception as e:
            print(f"❌ 存储记忆失败: {e}")
            return False

    def query_memories(self, query: str, k: int = 5,
                       user_id: str = "default") -> List[str]:
        """检索与 query 语义最相关的记忆"""
        try:
            if self.collection.count() == 0:
                return []

            results = self.collection.query(
                query_texts=[query],
                n_results=min(k, self.collection.count()),
                where={"user_id": user_id},
            )

            if results and results["documents"] and results["documents"][0]:
                return results["documents"][0]
            return []
        except Exception as e:
            print(f"❌ 检索记忆失败: {e}")
            return []

    # ------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------

    def get_memory_context(self, query: str, user_id: str = "default",
                           k: int = 5) -> str:
        """
        获取格式化的记忆上下文，用于注入到 Agent 系统提示词中
        返回空字符串表示没有相关记忆
        """
        memories = self.query_memories(query, k=k, user_id=user_id)
        if not memories:
            return ""

        lines = ["\n【关于用户的记忆】"]
        for i, mem in enumerate(memories, 1):
            lines.append(f"{i}. {mem}")
        lines.append("（请参考以上记忆，让回答更个性化、更贴心）\n")
        return "\n".join(lines)

    def get_all_memories(self, user_id: str = "default") -> List[Dict]:
        """获取所有记忆（用于展示）"""
        try:
            if self.collection.count() == 0:
                return []

            results = self.collection.get(where={"user_id": user_id})
            memories = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    meta = results["metadatas"][i] if results["metadatas"] else {}
                    memories.append({
                        "text": doc,
                        "timestamp": meta.get("timestamp", "未知"),
                        "id": results["ids"][i] if results["ids"] else "",
                    })
                memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return memories
        except Exception as e:
            print(f"❌ 获取记忆列表失败: {e}")
            return []

    def delete_memory_by_id(self, memory_id: str) -> bool:
        """根据ID删除单条记忆"""
        try:
            self.collection.delete(ids=[memory_id])
            self.memory_count = self.collection.count()
            return True
        except Exception as e:
            print(f"❌ 删除记忆失败: {e}")
            return False

    def clear_memories(self, user_id: str = "default") -> bool:
        """清除指定用户的所有记忆"""
        try:
            all_items = self.collection.get(where={"user_id": user_id})
            if all_items and all_items["ids"]:
                self.collection.delete(ids=all_items["ids"])
            self.memory_count = self.collection.count()
            print(f"🧹 已清除 {user_id} 的所有记忆")
            return True
        except Exception as e:
            print(f"❌ 清除记忆失败: {e}")
            return False


def extract_memories_from_conversation(
    conversation_text: str,
    llm_client,
) -> List[str]:
    """
    使用 LLM 从对话中提取值得记住的信息

    Args:
        conversation_text: 包含角色标记的对话文本
        llm_client: 提供 think_nonstream() 方法的 LLM 客户端

    Returns:
        提取出的记忆文本列表
    """
    try:
        messages = [
            {"role": "system", "content": MEMORY_EXTRACT_PROMPT},
            {"role": "user", "content": f"对话内容：\n{conversation_text}"},
        ]

        result = llm_client.think_nonstream(messages)
        if not result:
            return []

        result = result.strip()

        # 处理 markdown 代码块包裹
        if "```" in result:
            parts = result.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("[") and part.endswith("]"):
                    result = part
                    break
            else:
                # fallback：取最后一个非空代码块
                for part in reversed(parts):
                    if part.strip():
                        result = part.strip()
                        break

        # 尝试 JSON 解析
        try:
            memories = json.loads(result)
            if isinstance(memories, list):
                return [
                    m.strip() for m in memories
                    if m.strip() and len(m.strip()) > 3
                ]
        except json.JSONDecodeError:
            pass

        # fallback：正则提取 JSON 数组
        import re
        json_match = re.search(r"\[.*?\]", result, re.DOTALL)
        if json_match:
            try:
                memories = json.loads(json_match.group(0))
                if isinstance(memories, list):
                    return [
                        m.strip() for m in memories
                        if m.strip() and len(m.strip()) > 3
                    ]
            except json.JSONDecodeError:
                pass

        # 最后的 fallback：按行解析
        lines = []
        for line in result.split("\n"):
            line = line.strip().strip("- *").strip('"').strip()
            if line and not line.startswith(("{", "```", "json", "返回")):
                lines.append(line)
        return lines

    except Exception as e:
        print(f"❌ 提取记忆失败: {e}")
        return []
