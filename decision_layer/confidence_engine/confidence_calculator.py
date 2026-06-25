import logging
from typing import Dict, Any

logger = logging.getLogger("trust_framework")

class ConfidenceCalculator:
    """Base interface for Confidence updates."""
    def calculate(self, metrics: Dict[str, Any]) -> float:
        raise NotImplementedError("Subclasses must implement calculate()")

class RuleBasedConfidenceCalculator(ConfidenceCalculator):
    """Rule-Based baseline updates using static linear weights."""
    def __init__(self, w_ver: float = 0.4, w_qual: float = 0.3, w_cov: float = 0.3):
        self.w_ver = w_ver
        self.w_qual = w_qual
        self.w_cov = w_cov

    def calculate(self, metrics: Dict[str, Any]) -> float:
        verification_score = metrics.get("verification_score", 1.0)
        quality_score = metrics.get("quality_score", 1.0)
        evidence_coverage = metrics.get("evidence_coverage", 1.0)
        
        composite = (
            self.w_ver * verification_score +
            self.w_qual * quality_score +
            self.w_cov * evidence_coverage
        )
        return max(0.0, min(1.0, composite))

class BayesianConfidenceCalculator(ConfidenceCalculator):
    """Bayesian baseline updates modeling expected correctness using Beta priors."""
    def __init__(self, alpha_prior: float = 4.0, beta_prior: float = 1.0):
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior

    def calculate(self, metrics: Dict[str, Any]) -> float:
        verification_score = metrics.get("verification_score", 1.0)
        
        # Bayesian Beta posterior update
        new_alpha = self.alpha_prior + verification_score
        new_beta = self.beta_prior + (1.0 - verification_score)
        
        composite = new_alpha / (new_alpha + new_beta)
        return max(0.0, min(1.0, composite))

class ProposedConfidenceCalculator(ConfidenceCalculator):
    """Our proposed Adaptive Claim-Aware Confidence update algorithm."""
    def __init__(self, w_cov: float = 0.5, w_cred: float = 0.3, w_risk: float = 0.2):
        self.w_cov = w_cov
        self.w_cred = w_cred
        self.w_risk = w_risk

    def calculate(self, metrics: Dict[str, Any]) -> float:
        # Proposed Claim-Aware: extract claim level coverage, credibility, and risks
        claims_list = metrics.get("claims", [])
        
        if not claims_list:
            # Fallback to response level values if no subclaims are indexed
            verification_score = metrics.get("verification_score", 1.0)
            quality_score = metrics.get("quality_score", 1.0)
            hallucination_risk = metrics.get("hallucination_risk", 0.0)
            
            composite = (
                self.w_cov * verification_score +
                self.w_cred * quality_score -
                self.w_risk * (hallucination_risk ** 2)
            )
            return max(0.0, min(1.0, composite))

        claim_scores = []
        for claim in claims_list:
            coverage = claim.get("coverage", 1.0)
            credibility = claim.get("credibility", 1.0)
            risk = claim.get("hallucination_risk", 0.0)
            
            # Claim-level confidence
            claim_conf = coverage * credibility * ((1.0 - risk) ** 2)
            claim_scores.append(claim_conf)
            
        # Aggregate average claim confidence
        avg_claim_conf = sum(claim_scores) / len(claim_scores)
        
        # Apply critical issue penalty (e.g. if verification failed or high risk issues found)
        critical_issues = metrics.get("critical_issues", 0)
        penalty = 0.25 * critical_issues
        
        composite = avg_claim_conf - penalty
        return max(0.0, min(1.0, composite))
