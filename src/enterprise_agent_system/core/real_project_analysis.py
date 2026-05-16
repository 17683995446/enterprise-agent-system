"""
Core Layer - Real Project Analysis Task
核心层 - 真实项目分析任务

职责：
- 分析本地仓库的项目结构
- 提取代码信息和文档
- 评估项目质量
- 生成项目分析报告
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
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


@dataclass
class ProjectStatistics:
    """项目统计信息"""
    total_files: int = 0
    python_files: int = 0
    test_files: int = 0
    doc_files: int = 0
    code_lines: int = 0
    test_lines: int = 0
    doc_lines: int = 0
    total_folders: int = 0


@dataclass
class ProjectAnalysisResult:
    """项目分析结果"""
    project_name: str
    project_path: str
    project_type: str
    has_tests: bool
    has_ci_cd: bool
    has_docs: bool
    has_readme: bool
    has_pyproject: bool
    has_requirements: bool
    statistics: ProjectStatistics
    analysis_time: str
    tags: List[str]


class RealProjectAnalyzer:
    """真实项目分析器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_name = self.project_path.name
        logger.info(f"Project analyzer initialized for: {self.project_name}")

    def analyze_project(self) -> ProjectAnalysisResult:
        """分析项目"""
        logger.info(f"Starting project analysis: {self.project_path}")

        # 收集项目统计
        stats = self._collect_statistics()

        # 检查项目特征
        has_tests = self._has_tests()
        has_ci_cd = self._has_ci_cd()
        has_docs = self._has_docs()
        has_readme = self._has_readme()
        has_pyproject = (self.project_path / "pyproject.toml").exists()
        has_requirements = (self.project_path / "requirements.txt").exists()

        # 确定项目类型
        project_type = self._identify_project_type()

        # 生成标签
        tags = self._generate_tags(project_type, has_tests, has_ci_cd, has_docs)

        result = ProjectAnalysisResult(
            project_name=self.project_name,
            project_path=str(self.project_path),
            project_type=project_type,
            has_tests=has_tests,
            has_ci_cd=has_ci_cd,
            has_docs=has_docs,
            has_readme=has_readme,
            has_pyproject=has_pyproject,
            has_requirements=has_requirements,
            statistics=stats,
            analysis_time=asyncio.get_event_loop().time().__str__(),
            tags=tags,
        )

        logger.info(f"Project analysis complete for: {self.project_name}")
        return result

    def _collect_statistics(self) -> ProjectStatistics:
        """收集项目统计信息"""
        stats = ProjectStatistics()

        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            
            # 排除.git等隐藏文件夹
            if root_path.name.startswith('.'):
                dirs[:] = []  # 不进入子目录
                continue
            
            stats.total_folders += 1

            for file in files:
                file_path = root_path / file
                stats.total_files += 1

                if file.endswith('.py'):
                    stats.python_files += 1
                    # 简单统计代码行数
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            line_count = len(lines)
                            if 'test' in file_path.name.lower():
                                stats.test_lines += line_count
                            else:
                                stats.code_lines += line_count
                    except Exception as e:
                        pass
                elif file.endswith(('.md', '.rst', '.txt')) and any(term in file.lower() for term in ['readme', 'doc', 'changelog', 'license']):
                    stats.doc_files += 1

        return stats

    def _has_tests(self) -> bool:
        """检查是否有测试"""
        test_dirs = ['tests', 'test', '__tests__']
        for test_dir in test_dirs:
            if (self.project_path / test_dir).exists():
                return True
        # 也检查文件中是否有test_开头的
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    return True
        return False

    def _has_ci_cd(self) -> bool:
        """检查是否有CI/CD配置"""
        ci_dirs = ['.github/workflows', '.gitlab', 'jenkins']
        for ci_dir in ci_dirs:
            if (self.project_path / ci_dir).exists():
                return True
        ci_files = ['.github', '.travis.yml', 'Jenkinsfile', 'circle.yml']
        for ci_file in ci_files:
            if (self.project_path / ci_file).exists():
                return True
        return False

    def _has_docs(self) -> bool:
        """检查是否有文档"""
        doc_dirs = ['docs', 'documentation', 'doc']
        for doc_dir in doc_dirs:
            if (self.project_path / doc_dir).exists():
                return True
        return False

    def _has_readme(self) -> bool:
        """检查是否有README"""
        readme_files = ['README.md', 'README.rst', 'README.txt', 'readme.md']
        for readme in readme_files:
            if (self.project_path / readme).exists():
                return True
        return False

    def _identify_project_type(self) -> str:
        """识别项目类型"""
        # 检查Python项目
        if (self.project_path / 'pyproject.toml').exists() or (self.project_path / 'setup.py').exists():
            return 'Python'
        # 检查Node.js项目
        if (self.project_path / 'package.json').exists():
            return 'Node.js'
        # 检查Java项目
        if (self.project_path / 'pom.xml').exists():
            return 'Java'
        # 检查Rust项目
        if (self.project_path / 'Cargo.toml').exists():
            return 'Rust'
        return 'Unknown'

    def _generate_tags(self, project_type: str, has_tests: bool, has_ci_cd: bool, has_docs: bool) -> List[str]:
        """生成项目标签"""
        tags = ['project', project_type.lower()]
        if has_tests:
            tags.append('has-tests')
        if has_ci_cd:
            tags.append('has-ci-cd')
        if has_docs:
            tags.append('has-docs')
        return tags

    def generate_report(self, result: ProjectAnalysisResult) -> str:
        """生成分析报告"""
        report_lines = [
            "=" * 80,
            f"REAL PROJECT ANALYSIS REPORT - {result.project_name}",
            "=" * 80,
            "",
            f"Project Path: {result.project_path}",
            f"Project Type: {result.project_type}",
            f"Analysis Time: {result.analysis_time}",
            "",
            "-" * 80,
            "PROJECT STATISTICS",
            "-" * 80,
            f"Total Files: {result.statistics.total_files}",
            f"Total Folders: {result.statistics.total_folders}",
            f"Python Files: {result.statistics.python_files}",
            f"Test Files: {result.statistics.test_files}",
            f"Doc Files: {result.statistics.doc_files}",
            f"Code Lines: {result.statistics.code_lines:,}",
            f"Test Lines: {result.statistics.test_lines:,}",
            f"Doc Lines: {result.statistics.doc_lines:,}",
            "",
            "-" * 80,
            "PROJECT FEATURES",
            "-" * 80,
            f"README: {'✅ Yes' if result.has_readme else '❌ No'}",
            f"Tests: {'✅ Yes' if result.has_tests else '❌ No'}",
            f"CI/CD: {'✅ Yes' if result.has_ci_cd else '❌ No'}",
            f"Documentation: {'✅ Yes' if result.has_docs else '❌ No'}",
            f"pyproject.toml: {'✅ Yes' if result.has_pyproject else '❌ No'}",
            f"requirements.txt: {'✅ Yes' if result.has_requirements else '❌ No'}",
            "",
            "-" * 80,
            "PROJECT TAGS",
            "-" * 80,
            f"Tags: {', '.join(result.tags)}",
            "",
            "-" * 80,
            "PROJECT QUALITY EVALUATION",
            "-" * 80,
        ]

        # 简单的质量评分
        quality_score = 0
        if result.has_readme:
            quality_score += 2
        if result.has_tests:
            quality_score += 3
        if result.has_ci_cd:
            quality_score += 2
        if result.has_docs:
            quality_score += 2

        report_lines.append(f"Quality Score: {quality_score}/9")

        if quality_score >= 8:
            report_lines.append("Overall Evaluation: ✅ Excellent - Production-ready!")
        elif quality_score >= 5:
            report_lines.append("Overall Evaluation: ⚠️ Good - Needs some improvements")
        else:
            report_lines.append("Overall Evaluation: ❌ Poor - Significant improvements needed")

        report_lines.extend([
            "",
            "=" * 80,
            "END OF REPORT",
            "=" * 80,
        ])

        return "\n".join(report_lines)


