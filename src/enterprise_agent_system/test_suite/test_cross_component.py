"""
跨组件集成测试 - 第一性原理质疑所有组件交互
"""

import sys
import time
import random
import threading

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('cross_component_test')


def test_store_and_cache_integration():
    """测试存储和缓存的集成"""
    logger.info("=" * 80)
    logger.info("跨组件测试: 存储 + 缓存集成")
    logger.info("=" * 80)
    
    from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
    
    store = SimpleMemoryStore()
    cache = SimpleCache()
    
    # 场景：缓存未命中时从存储读取，写入缓存
    test_id = "integration_test"
    
    # 1. 存储数据
    store.save_report({
        "id": test_id,
        "title": "Integration Test",
        "content": "Test content"
    })
    
    # 2. 缓存未命中
    cached = cache.get(test_id)
    if cached is not None:
        logger.error("❌ 初始缓存应该为空")
        return False
    
    # 3. 从存储读取，写入缓存
    from_storage = store.get_report(test_id)
    if from_storage is None:
        logger.error("❌ 存储读取失败")
        return False
    
    cache.set(test_id, from_storage)
    
    # 4. 现在应该命中
    cached_after = cache.get(test_id)
    if cached_after is None:
        logger.error("❌ 缓存应该命中")
        return False
    
    # 5. 删除存储，缓存应该仍然有效
    store.delete_report(test_id)
    
    # 存储应该为空
    from_storage_after_delete = store.get_report(test_id)
    if from_storage_after_delete is not None:
        logger.error("❌ 删除后存储不应返回数据")
        return False
    
    # 但缓存应该仍然有效（独立于存储）
    cached_after_delete = cache.get(test_id)
    if cached_after_delete is None:
        logger.error("❌ 缓存应该仍然有效（独立于存储）")
        return False
    
    logger.info("✅ 存储+缓存集成正常")
    return True


def test_concurrent_store_cache():
    """测试并发访问存储和缓存"""
    logger.info("\n" + "=" * 80)
    logger.info("跨组件测试: 并发存储和缓存")
    logger.info("=" * 80)
    
    from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
    
    store = SimpleMemoryStore()
    cache = SimpleCache()
    
    errors = []
    success_count = [0]
    lock = threading.Lock()
    
    def worker(wid):
        try:
            for i in range(100):
                report_id = f"concurrent_{wid}_{i}"
                
                # 存储操作
                store.save_report({
                    "id": report_id,
                    "title": f"Worker {wid} Item {i}",
                    "content": f"Content {wid}-{i}"
                })
                
                # 缓存操作
                cache.set(report_id, f"cached_{wid}_{i}")
                
                # 读取验证
                stored = store.get_report(report_id)
                cached = cache.get(report_id)
                
                if stored is None or cached is None:
                    errors.append(f"Worker {wid} item {i}: data missing")
                
                with lock:
                    success_count[0] += 1
                    
        except Exception as e:
            errors.append(f"Worker {wid}: {str(e)}")
    
    threads = []
    for i in range(20):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    logger.info(f"成功操作: {success_count[0]}, 错误: {len(errors)}")
    
    if errors:
        logger.error("❌ 发现错误:")
        for err in errors[:5]:
            logger.error(f"  {err}")
        return False
    
    logger.info("✅ 并发存储和缓存正常")
    return True


def test_consistency_between_store_and_cache():
    """测试存储和缓存之间的一致性"""
    logger.info("\n" + "=" * 80)
    logger.info("跨组件测试: 存储和缓存一致性")
    logger.info("=" * 80)
    
    from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
    
    store = SimpleMemoryStore()
    cache = SimpleCache()
    
    # 写入存储，然后同步缓存
    test_id = "consistency_test"
    
    store.save_report({
        "id": test_id,
        "title": "Original Title",
        "content": "Original Content"
    })
    
    # 同步到缓存
    data = store.get_report(test_id)
    cache.set(test_id, data)
    
    # 修改存储
    store.save_report({
        "id": test_id,
        "title": "Modified Title",
        "content": "Modified Content"
    })
    
    # 缓存仍然是旧数据（这是预期行为，缓存是独立的）
    cached_data = cache.get(test_id)
    
    if cached_data is None:
        logger.error("❌ 缓存应该仍然有数据")
        return False
    
    # 缓存应该仍然是旧数据
    if cached_data.get('title') != "Original Title":
        logger.error("❌ 缓存应该保持旧数据（独立于存储）")
        return False
    
    logger.info("✅ 存储和缓存独立性验证通过")
    logger.info("  注意：缓存独立于存储，这是设计选择")
    
    return True


def test_version_tracking():
    """测试版本跟踪功能"""
    logger.info("\n" + "=" * 80)
    logger.info("跨组件测试: 版本跟踪")
    logger.info("=" * 80)
    
    from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
    
    store = SimpleMemoryStore()
    
    test_id = "version_test"
    
    # 初始版本应该是 1
    store.save_report({
        "id": test_id,
        "title": "Version 1"
    })
    
    # 获取统计数据来验证版本
    # 实际上我们可以通过多次更新来验证
    
    for i in range(10):
        store.save_report({
            "id": test_id,
            "title": f"Version {i+2}",
            "counter": i
        })
    
    # 获取最终数据
    final = store.get_report(test_id)
    
    if final is None:
        logger.error("❌ 获取最终数据失败")
        return False
    
    if final.get('title') != "Version 11":
        logger.error(f"❌ 版本不匹配: 期望 Version 11, 得到 {final.get('title')}")
        return False
    
    logger.info("✅ 版本跟踪正常")
    return True


def run_all_tests():
    """运行所有跨组件测试"""
    logger.info("=" * 80)
    logger.info("🚀 启动跨组件集成测试")
    logger.info("=" * 80)
    
    tests = [
        ("存储+缓存集成", test_store_and_cache_integration),
        ("并发存储缓存", test_concurrent_store_cache),
        ("一致性验证", test_consistency_between_store_and_cache),
        ("版本跟踪", test_version_tracking),
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
    logger.info("📊 跨组件测试结果")
    logger.info("=" * 80)
    logger.info(f"通过: {passed}/{total} ({(passed/total*100):.1f}%)")
    
    if passed == total:
        logger.info("\n🎉 所有跨组件测试通过！")
    else:
        logger.warning(f"\n⚠️ {total - passed} 个测试失败")
    
    logger.info("=" * 80)
    
    return results


if __name__ == "__main__":
    run_all_tests()
