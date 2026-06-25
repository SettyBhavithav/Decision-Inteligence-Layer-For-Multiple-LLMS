import logging
import datetime
from typing import Dict, Any, List

from decision_layer.communication_manager.models import CommunicationNode, CommunicationEdge
from decision_layer.communication_manager.communication_store import CommunicationStore
from decision_layer.communication_manager.graph_builder import CommunicationGraphBuilder
from decision_layer.communication_manager.routing_engine import RoutingEngine
from decision_layer.communication_manager.message_filter import MessageFilter
from decision_layer.communication_manager.communication_optimizer import CommunicationOptimizer
from decision_layer.communication_manager.routing_explainer import RoutingExplainer
from decision_layer.communication_manager.communication_validator import CommunicationValidator
from decision_layer.communication_manager.communication_package import CommunicationPackageGenerator
from decision_layer.communication_manager.communication_metrics import CommunicationMetricsTracker

logger = logging.getLogger("trust_framework")

class CommunicationManager:
    """
    Adaptive Communication Manager implementing pluggable strategies:
    1. Full Broadcast (baseline)
    2. Static pipeline routing (baseline)
    3. Proposed Adaptive Value-Based routing (our algorithm)
    
    Includes backward compatible legacy should_route logic.
    """
    def __init__(self, 
                 bypass_enabled: bool = True, 
                 strategy: str = "adaptive", 
                 model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
                 
        self.bypass_enabled = bypass_enabled
        self.strategy_name = strategy.strip().lower()
        self.total_tokens_saved = 0
        self.history: List[Dict[str, Any]] = []
        
        self.store = CommunicationStore()
        self.graph_builder = CommunicationGraphBuilder(self.store)
        self.routing_engine = RoutingEngine(self.store)
        self.message_filter = MessageFilter()
        self.optimizer = CommunicationOptimizer()
        self.explainer = RoutingExplainer(model)
        self.validator = CommunicationValidator(self.store)
        self.package_gen = CommunicationPackageGenerator()
        self.tracker = CommunicationMetricsTracker(self.store)
        
        logger.info(f"CommunicationManager: Initialized using strategy: '{self.strategy_name}'")

    def route_message(self, 
                      workflow_id: str, 
                      source: str, 
                      target: str, 
                      payload: Dict[str, Any], 
                      metrics: Dict[str, Any], 
                      compress: bool = False) -> Dict[str, Any]:
        """
        New pluggable entry point for message routing.
        Filters redundant payloads, optimizes context sizes, and generates routes.
        """
        self.tracker.start_timer()
        
        # 1. Rebuild connection topology
        active_agents = metrics.get("active_agents", ["planner", "research", "writing", "citation", "reviewer", "verification"])
        self.graph_builder.rebuild_graph(active_agents, metrics.get("decision_package"))
        
        # 2. Compute route path
        route = self.routing_engine.compute_route(self.strategy_name, source, target, metrics)
        
        # 3. Apply message filter checks
        filtered = self.message_filter.should_filter(payload)
        
        # 4. Optimize token footprint
        optimized_payload = self.optimizer.optimize_payload(payload, compress)
        
        # 5. Validate pathway
        if not self.validator.validate_route(route):
            logger.warning("CommunicationManager: Route validation failed. Defaulting to direct path.")
            route = [source, target]
            
        # 6. Generate route explanations
        explanation = self.explainer.explain_route(source, target, route, metrics)
        
        # 7. Collect telemetry and log record
        msg_size = len(optimized_payload.get("content", ""))
        self.tracker.log_message(msg_size, filtered, tokens=metrics.get("tokens", 100))
        self.tracker.stop_timer()
        
        # Legacy history record binding
        legacy_record = {
            "from": source,
            "to": target,
            "snippet": optimized_payload.get("content", "")[:100] + ("..." if msg_size > 100 else ""),
            "confidence": metrics.get("confidence_score", 0.85),
            "step": metrics.get("step_index", 1)
        }
        self.history.append(legacy_record)
        
        # History track log list
        hist_entry = {
            "source": source,
            "target": target,
            "route": route,
            "filtered": filtered,
            "explanation": explanation,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        comp_metrics = self.tracker.compile_metrics()
        package = self.package_gen.build_package(
            workflow_id=workflow_id,
            route=route,
            strategy=self.strategy_name,
            messages=[optimized_payload] if not filtered else [],
            metrics=comp_metrics,
            history=[hist_entry]
        )
        
        logger.info(f"CommunicationManager: Message routed from '{source}' to '{target}'. Path length: {len(route)}")
        return package.model_dump()

    def log_communication(self, 
                          sender: str, 
                          receiver: str, 
                          message_snippet: str, 
                          confidence: float, 
                          step_index: int) -> None:
        """Legacy helper for backward compatibility."""
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
        Legacy routing check helper.
        Bypasses intermediate steps if confidence/trust is high.
        """
        if not self.bypass_enabled:
            return True
            
        reliability = calibrated_conf * trust_score
        complexity = task_metadata.get("complexity", "medium").lower()

        if next_role.lower() in ["citation", "reviewer"] and reliability > 0.88 and complexity != "high":
            logger.info(f"Communication: Bypassing {next_role} due to high reliability ({reliability:.3f}) and complexity ({complexity}).")
            self.total_tokens_saved += 500
            return False
            
        return True

    def get_graph(self) -> List[Dict[str, Any]]:
        """Legacy helper for backward compatibility."""
        return list(self.history)

    def get_metrics(self) -> Dict[str, Any]:
        """Legacy helper for backward compatibility."""
        return {
            "total_interactions": len(self.history),
            "estimated_tokens_saved": self.total_tokens_saved,
            "bypasses_count": sum(1 for h in self.history if "bypass" in h.get("snippet", "").lower())
        }

    def reset(self) -> None:
        """Legacy helper for backward compatibility."""
        self.history.clear()
        self.total_tokens_saved = 0
