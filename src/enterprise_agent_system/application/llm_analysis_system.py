"""
LLM Analysis System with Enhanced Capabilities
Application Layer - LLM驱动的增强分析系统
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from enterprise_agent_system.infrastructure.llm_integration import (
    get_llm_manager,
    AdvancedLLMManager,
    CompletionResult,
    AnalysisOptions,
    AnalysisDepth,
)
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance


logger = get_logger_instance(__name__)


@dataclass
class AnalysisReport:
    """分析报告"""
    title: str
    content: str
    findings: List[str]
    recommendations: List[str]
    quality_score: float
    confidence: float
    processing_time: float


class EnhancedCodeAnalyzer:
    """LLM驱动的增强代码分析器"""
    
    def __init__(self):
        self.llm = get_llm_manager()
        self.analysis_cache: Dict[str, AnalysisReport] = {}
        logger.info("EnhancedCodeAnalyzer initialized with LLM support")
    
    async def analyze_file(self, file_path: str) -> AnalysisReport:
        """分析单个文件"""
        logger.info(f"Analyzing file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            lines = len(code.split('\n'))
            ext = Path(file_path).suffix
            
            options = AnalysisOptions(
                depth=AnalysisDepth.DEEP,
                include_security=True,
                include_performance=True,
                include_best_practices=True,
            )
            
            result = await self.llm.analyze_code(
                code=code,
                language=self._get_language(ext),
                options=options,
            )
            
            findings = self._extract_findings(result.content)
            recommendations = self._extract_recommendations(result.content)
            
            return AnalysisReport(
                title=f"代码分析报告: {Path(file_path).name}",
                content=result.content,
                findings=findings,
                recommendations=recommendations,
                quality_score=self._calculate_quality_score(findings, recommendations),
                confidence=0.85,
                processing_time=result.latency,
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return AnalysisReport(
                title=f"Error analyzing {file_path}",
                content=str(e),
                findings=[],
                recommendations=[],
                quality_score=0.0,
                confidence=0.0,
                processing_time=0.0,
            )
    
    async def analyze_project(self, project_path: str) -> Dict[str, AnalysisReport]:
        """分析整个项目"""
        logger.info(f"Analyzing project: {project_path}")
        
        project_reports = {}
        project_dir = Path(project_path)
        
        code_files = []
        for pattern in ['**/*.py', '**/*.js', '**/*.ts', '**/*.tsx', '**/*.java']:
            code_files.extend(project_dir.glob(pattern))
        
        code_files = [f for f in code_files if not any(
            part.startswith('.') or part in ['node_modules', '__pycache__', 'venv', '.venv']
            for part in f.parts
        )]
        
        code_files = code_files[:30]
        
        tasks = [self.analyze_file(str(file_path)) for file_path in code_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for file_path, result in zip(code_files, results):
            if isinstance(result, AnalysisReport):
                project_reports[str(file_path)] = result
        
        project_summary = await self._generate_project_summary(project_reports)
        
        return {
            "files": project_reports,
            "summary": project_summary,
        }
    
    async def analyze_security(self, code: str, language: str = "python") -> AnalysisReport:
        """专门的安全分析"""
        logger.info(f"Performing security analysis for {language}")
        
        result = await self.llm.analyze_security(code=code, language=language)
        
        findings = self._extract_findings(result.content)
        recommendations = self._extract_recommendations(result.content)
        
        return AnalysisReport(
            title=f"{language}代码安全分析",
            content=result.content,
            findings=findings,
            recommendations=recommendations,
            quality_score=self._calculate_quality_score(findings, recommendations),
            confidence=0.9,
            processing_time=result.latency,
        )
    
    async def analyze_performance(self, code: str, language: str = "python") -> AnalysisReport:
        """专门的性能分析"""
        logger.info(f"Performing performance analysis for {language}")
        
        result = await self.llm.analyze_performance(code=code, language=language)
        
        findings = self._extract_findings(result.content)
        recommendations = self._extract_recommendations(result.content)
        
        return AnalysisReport(
            title=f"{language}代码性能分析",
            content=result.content,
            findings=findings,
            recommendations=recommendations,
            quality_score=self._calculate_quality_score(findings, recommendations),
            confidence=0.85,
            processing_time=result.latency,
        )
    
    async def analyze_architecture(self, code: str, language: str = "python") -> AnalysisReport:
        """架构分析"""
        logger.info(f"Performing architecture analysis for {language}")
        
        result = await self.llm.analyze_architecture(code=code, language=language)
        
        findings = self._extract_findings(result.content)
        recommendations = self._extract_recommendations(result.content)
        
        return AnalysisReport(
            title=f"{language}代码架构分析",
            content=result.content,
            findings=findings,
            recommendations=recommendations,
            quality_score=self._calculate_quality_score(findings, recommendations),
            confidence=0.88,
            processing_time=result.latency,
        )
    
    async def generate_tests(self, code: str, language: str = "python", 
                            test_framework: str = "pytest") -> AnalysisReport:
        """生成测试用例"""
        logger.info(f"Generating test cases for {language} using {test_framework}")
        
        result = await self.llm.generate_tests(
            code=code,
            language=language,
            test_framework=test_framework,
        )
        
        return AnalysisReport(
            title=f"{language}代码测试用例生成",
            content=result.content,
            findings=[],
            recommendations=["运行生成的测试用例验证功能"],
            quality_score=8.5,
            confidence=0.9,
            processing_time=result.latency,
        )
    
    async def suggest_refactoring(self, code: str, language: str = "python") -> AnalysisReport:
        """重构建议"""
        logger.info(f"Generating refactoring suggestions for {language}")
        
        result = await self.llm.suggest_refactoring(code=code, language=language)
        
        findings = self._extract_findings(result.content)
        recommendations = self._extract_recommendations(result.content)
        
        return AnalysisReport(
            title=f"{language}代码重构建议",
            content=result.content,
            findings=findings,
            recommendations=recommendations,
            quality_score=self._calculate_quality_score(findings, recommendations),
            confidence=0.85,
            processing_time=result.latency,
        )
    
    async def explain_code(self, code: str, language: str = "python") -> AnalysisReport:
        """代码解释"""
        logger.info(f"Explaining {language} code")
        
        result = await self.llm.explain_code(code=code, language=language)
        
        return AnalysisReport(
            title=f"{language}代码解释",
            content=result.content,
            findings=[],
            recommendations=[],
            quality_score=9.0,
            confidence=0.95,
            processing_time=result.latency,
        )
    
    async def document_code(self, code: str, language: str = "python",
                           doc_format: str = "docstring") -> AnalysisReport:
        """生成代码文档"""
        logger.info(f"Generating documentation for {language} code in {doc_format} format")
        
        result = await self.llm.document_code(code=code, language=language, doc_format=doc_format)
        
        return AnalysisReport(
            title=f"{language}代码文档生成",
            content=result.content,
            findings=[],
            recommendations=["检查生成的文档是否准确"],
            quality_score=8.5,
            confidence=0.9,
            processing_time=result.latency,
        )
    
    async def compare_alternatives(self, code: str, alternatives: List[str],
                                   language: str = "python") -> AnalysisReport:
        """比较替代方案"""
        logger.info(f"Comparing {len(alternatives)} alternative implementations")
        
        result = await self.llm.compare_alternatives(
            code=code,
            alternatives=alternatives,
            language=language,
        )
        
        findings = self._extract_findings(result.content)
        recommendations = self._extract_recommendations(result.content)
        
        return AnalysisReport(
            title=f"{language}代码替代方案比较",
            content=result.content,
            findings=findings,
            recommendations=recommendations,
            quality_score=8.0,
            confidence=0.85,
            processing_time=result.latency,
        )
    
    async def _generate_project_summary(self, reports: Dict[str, AnalysisReport]) -> AnalysisReport:
        """生成项目总体报告"""
        total_files = len(reports)
        total_findings = sum(len(r.findings) for r in reports.values())
        total_recommendations = sum(len(r.recommendations) for r in reports.values())
        avg_quality = sum(r.quality_score for r in reports.values()) / total_files if total_files > 0 else 0
        
        summary_content = f"""# 项目总体分析报告

