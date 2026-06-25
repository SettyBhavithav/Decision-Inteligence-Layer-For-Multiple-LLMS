import logging
from typing import Dict, Any, List

logger = logging.getLogger("trust_framework")

class CommunicationManager:
    """
    Adaptive Communication Manager.
    Logs communication events, constructs the communication graph,
    and dynamically determines optimal routing paths.
    """
    def __init__(self, bypass_enabled: bool = True):
        self.bypass_enabled = bypass_enabled
        # List of communication records: {"from": str, "to": str, "message": str, "confidence": float, "step": int}
        self.history: List[Dict[str, Any]] = []
        self.total_tokens_saved: int = 0

    def log_communication(self, 
                          sender: str, 
                          receiver: str, 
                          message_snippet: str, 
                          confidence: float, 
                          step_index: int) -> None:
        """Record a communication transition between agents."""
        record = {
            "from": sender,
            "to": receiver,
            "snippet": message_snippet[:100] + ("..." if len(message_snippet) > 100 else ""),
            "confidence": confidence,
            "step": step_index
        }
        self.history.append(record)
        logger.info(f"Communication: {sender} -> {receiver} at step {step_index} (Confidence: {confidence:.2f})")

    def should_route(self, 
                     current_role: str, 
                     next_role: str, 
                     calibrated_conf: float, 
                     trust_score: float, 
                     task_metadata: Dict[str, Any]) -> bool:
        """
        Adaptive routing decision.
        Decides if we can skip/bypass the next role in the pipeline.
        Example: If we are writing (writing -> citation) and confidence * trust is extremely high (e.g. > 0.85)
        and task complexity is 'low', we can bypass citation or review to save tokens.
        """
        if not self.bypass_enabled:
            return True
            
        reliability = calibrated_conf * trust_score
        complexity = task_metadata.get("complexity", "medium").lower()

        # If reliability is extremely high, and complexity is low or medium, we can bypass review/citation
        if next_role.lower() in ["citation", "reviewer"] and reliability > 0.88 and complexity != "high":
            logger.info(f"Communication: Bypassing {next_role} due to high reliability ({reliability:.3f}) and complexity ({complexity}).")
            self.total_tokens_saved += 500  # Estimate saved tokens
            return False
            
        return True

    def get_graph(self) -> List[Dict[str, Any]]:
        """Return the logged communication trace as nodes/edges for UI visualization."""
        return list(self.history)

    def get_metrics(self) -> Dict[str, Any]:
        """Return communication efficiency statistics."""
        return {
            "total_interactions": len(self.history),
            "estimated_tokens_saved": self.total_tokens_saved,
            "bypasses_count": sum(1 for h in self.history if "bypass" in h.get("snippet", "").lower())
        }

    def reset(self) -> None:
        """Reset the communication trace."""
        self.history.clear()
        self.total_tokens_saved = 0
