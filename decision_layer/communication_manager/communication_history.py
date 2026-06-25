import logging
from typing import List, Dict, Any

logger = logging.getLogger("trust_framework")

class CommunicationHistoryManager:
    """Submodule 6: Tracks historical connection path routing results per workflow execution."""
    def __init__(self):
        self._history: Dict[str, List[Dict[str, Any]]] = {}

    def log_routing(self, workflow_id: str, record: Dict[str, Any]) -> None:
        if workflow_id not in self._history:
            self._history[workflow_id] = []
        self._history[workflow_id].append(record)
        logger.debug(f"CommunicationHistory: Logged route event for workflow '{workflow_id}'")

    def get_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        return list(self._history.get(workflow_id, []))
