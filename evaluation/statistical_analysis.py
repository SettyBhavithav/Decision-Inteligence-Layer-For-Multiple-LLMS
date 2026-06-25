import numpy as np
from scipy import stats
from typing import List, Dict, Any

class StatisticalAnalysis:
    """
    Statistical analysis utilities for research paper reporting.
    Computes: Mean, Std, 95% CI, paired t-test p-value, Cohen's d effect size.
    """

    @staticmethod
    def describe(values: List[float]) -> Dict[str, float]:
        arr = np.array(values, dtype=float)
        n = len(arr)
        mean = float(np.mean(arr))
        std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
        se = std / np.sqrt(n) if n > 0 else 0.0
        # 95% CI using t-distribution
        if n > 1:
            t_crit = stats.t.ppf(0.975, df=n - 1)
            ci_low = mean - t_crit * se
            ci_high = mean + t_crit * se
        else:
            ci_low = ci_high = mean
        return {
            "n": n,
            "mean": round(mean, 4),
            "std": round(std, 4),
            "se": round(se, 4),
            "ci_95_low": round(ci_low, 4),
            "ci_95_high": round(ci_high, 4),
        }

    @staticmethod
    def paired_ttest(proposed: List[float], baseline: List[float]) -> Dict[str, float]:
        """Paired t-test between proposed and a baseline condition."""
        if len(proposed) != len(baseline) or len(proposed) < 2:
            return {"t_statistic": 0.0, "p_value": 1.0, "significant": False}
        t_stat, p_val = stats.ttest_rel(proposed, baseline)
        return {
            "t_statistic": round(float(t_stat), 4),
            "p_value": round(float(p_val), 4),
            "significant": bool(p_val < 0.05),
        }

    @staticmethod
    def cohens_d(proposed: List[float], baseline: List[float]) -> float:
        """Cohen's d effect size measure."""
        a, b = np.array(proposed, dtype=float), np.array(baseline, dtype=float)
        pooled_std = np.sqrt((np.std(a, ddof=1) ** 2 + np.std(b, ddof=1) ** 2) / 2)
        if pooled_std == 0:
            return 0.0
        return round(float((np.mean(a) - np.mean(b)) / pooled_std), 4)

    @staticmethod
    def compare_conditions(proposed: List[float],
                            baseline: List[float],
                            metric_name: str = "metric") -> Dict[str, Any]:
        """Full comparison: descriptive stats + significance + effect size."""
        return {
            "metric": metric_name,
            "proposed": StatisticalAnalysis.describe(proposed),
            "baseline": StatisticalAnalysis.describe(baseline),
            "ttest": StatisticalAnalysis.paired_ttest(proposed, baseline),
            "cohens_d": StatisticalAnalysis.cohens_d(proposed, baseline),
        }

    @staticmethod
    def format_report(comparisons: List[Dict[str, Any]]) -> str:
        """Format a human-readable stats report string."""
        lines = ["=" * 60, "STATISTICAL ANALYSIS REPORT", "=" * 60]
        for cmp in comparisons:
            m = cmp["metric"]
            p = cmp["proposed"]
            b = cmp["baseline"]
            t = cmp["ttest"]
            d = cmp["cohens_d"]
            lines.append(f"\nMetric: {m}")
            lines.append(f"  Proposed : {p['mean']:.4f} ± {p['std']:.4f}  "
                         f"[95% CI: {p['ci_95_low']:.4f} – {p['ci_95_high']:.4f}]")
            lines.append(f"  Baseline : {b['mean']:.4f} ± {b['std']:.4f}  "
                         f"[95% CI: {b['ci_95_low']:.4f} – {b['ci_95_high']:.4f}]")
            sig = "YES ✓" if t["significant"] else "NO"
            lines.append(f"  t={t['t_statistic']:.3f}, p={t['p_value']:.4f} | Significant: {sig}")
            lines.append(f"  Cohen's d = {d:.4f}")
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
