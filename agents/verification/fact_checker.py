import json
import logging
from typing import List, Dict, Any
from agents.base_agent import client
from agents.verification.prompts import FACT_CHECK_PROMPT
from agents.verification.models import VerificationIssue

logger = logging.getLogger("trust_framework")

class FactChecker:
    """Submodule 3: Verifies specific dates, values, and calculations against evidence."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def check_facts(self, claims: List[Dict[str, Any]], sources: List[Dict[str, Any]]) -> List[VerificationIssue]:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": FACT_CHECK_PROMPT},
                    {"role": "user", "content": f"Claims: {json.dumps(claims)}\n\nSources: {json.dumps(sources)}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            issues = []
            for item in parsed.get("issues", []):
                issues.append(VerificationIssue(
                    claim_id=item.get("claim_id"),
                    description=item.get("description", "Factual discrepancy detected"),
                    severity=item.get("severity", "warning")
                ))
            return issues
        except Exception as e:
            logger.warning(f"FactChecker: Submodule call failed: {e}. Returning empty list.")
            return []
