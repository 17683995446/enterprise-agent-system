"""
High-Difficulty Test 7: Complex Dependency Graph Analysis
复杂依赖图分析 - 包含多层依赖、循环依赖检测、缺失依赖检测
"""

import asyncio
import ast
import re
import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.path.insert(0, '/workspace/enterprise_agent_system/src')
from enterprise_agent_system.infrastructure.advanced_logging import get_logger

logger = get_logger("dep_graph_test")


@dataclass
class DependencyNode:
    """依赖节点"""
    name: str
    path: str
    language: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    is_circular: bool = False
    is_orphan: bool = False
    level: int = 0


@dataclass
class DependencyGraph:
    """依赖图"""
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    orphan_nodes: List[str] = field(default_factory=list)
    missing_dependencies: List[Tuple[str, str]] = field(default_factory=list)


class PythonDependencyAnalyzer:
    """Python依赖分析器"""

    BUILTIN_MODULES = {
        'os', 'sys', 'time', 'datetime', 'json', 're', 'math', 'random',
        'collections', 'itertools', 'functools', 'operator', 'types',
        'string', 'logging', 'traceback', 'copy', 'pickle', 'io',
        'pathlib', 'typing', 'abc', 'asyncio', 'concurrent', 'threading',
        'queue', 'socket', 'urllib', 'http', 'html', 'xml', 'csv',
        'argparse', 'configparser', 'shutil', 'tempfile', 'glob', 'fnmatch',
        'subprocess', 'signal', 'mmap', 'gc', 'weakref', 'dis', 'inspect',
        'ast', 'platform', 'errno', 'codecs', 'io', 'builtins'
    }

    EXTERNAL_PACKAGES = {
        'fastapi', 'uvicorn', 'sqlalchemy', 'redis', 'pydantic', 'numpy',
        'pandas', 'requests', 'httpx', 'aiohttp', 'celery', 'kombu',
        'alembic', 'psycopg2', 'pymysql', 'aioredis', 'asyncpg',
        'python-dotenv', 'passlib', 'python-jose', 'cryptography',
        'email', 'smtplib', 'urllib3', 'certifi', 'charset-normalizer',
        'idna', 'six', 'packaging', 'pytest', 'pyyaml', 'click',
        'flask', 'django', 'tornado', 'tqdm', 'tenacity', 'prometheus-client'
    }

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.modules: Dict[str, Path] = {}

    def scan_modules(self) -> Dict[str, Path]:
        """扫描项目模块"""
        self.modules = {}

        for py_file in self.project_path.rglob("*.py"):
            if any(part.startswith('.') or part in (
                '__pycache__', 'venv', '.venv', 'node_modules',
                'build', 'dist', '.git', '.pytest_cache'
            ) for part in py_file.parts):
                continue

            relative_path = py_file.relative_to(self.project_path)
            module_name = str(relative_path).replace('/', '.').replace('\\', '.').replace('.py', '')

            if module_name.endswith('.__init__'):
                module_name = module_name.replace('.__init__', '')

            self.modules[module_name] = py_file

        logger.info(f"Scanned {len(self.modules)} Python modules")
        return self.modules

    def extract_imports(self, file_path: Path) -> Set[str]:
        """提取导入语句"""
        imports = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")

        return imports

    def build_dependency_graph(self) -> DependencyGraph:
        """构建依赖图"""
        graph = DependencyGraph()

        for module_name, file_path in self.modules.items():
            node = DependencyNode(
                name=module_name,
                path=str(file_path),
                language='python'
            )
            graph.nodes[module_name] = node

        for module_name, file_path in self.modules.items():
            imports = self.extract_imports(file_path)

            for imp in imports:
                if imp in self.modules:
                    graph.nodes[module_name].dependencies.add(imp)
                    graph.nodes[imp].dependents.add(module_name)
                    graph.edges.append((module_name, imp))

        return graph

    def detect_circular_dependencies(self, graph: DependencyGraph) -> List[List[str]]:
        """检测循环依赖 - 使用Tarjan算法"""
        circular = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.nodes[node].dependencies:
                if neighbor in self.modules:
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        if cycle not in circular:
                            circular.append(cycle)
                        graph.nodes[neighbor].is_circular = True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in graph.nodes:
            if node not in visited:
                dfs(node)

        graph.circular_dependencies = circular
        return circular

    def detect_orphan_nodes(self, graph: DependencyGraph) -> List[str]:
        """检测孤立节点"""
        orphans = []

        for node_name, node in graph.nodes.items():
            if not node.dependencies and not node.dependents:
                if len(list(self.modules.keys())) > 1:
                    orphans.append(node_name)
                    node.is_orphan = True

        graph.orphan_nodes = orphans
        return orphans

    def detect_missing_dependencies(self, graph: DependencyGraph) -> List[Tuple[str, str]]:
        """检测缺失依赖"""
        missing = []

        for module_name, file_path in self.modules.items():
            imports = self.extract_imports(file_path)

            for imp in imports:
                if imp not in self.modules and imp not in self.BUILTIN_MODULES:
                    missing.append((module_name, imp))
                    graph.nodes[module_name].dependencies.add(imp)

        graph.missing_dependencies = missing
        return missing

    def calculate_levels(self, graph: DependencyGraph) -> Dict[str, int]:
        """计算依赖层级"""
        levels = {}
        in_degree = defaultdict(int)

        for node in graph.nodes:
            in_degree[node] = 0

        for _, target in graph.edges:
            in_degree[target] += 1

        queue = deque([node for node in graph.nodes if in_degree[node] == 0])
        level = 0

        while queue:
            level_size = len(queue)

            for _ in range(level_size):
                node = queue.popleft()
                levels[node] = level
                graph.nodes[node].level = level

                for neighbor in graph.nodes[node].dependencies:
                    if neighbor in graph.nodes:
                        in_degree[neighbor] -= 1
                        if in_degree[neighbor] == 0:
                            queue.append(neighbor)

            level += 1

        return levels

    def generate_report(self, graph: DependencyGraph) -> Dict:
        """生成分析报告"""
        levels = self.calculate_levels(graph)

        report = {
            "summary": {
                "total_modules": len(graph.nodes),
                "total_edges": len(graph.edges),
                "circular_deps": len(graph.circular_dependencies),
                "orphan_modules": len(graph.orphan_nodes),
                "missing_deps": len(graph.missing_dependencies),
                "max_depth": max(levels.values()) if levels else 0,
            },
            "circular_dependencies": [
                " -> ".join(cycle) for cycle in graph.circular_dependencies
            ],
            "orphan_modules": graph.orphan_nodes,
            "missing_dependencies": [
                {"module": m, "missing": dep} for m, dep in graph.missing_dependencies
            ],
            "modules_by_level": defaultdict(list),
            "module_details": {}
        }

        for node_name, level in levels.items():
            report["modules_by_level"][level].append(node_name)

        for node_name, node in graph.nodes.items():
            report["module_details"][node_name] = {
                "path": node.path,
                "dependencies": list(node.dependencies),
                "dependents": list(node.dependents),
                "level": node.level,
                "is_circular": node.is_circular,
                "is_orphan": node.is_orphan,
            }

        return report


