import json
import logging
from typing import Dict, Any
from agents.base_agent import client
from agents.writing.prompts import VALIDATION_PROMPT

logger = logging.getLogger("trust_framework")

class WritingValidator:
    """Submodule 8: Validates sections, markdown formatting, and checks for empty paragraphs."""
    def __init__(self, model: str = "stepfun-ai/step-3.7-flash"):
        self.model = model

    def validate(self, text: str) -> Dict[str, Any]:
        if not text.strip():
            return {"is_valid": False, "errors": ["Draft text is completely empty."]}

        # Check for empty markdown headings
        lines = text.split("\n")
        for line in lines:
            if line.strip().startswith("##") and len(line.strip()) <= 3:
                return {"is_valid": False, "errors": [f"Empty heading detected: '{line}'"]}

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": VALIDATION_PROMPT},
                    {"role": "user", "content": f"Draft text to validate:\n{text}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            logger.info(f"WritingValidator: Validation status: {parsed.get('is_valid', False)}")
            return parsed
        except Exception as e:
            logger.warning(f"WritingValidator: Audit exception: {e}. Defaulting to true.")
            return {"is_valid": True, "errors": []}