async def analyze_real_project_with_agent(project_path: str):
    """用Agent分析真实项目"""
    print("\n" + "=" * 80)
    print("REAL PROJECT ANALYSIS WITH AGENT SYSTEM")
    print("=" * 80 + "\n")

    # 初始化Agent
    agent = AgentOrchestratorAndExecutor("Real Project Analyzer Agent")
    print(f"✅ Agent initialized: {agent.agent_name}\n")

    # 分析项目
    print(f"🔍 Analyzing project: {project_path}")
    analyzer = RealProjectAnalyzer(project_path)
    result = analyzer.analyze_project()

    # 生成报告
    report = analyzer.generate_report(result)
    print(report)

    # 创建Agent任务
    print(f"\n🎯 Creating agent tasks...")
    task_id1 = agent.create_and_queue_task(
        task_title=f"Analyze {result.project_name} project structure",
        task_description=f"Analyze the project structure, identify key files, and document findings",
        priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL,
    )
    print(f"   ✅ Task created: {task_id1}")

    task_id2 = agent.create_and_queue_task(
        task_title=f"Run quality checks on {result.project_name}",
        task_description=f"Evaluate the project quality based on tests, CI/CD, and documentation",
        priority_level=TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
    )
    print(f"   ✅ Task created: {task_id2}")

    task_id3 = agent.create_and_queue_task(
        task_title=f"Generate documentation summary for {result.project_name}",
        task_description=f"Create a summary of the project's documentation and suggest improvements",
        priority_level=TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL,
    )
    print(f"   ✅ Task created: {task_id3}")

    # 运行Agent
    print(f"\n🚀 Running agent execution loop (5 iterations)...")
    await agent.run_main_execution_loop(max_iteration_count=5)

    # 显示统计信息
    stats = agent.current_system_statistics
    print(f"\n📊 Agent Statistics:")
    print(f"  Total Tasks: {stats.total_tasks_count}")
    print(f"  Completed Tasks: {stats.completed_tasks_count}")
    print(f"  Success Rate: {stats.success_rate_percentage}%")
    print(f"  Total Memories: {stats.total_memories_count}")
    print(f"  Knowledge Graph Nodes: {stats.knowledge_graph_nodes_count}")

    print("\n" + "=" * 80)
    print("REAL PROJECT ANALYSIS COMPLETE!")
    print("=" * 80 + "\n")

    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "/workspace/cookiecutter"
    asyncio.run(analyze_real_project_with_agent(project_path))