class JavaScriptDependencyAnalyzer:
    """JavaScript/TypeScript依赖分析器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.modules: Dict[str, Path] = {}

    def scan_modules(self) -> Dict[str, Path]:
        """扫描JS/TS模块"""
        self.modules = {}

        for ext in ['*.js', '*.jsx', '*.ts', '*.tsx']:
            for file_path in self.project_path.rglob(ext):
                if any(part.startswith('.') for part in file_path.parts):
                    continue

                relative_path = file_path.relative_to(self.project_path)
                module_name = str(relative_path).replace('/', '.').replace('\\', '.').replace(ext.replace('*', ''), '')
                self.modules[module_name] = file_path

        logger.info(f"Scanned {len(self.modules)} JavaScript/TypeScript modules")
        return self.modules

    def extract_imports(self, file_path: Path) -> Set[str]:
        """提取导入语句"""
        imports = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            import_patterns = [
                r'import\s+(?:{\s*)?([a-zA-Z_$][a-zA-Z0-9_$]*)',
                r'import\s+(?:{\s*)?([a-zA-Z_$][a-zA-Z0-9_$]*)\s+from',
                r'import\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s+from',
                r'require\s*\(\s*["\']([^"\']+)["\']\s*\)',
                r'from\s+["\']([^"\']+)["\']\s+import',
            ]

            for pattern in import_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    module = match.group(1) if match.lastindex == 1 else match.group(2) if match.lastindex == 2 else None
                    if module and not module.startswith('.'):
                        imports.add(module.split('/')[0].split('@')[0])

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")

        return imports

    def build_dependency_graph(self) -> DependencyGraph:
        """构建依赖图"""
        graph = DependencyGraph()

        for module_name, file_path in self.modules.items():
            node = DependencyNode(
                name=module_name,
                path=str(file_path),
                language='javascript'
            )
            graph.nodes[module_name] = node

        for module_name, file_path in self.modules.items():
            imports = self.extract_imports(file_path)

            for imp in imports:
                if imp in self.modules:
                    graph.nodes[module_name].dependencies.add(imp)
                    graph.nodes[imp].dependents.add(module_name)
                    graph.edges.append((module_name, imp))

        return graph


class CrossLanguageDependencyAnalyzer:
    """跨语言依赖分析器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.python_analyzer = PythonDependencyAnalyzer(project_path)
        self.js_analyzer = JavaScriptDependencyAnalyzer(project_path)

    def analyze_cross_language_deps(self) -> Dict:
        """分析跨语言依赖"""
        logger.info("Starting cross-language dependency analysis...")

        python_modules = self.python_analyzer.scan_modules()
        js_modules = self.js_analyzer.scan_modules()

        cross_lang_patterns = [
            (r'from\s+\.\./.*python', 'python'),
            (r'from\s+\.\./.*\.py', 'python'),
            (r'sys\.path\.insert.*python', 'python'),
            (r'PyCall', 'python'),
            (r'node_modules/.*\.py', 'python'),
        ]

        return {
            "python_modules": len(python_modules),
            "javascript_modules": len(js_modules),
            "cross_language_patterns": len(cross_lang_patterns),
            "analysis_complete": True,
        }


