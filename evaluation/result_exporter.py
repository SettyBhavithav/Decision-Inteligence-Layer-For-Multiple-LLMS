import os
import json
import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger("trust_framework")

class ResultExporter:
    """
    Exports benchmark results to:
    - JSON file (full numeric results)
    - Markdown table (for research paper)
    - Plain-text statistical summary report
    """
    def __init__(self, output_dir: str = "experiments"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _timestamp(self) -> str:
        return time.strftime("%Y%m%d_%H%M%S")

    def export_json(self, results: Dict[str, Any], filename: str = None) -> str:
        fname = filename or f"results_{self._timestamp()}.json"
        path = os.path.join(self.output_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        logger.info(f"ResultExporter: JSON results written to {path}")
        return path

    def export_markdown_table(self, results: Dict[str, Any], filename: str = "summary_table.md") -> str:
        """Builds a Markdown comparison table from benchmark results dict."""
        path = os.path.join(self.output_dir, filename)
        baselines = list(results.keys())
        # Collect all metric keys from first baseline
        if not baselines:
            return path
        sample = results[baselines[0]]
        # Build flat metric rows
        metrics = {}
        for cat, vals in sample.items():
            if isinstance(vals, dict):
                for k, v in vals.items():
                    if isinstance(v, (int, float)):
                        metrics[f"{cat}.{k}"] = {}
        # Fill in values per baseline
        for bl in baselines:
            bl_data = results.get(bl, {})
            for cat, vals in bl_data.items():
                if isinstance(vals, dict):
                    for k, v in vals.items():
                        key = f"{cat}.{k}"
                        if key in metrics and isinstance(v, (int, float)):
                            metrics[key][bl] = v

        lines = []
        header = "| Metric | " + " | ".join(baselines) + " |"
        sep = "|---|" + "---|" * len(baselines)
        lines.append("# Benchmark Results Summary\n")
        lines.append(header)
        lines.append(sep)
        for metric_key, bl_vals in metrics.items():
            row = f"| {metric_key} |"
            for bl in baselines:
                val = bl_vals.get(bl, "—")
                row += f" {val} |"
            lines.append(row)

        content = "\n".join(lines)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"ResultExporter: Markdown table written to {path}")
        return path

    def export_stats_report(self, report_text: str, filename: str = "stats_report.txt") -> str:
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(report_text)
        logger.info(f"ResultExporter: Statistical report written to {path}")
        return path
