import logging
import datetime
from typing import Dict, Any, List, Optional

from decision_layer.decision_engine.models import DecisionResult, DecisionPackage
from decision_layer.decision_engine.decision_store import DecisionStore
from decision_layer.decision_engine.decision_calculator import RuleBasedDecisionCalculator, WeightedDecisionCalculator, ProposedDecisionCalculator
from decision_layer.decision_engine.policy_manager import PolicyManager
from decision_layer.decision_engine.rule_engine import RuleEngine
from decision_layer.decision_engine.decision_history import DecisionHistoryManager
from decision_layer.decision_engine.decision_explainer import DecisionExplainer
from decision_layer.decision_engine.decision_validator import DecisionValidator
from decision_layer.decision_engine.decision_package import DecisionPackageGenerator
from decision_layer.decision_engine.decision_metrics import DecisionMetricsTracker

logger = logging.getLogger("trust_framework")

class DecisionEngine:
    """
    Modular Decision Engine implementing pluggable strategies:
    1. Rule-Based decisions (baseline)
    2. Weighted composite decisions (baseline)
    3. Proposed Adaptive Multi-Signal decision (our algorithm)
    
    Includes backward compatible legacy make_decision wrapper.
    """
    def __init__(self, 
                 algorithm: str = "proposed", 
                 model: str = "nvidia/nvidia-nemotron-nano-9b-v2",
                 theta_accept: float = 0.65, 
                 theta_verify: float = 0.35):
                 
        self.theta_accept = theta_accept
        self.theta_verify = theta_verify
        self.algorithm_name = algorithm.strip().lower()
        
        self.store = DecisionStore()
        self.policy_mgr = PolicyManager()
        self.rule_engine = RuleEngine()
        self.history_mgr = DecisionHistoryManager()
        self.explainer = DecisionExplainer(model)
        self.validator = DecisionValidator()
        self.package_gen = DecisionPackageGenerator()
        self.tracker = DecisionMetricsTracker()
        
        if self.algorithm_name == "rule_based":
            self.calculator = RuleBasedDecisionCalculator()
        elif self.algorithm_name == "weighted":
            self.calculator = WeightedDecisionCalculator()
        else:
            self.calculator = ProposedDecisionCalculator()
            
        logger.info(f"DecisionEngine: Initialized using pluggable calculator: '{self.algorithm_name}'")

    def evaluate_decision(self, workflow_id: str, inputs: Dict[str, float], limits: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluates a complete decision step for the multi-agent system.
        Inputs: Dict containing trust_score, confidence_score, verification_score, quality_score, hallucination_risk, evidence_coverage.
        """
        logger.info(f"DecisionEngine: Evaluating decision for workflow '{workflow_id}' using '{self.algorithm_name}'")
        self.tracker.start_timer()
        
        # 1. Rule Override Evaluation
        decision = self.rule_engine.evaluate_rules(inputs)
        
        # 2. Main Strategy Evaluation
        if not decision:
            decision = self.calculator.calculate_decision(inputs, limits)
            
        # 3. Boundary validation
        if not self.validator.validate_decision(decision, inputs):
            logger.warning("DecisionEngine: Invalid decision output. Defaulting to VERIFY.")
            decision = "VERIFY"
            
        # 4. Generate dynamic explanation
        explanation = self.explainer.explain_decision(decision, inputs)
        
        # 5. Save to Store and History
        timestamp = datetime.datetime.now().isoformat()
        res_record = DecisionResult(
            decision=decision,
            reason=explanation,
            timestamp=timestamp
        )
        self.store.set_decision(workflow_id, res_record)
        self.history_mgr.log_decision(workflow_id, res_record)
        
        self.tracker.log_decision_type(decision)
        self.tracker.stop_timer()
        
        # 6. Compile package
        history = self.history_mgr.get_history(workflow_id)
        metrics = self.tracker.compile_metrics()
        package = self.package_gen.build_package(
            workflow_id=workflow_id,
            decision=decision,
            algorithm=self.algorithm_name,
            explanation=explanation,
            inputs=inputs,
            history=history,
            metrics=metrics
        )
        
        logger.info(f"DecisionEngine: Decision evaluation step complete. Output: '{decision}'")
        return package.model_dump()

    def make_decision(self, 
                      trust_score: float, 
                      calibrated_conf: float, 
                      task_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy decision helper for backward compatibility.
        Scales thresholds based on task complexity.
        """
        complexity = task_metadata.get("complexity", "medium").lower()
        
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
                f"Reliability score ({reliability_score:.3f}) meets accept threshold ({t_accept:.3f}). "
                f"Agent Trust: {trust_score:.2f}, Calibrated Confidence: {calibrated_conf:.2f}."
            )
        elif reliability_score >= t_verify:
            decision = "VERIFY"
            reason = (
                f"Reliability score ({reliability_score:.3f}) falls between verification ({t_verify:.3f}) "
                f"and accept ({t_accept:.3f}) thresholds. Fact-checking required."
            )
        else:
            decision = "REJECT"
            reason = (
                f"Reliability score ({reliability_score:.3f}) is below verification threshold ({t_verify:.3f}). "
                f"The response is rejected."
            )

        logger.info(f"Decision Engine: Legacy decision is {decision}. Score: {reliability_score:.3f}")
        
        # Log to Store and History to make it trace-friendly
        timestamp = datetime.datetime.now().isoformat()
        res_record = DecisionResult(
            decision=decision,
            reason=reason,
            timestamp=timestamp
        )
        self.store.set_decision("legacy_workflow", res_record)
        self.history_mgr.log_decision("legacy_workflow", res_record)
        
        return {
            "decision": decision,
            "reliability_score": reliability_score,
            "reason": reason,
            "thresholds": {
                "accept": t_accept,
                "verify": t_verify
            }
        }
