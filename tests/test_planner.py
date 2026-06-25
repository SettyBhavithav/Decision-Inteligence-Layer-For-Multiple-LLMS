import pytest
from agents.planner.intent_analyzer import IntentAnalyzer
from agents.planner.task_decomposer import TaskDecomposer
from agents.planner.task_prioritizer import TaskPrioritizer
from agents.planner.agent_selector import AgentSelector
from agents.planner.planner_agent import PlannerAgent

def test_intent_analyzer_simulation():
    # Since we are testing offline/without NIM keys, we verify the analyzer can initialize
    analyzer = IntentAnalyzer()
    assert analyzer.model == "nvidia/nvidia-nemotron-nano-9b-v2"

def test_task_prioritizer():
    prioritizer = TaskPrioritizer()
    
    # Standard linear dependencies
    tasks = [
        {"id": "task_1", "description": "Write report", "dependencies": ["task_0"]},
        {"id": "task_0", "description": "Collect research", "dependencies": []}
    ]
    ordered = prioritizer.prioritize(tasks)
    assert ordered[0]["id"] == "task_0"
    assert ordered[1]["id"] == "task_1"
    
    # Circular dependency detection
    circular_tasks = [
        {"id": "task_0", "description": "A depends on B", "dependencies": ["task_1"]},
        {"id": "task_1", "description": "B depends on A", "dependencies": ["task_0"]}
    ]
    fallback_ordered = prioritizer.prioritize(circular_tasks)
    assert len(fallback_ordered) == 2

def test_agent_selector_fallback():
    selector = AgentSelector()
    
    # Test fallback classification rules
    role_1 = selector._fallback_rule_selector("Gather research data and relevant evidence")
    assert role_1 == "research"
    
    role_2 = selector._fallback_rule_selector("Format bibliography in IEEE format and citations")
    assert role_2 == "citation"
    
    role_3 = selector._fallback_rule_selector("Double-check all facts and detect hallucinations")
    assert role_3 == "verification"
    
    role_4 = selector._fallback_rule_selector("Audit inconsistency and logical review")
    assert role_4 == "reviewer"
    
    role_5 = selector._fallback_rule_selector("Draft general report content")
    assert role_5 == "writing"

def test_planner_agent_simulation():
    planner = PlannerAgent()
    planner.use_simulation = True
    
    tasks = planner.decompose("Write a paper on AI Safety")
    assert len(tasks) == 4
    assert tasks[0]["assigned_role"] == "research"
    assert tasks[1]["assigned_role"] == "writing"
    
    plan = planner.get_last_plan()
    assert "workflow_id" in plan
    assert plan["intent"] == "general"
