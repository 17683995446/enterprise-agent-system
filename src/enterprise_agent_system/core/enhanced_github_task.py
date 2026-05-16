"""
Core Layer - Enhanced GitHub Repository Analysis Task
核心层 - 增强版GitHub仓库分析任务

职责：
- 定义GitHub仓库分析任务
- 执行真实的GitHub API调用或模拟数据
- 支持多种分析模式
- 生成分析报告
- 与Agent系统集成
"""

import asyncio
from typing import Optional, Dict, Any

from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
)
from enterprise_agent_system.core.agent_orchestrator_and_executor import (
    AgentOrchestratorAndExecutor,
)
from enterprise_agent_system.infrastructure.enhanced_github_analyzer import (
    EnhancedGitHubRepositoryAnalyzer,
    RepositoryAnalysisResult,
    AnalysisMode,
)
from enterprise_agent_system.infrastructure.enterprise_logging_system import (
    get_logger_instance,
)

logger = get_logger_instance(__name__)


class EnhancedGitHubAnalysisTaskExecutor:
    """
    增强版GitHub分析任务执行器

    功能：
    - 创建GitHub分析任务
    - 支持LIVE/MOCK/AUTO三种模式
    - 执行仓库分析
    - 生成分析报告
    - 与Agent记忆系统集成
    """

    def __init__(
        self,
        github_token: Optional[str] = None,
        analysis_mode: AnalysisMode = AnalysisMode.AUTO
    ):
        """
        初始化增强版GitHub分析任务执行器

        Args:
            github_token: GitHub个人访问令牌（可选）
            analysis_mode: 分析模式
        """
        self.analyzer = EnhancedGitHubRepositoryAnalyzer(
            github_token=github_token,
            analysis_mode=analysis_mode
        )
        logger.info(f"Enhanced GitHub Analysis Executor initialized (mode: {analysis_mode.value})")

    async def execute_github_analysis(
        self,
        repo_url: str,
        agent: AgentOrchestratorAndExecutor
    ) -> Dict[str, Any]:
        """
        执行GitHub仓库分析任务

        Args:
            repo_url: GitHub仓库URL
            agent: Agent实例用于记录记忆

        Returns:
            分析结果字典
        """
        logger.info(f"Starting GitHub analysis for: {repo_url}")

        try:
            result = await self.analyzer.analyze_repository(repo_url)

            report = self.analyzer.generate_analysis_report(result)

            memory_content = f"""
GitHub仓库分析完成: {result.repository_name} (模式: {result.analysis_mode})

技术栈: {', '.join(result.tech_stack_list) if result.tech_stack_list else '未检测'}

质量指标:
- Stars: {result.number_of_stars:,}
- Forks: {result.number_of_forks:,}
- 主要语言: {result.primary_language}

项目评估:
- 文档完整性: {'✅ 有' if result.has_documentation else '❌ 无'}
- 测试覆盖: {'✅ 有' if result.has_tests else '❌ 无'}
- CI/CD配置: {'✅ 有' if result.has_ci_cd else '❌ 无'}
"""

            agent.storage_backend.create_new_memory_entry(
                content_text=memory_content,
                category_type=None,
                tags_list=[
                    "github",
                    "analysis",
                    "project-review",
                    result.primary_language.lower() if result.primary_language else "unknown",
                    f"mode-{result.analysis_mode.lower()}"
                ],
                importance_score=4,
                source_task_id=None,
            )

            return {
                "success": True,
                "repository_name": result.repository_name,
                "analysis_result": result,
                "report": report,
                "memory_saved": True,
                "analysis_mode": result.analysis_mode,
            }

        except Exception as e:
            logger.error(f"GitHub analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "repository_url": repo_url,
            }

    async def execute_multiple_repositories(
        self,
        repo_urls: list[str],
        agent: AgentOrchestratorAndExecutor
    ) -> list[Dict[str, Any]]:
        """
        批量执行多个仓库分析

        Args:
            repo_urls: 仓库URL列表
            agent: Agent实例

        Returns:
            分析结果列表
        """
        logger.info(f"Starting batch analysis for {len(repo_urls)} repositories")

        tasks = [
            self.execute_github_analysis(repo_url, agent)
            for repo_url in repo_urls
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed = [r for r in results if not (isinstance(r, dict) and r.get("success"))]

        logger.info(f"Batch analysis completed: {len(successful)} successful, {len(failed)} failed")

        return results


async def demo_enhanced_github_analysis():
    """增强版GitHub分析演示"""
    from enterprise_agent_system.application.command_line_interface_application import (
        CommandLineInterfaceApplication,
    )

    print("\n" + "=" * 80)
    print("Enhanced GitHub Repository Analysis Demo")
    print("=" * 80 + "\n")

    print("📝 Available Analysis Modes:")
    print("  • LIVE  - Real GitHub API calls (requires token)")
    print("  • MOCK  - Simulated data (perfect for demos)")
    print("  • AUTO  - Auto-detect (default)")
    print()

    agent = AgentOrchestratorAndExecutor("Enhanced GitHub Analyzer Agent")

    executor = EnhancedGitHubAnalysisTaskExecutor(analysis_mode=AnalysisMode.AUTO)

    test_repos = [
        "https://github.com/facebook/react",
        "https://github.com/microsoft/vscode",
        "https://github.com/fastapi/fastapi",
    ]

    print(f"🔍 Analyzing {len(test_repos)} popular GitHub repositories...\n")

    for repo_url in test_repos:
        print(f"\n{'=' * 80}")
        print(f"Analyzing: {repo_url}")
        print("=" * 80)

        result = await executor.execute_github_analysis(repo_url, agent)

        if result["success"]:
            print(result["report"])
        else:
            print(f"\n❌ Analysis failed: {result.get('error', 'Unknown error')}")

        print()

    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80)

    stats = agent.current_system_statistics
    print(f"\n📊 Agent Statistics:")
    print(f"  • Total Memories: {stats.total_memories_count}")
    print(f"  • Knowledge Graph Nodes: {stats.knowledge_graph_nodes_count}")

    print("\n💡 Next Steps:")
    print("  • Set GITHUB_TOKEN environment variable for LIVE analysis")
    print("  • Try AnalysisMode.LIVE for real API calls")


if __name__ == "__main__":
    asyncio.run(demo_enhanced_github_analysis())
