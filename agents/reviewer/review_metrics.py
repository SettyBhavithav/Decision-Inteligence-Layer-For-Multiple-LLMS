import time
from typing import Dict
from agents.reviewer.models import ReviewMetrics

class ReviewMetricsTracker:
    """Submodule 11: Telemetry logger tracking evaluation latencies, issues detected, and tokens."""
    def __init__(self):
        self.start_time = 0.0
        self.review_time = 0.0
        self.issues_count = 0
        self.suggestions_count = 0
        self.token_usage = {"prompt": 0, "completion": 0, "total": 0}

    def start_review(self) -> None:
        self.start_time = time.time()

    def stop_review(self) -> None:
        self.review_time = time.time() - self.start_time

    def add_tokens(self, prompt: int, completion: int) -> None:
        self.token_usage["prompt"] += prompt
        self.token_usage["completion"] += completion
        self.token_usage["total"] += (prompt + completion)

    def get_metrics(self) -> ReviewMetrics:
        return ReviewMetrics(
            review_time=self.review_time,
            issues_count=self.issues_count,
            suggestions_count=self.suggestions_count,
            token_usage=self.token_usage
        )
