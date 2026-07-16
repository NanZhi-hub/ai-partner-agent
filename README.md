# AI Partner Agent 🤖

基于 **ReAct 范式**的智能伴侣系统，融合大语言模型对话与搜索引擎、计算器等工具调用能力，支持**长期记忆**（ChromaDB 向量记忆）。

## 项目定位

简历项目。展示对 Agent 架构（ReAct 范式）的理解和 Python 工程化能力。

---

## 功能特性

- 🧠 **ReAct 智能体** — Thought→Action→Observation 循环，自主决策工具调用
- 🔍 **网页搜索** — 集成 Tavily API，获取实时信息
- 🧮 **数学计算** — 表达式计算器
- 🌤️ **天气查询** — 全球城市实时天气
- 💬 **双模式切换** — 日常聊天 / 智能助手（ReAct）
- 🧠 **长期记忆** — ChromaDB 向量数据库，跨会话记住用户偏好（自动提取 + 语义检索）
- 📝 **日志系统** — 分级日志（INFO/WARNING/ERROR），控制台+文件双输出，按日轮转
- 💾 **会话管理** — 保存 / 加载 / 删除对话历史

## 技术栈

| 层      | 技术                                     |
| ------- | ---------------------------------------- |
| UI      | Streamlit                                |
| Agent   | ReAct 范式（纯手动实现）                 |
| LLM     | DeepSeek API                             |
| 工具    | Tavily / Calculator / wttr.in            |
| 记忆    | ChromaDB（向量语义检索 + RAG）           |
| 日志    | 自定义 logging 模块（控制台 + 文件输出） |

## 架构

```
app.py (UI 层) → react_agent.py (Agent 层) → tools.py (工具层)
                      ↕
              memory.py (ChromaDB 长期记忆)
```

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/NanZhi-hub/ai-partner-agent.git
cd ai-partner-agent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的 API Key：

```
DEEPSEEK_API_KEY=your_deepseek_api_key
TAVILY_API_KEY=your_tavily_api_key
LLM_MODEL_ID=deepseek-chat
```

### 4. 启动应用

```bash
python -m streamlit run app.py
```

打开 http://localhost:8501 即可使用。

## 使用方法

| 模式 | 说明 |
|------|------|
| 💬 日常聊天 | 直接对话，会记住你的偏好信息 |
| 🧠 智能助手 | ReAct 模式，可调用搜索、计算、天气等工具 |

对话一段时间后，侧边栏底部的「🧠 长期记忆」区域会显示 Agent 记住的信息。支持单条删除和全部清除。

## 项目结构

```
ai-partner-agent/
├── app.py                  # Streamlit UI 入口
├── agent/
│   ├── __init__.py
│   ├── logger.py            # 日志模块（分级 + 文件输出）
│   ├── llm_client.py       # LLM 调用封装（流式/非流式）
│   ├── react_agent.py      # ReAct 循环引擎
│   ├── tools.py            # 工具注册表（搜索/计算/天气）
│   └── memory.py           # ChromaDB 长期记忆管理器
├── logs/                    # 日志文件（按日轮转，保留7天）
├── sessions/               # 会话持久化存储
├── memory_store/           # 长期记忆向量数据库存储
├── .env.example            # 环境变量模板
├── requirements.txt
└── README.md
```

- **ReAct 范式手动实现** — 深入理解 Agent 底层原理，而不是套 LangChain
- **工具注册表模式** — 低代码扩展新工具，展示架构设计能力
- **RAG 实战经验** — ChromaDB 向量检索 + LLM 记忆提取，面试高频考点
- **工程化思维** — 分层解耦、会话持久化、安全性处理