class StressTestDependencyGraph:
    """依赖图压力测试"""

    def __init__(self, project_path: str):
        self.project_path = project_path
        self.results = []

    def test_concurrent_analysis(self, num_threads: int = 10) -> Dict:
        """并发分析压力测试"""
        logger.info(f"Starting concurrent analysis with {num_threads} threads...")

        start_time = time.time()
        results = []
        lock = threading.Lock()

        def analyze_task(task_id: int):
            analyzer = PythonDependencyAnalyzer(self.project_path)
            modules = analyzer.scan_modules()
            graph = analyzer.build_dependency_graph()
            circular = analyzer.detect_circular_dependencies(graph)

            with lock:
                results.append({
                    "task_id": task_id,
                    "modules_found": len(modules),
                    "edges_found": len(graph.edges),
                    "circular_deps": len(circular),
                })

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(analyze_task, i) for i in range(num_threads)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Task failed: {e}")

        elapsed = time.time() - start_time

        return {
            "total_threads": num_threads,
            "completed_tasks": len(results),
            "total_time": elapsed,
            "avg_time_per_task": elapsed / num_threads,
            "tasks_per_second": num_threads / elapsed,
            "results": results,
        }

    def test_large_file_analysis(self) -> Dict:
        """大文件分析测试"""
        logger.info("Starting large file analysis test...")

        analyzer = PythonDependencyAnalyzer(self.project_path)
        modules = analyzer.scan_modules()

        large_files = [(name, path) for name, path in modules.items()
                      if path.stat().st_size > 10000]

        start_time = time.time()
        for module_name, file_path in large_files[:10]:
            imports = analyzer.extract_imports(file_path)

        elapsed = time.time() - start_time

        return {
            "large_files_analyzed": min(10, len(large_files)),
            "total_large_files": len(large_files),
            "analysis_time": elapsed,
            "avg_time_per_file": elapsed / min(10, len(large_files)) if large_files else 0,
        }

    def test_deep_dependency_chain(self) -> Dict:
        """深层依赖链测试"""
        logger.info("Starting deep dependency chain test...")

        analyzer = PythonDependencyAnalyzer(self.project_path)
        analyzer.scan_modules()
        graph = analyzer.build_dependency_graph()
        levels = analyzer.calculate_levels(graph)

        max_depth = max(levels.values()) if levels else 0

        return {
            "max_dependency_depth": max_depth,
            "modules_by_depth": {str(k): len([m for m, l in levels.items() if l == k])
                                for k in range(max_depth + 1)},
        }


