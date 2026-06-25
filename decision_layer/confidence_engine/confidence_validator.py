import logging

logger = logging.getLogger("trust_framework")

class ConfidenceValidator:
    """Submodule 6: Enforces boundary constraints on confidence scores (range [0.0 - 1.0])."""
    def __init__(self):
        pass

    def validate_confidence(self, score: float) -> bool:
        if score < 0.0 or score > 1.0:
            logger.error(f"ConfidenceValidator: Violation! Estimated score '{score}' falls outside range [0.0, 1.0]!")
            return False
        return True
