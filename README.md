# Enterprise Dual-Mode Agent System

Multi-layered enterprise-grade AI agent system with dual-mode operation (task execution and idle improvement).

## Features

- Dual-mode operation (Task Execution + Idle Improvement)
- Knowledge graph memory
- Priority-based task scheduling
- REST API with FastAPI
- Prometheus metrics
- Docker deployment

## Quick Start

### CLI Mode

```bash
python -m enterprise_agent_system
python -m enterprise_agent_system demo
python -m enterprise_agent_system test
```

### Docker Mode

```bash
docker-compose up --build
```

### API Mode

```bash
uvicorn enterprise_agent_system.infrastructure.fastapi_rest_api_application:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /docs` - Swagger UI
- `POST /tasks` - Create task
- `GET /tasks/` - List tasks
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

## Testing

```bash
pytest src/enterprise_agent_system/test_suite/ -v
```
