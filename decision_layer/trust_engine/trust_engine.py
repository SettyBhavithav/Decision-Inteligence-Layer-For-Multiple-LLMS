import logging
import datetime
from typing import Dict, Any, List

from decision_layer.trust_engine.models import TrustUpdate, TrustPackage
from decision_layer.trust_engine.trust_store import TrustStore
from decision_layer.trust_engine.trust_calculator import RuleBasedTrustCalculator, BayesianTrustCalculator, ProposedTrustCalculator
from decision_layer.trust_engine.trust_updater import TrustUpdater
from decision_layer.trust_engine.trust_history import TrustHistoryManager
from decision_layer.trust_engine.trust_explainer import TrustExplainer
from decision_layer.trust_engine.trust_validator import TrustValidator
from decision_layer.trust_engine.trust_package import TrustPackageGenerator
from decision_layer.trust_engine.trust_metrics import TrustMetricsTracker

logger = logging.getLogger("trust_framework")

class TrustEngine:
    """
    Novel Dynamic Trust Engine orchestrating pluggable calculators:
    1. Rule-Based updates (baseline)
    2. Bayesian Beta updates (baseline)
    3. Proposed EMA + Quadratic Penalty updates (our algorithm)
    """
    def __init__(self, 
                 algorithm: str = "proposed", 
                 model: str = "nvidia/nvidia-nemotron-nano-9b-v2",
                 initial_trust: float = 0.80,
                 eta_success: float = 0.15,
                 eta_failure: float = 0.25,
                 eta_decay: float = 0.02):
        self.initial_trust = initial_trust
        self.eta_success = eta_success
        self.eta_failure = eta_failure
        self.eta_decay = eta_decay
        
        self.store = TrustStore(initial_trust)
        self.updater = TrustUpdater(self.store)
        self.history_mgr = TrustHistoryManager()
        self.explainer = TrustExplainer(model)
        self.validator = TrustValidator()
        self.package_gen = TrustPackageGenerator()
        self.tracker = TrustMetricsTracker()
        
        # Pluggable algorithm configuration
        self.algorithm_name = algorithm.strip().lower()
        if self.algorithm_name == "rule_based":
            self.calculator = RuleBasedTrustCalculator(eta_success, eta_failure)
        elif self.algorithm_name == "bayesian":
            self.calculator = BayesianTrustCalculator()
        else:
            self.calculator = ProposedTrustCalculator()
            
        logger.info(f"TrustEngine: Initialized using pluggable calculator: '{self.algorithm_name}'")

    def update_trust(self, agent_id: str, verification_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a trust evaluation step for a specified collaborator.
        Returns serialized TrustPackage dictionary.
        """
        logger.info(f"TrustEngine: Evaluating trust updates for agent '{agent_id}' using '{self.algorithm_name}'")
        
        self.tracker.start_timer()
        
        # 1. Fetch current trust values
        current_record = self.store.get_trust(agent_id)
        previous_trust = current_record.trust_score
        
        # 2. Calculate updated trust score
        new_trust = self.calculator.calculate(previous_trust, verification_metrics)
        
        # 3. Validate boundaries
        if not self.validator.validate_trust(new_trust):
            self.tracker.log_failed()
            self.tracker.stop_timer()
            # Suppress bad update, fallback to previous trust
            new_trust = previous_trust
            
        # 4. Save to Store
        success = verification_metrics.get("success", True)
        self.updater.update(agent_id, new_trust, success)
        
        # 5. Generate dynamic explanation
        explanation = self.explainer.explain_change(
            agent_id=agent_id,
            previous_trust=previous_trust,
            updated_trust=new_trust,
            metrics=verification_metrics
        )
        
        # 6. Log historical ledger entry
        timestamp = datetime.datetime.now().isoformat()
        diff = new_trust - previous_trust
        change_sign = f"+{diff:.3f}" if diff >= 0 else f"{diff:.3f}"
        
        update_record = TrustUpdate(
            agent_id=agent_id,
            previous_trust=previous_trust,
            updated_trust=new_trust,
            change=change_sign,
            reason=explanation,
            timestamp=timestamp
        )
        self.history_mgr.log_update(update_record)
        
        self.tracker.stop_timer()
        
        # 7. Compile final Trust Package
        history = self.history_mgr.get_history(agent_id)
        metrics = self.tracker.compile_metrics(new_trust, diff, history)
        
        package = self.package_gen.build_package(
            agent_id=agent_id,
            trust_score=new_trust,
            history=history,
            metrics=metrics
        )
        
        logger.info(f"TrustEngine: Trust calculation step complete. New trust score: {new_trust:.3f}")
        return package.model_dump()

    def get_trust(self, agent_role: str) -> float:
        """Get current trust score of an agent role. For backward compatibility."""
        role = agent_role.lower()
        return self.store.get_trust(role).trust_score

    def update_trust_on_success(self, agent_role: str, w_contrib: float = 1.0) -> float:
        """Success update for backward compatibility."""
        role = agent_role.lower()
        t_curr = self.get_trust(role)
        t_new = t_curr + self.eta_success * (1.0 - t_curr) * w_contrib
        t_new = max(0.0, min(1.0, t_new))
        self.store.set_trust(role, t_new, success=True)
        
        timestamp = datetime.datetime.now().isoformat()
        update_record = TrustUpdate(
            agent_id=role,
            previous_trust=t_curr,
            updated_trust=t_new,
            change=f"+{t_new-t_curr:.3f}",
            reason="Rule-based success update",
            timestamp=timestamp
        )
        self.history_mgr.log_update(update_record)
        return t_new

    def update_trust_on_failure(self, responsible_role: str, active_roles: List[str]) -> None:
        """Failure update for backward compatibility."""
        resp_role = responsible_role.lower()
        t_curr = self.get_trust(resp_role)
        t_new = t_curr - self.eta_failure * t_curr
        t_new = max(0.0, min(1.0, t_new))
        self.store.set_trust(resp_role, t_new, success=False)
        
        timestamp = datetime.datetime.now().isoformat()
        update_record = TrustUpdate(
            agent_id=resp_role,
            previous_trust=t_curr,
            updated_trust=t_new,
            change=f"{t_new-t_curr:.3f}",
            reason="Rule-based failure penalty",
            timestamp=timestamp
        )
        self.history_mgr.log_update(update_record)
        
        for role in active_roles:
            role_lower = role.lower()
            if role_lower == resp_role:
                continue
            t_c = self.get_trust(role_lower)
            t_n = t_c - self.eta_decay * t_c
            t_n = max(0.0, min(1.0, t_n))
            self.store.set_trust(role_lower, t_n, success=True)

    def get_all_trust_scores(self) -> Dict[str, float]:
        """Get dictionary copy of all scores. For backward compatibility."""
        with self.store._lock:
            return {k: v.trust_score for k, v in self.store._store.items()}
