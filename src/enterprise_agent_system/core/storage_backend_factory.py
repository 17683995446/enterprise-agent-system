"""
Core Layer - Storage Backend Factory
核心层 - 存储后端工厂

职责：
- 根据配置创建合适的存储后端
- 支持多种后端切换（内存、SQLAlchemy、缓存等）
- 单例管理存储实例
"""

import os
import sys
from typing import Optional
from functools import lru_cache

from enterprise_agent_system.core.storage_backend_interface import (
    StorageBackendInterface,
    StorageBackendConfig,
)
from enterprise_agent_system.core.in_memory_data_storage_backend import (
    InMemoryDataStorageBackend,
)
from enterprise_agent_system.infrastructure.enterprise_logging_system import (
    get_logger_instance,
)
from enterprise_agent_system.infrastructure.application_configuration_management import (
    get_application_configuration_instance,
)

logger = get_logger_instance(__name__)


class StorageBackendFactory:
    """存储后端工厂类"""

    _instance: Optional["StorageBackendFactory"] = None
    _current_backend: Optional[StorageBackendInterface] = None
    _config: StorageBackendConfig

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(StorageBackendFactory, cls).__new__(cls)
            cls._instance._config = StorageBackendConfig()
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """初始化工厂"""
        config = get_application_configuration_instance()
        self._config = StorageBackendConfig(
            backend_type=config.database_connection_url_string.split("://")[0]
            if "://" in config.database_connection_url_string
            else "in_memory",
            database_url=config.database_connection_url_string,
        )
        logger.info(f"Storage factory initialized with backend type: {self._config.backend_type}")

    def create_storage_backend(
        self, config: Optional[StorageBackendConfig] = None
    ) -> StorageBackendInterface:
        """
        创建存储后端实例

        Args:
            config: 存储配置（可选），如不提供则使用默认配置

        Returns:
            存储后端实例
        """
        use_config = config or self._config
        logger.info(f"Creating storage backend: {use_config.backend_type}")

        if use_config.backend_type == "in_memory":
            backend = InMemoryDataStorageBackend()
            logger.info("In-memory storage backend created successfully")
            return backend
        elif use_config.backend_type in ["sqlite", "postgresql", "mysql"]:
            try:
                # 可选的 SQLAlchemy 后端导入
                from enterprise_agent_system.core.persistent_data_storage_backend import (
                    PersistentStorageBackend,
                )
                from enterprise_agent_system.infrastructure.database_session_manager import (
                    DatabaseSessionManager,
                )

                # 目前默认回退到内存后端，因为持久化后端需要异步会话
                logger.warning(
                    f"SQLAlchemy backend ({use_config.backend_type}) partially implemented, falling back to in-memory"
                )
                return InMemoryDataStorageBackend()
            except Exception as e:
                logger.warning(
                    f"Failed to create SQLAlchemy backend: {str(e)}, falling back to in-memory"
                )
                return InMemoryDataStorageBackend()
        else:
            logger.warning(
                f"Unknown backend type: {use_config.backend_type}, falling back to in-memory"
            )
            return InMemoryDataStorageBackend()

    def get_current_backend(self) -> StorageBackendInterface:
        """
        获取当前使用的存储后端

        Returns:
            当前存储后端实例
        """
        if self._current_backend is None:
            self._current_backend = self.create_storage_backend()
        return self._current_backend

    def reset(self) -> None:
        """重置工厂，清除当前后端实例"""
        self._current_backend = None
        self._initialize()
        logger.info("Storage backend factory reset")


@lru_cache(maxsize=1)
def get_storage_factory() -> StorageBackendFactory:
    """
    获取存储后端工厂单例

    Returns:
        存储后端工厂实例
    """
    return StorageBackendFactory()


def get_storage_backend_instance() -> StorageBackendInterface:
    """
    获取存储后端实例（向后兼容）

    Returns:
        存储后端实例
    """
    return get_storage_factory().get_current_backend()


def reset_storage_backend_instance() -> None:
    """重置存储后端实例（向后兼容）"""
    get_storage_factory.cache_clear()
    factory = StorageBackendFactory()
    factory.reset()
    # 清除单例，强制重新初始化
    StorageBackendFactory._instance = None
    StorageBackendFactory._current_backend = None
