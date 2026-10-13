"""
Advanced LLM Integration Module
Enhanced with Multi-Model Support, Caching, and Advanced Analysis
Infrastructure Layer - 高级LLM集成
"""

import os
import json
import asyncio
import hashlib
import time
from typing import Optional, List, Dict, Any, AsyncIterator, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict
import httpx
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance


logger = get_logger_instance(__name__)


class LLMProvider(Enum):
    """LLM提供商枚举"""
    SILICON_FLOW = "silicon_flow"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"


class ModelType(Enum):
    """模型类型"""
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    QWEN25 = "qwen-2.5"
    QWEN_MAX = "qwen-max"
    DEEPSEEK = "deepseek-chat"
    DEEPSEEK_CODER = "deepseek-coder"
    CHATGLM = "chatglm"
    YI = "yi-chat"
    MOCK = "mock"


class AnalysisDepth(Enum):
    """分析深度"""
    QUICK = "quick"          # 快速扫描
    STANDARD = "standard"    # 标准分析
    DEEP = "deep"           # 深度分析
    COMPREHENSIVE = "comprehensive"  # 全面分析


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: LLMProvider = LLMProvider.SILICON_FLOW
    api_key: str = ""
    base_url: str = "https://api.siliconflow.cn/v1"
    model: str = "Qwen/Qwen2.5-7B-Instruct"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    timeout: int = 60
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_cache: bool = True
    cache_ttl: int = 3600


@dataclass
class Message:
    """聊天消息"""
    role: str
    content: str
    name: Optional[str] = None


@dataclass
class CompletionResult:
    """完成结果"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    latency: float
    error: Optional[str] = None
    cached: bool = False


@dataclass
class StreamChunk:
    """流式输出块"""
    content: str
    delta: str
    done: bool


@dataclass
class AnalysisOptions:
    """分析选项"""
    depth: AnalysisDepth = AnalysisDepth.STANDARD
    include_security: bool = True
    include_performance: bool = True
    include_best_practices: bool = True
    include_documentation: bool = True
    generate_tests: bool = False
    explain_reasoning: bool = True


class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size: int = 100):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            self.cache[key] = value
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
    
    def clear(self):
        self.cache.clear()


class SiliconFlowClient:
    """硅基流动客户端"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        if self.client is None:
            self.client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.config.timeout,
            )
        return self.client
    
    async def complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        model: Optional[str] = None,
    ) -> Union[CompletionResult, AsyncIterator[StreamChunk]]:
        """发送完成请求"""
        start_time = time.time()
        
        request_data = {
            "model": model or self.config.model,
            "messages": [
                {"role": msg.role, "content": msg.content, "name": msg.name}
                for msg in messages
            ],
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "top_p": self.config.top_p,
            "stream": stream,
        }
        
        try:
            client = await self._get_client()
            
            if stream:
                return self._stream_complete(client, request_data, start_time)
            else:
                return await self._sync_complete(client, request_data, start_time, model or self.config.model)
                
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            return CompletionResult(
                content="",
                model=self.config.model,
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                finish_reason="error",
                latency=time.time() - start_time,
                error=str(e),
            )
    
    async def _sync_complete(
        self,
        client: httpx.AsyncClient,
        request_data: Dict[str, Any],
        start_time: float,
        model: str,
    ) -> CompletionResult:
        """同步完成请求"""
        for attempt in range(self.config.retry_attempts):
            try:
                response = await client.post("/chat/completions", json=request_data)
                response.raise_for_status()
                
                data = response.json()
                choice = data["choices"][0]
                
                return CompletionResult(
                    content=choice["message"]["content"],
                    model=data.get("model", model),
                    usage=data.get("usage", {}),
                    finish_reason=choice.get("finish_reason", "stop"),
                    latency=time.time() - start_time,
                )
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise
        
        raise Exception(f"Failed after {self.config.retry_attempts} attempts")
    
    async def _stream_complete(
        self,
        client: httpx.AsyncClient,
        request_data: Dict[str, Any],
        start_time: float,
    ) -> AsyncIterator[StreamChunk]:
        """流式完成请求"""
        try:
            async with client.stream("POST", "/chat/completions", json=request_data) as response:
                response.raise_for_status()
                
                full_content = ""
                
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    
                    if line.startswith("data: "):
                        line = line[6:]
                    
                    if line == "[DONE]":
                        yield StreamChunk(
                            content=full_content,
                            delta="",
                            done=True,
                        )
                        break
                    
                    try:
                        data = json.loads(line)
                        delta = data["choices"][0]["delta"].get("content", "")
                        full_content += delta
                        
                        yield StreamChunk(
                            content=full_content,
                            delta=delta,
                            done=False,
                        )
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield StreamChunk(
                content="",
                delta="",
                done=True,
            )
    
    async def close(self):
        """关闭客户端"""
        if self.client:
            await self.client.aclose()
            self.client = None


