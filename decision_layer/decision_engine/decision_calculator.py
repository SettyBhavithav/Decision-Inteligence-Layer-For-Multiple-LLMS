import logging
from typing import Dict, Any

logger = logging.getLogger("trust_framework")

class DecisionCalculator:
    """Base interface for workflow action decision calculations."""
    def calculate_decision(self, inputs: Dict[str, float], limits: Dict[str, Any] = None) -> str:
        raise NotImplementedError("Subclasses must implement calculate_decision()")

class RuleBasedDecisionCalculator(DecisionCalculator):
    """Rule-Based baseline updates using hard threshold rules."""
    def calculate_decision(self, inputs: Dict[str, float], limits: Dict[str, Any] = None) -> str:
        trust = inputs.get("trust_score", 0.80)
        confidence = inputs.get("confidence_score", 0.85)
        
        if confidence >= 0.90 and trust >= 0.80:
            return "ACCEPT"
        elif confidence < 0.60 or trust < 0.60:
            return "REGENERATE"
        else:
            return "VERIFY"

class WeightedDecisionCalculator(DecisionCalculator):
    """Weighted baseline updates combining signals linearly."""
    def __init__(self, w_t: float = 0.2, w_c: float = 0.3, w_v: float = 0.3, w_q: float = 0.2):
        self.w_t = w_t
        self.w_c = w_c
        self.w_v = w_v
        self.w_q = w_q

    def calculate_decision(self, inputs: Dict[str, float], limits: Dict[str, Any] = None) -> str:
        trust = inputs.get("trust_score", 0.80)
        confidence = inputs.get("confidence_score", 0.85)
        verification = inputs.get("verification_score", 1.0)
        quality = inputs.get("quality_score", 1.0)
        
        composite = (
            self.w_t * trust +
            self.w_c * confidence +
            self.w_v * verification +
            self.w_q * quality
        )
        
        if composite >= 0.85:
            return "ACCEPT"
        elif composite >= 0.65:
            return "VERIFY"
        else:
            return "REGENERATE"

class ProposedDecisionCalculator(DecisionCalculator):
    """Our proposed Adaptive Multi-Signal Decision update algorithm."""
    def calculate_decision(self, inputs: Dict[str, float], limits: Dict[str, Any] = None) -> str:
        trust = inputs.get("trust_score", 0.80)
        confidence = inputs.get("confidence_score", 0.85)
        risk = inputs.get("hallucination_risk", 0.0)
        
        if not limits:
            limits = {}
            
        attempts = limits.get("attempts", 1)
        max_attempts = limits.get("max_attempts", 3)
        
        # Risk-calibrated utility value
        utility = trust * confidence * ((1.0 - risk) ** 2)
        
        if utility >= 0.75:
            return "ACCEPT"
        elif utility >= 0.50 or (risk >= 0.10 and utility >= 0.40):
            return "VERIFY"
        elif utility >= 0.30 and risk < 0.30:
            if attempts >= max_attempts:
                return "ESCALATE"
            return "RETRY"
        elif risk >= 0.30:
            return "REGENERATE"
        else:
            return "REJECT"
