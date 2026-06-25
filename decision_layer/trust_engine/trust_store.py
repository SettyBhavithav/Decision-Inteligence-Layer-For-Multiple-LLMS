import threading
import logging
from typing import Dict
from decision_layer.trust_engine.models import AgentTrust

logger = logging.getLogger("trust_framework")

class TrustStore:
    """Submodule 1: Thread-safe storage for current agent trust scores."""
    def __init__(self, initial_trust: float = 0.80):
        self._lock = threading.Lock()
        self._store: Dict[str, AgentTrust] = {}
        self.initial_trust = initial_trust

    def get_trust(self, agent_id: str) -> AgentTrust:
        with self._lock:
            if agent_id not in self._store:
                # Initialize with configurable starting trust
                self._store[agent_id] = AgentTrust(agent_id=agent_id, trust_score=self.initial_trust)
            return self._store[agent_id]

    def set_trust(self, agent_id: str, trust_score: float, success: bool = True) -> None:
        with self._lock:
            current = self._store.get(agent_id)
            if not current:
                current = AgentTrust(agent_id=agent_id, trust_score=0.80)
                
            current.trust_score = trust_score
            if success:
                current.success_count += 1
            else:
                current.failure_count += 1
                
            self._store[agent_id] = current
            logger.info(f"TrustStore: Saved trust for {agent_id} as {trust_score:.3f}")
