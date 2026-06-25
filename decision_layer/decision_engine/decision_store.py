import threading
import logging
from typing import Dict, Optional
from decision_layer.decision_engine.models import DecisionResult

logger = logging.getLogger("trust_framework")

class DecisionStore:
    """Submodule 1: Thread-safe storage for current workflow execution decisions."""
    def __init__(self):
        self._lock = threading.Lock()
        self._store: Dict[str, DecisionResult] = {}

    def get_decision(self, workflow_id: str) -> Optional[DecisionResult]:
        with self._lock:
            return self._store.get(workflow_id)

    def set_decision(self, workflow_id: str, result: DecisionResult) -> None:
        with self._lock:
            self._store[workflow_id] = result
            logger.info(f"DecisionStore: Saved decision for workflow '{workflow_id}' as '{result.decision}'")
