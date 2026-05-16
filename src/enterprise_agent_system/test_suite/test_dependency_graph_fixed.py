"""
Enhanced Dependency Graph Analysis - Fixed Version
修复版依赖图分析 - 正确处理模块名匹配
"""

import ast
import re
import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.path.insert(0, '/workspace/enterprise_agent_system/src')
from enterprise_agent_system.infrastructure.advanced_logging import get_logger

logger = get_logger("dep_graph_fixed")


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
    lines: int = 0


@dataclass
class DependencyGraph:
    """依赖图"""
    nodes: Dict[str, DependencyNode] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    circular_dependencies: List[List[str]] = field(default_factory=list)
    orphan_nodes: List[str] = field(default_factory=list)
    missing_dependencies: List[Tuple[str, str]] = field(default_factory=list)


class EnhancedPythonDependencyAnalyzer:
    """增强Python依赖分析器 - 修复版"""

    BUILTIN_MODULES = {
        'os', 'sys', 'time', 'datetime', 'json', 're', 'math', 'random',
        'collections', 'itertools', 'functools', 'operator', 'types',
        'string', 'logging', 'traceback', 'copy', 'pickle', 'io',
        'pathlib', 'typing', 'abc', 'asyncio', 'concurrent', 'threading',
    }

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.modules: Dict[str, Path] = {}
        self.package_prefix = self._detect_package_prefix()

    def _detect_package_prefix(self) -> str:
        """检测包前缀"""
        parts = self.project_path.parts
        for i, part in enumerate(parts):
            if 'enterprise' in part.lower() or 'agent' in part.lower():
                return '.'.join(parts[i:])
        return ''

    def scan_modules(self) -> Dict[str, Path]:
        """扫描项目模块"""
        self.modules = {}
        package_parts = len(self.package_prefix.split('.')) if self.package_prefix else 0

        for py_file in self.project_path.rglob("*.py"):
            if any(part.startswith('.') or part in (
                '__pycache__', 'venv', '.venv', 'node_modules',
                'build', 'dist', '.git', '.pytest_cache', 'test_', 'tests'
            ) for part in py_file.parts):
                continue

            try:
                relative_path = py_file.relative_to(self.project_path)
            except ValueError:
                continue

            module_parts = relative_path.parts[:-1]
            module_name = relative_path.stem

            if module_name == '__init__':
                full_name = '.'.join(module_parts) if module_parts else '__root__'
            else:
                full_name = '.'.join([*module_parts, module_name]) if module_parts else module_name

            if self.package_prefix:
                full_name = f"{self.package_prefix}.{full_name}"

            full_name = full_name.replace('..', '.').strip('.')

            self.modules[full_name] = py_file

        logger.info(f"Scanned {len(self.modules)} Python modules")
        return self.modules

    def _normalize_import(self, import_name: str, current_module: str) -> Optional[str]:
        """规范化导入名称"""
        import_name = import_name.split('.')[0]

        if import_name in self.BUILTIN_MODULES:
            return None

        current_parts = current_module.split('.')[:-1]

        if import_name.startswith('enterprise_agent_system') or import_name.startswith('enterprise'):
            for module_name in self.modules:
                if module_name.endswith(import_name) or import_name.endswith(module_name.split('.')[-1]):
                    return module_name

        short_name = import_name.split('.')[-1]

        for module_name in self.modules:
            if module_name.split('.')[-1] == short_name:
                return module_name

        return None

    def extract_imports(self, file_path: Path, module_name: str) -> Set[str]:
        """提取导入语句"""
        imports = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            for i, line in enumerate(lines[:100]):
                line = line.strip()
                if line.startswith('from ') and ' import ' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        from_part = parts[1]
                        if not from_part.startswith('_'):
                            target = self._normalize_import(from_part, module_name)
                            if target:
                                imports.add(target)

                elif line.startswith('import '):
                    parts = line[7:].split(',')[0].strip().split()[0]
                    if not parts.startswith('_'):
                        target = self._normalize_import(parts, module_name)
                        if target:
                            imports.add(target)

        except Exception as e:
            logger.debug(f"Error parsing {file_path}: {e}")

        return imports

    def build_dependency_graph(self) -> DependencyGraph:
        """构建依赖图"""
        graph = DependencyGraph()

        for module_name, file_path in self.modules.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                lines = len(content.split('\n'))
            except:
                lines = 0

            node = DependencyNode(
                name=module_name,
                path=str(file_path),
                language='python',
                lines=lines
            )
            graph.nodes[module_name] = node

        for module_name, file_path in self.modules.items():
            imports = self.extract_imports(file_path, module_name)

            for imp in imports:
                if imp in graph.nodes and imp != module_name:
                    graph.nodes[module_name].dependencies.add(imp)
                    graph.nodes[imp].dependents.add(module_name)
                    graph.edges.append((module_name, imp))

        return graph

    def detect_circular_dependencies(self, graph: DependencyGraph) -> List[List[str]]:
        """检测循环依赖 - DFS方法"""
        circular = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.nodes[node].dependencies:
                if neighbor in graph.nodes:
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
            is_external_dep = all(
                dep not in graph.nodes or dep in self.BUILTIN_MODULES
                for dep in node.dependencies
            )
            is_not_used = len(node.dependents) == 0

            if is_external_dep and is_not_used and len(graph.nodes) > 5:
                orphans.append(node_name)
                node.is_orphan = True

        graph.orphan_nodes = orphans
        return orphans

    def detect_missing_dependencies(self, graph: DependencyGraph) -> List[Tuple[str, str]]:
        """检测缺失依赖"""
        missing = []

        for module_name, file_path in self.modules.items():
            imports = self.extract_imports(file_path, module_name)

            for imp in imports:
                if imp not in graph.nodes:
                    missing.append((module_name, imp))

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
                "avg_dependencies": sum(len(n.dependencies) for n in graph.nodes.values()) / len(graph.nodes) if graph.nodes else 0,
                "avg_dependents": sum(len(n.dependents) for n in graph.nodes.values()) / len(graph.nodes) if graph.nodes else 0,
            },
            "circular_dependencies": [
                " -> ".join(cycle) for cycle in graph.circular_dependencies[:10]
            ],
            "orphan_modules": graph.orphan_nodes[:20],
            "missing_dependencies": [
                {"module": m, "missing": dep} for m, dep in graph.missing_dependencies[:20]
            ],
            "modules_by_level": {},
            "module_details": {}
        }

        for level in range(max(levels.values()) + 1 if levels else 1):
            report["modules_by_level"][f"level_{level}"] = [
                name for name, lvl in levels.items() if lvl == level
            ]

        for node_name, node in graph.nodes.items():
            report["module_details"][node_name] = {
                "path": node.path,
                "lines": node.lines,
                "dependencies": list(node.dependencies)[:10],
                "dependents": list(node.dependents)[:10],
                "dependency_count": len(node.dependencies),
                "dependent_count": len(node.dependents),
                "level": node.level,
                "is_circular": node.is_circular,
                "is_orphan": node.is_orphan,
            }

        return report


