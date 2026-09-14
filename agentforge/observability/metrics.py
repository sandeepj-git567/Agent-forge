"""
System Telemetry and Metrics Collector for AgentForge AI
"""
import time
from typing import Any


class TelemetryCollector:
    """In-memory telemetry collector tracking requests, task executions, RAG queries, and latencies."""

    def __init__(self) -> None:
        self.total_requests = 0
        self.total_tasks_run = 0
        self.total_rag_queries = 0
        self.total_errors = 0
        self.total_evaluations = 0
        self._latencies: list[float] = []

    def record_request(self, latency_ms: float, is_error: bool = False) -> None:
        """Record an HTTP request event."""
        self.total_requests += 1
        if is_error:
            self.total_errors += 1
        self._latencies.append(latency_ms)
        if len(self._latencies) > 1000:
            self._latencies = self._latencies[-1000:]

    def record_task_run(self) -> None:
        """Increment total task executions counter."""
        self.total_tasks_run += 1

    def record_rag_query(self) -> None:
        """Increment total RAG search queries counter."""
        self.total_rag_queries += 1

    def record_evaluation(self) -> None:
        """Increment total evaluation executions counter."""
        self.total_evaluations += 1

    def get_summary(self) -> dict[str, Any]:
        """Return aggregated telemetry metrics summary."""
        avg_latency = round(sum(self._latencies) / max(len(self._latencies), 1), 2) if self._latencies else 0.0
        error_rate = round(self.total_errors / max(self.total_requests, 1), 4)

        return {
            "total_requests": self.total_requests,
            "total_tasks_run": self.total_tasks_run,
            "total_rag_queries": self.total_rag_queries,
            "total_evaluations": self.total_evaluations,
            "total_errors": self.total_errors,
            "error_rate": error_rate,
            "avg_latency_ms": avg_latency,
            "sample_size": len(self._latencies)
        }


default_telemetry_collector = TelemetryCollector()
