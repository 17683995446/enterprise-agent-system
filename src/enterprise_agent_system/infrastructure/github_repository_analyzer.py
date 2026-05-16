"""
Infrastructure Layer - GitHub Repository Analyzer
基础设施层 - GitHub仓库分析器

职责：
- 分析GitHub仓库的结构和质量指标
- 提取项目的技术栈信息
- 评估项目的文档完整性
- 生成项目分析报告
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import httpx

from enterprise_agent_system.infrastructure.enterprise_logging_system import (
    get_logger_instance,
)

logger = get_logger_instance(__name__)


@dataclass
class RepositoryAnalysisResult:
    """仓库分析结果数据类"""
    repository_name: str
    repository_url: str
    primary_language: Optional[str]
    number_of_stars: int
    number_of_forks: int
    number_of_open_issues: int
    number_of_contributors: int
    has_documentation: bool
    has_tests: bool
    has_ci_cd: bool
    readme_content: Optional[str]
    package_json_info: Optional[Dict[str, Any]]
    tech_stack_list: List[str]
    last_commit_timestamp: Optional[str]
    analysis_timestamp: str


class GitHubRepositoryAnalyzer:
    """
    GitHub仓库分析器类

    Features:
    - 获取仓库基本信息
    - 分析项目结构
    - 检测技术栈
    - 评估文档完整性
    - 生成分析报告
    """

    def __init__(self, github_token: Optional[str] = None):
        """
        初始化GitHub仓库分析器

        Args:
            github_token: GitHub个人访问令牌（可选，用于提高API限制）
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
            logger.info("GitHub analyzer initialized with authentication")
        else:
            logger.warning("GitHub analyzer initialized without authentication (rate limited)")

    def _parse_github_url(self, repo_url: str) -> tuple[str, str]:
        """
        解析GitHub URL获取owner和repo名称

        Args:
            repo_url: GitHub仓库URL

        Returns:
            (owner, repo)元组
        """
        parts = repo_url.rstrip("/").split("/")
        if "github.com" in repo_url:
            return parts[-2], parts[-1].replace(".git", "")
        return parts[-2], parts[-1].replace(".git", "")

    async def fetch_repository_info(self, repo_url: str) -> Dict[str, Any]:
        """
        获取仓库基本信息

        Args:
            repo_url: GitHub仓库URL

        Returns:
            仓库信息字典
        """
        owner, repo = self._parse_github_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching repo info: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Error fetching repo info: {str(e)}")
            raise

    async def fetch_readme(self, repo_url: str) -> Optional[str]:
        """
        获取README内容

        Args:
            repo_url: GitHub仓库URL

        Returns:
            README内容或None
        """
        owner, repo = self._parse_github_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}/readme"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    import base64
                    content = base64.b64decode(data["content"]).decode("utf-8")
                    return content
                return None
        except Exception as e:
            logger.warning(f"Could not fetch README: {str(e)}")
            return None

    async def fetch_file_content(self, repo_url: str, file_path: str) -> Optional[str]:
        """
        获取仓库中指定文件的内容

        Args:
            repo_url: GitHub仓库URL
            file_path: 文件路径

        Returns:
            文件内容或None
        """
        owner, repo = self._parse_github_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if "content" in data:
                        import base64
                        content = base64.b64decode(data["content"]).decode("utf-8")
                        return content
                return None
        except Exception as e:
            logger.warning(f"Could not fetch file {file_path}: {str(e)}")
            return None

    async def analyze_repository(self, repo_url: str) -> RepositoryAnalysisResult:
        """
        完整分析GitHub仓库

        Args:
            repo_url: GitHub仓库URL

        Returns:
            仓库分析结果
        """
        logger.info(f"Analyzing repository: {repo_url}")

        repo_info = await self.fetch_repository_info(repo_url)
        readme_content = await self.fetch_readme(repo_url)

        package_json_content = await self.fetch_file_content(repo_url, "package.json")
        package_json_info = None
        if package_json_content:
            try:
                package_json_info = json.loads(package_json_content)
            except json.JSONDecodeError:
                logger.warning("Could not parse package.json")

        has_tests = await self._check_file_exists(repo_url, "test") or \
                     await self._check_file_exists(repo_url, "tests") or \
                     await self._check_file_exists(repo_url, "__tests__")

        has_ci_cd = await self._check_file_exists(repo_url, ".github/workflows") or \
                     await self._check_file_exists(repo_url, ".gitlab-ci.yml") or \
                     await self._check_file_exists(repo_url, "Jenkinsfile")

        tech_stack = self._detect_tech_stack(
            repo_info.get("language"),
            package_json_info,
            readme_content
        )

        result = RepositoryAnalysisResult(
            repository_name=repo_info.get("full_name"),
            repository_url=repo_url,
            primary_language=repo_info.get("language"),
            number_of_stars=repo_info.get("stargazers_count", 0),
            number_of_forks=repo_info.get("forks_count", 0),
            number_of_open_issues=repo_info.get("open_issues_count", 0),
            number_of_contributors=repo_info.get("subscribers_count", 0),
            has_documentation=readme_content is not None and len(readme_content) > 100,
            has_tests=has_tests,
            has_ci_cd=has_ci_cd,
            readme_content=readme_content,
            package_json_info=package_json_info,
            tech_stack_list=tech_stack,
            last_commit_timestamp=repo_info.get("pushed_at"),
            analysis_timestamp=datetime.now().isoformat(),
        )

        logger.info(f"Repository analysis completed: {result.repository_name}")
        return result

    async def _check_file_exists(self, repo_url: str, path: str) -> bool:
        """
        检查文件或目录是否存在

        Args:
            repo_url: GitHub仓库URL
            path: 文件或目录路径

        Returns:
            是否存在
        """
        owner, repo = self._parse_github_url(repo_url)
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers)
                return response.status_code == 200
        except Exception:
            return False

    def _detect_tech_stack(
        self,
        primary_language: Optional[str],
        package_json: Optional[Dict],
        readme_content: Optional[str]
    ) -> List[str]:
        """
        检测技术栈

        Args:
            primary_language: 主要编程语言
            package_json: package.json内容
            readme_content: README内容

        Returns:
            技术栈列表
        """
        tech_stack = []

        if primary_language:
            tech_stack.append(primary_language)

        if package_json:
            dependencies = package_json.get("dependencies", {})
            dev_dependencies = package_json.get("devDependencies", {})

            all_deps = {**dependencies, **dev_dependencies}

            if "react" in all_deps or "react-dom" in all_deps:
                tech_stack.append("React")
            if "vue" in all_deps:
                tech_stack.append("Vue.js")
            if "angular" in all_deps:
                tech_stack.append("Angular")
            if "next" in all_deps:
                tech_stack.append("Next.js")
            if "express" in all_deps:
                tech_stack.append("Express")
            if "fastify" in all_deps:
                tech_stack.append("Fastify")
            if "django" in all_deps or "djangorestframework" in all_deps:
                tech_stack.append("Django")
            if "flask" in all_deps:
                tech_stack.append("Flask")
            if "sqlalchemy" in all_deps:
                tech_stack.append("SQLAlchemy")

        if readme_content:
            readme_lower = readme_content.lower()
            if "docker" in readme_lower:
                tech_stack.append("Docker")
            if "kubernetes" in readme_lower or "k8s" in readme_lower:
                tech_stack.append("Kubernetes")
            if "postgresql" in readme_lower or "postgres" in readme_lower:
                tech_stack.append("PostgreSQL")
            if "redis" in readme_lower:
                tech_stack.append("Redis")
            if "mongodb" in readme_lower:
                tech_stack.append("MongoDB")
            if "graphql" in readme_lower:
                tech_stack.append("GraphQL")
            if "aws" in readme_lower or "amazon" in readme_lower:
                tech_stack.append("AWS")
            if "typescript" in readme_lower:
                tech_stack.append("TypeScript")

        return list(set(tech_stack))

    def generate_analysis_report(self, result: RepositoryAnalysisResult) -> str:
        """
        生成分析报告

        Args:
            result: 分析结果

        Returns:
            格式化的报告文本
        """
        report_lines = [
            f"=" * 80,
            f"GitHub仓库分析报告",
            f"=" * 80,
            f"",
            f"仓库名称: {result.repository_name}",
            f"仓库URL: {result.repository_url}",
            f"分析时间: {result.analysis_timestamp}",
            f"",
            f"-" * 80,
            f"基本指标",
            f"-" * 80,
            f"主要语言: {result.primary_language or '未知'}",
            f"Stars: {result.number_of_stars}",
            f"Forks: {result.number_of_forks}",
            f"开放Issues: {result.number_of_open_issues}",
            f"最后提交: {result.last_commit_timestamp}",
            f"",
            f"-" * 80,
            f"项目质量评估",
            f"-" * 80,
            f"文档完整性: {'✓ 有' if result.has_documentation else '✗ 无'}",
            f"测试覆盖: {'✓ 有' if result.has_tests else '✗ 无'}",
            f"CI/CD配置: {'✓ 有' if result.has_ci_cd else '✗ 无'}",
            f"",
            f"-" * 80,
            f"技术栈",
            f"-" * 80,
        ]

        if result.tech_stack_list:
            for tech in sorted(result.tech_stack_list):
                report_lines.append(f"  • {tech}")
        else:
            report_lines.append("  未检测到技术栈信息")

        if result.package_json_info:
            report_lines.extend([
                f"",
                f"-" * 80,
                f"依赖包信息",
                f"-" * 80,
                f"项目名称: {result.package_json_info.get('name', 'N/A')}",
                f"版本: {result.package_json_info.get('version', 'N/A')}",
                f"描述: {result.package_json_info.get('description', 'N/A')}",
            ])

        report_lines.extend([
            f"",
            f"=" * 80,
            f"报告结束",
            f"=" * 80,
        ])

        return "\n".join(report_lines)
