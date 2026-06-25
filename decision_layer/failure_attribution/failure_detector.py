import logging
from typing import Dict, Any

logger = logging.getLogger("trust_framework")

class FailureDetector:
    """Submodule 2: Scans incoming metrics and packages to determine if a failure occurred."""
    def __init__(self, verification_threshold: float = 0.80, quality_threshold: float = 0.75, risk_threshold: float = 0.15):
        self.verification_threshold = verification_threshold
        self.quality_threshold = quality_threshold
        self.risk_threshold = risk_threshold

    def detect_failure(self, metrics: Dict[str, Any]) -> bool:
        # Check explicit failure flag
        if metrics.get("failed", False):
            logger.warning("FailureDetector: Explicit failure flag set in metrics")
            return True
            
        # Check verification scores
        verification_score = metrics.get("verification_score", 1.0)
        if verification_score < self.verification_threshold:
            logger.warning(f"FailureDetector: Factual verification failed. Score {verification_score:.2f} < {self.verification_threshold:.2f}")
            return True
            
        # Check reviewer quality scores
        quality_score = metrics.get("quality_score", 1.0)
        if quality_score < self.quality_threshold:
            logger.warning(f"FailureDetector: Reviewer quality score failed. Score {quality_score:.2f} < {self.quality_threshold:.2f}")
            return True
            
        # Check hallucination risk
        hallucination_risk = metrics.get("hallucination_risk", 0.0)
        if hallucination_risk >= self.risk_threshold:
            logger.warning(f"FailureDetector: Hallucination risk threshold violated. Risk {hallucination_risk:.2f} >= {self.risk_threshold:.2f}")
            return True
            
        # Check runtime errors
        if "error" in metrics or "exception" in metrics:
            logger.warning("FailureDetector: Exception or runtime error found in logs")
            return True
            
        return False
