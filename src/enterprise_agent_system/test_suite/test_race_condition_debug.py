"""
并发竞态条件深入诊断
找出为什么最终计数是0而不是1000
"""

import sys
import time
import threading
from collections import defaultdict

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('race_condition_debug')


def diagnose_race_condition():
    """诊断竞态条件"""
    
    logger.info("=" * 80)
    logger.info("深入诊断并发竞态条件")
    logger.info("=" * 80)
    
    store = SimpleMemoryStore()
    
    # 创建共享数据
    shared_id = "diagnose_race"
    store.save_report({
        "id": shared_id,
        "title": "Race Test",
        "counter": 0
    })
    
    logger.info(f"初始状态: {store.get_report(shared_id)}")
    
    # 记录操作
    operations = []
    lock = threading.Lock()
    
    def worker_with_logging(worker_id: int, iterations: int):
        for i in range(iterations):
            # 读取
            data = store.get_report(shared_id)
            old_counter = data.get('counter', 0) if data else -1
            
            # 模拟一些处理时间（放大竞态窗口）
            time.sleep(0.0001)
            
            # 写入
            new_counter = old_counter + 1
            data['counter'] = new_counter
            store.save_report(data)
            
            # 记录操作
            with lock:
                operations.append({
                    'worker': worker_id,
                    'iteration': i,
                    'old': old_counter,
                    'new': new_counter
                })
    
    # 启动10个线程
    threads = []
    num_workers = 10
    iterations = 100
    
    logger.info(f"启动 {num_workers} 个线程，每线程 {iterations} 次操作")
    logger.info(f"期望最终计数: {num_workers * iterations}")
    
    start_time = time.time()
    
    for i in range(num_workers):
        t = threading.Thread(target=worker_with_logging, args=(i, iterations))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    elapsed = time.time() - start_time
    
    # 检查结果
    final_data = store.get_report(shared_id)
    final_counter = final_data.get('counter', 0) if final_data else 0
    
    logger.info(f"\n执行时间: {elapsed:.2f}秒")
    logger.info(f"总操作数: {len(operations)}")
    logger.info(f"最终计数: {final_counter}")
    logger.info(f"期望计数: {num_workers * iterations}")
    logger.info(f"丢失更新: {num_workers * iterations - final_counter}")
    logger.info(f"丢失率: {(1 - final_counter / (num_workers * iterations)) * 100:.1f}%")
    
    # 分析操作序列
    logger.info("\n操作序列分析 (前20个):")
    for i, op in enumerate(operations[:20]):
        logger.info(f"  {i+1}. Worker {op['worker']}: counter {op['old']} -> {op['new']}")
    
    # 统计每个worker的更新
    worker_updates = defaultdict(list)
    for op in operations:
        worker_updates[op['worker']].append((op['old'], op['new']))
    
    logger.info("\n各Worker的更新详情:")
    for worker_id in sorted(worker_updates.keys())[:5]:
        updates = worker_updates[worker_id]
        logger.info(f"  Worker {worker_id}:")
        logger.info(f"    更新次数: {len(updates)}")
        logger.info(f"    起始值: {updates[0][0] if updates else 'N/A'}")
        logger.info(f"    结束值: {updates[-1][1] if updates else 'N/A'}")
        
        # 检查是否有重复的new值
        new_values = [u[1] for u in updates]
        if len(new_values) != len(set(new_values)):
            duplicates = [v for v in set(new_values) if new_values.count(v) > 1]
            logger.info(f"    ⚠️ 重复的new值: {duplicates[:10]}")
    
    # 关键问题：为什么最终是0？
    # 可能的原因：
    # 1. 所有worker同时读取到counter=0
    # 2. 所有worker都写入了counter=1
    # 3. 最后一个写入的worker覆盖了其他人的值
    
    logger.info("\n" + "=" * 80)
    logger.info("根本原因分析:")
    logger.info("=" * 80)
    
    # 统计每个new值出现了多少次
    new_value_counts = defaultdict(int)
    for op in operations:
        new_value_counts[op['new']] += 1
    
    logger.info("\n每个new值被写入的次数:")
    for value in sorted(new_value_counts.keys())[:20]:
        count = new_value_counts[value]
        if count > 1:
            logger.warning(f"  值 {value}: 被写入 {count} 次 (冲突!)")
        else:
            logger.info(f"  值 {value}: 被写入 1 次")
    
    # 找出最大值
    max_value = max(new_value_counts.keys())
    logger.info(f"\n最大计数值: {max_value}")
    logger.info(f"最终计数值: {final_counter}")
    
    if max_value > final_counter:
        logger.warning(f"⚠️ 最大值 {max_value} > 最终值 {final_counter}")
        logger.warning("这意味着有更新被后续的更新覆盖了！")
    
    # 结论
    logger.info("\n" + "=" * 80)
    logger.info("诊断结论:")
    logger.info("=" * 80)
    
    if final_counter < num_workers * iterations:
        logger.error(f"❌ 发现竞态条件！")
        logger.error(f"   - {num_workers * iterations - final_counter} 次更新丢失")
        logger.error(f"   - 原因: 读-修改-写不是原子操作")
        logger.error(f"   - 解决方案: 需要使用原子操作或更细粒度的锁")
        
        if max_value > 1:
            logger.warning(f"   - 检测到 {max_value} 个不同的最终值被写入")
            logger.warning(f"   - 说明存在写冲突")
    else:
        logger.info("✅ 没有发现竞态条件")


