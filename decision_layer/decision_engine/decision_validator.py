import logging
from typing import Dict

logger = logging.getLogger("trust_framework")

class DecisionValidator:
    """Submodule 8: Validates that decisions belong to acceptable enum sets and contains proper fields."""
    def __init__(self):
        self.allowed_decisions = {"ACCEPT", "VERIFY", "REGENERATE", "RETRY", "ESCALATE", "REJECT"}

    def validate_decision(self, decision: str, inputs: Dict[str, float]) -> bool:
        if decision not in self.allowed_decisions:
            logger.error(f"DecisionValidator: Violation! Decision '{decision}' is not recognized!")
            return False
            
        required_keys = {"trust_score", "confidence_score"}
        for key in required_keys:
            if key not in inputs:
                logger.error(f"DecisionValidator: Violation! Missing critical decision input field '{key}'!")
                return False
                
        return True
