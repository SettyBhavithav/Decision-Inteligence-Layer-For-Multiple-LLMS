"""
experiment_config.py — Central configuration for all Phase 25 experiments.
All runners import this module to stay synchronized.
"""
from dataclasses import dataclass, field
from typing import Dict, List

# ─── Agent skill profiles ──────────────────────────────────────────────────
SKILLS_HIGH   = {"research": 0.92, "writing": 0.88, "citation": 0.95, "reviewer": 0.85, "verification": 0.97}
SKILLS_MEDIUM = {"research": 0.82, "writing": 0.70, "citation": 0.88, "reviewer": 0.68, "verification": 0.95}
SKILLS_LOW    = {"research": 0.60, "writing": 0.55, "citation": 0.65, "reviewer": 0.50, "verification": 0.75}

BIASES_DEFAULT = {"research": 0.15, "writing": 0.20, "citation": 0.12, "reviewer": 0.25, "verification": 0.05}
BIASES_NONE    = {"research": 0.0,  "writing": 0.0, "citation": 0.0,   "reviewer": 0.0,  "verification": 0.0}

# ─── Reproducibility ──────────────────────────────────────────────────────
NUM_SEEDS       = 15    # cross-seed runs per condition (Phase 11)
RUNS_PER_SEED   = 10    # simulation episodes per seed run
ABLATION_RUNS   = 10    # runs per ablation condition
ROBUSTNESS_RUNS = 10    # runs per robustness scenario
SCALABILITY_RUNS = 5    # runs per scalability data point

# ─── Hyperparameter sweep ranges ─────────────────────────────────────────
HYPERPARAM_SWEEPS: Dict[str, List[float]] = {
    "trust_alpha":              [0.10, 0.20, 0.30, 0.40, 0.50],
    "confidence_threshold":     [0.60, 0.65, 0.70, 0.75, 0.80],
    "decision_threshold":       [0.55, 0.65, 0.75, 0.85],
    "comm_value_threshold":     [0.30, 0.40, 0.50, 0.60, 0.70],
    "failure_severity_threshold": [0.10, 0.15, 0.20, 0.25],
}

# ─── Ablation study IDs ───────────────────────────────────────────────────
ABLATION_STUDIES = {
    "A1_No_Trust":          {"static_trust": True,  "calibration": True,  "bypass_comm": True,  "use_fae": True},
    "A2_No_Confidence":     {"static_trust": False, "calibration": False, "bypass_comm": True,  "use_fae": True},
    "A3_No_Decision":       {"static_trust": False, "calibration": True,  "bypass_comm": True,  "use_fae": True,  "no_decision": True},
    "A4_No_Communication":  {"static_trust": False, "calibration": True,  "bypass_comm": False, "use_fae": True},
    "A5_No_Failure_Attrib": {"static_trust": False, "calibration": True,  "bypass_comm": True,  "use_fae": False},
}

# ─── Robustness scenarios ─────────────────────────────────────────────────
ROBUSTNESS_SCENARIOS = {
    "Noisy_Inputs":             {"research": -0.15},
    "Conflicting_Evidence":     {"research": -0.10, "writing": -0.10},
    "Missing_Citations":        {"citation": -0.30},
    "Hallucinated_Outputs":     {"writing": -0.25},
    "Partial_Retrieval_Failure":{"research": -0.20},
    "Communication_Failure":    {"bypass_comm_override": False},
    "Agent_Timeout":            {"research": -0.10, "writing": -0.10, "citation": -0.10,
                                 "reviewer": -0.10, "verification": -0.10},
}

# ─── Scalability sweep values ─────────────────────────────────────────────
SCALABILITY_NUM_AGENTS    = [2, 4, 6, 8, 10]
SCALABILITY_WORKFLOW_DEPTH = [2, 3, 4, 5, 6]
SCALABILITY_TOKEN_BUDGETS  = [500, 1000, 2000, 4000]

# ─── Output directories ────────────────────────────────────────────────────
OUT_BASELINES       = "experiments/baselines"
OUT_ABLATION        = "experiments/ablation"
OUT_ROBUSTNESS      = "experiments/robustness"
OUT_SCALABILITY     = "experiments/scalability"
OUT_HYPERPARAMETER  = "experiments/hyperparameter"
OUT_VISUALIZATIONS  = "experiments/visualizations"
OUT_REPORT          = "experiments/REPORT.md"
OUT_REPORT_SUMMARY  = "experiments/report_summary.txt"
OUT_RESULTS_JSON    = "experiments/results_phase25.json"
