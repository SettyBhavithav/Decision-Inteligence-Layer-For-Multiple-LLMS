from typing import List
from agents.reviewer.models import ReviewPackage, QualityScore, ReviewIssue, ReviewSuggestion, ReviewMetrics

class ReviewPackageGenerator:
    """Submodule 10: Compiles the completed verified Review Package container."""
    def __init__(self):
        pass

    def build_package(self, 
                      workflow_id: str, 
                      status: str, 
                      score: QualityScore, 
                      issues: List[ReviewIssue], 
                      suggestions: List[ReviewSuggestion], 
                      metrics: ReviewMetrics) -> ReviewPackage:
                      
        return ReviewPackage(
            workflow_id=workflow_id,
            review_status=status,
            quality_scores=score,
            issues=issues,
            suggestions=suggestions,
            metrics=metrics
        )
