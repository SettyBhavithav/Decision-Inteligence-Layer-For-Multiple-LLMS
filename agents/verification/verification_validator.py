import logging
from typing import List
from agents.verification.models import VerificationScore, VerificationIssue

logger = logging.getLogger("trust_framework")

class VerificationValidator:
    """Submodule 8: Evaluates verified status (True/False) based on scoring indices and issue severities."""
    def __init__(self, accuracy_threshold: float = 0.85, hallucination_threshold: float = 0.15):
        self.accuracy_threshold = accuracy_threshold
        self.hallucination_threshold = hallucination_threshold

    def validate_verification(self, score: VerificationScore, issues: List[VerificationIssue]) -> bool:
        # Check if overall score falls below the threshold
        if score.overall_verification < self.accuracy_threshold:
            logger.warning(f"VerificationValidator: Overall score {score.overall_verification} below threshold {self.accuracy_threshold}!")
            return False
            
        # Check if hallucination risk exceeds the threshold
        if score.hallucination_risk > self.hallucination_threshold:
            logger.warning(f"VerificationValidator: Hallucination risk {score.hallucination_risk} exceeds threshold {self.hallucination_threshold}!")
            return False
            
        # Check if any critical issues were flagged
        for issue in issues:
            if issue.severity == "critical":
                logger.warning(f"VerificationValidator: Critical verification issue detected: {issue.description}")
                return False
                
        logger.info("VerificationValidator: Factual verification succeeded.")
        return True
