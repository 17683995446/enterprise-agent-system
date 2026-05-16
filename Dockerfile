FROM python:3.11-slim

LABEL maintainer="Enterprise Agent Team"
LABEL version="8.0.0"
LABEL description="Enterprise Dual-Mode Agent System"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

ENV AGENT_APPLICATION_NAME="Enterprise Dual-Mode Agent System"
ENV AGENT_API_PORT_NUMBER=8000
ENV AGENT_DEBUG_MODE_ENABLED=false
ENV DATABASE_PATH=/app/data/agent_system.db

VOLUME ["/app/data"]

USER nobody

ENTRYPOINT ["python", "-m", "enterprise_agent_system.application.complete_system_runner"]
CMD ["api", "--host", "0.0.0.0", "--port", "8000"]
