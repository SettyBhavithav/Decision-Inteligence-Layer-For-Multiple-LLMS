import numpy as np
from typing import List

class TaskMetrics:
    """Category 1: Task Performance — Success Rate, Precision, Recall, F1."""
    def __init__(self):
        self.results: List[bool] = []
        self.true_positives: int = 0
        self.false_positives: int = 0
        self.false_negatives: int = 0

    def log_result(self, success: bool, true_positive: bool = False,
                   false_positive: bool = False, false_negative: bool = False) -> None:
        self.results.append(success)
        if true_positive:
            self.true_positives += 1
        if false_positive:
            self.false_positives += 1
        if false_negative:
            self.false_negatives += 1

    def success_rate(self) -> float:
        return float(np.mean(self.results)) if self.results else 0.0

    def accuracy(self) -> float:
        return self.success_rate()

    def precision(self) -> float:
        denom = self.true_positives + self.false_positives
        return self.true_positives / denom if denom > 0 else 0.0

    def recall(self) -> float:
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom > 0 else 0.0

    def f1_score(self) -> float:
        p, r = self.precision(), self.recall()
        return (2 * p * r) / (p + r) if (p + r) > 0 else 0.0

    def summary(self) -> dict:
        return {
            "success_rate": round(self.success_rate(), 4),
            "accuracy": round(self.accuracy(), 4),
            "precision": round(self.precision(), 4),
            "recall": round(self.recall(), 4),
            "f1_score": round(self.f1_score(), 4),
            "total_runs": len(self.results),
        }
