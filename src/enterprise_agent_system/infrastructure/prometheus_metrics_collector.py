"""
Infrastructure Layer - Prometheus Metrics Collection
基础设施层 - Prometheus 指标采集

Provides system metrics collection for monitoring and observability.
Integrates with Prometheus for metrics scraping.
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

try:
    from prometheus_client import Counter, Gauge, Histogram, Info, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    SystemHealthStatusEnumeration,
    AgentOperatingModeEnumeration,
)


@dataclass
class SystemMetricsCollector:
    """
    System metrics collector for Prometheus integration

    Tracks:
    - Task execution metrics
    - Agent performance metrics
    - System health metrics
    - Knowledge graph metrics
    """

    application_start_time: float = field(default_factory=time.time)
    tasks_created_total: int = 0
    tasks_completed_total: int = 0
    tasks_failed_total: int = 0
    tasks_in_progress: int = 0
    memories_created_total: int = 0
    experiences_recorded_total: int = 0
    knowledge_graph_nodes_total: int = 0
    knowledge_graph_edges_total: int = 0
    current_agent_mode: AgentOperatingModeEnumeration = AgentOperatingModeEnumeration.PAUSED_MODE
    health_status: SystemHealthStatusEnumeration = SystemHealthStatusEnumeration.HEALTHY_STATUS

    def record_task_created(self) -> None:
        """Record a new task creation"""
        self.tasks_created_total += 1

    def record_task_completed(self) -> None:
        """Record a task completion"""
        self.tasks_completed_total += 1
        self.tasks_in_progress = max(0, self.tasks_in_progress - 1)

    def record_task_failed(self) -> None:
        """Record a task failure"""
        self.tasks_failed_total += 1
        self.tasks_in_progress = max(0, self.tasks_in_progress - 1)

    def record_task_started(self) -> None:
        """Record a task started"""
        self.tasks_in_progress += 1

    def record_memory_created(self) -> None:
        """Record a new memory"""
        self.memories_created_total += 1

    def record_experience_recorded(self) -> None:
        """Record a new experience"""
        self.experiences_recorded_total += 1

    def update_knowledge_graph_stats(self, nodes: int, edges: int) -> None:
        """Update knowledge graph statistics"""
        self.knowledge_graph_nodes_total = nodes
        self.knowledge_graph_edges_total = edges

    def set_agent_mode(self, mode: AgentOperatingModeEnumeration) -> None:
        """Set current agent mode"""
        self.current_agent_mode = mode

    def set_health_status(self, status: SystemHealthStatusEnumeration) -> None:
        """Set system health status"""
        self.health_status = status

    def get_uptime_seconds(self) -> float:
        """Get system uptime in seconds"""
        return time.time() - self.application_start_time

    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = self.tasks_completed_total + self.tasks_failed_total
        if total == 0:
            return 0.0
        return (self.tasks_completed_total / total) * 100

    def to_prometheus_format(self) -> str:
        """Export metrics in Prometheus text format"""
        if not PROMETHEUS_AVAILABLE:
            return "# Prometheus client not available\n"

        output = []

        output.append(f"# HELP agent_tasks_created_total Total number of tasks created")
        output.append(f"# TYPE agent_tasks_created_total counter")
        output.append(f"agent_tasks_created_total {self.tasks_created_total}\n")

        output.append(f"# HELP agent_tasks_completed_total Total number of tasks completed")
        output.append(f"# TYPE agent_tasks_completed_total counter")
        output.append(f"agent_tasks_completed_total {self.tasks_completed_total}\n")

        output.append(f"# HELP agent_tasks_failed_total Total number of tasks failed")
        output.append(f"# TYPE agent_tasks_failed_total counter")
        output.append(f"agent_tasks_failed_total {self.tasks_failed_total}\n")

        output.append(f"# HELP agent_tasks_in_progress Current number of tasks in progress")
        output.append(f"# TYPE agent_tasks_in_progress gauge")
        output.append(f"agent_tasks_in_progress {self.tasks_in_progress}\n")

        output.append(f"# HELP agent_memories_total Total number of memories")
        output.append(f"# TYPE agent_memories_total counter")
        output.append(f"agent_memories_total {self.memories_created_total}\n")

        output.append(f"# HELP agent_experiences_total Total number of experiences")
        output.append(f"# TYPE agent_experiences_total counter")
        output.append(f"agent_experiences_total {self.experiences_recorded_total}\n")

        output.append(f"# HELP agent_knowledge_graph_nodes_total Total knowledge graph nodes")
        output.append(f"# TYPE agent_knowledge_graph_nodes_total gauge")
        output.append(f"agent_knowledge_graph_nodes_total {self.knowledge_graph_nodes_total}\n")

        output.append(f"# HELP agent_knowledge_graph_edges_total Total knowledge graph edges")
        output.append(f"# TYPE agent_knowledge_graph_edges_total gauge")
        output.append(f"agent_knowledge_graph_edges_total {self.knowledge_graph_edges_total}\n")

        output.append(f"# HELP agent_uptime_seconds System uptime in seconds")
        output.append(f"# TYPE agent_uptime_seconds gauge")
        output.append(f"agent_uptime_seconds {self.get_uptime_seconds():.2f}\n")

        output.append(f"# HELP agent_success_rate_percentage Task success rate")
        output.append(f"# TYPE agent_success_rate_percentage gauge")
        output.append(f"agent_success_rate_percentage {self.get_success_rate():.2f}\n")

        output.append(f"# HELP agent_health_status System health status (1=healthy, 0.5=degraded, 0=unhealthy)")
        output.append(f"# TYPE agent_health_status gauge")
        health_value = 1.0 if self.health_status == SystemHealthStatusEnumeration.HEALTHY_STATUS else (
            0.5 if self.health_status == SystemHealthStatusEnumeration.DEGRADED_STATUS else 0.0
        )
        output.append(f"agent_health_status {health_value}\n")

        return "\n".join(output)

    def to_dict(self) -> Dict:
        """Export metrics as dictionary"""
        return {
            "tasks_created_total": self.tasks_created_total,
            "tasks_completed_total": self.tasks_completed_total,
            "tasks_failed_total": self.tasks_failed_total,
            "tasks_in_progress": self.tasks_in_progress,
            "memories_created_total": self.memories_created_total,
            "experiences_recorded_total": self.experiences_recorded_total,
            "knowledge_graph_nodes_total": self.knowledge_graph_nodes_total,
            "knowledge_graph_edges_total": self.knowledge_graph_edges_total,
            "uptime_seconds": self.get_uptime_seconds(),
            "success_rate_percentage": self.get_success_rate(),
            "current_agent_mode": self.current_agent_mode.value,
            "health_status": self.health_status.value,
        }


_global_metrics_collector: Optional[SystemMetricsCollector] = None


def get_metrics_collector() -> SystemMetricsCollector:
    """
    Get global metrics collector instance

    Returns:
        System metrics collector singleton
    """
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = SystemMetricsCollector()
    return _global_metrics_collector


def reset_metrics_collector() -> None:
    """Reset global metrics collector"""
    global _global_metrics_collector
    _global_metrics_collector = None
