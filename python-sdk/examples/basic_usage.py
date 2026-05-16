#!/usr/bin/env python3
"""
Enterprise Agent System - Python SDK使用示例

本文件展示如何使用Python SDK进行各种操作
"""

import asyncio
import os
from enterprise_agent_sdk import (
    EnterpriseAgentSDK,
    TaskPriority,
    TaskStatus,
)


async def basic_task_example():
    """基础任务操作示例"""
    print("=" * 60)
    print("基础任务操作示例")
    print("=" * 60)
    
    async with EnterpriseAgentSDK(
        base_url="http://localhost:8000",
        api_key=os.getenv("AGENT_API_KEY"),
    ) as sdk:
        # 创建任务
        task = await sdk.tasks.create(
            task_title="分析Vue.js项目",
            task_description="深度分析Vue.js 3的响应式系统实现",
            priority=TaskPriority.HIGH,
            tags=["vue", "javascript", "analysis"],
        )
        print(f"✅ 任务创建成功: {task.task_id}")
        print(f"   标题: {task.task_title}")
        print(f"   优先级: {task.priority.value}")
        
        # 列出所有任务
        all_tasks = await sdk.tasks.list()
        print(f"\n📋 当前任务总数: {len(all_tasks)}")
        
        # 获取任务统计
        stats = await sdk.tasks.statistics()
        print(f"\n📊 任务统计:")
        print(f"   总数: {stats['total']}")
        print(f"   待处理: {stats['pending']}")
        print(f"   运行中: {stats['running']}")
        print(f"   已完成: {stats['completed']}")
        print(f"   失败: {stats['failed']}")
        print(f"   成功率: {stats['success_rate']}")


async def advanced_task_example():
    """高级任务操作示例"""
    print("\n" + "=" * 60)
    print("高级任务操作示例")
    print("=" * 60)
    
    async with EnterpriseAgentSDK() as sdk:
        # 创建多个任务
        tasks = await asyncio.gather(
            sdk.tasks.create(
                task_title=f"任务 {i}",
                task_description=f"这是任务 {i} 的描述",
                priority=TaskPriority.HIGH if i % 3 == 0 else TaskPriority.MEDIUM,
            )
            for i in range(1, 6)
        )
        print(f"✅ 批量创建 {len(tasks)} 个任务")
        
        # 筛选高优先级任务
        high_priority = await sdk.tasks.list(priority=TaskPriority.HIGH)
        print(f"\n🔴 高优先级任务: {len(high_priority)}")
        
        # 启动任务
        task_id = tasks[0].task_id
        started_task = await sdk.tasks.start(task_id)
        print(f"\n▶️ 启动任务: {started_task.task_id}")
        print(f"   状态: {started_task.status.value}")
        
        # 完成任务
        completed_task = await sdk.tasks.complete(
            task_id,
            result={
                "analysis": "Vue.js响应式系统分析完成",
                "findings": [
                    "使用Proxy实现响应式",
                    "依赖追踪机制完善",
                    "计算属性优化",
                ],
            },
        )
        print(f"\n✅ 完成任务: {completed_task.task_id}")
        print(f"   状态: {completed_task.status.value}")
        print(f"   结果: {completed_task.result}")


async def agent_example():
    """Agent管理示例"""
    print("\n" + "=" * 60)
    print("Agent管理示例")
    print("=" * 60)
    
    async with EnterpriseAgentSDK() as sdk:
        # 创建Agent
        agent = await sdk.agents.create(
            agent_name="Vue Analyzer Agent",
            agent_mode="dual",
        )
        print(f"✅ Agent创建成功: {agent.agent_id}")
        print(f"   名称: {agent.agent_name}")
        print(f"   模式: {agent.agent_mode}")
        
        # 列出所有Agent
        agents = await sdk.agents.list()
        print(f"\n📋 当前Agent总数: {len(agents)}")
        
        # 启动Agent
        await sdk.agents.start(agent.agent_id)
        print(f"\n▶️ Agent已启动")
        
        # 停止Agent
        await sdk.agents.stop(agent.agent_id)
        print(f"⏹️ Agent已停止")


