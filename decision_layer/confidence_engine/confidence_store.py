import threading
import datetime
import logging
from typing import Dict
from decision_layer.confidence_engine.models import AgentConfidence

logger = logging.getLogger("trust_framework")

class ConfidenceStore:
    """Submodule 1: Thread-safe storage for current agent confidence estimations."""
    def __init__(self, initial_confidence: float = 0.85):
        self._lock = threading.Lock()
        self._store: Dict[str, AgentConfidence] = {}
        self.initial_confidence = initial_confidence

    def get_confidence(self, agent_id: str) -> AgentConfidence:
        with self._lock:
            if agent_id not in self._store:
                timestamp = datetime.datetime.now().isoformat()
                self._store[agent_id] = AgentConfidence(
                    agent_id=agent_id, 
                    confidence_score=self.initial_confidence,
                    algorithm_used="proposed",
                    timestamp=timestamp
                )
            return self._store[agent_id]

    def set_confidence(self, agent_id: str, confidence_score: float, algorithm: str) -> None:
        with self._lock:
            timestamp = datetime.datetime.now().isoformat()
            self._store[agent_id] = AgentConfidence(
                agent_id=agent_id,
                confidence_score=confidence_score,
                algorithm_used=algorithm,
                timestamp=timestamp
            )
            logger.info(f"ConfidenceStore: Saved confidence for {agent_id} as {confidence_score:.3f}")
