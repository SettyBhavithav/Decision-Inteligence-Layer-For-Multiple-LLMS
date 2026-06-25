"""
statistical_tests.py — RQ-level statistical significance testing.
Wraps StatisticalAnalysis from Phase 24 to answer RQ1–RQ6 with p-values and Cohen's d.
"""
import logging
from typing import Dict, Any, List
from evaluation.benchmark_runner import PROPOSED, BASELINE_A, BASELINE_B, BASELINE_C
from evaluation.statistical_analysis import StatisticalAnalysis

logger = logging.getLogger("trust_framework")

# Maps each RQ to the metric and condition it tests
RQ_DEFINITIONS = {
    "RQ1": {"metric": "success_rate",          "description": "Task quality vs baselines"},
    "RQ2": {"metric": "success_rate",          "description": "Long-term reliability (trust engine)"},
    "RQ3": {"metric": "ece",                   "description": "Confidence calibration quality"},
    "RQ4": {"metric": "accept_rate",           "description": "Decision correctness & efficiency"},
    "RQ5": {"metric": "filter_ratio",          "description": "Communication overhead reduction"},
    "RQ6": {"metric": "top1_accuracy",         "description": "Failure attribution accuracy"},
}

EFFECT_SIZE_LABELS = {
    lambda d: abs(d) < 0.2: "negligible",
    lambda d: 0.2 <= abs(d) < 0.5: "small",
    lambda d: 0.5 <= abs(d) < 0.8: "medium",
    lambda d: abs(d) >= 0.8: "large",
}


def _effect_label(d: float) -> str:
    if abs(d) >= 0.8: return "large"
    if abs(d) >= 0.5: return "medium"
    if abs(d) >= 0.2: return "small"
    return "negligible"


def run_statistical_tests(baseline_accumulator: Dict[str, Dict[str, List[float]]]) -> Dict[str, Any]:
    """
    For each RQ, run pairwise t-tests between Proposed and each baseline.
    Returns a structured RQ-answer table.
    """
    rq_results: Dict[str, Any] = {}

    for rq_id, rq_def in RQ_DEFINITIONS.items():
        metric  = rq_def["metric"]
        desc    = rq_def["description"]
        proposed_vals = baseline_accumulator.get(PROPOSED, {}).get(metric, [])
        rq_results[rq_id] = {"description": desc, "metric": metric, "comparisons": {}}

        for bl in [BASELINE_A, BASELINE_B, BASELINE_C]:
            bl_vals = baseline_accumulator.get(bl, {}).get(metric, [])
            if not proposed_vals or not bl_vals:
                continue
            # Pad to same length if needed
            n = min(len(proposed_vals), len(bl_vals))
            p_vals = proposed_vals[:n]
            b_vals = bl_vals[:n]

            ttest = StatisticalAnalysis.paired_ttest(p_vals, b_vals)
            d     = StatisticalAnalysis.cohens_d(p_vals, b_vals)
            p_desc = StatisticalAnalysis.describe(p_vals)
            b_desc = StatisticalAnalysis.describe(b_vals)

            rq_results[rq_id]["comparisons"][bl] = {
                "proposed_mean_std":  f"{p_desc['mean']:.3f} ± {p_desc['std']:.3f}",
                "baseline_mean_std":  f"{b_desc['mean']:.3f} ± {b_desc['std']:.3f}",
                "p_value":            ttest["p_value"],
                "significant":        ttest["significant"],
                "cohens_d":           d,
                "effect_size":        _effect_label(d),
            }
        logger.info(f"StatTests [{rq_id}]: {desc} — analysis complete")

    return rq_results
