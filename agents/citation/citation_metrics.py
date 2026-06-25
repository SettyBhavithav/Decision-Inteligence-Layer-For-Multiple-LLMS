import time
from typing import Dict
from agents.citation.models import CitationMetrics

class CitationMetricsTracker:
    """Submodule 10: Telemetry logger tracking formatting speeds and token consumption."""
    def __init__(self):
        self.fmt_start = 0.0
        self.formatting_time = 0.0
        
        self.val_start = 0.0
        self.validation_time = 0.0
        
        self.token_usage = {"prompt": 0, "completion": 0, "total": 0}

    def start_formatting(self) -> None:
        self.fmt_start = time.time()

    def stop_formatting(self) -> None:
        self.formatting_time = time.time() - self.fmt_start

    def start_validation(self) -> None:
        self.val_start = time.time()

    def stop_validation(self) -> None:
        self.validation_time = time.time() - self.val_start

    def add_tokens(self, prompt: int, completion: int) -> None:
        self.token_usage["prompt"] += prompt
        self.token_usage["completion"] += completion
        self.token_usage["total"] += (prompt + completion)

    def get_metrics(self) -> CitationMetrics:
        return CitationMetrics(
            formatting_time=self.formatting_time,
            validation_time=self.validation_time,
            token_usage=self.token_usage
        )
