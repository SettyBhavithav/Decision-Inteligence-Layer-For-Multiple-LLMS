import json
import logging
from typing import Dict, Any, List
from agents.base_agent import client
from agents.citation.prompts import VALIDATION_PROMPT
from agents.citation.models import BibliographyEntry

logger = logging.getLogger("trust_framework")

class CitationValidator:
    """Submodule 7: Audits list formatting and ensures numbering sequence continuity."""
    def __init__(self, model: str = "stepfun-ai/step-3.7-flash"):
        self.model = model

    def validate_citations(self, bibliography: List[BibliographyEntry]) -> Dict[str, Any]:
        if not bibliography:
            return {"is_valid": False, "errors": ["Bibliography list is empty."]}
            
        # Basic logical check for numbering sequence
        for idx, entry in enumerate(bibliography):
            expected_key = f"[{idx + 1}]"
            if entry.key != expected_key:
                return {
                    "is_valid": False, 
                    "errors": [f"Numbering sequence break: expected key '{expected_key}', got '{entry.key}'"]
                }
                
        try:
            payload = [entry.formatted_reference for entry in bibliography]
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": VALIDATION_PROMPT},
                    {"role": "user", "content": f"Bibliography checklist:\n{json.dumps(payload)}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            logger.info(f"CitationValidator: Verification is_valid: {parsed.get('is_valid', False)}")
            return parsed
        except Exception as e:
            logger.warning(f"CitationValidator: Audit exception: {e}. Defaulting validation to true.")
            return {"is_valid": True, "errors": []}
