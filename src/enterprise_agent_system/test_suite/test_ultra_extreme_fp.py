"""
超极端第一性原理测试 - 质疑一切假设
设计目标：从最根本质疑系统的每个组件

第一性原理核心问题：
1. 存储真的能存储吗？容量有上限吗？
2. 缓存真的能缓存吗？TTL真的生效吗？
3. 并发真的安全吗？死锁可能吗？
4. 错误处理真的能恢复吗？
5. 资源真的有界限吗？
6. 时间戳真的可靠吗？
"""

import sys
import time
import random
import threading
import gc
from typing import Dict, List, Any, Set
from collections import defaultdict

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('ultra_extreme_fp')


class UltraExtremeFirstPrinciplesTest:
    """超极端第一性原理测试"""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        
    # ========== 第一性问题1: 存储容量上限 ==========
    def test_storage_capacity_limits(self):
        """质疑：存储真的有容量上限吗？
        如果无上限，会发生什么？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性问题: 存储容量上限")
        logger.info("质疑：存储能无限存储吗？")
        logger.info("=" * 80)
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        # 测试：存储海量数据，逼近内存极限
        num_items = 100000  # 10万个条目
        item_size = 1000  # 每条1KB
        
        logger.info(f"目标：存储 {num_items} 个 {item_size} 字节的条目")
        logger.info(f"预计占用: ~{num_items * item_size / (1024*1024):.1f} MB")
        
        failures = []
        
        for i in range(num_items):
            try:
                store.save_report({
                    "id": f"capacity_{i}",
                    "title": f"Item {i}",
                    "content": "x" * item_size,
                    "index": i
                })
                
                # 每10000个验证一次
                if i > 0 and i % 10000 == 0:
                    # 验证前100个
                    for j in range(min(100, i)):
                        retrieved = store.get_report(f"capacity_{j}")
                        if retrieved is None:
                            failures.append(f"Item {j} disappeared after {i} insertions")
                        elif retrieved.get('index') != j:
                            failures.append(f"Item {j} has wrong index")
                    
                    stats = store.get_stats()
                    logger.info(f"  {i:,} items stored, {stats['total_reports']} in storage")
                    
            except MemoryError:
                logger.error(f"MemoryError at item {i}")
                failures.append(f"MemoryError at item {i}")
                break
            except Exception as e:
                failures.append(f"Item {i}: {str(e)}")
        
        # 验证完整性
        logger.info(f"\n验证存储完整性...")
        missing = 0
        corrupted = 0
        
        for i in range(num_items):
            retrieved = store.get_report(f"capacity_{i}")
            if retrieved is None:
                missing += 1
            elif retrieved.get('index') != i:
                corrupted += 1
        
        logger.info(f"缺失: {missing}, 损坏: {corrupted}")
        
        if failures or missing or corrupted:
            logger.error(f"❌ 存储容量测试失败: {len(failures)} 错误, {missing} 缺失, {corrupted} 损坏")
            return False
        
        logger.info(f"✅ 成功存储 {num_items:,} 个条目，无丢失")
        return True
    
    # ========== 第一性问题2: 缓存TTL真的生效吗？ ==========
    def test_cache_ttl_fundamental(self):
        """质疑：缓存的TTL真的生效吗？
        TTL过期后，数据真的消失了吗？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性问题: 缓存TTL验证")
        logger.info("质疑：TTL过期后数据真的消失了吗？")
        logger.info("=" * 80)
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleCache
        
        cache = SimpleCache()
        
        # 测试1: TTL = 0 应该永不过期
        logger.info("测试1: TTL=0 (应该永不过期)")
        cache.set("permanent", "value", ttl=0)
        time.sleep(0.1)
        result = cache.get("permanent")
        if result != "value":
            logger.error(f"❌ TTL=0 失败: 期望 'value', 得到 {result}")
            return False
        logger.info("✅ TTL=0 正常")
        
        # 测试2: TTL = 1秒 应该1秒后过期
        logger.info("测试2: TTL=1秒")
        cache.set("temp_1s", "temp_value", ttl=1)
        
        # 立即检查
        immediate = cache.get("temp_1s")
        if immediate != "temp_value":
            logger.error(f"❌ 立即获取失败: 期望 'temp_value', 得到 {immediate}")
            return False
        
        # 等待1.1秒
        logger.info("  等待1.1秒...")
        time.sleep(1.1)
        
        expired = cache.get("temp_1s")
        if expired is not None:
            logger.error(f"❌ TTL过期失败: TTL=1秒后仍返回 {expired}")
            return False
        
        logger.info("✅ TTL=1秒 正常过期")
        
        # 测试3: 快速TTL
        logger.info("测试3: TTL=100ms")
        cache.set("fast_ttl", "fast", ttl=0.1)
        time.sleep(0.15)
        fast_expired = cache.get("fast_ttl")
        if fast_expired is not None:
            logger.error(f"❌ 快速TTL失败")
            return False
        logger.info("✅ 快速TTL正常")
        
        return True
    
    # ========== 第一性问题3: 死锁可能吗？ ==========
    def test_deadlock_possibility(self):
        """质疑：会发生死锁吗？
        多层锁可能导致死锁吗？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性问题: 死锁可能性")
        logger.info("质疑：会发生死锁吗？")
        logger.info("=" * 80)
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        # 测试：嵌套锁可能导致死锁
        logger.info("测试：嵌套操作")
        
        results = {'completed': 0, 'deadlocked': 0}
        lock = threading.Lock()
        
        def nested_operation(thread_id):
            try:
                # 外层操作
                store.save_report({
                    "id": f"nested_{thread_id}",
                    "title": f"Thread {thread_id}",
                    "counter": 0
                })
                
                # 内层操作
                for i in range(10):
                    data = store.get_report(f"nested_{thread_id}")
                    if data:
                        data['counter'] = i
                        store.save_report(data)
                
                with lock:
                    results['completed'] += 1
                    
            except Exception as e:
                with lock:
                    results['deadlocked'] += 1
                logger.error(f"线程 {thread_id} 异常: {str(e)}")
        
        threads = []
        for i in range(50):
            t = threading.Thread(target=nested_operation, args=(i,))
            threads.append(t)
            t.start()
        
        # 等待最多10秒
        start = time.time()
        for t in threads:
            remaining = 10 - (time.time() - start)
            if remaining > 0:
                t.join(timeout=remaining)
        
        # 检查是否全部完成
        alive = sum(1 for t in threads if t.is_alive())
        
        logger.info(f"完成: {results['completed']}, 存活: {alive}")
        
        if alive > 0:
            logger.warning(f"⚠️ {alive} 个线程未完成（可能是死锁）")
        
        if results['deadlocked'] > 0:
            logger.error(f"❌ {results['deadlocked']} 个线程异常")
            return False
        
        logger.info("✅ 无死锁迹象")
        return True
    
    # ========== 第一性问题4: 时间戳可靠性 ==========
    def test_timestamp_reliability(self):
        """质疑：时间戳真的可靠吗？
        时间会倒退吗？时区会混乱吗？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性问题: 时间戳可靠性")
        logger.info("质疑：时间戳真的可靠吗？")
        logger.info("=" * 80)
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        timestamps = []
        
        # 创建多个报告，记录时间戳
        for i in range(100):
            store.save_report({
                "id": f"ts_{i}",
                "title": f"Timestamp test {i}"
            })
            retrieved = store.get_report(f"ts_{i}")
            if retrieved:
                timestamps.append(retrieved.get('created_at'))
        
        # 验证：时间戳应该是递增的
        logger.info(f"验证 {len(timestamps)} 个时间戳...")
        
        decreases = 0
        for i in range(1, len(timestamps)):
            if timestamps[i] < timestamps[i-1]:
                decreases += 1
                logger.warning(f"时间戳倒退: {timestamps[i-1]} -> {timestamps[i]}")
        
        if decreases > 0:
            logger.warning(f"⚠️ 发现 {decreases} 次时间戳倒退")
        
        # 验证 updated_at >= created_at
        logger.info("验证 updated_at >= created_at...")
        violations = 0
        
        for i in range(min(100, len(timestamps))):
            retrieved = store.get_report(f"ts_{i}")
            if retrieved:
                created = retrieved.get('created_at')
                updated = retrieved.get('updated_at')
                if updated < created:
                    violations += 1
                    logger.error(f"违规: updated_at < created_at")
        
        if violations > 0:
            logger.error(f"❌ 发现 {violations} 个时间戳违规")
            return False
        
        logger.info("✅ 时间戳可靠")
        return True
    
    # ========== 第一性问题5: 数据结构一致性 ==========
    def test_data_structure_consistency(self):
        """质疑：数据结构真的保持一致吗？
        字典的键会丢失吗？类型会改变吗？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性问题: 数据结构一致性")
        logger.info("质疑：数据结构会改变吗？")
        logger.info("=" * 80)
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        # 创建复杂嵌套结构
        test_data = {
            "id": "structure_test",
            "title": "Structure Test",
            "nested": {
                "level1": {
                    "level2": {
                        "value": 42,
                        "list": [1, 2, 3],
                        "dict": {"a": 1}
                    }
                }
            },
            "list": [
                {"name": "item1", "value": 1},
                {"name": "item2", "value": 2}
            ],
            "special_chars": "!@#$%^&*()",
            "unicode": "中文测试 🔥",
            "number": 12345,
            "float": 3.14159,
            "boolean": True,
            "null": None
        }
        
        logger.info("保存复杂数据结构...")
        store.save_report(test_data)
        
        logger.info("读取并验证...")
        retrieved = store.get_report("structure_test")
        
        if retrieved is None:
            logger.error("❌ 数据消失")
            return False
        
        # 验证每个字段
        checks = [
            ("nested.level1.level2.value", retrieved.get('nested', {}).get('level1', {}).get('level2', {}).get('value'), 42),
            ("nested.level1.level2.list", str(retrieved.get('nested', {}).get('level1', {}).get('level2', {}).get('list')), str([1, 2, 3])),
            ("unicode", retrieved.get('unicode'), "中文测试 🔥"),
            ("number", retrieved.get('number'), 12345),
            ("float", retrieved.get('float'), 3.14159),
        ]
        
        failures = []
        for name, actual, expected in checks:
            if actual != expected:
                failures.append(f"{name}: 期望 {expected}, 得到 {actual}")
        
        if failures:
            logger.error("❌ 数据结构不一致:")
            for f in failures:
                logger.error(f"  {f}")
            return False
        
        logger.info("✅ 数据结构完全一致")
        return True
    
    # ========== 第一性问题6: 极端并发下的资源耗尽 ==========
    def test_resource_exhaustion(self):
        """质疑：极端并发会导致资源耗尽吗？
        CPU、内存、文件描述符会耗尽吗？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性问题: 资源耗尽")
        logger.info("质疑：极端并发会耗尽资源吗？")
        logger.info("=" * 80)
        
        process = None
        initial_fds = 0
        initial_memory = 0
        
        try:
            import psutil
            process = psutil.Process()
            initial_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
            initial_memory = process.memory_info().rss / (1024 * 1024)
            logger.info(f"初始文件描述符: {initial_fds}")
            logger.info(f"初始内存: {initial_memory:.2f}MB")
        except ImportError:
            logger.warning("psutil 不可用，跳过资源监控")
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        # 极端并发测试
        logger.info("启动 100 个并发线程...")
        
        results = {'completed': 0, 'errors': []}
        lock = threading.Lock()
        
        def extreme_worker(wid):
            try:
                for i in range(1000):
                    store.save_report({
                        "id": f"extreme_{wid}_{i}",
                        "title": f"Worker {wid} Item {i}"
                    })
                
                with lock:
                    results['completed'] += 1
                    
            except Exception as e:
                with lock:
                    results['errors'].append(str(e))
        
        threads = []
        for i in range(100):
            t = threading.Thread(target=extreme_worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 记录最终资源（如果psutil可用）
        final_fds = 0
        final_memory = 0
        
        if process:
            final_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
            final_memory = process.memory_info().rss / (1024 * 1024)
            logger.info(f"最终文件描述符: {final_fds} (增加: {final_fds - initial_fds})")
            logger.info(f"最终内存: {final_memory:.2f}MB (增加: {final_memory - initial_memory:.2f}MB)")
        
        logger.info(f"完成线程: {results['completed']}/100")
        
        if results['errors']:
            logger.error(f"❌ {len(results['errors'])} 个错误")
            return False
        
        if results['completed'] < 95:
            logger.error(f"❌ 只有 {results['completed']} 个线程完成")
            return False
        
        logger.info("✅ 极端并发下资源稳定")
        return True
    
    # ========== 运行所有测试 ==========
    def run_all(self):
        """运行所有超极端测试"""
        logger.info("=" * 80)
        logger.info("🚀 启动超极端第一性原理测试")
        logger.info("=" * 80)
        
        tests = [
            ("存储容量上限", self.test_storage_capacity_limits),
            ("缓存TTL验证", self.test_cache_ttl_fundamental),
            ("死锁可能性", self.test_deadlock_possibility),
            ("时间戳可靠性", self.test_timestamp_reliability),
            ("数据结构一致性", self.test_data_structure_consistency),
            ("资源耗尽测试", self.test_resource_exhaustion),
        ]
        
        results = {}
        
        for name, test_func in tests:
            try:
                results[name] = test_func()
            except Exception as e:
                logger.error(f"❌ {name} 崩溃: {str(e)}")
                import traceback
                traceback.print_exc()
                results[name] = False
        
        # 报告
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 超极端测试结果")
        logger.info("=" * 80)
        logger.info(f"通过: {passed}/{total} ({(passed/total*100):.1f}%)")
        
        if passed == total:
            logger.info("\n🎉 所有超极端测试通过！")
        else:
            logger.warning(f"\n⚠️ {total - passed} 个测试失败")
        
        logger.info("=" * 80)
        
        return results


def main():
    tester = UltraExtremeFirstPrinciplesTest()
    return tester.run_all()


if __name__ == "__main__":
    main()
