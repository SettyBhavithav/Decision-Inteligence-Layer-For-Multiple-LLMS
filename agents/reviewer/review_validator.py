import logging
from typing import List
from agents.reviewer.models import QualityScore, ReviewIssue

logger = logging.getLogger("trust_framework")

class ReviewValidator:
    """Submodule 9: Formulates review statuses (approved vs revision_needed) using scores and issue severities."""
    def __init__(self, quality_threshold: float = 0.80):
        self.quality_threshold = quality_threshold

    def validate_review(self, score: QualityScore, issues: List[ReviewIssue]) -> str:
        # Check if overall score falls below the threshold
        if score.overall_quality < self.quality_threshold:
            logger.warning(f"ReviewValidator: Overall score {score.overall_quality} below threshold {self.quality_threshold}!")
            return "revision_needed"
            
        # Check if any critical issues were flagged
        for issue in issues:
            if issue.severity == "critical":
                logger.warning(f"ReviewValidator: Critical structural/logic issue detected: {issue.description}")
                return "revision_needed"
                
        logger.info("ReviewValidator: Document passed review benchmarks.")
        return "approved"
