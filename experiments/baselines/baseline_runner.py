"""
baseline_runner.py — Multi-seed baseline experiment runner.
Answers RQ1–RQ6 by comparing Proposed vs Baselines A/B/C across NUM_SEEDS seeds.
"""
import logging
import numpy as np
from typing import Dict, Any, List
from evaluation.benchmark_runner import BenchmarkRunner, PROPOSED, BASELINE_A, BASELINE_B, BASELINE_C
from experiments.experiment_config import SKILLS_MEDIUM, BIASES_DEFAULT, NUM_SEEDS, RUNS_PER_SEED

logger = logging.getLogger("trust_framework")


def run_baseline_experiments(num_seeds: int = NUM_SEEDS,
                              runs_per_seed: int = RUNS_PER_SEED) -> Dict[str, Any]:
    """
    Run all 4 conditions over num_seeds independent seeds.
    Returns per-condition metric arrays for downstream statistical analysis.
    """
    logger.info(f"BaselineRunner: Starting {num_seeds} seeds × {runs_per_seed} runs per condition")

    # per-condition per-metric accumulator
    accumulator: Dict[str, Dict[str, List[float]]] = {
        cond: {"success_rate": [], "f1_score": [], "ece": [],
               "accept_rate": [], "filter_ratio": [], "top1_accuracy": [],
               "average_e2e_latency_s": []}
        for cond in [PROPOSED, BASELINE_A, BASELINE_B, BASELINE_C]
    }

    for seed in range(num_seeds):
        np.random.seed(seed)
        runner = BenchmarkRunner()
        results = runner.run_all(num_runs=runs_per_seed,
                                 agent_skills=SKILLS_MEDIUM,
                                 agent_biases=BIASES_DEFAULT)
        for cond, data in results.items():
            acc = accumulator[cond]
            acc["success_rate"].append(data["task"]["success_rate"])
            acc["f1_score"].append(data["task"]["f1_score"])
            acc["ece"].append(data["confidence"]["ece"])
            acc["accept_rate"].append(data["decision"]["accept_rate"])
            acc["filter_ratio"].append(data["communication"]["filter_ratio"])
            acc["top1_accuracy"].append(data["attribution"]["top1_accuracy"])
            acc["average_e2e_latency_s"].append(data["system"]["average_e2e_latency_s"])

    logger.info("BaselineRunner: All seeds complete.")
    return accumulator
