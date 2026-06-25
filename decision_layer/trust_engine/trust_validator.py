import logging

logger = logging.getLogger("trust_framework")

class TrustValidator:
    """Submodule 6: Enforces boundary constraints on trust updates (range [0.0 - 1.0])."""
    def __init__(self):
        pass

    def validate_trust(self, score: float) -> bool:
        if score < 0.0 or score > 1.0:
            logger.error(f"TrustValidator: Violation! Target trust score '{score}' falls outside range [0.0, 1.0]!")
            return False
        return True
