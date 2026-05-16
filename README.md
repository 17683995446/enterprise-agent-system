# Enterprise Agent System
# 企业级双模式 Agent 系统

## 📖 文档导航

- [快速开始](#quick-start)
- [架构说明](#architecture)
- [API 文档](#api-documentation)
- [配置指南](#configuration-guide)
- [部署说明](#deployment)
- [贡献指南](#contributing)

---

## <a name="quick-start"></a>🚀 快速开始

### 环境要求

- Python 3.9+
- 内存：推荐 4GB+
- 磁盘：1GB 可用空间

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/your-org/enterprise-agent-system.git
cd enterprise-agent-system
```

2. 创建虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境（可选）
```bash
cp .env.example .env
# 编辑 .env 文件
```

5. 运行演示
```bash
python demo_llm_integration.py
```

### 启动服务

#### API 服务
```bash
python -m uvicorn src.enterprise_agent_system.infrastructure.api.api_server:app --host 0.0.0.0 --port 8000
```

#### CLI 工具
```bash
python cli.py analyze <file-or-directory>
python cli.py chat
python cli.py stats
```

---

## <a name="architecture"></a>🏗️ 架构说明

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                          API 层 (FastAPI)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │LLM Analy│  │Reports   │  │Tasks     │  │Agents    │       │
│  │Endpoints│  │Endpoints  │  │Endpoints │  │Endpoints │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
┌───────▼───────────┐      ┌────────▼─────────────┐
│  应用服务层         │      │  基础设施层            │
├───────────────────┤      ├──────────────────────┤
│ - LLM 分析        │      │ - 配置管理            │
│ - 数据管道        │      │ - 高级日志            │
│ - RAG 系统        │      │ - 报告存储            │
│ - 项目分析        │      │ - Redis 缓存         │
└───────────────────┘      └──────────────────────┘
                      │
┌─────────────────────┴───────────────────────────┐
│                 数据库                          │
│             (SQLite/PostgreSQL)                │
└─────────────────────────────────────────────────┘
```

### 主要模块

| 模块 | 功能 | 位置 |
|------|------|------|
| LLM 集成 | 多模型支持、缓存、对话管理 | `infrastructure/llm_integration.py` |
| 静态分析 | 安全、性能、最佳实践检查 | `application/enhanced_analysis_system.py` |
| RAG 系统 | 知识库、向量存储、语义搜索 | `application/rag_system.py` |
| 数据管道 | 批量处理、项目扫描 | `application/data_pipeline.py` |
| 配置管理 | 多环境配置、热重载 | `infrastructure/config_manager.py` |
| 高级日志 | 结构化日志、监控指标 | `infrastructure/advanced_logging.py` |
| 报告存储 | 分析报告的持久化 | `infrastructure/analysis_report_store.py` |

---

## <a name="api-documentation"></a>📚 API 文档

### 通用响应格式

所有 API 响应统一格式：

```json
{
  "status": "success",
  "data": { ... },
  "meta": { ... },
  "timestamp": "2024-05-16T12:00:00Z"
}
```

### LLM 分析 API

#### 分析代码
```http
POST /api/v1/llm/analyze/code
Content-Type: application/json

{
  "code": "def add(a, b): return a + b",
  "language": "python",
  "analysis_type": "comprehensive",
  "depth": "deep"
}
```

#### 分析文件
```http
POST /api/v1/llm/analyze/file
Content-Type: application/json

{
  "file_path": "/path/to/file.py"
}
```

#### 深度安全分析
```http
POST /api/v1/llm/analyze/security-deep
Content-Type: application/json

{
  "code": "import pickle; pickle.loads(data)",
  "language": "python"
}
```

#### 获取统计信息
```http
GET /api/v1/llm/stats
```

### 报告管理 API

#### 列出报告
```http
GET /api/v1/reports/?report_type=python&min_score=0.8
```

#### 获取单个报告
```http
GET /api/v1/reports/{report_id}
```

#### 删除报告
```http
DELETE /api/v1/reports/{report_id}
```

#### 获取报告统计
```http
GET /api/v1/reports/stats/summary
```

---

## <a name="configuration-guide"></a>⚙️ 配置指南

### 配置文件

主要配置文件位于 `config/default.yaml`。也可以根据环境创建 `config/development.yaml` 或 `config/production.yaml`。

### 配置项

#### LLM 配置
```yaml
llm:
  provider: "silicon_flow"
  api_key: "${SILICON_FLOW_API_KEY}"
  model: "Qwen/Qwen2.5-7B-Instruct"
  temperature: 0.7
  max_tokens: 4096
```

#### API 配置
```yaml
api:
  host: "0.0.0.0"
  port: 8000
  rate_limit:
    enabled: true
    requests_per_minute: 100
```

#### 日志配置
```yaml
logging:
  level: "INFO"
  format: "json"  # 或 "text"
  file: "/var/log/enterprise_agent/app.log"
```

### 环境变量

可以通过环境变量覆盖配置，格式为 `EA_` 前缀：

```bash
export EA_LLM_API_KEY="your-api-key"
export EA_API_PORT=8080
export EA_LOGGING_LEVEL="DEBUG"
```

---

## <a name="deployment"></a>🚢 部署说明

### Docker 部署

创建 Dockerfile：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.enterprise_agent_system.infrastructure.api.api_server:app", \
     "--host", "0.0.0.0", "--port", "8000"]
```

### 使用 Docker Compose

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db/enterprise_agent
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: enterprise_agent
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:7-alpine
```

---

## <a name="contributing"></a>🤝 贡献指南

### 开发环境

1. 安装开发依赖
```bash
pip install -r requirements.txt
pip install black isort flake8 mypy pytest
```

2. 安装预提交钩子
```bash
pip install pre-commit
pre-commit install
```

### 开发流程

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/awesome-feature`)
3. 提交更改 (`git commit -m 'feat: Add awesome feature'`)
4. 推送到分支 (`git push origin feature/awesome-feature`)
5. 提交 Pull Request

### 代码规范

- 使用 `black` 自动格式化代码
- 使用 `isort` 组织导入
- 使用 `flake8` 检查代码风格
- 使用 `mypy` 做类型检查
- 编写测试用例

### 测试命令

```bash
# 运行所有测试
pytest src -v

# 特定模块测试
pytest src/enterprise_agent_system/test_suite/

# 运行基准测试
python -m src.enterprise_agent_system.benchmarking.performance_benchmark
```

---

## 📞 社区与支持

- 问题报告：GitHub Issues
- 讨论：GitHub Discussions
- 安全漏洞：请私下联系

---

## 📄 许可证

本项目采用 MIT 许可证。
