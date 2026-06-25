import json
import logging
from typing import List, Dict, Any
from agents.base_agent import client
from agents.reviewer.prompts import LOGIC_REVIEW_PROMPT
from agents.reviewer.models import ReviewIssue

logger = logging.getLogger("trust_framework")

class LogicReviewer:
    """Submodule 3: Evaluates writing transitions and flags internal logical contradictions."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def review_logic(self, text: str) -> List[ReviewIssue]:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": LOGIC_REVIEW_PROMPT},
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
                    category="logic",
                    severity=issue.get("severity", "warning"),
                    description=issue.get("description", "Potential logical contradiction"),
                    location=issue.get("location", "body")
                ))
            return issues
        except Exception as e:
            logger.warning(f"LogicReviewer: Submodule call failed: {e}. Returning empty list.")
            return []
