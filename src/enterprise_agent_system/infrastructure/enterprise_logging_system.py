"""
Infrastructure Layer - Enterprise Logging System
基础设施层 - 企业级日志系统

职责：
- 提供企业级日志功能
- 支持多种输出格式
- 支持日志文件轮转
"""

import logging
import logging.handlers
import sys
from typing import Optional
from functools import lru_cache


def setup_logging_system_configuration(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    设置日志系统配置

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_format: 日志格式 (CONSOLE, JSON)
        log_file: 日志文件路径
    """
    from enterprise_agent_system.infrastructure.application_configuration_management import (
        get_application_configuration_instance,
    )

    config = get_application_configuration_instance()

    log_level = log_level or config.logging_level_setting_string
    log_format = log_format or config.logging_format_type_string
    log_file = log_file or config.log_file_path_string

    root_logger = logging.getLogger()

    # 避免重复添加处理器
    if root_logger.handlers:
        return

    level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(level)

    # 格式化器
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器（带轮转）
    if log_file:
        rotating_file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        rotating_file_handler.setLevel(level)
        rotating_file_handler.setFormatter(console_formatter)
        root_logger.addHandler(rotating_file_handler)


@lru_cache(maxsize=128)
def get_logger_instance(logger_name: str = __name__) -> logging.Logger:
    """
    获取日志记录器实例

    Args:
        logger_name: 日志记录器名称

    Returns:
        配置好的日志记录器实例
    """
    setup_logging_system_configuration()
    return logging.getLogger(logger_name)