## 项目概况
- 分析文件数：{total_files}
- 总发现问题：{total_findings}
- 总建议数：{total_recommendations}
- 平均质量评分：{avg_quality:.2f}/10

## 主要发现
"""
        
        all_findings = []
        for report in reports.values():
            all_findings.extend(report.findings[:3])
        
        summary_content += "\n".join(f"- {f}" for f in all_findings[:10])
        
        summary_content += "\n\n## 主要建议\n"
        
        all_recommendations = []
        for report in reports.values():
            all_recommendations.extend(report.recommendations[:3])
        
        summary_content += "\n".join(f"- {r}" for r in all_recommendations[:10])
        
        return AnalysisReport(
            title="项目总体分析报告",
            content=summary_content,
            findings=all_findings[:10],
            recommendations=all_recommendations[:10],
            quality_score=avg_quality,
            confidence=0.9,
            processing_time=sum(r.processing_time for r in reports.values()),
        )
    
    def _get_language(self, ext: str) -> str:
        """获取语言标识"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
        }
        return language_map.get(ext.lower(), 'unknown')
    
    def _extract_findings(self, content: str) -> List[str]:
        """提取发现"""
        findings = []
        lines = content.split('\n')
        
        in_findings = False
        for line in lines:
            if any(keyword in line.lower() for keyword in ['发现', '问题', '分析', 'issue', 'finding', 'bug', '漏洞']):
                in_findings = True
            elif in_findings and line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '·', '*')):
                findings.append(line.strip())
        
        return findings[:15]
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """提取建议"""
        recommendations = []
        lines = content.split('\n')
        
        in_recommendations = False
        for line in lines:
            if any(keyword in line.lower() for keyword in ['建议', '优化', '改进', 'recommendation', 'suggestion']):
                in_recommendations = True
            elif in_recommendations and line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '·', '*')):
                recommendations.append(line.strip())
        
        return recommendations[:15]
    
    def _calculate_quality_score(self, findings: List[str], recommendations: List[str]) -> float:
        """计算质量评分"""
        score = 10.0
        
        score -= len(findings) * 0.15
        score += len(recommendations) * 0.05
        
        return max(0.0, min(10.0, score))
    
    def get_llm_stats(self) -> Dict[str, Any]:
        """获取LLM统计信息"""
        return self.llm.get_stats()


