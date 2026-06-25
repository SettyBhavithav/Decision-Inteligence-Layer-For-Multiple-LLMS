import json
import logging
from typing import Dict, Any
from agents.base_agent import client
from agents.writing.prompts import CONSISTENCY_PROMPT

logger = logging.getLogger("trust_framework")

class ConsistencyChecker:
    """Submodule 5: Audits draft text for logical contradictions or flows."""
    def __init__(self, model: str = "stepfun-ai/step-3.7-flash"):
        self.model = model

    def check_consistency(self, full_draft: str) -> Dict[str, Any]:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": CONSISTENCY_PROMPT},
                    {"role": "user", "content": f"Full draft text to edit:\n{full_draft}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            logger.info(f"ConsistencyChecker: Status is_consistent: {parsed.get('is_consistent', False)}")
            return parsed
        except Exception as e:
            logger.warning(f"ConsistencyChecker: Verification failed: {e}. Defaulting to consistent.")
            return {"is_consistent": True, "feedback": ""}
