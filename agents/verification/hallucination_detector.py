import json
import logging
from typing import List, Dict, Any
from agents.base_agent import client
from agents.verification.prompts import HALLUCINATION_PROMPT
from agents.verification.models import VerificationIssue

logger = logging.getLogger("trust_framework")

class HallucinationDetector:
    """Submodule 4: Identifies fabricated citations or ungrounded conclusions."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def detect_hallucinations(self, text: str) -> List[VerificationIssue]:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": HALLUCINATION_PROMPT},
                    {"role": "user", "content": f"Text to audit:\n{text[:1500]}"}
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
                    description=item.get("description", "Ungrounded hallucination"),
                    severity=item.get("severity", "critical")
                ))
            return issues
        except Exception as e:
            logger.warning(f"HallucinationDetector: Submodule call failed: {e}. Returning empty list.")
            return []
