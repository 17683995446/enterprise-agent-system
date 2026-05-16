# Enterprise Dual-Mode Perpetual Agent System v8.0.0

**企业级双模式永续 Agent 系统**

---

## 📋 项目概述

一个高度模块化、工程化的智能 Agent 系统，具有以下核心功能：

- **双重运行模式**：任务执行模式 + 空闲改进模式
- **知识图谱记忆**：从任务中学习并构建语义记忆
- **优先级任务调度**：支持 URGENT > HIGH > MEDIUM > LOW
- **完整监控统计**：实时健康检查和性能指标
- **企业级架构**：清晰分层，高度模块化

---

## 🏗️ 项目架构（清晰分层，见名知意）

```
enterprise_agent_system/
├── src/
│   └── enterprise_agent_system/
│       ├── __init__.py
│       ├── __main__.py
│       │
│       ├── domain/
│       │   └── core_data_models_and_enumerations.py
│       │
│       ├── core/
│       │   ├── agent_orchestrator_and_executor.py
│       │   └── in_memory_data_storage_backend.py
│       │
│       ├── infrastructure/
│       │   ├── application_configuration_management.py
│       │   └── enterprise_logging_system.py
│       │
│       ├── application/
│       │   └── command_line_interface_application.py
│       │
│       └── test_suite/
│           ├── unit/
│           │   ├── test_domain_models.py
│           │   └── test_storage_backend.py
│           └── integration/
│               └── test_agent_integration.py
```

---

## 📝 文件命名规范（4+ 单词，见名知意）

| 文件名（4+ 单词） | 说明 |
|-----------------|------|
| `core_data_models_and_enumerations.py` | 核心数据模型和枚举 |
| `agent_orchestrator_and_executor.py` | Agent 编排器和执行器 |
| `in_memory_data_storage_backend.py` | 内存数据存储后端 |
| `application_configuration_management.py` | 应用配置管理 |
| `enterprise_logging_system.py` | 企业级日志系统 |
| `command_line_interface_application.py` | 命令行界面应用程序 |

---

## 🚀 快速开始

### 安装

```bash
# 进入项目目录
cd enterprise_agent_system/src

# 运行演示（无需依赖！）
python -m enterprise_agent_system demo

# 运行测试
python -m enterprise_agent_system test
```

### 可选依赖

```bash
pip install rich
```

---

## 📦 核心模块

### Domain Layer（领域层）

```python
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionDataModel,
    MemoryStorageDataModel,
    ExperienceLearningDataModel,
    TaskPriorityLevelEnumeration,
)
```

### Core Layer（核心层）

```python
from enterprise_agent_system.core.agent_orchestrator_and_executor import (
    AgentOrchestratorAndExecutor,
)

agent = AgentOrchestratorAndExecutor("My Agent")
task_id = agent.create_and_queue_task(
    "Data Analysis Task",
    "Analyze customer data",
    priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL
)
```

### Infrastructure Layer（基础设施层）

```python
from enterprise_agent_system.infrastructure.application_configuration_management import (
    get_application_configuration_instance,
)
from enterprise_agent_system.infrastructure.enterprise_logging_system import (
    get_logger_instance,
)
```

### Application Layer（应用层）

```python
from enterprise_agent_system.application.command_line_interface_application import (
    CommandLineInterfaceApplication,
)
```

---

## 📊 功能特性

| 功能 | 描述 |
|------|------|
| **双重模式运行** | 任务执行 + 空闲改进 |
| **优先级调度** | URGENT > HIGH > MEDIUM > LOW |
| **知识图谱记忆** | 图结构语义记忆 |
| **自我学习** | 从每个任务中学习 |
| **完整统计** | 实时指标和监控 |
| **企业级日志** | 结构化日志记录 |

---

## 🧪 测试

```bash
python -m enterprise_agent_system test
```

---

## 📄 许可证

MIT License

---

**Built with ❤️ by Enterprise Agent Engineering Team**
