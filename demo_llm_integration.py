#!/usr/bin/env python
"""
LLM Integration Demo
Demonstrates the enhanced LLM-powered analysis capabilities
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from enterprise_agent_system.infrastructure.llm_integration import (
    get_llm_manager,
    AdvancedLLMManager,
    AnalysisOptions,
    AnalysisDepth,
)
from enterprise_agent_system.application.enhanced_analysis_system import EnhancedAnalyzer


async def demo_basic_llm():
    """演示基本LLM功能"""
    print("=" * 80)
    print("1. 基本LLM对话演示")
    print("=" * 80)
    
    llm = get_llm_manager()
    
    print("\n📤 发送测试请求到硅基流动...")
    
    result = await llm.complete(
        prompt="请用50字介绍企业级Agent系统的优势",
        system_prompt="你是一个AI助手，请简洁、专业地回答。"
    )
    
    print(f"\n✅ 响应内容:\n{result.content}")
    print(f"⏱️ 延迟: {result.latency:.2f}秒")
    print(f"📊 Token使用: {result.usage}")
    
    stats = llm.get_stats()
    print(f"\n📈 统计信息:")
    print(f"  - 总请求数: {stats['total_requests']}")
    print(f"  - 缓存命中率: {stats['cache_hit_rate']:.2%}")
    print(f"  - 平均延迟: {stats['avg_latency']:.2f}秒")
    
    print()


async def demo_code_analysis():
    """演示代码分析"""
    print("=" * 80)
    print("2. LLM代码分析演示")
    print("=" * 80)
    
    llm = get_llm_manager()
    
    code = '''
def calculate_factorial(n):
    """计算阶乘"""
    if n < 0:
        raise ValueError("负数没有阶乘")
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

def fetch_user_data(user_id):
    """获取用户数据"""
    import requests
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()
'''
    
    print("\n📤 分析Python代码...")
    
    options = AnalysisOptions(
        depth=AnalysisDepth.DEEP,
        include_security=True,
        include_performance=True,
        include_best_practices=True,
    )
    
    result = await llm.analyze_code(
        code=code,
        language="python",
        options=options,
    )
    
    print(f"\n✅ 分析完成!")
    print(f"⏱️ 延迟: {result.latency:.2f}秒")
    print(f"\n📝 分析结果:\n{result.content[:1000]}...")
    
    print()


async def demo_security_analysis():
    """演示安全分析"""
    print("=" * 80)
    print("3. 专门安全分析演示")
    print("=" * 80)
    
    llm = get_llm_manager()
    
    insecure_code = '''
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    return result

def execute_user_code(code):
    exec(code)
'''
    
    print("\n📤 执行深度安全分析...")
    
    result = await llm.analyze_security(code=insecure_code, language="python")
    
    print(f"\n✅ 安全分析完成!")
    print(f"⏱️ 延迟: {result.latency:.2f}秒")
    print(f"\n📝 安全问题:\n{result.content[:800]}...")
    
    print()


async def demo_comprehensive_analysis():
    """演示综合分析"""
    print("=" * 80)
    print("4. 综合分析演示 (静态 + LLM)")
    print("=" * 80)
    
    analyzer = EnhancedAnalyzer()
    
    sample_code = '''
import os
import pickle
from functools import lru_cache

@lru_cache(maxsize=1000)
def fibonacci(n):
    """计算斐波那契数列"""
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class DataManager:
    """数据管理器"""
    
    def __init__(self, path):
        self.path = path
        self.data = None
    
    def load(self):
        """加载数据"""
        with open(self.path, 'rb') as f:
            self.data = pickle.load(f)
        return self.data
    
    def save(self, data):
        """保存数据"""
        with open(self.path, 'wb') as f:
            pickle.dump(data, f)
'''
    
    print("\n📤 执行综合代码分析...")
    
    report = await analyzer.analyze_code(
        code=sample_code,
        language="python",
        options=AnalysisOptions(
            depth=AnalysisDepth.COMPREHENSIVE,
            include_security=True,
            include_performance=True,
        )
    )
    
    print(f"\n✅ 综合分析完成!")
    print(f"📊 质量评分: {report.quality_score:.2f}/10")
    print(f"🔍 发现问题数: {len(report.findings)}")
    print(f"💡 建议数: {len(report.recommendations)}")
    print(f"⏱️ 处理时间: {report.processing_time:.2f}秒")
    
    print(f"\n⚠️ 发现的问题:")
    for finding in report.findings[:5]:
        print(f"  [{finding.severity}] {finding.title} - {finding.description}")
    
    print(f"\n💡 主要建议:")
    for rec in report.recommendations[:5]:
        print(f"  - {rec}")
    
    print()


async def demo_performance_analysis():
    """演示性能分析"""
    print("=" * 80)
    print("5. 性能分析演示")
    print("=" * 80)
    
    llm = get_llm_manager()
    
    slow_code = '''
def find_duplicates(items):
    """找出重复项"""
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == items[j] and i != j:
                if items[i] not in duplicates:
                    duplicates.append(items[i])
    return duplicates
'''
    
    print("\n📤 执行性能分析...")
    
    result = await llm.analyze_performance(code=slow_code, language="python")
    
    print(f"\n✅ 性能分析完成!")
    print(f"⏱️ 延迟: {result.latency:.2f}秒")
    print(f"\n📝 分析结果:\n{result.content[:800]}...")
    
    print()


async def demo_test_generation():
    """演示测试生成"""
    print("=" * 80)
    print("6. 自动测试生成演示")
    print("=" * 80)
    
    llm = get_llm_manager()
    
    code = '''
def add(a, b):
    """加法函数"""
    return a + b

def divide(a, b):
    """除法函数"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b
'''
    
    print("\n📤 生成测试用例...")
    
    result = await llm.generate_tests(
        code=code,
        language="python",
        test_framework="pytest",
    )
    
    print(f"\n✅ 测试生成完成!")
    print(f"⏱️ 延迟: {result.latency:.2f}秒")
    print(f"\n📝 生成的测试代码:\n{result.content[:800]}...")
    
    print()


async def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🌟 企业级双模式Agent系统 - LLM集成演示")
    print("=" * 80)
    print("\n🔗 连接到硅基流动API...")
    print(f"📡 模型: Qwen/Qwen2.5-7B-Instruct")
    print(f"🔑 API Key: {('*' * 20) + '...gq'}\n")
    
    try:
        await demo_basic_llm()
        await demo_code_analysis()
        await demo_security_analysis()
        await demo_comprehensive_analysis()
        await demo_performance_analysis()
        await demo_test_generation()
        
        print("=" * 80)
        print("✅ 所有演示完成!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        llm = get_llm_manager()
        await llm.close()


if __name__ == "__main__":
    asyncio.run(main())
