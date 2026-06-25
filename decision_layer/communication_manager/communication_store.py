import threading
import logging
from typing import Dict, List, Any
from decision_layer.communication_manager.models import CommunicationNode, CommunicationEdge

logger = logging.getLogger("trust_framework")

class CommunicationStore:
    """Submodule 1: Thread-safe storage for connection nodes and edges."""
    def __init__(self):
        self._lock = threading.Lock()
        self._nodes: Dict[str, CommunicationNode] = {}
        self._edges: List[CommunicationEdge] = []

    def get_nodes(self) -> List[CommunicationNode]:
        with self._lock:
            return list(self._nodes.values())

    def get_edges(self) -> List[CommunicationEdge]:
        with self._lock:
            return list(self._edges)

    def add_node(self, node: CommunicationNode) -> None:
        with self._lock:
            self._nodes[node.agent_id] = node
            logger.debug(f"CommunicationStore: Registered node '{node.agent_id}'")

    def add_edge(self, edge: CommunicationEdge) -> None:
        with self._lock:
            self._edges.append(edge)
            logger.debug(f"CommunicationStore: Registered edge '{edge.source} -> {edge.target}'")

    def clear_topology(self) -> None:
        with self._lock:
            self._nodes.clear()
            self._edges.clear()
            logger.info("CommunicationStore: Cleared topology layout")
