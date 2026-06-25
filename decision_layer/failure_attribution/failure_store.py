import threading
import logging
from typing import Dict, Optional
from decision_layer.failure_attribution.models import FailurePackage

logger = logging.getLogger("trust_framework")

class FailureStore:
    """Submodule 1: Thread-safe storage for failure package reports."""
    def __init__(self):
        self._lock = threading.Lock()
        self._store: Dict[str, FailurePackage] = {}

    def get_failure(self, workflow_id: str) -> Optional[FailurePackage]:
        with self._lock:
            return self._store.get(workflow_id)

    def set_failure(self, workflow_id: str, package: FailurePackage) -> None:
        with self._lock:
            self._store[workflow_id] = package
            logger.info(f"FailureStore: Logged failure package for workflow '{workflow_id}'")
