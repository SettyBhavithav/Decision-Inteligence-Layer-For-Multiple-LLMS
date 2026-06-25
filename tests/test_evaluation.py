import pytest
from evaluation.task_metrics import TaskMetrics
from evaluation.trust_metrics import TrustMetrics
from evaluation.confidence_metrics import ConfidenceMetrics
from evaluation.decision_metrics import DecisionMetrics
from evaluation.communication_metrics import CommunicationMetrics
from evaluation.attribution_metrics import AttributionMetrics
from evaluation.system_metrics import SystemMetrics
from evaluation.statistical_analysis import StatisticalAnalysis
from evaluation.experiment_logger import ExperimentLogger
from evaluation.result_exporter import ResultExporter
from evaluation.benchmark_runner import BenchmarkRunner, PROPOSED, BASELINE_A, BASELINE_B, BASELINE_C


# ─── Category 1 ──────────────────────────────────────────────────────────────
def test_task_metrics_f1():
    m = TaskMetrics()
    # 3 TP, 1 FP, 1 FN
    m.log_result(True,  true_positive=True)
    m.log_result(True,  true_positive=True)
    m.log_result(True,  true_positive=True)
    m.log_result(False, false_positive=True)
    m.log_result(False, false_negative=True)

    assert m.success_rate() == pytest.approx(0.6, abs=1e-4)
    assert m.precision()    == pytest.approx(3 / 4, abs=1e-4)
    assert m.recall()       == pytest.approx(3 / 4, abs=1e-4)
    f1 = m.f1_score()
    assert 0.0 < f1 <= 1.0


# ─── Category 2 ──────────────────────────────────────────────────────────────
def test_trust_metrics_stability():
    m = TrustMetrics()
    scores = [0.80, 0.82, 0.81, 0.83, 0.80]
    for s in scores:
        m.log_trust("research", s)

    import numpy as np
    expected_std = round(float(np.std(scores)), 4)
    assert m.trust_stability()["research"] == pytest.approx(expected_std, abs=1e-3)
    assert 0.0 <= m.trust_recovery_rate() <= 1.0


# ─── Category 3 ──────────────────────────────────────────────────────────────
def test_confidence_metrics_ece():
    m = ConfidenceMetrics()
    for conf, suc in [(0.9, True), (0.8, True), (0.3, False), (0.4, False), (0.7, True)]:
        m.log_confidence(conf, suc)
    ece = m.ece()
    assert 0.0 <= ece <= 1.0
    assert m.average_confidence() > 0.0


# ─── Category 4 ──────────────────────────────────────────────────────────────
def test_decision_metrics_rates():
    m = DecisionMetrics()
    for action, lat in [("ACCEPT", 0.1), ("ACCEPT", 0.2), ("REJECT", 0.3), ("VERIFY", 0.15)]:
        m.log_decision(action, lat)

    total = m.accept_rate() + m.verify_rate() + m.reject_rate() + m.regenerate_rate()
    assert total == pytest.approx(1.0, abs=1e-4)
    assert m.average_latency() == pytest.approx((0.1 + 0.2 + 0.3 + 0.15) / 4, abs=1e-4)


# ─── Category 5 ──────────────────────────────────────────────────────────────
def test_communication_metrics_filter_ratio():
    m = CommunicationMetrics()
    m.log_message(sent=True,  filtered=False, payload_tokens=100, latency_s=0.05)
    m.log_message(sent=True,  filtered=False, payload_tokens=120, latency_s=0.04)
    m.log_message(sent=False, filtered=True,  payload_tokens=0,   latency_s=0.0)

    assert m.messages_sent    == 2
    assert m.messages_filtered == 1
    assert m.filter_ratio()   == pytest.approx(1/3, abs=1e-3)
    assert m.average_payload_size() == pytest.approx(110.0, abs=1e-3)


# ─── Category 6 ──────────────────────────────────────────────────────────────
def test_attribution_metrics_top2_gte_top1():
    m = AttributionMetrics()
    events = [
        ("research", "research", "writing",  True,  0.5),
        ("writing",  "writing",  "research",  True,  0.3),
        ("writing",  "research", "writing",   False, 0.0),  # top-2 correct
        ("citation", "research", "citation",  False, 0.0),  # top-2 correct
    ]
    for gt, t1, t2, rec, rt in events:
        m.log_attribution(gt, t1, t2, rec, rt)

    assert m.top2_accuracy() >= m.top1_accuracy()
    assert 0.0 <= m.recovery_success_rate() <= 1.0


# ─── Statistical Analysis ────────────────────────────────────────────────────
def test_statistical_analysis_ci():
    proposed = [0.85, 0.87, 0.88, 0.84, 0.86]
    baseline = [0.70, 0.72, 0.68, 0.71, 0.73]

    stats = StatisticalAnalysis.describe(proposed)
    assert stats["ci_95_low"] <= stats["mean"] <= stats["ci_95_high"]

    ttest = StatisticalAnalysis.paired_ttest(proposed, baseline)
    assert "t_statistic" in ttest
    assert "p_value" in ttest
    assert ttest["significant"] is True   # clearly different means

    d = StatisticalAnalysis.cohens_d(proposed, baseline)
    assert d > 0   # proposed > baseline


# ─── Benchmark Runner structure ───────────────────────────────────────────────
def test_benchmark_runner_structure():
    runner = BenchmarkRunner()
    results = runner.run_all(num_runs=3)

    # All 4 conditions must be present
    assert PROPOSED   in results
    assert BASELINE_A in results
    assert BASELINE_B in results
    assert BASELINE_C in results

    # Each condition must have all 7 metric categories
    required_cats = {"task", "trust", "confidence", "decision",
                     "communication", "attribution", "system"}
    for condition, data in results.items():
        assert required_cats.issubset(set(data.keys())), \
            f"Condition '{condition}' missing metric categories"

    # Task success rates must be in [0, 1]
    for condition in results:
        sr = results[condition]["task"]["success_rate"]
        assert 0.0 <= sr <= 1.0