class EnhancedProjectAnalyzer:
    """LLM驱动的增强项目分析器"""
    
    def __init__(self):
        self.llm = get_llm_manager()
        self.code_analyzer = EnhancedCodeAnalyzer()
        logger.info("EnhancedProjectAnalyzer initialized")
    
    async def analyze_vue_reactivity_system(self, project_path: str) -> AnalysisReport:
        """深度分析Vue响应式系统"""
        logger.info(f"Analyzing Vue reactivity system in: {project_path}")
        
        reactivity_path = Path(project_path) / "packages" / "reactivity" / "src"
        
        if not reactivity_path.exists():
            return AnalysisReport(
                title="Vue响应式系统分析",
                content="Reactivity source not found",
                findings=[],
                recommendations=[],
                quality_score=0.0,
                confidence=0.0,
                processing_time=0.0,
            )
        
        core_files = list(reactivity_path.glob("*.ts"))
        
        analysis_results = []
        for file_path in core_files:
            report = await self.code_analyzer.analyze_file(str(file_path))
            analysis_results.append(report)
        
        comprehensive_content = "# Vue.js 响应式系统深度分析报告\n\n"
        
        for report in analysis_results:
            comprehensive_content += f"\n## {report.title}\n\n"
            comprehensive_content += report.content
            comprehensive_content += "\n---\n"
        
        all_findings = []
        all_recommendations = []
        
        for report in analysis_results:
            all_findings.extend(report.findings)
            all_recommendations.extend(report.recommendations)
        
        return AnalysisReport(
            title="Vue.js 响应式系统深度分析",
            content=comprehensive_content,
            findings=all_findings[:15],
            recommendations=all_recommendations[:15],
            quality_score=sum(r.quality_score for r in analysis_results) / len(analysis_results),
            confidence=0.92,
            processing_time=sum(r.processing_time for r in analysis_results),
        )
    
    async def compare_frameworks(
        self,
        framework1_code: str,
        framework2_code: str,
        framework1_name: str = "Vue.js",
        framework2_name: str = "React",
    ) -> AnalysisReport:
        """比较两个框架"""
        prompt = f"""请比较以下两个前端框架的实现：

## {framework1_name}
```javascript
{framework1_code[:2000]}
```

## {framework2_name}
```javascript
{framework2_code[:2000]}
```

请从以下维度进行比较：
1. 响应式实现方式
2. 性能特点
3. 开发体验
4. 生态系统
5. 适用场景

请用中文回答，提供详细的对比分析。"""
        
        result = await self.llm.complete(
            prompt=prompt,
            system_prompt="你是一个专业的前端架构师和框架比较专家。",
        )
        
        findings = self.code_analyzer._extract_findings(result.content)
        recommendations = self.code_analyzer._extract_recommendations(result.content)
        
        return AnalysisReport(
            title=f"{framework1_name} vs {framework2_name} 对比分析",
            content=result.content,
            findings=findings,
            recommendations=recommendations,
            quality_score=8.5,
            confidence=0.88,
            processing_time=result.latency,
        )
    
    async def analyze_microservices_architecture(self, services: Dict[str, str]) -> AnalysisReport:
        """分析微服务架构"""
        logger.info(f"Analyzing {len(services)} microservices")
        
        services_description = "\n\n".join([
            f"## {name}\n```python\n{code[:1000]}\n```"
            for name, code in services.items()
        ])
        
        prompt = f"""请分析以下微服务架构：

{services_description}

请提供：
1. 服务划分评估
2. 服务间通信分析
3. 架构问题识别
4. 改进建议
5. 部署建议

请用中文回答，保持专业和详细。"""
        
        result = await self.llm.complete(
            prompt=prompt,
            system_prompt="你是一个微服务架构专家。",
        )
        
        findings = self.code_analyzer._extract_findings(result.content)
        recommendations = self.code_analyzer._extract_recommendations(result.content)
        
        return AnalysisReport(
            title="微服务架构分析",
            content=result.content,
            findings=findings,
            recommendations=recommendations,
            quality_score=8.0,
            confidence=0.85,
            processing_time=result.latency,
        )
    
    async def analyze_database_schema(self, schema: str) -> AnalysisReport:
        """分析数据库架构"""
        logger.info("Analyzing database schema")
        
        result = await self.llm.complete(
            prompt=f"""请分析以下数据库架构：

```sql
{schema}
```

请提供：
1. 表结构评估
2. 关系分析
3. 潜在问题
4. 优化建议
5. 索引建议

请用中文回答。""",
            system_prompt="你是一个数据库架构专家。",
        )
        
        findings = self.code_analyzer._extract_findings(result.content)
        recommendations = self.code_analyzer._extract_recommendations(result.content)
        
        return AnalysisReport(
            title="数据库架构分析",
            content=result.content,
            findings=findings,
            recommendations=recommendations,
            quality_score=8.0,
            confidence=0.85,
            processing_time=result.latency,
        )


