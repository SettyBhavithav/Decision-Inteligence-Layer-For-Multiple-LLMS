import logging
from typing import List, Dict, Any
from decision_layer.trust_engine.models import TrustUpdate

logger = logging.getLogger("trust_framework")

class TrustHistoryManager:
    """Submodule 4: Tracks chronological logs of trust score updates per agent."""
    def __init__(self):
        self._history: Dict[str, List[TrustUpdate]] = {}

    def log_update(self, update: TrustUpdate) -> None:
        agent_id = update.agent_id
        if agent_id not in self._history:
            self._history[agent_id] = []
        self._history[agent_id].append(update)
        logger.debug(f"TrustHistory: Logged update for {agent_id} ({update.change})")

    def get_history(self, agent_id: str) -> List[Dict[str, Any]]:
        records = self._history.get(agent_id, [])
        return [r.model_dump() for r in records]
