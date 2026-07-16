"""
AI Partner Agent — 基于 ReAct 范式的智能伴侣系统
融合多轮对话 + 搜索引擎 + 工具调用 + 长期记忆
"""

import streamlit as st
import os
import sys
import json
import datetime

from agent.llm_client import HelloAgentsLLM
from agent.react_agent import ReActAgent
from agent.memory import MemoryManager

# Windows 终端兼容
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="AI Partner Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🤖 AI Partner Agent")
st.caption("基于 ReAct 范式的智能伴侣系统 · 能聊天 / 能搜索 / 能计算 / 能查天气")

# ============================================================
# 初始化 LLM 和 Agent（缓存避免重复创建）
# ============================================================
@st.cache_resource
def init_llm():
    return HelloAgentsLLM()

@st.cache_resource
def init_memory():
    return MemoryManager()

@st.cache_resource
def init_agent(_llm, _memory):
    return ReActAgent(llm=_llm, memory_manager=_memory)


llm = init_llm()
memory = init_memory()
agent = init_agent(llm, memory)

# ============================================================
# 工具函数：会话管理
# ============================================================

SESSION_DIR = "sessions"


def generate_session_name():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_session():
    if not st.session_state.messages:
        return
    session_data = {
        "current_session": st.session_state.current_session,
        "messages": st.session_state.messages,
        "partner_name": st.session_state.partner_name,
        "partner_personality": st.session_state.partner_personality,
        "chat_mode": st.session_state.chat_mode,
    }
    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR)
    with open(f"{SESSION_DIR}/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)


def load_session_list():
    if not os.path.exists(SESSION_DIR):
        return []
    files = [f for f in os.listdir(SESSION_DIR) if f.endswith(".json")]
    files.sort(key=lambda x: os.path.getmtime(f"{SESSION_DIR}/{x}"), reverse=True)
    return files


def load_session(session_file):
    try:
        with open(f"{SESSION_DIR}/{session_file}", "r", encoding="utf-8") as f:
            data = json.load(f)
        st.session_state.current_session = data["current_session"]
        st.session_state.messages = data["messages"]
        st.session_state.partner_name = data.get("partner_name", "小甜甜")
        st.session_state.partner_personality = data.get("partner_personality", "活泼开朗的南方姑娘")
        st.session_state.chat_mode = data.get("chat_mode", "chat")
        return True
    except Exception as e:
        st.error(f"加载会话失败：{e}")
        return False


def delete_session(session_file):
    try:
        os.remove(f"{SESSION_DIR}/{session_file}")
        return True
    except Exception as e:
        st.error(f"删除会话失败：{e}")
        return False


def get_session_info(session_file):
    try:
        with open(f"{SESSION_DIR}/{session_file}", "r", encoding="utf-8") as f:
            data = json.load(f)
        messages = data.get("messages", [])
        msg_count = len([m for m in messages if m["role"] == "user"])
        preview = ""
        for msg in messages:
            if msg["role"] == "user":
                preview = msg["content"]
                if len(preview) > 20:
                    preview = preview[:20] + "..."
                break
        return {
            "name": session_file.replace(".json", ""),
            "msg_count": msg_count,
            "preview": preview,
            "partner_name": data.get("partner_name", "小甜甜"),
        }
    except:
        return None


# ============================================================
# 会话状态初始化
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "partner_name" not in st.session_state:
    st.session_state.partner_name = "小甜甜"

if "partner_personality" not in st.session_state:
    st.session_state.partner_personality = "活泼开朗的南方姑娘"

if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "chat"  # "chat" 或 "agent"

if "current_session" not in st.session_state:
    st.session_state.current_session = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# ============================================================
# 侧边栏
# ============================================================
with st.sidebar:
    st.subheader("💕 伴侣信息")
    st.caption(f"昵称：{st.session_state.partner_name}")
    st.caption(f"性格：{st.session_state.partner_personality}")
    st.divider()

    # ---------- 对话模式切换 ----------
    st.subheader("🎛️ 对话模式")

    mode_options = {
        "chat": "💬 日常聊天",
        "agent": "🧠 智能助手（ReAct）",
    }
    selected_mode = st.radio(
        "选择模式",
        options=list(mode_options.keys()),
        format_func=lambda x: mode_options[x],
        index=0 if st.session_state.chat_mode == "chat" else 1,
        label_visibility="collapsed",
    )
    st.session_state.chat_mode = selected_mode

    if selected_mode == "agent":
        st.info("智能助手模式：当需要搜索信息、计算、查天气时自动使用工具，适合复杂问题。")

    st.divider()

    # ---------- 控制按钮 ----------
    st.subheader("📋 操作")

    if st.button("🔄 新建会话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_session = generate_session_name()
        st.rerun()

    if st.button("💾 保存会话", use_container_width=True):
        if st.session_state.messages:
            save_session()
            st.success("✅ 已保存！")
        else:
            st.warning("暂无内容可保存")

    st.divider()

    # ---------- 历史会话 ----------
    st.subheader("📂 历史会话")

    sessions = load_session_list()

    if sessions:
        st.caption(f"共 {len(sessions)} 个会话")
        for session_file in sessions:
            info = get_session_info(session_file)
            if not info:
                continue
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    display_name = info["name"]
                    if len(display_name) > 16:
                        display_name = display_name[:16] + "..."
                    st.caption(f"📝 {display_name}")
                    st.caption(f"💬 {info['msg_count']}轮 | 👤{info['partner_name']}")
                    if info["preview"]:
                        st.caption(f"📌 {info['preview']}")
                with col2:
                    if st.button("📂", key=f"load_{session_file}", use_container_width=True):
                        if load_session(session_file):
                            st.success("✅ 已加载！")
                            st.rerun()
                with col3:
                    if st.button("🗑️", key=f"del_{session_file}", use_container_width=True):
                        if delete_session(session_file):
                            st.rerun()
                st.divider()
    else:
        st.caption("暂无历史会话 💭")

    st.divider()

    # ---------- 伴侣设置 ----------
    st.subheader("💑 伴侣设置")
    new_name = st.text_input("昵称", value=st.session_state.partner_name)
    new_personality = st.text_input("性格", value=st.session_state.partner_personality)

    if st.button("✅ 更新", use_container_width=True):
        st.session_state.partner_name = new_name
        st.session_state.partner_personality = new_personality
        st.success("✅ 已更新！")
        st.rerun()

    st.divider()

    # ---------- 长期记忆查看器 ----------
    st.subheader("🧠 长期记忆")
    all_memories = memory.get_all_memories()
    if all_memories:
        st.caption(f"共记住 {len(all_memories)} 条信息")
        for m in all_memories:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.caption(f"📌 {m['text']}")
            with col2:
                if st.button("✕", key=f"del_mem_{m['id']}", use_container_width=True):
                    memory.delete_memory_by_id(m['id'])
                    st.rerun()
    else:
        st.caption("还没有记住任何信息 💭")
        st.caption("和 Agent 聊聊天，它会自动记住你的偏好")

    if st.button("🗑️ 清除所有记忆", use_container_width=True, type="secondary"):
        memory.clear_memories()
        st.rerun()

    st.divider()

    # ---------- 项目信息 ----------
    st.caption("---")
    st.caption("🤖 AI Partner Agent v2.0")
    st.caption("技术栈：Streamlit · DeepSeek · ReAct · Tavily")

# ============================================================
# 主界面：显示聊天历史
# ============================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ============================================================
# 输入处理
# ============================================================
prompt = st.chat_input("说点什么吧...")

if prompt:
    # 显示用户消息
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ---------- 根据模式选择处理方式 ----------
    if st.session_state.chat_mode == "agent":
        # ======== Agent 模式（ReAct） ========
        with st.chat_message("assistant"):
            with st.spinner("🤔 思考中..."):
                try:
                    # 更新 Agent 的伴侣信息
                    agent.name = st.session_state.partner_name
                    agent.personality = st.session_state.partner_personality

                    # 运行 ReAct 循环（取最近的历史消息作为上下文）
                    response = agent.run(prompt, st.session_state.messages[:-1])

                    # 显示回复
                    st.write(response)

                    # 保存到历史
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )

                    # 提取并存储长期记忆（后台异步风格）
                    try:
                        agent.record_interaction(
                            prompt, response, st.session_state.messages[:-1]
                        )
                    except Exception as e:
                        print(f"🧠 记忆提取跳过: {e}")

                    save_session()

                except Exception as e:
                    error_msg = f"处理出错: {e}"
                    st.error(error_msg)
                    print("错误:", e)

    else:
        # ======== 日常聊天模式（直接 LLM 调用 + 流式） ========
        system_prompt = f"""
你叫{st.session_state.partner_name}，现在是用户的真实伴侣，请完全代入伴侣角色。

规则：
1. 每次只回1条消息
2. 禁止任何场景或状态描述性文字
3. 匹配用户的语言
4. 回复简短，像微信聊天一样
5. 有需要的话可以用❤️❤️等emoji表情
6. 用符合伴侣性格的方式对话
7. 回复的内容要充分体现伴侣的性格特征

伴侣性格：{st.session_state.partner_personality}

你必须严格遵守上述规则来回复用户。
"""

        messages_for_llm = [
            {"role": "system", "content": system_prompt},
            *st.session_state.messages,
        ]

        try:
            response = llm.client.chat.completions.create(
                model=llm.model,
                messages=messages_for_llm,
                stream=True,
            )

            with st.chat_message("assistant"):
                full_response = ""
                placeholder = st.empty()

                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        placeholder.write(full_response)

                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

                # 聊天模式也提取记忆
                try:
                    agent.record_interaction(
                        prompt, full_response, st.session_state.messages[:-1]
                    )
                except Exception as e:
                    print(f"🧠 聊天模式记忆提取跳过: {e}")

                save_session()

        except Exception as e:
            st.error(f"调用AI失败：{e}")
            print("错误:", e)
