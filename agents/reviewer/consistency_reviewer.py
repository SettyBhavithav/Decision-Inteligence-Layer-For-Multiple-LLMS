import logging
from typing import List
from agents.reviewer.models import ReviewIssue

logger = logging.getLogger("trust_framework")

class ConsistencyReviewer:
    """Submodule 6: Screens texts for lexical and numerical style discrepancies."""
    def __init__(self):
        pass

    def review_consistency(self, text: str) -> List[ReviewIssue]:
        issues = []
        # Basic check for spelling variations or casing discrepancies of framework words
        words = ["multi-agent", "multiagent", "large language model", "llm"]
        
        # Check if both "multi-agent" and "multiagent" are present in the text (inconsistency)
        text_lower = text.lower()
        if "multi-agent" in text_lower and "multiagent" in text_lower:
            issues.append(ReviewIssue(
                category="consistency",
                severity="suggestion",
                description="Acronym or term mismatch: detected both hyphenated 'multi-agent' and flat 'multiagent'",
                location="overall"
            ))
            
        logger.info(f"ConsistencyReviewer: Detected {len(issues)} consistency issues.")
        return issues
