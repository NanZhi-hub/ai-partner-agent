"""
日志模块
统一的日志记录，支持控制台和文件输出
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


def ensure_log_dir():
    """确保日志目录存在"""
    os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str, level: str = None) -> logging.Logger:
    """
    获取一个日志记录器

    Args:
        name: 模块名称，如 'agent.react_agent'
        level: 日志级别，默认从环境变量 LOG_LEVEL 读取，兜底 INFO

    Returns:
        配置好的 Logger 实例
    """
    # 从环境变量读取级别（优先级：参数 > 环境变量 > 默认）
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)

    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        logger.setLevel(log_level)
        return logger

    logger.setLevel(log_level)

    # ---------- 格式 ----------
    file_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_fmt = logging.Formatter(
        "%(levelname)s | %(message)s"
    )

    # ---------- 控制台 Handler ----------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # ---------- 文件 Handler（按日期轮转，保留 7 天） ----------
    try:
        ensure_log_dir()
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(LOG_DIR, f"{today}.log")

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=7,
            encoding="utf-8",
        )
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)

        # 单独的 error 日志文件
        error_log_file = os.path.join(LOG_DIR, f"error-{today}.log")
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=7,
            encoding="utf-8",
        )
        error_handler.setFormatter(file_fmt)
        error_handler.setLevel(logging.WARNING)
        logger.addHandler(error_handler)

    except Exception as e:
        # 文件日志失败不影响控制台输出
        print(f"[logger] 文件日志初始化失败: {e}")

    return logger


def get_log_files(days: int = 7) -> list:
    """获取最近 N 天的日志文件列表"""
    ensure_log_dir()
    files = sorted(os.listdir(LOG_DIR), reverse=True)
    return [f for f in files if f.endswith(".log")][:days]
