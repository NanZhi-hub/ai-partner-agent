# ============================================================
# AI Partner Agent — Docker 镜像
# 基于 ReAct 范式的智能伴侣系统
# ============================================================

FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（ChromaDB 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建运行时数据目录（会话、日志、记忆）
RUN mkdir -p sessions logs memory_store

# Streamlit 端口
EXPOSE 8501

# 启动入口
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
