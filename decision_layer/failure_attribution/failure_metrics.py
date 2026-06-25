import time
from typing import List, Dict, Any
from decision_layer.failure_attribution.models import FailureMetrics

class FailureMetricsTracker:
    """Submodule 10: Telemetry logger tracking failure type frequencies and latency audits."""
    def __init__(self):
        self.start_time = 0.0
        self.latency = 0.0
        self.total_failures = 0
        self.type_counts = {}
        self.agent_counts = {}
        self.total_penalties = 0.0

    def start_timer(self) -> None:
        self.start_time = time.time()

    def stop_timer(self) -> None:
        self.latency = time.time() - self.start_time

    def log_failure_event(self, failure_type: str, culprit_agent: str, penalty: float = 0.0) -> None:
        self.total_failures += 1
        self.type_counts[failure_type] = self.type_counts.get(failure_type, 0) + 1
        self.agent_counts[culprit_agent] = self.agent_counts.get(culprit_agent, 0) + 1
        self.total_penalties += penalty

    def compile_metrics(self) -> FailureMetrics:
        return FailureMetrics(
            total_failures=self.total_failures,
            type_distribution=dict(self.type_counts),
            agent_distribution=dict(self.agent_counts),
            attribution_latency=self.latency,
            trust_penalties=self.total_penalties
        )
