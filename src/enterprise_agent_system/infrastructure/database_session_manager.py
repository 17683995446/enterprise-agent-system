"""
Infrastructure Layer - Database Session Management
基础设施层 - 数据库会话管理

Provides SQLAlchemy async session factory and database operations.
Supports SQLite with aiosqlite for async operations.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from enterprise_agent_system.infrastructure.sqlalchemy_database_models import Base


class DatabaseSessionManager:
    """
    Database session manager for async SQLAlchemy operations

    Features:
    - Async session factory
    - Automatic table creation
    - Connection pooling
    - Graceful shutdown
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        echo: bool = False,
        pool_size: int = 5,
    ):
        """
        Initialize database session manager

        Args:
            database_url: Database connection URL
            echo: Enable SQL echo mode
            pool_size: Connection pool size
        """
        if database_url is None:
            db_path = os.getenv("DATABASE_PATH", "agent_system.db")
            database_url = f"sqlite+aiosqlite:///{db_path}"

        self.database_url = database_url
        self.echo = echo

        self.engine = create_async_engine(
            database_url,
            echo=echo,
            poolclass=NullPool,
            connect_args={"check_same_thread": False}
            if "sqlite" in database_url
            else {},
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def initialize_database(self) -> None:
        """
        Initialize database by creating all tables

        This method should be called once at application startup.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close_database(self) -> None:
        """
        Close database connections gracefully

        This method should be called at application shutdown.
        """
        await self.engine.dispose()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session as context manager

        Usage:
            async with db_manager.get_session() as session:
                result = await session.execute(select(TaskEntity))
        """
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class DatabaseManagerSingleton:
    """
    Singleton database manager for application-wide use

    Provides lazy initialization and global access to database.
    """

    _instance: Optional[DatabaseSessionManager] = None

    @classmethod
    def get_instance(
        cls,
        database_url: Optional[str] = None,
        echo: bool = False,
    ) -> DatabaseSessionManager:
        """
        Get singleton database manager instance

        Args:
            database_url: Database connection URL
            echo: Enable SQL echo mode

        Returns:
            Database session manager instance
        """
        if cls._instance is None:
            cls._instance = DatabaseSessionManager(
                database_url=database_url, echo=echo
            )
        return cls._instance

    @classmethod
    async def initialize(
        cls,
        database_url: Optional[str] = None,
        echo: bool = False,
    ) -> DatabaseSessionManager:
        """
        Initialize and get singleton database manager

        Args:
            database_url: Database connection URL
            echo: Enable SQL echo mode

        Returns:
            Initialized database session manager
        """
        instance = cls.get_instance(database_url=database_url, echo=echo)
        await instance.initialize_database()
        return instance

    @classmethod
    async def close(cls) -> None:
        """
        Close database connections
        """
        if cls._instance is not None:
            await cls._instance.close_database()
            cls._instance = None


db_manager = DatabaseManagerSingleton.get_instance
