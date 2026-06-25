import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger("trust_framework")

class ExperimentLogger:
    """
    Per-run structured experiment logger.
    Records workflow ID, baseline name, all 7 metric category snapshots, and timestamp.
    """
    def __init__(self):
        self._runs: List[Dict[str, Any]] = []

    def log_run(self, workflow_id: str,
                baseline_name: str,
                task: Dict[str, Any],
                trust: Dict[str, Any],
                confidence: Dict[str, Any],
                decision: Dict[str, Any],
                communication: Dict[str, Any],
                attribution: Dict[str, Any],
                system: Dict[str, Any]) -> None:
        entry = {
            "workflow_id": workflow_id,
            "baseline_name": baseline_name,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "task": task,
            "trust": trust,
            "confidence": confidence,
            "decision": decision,
            "communication": communication,
            "attribution": attribution,
            "system": system,
        }
        self._runs.append(entry)
        logger.debug(f"ExperimentLogger: Logged run [{workflow_id}] for baseline '{baseline_name}'")

    def get_all_runs(self) -> List[Dict[str, Any]]:
        return list(self._runs)

    def get_runs_by_baseline(self, baseline_name: str) -> List[Dict[str, Any]]:
        return [r for r in self._runs if r["baseline_name"] == baseline_name]

    def extract_metric_series(self, baseline_name: str, category: str, key: str) -> List[float]:
        """Extract a flat list of a specific metric value across all runs for a baseline."""
        runs = self.get_runs_by_baseline(baseline_name)
        values = []
        for r in runs:
            cat_data = r.get(category, {})
            if key in cat_data:
                values.append(float(cat_data[key]))
        return values

    def clear(self) -> None:
        self._runs.clear()
