import json
import logging
from typing import Dict, Any
from agents.base_agent import client
from decision_layer.decision_engine.prompts import EXPLANATION_PROMPT

logger = logging.getLogger("trust_framework")

class DecisionExplainer:
    """Submodule 7: Generates text justifications for chosen decisions using NIM model."""
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model

    def explain_decision(self, 
                         decision: str, 
                         inputs: Dict[str, float]) -> str:
                         
        payload = {
            "decision": decision,
            "inputs": inputs
        }
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXPLANATION_PROMPT},
                    {"role": "user", "content": f"Decision event: {json.dumps(payload)}"}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            explanation = parsed.get("explanation", "").strip()
            return explanation
        except Exception as e:
            logger.warning(f"DecisionExplainer: Explanation call failed: {e}. Defaulting to template.")
            return f"Decision chosen as '{decision}' based on multi-signal inputs: {inputs}"