async def demo_llm_analysis():
    """演示LLM驱动的分析"""
    print("=" * 80)
    print("LLM驱动的增强分析系统演示")
    print("=" * 80)
    
    analyzer = EnhancedCodeAnalyzer()
    
    sample_code = '''
import os
import requests
from functools import wraps

def cache_result(func):
    """简单的缓存装饰器"""
    cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key in cache:
            return cache[key]
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    return wrapper

@cache_result
def fetch_user_data(user_id: int) -> dict:
    """获取用户数据"""
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.results = []
    
    def process(self, data: list) -> list:
        """处理数据"""
        for item in data:
            processed = self._transform(item)
            self.results.append(processed)
        return self.results
    
    def _transform(self, item: dict) -> dict:
        """转换数据"""
        return {k.upper(): v for k, v in item.items()}
'''
    
    print("\n🔍 演示LLM代码分析...")
    
    report = await analyzer.analyze_file_content(
        code=sample_code,
        language="python",
    )
    
    print(f"\n✅ 分析完成！")
    print(f"📊 质量评分: {report.quality_score:.2f}/10")
    print(f"🔍 发现数量: {len(report.findings)}")
    print(f"💡 建议数量: {len(report.recommendations)}")
    print(f"⏱️ 处理时间: {report.processing_time:.2f}秒")
    
    print(f"\n📝 分析内容摘要:")
    print(report.content[:1000])
    
    print("\n\n🔍 演示安全分析...")
    
    security_report = await analyzer.analyze_security(
        code='''
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = execute_query(query)
    return result
''',
        language="python"
    )
    
    print(f"\n⚠️ 安全问题数量: {len(security_report.findings)}")
    print(f"📝 安全分析: {security_report.content[:500]}")
    
    print("\n\n🔍 LLM统计信息:")
    stats = analyzer.get_llm_stats()
    print(f"- 总请求数: {stats['total_requests']}")
    print(f"- 缓存命中率: {stats['cache_hit_rate']:.2%}")
    print(f"- 平均延迟: {stats['avg_latency']:.2f}秒")
    
    print("\n" + "=" * 80)
    print("演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demo_llm_analysis())
