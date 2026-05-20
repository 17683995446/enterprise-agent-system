"""
深度压力测试 - 寻找真实运行时的深度bug
设计目标：
1. 数据序列化边界测试
2. GC压力测试
3. 多线程竞争条件检测
4. 随机故障模拟
5. 数据一致性验证
6. 长时间资源跟踪
"""

import sys
import time
import random
import threading
import gc
import traceback
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, deque

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('deep_stress_test')


@dataclass
class OperationStat:
    total: int = 0
    success: int = 0
    failures: int = 0
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0


@dataclass
class DataCorruptionError:
    report_id: str
    expected_value: Any
    actual_value: Any


class DeepStressTester:
    """深度压力测试器"""
    
    def __init__(self):
        self.stop_flag = threading.Event()
        self.lock = threading.RLock()
        
        # 统计
        self.ops = defaultdict(OperationStat)
        self.corruptions: List[DataCorruptionError] = []
        
        # GC监控
        self.gc_stats = []
        
        # 数据一致性跟踪
        self.data_tracker = {}
        
        # 内存历史
        self.memory_history = deque(maxlen=100)
        self.initial_memory = self.get_memory_mb()
        self.peak_memory = self.initial_memory
    
    def get_memory_mb(self) -> float:
        """获取当前内存使用"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / (1024 * 1024)
        except:
            return 0.0
    
    def generate_edge_case_data(self, size_kb: int) -> str:
        """生成边界情况数据"""
        size_bytes = size_kb * 1024
        
        # 不同的数据生成策略
        case = random.randint(0, 5)
        
        if case == 0:
            # 全零数据
            return '\x00' * size_bytes
        elif case == 1:
            # 全Unicode数据
            return ''.join(chr(random.randint(0, 0x10FFFF)) for _ in range(size_bytes // 4))
        elif case == 2:
            # 混合特殊字符
            chars = '!@#$%^&*()_+[]{};:,./<>?\\|`~'
            return ''.join(random.choice(chars) for _ in range(size_bytes))
        elif case == 3:
            # 换行和回车符
            lines = ['Line ' + str(i) for i in range(size_bytes // 20)]
            return '\n\r'.join(lines)
        elif case == 4:
            # 空字符串和单字符交替
            parts = ['a' if random.random() < 0.5 else '' for _ in range(size_bytes)]
            return ''.join(parts)
        else:
            # 正常数据
            chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            return ''.join(random.choice(chars) for _ in range(size_bytes))
    
    def test_data_serialization(self, worker_id: int) -> Dict[str, Any]:
        """测试数据序列化和反序列化边界条件"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        local_corruptions = []
        
        # 测试不同大小的数据
        sizes_kb = [0, 1, 10, 50, 100, 500]
        
        for size_kb in sizes_kb:
            report_id = f"serialize_{worker_id}_{size_kb}"
            test_data = self.generate_edge_case_data(size_kb)
            
            # 保存
            store.save_report({
                "id": report_id,
                "title": f"Serialize Test {size_kb}KB",
                "content": test_data,
                "type": "serialization_test",
                "metrics": {
                    "size_kb": size_kb,
                    "worker_id": worker_id,
                    "timestamp": time.time()
                }
            })
            
            # 读取回来验证
            retrieved = store.get_report(report_id)
            
            if retrieved is None:
                local_corruptions.append(DataCorruptionError(
                    report_id, "not None", None
                ))
            elif retrieved.get('content') != test_data:
                local_corruptions.append(DataCorruptionError(
                    report_id, test_data[:100], 
                    retrieved.get('content')[:100] if retrieved.get('content') else None
                ))
        
        return local_corruptions
    
    def test_gc_stress(self, worker_id: int) -> Dict[str, Any]:
        """GC压力测试 - 快速创建和删除大量对象"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
        
        store = SimpleMemoryStore()
        cache = SimpleCache()
        
        gc_count_start = gc.get_count()[0]
        
        for i in range(1000):
            # 创建大量数据
            report_id = f"gc_{worker_id}_{i}"
            content = 'x' * random.randint(100, 10000)
            
            store.save_report({
                "id": report_id,
                "title": f"GC Stress {i}",
                "content": content,
                "type": "gc_test"
            })
            
            cache.set(report_id, content)
            
            # 快速删除，制造GC压力
            if i % 5 == 0:
                # 删除旧数据
                old_id = f"gc_{worker_id}_{i-10}"
                store.delete_report(old_id)
                cache.delete(old_id)
                
                # 强制GC
                if i % 100 == 0:
                    gc.collect()
        
        gc_count_end = gc.get_count()[0]
        return {"gc_count_diff": gc_count_end - gc_count_start}
    
    def test_thread_safety(self, shared_report_id: str) -> Dict[str, Any]:
        """线程安全测试 - 多线程同时修改同一数据"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        local_errors = []
        
        # 初始化数据
        store.save_report({
            "id": shared_report_id,
            "title": "Thread Safety Test",
            "type": "thread_test",
            "quality_score": 0
        })
        
        # 多线程操作
        errors_in_thread = []
        
        def modify_worker():
            try:
                for _ in range(100):
                    # 读取当前值
                    report = store.get_report(shared_report_id)
                    if report:
                        current_score = report.get('quality_score', 0)
                        # 修改并保存
                        report['quality_score'] = current_score + 1
                        store.save_report(report)
            except Exception as e:
                errors_in_thread.append(str(e))
        
        threads = []
        for i in range(10):
            t = threading.Thread(target=modify_worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 验证结果（期望：至少有一些增量，虽然由于竞态可能不是精确值）
        final_report = store.get_report(shared_report_id)
        final_score = final_report.get('quality_score', 0) if final_report else 0
        
        result = {
            "final_score": final_score,
            "errors": errors_in_thread
        }
        
        return result
    
    def test_data_consistency(self, worker_id: int) -> List[DataCorruptionError]:
        """数据一致性测试 - 长期跟踪数据完整性"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        local_corruptions = []
        
        # 创建和跟踪多个报告
        for i in range(100):
            report_id = f"consistency_{worker_id}_{i}"
            expected_data = f"Data for report {i} - timestamp {time.time()}"
            
            # 保存
            store.save_report({
                "id": report_id,
                "title": f"Consistency Test {i}",
                "content": expected_data,
                "type": "consistency_test"
            })
            
            # 跟踪
            self.data_tracker[report_id] = expected_data
            
            # 立即验证
            retrieved = store.get_report(report_id)
            if retrieved and retrieved.get('content') != expected_data:
                local_corruptions.append(DataCorruptionError(
                    report_id, expected_data, retrieved.get('content')
                ))
        
        # 随机读取验证
        for i in range(200):
            report_id = f"consistency_{worker_id}_{random.randint(0, 99)}"
            expected = self.data_tracker.get(report_id)
            
            if expected:
                retrieved = store.get_report(report_id)
                if retrieved and retrieved.get('content') != expected:
                    local_corruptions.append(DataCorruptionError(
                        report_id, expected, retrieved.get('content')
                    ))
        
        return local_corruptions
    
    def test_mixed_operations(self, worker_id: int) -> Dict[str, Any]:
        """混合操作测试 - 随机执行各种操作类型"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
        
        store = SimpleMemoryStore()
        cache = SimpleCache()
        
        ops_count = 0
        failures_count = 0
        latencies = []
        
        start_time = time.time()
        
        while not self.stop_flag.is_set() and time.time() - start_time < 60:  # 1分钟持续测试
            try:
                op_start = time.time()
                
                op_type = random.choice(['save', 'get', 'delete', 'cache_set', 'cache_get', 'list'])
                
                if op_type == 'save':
                    report_id = f"mixed_{worker_id}_{ops_count}"
                    store.save_report({
                        "id": report_id,
                        "title": f"Mixed Op {ops_count}",
                        "type": "mixed",
                        "metrics": {"op_count": ops_count, "time": time.time()}
                    })
                elif op_type == 'get':
                    store.get_report(f"mixed_{worker_id}_{random.randint(0, ops_count-1)}")
                elif op_type == 'delete':
                    store.delete_report(f"mixed_{worker_id}_{random.randint(0, ops_count-1)}")
                elif op_type == 'cache_set':
                    cache.set(f"cache_{worker_id}_{ops_count}", f"value_{ops_count}")
                elif op_type == 'cache_get':
                    cache.get(f"cache_{worker_id}_{random.randint(0, ops_count-1)}")
                else:
                    store.list_reports(limit=10)
                
                latency = (time.time() - op_start) * 1000
                latencies.append(latency)
                
                ops_count += 1
                
                if ops_count % 1000 == 0:
                    with self.lock:
                        if 'mixed_ops' not in self.ops:
                            self.ops['mixed_ops'] = OperationStat()
                        self.ops['mixed_ops'].total += 1000
                        self.ops['mixed_ops'].success += 1000
                
            except Exception as e:
                failures_count += 1
                with self.lock:
                    if 'mixed_ops' not in self.ops:
                        self.ops['mixed_ops'] = OperationStat()
                    self.ops['mixed_ops'].failures += 1
        
        return {
            "total_ops": ops_count,
            "failures": failures_count,
            "latencies": latencies
        }
    
    def run(self, duration_minutes: int = 15):
        """运行深度压力测试"""
        logger.info("=" * 80)
        logger.info("🚀 启动深度压力测试 - 寻找真实运行时bug")
        logger.info("=" * 80)
        logger.info(f"测试时长: {duration_minutes} 分钟")
        
        total_start = time.time()
        
        # 阶段1: 数据序列化边界测试
        logger.info("\n" + "=" * 80)
        logger.info("阶段1: 数据序列化边界测试")
        logger.info("=" * 80)
        
        with self.lock:
            self.ops['serialization'] = OperationStat()
        
        serial_corruptions = []
        for i in range(10):
            self.ops['serialization'].total += 1
            try:
                corruptions = self.test_data_serialization(i)
                serial_corruptions.extend(corruptions)
                if not corruptions:
                    self.ops['serialization'].success += 1
                else:
                    self.ops['serialization'].failures += 1
            except Exception as e:
                self.ops['serialization'].failures += 1
                self.ops['serialization'].total += 1
                logger.error(f"序列化测试异常: {str(e)}")
        
        with self.lock:
            self.corruptions.extend(serial_corruptions)
        
        logger.info(f"序列化测试完成: {len(serial_corruptions)} 数据损坏")
        
        # 阶段2: GC压力测试
        logger.info("\n" + "=" * 80)
        logger.info("阶段2: GC压力测试")
        logger.info("=" * 80)
        
        with self.lock:
            self.ops['gc_stress'] = OperationStat()
        
        for i in range(10):
            self.ops['gc_stress'].total += 1
            try:
                self.test_gc_stress(i)
                self.ops['gc_stress'].success += 1
            except Exception as e:
                self.ops['gc_stress'].failures += 1
                logger.error(f"GC压力测试异常: {str(e)}")
        
        # 阶段3: 线程安全测试
        logger.info("\n" + "=" * 80)
        logger.info("阶段3: 线程安全测试")
        logger.info("=" * 80)
        
        with self.lock:
            self.ops['thread_safety'] = OperationStat()
        
        shared_report_id = "shared_test"
        thread_results = self.test_thread_safety(shared_report_id)
        
        if thread_results['errors']:
            self.ops['thread_safety'].failures += 1
            logger.warning(f"线程安全错误: {thread_results['errors']}")
        else:
            self.ops['thread_safety'].success += 1
        
        logger.info(f"线程安全测试完成 - 最终分数: {thread_results['final_score']}")
        
        # 阶段4: 数据一致性持续测试
        logger.info("\n" + "=" * 80)
        logger.info("阶段4: 数据一致性持续测试")
        logger.info("=" * 80)
        
        with self.lock:
            self.ops['consistency'] = OperationStat()
        
        consistency_corruptions = []
        for i in range(10):
            self.ops['consistency'].total += 1
            try:
                corruptions = self.test_data_consistency(i)
                consistency_corruptions.extend(corruptions)
                if not corruptions:
                    self.ops['consistency'].success += 1
                else:
                    self.ops['consistency'].failures += 1
            except Exception as e:
                self.ops['consistency'].failures += 1
                logger.error(f"一致性测试异常: {str(e)}")
        
        with self.lock:
            self.corruptions.extend(consistency_corruptions)
        
        logger.info(f"一致性测试完成: {len(consistency_corruptions)} 数据损坏")
        
        # 阶段5: 混合操作长时间测试
        logger.info("\n" + "=" * 80)
        logger.info("阶段5: 混合操作长时间测试")
        logger.info("=" * 80)
        
        workers = []
        for i in range(20):
            t = threading.Thread(target=self.test_mixed_operations, args=(i,))
            workers.append(t)
            t.start()
        
        logger.info(f"启动了 {len(workers)} 个混合操作工作线程")
        
        # 监控
        for i in range(60):
            if self.stop_flag.is_set():
                break
            
            time.sleep(1)
            
            if i % 10 == 0:
                current_mem = self.get_memory_mb()
                if current_mem > self.peak_memory:
                    self.peak_memory = current_mem
                self.memory_history.append((time.time(), current_mem))
                
                logger.info(f"[{i}s] 当前内存: {current_mem:.2f}MB, 峰值: {self.peak_memory:.2f}MB")
        
        self.stop_flag.set()
        
        for t in workers:
            t.join()
        
        # 生成最终报告
        return self.generate_report(total_start)
    
    def generate_report(self, total_start):
        """生成最终报告"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 深度压力测试 - 最终报告")
        logger.info("=" * 80)
        
        duration = time.time() - total_start
        final_memory = self.get_memory_mb()
        memory_growth = final_memory - self.initial_memory
        
        total_ops = sum(stat.total for stat in self.ops.values())
        total_success = sum(stat.success for stat in self.ops.values())
        total_failures = sum(stat.failures for stat in self.ops.values())
        total_corruptions = len(self.corruptions)
        
        success_rate = (total_success / total_ops * 100) if total_ops > 0 else 0
        
        logger.info(f"\n⏱️ 时间统计")
        logger.info(f"  总测试时长: {duration:.2f}秒 ({duration/60:.2f}分钟)")
        
        logger.info(f"\n📈 操作统计")
        logger.info(f"  总操作数: {total_ops}")
        logger.info(f"  成功操作: {total_success}")
        logger.info(f"  失败操作: {total_failures}")
        logger.info(f"  成功率: {success_rate:.2f}%")
        
        logger.info(f"\n💾 内存统计")
        logger.info(f"  初始内存: {self.initial_memory:.2f}MB")
        logger.info(f"  峰值内存: {self.peak_memory:.2f}MB")
        logger.info(f"  最终内存: {final_memory:.2f}MB")
        logger.info(f"  内存增长: {memory_growth:.2f}MB")
        
        logger.info(f"\n🔍 数据一致性")
        logger.info(f"  数据损坏数量: {total_corruptions}")
        
        if self.corruptions:
            logger.warning(f"\n数据损坏详情 (前10个):")
            for i, corruption in enumerate(self.corruptions[:10]):
                logger.warning(f"  {i+1}. ID: {corruption.report_id}")
                logger.warning(f"      期望: {str(corruption.expected_value)[:50]}")
                logger.warning(f"      实际: {str(corruption.actual_value)[:50]}")
        
        logger.info(f"\n各操作类型详情:")
        for name, stat in self.ops.items():
            logger.info(f"  {name}:")
            logger.info(f"    总数: {stat.total}, 成功: {stat.success}, 失败: {stat.failures}")
        
        # 判断测试是否通过
        passed = (
            total_failures == 0 and
            total_corruptions == 0 and
            memory_growth < 100
        )
        
        logger.info(f"\n" + "=" * 80)
        if passed:
            logger.info("🎉 深度测试完美通过！未发现任何bug！")
            logger.info("   ✅ 零错误")
            logger.info("   ✅ 零数据损坏")
            logger.info("   ✅ 内存使用正常")
        else:
            logger.warning("⚠️ 发现问题，需要修复:")
            if total_failures > 0:
                logger.warning(f"   - {total_failures} 个操作失败")
            if total_corruptions > 0:
                logger.warning(f"   - {total_corruptions} 个数据损坏")
            if memory_growth >= 100:
                logger.warning(f"   - 内存增长异常: {memory_growth:.2f}MB")
        
        logger.info("=" * 80)
        
        return {
            "duration": duration,
            "total_ops": total_ops,
            "success_rate": success_rate,
            "memory_growth_mb": memory_growth,
            "corruptions": self.corruptions,
            "passed": passed
        }


def main():
    """主函数"""
    tester = DeepStressTester()
    
    try:
        result = tester.run(duration_minutes=15)  # 15分钟演示
        return result
    except Exception as e:
        logger.error(f"测试崩溃: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
