import logging
import math
from typing import Dict, Any

logger = logging.getLogger("trust_framework")

class TrustCalculator:
    """Base interface for Dynamic Trust update calculations."""
    def calculate(self, current_trust: float, metrics: Dict[str, Any]) -> float:
        raise NotImplementedError("Subclasses must implement calculate()")

class RuleBasedTrustCalculator(TrustCalculator):
    """Rule-Based baseline updates by static increments."""
    def __init__(self, increment: float = 0.05, penalty: float = 0.10):
        self.increment = increment
        self.penalty = penalty

    def calculate(self, current_trust: float, metrics: Dict[str, Any]) -> float:
        success = metrics.get("success", True)
        if success:
            new_trust = current_trust + self.increment
        else:
            new_trust = current_trust - self.penalty
        return max(0.0, min(1.0, new_trust))

class BayesianTrustCalculator(TrustCalculator):
    """Bayesian baseline updates modeling expected success rates using Beta distributions."""
    def __init__(self, alpha_prior: float = 2.0, beta_prior: float = 1.0):
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior

    def calculate(self, current_trust: float, metrics: Dict[str, Any]) -> float:
        # Map quality and verification scores as fractional observations
        success_weight = metrics.get("verification_score", 1.0)
        quality_weight = metrics.get("quality_score", 1.0)
        success = metrics.get("success", True)
        
        # Calculate rewards and penalties
        reward = success_weight * 0.8 + quality_weight * 0.2
        penalty = 1.0 - reward if not success else 0.0
        
        # Update Beta parameters based on current trust as a pseudo-prior
        eff_prior_count = 5.0
        prior_alpha = current_trust * eff_prior_count
        prior_beta = (1.0 - current_trust) * eff_prior_count
        
        new_alpha = prior_alpha + reward
        new_beta = prior_beta + penalty
        
        # Beta expectation mean
        new_trust = new_alpha / (new_alpha + new_beta)
        return max(0.0, min(1.0, new_trust))

class ProposedTrustCalculator(TrustCalculator):
    """Our proposed Dynamic Trust update algorithm employing EMA and quadratic penalty scaling."""
    def __init__(self, learning_rate: float = 0.15, w_verification: float = 0.6, w_quality: float = 0.4, w_risk: float = 0.2):
        self.learning_rate = learning_rate
        self.w_verification = w_verification
        self.w_quality = w_quality
        self.w_risk = w_risk

    def calculate(self, current_trust: float, metrics: Dict[str, Any]) -> float:
        verification_score = metrics.get("verification_score", 1.0)
        quality_score = metrics.get("quality_score", 1.0)
        hallucination_risk = metrics.get("hallucination_risk", 0.0)
        
        # Non-linear quadratic penalty scaling for hallucination risk
        composite_quality = (
            self.w_verification * verification_score +
            self.w_quality * quality_score -
            self.w_risk * (hallucination_risk ** 2)
        )
        composite_quality = max(0.0, min(1.0, composite_quality))
        
        # Exponential Moving Average update
        new_trust = (1 - self.learning_rate) * current_trust + self.learning_rate * composite_quality
        return max(0.0, min(1.0, new_trust))
