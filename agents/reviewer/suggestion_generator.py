import logging
from typing import List
from agents.reviewer.models import ReviewIssue, ReviewSuggestion

logger = logging.getLogger("trust_framework")

class SuggestionGenerator:
    """Submodule 8: Maps identified layout/logical issues into actionable improvement items."""
    def __init__(self):
        pass

    def generate_suggestions(self, issues: List[ReviewIssue]) -> List[ReviewSuggestion]:
        suggestions = []
        for idx, issue in enumerate(issues):
            issue_id = f"issue_{idx+1:02d}"
            
            # Map suggestion text based on category
            if issue.category == "structure":
                suggestion_text = f"Review the document layout and insert heading for: {issue.description}."
            elif issue.category == "logic":
                suggestion_text = f"Audit the flow and transitions at location: '{issue.location}'."
            elif issue.category == "claim":
                suggestion_text = f"Attach verifying references/evidence to support assertion: '{issue.description}'."
            else:
                suggestion_text = f"Check formatting details: {issue.description}."
                
            suggestions.append(ReviewSuggestion(
                issue_id=issue_id,
                suggestion=suggestion_text,
                example="Example correction: check citation numbering index"
            ))
            
        logger.info(f"SuggestionGenerator: Generated {len(suggestions)} suggestions.")
        return suggestions
