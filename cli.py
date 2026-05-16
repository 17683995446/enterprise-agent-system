"""
CLI Tool for Enterprise Agent System
提供命令行接口进行代码分析和系统管理
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from enterprise_agent_system.application.llm_analysis_system import EnhancedCodeAnalyzer
from enterprise_agent_system.application.enhanced_analysis_system import EnhancedAnalyzer
from enterprise_agent_system.infrastructure.llm_integration import get_llm_manager, AnalysisOptions, AnalysisDepth
from enterprise_agent_system.infrastructure.analysis_report_store import AnalysisReportStore
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance(__name__)


def print_banner():
    """打印横幅"""
    print("=" * 80)
    print("  Enterprise Agent System - CLI Tool")
    print("  企业级双模式 Agent 系统 - 命令行工具")
    print("=" * 80)


async def analyze_file(file_path: str, analysis_type: str = "comprehensive", save: bool = False):
    """分析单个文件"""
    print(f"\n📁 分析文件: {file_path}")
    print("-" * 60)
    
    try:
        analyzer = EnhancedCodeAnalyzer()
        
        options = AnalysisOptions(
            depth=AnalysisDepth.DEEP,
            include_security=True,
            include_performance=True,
            include_best_practices=True
        )
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 使用LLM分析
        llm = get_llm_manager()
        result = await llm.analyze_code(
            code=code,
            language=guess_language(file_path),
            options=options
        )
        
        print(f"✅ 分析完成")
        print(f"⏱️  处理时间: {result.latency:.2f}秒")
        print(f"\n📋 分析结果:")
        print("-" * 60)
        print(result.content[:1000] + "..." if len(result.content) > 1000 else result.content)
        
        # 保存报告
        if save:
            store = AnalysisReportStore()
            report_id = store.save_report({
                "title": f"Analysis of {Path(file_path).name}",
                "type": analysis_type,
                "content": result.content,
                "findings": [],
                "recommendations": [],
                "quality_score": 8.0,
                "processing_time": result.latency,
                "file_path": file_path,
                "llm_insights": result.content
            })
            print(f"\n💾 报告已保存, ID: {report_id}")
        
        return result
    
    except Exception as e:
        logger.error(f"分析失败: {e}")
        print(f"❌ 错误: {e}")
        return None


async def analyze_directory(dir_path: str, pattern: str = "*.py", save: bool = False):
    """分析目录"""
    print(f"\n📂 分析目录: {dir_path}")
    print(f"🔍 文件模式: {pattern}")
    print("-" * 60)
    
    path = Path(dir_path)
    if not path.is_dir():
        print(f"❌ 无效的目录路径")
        return
    
    files = list(path.rglob(pattern))
    print(f"📁 找到 {len(files)} 个文件")
    
    results = []
    for file in files[:10]:  # 限制数量防止过载
        print(f"\n  分析: {file.name}")
        result = await analyze_file(str(file), save=save)
        if result:
            results.append(result)
    
    print(f"\n✅ 完成, 分析了 {len(results)} 个文件")


async def interactive_chat():
    """交互式对话模式"""
    print("\n💬 交互式对话模式 (输入 'quit' 退出)")
    print("-" * 60)
    
    llm = get_llm_manager()
    
    while True:
        try:
            user_input = input("\n👤 你: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见!")
                break
            
            if not user_input:
                continue
            
            print("🤖 AI: ", end="", flush=True)
            result = await llm.complete(user_input, system_prompt="你是一个专业的AI助手。")
            print(result.content)
        
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


async def show_stats():
    """显示统计信息"""
    llm = get_llm_manager()
    stats = llm.get_stats()
    
    store = AnalysisReportStore()
    report_stats = store.get_stats()
    
    print("\n📊 系统统计")
    print("-" * 60)
    print(f"  总请求数: {stats['total_requests']}")
    print(f"  缓存命中: {stats['cached_requests']}")
    print(f"  缓存命中率: {stats['cache_hit_rate']:.2%}")
    print(f"  平均响应时间: {stats['avg_latency']:.2f}秒")
    print(f"\n  分析报告数: {report_stats['total_reports']}")
    print(f"  平均质量分: {report_stats['average_score']:.2f}")


def guess_language(file_path: str) -> str:
    """根据文件扩展名猜测语言"""
    ext = Path(file_path).suffix.lower()
    language_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".go": "go",
        ".rs": "rust",
    }
    return language_map.get(ext, "unknown")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Enterprise Agent System CLI - 企业级Agent系统命令行工具"
    )
    
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    
    # 分析命令
    analyze_parser = subparsers.add_parser("analyze", help="分析代码文件/目录")
    analyze_parser.add_argument("path", help="文件或目录路径")
    analyze_parser.add_argument("--type", "-t", default="comprehensive", 
                              choices=["comprehensive", "security", "performance", "architecture"],
                              help="分析类型")
    analyze_parser.add_argument("--save", "-s", action="store_true", help="保存分析报告")
    
    # 聊天命令
    chat_parser = subparsers.add_parser("chat", help="交互式对话模式")
    
    # 统计命令
    stats_parser = subparsers.add_parser("stats", help="显示系统统计")
    
    # 服务器命令
    server_parser = subparsers.add_parser("server", help="启动API服务器")
    server_parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    server_parser.add_argument("--port", type=int, default=8000, help="监听端口")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.command == "analyze":
        path = Path(args.path)
        if path.is_file():
            await analyze_file(str(path), args.type, args.save)
        elif path.is_dir():
            await analyze_directory(str(path), save=args.save)
        else:
            print(f"❌ 路径不存在: {path}")
    
    elif args.command == "chat":
        await interactive_chat()
    
    elif args.command == "stats":
        await show_stats()
    
    elif args.command == "server":
        from enterprise_agent_system.infrastructure.api.api_server import start_api_server
        start_api_server(args.host, args.port)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
