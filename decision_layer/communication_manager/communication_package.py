from typing import List, Dict, Any
from decision_layer.communication_manager.models import CommunicationPackage, CommunicationMetrics

class CommunicationPackageGenerator:
    """Submodule 9: Compiles the completed verified Communication Package container."""
    def __init__(self):
        pass

    def build_package(self, 
                      workflow_id: str, 
                      route: List[str], 
                      strategy: str,
                      messages: List[Dict[str, Any]], 
                      metrics: CommunicationMetrics,
                      history: List[Dict[str, Any]]) -> CommunicationPackage:
                      
        return CommunicationPackage(
            workflow_id=workflow_id,
            route=route,
            strategy=strategy,
            messages=messages,
            metrics=metrics,
            history=history
        )
