"""
慢工出细活 - 慢速、细致、深度验证测试
"""

import sys
import time
import random
import threading

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('slow_thorough_test')


class SlowButThoroughTester:
    """细致的深度验证器"""
    
    def __init__(self):
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
        self.store = SimpleMemoryStore()
        self.cache = SimpleCache()
        self.errors = []
        self.warnings = []
    
    def log_error(self, context: str, message: str):
        """记录错误"""
        self.errors.append((context, message))
        logger.error(f"❌ [{context}] {message}")
    
    def log_warning(self, context: str, message: str):
        """记录警告"""
        self.warnings.append((context, message))
        logger.warning(f"⚠️ [{context}] {message}")
    
    def log_success(self, context: str, message: str):
        """记录成功"""
        logger.info(f"✅ [{context}] {message}")
    
    def test_import_optimization(self):
        """测试1: 重复导入的优化问题"""
        logger.info("\n" + "=" * 80)
        logger.info("细致测试1: 检查重复导入问题")
        logger.info("=" * 80)
        
        context = "重复导入检查"
        
        # 测量多次调用get_report的时间
        report_id = "import_test"
        self.store.save_report({
            "id": report_id,
            "title": "Import Test",
            "content": "Test Content"
        })
        
        # 第一次调用
        start = time.time()
        self.store.get_report(report_id)
        first = time.time() - start
        
        # 多次调用，应该有缓存优化
        times = []
        for i in range(100):
            s = time.time()
            self.store.get_report(report_id)
            times.append(time.time() - s)
        
        avg = sum(times) / len(times)
        
        logger.info(f"第一次调用: {first * 1000:.4f}ms")
        logger.info(f"后续100次平均: {avg * 1000:.4f}ms")
        
        # 检查导入是否在每次调用时都发生
        # 虽然这不是功能错误，但这是性能优化点
        if first > avg * 3:
            self.log_warning(context, 
                "第一次调用明显较慢，可能是重复导入的影响 "
                "(copy模块在get_report中每次都导入)")
        
        self.log_success(context, "导入测试完成")
        return True
    
    def test_extra_field_handling(self):
        """测试2: 额外字段处理的边界情况"""
        logger.info("\n" + "=" * 80)
        logger.info("细致测试2: 额外字段处理的边界情况")
        logger.info("=" * 80)
        
        context = "额外字段处理"
        
        # 测试1: 添加额外字段
        report_id = "extra_fields_test"
        
        self.store.save_report({
            "id": report_id,
            "title": "Original Report",
            "custom_field_1": "Custom Value 1",
            "custom_field_2": 12345,
            "metadata": {"key": "value"}
        })
        
        retrieved = self.store.get_report(report_id)
        
        if retrieved is None:
            self.log_error(context, "报告保存后无法获取")
            return False
        
        if retrieved.get("custom_field_1") != "Custom Value 1":
            self.log_error(context, f"自定义字段custom_field_1值错误: {retrieved.get('custom_field_1')}")
            return False
        
        # 测试2: 更新时部分字段为None
        self.store.save_report({
            "id": report_id,
            "title": "Updated Report",
            "custom_field_1": None,
            "custom_field_2": None,
            "custom_field_3": "New Custom Value"
        })
        
        updated = self.store.get_report(report_id)
        
        if updated.get("custom_field_1") is not None:
            self.log_warning(context, 
                f"custom_field_1被设置为None后仍然存在: {updated.get('custom_field_1')}")
        
        if updated.get("custom_field_2") is not None:
            self.log_warning(context, 
                f"custom_field_2被设置为None后仍然存在: {updated.get('custom_field_2')}")
        
        if updated.get("custom_field_3") != "New Custom Value":
            self.log_error(context, "新增的custom_field_3未正确保存")
            return False
        
        # 测试3: 更新时不存在的字段
        self.store.save_report({
            "id": report_id,
            "title": "Another Update",
            "new_extra_field": "Another Extra"
        })
        
        final = self.store.get_report(report_id)
        
        if final.get("new_extra_field") != "Another Extra":
            self.log_error(context, "新增的new_extra_field未正确保存")
            return False
        
        self.log_success(context, "额外字段处理测试完成")
        return True
    
    def test_special_characters_in_ids(self):
        """测试3: 特殊字符在ID中的处理"""
        logger.info("\n" + "=" * 80)
        logger.info("细致测试3: 特殊字符ID处理")
        logger.info("=" * 80)
        
        context = "特殊字符ID"
        
        special_ids = [
            "",  # 空字符串
            " ",  # 单个空格
            "   ",  # 多个空格
            "测试中文ID",  # 中文
            "🔥Unicode🔥",  # Emoji
            "with/slashes/and\\backslashes",  # 路径字符
            'with"quotes"',  # 引号
            "with\nnewline\rreturn",  # 换行
            "with.dot",  # 点号
            "with$dollar#hash@at%percent^caret&star",  # 符号
            "x" * 1000,  # 超长ID
            "12345",  # 纯数字
            "_under_score_",  # 下划线
            "-dash-",  # 连字符
        ]
        
        successes = 0
        failures = 0
        
        for test_id in special_ids:
            try:
                # 保存
                saved_id = self.store.save_report({
                    "id": test_id,
                    "title": f"ID Test for {repr(test_id)}",
                    "content": "Special ID test"
                })
                
                # 读取
                retrieved = self.store.get_report(saved_id)
                
                if retrieved is None:
                    self.log_error(context, f"ID {repr(test_id)} 保存后无法读取")
                    failures += 1
                else:
                    successes += 1
                
                # 删除
                deleted = self.store.delete_report(saved_id)
                
            except Exception as e:
                self.log_error(context, f"ID {repr(test_id)} 处理异常: {str(e)}")
                failures += 1
        
        logger.info(f"特殊ID测试: {successes}成功, {failures}失败")
        
        if failures > 0:
            return False
        
        self.log_success(context, "所有特殊字符ID处理正常")
        return True
    
    def test_slow_concurrent_updates(self):
        """测试4: 慢速的并发更新（增加竞态窗口）"""
        logger.info("\n" + "=" * 80)
        logger.info("细致测试4: 慢速并发更新（增加竞态窗口）")
        logger.info("=" * 80)
        
        context = "慢速并发更新"
        
        shared_id = "slow_concurrent_test"
        
        # 初始化数据
        self.store.save_report({
            "id": shared_id,
            "title": "Slow Concurrent Test",
            "counter": 0
        })
        
        lock = threading.Lock()
        errors = []
        
        def slow_worker(wid):
            try:
                for i in range(10):
                    # 慢速读取 - 修改 - 写入循环
                    # 这会扩大竞态窗口
                    
                    # 读取
                    data = self.store.get_report(shared_id)
                    if data is None:
                        with lock:
                            errors.append(f"Worker {wid}: data is None at step {i}")
                        continue
                    
                    # 模拟一些延迟处理
                    time.sleep(0.001 + random.random() * 0.01)
                    
                    # 修改
                    current = data.get("counter", 0)
                    data["counter"] = current + 1
                    
                    # 再模拟一些延迟
                    time.sleep(0.001 + random.random() * 0.01)
                    
                    # 写入
                    self.store.save_report(data)
                    
            except Exception as e:
                with lock:
                    errors.append(f"Worker {wid}: {str(e)}")
        
        # 启动5个慢速工人
        workers = []
        for i in range(5):
            t = threading.Thread(target=slow_worker, args=(i,))
            workers.append(t)
            t.start()
        
        for w in workers:
            w.join()
        
        if errors:
            self.log_warning(context, f"发生 {len(errors)} 个异常")
        
        # 获取最终结果
        final = self.store.get_report(shared_id)
        final_counter = final.get("counter", 0) if final else 0
        expected = 5 * 10  # 5个工人各10次
        
        logger.info(f"最终counter: {final_counter}, 期望: {expected}")
        
        if final_counter < expected:
            self.log_warning(context, 
                f"Counter值低于期望值，可能存在竞态丢失：期望{expected}, 实际{final_counter}")
            logger.info(f"  (这可能是因为没有使用原子操作，这是可预期的行为)")
        elif final_counter > expected:
            self.log_error(context, 
                f"Counter值超过期望值，这是不应该的：期望{expected}, 实际{final_counter}")
            return False
        
        self.log_success(context, "慢速并发更新测试完成")
        return True
    
    def test_memory_cleanup(self):
        """测试5: 内存清理 - 大量创建删除后的内存状态"""
        logger.info("\n" + "=" * 80)
        logger.info("细致测试5: 内存清理验证")
        logger.info("=" * 80)
        
        context = "内存清理"
        
        # 记录初始状态
        initial_reports = len(self.store._storage)
        initial_version = len(self.store._version)
        
        logger.info(f"初始存储数量: {initial_reports}")
        logger.info(f"初始版本数量: {initial_version}")
        
        # 创建大量数据
        created_ids = []
        for i in range(10000):
            rid = f"memory_test_{i}"
            self.store.save_report({
                "id": rid,
                "title": f"Report {i}",
                "content": "x" * 100  # 一些内容
            })
            created_ids.append(rid)
        
        after_create = len(self.store._storage)
        after_create_version = len(self.store._version)
        
        logger.info(f"创建后存储数量: {after_create}")
        logger.info(f"创建后版本数量: {after_create_version}")
        
        # 删除所有创建的数据
        for rid in created_ids:
            self.store.delete_report(rid)
        
        after_delete = len(self.store._storage)
        after_delete_version = len(self.store._version)
        
        logger.info(f"删除后存储数量: {after_delete}")
        logger.info(f"删除后版本数量: {after_delete_version}")
        
        # 验证清理
        if after_delete > initial_reports:
            self.log_error(context, 
                f"删除后存储数量未回到初始值: 期望{initial_reports}, 实际{after_delete}")
            return False
        
        if after_delete_version > initial_version:
            self.log_error(context, 
                f"删除后版本数量未回到初始值: 期望{initial_version}, 实际{after_delete_version}")
            return False
        
        self.log_success(context, "内存清理验证通过")
        return True
    
    def test_time_consistency_over_long_duration(self):
        """测试6: 长时间的时间戳一致性"""
        logger.info("\n" + "=" * 80)
        logger.info("细致测试6: 长时间时间戳一致性")
        logger.info("=" * 80)
        
        context = "长时间时间戳一致性"
        
        report_id = "time_consistency_test"
        
        # 创建初始报告
        self.store.save_report({
            "id": report_id,
            "title": "Time Test Initial",
            "created_at": None  # 让系统自动生成
        })
        
        initial = self.store.get_report(report_id)
        initial_created = initial.get("created_at")
        logger.info(f"初始created_at: {initial_created}")
        
        # 多次更新，检查created_at不会变
        previous_updated = None
        created_remained_constant = True
        
        for i in range(100):
            time.sleep(0.01)  # 小延迟，让时间戳有差异
            
            self.store.save_report({
                "id": report_id,
                "title": f"Time Test Update {i}",
                "counter": i
            })
            
            current = self.store.get_report(report_id)
            current_created = current.get("created_at")
            current_updated = current.get("updated_at")
            
            if current_created != initial_created:
                self.log_error(context, f"created_at在第{i}次更新时发生改变")
                created_remained_constant = False
                break
            
            if previous_updated is not None and current_updated <= previous_updated:
                self.log_warning(context, 
                    f"updated_at在第{i}次更新时没有递增: {current_updated} <= {previous_updated}")
            
            previous_updated = current_updated
        
        if not created_remained_constant:
            return False
        
        self.log_success(context, "时间戳长时间一致性验证通过")
        return True
    
    def run_all_tests(self):
        """运行所有细致测试"""
        logger.info("=" * 80)
        logger.info("🚀 启动慢工出细活 - 深度细致验证测试")
        logger.info("=" * 80)
        
        tests = [
            ("重复导入优化检查", self.test_import_optimization),
            ("额外字段边界情况", self.test_extra_field_handling),
            ("特殊字符ID处理", self.test_special_characters_in_ids),
            ("慢速并发更新", self.test_slow_concurrent_updates),
            ("内存清理验证", self.test_memory_cleanup),
            ("长时间时间戳一致性", self.test_time_consistency_over_long_duration),
        ]
        
        results = {}
        
        for name, test_func in tests:
            try:
                results[name] = test_func()
            except Exception as e:
                self.log_error(name, f"测试崩溃: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                results[name] = False
        
        # 最终报告
        self.generate_final_report(results)
        
        return results
    
    def generate_final_report(self, results: dict):
        """生成最终详尽报告"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 慢工出细活 - 细致验证最终报告")
        logger.info("=" * 80)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        logger.info(f"总测试数: {total}")
        logger.info(f"通过: {passed}")
        logger.info(f"失败: {total - passed}")
        logger.info(f"通过率: {(passed / total * 100):.1f}%")
        
        if self.errors:
            logger.info(f"\n❌ 发现 {len(self.errors)} 个错误:")
            for ctx, msg in self.errors:
                logger.error(f"  [{ctx}] {msg}")
        
        if self.warnings:
            logger.info(f"\n⚠️ 发现 {len(self.warnings)} 个警告:")
            for ctx, msg in self.warnings:
                logger.warning(f"  [{ctx}] {msg}")
        
        if passed == total:
            logger.info("\n🎉🎉🎉 所有细致验证测试全部通过！")
        else:
            logger.warning(f"\n⚠️ {total - passed} 个测试失败，需要处理")
        
        logger.info("=" * 80)


def main():
    tester = SlowButThoroughTester()
    results = tester.run_all_tests()
    return results


if __name__ == "__main__":
    main()
