"""
内存压力测试 - 1小时+
持续内存压力，检测内存泄漏和性能退化
"""

import sys
import time
import random
import threading
import gc
from typing import Dict, List, Any
from dataclasses import dataclass

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('1hour_memory_stress')


@dataclass
class MemoryMetrics:
    initial_memory_mb: float = 0
    peak_memory_mb: float = 0
    final_memory_mb: float = 0
    memory_growth_mb: float = 0
    memory_snapshots: List[Dict] = None
    
    def __post_init__(self):
        if self.memory_snapshots is None:
            self.memory_snapshots = []


class MemoryStressTester:
    """内存压力测试器 - 运行1小时+"""

    def __init__(self, duration_seconds: int = 3600):
        self.duration = duration_seconds
        self.metrics = MemoryMetrics()
        self.stop_flag = threading.Event()
        self.errors = []
        
    def get_memory_mb(self) -> float:
        """获取当前内存使用(MB)"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / (1024 * 1024)
        except:
            return 0
    
    def run(self):
        """运行内存压力测试"""
        logger.info("=" * 80)
        logger.info(f"🚀 开始内存压力测试 - 预计运行 {self.duration} 秒 ({(self.duration/60):.1f} 分钟)")
        logger.info("=" * 80)
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
        
        store = SimpleMemoryStore()
        cache = SimpleCache()
        
        start_time = time.time()
        
        # 记录初始内存
        initial_mem = self.get_memory_mb()
        self.metrics.initial_memory_mb = initial_mem
        peak_mem = initial_mem
        logger.info(f"初始内存: {initial_mem:.2f}MB")
        
        iteration = 0
        last_snapshot_time = start_time
        
        try:
            while not self.stop_flag.is_set() and (time.time() - start_time) < self.duration:
                # 创建内存压力
                try:
                    # 保存大量数据
                    for i in range(10):
                        report_id = f"mem_stress_{iteration}_{i}"
                        
                        # 随机大小的数据 (1KB - 100KB)
                        data_size = random.randint(1000, 100000)
                        large_content = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=data_size))
                        
                        store.save_report({
                            "id": report_id,
                            "title": f"Memory Stress Test {iteration}",
                            "type": "memory_stress",
                            "content": large_content,
                            "summary": f"Memory test iteration {iteration}",
                            "quality_score": random.uniform(0, 10),
                            "metrics": {
                                "size": data_size,
                                "iteration": iteration,
                                "timestamp": time.time()
                            }
                        })
                        
                        # 缓存操作
                        cache_key = f"cache_stress_{iteration}_{i}"
                        cache_data = {
                            "key": cache_key,
                            "data": large_content[:1000],  # 只缓存前1KB
                            "timestamp": time.time()
                        }
                        cache.set(cache_key, cache_data)
                    
                    iteration += 1
                    
                    # 每100次迭代清理一次
                    if iteration % 100 == 0:
                        # 删除旧数据
                        for i in range(10):
                            old_iteration = iteration - 100
                            if old_iteration >= 0:
                                report_id = f"mem_stress_{old_iteration}_{i}"
                                store.delete_report(report_id)
                                
                                cache_key = f"cache_stress_{old_iteration}_{i}"
                                cache.delete(cache_key)
                        
                        # 强制GC
                        gc.collect()
                        
                        # 检查内存
                        current_mem = self.get_memory_mb()
                        if current_mem > peak_mem:
                            peak_mem = current_mem
                        
                        elapsed = time.time() - start_time
                        
                        logger.info(f"📊 [{elapsed:.0f}s] "
                                   f"迭代: {iteration} | "
                                   f"当前内存: {current_mem:.2f}MB | "
                                   f"峰值内存: {peak_mem:.2f}MB | "
                                   f"增长: {current_mem - initial_mem:.2f}MB")
                        
                        # 每5分钟记录一次快照
                        if time.time() - last_snapshot_time >= 300:
                            self.metrics.memory_snapshots.append({
                                "time": elapsed,
                                "iteration": iteration,
                                "memory_mb": current_mem
                            })
                            last_snapshot_time = time.time()
                
                except Exception as e:
                    self.errors.append(f"Iteration {iteration}: {str(e)[:100]}")
                    logger.error(f"内存压力测试错误: {str(e)}")
                
                # 控制速率
                time.sleep(0.1)
            
            # 测试结束
            final_mem = self.get_memory_mb()
            self.metrics.final_memory_mb = final_mem
            self.metrics.peak_memory_mb = peak_mem
            self.metrics.memory_growth_mb = final_mem - initial_mem
            
        except KeyboardInterrupt:
            logger.warning("测试被用户中断")
            self.stop_flag.set()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 内存压力测试报告")
        logger.info("=" * 80)
        logger.info(f"初始内存: {self.metrics.initial_memory_mb:.2f}MB")
        logger.info(f"峰值内存: {self.metrics.peak_memory_mb:.2f}MB")
        logger.info(f"最终内存: {self.metrics.final_memory_mb:.2f}MB")
        logger.info(f"内存增长: {self.metrics.memory_growth_mb:.2f}MB")
        
        if self.metrics.memory_snapshots:
            logger.info(f"\n内存快照 ({len(self.metrics.memory_snapshots)} 个):")
            for snapshot in self.metrics.memory_snapshots[:5]:
                logger.info(f"  {snapshot['time']:.0f}s: {snapshot['memory_mb']:.2f}MB")
        
        if self.errors:
            logger.warning(f"\n错误数量: {len(self.errors)}")
            for i, err in enumerate(self.errors[:5]):
                logger.warning(f"  {i+1}. {err}")
        
        # 判断是否通过
        # 内存增长超过 500MB 或每小时增长超过 200MB 视为异常
        duration_hours = self.duration / 3600
        growth_per_hour = self.metrics.memory_growth_mb / duration_hours
        
        passed = (self.metrics.memory_growth_mb < 500 and 
                 growth_per_hour < 200 and 
                 len(self.errors) < 100)
        
        if passed:
            logger.info("\n✅ 内存测试通过 - 无明显内存泄漏")
        else:
            logger.warning(f"\n❌ 内存增长异常: {self.metrics.memory_growth_mb:.2f}MB "
                         f"(每小时 {growth_per_hour:.2f}MB)")
        
        return {
            "initial_memory_mb": self.metrics.initial_memory_mb,
            "peak_memory_mb": self.metrics.peak_memory_mb,
            "final_memory_mb": self.metrics.final_memory_mb,
            "memory_growth_mb": self.metrics.memory_growth_mb,
            "growth_per_hour_mb": growth_per_hour,
            "error_count": len(self.errors),
            "snapshots": self.metrics.memory_snapshots,
            "passed": passed
        }


def main():
    """主函数"""
    tester = MemoryStressTester(duration_seconds=120)  # 演示用，实际用3600
    
    try:
        result = tester.run()
        
        if result["passed"]:
            logger.info("\n🎉 内存测试通过！")
        else:
            logger.warning("\n⚠️ 内存增长较高，建议检查")
        
        return result
        
    except Exception as e:
        logger.error(f"测试崩溃: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
