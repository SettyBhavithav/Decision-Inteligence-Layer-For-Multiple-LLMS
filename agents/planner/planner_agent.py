import logging
from typing import Dict, Any, List

from agents.planner.intent_analyzer import IntentAnalyzer
from agents.planner.task_decomposer import TaskDecomposer
from agents.planner.task_prioritizer import TaskPrioritizer
from agents.planner.agent_selector import AgentSelector
from agents.planner.workflow_generator import WorkflowGenerator

logger = logging.getLogger("trust_framework")

class PlannerAgent:
    """
    Modular Planner Agent orchestrating 5 submodules:
    1. Intent Analyzer
    2. Task Decomposer
    3. Task Prioritizer
    4. Agent Selector
    5. Workflow Generator
    """
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.intent_analyzer = IntentAnalyzer(model)
        self.task_decomposer = TaskDecomposer(model)
        self.task_prioritizer = TaskPrioritizer()
        self.agent_selector = AgentSelector(model)
        self.workflow_generator = WorkflowGenerator()
        
        self.use_simulation: bool = False
        self.last_plan: Dict[str, Any] = {}

    def decompose(self, query: str) -> List[Dict[str, Any]]:
        """
        Runs the full 5-stage planning pipeline.
        Returns a topologically sorted list of subtasks (for orchestrator compatibility).
        """
        if self.use_simulation:
            plan = self._decompose_simulation(query)
            self.last_plan = plan
            return plan["tasks"]

        logger.info(f"PlannerAgent: Starting planning pipeline for query: '{query}'")
        
        # 1. Intent Analysis
        intent = self.intent_analyzer.analyze(query)
        
        # 2. Task Decomposition
        raw_tasks = self.task_decomposer.decompose(query)
        if not raw_tasks:
            # Fallback to simulation template if decomposition fails completely
            plan = self._decompose_simulation(query)
            self.last_plan = plan
            return plan["tasks"]
            
        # 3. Task Prioritization (Topological Sort)
        prioritized_tasks = self.task_prioritizer.prioritize(raw_tasks)
        
        # 4. Agent Selection (Role Mapping)
        mapped_tasks = self.agent_selector.select_agents(prioritized_tasks)
        
        # 5. Workflow Generation
        plan = self.workflow_generator.generate_plan(intent, mapped_tasks)
        self.last_plan = plan
        
        logger.info(f"PlannerAgent: Execution plan generated successfully (Workflow ID: {plan['workflow_id']})")
        return plan["tasks"]

    def get_last_plan(self) -> Dict[str, Any]:
        """Returns the full execution plan generated during the last decompose() call."""
        return self.last_plan

    def _decompose_simulation(self, query: str) -> Dict[str, Any]:
        """Simulation fallback generator."""
        subtasks = [
            {
                "id": "task_0",
                "description": f"Gather research data and relevant evidence for: '{query}'",
                "assigned_role": "research",
                "dependencies": []
            },
            {
                "id": "task_1",
                "description": f"Draft the report and compile research findings for: '{query}'",
                "assigned_role": "writing",
                "dependencies": ["task_0"]
            },
            {
                "id": "task_2",
                "description": "Cross-check details and format bibliography in IEEE style.",
                "assigned_role": "citation",
                "dependencies": ["task_1"]
            },
            {
                "id": "task_3",
                "description": "Conduct a critical review, check for logical consistency and accuracy.",
                "assigned_role": "reviewer",
                "dependencies": ["task_2"]
            }
        ]
        return self.workflow_generator.generate_plan("general", subtasks)
