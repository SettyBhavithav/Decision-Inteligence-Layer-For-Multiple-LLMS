"""
report_generator.py — Generates REPORT.md and report_summary.txt from all experiment results.
"""
import os
import logging
from typing import Dict, Any
from evaluation.benchmark_runner import PROPOSED, BASELINE_A, BASELINE_B, BASELINE_C
from experiments.experiment_config import OUT_REPORT, OUT_REPORT_SUMMARY

logger = logging.getLogger("trust_framework")

CONDITIONS_ORDER = [PROPOSED, BASELINE_A, BASELINE_B, BASELINE_C]
CORE_METRICS = ["success_rate", "f1_score", "ece", "accept_rate",
                "filter_ratio", "top1_accuracy", "average_e2e_latency_s"]


def _md_table(summary: Dict[str, Any]) -> str:
    header = "| Metric | " + " | ".join(CONDITIONS_ORDER) + " |"
    sep    = "|---|" + "---|" * len(CONDITIONS_ORDER)
    rows   = [header, sep]
    per = summary.get("per_condition", {})
    for metric in CORE_METRICS:
        row = f"| {metric} |"
        for cond in CONDITIONS_ORDER:
            d = per.get(cond, {}).get(metric, {})
            mean = d.get("mean", 0.0)
            std  = d.get("std",  0.0)
            ci_l = d.get("ci_95_low", mean)
            ci_h = d.get("ci_95_high", mean)
            row += f" {mean:.3f}±{std:.3f} [{ci_l:.3f}–{ci_h:.3f}] |"
        rows.append(row)
    return "\n".join(rows)


def _rq_table(rq_results: Dict[str, Any]) -> str:
    lines = ["| RQ | Description | vs Baseline | mean±std | p-value | Sig? | Cohen's d | Effect |",
             "|---|---|---|---|---|---|---|---|"]
    for rq_id, rq in rq_results.items():
        desc = rq.get("description", "")
        for bl, cmp in rq.get("comparisons", {}).items():
            sig = "✓" if cmp.get("significant") else "✗"
            lines.append(
                f"| {rq_id} | {desc} | vs {bl} | "
                f"{cmp['proposed_mean_std']} | "
                f"{cmp['p_value']:.4f} | {sig} | "
                f"{cmp['cohens_d']:.3f} | {cmp['effect_size']} |"
            )
    return "\n".join(lines)


def _ablation_table(ablation_results: Dict[str, Any]) -> str:
    lines = ["| Ablation | Component Removed | ΔSuccess Rate | ΔF1 | ΔLatency (s) |",
             "|---|---|---|---|---|"]
    for abl_id, data in ablation_results.items():
        d = data.get("delta", {})
        lines.append(
            f"| {abl_id} | {abl_id.split('_', 1)[1]} | "
            f"{d.get('success_rate_drop', 0):+.3f} | "
            f"{d.get('f1_drop', 0):+.3f} | "
            f"{d.get('latency_increase_s', 0):+.3f} |"
        )
    return "\n".join(lines)


def _robustness_table(robustness_results: Dict[str, Any]) -> str:
    lines = ["| Scenario | ΔSuccess Rate | ΔF1 |",
             "|---|---|---|"]
    for scenario, data in robustness_results.items():
        d = data.get("degradation_delta", {})
        lines.append(
            f"| {scenario} | {d.get('success_rate', 0):+.3f} | {d.get('f1_drop', 0):+.3f} |"
        )
    return "\n".join(lines)


def generate_report(summary: Dict[str, Any],
                    rq_results: Dict[str, Any],
                    ablation_results: Dict[str, Any],
                    robustness_results: Dict[str, Any],
                    scalability_results: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(OUT_REPORT), exist_ok=True)

    md_lines = [
        "# Experimental Evaluation Report",
        "## Confidence-Calibrated Trust-Aware Dynamic Collaboration Framework\n",
        "### Data Source Classification",
        "* **Real Data:** Baseline comparisons and task evaluations are based on real scientific papers (claim verification and citation verification tasks).",
        "* **Semi-Synthetic Data:** Robustness testing and hyperparameter sweep scenarios utilize degraded agent performance profiles and biases derived from empirical LLM API latency/error rate distributions.",
        "* **Fully Simulated Data:** Scalability evaluations (agent sweeps 2–10, graph depth sweeps) use fully simulated task DAG topologies to track execution constraints without live API limits.\n",
        "---",
        "## 1. Baseline Comparison (RQ1–RQ6)\n",
        "### 1.1 Overall Performance Table (mean ± std [95% CI])\n",
        _md_table(summary),
        "\n### 1.2 Statistical Significance Results\n",
        _rq_table(rq_results),
        "\n---",
        "## 2. Ablation Studies\n",
        _ablation_table(ablation_results),
        "\n---",
        "## 3. Robustness Testing\n",
        _robustness_table(robustness_results),
        "\n---",
        "## 4. Scalability Analysis\n",
        "### Agent Count Sweep\n",
        "| Num Agents | Success Rate | Latency (s) |",
        "|---|---|---|",
    ]
    for n, m in scalability_results.get("num_agents", {}).items():
        md_lines.append(f"| {n} | {m['success_rate']:.3f} | {m['average_e2e_latency_s']:.3f} |")

    md_lines += [
        "\n### Token Budget Sweep\n",
        "| Token Budget | Success Rate | Throughput |",
        "|---|---|---|",
    ]
    for b, m in scalability_results.get("token_budget", {}).items():
        md_lines.append(f"| {b} | {m['success_rate']:.3f} | {m['throughput']:.3f} |")

    md_lines.append("\n---\n*Generated by Phase 25 Experimental Framework*")

    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    logger.info(f"ReportGenerator: Full report written to {OUT_REPORT}")

    # Executive summary
    sig_rqs = [rq_id for rq_id, rq in rq_results.items()
               if any(c.get("significant") for c in rq.get("comparisons", {}).values())]
    summary_txt = (
        "EXECUTIVE SUMMARY\n" + "=" * 50 + "\n"
        f"Significant improvements found for: {', '.join(sig_rqs) if sig_rqs else 'None'}\n"
        f"Ablation studies completed: {len(ablation_results)}\n"
        f"Robustness scenarios tested: {len(robustness_results)}\n"
        f"See {OUT_REPORT} for full details.\n"
    )
    with open(OUT_REPORT_SUMMARY, "w", encoding="utf-8") as f:
        f.write(summary_txt)
    logger.info(f"ReportGenerator: Summary written to {OUT_REPORT_SUMMARY}")
