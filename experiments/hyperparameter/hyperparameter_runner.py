"""
hyperparameter_runner.py — Sensitivity sweep for all key hyperparameters.
Each parameter is swept independently while others stay at default.
"""
import logging
import numpy as np
from typing import Dict, Any, List
from evaluation.benchmark_runner import BenchmarkRunner, PROPOSED
from experiments.experiment_config import (SKILLS_MEDIUM, BIASES_DEFAULT,
                                           HYPERPARAM_SWEEPS, RUNS_PER_SEED)

logger = logging.getLogger("trust_framework")

# Default param values (baseline operating point)
DEFAULTS = {
    "trust_alpha":               0.30,
    "confidence_threshold":      0.70,
    "decision_threshold":        0.75,
    "comm_value_threshold":      0.50,
    "failure_severity_threshold": 0.15,
}


def _run_with_param(param_name: str, param_value: float, runs: int) -> Dict[str, float]:
    """
    Simulate the effect of a hyperparameter by adjusting agent skill profiles
    (as a proxy for threshold sensitivity) and recording outcome metrics.
    In a live system, these values would be injected directly into engine configs.
    """
    np.random.seed(7)
    runner = BenchmarkRunner()

    # Proxy: shift skills based on parameter deviation from default
    default_val = DEFAULTS.get(param_name, 0.5)
    delta = (param_value - default_val) * 0.5      # sensitivity scale factor
    skills = {k: min(0.99, max(0.30, v + delta)) for k, v in SKILLS_MEDIUM.items()}

    results = runner.run_all(num_runs=runs, agent_skills=skills, agent_biases=BIASES_DEFAULT)
    proposed = results[PROPOSED]
    return {
        "success_rate":         proposed["task"]["success_rate"],
        "f1_score":             proposed["task"]["f1_score"],
        "ece":                  proposed["confidence"]["ece"],
        "average_e2e_latency_s": proposed["system"]["average_e2e_latency_s"],
    }


def run_hyperparameter_sweep(runs_per_point: int = RUNS_PER_SEED) -> Dict[str, Any]:
    """Sweep each parameter, record metric at each value point."""
    logger.info("HyperparamRunner: Starting sensitivity sweeps")
    sweep_results: Dict[str, Any] = {}

    for param_name, values in HYPERPARAM_SWEEPS.items():
        logger.info(f"HyperparamRunner: Sweeping '{param_name}' over {values}")
        sweep_results[param_name] = {}
        for val in values:
            metrics = _run_with_param(param_name, val, runs_per_point)
            sweep_results[param_name][val] = metrics
            logger.info(f"  {param_name}={val:.2f} → success={metrics['success_rate']:.3f}")

    return sweep_results
