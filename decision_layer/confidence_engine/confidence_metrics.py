import time
from typing import List, Dict, Any
from decision_layer.confidence_engine.models import ConfidenceMetrics

class ConfidenceMetricsTracker:
    """Submodule 8: Telemetry logger tracking confidence growth rates and latencies."""
    def __init__(self):
        self.start_time = 0.0
        self.estimation_latency = 0.0
        self.failed_estimations = 0

    def start_timer(self) -> None:
        self.start_time = time.time()

    def stop_timer(self) -> None:
        self.estimation_latency = time.time() - self.start_time

    def log_failed(self) -> None:
        self.failed_estimations += 1

    def compile_metrics(self, current_conf: float, last_change: float, history: List[Dict[str, Any]]) -> ConfidenceMetrics:
        # Calculate running average confidence
        total = current_conf
        count = 1
        for record in history:
            total += record.get("updated_confidence", 0.85)
            count += 1
            
        return ConfidenceMetrics(
            current_confidence=current_conf,
            confidence_change=last_change,
            average_confidence=total / count,
            failed_estimations=self.failed_estimations,
            estimation_latency=self.estimation_latency
        )
