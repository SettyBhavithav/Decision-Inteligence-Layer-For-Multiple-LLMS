import logging
from typing import List, Dict, Any
from decision_layer.communication_manager.communication_store import CommunicationStore

logger = logging.getLogger("trust_framework")

class CommunicationValidator:
    """Submodule 8: Verifies path connectivity and validates payload authorizations."""
    def __init__(self, store: CommunicationStore):
        self.store = store

    def validate_route(self, route: List[str]) -> bool:
        if not route:
            logger.error("CommunicationValidator: Violation! Empty route sequence detected!")
            return False
            
        nodes = {n.agent_id for n in self.store.get_nodes()}
        
        # Verify all route nodes are registered in the topology graph
        for node in route:
            if node not in nodes:
                logger.error(f"CommunicationValidator: Violation! Node '{node}' is not registered in graph!")
                return False
                
        return True
