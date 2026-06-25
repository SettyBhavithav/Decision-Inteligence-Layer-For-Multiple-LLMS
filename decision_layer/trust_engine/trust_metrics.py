import time
from typing import List, Dict, Any
from decision_layer.trust_engine.models import TrustMetrics

class TrustMetricsTracker:
    """Submodule 8: Telemetry logger tracking trust growth rates and latencies."""
    def __init__(self):
        self.start_time = 0.0
        self.update_time = 0.0
        self.failed_updates = 0

    def start_timer(self) -> None:
        self.start_time = time.time()

    def stop_timer(self) -> None:
        self.update_time = time.time() - self.start_time

    def log_failed(self) -> None:
        self.failed_updates += 1

    def compile_metrics(self, current_trust: float, last_change: float, history: List[Dict[str, Any]]) -> TrustMetrics:
        # Calculate running average trust
        total = current_trust
        count = 1
        for record in history:
            total += record.get("updated_trust", 0.80)
            count += 1
            
        return TrustMetrics(
            current_trust=current_trust,
            trust_change=last_change,
            average_trust=total / count,
            failed_updates=self.failed_updates,
            update_time=self.update_time
        )
