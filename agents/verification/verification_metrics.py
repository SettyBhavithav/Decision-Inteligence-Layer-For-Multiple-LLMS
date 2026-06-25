import time
from typing import Dict
from agents.verification.models import VerificationMetrics

class VerificationMetricsTracker:
    """Submodule 10: Telemetry logger tracking factual review speeds and hallucination counts."""
    def __init__(self):
        self.start_time = 0.0
        self.verification_latency = 0.0
        self.claims_verified = 0
        self.hallucinations_detected = 0
        self.token_usage = {"prompt": 0, "completion": 0, "total": 0}

    def start_verification(self) -> None:
        self.start_time = time.time()

    def stop_verification(self) -> None:
        self.verification_latency = time.time() - self.start_time

    def add_tokens(self, prompt: int, completion: int) -> None:
        self.token_usage["prompt"] += prompt
        self.token_usage["completion"] += completion
        self.token_usage["total"] += (prompt + completion)

    def get_metrics(self) -> VerificationMetrics:
        return VerificationMetrics(
            claims_verified=self.claims_verified,
            hallucinations_detected=self.hallucinations_detected,
            verification_latency=self.verification_latency,
            token_usage=self.token_usage
        )
