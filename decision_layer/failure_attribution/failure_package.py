from typing import List, Dict, Any
from decision_layer.failure_attribution.models import FailurePackage, RootCause, RecoveryPlan, FailureMetrics

class FailurePackageGenerator:
    """Submodule 9: Compiles the completed verified Failure Package container."""
    def __init__(self):
        pass

    def build_package(self, 
                      workflow_id: str, 
                      failure_detected: bool, 
                      failure_type: str,
                      root_cause: RootCause, 
                      propagation_graph: List[str], 
                      recovery_plan: RecoveryPlan, 
                      metrics: FailureMetrics,
                      history: List[Dict[str, Any]] = None) -> FailurePackage:
                      
        return FailurePackage(
            workflow_id=workflow_id,
            failure_detected=failure_detected,
            failure_type=failure_type,
            root_cause=root_cause,
            propagation_graph=propagation_graph,
            recovery_plan=recovery_plan,
            metrics=metrics,
            history=history or []
        )
