# 🤖 AI Partner Agent

基于 **ReAct（Reasoning + Acting）范式** 的智能伴侣系统，融合大语言模型对话能力与搜索引擎、计算器等工具调用能力。

## ✨ 特性

- **🧠 ReAct 智能体架构** — 自主思考→行动→观察→再思考的循环，突破纯对话的能力边界
- **🔍 搜索引擎** — 集成 Tavily API，支持实时信息查询（新闻、百科、时事等）
- **🧮 计算器** — 支持数学表达式计算
- **🌤️ 天气查询** — 查询任意城市实时天气（免费，无需 API Key）
- **💬 双模式切换** — 日常聊天 / 智能助手模式一键切换
- **🎭 可自定义性格** — 伴侣昵称和性格自由设置，对话风格随之变化

## 🏗️ 项目架构

```
ai-partner-agent/
├── app.py                  # Streamlit 主界面（入口）
├── agent/
│   ├── __init__.py
│   ├── llm_client.py       # LLM 调用封装（流式/非流式）
│   ├── react_agent.py      # ReAct 循环引擎（核心）
│   └── tools.py            # 工具集（搜索/计算/时间/天气）
├── requirements.txt        # 依赖清单
├── .env                    # API 密钥配置（不提交到 Git）
├── .env.example            # 环境变量模板
└── README.md
```

### 架构流程图

```
用户输入
    │
    ▼
┌─────────────────────────────┐
│      Streamlit UI (app.py)   │
│   ┌─────────────────────┐   │
│   │  日常聊天模式         │   │
│   │  (直接 LLM 流式对话) │   │
│   └─────────┬───────────┘   │
│             │ 或             │
│   ┌─────────▼───────────┐   │
│   │  Agent 模式 (ReAct)  │   │
│   └─────────┬───────────┘   │
└─────────────┼───────────────┘
              │
              ▼
┌─────────────────────────────┐
│    ReAct 循环 (react_agent)  │
│                             │
│  Thought → Action → Observation → 循环 → Finish
│              │                      │
│              ▼                      ▼
│       ┌──────────┐          返回最终回答
│       │ 工具调用  │
│       ├──────────┤
│       │ web_search│── Tavily API
│       │ calculator│── 数学计算
│       │ get_time  │── 系统时间
│       │ get_weather│── wttr.in API
│       └──────────┘
└─────────────────────────────┘
```

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.10+ | 开发语言 |
| Streamlit | Web 交互界面 |
| DeepSeek API | 大语言模型（兼容 OpenAI 接口） |
| Tavily API | AI 搜索引擎 |
| wttr.in | 免费天气 API（无需 Key） |
| ReAct 范式 | 智能体推理框架 |

## 🚀 快速开始

### 前置要求

- Python 3.10+
- DeepSeek API Key（[获取](https://platform.deepseek.com/)）
- Tavily API Key（[获取](https://tavily.com/)）

### 安装

```bash
# 1. 克隆项目
cd ai-partner-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 API 密钥
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 运行

```bash
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`

## 📸 功能预览

- **日常聊天**：和设定好性格的智能伴侣自然对话
- **智能助手**：问实时问题，自动调用搜索引擎获取最新信息
- **天气查询**：说"北京天气怎么样"即可
- **数学计算**：说"计算 1024 * 768"即可

## 📄 项目亮点

> **基于 ReAct 范式的多工具智能体应用**
>
> 不同于传统的对话式聊天机器人，本项目实现了 ReAct（Reasoning+Acting）智能体架构。LLM 不再是简单的"输入→输出"，而是在循环中自主思考（Thought）、决定调用何种工具（Action）、观察工具返回结果（Observation），直到得出最终答案。这种架构让 AI 突破纯对话的能力边界，能够获取实时信息、进行计算，真正具备"行动能力"。

## 📝 待办 / 可扩展方向

- [ ] ChromaDB 长期记忆（跨会话回忆用户偏好）
- [ ] 多工具并行调用
- [ ] Docker 部署
- [ ] 语音输入/输出

## 📜 致谢

- [Datawhale Hello-Agents](https://github.com/datawhalechina/hello-agents) — 智能体学习教程
- [Streamlit](https://streamlit.io/) — Web 框架
- [Tavily](https://tavily.com/) — AI 搜索引擎
