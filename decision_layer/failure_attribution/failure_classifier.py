import logging
from typing import Dict, Any

logger = logging.getLogger("trust_framework")

class FailureClassifier:
    """Submodule 4: Categorizes failure logs into specific classifications."""
    def __init__(self):
        pass

    def classify_failure(self, metrics: Dict[str, Any]) -> str:
        # Check for explicitly declared error categories
        error_msg = str(metrics.get("error", "")).lower()
        if "hallucinate" in error_msg or "fake" in error_msg:
            return "Hallucination"
        if "citation" in error_msg or "doi" in error_msg or "reference" in error_msg:
            return "Citation Failure"
        if "unsupported" in error_msg or "claim" in error_msg:
            return "Unsupported Claim"
            
        # Fallback check based on scores
        verification_score = metrics.get("verification_score", 1.0)
        hallucination_risk = metrics.get("hallucination_risk", 0.0)
        quality_score = metrics.get("quality_score", 1.0)
        
        if hallucination_risk >= 0.15:
            return "Hallucination"
        if verification_score < 0.80:
            return "Verification Failure"
        if quality_score < 0.75:
            return "Unsupported Claim"
            
        return "Unknown Failure"
