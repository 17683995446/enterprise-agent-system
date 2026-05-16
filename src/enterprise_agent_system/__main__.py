"""
Enterprise Agent System - Main Entry Point
企业级 Agent 系统主入口点
"""

import sys
import asyncio

from enterprise_agent_system.application.command_line_interface_application import (
    main,
)


if __name__ == "__main__":
    main()
