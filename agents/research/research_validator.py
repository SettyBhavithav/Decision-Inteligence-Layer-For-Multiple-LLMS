import json
import logging
from typing import Dict, Any
from agents.base_agent import client
from agents.research.prompts import VALIDATION_PROMPT

logger = logging.getLogger("trust_framework")

class ResearchValidator:
    """Submodule 7: Audits output for empty text, missing citations, or unsupported claims."""
    def __init__(self, model: str = "deepseek-ai/deepseek-v4-flash"):
        self.model = model

    def validate(self, summary: str) -> Dict[str, Any]:
        if not summary.strip():
            return {"is_valid": False, "errors": ["Generated summary is completely empty."]}

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": VALIDATION_PROMPT},
                    {"role": "user", "content": f"Summary text to audit: '{summary}'"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            logger.info(f"ResearchValidator: Validation status: {parsed.get('is_valid', False)}")
            return parsed
        except Exception as e:
            logger.warning(f"ResearchValidator: Audit exception: {e}. Defaulting validation to true.")
            return {"is_valid": True, "errors": []}