class AdvancedLLMManager:
    """高级LLM管理器 - 增强版本"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or self._load_config()
        self.client = SiliconFlowClient(self.config)
        self.conversation_history: Dict[str, List[Message]] = {}
        self.cache = LRUCache(max_size=200) if self.config.enable_cache else None
        self.request_stats = {
            "total_requests": 0,
            "cached_requests": 0,
            "total_tokens": 0,
            "total_latency": 0.0,
        }
        logger.info(f"Advanced LLM Manager initialized with {self.config.provider.value}")
    
    def _load_config(self) -> LLMConfig:
        """加载配置"""
        api_key = os.getenv("SILICON_FLOW_API_KEY", "REDACTED_API_KEY")
        
        return LLMConfig(
            provider=LLMProvider.SILICON_FLOW,
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1",
            model="Qwen/Qwen2.5-7B-Instruct",
            temperature=0.7,
            max_tokens=4096,
            enable_cache=True,
            cache_ttl=3600,
        )
    
    def _get_cache_key(self, prompt: str, system_prompt: Optional[str], model: str) -> str:
        """生成缓存键"""
        content = f"{system_prompt or ''}:{prompt}:{model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_id: Optional[str] = None,
        stream: bool = False,
        model: Optional[str] = None,
        use_cache: bool = True,
    ) -> CompletionResult:
        """完成文本生成"""
        model = model or self.config.model
        
        # 检查缓存
        if use_cache and self.cache and not stream:
            cache_key = self._get_cache_key(prompt, system_prompt, model)
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self.request_stats["cached_requests"] += 1
                cached_result.cached = True
                return cached_result
        
        messages = []
        
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        
        if conversation_id and conversation_id in self.conversation_history:
            messages.extend(self.conversation_history[conversation_id])
        
        messages.append(Message(role="user", content=prompt))
        
        if stream:
            result = await self.client.complete(messages, stream=True)
            if hasattr(result, "__anext__"):
                return result
            return result
        
        result = await self.client.complete(messages, model=model)
        
        if conversation_id:
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []
            self.conversation_history[conversation_id].append(Message(role="user", content=prompt))
            self.conversation_history[conversation_id].append(Message(role="assistant", content=result.content))
        
        # 更新统计
        self.request_stats["total_requests"] += 1
        self.request_stats["total_tokens"] += result.usage.get("total_tokens", 0)
        self.request_stats["total_latency"] += result.latency
        
        # 缓存结果
        if use_cache and self.cache and not result.error:
            cache_key = self._get_cache_key(prompt, system_prompt, model)
            self.cache.set(cache_key, result)
        
        return result
    
    async def batch_complete(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        max_concurrent: int = 5,
    ) -> List[CompletionResult]:
        """批量完成"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def complete_one(prompt: str) -> CompletionResult:
            async with semaphore:
                return await self.complete(prompt, system_prompt)
        
        tasks = [complete_one(p) for p in prompts]
        return await asyncio.gather(*tasks)
    
    async def analyze_code(
        self,
        code: str,
        language: str = "python",
        options: Optional[AnalysisOptions] = None,
    ) -> CompletionResult:
        """增强的代码分析"""
        options = options or AnalysisOptions()
        
        analysis_focus = []
        if options.include_security:
            analysis_focus.append("安全性分析（SQL注入、XSS、CSRF、敏感信息泄露）")
        if options.include_performance:
            analysis_focus.append("性能分析（时间复杂度、空间复杂度、潜在瓶颈）")
        if options.include_best_practices:
            analysis_focus.append("最佳实践（代码风格、设计模式、可维护性）")
        if options.include_documentation:
            analysis_focus.append("文档完整性")
        if options.generate_tests:
            analysis_focus.append("测试建议")
        
        depth_instruction = {
            AnalysisDepth.QUICK: "快速扫描主要问题",
            AnalysisDepth.STANDARD: "标准分析，覆盖主要方面",
            AnalysisDepth.DEEP: "深入分析所有细节",
            AnalysisDepth.COMPREHENSIVE: "全面分析，包括架构、设计、测试等",
        }
        
        system_prompt = f"""你是一个专业的{language}代码分析专家。请对提供的代码进行全面分析：

分析重点：
{chr(10).join(f"- {f}" for f in analysis_focus)}

分析深度：{depth_instruction.get(options.depth, "标准分析")}

输出格式：
1. 代码概述
2. 功能分析
3. 发现的问题（分类：安全、性能、最佳实践等）
4. 详细建议（按优先级排序）
5. 优化代码（如果有）
6. 风险评估

请用中文回答，保持专业、详细和准确。"""
        
        prompt = f"""请分析以下{language}代码：

```{language}
{code}
```

请提供详细的分析报告，包括所有发现的问题和具体的改进建议。"""
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    async def analyze_security(
        self,
        code: str,
        language: str = "python",
    ) -> CompletionResult:
        """专门的安全分析"""
        system_prompt = """你是一个专业的安全分析师。请分析代码中的安全漏洞：

检查类型：
1. 注入攻击（SQL注入、命令注入、XSS）
2. 认证和授权问题
3. 敏感数据泄露
4. 加密算法使用
5. 依赖库安全
6. 配置安全问题

输出格式：
1. 漏洞列表（严重程度：高/中/低）
2. 漏洞位置
3. 攻击原理
4. 修复建议
5. 参考CWE/CVE

请用中文回答，重点关注实际可利用的漏洞。"""
        
        prompt = f"""请对以下{language}代码进行安全分析：

```{language}
{code}
```

请列出所有发现的安全问题，并提供详细的修复方案。"""
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    async def analyze_performance(
        self,
        code: str,
        language: str = "python",
    ) -> CompletionResult:
        """专门的性能分析"""
        system_prompt = """你是一个专业的性能工程师。请分析代码的性能问题：

分析维度：
1. 时间复杂度分析
2. 空间复杂度分析
3. I/O瓶颈识别
4. 内存泄漏风险
5. 并发/并行机会
6. 缓存优化建议
7. 算法优化建议

输出格式：
1. 当前性能评估
2. 主要瓶颈（按影响排序）
3. 优化建议（预估收益）
4. 优化后的代码示例
5. 性能测试建议

请用中文回答，提供具体的数值估算。"""
        
        prompt = f"""请分析以下{language}代码的性能：

```{language}
{code}
```

请识别所有性能问题，并提供具体的优化方案。"""
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    async def analyze_architecture(
        self,
        code: str,
        language: str = "python",
    ) -> CompletionResult:
        """架构分析"""
        system_prompt = """你是一个软件架构师。请分析代码的架构设计：

分析维度：
1. 设计模式识别
2. 模块化程度
3. 耦合度分析
4. 内聚度分析
5. 扩展性评估
6. 技术债务评估
7. 架构建议

输出格式：
1. 当前架构概述
2. 识别的设计模式
3. 架构问题
4. 重构建议
5. 目标架构方案

请用中文回答，关注架构的长期可维护性。"""
        
        prompt = f"""请分析以下{language}代码的架构设计：

```{language}
{code}
```

请提供详细的架构分析和改进建议。"""
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    async def generate_tests(
        self,
        code: str,
        language: str = "python",
        test_framework: str = "pytest",
    ) -> CompletionResult:
        """生成测试用例"""
        system_prompt = f"""你是一个测试工程师。请为代码生成全面的测试用例：

测试策略：
1. 单元测试（边界条件、正常路径）
2. 集成测试（组件交互）
3. 异常测试（错误处理）
4. 性能测试（基准测试）
5. 安全测试（如果适用）

请使用{test_framework}框架。

输出格式：
1. 测试用例列表
2. 每个测试的说明
3. 完整的测试代码
4. 运行说明
5. 覆盖率目标

请用中文回答，测试代码要实际可运行。"""
        
        prompt = f"""请为以下{language}代码生成测试用例：

```{language}
{code}
```

请提供完整的、可运行的测试代码。"""
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    async def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "comprehensive",
    ) -> CompletionResult:
        """代码解释"""
        detail_instruction = {
            "brief": "简洁解释核心功能",
            "standard": "标准解释，包括主要逻辑",
            "comprehensive": "详细解释每个部分",
        }
        
        system_prompt = f"""你是一个技术讲师。请解释代码的工作原理：

解释深度：{detail_instruction.get(detail_level, "标准解释")}

输出格式：
1. 整体功能说明
2. 核心概念解释
3. 执行流程说明
4. 关键代码解释
5. 使用示例

请用中文回答，语言要清晰易懂。"""
        
        prompt = f"""请解释以下{language}代码：

```{language}
{code}
```

请详细说明代码的功能和工作原理。"""
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    async def suggest_refactoring(
        self,
        code: str,
        language: str = "python",
        target_style: Optional[str] = None,
    ) -> CompletionResult:
        """重构建议"""
        system_prompt = f"""你是一个代码重构专家。请提供重构建议：

目标风格：{target_style or "现代最佳实践"}

分析维度：
1. 代码复杂度
2. 可读性问题
3. 重复代码
4. 硬编码值
5. 错误处理
6. 命名规范

输出格式：
1. 当前问题列表
2. 重构优先级
3. 详细的重构步骤
4. 重构后的代码
5. 重构前后的对比

请用中文回答，关注代码质量提升。"""
        
        prompt = f"""请为以下{language}代码提供重构建议：

```{language}
{code}
```

请提供详细的重构方案和改进后的代码。"""
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    async def analyze_dependencies(
        self,
        project_structure: str,
        language: str = "python",
    ) -> CompletionResult:
        """依赖分析"""
        system_prompt = """你是一个依赖管理专家。请分析项目依赖：

分析维度：
1. 直接和传递依赖
2. 版本兼容性
3. 安全漏洞检查
4. 依赖必要性
5. 更新建议
6. 许可协议

输出格式：
1. 依赖概览
2. 问题依赖（如果有）
3. 安全评估
4. 优化建议
5. 版本建议

请用中文回答，关注依赖的安全性和必要性。"""
        
        prompt = f"""请分析以下{language}项目的依赖：

{project_structure}

请提供详细的依赖分析报告。"""
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    async def compare_alternatives(
        self,
        code: str,
        alternatives: List[str],
        language: str = "python",
        criteria: Optional[List[str]] = None,
    ) -> CompletionResult:
        """比较替代方案"""
        criteria = criteria or ["性能", "可读性", "可维护性", "生态系统", "学习曲线"]
        
        system_prompt = f"""你是一个技术顾问。请比较不同的实现方案：

比较标准：{', '.join(criteria)}

分析要求：
1. 分析每个方案的优势和劣势
2. 根据不同场景推荐方案
3. 权衡取舍说明
4. 最终建议

请用中文回答，提供清晰的推荐。"""
        
        prompt = f"""请比较以下{language}代码的替代实现方案：

原始代码：
```{language}
{code}
```

替代方案：
{chr(10).join(f"{i+1}. {alt}" for i, alt in enumerate(alternatives))}

请提供详细的对比分析和建议。"""
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    async def document_code(
        self,
        code: str,
        language: str = "python",
        doc_format: str = "docstring",
    ) -> CompletionResult:
        """生成代码文档"""
        system_prompt = f"""你是一个技术文档工程师。请为代码生成完整的文档：

文档格式：{doc_format}

文档要求：
1. 模块/类/函数说明
2. 参数和返回值
3. 异常说明
4. 使用示例
5. 注意事项
6. 复杂算法的解释

请用中文回答，文档要清晰、完整、准确。"""
        
        prompt = f"""请为以下{language}代码生成{doc_format}格式的文档：

```{language}
{code}
```

请提供完整的代码文档。"""
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    async def explain_error(
        self,
        error_message: str,
        code_context: Optional[str] = None,
        stack_trace: Optional[str] = None,
    ) -> CompletionResult:
        """解释错误"""
        system_prompt = """你是一个调试专家。请分析错误并提供解决方案：

分析要求：
1. 错误原因分析
2. 可能的根因
3. 解决方案（按优先级排序）
4. 预防措施
5. 相关资源链接

请用中文回答，保持实用和准确。"""
        
        prompt = f"""错误信息：
```
{error_message}
```
"""
        
        if stack_trace:
            prompt += f"\n堆栈跟踪：\n```\n{stack_trace}\n```\n"
        
        if code_context:
            prompt += f"\n相关代码：\n```\n{code_context}\n```\n"
        
        prompt += "\n请提供详细的错误分析和解决方案。"
        
        return await self.complete(prompt, system_prompt=system_prompt)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        avg_latency = (
            self.request_stats["total_latency"] / self.request_stats["total_requests"]
            if self.request_stats["total_requests"] > 0
            else 0
        )
        
        cache_hit_rate = (
            self.request_stats["cached_requests"] / self.request_stats["total_requests"]
            if self.request_stats["total_requests"] > 0
            else 0
        )
        
        return {
            **self.request_stats,
            "avg_latency": avg_latency,
            "cache_hit_rate": cache_hit_rate,
            "cache_size": len(self.cache.cache) if self.cache else 0,
        }
    
    def clear_history(self, conversation_id: Optional[str] = None):
        """清除历史"""
        if conversation_id:
            self.conversation_history.pop(conversation_id, None)
        else:
            self.conversation_history.clear()
    
    def clear_cache(self):
        """清除缓存"""
        if self.cache:
            self.cache.clear()
            logger.info("LLM cache cleared")
    
    async def close(self):
        """关闭管理器"""
        await self.client.close()


# 全局LLM管理器实例
_llm_manager: Optional[AdvancedLLMManager] = None


def get_llm_manager(config: Optional[LLMConfig] = None) -> AdvancedLLMManager:
    """获取LLM管理器实例"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = AdvancedLLMManager(config)
    return _llm_manager
