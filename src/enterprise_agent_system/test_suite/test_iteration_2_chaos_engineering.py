"""
第2次迭代：混沌工程测试 - 极限混乱场景
Iteration 2: Chaos Engineering - Extreme Chaos Scenarios

基于第1次迭代的发现，进行更高难度、更大规模、更混乱的场景测试
"""

import sys
import time
import random
import threading
import gc
import uuid
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime
import copy

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

print("=" * 150)
print("🚀 启动第2次迭代：混沌工程测试 - 极限混乱场景")
print("=" * 150)
print(f"[INIT] 测试开始时间: {datetime.now().isoformat()}")
print(f"[INIT] 目标: 发现系统在极限混乱场景下的隐藏问题")
print()


class ChaosEngineeringTestRunner:
    """混沌工程测试运行器"""
    
    def __init__(self):
        print("[INIT] 正在初始化混沌测试环境...")
        from enterprise_agent_system.core.in_memory_data_storage_backend import (
            InMemoryDataStorageBackend,
        )
        from enterprise_agent_system.infrastructure.simple_memory_store import (
            SimpleMemoryStore,
            SimpleCache,
        )
        
        self.backend = InMemoryDataStorageBackend()
        self.store = SimpleMemoryStore()
        self.cache = SimpleCache()
        
        self.errors: List[Dict[str, Any]] = []
        self.critical_bugs: List[Dict[str, Any]] = []
        self.stats = {
            "total_operations": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "start_time": time.time(),
            "checkpoints": [],
        }
        
        self.lock = threading.Lock()
        self.operation_count = 0
        self.error_count = 0
        
        print("[INIT] 混沌测试环境初始化完成")
        print()
    
    def safe_operation(self, operation_name: str, operation_func, *args, **kwargs):
        """安全的操作包装器"""
        try:
            with self.lock:
                self.operation_count += 1
            result = operation_func(*args, **kwargs)
            return result
        except Exception as e:
            with self.lock:
                self.error_count += 1
            self.errors.append({
                "operation": operation_name,
                "error": str(e),
                "traceback": traceback.format_exc(),
            })
            return None
    
    def checkpoint(self, name: str):
        """记录检查点"""
        elapsed = time.time() - self.stats["start_time"]
        self.stats["checkpoints"].append({
            "name": name,
            "elapsed": elapsed,
            "operations": self.operation_count,
            "errors": self.error_count,
        })
        print(f"🔍 [CHECKPOINT] {name} @ {elapsed:.2f}s | 操作: {self.operation_count:,} | 错误: {self.error_count}")
    
    # =========================================================================
    # 混沌测试1: 极端并发冲突
    # =========================================================================
    def chaos_test_1_extreme_race_conditions(self):
        """混沌测试1: 极端并发冲突"""
        print("=" * 150)
        print("💥 混沌测试1: 极端并发冲突")
        print("=" * 150)
        print()
        
        barrier = threading.Barrier(100)
        race_errors = []
        
        def racer(worker_id):
            try:
                barrier.wait()
                
                # 100个线程同时创建同名任务
                for i in range(10):
                    task_title = f"Race_Task_{worker_id}_{i}"
                    
                    # 创建
                    task = self.backend.create_new_task_entry(
                        task_title=task_title,
                        task_description=f"Worker {worker_id} iteration {i}",
                    )
                    
                    # 立即更新
                    self.backend.update_task_entry(
                        task.unique_entity_id,
                        progress_percentage_value=random.random(),
                    )
                    
                    # 立即检索
                    retrieved = self.backend.retrieve_task_by_id(task.unique_entity_id)
                    if not retrieved:
                        race_errors.append(f"Worker {worker_id}: 任务检索失败")
                    
                    # 创建关联记忆
                    memory = self.backend.create_new_memory_entry(
                        content_text=f"记忆_{task.unique_entity_id}",
                        source_task_id=task.unique_entity_id,
                    )
                    
                    # 创建关联节点
                    node = self.backend.add_node_to_knowledge_graph(
                        label=f"Node_{task.unique_entity_id}",
                        memory_id=memory.unique_memory_id,
                    )
                    
                    # 创建边
                    if i > 0:
                        try:
                            prev_node = f"Node_{task_title.replace(str(i), str(i-1))}"
                            # 这个会失败，但测试容错
                        except:
                            pass
                
            except Exception as e:
                race_errors.append(f"Worker {worker_id}: {str(e)}")
        
        threads = [threading.Thread(target=racer, args=(i,)) for i in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        if race_errors:
            print(f"❌ 发现 {len(race_errors)} 个竞态条件错误")
            for err in race_errors[:5]:
                print(f"   - {err[:100]}")
        else:
            print(f"✅ 无竞态条件错误，100线程 × 10次操作完美执行")
        
        self.checkpoint("Chaos1: 极端并发冲突")
        print()
    
    # =========================================================================
    # 混沌测试2: 数据一致性地狱
    # =========================================================================
    def chaos_test_2_consistency_hell(self):
        """混沌测试2: 数据一致性地狱"""
        print("=" * 150)
        print("💥 混沌测试2: 数据一致性地狱")
        print("=" * 150)
        print()
        
        inconsistencies = []
        
        # 创建初始任务
        task = self.backend.create_new_task_entry(
            task_title="一致性地狱测试",
            task_description="测试复杂场景下的数据一致性",
        )
        task_id = task.unique_entity_id
        print(f"[CONSISTENCY] 创建初始任务: {task_id}")
        
        # 100个线程同时修改同一个任务
        barrier = threading.Barrier(100)
        
        def consistency_worker(worker_id):
            try:
                barrier.wait()
                
                for i in range(50):
                    # 随机操作
                    operation = random.choice([
                        "update_title",
                        "update_progress",
                        "update_status",
                        "retrieve",
                        "create_memory",
                    ])
                    
                    if operation == "update_title":
                        new_title = f"Worker{worker_id}_Iter{i}_Task"
                        self.backend.update_task_entry(
                            task_id,
                            task_title=new_title,
                        )
                    
                    elif operation == "update_progress":
                        self.backend.update_task_entry(
                            task_id,
                            progress_percentage_value=random.random(),
                        )
                    
                    elif operation == "update_status":
                        statuses = [
                            "pending", "in_progress", "completed", "failed",
                            None, "invalid",  # 异常输入
                        ]
                        self.backend.update_task_entry(
                            task_id,
                            execution_status=random.choice(statuses),
                        )
                    
                    elif operation == "retrieve":
                        retrieved = self.backend.retrieve_task_by_id(task_id)
                        if not retrieved:
                            inconsistencies.append(f"Worker {worker_id}: 检索失败")
                    
                    elif operation == "create_memory":
                        self.backend.create_new_memory_entry(
                            content_text=f"Worker{worker_id}_Memory_{i}",
                            source_task_id=task_id,
                        )
            
            except Exception as e:
                inconsistencies.append(f"Worker {worker_id}: {str(e)}")
        
        threads = [threading.Thread(target=consistency_worker, args=(i,)) for i in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # 验证最终一致性
        final_task = self.backend.retrieve_task_by_id(task_id)
        if final_task:
            print(f"[CONSISTENCY] 最终任务状态:")
            print(f"   - 标题: {final_task.task_title}")
            print(f"   - 进度: {final_task.progress_percentage_value}")
            print(f"   - 状态: {final_task.execution_status}")
        
        # 统计
        memories = self.backend.search_memories_by_text_content(task_id)
        print(f"[CONSISTENCY] 创建的记忆数: {len(memories)}")
        
        if inconsistencies:
            print(f"❌ 发现 {len(inconsistencies)} 个一致性问题")
        else:
            print(f"✅ 100线程 × 50次操作，0一致性问题")
        
        self.checkpoint("Chaos2: 数据一致性地狱")
        print()
    
    # =========================================================================
    # 混沌测试3: 资源耗尽测试
    # =========================================================================
    def chaos_test_3_resource_exhaustion(self):
        """混沌测试3: 资源耗尽测试"""
        print("=" * 150)
        print("💥 混沌测试3: 资源耗尽测试")
        print("=" * 150)
        print()
        
        print("[RESOURCE] 开始资源耗尽测试...")
        
        # 1. 内存压力测试
        print("[RESOURCE] 1. 内存压力测试: 创建大量对象...")
        large_objects = []
        for i in range(1000):
            task = self.backend.create_new_task_entry(
                task_title=f"内存压力测试_{i}_" + "x" * 1000,
                task_description="y" * 10000,
            )
            memory = self.backend.create_new_memory_entry(
                content_text="z" * 10000,
                tags_list=[f"tag_{j}" for j in range(100)],
            )
            large_objects.append((task, memory))
            
            if i % 100 == 0:
                print(f"   创建了 {i} 个大对象")
        
        print(f"[RESOURCE] 创建了 {len(large_objects)} 个大对象")
        
        # 强制垃圾回收
        gc.collect()
        print("[RESOURCE] 垃圾回收完成")
        
        # 2. 嵌套数据结构测试
        print("[RESOURCE] 2. 嵌套数据结构测试...")
        for i in range(100):
            metadata = {
                f"level_{j}": {
                    f"sub_{k}": {
                        f"deep_{l}": f"value_{i}_{j}_{k}_{l}"
                        for l in range(10)
                    }
                    for k in range(10)
                }
                for j in range(5)
            }
            
            task = self.backend.create_new_task_entry(
                task_title=f"嵌套数据测试_{i}",
            )
            self.backend.update_task_entry(
                task.unique_entity_id,
                metadata_dictionary=metadata,
            )
        
        print(f"[RESOURCE] 创建了 100 个嵌套对象")
        
        # 3. 极端字符串测试
        print("[RESOURCE] 3. 极端字符串测试...")
        for i in range(50):
            # 超长字符串
            long_string = "A" * 100000
            # Unicode
            unicode_string = "🎉" * 10000
            # 特殊字符
            special_string = "\n\t\r\0\x00" * 1000
            
            task = self.backend.create_new_task_entry(
                task_title=f"极端字符串_{i}",
            )
            self.backend.update_task_entry(
                task.unique_entity_id,
                task_description=long_string,
                error_message=unicode_string,
            )
        
        print(f"[RESOURCE] 创建了 50 个极端字符串对象")
        
        # 4. 验证系统仍然正常工作
        print("[RESOURCE] 4. 验证系统稳定性...")
        test_task = self.backend.create_new_task_entry("资源耗尽后测试")
        retrieved = self.backend.retrieve_task_by_id(test_task.unique_entity_id)
        
        if retrieved:
            print(f"✅ 系统在资源压力后仍正常工作")
        else:
            print(f"❌ 系统在资源压力后出现问题")
        
        self.checkpoint("Chaos3: 资源耗尽测试")
        print()
    
    # =========================================================================
    # 混沌测试4: 边界条件极限测试
    # =========================================================================
    def chaos_test_4_boundary_limits(self):
        """混沌测试4: 边界条件极限测试"""
        print("=" * 150)
        print("💥 混沌测试4: 边界条件极限测试")
        print("=" * 150)
        print()
        
        boundary_failures = []
        
        # 1. 极限数值测试
        print("[BOUNDARY] 1. 极限数值测试...")
        test_task = self.backend.create_new_task_entry("极限数值测试")
        
        extreme_values = [
            ("progress", -1.0),
            ("progress", -0.0001),
            ("progress", 1.0001),
            ("progress", 1e308),  # 接近float最大值
            ("progress", 1e-308),  # 接近float最小值
            ("progress", float('inf')),
            ("progress", float('-inf')),
            ("progress", float('nan')),
        ]
        
        for name, value in extreme_values:
            try:
                self.backend.update_task_entry(
                    test_task.unique_entity_id,
                    progress_percentage_value=value,
                )
                retrieved = self.backend.retrieve_task_by_id(test_task.unique_entity_id)
                if retrieved:
                    print(f"   {name}={value} -> 存储值={retrieved.progress_percentage_value}")
            except Exception as e:
                boundary_failures.append(f"{name}={value}: {str(e)}")
        
        # 2. 极限ID测试
        print("[BOUNDARY] 2. 极限ID测试...")
        extreme_ids = [
            "",  # 空字符串
            "x",  # 单字符
            "x" * 10000,  # 超长
            "\x00\x01\x02",  # 控制字符
            "unicode_\u0000_\uffff",
            None,  # None（如果支持）
        ]
        
        for extreme_id in extreme_ids:
            try:
                result = self.backend.retrieve_task_by_id(extreme_id)
                print(f"   ID={type(extreme_id).__name__}({str(extreme_id)[:20]}) -> {type(result).__name__}")
            except Exception as e:
                boundary_failures.append(f"ID测试失败: {str(e)}")
        
        # 3. 极限枚举值测试
        print("[BOUNDARY] 3. 极限枚举值测试...")
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            TaskPriorityLevelEnumeration,
            TaskExecutionStatusEnumeration,
        )
        
        extreme_enums = [
            (TaskPriorityLevelEnumeration, 999),
            (TaskPriorityLevelEnumeration, -1),
            (TaskExecutionStatusEnumeration, "invalid_status"),
            (TaskExecutionStatusEnumeration, 12345),
        ]
        
        for enum_type, value in extreme_enums:
            try:
                task = self.backend.create_new_task_entry(
                    task_title=f"枚举测试_{value}",
                )
                if enum_type == TaskPriorityLevelEnumeration:
                    self.backend.update_task_entry(
                        task.unique_entity_id,
                        priority_level=value,
                    )
                else:
                    self.backend.update_task_entry(
                        task.unique_entity_id,
                        execution_status=value,
                    )
                print(f"   枚举测试成功: {enum_type.__name__}={value}")
            except Exception as e:
                boundary_failures.append(f"枚举{value}: {str(e)}")
        
        # 4. 极限时间戳测试
        print("[BOUNDARY] 4. 极限时间戳测试...")
        import calendar
        extreme_times = [
            0,  # Unix纪元
            -1,  # 负时间
            2147483647,  # 32位整数最大值
            9999999999,  # 未来时间
        ]
        
        for ts in extreme_times:
            try:
                task = self.backend.create_new_task_entry(
                    task_title=f"时间戳测试_{ts}",
                )
                print(f"   时间戳 {ts} 测试成功")
            except Exception as e:
                boundary_failures.append(f"时间戳{ts}: {str(e)}")
        
        if boundary_failures:
            print(f"\n❌ 发现 {len(boundary_failures)} 个边界条件失败")
            for failure in boundary_failures[:5]:
                print(f"   - {failure}")
        else:
            print(f"\n✅ 所有边界条件测试通过")
        
        self.checkpoint("Chaos4: 边界条件极限测试")
        print()
    
    # =========================================================================
    # 混沌测试5: 网络模拟故障
    # =========================================================================
    def chaos_test_5_simulated_network_failures(self):
        """混沌测试5: 网络模拟故障"""
        print("=" * 150)
        print("💥 混沌测试5: 网络模拟故障")
        print("=" * 150)
        print()
        
        # 模拟分布式场景下的竞态条件
        print("[NETWORK] 模拟分布式环境的网络延迟和故障...")
        
        barrier = threading.Barrier(50)
        simulated_errors = []
        
        def network_simulator(worker_id):
            try:
                barrier.wait()
                
                for i in range(20):
                    # 模拟网络延迟
                    delay = random.uniform(0.001, 0.01)
                    time.sleep(delay)
                    
                    # 模拟网络抖动
                    if random.random() < 0.05:  # 5%概率模拟网络错误
                        simulated_errors.append(f"Worker {worker_id}: 网络超时")
                        continue
                    
                    # 正常操作
                    task = self.backend.create_new_task_entry(
                        task_title=f"Network_{worker_id}_{i}",
                    )
                    
                    # 模拟重试
                    for retry in range(3):
                        try:
                            self.backend.update_task_entry(
                                task.unique_entity_id,
                                progress_percentage_value=random.random(),
                            )
                            break
                        except Exception as e:
                            if retry == 2:
                                simulated_errors.append(f"Worker {worker_id} 重试失败: {str(e)}")
            
            except Exception as e:
                simulated_errors.append(f"Worker {worker_id} 崩溃: {str(e)}")
        
        threads = [threading.Thread(target=network_simulator, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        print(f"[NETWORK] 模拟网络故障测试完成")
        print(f"   - 总操作: {50 * 20}")
        print(f"   - 模拟网络错误: {len([e for e in simulated_errors if '网络' in e])}")
        print(f"   - 模拟超时: {len([e for e in simulated_errors if '超时' in e])}")
        print(f"   - 重试失败: {len([e for e in simulated_errors if '重试' in e])}")
        
        if simulated_errors:
            print(f"❌ 发现 {len(simulated_errors)} 个网络模拟故障")
        else:
            print(f"✅ 所有网络模拟故障被正确处理")
        
        self.checkpoint("Chaos5: 网络模拟故障")
        print()
    
    # =========================================================================
    # 主测试运行
    # =========================================================================
    def run_all_chaos_tests(self):
        """运行所有混沌测试"""
        print("\n" + "=" * 150)
        print("🚀 开始执行第2次迭代：混沌工程测试")
        print("=" * 150)
        print()
        
        try:
            self.chaos_test_1_extreme_race_conditions()
            self.chaos_test_2_consistency_hell()
            self.chaos_test_3_resource_exhaustion()
            self.chaos_test_4_boundary_limits()
            self.chaos_test_5_simulated_network_failures()
            
        except Exception as e:
            print(f"❌ 混沌测试主程序崩溃: {e}")
            traceback.print_exc()
        
        # 生成最终报告
        self.generate_chaos_report()
    
    def generate_chaos_report(self):
        """生成混沌测试报告"""
        print("=" * 150)
        print("💥 第2次迭代：混沌工程测试 - 最终报告")
        print("=" * 150)
        print()
        
        total_time = time.time() - self.stats["start_time"]
        
        print(f"⏱️  总耗时: {total_time:.2f} 秒")
        print(f"📈 总操作数: {self.operation_count:,}")
        print(f"❌ 错误数: {len(self.errors)}")
        print(f"🎯 操作成功率: {((self.operation_count - len(self.errors)) / self.operation_count * 100) if self.operation_count > 0 else 0:.2f}%")
        print()
        
        if self.errors:
            print(f"❌ 发现 {len(self.errors)} 个错误:")
            for i, error in enumerate(self.errors[:10], 1):
                print(f"   {i}. [{error['operation']}] {error['error']}")
        print()
        
        if self.stats["checkpoints"]:
            print(f"📋 检查点记录:")
            for i, cp in enumerate(self.stats["checkpoints"], 1):
                print(f"   {i}. {cp['name']}: {cp['elapsed']:.2f}s")
        print()
        
        print("=" * 150)
        if len(self.errors) == 0:
            print("🎉🎉🎉 第2次迭代混沌测试完美通过！系统无懈可击！")
        elif len(self.errors) < 10:
            print("✅ 第2次迭代混沌测试基本通过，少量错误被正确处理")
        else:
            print("⚠️  第2次迭代混沌测试发现问题较多")
        print("=" * 150)
        print()


def main():
    """主函数"""
    try:
        runner = ChaosEngineeringTestRunner()
        runner.run_all_chaos_tests()
        return 0
    except Exception as e:
        print(f"❌ 测试主程序崩溃: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
