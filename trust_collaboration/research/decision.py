import logging
from typing import Dict, Any

logger = logging.getLogger("trust_framework")

class DecisionEngine:
    """
    Intelligent Decision Engine.
    Combines agent trust score and calibrated confidence using adaptive thresholds.
    Outputs: ACCEPT, VERIFY, REJECT, or REGENERATE.
    """
    def __init__(self, 
                 theta_accept: float = 0.65, 
                 theta_verify: float = 0.35):
        self.theta_accept = theta_accept
        self.theta_verify = theta_verify

    def make_decision(self, 
                      trust_score: float, 
                      calibrated_conf: float, 
                      task_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate agent response reliability.
        Formula: Reliability Score = trust_score * calibrated_conf
        Thresholds scale dynamically with task complexity:
            - If task complexity is 'high', thresholds scale up by 15%.
            - If task complexity is 'low', thresholds scale down by 10%.
        """
        complexity = task_metadata.get("complexity", "medium").lower()
        
        # Determine dynamic thresholds
        t_accept = self.theta_accept
        t_verify = self.theta_verify
        
        if complexity == "high":
            t_accept = min(0.95, t_accept * 1.15)
            t_verify = min(0.70, t_verify * 1.15)
        elif complexity == "low":
            t_accept = max(0.40, t_accept * 0.90)
            t_verify = max(0.20, t_verify * 0.90)
            
        reliability_score = trust_score * calibrated_conf
        
        if reliability_score >= t_accept:
            decision = "ACCEPT"
            reason = (
                f"Reliability score ({reliability_score:.3f}) exceeds accept threshold ({t_accept:.3f}). "
                f"Agent Trust: {trust_score:.2f}, Calibrated Confidence: {calibrated_conf:.2f}."
            )
        elif reliability_score >= t_verify:
            decision = "VERIFY"
            reason = (
                f"Reliability score ({reliability_score:.3f}) is between verification threshold ({t_verify:.3f}) "
                f"and accept threshold ({t_accept:.3f}). Verification required."
            )
        else:
            decision = "REJECT"
            reason = (
                f"Reliability score ({reliability_score:.3f}) is below verification threshold ({t_verify:.3f}). "
                f"The response is rejected as untrustworthy."
            )

        logger.info(f"Decision Engine: Made {decision} decision. Score: {reliability_score:.3f} (Thresholds: A={t_accept:.2f}, V={t_verify:.2f})")
        
        return {
            "decision": decision,
            "reliability_score": reliability_score,
            "reason": reason,
            "thresholds": {
                "accept": t_accept,
                "verify": t_verify
            }
        }
