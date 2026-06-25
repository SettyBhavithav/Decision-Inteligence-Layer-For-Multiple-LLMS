import pytest
from decision_layer.communication_manager.models import CommunicationNode, CommunicationEdge
from decision_layer.communication_manager.communication_store import CommunicationStore
from decision_layer.communication_manager.graph_builder import CommunicationGraphBuilder
from decision_layer.communication_manager.routing_engine import RoutingEngine
from decision_layer.communication_manager.message_filter import MessageFilter
from decision_layer.communication_manager.communication_optimizer import CommunicationOptimizer
from decision_layer.communication_manager.communication_validator import CommunicationValidator
from decision_layer.communication_manager.communication_manager import CommunicationManager

def test_graph_builder_and_store():
    store = CommunicationStore()
    builder = CommunicationGraphBuilder(store)
    
    agents = ["planner", "research", "writing"]
    builder.rebuild_graph(agents)
    
    nodes = store.get_nodes()
    edges = store.get_edges()
    
    assert len(nodes) == 3
    assert len(edges) == 2
    assert edges[0].source == "planner"
    assert edges[0].target == "research"

def test_broadcast_routing():
    store = CommunicationStore()
    builder = CommunicationGraphBuilder(store)
    engine = RoutingEngine(store)
    
    agents = ["planner", "research", "writing"]
    builder.rebuild_graph(agents)
    
    route = engine.compute_route("full_broadcast", "planner", "writing", {})
    assert len(route) == 3
    assert "research" in route

def test_static_routing():
    store = CommunicationStore()
    builder = CommunicationGraphBuilder(store)
    engine = RoutingEngine(store)
    
    agents = ["planner", "research", "writing", "citation", "reviewer", "verification"]
    builder.rebuild_graph(agents)
    
    route = engine.compute_route("static", "research", "reviewer", {})
    assert route == ["research", "writing", "citation", "reviewer"]

def test_adaptive_routing_bypass():
    store = CommunicationStore()
    builder = CommunicationGraphBuilder(store)
    engine = RoutingEngine(store)
    
    agents = ["planner", "research", "writing", "citation", "reviewer", "verification"]
    builder.rebuild_graph(agents)
    
    # Low complexity and high trust -> bypass intermediates
    metrics = {
        "trust_score": 0.95,
        "confidence_score": 0.95,
        "complexity": "low",
        "decision": "ACCEPT"
    }
    
    route = engine.compute_route("adaptive", "research", "reviewer", metrics)
    assert route == ["research", "reviewer"]

def test_message_filter():
    filt = MessageFilter()
    
    p1 = {"content": " Factual data assertion. "}
    p2 = {"content": " Factual data assertion. "}
    p3 = {"content": " Factual data assertion. "}
    p4 = {"content": " Different claim data assertion. "}
    
    assert filt.should_filter(p1) is False
    assert filt.should_filter(p2) is True
    assert filt.should_filter(p3) is True
    assert filt.should_filter(p4) is False

def test_communication_optimizer():
    opt = CommunicationOptimizer()
    
    content = "A" * 600
    payload = {"content": content}
    
    opt_payload = opt.optimize_payload(payload, compress=True)
    assert opt_payload["compressed"] is True
    assert len(opt_payload["content"]) < len(content)

def test_communication_validator():
    store = CommunicationStore()
    builder = CommunicationGraphBuilder(store)
    validator = CommunicationValidator(store)
    
    agents = ["planner", "research", "writing"]
    builder.rebuild_graph(agents)
    
    assert validator.validate_route(["planner", "research"]) is True
    assert validator.validate_route(["planner", "unknown_agent"]) is False

def test_communication_manager_orchestrator():
    manager = CommunicationManager(strategy="adaptive")
    
    payload = {"content": "A literature review draft on systems."}
    metrics = {
        "trust_score": 0.90,
        "confidence_score": 0.90,
        "complexity": "medium",
        "active_agents": ["planner", "research", "writing", "reviewer"],
        "tokens": 120
    }
    
    res = manager.route_message("w_101", "research", "writing", payload, metrics)
    assert res["strategy"] == "adaptive"
    assert "research" in res["route"]
    assert len(res["history"]) == 1
