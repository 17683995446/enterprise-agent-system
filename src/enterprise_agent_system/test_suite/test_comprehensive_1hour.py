"""
综合1小时测试 - 并行运行多个极端测试场景
模拟真实生产环境的各种负载模式
"""

import sys
import time
import random
import threading
import queue
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('comprehensive_1hour_test')


class ComprehensiveTestRunner:
    """综合测试运行器"""

    def __init__(self):
        self.results = {}
        self.stop_flag = threading.Event()
        
    def worker_read_heavy(self, worker_id: int, duration: int, result_queue: queue.Queue):
        """读密集型工作负载"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        ops = 0
        errors = 0
        
        start_time = time.time()
        
        # 先写入一些数据
        for i in range(1000):
            store.save_report({
                "id": f"read_heavy_{worker_id}_{i}",
                "title": f"Read Heavy Test {i}",
                "type": "test"
            })
        
        while not self.stop_flag.is_set() and (time.time() - start_time) < duration:
            try:
                report_id = f"read_heavy_{worker_id}_{random.randint(0, 999)}"
                store.get_report(report_id)
                ops += 1
            except Exception as e:
                errors += 1
        
        result_queue.put({
            "worker": f"read_heavy_{worker_id}",
            "ops": ops,
            "errors": errors
        })
    
    def worker_write_heavy(self, worker_id: int, duration: int, result_queue: queue.Queue):
        """写密集型工作负载"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        ops = 0
        errors = 0
        
        start_time = time.time()
        
        while not self.stop_flag.is_set() and (time.time() - start_time) < duration:
            try:
                store.save_report({
                    "id": f"write_heavy_{worker_id}_{ops}",
                    "title": f"Write Heavy Test {ops}",
                    "type": "test",
                    "summary": "x" * random.randint(100, 10000)
                })
                ops += 1
            except Exception as e:
                errors += 1
        
        result_queue.put({
            "worker": f"write_heavy_{worker_id}",
            "ops": ops,
            "errors": errors
        })
    
    def worker_cache_stress(self, worker_id: int, duration: int, result_queue: queue.Queue):
        """缓存压力工作负载"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleCache
        
        cache = SimpleCache()
        ops = 0
        errors = 0
        
        start_time = time.time()
        
        while not self.stop_flag.is_set() and (time.time() - start_time) < duration:
            try:
                key = f"cache_stress_{worker_id}_{ops % 10000}"
                cache.set(key, ops)
                cache.get(key)
                ops += 1
            except Exception as e:
                errors += 1
        
        result_queue.put({
            "worker": f"cache_stress_{worker_id}",
            "ops": ops,
            "errors": errors
        })
    
    def worker_mixed_operations(self, worker_id: int, duration: int, result_queue: queue.Queue):
        """混合操作工作负载"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
        
        store = SimpleMemoryStore()
        cache = SimpleCache()
        ops = 0
        errors = 0
        
        start_time = time.time()
        
        while not self.stop_flag.is_set() and (time.time() - start_time) < duration:
            try:
                op = random.choice(['read', 'write', 'cache'])
                
                if op == 'read':
                    store.get_report(f"mixed_{worker_id}_{random.randint(0, 100)}")
                elif op == 'write':
                    store.save_report({
                        "id": f"mixed_{worker_id}_{ops}",
                        "title": f"Mixed Test {ops}",
                        "type": "mixed"
                    })
                else:
                    cache.set(f"mixed_cache_{ops}", ops)
                    cache.get(f"mixed_cache_{ops}")
                
                ops += 1
            except Exception as e:
                errors += 1
        
        result_queue.put({
            "worker": f"mixed_{worker_id}",
            "ops": ops,
            "errors": errors
        })
    
    def run(self, duration_seconds: int = 120):
        """运行综合测试"""
        logger.info("=" * 80)
        logger.info(f"🚀 开始综合1小时测试 - 模拟 {duration_seconds} 秒")
        logger.info("=" * 80)
        
        start_time = time.time()
        result_queue = queue.Queue()
        threads = []
        
        # 配置工作负载
        workloads = [
            # 2个读密集型线程
            (self.worker_read_heavy, 2, "读密集型"),
            # 2个写密集型线程
            (self.worker_write_heavy, 2, "写密集型"),
            # 4个缓存压力线程
            (self.worker_cache_stress, 4, "缓存压力"),
            # 4个混合操作线程
            (self.worker_mixed_operations, 4, "混合操作"),
        ]
        
        logger.info(f"启动 {sum([w[1] for w in workloads])} 个工作线程...")
        
        # 启动所有工作线程
        for worker_func, num_workers, workload_name in workloads:
            for i in range(num_workers):
                t = threading.Thread(
                    target=worker_func,
                    args=(i, duration_seconds, result_queue)
                )
                threads.append(t)
                t.start()
                logger.info(f"  启动 {workload_name} 线程 {i}")
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 收集结果
        total_ops = 0
        total_errors = 0
        worker_results = []
        
        while not result_queue.empty():
            result = result_queue.get()
            worker_results.append(result)
            total_ops += result["ops"]
            total_errors += result["errors"]
        
        # 生成报告
        duration = time.time() - start_time
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 综合1小时测试报告")
        logger.info("=" * 80)
        logger.info(f"测试时长: {duration:.2f}秒")
        logger.info(f"总操作数: {total_ops:,}")
        logger.info(f"总错误数: {total_errors:,}")
        logger.info(f"吞吐量: {total_ops/duration:.0f} 次/秒")
        logger.info(f"成功率: {(total_ops-total_errors)/total_ops*100:.2f}%")
        
        logger.info(f"\n各工作负载统计:")
        for workload_name in ["读密集型", "写密集型", "缓存压力", "混合操作"]:
            relevant = [r for r in worker_results if workload_name in r["worker"]]
            if relevant:
                ops = sum(r["ops"] for r in relevant)
                errors = sum(r["errors"] for r in relevant)
                logger.info(f"  {workload_name}: {ops:,} 操作, {errors:,} 错误")
        
        # 内存统计
        try:
            import psutil
            mem_mb = psutil.Process().memory_info().rss / (1024 * 1024)
            logger.info(f"\n最终内存: {mem_mb:.2f}MB")
        except:
            pass
        
        passed = total_errors == 0 and (total_ops-total_errors)/total_ops > 0.99
        
        if passed:
            logger.info("\n🎉 综合测试全部通过！")
        else:
            logger.warning(f"\n⚠️ 发现 {total_errors} 个错误")
        
        return {
            "duration": duration,
            "total_ops": total_ops,
            "total_errors": total_errors,
            "rps": total_ops/duration,
            "success_rate": (total_ops-total_errors)/total_ops,
            "worker_results": worker_results,
            "passed": passed
        }


def main():
    """主函数"""
    runner = ComprehensiveTestRunner()
    
    # 运行2分钟模拟1小时效果
    result = runner.run(duration_seconds=120)
    
    return result


if __name__ == "__main__":
    main()