async def memory_example():
    """知识图谱记忆示例"""
    print("\n" + "=" * 60)
    print("知识图谱记忆示例")
    print("=" * 60)
    
    async with EnterpriseAgentSDK() as sdk:
        # 创建记忆
        memory = await sdk.memory.create(
            memory_title="Vue.js响应式原理",
            memory_content="""
            Vue.js 3使用Proxy实现响应式系统：
            1. 使用Proxy拦截对象操作
            2. 通过WeakMap存储响应式映射
            3. 依赖追踪使用Dep类管理
            4. effect函数自动收集依赖
            5. 触发更新时执行所有effect
            """,
            memory_category="technology",
            memory_tags=["vue", "reactivity", "proxy", "javascript"],
        )
        print(f"✅ 记忆创建成功: {memory.memory_id}")
        print(f"   标题: {memory.memory_title}")
        print(f"   分类: {memory.memory_category}")
        print(f"   标签: {memory.memory_tags}")
        
        # 搜索记忆
        results = await sdk.memory.search("Vue.js 响应式")
        print(f"\n🔍 搜索结果: {len(results)} 条")
        
        # 获取知识图谱摘要
        summary = await sdk.memory.knowledge_graph_summary()
        print(f"\n🧠 知识图谱摘要:")
        print(f"   总记忆数: {summary['total_memories']}")
        print(f"   分类: {summary['categories']}")
        print(f"   节点数: {summary['total_nodes']}")
        print(f"   边数: {summary['total_edges']}")


async def project_analysis_example():
    """项目分析示例"""
    print("\n" + "=" * 60)
    print("项目分析示例")
    print("=" * 60)
    
    async with EnterpriseAgentSDK() as sdk:
        # 获取支持的项目类型
        types = await sdk.projects.supported_types()
        print("📦 支持的项目类型:")
        for ptype in types["types"]:
            print(f"   {ptype['name']}: {', '.join(ptype['extensions'])}")
        
        # 分析本地项目
        result = await sdk.projects.analyze(
            project_path="/workspace/vue-core",
            analysis_type="typescript",
        )
        print(f"\n📊 项目分析结果:")
        print(f"   项目名称: {result['project_name']}")
        print(f"   项目类型: {result['project_type']}")
        print(f"   质量评分: {result['quality_score']}")
        print(f"   统计信息: {result['statistics']}")


async def batch_processing_example():
    """批量处理示例"""
    print("\n" + "=" * 60)
    print("批量处理示例")
    print("=" * 60)
    
    async with EnterpriseAgentSDK() as sdk:
        # 批量创建任务
        task_configs = [
            {"title": f"分析模块 {i}", "desc": f"分析第{i}个模块"}
            for i in range(1, 11)
        ]
        
        tasks = []
        for config in task_configs:
            task = await sdk.tasks.create(
                task_title=config["title"],
                task_description=config["desc"],
                priority=TaskPriority.MEDIUM,
            )
            tasks.append(task)
        
        print(f"✅ 批量创建 {len(tasks)} 个任务")
        
        # 批量启动任务
        await asyncio.gather(*[sdk.tasks.start(t.task_id) for t in tasks])
        print(f"▶️ 批量启动 {len(tasks)} 个任务")
        
        # 模拟处理时间
        await asyncio.sleep(1)
        
        # 批量完成任务
        await asyncio.gather(*[
            sdk.tasks.complete(t.task_id, result={"status": "success"})
            for t in tasks
        ])
        print(f"✅ 批量完成 {len(tasks)} 个任务")


async def error_handling_example():
    """错误处理示例"""
    print("\n" + "=" * 60)
    print("错误处理示例")
    print("=" * 60)
    
    async with EnterpriseAgentSDK() as sdk:
        try:
            # 尝试获取不存在的任务
            task = await sdk.tasks.get("non-existent-id")
        except Exception as e:
            print(f"❌ 捕获异常: {type(e).__name__}")
            print(f"   消息: {str(e)}")
        
        print("\n✅ 错误处理完成")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Enterprise Agent System - Python SDK演示")
    print("=" * 60)
    
    try:
        # 运行所有示例
        await basic_task_example()
        await advanced_task_example()
        await agent_example()
        await memory_example()
        await project_analysis_example()
        await batch_processing_example()
        await error_handling_example()
        
        print("\n" + "=" * 60)
        print("🎉 所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
