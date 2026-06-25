import logging
from typing import List, Dict, Any
from decision_layer.decision_engine.models import DecisionResult

logger = logging.getLogger("trust_framework")

class DecisionHistoryManager:
    """Submodule 6: Logs and retrieves historical decisions per workflow ID."""
    def __init__(self):
        self._history: Dict[str, List[DecisionResult]] = {}

    def log_decision(self, workflow_id: str, result: DecisionResult) -> None:
        if workflow_id not in self._history:
            self._history[workflow_id] = []
        self._history[workflow_id].append(result)
        logger.debug(f"DecisionHistory: Logged decision '{result.decision}' for workflow '{workflow_id}'")

    def get_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        records = self._history.get(workflow_id, [])
        return [r.model_dump() for r in records]
