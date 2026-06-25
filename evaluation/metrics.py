import time
import json
import logging
import numpy as np
from typing import Dict, Any, List

logger = logging.getLogger("trust_framework")

class EventLogger:
    """
    Evaluation & Logging Layer.
    Aggregates runtime events, token counts, execution latency, and error states.
    Computes ECE (Expected Calibration Error) and Brier score for evaluation.
    """
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.token_usage: Dict[str, int] = {"prompt": 0, "completion": 0, "total": 0}
        self.start_times: Dict[str, float] = {}
        self.latencies: Dict[str, float] = {}
        
        # Calibration logs: list of tuples (predicted_calibrated_conf, actual_success_label)
        self.calibration_data: List[tuple] = []

    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log a generic system event with timestamp."""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "details": details
        }
        self.events.append(event)
        logger.info(f"[{event_type.upper()}] {details.get('message', str(details))}")

    def start_timer(self, label: str) -> None:
        """Start execution latency timer."""
        self.start_times[label] = time.time()

    def stop_timer(self, label: str) -> float:
        """Stop execution latency timer and record result."""
        if label in self.start_times:
            elapsed = time.time() - self.start_times[label]
            self.latencies[label] = elapsed
            self.log_event("latency", {
                "label": label, 
                "elapsed_seconds": elapsed, 
                "message": f"{label} executed in {elapsed:.3f}s"
            })
            return elapsed
        return 0.0

    def add_tokens(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Record token consumption."""
        self.token_usage["prompt"] += prompt_tokens
        self.token_usage["completion"] += completion_tokens
        self.token_usage["total"] += (prompt_tokens + completion_tokens)
        self.log_event("tokens", {
            "added_prompt": prompt_tokens, 
            "added_completion": completion_tokens,
            "message": f"Tokens added: Prompt={prompt_tokens}, Completion={completion_tokens}. Total={self.token_usage['total']}"
        })

    def log_calibration_point(self, conf: float, success: bool) -> None:
        """Record calibration point: (calibrated_confidence, success_label 1/0)."""
        label = 1 if success else 0
        self.calibration_data.append((conf, label))

    def calculate_ece(self, n_bins: int = 5) -> float:
        """
        Calculates the Expected Calibration Error (ECE).
        """
        if not self.calibration_data:
            return 0.0
            
        confs = np.array([p[0] for p in self.calibration_data])
        labels = np.array([p[1] for p in self.calibration_data])
        n_samples = len(self.calibration_data)
        
        ece = 0.0
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        
        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]
            
            # Find elements in this bin
            in_bin = (confs >= bin_lower) & (confs < bin_upper)
            prop_in_bin = np.mean(in_bin)
            
            if prop_in_bin > 0:
                accuracy_in_bin = np.mean(labels[in_bin])
                avg_confidence_in_bin = np.mean(confs[in_bin])
                ece += prop_in_bin * np.abs(avg_confidence_in_bin - accuracy_in_bin)
                
        return float(ece)

    def calculate_brier_score(self) -> float:
        """
        Calculates the Brier Score (mean squared error of probability predictions).
        """
        if not self.calibration_data:
            return 0.0
            
        errors = [(conf - label) ** 2 for conf, label in self.calibration_data]
        return float(np.mean(errors))

    def get_summary(self) -> Dict[str, Any]:
        """Compile execution logs and evaluation stats."""
        return {
            "total_events": len(self.events),
            "token_usage": self.token_usage,
            "latencies": self.latencies,
            "failures_detected": sum(1 for e in self.events if e["type"] == "failure"),
            "ece_score": self.calculate_ece(),
            "brier_score": self.calculate_brier_score()
        }

    def save_logs_to_file(self, filepath: str) -> None:
        """Serialize logs to JSON file."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({
                    "token_usage": self.token_usage,
                    "latencies": self.latencies,
                    "metrics": self.get_summary(),
                    "events": self.events
                }, f, indent=2)
            logger.info(f"Logs saved successfully to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save logs to file: {e}")
            
    def clear(self) -> None:
        """Clear session logs."""
        self.events.clear()
        self.token_usage = {"prompt": 0, "completion": 0, "total": 0}
        self.start_times.clear()
        self.latencies.clear()
        self.calibration_data.clear()
