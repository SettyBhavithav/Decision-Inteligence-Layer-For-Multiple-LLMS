import time
from typing import Dict
from agents.research.models import ResearchMetrics

class ResearchMetricsTracker:
    """Submodule 10: Performance metrics logger tracking latencies, sources, claims, and token usage."""
    def __init__(self):
        self.retrieval_start = 0.0
        self.retrieval_time = 0.0
        
        self.synthesis_start = 0.0
        self.synthesis_time = 0.0
        
        self.num_sources = 0
        self.num_claims = 0
        self.num_citations = 0
        self.duplicates_removed = 0
        self.token_usage = {"prompt": 0, "completion": 0, "total": 0}

    def start_retrieval(self) -> None:
        self.retrieval_start = time.time()

    def stop_retrieval(self) -> None:
        self.retrieval_time = time.time() - self.retrieval_start

    def start_synthesis(self) -> None:
        self.synthesis_start = time.time()

    def stop_synthesis(self) -> None:
        self.synthesis_time = time.time() - self.synthesis_start

    def add_tokens(self, prompt: int, completion: int) -> None:
        self.token_usage["prompt"] += prompt
        self.token_usage["completion"] += completion
        self.token_usage["total"] += (prompt + completion)

    def get_metrics(self) -> ResearchMetrics:
        return ResearchMetrics(
            retrieval_time=self.retrieval_time,
            synthesis_time=self.synthesis_time,
            num_sources=self.num_sources,
            num_claims=self.num_claims,
            num_citations=self.num_citations,
            duplicates_removed=self.duplicates_removed,
            token_usage=self.token_usage
        )
