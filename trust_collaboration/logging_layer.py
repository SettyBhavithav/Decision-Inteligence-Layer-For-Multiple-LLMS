import time
import json
import logging
from typing import Dict, Any, List

# Setup default logger
logger = logging.getLogger("trust_framework")
logger.setLevel(logging.DEBUG)

# File handler and stream handler can be configured
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)

class EventLogger:
    """
    Logging Layer (Layer 9).
    Aggregates runtime events, token counts, execution latency, and error states.
    """
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.token_usage: Dict[str, int] = {"prompt": 0, "completion": 0, "total": 0}
        self.start_times: Dict[str, float] = {}
        self.latencies: Dict[str, float] = {}

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
            self.log_event("latency", {"label": label, "elapsed_seconds": elapsed, "message": f"{label} executed in {elapsed:.3f}s"})
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

    def get_summary(self) -> Dict[str, Any]:
        """Compile a summary of execution logs."""
        return {
            "total_events": len(self.events),
            "token_usage": self.token_usage,
            "latencies": self.latencies,
            "failures_detected": sum(1 for e in self.events if e["type"] == "failure")
        }

    def save_logs_to_file(self, filepath: str) -> None:
        """Serialize all events to a JSON file."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({
                    "token_usage": self.token_usage,
                    "latencies": self.latencies,
                    "events": self.events
                }, f, indent=2)
            logger.info(f"Logs saved successfully to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save log file: {e}")
            
    def clear(self) -> None:
        """Clear session logs."""
        self.events.clear()
        self.token_usage = {"prompt": 0, "completion": 0, "total": 0}
        self.start_times.clear()
        self.latencies.clear()
