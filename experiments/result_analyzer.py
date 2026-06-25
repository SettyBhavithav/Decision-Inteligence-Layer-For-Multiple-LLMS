"""
result_analyzer.py — Aggregates multi-seed results into summary statistics.
"""
import numpy as np
import logging
from typing import Dict, Any, List
from evaluation.benchmark_runner import PROPOSED, BASELINE_A, BASELINE_B, BASELINE_C
from evaluation.statistical_analysis import StatisticalAnalysis

logger = logging.getLogger("trust_framework")

CONDITIONS = [PROPOSED, BASELINE_A, BASELINE_B, BASELINE_C]
CORE_METRICS = ["success_rate", "f1_score", "ece", "accept_rate",
                "filter_ratio", "top1_accuracy", "average_e2e_latency_s"]


def aggregate_baseline_results(accumulator: Dict[str, Dict[str, List[float]]]) -> Dict[str, Any]:
    """
    For each condition × metric: compute mean, std, 95% CI.
    Also build cross-condition delta table (Proposed minus each baseline).
    """
    summary: Dict[str, Any] = {"per_condition": {}, "deltas": {}}

    for cond in CONDITIONS:
        summary["per_condition"][cond] = {}
        for metric in CORE_METRICS:
            vals = accumulator.get(cond, {}).get(metric, [])
            if vals:
                summary["per_condition"][cond][metric] = StatisticalAnalysis.describe(vals)
            else:
                summary["per_condition"][cond][metric] = {"mean": 0.0, "std": 0.0}

    # Delta: Proposed vs each baseline
    for bl in [BASELINE_A, BASELINE_B, BASELINE_C]:
        summary["deltas"][bl] = {}
        for metric in CORE_METRICS:
            p_mean = summary["per_condition"].get(PROPOSED, {}).get(metric, {}).get("mean", 0.0)
            b_mean = summary["per_condition"].get(bl, {}).get(metric, {}).get("mean", 0.0)
            summary["deltas"][bl][metric] = round(p_mean - b_mean, 4)

    return summary


def find_best_worst_seed(accumulator: Dict[str, Dict[str, List[float]]],
                          metric: str = "success_rate") -> Dict[str, int]:
    """Identify which seed produced best/worst result for the Proposed condition."""
    vals = accumulator.get(PROPOSED, {}).get(metric, [])
    if not vals:
        return {"best_seed": -1, "worst_seed": -1}
    return {
        "best_seed":  int(np.argmax(vals)),
        "worst_seed": int(np.argmin(vals)),
        "best_value": round(float(np.max(vals)), 4),
        "worst_value": round(float(np.min(vals)), 4),
    }
