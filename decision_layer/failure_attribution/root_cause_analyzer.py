import logging
import math
from typing import Dict, Any, List
from decision_layer.failure_attribution.models import RootCause

logger = logging.getLogger("trust_framework")

class RootCauseAnalyzer:
    """Submodule 3: Pinpoints the originating culprit agent and estimates attribution confidence."""
    def __init__(self):
        pass

    def analyze_root_cause(self, failure_type: str, metrics: Dict[str, Any]) -> RootCause:
        # Default likelihoods dictionary mapping culprit agents (small base for all)
        likelihoods = {"research": 0.02, "writing": 0.02, "citation": 0.02, "reviewer": 0.02, "verification": 0.02}
        
        category = failure_type.strip().lower()
        
        if "hallucination" in category or "verification" in category:
            likelihoods["research"] = 2.50
            likelihoods["writing"] = 1.00
            likelihoods["verification"] = 0.30
        elif "citation" in category:
            likelihoods["citation"] = 3.50
            likelihoods["research"] = 0.40
            likelihoods["writing"] = 0.10
        elif "unsupported" in category:
            likelihoods["research"] = 3.00
            likelihoods["writing"] = 0.60
        elif "planning" in category:
            likelihoods["planner"] = 3.50
            likelihoods["research"] = 0.20
        else:
            # Fallback — mild preference toward research and writing
            likelihoods["research"] = 1.00
            likelihoods["writing"] = 0.80
            
        # Apply softmax normalization: P(a) = e^L(a) / sum(e^L(j))
        exps = {k: math.exp(v) for k, v in likelihoods.items()}
        sum_exps = sum(exps.values())
        confidences = {k: v / sum_exps for k, v in exps.items()}
        
        # Sort candidates descending
        sorted_candidates = sorted(confidences.items(), key=lambda x: x[1], reverse=True)
        
        top_agent, top_conf = sorted_candidates[0]
        
        alternative_candidates = []
        for agent, conf in sorted_candidates[1:3]:
            alternative_candidates.append({"agent": agent, "confidence": round(conf, 3)})
            
        logger.info(f"RootCauseAnalyzer: Primary culprit: '{top_agent}' with confidence {top_conf:.3f}")
        return RootCause(
            responsible_agent=top_agent,
            attribution_confidence=round(top_conf, 3),
            alternative_candidates=alternative_candidates
        )
