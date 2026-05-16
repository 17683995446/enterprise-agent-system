"""
Core Layer - GitHub Repository Analysis Task
核心层 - GitHub仓库分析任务

职责：
- 定义GitHub仓库分析任务
- 执行真实的GitHub API调用
- 生成分析报告
- 与Agent系统集成
"""

import asyncio
from typing import Optional, Dict, Any

from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionDataModel,
    TaskExecutionStatusEnumeration,
)
from enterprise_agent_system.core.agent_orchestrator_and_executor import (
    AgentOrchestratorAndExecutor,
)
from enterprise_agent_system.infrastructure.github_repository_analyzer import (
    GitHubRepositoryAnalyzer,
    RepositoryAnalysisResult,
)
from enterprise_agent_system.infrastructure.enterprise_logging_system import (
    get_logger_instance,
)

logger = get_logger_instance(__name__)


class GitHubAnalysisTaskExecutor:
    """
    GitHub分析任务执行器

    功能：
    - 创建GitHub分析任务
    - 执行仓库分析
    - 生成分析报告
    - 与Agent记忆系统集成
    """

    def __init__(self, github_token: Optional[str] = None):
        """
        初始化GitHub分析任务执行器

        Args:
            github_token: GitHub个人访问令牌（可选）
        """
        self.analyzer = GitHubRepositoryAnalyzer(github_token=github_token)
        logger.info("GitHub Analysis Task Executor initialized")

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
GitHub仓库分析完成: {result.repository_name}

技术栈: {', '.join(result.tech_stack_list) if result.tech_stack_list else '未检测'}

质量指标:
- Stars: {result.number_of_stars}
- Forks: {result.number_of_forks}
- 主要语言: {result.primary_language}

项目评估:
- 文档完整性: {'✓' if result.has_documentation else '✗'}
- 测试覆盖: {'✓' if result.has_tests else '✗'}
- CI/CD配置: {'✓' if result.has_ci_cd else '✗'}

关键洞察:
- 这是一个{self._assess_project_size(result)}的开源项目
- {'有完善的CI/CD流程，适合生产环境使用' if result.has_ci_cd else '缺少CI/CD配置，需要关注自动化测试和部署'}
- {'文档完善，有助于项目学习和使用' if result.has_documentation else '文档较少，需要加强文档建设'}
"""

            agent.storage_backend.create_new_memory_entry(
                content_text=memory_content,
                category_type=agent.storage_backend.retrieve_all_memories()[0].category_type if agent.storage_backend.retrieve_all_memories() else None,
                tags_list=["github", "analysis", "project-review", result.primary_language or "unknown"],
                importance_score=4,
                source_task_id=None,
            )

            return {
                "success": True,
                "repository_name": result.repository_name,
                "analysis_result": result,
                "report": report,
                "memory_saved": True,
            }

        except Exception as e:
            logger.error(f"GitHub analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "repository_url": repo_url,
            }

    def _assess_project_size(self, result: RepositoryAnalysisResult) -> str:
        """
        评估项目规模

        Args:
            result: 分析结果

        Returns:
            项目规模描述
        """
        stars = result.number_of_stars
        forks = result.number_of_forks

        if stars > 50000 or forks > 10000:
            return "非常大型流行"
        elif stars > 10000 or forks > 2000:
            return "大型成熟"
        elif stars > 1000 or forks > 200:
            return "中等规模活跃"
        elif stars > 100 or forks > 20:
            return "小型成长中"
        else:
            return "小型新起步"

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


async def demo_github_analysis():
    """
    GitHub分析演示
    """
    from enterprise_agent_system.application.command_line_interface_application import (
        CommandLineInterfaceApplication,
    )

    print("\n" + "=" * 80)
    print("GitHub Repository Analysis Demo")
    print("=" * 80 + "\n")

    agent = AgentOrchestratorAndExecutor("GitHub Analyzer Agent")

    executor = GitHubAnalysisTaskExecutor()

    test_repos = [
        "https://github.com/facebook/react",
        "https://github.com/microsoft/vscode",
        "https://github.com/torvalds/linux",
    ]

    print(f"Analyzing {len(test_repos)} popular GitHub repositories...\n")

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
    print(f"\nAgent Statistics:")
    print(f"  Total Memories: {stats.total_memories_count}")
    print(f"  Knowledge Graph Nodes: {stats.knowledge_graph_nodes_count}")


if __name__ == "__main__":
    asyncio.run(demo_github_analysis())
