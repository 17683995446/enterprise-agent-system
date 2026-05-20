"""
终极生产环境模拟测试 - 2小时+
模拟真实生产环境的所有复杂场景
包括：故障注入、资源压力、边界条件、并发风暴等
"""

import sys
import time
import random
import threading
import gc
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import deque

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('ultimate_production_test')


@dataclass
class Stage:
    name: str
    duration: float
    threads: int
    ops_per_sec_target: float
    data_size_range: tuple
    special_behavior: Optional[str] = None


class UltimateProductionSimulator:
    """终极生产环境模拟器"""
    
    def __init__(self, total_duration: int = 7200):
        self.total_duration = total_duration
        self.stop_flag = threading.Event()
        self.lock = threading.RLock()
        
        # 统计
        self.total_ops = 0
        self.success_ops = 0
        self.failed_ops = 0
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # 内存监控
        self.memory_snapshots: List[Dict] = []
        self.initial_memory = 0
        self.peak_memory = 0
        
        # 阶段配置（完整的2小时测试）
        self.stages = [
            # 第一阶段：逐步升温 (5分钟)
            Stage("Stage 1: Ramp Up", 300, 4, 200, (100, 500)),
            
            # 第二阶段：正常负载 (15分钟)
            Stage("Stage 2: Normal Load", 900, 8, 500, (500, 2000)),
            
            # 第三阶段：负载上升 (15分钟)
            Stage("Stage 3: Load Increase", 900, 16, 1000, (1000, 5000)),
            
            # 第四阶段：峰值负载 (20分钟)
            Stage("Stage 4: Peak Load", 1200, 32, 2000, (2000, 10000), "memory_intensive"),
            
            # 第五阶段：突发流量 (10分钟)
            Stage("Stage 5: Traffic Burst", 600, 64, 5000, (100, 2000), "burst_mode"),
            
            # 第六阶段：资源压力 (15分钟)
            Stage("Stage 6: Resource Stress", 900, 16, 1500, (5000, 50000), "disk_intensive"),
            
            # 第七阶段：混沌模式 (15分钟)
            Stage("Stage 7: Chaos Mode", 900, 24, 2000, (100, 5000), "chaos_injection"),
            
            # 第八阶段：恢复测试 (10分钟)
            Stage("Stage 8: Recovery Test", 600, 8, 1000, (500, 2000)),
            
            # 第九阶段：最终压测 (15分钟)
            Stage("Stage 9: Final Stress", 900, 48, 3000, (1000, 8000)),
            
            # 第十阶段：冷却 (5分钟)
            Stage("Stage 10: Cooldown", 300, 4, 200, (100, 500)),
        ]
        
    def get_memory_mb(self) -> float:
        """获取内存使用MB"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / (1024 * 1024)
        except:
            return 0
    
    def generate_data(self, min_size: int, max_size: int) -> str:
        """生成随机数据"""
        size = random.randint(min_size, max_size)
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=size))
    
    def chaos_injection(self) -> bool:
        """混沌注入：模拟各种故障场景"""
        roll = random.random()
        
        if roll < 0.05:  # 5% 概率：超长ID
            return True
        elif roll < 0.10:  # 5% 概率：空数据
            return True
        elif roll < 0.15:  # 5% 概率：极端数值
            return True
        elif roll < 0.20:  # 5% 概率：删除不存在的数据
            return True
        
        return False
    
    def worker(self, stage: Stage, worker_id: int):
        """工作线程"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
        
        store = SimpleMemoryStore()
        cache = SimpleCache()
        
        stage_start = time.time()
        stage_end = stage_start + stage.duration
        
        local_ops = 0
        local_errors = 0
        
        # 预填充一些数据
        for i in range(100):
            store.save_report({
                "id": f"worker_{worker_id}_seed_{i}",
                "title": f"Seed {i}",
                "type": "seed",
                "summary": "Initial data"
            })
        
        while not self.stop_flag.is_set() and time.time() < stage_end:
            try:
                report_id = f"ultimate_{worker_id}_{local_ops}"
                
                # 混沌注入
                inject_chaos = stage.special_behavior == "chaos_injection" and self.chaos_injection()
                
                if inject_chaos:
                    # 混沌场景
                    chaos_type = random.choice(['long_id', 'empty', 'extreme', 'nonexist'])
                    
                    if chaos_type == 'long_id':
                        # 超长ID - 应该被接受或优雅处理
                        store.save_report({
                            "id": 'x' * 1000,
                            "title": "Long ID Test",
                            "type": "chaos"
                        })
                    elif chaos_type == 'empty':
                        # 空数据
                        store.save_report({
                            "id": report_id,
                            "title": None,
                            "type": "",
                            "quality_score": None
                        })
                    elif chaos_type == 'extreme':
                        # 极端数值
                        store.save_report({
                            "id": report_id,
                            "title": "Extreme Test",
                            "quality_score": 1e308 if random.random() < 0.5 else -1e308,
                            "type": "chaos"
                        })
                    else:  # nonexist
                        # 删除不存在的数据 - 应该无害
                        store.delete_report("definitely_does_not_exist_123456789")
                else:
                    # 正常操作
                    op_choice = random.random()
                    
                    if op_choice < 0.3:  # 30% 读操作
                        store.get_report(f"ultimate_{worker_id}_{random.randint(0, max(0, local_ops-50))}")
                    elif op_choice < 0.4:  # 10% 缓存操作
                        cache.set(report_id, local_ops)
                        cache.get(report_id)
                    else:  # 60% 写操作
                        min_size, max_size = stage.data_size_range
                        
                        # 特殊行为：内存密集型
                        if stage.special_behavior == "memory_intensive":
                            # 存储更多数据在内存中
                            large_data = self.generate_data(min_size, max_size * 2)
                        else:
                            large_data = self.generate_data(min_size, max_size)
                        
                        store.save_report({
                            "id": report_id,
                            "title": f"Production Test {report_id}",
                            "type": stage.name.split(':')[1].strip() if ':' in stage.name else stage.name,
                            "content": large_data,
                            "summary": f"Stage: {stage.name}, Worker: {worker_id}",
                            "quality_score": random.uniform(0, 10),
                            "metrics": {
                                "worker_id": worker_id,
                                "stage": stage.name,
                                "timestamp": time.time(),
                                "size": len(large_data)
                            }
                        })
                
                local_ops += 1
                
                # 突发模式：尝试达到更高的TPS
                if stage.special_behavior == "burst_mode":
                    # 减少延迟以产生突发流量
                    time.sleep(random.uniform(0, 0.001))
                else:
                    # 正常延迟控制
                    time.sleep(max(0, 1.0 / stage.ops_per_sec_target - 0.001))
                    
            except Exception as e:
                local_errors += 1
                error_msg = f"W{worker_id} in {stage.name}: {str(e)[:80]}"
                
                with self.lock:
                    self.errors.append(error_msg)
                    if len(self.errors) > 100:
                        self.errors = self.errors[-50:]
        
        # 更新全局统计
        with self.lock:
            self.total_ops += local_ops
            self.success_ops += (local_ops - local_errors)
            self.failed_ops += local_errors
    
    def run(self):
        """运行终极测试"""
        logger.info("=" * 80)
        logger.info("🚀 启动终极生产环境模拟测试 - 2小时+")
        logger.info("=" * 80)
        
        total_start = time.time()
        self.initial_memory = self.get_memory_mb()
        self.peak_memory = self.initial_memory
        
        try:
            for stage_idx, stage in enumerate(self.stages):
                stage_name = stage.name
                
                logger.info(f"\n{'=' * 80}")
                logger.info(f"阶段 {stage_idx+1}/{len(self.stages)}: {stage_name}")
                logger.info(f"{'=' * 80}")
                logger.info(f"线程: {stage.threads}, 目标TPS: {stage.ops_per_sec_target}")
                logger.info(f"数据大小: {stage.data_size_range} bytes")
                if stage.special_behavior:
                    logger.info(f"特殊行为: {stage.special_behavior}")
                
                stage_start = time.time()
                stage_ops_start = self.total_ops
                
                # 启动工作线程
                threads = []
                for i in range(stage.threads):
                    t = threading.Thread(target=self.worker, args=(stage, i))
                    threads.append(t)
                    t.start()
                
                # 监控循环
                last_report = time.time()
                last_gc = time.time()
                
                while any(t.is_alive() for t in threads):
                    current_time = time.time()
                    
                    # 监控内存
                    current_mem = self.get_memory_mb()
                    if current_mem > self.peak_memory:
                        self.peak_memory = current_mem
                    
                    # 定期报告
                    if current_time - last_report >= 120:  # 每2分钟报告
                        elapsed = current_time - stage_start
                        stage_ops = self.total_ops - stage_ops_start
                        actual_tps = stage_ops / elapsed if elapsed > 0 else 0
                        
                        logger.info(f"[{stage_name}] "
                                   f"Elapsed: {elapsed/60:.1f}min, "
                                   f"Ops: {stage_ops:,}, "
                                   f"TPS: {actual_tps:.0f}, "
                                   f"Total Errors: {self.failed_ops}, "
                                   f"Memory: {current_mem:.1f}MB")
                        
                        last_report = current_time
                    
                    # 定期GC
                    if current_time - last_gc >= 180:  # 每3分钟GC
                        gc.collect()
                        last_gc = current_time
                    
                    time.sleep(5)
                
                # 等待线程结束
                for t in threads:
                    t.join()
                
                # 阶段总结
                stage_duration = time.time() - stage_start
                stage_ops = self.total_ops - stage_ops_start
                stage_tps = stage_ops / stage_duration if stage_duration > 0 else 0
                
                logger.info(f"✅ {stage_name} 完成: "
                           f"{stage_ops:,} ops @ {stage_tps:.0f} TPS")
                
                # 阶段间GC
                gc.collect()
        
        except KeyboardInterrupt:
            logger.warning("测试被用户中断")
            self.stop_flag.set()
        
        total_duration = time.time() - total_start
        
        return self._generate_final_report(total_duration)
    
    def _generate_final_report(self, total_duration: float) -> Dict[str, Any]:
        """生成最终报告"""
        final_memory = self.get_memory_mb()
        memory_growth = final_memory - self.initial_memory
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 终极生产环境模拟测试 - 最终报告")
        logger.info("=" * 80)
        
        logger.info(f"\n⏱️  时间统计:")
        logger.info(f"  总测试时长: {total_duration:.2f}秒 ({total_duration/60:.1f}分钟, {total_duration/3600:.2f}小时)")
        
        logger.info(f"\n📈 操作统计:")
        logger.info(f"  总操作数: {self.total_ops:,}")
        logger.info(f"  成功操作: {self.success_ops:,}")
        logger.info(f"  失败操作: {self.failed_ops:,}")
        
        if self.total_ops > 0:
            success_rate = self.success_ops / self.total_ops * 100
            avg_tps = self.total_ops / total_duration if total_duration > 0 else 0
            logger.info(f"  成功率: {success_rate:.2f}%")
            logger.info(f"  平均TPS: {avg_tps:.0f}")
        
        logger.info(f"\n💾 内存统计:")
        logger.info(f"  初始内存: {self.initial_memory:.2f}MB")
        logger.info(f"  峰值内存: {self.peak_memory:.2f}MB")
        logger.info(f"  最终内存: {final_memory:.2f}MB")
        logger.info(f"  内存增长: {memory_growth:.2f}MB")
        
        # 错误分析
        logger.info(f"\n❌ 错误分析:")
        if self.errors:
            error_types = {}
            for err in self.errors:
                # 提取错误类型
                err_key = err.split(':')[0] if ':' in err else err[:50]
                error_types[err_key] = error_types.get(err_key, 0) + 1
            
            logger.info(f"  总错误数: {len(self.errors)}")
            logger.info(f"  错误类型分布:")
            for err_type, count in sorted(error_types.items(), key=lambda x: -x[1])[:10]:
                logger.info(f"    - {err_type}: {count}次")
            
            logger.info(f"\n  错误详情 (前10条):")
            for i, err in enumerate(self.errors[:10]):
                logger.warning(f"    {i+1}. {err}")
        else:
            logger.info("  ✅ 没有错误！")
        
        # 判断测试是否通过
        passed = (
            self.failed_ops == 0 and
            memory_growth < 500 and  # 内存增长不超过500MB
            self.total_ops > 1000000  # 至少执行100万次操作
        )
        
        logger.info(f"\n{'=' * 80}")
        if passed:
            logger.info("🎉 测试完美通过！系统可以投入生产！")
            logger.info("   ✅ 零错误率")
            logger.info("   ✅ 内存稳定")
            logger.info("   ✅ 高吞吐量")
            logger.info("   ✅ 极端场景全部通过")
        else:
            logger.warning("⚠️  测试发现问题，需要检查:")
            if self.failed_ops > 0:
                logger.warning(f"   - 存在 {self.failed_ops} 个错误")
            if memory_growth >= 500:
                logger.warning(f"   - 内存增长过高: {memory_growth:.2f}MB")
            if self.total_ops < 1000000:
                logger.warning(f"   - 操作数不足: {self.total_ops:,} < 1,000,000")
        
        logger.info("=" * 80)
        
        return {
            "duration_seconds": total_duration,
            "total_ops": self.total_ops,
            "success_ops": self.success_ops,
            "failed_ops": self.failed_ops,
            "success_rate": self.success_ops / self.total_ops if self.total_ops > 0 else 0,
            "avg_tps": self.total_ops / total_duration if total_duration > 0 else 0,
            "initial_memory_mb": self.initial_memory,
            "peak_memory_mb": self.peak_memory,
            "final_memory_mb": final_memory,
            "memory_growth_mb": memory_growth,
            "error_count": len(self.errors),
            "errors": self.errors[:20],  # 返回前20个错误
            "passed": passed
        }


def main():
    """主函数"""
    # 完整测试需要2小时，这里设为10分钟演示版
    # 实际生产环境测试应设为 7200 秒 (2小时)
    tester = UltimateProductionSimulator(total_duration=600)  # 10分钟演示
    
    try:
        results = tester.run()
        
        # 输出Python格式的结果
        print("\n" + "=" * 80)
        print("Python 结果对象:")
        print("=" * 80)
        for key, value in results.items():
            if key == 'errors':
                print(f"{key}: {len(value)} errors")
            elif isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
        
        return results
        
    except Exception as e:
        logger.error(f"测试崩溃: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
