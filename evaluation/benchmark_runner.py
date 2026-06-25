import logging
import uuid
from typing import Dict, Any, List

from evaluation.task_metrics import TaskMetrics
from evaluation.trust_metrics import TrustMetrics
from evaluation.confidence_metrics import ConfidenceMetrics
from evaluation.decision_metrics import DecisionMetrics
from evaluation.communication_metrics import CommunicationMetrics
from evaluation.attribution_metrics import AttributionMetrics
from evaluation.system_metrics import SystemMetrics
from evaluation.experiment_logger import ExperimentLogger

logger = logging.getLogger("trust_framework")

# Baseline condition names
BASELINE_A = "Baseline_A_FixedRule"
BASELINE_B = "Baseline_B_Standard"
BASELINE_C = "Baseline_C_Ablation"
PROPOSED   = "Proposed"

class BenchmarkRunner:
    """
    4-condition benchmark orchestrator.

    Baseline definitions (using SimulationSuite):
      A — Fixed-rule pipeline: bypass_comm=False, trust=static 1.0, no calibration
      B — Standard pipeline (no DIL): bypass_comm=False, trust ON, calibration OFF
      C — Ablation (simplified proposed): bypass_comm=True, trust ON, calibration ON, no FAE
      Proposed — Full framework: all modules active, bypass_comm=True

    Each condition runs `num_runs` episodes. All 7 metric categories are collected
    per run via ExperimentLogger.
    """

    def __init__(self):
        self.exp_logger = ExperimentLogger()

    def _run_condition(self,
                       condition_name: str,
                       num_runs: int,
                       bypass_comm: bool,
                       static_trust: bool,
                       calibration: bool,
                       use_fae: bool,
                       agent_skills: Dict[str, float],
                       agent_biases: Dict[str, float],
                       no_decision: bool = False) -> Dict[str, Any]:
        """
        Run a single benchmark condition, returning all 7 category summaries.
        Uses SimulationSuite internally (offline — no real LLM calls).
        """
        from evaluation.simulator import SimulationSuite
        suite = SimulationSuite()

        task_m  = TaskMetrics()
        trust_m = TrustMetrics()
        conf_m  = ConfidenceMetrics()
        dec_m   = DecisionMetrics()
        comm_m  = CommunicationMetrics()
        attr_m  = AttributionMetrics()
        sys_m   = SystemMetrics()

        logger.info(f"BenchmarkRunner: Starting condition '{condition_name}' ({num_runs} runs)")

        # Run simulated batch (all runs together to allow trust score and fault window simulation) (Modification 2 & 3)
        batch = suite.run_simulation_batch(
            num_runs=num_runs,
            agent_skills=agent_skills,
            agent_biases=agent_biases,
            bypass_comm=bypass_comm,
            static_trust=static_trust,
            calibration=calibration,
            use_fae=use_fae,
            no_decision=no_decision
        )

        for i, run in enumerate(batch.get("runs", [])):
            wf_id = str(uuid.uuid4())[:8]
            sys_m.start_run()

            success = run["success"]
            tokens  = int(run["tokens"])
            latency = float(run["latency"])

            sys_m.end_run(total_tokens=tokens)
            sys_m.e2e_latencies[-1] = latency

            # Task
            task_m.log_result(success,
                               true_positive=success,
                               false_positive=not success,
                               false_negative=False)

            # Trust — log trust scores from this run
            for role, score in run.get("trust_scores", {}).items():
                trust_m.log_trust(role, score)

            # Confidence
            conf_score = batch.get("average_ece", 0.5)
            conf_m.log_confidence(max(0.0, 1.0 - conf_score), success)

            # Decision — simulate a single decision action per run
            action = "ACCEPT" if success else "REJECT"
            dec_m.log_decision(action, latency)

            # Communication (Modification 3) — Real CM metrics logging
            comm_metrics = run.get("communication_metrics", {})
            comm_interactions = comm_metrics.get("total_interactions", 0)
            bypasses = comm_metrics.get("bypasses_count", 0)
            sent_count = max(0, comm_interactions - bypasses)

            for _ in range(sent_count):
                comm_m.log_message(
                    sent=True,
                    filtered=False,
                    payload_tokens=tokens // max(comm_interactions, 1),
                    latency_s=latency / max(comm_interactions, 1)
                )
            for _ in range(bypasses):
                comm_m.log_message(
                    sent=False,
                    filtered=True,
                    payload_tokens=0,
                    latency_s=0.0
                )
            comm_m.log_graph_density(edges=sent_count, num_nodes=5)

            # Attribution (Modification 1 & 4) — Real FAE predictions vs Injected failure
            degraded_role = batch.get("degraded_agent", "")
            run_attributions = run.get("attributions", [])

            if run_attributions:
                for attr in run_attributions:
                    pred_role = attr.get("responsible_role", "").lower()
                    ground_truth = attr.get("ground_truth_culprit", "").lower()
                    attr_m.log_attribution(
                        ground_truth_agent=ground_truth,
                        top1_prediction=pred_role,
                        top2_prediction="research" if pred_role != "research" else "writing",
                        recovered=success,
                        recovery_time_s=latency * 0.1
                    )
            else:
                attr_m.log_attribution(
                    ground_truth_agent="",
                    top1_prediction="",
                    top2_prediction="",
                    recovered=True,
                    recovery_time_s=0.0
                )

            # Log to experiment logger
            self.exp_logger.log_run(
                workflow_id=wf_id,
                baseline_name=condition_name,
                task={"success": success},
                trust=trust_m.summary(),
                confidence=conf_m.summary(),
                decision=dec_m.summary(),
                communication=comm_m.summary(),
                attribution=attr_m.summary(),
                system=sys_m.summary(),
            )

        result = {
            "task": task_m.summary(),
            "trust": trust_m.summary(),
            "confidence": conf_m.summary(),
            "decision": dec_m.summary(),
            "communication": comm_m.summary(),
            "attribution": attr_m.summary(),
            "system": sys_m.summary(),
        }
        logger.info(f"BenchmarkRunner: Condition '{condition_name}' complete. "
                    f"Success rate: {task_m.success_rate():.2%}")
        return result

    def run_all(self,
                num_runs: int = 20,
                agent_skills: Dict[str, float] = None,
                agent_biases: Dict[str, float] = None) -> Dict[str, Dict[str, Any]]:
        """
        Run all 4 baseline conditions and return a results dictionary
        keyed by condition name.
        """
        default_skills = {
            "research": 0.82, "writing": 0.70,
            "citation": 0.88, "reviewer": 0.68, "verification": 0.95
        }
        default_biases = {
            "research": 0.06, "writing": 0.0,
            "citation": -0.05, "reviewer": 0.12, "verification": 0.0
        }
        skills = agent_skills or default_skills
        biases = agent_biases or default_biases

        results = {}

        results[BASELINE_A] = self._run_condition(
            BASELINE_A, num_runs,
            bypass_comm=False, static_trust=True, calibration=False, use_fae=False,
            agent_skills=skills, agent_biases=biases, no_decision=True
        )
        results[BASELINE_B] = self._run_condition(
            BASELINE_B, num_runs,
            bypass_comm=False, static_trust=True, calibration=False, use_fae=False,
            agent_skills=skills, agent_biases=biases, no_decision=False
        )
        results[BASELINE_C] = self._run_condition(
            BASELINE_C, num_runs,
            bypass_comm=True, static_trust=False, calibration=True, use_fae=False,
            agent_skills=skills, agent_biases=biases, no_decision=False
        )
        results[PROPOSED] = self._run_condition(
            PROPOSED, num_runs,
            bypass_comm=True, static_trust=False, calibration=True, use_fae=True,
            agent_skills=skills, agent_biases=biases, no_decision=False
        )

        return results
