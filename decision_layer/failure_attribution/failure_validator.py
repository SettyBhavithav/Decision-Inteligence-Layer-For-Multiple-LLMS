import logging
from decision_layer.failure_attribution.models import FailurePackage

logger = logging.getLogger("trust_framework")

class FailureValidator:
    """Submodule 8: Validates that failure packages contain complete attribution profiles."""
    def __init__(self):
        self.allowed_actions = {"RETRY", "REGENERATE", "ESCALATE", "REJECT", "CONTINUE"}

    def validate_package(self, package: FailurePackage) -> bool:
        if not package.failure_detected:
            return True
            
        if not package.root_cause.responsible_agent:
            logger.error("FailureValidator: Violation! Missing responsible culprit agent identification!")
            return False
            
        if package.recovery_plan.recommended_action not in self.allowed_actions:
            logger.error(f"FailureValidator: Violation! Recovery action '{package.recovery_plan.recommended_action}' is not recognized!")
            return False
            
        return True
