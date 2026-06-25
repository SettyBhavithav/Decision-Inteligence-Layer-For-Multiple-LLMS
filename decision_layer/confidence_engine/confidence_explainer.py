import json
import logging
from typing import Dict, Any
from agents.base_agent import client
from decision_layer.confidence_engine.prompts import EXPLANATION_PROMPT

logger = logging.getLogger("trust_framework")

class ConfidenceExplainer:
    """Submodule 5: Explains why confidence score was estimated using prompt synthesis."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def explain_confidence(self, 
                           agent_id: str, 
                           previous_conf: float, 
                           updated_conf: float, 
                           metrics: Dict[str, Any]) -> str:
                           
        payload = {
            "agent_id": agent_id,
            "previous_confidence": previous_conf,
            "updated_confidence": updated_conf,
            "verification_score": metrics.get("verification_score", 1.0),
            "quality_score": metrics.get("quality_score", 1.0),
            "evidence_coverage": metrics.get("evidence_coverage", 1.0),
            "hallucination_risk": metrics.get("hallucination_risk", 0.0),
            "citation_accuracy": metrics.get("citation_accuracy", 1.0)
        }
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXPLANATION_PROMPT},
                    {"role": "user", "content": f"Estimation metrics: {json.dumps(payload)}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            explanation = parsed.get("explanation", "").strip()
            return explanation
        except Exception as e:
            logger.warning(f"ConfidenceExplainer: Explanation call failed: {e}. Defaulting to template.")
            diff = updated_conf - previous_conf
            direction = "increased" if diff >= 0 else "decreased"
            return f"Confidence {direction} by {abs(diff):.3f} based on claim coverage and verification."
