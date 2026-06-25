import json
import logging
from typing import Dict, Any
from agents.base_agent import client
from decision_layer.failure_attribution.prompts import EXPLANATION_PROMPT

logger = logging.getLogger("trust_framework")

class AttributionExplainer:
    """Submodule 7: Generates text justifications for failure attributions using NIM model."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def explain_attribution(self, 
                            responsible_agent: str, 
                            failure_type: str, 
                            severity: str, 
                            metrics: Dict[str, Any]) -> str:
                            
        payload = {
            "responsible_agent": responsible_agent,
            "failure_type": failure_type,
            "severity": severity,
            "metrics": metrics
        }
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXPLANATION_PROMPT},
                    {"role": "user", "content": f"Failure event: {json.dumps(payload)}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            explanation = parsed.get("explanation", "").strip()
            return explanation
        except Exception as e:
            logger.warning(f"AttributionExplainer: Explanation call failed: {e}. Defaulting to template.")
            return f"Failure of type '{failure_type}' was attributed to '{responsible_agent}' due to score threshold violations."
