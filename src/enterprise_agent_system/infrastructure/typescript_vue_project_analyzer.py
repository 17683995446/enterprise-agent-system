"""
Infrastructure Layer - TypeScript and Vue.js Project Analyzer
基础设施层 - TypeScript和Vue.js项目分析器

职责：
- 分析TypeScript/JavaScript/Vue.js项目结构
- 提取包信息和依赖关系
- 评估项目质量
- 生成项目分析报告
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
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
class TypeScriptProjectStatistics:
    """TypeScript项目统计信息"""
    total_files: int = 0
    type_script_files: int = 0
    java_script_files: int = 0
    vue_files: int = 0
    test_files: int = 0
    doc_files: int = 0
    config_files: int = 0
    code_lines: int = 0
    test_lines: int = 0
    doc_lines: int = 0
    total_folders: int = 0
    package_count: int = 0


@dataclass
class PackageInfo:
    """包信息"""
    name: str = ""
    version: str = ""
    path: str = ""
    type: str = "unknown"
    dependencies_count: int = 0
    dev_dependencies_count: int = 0


@dataclass
class TypeScriptProjectAnalysisResult:
    """TypeScript项目分析结果"""
    project_name: str
    project_path: str
    project_type: str
    framework: str
    has_tests: bool
    has_ci_cd: bool
    has_docs: bool
    has_readme: bool
    has_type_script: bool
    has_eslint: bool
    has_prettier: bool
    has_vite: bool
    has_monorepo: bool
    statistics: TypeScriptProjectStatistics
    packages: List[PackageInfo]
    analysis_time: str
    tags: List[str]


class TypeScriptVueProjectAnalyzer:
    """TypeScript和Vue.js项目分析器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_name = self.project_path.name
        self.visited_dirs: Set[str] = set()
        logger.info(f"TypeScript/Vue.js Project analyzer initialized for: {self.project_name}")

    def analyze_project(self) -> TypeScriptProjectAnalysisResult:
        """分析TypeScript/Vue.js项目"""
        logger.info(f"Starting TypeScript/Vue.js project analysis: {self.project_path}")

        stats = self._collect_statistics()
        packages = self._collect_package_info()

        has_tests = self._has_tests()
        has_ci_cd = self._has_ci_cd()
        has_docs = self._has_docs()
        has_readme = self._has_readme()
        has_type_script = self._has_type_script()
        has_eslint = self._has_eslint()
        has_prettier = self._has_prettier()
        has_vite = self._has_vite()
        has_monorepo = self._is_monorepo()

        project_type = self._identify_project_type()
        framework = self._identify_framework()

        tags = self._generate_tags(
            project_type, framework, has_tests, has_ci_cd, has_docs, has_monorepo
        )

        result = TypeScriptProjectAnalysisResult(
            project_name=self.project_name,
            project_path=str(self.project_path),
            project_type=project_type,
            framework=framework,
            has_tests=has_tests,
            has_ci_cd=has_ci_cd,
            has_docs=has_docs,
            has_readme=has_readme,
            has_type_script=has_type_script,
            has_eslint=has_eslint,
            has_prettier=has_prettier,
            has_vite=has_vite,
            has_monorepo=has_monorepo,
            statistics=stats,
            packages=packages,
            analysis_time=asyncio.get_event_loop().time().__str__(),
            tags=tags,
        )

        logger.info(f"TypeScript/Vue.js project analysis complete for: {self.project_name}")
        return result

    def _collect_statistics(self) -> TypeScriptProjectStatistics:
        """收集项目统计信息"""
        stats = TypeScriptProjectStatistics()

        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            dir_id = str(root_path.resolve())

            if dir_id in self.visited_dirs:
                continue
            self.visited_dirs.add(dir_id)

            if root_path.name.startswith('.'):
                dirs[:] = []
                continue

            if root_path.name in ['node_modules', 'dist', 'build', 'coverage', '__pycache__']:
                dirs[:] = []
                continue

            stats.total_folders += 1

            for file in files:
                file_path = root_path / file
                stats.total_files += 1

                if file.endswith(('.ts', '.tsx')):
                    stats.type_script_files += 1
                    self._count_lines(file_path, stats, is_test='spec.' in file or '.test.' in file or '.bench.' in file)
                elif file.endswith(('.js', '.jsx', '.mjs', '.cjs')):
                    stats.java_script_files += 1
                    self._count_lines(file_path, stats, is_test='spec.' in file or '.test.' in file)
                elif file.endswith('.vue'):
                    stats.vue_files += 1
                    self._count_lines(file_path, stats, is_test=False)
                elif file.endswith(('.json', '.config.js', '.config.ts')):
                    if any(term in file.lower() for term in ['package', 'tsconfig', 'eslint', 'prettier', 'vite', 'jest']):
                        stats.config_files += 1
                elif file.endswith(('.md', '.rst')) and any(term in file.lower() for term in ['readme', 'doc', 'changelog', 'license']):
                    stats.doc_files += 1
                    self._count_lines(file_path, stats, is_doc=True)

        stats.package_count = self._count_packages()
        return stats

    def _count_lines(self, file_path: Path, stats: TypeScriptProjectStatistics, is_test: bool = False, is_doc: bool = False):
        """统计文件行数"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = len(f.readlines())
                if is_doc:
                    stats.doc_lines += lines
                elif is_test:
                    stats.test_lines += lines
                else:
                    stats.code_lines += lines
        except Exception:
            pass

    def _count_packages(self) -> int:
        """统计packages数量"""
        packages_dir = self.project_path / 'packages'
        if packages_dir.exists():
            return len([d for d in packages_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
        return 0

    def _collect_package_info(self) -> List[PackageInfo]:
        """收集包信息"""
        packages = []

        root_package_json = self.project_path / 'package.json'
        if root_package_json.exists():
            try:
                with open(root_package_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pkg = PackageInfo(
                        name=data.get('name', 'unknown'),
                        version=data.get('version', 'unknown'),
                        path=str(self.project_path),
                        type='root',
                        dependencies_count=len(data.get('dependencies', {})),
                        dev_dependencies_count=len(data.get('devDependencies', {}))
                    )
                    packages.append(pkg)
            except Exception as e:
                logger.warning(f"Failed to parse root package.json: {e}")

        packages_dir = self.project_path / 'packages'
        if packages_dir.exists():
            for pkg_dir in packages_dir.iterdir():
                if pkg_dir.is_dir() and not pkg_dir.name.startswith('.'):
                    pkg_json = pkg_dir / 'package.json'
                    if pkg_json.exists():
                        try:
                            with open(pkg_json, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                pkg = PackageInfo(
                                    name=data.get('name', 'unknown'),
                                    version=data.get('version', 'unknown'),
                                    path=str(pkg_dir),
                                    type='monorepo-package',
                                    dependencies_count=len(data.get('dependencies', {})),
                                    dev_dependencies_count=len(data.get('devDependencies', {}))
                                )
                                packages.append(pkg)
                        except Exception:
                            pass

        return packages

    def _has_tests(self) -> bool:
        """检查是否有测试"""
        test_patterns = ['__tests__', 'test', 'tests', '.spec.', '.test.', 'spec.ts', 'test.ts', '.bench.ts']
        for root, dirs, files in os.walk(self.project_path):
            if any(pattern in root for pattern in ['node_modules', 'dist']):
                continue
            for pattern in test_patterns:
                if pattern in ' '.join(files) or pattern in root:
                    return True
        return False

    def _has_ci_cd(self) -> bool:
        """检查是否有CI/CD配置"""
        ci_paths = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', '.circleci', 'azure-pipelines.yml']
        for ci_path in ci_paths:
            if (self.project_path / ci_path).exists():
                return True
        return False

    def _has_docs(self) -> bool:
        """检查是否有文档"""
        doc_dirs = ['docs', 'documentation', 'doc', 'api', 'guide']
        for doc_dir in doc_dirs:
            if (self.project_path / doc_dir).exists():
                return True
        return False

    def _has_readme(self) -> bool:
        """检查是否有README"""
        readme_files = ['README.md', 'README.rst', 'readme.md']
        for readme in readme_files:
            if (self.project_path / readme).exists():
                return True
        return False

    def _has_type_script(self) -> bool:
        """检查是否有TypeScript"""
        return (self.project_path / 'tsconfig.json').exists()

    def _has_eslint(self) -> bool:
        """检查是否有ESLint"""
        eslint_files = ['.eslintrc', '.eslintrc.js', '.eslintrc.json', '.eslintrc.cjs', 'eslint.config.js']
        for eslint in eslint_files:
            if (self.project_path / eslint).exists():
                return True
        return False

    def _has_prettier(self) -> bool:
        """检查是否有Prettier"""
        prettier_files = ['.prettierrc', '.prettierrc.json', '.prettierrc.js', 'prettier.config.js']
        for prettier in prettier_files:
            if (self.project_path / prettier).exists():
                return True
        return False

    def _has_vite(self) -> bool:
        """检查是否使用Vite"""
        if (self.project_path / 'vite.config.ts').exists() or (self.project_path / 'vite.config.js').exists():
            return True
        root_package = self.project_path / 'package.json'
        if root_package.exists():
            try:
                with open(root_package, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    if 'vite' in deps:
                        return True
            except Exception:
                pass
        return False

    def _is_monorepo(self) -> bool:
        """检查是否是monorepo"""
        return (self.project_path / 'packages').exists() or (self.project_path / 'pnpm-workspace.yaml').exists()

    def _identify_project_type(self) -> str:
        """识别项目类型"""
        if self._has_vite():
            return 'Vite-based SPA'
        if (self.project_path / 'webpack.config.js').exists():
            return 'Webpack-based'
        if (self.project_path / 'rollup.config.js').exists():
            return 'Rollup-based'
        if (self.project_path / 'tsconfig.json').exists():
            return 'TypeScript Library'
        return 'JavaScript Project'

    def _identify_framework(self) -> str:
        """识别框架"""
        root_package = self.project_path / 'package.json'
        if root_package.exists():
            try:
                with open(root_package, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}

                    if '@vue/' in ' '.join(deps.keys()):
                        return 'Vue.js'
                    if 'react' in deps:
                        return 'React'
                    if 'angular' in deps or '@angular/' in ' '.join(deps.keys()):
                        return 'Angular'
                    if 'svelte' in deps:
                        return 'Svelte'
                    if 'nuxt' in deps:
                        return 'Nuxt'
                    if 'next' in deps:
                        return 'Next.js'
            except Exception:
                pass
        return 'Vanilla JS/TS'

    def _generate_tags(
        self,
        project_type: str,
        framework: str,
        has_tests: bool,
        has_ci_cd: bool,
        has_docs: bool,
        has_monorepo: bool
    ) -> List[str]:
        """生成项目标签"""
        tags = ['typescript', framework.lower().replace('.js', '').replace(' ', '-')]
        if has_tests:
            tags.append('tested')
        if has_ci_cd:
            tags.append('ci-cd')
        if has_docs:
            tags.append('documented')
        if has_monorepo:
            tags.append('monorepo')
        tags.append(project_type.lower().replace(' ', '-'))
        return tags

    def generate_report(self, result: TypeScriptProjectAnalysisResult) -> str:
        """生成分析报告"""
        report_lines = [
            "=" * 80,
            f"TYPE SCRIPT & VUE.JS PROJECT ANALYSIS REPORT - {result.project_name}",
            "=" * 80,
            "",
            f"Project Path: {result.project_path}",
            f"Project Type: {result.project_type}",
            f"Framework: {result.framework}",
            f"Analysis Time: {result.analysis_time}",
            "",
            "-" * 80,
            "PROJECT STATISTICS",
            "-" * 80,
            f"Total Files: {result.statistics.total_files:,}",
            f"Total Folders: {result.statistics.total_folders}",
            f"TypeScript Files: {result.statistics.type_script_files:,}",
            f"JavaScript Files: {result.statistics.java_script_files:,}",
            f"Vue Files: {result.statistics.vue_files:,}",
            f"Config Files: {result.statistics.config_files:,}",
            f"Code Lines: {result.statistics.code_lines:,}",
            f"Test Lines: {result.statistics.test_lines:,}",
            f"Doc Lines: {result.statistics.doc_lines:,}",
            f"Package Count: {result.statistics.package_count}",
            "",
            "-" * 80,
            "MONOREPO PACKAGES",
            "-" * 80,
        ]

        if result.packages:
            for pkg in result.packages:
                report_lines.append(
                    f"  📦 {pkg.name}@{pkg.version} ({pkg.type}) - "
                    f"{pkg.dependencies_count} deps, {pkg.dev_dependencies_count} devDeps"
                )
        else:
            report_lines.append("  No packages found")

        report_lines.extend([
            "",
            "-" * 80,
            "PROJECT FEATURES",
            "-" * 80,
            f"README: {'✅ Yes' if result.has_readme else '❌ No'}",
            f"Tests: {'✅ Yes' if result.has_tests else '❌ No'}",
            f"CI/CD: {'✅ Yes' if result.has_ci_cd else '❌ No'}",
            f"Documentation: {'✅ Yes' if result.has_docs else '❌ No'}",
            f"TypeScript: {'✅ Yes' if result.has_type_script else '❌ No'}",
            f"ESLint: {'✅ Yes' if result.has_eslint else '❌ No'}",
            f"Prettier: {'✅ Yes' if result.has_prettier else '❌ No'}",
            f"Vite: {'✅ Yes' if result.has_vite else '❌ No'}",
            f"Monorepo: {'✅ Yes' if result.has_monorepo else '❌ No'}",
            "",
            "-" * 80,
            "PROJECT TAGS",
            "-" * 80,
            f"Tags: {', '.join(result.tags)}",
            "",
            "-" * 80,
            "PROJECT QUALITY EVALUATION",
            "-" * 80,
        ])

        quality_score = 0
        if result.has_readme:
            quality_score += 1
        if result.has_tests:
            quality_score += 2
        if result.has_ci_cd:
            quality_score += 2
        if result.has_docs:
            quality_score += 1
        if result.has_type_script:
            quality_score += 1
        if result.has_eslint:
            quality_score += 1
        if result.has_monorepo:
            quality_score += 1

        report_lines.append(f"Quality Score: {quality_score}/10")

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


async def analyze_typescript_vue_project_with_agent(project_path: str):
    """用Agent分析TypeScript/Vue.js项目"""
    print("\n" + "=" * 80)
    print("TYPESCRIPT & VUE.JS PROJECT ANALYSIS WITH AGENT SYSTEM")
    print("=" * 80 + "\n")

    agent = AgentOrchestratorAndExecutor("TypeScript Vue.js Project Analyzer Agent")
    print(f"✅ Agent initialized: {agent.agent_name}\n")

    print(f"🔍 Analyzing TypeScript/Vue.js project: {project_path}")
    analyzer = TypeScriptVueProjectAnalyzer(project_path)
    result = analyzer.analyze_project()

    report = analyzer.generate_report(result)
    print(report)

    print(f"\n🎯 Creating agent tasks for complex analysis...")
    task_id1 = agent.create_and_queue_task(
        task_title=f"Analyze {result.project_name} reactivity system architecture",
        task_description=f"Deep analysis of the reactivity system in {result.project_name}, identify key components and patterns",
        priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL,
    )
    print(f"   ✅ Task created: {task_id1}")

    task_id2 = agent.create_and_queue_task(
        task_title=f"Analyze {result.project_name} monorepo package dependencies",
        task_description=f"Analyze the dependencies between packages in the monorepo structure",
        priority_level=TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
    )
    print(f"   ✅ Task created: {task_id2}")

    task_id3 = agent.create_and_queue_task(
        task_title=f"Evaluate {result.project_name} code quality and test coverage",
        task_description=f"Evaluate the overall code quality, test coverage, and best practices",
        priority_level=TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
    )
    print(f"   ✅ Task created: {task_id3}")

    print(f"\n🚀 Running agent execution loop (5 iterations)...")
    await agent.run_main_execution_loop(max_iteration_count=5)

    stats = agent.current_system_statistics
    print(f"\n📊 Agent Statistics:")
    print(f"  Total Tasks: {stats.total_tasks_count}")
    print(f"  Completed Tasks: {stats.completed_tasks_count}")
    print(f"  Success Rate: {stats.success_rate_percentage}%")
    print(f"  Total Memories: {stats.total_memories_count}")
    print(f"  Knowledge Graph Nodes: {stats.knowledge_graph_nodes_count}")

    print("\n" + "=" * 80)
    print("TYPESCRIPT & VUE.JS PROJECT ANALYSIS COMPLETE!")
    print("=" * 80 + "\n")

    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "/workspace/vue-core"
    asyncio.run(analyze_typescript_vue_project_with_agent(project_path))
