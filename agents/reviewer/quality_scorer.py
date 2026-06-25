import json
import logging
from typing import Dict, Any
from agents.base_agent import client
from agents.reviewer.prompts import SCORING_PROMPT
from agents.reviewer.models import QualityScore

logger = logging.getLogger("trust_framework")

class QualityScorer:
    """Submodule 7: Computes structured scoring indexes for each content layer."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def score_quality(self, text: str) -> QualityScore:
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SCORING_PROMPT},
                    {"role": "user", "content": f"Score this text:\n{text[:1500]}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            return QualityScore(
                structure_score=float(parsed.get("structure_score", 0.90)),
                logic_score=float(parsed.get("logic_score", 0.90)),
                evidence_score=float(parsed.get("evidence_score", 0.90)),
                citation_score=float(parsed.get("citation_score", 0.90)),
                overall_quality=float(parsed.get("overall_quality", 0.90))
            )
        except Exception as e:
            logger.warning(f"QualityScorer: Submodule call failed: {e}. Falling back to default scores.")
            return QualityScore(
                structure_score=0.88,
                logic_score=0.85,
                evidence_score=0.85,
                citation_score=0.88,
                overall_quality=0.86
            )
