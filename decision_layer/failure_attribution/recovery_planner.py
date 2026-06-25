import logging
from typing import Dict, Any, List
from decision_layer.failure_attribution.models import RecoveryPlan

logger = logging.getLogger("trust_framework")

class RecoveryPlanner:
    """Submodule 6: Prescribes actionable recovery steps."""
    def __init__(self):
        pass

    def plan_recovery(self, failure_type: str, culprit_agent: str, metrics: Dict[str, Any]) -> RecoveryPlan:
        category = failure_type.strip().lower()
        
        attempts = metrics.get("attempts", 1)
        max_attempts = metrics.get("max_attempts", 3)
        
        if attempts >= max_attempts:
            return RecoveryPlan(
                recommended_action="ESCALATE",
                steps=[
                    f"Stop pipeline execution.",
                    f"Escalate to administrator console.",
                    f"Request human verification audits."
                ]
            )
            
        if "hallucination" in category:
            return RecoveryPlan(
                recommended_action="REGENERATE",
                steps=[
                    f"Re-trigger Writing Agent.",
                    f"Inject strict factual grounding context prompts."
                ]
            )
        elif "citation" in category:
            return RecoveryPlan(
                recommended_action="RETRY",
                steps=[
                    f"Re-trigger Citation Agent.",
                    f"Re-validate DOI records against registry databases."
                ]
            )
        elif "unsupported" in category:
            return RecoveryPlan(
                recommended_action="RETRY",
                steps=[
                    f"Re-trigger Research Agent.",
                    f"Expand document chunk indexing thresholds."
                ]
            )
            
        return RecoveryPlan(
            recommended_action="REJECT",
            steps=["Discard workflow output package."]
        )