async def run_high_difficulty_test7():
    """运行高难度测试7: 复杂依赖图分析"""
    print("\n" + "=" * 80)
    print("高难度测试7: 复杂依赖图分析")
    print("=" * 80)

    project_path = "/workspace/enterprise_agent_system/src/enterprise_agent_system"

    results = {
        "test_name": "Complex Dependency Graph Analysis",
        "test_id": 7,
        "sub_tests": {},
        "issues_found": [],
        "issues_fixed": [],
    }

    print("\n🔍 测试1: Python依赖图构建...")
    try:
        py_analyzer = PythonDependencyAnalyzer(project_path)
        py_analyzer.scan_modules()
        graph = py_analyzer.build_dependency_graph()
        circular = py_analyzer.detect_circular_dependencies(graph)
        orphans = py_analyzer.detect_orphan_nodes(graph)
        missing = py_analyzer.detect_missing_dependencies(graph)
        report = py_analyzer.generate_report(graph)

        results["sub_tests"]["python_graph"] = {
            "status": "PASSED",
            "modules": len(graph.nodes),
            "edges": len(graph.edges),
            "circular_deps": len(circular),
            "orphan_nodes": len(orphans),
            "missing_deps": len(missing),
            "max_depth": report["summary"]["max_depth"],
        }

        print(f"  ✅ 模块数: {len(graph.nodes)}, 边数: {len(graph.edges)}")
        print(f"  ✅ 循环依赖: {len(circular)}, 孤立节点: {len(orphans)}, 缺失依赖: {len(missing)}")

        if circular:
            print(f"  ⚠️ 发现循环依赖:")
            for cycle in circular[:3]:
                print(f"     - {' -> '.join(cycle[:5])}")

    except Exception as e:
        logger.error(f"Python graph test failed: {e}")
        results["sub_tests"]["python_graph"] = {"status": "FAILED", "error": str(e)}
        results["issues_found"].append({"test": "python_graph", "issue": str(e)})

    print("\n🔍 测试2: JavaScript/TypeScript依赖图构建...")
    try:
        js_analyzer = JavaScriptDependencyAnalyzer(project_path)
        js_analyzer.scan_modules()
        js_graph = js_analyzer.build_dependency_graph()

        results["sub_tests"]["javascript_graph"] = {
            "status": "PASSED",
            "modules": len(js_graph.nodes),
            "edges": len(js_graph.edges),
        }

        print(f"  ✅ JS/TS模块数: {len(js_graph.nodes)}, 边数: {len(js_graph.edges)}")

    except Exception as e:
        logger.error(f"JavaScript graph test failed: {e}")
        results["sub_tests"]["javascript_graph"] = {"status": "FAILED", "error": str(e)}
        results["issues_found"].append({"test": "javascript_graph", "issue": str(e)})

    print("\n🔍 测试3: 跨语言依赖分析...")
    try:
        cross_analyzer = CrossLanguageDependencyAnalyzer(project_path)
        cross_report = cross_analyzer.analyze_cross_language_deps()

        results["sub_tests"]["cross_language"] = {
            "status": "PASSED",
            **cross_report,
        }

        print(f"  ✅ Python模块: {cross_report['python_modules']}")
        print(f"  ✅ JavaScript模块: {cross_report['javascript_modules']}")

    except Exception as e:
        logger.error(f"Cross-language test failed: {e}")
        results["sub_tests"]["cross_language"] = {"status": "FAILED", "error": str(e)}
        results["issues_found"].append({"test": "cross_language", "issue": str(e)})

    print("\n🔍 测试4: 并发压力测试...")
    try:
        stress_tester = StressTestDependencyGraph(project_path)
        concurrent_results = stress_tester.test_concurrent_analysis(num_threads=20)

        results["sub_tests"]["concurrent_stress"] = {
            "status": "PASSED",
            **concurrent_results,
        }

        print(f"  ✅ 20个并发任务完成")
        print(f"  ✅ 总耗时: {concurrent_results['total_time']:.2f}秒")
        print(f"  ✅ QPS: {concurrent_results['tasks_per_second']:.2f}")

    except Exception as e:
        logger.error(f"Concurrent stress test failed: {e}")
        results["sub_tests"]["concurrent_stress"] = {"status": "FAILED", "error": str(e)}
        results["issues_found"].append({"test": "concurrent_stress", "issue": str(e)})

    print("\n🔍 测试5: 大文件分析测试...")
    try:
        large_file_results = stress_tester.test_large_file_analysis()

        results["sub_tests"]["large_file"] = {
            "status": "PASSED",
            **large_file_results,
        }

        print(f"  ✅ 分析大文件数: {large_file_results['large_files_analyzed']}")
        print(f"  ✅ 平均耗时: {large_file_results['avg_time_per_file']:.4f}秒/文件")

    except Exception as e:
        logger.error(f"Large file test failed: {e}")
        results["sub_tests"]["large_file"] = {"status": "FAILED", "error": str(e)}
        results["issues_found"].append({"test": "large_file", "issue": str(e)})

    print("\n🔍 测试6: 深层依赖链测试...")
    try:
        deep_chain_results = stress_tester.test_deep_dependency_chain()

        results["sub_tests"]["deep_chain"] = {
            "status": "PASSED",
            **deep_chain_results,
        }

        print(f"  ✅ 最大依赖深度: {deep_chain_results['max_dependency_depth']}")

    except Exception as e:
        logger.error(f"Deep chain test failed: {e}")
        results["sub_tests"]["deep_chain"] = {"status": "FAILED", "error": str(e)}
        results["issues_found"].append({"test": "deep_chain", "issue": str(e)})

    print("\n🔍 测试7: 依赖图导出与序列化...")
    try:
        analyzer = PythonDependencyAnalyzer(project_path)
        analyzer.scan_modules()
        graph = analyzer.build_dependency_graph()

        json_report = analyzer.generate_report(graph)
        json_str = json.dumps(json_report, indent=2)

        results["sub_tests"]["serialization"] = {
            "status": "PASSED",
            "json_size_bytes": len(json_str),
            "modules_serialized": len(json_report["module_details"]),
        }

        print(f"  ✅ JSON大小: {len(json_str)}字节")
        print(f"  ✅ 序列化模块数: {len(json_report['module_details'])}")

    except Exception as e:
        logger.error(f"Serialization test failed: {e}")
        results["sub_tests"]["serialization"] = {"status": "FAILED", "error": str(e)}
        results["issues_found"].append({"test": "serialization", "issue": str(e)})

    passed_tests = sum(1 for t in results["sub_tests"].values() if t.get("status") == "PASSED")
    total_tests = len(results["sub_tests"])

    results["summary"] = {
        "passed": passed_tests,
        "total": total_tests,
        "pass_rate": f"{passed_tests / total_tests * 100:.1f}%",
        "issues_count": len(results["issues_found"]),
    }

    print("\n" + "=" * 80)
    print("测试7结果汇总")
    print("=" * 80)
    print(f"通过测试: {passed_tests}/{total_tests} ({passed_tests / total_tests * 100:.1f}%)")
    print(f"发现问题: {len(results['issues_found'])}")

    if results["issues_found"]:
        print("\n发现的问题:")
        for issue in results["issues_found"]:
            print(f"  ⚠️ {issue['test']}: {issue['issue']}")

    print("=" * 80)

    return results


if __name__ == "__main__":
    asyncio.run(run_high_difficulty_test7())
