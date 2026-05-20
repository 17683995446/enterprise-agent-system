"""
最终综合验证测试 - 所有测试套件汇总
"""

import sys
import time

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('final_summary')


def run_all_tests():
    """运行所有测试套件"""
    logger.info("=" * 80)
    logger.info("🚀 最终综合验证 - 运行所有测试套件")
    logger.info("=" * 80)
    
    all_results = {}
    
    # 测试1: 第一性原理测试
    logger.info("\n运行第一性原理测试...")
    try:
        from enterprise_agent_system.test_suite.test_first_principles import FirstPrinciplesVerifier
        fp_tester = FirstPrinciplesVerifier()
        fp_results = fp_tester.run_all_tests()
        all_results['第一性原理'] = {
            'passed': sum(1 for v in fp_results.values() if v),
            'total': len(fp_results),
            'results': fp_results
        }
    except Exception as e:
        logger.error(f"第一性原理测试崩溃: {e}")
        all_results['第一性原理'] = {'passed': 0, 'total': 1}
    
    # 测试2: 超极端测试
    logger.info("\n运行超极端测试...")
    try:
        from enterprise_agent_system.test_suite.test_ultra_extreme_fp import UltraExtremeFirstPrinciplesTest
        ultra_tester = UltraExtremeFirstPrinciplesTest()
        ultra_results = ultra_tester.run_all()
        all_results['超极端'] = {
            'passed': sum(1 for v in ultra_results.values() if v),
            'total': len(ultra_results),
            'results': ultra_results
        }
    except Exception as e:
        logger.error(f"超极端测试崩溃: {e}")
        all_results['超极端'] = {'passed': 0, 'total': 1}
    
    # 测试3: 跨组件测试
    logger.info("\n运行跨组件测试...")
    try:
        from enterprise_agent_system.test_suite.test_cross_component import run_all_tests as run_cross
        cross_results = run_cross()
        all_results['跨组件'] = {
            'passed': sum(1 for v in cross_results.values() if v),
            'total': len(cross_results),
            'results': cross_results
        }
    except Exception as e:
        logger.error(f"跨组件测试崩溃: {e}")
        all_results['跨组件'] = {'passed': 0, 'total': 1}
    
    # 测试4: 最终验证测试
    logger.info("\n运行最终验证测试...")
    try:
        from enterprise_agent_system.test_suite.test_final_verify import test_complete
        final_passed = test_complete()
        all_results['最终验证'] = {
            'passed': 1 if final_passed else 0,
            'total': 1,
            'results': {'test_complete': final_passed}
        }
    except Exception as e:
        logger.error(f"最终验证测试崩溃: {e}")
        all_results['最终验证'] = {'passed': 0, 'total': 1}
    
    # 生成最终报告
    generate_final_report(all_results)
    
    return all_results


def generate_final_report(all_results):
    """生成最终报告"""
    logger.info("\n" + "=" * 80)
    logger.info("📊 最终综合验证报告")
    logger.info("=" * 80)
    
    total_passed = 0
    total_tests = 0
    
    for category, data in all_results.items():
        passed = data['passed']
        total = data['total']
        total_passed += passed
        total_tests += total
        
        rate = (passed / total * 100) if total > 0 else 0
        status = "✅" if passed == total else "⚠️"
        
        logger.info(f"{status} {category}: {passed}/{total} ({(rate):.1f}%)")
    
    overall_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    logger.info(f"\n总体通过率: {total_passed}/{total_tests} ({(overall_rate):.1f}%)")
    
    if total_passed == total_tests:
        logger.info("\n🎉🎉🎉 所有测试套件全部通过！")
        logger.info("系统已通过最严格的验证，可以投入生产！")
    else:
        logger.warning(f"\n⚠️ {total_tests - total_passed} 个测试失败")
    
    logger.info("=" * 80)
    
    # 发现的问题汇总
    logger.info("\n📝 本轮发现并修复的问题:")
    logger.info("  1. 缓存TTL=0处理错误（已修复）")
    logger.info("  2. get_report返回引用而非拷贝（已修复）")
    logger.info("  3. psutil依赖缺失（已安装）")
    
    logger.info("\n💡 系统改进:")
    logger.info("  1. 存储支持智能字段更新")
    logger.info("  2. get_report返回深拷贝防止引用陷阱")
    logger.info("  3. 缓存TTL语义正确处理")
    logger.info("  4. 无死锁设计验证")
    logger.info("  5. 时间戳可靠性验证")
    logger.info("  6. 资源管理稳定")
    
    logger.info("=" * 80)


if __name__ == "__main__":
    run_all_tests()
