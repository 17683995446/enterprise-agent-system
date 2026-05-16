"""
Database initialization and utilities
数据库初始化和工具
"""

import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Optional

# 确保项目根目录在路径中
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from enterprise_agent_system.infrastructure.sqlalchemy_database_models import Base
from enterprise_agent_system.infrastructure.enterprise_logging_system import (
    get_logger_instance,
)

logger = get_logger_instance(__name__)


def get_database_url() -> str:
    """
    获取数据库连接 URL

    Returns:
        数据库连接字符串
    """
    db_path = os.getenv("DATABASE_PATH", "agent_system_data.db")
    return f"sqlite+aiosqlite:///{db_path}"


def create_engine(database_url: Optional[str] = None):
    """
    创建异步数据库引擎

    Args:
        database_url: 数据库 URL，如果不提供则从环境变量获取

    Returns:
        SQLAlchemy 异步引擎
    """
    url = database_url or get_database_url()
    logger.info(f"Creating database engine for: {url}")
    return create_async_engine(
        url,
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
        connect_args={"check_same_thread": False} if "sqlite" in url else {},
    )


def create_session_maker(engine):
    """
    创建异步会话工厂

    Args:
        engine: SQLAlchemy 异步引擎

    Returns:
        异步会话工厂
    """
    return sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def init_database(database_url: Optional[str] = None):
    """
    初始化数据库（创建表）

    Args:
        database_url: 数据库 URL
    """
    engine = create_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def drop_all_tables(database_url: Optional[str] = None):
    """
    删除所有表（谨慎使用）

    Args:
        database_url: 数据库 URL
    """
    engine = create_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All tables dropped from database")
