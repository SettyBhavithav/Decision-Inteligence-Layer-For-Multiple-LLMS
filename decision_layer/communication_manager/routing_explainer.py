import json
import logging
from typing import Dict, Any, List
from agents.base_agent import client
from decision_layer.communication_manager.prompts import EXPLANATION_PROMPT

logger = logging.getLogger("trust_framework")

class RoutingExplainer:
    """Submodule 7: Generates text justifications for routing pathways using NIM models."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def explain_route(self, 
                      source: str, 
                      target: str, 
                      route: List[str], 
                      metrics: Dict[str, Any]) -> str:
                      
        payload = {
            "source": source,
            "target": target,
            "computed_route": route,
            "trust_score": metrics.get("trust_score", 0.80),
            "confidence_score": metrics.get("confidence_score", 0.85),
            "complexity": metrics.get("complexity", "medium")
        }
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXPLANATION_PROMPT},
                    {"role": "user", "content": f"Routing event: {json.dumps(payload)}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            explanation = parsed.get("explanation", "").strip()
            return explanation
        except Exception as e:
            logger.warning(f"RoutingExplainer: Explanation call failed: {e}. Defaulting to template.")
            return f"Routed message from '{source}' to '{target}' along path {route} based on task metadata."
