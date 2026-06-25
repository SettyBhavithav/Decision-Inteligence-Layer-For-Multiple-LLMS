import logging
from typing import List, Dict, Any
from decision_layer.communication_manager.models import CommunicationNode, CommunicationEdge
from decision_layer.communication_manager.communication_store import CommunicationStore

logger = logging.getLogger("trust_framework")

class CommunicationGraphBuilder:
    """Submodule 2: Constructs directed connection graphs representing agent pathways."""
    def __init__(self, store: CommunicationStore):
        self.store = store

    def rebuild_graph(self, active_agents: List[str], decision_package: Dict[str, Any] = None) -> None:
        self.store.clear_topology()
        
        # Register nodes
        for agent in active_agents:
            node = CommunicationNode(agent_id=agent, active=True)
            self.store.add_node(node)
            
        # Add primary sequential pipeline edges
        for i in range(len(active_agents) - 1):
            edge = CommunicationEdge(source=active_agents[i], target=active_agents[i+1], weight=1.0)
            self.store.add_edge(edge)
            
        # Dynamically inject retry/escalation edges based on Decision Engine output
        if decision_package:
            decision = decision_package.get("decision", "ACCEPT")
            workflow_id = decision_package.get("workflow_id", "w_1")
            
            if decision == "VERIFY":
                # Add edge to Verification agent
                edge = CommunicationEdge(source="writing", target="verification", weight=0.90)
                self.store.add_edge(edge)
            elif decision == "RETRY" or decision == "REGENERATE":
                # Add loopback retry edge to source agent
                edge = CommunicationEdge(source="reviewer", target="writing", weight=0.95)
                self.store.add_edge(edge)
                
        logger.info("CommunicationGraphBuilder: Finished rebuilding dynamic connection graph")
