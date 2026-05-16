"""
Application Layer - Command Line Interface Application
应用层 - 命令行界面应用程序

职责：
- 提供用户友好的命令行界面
- 运行演示模式
- 运行测试套件
"""

import sys
import asyncio
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn

    RICH_LIBRARY_AVAILABLE = True
except ImportError:
    RICH_LIBRARY_AVAILABLE = False

from enterprise_agent_system.core.agent_orchestrator_and_executor import (
    AgentOrchestratorAndExecutor,
)
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskPriorityLevelEnumeration,
)
from enterprise_agent_system.infrastructure.enterprise_logging_system import (
    get_logger_instance,
)


logger = get_logger_instance(__name__)


class CommandLineInterfaceApplication:
    """
    命令行界面应用程序类
    """

    def __init__(self):
        self.agent_instance: Optional[AgentOrchestratorAndExecutor] = None

        if RICH_LIBRARY_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

    def display_welcome_banner(self) -> None:
        """显示欢迎横幅"""
        if RICH_LIBRARY_AVAILABLE and self.console:
            banner_content = """
[bold cyan]Enterprise Dual-Mode Perpetual Agent System v8.0.0[/bold cyan]

[dim]An intelligent, self-improving, enterprise-grade agent[/dim]

[green]✓[/green] Task Execution Mode
[green]✓[/green] Idle Improvement Mode
[green]✓[/green] Knowledge Graph Memory
[green]✓[/green] Enterprise-grade Architecture
"""

            banner_panel = Panel(
                banner_content,
                title="[bold blue]Welcome to the Enterprise Agent System[/bold blue]",
                border_style="cyan",
                padding=(1, 2),
            )
            self.console.print(banner_panel)
        else:
            print("=" * 80)
            print("Enterprise Dual-Mode Perpetual Agent System v8.0.0")
            print("=" * 80)

    async def run_complete_demonstration(self) -> None:
        """
        运行完整演示
        """
        self.display_welcome_banner()

        print("\n[Step 1/5] Initializing Agent System...")
        self.agent_instance = AgentOrchestratorAndExecutor(
            "Demonstration Agent"
        )

        print("\n[Step 2/5] Creating demonstration tasks...")

        if RICH_LIBRARY_AVAILABLE and self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                add_tasks_progress = progress.add_task(
                    "Creating tasks...", total=1
                )

                self.agent_instance.create_and_queue_task(
                    "Customer Data Analysis Task",
                    "Analyze customer behavior data for Q4 report",
                    priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL,
                )
                self.agent_instance.create_and_queue_task(
                    "API Documentation Update Task",
                    "Update REST API documentation for version 2",
                    priority_level=TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
                )
                self.agent_instance.create_and_queue_task(
                    "System Backup Operation Task",
                    "Perform daily system backup operation",
                    priority_level=TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL,
                )

                progress.update(add_tasks_progress, advance=1)
        else:
            self.agent_instance.create_and_queue_task(
                "Customer Data Analysis Task",
                "Analyze customer behavior data for Q4 report",
                priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL,
            )
            self.agent_instance.create_and_queue_task(
                "API Documentation Update Task",
                "Update REST API documentation for version 2",
                priority_level=TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
            )
            self.agent_instance.create_and_queue_task(
                "System Backup Operation Task",
                "Perform daily system backup operation",
                priority_level=TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL,
            )

        print("  ✓ Created 3 demonstration tasks with different priorities")

        print("\n[Step 3/5] Running Agent main execution loop (8 iterations)...")

        if RICH_LIBRARY_AVAILABLE and self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                main_loop_progress = progress.add_task(
                    "Agent running...", total=8
                )
                progress.update(main_loop_progress, advance=1)

                await self.agent_instance.run_main_execution_loop(
                    max_iteration_count=8
                )

                progress.update(main_loop_progress, advance=7)
        else:
            await self.agent_instance.run_main_execution_loop(
                max_iteration_count=8
            )

        print("\n[Step 4/5] Gathering final statistics...")
        self.display_system_statistics()

        print("\n[Step 5/5] Demonstration complete!")

        if RICH_LIBRARY_AVAILABLE and self.console:
            self.console.print(
                "\n[bold green]Demonstration completed successfully![/bold green]\n"
            )
        else:
            print("\nDemonstration completed successfully!\n")

    def display_system_statistics(self) -> None:
        """显示系统统计信息"""
        if not self.agent_instance:
            return

        stats = self.agent_instance.current_system_statistics

        if RICH_LIBRARY_AVAILABLE and self.console:
            stats_table = Table(title="System Statistics Report")
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")

            stats_table.add_row(
                "Total Tasks", str(stats.total_tasks_count)
            )
            stats_table.add_row(
                "Completed Tasks", str(stats.completed_tasks_count)
            )
            stats_table.add_row(
                "Pending Tasks", str(stats.pending_tasks_count)
            )
            stats_table.add_row(
                "Failed Tasks", str(stats.failed_tasks_count)
            )
            stats_table.add_row(
                "Success Rate", f"{stats.success_rate_percentage:.1f}%"
            )
            stats_table.add_row(
                "Total Memories", str(stats.total_memories_count)
            )
            stats_table.add_row(
                "Total Experiences", str(stats.total_experiences_count)
            )
            stats_table.add_row(
                "Knowledge Graph Nodes",
                str(stats.knowledge_graph_nodes_count),
            )
            stats_table.add_row(
                "Knowledge Graph Edges",
                str(stats.knowledge_graph_edges_count),
            )
            stats_table.add_row(
                "System Uptime",
                f"{stats.uptime_seconds_value:.1f} seconds",
            )
            stats_table.add_row(
                "Current Mode", stats.current_operating_mode.value
            )

            self.console.print(stats_table)
        else:
            print("\nSystem Statistics Report:")
            print(f"  Total Tasks: {stats.total_tasks_count}")
            print(f"  Completed: {stats.completed_tasks_count}")
            print(f"  Success Rate: {stats.success_rate_percentage:.1f}%")
            print(f"  Total Memories: {stats.total_memories_count}")
            print(
                f"  Knowledge Graph Nodes: {stats.knowledge_graph_nodes_count}"
            )

    def run_test_suite(self) -> bool:
        """
        运行测试套件

        Returns:
            是否所有测试通过
        """
        from enterprise_agent_system.test_suite.unit.test_domain_models import (
            run_domain_model_tests,
        )
        from enterprise_agent_system.test_suite.unit.test_storage_backend import (
            run_storage_backend_tests,
        )
        from enterprise_agent_system.test_suite.integration.test_agent_integration import (
            run_agent_integration_tests,
        )

        print("\n" + "=" * 80)
        print("Running Comprehensive Test Suite")
        print("=" * 80)

        print("\nUnit Tests [1/3] - Domain Models")
        domain_passed, domain_failed = run_domain_model_tests()

        print("\nUnit Tests [2/3] - Storage Backend")
        storage_passed, storage_failed = run_storage_backend_tests()

        print("\nIntegration Tests [3/3] - Agent")
        agent_passed, agent_failed = run_agent_integration_tests()

        total_passed = domain_passed + storage_passed + agent_passed
        total_failed = domain_failed + storage_failed + agent_failed

        print("\n" + "=" * 80)
        print("Test Summary")
        print("=" * 80)
        print(f"Total Passed: {total_passed}")
        print(f"Total Failed: {total_failed}")
        print(f"Total Tests: {total_passed + total_failed}")

        if total_failed == 0:
            print("\nALL TESTS PASSED!")
            return True
        else:
            print(f"\n{total_failed} test(s) failed")
            return False

    def display_help_information(self) -> None:
        """显示帮助信息"""
        help_text = """
Enterprise Dual-Mode Perpetual Agent System v8.0.0

Usage:
    python -m enterprise_agent_system [COMMAND]

Commands:
    demo    - Run complete demonstration (default)
    test    - Run comprehensive test suite
    help    - Show this help message

Examples:
    python -m enterprise_agent_system
    python -m enterprise_agent_system demo
    python -m enterprise_agent_system test

Optional Dependencies:
    pip install rich pydantic

For more information, see README.md
"""
        print(help_text)


def main() -> None:
    """主入口函数"""
    cli = CommandLineInterfaceApplication()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "demo":
            asyncio.run(cli.run_complete_demonstration())
        elif command == "test":
            success = cli.run_test_suite()
            sys.exit(0 if success else 1)
        elif command == "help":
            cli.display_help_information()
        else:
            print(f"Unknown command: {command}")
            cli.display_help_information()
    else:
        asyncio.run(cli.run_complete_demonstration())


if __name__ == "__main__":
    main()
