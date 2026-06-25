"""
robustness_runner.py — Tests framework behavior under 7 adversarial scenarios.
Each scenario degrades specific agent skills to simulate challenging conditions.
"""
import logging
import numpy as np
from typing import Dict, Any
from evaluation.benchmark_runner import BenchmarkRunner, PROPOSED
from experiments.experiment_config import (SKILLS_MEDIUM, BIASES_DEFAULT,
                                           ROBUSTNESS_SCENARIOS, ROBUSTNESS_RUNS)

logger = logging.getLogger("trust_framework")


def run_robustness_experiments(runs: int = ROBUSTNESS_RUNS) -> Dict[str, Any]:
    """
    For each scenario, degrade agent skills accordingly and run the Proposed framework.
    Also record the clean baseline for comparison delta.
    """
    logger.info(f"RobustnessRunner: Testing {len(ROBUSTNESS_SCENARIOS)} adversarial scenarios")
    results: Dict[str, Any] = {}

    # Clean reference
    np.random.seed(0)
    clean_runner = BenchmarkRunner()
    clean_res = clean_runner.run_all(num_runs=runs,
                                     agent_skills=SKILLS_MEDIUM,
                                     agent_biases=BIASES_DEFAULT)
    clean_metrics = clean_res[PROPOSED]

    for scenario_name, degradations in ROBUSTNESS_SCENARIOS.items():
        np.random.seed(1)
        # Build degraded skill profile
        skills = dict(SKILLS_MEDIUM)
        bypass = True

        bypass_override = degradations.pop("bypass_comm_override", None)
        for role, delta in degradations.items():
            if role in skills:
                skills[role] = max(0.20, skills[role] + delta)
        if bypass_override is not None:
            bypass = bypass_override

        runner = BenchmarkRunner()
        degraded = runner._run_condition(
            condition_name=scenario_name,
            num_runs=runs,
            bypass_comm=bypass,
            static_trust=False,
            calibration=True,
            use_fae=True,
            agent_skills=skills,
            agent_biases=BIASES_DEFAULT
        )

        delta_success = degraded["task"]["success_rate"] - clean_metrics["task"]["success_rate"]
        results[scenario_name] = {
            "metrics": degraded,
            "clean_reference": clean_metrics,
            "degradation_delta": {
                "success_rate": round(delta_success, 4),
                "f1_drop":      round(degraded["task"]["f1_score"]
                                      - clean_metrics["task"]["f1_score"], 4),
            }
        }
        logger.info(f"RobustnessRunner [{scenario_name}]: ΔSuccess={delta_success:+.3f}")

    return results
