import json
import logging
from typing import List, Dict, Any
from agents.base_agent import client
from agents.reviewer.prompts import CLAIM_REVIEW_PROMPT
from agents.reviewer.models import ReviewIssue

logger = logging.getLogger("trust_framework")

class ClaimReviewer:
    """Submodule 4: Identifies unsupported claims and missing citations in text blocks."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def review_claims(self, text: str) -> List[ReviewIssue]:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": CLAIM_REVIEW_PROMPT},
                    {"role": "user", "content": f"Text to audit:\n{text[:1500]}"}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            issues = []
            for issue in parsed.get("issues", []):
                issues.append(ReviewIssue(
                    category="claim",
                    severity=issue.get("severity", "warning"),
                    description=issue.get("description", "Unsupported assertion detected"),
                    location=issue.get("location", "body")
                ))
            return issues
        except Exception as e:
            logger.warning(f"ClaimReviewer: Submodule call failed: {e}. Returning empty list.")
            return []
