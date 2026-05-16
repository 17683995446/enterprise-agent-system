"""
Infrastructure Layer - Application Configuration Management
基础设施层 - 应用配置管理

职责：
- 管理应用程序配置
- 支持环境变量覆盖
- 提供类型安全的配置访问
"""

import os
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class ApplicationConfigurationManagement:
    """
    应用程序配置管理类 - 集中管理所有配置

    Attributes:
        application_name_string: 应用程序名称字符串
        application_version_string: 应用程序版本字符串
        debug_mode_enabled_flag: 调试模式启用标志
        api_host_address_string: API 主机地址字符串
        api_port_number_integer: API 端口号整数
        database_connection_url_string: 数据库连接 URL 字符串
        max_concurrent_tasks_integer: 最大并发任务数整数
        idle_improvement_interval_seconds_float: 空闲改进间隔秒数浮点数
        task_execution_timeout_seconds_float: 任务执行超时秒数浮点数
        logging_level_setting_string: 日志级别设置字符串
        logging_format_type_string: 日志格式类型字符串
        log_file_path_string: 日志文件路径字符串
        monitoring_metrics_enabled_flag: 监控指标启用标志
        monitoring_health_checks_enabled_flag: 监控健康检查启用标志
    """
    application_name_string: str = "Enterprise Dual-Mode Agent System"
    application_version_string: str = "8.0.0"
    debug_mode_enabled_flag: bool = True

    api_host_address_string: str = "0.0.0.0"
    api_port_number_integer: int = 8000

    database_connection_url_string: str = "sqlite:///agent_system_data.db"

    max_concurrent_tasks_integer: int = 5
    idle_improvement_interval_seconds_float: float = 30.0
    task_execution_timeout_seconds_float: float = 3600.0

    logging_level_setting_string: str = "INFO"
    logging_format_type_string: str = "CONSOLE"
    log_file_path_string: str = "agent_system.log"

    monitoring_metrics_enabled_flag: bool = True
    monitoring_health_checks_enabled_flag: bool = True


@lru_cache(maxsize=1)
def get_application_configuration_instance() -> ApplicationConfigurationManagement:
    """
    获取应用程序配置实例 - 单例模式

    Returns:
        应用程序配置实例
    """
    config = ApplicationConfigurationManagement()

    # 从环境变量覆盖配置
    if os.getenv("AGENT_APPLICATION_NAME"):
        config.application_name_string = os.getenv("AGENT_APPLICATION_NAME")

    if os.getenv("AGENT_DEBUG_MODE_ENABLED"):
        config.debug_mode_enabled_flag = (
            os.getenv("AGENT_DEBUG_MODE_ENABLED").lower() == "true"
        )

    if os.getenv("AGENT_API_PORT_NUMBER"):
        config.api_port_number_integer = int(
            os.getenv("AGENT_API_PORT_NUMBER")
        )

    if os.getenv("AGENT_LOGGING_LEVEL"):
        config.logging_level_setting_string = os.getenv("AGENT_LOGGING_LEVEL")

    if os.getenv("AGENT_LOG_FILE_PATH"):
        config.log_file_path_string = os.getenv("AGENT_LOG_FILE_PATH")

    return config
