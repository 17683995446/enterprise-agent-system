"""
API Package for Enterprise Agent System
"""

from enterprise_agent_system.infrastructure.api.api_server import (
    app,
    start_api_server,
)
from enterprise_agent_system.infrastructure.api.task_routes import (
    router as task_router,
)
from enterprise_agent_system.infrastructure.api.agent_routes import (
    router as agent_router,
)
from enterprise_agent_system.infrastructure.api.memory_routes import (
    router as memory_router,
)
from enterprise_agent_system.infrastructure.api.project_analyzer_routes import (
    router as project_router,
)

__all__ = [
    "app",
    "start_api_server",
    "task_router",
    "agent_router",
    "memory_router",
    "project_router",
]
