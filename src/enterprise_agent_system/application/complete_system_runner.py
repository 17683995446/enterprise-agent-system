"""
Application Layer - Complete System Runner
应用层 - 完整系统运行器

提供多种运行模式：
- CLI 模式
- API 服务器模式
- Docker 模式
"""

import sys
import asyncio
import argparse
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from enterprise_agent_system.infrastructure.enterprise_logging_system import (
    get_logger_instance,
)
from enterprise_agent_system.infrastructure.application_configuration_management import (
    get_application_configuration_instance,
)


logger = get_logger_instance(__name__)
console = Console() if RICH_AVAILABLE else None
config = get_application_configuration_instance()


def display_system_banner() -> None:
    """显示系统横幅"""
    if RICH_AVAILABLE and console:
        banner_content = f"""
[bold cyan]{config.application_name_string}[/bold cyan] v{config.application_version_string}

[dim]企业级双模式永续运行 Agent 系统[/dim]

[green]✓[/green] 双模式运行 (任务执行 + 空闲改进)
[green]✓[/green] 知识图谱记忆
[green]✓[/green] 优先级任务调度
[green]✓[/green] REST API (FastAPI)
[green]✓[/green] Prometheus 监控
[green]✓[/green] Docker 部署支持
"""
        panel = Panel(
            banner_content,
            title="[bold blue]Enterprise Agent System[/bold blue]",
            border_style="cyan",
            padding=(1, 2),
        )
        console.print(panel)
    else:
        print("=" * 60)
        print(f"{config.application_name_string} v{config.application_version_string}")
        print("=" * 60)


async def run_cli_mode() -> None:
    """运行 CLI 模式"""
    display_system_banner()

    from enterprise_agent_system.application.command_line_interface_application import (
        CommandLineInterfaceApplication,
    )

    cli = CommandLineInterfaceApplication()
    await cli.run_complete_demonstration()


async def run_api_mode(host: str = "0.0.0.0", port: int = 8000) -> None:
    """运行 API 服务器模式"""
    display_system_banner()

    try:
        import uvicorn
        from enterprise_agent_system.infrastructure.fastapi_rest_api_application import (
            app,
            set_agent_instance,
        )
        from enterprise_agent_system.core.agent_orchestrator_and_executor import (
            AgentOrchestratorAndExecutor,
        )

        agent = AgentOrchestratorAndExecutor("API Agent")
        set_agent_instance(agent)

        logger.info(f"Starting API server on {host}:{port}")

        if RICH_AVAILABLE and console:
            console.print(f"[green]API Server running at http://{host}:{port}[/green]")
            console.print(f"[dim]Swagger UI: http://{host}:{port}/docs[/dim]")

        config = get_application_configuration_instance()
        await uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=config.logging_level_setting_string.lower(),
        )
    except ImportError:
        logger.error("FastAPI/Uvicorn not installed. Run: pip install fastapi uvicorn")
        sys.exit(1)


def run_test_mode() -> None:
    """运行测试模式"""
    display_system_banner()

    from enterprise_agent_system.application.command_line_interface_application import (
        CommandLineInterfaceApplication,
    )

    cli = CommandLineInterfaceApplication()
    success = cli.run_test_suite()
    sys.exit(0 if success else 1)


def main() -> None:
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="Enterprise Dual-Mode Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "mode",
        nargs="?",
        default="cli",
        choices=["cli", "api", "test"],
        help="运行模式: cli (默认), api, test",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API 主机地址 (默认: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API 端口号 (默认: 8000)",
    )

    args = parser.parse_args()

    if args.mode == "cli":
        asyncio.run(run_cli_mode())
    elif args.mode == "api":
        asyncio.run(run_api_mode(host=args.host, port=args.port))
    elif args.mode == "test":
        run_test_mode()


if __name__ == "__main__":
    main()
