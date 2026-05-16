"""
End-to-End Integration Tests
端到端集成测试 - 完整流程测试
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from enterprise_agent_system.infrastructure.api.api_server import app
from enterprise_agent_system.application.llm_analysis_system import EnhancedCodeAnalyzer
from enterprise_agent_system.application.data_pipeline import DataPipeline, FileAnalysisTask


class TestAPIIntegration:
    """API集成测试"""
    
    def test_root_endpoint(self):
        """测试根端点"""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "name" in response.json()["data"]
    
    def test_health_endpoint(self):
        """测试健康检查端点"""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "healthy"


class TestLLMAnalysisIntegration:
    """LLM分析集成测试"""
    
    @pytest.mark.asyncio
    async def test_code_analysis_flow(self):
        """测试代码分析流程"""
        analyzer = EnhancedCodeAnalyzer()
        
        sample_code = """
def add(a, b):
    return a + b
"""
        
        with patch.object(analyzer.llm.client, 'complete', new_callable=AsyncMock) as mock_complete:
            mock_complete.return_value = type('obj', (object,), {
                'content': 'Code analysis result',
                'latency': 1.0,
                'usage': {'total_tokens': 100}
            })()
            
            result = await analyzer.llm.analyze_code(
                code=sample_code,
                language="python"
            )
            
            assert result.content == 'Code analysis result'
            assert result.latency == 1.0


class TestDataPipelineIntegration:
    """数据管道集成测试"""
    
    def test_pipeline_creation(self):
        """测试管道创建"""
        pipeline = DataPipeline(max_workers=5)
        assert pipeline.max_workers == 5
        assert pipeline.progress.total_tasks == 0
    
    def test_file_task_creation(self):
        """测试文件任务创建"""
        task = FileAnalysisTask(
            file_path="test.py",
            file_type="py",
            language="python"
        )
        
        assert task.file_path == "test.py"
        assert task.language == "python"
        assert task.status == "pending"


class TestModuleIntegration:
    """模块集成测试"""
    
    def test_config_module(self):
        """测试配置模块"""
        from enterprise_agent_system.infrastructure.config_manager import get_config
        config = get_config()
        assert config is not None
        assert config.llm.model is not None
    
    def test_logging_module(self):
        """测试日志模块"""
        from enterprise_agent_system.infrastructure.advanced_logging import get_logger
        logger = get_logger("test")
        assert logger is not None
    
    def test_error_handling_module(self):
        """测试错误处理模块"""
        from enterprise_agent_system.infrastructure.error_handling import ErrorHandler
        error = ValueError("Test")
        result = ErrorHandler.handle(error)
        assert result["error"] == "INTERNAL_ERROR"


class TestCacheIntegration:
    """缓存集成测试"""
    
    def test_cache_manager(self):
        """测试缓存管理器"""
        from enterprise_agent_system.infrastructure.redis_cache import get_cache_manager
        cache = get_cache_manager()
        assert cache is not None
        assert isinstance(cache.get_stats(), dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
