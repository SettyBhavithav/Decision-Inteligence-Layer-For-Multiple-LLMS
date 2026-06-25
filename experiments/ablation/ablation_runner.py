"""
ablation_runner.py — Systematic ablation study runner (A1–A5).
Disables one module at a time and measures performance impact vs full Proposed framework.
"""
import logging
import numpy as np
from typing import Dict, Any, List
from evaluation.benchmark_runner import BenchmarkRunner, PROPOSED
from experiments.experiment_config import (SKILLS_MEDIUM, BIASES_DEFAULT,
                                           ABLATION_STUDIES, ABLATION_RUNS)

logger = logging.getLogger("trust_framework")


def run_ablation_experiments(runs: int = ABLATION_RUNS) -> Dict[str, Any]:
    """
    For each ablation study A1–A5:
      - Run the full Proposed framework as reference
      - Run the ablated condition
      - Compute delta (Proposed - Ablated) for key metrics
    """
    logger.info(f"AblationRunner: Running {len(ABLATION_STUDIES)} ablation studies ({runs} runs each)")

    results: Dict[str, Any] = {}

    # Proposed reference
    ref_runner = BenchmarkRunner()
    np.random.seed(42)
    ref_res = ref_runner.run_all(num_runs=runs,
                                 agent_skills=SKILLS_MEDIUM,
                                 agent_biases=BIASES_DEFAULT)
    ref_proposed = ref_res[PROPOSED]

    for ablation_id, flags in ABLATION_STUDIES.items():
        np.random.seed(42)
        runner = BenchmarkRunner()
        bypass = flags.get("bypass_comm", True)
        ablated = runner._run_condition(
            condition_name=ablation_id,
            num_runs=runs,
            bypass_comm=bypass,
            static_trust=flags.get("static_trust", False),
            calibration=flags.get("calibration", True),
            use_fae=flags.get("use_fae", True),
            agent_skills=SKILLS_MEDIUM,
            agent_biases=BIASES_DEFAULT,
            no_decision=flags.get("no_decision", False)
        )

        delta_success = (ref_proposed["task"]["success_rate"]
                         - ablated["task"]["success_rate"])
        delta_f1      = (ref_proposed["task"]["f1_score"]
                         - ablated["task"]["f1_score"])
        delta_latency = (ablated["system"]["average_e2e_latency_s"]
                         - ref_proposed["system"]["average_e2e_latency_s"])

        results[ablation_id] = {
            "ablated": ablated,
            "reference": ref_proposed,
            "delta": {
                "success_rate_drop": round(delta_success, 4),
                "f1_drop":           round(delta_f1, 4),
                "latency_increase_s": round(delta_latency, 4),
            }
        }
        logger.info(f"AblationRunner [{ablation_id}]: "
                    f"ΔSuccess={delta_success:+.3f}, ΔF1={delta_f1:+.3f}")

    return results
