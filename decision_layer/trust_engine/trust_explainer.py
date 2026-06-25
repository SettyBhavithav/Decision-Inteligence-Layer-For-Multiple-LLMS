import json
import logging
from typing import Dict, Any
from agents.base_agent import client
from decision_layer.trust_engine.prompts import EXPLANATION_PROMPT

logger = logging.getLogger("trust_framework")

class TrustExplainer:
    """Submodule 5: Explains why trust score changed using prompt synthesis."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def explain_change(self, 
                       agent_id: str, 
                       previous_trust: float, 
                       updated_trust: float, 
                       metrics: Dict[str, Any]) -> str:
                       
        payload = {
            "agent_id": agent_id,
            "previous_trust": previous_trust,
            "updated_trust": updated_trust,
            "verification_score": metrics.get("verification_score", 1.0),
            "quality_score": metrics.get("quality_score", 1.0),
            "hallucination_risk": metrics.get("hallucination_risk", 0.0),
            "success": metrics.get("success", True)
        }
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXPLANATION_PROMPT},
                    {"role": "user", "content": f"Update event metrics: {json.dumps(payload)}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            explanation = parsed.get("explanation", "").strip()
            return explanation
        except Exception as e:
            logger.warning(f"TrustExplainer: Explanation call failed: {e}. Defaulting to template.")
            diff = updated_trust - previous_trust
            direction = "increased" if diff >= 0 else "decreased"
            return f"Trust score {direction} by {abs(diff):.3f} based on verification outcomes."
class TrustExplainerTask:
    pass
