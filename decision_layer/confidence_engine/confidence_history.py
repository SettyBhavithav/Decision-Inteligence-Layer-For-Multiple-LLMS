import logging
from typing import List, Dict, Any
from decision_layer.confidence_engine.models import ConfidenceUpdate

logger = logging.getLogger("trust_framework")

class ConfidenceHistoryManager:
    """Submodule 4: Tracks chronological logs of confidence score updates per agent."""
    def __init__(self):
        self._history: Dict[str, List[ConfidenceUpdate]] = {}

    def log_update(self, update: ConfidenceUpdate) -> None:
        agent_id = update.agent_id
        if agent_id not in self._history:
            self._history[agent_id] = []
        self._history[agent_id].append(update)
        logger.debug(f"ConfidenceHistory: Logged update for {agent_id} ({update.change})")

    def get_history(self, agent_id: str) -> List[Dict[str, Any]]:
        records = self._history.get(agent_id, [])
        return [r.model_dump() for r in records]
