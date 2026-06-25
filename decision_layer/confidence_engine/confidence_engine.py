import logging
import datetime
from typing import Dict, Any

from decision_layer.confidence_engine.models import ConfidenceUpdate, ConfidencePackage
from decision_layer.confidence_engine.confidence_store import ConfidenceStore
from decision_layer.confidence_engine.confidence_calculator import RuleBasedConfidenceCalculator, BayesianConfidenceCalculator, ProposedConfidenceCalculator
from decision_layer.confidence_engine.confidence_updater import ConfidenceUpdater
from decision_layer.confidence_engine.confidence_history import ConfidenceHistoryManager
from decision_layer.confidence_engine.confidence_explainer import ConfidenceExplainer
from decision_layer.confidence_engine.confidence_validator import ConfidenceValidator
from decision_layer.confidence_engine.confidence_package import ConfidencePackageGenerator
from decision_layer.confidence_engine.confidence_metrics import ConfidenceMetricsTracker

logger = logging.getLogger("trust_framework")

class ConfidenceEngine:
    """
    Novel Confidence Engine orchestrating pluggable calculators:
    1. Rule-Based updates (baseline)
    2. Bayesian conjugate updates (baseline)
    3. Proposed Adaptive Claim-Aware updates (our algorithm)
    """
    def __init__(self, algorithm: str = "proposed", model: str = "nvidia/nvidia-nemotron-nano-9b-v2", initial_confidence: float = 0.85):
        self.initial_confidence = initial_confidence
        self.store = ConfidenceStore(initial_confidence)
        self.updater = ConfidenceUpdater(self.store)
        self.history_mgr = ConfidenceHistoryManager()
        self.explainer = ConfidenceExplainer(model)
        self.validator = ConfidenceValidator()
        self.package_gen = ConfidencePackageGenerator()
        self.tracker = ConfidenceMetricsTracker()
        
        # Pluggable algorithm configuration
        self.algorithm_name = algorithm.strip().lower()
        if self.algorithm_name == "rule_based":
            self.calculator = RuleBasedConfidenceCalculator()
        elif self.algorithm_name == "bayesian":
            self.calculator = BayesianConfidenceCalculator()
        else:
            self.calculator = ProposedConfidenceCalculator()
            
        logger.info(f"ConfidenceEngine: Initialized using pluggable calculator: '{self.algorithm_name}'")

    def estimate_confidence(self, agent_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates and records the confidence estimation for an agent's output.
        Returns serialized ConfidencePackage dictionary.
        """
        logger.info(f"ConfidenceEngine: Estimating confidence for agent '{agent_id}' using '{self.algorithm_name}'")
        
        self.tracker.start_timer()
        
        # 1. Fetch previous confidence value
        current_record = self.store.get_confidence(agent_id)
        previous_conf = current_record.confidence_score
        
        # 2. Calculate updated confidence score
        new_conf = self.calculator.calculate(metrics)
        
        # 3. Validate boundaries
        if not self.validator.validate_confidence(new_conf):
            self.tracker.log_failed()
            self.tracker.stop_timer()
            new_conf = previous_conf
            
        # 4. Save to Store
        self.updater.update(agent_id, new_conf, self.algorithm_name)
        
        # 5. Generate dynamic explanation
        explanation = self.explainer.explain_confidence(
            agent_id=agent_id,
            previous_conf=previous_conf,
            updated_conf=new_conf,
            metrics=metrics
        )
        
        # 6. Log historical ledger entry
        timestamp = datetime.datetime.now().isoformat()
        diff = new_conf - previous_conf
        change_sign = f"+{diff:.3f}" if diff >= 0 else f"{diff:.3f}"
        
        update_record = ConfidenceUpdate(
            agent_id=agent_id,
            previous_confidence=previous_conf,
            updated_confidence=new_conf,
            change=change_sign,
            reason=explanation,
            timestamp=timestamp
        )
        self.history_mgr.log_update(update_record)
        
        self.tracker.stop_timer()
        
        # 7. Compile final Confidence Package
        history = self.history_mgr.get_history(agent_id)
        metrics_summary = self.tracker.compile_metrics(new_conf, diff, history)
        
        package = self.package_gen.build_package(
            agent_id=agent_id,
            confidence=new_conf,
            algorithm=self.algorithm_name,
            history=history,
            metrics=metrics_summary
        )
        
        logger.info(f"ConfidenceEngine: Confidence estimation complete. Score: {new_conf:.3f}")
        return package.model_dump()
