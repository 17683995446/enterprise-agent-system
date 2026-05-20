"""
调试测试 - 找出具体是什么操作失败了
"""

import sys
import time
import random
import threading

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('debug_errors')


def test_specific_ops():
    """测试每个操作类型，找出失败的那个"""
    
    logger.info("=" * 80)
    logger.info("开始调试测试")
    logger.info("=" * 80)
    
    store = SimpleMemoryStore()
    cache = SimpleCache()
    
    # 测试1: 保存操作
    logger.info("\n测试1: 保存操作")
    try:
        for i in range(10):
            store.save_report({
                "id": f"test_{i}",
                "title": f"Test {i}",
                "type": "test"
            })
        logger.info("✅ 保存操作成功")
    except Exception as e:
        logger.error(f"❌ 保存操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试2: 读取操作
    logger.info("\n测试2: 读取操作")
    try:
        for i in range(10):
            report = store.get_report(f"test_{i}")
            assert report is not None, f"Report test_{i} not found"
        logger.info("✅ 读取操作成功")
    except Exception as e:
        logger.error(f"❌ 读取操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试3: 删除操作
    logger.info("\n测试3: 删除操作")
    try:
        for i in range(5):
            store.delete_report(f"test_{i}")
        # 尝试删除不存在的
        store.delete_report("non_existent")
        logger.info("✅ 删除操作成功")
    except Exception as e:
        logger.error(f"❌ 删除操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试4: 列表操作
    logger.info("\n测试4: 列表操作")
    try:
        reports = store.list_reports(limit=10)
        logger.info(f"✅ 列表操作成功，返回 {len(reports)} 个报告")
    except Exception as e:
        logger.error(f"❌ 列表操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试5: 缓存操作
    logger.info("\n测试5: 缓存操作")
    try:
        for i in range(10):
            cache.set(f"cache_{i}", f"value_{i}")
            cache.get(f"cache_{i}")
        cache.delete(f"cache_0")
        logger.info("✅ 缓存操作成功")
    except Exception as e:
        logger.error(f"❌ 缓存操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试6: 边界情况
    logger.info("\n测试6: 边界情况")
    try:
        # 超长ID
        store.save_report({
            "id": "x" * 1000,
            "title": "Long ID",
            "type": "test"
        })
        
        # 空值
        store.save_report({
            "id": "test_null",
            "title": None,
            "type": "",
            "quality_score": None
        })
        
        # 极端值
        store.save_report({
            "id": "test_extreme",
            "title": "Extreme",
            "quality_score": 1e100,
            "type": "test"
        })
        
        logger.info("✅ 边界情况成功")
    except Exception as e:
        logger.error(f"❌ 边界情况失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试7: 并发操作
    logger.info("\n测试7: 并发操作")
    errors = []
    
    def worker(wid):
        try:
            for i in range(100):
                report_id = f"concurrent_{wid}_{i}"
                store.save_report({
                    "id": report_id,
                    "title": f"Concurrent {wid}-{i}",
                    "type": "test"
                })
                store.get_report(report_id)
        except Exception as e:
            errors.append(f"Worker {wid}: {str(e)}")
    
    threads = []
    for i in range(10):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    if errors:
        logger.error(f"❌ 并发操作有 {len(errors)} 个错误:")
        for err in errors[:5]:
            logger.error(f"  - {err}")
    else:
        logger.info("✅ 并发操作成功")
    
    logger.info("\n" + "=" * 80)
    logger.info("调试测试完成")
    logger.info("=" * 80)


def run_randomized_test():
    """模拟之前的随机测试，记录详细错误"""
    
    logger.info("\n" + "=" * 80)
    logger.info("开始随机化错误复现测试")
    logger.info("=" * 80)
    
    store = SimpleMemoryStore()
    cache = SimpleCache()
    
    errors = []
    error_types = {}
    ops_per_type = {
        'save': 0, 'get': 0, 'delete': 0, 'cache_set': 0, 'cache_get': 0, 'list': 0
    }
    
    for i in range(10000):
        op_type = random.choice(['save', 'get', 'delete', 'cache_set', 'cache_get', 'list'])
        
        try:
            if op_type == 'save':
                ops_per_type['save'] += 1
                report_id = f"rand_{i}"
                store.save_report({
                    "id": report_id,
                    "title": f"Rand {i}",
                    "type": "test"
                })
            elif op_type == 'get':
                ops_per_type['get'] += 1
                store.get_report(f"rand_{random.randint(0, max(0, i-1))}")
            elif op_type == 'delete':
                ops_per_type['delete'] += 1
                store.delete_report(f"rand_{random.randint(0, max(0, i-1))}")
            elif op_type == 'cache_set':
                ops_per_type['cache_set'] += 1
                cache.set(f"rand_cache_{i}", i)
            elif op_type == 'cache_get':
                ops_per_type['cache_get'] += 1
                cache.get(f"rand_cache_{random.randint(0, max(0, i-1))}")
            elif op_type == 'list':
                ops_per_type['list'] += 1
                store.list_reports(limit=10)
        except Exception as e:
            error_key = f"{op_type}: {str(e)}"
            error_types[error_key] = error_types.get(error_key, 0) + 1
            errors.append((op_type, str(e), i))
    
    # 报告结果
    logger.info("\n操作次数统计:")
    for op, count in ops_per_type.items():
        logger.info(f"  {op}: {count}")
    
    if error_types:
        logger.warning("\n发现的错误类型:")
        for err, count in sorted(error_types.items(), key=lambda x: -x[1]):
            logger.warning(f"  {err}: {count} 次")
        
        if errors:
            logger.warning("\n错误详情:")
            for i, (op, err, idx) in enumerate(errors[:10]):
                logger.warning(f"  {i+1}. 操作: {op}, 索引: {idx}, 错误: {err}")
    else:
        logger.info("\n✅ 无错误！")
    
    logger.info("\n" + "=" * 80)
    logger.info("随机化测试完成")
    logger.info("=" * 80)


if __name__ == "__main__":
    test_specific_ops()
    run_randomized_test()
