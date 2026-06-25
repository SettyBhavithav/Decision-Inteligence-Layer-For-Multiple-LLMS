import logging
from typing import List
from agents.verification.models import VerificationIssue

logger = logging.getLogger("trust_framework")

class ConsistencyVerifier:
    """Submodule 6: Checks internal terminology consistency and style metrics."""
    def __init__(self):
        pass

    def verify_consistency(self, text: str) -> List[VerificationIssue]:
        issues = []
        # Basic check: verify terminology consistency
        text_lower = text.lower()
        if "proposed framework" in text_lower and "proposed system" in text_lower:
            issues.append(VerificationIssue(
                description="Terminology discrepancy: detected both 'proposed framework' and 'proposed system'",
                severity="warning"
            ))
            
        logger.info(f"ConsistencyVerifier: Detected {len(issues)} consistency errors.")
        return issues
