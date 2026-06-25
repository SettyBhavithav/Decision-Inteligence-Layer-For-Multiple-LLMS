import time
import numpy as np
from typing import List

DECISION_ACTIONS = ["ACCEPT", "VERIFY", "REJECT", "REGENERATE"]

class DecisionMetrics:
    """Category 4: Decision Evaluation — Accept/Verify/Reject/Regenerate rates, Latency."""
    def __init__(self):
        self.decisions: List[str] = []
        self.latencies: List[float] = []

    def log_decision(self, action: str, latency_seconds: float) -> None:
        self.decisions.append(action.upper())
        self.latencies.append(latency_seconds)

    def _rate(self, action: str) -> float:
        if not self.decisions:
            return 0.0
        return round(self.decisions.count(action) / len(self.decisions), 4)

    def accept_rate(self) -> float:
        return self._rate("ACCEPT")

    def verify_rate(self) -> float:
        return self._rate("VERIFY")

    def reject_rate(self) -> float:
        return self._rate("REJECT")

    def regenerate_rate(self) -> float:
        return self._rate("REGENERATE")

    def average_latency(self) -> float:
        return round(float(np.mean(self.latencies)), 4) if self.latencies else 0.0

    def summary(self) -> dict:
        return {
            "accept_rate": self.accept_rate(),
            "verify_rate": self.verify_rate(),
            "reject_rate": self.reject_rate(),
            "regenerate_rate": self.regenerate_rate(),
            "total_decisions": len(self.decisions),
            "average_decision_latency_s": self.average_latency(),
        }
