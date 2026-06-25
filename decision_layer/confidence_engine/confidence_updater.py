import logging
from decision_layer.confidence_engine.confidence_store import ConfidenceStore

logger = logging.getLogger("trust_framework")

class ConfidenceUpdater:
    """Submodule 3: Orchestrates saving the newly calculated confidence scores back to the store."""
    def __init__(self, store: ConfidenceStore):
        self.store = store

    def update(self, agent_id: str, new_score: float, algorithm: str) -> None:
        self.store.set_confidence(agent_id, new_score, algorithm)
        logger.info(f"ConfidenceUpdater: Successfully updated agent '{agent_id}' confidence to {new_score:.3f}")
