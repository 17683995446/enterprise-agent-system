"""
OpenAPI Documentation Generator for Enterprise Agent System
应用层 - OpenAPI文档自动生成器
"""

from fastapi import FastAPI, Request
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any, Optional
import json
from datetime import datetime
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance


logger = get_logger_instance(__name__)


class OpenAPIDocsGenerator:
    """OpenAPI文档生成器"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.title = "Enterprise Agent System API"
        self.version = "2.0.0"
        self.description = """
## 🏢 企业级双模式Agent系统

Enterprise-level Dual-Mode Agent System with Knowledge Graph Memory

### 主要功能

- 🤖 **双模式执行**: 任务执行模式 + 空闲改进模式
- 🧠 **知识图谱记忆**: 从任务中提取并构建语义记忆
- ⚡ **优先级调度**: URGENT > HIGH > MEDIUM > LOW 任务调度
- 📊 **分布式执行**: Redis + Celery 分布式任务队列
- 🔍 **项目分析**: GitHub仓库和TypeScript/Vue.js项目分析
- 📈 **性能监控**: Prometheus + Grafana 实时监控

### 认证方式

本API使用API Key进行认证，请在请求头中添加：

```
X-API-Key: your-api-key-here
```

### 限流策略

- 默认：100请求/分钟
- 企业版：1000请求/分钟
- 超限返回 `429 Too Many Requests`

### 错误代码

| 代码 | 描述 |
|------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

### 版本历史

