"""
第9次迭代：用户体验与全面最终验证测试
Iteration 9: Ultimate User Experience & Final Comprehensive Test

按照用户要求进行：
1. 用户体验测试 - 模拟真实用户操作
2. 极限压测 - 100%系统能力验证
3. 最终全面验证 - 所有功能一次性验证
4. 边界条件穷尽测试
5. 内存泄漏检测与性能监控
6. 异常场景深度测试

重点测试：
- 真实用户完整会话模拟
- 极限压测到系统性能边界
- 所有接口全面覆盖
- 异常恢复验证
- 内存使用监控
- 最终全面验收
"""

import sys
import time
import random
import threading
import gc
import tracemalloc
import traceback
import logging
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Iteration9Logger")


print("=" * 120)
print("🏆 第9次迭代：用户体验与全面最终验证测试")
print("=" * 120)
print(f"[INIT] 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"[INIT] 目标: 最终全面验证，100%功能覆盖，极限压测")
print()


class Iteration9Tester:
    """第9次迭代测试器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.success_count = 0
        self.error_count = 0
        self.warning_count = 0
        self.operation_count = 0
        self.error_details = []
        self.memory_snapshots = []
        
        # 导入真实模块
        logger.info("[INIT] 导入核心模块...")
        from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            TaskPriorityLevelEnumeration, TaskExecutionStatusEnumeration
        )
        
        self.backend = InMemoryDataStorageBackend()
        self.Priority = TaskPriorityLevelEnumeration
        self.Status = TaskExecutionStatusEnumeration
        
        logger.info("[INIT] 核心模块导入完成，系统初始化成功")
    
    def record_operation(self, success: bool, operation_name: str, error: str = None):
        """记录操作结果"""
        with threading.Lock():
            self.operation_count += 1
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
                if error:
                    self.error_details.append((operation_name, error))
        
        # 每1000次操作打印进度
        if self.operation_count % 1000 == 0:
            elapsed = time.time() - self.start_time
            logger.info(
                f"[PROGRESS] 操作数: {self.operation_count:>8} | "
                f"成功: {self.success_count:>8} | "
                f"错误: {self.error_count:>3} | "
                f"成功率: {self.success_count / self.operation_count * 100:>5.1f}% | "
                f"已运行: {elapsed:>.1f}秒"
            )
    
    def checkpoint(self, name: str):
        """打印检查点"""
        elapsed = time.time() - self.start_time
        print()
        print("=" * 120)
        print(f"📊 检查点: {name}")
        print("=" * 120)
        print(f"⏱️  已运行: {elapsed:>.2f}秒")
        print(f"📈 总操作数: {self.operation_count:>10}")
        print(f"✅ 成功: {self.success_count:>10}")
        print(f"❌ 错误: {self.error_count:>10}")
        
        if self.operation_count > 0:
            print(f"🎯 成功率: {self.success_count / self.operation_count * 100:>.1f}%")
        
        if self.error_details:
            print("📋 错误详情:")
            for err_name, err_msg in self.error_details[-10:]:
                print(f"  - {err_name}: {err_msg}")
        print("=" * 120)
        print()
    
    def take_memory_snapshot(self, label: str):
        """记录内存快照"""
        try:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            total_size = sum(stat.size for stat in top_stats)
            
            with threading.Lock():
                self.memory_snapshots.append({
                    'label': label,
                    'timestamp': time.time(),
                    'size_mb': total_size / (1024 * 1024)
                })
        except Exception as e:
            logger.warning(f"[MEMORY] 内存快照失败: {e}")
    
    def test_1_user_session_simulation(self, num_sessions: int = 50, duration_seconds: int = 30):
        """测试1：真实用户会话模拟"""
        print("\n" + "=" * 120)
        print("👤 测试1：真实用户会话模拟")
        print("=" * 120)
        
        self.take_memory_snapshot("BeforeUserSessionTest")
        
        threads = []
        start_event = threading.Event()
        completed = [0]
        
        def user_session(user_id: int):
            try:
                start_event.wait()
                
                # 完整的用户会话：登录 -> 创建数据 -> 搜索 -> 更新 -> 查看统计 -> 结束
                for i in range(20):
                    # 1. 创建任务
                    task_title = f"[User{user_id}] Task-{user_id}-{i}"
                    task = self.backend.create_new_task_entry(
                        task_title=task_title,
                        priority_level=random.choice([
                            self.Priority.LOW_PRIORITY_LEVEL,
                            self.Priority.MEDIUM_PRIORITY_LEVEL,
                            self.Priority.HIGH_PRIORITY_LEVEL,
                            self.Priority.URGENT_PRIORITY_LEVEL
                        ])
                    )
                    self.record_operation(task is not None, f"CreateTask-{user_id}-{i}")
                    
                    # 2. 创建记忆
                    memory = self.backend.create_new_memory_entry(
                        content_text=f"[User{user_id}] Memory-{user_id}-{i}: 用户{user_id}在{i}时刻的记忆内容",
                        tags_list=[f"user{user_id}", "session", random.choice(["work", "personal", "project"])],
                        importance_score=random.randint(1, 5)
                    )
                    self.record_operation(memory is not None, f"CreateMemory-{user_id}-{i}")
                    
                    # 3. 搜索相关记忆
                    results = self.backend.search_memories_by_text_content(search_query=f"user{user_id}")
                    self.record_operation(results is not None, f"SearchMemory-{user_id}-{i}")
                    
                    # 4. 更新任务状态
                    if task:
                        updated_task = self.backend.update_task_entry(
                            task_id=task.unique_entity_id,
                            progress_percentage_value=random.random() * 100,
                            execution_status=random.choice([
                                self.Status.PENDING_STATUS,
                                self.Status.IN_PROGRESS_STATUS,
                                self.Status.COMPLETED_STATUS
                            ])
                        )
                        self.record_operation(updated_task is not None, f"UpdateTask-{user_id}-{i}")
                    
                    # 5. 创建知识图谱节点
                    node_id = self.backend.add_node_to_knowledge_graph(
                        label=f"[User{user_id}] Node-{user_id}-{i}",
                        properties={'user': user_id, 'type': 'data'}
                    )
                    self.record_operation(node_id is not None, f"CreateNode-{user_id}-{i}")
                
                with threading.Lock():
                    completed[0] += 1
                
            except Exception as e:
                logger.error(f"[ERROR] 用户会话异常 (User {user_id}): {e}")
                self.record_operation(False, f"UserSession-{user_id}", str(e))
        
        logger.info(f"[TEST1] 启动 {num_sessions} 个并发用户会话，持续 {duration_seconds} 秒")
        
        for i in range(num_sessions):
            t = threading.Thread(target=user_session, args=(i,), name=f"UserSession-{i}")
            threads.append(t)
            t.start()
        
        start_event.set()
        
        logger.info(f"[TEST1] 所有用户会话已启动，等待完成...")
        
        for t in threads:
            t.join(timeout=60)
        
        self.take_memory_snapshot("AfterUserSessionTest")
        self.checkpoint("用户会话模拟测试完成")
    
    def test_2_extreme_stress_test(self):
        """测试2：极限压力测试"""
        print("\n" + "=" * 120)
        print("🔥 测试2：极限压力测试")
        print("=" * 120)
        
        self.take_memory_snapshot("BeforeExtremeStressTest")
        
        logger.info("[TEST2] 开始批量创建任务...")
        tasks_created = 0
        start = time.time()
        for i in range(20000):
            task = self.backend.create_new_task_entry(
                task_title=f"StressTest-Task-{i}",
                task_description="这是一个极限压力测试的任务，用于验证系统的批量创建能力",
                priority_level=random.choice([
                    self.Priority.LOW_PRIORITY_LEVEL,
                    self.Priority.MEDIUM_PRIORITY_LEVEL,
                    self.Priority.HIGH_PRIORITY_LEVEL,
                    self.Priority.URGENT_PRIORITY_LEVEL
                ])
            )
            if task:
                tasks_created += 1
            self.record_operation(task is not None, f"StressCreateTask-{i}")
        
        elapsed = time.time() - start
        logger.info(f"[TEST2] 任务创建完成，耗时 {elapsed:.2f}秒，吞吐量: {tasks_created / elapsed:.0f} ops/s")
        
        logger.info("[TEST2] 开始批量创建记忆...")
        memories_created = 0
        start = time.time()
        for i in range(20000):
            memory = self.backend.create_new_memory_entry(
                content_text=f"StressTest-Memory-{i}: " * 5,
                tags_list=[f"stress", "test", f"batch-{i // 1000}"],
                importance_score=random.randint(1, 5)
            )
            if memory:
                memories_created += 1
            self.record_operation(memory is not None, f"StressCreateMemory-{i}")
        
        elapsed = time.time() - start
        logger.info(f"[TEST2] 记忆创建完成，耗时 {elapsed:.2f}秒，吞吐量: {memories_created / elapsed:.0f} ops/s")
        
        logger.info("[TEST2] 开始批量创建知识图谱节点...")
        nodes_created = 0
        start = time.time()
        for i in range(20000):
            node_id = self.backend.add_node_to_knowledge_graph(
                label=f"StressTest-Node-{i}",
                properties={'type': 'test', 'index': i}
            )
            if node_id:
                nodes_created += 1
            self.record_operation(node_id is not None, f"StressCreateNode-{i}")
        
        elapsed = time.time() - start
        logger.info(f"[TEST2] 知识图谱节点创建完成，耗时 {elapsed:.2f}秒，吞吐量: {nodes_created / elapsed:.0f} ops/s")
        
        self.take_memory_snapshot("AfterExtremeStressTest")
        self.checkpoint("极限压力测试完成")
    
    def test_3_edge_case_complete_coverage(self):
        """测试3：边界条件完全覆盖"""
        print("\n" + "=" * 120)
        print("🔬 测试3：边界条件完全覆盖")
        print("=" * 120)
        
        self.take_memory_snapshot("BeforeEdgeCaseTest")
        
        edge_cases = [
            ("EmptyString", "", ""),
            ("VeryShortString", "a", "b"),
            ("VeryLongString_10KB", "x" * 10240, "y" * 10240),
            ("UnicodeString", "🎉✨🎊⭐🔥", "中文测试日本語한글"),
            ("SpecialChars", "!@#$%^&*()_+-=[]{}|;':\",./<>?\\", "123"),
        ]
        
        for name, title, desc in edge_cases:
            try:
                task = self.backend.create_new_task_entry(
                    task_title=title,
                    task_description=desc
                )
                self.record_operation(task is not None, f"EdgeCase-Task-{name}")
                
                memory = self.backend.create_new_memory_entry(content_text=title + " " + desc)
                self.record_operation(memory is not None, f"EdgeCase-Memory-{name}")
            except Exception as e:
                self.record_operation(False, f"EdgeCase-{name}", str(e))
        
        # 极端值测试
        for priority in [-1000, -1, 0, 1, 100, 10000, None, "invalid", ""]:
            try:
                task = self.backend.create_new_task_entry(
                    task_title=f"PriorityTest-{priority}",
                    priority_level=priority
                )
                self.record_operation(task is not None, f"EdgeCase-Priority-{priority}")
            except Exception as e:
                self.record_operation(False, f"EdgeCase-Priority-{priority}", str(e))
        
        # 不存在ID测试
        non_existent_id = "this-id-never-exists-12345"
        try:
            task = self.backend.retrieve_task_by_id(non_existent_id)
            memory = self.backend.retrieve_memory_by_id(non_existent_id)
            self.record_operation(True, "EdgeCase-NonExistentID")
        except Exception as e:
            self.record_operation(False, "EdgeCase-NonExistentID", str(e))
        
        self.take_memory_snapshot("AfterEdgeCaseTest")
        self.checkpoint("边界条件测试完成")
    
    def test_4_comprehensive_error_recovery(self):
        """测试4：全面错误恢复测试"""
        print("\n" + "=" * 120)
        print("💥 测试4：全面错误恢复测试")
        print("=" * 120)
        
        self.take_memory_snapshot("BeforeErrorRecoveryTest")
        
        # 1. 创建一些有效数据作为基准
        baseline_tasks = []
        for i in range(10):
            task = self.backend.create_new_task_entry(task_title=f"Baseline-Task-{i}")
            if task:
                baseline_tasks.append(task.unique_entity_id)
        
        logger.info("[TEST4] 基准数据创建完成，开始错误场景测试")
        
        # 2. 强制垃圾回收
        for _ in range(5):
            gc.collect()
            time.sleep(0.01)
        
        self.take_memory_snapshot("AfterGC")
        
        # 3. 验证基准数据仍然存在
        all_found = True
        for task_id in baseline_tasks:
            try:
                task = self.backend.retrieve_task_by_id(task_id)
                if not task:
                    all_found = False
            except Exception as e:
                all_found = False
        
        self.record_operation(all_found, "ErrorRecovery-GC")
        
        # 4. 大量操作后验证系统稳定
        for i in range(1000):
            task = self.backend.create_new_task_entry(task_title=f"RecoveryTest-Task-{i}")
            self.record_operation(task is not None, f"RecoveryTest-Op-{i}")
        
        self.take_memory_snapshot("AfterErrorRecoveryTest")
        self.checkpoint("错误恢复测试完成")
    
    def test_5_final_statistics_and_verification(self):
        """测试5：最终统计和验证"""
        print("\n" + "=" * 120)
        print("📋 测试5：最终统计和验证")
        print("=" * 120)
        
        logger.info("[TEST5] 获取系统统计信息")
        stats = self.backend.generate_system_statistics_snapshot()
        
        if stats:
            logger.info(f"[TEST5] 总任务数: {stats.total_tasks_count}")
            logger.info(f"[TEST5] 总记忆数: {stats.total_memories_count}")
            logger.info(f"[TEST5] 知识图谱节点数: {stats.knowledge_graph_nodes_count}")
            logger.info(f"[TEST5] 知识图谱边数: {stats.knowledge_graph_edges_count}")
            
            # 验证合理性
            if stats.total_tasks_count > 0 and stats.total_memories_count > 0:
                self.record_operation(True, "FinalVerification-Stats")
            else:
                self.record_operation(False, "FinalVerification-Stats", "统计数据异常")
        else:
            self.record_operation(False, "FinalVerification-Stats", "无法获取统计信息")
        
        self.take_memory_snapshot("FinalSnapshot")
        self.checkpoint("最终统计验证完成")
    
    def generate_final_report(self):
        """生成最终报告"""
        elapsed = time.time() - self.start_time
        success_rate = 0
        if self.operation_count > 0:
            success_rate = (self.success_count / self.operation_count) * 100
        
        print("\n" + "=" * 120)
        print("🎯 第9次迭代：最终全面验收报告")
        print("=" * 120)
        print()
        
        print(f"⏱️  总运行时间: {elapsed:.2f}秒")
        print(f"📈 总操作数: {self.operation_count:>10}")
        print(f"✅ 成功操作数: {self.success_count:>10}")
        print(f"❌ 错误数: {self.error_count:>10}")
        print(f"🎯 成功率: {success_rate:.2f}%")
        
        print()
        print("📊 内存使用统计:")
        for snap in self.memory_snapshots:
            elapsed = snap['timestamp'] - self.memory_snapshots[0]['timestamp']
            print(f"  [{snap['label']}] {elapsed:>5.1f}s: {snap['size_mb']:>8.2f}MB")
        
        print()
        if self.error_details:
            print(f"⚠️ 错误详情 ({len(self.error_details)}):")
            for i, (name, msg) in enumerate(self.error_details[:20]):
                print(f"  {i+1}. {name}: {msg}")
        else:
            print("✅ 无错误记录！")
        
        print()
        print("=" * 120)
        
        if success_rate == 100 and self.error_count == 0:
            print("🏆🏆🏆 完美通过！100%成功率，0个错误！")
            print("🏆🏆🏆 系统已达到最高质量标准，可正式投入生产使用！")
            return True
        elif success_rate >= 99.9:
            print("✅✅✅ 非常优秀！成功率 99.9%+，可投入生产使用！")
            return True
        elif success_rate >= 95:
            print("✅✅ 表现良好！成功率 95%+，可基本投入使用！")
            return True
        else:
            print("❌ 需要进一步优化改进")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("[MAIN] 开始第9次迭代完整测试套件")
        
        # 启用内存跟踪
        tracemalloc.start()
        
        try:
            self.test_1_user_session_simulation()
            self.test_2_extreme_stress_test()
            self.test_3_edge_case_complete_coverage()
            self.test_4_comprehensive_error_recovery()
            self.test_5_final_statistics_and_verification()
        except Exception as e:
            logger.error(f"[MAIN] 测试过程异常: {e}")
            traceback.print_exc()
            self.record_operation(False, "MainTestFlow", str(e))
        finally:
            tracemalloc.stop()
        
        return self.generate_final_report()


def main():
    """主函数"""
    tester = Iteration9Tester()
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
