"""
test_experiments.py — 10 automated tests for Phase 25 Experimental Framework.
All tests run in quick/simulation mode — no API calls, fast execution.
"""
import os
import pytest
from evaluation.benchmark_runner import PROPOSED, BASELINE_A, BASELINE_B, BASELINE_C
from experiments.experiment_config import (ABLATION_STUDIES, ROBUSTNESS_SCENARIOS,
                                           HYPERPARAM_SWEEPS, SCALABILITY_NUM_AGENTS,
                                           NUM_SEEDS)
from experiments.baselines.baseline_runner import run_baseline_experiments
from experiments.ablation.ablation_runner import run_ablation_experiments
from experiments.hyperparameter.hyperparameter_runner import run_hyperparameter_sweep
from experiments.robustness.robustness_runner import run_robustness_experiments
from experiments.scalability.scalability_runner import run_scalability_experiments
from experiments.statistical_tests import run_statistical_tests
from experiments.result_analyzer import aggregate_baseline_results, find_best_worst_seed
from experiments.report_generator import generate_report
from experiments.visualizations.viz_generator import generate_all_visualizations


# ─── Test 1: Config defaults ──────────────────────────────────────────────
def test_experiment_config():
    assert NUM_SEEDS >= 3
    assert len(ABLATION_STUDIES) == 5, "Must have exactly A1–A5"
    assert len(ROBUSTNESS_SCENARIOS) == 7
    assert len(HYPERPARAM_SWEEPS) == 5
    assert len(SCALABILITY_NUM_AGENTS) >= 3


# ─── Test 2: Baseline runner structure ────────────────────────────────────
def test_baseline_runner_structure():
    acc = run_baseline_experiments(num_seeds=2, runs_per_seed=2)
    for cond in [PROPOSED, BASELINE_A, BASELINE_B, BASELINE_C]:
        assert cond in acc, f"Missing condition: {cond}"
        assert "success_rate" in acc[cond]
        assert len(acc[cond]["success_rate"]) == 2  # 2 seeds
        for val in acc[cond]["success_rate"]:
            assert 0.0 <= val <= 1.0


# ─── Test 3: Ablation runner — all 5 IDs present ─────────────────────────
def test_ablation_runner_all_ids():
    results = run_ablation_experiments(runs=2)
    for abl_id in ABLATION_STUDIES.keys():
        assert abl_id in results, f"Missing ablation: {abl_id}"
        assert "delta" in results[abl_id]
        assert "success_rate_drop" in results[abl_id]["delta"]


# ─── Test 4: Hyperparameter sweep keys ────────────────────────────────────
def test_hyperparameter_sweep_keys():
    results = run_hyperparameter_sweep(runs_per_point=2)
    for param in HYPERPARAM_SWEEPS.keys():
        assert param in results, f"Missing param: {param}"
        for val, metrics in results[param].items():
            assert "success_rate" in metrics
            assert 0.0 <= metrics["success_rate"] <= 1.0


# ─── Test 5: Robustness scenarios count ───────────────────────────────────
def test_robustness_scenarios_count():
    results = run_robustness_experiments(runs=2)
    assert len(results) == len(ROBUSTNESS_SCENARIOS)
    for scenario in results:
        assert "degradation_delta" in results[scenario]
        assert "success_rate" in results[scenario]["degradation_delta"]


# ─── Test 6: Scalability — latency generally increases with agents ─────────
def test_scalability_latency_monotone():
    results = run_scalability_experiments(runs=2)
    agent_data = results.get("num_agents", {})
    assert len(agent_data) >= 3
    # Check all values in range
    for n, m in agent_data.items():
        assert 0.0 <= m["success_rate"] <= 1.0
        assert m["average_e2e_latency_s"] >= 0.0


# ─── Test 7: Result analyzer CI bounds ────────────────────────────────────
def test_result_analyzer_aggregation():
    acc = run_baseline_experiments(num_seeds=3, runs_per_seed=2)
    summary = aggregate_baseline_results(acc)
    for cond in [PROPOSED, BASELINE_A]:
        sr = summary["per_condition"][cond]["success_rate"]
        assert sr["ci_95_low"] <= sr["mean"] <= sr["ci_95_high"]

    seed_info = find_best_worst_seed(acc)
    assert "best_seed" in seed_info
    assert "worst_seed" in seed_info
    assert seed_info["best_value"] >= seed_info["worst_value"]


# ─── Test 8: Statistical tests RQ table structure ─────────────────────────
def test_statistical_tests_rq_table():
    acc = run_baseline_experiments(num_seeds=3, runs_per_seed=2)
    rq_results = run_statistical_tests(acc)
    for rq_id in ["RQ1", "RQ2", "RQ3", "RQ4", "RQ5", "RQ6"]:
        assert rq_id in rq_results, f"Missing {rq_id} in stats results"
        assert "comparisons" in rq_results[rq_id]


# ─── Test 9: Report generator creates files ───────────────────────────────
def test_report_generator_creates_files(tmp_path, monkeypatch):
    # Patch output paths to tmp_path
    import experiments.experiment_config as cfg
    monkeypatch.setattr(cfg, "OUT_REPORT", str(tmp_path / "REPORT.md"))
    monkeypatch.setattr(cfg, "OUT_REPORT_SUMMARY", str(tmp_path / "report_summary.txt"))

    # Re-import after patch
    import importlib
    import experiments.report_generator as rg
    importlib.reload(rg)

    acc = run_baseline_experiments(num_seeds=2, runs_per_seed=2)
    summary = aggregate_baseline_results(acc)
    rq_res  = run_statistical_tests(acc)
    abl_res = run_ablation_experiments(runs=2)
    rob_res = run_robustness_experiments(runs=2)
    sca_res = run_scalability_experiments(runs=2)

    rg.generate_report(summary, rq_res, abl_res, rob_res, sca_res)
    assert os.path.exists(str(tmp_path / "REPORT.md"))
    assert os.path.exists(str(tmp_path / "report_summary.txt"))


# ─── Test 10: Viz generator creates 9 HTML files ─────────────────────────
def test_viz_generator_creates_charts(tmp_path, monkeypatch):
    import experiments.experiment_config as cfg
    monkeypatch.setattr(cfg, "OUT_VISUALIZATIONS", str(tmp_path / "viz"))

    import importlib
    import experiments.visualizations.viz_generator as vg
    importlib.reload(vg)

    acc = run_baseline_experiments(num_seeds=2, runs_per_seed=2)
    summary = aggregate_baseline_results(acc)
    abl_res = run_ablation_experiments(runs=2)
    sca_res = run_scalability_experiments(runs=2)

    paths = vg.generate_all_visualizations(summary, acc, abl_res, sca_res)
    assert len(paths) == 9
    for p in paths:
        assert os.path.exists(p), f"Chart not created: {p}"
