import time
from typing import Dict
from agents.writing.models import WritingMetrics

class WritingMetricsTracker:
    """Submodule 10: Performance metrics logger tracking generation latency, word counts, and token usage."""
    def __init__(self):
        self.start_time = 0.0
        self.generation_time = 0.0
        self.sections_count = 0
        self.word_count = 0
        self.placeholder_count = 0
        self.validation_failures = 0
        self.token_usage = {"prompt": 0, "completion": 0, "total": 0}

    def start_generation(self) -> None:
        self.start_time = time.time()

    def stop_generation(self) -> None:
        self.generation_time = time.time() - self.start_time

    def add_tokens(self, prompt: int, completion: int) -> None:
        self.token_usage["prompt"] += prompt
        self.token_usage["completion"] += completion
        self.token_usage["total"] += (prompt + completion)

    def get_metrics(self) -> WritingMetrics:
        return WritingMetrics(
            generation_time=self.generation_time,
            sections_count=self.sections_count,
            word_count=self.word_count,
            placeholder_count=self.placeholder_count,
            validation_failures=self.validation_failures,
            token_usage=self.token_usage
        )
