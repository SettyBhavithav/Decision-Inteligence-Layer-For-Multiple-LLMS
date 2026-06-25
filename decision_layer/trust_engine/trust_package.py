from typing import List, Dict, Any
from decision_layer.trust_engine.models import TrustPackage, TrustMetrics

class TrustPackageGenerator:
    """Submodule 7: Compiles the completed verified Trust Package container."""
    def __init__(self):
        pass

    def build_package(self, 
                      agent_id: str, 
                      trust_score: float, 
                      history: List[Dict[str, Any]], 
                      metrics: TrustMetrics) -> TrustPackage:
                      
        return TrustPackage(
            agent_id=agent_id,
            trust_score=trust_score,
            history=history,
            metrics=metrics
        )
