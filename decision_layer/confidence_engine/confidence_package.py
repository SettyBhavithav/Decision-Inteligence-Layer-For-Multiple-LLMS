from typing import List, Dict, Any
from decision_layer.confidence_engine.models import ConfidencePackage, ConfidenceMetrics

class ConfidencePackageGenerator:
    """Submodule 7: Compiles the completed verified Confidence Package container."""
    def __init__(self):
        pass

    def build_package(self, 
                      agent_id: str, 
                      confidence: float, 
                      algorithm: str,
                      history: List[Dict[str, Any]], 
                      metrics: ConfidenceMetrics) -> ConfidencePackage:
                      
        return ConfidencePackage(
            agent_id=agent_id,
            confidence=confidence,
            algorithm=algorithm,
            history=history,
            metrics=metrics
        )
