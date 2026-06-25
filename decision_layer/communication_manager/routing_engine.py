import logging
from typing import List, Dict, Any
from decision_layer.communication_manager.communication_store import CommunicationStore

logger = logging.getLogger("trust_framework")

class RoutingEngine:
    """Submodule 3: Decides source, target, and pathway sequence paths using routing strategies."""
    def __init__(self, store: CommunicationStore):
        self.store = store

    def compute_route(self, 
                      strategy: str, 
                      source: str, 
                      target: str, 
                      metrics: Dict[str, Any]) -> List[str]:
                      
        strategy_name = strategy.strip().lower()
        
        if strategy_name == "full_broadcast":
            return self._compute_broadcast(source, target)
        elif strategy_name == "static":
            return self._compute_static(source, target)
        else:
            return self._compute_adaptive(source, target, metrics)

    def _compute_broadcast(self, source: str, target: str) -> List[str]:
        # Connect active source to all registered nodes in the topology
        nodes = self.store.get_nodes()
        path = [source]
        for node in nodes:
            if node.agent_id != source:
                path.append(node.agent_id)
        return path

    def _compute_static(self, source: str, target: str) -> List[str]:
        # Static sequential chain mapping
        pipeline = ["planner", "research", "writing", "citation", "reviewer", "verification"]
        
        if source not in pipeline or target not in pipeline:
            return [source, target]
            
        i_src = pipeline.index(source)
        i_tgt = pipeline.index(target)
        
        if i_src < i_tgt:
            return pipeline[i_src : i_tgt + 1]
        else:
            return [source, target]

    def _compute_adaptive(self, source: str, target: str, metrics: Dict[str, Any]) -> List[str]:
        # Proposed Adaptive Strategy
        # Estimate expected Communication Value (CV)
        trust = metrics.get("trust_score", 0.80)
        confidence = metrics.get("confidence_score", 0.85)
        complexity = metrics.get("complexity", "medium").lower()
        
        comp_val = 1.0 if complexity == "high" else (0.60 if complexity == "medium" else 0.30)
        
        # Communication Value estimation
        comm_value = trust * confidence * comp_val
        
        # Default decision-based routing
        decision = metrics.get("decision", "ACCEPT")
        
        if decision == "ACCEPT" and comm_value < 0.40:
            # Low value accept, bypass intermediate stages (e.g. skip Reviewer/Verification)
            logger.info("RoutingEngine: Low complexity and high trust, bypass intermediate citation/reviewer steps")
            return [source, target]
            
        # Standard dynamic path calculation based on topology connections
        edges = self.store.get_edges()
        path = [source]
        
        # Simple traversal along edges from source to target
        current = source
        visited = {source}
        
        while current != target:
            next_node = None
            for edge in edges:
                if edge.source == current and edge.target not in visited:
                    next_node = edge.target
                    break
            if next_node:
                path.append(next_node)
                visited.add(next_node)
                current = next_node
            else:
                # Direct route fallback if graph traversal fails
                if target not in path:
                    path.append(target)
                break
                
        return path
