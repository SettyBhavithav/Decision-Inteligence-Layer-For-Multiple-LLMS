import logging
from typing import List, Dict, Any

logger = logging.getLogger("trust_framework")

class FailurePropagationAnalyzer:
    """Submodule 5: Traces downstream error propagation through collaborator pipelines."""
    def __init__(self):
        pass

    def trace_propagation(self, culprit_agent: str, active_agents: List[str]) -> List[str]:
        if culprit_agent not in active_agents:
            return [culprit_agent]
            
        i_culprit = active_agents.index(culprit_agent)
        
        # Build path showing how the error spread from culprit down the remaining pipeline
        path = active_agents[i_culprit:]
        logger.info(f"FailurePropagationAnalyzer: Rebuilt propagation path: {' -> '.join(path)}")
        return path