- **v2.0.0** (2026-05-16): 添加分布式任务执行和监控
- **v1.0.0** (2026-01-01): 初始版本
        """
        self.contact = {
            "name": "Enterprise Agent System Team",
            "email": "contact@enterprise-agent.com",
            "url": "https://github.com/17683995446/enterprise-agent-system",
        }
        self.license_info = {
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        }
    
    def generate_openapi_schema(self) -> Dict[str, Any]:
        """生成OpenAPI schema"""
        
        if self.app.openapi_schema:
            return self.app.openapi_schema
        
        openapi_schema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.app.routes,
            contact=self.contact,
            license_info=self.license_info,
        )
        
        # 添加额外信息
        openapi_schema["info"]["x-logo"] = {
            "url": "https://via.placeholder.com/200x80?text=Agent+System"
        }
        
        openapi_schema["info"]["x-readme"] = {
            "version": self.version,
            "lastUpdated": datetime.now().isoformat(),
            "generator": "OpenAPIDocsGenerator v1.0",
        }
        
        # 添加标签定义
        openapi_schema["tags"] = [
            {
                "name": "Tasks",
                "description": "任务管理接口",
                "externalDocs": {
                    "description": "任务管理文档",
                    "url": "https://docs.enterprise-agent.com/tasks",
                },
            },
            {
                "name": "Agents",
                "description": "Agent管理接口",
                "externalDocs": {
                    "description": "Agent管理文档",
                    "url": "https://docs.enterprise-agent.com/agents",
                },
            },
            {
                "name": "Memory",
                "description": "知识图谱记忆接口",
                "externalDocs": {
                    "description": "知识图谱文档",
                    "url": "https://docs.enterprise-agent.com/memory",
                },
            },
            {
                "name": "Projects",
                "description": "项目分析接口",
                "externalDocs": {
                    "description": "项目分析文档",
                    "url": "https://docs.enterprise-agent.com/projects",
                },
            },
            {
                "name": "Monitoring",
                "description": "系统监控接口",
                "externalDocs": {
                    "description": "监控文档",
                    "url": "https://docs.enterprise-agent.com/monitoring",
                },
            },
        ]
        
        # 添加安全方案
        openapi_schema["components"]["securitySchemes"] = {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "API密钥认证",
            },
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT Bearer Token认证",
            },
        }
        
        # 添加通用响应
        openapi_schema["components"]["responses"] = {
            "400": {
                "description": "请求参数错误",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"},
                                "detail": {"type": "string"},
                                "code": {"type": "string"},
                            },
                        },
                        "example": {
                            "error": "Invalid request parameters",
                            "detail": "The 'task_title' field is required",
                            "code": "INVALID_PARAMS",
                        },
                    },
                },
            },
            "401": {
                "description": "未授权",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"},
                                "detail": {"type": "string"},
                            },
                        },
                        "example": {
                            "error": "Unauthorized",
                            "detail": "Invalid or missing API key",
                        },
                    },
                },
            },
            "404": {
                "description": "资源不存在",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"},
                                "detail": {"type": "string"},
                            },
                        },
                    },
                },
            },
            "429": {
                "description": "请求过于频繁",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"},
                                "retry_after": {"type": "integer"},
                            },
                        },
                        "example": {
                            "error": "Too many requests",
                            "retry_after": 60,
                        },
                    },
                },
            },
            "500": {
                "description": "服务器内部错误",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"},
                                "request_id": {"type": "string"},
                            },
                        },
                    },
                },
            },
        }
        
        # 添加通用参数
        openapi_schema["components"]["parameters"] = {
            "page": {
                "name": "page",
                "in": "query",
                "description": "页码",
                "required": False,
                "schema": {
                    "type": "integer",
                    "default": 1,
                    "minimum": 1,
                },
            },
            "page_size": {
                "name": "page_size",
                "in": "query",
                "description": "每页数量",
                "required": False,
                "schema": {
                    "type": "integer",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            "sort_by": {
                "name": "sort_by",
                "in": "query",
                "description": "排序字段",
                "required": False,
                "schema": {
                    "type": "string",
                    "enum": ["created_at", "updated_at", "priority", "status"],
                },
            },
            "order": {
                "name": "order",
                "in": "query",
                "description": "排序方向",
                "required": False,
                "schema": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "default": "desc",
                },
            },
        }
        
        self.app.openapi_schema = openapi_schema
        return openapi_schema
    
    def get_custom_swagger_ui_html(self) -> HTMLResponse:
        """获取自定义Swagger UI HTML"""
        return HTMLResponse(
            content=get_swagger_ui_html(
                openapi_url=self.app.openapi_url,
                title=self.title,
                oauth2_redirect_url=self.app.swagger_ui_oauth2_redirect_url,
                swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
                swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
            )
        )
    
    def get_custom_redoc_html(self) -> HTMLResponse:
        """获取自定义ReDoc HTML"""
        return HTMLResponse(
            content=get_redoc_html(
                openapi_url=self.app.openapi_url,
                title=self.title,
                redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
            )
        )
    
    def export_openapi_json(self, file_path: str) -> bool:
        """导出OpenAPI JSON文件"""
        try:
            schema = self.generate_openapi_schema()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            logger.info(f"OpenAPI schema exported to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export OpenAPI schema: {e}")
            return False
    
    def export_openapi_yaml(self, file_path: str) -> bool:
        """导出OpenAPI YAML文件"""
        try:
            import yaml
            schema = self.generate_openapi_schema()
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(schema, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"OpenAPI schema exported to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export OpenAPI YAML: {e}")
            return False


class HTMLResponse:
    """HTML响应类"""
    
    def __init__(self, content: str, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {"content-type": "text/html; charset=utf-8"}
    
    async def __call__(self, scope, receive, send):
        """ASGI应用"""
        await send({
            "type": "http.response.start",
            "status": self.status_code,
            "headers": [(k.encode(), v.encode()) for k, v in self.headers.items()],
        })
        await send({
            "type": "http.response.body",
            "body": self.content.encode(),
        })


def setup_openapi_docs(app: FastAPI) -> OpenAPIDocsGenerator:
    """
    设置OpenAPI文档
    
    Args:
        app: FastAPI应用实例
    
    Returns:
        OpenAPI文档生成器
    """
    generator = OpenAPIDocsGenerator(app)
    
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """自定义Swagger UI"""
        return generator.get_custom_swagger_ui_html()
    
    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc_html():
        """自定义ReDoc"""
        return generator.get_custom_redoc_html()
    
    @app.get("/api-docs.json", include_in_schema=False, response_model=dict)
    async def get_openapi_json():
        """获取OpenAPI JSON"""
        return generator.generate_openapi_schema()
    
    @app.get("/api-docs.yaml", include_in_schema=False)
    async def get_openapi_yaml():
        """获取OpenAPI YAML"""
        import yaml
        return YAMLResponse(
            yaml.dump(generator.generate_openapi_schema())
        )
    
    @app.get("/api-docs/validate", include_in_schema=False)
    async def validate_openapi():
        """验证OpenAPI文档"""
        schema = generator.generate_openapi_schema()
        
        # 基本验证
        errors = []
        
        if "openapi" not in schema:
            errors.append("Missing 'openapi' field")
        
        if "info" not in schema:
            errors.append("Missing 'info' field")
        
        if "paths" not in schema:
            errors.append("Missing 'paths' field")
        
        if "components" not in schema:
            errors.append("Missing 'components' field")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "schema_version": schema.get("openapi"),
            "paths_count": len(schema.get("paths", {})),
            "components_count": len(schema.get("components", {})),
        }
    
    return generator


class YAMLResponse:
    """YAML响应类"""
    
    def __init__(self, content: str):
        self.content = content
    
    async def __call__(self, scope, receive, send):
        """ASGI应用"""
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"application/x-yaml; charset=utf-8"),
            ],
        })
        await send({
            "type": "http.response.body",
            "body": self.content.encode(),
        })
