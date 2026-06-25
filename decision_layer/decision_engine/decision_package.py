from typing import Dict, List, Any
from decision_layer.decision_engine.models import DecisionPackage, DecisionMetrics

class DecisionPackageGenerator:
    """Submodule 9: Compiles the completed verified Decision Package container."""
    def __init__(self):
        pass

    def build_package(self, 
                      workflow_id: str, 
                      decision: str, 
                      algorithm: str,
                      explanation: str,
                      inputs: Dict[str, float], 
                      history: List[Dict[str, Any]],
                      metrics: DecisionMetrics) -> DecisionPackage:
                      
        return DecisionPackage(
            workflow_id=workflow_id,
            decision=decision,
            algorithm=algorithm,
            explanation=explanation,
            inputs=inputs,
            history=history,
            metrics=metrics
        )
