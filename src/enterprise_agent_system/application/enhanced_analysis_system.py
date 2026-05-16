"""
Enhanced Analysis System with LLM Power
Deep Static Analysis, Security Scanning, and Architecture Review
Application Layer - 深度分析系统
"""

import os
import re
import ast
import asyncio
from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict
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
class Finding:
    """分析发现"""
    severity: str
    category: str
    title: str
    description: str
    location: str
    line_number: int
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    cwe_id: Optional[str] = None
    confidence: float = 0.9


@dataclass
class AnalysisReport:
    """增强分析报告"""
    title: str
    summary: str
    findings: List[Finding]
    metrics: Dict[str, Any]
    llm_insights: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    processing_time: float = 0.0


class StaticCodeAnalyzer:
    """静态代码分析器"""
    
    def __init__(self):
        self.findings: List[Finding] = []
        self.metrics: Dict[str, Any] = {}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            findings = []
            
            if file_path.endswith('.py'):
                findings = self._analyze_python(content, file_path)
            elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                findings = self._analyze_javascript(content, file_path)
            
            return {
                'file_path': file_path,
                'lines': len(content.split('\n')),
                'findings': findings,
                'metrics': self._calculate_metrics(content),
            }
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {'file_path': file_path, 'error': str(e)}
    
    def _analyze_python(self, content: str, file_path: str) -> List[Finding]:
        """Python静态分析"""
        findings = []
        
        try:
            tree = ast.parse(content)
            findings.extend(self._check_security_issues(content, file_path))
            findings.extend(self._check_code_quality(content, file_path))
            findings.extend(self._check_best_practices(content, tree, file_path))
        except SyntaxError:
            findings.append(Finding(
                severity="error",
                category="syntax",
                title="语法错误",
                description="代码无法被Python解析",
                location=file_path,
                line_number=1,
            ))
        
        return findings
    
    def _check_security_issues(self, content: str, file_path: str) -> List[Finding]:
        """安全检查"""
        findings = []
        lines = content.split('\n')
        
        security_patterns = [
            (r'eval\s*\(', "使用eval()函数", "高", "CWE-95"),
            (r'exec\s*\(', "使用exec()函数", "高", "CWE-78"),
            (r'os\.system\s*\(', "使用os.system()", "中", "CWE-78"),
            (r'subprocess\.call.*shell\s*=\s*True', "subprocess调用中启用shell", "中", "CWE-78"),
            (r'pickle\.load', "使用pickle.load()", "中", "CWE-502"),
            (r'yaml\.load.*Loader\s*=\s*yaml\.FullLoader', "使用不安全的yaml.load", "中", "CWE-20"),
            (r'SQL', "可能的SQL注入风险", "高", "CWE-89"),
            (r'password\s*=\s*["\'][^"\']+["\']', "硬编码密码", "高", "CWE-798"),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "硬编码API密钥", "高", "CWE-798"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "硬编码密钥", "中", "CWE-798"),
            (r'os\.popen', "使用os.popen()", "中", "CWE-78"),
            (r'shutil\.rmtree.*onerrors', "shutil.rmtree缺少错误处理", "中", None),
            (r'requests\.get.*verify\s*=\s*False', "SSL验证被禁用", "中", "CWE-295"),
            (r'\.format\(.*request\.', "格式化字符串中使用request数据", "低", None),
            (r'f["\'].*\{.*request', "f-string中使用request数据", "低", None),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc, severity, cwe in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(Finding(
                        severity=severity,
                        category="security",
                        title=desc,
                        description=f"在第{i}行发现: {desc}",
                        location=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        cwe_id=cwe,
                    ))
        
        return findings
    
    def _check_code_quality(self, content: str, file_path: str) -> List[Finding]:
        """代码质量检查"""
        findings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            if len(line_stripped) > 120:
                findings.append(Finding(
                    severity="info",
                    category="quality",
                    title="行过长",
                    description=f"第{i}行超过120个字符",
                    location=file_path,
                    line_number=i,
                    code_snippet=line_stripped[:80] + "...",
                ))
            
            if re.match(r'^[A-Z][A-Z_]+$', line_stripped) and len(line_stripped) > 1:
                findings.append(Finding(
                    severity="info",
                    category="quality",
                    title="常量命名使用全大写",
                    description=f"第{i}行: 常量命名规范",
                    location=file_path,
                    line_number=i,
                ))
            
            if 'TODO' in line or 'FIXME' in line or 'HACK' in line:
                findings.append(Finding(
                    severity="info",
                    category="maintenance",
                    title="存在标记注释",
                    description=f"第{i}行: {line_stripped[:50]}",
                    location=file_path,
                    line_number=i,
                ))
        
        return findings
    
    def _check_best_practices(self, content: str, tree: ast.AST, file_path: str) -> List[Finding]:
        """最佳实践检查"""
        findings = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(ast.unparse(node.args.args)) > 6:
                    findings.append(Finding(
                        severity="info",
                        category="best_practice",
                        title="函数参数过多",
                        description=f"函数 {node.name} 有超过6个参数",
                        location=file_path,
                        line_number=node.lineno or 1,
                    ))
                
                if node.name.startswith('_') and not node.name.startswith('__'):
                    findings.append(Finding(
                        severity="info",
                        category="best_practice",
                        title="私有方法以单下划线开头",
                        description=f"函数 {node.name}",
                        location=file_path,
                        line_number=node.lineno or 1,
                    ))
        
        return findings
    
    def _analyze_javascript(self, content: str, file_path: str) -> List[Finding]:
        """JavaScript静态分析"""
        findings = []
        lines = content.split('\n')
        
        js_patterns = [
            (r'innerHTML\s*=', "使用innerHTML可能导致XSS", "高", "CWE-79"),
            (r'document\.write', "使用document.write可能导致XSS", "高", "CWE-79"),
            (r'eval\s*\(', "使用eval()函数", "高", "CWE-95"),
            (r'var\s+\w+\s*=\s*["\'][^"\']*password[^"\']*["\']', "可能的硬编码密码", "高", "CWE-798"),
            (r'console\.log.*\(.*\)', "生产代码中的console.log", "info", None),
            (r'await.*fetch\(.*credentials', "fetch请求可能泄露凭证", "中", "CWE-200"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc, severity, cwe in js_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(Finding(
                        severity=severity,
                        category="security",
                        title=desc,
                        description=f"在第{i}行发现: {desc}",
                        location=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        cwe_id=cwe,
                    ))
        
        return findings
    
    def _calculate_metrics(self, content: str) -> Dict[str, Any]:
        """计算代码度量"""
        lines = content.split('\n')
        
        return {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'comment_lines': len([l for l in lines if l.strip().startswith('#')]),
            'blank_lines': len([l for l in lines if not l.strip()]),
            'avg_line_length': sum(len(l) for l in lines) / len(lines) if lines else 0,
        }


class EnhancedAnalyzer:
    """增强分析器 - 结合静态分析和LLM"""
    
    def __init__(self):
        self.llm = get_llm_manager()
        self.static_analyzer = StaticCodeAnalyzer()
        logger.info("Enhanced Analyzer initialized with LLM + Static Analysis")
    
    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        options: Optional[AnalysisOptions] = None,
    ) -> AnalysisReport:
        """综合代码分析"""
        options = options or AnalysisOptions()
        
        import time
        start_time = time.time()
        
        static_results = self._static_analyze_code(code, language)
        
        llm_result = await self.llm.analyze_code(
            code=code,
            language=language,
            options=options,
        )
        
        findings = static_results['findings']
        
        recommendations = self._extract_recommendations(llm_result.content)
        
        quality_score = self._calculate_quality_score(findings, recommendations)
        
        processing_time = time.time() - start_time
        
        return AnalysisReport(
            title=f"{language.upper()}代码综合分析报告",
            summary=llm_result.content[:500] + "..." if len(llm_result.content) > 500 else llm_result.content,
            findings=findings,
            metrics=static_results['metrics'],
            llm_insights=llm_result.content,
            recommendations=recommendations,
            quality_score=quality_score,
            processing_time=processing_time,
        )
    
    async def analyze_file_full(
        self,
        file_path: str,
        options: Optional[AnalysisOptions] = None,
    ) -> AnalysisReport:
        """完整文件分析"""
        options = options or AnalysisOptions()
        
        import time
        start_time = time.time()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            file_analysis = self.static_analyzer.analyze_file(file_path)
            
            language = self._detect_language(file_path)
            
            llm_result = await self.llm.analyze_code(
                code=code,
                language=language,
                options=options,
            )
            
            all_findings = file_analysis.get('findings', [])
            
            recommendations = self._extract_recommendations(llm_result.content)
            recommendations.extend(self._extract_findings_from_llm(llm_result.content))
            
            quality_score = self._calculate_quality_score(all_findings, recommendations)
            
            processing_time = time.time() - start_time
            
            return AnalysisReport(
                title=f"文件分析报告: {Path(file_path).name}",
                summary=llm_result.content[:500] + "..." if len(llm_result.content) > 500 else llm_result.content,
                findings=all_findings,
                metrics={**file_analysis.get('metrics', {}), 'file_path': file_path},
                llm_insights=llm_result.content,
                recommendations=recommendations,
                quality_score=quality_score,
                processing_time=processing_time,
            )
            
        except Exception as e:
            logger.error(f"Error in full file analysis: {e}")
            return AnalysisReport(
                title=f"分析失败: {file_path}",
                summary=str(e),
                findings=[],
                metrics={},
                recommendations=["检查文件是否存在和可读"],
                quality_score=0.0,
                processing_time=time.time() - start_time,
            )
    
    async def analyze_project_full(
        self,
        project_path: str,
        options: Optional[AnalysisOptions] = None,
    ) -> Dict[str, AnalysisReport]:
        """完整项目分析"""
        options = options or AnalysisOptions()
        
        logger.info(f"Starting full project analysis: {project_path}")
        
        project_reports = {}
        project_dir = Path(project_path)
        
        code_files = []
        for pattern in ['**/*.py', '**/*.js', '**/*.ts', '**/*.tsx']:
            code_files.extend(project_dir.glob(pattern))
        
        code_files = [f for f in code_files if not any(
            part.startswith('.') or part in ['node_modules', '__pycache__', 'venv', '.venv']
            for part in f.parts
        )]
        
        code_files = code_files[:50]
        
        for file_path in code_files:
            try:
                report = await self.analyze_file_full(str(file_path), options)
                project_reports[str(file_path)] = report
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
        
        project_summary = await self._generate_project_summary(project_reports)
        
        project_reports['_summary'] = project_summary
        
        return project_reports
    
    async def analyze_security_deep(
        self,
        code: str,
        language: str = "python",
    ) -> AnalysisReport:
        """深度安全分析"""
        import time
        start_time = time.time()
        
        static_findings = self._static_analyze_code(code, language)['findings']
        
        llm_result = await self.llm.analyze_security(code=code, language=language)
        
        security_findings = [f for f in static_findings if f.category == 'security']
        
        recommendations = self._extract_recommendations(llm_result.content)
        
        return AnalysisReport(
            title=f"{language.upper()}代码安全分析报告",
            summary=llm_result.content,
            findings=security_findings,
            metrics={'total_issues': len(security_findings)},
            llm_insights=llm_result.content,
            recommendations=recommendations,
            quality_score=max(0, 10 - len(security_findings)),
            processing_time=time.time() - start_time,
        )
    
    async def analyze_performance_deep(
        self,
        code: str,
        language: str = "python",
    ) -> AnalysisReport:
        """深度性能分析"""
        import time
        start_time = time.time()
        
        static_findings = self._static_analyze_code(code, language)['findings']
        
        llm_result = await self.llm.analyze_performance(code=code, language=language)
        
        recommendations = self._extract_recommendations(llm_result.content)
        
        return AnalysisReport(
            title=f"{language.upper()}代码性能分析报告",
            summary=llm_result.content,
            findings=[],
            metrics={},
            llm_insights=llm_result.content,
            recommendations=recommendations,
            quality_score=8.0,
            processing_time=time.time() - start_time,
        )
    
    async def analyze_architecture_deep(
        self,
        code: str,
        language: str = "python",
    ) -> AnalysisReport:
        """深度架构分析"""
        import time
        start_time = time.time()
        
        llm_result = await self.llm.analyze_architecture(code=code, language=language)
        
        recommendations = self._extract_recommendations(llm_result.content)
        
        return AnalysisReport(
            title=f"{language.upper()}代码架构分析报告",
            summary=llm_result.content,
            findings=[],
            metrics={},
            llm_insights=llm_result.content,
            recommendations=recommendations,
            quality_score=8.0,
            processing_time=time.time() - start_time,
        )
    
    async def generate_test_suite(
        self,
        code: str,
        language: str = "python",
        test_framework: str = "pytest",
    ) -> AnalysisReport:
        """生成测试套件"""
        import time
        start_time = time.time()
        
        llm_result = await self.llm.generate_tests(
            code=code,
            language=language,
            test_framework=test_framework,
        )
        
        return AnalysisReport(
            title=f"{language.upper()}代码测试套件",
            summary=llm_result.content,
            findings=[],
            metrics={},
            llm_insights=llm_result.content,
            recommendations=["运行生成的测试用例验证功能"],
            quality_score=8.5,
            processing_time=time.time() - start_time,
        )
    
    async def refactor_code(
        self,
        code: str,
        language: str = "python",
    ) -> AnalysisReport:
        """代码重构建议"""
        import time
        start_time = time.time()
        
        llm_result = await self.llm.suggest_refactoring(code=code, language=language)
        
        recommendations = self._extract_recommendations(llm_result.content)
        
        return AnalysisReport(
            title=f"{language.upper()}代码重构建议",
            summary=llm_result.content,
            findings=[],
            metrics={},
            llm_insights=llm_result.content,
            recommendations=recommendations,
            quality_score=8.0,
            processing_time=time.time() - start_time,
        )
    
    def _static_analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """静态分析代码"""
        analyzer = StaticCodeAnalyzer()
        
        temp_file = f"/tmp/temp_analysis.{'py' if language == 'python' else 'js'}"
        with open(temp_file, 'w') as f:
            f.write(code)
        
        result = analyzer.analyze_file(temp_file)
        
        os.remove(temp_file)
        
        return {
            'findings': result.get('findings', []),
            'metrics': result.get('metrics', {}),
        }
    
    def _detect_language(self, file_path: str) -> str:
        """检测语言"""
        ext = Path(file_path).suffix.lower()
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
        return language_map.get(ext, 'unknown')
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """提取建议"""
        recommendations = []
        lines = content.split('\n')
        
        in_section = False
        for line in lines:
            if '建议' in line or '优化' in line or '改进' in line or 'recommendation' in line.lower():
                in_section = True
            elif in_section and line.strip().startswith(('1.', '2.', '3.', '-', '•', '*', '+')):
                recommendations.append(line.strip())
        
        return recommendations[:10]
    
    def _extract_findings_from_llm(self, content: str) -> List[str]:
        """从LLM输出中提取发现"""
        findings = []
        lines = content.split('\n')
        
        in_section = False
        for line in lines:
            if '问题' in line or '发现' in line or 'issue' in line.lower() or 'finding' in line.lower():
                in_section = True
            elif in_section and line.strip().startswith(('1.', '2.', '3.', '-', '•', '*', '+')):
                findings.append(line.strip())
        
        return findings[:5]
    
    def _calculate_quality_score(self, findings: List[Finding], recommendations: List[str]) -> float:
        """计算质量评分"""
        score = 10.0
        
        for finding in findings:
            if finding.severity == "高":
                score -= 1.0
            elif finding.severity == "中":
                score -= 0.5
            elif finding.severity == "info":
                score -= 0.1
        
        score += len(recommendations) * 0.1
        
        return max(0.0, min(10.0, score))
    
    async def _generate_project_summary(self, reports: Dict[str, AnalysisReport]) -> AnalysisReport:
        """生成项目总结"""
        total_files = len([r for k, r in reports.items() if k != '_summary'])
        
        all_findings = []
        all_recommendations = []
        
        for report in reports.values():
            if isinstance(report, AnalysisReport):
                all_findings.extend(report.findings)
                all_recommendations.extend(report.recommendations)
        
        avg_quality = sum(r.quality_score for r in reports.values() if isinstance(r, AnalysisReport)) / total_files if total_files > 0 else 0
        
        severity_counts = defaultdict(int)
        for finding in all_findings:
            severity_counts[finding.severity] += 1
        
        summary_content = f"""# 项目综合分析报告

## 统计概览
- 分析文件数: {total_files}
- 总发现数: {len(all_findings)}
- 高严重性问题: {severity_counts.get('高', 0)}
- 中严重性问题: {severity_counts.get('中', 0)}
- 平均质量评分: {avg_quality:.2f}/10

## 主要发现
"""
        for finding in all_findings[:10]:
            summary_content += f"- [{finding.severity}] {finding.title}: {finding.description}\n"
        
        summary_content += "\n## 主要建议\n"
        for rec in all_recommendations[:10]:
            summary_content += f"- {rec}\n"
        
        return AnalysisReport(
            title="项目综合分析报告",
            summary=summary_content,
            findings=all_findings,
            metrics={
                'total_files': total_files,
                'total_findings': len(all_findings),
                'avg_quality': avg_quality,
                'severity_counts': dict(severity_counts),
            },
            recommendations=all_recommendations[:10],
            quality_score=avg_quality,
            processing_time=0.0,
        )


async def demo_enhanced_analysis():
    """演示增强分析"""
    print("=" * 80)
    print("增强分析系统演示 - LLM + 静态分析")
    print("=" * 80)
    
    analyzer = EnhancedAnalyzer()
    
    sample_code = '''
import os
import pickle
import requests

def process_user_data(user_id):
    """处理用户数据"""
    password = "hardcoded_password123"
    data = requests.get(f"https://api.example.com/users/{user_id}", verify=False)
    result = pickle.loads(data.content)
    return result

def execute_command(cmd):
    """执行命令"""
    eval(cmd)
    
def save_file(path, content):
    """保存文件"""
    os.system(f"echo {content} > {path}")
'''
    
    print("\n🔍 正在执行综合代码分析...")
    
    report = await analyzer.analyze_code(
        code=sample_code,
        language="python",
        options=AnalysisOptions(
            depth=AnalysisDepth.DEEP,
            include_security=True,
            include_performance=True,
        )
    )
    
    print(f"\n✅ 分析完成！")
    print(f"📊 质量评分: {report.quality_score:.2f}/10")
    print(f"🔍 发现数量: {len(report.findings)}")
    print(f"⏱️ 处理时间: {report.processing_time:.2f}秒")
    
    print(f"\n⚠️ 发现的问题:")
    for finding in report.findings:
        print(f"  [{finding.severity}] {finding.title} (行{finding.line_number})")
    
    print(f"\n📝 LLM分析摘要:")
    print(report.llm_insights[:800] if report.llm_insights else "无")
    
    print("\n" + "=" * 80)
    print("演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demo_enhanced_analysis())
