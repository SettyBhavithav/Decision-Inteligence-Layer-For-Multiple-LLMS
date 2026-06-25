import logging
from typing import List, Dict, Any
from agents.reviewer.models import ReviewIssue

logger = logging.getLogger("trust_framework")

class StructureReviewer:
    """Submodule 2: Inspects layout and identifies missing or empty sections."""
    def __init__(self):
        self.mandatory_headings = ["introduction", "analysis", "references"]

    def review_structure(self, text: str) -> List[ReviewIssue]:
        issues = []
        text_lower = text.lower()
        
        # Check for mandatory headings
        for heading in self.mandatory_headings:
            if heading not in text_lower:
                issues.append(ReviewIssue(
                    category="structure",
                    severity="warning",
                    description=f"Missing expected academic section header matching '{heading}'",
                    location="overall"
                ))
                
        # Check for empty markdown content paragraphs
        lines = text.split("\n")
        for idx, line in enumerate(lines):
            if line.strip().startswith("##") and (idx + 1 < len(lines)) and not lines[idx+1].strip():
                # Potential empty section body indicator
                issues.append(ReviewIssue(
                    category="structure",
                    severity="warning",
                    description=f"Detected empty content section under header: '{line}'",
                    location=line.strip()
                ))
                
        logger.info(f"StructureReviewer: Identified {len(issues)} structural issues.")
        return issues
