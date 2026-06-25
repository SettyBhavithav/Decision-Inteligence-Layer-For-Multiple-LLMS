# Experimental Evaluation Report
## Confidence-Calibrated Trust-Aware Dynamic Collaboration Framework

### Data Source Classification
* **Real Data:** Baseline comparisons and task evaluations are based on real scientific papers (claim verification and citation verification tasks).
* **Semi-Synthetic Data:** Robustness testing and hyperparameter sweep scenarios utilize degraded agent performance profiles and biases derived from empirical LLM API latency/error rate distributions.
* **Fully Simulated Data:** Scalability evaluations (agent sweeps 2–10, graph depth sweeps) use fully simulated task DAG topologies to track execution constraints without live API limits.

---
## 1. Baseline Comparison (RQ1–RQ6)

### 1.1 Overall Performance Table (mean ± std [95% CI])

| Metric | Proposed | Baseline_A_FixedRule | Baseline_B_Standard | Baseline_C_Ablation |
|---|---|---|---|---|
| success_rate | 0.300±0.236 [0.131–0.469] | 0.220±0.175 [0.095–0.345] | 0.500±0.271 [0.306–0.694] | 0.440±0.158 [0.327–0.553] |
| f1_score | 0.415±0.285 [0.211–0.620] | 0.332±0.224 [0.172–0.492] | 0.630±0.227 [0.468–0.793] | 0.595±0.162 [0.480–0.711] |
| ece | 0.373±0.192 [0.235–0.510] | 0.574±0.201 [0.430–0.718] | 0.301±0.249 [0.123–0.479] | 0.256±0.232 [0.090–0.421] |
| accept_rate | 0.300±0.236 [0.131–0.469] | 0.220±0.175 [0.095–0.345] | 0.500±0.271 [0.306–0.694] | 0.440±0.158 [0.327–0.553] |
| filter_ratio | 0.000±0.000 [0.000–0.000] | 0.000±0.000 [0.000–0.000] | 0.000±0.000 [0.000–0.000] | 0.000±0.000 [0.000–0.000] |
| top1_accuracy | 0.249±0.307 [0.029–0.469] | 1.000±0.000 [1.000–1.000] | 0.589±0.221 [0.431–0.746] | 0.288±0.330 [0.052–0.524] |
| average_e2e_latency_s | 0.035±0.015 [0.024–0.045] | 0.017±0.010 [0.010–0.024] | 0.030±0.023 [0.013–0.046] | 0.038±0.020 [0.024–0.053] |

### 1.2 Statistical Significance Results

| RQ | Description | vs Baseline | mean±std | p-value | Sig? | Cohen's d | Effect |
|---|---|---|---|---|---|---|---|
| RQ1 | Task quality vs baselines | vs Baseline_A_FixedRule | 0.300 ± 0.236 | 0.3994 | ✗ | 0.385 | small |
| RQ1 | Task quality vs baselines | vs Baseline_B_Standard | 0.300 ± 0.236 | 0.1582 | ✗ | -0.788 | medium |
| RQ1 | Task quality vs baselines | vs Baseline_C_Ablation | 0.300 ± 0.236 | 0.0886 | ✗ | -0.698 | medium |
| RQ2 | Long-term reliability (trust engine) | vs Baseline_A_FixedRule | 0.300 ± 0.236 | 0.3994 | ✗ | 0.385 | small |
| RQ2 | Long-term reliability (trust engine) | vs Baseline_B_Standard | 0.300 ± 0.236 | 0.1582 | ✗ | -0.788 | medium |
| RQ2 | Long-term reliability (trust engine) | vs Baseline_C_Ablation | 0.300 ± 0.236 | 0.0886 | ✗ | -0.698 | medium |
| RQ3 | Confidence calibration quality | vs Baseline_A_FixedRule | 0.373 ± 0.192 | 0.0585 | ✗ | -1.023 | large |
| RQ3 | Confidence calibration quality | vs Baseline_B_Standard | 0.373 ± 0.192 | 0.5664 | ✗ | 0.322 | small |
| RQ3 | Confidence calibration quality | vs Baseline_C_Ablation | 0.373 ± 0.192 | 0.2142 | ✗ | 0.551 | medium |
| RQ4 | Decision correctness & efficiency | vs Baseline_A_FixedRule | 0.300 ± 0.236 | 0.3994 | ✗ | 0.385 | small |
| RQ4 | Decision correctness & efficiency | vs Baseline_B_Standard | 0.300 ± 0.236 | 0.1582 | ✗ | -0.788 | medium |
| RQ4 | Decision correctness & efficiency | vs Baseline_C_Ablation | 0.300 ± 0.236 | 0.0886 | ✗ | -0.698 | medium |
| RQ5 | Communication overhead reduction | vs Baseline_A_FixedRule | 0.000 ± 0.000 | nan | ✗ | 0.000 | negligible |
| RQ5 | Communication overhead reduction | vs Baseline_B_Standard | 0.000 ± 0.000 | nan | ✗ | 0.000 | negligible |
| RQ5 | Communication overhead reduction | vs Baseline_C_Ablation | 0.000 ± 0.000 | nan | ✗ | 0.000 | negligible |
| RQ6 | Failure attribution accuracy | vs Baseline_A_FixedRule | 0.249 ± 0.307 | 0.0000 | ✓ | -3.457 | large |
| RQ6 | Failure attribution accuracy | vs Baseline_B_Standard | 0.249 ± 0.307 | 0.0248 | ✓ | -1.270 | large |
| RQ6 | Failure attribution accuracy | vs Baseline_C_Ablation | 0.249 ± 0.307 | 0.7589 | ✗ | -0.123 | negligible |

---
## 2. Ablation Studies

| Ablation | Component Removed | ΔSuccess Rate | ΔF1 | ΔLatency (s) |
|---|---|---|---|---|
| A1_No_Trust | No_Trust | -0.800 | -0.667 | -0.023 |
| A2_No_Confidence | No_Confidence | -0.200 | -0.238 | -0.001 |
| A3_No_Decision | No_Decision | -0.400 | -0.417 | -0.013 |
| A4_No_Communication | No_Communication | -0.600 | -0.556 | -0.001 |
| A5_No_Failure_Attrib | No_Failure_Attrib | -0.200 | -0.238 | -0.003 |

---
## 3. Robustness Testing

| Scenario | ΔSuccess Rate | ΔF1 |
|---|---|---|
| Noisy_Inputs | +0.000 | +0.000 |
| Conflicting_Evidence | +0.400 | +0.571 |
| Missing_Citations | +0.600 | +0.750 |
| Hallucinated_Outputs | +0.200 | +0.333 |
| Partial_Retrieval_Failure | +0.000 | +0.000 |
| Communication_Failure | +0.400 | +0.571 |
| Agent_Timeout | +0.000 | +0.000 |

---
## 4. Scalability Analysis

### Agent Count Sweep

| Num Agents | Success Rate | Latency (s) |
|---|---|---|
| 2 | 0.200 | 0.140 |
| 4 | 0.600 | 0.038 |
| 6 | 0.400 | 0.040 |
| 8 | 0.000 | 0.024 |
| 10 | 0.000 | 0.031 |

### Token Budget Sweep

| Token Budget | Success Rate | Throughput |
|---|---|---|
| 500 | 0.200 | 27.335 |
| 1000 | 0.600 | 27.731 |
| 2000 | 0.400 | 41.456 |
| 4000 | 0.400 | 33.165 |

---
*Generated by Phase 25 Experimental Framework*