async def run_fixed_dependency_test():
    """运行修复版依赖图测试"""
    print("\n" + "=" * 80)
    print("修复版依赖图分析测试")
    print("=" * 80)

    project_path = "/workspace/enterprise_agent_system/src/enterprise_agent_system"

    print("\n🔍 正在扫描模块...")
    analyzer = EnhancedPythonDependencyAnalyzer(project_path)
    modules = analyzer.scan_modules()

    print(f"✅ 发现 {len(modules)} 个模块")

    print("\n🔍 正在构建依赖图...")
    start_time = time.time()
    graph = analyzer.build_dependency_graph()
    build_time = time.time() - start_time

    print(f"✅ 依赖图构建完成: {len(graph.nodes)} 节点, {len(graph.edges)} 边")
    print(f"   耗时: {build_time:.2f}秒")

    print("\n🔍 正在检测循环依赖...")
    circular = analyzer.detect_circular_dependencies(graph)
    print(f"✅ 发现 {len(circular)} 个循环依赖")

    print("\n🔍 正在计算依赖层级...")
    levels = analyzer.calculate_levels(graph)
    max_depth = max(levels.values()) if levels else 0
    print(f"✅ 最大依赖深度: {max_depth}")

    print("\n🔍 正在生成报告...")
    report = analyzer.generate_report(graph)

    print("\n" + "=" * 80)
    print("依赖图分析结果")
    print("=" * 80)
    print(f"\n📊 统计信息:")
    print(f"   - 总模块数: {report['summary']['total_modules']}")
    print(f"   - 总边数: {report['summary']['total_edges']}")
    print(f"   - 循环依赖: {report['summary']['circular_deps']}")
    print(f"   - 孤立模块: {report['summary']['orphan_modules']}")
    print(f"   - 缺失依赖: {report['summary']['missing_deps']}")
    print(f"   - 最大深度: {report['summary']['max_depth']}")
    print(f"   - 平均依赖数: {report['summary']['avg_dependencies']:.2f}")
    print(f"   - 平均被依赖数: {report['summary']['avg_dependents']:.2f}")

    if circular:
        print(f"\n⚠️ 循环依赖详情:")
        for i, cycle in enumerate(circular[:5]):
            print(f"   {i+1}. {' -> '.join(cycle[:6])}")

    print(f"\n📁 各层级模块分布:")
    for level, mods in sorted(report['modules_by_level'].items(), key=lambda x: int(x[0].split('_')[1])):
        if mods:
            print(f"   {level}: {len(mods)} 个模块")

    print(f"\n🔝 核心模块 (被依赖最多):")
    top_modules = sorted(
        [(name, details['dependent_count']) for name, details in report['module_details'].items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    for name, count in top_modules:
        if count > 0:
            print(f"   - {name}: 被 {count} 个模块依赖")

    json_str = json.dumps(report, indent=2, ensure_ascii=False)
    print(f"\n📄 JSON报告大小: {len(json_str)} 字节")

    return report


if __name__ == "__main__":
    asyncio.run(run_fixed_dependency_test())