def test_with_proper_lock():
    """测试使用正确的锁机制"""
    
    logger.info("\n" + "=" * 80)
    logger.info("对比测试: 使用全局锁保护")
    logger.info("=" * 80)
    
    store = SimpleMemoryStore()
    
    shared_id = "proper_lock_test"
    store.save_report({
        "id": shared_id,
        "title": "Proper Lock Test",
        "counter": 0
    })
    
    # 全局锁
    global_lock = threading.Lock()
    
    def worker_with_lock(worker_id: int, iterations: int):
        for _ in range(iterations):
            with global_lock:
                data = store.get_report(shared_id)
                current = data.get('counter', 0)
                data['counter'] = current + 1
                store.save_report(data)
    
    # 启动线程
    threads = []
    num_workers = 10
    iterations = 100
    
    for i in range(num_workers):
        t = threading.Thread(target=worker_with_lock, args=(i, iterations))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # 检查结果
    final_data = store.get_report(shared_id)
    final_counter = final_data.get('counter', 0) if final_data else 0
    expected = num_workers * iterations
    
    logger.info(f"期望: {expected}, 实际: {final_counter}")
    
    if final_counter == expected:
        logger.info("✅ 使用全局锁后，竞态条件被解决！")
    else:
        logger.error(f"❌ 仍然有问题: 期望 {expected}, 得到 {final_counter}")


def test_atomic_increment():
    """测试原子增量操作"""
    
    logger.info("\n" + "=" * 80)
    logger.info("对比测试: 使用原子增量操作")
    logger.info("=" * 80)
    
    store = SimpleMemoryStore()
    
    shared_id = "atomic_test"
    store.save_report({
        "id": shared_id,
        "title": "Atomic Test",
        "counter": 0
    })
    
    def worker_atomic(worker_id: int, iterations: int):
        for _ in range(iterations):
            # 使用原子操作
            new_value = store.atomic_increment(shared_id, "counter", 1)
    
    # 启动线程
    threads = []
    num_workers = 10
    iterations = 100
    
    for i in range(num_workers):
        t = threading.Thread(target=worker_atomic, args=(i, iterations))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # 检查结果
    final_data = store.get_report(shared_id)
    final_counter = final_data.get('counter', 0) if final_data else 0
    expected = num_workers * iterations
    
    logger.info(f"期望: {expected}, 实际: {final_counter}")
    
    if final_counter == expected:
        logger.info("✅ 使用原子增量操作后，竞态条件被解决！")
    else:
        logger.error(f"❌ 原子操作也失败了: 期望 {expected}, 得到 {final_counter}")


if __name__ == "__main__":
    diagnose_race_condition()
    test_with_proper_lock()
    test_atomic_increment()
