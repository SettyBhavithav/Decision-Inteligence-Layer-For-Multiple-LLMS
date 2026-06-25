import numpy as np
from typing import List, Dict, Any

class AttributionMetrics:
    """Category 6: Failure Attribution — Top-1/2 Accuracy, Recovery Rate, Mean Recovery Time."""
    def __init__(self):
        # Each entry: {"ground_truth": str, "top1": str, "top2": str, "recovered": bool, "recovery_time_s": float}
        self.attribution_events: List[Dict[str, Any]] = []

    def log_attribution(self, ground_truth_agent: str,
                        top1_prediction: str,
                        top2_prediction: str,
                        recovered: bool,
                        recovery_time_s: float = 0.0) -> None:
        self.attribution_events.append({
            "ground_truth": ground_truth_agent,
            "top1": top1_prediction,
            "top2": top2_prediction,
            "recovered": recovered,
            "recovery_time_s": recovery_time_s,
        })

    def top1_accuracy(self) -> float:
        if not self.attribution_events:
            return 0.0
        correct = sum(1 for e in self.attribution_events if e["ground_truth"] == e["top1"])
        return round(correct / len(self.attribution_events), 4)

    def top2_accuracy(self) -> float:
        if not self.attribution_events:
            return 0.0
        correct = sum(1 for e in self.attribution_events
                      if e["ground_truth"] in (e["top1"], e["top2"]))
        return round(correct / len(self.attribution_events), 4)

    def recovery_success_rate(self) -> float:
        if not self.attribution_events:
            return 0.0
        return round(sum(1 for e in self.attribution_events if e["recovered"])
                     / len(self.attribution_events), 4)

    def mean_recovery_time(self) -> float:
        times = [e["recovery_time_s"] for e in self.attribution_events if e["recovered"]]
        return round(float(np.mean(times)), 4) if times else 0.0

    def summary(self) -> dict:
        return {
            "total_attribution_events": len(self.attribution_events),
            "top1_accuracy": self.top1_accuracy(),
            "top2_accuracy": self.top2_accuracy(),
            "recovery_success_rate": self.recovery_success_rate(),
            "mean_recovery_time_s": self.mean_recovery_time(),
        }
