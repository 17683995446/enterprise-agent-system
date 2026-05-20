"""
Configuration Management System
企业级配置管理系统，支持 YAML 配置、环境变量、多环境
"""

import os
import yaml
import re
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance(__name__)


@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: str = "silicon_flow"
    api_key: str = ""
    base_url: str = "https://api.siliconflow.cn/v1"
    model: str = "Qwen/Qwen2.5-7B-Instruct"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60
    retry_attempts: int = 3
    enable_cache: bool = True
    cache_ttl: int = 3600


@dataclass
class APIConfig:
    """API 配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = field(default_factory=lambda: ["*"])
    rate_limit: Dict = field(default_factory=lambda: {"enabled": True, "requests_per_minute": 100})


@dataclass
class DatabaseConfig:
    """数据库配置"""
    url: str = "sqlite:///data/enterprise_agent.db"
    echo: bool = False
    pool_size: int = 20
    max_overflow: int = 10


@dataclass
class CacheConfig:
    """缓存配置"""
    type: str = "memory"
    redis_url: str = "redis://localhost:6379/0"
    default_ttl: int = 3600


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "json"
    file: Optional[str] = None
    max_size: str = "100MB"
    backup_count: int = 10


@dataclass
class AnalysisConfig:
    """分析配置"""
    default_depth: str = "deep"
    include_security: bool = True
    include_performance: bool = True
    include_best_practices: bool = True
    batch_size: int = 50


@dataclass
class RAGConfig:
    """RAG 配置"""
    enabled: bool = True
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    vector_store: str = "memory"


@dataclass
class MonitoringConfig:
    """监控配置"""
    enabled: bool = True
    prometheus: Dict = field(default_factory=lambda: {"port": 9090})
    grafana: Dict = field(default_factory=lambda: {"enabled": True, "url": "http://localhost:3000"})


@dataclass
class StorageConfig:
    """存储配置"""
    upload_dir: str = "./uploads"
    report_dir: str = "./reports"
    data_dir: str = "./data"


@dataclass
class AppConfig:
    """主配置类"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    api: APIConfig = field(default_factory=APIConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path(__file__).parent.parent.parent / "config"
        self.config = AppConfig()
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        # 先加载默认配置
        default_config = self.config_dir / "default.yaml"
        if default_config.exists():
            self._merge_yaml_file(default_config)

        # 加载环境特定配置
        env = os.getenv("ENVIRONMENT", "development")
        env_config = self.config_dir / f"{env}.yaml"
        if env_config.exists():
            self._merge_yaml_file(env_config)

        # 加载环境变量
        self._merge_env_vars()

        # 确保必要的目录存在
        self._ensure_directories()

    def _merge_yaml_file(self, file_path: Path):
        """合并 YAML 配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                self._merge_dict_data(config_data, self.config)
        except Exception as e:
            logger.warning(f"Failed to load config {file_path}: {e}")

    def _merge_dict_data(self, data: Dict[str, Any], target: Any):
        """递归合并字典数据"""
        if not data:
            return
        
        for key, value in data.items():
            if hasattr(target, key):
                if isinstance(value, dict) and hasattr(getattr(target, key), object):
                    self._merge_dict_data(value, getattr(target, key))
                else:
                    # 处理环境变量插值
                    if isinstance(value, str):
                        value = self._interpolate_env_vars(value)
                    setattr(target, key, value)

    def _interpolate_env_vars(self, value: str) -> str:
        """环境变量插值，如 ${VAR:-default}"""
        pattern = r'\${([^}]+)}'
        
        def replace_env_var(match):
            var_part = match.group(1)
            if ':-' in var_part:
                var_name, default_val = var_part.split(':-', 1)
                return os.getenv(var_name, default_val)
            else:
                return os.getenv(var_name, '')
        
        return re.sub(pattern, replace_env_var, value)

    def _merge_env_vars(self):
        """从环境变量合并配置"""
        prefix = "EA_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_path = key[len(prefix):].lower().split('_')
                self._set_nested_value(self.config, config_path, value)

    def _set_nested_value(self, obj: Any, path: list, value: str):
        """设置嵌套值"""
        current = obj
        for part in path[:-1]:
            if hasattr(current, part):
                current = getattr(current, part)
        
        if hasattr(current, path[-1]):
            # 类型转换
            target_type = type(getattr(current, path[-1]))
            try:
                if target_type == bool:
                    converted_value = value.lower() in ('true', '1', 'yes', 'on')
                elif target_type == int:
                    converted_value = int(value)
                elif target_type == float:
                    converted_value = float(value)
                else:
                    converted_value = value
                
                setattr(current, path[-1], converted_value)
            except (ValueError, TypeError):
                pass

    def _ensure_directories(self):
        """确保必要的目录存在"""
        dirs = [
            self.config.storage.upload_dir,
            self.config.storage.report_dir,
            self.config.storage.data_dir,
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)

    def get(self) -> AppConfig:
        """获取配置"""
        return self.config

    def reload(self):
        """重新加载配置"""
        self.config = AppConfig()
        self._load_config()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "llm": self._dataclass_to_dict(self.config.llm),
            "api": self._dataclass_to_dict(self.config.api),
            "database": self._dataclass_to_dict(self.config.database),
            "cache": self._dataclass_to_dict(self.config.cache),
            "logging": self._dataclass_to_dict(self.config.logging),
            "analysis": self._dataclass_to_dict(self.config.analysis),
            "rag": self._dataclass_to_dict(self.config.rag),
            "monitoring": self._dataclass_to_dict(self.config.monitoring),
            "storage": self._dataclass_to_dict(self.config.storage),
        }

    def _dataclass_to_dict(self, obj: Any) -> Dict[str, Any]:
        """数据类转字典"""
        result = {}
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            if hasattr(value, '__dataclass_fields__'):
                result[field_name] = self._dataclass_to_dict(value)
            else:
                result[field_name] = value
        return result


# 全局配置实例
_config_manager: Optional[ConfigManager] = None
_config_lock = threading.RLock()


def get_config() -> AppConfig:
    """获取配置"""
    global _config_manager
    with _config_lock:
        if _config_manager is None:
            _config_manager = ConfigManager()
        return _config_manager.get()


def reload_config():
    """重新加载配置"""
    global _config_manager
    with _config_lock:
        if _config_manager:
            _config_manager.reload()
