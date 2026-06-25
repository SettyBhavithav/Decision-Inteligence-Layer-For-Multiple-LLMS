"""
experiment_runner.py — Master orchestrator for all Phase 25 experiments.
Runs the full experimental pipeline in a single command:
  python experiments/experiment_runner.py
"""
import os
import sys
import json
import logging
import time

# Ensure project root is on the path when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from experiments.experiment_config import OUT_RESULTS_JSON
from experiments.baselines.baseline_runner import run_baseline_experiments
from experiments.ablation.ablation_runner import run_ablation_experiments
from experiments.hyperparameter.hyperparameter_runner import run_hyperparameter_sweep
from experiments.robustness.robustness_runner import run_robustness_experiments
from experiments.scalability.scalability_runner import run_scalability_experiments
from experiments.statistical_tests import run_statistical_tests
from experiments.result_analyzer import aggregate_baseline_results, find_best_worst_seed
from experiments.report_generator import generate_report
from experiments.visualizations.viz_generator import generate_all_visualizations

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger("trust_framework")


def run_all_experiments(num_seeds: int = 10, quick: bool = False) -> dict:
    """
    Run the complete Phase 25 experimental suite.

    Args:
        num_seeds: Number of cross-seed runs (default 10 for publication, 3 for quick test).
        quick:     If True, use 3 seeds and 3 runs/seed for fast local validation.
    """
    seeds = 3 if quick else num_seeds
    runs  = 3 if quick else 5

    wall_start = time.time()
    logger.info("=" * 60)
    logger.info("PHASE 25 — EXPERIMENTAL FRAMEWORK — START")
    logger.info("=" * 60)

    # 1. Baseline experiments (RQ1–RQ6)
    logger.info("\n[1/7] Running baseline experiments …")
    baseline_acc = run_baseline_experiments(num_seeds=seeds, runs_per_seed=runs)

    # 2. Ablation studies
    logger.info("\n[2/7] Running ablation studies …")
    ablation_res = run_ablation_experiments(runs=runs)

    # 3. Hyperparameter sweeps
    logger.info("\n[3/7] Running hyperparameter sweeps …")
    hyperparam_res = run_hyperparameter_sweep(runs_per_point=runs)

    # 4. Robustness tests
    logger.info("\n[4/7] Running robustness tests …")
    robustness_res = run_robustness_experiments(runs=runs)

    # 5. Scalability tests
    logger.info("\n[5/7] Running scalability experiments …")
    scalability_res = run_scalability_experiments(runs=runs)

    # 6. Statistical analysis
    logger.info("\n[6/7] Computing statistical tests …")
    rq_results = run_statistical_tests(baseline_acc)
    summary    = aggregate_baseline_results(baseline_acc)
    seed_info  = find_best_worst_seed(baseline_acc)

    # 7. Reports & Visualizations
    logger.info("\n[7/7] Generating reports and visualizations …")
    generate_report(summary, rq_results, ablation_res, robustness_res, scalability_res)
    chart_paths = generate_all_visualizations(summary, baseline_acc, ablation_res, scalability_res)

    # Package all results
    all_results = {
        "baseline_summary":     summary,
        "rq_results":           rq_results,
        "ablation":             {k: v["delta"] for k, v in ablation_res.items()},
        "hyperparameter":       hyperparam_res,
        "robustness":           {k: v["degradation_delta"] for k, v in robustness_res.items()},
        "scalability":          scalability_res,
        "seed_info":            seed_info,
        "charts_generated":     len(chart_paths),
        "wall_time_seconds":    round(time.time() - wall_start, 2),
    }

    os.makedirs(os.path.dirname(OUT_RESULTS_JSON), exist_ok=True)
    with open(OUT_RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    logger.info("=" * 60)
    logger.info(f"PHASE 25 COMPLETE in {all_results['wall_time_seconds']}s")
    logger.info(f"Results → {OUT_RESULTS_JSON}")
    logger.info(f"Charts  → experiments/visualizations/ ({len(chart_paths)} files)")
    logger.info(f"Report  → experiments/REPORT.md")
    logger.info("=" * 60)
    return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Phase 25 Experimental Framework")
    parser.add_argument("--quick", action="store_true",
                        help="Run quick validation (3 seeds, 3 runs each)")
    parser.add_argument("--seeds", type=int, default=10,
                        help="Number of cross-seed runs (default: 10)")
    args = parser.parse_args()
    run_all_experiments(num_seeds=args.seeds, quick=args.quick)
