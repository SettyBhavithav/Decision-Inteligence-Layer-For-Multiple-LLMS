import json
import logging
from typing import List, Dict, Any
from agents.base_agent import client
from agents.verification.prompts import CLAIM_EXTRACTION_PROMPT
from agents.verification.models import ClaimRecord

logger = logging.getLogger("trust_framework")

class ClaimExtractor:
    """Submodule 1: Parses drafts and extracts all concrete factual/numerical assertions."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def extract_claims(self, text: str) -> List[ClaimRecord]:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": CLAIM_EXTRACTION_PROMPT},
                    {"role": "user", "content": f"Text to parse claims from:\n{text[:1500]}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            claims = []
            for item in parsed.get("claims", []):
                claims.append(ClaimRecord(
                    claim_id=int(item.get("claim_id", 1)),
                    claim=item.get("claim", ""),
                    paragraph=int(item.get("paragraph", 0))
                ))
            logger.info(f"ClaimExtractor: Extracted {len(claims)} claims from document.")
            return claims
        except Exception as e:
            logger.warning(f"ClaimExtractor: Submodule call failed: {e}. Returning default claim.")
            return [ClaimRecord(claim_id=1, claim="System calibration performance metrics.", paragraph=1)]
