import logging
from decision_layer.trust_engine.trust_store import TrustStore

logger = logging.getLogger("trust_framework")

class TrustUpdater:
    """Submodule 3: Orchestrates saving the newly calculated trust scores back to the store."""
    def __init__(self, store: TrustStore):
        self.store = store

    def update(self, agent_id: str, new_score: float, success: bool = True) -> None:
        self.store.set_trust(agent_id, new_score, success)
        logger.info(f"TrustUpdater: Successfully updated agent '{agent_id}' to score {new_score:.3f}")
